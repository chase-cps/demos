## Bus arbiter: two viewpoints that cannot be merged, and the assumption that fixes them

**The question.** Two teams wrote two viewpoints of the same arbiter of the
AMBA AHB bus: one on how the bus is given to the masters, one on how a
master locks it. Is there an arbiter that meets both, and what must it
assume of the masters?

**What it shows.**
- SystemVerilog Assertions as contracts: the two viewpoints are read from
  `sva/`, with the number of each requirement as the label of its assertion.
- Merging (•): the two viewpoints of one component are put together as one
  contract.
- Realizability (slugs, GR(1)): each viewpoint is realizable; their merge is
  not.
- Unrealizable core: 5 of the 7 guarantees of the merge (GR1, GR2, GR3.2,
  LK1, LK2.1), found in under a second, which point to the missing
  assumption LA2.
- Synthesis: with LA2, slugs synthesizes a controller of 81 states.
- Export: the merge is written back as SVA (`out/arbiter.sv`).
- Implementation (nuXmv): the controller implements the merge (M ⊨ C).

<p align="center">
  <img src="images/overview-arbiter.png" alt="The page of the demo: Arbiter, the merge of Grant and Lock, realizable; the merge without LA2, unrealizable, with its core in red; and the synthesized controller">
  <br>
  <em>The page of the demo: the merge with LA2 (R green), the merge without it (R red, its core in red), and the controller (M ⊨ C).</em>
</p>

The arbiter gives the bus to one of two masters. The requirements are
simplified from Bloem et al., "Specify, Compile, Run: Hardware from PSL"
(COCV 2007), and written in SystemVerilog Assertions. The variables are:

- `hbusreq`: a master asks for the bus;
- `hlock`: a master asks for a locked access;
- `hgrant`: the arbiter grants the bus;
- `hmastlock`: the bus is locked.

The requirements are written as two viewpoints:

- _Grant_ gives the bus to master 1 at the start (GR1) and to exactly one
  master (GR2), and no master waits forever (GR3.1, GR3.2).
- _Lock_ locks the bus for a master that asks for a locked access (LK1),
  and keeps it while that master asks (LK2.1, LK2.2). It assumes that a
  master that asks for a locked access also asks for the bus (LA1.1,
  LA1.2), and that a master that has locked the bus stops asking for it
  sooner or later (LA2).

The two viewpoints are put together by merging (•), the operation for
viewpoints of one component.

### The steps

**Step 1. Each viewpoint.** _Grant_ and _Lock_ are each realizable.

<p align="center">
  <img src="images/step1-viewpoints.png" alt="Step 1: Grant and Lock, open inside Arbiter, each realizable">
  <br>
  <em>Step 1: Grant and Lock, each realizable (R).</em>
</p>

**Step 2. The merge without LA2.** Without LA2, the merge is unrealizable.
When master 1 locks the bus and keeps asking for it, _Lock_ says that
master 1 keeps the bus (LK2.1), and _Grant_ says that master 2 does not
wait forever (GR3.2). The core is these two, with GR1, GR2, and LK1, which
make the conflict possible.

<p align="center">
  <img src="images/step2-merge-core.png" alt="Step 2: the merge without LA2 is unrealizable; the core in red, and the panel of the check">
  <br>
  <em>Step 2: the merge without LA2 is unrealizable; the terms of the core are red.</em>
</p>

**Step 3. What the arbiter must assume.** The core points to the missing
assumption: a master that has locked the bus stops asking for it sooner or
later (LA2). With LA2 in _Lock_, the merge _Arbiter_ (3 assumptions, 7
guarantees) is realizable, and slugs synthesizes a controller of 81
states. _Arbiter_ is also written as SVA (`out/arbiter.sv`).

<p align="center">
  <img src="images/step3-arbiter.png" alt="Step 3: Arbiter, the merge with LA2, open: its assumptions and guarantees, realizable">
  <br>
  <em>Step 3: Arbiter, the merge with LA2, is realizable.</em>
</p>

**Step 4. The controller.** The synthesized controller, read as a state
machine, implements _Arbiter_ (M ⊨ C).

<p align="center">
  <img src="images/step4-controller.png" alt="Step 4: Arbiter and the synthesized controller, which implements it">
  <br>
  <em>Step 4: the controller implements Arbiter (M ⊨ C).</em>
</p>

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements, numbered;
- `sva/`: the two viewpoints in SystemVerilog Assertions, one module each,
  whose ports give the inputs and the outputs: _Grant_ (`grant.sv`) and
  _Lock_ (`lock.sv`). The label of each assertion is the number of the
  requirement;
- `sva/*.results.json`: the results kept by `chase-cps view --check` on
  each file;
- `ahb.py`: the steps with the CHASE Python package;
- `out/arbiter.sv`: the merge of the viewpoints as SVA, written by
  `ahb.py`;
- `out/arbiter.html`: the diagrams above, written by `ahb.py`.

### Run it

```
pip install chase-cps                       # version 0.5.0 or later
chase-cps install nuxmv --accept-license
chase-cps install slugs
python ahb.py --expect
chase-cps view sva/lock.sv --check --realizable -o out/lock-view.html
```

The script prints the result of each step and writes `out/arbiter.html`, a
page to open in a browser: a click on a name opens or closes the contract,
a click on a red tag shows or hides its core, and the button of the
problems lists the check that fails. With `--expect` the script exits with
code 1 when a result is not the expected one. `chase-cps view` draws one
viewpoint on its own, with its checks.
