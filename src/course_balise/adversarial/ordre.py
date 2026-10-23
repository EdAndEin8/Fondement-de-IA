"""Ordres d'exploration des coups pour Min-Max et Alpha-Bêta.

Un ordre est une fonction ``(jeu, etat, actions, evaluation) -> actions``.
Pour l'instant, seul l'ordre naturel est disponible.
"""

from __future__ import annotations

from collections.abc import Callable

from ..etat import Etat
from ..regles import Jeu

type Ordre = Callable[[Jeu, Etat, list[str], Callable[[Etat], float]], list[str]]


def naturel(jeu, etat, actions, evaluation):
    """Ordre fixe N, S, O, E (celui de ``actions_legales``)."""
    return actions


ORDRES: dict[str, Ordre] = {
    "naturel": naturel,
}
