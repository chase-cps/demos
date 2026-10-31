## Resource arbiter: the least bound on a waiting time

**The question.** A client waits for a resource that an arbiter grants every
third step. What is the least bound `k` such that no request waits more
than `k` steps?

**What it shows.**
- Counterexample over an infinite run (LTL, nuXmv): a request made at
  `c = 0` is granted at `c = 2`, after waiting 2 steps, and the run loops.
- Repair by counterexamples: `k = 2`, the least value, in 2 rounds and
  0.1 s, each candidate checked by nuXmv.
- The same answer by brute force: checking `k = 0, 1, ..., 9` one by one,
  2 is the least that passes.

<p align="center">
  <img src="images/before-and-after-repair.png" alt="Before the repair (k = 1, red) and after it (k = 2, green)">
  <br>
  <em>Before the repair (k = 1, ⪯ red) and after it (k = 2, green).</em>
</p>

The contracts are in `deadline.ltl`:

- `Client`: once it asks (`req`), it keeps asking until it is granted.
- `Arbiter`: a counter `c` goes 0, 1, 2, 0, ...; it grants (`grant`) when
  `c = 2`.
- `Wait`: `w` counts the steps a request has waited, and is 0 again once
  the request is granted or withdrawn.
- `Bound`: the requirement `G (w <= k)`, with the named constant `k` (θ in
  the diagram) at 1.

The formulas are LTL over an infinite run, so nuXmv checks them.

### The steps

**Step 1. The bound is too small.** The composition of `Client`, `Arbiter`,
and `Wait` does not refine `Bound`. In the counterexample, a request at
`c = 0` is granted at `c = 2`: it waits 2 steps (`w = 2`), and the run
goes back to step 0.

<p align="center">
  <img src="images/wait-counterexample.png" alt="The panel of the check of Bound: the counterexample, w = 0, 1, 2 while c = 0, 1, 2, step 2 on the ports; the guarantee G (w <= k) in red">
  <br>
  <em>The counterexample: w reaches 2 at step 2, when the grant comes.</em>
</p>

**Step 2. Repair the bound.** `repair` finds `k = 2`, the least value. Each
round optimizes `k` under the conditions that the counterexamples found so
far are no longer counterexamples (a counterexample with `w = 2` gives
`k >= 2`), then checks the refinement with nuXmv. Two rounds: `k = 1`
fails, `k = 2` passes. Because each condition only removes values that
cannot work, the value that passes is the least. `k` belongs to the
requirement, so the viewer changes it only when it is picked.

<p align="center">
  <img src="images/repair-k.png" alt="Find repairs with k picked: k 1 to 2, optimal, change 1; the diagram shows the new value">
  <br>
  <em>Find repairs, k picked: 1 → 2, optimal.</em>
</p>

**Step 3. Check every value.** Checking `k = 0, 1, ..., 9` one by one with
nuXmv gives the same answer: 2 is the least that passes.

### Content of the directory
The directory of the demo contains:
- `deadline.ltl`: the contracts of the client, the arbiter, the counter of
  the wait, and the requirement. The line `# view:` at the top gives the
  refinement that `chase-cps view` draws;
- `deadline.py`: the steps with the CHASE Python package;
- `deadline.results.json`: the results of `chase-cps view deadline.ltl --check`;
- `out/deadline.html`: the diagram before and after the repair, written by
  `deadline.py`.

### Run it

```
pip install "chase-cps[z3]"      # and nuXmv: chase-cps install nuxmv --accept-license
python deadline.py --expect
chase-cps view deadline.ltl --check -o out/deadline-view.html
chase-cps repair deadline.ltl --refines Client+Arbiter+Wait Bound --param k=0..9:int
chase-cps view deadline.ltl --check --serve                   # Find repairs in the page
```
