## Lift-Plus-Cruise: requirements with real variables

Lift-Plus-Cruise is an aircraft studied at NASA: lift rotors for the
vertical take-off, the landing, and the hover, and a wing with a pusher
propeller for the cruise. The requirements of the demo are those of the
LPC_mini project of the FRET case study Lift-Plus-Cruise
(https://github.com/NASA-SW-VnV/fret, caseStudies/LiftPlusCruise;
Pressburger, Katis, Dutle, Mavridou, REFSQ 2023). They give the lift mode of
the aircraft (_wing borne_, _semi wing borne_, _semi thrust borne_, or
_thrust borne_, i.e., hover) from its airspeed `kias` and its ground speed
`kgs`, both real numbers.

The airspeed is 120 at the start (LPC_INIT_KIAS), and it changes by 10 at
most at each step (LPC_KIAS_DERIVATIVE). Two requirements ask the vehicle to
hover within 12 steps (LPC_REACH_HOVER_12) or within 6 steps
(LPC_REACH_HOVER_06). FRET finds that the requirements are realizable with
the first one, and unrealizable with the second one. All the variables are
outputs of the vehicle, so the requirements are realizable when they are
consistent: CHASE checks their consistency.

![The vehicle: the mode logic and the pilot, wired by the speeds, the hover control, and the lift mode](diagram-system.png)
_The vehicle: the mode logic and the pilot, wired by the speeds, the hover control, and the lift mode._

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements in FRETish, as in FRET;
- `lpc.ltl`: the requirements in the logics language of CHASE, written by
  hand from the LTL formulas that FRET gives for them. The contract
  _Vehicle_ has all of them but the two LPC_REACH_HOVER ones, the contracts
  _Reach12_ and _Reach06_ have one each. The comment at the end of each line
  is the name of the requirement;
- `lpc.chase`: the commands of the logics-based flow;
- `lpc.py`: the checks with the CHASE Python package.

### Logic-based Flow

The console of the `logics_tool` conjoins _Vehicle_ with _Reach12_ and with
_Reach06_, and writes the consistency checks:

`$> logics_tool -i lpc.ltl -o /tmp/lpc/ -c lpc.chase`

The console says that the files have real variables: NuSMV cannot read them,
and nuXmv checks them with its SMT engine:

`$> nuXmv -int /tmp/lpc/vehicle12.smv`\
`nuXmv > go_msat`\
`nuXmv > check_ltlspec_ic3`

The second formula, the negation of the guarantees, is false: the
requirements with LPC_REACH_HOVER_12 are consistent. The third one, the
negation of A & G, is false too: the assumptions and the guarantees can hold
together. With `/tmp/lpc/vehicle06.smv` the second and the third formulas
are true: the requirements with LPC_REACH_HOVER_06 are not consistent.

### Python Flow

`$> python3 lpc.py`

The script needs the CHASE Python package (`pip install chase-cps`, version
0.5.0) and nuXmv. It prints:
1. a behavior of the requirements with LPC_REACH_HOVER_12. In the one that
   nuXmv finds, `kias` goes down from 120 by 10 at each step, the vehicle
   leaves the wing borne mode when `kias` is 90, and it hovers at step 11;
2. the unsat core of the requirements with LPC_REACH_HOVER_06, by name. The
   vehicle stays wing borne while `kias` is above 90 (LPC_WB_STAY_ON_NEXT),
   that is, for 3 steps. Then it is semi wing borne while `kias` is above 30
   (LPC_SWB_STAY_ON_NEXT), and `kias` cannot reach 30 by step 6.

Consistency says that some behavior hovers within 12 steps, not that every
one does. The next steps ask what makes the vehicle hover. The requirements
are split between two components: _ModeLogic_ gives `lift_mode` from the
speeds and the hover control mode (the LPC_*_TO_* and LPC_*_STAY_*
requirements, LPC_INIT_LIFT_MODE, LPC_LIFT_MODE), and _Pilot_ gives `kias`,
`kgs`, and `hover_control_mode` (LPC_INIT_KIAS, LPC_KIAS_KGS,
LPC_KIAS_DERIVATIVE, LPC_KIAS_0, LPC_INIT_HOVER_MODE).

3. _ModeLogic_ ∥ _Pilot_ refines _Vehicle_: the split keeps the
   requirements.
4. _Q12_ = _Reach12_ / _ModeLogic_, the quotient with discharge, is what the
   pilot must do for the vehicle to hover within 12 steps. _Pilot_ does not
   refine it: the counterexample keeps `kias` at 120, and the vehicle wing
   borne, forever.
5. _Slow_, the pilot that slows down by 10 at each step, does not refine it
   either: the counterexample never turns the hover control mode on, and the
   vehicle stays semi thrust borne. LPC_INIT_HOVER_MODE ties the hover
   control mode to `kgs` only at the start.
6. _Decel_, which also turns the hover control mode on when `kgs` is below
   20, refines _Q12_. So _ModeLogic_ ∥ _Decel_ refines _Reach12_ (the
   script checks it too): with this pilot, every behavior hovers within 12
   steps. _Decel_ does not refine _Q06_ = _Reach06_ / _ModeLogic_, as no
   pilot can (step 2).

With `--expect` the script exits with code 1 when a result is not the
expected one.

`out/lpc.html`, written by `lpc.py`, draws _Vehicle_ with each of
LPC_REACH_HOVER_12 and LPC_REACH_HOVER_06 and whether it is consistent (G,
green and red), _ModeLogic_ ∥ _Pilot_ inside _Vehicle_, and the quotient
_Q12_ once for each pilot in its hole (_Pilot_, _Slow_, _Decel_), then _Q06_
with _Decel_, with the result of each refinement (⪯, green when it holds,
red when it does not). The holes Q12 and the contract of _Decel_ are drawn
open. It opens in a browser; a click on a name opens or closes the
contract, and a click on a red tag shows its core.

![The requirements are consistent with the deadline of 12 s, not with 6 s: the core, on a red ground, is the 8 requirements in conflict (kias falls by 10 at most at each step, from 120)](diagram-1.png)
_The requirements are consistent with the deadline of 12 s, not with 6 s: the core, on a red ground, is the 8 requirements in conflict (kias falls by 10 at most at each step, from 120)._

![ModeLogic ∥ Pilot refines Vehicle](diagram-2.png)
_ModeLogic ∥ Pilot refines Vehicle._

![Q12 = Reach12 / ModeLogic, what the pilot must do to hover within 12 s; Pilot, with the requirements only, does not refine it (kias may stay at 120)](diagram-3.png)
_Q12 = Reach12 / ModeLogic, what the pilot must do to hover within 12 s; Pilot, with the requirements only, does not refine it (kias may stay at 120)._

![Slow, which slows down by 10 at each step, does not refine Q12: the hover control mode never comes](diagram-4.png)
_Slow, which slows down by 10 at each step, does not refine Q12: the hover control mode never comes._

![Decel, which also turns the hover control mode on when kgs < 20, refines Q12](diagram-5.png)
_Decel, which also turns the hover control mode on when kgs < 20, refines Q12._

![Decel does not refine Q06 = Reach06 / ModeLogic: no pilot can hover within 6 s](diagram-6.png)
_Decel does not refine Q06 = Reach06 / ModeLogic: no pilot can hover within 6 s._
