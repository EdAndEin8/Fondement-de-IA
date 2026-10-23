"""Ordres d'exploration des coups pour Min-Max et Alpha-Bêta.

L'ordre ne change pas la valeur Min-Max, mais il change beaucoup le nombre
de nœuds visités par Alpha-Bêta : les coupures arrivent tôt si le meilleur
coup est exploré en premier.

Un ordre est une fonction ``(jeu, etat, actions, evaluation) -> actions``.
"""

from __future__ import annotations

import random
from collections.abc import Callable

from ..etat import BLEU, Etat
from ..regles import Jeu

type Ordre = Callable[[Jeu, Etat, list[str], Callable[[Etat], float]], list[str]]


def naturel(jeu, etat, actions, evaluation):
    """Ordre fixe N, S, O, E (celui de ``actions_legales``)."""
    return actions


def aleatoire(graine: int = 0) -> Ordre:
    """Ordre aléatoire, reproductible : le mélange ne dépend que de la graine
    et de l'état, si bien que Min-Max et Alpha-Bêta voient le même ordre."""

    def ordre(jeu, etat, actions, evaluation):
        # Pas de hash() : il est randomisé d'une exécution Python à l'autre
        # pour les chaînes. Random(str) passe par SHA-512, donc stable.
        cle = (graine, etat.pb, etat.pr, etat.joueur, etat.kb, etat.kr,
               sorted(etat.cles_sol), sorted(etat.portes_ouvertes), etat.t, etat.p)
        rng = random.Random(repr(cle))
        melange = list(actions)
        rng.shuffle(melange)
        return melange

    return ordre


def _par_evaluation(meilleur_d_abord: bool) -> Ordre:
    def ordre(jeu, etat, actions, evaluation):
        if len(actions) < 2:
            return actions
        maxi = etat.joueur == BLEU
        cle = {a: evaluation(jeu.transition(etat, a)) for a in actions}
        # MAX veut les valeurs hautes en premier, MIN les basses.
        decroissant = maxi == meilleur_d_abord
        return sorted(actions, key=cle.__getitem__, reverse=decroissant)

    return ordre


evaluation_d_abord = _par_evaluation(True)
pire_d_abord = _par_evaluation(False)

ORDRES: dict[str, Ordre] = {
    "naturel": naturel,
    "aleatoire": aleatoire(0),
    "evaluation": evaluation_d_abord,
    "pire": pire_d_abord,
}
