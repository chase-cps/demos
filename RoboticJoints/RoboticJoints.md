## Robotic arm: three joints, checked and synthesized one at a time

**The question.** A robotic arm moves three joints to the angles it asks
for. The contract of the arm is written for the whole arm, the contracts
of the joints for one joint each. Do the joints together meet the contract
of the arm, can a controller be built for each joint alone, and how does
the check grow with the number of joints?

**What it shows.**
- Composition and refinement (nuXmv): Joint1 ∥ Joint2 ∥ Joint3 refines
  _Joints_, the contract of the arm (2 s with the console, both formulas
  true).
- Realizability and synthesis (slugs, GR(1)): each joint is realizable, and
  slugs synthesizes a controller of 72 states for each.
- Compositional synthesis: the contract of the whole arm is realizable too
  (0.4 s), but its explicit controller has at least 375,000 states; slugs
  had written 111 of them (107 MB) after 15 minutes, against 3 x 72 states
  for the joints one at a time.
- Scaling (`scaling.py`): the refinement of N joints against the arm is
  proved for N = 1 to 8, in 4.8 s for 8 joints. When Joint1 drops its
  liveness guarantee, the counterexample (3 steps) is found in 4.8 s for 8
  joints.
- Composition with discharge: the same check with the terms kept, 3.3 s
  for 8 joints.

<p align="center">
  <img src="images/overview-three-joints.png" alt="The arm: Joint1, Joint2, and Joint3 inside Joints, each joint with its own ports; every check green">
  <br>
  <em>The three joints inside the contract of the arm: for each, the assumptions and the guarantees can hold together (A∧G), and it is realizable (R); together they refine Joints (⪯).</em>
</p>

The example was shown at CPS-IoT Week 2022 (see `../CPSWeek22`). The
variables of joint _i_ are:

- `req_ji`: the arm asks the joint to move (input);
- `ji_dangle`: the angle asked for, 0 to 4 (input);
- `ji_angle`: the angle of the joint, 0 to 4 (input);
- `ji_cmd`: the command, 0 stay, 1 up, 2 down (output);
- `ji_done`: the joint is at the angle asked for (output).

Each joint assumes how a command moves the angle, that a request is kept
until the joint is done, that the angle asked for does not change during a
request, and that requests come and go infinitely often. It guarantees
that it stays still when not asked, that `ji_done` tells whether the angle
is the one asked for, and that it is done infinitely often (`G F ji_done`).
_Joints_ has the assumptions and the guarantees of the three joints.

### The steps

**Step 1. The joints refine the arm.** The three joint contracts are
composed, and the composition refines _Joints_. With the console,
`verification.chase` composes the joints and writes the check in
`refinement.smv`; nuXmv (IC3) proves both formulas (assumptions and
guarantees) in 2 s. `diagram.sh` draws the same check with the checks of
each contract: all green.

<p align="center">
  <img src="images/step1-joints-refine-arm.png" alt="Step 1: Joints and Joint1 open: the assumptions and the guarantees of one joint and of the arm; the refinement holds">
  <br>
  <em>Step 1: Joint1 and Joints open: what one joint and the arm assume and guarantee.</em>
</p>

**Step 2. A controller for each joint.** Each joint contract is realizable
(R in the diagram above). With the console, `synthesis.chase` writes one
file for slugs per joint, and slugs synthesizes a controller of 72 states
for each (`joint1.json`, `joint2.json`, `joint3.json`).

**Step 3. One controller for the whole arm.** `singlemodel.chase` writes
_Joints_ alone for slugs. It is realizable (0.4 s), but the explicit
strategy of the whole arm has at least 375,000 states (the successors of
the first states written reach state 374,999), about the product of the
three joint controllers (72 x 72 x 72 = 373,248). slugs had written 111
states (107 MB) after 15 minutes, and was stopped. Synthesizing the joints
one at a time keeps three controllers of 72 states.

**Step 4. Scaling.** `scaling.py` builds the same contracts for N joints,
composes them, and checks the refinement against the arm of N joints. With
`--broken`, Joint1 does not guarantee `G F j1_done`, and the check must
fail. On an Apple M4 Pro (nuXmv 2.2.0, chase-cps 0.5.0):

- closed composition: refinement proved in 1.0 s for 3 joints, 2.7 s for
  5, 4.8 s for 8; the counterexample of the broken version (3 steps) in
  1.0 s, 2.3 s, and 4.8 s;
- composition with discharge (`--discharge`, the terms of the joints kept):
  refinement in 0.7 s, 1.6 s, and 3.3 s; the composition itself takes 11.0 s
  for 8 joints.

`results/` keeps the measurements of older versions: with chase-cps 0.1.0
the closed composition did not finish in 600 s from 6 joints
(`results/scaling.csv`, `results/scaling.pdf`).

### Content of the directory
The directory of the demo contains:
- `specs.ltl`: the contracts of the three joints (_Joint1_, _Joint2_,
  _Joint3_) and of the arm (_Joints_);
- `single_model.ltl`: the contract of the arm alone;
- `specs.results.json`, `single_model.results.json`: the results kept by
  `chase-cps view --check`;
- `verification.chase`, `synthesis.chase`, `singlemodel.chase`,
  `script.chase`: commands of the console;
- `compositional_demo.sh`: the refinement check and the synthesis of each
  joint with the console, slugs, and nuXmv;
- `singlemodel_demo.sh`: the synthesis of the whole arm with the console
  and slugs;
- `refinement.smv`: the refinement check written by `verification.chase`;
- `diagram.sh`: draws `out/specs.html` with `chase-cps view`;
- `scaling.py`: the check for N joints with the CHASE Python package;
- `plot_scaling.py`: draws the results of `scaling.py` (needs matplotlib);
- `results/`: measurements of `scaling.py` with older versions;
- `out/specs.html`: the diagrams above, written by `diagram.sh`.

### Run it

```
pip install chase-cps                       # version 0.5.0 or later
chase-cps install nuxmv --accept-license
chase-cps install slugs
python scaling.py --expect
python scaling.py --joints 1 2 3 4 5 6 7 8 --broken --expect --csv /tmp/scaling.csv
python plot_scaling.py /tmp/scaling.csv -o /tmp/scaling.pdf
sh diagram.sh
```

`scaling.py` prints one row per number of joints: the time to compose, the
time and the verdict of the refinement check, and with `--broken` the time
to find the counterexample and its length. With `--expect` it exits with
code 1 unless every correct version is proved and every broken one
refuted.

Console. The two shell scripts run the console of `logics_tool`, slugs,
and nuXmv, and wait for the Enter key between the steps (`$SLUGSCOMPILER`
is `tools/StructuredSlugsParser/compiler.py` of slugs):

```
$> sh compositional_demo.sh /tmp/joints
$> sh singlemodel_demo.sh /tmp/joints
```

`compositional_demo.sh` takes about 2 s after the key presses.
`singlemodel_demo.sh` prints that the arm is realizable at once, then
writes the explicit strategy of the whole arm in `single_mode.fsm`, which
does not finish in practice (step 3): stop it with Ctrl-C.
