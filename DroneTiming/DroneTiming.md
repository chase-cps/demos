## Fire-suppression drone timing: the margins, as a linear program

**The question.** Three drones put out fires; each must move within
400 ms of its timer. Is the bound met, by how much, and how much slower
may a reaction be, or the rest of the mission, before it is not?

**The result.**
- The bound holds. The worst case of a drone, found by one optimization,
  is 280 ms: the least bound that holds.
- Repair as optimization: the planner may take up to `x_plan = 192` ms,
  and the mission may delay the drones by up to `offset = 179` ms. Each
  is optimal, and checked by the refinement.
- z3 checks and optimizes these linear constraints over the reals, in
  place of the Gurobi MILP (mixed-integer linear program) of the paper.

<p align="center">
  <img src="images/mission-and-drone.png" alt="The mission subgraph and the pipeline of a drone inside their requirements">
  <br>
  <em>The mission inside Mission, and a drone inside Available at its least bound.</em>
</p>

This is the multi-drone fire suppression of ContrACT (Xiao, Lutz,
Castillo-Effen, Nuzzo, MEMOCODE 2026). `dronetiming.ltl` has the timing
contracts of each reaction. _Mission_ bounds the delay that the fire
simulation causes to the drone timer. _Available_: given that delay (`offset`), the drone
moves at most `lam` after its timestamp. The three drones run the same
pipeline and do not wait for each other, so one pipeline gives the bound
of each.

### The steps

**Step 1. The mission.** The mission subgraph (the timer, the fire
spreading, the coordinator reading the fire) refines _Mission_. Its worst
case is 59 ms: the offset of the drones.

<p align="center">
  <img src="images/mission-refines-mission.png" alt="The mission subgraph inside Mission, the refinement green">
  <br>
  <em>Step 1: the mission subgraph inside Mission (y0 = 59): ⪯ green.</em>
</p>

**Step 2. The bound holds.** The pipeline of a drone refines _Available_
with `lam = 400`. One optimization over its behaviors gives the worst
case, 280 ms: 59 ms of offset, 55 ms for the drone to report its cell,
33 ms for the coordinator to assign a target and 8 ms for the controller
to take it (the planner waits for it), 72 ms to plan, and 53 ms to send
the move.

<p align="center">
  <img src="images/drone-refines-available.png" alt="The pipeline of a drone inside Available, lam = 400, the refinement green">
  <br>
  <em>Step 2: the pipeline of a drone inside Available (lam = 400): ⪯ green.</em>
</p>

**Step 3. The margins, by repair.** Repair is here an optimization over
one named constant. The least bound that holds is `lam = 280`. The
planner may take up to `x_plan = 192` ms, and the mission may delay the
drones by up to `offset = 179` ms: both 120 ms more than now, the slack
of step 2.

<p align="center">
  <img src="images/drone-least-bound.png" alt="The pipeline inside Available_least, lam = 280, Plan open">
  <br>
  <em>Step 3: at lam = 280 the refinement still holds; Plan open.</em>
</p>

### Run it

```
pip install "chase-cps[z3]"
python dronetiming.py --expect
chase-cps view dronetiming.ltl --check --serve
```

### Content of the directory
- `dronetiming.ltl`: the contracts of the reactions and the requirements;
- `dronetiming.py`: the steps with the CHASE Python package;
- `dronetiming.results.json`: the results of `chase-cps view --check`;
- `out/dronetiming.html`: the diagram of the mission and of a drone at
  its least bound.
