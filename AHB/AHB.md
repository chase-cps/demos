## AHB: two viewpoints of an arbiter

The question: two teams wrote two viewpoints of the same arbiter of the
AMBA AHB bus, one on how the bus is given to the masters, one on how a
master locks it. Is there an arbiter that meets both, and what must it
assume of the masters?

The arbiter gives the bus to one of two masters, and a master can lock the
bus. The requirements are simplified from those of R. Bloem et al.,
"Specify, Compile, Run: Hardware from PSL" (COCV 2007), a case study of
GR(1) synthesis: two masters, no bursts, and no HREADY. The viewpoints are
put together by merging, the operation for viewpoints of one component.

![The arbiter: the merge of the two viewpoints, Grant and Lock, over the requests and the locks of two masters](diagram-system.png)
_The arbiter: the merge of the two viewpoints, Grant and Lock, over the requests and the locks of two masters._

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements, numbered;
- `sva/`: the two viewpoints in SystemVerilog Assertions, one module each,
  whose ports give the inputs and the outputs: _Grant_ (`grant.sv`) and
  _Lock_ (`lock.sv`). The label of each assertion is the number of the
  requirement;
- `ahb.py`: the steps with the CHASE Python package;
- `out/arbiter.sv`: the merge of the viewpoints as SVA, written by
  `ahb.py`;
- `out/arbiter.html`: the diagram, written by `ahb.py`.

### The contracts
- _Grant_ gives the bus to exactly one master, master 1 at the start, and no
  master waits forever (GR1, GR2, GR3.1, GR3.2). It assumes nothing.
- _Lock_: a master that has locked the bus keeps it while it asks for it
  (LK1, LK2.1, LK2.2). It assumes that a master asks for the bus when it
  asks for a locked access (LA1.1, LA1.2), and that a master that has
  locked the bus stops asking for it sooner or later (LA2).

### Python Flow
The script needs the CHASE Python package (`pip install chase-cps`, version
0.5.0), slugs, and nuXmv or NuSMV:

`$> python3 ahb.py`

It prints the result of each step:
1. _Grant_ and _Lock_ are each realizable.
2. The merge of _Grant_ and _Lock_ without LA2 is unrealizable. Its
   unrealizable core is GR1, GR2, GR3.2, LK1, LK2.1: master 1 locks the bus
   and keeps asking for it, _Lock_ says that it keeps the bus (LK2.1), and
   _Grant_ says that master 2 does not wait forever (GR3.2).
3. With LA2, the merge is realizable. The merge with discharge keeps the
   terms of both viewpoints, (A1 & A2, G1 & G2), the same contract as the
   closed form (A1 & A2, (G1 & G2) | !(A1 & A2)). This is _Arbiter_. Slugs
   synthesizes a controller, and _Arbiter_ is written as SVA.
4. The controller implements _Arbiter_.

So the answer is: the viewpoints have an arbiter together only if the
masters release a locked bus sooner or later (LA2).

With `--expect` the script exits with code 1 when a result is not the
expected one.

`out/arbiter.html` draws _Arbiter_ with its two viewpoints, the merge
without LA2 drawn open on its unrealizable core, and the controller. The
page opens in a browser; a click on a name opens its contract, and a click
on a red tag shows its core.

![Grant and Lock merged into Arbiter: each viewpoint and the merge are realizable (R)](diagram-1.png)
_Grant and Lock merged into Arbiter: each viewpoint and the merge are realizable (R)._

![Without LA2 the merge is unrealizable: the core, on a red ground, is GR1, GR2, GR3.2, LK1, and LK2.1 (master 1 can keep the lock, and master 2 waits forever)](diagram-2.png)
_Without LA2 the merge is unrealizable: the core, on a red ground, is GR1, GR2, GR3.2, LK1, and LK2.1 (master 1 can keep the lock, and master 2 waits forever)._

![The synthesized controller (81 states) implements Arbiter (M ⊨ C)](diagram-3.png)
_The synthesized controller (81 states) implements Arbiter (M ⊨ C)._
