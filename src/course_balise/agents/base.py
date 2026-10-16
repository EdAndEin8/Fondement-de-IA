"""Interface commune des agents et agent aléatoire."""

from __future__ import annotations

import random

from ..etat import Etat
from ..regles import Jeu


class Agent:
    """Un agent choisit une action légale pour le joueur courant.

    ``reinitialiser`` est appelé par :func:`course_balise.jeu.jouer` avant
    chaque partie avec une graine dérivée de la graine de la partie, ce qui
    rend toute simulation reproductible. ``noeuds`` compte les nœuds visités
    lors de la dernière décision (0 pour les agents sans recherche).
    """

    nom = "agent"

    def __init__(self) -> None:
        self.rng = random.Random(0)
        self.noeuds = 0

    def reinitialiser(self, graine: int) -> None:
        self.rng = random.Random(graine)
        self.noeuds = 0

    def choisir(self, jeu: Jeu, etat: Etat) -> str:  # pragma: no cover - abstrait
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.nom


class AgentAleatoire(Agent):
    """Choisit uniformément une action légale."""

    nom = "aleatoire"

    def choisir(self, jeu: Jeu, etat: Etat) -> str:
        return self.rng.choice(jeu.actions_legales(etat))
