"""Boucle de partie : ``jouer(agent_bleu, agent_rouge, carte)``.

Le temps de décision des agents est mesuré séparément du temps d'affichage
(point de méthode de l'énoncé).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .affichage import afficher, animer
from .agents.base import Agent
from .carte import Carte
from .etat import BLEU, NOMS, ROUGE, Etat
from .regles import TMAX, Jeu


@dataclass
class Coup:
    t: int
    joueur: str
    action: str
    temps: float  # secondes de réflexion de l'agent
    noeuds: int


@dataclass
class ResultatPartie:
    carte: str
    bleu: str
    rouge: str
    graine: int
    gagnant: str | None           # "B", "R" ou None (nul)
    raison: str
    tours: int
    coups: list[Coup] = field(default_factory=list)
    etat_final: Etat | None = None
    duree: float = 0.0            # durée totale de la partie, affichage exclu

    def temps_moyen(self, joueur: str) -> float:
        ts = [c.temps for c in self.coups if c.joueur == joueur]
        return sum(ts) / len(ts) if ts else 0.0

    def noeuds_moyens(self, joueur: str) -> float:
        ns = [c.noeuds for c in self.coups if c.joueur == joueur]
        return sum(ns) / len(ns) if ns else 0.0


def jouer(
    agent_bleu: Agent,
    agent_rouge: Agent,
    carte: Carte,
    graine: int = 0,
    premier: str = BLEU,
    tmax: int = TMAX,
    affichage: bool = False,
    animation: bool = False,
    delai: float = 0.3,
) -> ResultatPartie:
    """Simule une partie complète et reproductible.

    - ``graine`` initialise les générateurs aléatoires des deux agents ;
    - ``premier`` permet d'inverser le joueur qui commence ;
    - ``affichage`` imprime le plateau à chaque tour, ``animation`` l'anime
      en place dans le terminal (``delai`` secondes entre deux images).
    """
    jeu = Jeu(carte, tmax=tmax)
    agents = {BLEU: agent_bleu, ROUGE: agent_rouge}
    agent_bleu.reinitialiser(2 * graine)
    agent_rouge.reinitialiser(2 * graine + 1)

    etat = jeu.etat_initial(premier)
    coups: list[Coup] = []
    duree = 0.0

    def montrer(legende: str) -> None:
        if animation:
            animer(etat, carte, legende, delai)
        elif affichage:
            print(afficher(etat, carte) + ("\n" + legende if legende else "") + "\n")

    montrer(f"{agent_bleu} (Bleu) contre {agent_rouge} (Rouge) sur {carte.nom}")
    while not jeu.terminal(etat):
        j = etat.joueur
        debut = time.perf_counter()
        action = agents[j].choisir(jeu, etat)
        dt = time.perf_counter() - debut
        if action not in jeu.actions_legales(etat):
            raise RuntimeError(f"{agents[j]} a joué une action illégale : {action}")
        coups.append(Coup(etat.t, j, action, dt, agents[j].noeuds))
        t0 = time.perf_counter()
        etat = jeu.transition(etat, action)
        duree += dt + (time.perf_counter() - t0)
        montrer(f"{NOMS[j]} joue {action}  ({dt * 1000:.1f} ms)")

    resultat = ResultatPartie(
        carte=carte.nom,
        bleu=str(agent_bleu),
        rouge=str(agent_rouge),
        graine=graine,
        gagnant=jeu.gagnant(etat),
        raison=jeu.raison_fin(etat),
        tours=etat.t,
        coups=coups,
        etat_final=etat,
        duree=duree,
    )
    if affichage or animation:
        print(f"Fin de partie : {resultat.raison} en {resultat.tours} tours.")
    return resultat
