## Lockheed Martin autopilot: the requirements in conflict, and the time the pullup takes

**The question.** An autopilot commands a safety maneuver (pullup) when a
sensor reports a hazard. Which of its first requirements conflict? Once
corrected, does the pullup come when its requirement says?

**The result.**
- The first requirements are unrealizable. Fixing one requirement per
  unrealizable core (the smallest set of requirements in conflict), the
  script finds four conflicts in the autopilot and one in the sensor, like
  FRET.
- The corrected autopilot and sensor do not refine FSM-001, the
  system requirement: the counterexample has three steps.
- They refine FSM-001t, its timed version.

<p align="center">
  <img src="images/overview-all-checks.png" alt="The first requirements, unrealizable; the corrected ones inside System (red) and SystemTimed (green)">
  <br>
  <em>The first requirements (R red), and the corrected ones inside System (⪯ red) and SystemTimed (⪯ green).</em>
</p>

The requirements come from the Ten Lockheed Martin Cyber-Physical
Challenges (Mavridou et al., RE 2020), first and corrected, as in the FRET
case study. Each is a transition of the autopilot (TRANSITION, NOMINAL,
MANEUVER, STANDBY) or of the sensor; `x'` is the value of `x` at the next
step.

### The steps

**Step 1. The first requirements.** Each core of _AutopilotFirst_ and
_SensorFirst_ is the initial state and the requirements that send the
machine to two states for the same inputs. In TRANSITION, for instance,
with the pilot in control (`standby`), the system supported and good sensor
data, FSM-002 says STANDBY and FSM-003 says NOMINAL. The script replaces
one requirement per core by its corrected version until the contract is
realizable: four conflicts in the autopilot, one in the sensor.

<p align="center">
  <img src="images/step1-first-requirements-unrealizable.png" alt="Step 1: AutopilotFirst, unrealizable, with its first core in red">
  <br>
  <em>Step 1: the first requirements; the cores in red.</em>
</p>

**Step 2. The system.** The corrected _Autopilot_ and _Sensor_ are
realizable; composed with discharge, they leave no assumption. They do not
refine _System_ (FSM-001: a pullup when the limits are exceeded, with the
pilot not in control, the system supported, and no failure). At step 1 of
the counterexample the limits are exceeded, but the autopilot is still in
NOMINAL: no pullup.

<p align="center">
  <img src="images/step2-does-not-refine-system.png" alt="Step 2: the counterexample, in the panel and on the wires">
  <br>
  <em>Step 2: the composition does not refine System; the values at step 1.</em>
</p>

**Step 3. The system, with time.** The sensor and the autopilot each take a
step to react, and the autopilot must first reach NOMINAL. _SystemTimed_
(FSM-001t) gives the pullup that time: after three steps within the limits
and one beyond, with the pilot not in control and no failure, the pullup
comes at the fifth step. The composition refines it.

<p align="center">
  <img src="images/step3-refines-systemtimed.png" alt="Step 3: Autopilot and Sensor inside SystemTimed; the refinement holds">
  <br>
  <em>Step 3: the composition refines SystemTimed.</em>
</p>

### Run it

```
pip install chase-cps
chase-cps install nuxmv --accept-license
chase-cps install slugs
python fsm.py --expect
```

### Content of the directory
- `requirements.txt`: the requirements, numbered as in the paper;
- `fsm.ltl`: the contracts of the autopilot and of the sensor, first and
  corrected, and of the system; each line ends with its number;
- `fsm.results.json`: the results of `chase-cps view --check`;
- `fsm.py`: the steps with the CHASE Python package;
- `out/fsm.html`: the diagrams above, written by `fsm.py`.
