"""Delegation: a task of an AI agent split among three sub-agents.

The question: a parent agent splits a task among three sub-agents and
gives each one a contract over its tool calls. Do the sub-agents, together,
keep every rule of the user and deliver what the user asked for? If not,
what is missing, and who should do it?

The task is 530b157_1 of AppWorld (Trivedi et al., ACL 2024), with the
plan and the contracts of a run of ACORN, whose contracts are those of
ContrAgent (temporal formulas over the tool calls of an agent): "Kristin
paid for the groceries; pay her back on Venmo the amount in her text
messages, with the note 'Groceries', then text her 'It is done.'"
(requirements.txt). The sub-agents are 1, Messages (finds the amount), 2,
Payment (pays on Venmo), and 3, Text (sends the text); the parent keeps
the completion of the task. This script follows the check of the plan with
the CHASE Python package (pip install chase-cps):

  1. The contracts that follow from the tools alone (each rule goes to the
     sub-agents that hold its tools; the payment to the only one that holds
     Venmo) do not refine the contract of the parent. The counterexample
     pays and never sends the text: no sub-agent has to.
  2. Q3 = Parent / (Messages || Payment || Keep), the quotient with
     discharge, is what Text must do: its rules, and F text3.
  3. Text, with F text3 and the start condition that the payment is done,
     refines Q3, so the plan refines the contract of the parent.
  4. A plan in which the parent also writes "never pay" (a slip) is not
     consistent, and the unsat core names the two clauses in conflict.

    python delegation.py
    python delegation.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv or NuSMV. The formulas are read on infinite traces,
as CHASE reads them.
"""

from __future__ import annotations

import argparse
import sys
import time

from chase_cps import Contract, is_consistent, ltl, refines

B = "bool"
# The variables: one per tool call of a sub-agent (a call does not say who
# makes it, so each one has its own), the arguments, and the fact that the
# payment is done, which the Venmo tool writes.
SIGNALS = ("voice1", "tx2", "desc_ok", "paid", "text3", "msg_ok", "voice3", "complete")

# H: the rules of the user and what the user asked for (the contract of the parent).
H = {
    "G (text3 -> paid)": "H1 text after the payment",
    "G (paid -> G !tx2)": "H2 pay once",
    "G (tx2 -> desc_ok)": "H3 the note is 'Groceries'",
    "G (text3 -> msg_ok)": "H4 the text is 'It is done.'",
    "G (!voice1 & !voice3)": "H5 no voice message",
    "F tx2": "H6 deliver: the payment",
    "F text3": "H7 deliver: the text",
    "F complete": "H8 deliver: the task marked complete",
}
PARENT = Contract.from_strings(name="Parent", outputs={v: B for v in SIGNALS}, guarantees=list(H))

MESSAGES = Contract.from_strings(          # 1: reads the messages; holds the voice tool
    name="Messages", outputs={"voice1": B}, guarantees=["G !voice1"])
PAYMENT = Contract.from_strings(           # 2: the only one that holds Venmo
    name="Payment", outputs={"tx2": B, "desc_ok": B, "paid": B},
    guarantees=["!paid", "G (X paid <-> (paid | tx2))",       # the Venmo tool writes paid
                "G (paid -> G !tx2)", "G (tx2 -> desc_ok)", "F tx2"])
KEEP = Contract.from_strings(              # what the parent keeps
    name="Keep", outputs={"complete": B}, guarantees=["F complete"])
TEXT_FROM_TOOLS = Contract.from_strings(   # 3: the rules of its tools only
    name="Text", inputs={"paid": B}, outputs={"text3": B, "msg_ok": B, "voice3": B},
    guarantees=["G (text3 -> paid)", "G (text3 -> msg_ok)", "G !voice3"])
TEXT = Contract.from_strings(              # 3: as the contract agent of ACORN wrote it
    name="Text", inputs={"paid": B}, outputs={"text3": B, "msg_ok": B, "voice3": B},
    assumptions=["F paid"],                                   # start when the payment is done
    guarantees=["G (text3 -> paid)", "G (text3 -> msg_ok)", "G !voice3", "F text3"])


def show(trace) -> None:
    """The steps of a counterexample, one line per step."""
    for i, s in enumerate(trace.prefix + trace.loop):
        loop = "   <- the loop starts" if trace.loop and i == len(trace.prefix) else ""
        print(f"     {i}: " + " ".join(f"{x}={int(bool(s.get(x)))}" for x in SIGNALS) + loop)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    t = args.timeout
    wrong = []

    def compose(contracts, name):
        c = contracts[0]
        for d in contracts[1:]:
            c = c.compose(d, name=name, discharge=True, timeout=t)
        return c

    def step(title, expected, run, counterexample=False):
        start = time.time()
        r = run()
        mark = "" if r.status == expected else f"   (expected {expected})"
        print(f"\n{title}: {r.status} [{time.time() - start:.1f} s]{mark}")
        if counterexample and r.guarantees.trace is not None:
            print("   a counterexample:")
            show(r.guarantees.trace)
        if r.status != expected:
            wrong.append(title)

    step("1. Messages || Payment || Text (from the tools) || Keep refines Parent", "invalid",
         lambda: refines(compose([MESSAGES, PAYMENT, TEXT_FROM_TOOLS, KEEP], "Plan"), PARENT,
                         timeout=t), counterexample=True)

    q3 = PARENT.divide(compose([MESSAGES, PAYMENT, KEEP], "Rest"), name="Q3", discharge=True,
                       timeout=t)
    print("\n2. Q3 = Parent / (Messages || Payment || Keep) guarantees:")
    for g in q3.guarantees:
        print("      " + ltl.to_str(g))

    step("3. Text refines Q3", "valid", lambda: refines(TEXT, q3, timeout=t))
    step("   Messages || Payment || Text || Keep refines Parent", "valid",
         lambda: refines(compose([MESSAGES, PAYMENT, TEXT, KEEP], "Plan"), PARENT, timeout=t))

    start = time.time()
    slip = PARENT.ensure("G !tx2", name="ParentWithSlip")
    r = is_consistent(slip, core=True, timeout=t)
    mark = "" if r.status == "unsat" else "   (expected unsat)"
    print(f"\n4. The parent with 'never pay' is consistent: {r.status} "
          f"[{time.time() - start:.1f} s]{mark}")
    if r.core is not None and r.core.status == "found":
        print("   unsat core:")
        for g in r.core.core.guarantees:
            text = ltl.to_str(g)
            print(f"      {text:24} {H.get(text, 'the slip of the parent')}")
    if r.status != "unsat":
        wrong.append("4")

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
