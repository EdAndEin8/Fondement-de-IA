"""Agents de décision adversariale : Min-Max, Alpha-Bêta, Alpha-Bêta itératif.

Un même agent peut jouer Bleu ou Rouge : la recherche est toujours menée
du point de vue de Bleu (MAX) et choisit le coup MIN quand Rouge a le trait.
L'évaluation est construite à la première décision sur une carte, puis
réutilisée (ses tables de distances sont mises en cache).
"""

from __future__ import annotations

from ..adversarial.evaluation import POIDS_BASE, Evaluation, Poids
from ..adversarial.iteratif import approfondissement_iteratif
from ..adversarial.minimax import alphabeta, minimax
from ..etat import Etat
from ..regles import Jeu
from .base import Agent


class _AgentEvalue(Agent):
    def __init__(self, poids: Poids = POIDS_BASE):
        super().__init__()
        self.poids = poids
        self._evaluation: Evaluation | None = None
        self.derniere_decision = None

    def evaluation(self, jeu: Jeu) -> Evaluation:
        if self._evaluation is None or self._evaluation.carte is not jeu.carte:
            self._evaluation = Evaluation(jeu.carte, self.poids)
        return self._evaluation


class AgentMinMax(_AgentEvalue):
    def __init__(self, profondeur: int = 4, poids: Poids = POIDS_BASE):
        super().__init__(poids)
        self.profondeur = profondeur
        self.nom = f"minmax-d{profondeur}"

    def choisir(self, jeu: Jeu, etat: Etat) -> str:
        dec = minimax(jeu, etat, self.profondeur, self.evaluation(jeu))
        self.noeuds = dec.stats.noeuds
        self.derniere_decision = dec
        return dec.action


class AgentAlphaBeta(_AgentEvalue):
    def __init__(self, profondeur: int = 4, poids: Poids = POIDS_BASE,
                 ordre: str = "evaluation"):
        super().__init__(poids)
        self.profondeur = profondeur
        self.ordre = ordre
        self.nom = f"alphabeta-d{profondeur}"

    def choisir(self, jeu: Jeu, etat: Etat) -> str:
        dec = alphabeta(jeu, etat, self.profondeur, self.evaluation(jeu), ordre=self.ordre)
        self.noeuds = dec.stats.noeuds
        self.derniere_decision = dec
        return dec.action


class AgentAlphaBetaIteratif(_AgentEvalue):
    """Alpha-Bêta avec approfondissement itératif et budget par coup."""

    def __init__(self, budget: float = 0.1, poids: Poids = POIDS_BASE,
                 profondeur_max: int = 40):
        super().__init__(poids)
        self.budget = budget
        self.profondeur_max = profondeur_max
        self.nom = f"alphabeta-it{int(budget * 1000)}ms"
        self.profondeurs: list[int] = []

    def reinitialiser(self, graine: int) -> None:
        super().reinitialiser(graine)
        self.profondeurs = []

    def choisir(self, jeu: Jeu, etat: Etat) -> str:
        res = approfondissement_iteratif(jeu, etat, self.evaluation(jeu), self.budget,
                                         self.profondeur_max)
        self.noeuds = res.noeuds
        self.profondeurs.append(res.profondeur)
        self.derniere_decision = res
        return res.action

