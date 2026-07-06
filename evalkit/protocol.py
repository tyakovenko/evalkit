"""
evalkit — a thin protocol for evaluations you can trust.

The methodology is enforced in code, not just documented:

  1. The grader is the experiment.  `run_eval` REFUSES an unvalidated grader.
  2. Grade the trajectory, not the final state.  An `item` is whatever the grader
     judges — a text output, a (notes, output) pair, or a whole agent trajectory.
  3. Always show the baseline.  `run_eval` requires a baseline condition; the
     report is built around the comparison, not a lone number.
  4. Report the null.  Every condition (including "the intervention did nothing")
     appears in the report; nothing is dropped for being unflattering.

Each grader in graders/ is drawn from a real project (see README).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from statistics import mean


@dataclass
class Validation:
    """The result of checking the grader itself (principle 1)."""
    method: str            # "empirical" | "by-construction"
    passed: bool
    detail: str
    correlation: float | None = None
    null_score: float | None = None


class Grader(ABC):
    """Scores an item in [0, 1], higher = better.

    A grader must be validated before an eval will run it. There are two honest
    ways to validate (principle 1): correlate it against human-gold labels with a
    null floor, or establish that it is correct by construction (a proper scoring
    rule, a formal spec). Both set `validated`.
    """
    name: str = "grader"

    def __init__(self) -> None:
        self._validation: Validation | None = None

    @abstractmethod
    def grade(self, item) -> float:
        ...

    # --- Principle 1, empirical form: validate against gold + a null floor ---
    def validate_empirical(
        self,
        gold: list[tuple[object, float]],
        null: list[object],
        *,
        min_corr: float = 0.5,
        null_ceiling: float = 0.5,
    ) -> Validation:
        """gold: [(item, human_score)]; null: items expected to score low.

        Passes only if the grader tracks human judgement (Spearman >= min_corr)
        AND known-bad inputs stay under the floor. This is the blogAI-evals gate.
        """
        from evalkit.stats import spearman

        g_items = [g[0] for g in gold]
        g_human = [g[1] for g in gold]
        g_pred = [self.grade(i) for i in g_items]
        corr = spearman(g_pred, g_human)
        null_mean = mean(self.grade(i) for i in null) if null else 0.0
        passed = corr >= min_corr and null_mean <= null_ceiling
        self._validation = Validation(
            "empirical",
            passed,
            f"Spearman rho={corr:.3f} (need >= {min_corr}); "
            f"null mean={null_mean:.3f} (need <= {null_ceiling})",
            correlation=corr,
            null_score=null_mean,
        )
        return self._validation

    # --- Principle 1, construction form: correctness by design ---
    def validate_by_construction(self, reason: str) -> Validation:
        """For graders whose correctness comes from construction, not from
        correlating with a fuzzy label — a proper scoring rule (Brier) or a
        formal spec / model checker (see the trajectory grader + tlaGuards)."""
        self._validation = Validation("by-construction", True, reason)
        return self._validation

    @property
    def validated(self) -> bool:
        return self._validation is not None and self._validation.passed


@dataclass
class ConditionResult:
    name: str
    n: int
    mean_score: float
    scores: list[float]


@dataclass
class EvalReport:
    grader: str
    validation: Validation
    baseline: ConditionResult          # principle 3: never optional
    conditions: list[ConditionResult]

    def edge_over_baseline(self) -> dict[str, float]:
        return {c.name: c.mean_score - self.baseline.mean_score for c in self.conditions}

    def __str__(self) -> str:
        lines = [
            f"Grader: {self.grader}",
            f"  validation ({self.validation.method}): "
            f"{'PASS' if self.validation.passed else 'FAIL'} — {self.validation.detail}",
            f"  baseline [{self.baseline.name}]: {self.baseline.mean_score:.3f} (n={self.baseline.n})",
        ]
        edges = self.edge_over_baseline()
        for c in self.conditions:
            lines.append(
                f"  {c.name:16} {c.mean_score:.3f} (n={c.n})   edge {edges[c.name]:+.3f}"
            )
        return "\n".join(lines)


def _score_condition(grader: Grader, name: str, items: list) -> ConditionResult:
    scores = [grader.grade(i) for i in items]
    return ConditionResult(name, len(scores), mean(scores) if scores else 0.0, scores)


def run_eval(
    grader: Grader,
    conditions: dict[str, list],
    baseline: tuple[str, list],
) -> EvalReport:
    """Score each condition with the grader and compare against the baseline.

    Enforces principle 1: a grader that has not passed validation raises, rather
    than silently producing confident noise.
    """
    if not grader.validated:
        raise RuntimeError(
            f"Grader {grader.name!r} is not validated. Call validate_empirical() "
            "or validate_by_construction() (and pass) before running an eval — "
            "an unvalidated grader is confident noise."
        )
    base_name, base_items = baseline
    return EvalReport(
        grader=grader.name,
        validation=grader._validation,  # present: validated is True
        baseline=_score_condition(grader, base_name, base_items),
        conditions=[_score_condition(grader, n, items) for n, items in conditions.items()],
    )
