# How I think about evals

The long-form version of the five principles, with the evidence each one came from.

## 1. The grader is the experiment
Most eval failures are grader failures wearing a metric's clothes. A rubric that
doesn't track human judgement, or an LLM judge that rewards length, will produce a
clean-looking number that means nothing. So the first experiment is on the grader,
not the system.

Two honest ways to earn trust:
- **Empirical** — correlate the grader against human-gold labels and check that
  known-bad inputs stay under a floor. In blogAI_evals this was a hard gate:
  substance ρ = 0.926, voice ρ = 0.876 against human-edited gold, with null
  baselines setting the floor, *before* any generation ran.
- **By construction** — a proper scoring rule (Brier) or a formal spec (TLA+/TLC)
  is correct by design; there is no fuzzy label to correlate against. fishy's
  calibration and tlaGuards' safety spec are this kind.

`evalkit` enforces this: `run_eval` raises on an unvalidated grader.

## 2. Grade the trajectory, not the final state
A final-state eval scores the last thing that happened. The dangerous failures are
one level up:
- blogAI_evals' **flattening flag**: the headline claim survives, the reasoning
  that made it worth writing is gone. A single quality score misses it.
- tlaGuards: under "the suite is flaky, just ship it," the agent did `Build → Deploy`
  and the last tool result was "Deployed to production successfully." A final-state
  eval passes that run. The trajectory spec catches that it deployed *untested*.

## 3. Always show the baseline
The comparison is the finding, not the absolute number:
- fishy: Brier vs a coin flip (0.75) and vs always-up base rate.
- blogAI_evals: the cheap Qwen→Haiku pipeline vs Haiku standalone (LinkedIn 0.663
  vs 0.624, paired Wilcoxon p = 0.030).
- tlaGuards: guarded vs unguarded (violations 0/12 vs 6/12).

## 4. Report the null
- tlaGuards: on clean prompts the guard never fired — reported as a result, not
  hidden. The guard only earns its keep under stress.
- blogAI_evals: the Haiku edit pass *lowered* substance rather than raising it.

A framework that only surfaces wins is a marketing tool.

## 5. Two graders: guard + judge
Deterministic/formal checks for the invariants that must never break; an LLM judge
for everything fuzzy. This is the design of the octopus orchestrator's review
layer — a procedural guard at the Agent SDK `PreToolUse` hook plus a model judge —
and tlaGuards is the shipped proof that the formal half works. The eval work is
where each grader type gets validated before it is trusted to gate a live agent.

That last step is the whole point: an eval methodology is only finished when it can
sit in the loop of a running system, not just score a spreadsheet after the fact.
