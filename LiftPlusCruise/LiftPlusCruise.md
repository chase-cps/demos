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
requirements with LPC_REACH_HOVER_12 are consistent. With
`/tmp/lpc/vehicle06.smv` the second formula is true: the requirements with
LPC_REACH_HOVER_06 are not consistent.

### Python Flow

`$> python3 lpc.py`

The script needs the CHASE Python package (`pip install chase-cps`, version
0.2.0) and nuXmv. It prints:
1. a behavior of the requirements with LPC_REACH_HOVER_12. In the one that
   nuXmv finds, `kias` goes down from 120 by 10 at each step, the vehicle
   leaves the wing borne mode when `kias` is 90, and it hovers at step 11;
2. the unsat core of the requirements with LPC_REACH_HOVER_06, by name. The
   vehicle stays wing borne while `kias` is above 90 (LPC_WB_STAY_ON_NEXT),
   that is, for 3 steps. Then it is semi wing borne while `kias` is above 30
   (LPC_SWB_STAY_ON_NEXT), and `kias` cannot reach 30 by step 6.

With `--expect` the script exits with code 1 when a result is not the
expected one.
