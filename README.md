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
    in conflict in the other one.
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

The scripts expect `dsl_tool`, `logics_tool`, `gr1c`, `slugs`, and `nuXmv` to
be in the `PATH`. All of them are available in the Docker image of CHASE,
described in the [core-library][CORE] repository. The Python scripts use the
CHASE Python package (`pip install chase-cps`; Charger and LiftPlusCruise
need version 0.2.0, BufferSwap version 0.4.1 with `pip install
chase-cps[rtl]`).

[WEB]: https://chase-cps.github.io
[DATE21]: DATE21/DATE21.md
[CORE]: https://github.com/chase-cps/core-library
[FRET]: https://github.com/NASA-SW-VnV/fret
[CHARGER]: Charger/Charger.md
[LPC]: LiftPlusCruise/LiftPlusCruise.md
[BUFFERSWAP]: BufferSwap/BufferSwap.md
[LMFSM]: LMFSM/FSM.md
