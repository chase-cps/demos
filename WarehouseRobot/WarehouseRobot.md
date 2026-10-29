## Warehouse robot: a controller to delegate

The question: the local controller of a warehouse robot is given to a
designer (a person, or a language model) while perception and localization
stay as they are. What must the controller satisfy for the robot to meet the
requirements of the system?

The example is simplified from S. S. Damera, R. Matheu, and J. S. Baras,
"Contract-Based Agentic Systems Engineering: Delegation as Quotient for
Assured System Design" (arXiv 2610.33349, 2026), with the bounds of the
paper. The robot crosses the floor, keeps 0.40 m from a worker, and rests
at a dock. The controller commands the yaw rate and the rest; it sees the
clearance to the worker and the distance to the dock only as perception and
localization report them. The answer is the quotient of the system by the
fixed components: the weakest contract of the controller with which the
system meets its requirements. It holds what the neighbours assume of the
controller, which a requirement written for the mission alone leaves out.

![The system with the place of the controller: the hole Q next to perception and localization](diagram-system.png)
_The system with the place of the controller: the hole Q next to perception and localization._

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the variables, the contracts, and the three candidate
  contracts of the controller;
- `warehouse.py`: the steps with the CHASE Python package.

### The contracts
- _Perception_ assumes that the robot turns slowly enough (|w| <= 0.8), and
  guarantees that the reported clearance is at most 0.3 more than the true
  one.
- _Localization_ assumes |w| <= 1.0, and guarantees that the true distance
  to the dock is at most 0.05 more than the estimate.
- _System_: the robot keeps 0.40 from the worker, and rests within 0.10 of
  the dock sooner or later.
- The candidates for the controller: _MissionOnly_ (the requirements of the
  system written on what the controller sees), _Margins_ (the bounds less
  the errors of perception and localization), and _Dispatched_ (_Margins_
  with |w| <= 0.8).

### Python Flow
The script needs the CHASE Python package (`pip install chase-cps`, version
0.4.2) and nuXmv, whose SMT engine checks the real variables:

`$> python3 warehouse.py`

It prints the result of each step:
1. _Q_ = _System_ / (_Perception_ ∥ _Localization_), with discharge. It
   assumes the guarantees of perception and localization (under their
   assumptions), and guarantees the requirements of the system and |w| <=
   0.8, the assumption of perception (the one of localization, |w| <= 1.0,
   is implied by it).
2. _MissionOnly_ does not refine _Q_. In the counterexample the reported
   clearance is 0.40 and the true one is 0.10, which the error of
   perception (0.3) allows. At the next step the controller turns at -0.82,
   faster than perception allows.
3. _Margins_ does not refine _Q_ either: the margins hold, but the
   controller turns at -1.20, and the true clearance is 0.
4. _Dispatched_ refines _Q_, so _Perception_ ∥ _Localization_ ∥
   _Dispatched_ refines _System_ (the script checks it too). This is the
   contract to hand to the designer.

As in the paper, the requirement written for the mission fails in two ways:
it ignores the error of what the controller sees (the margins), and it
lets the controller break an assumption of its neighbours (the yaw rate).
The quotient gives the second one by itself; the margins are written by the
engineer on what the controller sees, and checked against the quotient.

With `--expect` the script exits with code 1 when a result is not the
expected one.

`out/warehouse.html`, written by `warehouse.py`, draws _Q_ as the hole next
to _Perception_ and _Localization_, once for each candidate in it:
_MissionOnly_ and _Margins_ (⪯, red), and _Dispatched_ (⪯, green). It opens
in a browser; a click on a name shows the contract.

![Q = System / (Perception ∥ Localization): MissionOnly does not refine it](diagram-1.png)
_Q = System / (Perception ∥ Localization): MissionOnly does not refine it._

![Margins does not refine Q](diagram-2.png)
_Margins does not refine Q._

![Dispatched refines Q](diagram-3.png)
_Dispatched refines Q._
