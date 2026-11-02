## Room thermostat: repairing the threshold, then checking its C code

**The system.** A thermostat keeps a room warm without overheating it. It
is a small example made for these pages. _Room_ starts at 60 degrees and,
at each step, gains the heat `u` and loses 1. _Thermostat_ heats
(`u = 3`) while the temperature `T` is below a threshold `theta`, here
76; it is also written in C, in `heater.c`. The requirement _Comfort_
asks `T <= tmax` (75 degrees) at every step. The contracts are written in
signal temporal logic in discrete time over the steps 0 to 10 (`G[0,10]`
is "at each of the steps 0 to 10"), so the solver z3 checks them.

**The question.** Does the thermostat keep the room within 75 degrees?
If not, which threshold does, and does the C code implement it? The
designer needs a threshold that works before tuning the code.

<p align="center">
  <img src="images/system.png" alt="Room and Thermostat inside Comfort, with their terms" width="726">
  <br>
  <em>The system: Room and Thermostat (with its C code) inside the requirement Comfort.</em>
</p>

### The steps

**Step 1. The thermostat overshoots.** _Room_ and _Thermostat_ composed
do not refine _Comfort_ (the tag ⪯; refine: every behavior of the parts
meets the requirement). The tag A∧G says that the terms of a contract can
hold together. The counterexample: the room heats to 76, cools to 75,
and heats again to 77 at step 10. CHASE also computes the robustness of
`T <= 75`, the margin by which it holds in the worst case: -2, two
degrees too hot.

<p align="center">
  <img src="images/repair-theta-or-tmax.png" alt="The counterexample, T from 60 to 77, and the two repairs: theta 76 to 74, or tmax 75 to 77">
  <br>
  <em>Steps 1 and 2: the counterexample at the top (step 8, where it fails, on the ports), the two repairs at the bottom; the mouse on the first one shows it on Thermostat.</em>
</p>

**Step 2. Repair.** `repair` changes a named constant (θ in the boxes)
as little as possible so that the check passes, and shows that no smaller change
works. On the thermostat it gives `theta = 74`, a change of 2: the room
then reaches 75 and no more. On the requirement it gives `tmax = 77`:
the requirement accepts the overshoot. In the viewer, `tmax` belongs to
the requirement (the orange chip: a constant of the requirement) and is
picked only by hand.

**Step 3. The code.** Each step of _Thermostat_ is one call of the C
function, so ESBMC checks one call against one step of the formula
(the tag M ⊨ C: the code meets the contract). With `theta = 76` it fails: the call with `T = 75`
returns 0 where the contract asks for 3. `repair` finds the threshold
that the code implements: 74.

<p align="center">
  <img src="images/code-repair-theta.png" alt="The panel of M ⊨ C: counterexample T = 75, u = 0, and the repair of theta">
  <br>
  <em>Step 3: M ⊨ C fails on T = 75; the repair of theta below.</em>
</p>

**Step 4. Between the samples.** A step is a sample taken every 20 s,
and the temperature changes at most 0.1 degree per second (its Lipschitz
constant: a bound on how fast it changes). Between two samples it can
then move by 2 degrees, so CHASE checks `T + 2 < 75` at the samples
(Fainekos and Pappas): if that holds, `T <= 75` holds at every instant.
With `theta = 74` the samples reach 75: the answer is unknown, not a
counterexample, since the margin is only sufficient. With `theta = 71`
the refinement holds in continuous time.

```
$> chase-cps check heater.ltl --period 20 --lipschitz T=0.1 --refines Room+Thermostat Comfort
```

The tags of the pictures are explained on the page
[Diagrams](https://chase-cps.github.io/interfaces/diagrams/#what-is-drawn).

### Run it

```
pip install "chase-cps[z3]"      # and ESBMC or CBMC for step 3
python heater.py --expect
chase-cps view heater.ltl --check --serve
```

### Content of the directory
- `heater.ltl`: the three contracts;
- `heater.c`: the thermostat in C, called once per step;
- `heater.py`: the steps with the CHASE Python package;
- `heater.results.json`: the results of `chase-cps view --check`;
- `out/heater.html`: the diagram before and after the repair;
  `out/heater-system.html`: the system, with no check.
