## Fire-suppression drone: climbing to the drop altitude in the wind

**The question.** A drone of the fire-suppression mission climbs to the
altitude where it drops its water, in the updraft of the fire. Does it get
there in time and stay there long enough? When it does not, is it the
controller to change, or the requirement?

**What it shows.**
- Counterexample over time (signal temporal logic over reals, z3): in a
  wind of 1 against it, the drone stays below 18 m, outside the tolerance
  of 2 around 20 m.
- Robustness: the worst case of the requirement is 0.75 in a wind of 0.5
  (it holds, with 0.75 to spare) and -0.5 in a wind of 1 (the drone stays
  2.5 below the drop altitude).
- Repair that proves a change cannot work: no climb rate `vmax` meets the
  requirement (impossible, in 2.7 s).
- Repair of the requirement, each value checked on both sides: the least
  tolerance `eps = 2.5` (2.49 fails), or the strongest wind
  `wmax = 17/21`, about 0.81 (0.82 fails).

<p align="center">
  <img src="images/climb-before-and-after.png" alt="The drone inside Hover in a wind of 1 (red), and with the tolerance of 2.5 (green)">
  <br>
  <em>The drone inside Hover in a wind of 1 (⪯ red), and with the tolerance of 2.5 (green).</em>
</p>

The drone is one of the multi-drone fire suppression (MDFS) of ContrACT
(Xiao, Lutz, Castillo-Effen, Nuzzo, MEMOCODE 2026). `altitude.ltl` has its
contracts in signal temporal logic in discrete time (one step is one period
of the controller):

- `Plant`: the drone starts on the ground, and its altitude changes by its
  climb rate and the wind, `G[0,14] (h' = h + v + w)`.
- `Climb`: the controller climbs at a rate proportional to the error
  `r - h` (gain 0.5), at most `vmax` (3) up or down. `r` is the drop
  altitude, 20.
- `Hover`: the requirement. In a wind of at most `wmax` (1) up or down at
  each step, the drone is within `eps` (2) of `r` from some step of the
  first 10 on, for 5 steps (`F[0,10] G[0,5] (h >= r - eps & h <= r + eps)`),
  and never higher than `r + eps`.

`r`, `vmax`, `eps`, and `wmax` are named constants (θ in the diagram). The
formulas read 16 steps of reals, so z3 checks them.

### The steps

**Step 1. The wind of the fire.** `Plant` and `Climb` composed refine
`Hover` in a wind of 0.5, not in a wind of 1. In the counterexample the
wind pushes the drone down from step 4 on, and it stays below 18 (17.5 at
step 7, 17.97 at step 11). The worst case of the requirement over the
behaviors, its smallest robustness, is 0.75 in a wind of 0.5 (0.75 to
spare) and -0.5 in a wind of 1: the drone stays 2.5 below the drop
altitude.

<p align="center">
  <img src="images/hover-counterexample.png" alt="The panel of the check of Hover: the counterexample, h, w, and v for the first 12 steps, step 7 on the ports (h = 17.5); the first guarantee of Hover in red">
  <br>
  <em>The counterexample in a wind of 1: the drone does not get within 2 of 20 m.</em>
</p>

**Step 2. The controller cannot fix it.** Repair of the climb rate `vmax`
finds no value that works: impossible. Once near the target, the error
goes as e' = e/2 + w: in a wind of 1 against the drone, it tends to 2 and
stays above it, however fast the drone climbs.

<p align="center">
  <img src="images/repair-vmax-impossible.png" alt="Find repairs with vmax picked: no value in [0, 9] works">
  <br>
  <em>Find repairs with vmax picked: no value in [0, 9] works (the script searches 0..10).</em>
</p>

**Step 3. The requirement.** Changing a requirement is for whoever wrote
it; repair says what would work, each value checked on both sides:
- the least tolerance: `eps = 2.5` (2.49 fails);
- or, keeping `eps = 2`, the strongest wind: `wmax = 17/21`, about 0.81
  (0.82 fails). This value has no finite decimal: the viewer shows it, and
  does not write it in the file (its Apply is off).

<p align="center">
  <img src="images/repair-eps-or-wmax.png" alt="Find repairs with eps and wmax picked: eps 2 to 2.5, or wmax 1 to about 0.8095, both optimal">
  <br>
  <em>eps and wmax picked: eps 2 → 2.5, or wmax 1 → ≈ 0.8095 (17/21).</em>
</p>

### Content of the directory
The directory of the demo contains:
- `altitude.ltl`: the contracts of the drone, of its controller, and the
  requirement. The line `# view:` at the top draws the drone inside
  `Hover`;
- `altitude.py`: the steps with the CHASE Python package;
- `altitude.results.json`: the results of `chase-cps view altitude.ltl --check`;
- `out/altitude.html`: the diagram before and after the repair of the
  tolerance, written by `altitude.py`.

### Run it

```
pip install "chase-cps[z3]"
python altitude.py --expect
chase-cps view altitude.ltl --check -o out/altitude-view.html
chase-cps repair altitude.ltl --refines Plant+Climb Hover --param vmax=0..10     # impossible
chase-cps repair altitude.ltl --refines Plant+Climb Hover --param eps=0..10
chase-cps view altitude.ltl --check --serve                   # Find repairs in the page
```
