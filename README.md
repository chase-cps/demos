# CHASE demos

This repository contains the demonstrations of [CHASE][WEB]. Each one
follows a design problem from its requirements to a result; its page on the
website and its README show each step with its diagram.

They are grouped by the kind of system; the website has the same groups.

### AI agents

- [**PaymentAssistant**][PAYMENT]: the plan of an AI agent, split among
  three sub-agents, checked before it runs; the quotient says which
  sub-agent must send the text.

### Aircraft and vehicles

- [**LiftPlusCruise**][LPC]: the requirements of a NASA aircraft are
  consistent with a hover in 12 steps, not in 6; the quotient says what the
  pilot must do.
- [**LMFSM**][LMFSM]: the Lockheed Martin autopilot: the unrealizable cores
  find the requirements in conflict, fixed one at a time.
- [**DATE18**][DATE18]: an aircraft power system in the domain-specific
  language: the bounds as written conflict; relaxed, they are realizable.

### Hardware

- [**Escalation**][ESCALATION]: the escalation link of the OpenTitan
  security chip, proven module by module from its RTL.
- [**BufferSwap**][BUFFERSWAP]: a smaller circuit buffer fails the old
  contract, but refines the quotient: the contract of its slot.
- [**AHB**][AHB]: the AMBA AHB bus arbiter: two viewpoints that cannot be
  merged, the assumption that fixes them, and the arbiter synthesized.
- [**Deadline**][DEADLINE]: a resource arbiter: the least bound on the
  waiting time of a request, repaired from counterexamples; the arbiter and
  its client as state machines in SMV.

### Software

- [**ContractsInC**][CONTRACTSINC]: the contract written in the C file
  (ESBMC, CBMC, or ACSL clauses), checked function by function.
- [**DroneGrid**][DRONEGRID]: a collision of two drones found and fixed on
  the contracts, then each C function checked against its contract.

### Drones and robots

- [**DroneAltitude**][DRONEALTITUDE]: a drone climbs in the wind; no climb
  rate is enough, and repair says what the requirement can ask, one
  constant or two.
- [**Charger**][CHARGER]: a robot charging station: refinement does not see
  the conflict, realizability does.
- [**RoboticJoints**][ROBOTICJOINTS]: three joints of a robotic arm, checked
  and synthesized one at a time; the check scales to 8 joints.
- [**DATE21**][DATE21]: a pick-and-place arm: the mission refines the
  target, and the coordinator is synthesized.
- [**DroneTiming**][DRONETIMING]: the timing of fire-suppression drones as a
  linear program: a faster timer fails, and repair finds the least bound or
  a faster planner.

### Buildings

- [**Heater**][HEATER]: a room thermostat: repair finds the threshold,
  ESBMC checks its C code, and the check between the samples holds in
  continuous time.

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

### Other folders

Four folders are in the repository but not on the website: [**Braking**][BRAKING] and
[**WarehouseRobot**][WAREHOUSE] (their steps are shown by DroneTiming and LiftPlusCruise),
and FDL2024 and CPSWeek22, added by other authors: [**FDL2024**][FDL2024]
is a factory gate controller in the domain-specific language, and
[**CPSWeek22**][CPSWEEK22] the robotic arm as shown at CPS-IoT Week 2022.
They still run.

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
