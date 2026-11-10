"""Course en solitaire : un seul robot se déplace (Partie IV).

Sert à comparer un robot qui connaît toute la carte et un robot qui la
découvre : l'adversaire reste immobile sur sa case de départ (obstacle
fixe, comme en Partie I) et le robot joue tous les coups jusqu'à G.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from ..agents.base import Agent
from ..carte import Carte
from ..etat import BLEU, Etat
from ..regles import PASSER, Jeu


@dataclass
class ResultatSolo:
    arrive: bool
    pas: int                 # déplacements joués
    noeuds: int              # nœuds développés, tous coups confondus
    temps: float             # secondes de décision
    positions: list          # trajectoire, départ compris


def course_solo(agent: Agent, carte: Carte, joueur: str = BLEU, limite: int = 400,
                graine: int = 0) -> ResultatSolo:
    jeu = Jeu(carte, tmax=10 * limite)
    agent.reinitialiser(graine)
    etat: Etat = jeu.etat_initial(joueur)
    positions = [etat.position(joueur)]
    noeuds = 0
    temps = 0.0
    while len(positions) <= limite and jeu.gagnant(etat) is None:
        t0 = time.perf_counter()
        action = agent.choisir(jeu, etat)
        temps += time.perf_counter() - t0
        noeuds += agent.noeuds
        if action == PASSER:
            break
        etat = jeu.transition(etat, action).avec(joueur=joueur, p=0)
        positions.append(etat.position(joueur))
    return ResultatSolo(jeu.gagnant(etat) == joueur, len(positions) - 1, noeuds, temps,
                        positions)
