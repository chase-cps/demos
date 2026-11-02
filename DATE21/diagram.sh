#!/bin/sh
# Mission refines Target, Target does not refine Mission (Mission and Target
# drawn open), and System = Mission || Coordinator || Move || Turn || Pick || Place,
# with the checks of each part: compatible (A), consistent (G), realizable (R).
# --no-results runs every check again, so that the page keeps the counterexample.
cd "$(dirname "$0")" && mkdir -p out
chase-cps view specs/robotic_arm.ltl \
    --contracts Target Mission Mission+Coordinator+Move+Turn+Pick+Place \
    --refines Mission Target --refines Target Mission --check --verify --realizable \
    --open Mission Target --no-results -o out/robotic_arm.html

# Steps 3 and 4: the whole system, whose assumptions (A) and guarantees (G)
# can hold, and the coordinator, realizable (R).
python - <<'PY'
from chase_cps import is_realizable, load_spec, verify, viz
c = load_spec("specs/robotic_arm.ltl")
system = c["Mission"]
for name in ("Coordinator", "Move", "Turn", "Pick", "Place"):
    system = system.compose(c[name], name="System")
v = verify(system)
r = is_realizable(c["Coordinator"])
print(f"System: compatible {v.compatible.status}, consistent {v.consistent.status}; "
      f"Coordinator: {r.status}")
print(viz.save(viz.diagram(system, checks=[(system, v), (c["Coordinator"], "realizable", r)],
                           title="Pick-and-place arm: the whole system"),
               "out/robotic_arm-whole.html"))
PY
