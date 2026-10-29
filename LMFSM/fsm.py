"""Finite state machine: conflicting requirements and the time of a pullup.

An autopilot commands a safety maneuver (pullup) when a sensor reports a
hazard; the requirements are those of the finite state machine of the Ten
Lockheed Martin Cyber-Physical Challenges (requirements.txt). fsm.ltl has
the contracts of the autopilot and of the sensor, first as the requirements
were written and then corrected, and of the whole system. This script
follows the analysis with the CHASE Python package (pip install chase-cps),
and gives the cores by the numbers of the requirements:

  1. The first requirements of the autopilot are unrealizable. The
     unrealizable core gives two requirements in conflict; the one with a
     corrected version (v2) is replaced, and the check is done again until
     the contract is realizable: four conflicts. The sensor has one.
  2. The corrected contracts, with what the Simulink model does in the
     other cases and its outputs, are realizable.
  3. The autopilot and the sensor feed each other (good, MODE, REQUEST).
     Composed with discharge, they do not refine FSM-001: the pullup does
     not come at the step the limits are exceeded. The counterexample shows
     why.
  4. They refine FSM-001t, which gives the pullup the steps it takes.

    python fsm.py
    python fsm.py --expect     # exit code 1 when a result is not the expected one

The checks need slugs (realizability, cores) and nuXmv or NuSMV
(discharge, refinement).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time

from chase_cps import Contract, load_spec, is_realizable, refines, ltl, viz

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(HERE, "fsm.ltl")
SIGNALS = ("standby", "apfail", "supported", "limits", "STATE", "SENSTATE", "good", "pullup")


def numbers(path: str) -> dict[str, dict[str, str]]:
    """The number of each term of each contract: the comment at the end of
    its line in the specification file."""
    out, contract = {}, None
    for line in open(path):
        m = re.match(r"CONTRACT (\w+):", line)
        if m:
            contract = m.group(1)
            out[contract] = {}
        m = re.match(r"\s*(.+);\s*# (\S+)\s*$", line)
        if m and contract:
            out[contract][ltl.to_str(ltl.parse(m.group(1)))] = m.group(2)
    return out


NUMBERS = numbers(SPEC)


def number(f, contract: str) -> str:
    return NUMBERS.get(contract, {}).get(ltl.to_str(f), "")


def terms(formulas, contract: str) -> str:
    return "\n".join(f"      {number(f, contract):10}{ltl.to_str(f)}" for f in formulas)


def trace(result) -> str:
    """The steps of a counterexample, one line per step."""
    t = result.trace
    lines = []
    for i, state in enumerate(t.prefix + t.loop):
        loop = "  <- loop" if t.loop and i == len(t.prefix) else ""
        lines.append(f"      {i}: " + " ".join(f"{s}={int(state.get(s))}" for s in SIGNALS) + loop)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    c = load_spec(SPEC)
    t = args.timeout
    wrong = []

    def step(title, expected, run):
        start = time.time()
        r, text = run()
        status = r.status
        seconds = time.time() - start
        mark = "" if status == expected else f"   (expected {expected})"
        print(f"\n{title}: {status} [{seconds:.1f} s]{mark}")
        if text:
            print(text)
        if status != expected:
            wrong.append(title)
        return r

    cores = {}                      # the first check of each contract, with its core

    def fix(first: str, fixed: str):
        """Replace a requirement of each unrealizable core by its corrected
        version, until the contract is realizable."""
        def run():
            contract, lines = c[first], []
            corrected = {n: f for f, n in ((ltl.parse(s), n) for s, n in NUMBERS[fixed].items())}
            while True:
                r = is_realizable(contract, core=True, timeout=t)
                cores.setdefault(first, r)
                if r.status != "unrealizable" or r.core is None or r.core.status != "found":
                    break
                core = r.core.core.guarantees
                lines.append("   unrealizable core:\n" + terms(core, first))
                old = [f for f in core if number(f, first) + "v2" in corrected]
                if not old:
                    break
                n = number(old[0], first)
                lines.append(f"   {n} is replaced by {n}v2")
                NUMBERS[first][ltl.to_str(corrected[n + "v2"])] = n + "v2"
                g = [corrected[n + "v2"] if f is old[0] else f for f in contract.guarantees]
                contract = Contract(first, dict(contract.inputs), dict(contract.outputs),
                                    list(contract.assumptions), g)
            return r, "\n".join(lines)
        return run
    step("1. AutopilotFirst, corrected at each core, is realizable", "realizable",
         fix("AutopilotFirst", "Autopilot"))
    step("   SensorFirst, corrected at each core, is realizable", "realizable",
         fix("SensorFirst", "Sensor"))

    autopilot = step("2. Autopilot is realizable", "realizable",
                     lambda: (is_realizable(c["Autopilot"], timeout=t), ""))
    sensor = step("   Sensor is realizable", "realizable",
                  lambda: (is_realizable(c["Sensor"], timeout=t), ""))

    fsm = c["Autopilot"].compose(c["Sensor"], discharge=True)

    def system():
        r = refines(fsm, c["System"], timeout=t)
        part = getattr(r, r.failed) if r.failed else None
        text = ""
        if part is not None and part.trace is not None:
            text = (f"   assumptions left after discharge: {len(fsm.assumptions)}\n"
                    f"   the {r.failed} fail; a counterexample:\n" + trace(part))
        return r, text
    untimed = step("3. Autopilot, Sensor refine System (FSM-001)", "invalid", system)

    timed = step("4. Autopilot, Sensor refine SystemTimed (FSM-001t)", "valid",
                 lambda: (refines(fsm, c["SystemTimed"], timeout=t), ""))

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(c["AutopilotFirst"], c["SensorFirst"],
                                refines=[(fsm, c["System"], untimed),
                                         (fsm, c["SystemTimed"], timed)],
                                checks=[(c[k], "realizable", r) for k, r in
                                        [("AutopilotFirst", cores["AutopilotFirst"]),
                                         ("SensorFirst", cores["SensorFirst"]),
                                         ("Autopilot", autopilot), ("Sensor", sensor)]],
                                title="Finite state machine: conflicting requirements"),
                    os.path.join(HERE, "out", "fsm.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
