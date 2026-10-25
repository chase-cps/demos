# RoboticJoints scaling results

`scaling.csv` and `scaling.pdf` were produced by

````
python scaling.py --joints 1 2 3 4 5 6 7 8 --broken --csv results/scaling.csv
python plot_scaling.py
````

Machine: Apple M4 Pro, 24 GB RAM, macOS 26.5. chase-cps 0.1.0, nuXmv 2.2.0
(IC3), Python 3.13.

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
