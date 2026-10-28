"""Buffer swap: replacing a block of a circuit.

A producer sends data to a consumer through a buffer, with a ready/valid
handshake. The buffer is bsg_two_fifo of BaseJump STL, a FIFO of two
entries; it is replaced by bsg_one_fifo, a FIFO of one entry, which is
smaller. The contracts are written in SystemVerilog Assertions (sva/), and
the RTL is in rtl/. This script follows the replacement with the CHASE
Python package (pip install chase-cps):

  1. The producer, the two-entry FIFO, and the consumer, composed with
     discharge, refine the requirements of the system.
  2. The one-entry FIFO does not refine the two-entry one: with one value in,
     it does not take another. It cannot replace it on the strength of its
     contract alone.
  3. The quotient of the system by the producer and the consumer is the
     contract of the place of the buffer: the weakest one with which the
     system meets its requirements. With discharge it keeps the terms: it
     assumes the guarantees of the producer and of the consumer, and
     guarantees the requirements of the system. The one-entry FIFO refines
     it, so it can replace the two-entry one, and the new system refines the
     requirements.
  4. That contract is written as SVA, to check the RTL of a buffer
     (out/slot.sv, bound to bsg_one_fifo), and the RTL of both FIFOs is
     checked against the contracts with Yosys and nuXmv.

    python bufferswap.py
    python bufferswap.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv; step 4 also needs Yosys (pip install chase-cps[rtl]),
and is skipped without it. jasper/run.tcl checks out/slot.sv on the RTL with
Jasper.
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from chase_cps import Model, implements, ltl, parse_sva, refines, to_sva
from chase_cps.rtl import yosys

HERE = os.path.dirname(os.path.abspath(__file__))
RTL = os.path.join(HERE, "rtl")
NAMES = {"producer": "Producer", "consumer": "Consumer", "two_fifo": "TwoFifo",
         "one_fifo": "OneFifo", "system": "System"}


def read(name: str):
    """The contract of sva/<name>.sv, with the labels of its properties."""
    with open(os.path.join(HERE, "sva", f"{name}.sv")) as f:
        r = parse_sva(f.read(), name=NAMES[name])
    assert not r.skipped, r.skipped
    return r.contract


def trace(result, signals=("v_i", "ready_o", "v_o", "yumi_i")) -> str:
    """The steps of a counterexample, one line per step."""
    t = result.trace
    lines = []
    for i, state in enumerate(t.prefix + t.loop):
        loop = "  <- loop" if t.loop and i == len(t.prefix) else ""
        lines.append(f"      {i}: " + " ".join(f"{s}={int(bool(state.get(s)))}"
                                              for s in signals) + loop)
    return "\n".join(lines)


def fifo(name: str) -> Model:
    """The RTL of bsg_one_fifo or bsg_two_fifo, with 4-bit data."""
    files = ["bsg_defines.sv", "bsg_dff_reset.sv", "bsg_dff_en.sv"]
    if name == "bsg_two_fifo":
        files += ["bsg_mem_1r1w_synth.sv", "bsg_mem_1r1w.sv"]
    files.append(f"{name}.sv")
    ready = {"bsg_one_fifo": "ready_and_o", "bsg_two_fifo": "ready_param_o"}[name]
    return Model.from_rtl([os.path.join(RTL, f) for f in files], name,
                          parameters={"width_p": 4}, reset="reset_i",
                          names={ready: "ready_o"},
                          defines={"BSG_HIDE_FROM_SYNTHESIS": 1, "XCELIUM": 1})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect", action="store_true",
                        help="exit with code 1 when a result is not the expected one")
    args = parser.parse_args()
    wrong = []

    def step(title, expected, run):
        start = time.monotonic()
        status, text = run()
        seconds = time.monotonic() - start
        mark = "" if status == expected else f"   (expected {expected})"
        print(f"\n{title}: {status} [{seconds:.1f} s]{mark}")
        if text:
            print(text)
        if status != expected:
            wrong.append(title)

    c = {name: read(name) for name in NAMES}
    producer, consumer, system = c["producer"], c["consumer"], c["system"]
    two, one = c["two_fifo"], c["one_fifo"]

    def old_system():
        s = producer.compose(two, discharge=True).compose(consumer, discharge=True)
        r = refines(s, system)
        return r.status, ("   assumptions left after discharge: "
                          + (", ".join(ltl.to_str(f) for f in s.assumptions) or "none"))
    step("1. Producer, TwoFifo, Consumer refine System", "valid", old_system)

    def swap():
        r = refines(one, two)
        part = getattr(r, r.failed) if r.failed else None
        text = f"   the {r.failed} fail; a counterexample:\n" + trace(part) if part is not None else ""
        return r.status, text
    step("2. OneFifo refines TwoFifo", "invalid", swap)

    # the quotient, with its terms: the guarantees of the neighbours are
    # assumed, and the guarantees of the system are guaranteed
    slot = system.divide(producer.compose(consumer), name="Slot", discharge=True)

    def quotient():
        r = refines(one, slot)
        return r.status, ("   Slot = System / (Producer, Consumer)"
                          "\n   assume: " + "; ".join(ltl.to_str(f) for f in slot.assumptions)
                          + "\n   guarantee: " + "; ".join(ltl.to_str(f) for f in slot.guarantees))
    step("3. OneFifo refines Slot", "valid", quotient)

    def new_system():
        s = producer.compose(one, discharge=True).compose(consumer, discharge=True)
        return refines(s, system).status, ""
    step("   Producer, OneFifo, Consumer refine System", "valid", new_system)

    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    out = os.path.join(HERE, "out", "slot.sv")
    with open(out, "w") as f:
        f.write(to_sva(slot, clock="clk_i", reset="reset_i", bind="bsg_one_fifo",
                       names={"ready_o": "ready_and_o"}))
    print(f"\n4. Slot as SVA, bound to bsg_one_fifo: {os.path.relpath(out, HERE)}")

    if yosys() is None:
        print("   the RTL checks need Yosys (pip install chase-cps[rtl]): skipped")
    else:
        def rtl_check(model, contract):
            return lambda: (implements(model, contract).status, "")
        one_rtl, two_rtl = fifo("bsg_one_fifo"), fifo("bsg_two_fifo")
        step("   the RTL of bsg_two_fifo implements TwoFifo", "valid", rtl_check(two_rtl, two))
        step("   the RTL of bsg_one_fifo implements OneFifo", "valid", rtl_check(one_rtl, one))
        step("   the RTL of bsg_one_fifo implements Slot", "valid", rtl_check(one_rtl, slot))
        step("   the RTL of bsg_one_fifo implements TwoFifo", "invalid", rtl_check(one_rtl, two))

    if wrong:
        print("\nNot the expected result: " + "; ".join(wrong))
    return 1 if args.expect and wrong else 0


if __name__ == "__main__":
    sys.exit(main())
