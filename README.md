# CHASE demos

This repository contains the demonstrations of [CHASE][WEB]:

- **DATE18**: specification files used to produce the experimental results
    presented in the DATE 2018 paper.
- [**DATE21**][DATE21]: specification files used during the hands-on tutorial
    presented at the DATE 2021 University Booth.
- **CPSWeek22**: demonstration presented at CPS-IoT Week 2022, about the
    verification and synthesis of the controller of a robotic arm, using both
    a single model and a compositional model.
- **RoboticJoints**: extended version of the robotic arm demonstration.
    `scaling.py` builds the same contracts for N joints with the CHASE Python
    package and measures the time of the refinement check.
- **FDL2024**: DSL specification of a small factory.
- [**Charger**][CHARGER]: two robots sharing a charging station through an
    arbiter. One design iteration of the arbiter: the unrealizable core of a
    first arbiter, the synthesis of a second one, the well-separation check,
    the removal of vacuous guarantees, and the composition with discharge of
    the arbiter and the robots, which feed each other.
- [**LiftPlusCruise**][LPC]: requirements of the Lift-Plus-Cruise case study
    of [FRET][FRET], with real variables. The consistency of two subsets of
    the requirements, a behavior of the consistent one, and the requirements
    in conflict in the other one; then the quotient of the deadline by the
    mode logic, which says what the pilot must do to hover in time.
- [**BufferSwap**][BUFFERSWAP]: the replacement of a buffer of a circuit
    (BaseJump STL), with contracts in SystemVerilog Assertions. The new
    buffer does not refine the old one, but it refines the quotient of the
    system by its neighbours, so it can replace it; the quotient is written
    as SVA and checked on the RTL with Yosys and nuXmv, and with Jasper.
- [**LMFSM**][LMFSM]: the finite state machine of the Ten Lockheed Martin
    Cyber-Physical Challenges, an autopilot and a sensor. The unrealizable
    cores of the requirements as first written, fixed one by one; the
    composition of the corrected autopilot and sensor, which does not give
    the pullup at once, and the time it takes.
- [**AHB**][AHB]: the arbiter of the AMBA AHB bus (Bloem et al., COCV 2007),
    simplified, as two viewpoints in SystemVerilog Assertions. Their merge is
    unrealizable without the assumption that a master releases a locked bus,
    with the requirements in conflict as its core; with it, it is
    synthesized and written as SVA.
- [**WarehouseRobot**][WAREHOUSE]: the local controller of a warehouse robot is
    delegated (Damera, Matheu, Baras, 2026). The quotient of the system by
    perception and localization is its contract, with the bound on the yaw
    rate that perception assumes; the requirements written for the mission
    alone do not refine it.
- [**Escalation**][ESCALATION]: the escalation link of a security chip (a
    toy version of the one of OpenTitan), checked module by module: the RTL
    of each module implements its contract in SVA, and the composition of
    the contracts refines the requirements, with no check on the whole
    design. A faster sender breaks its contract, and the link with it.
- [**PaymentAssistant**][PAYMENT]: a task in natural language (AppWorld) becomes the
    contract of an AI agent, over its tool calls, decomposed among three
    sub-agents. The decomposition misses a deliverable; the quotient says
    which sub-agent must do it; an unsat core finds a clause that
    contradicts the rules of the user.

The scripts expect `dsl_tool`, `logics_tool`, `slugs` (with its compiler,
`$SLUGS/tools/StructuredSlugsParser/compiler.py`), and `nuXmv` to be in the
`PATH`. All of them are available in the Docker image of CHASE,
described in the [core-library][CORE] repository. The Python scripts use the
CHASE Python package, version 0.5.0 or later, which draws the diagrams
(`pip install chase-cps`; BufferSwap and Escalation with
`pip install chase-cps[rtl]`).

[WEB]: https://chase-cps.github.io
[DATE21]: DATE21/DATE21.md
[CORE]: https://github.com/chase-cps/core-library
[FRET]: https://github.com/NASA-SW-VnV/fret
[CHARGER]: Charger/Charger.md
[LPC]: LiftPlusCruise/LiftPlusCruise.md
[BUFFERSWAP]: BufferSwap/BufferSwap.md
[LMFSM]: LMFSM/FSM.md
[AHB]: AHB/AHB.md
[WAREHOUSE]: WarehouseRobot/WarehouseRobot.md
[PAYMENT]: PaymentAssistant/PaymentAssistant.md
[ESCALATION]: Escalation/Escalation.md
