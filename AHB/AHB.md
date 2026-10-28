## AHB: two viewpoints of an arbiter

The arbiter of the AMBA AHB bus gives the bus to one of two masters, and a
master can lock the bus. The requirements are simplified from those of R.
Bloem et al., "Specify, Compile, Run: Hardware from PSL" (COCV 2007), a case
study of GR(1) synthesis: two masters, no bursts, and no HREADY. They are
written as two viewpoints of the same arbiter. The demo merges the
viewpoints, synthesizes the arbiter, and shows why the conjunction of the
viewpoints is not the arbiter.

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements, numbered;
- `ahb.ltl`: the two viewpoints, _Grant_ and _Lock_. The comment at the end
  of each line is the number of the requirement;
- `ahb.py`: the steps with the CHASE Python package.

### The contracts
- _Grant_ gives the bus to exactly one master, master 1 at the start, and no
  master waits forever (GR3.1, GR3.2). It assumes nothing.
- _Lock_: a master that has locked the bus keeps it while it asks for it
  (LK2.1, LK2.2). It assumes that a master asks for the bus when it asks for
  a locked access (LA1.1, LA1.2), and that a master that has locked the bus
  stops asking for it sooner or later (LA2).

### Python Flow
The script needs the CHASE Python package (`pip install chase-cps`), slugs,
and nuXmv or NuSMV:

`$> python3 ahb.py`

It prints the result of each step:
1. _Grant_ and _Lock_ are each realizable.
2. The merge of the viewpoints, (A1 & A2, (G1 & G2) | !(A1 & A2)), is
   equivalent to _Arbiter_, the contract with the assumptions of _Lock_ and
   the guarantees of both (CHASE checks that each refines the other).
   _Arbiter_ is realizable, and slugs synthesizes a controller.
3. The conjunction of the viewpoints, (A1 | A2, G1 & G2), refines _Arbiter_,
   and _Arbiter_ does not refine it. The conjunction asks for each viewpoint
   on its own: the guarantees of _Grant_ hold even when the assumptions of
   _Lock_ do not, so no master may wait forever even when a master keeps the
   bus locked.
4. The controller implements _Arbiter_, and not the conjunction. The
   counterexample: master 2 locks the bus and never stops asking (LA2 does
   not hold), and master 1 waits forever (GR3.1 does not hold). No arbiter
   implements the conjunction: it cannot tell from the past whether master 2
   will stop asking, so it would have to let master 2 keep the bus (_Lock_,
   when it stops later) and take the bus from it (_Grant_, when it never
   stops).

The conjunction is the weakest contract that refines both viewpoints: a
component that implements it can be used wherever either viewpoint is asked
for. The merge is for viewpoints that describe one component together: each
viewpoint holds under the assumptions of both. The realizability of the conjunction is not checked with slugs: its
assumption, A1 | A2, is not GR(1).

With `--expect` the script exits with code 1 when a result is not the
expected one.
