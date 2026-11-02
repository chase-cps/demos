## Contracts in C: each function checked against the clauses in its file

**The system.** Small C functions of controllers: the pump of a water
tank (`tank.c`), a ring buffer (`ring.c`), and a limit on the climb rate
of a drone (`climb.c`). Their contracts are written in the C file itself,
as the C checkers ESBMC, CBMC, and Frama-C read them: `requires` clauses
say what a call may assume (the assumptions of the contract), `ensures`
clauses what the function must give back (its guarantees). CHASE reads
these clauses, in any of the three syntaxes, and draws each function as
a component whose inputs are its parameters and whose output is its
return value. ESBMC (or CBMC) checks one call of the function against
its contract. The clauses CHASE reads are listed on the page
[C programs](https://chase-cps.github.io/tools/c-programs/).

**The question.** Does each function meet the contract written next to
it, and what does a failure look like? Code with no contract at all:
can it at least be checked for overflow? The same file then serves the
C checker and the contracts of a whole system.

<p align="center">
  <img src="images/system.png" alt="tank.c drawn: pump with the terms read from its clauses, and flow, with no clause" width="321">
  <br>
  <em>The system of <code>tank.c</code>: <code>pump</code>, with the terms read from its clauses, and <code>flow</code>, with none.</em>
</p>

### The steps

**Step 1. The pump meets its contract.** `pump` (clauses of ESBMC) runs
at full speed (3) from a level of 80 and is off below 20. Its function
button shows the code with its clauses. ESBMC proves that every call
within the assumed levels, 0 to 100, gives back what the contract asks
(the tag M ⊨ C: the code meets the contract). The tag A∧G says that the
terms can hold together.

<p align="center">
  <img src="images/step1-pump-meets-contract.png" alt="The code of pump with its ESBMC clauses, over the box of pump, its tags A∧G and M ⊨ C green" width="480">
  <br>
  <em>Step 1: the code of <code>pump</code> with its clauses; <code>pump</code> meets the contract read from them (M ⊨ C).</em>
</p>

**Step 2. Code with no clause.** `flow` divides the liters by the
seconds. It has no clause: its contract is (⊤, ⊤). M ⊨ C still asks
the code not to overflow, divide by zero, or go out of bounds;
`liters / seconds` overflows for `liters = -2147483648`, `seconds = -1`,
and the panel gives the line.

<p align="center">
  <img src="images/step2-flow-unsafe.png" alt="flow open, its contract (⊤, ⊤), its tag M ⊨ C red: the call on its ports, the overflow on line 25 in the panel">
  <br>
  <em>Step 2: <code>flow</code> does not meet even the contract (⊤, ⊤): its division overflows.</em>
</p>

**Step 3. The ring buffer, with and without the wrap.** `advance`
(clauses of CBMC) gives the next slot of a ring buffer of 8 slots, and
meets its contract. `advance_fast` does not wrap at the end: the slot
`i = 7` gives `ni = 8`, and the term `ni <= 7` is red. The values of the
failing call are on the ports.

<p align="center">
  <img src="images/step3-advance-fast-fails.png" alt="advance green; advance_fast red: i = 7 gives ni = 8, the term ni <= 7 red">
  <br>
  <em>Step 3: <code>advance</code> meets its contract, <code>advance_fast</code> does not.</em>
</p>

**Step 4. A contract in ACSL.** `climb.c` limits the climb rate of the
drone of the page [Drone climb](../DroneAltitude/DroneAltitude.md) to 3,
with its contract in an ACSL comment, `/*@ ... */`, the language of
Frama-C. `limit` meets it (ESBMC checks it; Frama-C is not run).
`limit_loose` tests the top with `v > 4`, so `v = 4` gives 4.

<p align="center">
  <img src="images/step6-limit-loose-fails.png" alt="limit green; limit_loose red: v = 4 gives 4, the term limit_loose_out <= 3 red">
  <br>
  <em>Step 4: <code>limit</code> meets its ACSL contract, <code>limit_loose</code> does not.</em>
</p>

Once read, a function is a contract like any other: it can be composed
with the others and checked against the contract of a system, as in
[Fire-suppression drones in C](../DroneGrid/DroneGrid.md). The tags of
the pictures are explained on the page
[Diagrams](https://chase-cps.github.io/interfaces/diagrams/#what-is-drawn).

### Run it

```
pip install "chase-cps[z3]"      # and ESBMC or CBMC
python contractsinc.py --expect
```

### Content of the directory
- `tank.c`, `ring.c`, `climb.c`: the functions, with their clauses;
- `contractsinc.py`: the steps with the CHASE Python package;
- `*.results.json`: the results of `chase-cps view FILE.c --check`;
- `out/*.html`: the diagrams, written by `contractsinc.py`;
  `out/tank-system.html`: `tank.c` with no check.
