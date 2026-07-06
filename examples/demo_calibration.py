"""
Calibration eval demo — the fishy-style evaluation, self-contained.

A model that is genuinely informative (probabilities that lean the right way)
should beat a coin flip on Brier. The baseline is the coin flip; the edge is the
finding. If the model can't beat 0.75, it isn't calibrated — reported honestly.

Run: python examples/demo_calibration.py
"""
from evalkit import run_eval
from evalkit.graders import CalibrationGrader

grader = CalibrationGrader()

# Items are (p_up, outcome). A modestly-skilled model: leans correct more often
# than not. Coin flip: always p=0.5.
model = [
    (0.8, 1), (0.7, 1), (0.6, 0), (0.9, 1), (0.3, 0), (0.65, 1), (0.55, 0), (0.75, 1),
]
coin_flip = [(0.5, o) for _, o in model]

report = run_eval(grader, {"model": model}, baseline=("coin_flip", coin_flip))
print(report)
print()
edge = report.edge_over_baseline()["model"]
print("Model beats coin flip." if edge > 0 else "Model does NOT beat coin flip — not calibrated.")
