"""Small stats helpers — pure Python so the core has no heavy dependencies."""
from __future__ import annotations


def _rank(xs: list[float]) -> list[float]:
    # Average ranks, ties shared — needed for a correct Spearman under ties.
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1  # ranks are 1-based
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(a: list[float], b: list[float]) -> float:
    """Spearman rank correlation. Returns 0.0 on degenerate input (no variance)."""
    if len(a) != len(b) or len(a) < 2:
        return 0.0
    ra, rb = _rank(a), _rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    va = sum((r - ma) ** 2 for r in ra) ** 0.5
    vb = sum((r - mb) ** 2 for r in rb) ** 0.5
    if va == 0 or vb == 0:
        return 0.0
    return cov / (va * vb)
