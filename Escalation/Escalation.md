## OpenTitan security chip: the escalation link proven module by module from its RTL

**The question.** The escalation link of a security chip is made of a
sender, the wires, and a receiver. Does it meet its requirements, and can
we show it by checking each module on its own?

**The result.**
- RTL against contracts (Yosys and nuXmv): the Verilog of each module
  implements its contract, written in SystemVerilog Assertions.
- Composition: the three contracts together refine both requirements,
  _Functional_ and _Integrity_, with no check on the whole design.
- A counterexample on the RTL: a faster sender breaks its contract in 4
  steps; in the whole link, a ping makes the receiver escalate.

<p align="center">
  <img src="images/overview-link.png" alt="The link: Sender and Channel, M ⊨ C green, and the receiver open on the right" width="870">
  <br>
  <em>The link, the composition of the three modules, with its assumptions and guarantees; each module with its RTL (M ⊨ C).</em>
</p>

The link is a small version of the escalation link of OpenTitan. To
escalate (order the receiver to react to an attack), the sender raises a
differential pair: two wires that carry opposite values, so a single wrong
wire makes them equal, which both ends detect. To ping (test that the
receiver is alive), it sends one-cycle pulses; a pulse of two cycles means
an escalation. The requirements follow the assertions of OpenTitan
(`prim_esc_rxtx_assert_fpv`).

### The steps

**Step 1. Each module.** The RTL of the sender, of the channel, and of
the receiver implements its contract. The receiver is drawn open: its
contract and its state machine of 4 states, read from the RTL.

<p align="center">
  <img src="images/step1-modules.png" alt="Step 1: the receiver open, M ⊨ C green, with its contract and its four states" width="870">
  <br>
  <em>Step 1: the receiver implements its contract (M ⊨ C); its state machine of four states.</em>
</p>

**Step 2. The composition.** _Sender_ ⊗ _Channel_ ⊗ _Receiver_ refines
_Functional_ and _Integrity_. The whole RTL, checked directly, meets both
too. The quotient SenderSlot = Functional / (Channel ⊗ Receiver), the
weakest contract any sender must meet in this link, is refined by
_Sender_.
In the diagram, the tag ⪯ of the link is green.

**Step 3. A faster sender.** A sender that pings at every cycle of a ping
request does not implement _Sender_. In the counterexample of 4 steps, the
ping request stays high and so does the pair, which only an escalation
may do. In the whole link, a ping makes the receiver escalate.

<p align="center">
  <img src="images/step5-fast-sender.png" alt="Step 3: the fast sender, M ⊨ C red; the counterexample in the panel, the broken guarantee in red">
  <br>
  <em>Step 3: the fast sender does not implement Sender; the guarantee it breaks in red.</em>
</p>

### Run it

```
pip install "chase-cps[rtl]"                # with Yosys
chase-cps install nuxmv --accept-license
python escalation.py --expect
```

### Content of the directory
- `sva/`: the contracts of the three modules and the two requirements, in
  SystemVerilog Assertions, with their `*.results.json`;
- `rtl/`: the Verilog of the modules, of the link, and of the fast sender
  (`esc_sender_fast.v`, `esc_link_fast.v`);
- `escalation.py`: the steps with the CHASE Python package;
- `out/escalation.html`: the diagrams, written by `escalation.py`.
