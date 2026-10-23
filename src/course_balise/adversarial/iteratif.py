"""Approfondissement itératif avec budget de temps (Partie III, 5.3).

Principe : on lance Alpha-Bêta à profondeur 1, 2, 3... tant qu'il reste du
temps. Si une itération dépasse l'échéance, elle est abandonnée (exception
:class:`TempsEcoule`) et on garde le coup de la dernière itération complète.

Garanties :
- une action légale est toujours renvoyée : avant toute recherche, on prend
  la meilleure action à profondeur 0 (tri par évaluation), qui ne coûte
  presque rien ;
- le meilleur coup de l'itération d - 1 est exploré en premier à
  l'itération d, ce qui augmente les coupures ;
- on s'arrête dès qu'une issue certaine est trouvée (victoire ou défaite
  forcée), ou quand la profondeur dépasse le nombre de tours restants.

Le coût des itérations d'avant est faible : avec un facteur de branchement
b, la dernière itération coûte à peu près autant que toutes les
précédentes réunies (b^d contre b^d / (b - 1)).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from ..etat import Etat
from ..regles import Jeu
from .minimax import Decision, FonctionEvaluation, TempsEcoule, alphabeta
from .ordre import ORDRES, Ordre

SEUIL_ISSUE_CERTAINE = 900  # |valeur| au-delà : victoire ou défaite forcée


@dataclass
class ResultatIteratif:
    action: str
    valeur: float
    profondeur: int                      # dernière profondeur terminée
    noeuds: int                          # total, itération abandonnée comprise
    temps: float
    interrompue: bool                    # une itération a été abandonnée
    iterations: list[Decision] = field(default_factory=list)


def approfondissement_iteratif(
    jeu: Jeu,
    etat: Etat,
    evaluation: FonctionEvaluation,
    budget: float,
    profondeur_max: int = 40,
    ordre: str | Ordre = "evaluation",
) -> ResultatIteratif:
    """Meilleure action trouvée en ``budget`` secondes."""
    debut = time.perf_counter()
    echeance = debut + budget
    ordonner = ORDRES[ordre] if isinstance(ordre, str) else ordre

    # Action de secours, valide même si aucune itération ne se termine.
    actions = ORDRES["evaluation"](jeu, etat, jeu.actions_legales(etat), evaluation)
    res = ResultatIteratif(actions[0], evaluation(jeu.transition(etat, actions[0])),
                           0, 0, 0.0, False)

    restants = jeu.tmax - etat.t
    for d in range(1, min(profondeur_max, restants) + 1):
        try:
            dec = alphabeta(jeu, etat, d, evaluation, ordre=ordonner,
                            echeance=echeance, premier_coup=res.action)
        except TempsEcoule:
            res.interrompue = True
            break
        res.noeuds += dec.stats.noeuds
        res.iterations.append(dec)
        res.action, res.valeur, res.profondeur = dec.action, dec.valeur, d
        if abs(dec.valeur) >= SEUIL_ISSUE_CERTAINE:
            break
        if time.perf_counter() >= echeance:
            break

    res.temps = time.perf_counter() - debut
    # Nœuds de l'itération abandonnée : non récupérables proprement, on
    # compte uniquement les itérations terminées.
    return res
