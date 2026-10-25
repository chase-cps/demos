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

The scripts expect `dsl_tool`, `logics_tool`, `gr1c`, `slugs`, and `NuSMV` to
be in the `PATH`. All of them are available in the Docker image of CHASE,
described in the [core-library][CORE] repository.

[WEB]: https://chase-cps.github.io
[DATE21]: DATE21/DATE21.md
[CORE]: https://github.com/chase-cps/core-library
