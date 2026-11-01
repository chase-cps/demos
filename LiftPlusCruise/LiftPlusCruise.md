## NASA Lift-Plus-Cruise aircraft: what the pilot must do to hover in time

**The question.** Some flights meet the requirements and hover within 12
steps. What must the pilot do so that every flight does?

**The result.**
- Within 12 steps the requirements are consistent; within 6 they are not:
  the unsat core (the smallest set of requirements in conflict) is 8.
- The quotient Q12, the weakest contract the pilot must meet, is refined
  neither by a pilot with the requirements alone nor by one that only
  slows down.
- _Decel_, which also turns on the hover control, refines Q12.

<p align="center">
  <img src="images/overview-requirements-and-pilots.png" alt="Reach12: ModeLogic, and the quotient Q12 with the pilot Pilot in it" width="870">
  <br>
  <em>The split of the vehicle: ModeLogic, and the quotient Q12, what the pilot must do, with a candidate pilot in it.</em>
</p>

Lift-Plus-Cruise is a NASA aircraft that hovers on lift rotors and
cruises on a wing. The requirements come from the LPC_mini project of
[FRET](https://github.com/NASA-SW-VnV/fret) (Pressburger et al., REFSQ
2023), on real variables (the SMT engine of nuXmv). The mode logic sets the
lift mode from the airspeed `kias`, the ground speed `kgs`, and the hover
control, set by the pilot.

### The steps

**Step 1. Two deadlines.** Within 12 steps the requirements are
consistent; within 6 they are not. The core, 8 requirements, says why:
`kias` starts at 120 and changes by at most 10 per step, and the vehicle
stays wing borne above 90, then semi wing borne above 30: it cannot hover
by step 6.

<p align="center">
  <img src="images/step1-reach06-inconsistent-core.png" alt="Step 1: Vehicle_Reach12, green; Vehicle_Reach06, red, with the terms of the core" width="733">
  <br>
  <em>Step 1: consistent with 12 steps, not with 6; the core in red.</em>
</p>

**Step 2. The split.** _ModeLogic_ ⊗ _Pilot_ refines _Vehicle_, the
requirements without a deadline.

<p align="center">
  <img src="images/step2-mode-logic-and-pilot.png" alt="Step 2: Vehicle with Pilot and ModeLogic inside; the refinement holds" width="661">
  <br>
  <em>Step 2: the split refines the vehicle.</em>
</p>

**Step 3. What the pilot must do.** Q12 = Reach12 / ModeLogic, the dashed
box, is the weakest contract of the pilot with which every flight hovers
in time. _Pilot_ does not refine it: `kias` may stay at 120.

<p align="center">
  <img src="images/step3-pilot-does-not-refine-q12.png" alt="Step 3: Pilot inside Q12; red, with the counterexample">
  <br>
  <em>Step 3: Pilot does not refine Q12: <code>kias</code> stays at 120.</em>
</p>

**Step 4. A pilot that slows down.** _Slow_ lowers `kias` by 10 per step, but
never turns the hover control on: it does not refine Q12.

<p align="center">
  <img src="images/step4-slow-does-not-refine-q12.png" alt="Step 4: Slow inside Q12; red, with the counterexample">
  <br>
  <em>Step 4: Slow slows down, but never turns the hover control on.</em>
</p>

**Step 5. A pilot that turns on the hover control.** _Decel_ also turns
the hover control on when `kgs` is below 20, and refines Q12. It does not
refine Q06 = Reach06 / ModeLogic: at step 6 the vehicle is still semi wing
borne.

<p align="center">
  <img src="images/step5-decel-refines-q12.png" alt="Step 5: Decel inside Q12; the refinement holds" width="598">
  <br>
  <em>Step 5: Decel refines Q12.</em>
</p>

<p align="center">
  <img src="images/step6-decel-does-not-refine-q06.png" alt="Step 5: Decel inside Q06; red, with the counterexample">
  <br>
  <em>Step 5: Decel does not refine Q06.</em>
</p>

### Run it

```
pip install chase-cps
chase-cps install nuxmv --accept-license
python lpc.py --expect
```

### Content of the directory
- `requirements.txt`: the requirements in FRETish;
- `lpc.ltl`: the three contracts; the comment at the end of each line
  names the requirement;
- `lpc.chase`: step 1 with `logics_tool`;
- `lpc.py`: the steps with the CHASE Python package;
- `lpc.results.json`: the results of `chase-cps view --check`;
- `out/lpc.html`: the diagrams above, written by `lpc.py`.
