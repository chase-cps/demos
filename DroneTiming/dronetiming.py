"""DroneTiming: the timing of the fire-suppression drones, as a linear program.

The multi-drone fire suppression (MDFS) of ContrACT (Section V.B): the
contracts that ContrACT builds for the timing of each reaction (latencies
of Table III) are in dronetiming.ltl, as linear constraints over the
reals; a reaction that waits for two others starts at the later of the two,
a disjunction (a binary variable of the MILP of ContrACT). z3 checks and
optimizes them, in place of Gurobi. This script follows the analysis with
the CHASE Python package (pip install chase-cps[z3]):

  1. The mission subgraph (FireTick, FireSpread, FireStateRx) refines
     Mission: it delays the drones by at most 59 ms, its worst case.
  2. The pipeline of a drone refines Available: with the offset of 59 ms,
     the drone moves within 400 ms of its timestamp. Repair finds nothing
     to change: it holds.
  3. The worst case of the pipeline, one optimization: 280 ms, the bound of
     the paper (why the timer can go from 500 ms to 300 ms).
  4. Repair as optimization: the least bound that holds (lam = 280), the
     slowest the planner may be (x_plan = 192 ms, 72 + 120), and the
     largest delay of the mission subgraph (offset = 179 ms, 59 + 120).

The page out/dronetiming.html draws the two subgraphs inside their
requirements, with the requirement at its least bound.

    python dronetiming.py
    python dronetiming.py --expect     # exit code 1 when a result is not the expected one
"""

import os
import sys

from chase_cps import load_spec, maximize, refines, repair, viz

HERE = os.path.dirname(os.path.abspath(__file__))
PIPELINE = ["DroneTick", "DroneSim2", "Assign", "Target", "Plan", "Grant", "Move", "DroneSim3"]


def number(v):
    return int(v) if v == int(v) else float(v)


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "dronetiming.ltl"))
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    mission = c["FireTick"].compose(c["FireSpread"]).compose(c["FireStateRx"])
    show(1, "the mission subgraph refines Mission", refines(mission, c["Mission"]).status, "valid")
    worst = maximize("d_fr - t_fr", [mission.assumption, mission.guarantee, "t_ft = d_ft"], mission.variables)
    show(1, "its worst case (ms)", number(worst.value), 59)

    pipeline = c[PIPELINE[0]]
    for name in PIPELINE[1:]:
        pipeline = pipeline.compose(c[name])
    show(2, "the pipeline of a drone refines Available", refines(pipeline, c["Available"]).status, "valid")
    r = repair("refines", pipeline, c["Available"], parameters={"lam": (0, 1000)})
    show(2, "repair of lam", r.status, "holds")

    worst = maximize("d_s3 - t_s3", [pipeline.assumption, pipeline.guarantee, "t_dk <= d_dk",
                                     "d_dk - t_dk <= 59"], pipeline.variables)
    show(3, "the worst case of the pipeline (ms)", number(worst.value), 280)

    for name, how, want in (("lam", "minimize", 280), ("x_plan", "maximize", 192), ("offset", "maximize", 179)):
        r = repair("refines", pipeline, c["Available"], parameters={name: (0, 1000)}, **{how: name})
        show(4, f"{how} {name}", number(r.values[name]), want)
        print(f"   {r.status}, optimal {r.optimal}, {r.method} in {r.rounds} rounds, {r.seconds:.1f} s")

    tight = c["Available"].instantiate({"lam": 280}, name="Available_least")
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=[(mission, c["Mission"]), (pipeline, tight, refines(pipeline, tight))],
                                open=[c["Mission"], tight, c["Plan"]],
                                title="DroneTiming: the mission and a drone, within their bounds"),
                    os.path.join(HERE, "out", "dronetiming.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
