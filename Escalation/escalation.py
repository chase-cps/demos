"""Escalation link: verifying a hardware design module by module.

The question: the escalation link of a security chip (a toy version of the
one of OpenTitan) is made of a sender, the wires, and a receiver. Does it
meet its requirements, and can we show it by verifying each module on its
own?

The sender raises a differential pair (esc_p/esc_n) to make the receiver
escalate, and pings the receiver with one-cycle pulses; the receiver
answers on a response pair (resp_p/resp_n). A wrong wire, a fault or an
attack, makes the two wires of a pair equal, which the receiver and the
sender detect. The requirements are written after the end-to-end
assertions of OpenTitan (prim_esc_rxtx_assert_fpv): Functional (escalation,
no false escalation, ping) and Integrity (a single wrong wire is detected).
The contracts are in SystemVerilog Assertions (sva/), the RTL in Verilog
(rtl/). This script follows the verification with the CHASE Python package
(pip install chase-cps[rtl]):

  1. The RTL of each module implements its contract (Yosys and nuXmv).
  2. Sender || Channel || Receiver refines Functional and Integrity. By the
     theory of contracts, the three modules together meet the requirements,
     with no check on the whole design.
  3. The same holds for the whole RTL, checked directly (a cross-check).
  4. SenderSlot = Functional / (Channel || Receiver) is what any sender
     must do; the contract of the sender refines it.
  5. A faster sender, which pings at every cycle of a ping request, does
     not implement the contract of the sender: its pulses last more than
     one cycle. In the whole link, a ping escalates the receiver.

The page out/escalation.html draws the system inside Functional, with
Functional and the receiver open.

    python escalation.py
    python escalation.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv or NuSMV, and Yosys (pip install chase-cps[rtl]).
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import Component, Model, System, is_implementation, parse_sva, refines, viz

HERE = os.path.dirname(os.path.abspath(__file__))
RTL = os.path.join(HERE, "rtl")
SHOWN = ("esc_req", "ping_req", "esc_p_tx", "esc_req_o", "ping_ok")


def read(name: str):
    """The contract of sva/<name>.sv."""
    with open(os.path.join(HERE, "sva", f"{name}.sv")) as f:
        r = parse_sva(f.read(), name=name.capitalize())
    assert not r.skipped, r.skipped
    return r.contract


def rtl(top: str, *files: str) -> Model:
    """The module top of the files in rtl/, as a state machine."""
    return Model.from_rtl([os.path.join(RTL, f) for f in files], top)


def trace(result) -> str:
    """The steps of a counterexample, one line per step."""
    t = result.trace
    lines = []
    for i, state in enumerate(t.prefix + t.loop):
        loop = "  <- loop" if t.loop and i == len(t.prefix) else ""
        lines.append(f"      {i}: " + " ".join(f"{s}={int(bool(state[s]))}"
                                              for s in SHOWN if s in state) + loop)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="time limit of each check, in seconds")
    args = parser.parse_args()
    t = args.timeout
    wrong = []

    def step(title, expected, run, show=False):
        start = time.time()
        r = run()
        mark = "" if r.status == expected else f"   (expected {expected})"
        print(f"\n{title}: {r.status} [{time.time() - start:.1f} s]{mark}")
        if show and getattr(r, "trace", None) is not None:
            print("   a counterexample:\n" + trace(r))
        if r.status != expected:
            wrong.append(title)
        return r

    sender, channel, receiver = read("sender"), read("channel"), read("receiver")
    functional, integrity = read("functional"), read("integrity")
    models = {"Sender": rtl("esc_sender", "esc_sender.v"),
              "Channel": rtl("esc_channel", "esc_channel.v"),
              "Receiver": rtl("esc_receiver", "esc_receiver.v")}

    link = System("Link", [Component("Sender", sender, models["Sender"]),
                           Component("Channel", channel, models["Channel"]),
                           Component("Receiver", receiver, models["Receiver"])],
                  contract=functional)
    for k in link.components:
        k.status = step(f"1. The RTL of {k.name} implements its contract", "valid",
                        lambda k=k: is_implementation(k.implementation, k.contract,
                                                      timeout=t)).status
    composed = link.composition(discharge=True, timeout=t)
    link.status = step("2. Sender || Channel || Receiver refines Functional", "valid",
                       lambda: refines(composed, functional, timeout=t)).status
    step("   Sender || Channel || Receiver refines Integrity", "valid",
         lambda: refines(composed, integrity, timeout=t))

    whole = rtl("esc_link", "esc_sender.v", "esc_channel.v", "esc_receiver.v", "esc_link.v")
    step("3. The whole RTL implements Functional", "valid",
         lambda: is_implementation(whole, functional, timeout=t))
    step("   The whole RTL implements Integrity", "valid",
         lambda: is_implementation(whole, integrity, timeout=t))

    rest = channel.compose(receiver, name="Rest", discharge=True, timeout=t)
    slot = functional.divide(rest, name="SenderSlot", discharge=True, timeout=t)
    step("4. Sender refines SenderSlot = Functional / (Channel || Receiver)", "valid",
         lambda: refines(sender, slot, timeout=t))

    fast = rtl("esc_sender_fast", "esc_sender_fast.v")
    step("5. The RTL of the fast sender implements Sender", "invalid",
         lambda: is_implementation(fast, sender, timeout=t), show=True)
    whole_fast = rtl("esc_link_fast", "esc_sender_fast.v", "esc_channel.v", "esc_receiver.v",
                     "esc_link_fast.v")
    step("   The whole RTL with the fast sender implements Functional", "invalid",
         lambda: is_implementation(whole_fast, functional, timeout=t), show=True)

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    # Functional and the receiver are drawn open: the requirement, and the
    # contract and the state machine (4 states) of the receiver. The sender
    # (23 states) stays closed; the channel has no registers.
    page = viz.save(viz.diagram(link, title="Escalation link",
                                open=[functional, link.components[2]]),
                    os.path.join(HERE, "out", "escalation.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
