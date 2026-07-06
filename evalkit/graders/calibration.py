"""
Calibration grader — drawn from `fishy` (the legislation/trade pipeline's eval).

Scores a probabilistic prediction by how well-calibrated it was, using the Brier
score (a *proper* scoring rule — you cannot game it by hedging). Item is a
prediction: (p_up, outcome_up), where p_up in [0,1] is the model's probability
the thing went up and outcome_up in {0,1} is what actually happened.

score = 1 - (p_up - outcome)^2   → 1.0 perfect, 0.75 for a coin flip, 0.0 worst.

Validation is by construction: Brier is a proper scoring rule, so a lower score
genuinely means worse calibration — no human-label correlation needed.
"""
from __future__ import annotations

from evalkit.protocol import Grader


class CalibrationGrader(Grader):
    name = "calibration (Brier)"

    def __init__(self) -> None:
        super().__init__()
        self.validate_by_construction(
            "Brier is a strictly proper scoring rule; 1-(p-outcome)^2 is minimized "
            "only by honest probabilities. Correct by construction."
        )

    def grade(self, item) -> float:
        p_up, outcome = item
        return 1.0 - (float(p_up) - float(outcome)) ** 2
