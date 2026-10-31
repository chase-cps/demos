## DroneAltitude: a drone climbs to its drop altitude in the wind

**The question.** A drone of the fire-suppression mission climbs to the
altitude where it drops its water, in the updraft of the fire. Does it get
there in time and stay there long enough? When it does not, is it the
controller to change, or the requirement?

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

`r`, `vmax`, `eps`, and `wmax` are named constants. The formulas read 16
steps of reals, so z3 checks them.

### The steps

**Step 1. The wind of the fire.** `Plant` and `Climb` composed refine
`Hover` in a wind of 0.5, not in a wind of 1. The worst case of the
requirement over the behaviors, its smallest robustness, is 0.75 in a wind
of 0.5 (0.75 to spare) and -0.5 in a wind of 1: the drone stays 2.5 below
the drop altitude.

**Step 2. The controller cannot fix it.** Repair of the climb rate `vmax`
finds no value that works: impossible. Once near the target, the error
goes as e' = e/2 + w: in a wind of 1 against the drone, it tends to 2 and
stays above it, however fast the drone climbs.

**Step 3. The requirement.** Changing a requirement is for whoever wrote
it; repair says what would work, each value checked on both sides:
- the least tolerance: `eps = 2.5` (2.49 fails);
- or, keeping `eps = 2`, the strongest wind: `wmax = 17/21`, about 0.81
  (0.82 fails). This value has no finite decimal: the diagram shows it, and
  does not write it in the file.

<p align="center">
  <img src="images/climb-before-and-after.png" alt="The drone inside Hover in a wind of 1 (red), and with the tolerance of 2.5 (green)">
  <br>
  <em>The drone inside Hover in a wind of 1 (⪯ red), and with the tolerance of 2.5 (green). Folded again, the requirement reads F[0,10] G[0,5].</em>
</p>

### Content of the directory
The directory of the demo contains:
- `altitude.ltl`: the contracts of the drone, of its controller, and the
  requirement. The line `# view:` at the top draws the drone inside
  `Hover`;
- `altitude.py`: the steps with the CHASE Python package;
- `altitude.results.json`: the results of `chase-cps view altitude.ltl --check`;
- `out/altitude.html`: the diagram above, written by `altitude.py`.

### Run it

```
pip install "chase-cps[z3]"
python altitude.py --expect
chase-cps view altitude.ltl --check -o out/altitude-view.html
```
