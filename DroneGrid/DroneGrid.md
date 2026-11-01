## Fire-suppression drones in C: a collision found and fixed on the contracts, then checked one function at a time

**The system.** Two drones of a fire-suppression mission move on a
10 x 10 grid, one cell per step. They come from the multi-drone fire
suppression of ContrACT (Xiao et al., MEMOCODE 2026), whose software is
written as reactions, pieces of code run at each step. Each step has five
parts, each with a contract and a C function:

- _Plan0_ and _Plan1_ (`plan.c`): each drone at `(x, y)` asks for a move
  `r` toward its target `(tx, ty)`: 0 stay, 1 right, 2 left, 3 down, 4 up;
- _Coordinator_ (`coordinator.c`, function `grant`): grants the moves
  `g`, refusing two moves into the same cell or a swap;
- _Move0_ and _Move1_ (`move.c`): each drone moves as granted, to
  `(nx, ny)`.

The requirement _Fleet_: two drones in different cells are, after the
step, in different cells, and do not cross. The contracts are on
integers, checked by z3; the C functions by ESBMC.

**The question.** Can two drones end in the same cell? And can each C
function be checked alone, without checking the whole program? A whole
program check grows with every function; one function at a time does not.

<p align="center">
  <img src="images/system.png" alt="Plan0, Plan1, Coordinator, Move0, and Move1 inside Fleet, each with its C code" width="870">
  <br>
  <em>The system: one step of the two drones inside the requirement Fleet; each part has its C function.</em>
</p>

### The steps

**Step 1. The contracts do not refine the requirement.** The five parts
composed do not refine _Fleet_ (some behavior of the parts breaks it).
In the counterexample, drone 0 is at its target (1, 0) and stays, and
drone 1 at (2, 0) moves left into its cell: the coordinator compares
only drones that both move. The script finds the same failure for a swap.

<p align="center">
  <img src="images/step1-fleet-does-not-refine.png" alt="Step 1: the tag ⪯ of Fleet red; the counterexample on the ports, the broken term in red">
  <br>
  <em>Step 1: the parts with <code>Coordinator</code> do not refine <code>Fleet</code>.</em>
</p>

**Step 2. The fix.** No number can be tuned: the rule must change.
CHASE computes the quotient of _Fleet_ by the other four parts: the
weakest contract the coordinator must meet so that the step meets
_Fleet_ (see [the contract algebra](https://chase-cps.github.io/contracts/algebra/)).
_Coordinator_ does not refine it. _CoordinatorSafe_, which grants a move
only into a cell that is free after the step, does, and the parts with
it refine _Fleet_.

<p align="center">
  <img src="images/step3-coordinator-safe-refines.png" alt="Step 2: Fleet_safe, the parts with CoordinatorSafe, the tag ⪯ green" width="870">
  <br>
  <em>Step 2: the parts with <code>CoordinatorSafe</code> refine <code>Fleet</code>.</em>
</p>

**Step 3. The code.** ESBMC checks each function against its contract
(the tag M ⊨ C), in about 0.1 s each. The five functions of the step
(`plan0`, `plan1`, `grant`, `move0`, `move1`) implement theirs. `grant`
does not implement _CoordinatorSafe_; `grant_safe` does. With steps 2
and 3, the C code with `grant_safe` keeps the drones apart, and the
whole program is never checked at once.

<p align="center">
  <img src="images/step4-grant-safe-code.png" alt="Step 3: CoordinatorSafe selected, M ⊨ C green; the section Code open on grant_safe">
  <br>
  <em>Step 3: <code>grant_safe</code> implements <code>CoordinatorSafe</code>.</em>
</p>

The tags of the pictures are explained on the page
[Diagrams](https://chase-cps.github.io/interfaces/diagrams/#what-is-drawn).

### Run it

```
pip install "chase-cps[z3]"      # and ESBMC or CBMC
python dronegrid.py --expect
```

### Content of the directory
- `plan.c`, `coordinator.c`, `move.c`: the reactions in C;
- `dronegrid.ltl`: the contracts of the functions and the requirement;
- `dronegrid.py`: the steps with the CHASE Python package;
- `dronegrid.results.json`, `out/dronegrid.html`: the results and the
  diagram; `out/dronegrid-system.html`: the system, with no check.
