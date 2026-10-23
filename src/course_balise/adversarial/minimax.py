"""Min-Max et Alpha-Bêta à profondeur limitée (Partie III).

Les deux algorithmes utilisent exactement les mêmes fonctions :
``jeu.actions_legales``, ``jeu.transition``, ``jeu.terminal`` et
:func:`valeur_feuille` (utilité ou évaluation). Ils ne diffèrent que par
l'élagage, si bien qu'à profondeur et évaluation identiques ils renvoient
la même valeur (testé dans tests/test_equivalence.py).

Convention : Bleu est MAX, Rouge est MIN, quel que soit le joueur qui
appelle la recherche. Valeurs terminales, avec ``ply`` le nombre de coups
depuis la racine :

    +1000 - ply  si Bleu gagne      (gagner vite vaut mieux)
    -1000 + ply  si Rouge gagne     (perdre tard vaut mieux)
    0            en cas de nul

Ce petit ajustement ne change pas le signe et garde |U| >= 1000 - Tmax,
toujours au-dessus de la borne de l'évaluation : les valeurs terminales
priment sur l'heuristique.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from ..etat import BLEU, Etat
from ..regles import Jeu
from .ordre import ORDRES, Ordre

INF = float("inf")
type FonctionEvaluation = Callable[[Etat], float]


@dataclass
class Statistiques:
    noeuds: int = 0        # appels récursifs (racine comprise)
    feuilles: int = 0      # nœuds évalués (terminaux ou profondeur 0)
    coupures: int = 0      # coupures alpha ou bêta
    temps: float = 0.0     # secondes


@dataclass
class Decision:
    action: str | None
    valeur: float
    profondeur: int
    stats: Statistiques = field(default_factory=Statistiques)
    valeurs_racine: dict[str, float] = field(default_factory=dict)


def valeur_feuille(jeu: Jeu, etat: Etat, ply: int, evaluation: FonctionEvaluation) -> float:
    """Utilité si l'état est terminal, sinon évaluation heuristique."""
    if jeu.terminal(etat):
        u = jeu.utilite(etat, BLEU)
        if u > 0:
            return u - ply
        if u < 0:
            return u + ply
        return 0
    return evaluation(etat)


def _resoudre_ordre(ordre: str | Ordre | None) -> Ordre:
    if ordre is None:
        return ORDRES["naturel"]
    if isinstance(ordre, str):
        return ORDRES[ordre]
    return ordre


# ------------------------------------------------------------------ Min-Max
def minimax(jeu: Jeu, etat: Etat, profondeur: int, evaluation: FonctionEvaluation,
            ordre: str | Ordre | None = None) -> Decision:
    ordonner = _resoudre_ordre(ordre)
    stats = Statistiques()

    def valeur(s: Etat, d: int, ply: int) -> float:
        stats.noeuds += 1
        if d == 0 or jeu.terminal(s):
            stats.feuilles += 1
            return valeur_feuille(jeu, s, ply, evaluation)
        enfants = [jeu.transition(s, a) for a in ordonner(jeu, s, jeu.actions_legales(s), evaluation)]
        vals = (valeur(e, d - 1, ply + 1) for e in enfants)
        return max(vals) if s.joueur == BLEU else min(vals)

    debut = time.perf_counter()
    stats.noeuds += 1
    maxi = etat.joueur == BLEU
    meilleure, meilleure_action, racine = (-INF if maxi else INF), None, {}
    for a in ordonner(jeu, etat, jeu.actions_legales(etat), evaluation):
        v = valeur(jeu.transition(etat, a), profondeur - 1, 1)
        racine[a] = v
        if (maxi and v > meilleure) or (not maxi and v < meilleure):
            meilleure, meilleure_action = v, a
    stats.temps = time.perf_counter() - debut
    return Decision(meilleure_action, meilleure, profondeur, stats, racine)


# --------------------------------------------------------------- Alpha-Bêta
def alphabeta(jeu: Jeu, etat: Etat, profondeur: int, evaluation: FonctionEvaluation,
              ordre: str | Ordre | None = None) -> Decision:
    ordonner = _resoudre_ordre(ordre)
    stats = Statistiques()

    def valeur(s: Etat, d: int, ply: int, alpha: float, beta: float) -> float:
        stats.noeuds += 1
        if d == 0 or jeu.terminal(s):
            stats.feuilles += 1
            return valeur_feuille(jeu, s, ply, evaluation)
        if s.joueur == BLEU:
            v = -INF
            for a in ordonner(jeu, s, jeu.actions_legales(s), evaluation):
                v = max(v, valeur(jeu.transition(s, a), d - 1, ply + 1, alpha, beta))
                if v >= beta:
                    stats.coupures += 1
                    return v
                alpha = max(alpha, v)
            return v
        v = INF
        for a in ordonner(jeu, s, jeu.actions_legales(s), evaluation):
            v = min(v, valeur(jeu.transition(s, a), d - 1, ply + 1, alpha, beta))
            if v <= alpha:
                stats.coupures += 1
                return v
            beta = min(beta, v)
        return v

    debut = time.perf_counter()
    stats.noeuds += 1
    actions = ordonner(jeu, etat, jeu.actions_legales(etat), evaluation)
    maxi = etat.joueur == BLEU
    alpha, beta = -INF, INF
    meilleure, meilleure_action, racine = (-INF if maxi else INF), None, {}
    for a in actions:
        v = valeur(jeu.transition(etat, a), profondeur - 1, 1, alpha, beta)
        racine[a] = v  # borne seulement, sauf pour le meilleur coup
        if maxi and v > meilleure:
            meilleure, meilleure_action = v, a
            alpha = max(alpha, v)
        elif not maxi and v < meilleure:
            meilleure, meilleure_action = v, a
            beta = min(beta, v)
    stats.temps = time.perf_counter() - debut
    return Decision(meilleure_action, meilleure, profondeur, stats, racine)
