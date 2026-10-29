## Delegation: a task of an AI agent split among sub-agents

The question: a parent agent splits a task among three sub-agents and
gives each one a contract over its tool calls. Do the sub-agents, together,
keep every rule of the user and deliver what the user asked for? If not,
what is missing, and who should do it?

This is the decomposition of a system contract into the contracts of its
components, with the components being AI agents and the behaviors being
their tool calls. The task is 530b157_1 of AppWorld (Trivedi et al., ACL
2024): pay a friend back on Venmo, with a given note, then text her. The
plan and the contracts are those of a run of ACORN, whose contracts are
those of ContrAgent: temporal formulas over the tool calls of an agent.

### Content of the directory
The directory of the demo contains:
- `requirements.txt`: the task, the plan, the variables, the rules of the
  user (H1 to H8), and the contracts of the sub-agents;
- `delegation.py`: the steps with the CHASE Python package.

### The contracts
- _Parent_ guarantees H: the rules of the user (the text after the
  payment, pay once, the note and the text word for word, no voice
  message) and what the user asked for (the payment, the text, the task
  marked complete).
- _Messages_ (sub-agent 1) finds the amount; it holds the tool of voice
  messages, so it keeps the rule of that tool.
- _Payment_ (sub-agent 2) is the only one with Venmo: it keeps the rules of
  Venmo and makes the payment.
- _Text_ (sub-agent 3) sends the text. From the rules of its tools alone it
  keeps H1, H4, and no voice message; as written in the run, it also sends
  the text (`F text3`), and starts when the payment is done.
- _Keep_: the parent marks the task complete.

### Python Flow
The script needs the CHASE Python package (`pip install chase-cps`, version
0.4.2) and nuXmv or NuSMV:

`$> python3 delegation.py`

It prints the result of each step:
1. The plan with the contracts from the tools alone does not refine
   _Parent_. In the counterexample the payment is made and the text is
   never sent: two sub-agents hold the tools to send it, and no contract
   asks either one to.
2. _Q3_ = _Parent_ / (_Messages_ ∥ _Payment_ ∥ _Keep_), the quotient with
   discharge, is what sub-agent 3 must do: the text after the payment, the
   text word for word, no voice message, and `F text3`.
3. _Text_, as written in the run, refines _Q3_, so the plan refines
   _Parent_.
4. If the parent also writes "never pay" (`G !tx2`), its contract is not
   consistent, and the unsat core names the two clauses in conflict: `F
   tx2` (deliver the payment) and the slip.

The quotient answers the question for the sub-agent with the open part of
the task: it is the weakest contract with which the plan meets the contract
of the parent. The formulas are read on infinite traces, as CHASE reads
them.

With `--expect` the script exits with code 1 when a result is not the
expected one.
