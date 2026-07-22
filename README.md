# evalkit

A thin protocol for **evaluations**. It encodes five principles I keep arriving at
across very different eval problems, and it enforces the load-bearing ones in code.

The same protocol expresses three graders drawn from real projects:

| Grader | From | Validation | Judges |
|---|---|---|---|
| **substance fidelity** | [blogAI_evals](https://github.com/tyakovenko/blogAI_evals) | empirical (vs human-gold + null floor) | a transformed output vs its source |
| **calibration (Brier)** | [fishy](https://github.com/tyakovenko/fishy) | by construction (proper scoring rule) | a probabilistic prediction vs outcome |
| **trajectory (safety-spec)** | [tlaGuards](https://github.com/tyakovenko/tlaGuards) → octopus | by construction (a formal spec) | an agent's whole tool-call trace |

## The five key ideas

1. **The grader is the experiment.** Before you measure the system, measure the
   measurer. `run_eval` **refuses to run an unvalidated grader** to avoid confident noise. Validate empirically or establish correctness by construction (a proper scoring
   rule, a formal spec).

2. **Grade the trajectory, not the final state.** The failures that matter are
   invisible to an outcome score: the claim survives but the reasoning is dropped;
   the code "deployed successfully" but was never tested. An `item` can be a whole
   trajectory, so the grader can see the path.

3. **Always show the baseline.** A number alone means nothing. Beat a coin flip
   (Brier vs 0.75), a standalone model, an unguarded agent. `EvalReport` cannot be
   built without a baseline; the comparison *is* the finding.

4. **Report the null.** When the intervention does nothing (a guard that never
   fires on clean inputs) or backfires (an edit pass that lowers quality), that is
   the result. Dropping it is how eval theater happens.

5. **Two graders: guard + judge.** Deterministic/formal checks for hard invariants,
   an LLM judge for the fuzzy rest. This is where the methodology graduates from a
   study into an architecture: it is the guard/judge layer of the octopus agent
   orchestrator, prototyped in tlaGuards.

## Run it

```bash
python examples/demo_trajectory.py    # guarded vs unguarded: catches "deployed untested"
python examples/demo_calibration.py   # model vs coin flip on Brier
```

Core is pure-Python (no heavy deps). The fidelity grader needs
`sentence-transformers` (see requirements.txt); the other two run as-is.

## Shape

```
evalkit/
  protocol.py        Grader ABC, validation gate, run_eval, EvalReport
  stats.py           Spearman (pure Python)
  graders/
    fidelity.py      empirical validation, the one that must be checked against gold
    calibration.py   by-construction (Brier)
    trajectory.py    by-construction (safety spec; formal version in tlaGuards)
examples/            runnable demos
docs/methodology.md  the long-form version
```

The three graders are deliberately different mechanically (cosine, Brier,
model-checking). They are **not** merged into one pipeline; that would be theater.
What they share is the *protocol*: validate the grader, show the baseline, grade
the path, report the null.
