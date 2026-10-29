"""AI agents: decomposing a task among sub-agents.

A user gives an AI agent a task in natural language, with rules: "Kristin
paid for the groceries. Pay her back on Venmo the amount in her text
messages, with the note 'Groceries', then text her 'It is done.' Do not
send voice messages." (task 530b157_1 of AppWorld, Trivedi et al., ACL
2024; requirements.txt). The rules and what the user asked for become a set
of contracts over the tool calls of the agent: the contract of the parent
agent. The parent splits the task among three sub-agents, 1 Messages (finds
the amount), 2 Payment (pays on Venmo), and 3 Text (sends the text), and
keeps the completion of the task.

The question: do the contracts of the sub-agents, together, refine the
contract of the parent? If not, what is missing, and which sub-agent must
do it? This script follows the decomposition with the CHASE Python package
(pip install chase-cps):

  1. Each sub-agent gets the rules of the tools it holds, and the payment
     goes to the only one that holds Venmo. These contracts, composed, do
     not refine the contract of the parent: the counterexample pays and
     never sends the text.
  2. Q3 = Parent / (Messages || Payment || Keep), the quotient with
     discharge, is what sub-agent 3 must guarantee: the rules of its tools,
     and F text3.
  3. Text, with F text3 and the start condition that the payment is done,
     refines Q3, so the decomposition refines the contract of the parent.
  4. A clause that contradicts the rules of the user (the parent also
     writes "never pay") makes the contract inconsistent, and the unsat
     core names the two clauses in conflict.

Once checked, the contracts of the sub-agents can be enforced on their
tool calls at run time, for instance with ContrAgent.

    python agents.py
    python agents.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv or NuSMV. The formulas are read on infinite traces,
as CHASE reads them.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import Component, Contract, System, is_consistent, ltl, refines, viz

HERE = os.path.dirname(os.path.abspath(__file__))

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
        return r

    tools = step("1. Messages || Payment || Text (from the tools) || Keep refines Parent",
                 "invalid",
                 lambda: refines(compose([MESSAGES, PAYMENT, TEXT_FROM_TOOLS, KEEP], "Plan"),
                                 PARENT, timeout=t),
                 counterexample=True)

    q3 = PARENT.divide(compose([MESSAGES, PAYMENT, KEEP], "Rest"), name="Q3", discharge=True,
                       timeout=t)
    print("\n2. Q3 = Parent / (Messages || Payment || Keep) guarantees:")
    for g in q3.guarantees:
        print("      " + ltl.to_str(g))

    text_q3 = step("3. Text refines Q3", "valid", lambda: refines(TEXT, q3, timeout=t))
    step("   Messages || Payment || Text || Keep refines Parent", "valid",
         lambda: refines(compose([MESSAGES, PAYMENT, TEXT, KEEP], "Plan"), PARENT, timeout=t))

    start = time.time()
    slip = PARENT.ensure("G !tx2", name="ParentWithSlip")
    r = slip_consistent = is_consistent(slip, core=True, timeout=t)
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

    # The diagram, one picture per step: the plan with sub-agent 3 from its
    # tools, inside the parent (1); Q3, with Text in its hole (2, 3); the
    # parent with the slip, and its core (4). The plan with Text inside the
    # parent is drawn like the first one, and is left out.
    plan = System("Plan", [Component("Messages", MESSAGES), Component("Payment", PAYMENT),
                           Component("Text", TEXT_FROM_TOOLS), Component("Keep", KEEP)],
                  contract=PARENT, status=tools.status)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    page = viz.save(viz.diagram(plan, q3, slip, refines=[(TEXT, q3, text_q3)],
                                checks=[(slip, "consistent", slip_consistent)],
                                open=[PARENT, TEXT_FROM_TOOLS, q3, TEXT, slip],
                                title="AI agents: decomposing a task"),
                    os.path.join(HERE, "out", "agents.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
