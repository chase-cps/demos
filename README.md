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

The scripts expect `dsl_tool`, `logics_tool`, `gr1c`, `slugs`, and `nuXmv` to
be in the `PATH`. All of them are available in the Docker image of CHASE,
described in the [core-library][CORE] repository. The Python scripts use the
CHASE Python package (`pip install chase-cps`; Charger and LiftPlusCruise
need version 0.2.0).

[WEB]: https://chase-cps.github.io
[DATE21]: DATE21/DATE21.md
[CORE]: https://github.com/chase-cps/core-library
[FRET]: https://github.com/NASA-SW-VnV/fret
[CHARGER]: Charger/Charger.md
[LPC]: LiftPlusCruise/LiftPlusCruise.md
