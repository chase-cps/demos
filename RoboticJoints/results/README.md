# RoboticJoints scaling results

`scaling.csv` and `scaling.pdf` were produced by

````
python scaling.py --joints 1 2 3 4 5 6 7 8 --broken --csv results/scaling.csv
python scaling.py --joints 1 2 3 4 5 6 7 8 --broken --discharge \
    --csv results/scaling_discharge.csv
python plot_scaling.py results/scaling.csv results/scaling_discharge.csv
````

`--discharge` composes with `compose(..., discharge=True)` (chase-cps after
0.1.0).

Machine: Apple M4 Pro, 24 GB RAM, macOS 26.5. nuXmv 2.2.0 (IC3), Python 3.13.
`scaling.csv`: chase-cps 0.1.0; `scaling_discharge.csv`: chase-cps 0.3.2.

Columns:

- `compose_s`: time to compose the N joint contracts.
- `refine_s`, `verdict`: time and result of the check that the composition
  refines the arm contract. The check is two implications (assumptions and
  guarantees), each stopped after 600 s; `timeout` means one of them was
  stopped.
- `cex_s`, `cex_length`, `cex_verdict`: the same check for the broken
  version (Joint1 without `G F j1_done`), and the length of the
  counterexample (prefix plus loop).

The correct version is checked up to 5 joints (84 s); from 6 joints the
guarantee check does not finish in 600 s. The counterexample of the broken
version is found up to 8 joints.

With `--discharge` the composite keeps the terms of the joint contracts, and
the refinement is proved up to 8 joints in 3.3 s. The composition itself
takes 21 s for 8 joints: the redundant terms are removed after each of the
7 compositions, one nuXmv call per term. The joints share no variable, so no
assumption is discharged here, and each call has only the terms of one
joint: a term is implied by the others iff it is implied by those that
share variables with it, when all the terms are satisfiable (chase-cps
0.3.2). `discharge_speedup.csv` compares the composition time before (0.3.1,
140 s for 8 joints) and after, on the same machine; the composite contracts
are the same. The gain comes from the form of the
composite: it is the list of the joint terms, the same terms as the arm
contract, instead of the nested formula (A1 & A2) | !(G1 & G2) of the closed
form.
