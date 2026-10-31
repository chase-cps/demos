## Aircraft power system: requirements written as patterns, checked for a controller

**The question.** The electrical power system of an aircraft has two
generators, buses, rectifiers, loads, and three contactors. Its
requirements are written as patterns over the architecture, not as
formulas. Can the contactors be controlled so that the requirements hold
when a generator fails, and if not, which requirements are in conflict?

**What it shows.**
- The domain-specific language of CHASE: the components, how they are
  connected, and patterns of requirements (`never-connect`,
  `never-disconnect`, ...) become one GR(1) contract for the controller of
  the contactors: 11 inputs, 7 outputs, 30 assumptions, 28 guarantees.
- Realizability (slugs, GR(1)): the requirements as written are
  unrealizable (in under 2 s).
- Unrealizable core: 4 of the 28 guarantees, the pattern that never
  connects the generators in parallel and the 15 ms bound of one DC bus.
- Realizable after the change: with 20 ms to disconnect a failed generator
  and 30 ms for a DC bus, the contract is realizable (0.1 s), and slugs
  synthesizes a controller of 97 states (console).

<p align="center">
  <img src="images/overview-two-versions.png" alt="The page of the demo: EPS_15ms, open, unrealizable with its core in red; EPS_30ms, realizable">
  <br>
  <em>The two versions of the requirements: as written (R red, the core in red) and relaxed (R green).</em>
</p>

The system is that of Nuzzo et al., "CHASE: Contract-based requirement
engineering for cyber-physical system design" (DATE 2018). Its components
are:

- a left and a right generator (`LG1`, `RG1`), which may fail;
- a left and a right AC bus (`LB1`, `RB1`), a rectifier, a DC bus (`LD1`,
  `RD1`), and a load on each side;
- contactor 1 between `LG1` and `LB1`, contactor 2 between `RG1` and
  `RB1`, and contactor 3 between the two AC buses.

The controller reads the state of the generators and of the contactors,
and commands the contactors. The requirements of
`template_0_unrealizable.txt` are:

- the generators are never connected in parallel through the AC buses
  (`never-connect`);
- a failed generator is disconnected within 15 ms
  (`must-disconnect-failed`);
- a DC bus is powered by the generator of its side when possible
  (`prefer-active-connection`);
- a DC bus is never unpowered for more than 15 ms (`never-disconnect`);
- a contactor that connects a working generator stays closed
  (`keep-connection-stable`).

The assumptions are that a contactor opens and closes in 10 ms or less,
that at most one generator fails and does not recover, and that the other
components do not fail. `requirements.txt` gives the requirements in
English, with 30 ms for a DC bus, the bound of the relaxed version.

The times become counters: with a step of 5 ms, 15 ms is three steps.

### The steps

**Step 1. The requirements as written.** The contract is unrealizable. The
unrealizable core is 4 of the 28 guarantees: the pattern that never
connects the two generators in parallel (contactors 1, 2, and 3 never all
closed), and the three terms of the counter of one DC bus, which say that
the bus is unpowered for at most 15 ms. When a generator fails, the bus on
its side can only be fed by the other generator through contactor 3, and
the contactors take up to 10 ms to switch.

The two DC buses are symmetric; the core names the right one (CHASE puts
the terms built from the patterns in a fixed order, so every run gives the
same core).

<p align="center">
  <img src="images/step1-unrealizable-core.png" alt="Step 1: EPS_15ms is unrealizable; the four guarantees of the core in red, and the panel of the check">
  <br>
  <em>Step 1: the requirements as written are unrealizable; the terms of the core are red.</em>
</p>

**Step 2. The relaxed requirements.** `template_0_realizable.txt` gives a
failed generator 20 ms to be disconnected, and a DC bus 30 ms without
power. The contract (24 assumptions, 26 guarantees, with a step of 10 ms)
is realizable. With the console, slugs synthesizes a controller of 97
states (`EPS.json`).

<p align="center">
  <img src="images/step2-relaxed-realizable.png" alt="Step 2: EPS_30ms, realizable, with the states of the generators and contactors as inputs and the commands of the contactors as outputs">
  <br>
  <em>Step 2: the relaxed requirements are realizable (R).</em>
</p>

The same language describes a small factory: `../FDL2024`.

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the requirements and the assumptions, in English;
- `template_0_unrealizable.txt`: the system and the requirements in the
  language of CHASE, as written;
- `template_0_realizable.txt`: the same, with 20 ms for a failed generator
  and 30 ms for a DC bus;
- `eps.py`: the steps with the CHASE Python package;
- `solution.sh`: the steps with `dsl_tool` and slugs;
- `out/eps.html`: the diagrams above, written by `eps.py`.

### Run it

```
pip install chase-cps                       # version 0.5.0 or later
chase-cps install slugs
python eps.py --expect
```

The script prints the size of the contract, the result of each step, and
the terms of the core, and writes `out/eps.html`, a page to open in a
browser: a click on a name opens or closes the contract, and a click on
the red tag shows or hides the core and opens the panel of the check. With
`--expect` the script exits with code 1 when a result is not the expected
one.

Console. `dsl_tool` reads the files of the language and writes the
specification for slugs; `solution.sh` runs both versions and waits for
the Enter key between the steps (`$SLUGSCOMPILER` is
`tools/StructuredSlugsParser/compiler.py` of slugs):

```
$> dsl_tool -i template_0_unrealizable.txt -o /tmp/eps/unrealizable
$> python3 $SLUGSCOMPILER /tmp/eps/unrealizable.structuredSlugs > /tmp/eps/unrealizable.slugsin
$> slugs /tmp/eps/unrealizable.slugsin
RESULT: Specification is unrealizable.
$> sh solution.sh /tmp/eps
```
