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
     the drone moves within 400 ms of its timestamp. Its worst case, one
     optimization: 280 ms, the bound of the paper (why the timer can go
     from 500 ms to 300 ms).
  3. A faster timer, of 250 ms (Fast): the pipeline does not refine it; the
     counterexample is a drone that moves 251 ms after its timestamp.
  4. Repair of Fast: the least bound that holds (deadline = 280), or a
     faster planner (x_plan = 42 ms, 30 ms less); each change is optimal.
  5. The margins under the bound of 400 ms: the slowest the planner may be
     (x_plan = 192 ms, 72 + 120), and the largest delay of the mission
     subgraph (offset = 179 ms, 59 + 120).

The page out/dronetiming.html draws the mission inside Mission, and the
pipeline of a drone inside Fast before the repair (red) and with the faster
planner (green).

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
    worst = maximize("d_s3 - t_s3", [pipeline.assumption, pipeline.guarantee, "t_dk <= d_dk",
                                     "d_dk - t_dk <= 59"], pipeline.variables)
    show(2, "its worst case (ms)", number(worst.value), 280)

    fast = refines(pipeline, c["Fast"])
    show(3, "the pipeline refines Fast (250 ms)", fast.status, "invalid")
    t = fast.guarantees.trace
    late = number((t.prefix + t.loop)[0]["d_s3"] - (t.prefix + t.loop)[0]["t_s3"]) if t else None
    show(3, f"in the counterexample, the drone moves {late} ms after its timestamp, more than 250",
         late is not None and late > 250, True)

    for name, want in (("deadline", 280), ("x_plan", 42)):
        r = repair("refines", pipeline, c["Fast"], parameters={name: (0, 1000)})
        show(4, f"repair of Fast by {name}", number(r.values[name]), want)
        print(f"   {r.status}, optimal {r.optimal}, {r.method} in {r.rounds} rounds, {r.seconds:.1f} s")

    plan42 = c["Plan"].instantiate({"x_plan": 42})
    faster = c[PIPELINE[0]]
    for name in PIPELINE[1:]:
        faster = faster.compose(plan42 if name == "Plan" else c[name])
    fixed = c["Fast"].instantiate({}, name="Fast_repaired")
    show(4, "with x_plan = 42, the pipeline refines Fast", refines(faster, c["Fast"]).status, "valid")

    for name, how, want in (("x_plan", "maximize", 192), ("offset", "maximize", 179)):
        r = repair("refines", pipeline, c["Available"], parameters={name: (0, 1000)}, **{how: name})
        show(5, f"{how} {name} under 400 ms", number(r.values[name]), want)
        print(f"   {r.status}, optimal {r.optimal}, {r.method} in {r.rounds} rounds, {r.seconds:.1f} s")

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(refines=[(mission, c["Mission"]), (pipeline, c["Fast"], fast),
                                         (faster, fixed, refines(faster, fixed))],
                                open=[c["Mission"], c["Fast"], fixed, c["Plan"], plan42],
                                title="DroneTiming: the mission, and a drone before and after the repair"),
                    os.path.join(HERE, "out", "dronetiming.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    sys.exit(main("--expect" in sys.argv))
