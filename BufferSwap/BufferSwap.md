## Circuit buffer swap: the new buffer fails the old contract, but the quotient shows it fits

**The question.** A buffer of a circuit is replaced by a smaller one,
whose contract does not refine the old one. Can it take its place, and
what must any buffer in that place satisfy?

**The result.**
- Refinement: the new buffer does not refine the old one; the
  counterexample has 4 steps.
- Quotient (the weakest contract a missing part must meet): _Slot_, the
  contract of the place of the buffer, has 3 assumptions and 3
  guarantees; the new buffer refines it.
- RTL against contracts (Yosys and nuXmv): the RTL of `bsg_one_fifo`
  implements _OneFifo_ and _Slot_, not _TwoFifo_.

<p align="center">
  <img src="images/overview-buffer-swap.png" alt="The old system (⪯ green), OneFifo against TwoFifo (⪯ red), and OneFifo in Slot (⪯ green)" width="839">
  <br>
  <em>The old system, OneFifo against TwoFifo, and OneFifo in Slot, the place of the buffer.</em>
</p>

A producer sends data to a consumer through a buffer, with a ready/valid
handshake. The buffer is `bsg_two_fifo` of BaseJump STL, a FIFO of two
entries; the demo replaces it with `bsg_one_fifo`, of one entry. The
contracts are written in SystemVerilog Assertions.

### The steps

**Step 1. The old system.** _Producer_, _TwoFifo_, and _Consumer_,
composed, refine _Pipeline_, and the RTL of `bsg_two_fifo` implements
_TwoFifo_.

<p align="center">
  <img src="images/step1-old-system.png" alt="Step 1: Producer, TwoFifo, and Consumer refine Pipeline; TwoFifo M ⊨ C green" width="834">
  <br>
  <em>Step 1: the old system refines Pipeline; the RTL implements TwoFifo.</em>
</p>

**Step 2. The new buffer against the old one.** _OneFifo_ does not refine
_TwoFifo_. In the counterexample of 4 steps, the empty buffer takes a
value at step 1 and is not ready at step 2, where _TwoFifo_ guarantees
that it is.

<p align="center">
  <img src="images/step2-onefifo-counterexample.png" alt="Step 2: OneFifo does not refine TwoFifo; the counterexample in the panel, the broken guarantee in red">
  <br>
  <em>Step 2: OneFifo does not refine TwoFifo; the guarantee it breaks in red.</em>
</p>

**Step 3. What the place needs.** The quotient Slot = Pipeline / (Producer
⊗ Consumer), the dashed box, has 3 assumptions and 3 guarantees. _Slot_
may assume what the consumer guarantees, that an offer is taken sooner or
later, so one entry is enough: _OneFifo_ refines _Slot_, and the system
with _OneFifo_ refines _Pipeline_.

<p align="center">
  <img src="images/step3-slot.png" alt="Step 3: Slot, the quotient, with OneFifo inside; the tag ⪯ green" width="823">
  <br>
  <em>Step 3: OneFifo refines Slot, the contract of the place.</em>
</p>

**Step 4. On the RTL.** Yosys reads the RTL, and nuXmv checks it: the RTL
of `bsg_one_fifo` implements _OneFifo_ and _Slot_, and does not implement
_TwoFifo_. The script also writes _Slot_ as SVA (`out/slot.sv`), for
Jasper (`jasper/run.tcl`, not run by the script).

<p align="center">
  <img src="images/step4-rtl-onefifo.png" alt="Step 4: the RTL of bsg_one_fifo in Slot, M ⊨ C green" width="463">
  <br>
  <em>Step 4: the RTL of bsg_one_fifo implements its contract (M ⊨ C).</em>
</p>

### Run it

```
pip install "chase-cps[rtl]"                # with Yosys
chase-cps install nuxmv --accept-license
python bufferswap.py --expect
```

### Content of the directory
- `sva/`: the five contracts, with their `*.results.json`;
- `rtl/`: the two buffers, from BaseJump STL (Solderpad license);
- `bufferswap.py`: the steps with the CHASE Python package;
- `out/`: the diagrams and `slot.sv`, written by `bufferswap.py`;
- `jasper/run.tcl`: the check of `out/slot.sv` with Jasper.
