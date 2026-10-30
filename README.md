# CHASE demos

This repository contains the demonstrations of [CHASE][WEB]. Each one
follows a design problem from its requirements to a result; its page on the
website and its README show each step with its diagram.

- [**PaymentAssistant**][PAYMENT] (payment assistant agent): a task in
    natural language (AppWorld) becomes the contract of an agent over its
    tool calls, split among sub-agents. The plan misses a deliverable, the
    quotient says what sub-agent 3 must do, and an unsat core finds a clause
    against the request of the user.
- [**Escalation**][ESCALATION] (security chip): the escalation link of a
    toy OpenTitan, checked module by module: the RTL of each module
    implements its contract, and the contracts together refine the
    requirements, with no check on the whole design.
- [**LiftPlusCruise**][LPC] (aircraft): the requirements of the
    Lift-Plus-Cruise case study of [FRET][FRET], with real variables. They
    are consistent with a hover within 12 steps, not within 6, and the
    quotient by the mode logic says what the pilot must do.
- [**AHB**][AHB] (bus arbiter): the arbiter of the AMBA AHB bus as two
    viewpoints in SystemVerilog Assertions. Their merge is unrealizable
    until the masters release a locked bus, and is then synthesized.
- [**BufferSwap**][BUFFERSWAP] (circuit buffer swap): a buffer of BaseJump
    STL is replaced by a smaller one. The new buffer does not refine the old
    one, but it refines the quotient, the contract of its place; the RTL is
    checked with Yosys and nuXmv, and with Jasper.
- [**WarehouseRobot**][WAREHOUSE] (warehouse robot): the controller of a
    robot is delegated; the quotient by perception and localization is its
    contract, and requirements written for the mission alone fail it.
- [**Charger**][CHARGER] (charging station): one design iteration of an
    arbiter for two robots: an unrealizable arbiter, a realizable one, one
    that is not well separated, one that is vacuous, and the composition
    with the robots.
- [**LMFSM**][LMFSM] (autopilot): the state machine of the Lockheed Martin
    challenge; the unrealizable cores find the requirements in conflict, and
    the corrected autopilot and sensor refine the timed requirement.
- **RoboticJoints** and **CPSWeek22** (robotic joints): three joints
    refine the contract of a robotic arm and are synthesized; `scaling.py`
    measures the refinement for N joints. CPSWeek22 is the version shown at
    CPS-IoT Week 2022.
- **DATE18** and **FDL2024** (power systems and factories): requirements
    written in the domain-specific language of CHASE. `DATE18/eps.py` checks
    the power system of the DATE 2018 paper with the Python package: the
    requirements as written are unrealizable, with the core, and the relaxed
    ones are realizable.
- [**DATE21**][DATE21]: the hands-on tutorial of the DATE 2021 University
    Booth, with the console tools of CHASE.

The Python scripts use the CHASE Python package, version 0.5.0 or later
(`pip install chase-cps`; BufferSwap and Escalation with
`pip install "chase-cps[rtl]"`), and nuXmv and slugs, which `chase-cps
install` installs. The console scripts expect `dsl_tool`, `logics_tool`,
`slugs` (with its compiler, `$SLUGS/tools/StructuredSlugsParser/compiler.py`),
and `nuXmv` in the `PATH`. The Docker image of CHASE
(`ghcr.io/chase-cps/chase`, built from the [chase][CHASE] repository) has
all of them but nuXmv, whose license does not allow redistribution:
`chase-cps install nuxmv --accept-license` adds it in a container.

[WEB]: https://chase-cps.github.io
[DATE21]: DATE21/DATE21.md
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
