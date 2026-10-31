## Braking: repairing the timing of an emergency braking system

**The question.** Brake 1 must start within 4 ms of its schedule, but the
camera path can delay it. How much must its bound grow, or how much must
the inconsistency of the network link grow, for the requirement to hold?

This is the braking system of ContrACT (Xiao, Lutz, Castillo-Effen, Nuzzo,
*Contract-Based Consistency and Availability Analysis for Distributed
Cyber-Physical Systems*, MEMOCODE 2026). `BrakePedal` is processed by
`PedalProcessing`, which triggers `Brake1`; the `Camera` triggers the
obstacle `Detection`, whose result crosses the network `Link` to `Brake2`.
`Brake1` and `Brake2` are two reactions of the same Braking reactor, which
handles its events in the order of their timestamps: while `Brake2` waits
for late camera data, a pedal event that comes after it waits too. This is
how the camera path delays Brake 1 (the offset of the paper).

`braking.ltl` has the timing contracts that ContrACT builds for each node
(Section III-C of the paper), over the timestamp `t`, the start `d`, and
the completion `T` of each event:

- a source (`BrakePedal`, `Camera`) starts at its timestamp or later and
  runs at most its worst-case latency;
- a processor (`PedalProcessing`, `Detection`, `Brake1`) takes the
  timestamp of its trigger and starts when the trigger completes;
- the `Link` schedules the receiver `kappa` (10) after the sender (the
  inconsistency) and delivers the data at most 9 after;
- `Brake2` starts at the later of the release of its event and the arrival
  of the data.

Two system contracts state the requirements:

- `SysB` (equation (8)): given that the pedal event is released at most
  `offset` (1) after its timestamp, Brake 1 starts at most `lam_b` (4)
  after its own.
- `DelayF`: Brake 2 starts at most `y_f` after its timestamp, the delay it
  passes on to Brake 1. Brake 1 can absorb `y_f = 0.95` (4 - 3.05 from its
  own path).

`offset`, `lam_b`, `kappa`, and `y_f` are named constants (`real constant`).
The contracts compare reals with no temporal operator, so z3 checks them,
and `repair` computes at once the values for which the check fails
(quantifier elimination), then the least change.

### The steps

**Step 1. The bound is violated.** The pedal path (`BrakePedal`,
`PedalProcessing`, `Brake1` composed) does not refine `SysB`: Brake 1 can
start 3.05 late on its own path, plus 1 from the camera path: 4.05.

**Step 2. Repair the bound.** `repair` gives `lam_b = 4.05`, optimal: the
paper's option A.

**Step 3. Repair the link, no delay.** The camera path (`Camera`,
`Detection`, `Link`, `Brake2` composed) must refine `DelayF`. With `y_f = 0`
(the camera path never delays Brake 1), `repair` gives `kappa = 11`: the
paper's option B (Table II). The detection takes up to 2 + 9 = 11 ms to
reach `Brake2`, so with `kappa = 11` it never waits.

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
chase-cps repair braking.ltl --refines BrakePedal+PedalProcessing+Brake1 SysB --param lam_b=0..10
```
