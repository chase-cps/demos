## Circuit buffer swap: a smaller buffer in its place

**The question.** A buffer of a circuit is replaced by a smaller one, whose
contract does not refine the old one. Can it take its place, and what must
any buffer in that place satisfy?

<p align="center">
  <img src="diagram-system.png" alt="The system: a producer, the buffer, and a consumer, with a ready/valid handshake">
  <br>
  <em>The system: a producer, the buffer, and a consumer, with a ready/valid handshake.</em>
</p>

A producer sends data to a consumer through a buffer, with a ready/valid
handshake: the producer offers a value (`v_i`) and the buffer takes it when
it is ready (`ready_o`); the buffer offers a value (`v_o`) and the consumer
takes it (`yumi_i`). The buffer is `bsg_two_fifo` of BaseJump STL, a FIFO
of two entries; the demo replaces it with `bsg_one_fifo`, a FIFO of one
entry. The contracts are written in SystemVerilog Assertions: every offer
is taken sooner or later, and what the buffer offers stays until it is
taken. The RTL is that of BaseJump STL.

### The steps

**Step 1. The old system.** The composition of _Producer_, _TwoFifo_, and
_Consumer_ refines _System_, and the RTL of `bsg_two_fifo` implements
_TwoFifo_ (the diagram at the top).

**Step 2. The new buffer against the old one.** _OneFifo_ does not refine
_TwoFifo_: with a value in, it takes no other. Its contract alone does not
say that it can take the place.

<p align="center">
  <img src="diagram-1.png" alt="Step 2: OneFifo does not refine TwoFifo">
  <br>
  <em>Step 2: OneFifo does not refine TwoFifo.</em>
</p>

**Step 3. What the place of the buffer needs.** The quotient Slot = System /
(Producer ∥ Consumer), drawn as a dashed box, is the weakest contract with
which the system meets its requirements. Any buffer that refines it can
take the place, and _OneFifo_ does: _Slot_ may assume what the consumer
guarantees, that an offer is taken sooner or later, so a buffer of one
entry is enough.

<p align="center">
  <img src="diagram-2.png" alt="Step 3: OneFifo refines Slot, the contract of the place">
  <br>
  <em>Step 3: OneFifo refines Slot, the contract of the place.</em>
</p>

**Step 4. On the RTL.** The RTL of `bsg_one_fifo` implements _Slot_: Yosys
reads the RTL and nuXmv checks it. (M ⊨ C in the diagrams is the check of
each RTL against the contract of its box.)

### Content of the directory
The directory of the demo contains:
- `sva/`: the contracts, one module per contract, whose ports give the
  inputs and the outputs: the producer (`producer.sv`), the consumer
  (`consumer.sv`), the two buffers (`two_fifo.sv`, `one_fifo.sv`), and the
  requirements of the system (`system.sv`);
- `rtl/`: the RTL of the two buffers, from BaseJump STL, under the Solderpad
  Hardware License (see `rtl/README.md`);
- `bufferswap.py`: the steps of the replacement with the CHASE Python
  package;
- `out/slot.sv`: the contract of the place of the buffer as SVA, written by
  `bufferswap.py`;
- `out/bufferswap.html`: the diagram, written by `bufferswap.py`;
- `jasper/run.tcl`: the check of `out/slot.sv` on the RTL of `bsg_one_fifo`
  with Jasper.

### Python Flow
The script needs the CHASE Python package with the RTL reader, version
0.5.0, and nuXmv. From the directory of the demo:

```
$> pip install "chase-cps[rtl]"
$> chase-cps install nuxmv --accept-license
$> python3 bufferswap.py
```

The script prints the result of each step and writes the diagrams above in
`out/bufferswap.html`, a page to open in a browser: a click on a name opens
or closes the contract. It also writes _Slot_ as SVA in `out/slot.sv`;
with Jasper (a commercial tool, optional here), `jasper/run.tcl` proves it
on the RTL as well.

With `--expect` the script exits with code 1 when a result is not the
expected one.

### Jasper
`jasper/run.tcl` proves the guarantees of `out/slot.sv` on the RTL of
`bsg_one_fifo`:

`$> jg -fpv -batch -tcl jasper/run.tcl`

The three guarantees of _Slot_ are proven.
