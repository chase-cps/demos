## Charger: diagnosis of an arbiter

Two robots share a charging station, and an arbiter gives the station to
the robots. The demo follows one design iteration of the arbiter: the
requirements of a first arbiter cannot be realized, a second one can be
realized but for a bad reason, and a third one is composed with the robots
and checked against the requirements of the whole system.

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements, numbered;
- `charger.ltl`: the contracts of the robots (_Robot1_, _Robot2_), of four
  arbiters (_Greedy_, _Fair_, _Pushy_, _Polite_), and of the system
  (_System_). The comment at the end of each line is the number of the
  requirement;
- `charger.chase`: the commands of the logics-based flow;
- `charger.py`: the whole iteration with the CHASE Python package.

### Logic-based Flow

The console of the `logics_tool` writes the files for slugs and nuXmv:

`$> logics_tool -i charger.ltl -o /tmp/charger/ -c charger.chase`

First, the _Greedy_ arbiter gives the station to each robot at the next step
after its request (R6.1, R6.2), and never to both robots (R5). Its
realizability is checked with slugs (`$SLUGSCOMPILER` is the
`tools/StructuredSlugsParser/compiler.py` script of slugs; it is set in the
Docker image of CHASE):

`$> python3 $SLUGSCOMPILER /tmp/charger/greedy.structuredSlugs > /tmp/charger/greedy.slugsin`\
`$> slugs /tmp/charger/greedy.slugsin`\
`RESULT: Specification is unrealizable.`

When both robots ask for the station at once, the arbiter cannot give it to
both. Thus, the _Fair_ arbiter gives the station to each robot eventually
(R7.1, R7.2):

`$> python3 $SLUGSCOMPILER /tmp/charger/fair.structuredSlugs > /tmp/charger/fair.slugsin`\
`$> slugs /tmp/charger/fair.slugsin`\
`RESULT: Specification is realizable.`

Finally, the script composes _Fair_ with the two robots, and writes the
refinement check of the composition against _System_ in
`/tmp/charger/refinement.smv`:

`$> nuXmv -int /tmp/charger/refinement.smv`\
`nuXmv > go`\
`nuXmv > build_boolean_model`\
`nuXmv > check_ltlspec_ic3`

Both formulas are true: the composition refines _System_.

### Python Flow

The checks that find why a contract fails are in the CHASE Python package
(`pip install chase-cps`, version 0.2.0):

`$> python3 charger.py`

The script prints the result of each step:
1. _Greedy_ is unrealizable. The unrealizable core is R6.1, R6.2, and R5:
   the three guarantees in conflict. The composition of _Greedy_ with the
   robots refines _System_ all the same: the refinement check does not see
   the conflict.
2. _Fair_ is realizable, and a controller is synthesized.
3. The _Pushy_ arbiter assumes that robot 1 asks for the station infinitely
   often (A2), and that it does not ask for it after it is given the station
   (A3). The arbiter can give the station to robot 1 forever: then robot 1
   never asks again, A2 is violated, and the arbiter satisfies its contract
   without serving anybody. The well-separation check finds it, and its core
   is A2 and A3. The _Polite_ arbiter assumes A4 instead of A3, and is well
   separated.
4. _Fair_ is not vacuous: it cannot win without granting each robot
   (`is_vacuous`). An arbiter that trusts the robots to stop asking on
   their own (it assumes G F !req1 and G F !req2) is vacuous: R7.1 and R7.2
   then hold without any grant, and `is_vacuous` gives the strategy that
   never grants and the assumptions that allow it. R8 is redundant: R7.1
   implies it. `remove_redundant` with `synth=True` removes it, and the
   contract stays realizable.
5. The arbiter and the robots feed each other (`req` and `grant`). Composed
   with discharge, the assumptions of the robots (A1.1, A1.2) are discharged
   by the guarantees of the arbiter (R7.1, R7.2): no assumption is left, and
   the composition refines _System_.

With `--expect` the script exits with code 1 when a result is not the
expected one.
