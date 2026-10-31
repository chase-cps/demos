## Braking: repairing the timing of an emergency braking system

**The question.** Brake 1 must start within 4 ms of its schedule, but the
camera path can delay it. How much must its bound grow, or how much must
the inconsistency of the network link grow, for the requirement to hold?

This is the braking system of ContrACT (Xiao, Lutz, Castillo-Effen, Nuzzo,
*Contract-Based Consistency and Availability Analysis for Distributed
Cyber-Physical Systems*, MEMOCODE 2026). The pedal `p` is processed by `a`,
which triggers Brake 1 (`b`); the camera `c` triggers the detection `d`,
whose result crosses the network link `e` to Brake 2 (`f`). `b` and `f` run
on the same controller, and the camera path can delay `b`.

`braking.json` has the timing contracts that ContrACT builds for each node,
over the timestamp `t`, the start `d`, and the completion `T` of each event,
and two system contracts:

- `SysB`: Brake 1 starts at most `lam_b` (4) after its timestamp, given the
  delay of 1 that the camera path can cause it (the offset of ContrACT).
- `DelayF`: the camera path delays Brake 1 by at most `y_f` (0.95, what
  Brake 1 can absorb: 4 - 3.05 from its own path).

The link `e` schedules `f` `kappa` (10) after `d`. The contracts compare
reals with no temporal operator, so z3 checks them, and `repair` computes
at once the values for which the check fails (quantifier elimination), then
the least change.

### The steps

**Step 1. The bound is violated.** The pedal path does not refine `SysB`:
Brake 1 can start 3.05 late on its own path, plus 1 from the camera path:
4.05.

**Step 2. Repair the bound.** `repair` gives `lam_b = 4.05`, optimal: the
paper's option A.

**Step 3. Repair the link, no delay.** With `y_f = 0` (the camera path never
delays Brake 1), `repair` gives `kappa = 11`: the paper's option B. The
detection takes up to 2 + 9 = 11 ms to reach `f`, so with `kappa = 11` it
never waits.

**Step 4. Repair the link, the delay that Brake 1 absorbs.** Brake 1 can
take a delay of 0.95 and still start within 4 (3.05 + 0.95). With
`y_f = 0.95`, `repair` gives `kappa = 10.05`, a smaller change than 11. The
camera path refines `DelayF` with 10.05 and not with 10.04. Run through the
whole analysis of ContrACT, `kappa = 10.05` gives Brake 1 a worst case of
exactly 4.0, which passes; 10.04 gives 4.01, which fails.

### Run it

```
pip install "chase-cps[z3]"
python braking.py --expect
```
