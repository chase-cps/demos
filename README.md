# CHASE demos

This repository contains the demonstrations of [CHASE][WEB]. Each one
follows a design problem from its requirements to a result; its page on the
website and its README show each step with its diagram.

They are grouped by what they show; the website has the same groups.

### AI agents and code

- [**PaymentAssistant**][PAYMENT] (payment assistant agent): a task in
    natural language (AppWorld) becomes the contract of an agent over its
    tool calls, split among sub-agents. The plan does not refine the parent
    (the counterexample never sends the text); the quotient Q3 says that
    sub-agent 3 must promise `F text3`, and the repaired sub-agent refines
    it; an unsat core finds the clause against the request of the user.
- [**ContractsInC**][CONTRACTSINC] (C): the
    contract written in the C file (ESBMC, CBMC, or ACSL clauses), next to
    the code. `chase-cps view
    FILE.c` draws each function as a component and checks it: a
    counterexample on the ports and the broken term in red, and a function
    with no clause checked as code alone (`safe`), with the line of the
    overflow.
- [**DroneGrid**][DRONEGRID] (fire-suppression drones, C): the reactions of
    two drones in C, checked one function at a time. The contracts (z3)
    find that the coordinator lets a drone move into the cell of the other;
    the quotient tells the fixed coordinator from the old one; ESBMC checks
    each function against its contract, and no check runs on the whole
    program.

### Repair and signals

- [**Heater**][HEATER] (thermostat): a thermostat in signal temporal logic
    overshoots its requirement (77 for at most 75, robustness -2). Repair
    finds the threshold (74, or 77 for the requirement), and ESBMC checks
    that the C code of the thermostat, called once per step, implements the
    repaired step.
- [**Braking**][BRAKING] (emergency braking): the braking system of
    ContrACT (MEMOCODE 2026). Brake 1 misses its bound by 0.05 ms
    (counterexample from z3). Repair finds the least change of the bound
    (4.05), or of the inconsistency of the network link: 11 when Brake 1
    takes no delay, as in the paper, or 10.05 when it absorbs the 0.95 it
    can.
- [**DroneAltitude**][DRONEALTITUDE] (fire-suppression drones, signal
    temporal logic): a drone climbs to its drop altitude in the wind. The
    robustness says by how much it misses (2.5 m below in a wind of 1).
    Repair shows that no climb rate can fix it and gives what the
    requirement can ask: a tolerance of 2.5, or a wind of at most 17/21.
- [**DroneTiming**][DRONETIMING] (fire-suppression drones, linear
    constraints): the timing of the drones of ContrACT (MDFS) as a linear
    program over the reals. The worst case is 280 ms, as in the paper, and
    repair gives the margins: the least bound (280), the slowest planner
    (192 ms), and the largest delay of the mission (179 ms).
- [**Deadline**][DEADLINE] (arbiter): the least bound on the waiting time
    of a request (2), repaired from counterexamples of nuXmv in two rounds
    and checked against every value.

### Hardware

- [**Escalation**][ESCALATION] (security chip): the escalation link of a
    toy OpenTitan, checked module by module: the RTL of each module
    implements its contract, and the contracts together refine the
    requirements, with no check on the whole design. A faster sender breaks
    its contract, with the counterexample on the RTL.
- [**AHB**][AHB] (bus arbiter): the arbiter of the AMBA AHB bus as two
    viewpoints in SystemVerilog Assertions, merged. Without the assumption
    that a master releases a locked bus, the merge is unrealizable, and its
    core points to that assumption; with it, slugs synthesizes a controller
    of 81 states, which implements the merge.
- [**BufferSwap**][BUFFERSWAP] (circuit buffer swap): a buffer of BaseJump
    STL is replaced by a smaller one. The new buffer does not refine the old
    one (a counterexample of 4 steps), but it refines the quotient, the
    contract of its place; the RTL is checked with Yosys and nuXmv, and the
    quotient is written as SVA for Jasper.

### Aircraft and robots

- [**LiftPlusCruise**][LPC] (aircraft): the requirements of the
    Lift-Plus-Cruise case study of [FRET][FRET], with real variables. They
    are consistent with a hover within 12 steps, not within 6 (an unsat
    core of 8 requirements); the quotient by the mode logic says what the
    pilot must do, two pilots fail it, and the one that slows down and turns
    on the hover control refines it.
- [**WarehouseRobot**][WAREHOUSE] (warehouse robot): the controller of a
    robot is delegated. The quotient by perception and localization, on
    real variables, is its contract and asks for `|w| <= 0.8`; the
    requirements written for the mission alone, and with margins, fail it
    with counterexamples; the contract with the yaw rate refines it.
- [**LMFSM**][LMFSM] (autopilot): the state machine of the Lockheed Martin
    challenge. The unrealizable cores find four conflicts in the autopilot
    and one in the sensor; the corrected parts do not refine FSM-001 (a
    counterexample of 3 steps) but refine its timed version.

### Controller synthesis

- [**Charger**][CHARGER] (charging station): four candidate arbiters for
    two robots, each problem caught by another check: Greedy is
    unrealizable, Fair is realizable (a controller of 18 states), Pushy is
    not well separated, Trusting is vacuous; Fair with the robots refines
    the system.
- [**RoboticJoints**][ROBOTICJOINTS] (robotic arm): three joint contracts
    refine the contract of the arm, and each joint has a controller of 72
    states (the whole arm has at least 375,000). `scaling.py` proves the
    refinement for up to 8 joints in 4.8 s, and finds the counterexample of
    a broken joint. [**CPSWeek22**][CPSWEEK22] is the same demo as shown at
    CPS-IoT Week 2022, with its original scripts.

### Domain-specific language

- [**DATE18**][DATE18] (power system): the aircraft power system of the
    DATE 2018 paper. As written, the requirements are unrealizable; the core
    is the never-connect pattern and the 15 ms bound of a DC bus. Relaxed,
    they are realizable, with a controller of 97 states.
- [**FDL2024**][FDL2024] (factory): a small factory of the FDL 2024 paper.
    The controller of its gates is realizable in 0.1 s, with slugs and with
    gr1c.
- [**DATE21**][DATE21] (tutorial): the hands-on tutorial of the DATE 2021
    University Booth: the domain-specific language on the power system, and
    the console on a robotic arm (refinement both ways, composition, and
    synthesis of the coordinator).

The Python scripts use the CHASE Python package, version 0.5.0 or later
(`pip install chase-cps`; BufferSwap and Escalation with
`pip install "chase-cps[rtl]"`; Braking, Heater, Deadline, DroneTiming,
DroneGrid, DroneAltitude, and ContractsInC with version 0.6.0 and
`pip install "chase-cps[z3]"`, and Heater, DroneGrid, and ContractsInC with ESBMC or CBMC), and nuXmv and slugs, which `chase-cps
install` installs. The console scripts expect `dsl_tool`, `logics_tool`,
`slugs` (with its compiler, `$SLUGS/tools/StructuredSlugsParser/compiler.py`),
and `nuXmv` in the `PATH`. The Docker image of CHASE
(`ghcr.io/chase-cps/chase`, built from the [chase][CHASE] repository) has
all of them but nuXmv, whose license does not allow redistribution:
`chase-cps install nuxmv --accept-license` adds it in a container.

[WEB]: https://chase-cps.github.io
[DATE21]: DATE21/DATE21.md
[FDL2024]: FDL2024/FDL2024.md
[CHASE]: https://github.com/chase-cps/chase
[FRET]: https://github.com/NASA-SW-VnV/fret
[CHARGER]: Charger/Charger.md
[LPC]: LiftPlusCruise/LiftPlusCruise.md
[BUFFERSWAP]: BufferSwap/BufferSwap.md
[LMFSM]: LMFSM/FSM.md
[AHB]: AHB/AHB.md
[WAREHOUSE]: WarehouseRobot/WarehouseRobot.md
[PAYMENT]: PaymentAssistant/PaymentAssistant.md
[ESCALATION]: Escalation/Escalation.md
[BRAKING]: Braking/Braking.md
[HEATER]: Heater/Heater.md
[DEADLINE]: Deadline/Deadline.md
[DRONETIMING]: DroneTiming/DroneTiming.md
[DRONEGRID]: DroneGrid/DroneGrid.md
[DRONEALTITUDE]: DroneAltitude/DroneAltitude.md
[CONTRACTSINC]: ContractsInC/ContractsInC.md
[ROBOTICJOINTS]: RoboticJoints/RoboticJoints.md
[CPSWEEK22]: CPSWeek22/CPSWeek22.md
[DATE18]: DATE18/DATE18.md
