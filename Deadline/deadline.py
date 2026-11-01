"""Deadline: the least bound on the waiting time of a request.

A client asks for a resource and keeps asking until it is granted; the
arbiter grants every third step; Wait counts the steps a request has waited
(deadline.ltl). The requirement MaxWait says that no request waits more than
the constant k (1). The formulas are LTL, so nuXmv checks them. This script
uses the CHASE Python package (pip install chase-cps):

  1. Client, Arbiter, and Wait composed do not refine MaxWait: a request can
     wait 2 steps.
  2. repair finds the least k: 2. Each round optimizes k under the
     conditions that the counterexamples found so far are no longer
     counterexamples, then checks the refinement with nuXmv.
  3. Every k from 0 to 9, checked one by one, gives the same answer: 2 is
     the least that passes.
  4. The arbiter as a state machine (arbiter.smv): it implements Arbiter,
     and it is receptive: it takes every request that the assumption of
     Arbiter allows. The same machine with a constraint on its input
     (refusing.smv) still implements Arbiter, but only because it refuses
     a request: it is not receptive.
  5. The client as a state machine (client.smv) is an environment of
     Arbiter: it holds a request until it is granted, as Arbiter assumes.
     A client that may give up (impatient.smv) is not.

The page out/deadline.html draws the system inside MaxWait with k = 1 (red)
and k = 2 (green), and the arbiter with its state machine, driven by the
two clients.

    python deadline.py
    python deadline.py --expect     # exit code 1 when a result is not the expected one

The checks need nuXmv (or NuSMV) and z3.
"""

import os
import sys

from chase_cps import (Component, Model, is_environment, is_implementation, is_receptive, load_spec,
                       System, refines, repair, viz)

HERE = os.path.dirname(os.path.abspath(__file__))


def main(expect: bool) -> int:
    c = load_spec(os.path.join(HERE, "deadline.ltl"))
    system = c["Client"].compose(c["Arbiter"]).compose(c["Wait"])
    bound = c["MaxWait"]
    results = []

    def show(step, text, got, want):
        results.append(got == want)
        mark = "" if got == want else f"   (expected {want})"
        print(f"{step}. {text}: {got}{mark}")

    r = refines(system, bound)
    show(1, "the system refines MaxWait with k = 1", r.status, "invalid")
    if r.guarantees.trace is not None:
        print("   counterexample:")
        print("\n".join("   " + line for line in str(r.guarantees.trace).splitlines()))

    r = repair("refines", system, bound, parameters={"k": (0, 9, "int")})
    show(2, "the least k", r.values, {"k": 2})
    print(f"   optimal {r.optimal}, {r.method} in {r.rounds} rounds, "
          f"checked by {r.check.guarantees.backend}")

    passing = [k for k in range(10)
               if refines(system, bound.instantiate({"k": k})).status == "valid"]
    show(3, "the least k that passes, checking every k", passing[0] if passing else None, 2)
    def model(name):
        with open(os.path.join(HERE, name + ".smv"), encoding="utf-8") as f:
            return Model.from_smv(f.read(), name=name)

    arbiter, refusing = model("arbiter"), model("refusing")
    impl = is_implementation(arbiter, c["Arbiter"])
    show(4, "arbiter.smv implements Arbiter", impl.status, "valid")
    recep = is_receptive(arbiter, c["Arbiter"])
    show(4, "arbiter.smv is receptive", recep.status, "receptive")
    show(4, "refusing.smv implements Arbiter", is_implementation(refusing, c["Arbiter"]).status, "valid")
    refused = is_receptive(refusing, c["Arbiter"])
    show(4, "refusing.smv is receptive", refused.status, "not_receptive")
    if refused.details:
        print(f"   it refuses {refused.details.get('input')} after {refused.details.get('state')}")
    envs = []
    for name, want in (("client", "valid"), ("impatient", "invalid")):
        e = is_environment(model(name), c["Arbiter"])
        show(5, f"{name}.smv is an environment of Arbiter", e.status, want)
        if e.status == "invalid" and e.trace is not None:
            print("\n".join("   " + line for line in str(e.trace).splitlines()))
        envs.append((Component(name, c["Client"], model(name)), e))
    # the page: before and after the repair, and the arbiter with its machine
    pairs = []
    for k in (1, 2):
        both = c["Client"].compose(c["Arbiter"]).compose(c["Wait"])
        b = bound.instantiate({"k": k}, name="MaxWait" if k == 1 else "MaxWait_repaired")
        pairs.append((both, b, refines(both, b)))
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    box = Component("Arbiter", c["Arbiter"], arbiter, status=impl)
    page = viz.save(viz.diagram(box, refines=pairs, open=[b for _, b, _ in pairs] + [box],
                                checks=[(box, recep)],
                                environments=[(e, box, r) for e, r in envs],
                                title="Deadline: before and after the repair; the arbiter as a state machine"),
                    os.path.join(HERE, "out", "deadline.html"))
    # the system alone, without the results: the client, the arbiter, and the
    # counter of the wait, in the requirement
    alone = System("Arbitration", [Component(n, c[n]) for n in ("Client", "Arbiter", "Wait")],
                   contract=bound)
    viz.save(viz.diagram(alone, open=[bound], results=False,
                         title="Resource arbiter: the client, the arbiter, and the wait"),
             os.path.join(HERE, "out", "deadline-system.html"))
    print(f"\nThe diagram: {os.path.relpath(page, HERE)}")
    return 0 if all(results) or not expect else 1


if __name__ == "__main__":
    import importlib.util
    if importlib.util.find_spec("z3") is None:      # the repair and the formulas over reals
        sys.exit('This demo needs z3: pip install "chase-cps[z3]"')
    sys.exit(main("--expect" in sys.argv))
