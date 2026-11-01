## Room thermostat: repairing the threshold, then checking its C code

**The question.** A thermostat heats a room while the temperature is
below a threshold, and the room must stay at most 75 degrees. Which
threshold works, and does the C code of the thermostat implement it?

**The result.**
- Counterexample over time: the room heats to 77 degrees. The worst case
  of `T <= 75` (its robustness: the margin by which it holds) is -2.
- Repair of the threshold: `theta = 74` instead of 76, optimal; the worst
  case is then 0. If the requirement may change instead: `tmax = 77`.
- C code: checked by ESBMC one call at a time, it implements the
  repaired thermostat, not the original one.
- Between the samples: with 20 s a step, `theta = 74` is not shown to
  hold at every instant; `theta = 71` is.

<p align="center">
  <img src="images/before-and-after-repair.png" alt="Before the repair (red) and after it (green)" width="650">
  <br>
  <em>Before the repair (red) and after it (green): the thermostat with its C code.</em>
</p>

The contracts in `heater.ltl` cover 10 steps, in signal temporal logic in
discrete time, so z3 checks them (the room and the thermostat run one
step more, for step 5). _Room_ starts at 60 degrees and, at
each step, gains the heat `u` and loses 1. _Thermostat_ heats (`u = 3`)
while `T < theta`. _Comfort_ requires `T <= tmax` at every step.

### The steps

**Step 1. The thermostat overshoots.** _Room_ and _Thermostat_ composed
do not refine _Comfort_. The room heats to 76, cools to 75, and heats
again to 77 at step 10. The worst case of `T <= 75` is -2: 2 degrees too
hot.

<p align="center">
  <img src="images/overshoot-counterexample.png" alt="The counterexample step by step, T from 60 to 77">
  <br>
  <em>Step 1: the counterexample; the slider puts step 10 on the ports.</em>
</p>

**Step 2. Repair the threshold.** `repair` changes `theta` as little as
possible: `theta = 74`, a change of 2, optimal. The worst case is then 0:
the room reaches 75 and no more.

<p align="center">
  <img src="images/repair-theta.png" alt="Find repairs: theta 76 to 74, optimal, change 2">
  <br>
  <em>Step 2: theta 76 to 74, optimal.</em>
</p>

**Step 3. Or repair the requirement.** Changing `tmax` instead gives 77:
the requirement accepts the overshoot. In the viewer, `tmax` belongs to
the requirement and is picked only by hand.

<p align="center">
  <img src="images/repair-theta-or-tmax.png" alt="Find repairs with theta and tmax picked: two repairs, both optimal">
  <br>
  <em>Step 3: both constants picked, two repairs.</em>
</p>

**Step 4. The code.** M ⊨ C checks that the code implements the
contract. Each step of _Thermostat_ is one call, so ESBMC checks one call
against one step of the formula. With `theta = 76` it fails: the call
with `T = 75` returns 0 where the contract asks for 3. `repair` finds
the threshold that the code implements: 74.

<p align="center">
  <img src="images/code-repair-theta.png" alt="The panel of M ⊨ C: counterexample T = 75, u = 0, and the repair of theta">
  <br>
  <em>Step 4: M ⊨ C fails on T = 75.</em>
</p>

**Step 5. Between the samples.** A step is a sample taken every 20 s, and
the temperature changes at most 0.1 degree per second. Between two
samples it can then move by 2 degrees, so CHASE checks `T + 2 < 75` at
the samples (Fainekos and Pappas): if that holds, `T <= 75` holds at
every instant. With `theta = 74` the samples reach 75: the answer is
unknown, not a counterexample, since the margin is a sufficient
condition. With `theta = 71` the samples stay at 72 or below, and the
refinement holds in continuous time.

```
$> chase-cps check heater.ltl --period 20 --lipschitz T=0.1 theta=0 tmax=0 --refines Room+Thermostat Comfort
```

### Run it

```
pip install "chase-cps[z3]"      # and ESBMC or CBMC for step 4
python heater.py --expect
chase-cps view heater.ltl --check --serve
```

### Content of the directory
- `heater.ltl`: the three contracts;
- `heater.c`: the thermostat in C, called once per step;
- `heater.py`: the steps with the CHASE Python package;
- `heater.results.json`: the results of `chase-cps view --check`;
- `out/heater.html`: the diagram before and after the repair.
