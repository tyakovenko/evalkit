"""
Fidelity grader — drawn from `blogAI_evals` (substance/voice under transformation).

Scores whether a transformed output preserves the substance of the source. Item
is (reference_text, candidate_text); score is embedding cosine similarity in
[0, 1]. This is the piece that must be validated *empirically* — an embedding
model is not correct by construction, so run validate_empirical() against
human-gold pairs and a null floor before trusting it (the blogAI-evals gate:
Spearman rho >= 0.5, null below the floor).

sentence-transformers is imported lazily so the rest of evalkit stays dependency-
light; only fidelity needs it.
"""
from __future__ import annotations

from evalkit.protocol import Grader

_DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class FidelityGrader(Grader):
    name = "substance fidelity (cosine)"

    def __init__(self, model: str = _DEFAULT_MODEL) -> None:
        super().__init__()
        self._model_name = model
        self._model = None

    def _embedder(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def grade(self, item) -> float:
        reference, candidate = item
        import numpy as np

        emb = self._embedder().encode([reference, candidate], convert_to_numpy=True)
        a, b = emb[0], emb[1]
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
        cos = float(np.dot(a, b) / denom)
        return max(0.0, min(1.0, cos))  # clamp to the [0,1] contract
