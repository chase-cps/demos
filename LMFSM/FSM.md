## LMFSM: conflicting requirements

The question: which requirements of a state machine, as first written,
contradict each other, and does the pullup of the corrected system come
when the requirement of the system says?

An autopilot commands a safety maneuver (pullup) when a sensor reports a
hazard. The requirements are those of the finite state machine of the Ten
Lockheed Martin Cyber-Physical Challenges (A. Mavridou et al., "The Ten
Lockheed Martin Cyber-Physical Challenges: Formalized, Analyzed, and
Explained", RE 2020), as in the FRET case study LMCPS. The demo finds the
requirements in conflict, checks that the corrected ones can be realized,
and checks the requirement of the whole system on the composition of the
autopilot and the sensor.

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements, with the numbers of the paper;
- `fsm.ltl`: the contracts of the autopilot and of the sensor as the
  requirements were first written (_AutopilotFirst_, _SensorFirst_) and
  corrected (_Autopilot_, _Sensor_), and of the system (_System_,
  _SystemTimed_). The comment at the end of each line is the number of the
  requirement;
- `fsm.py`: the analysis with the CHASE Python package.

### The contracts
The autopilot has four states (TRANSITION, NOMINAL, MANEUVER, STANDBY), and
the sensor three (NOMINAL, TRANSITION, FAULT). Each requirement is a
transition, written one step early: "from S to S' when c" is
`G((STATE = S & c) -> STATE' = S')`, where the inputs of the new step are
primed. The autopilot reads the sensor (`good`) of the previous step, and
the sensor reads the autopilot (`MODE`, `REQUEST`) of the same step.

_Autopilot_ and _Sensor_ have the corrected requirements (v2), and what the
Simulink model of the challenge does in the other cases: the machine stays
in its state (AP-S, SEN-S), and the outputs are given by the state (AP-O,
SEN-O).

### Python Flow
The script needs the CHASE Python package (`pip install chase-cps`), slugs,
and nuXmv or NuSMV:

`$> python3 fsm.py`

It prints the result of each step:
1. _AutopilotFirst_ is unrealizable. The unrealizable core gives the
   requirements in conflict: FSM-002 and FSM-003 both apply in TRANSITION
   when the pilot is in control and the sensor data is good, and lead to
   two states. The script replaces the requirement with a corrected version
   (FSM-003v2) and checks again. Four conflicts are found in a row (FSM-003,
   FSM-004, FSM-008, FSM-007), and the contract is realizable after the
   fourth fix. _SensorFirst_ has one conflict (FSM-010 and FSM-011).
2. _Autopilot_ and _Sensor_ are realizable.
3. _Autopilot_ and _Sensor_, composed with discharge, do not refine
   _System_ (FSM-001: a pullup when the limits are exceeded). The
   counterexample: the limits are exceeded at step 1 and the sensor goes
   to FAULT, but the autopilot reads the sensor of the previous step, and
   is not in MANEUVER at step 1.
4. They refine _SystemTimed_ (FSM-001t), which gives the pullup the steps it
   takes: the limits not exceeded for three steps, then exceeded, with the
   pilot not in control and no failure from the second step to the fifth,
   give a pullup at the fifth step. This is FSM-001v3 of FRET, with the
   limits not exceeded for one step less.

With `--expect` the script exits with code 1 when a result is not the
expected one.

The limits not exceeded at the start are needed: when the sensor is in
FAULT while the autopilot is in TRANSITION, and the limits stay exceeded,
the sensor stays in FAULT (the autopilot requests support) and the
autopilot stays in TRANSITION (the sensor data is not good), so there is
never a pullup.

### Diagram
`out/fsm.html`, written by `fsm.py`, draws _AutopilotFirst_ and
_SensorFirst_ with their realizability (R, red), and _Autopilot_ ∥ _Sensor_
inside _System_ (⪯, red) and inside _SystemTimed_ (⪯, green), with the
realizability of each (R, green). It opens in a browser; a click on a name
shows the contract, and a click on a red R marks the first unrealizable core
in it.

![The contracts as first written are unrealizable; a click on R marks the requirements in conflict](diagram-1.png)
_The contracts as first written are unrealizable; a click on R marks the requirements in conflict._

![Autopilot ∥ Sensor does not refine System (FSM-001): the pullup does not come at once](diagram-2.png)
_Autopilot ∥ Sensor does not refine System (FSM-001): the pullup does not come at once._

![Autopilot ∥ Sensor refines SystemTimed (FSM-001t)](diagram-3.png)
_Autopilot ∥ Sensor refines SystemTimed (FSM-001t)._
