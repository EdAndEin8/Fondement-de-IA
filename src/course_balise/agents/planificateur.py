"""Agent planificateur A* : replanifie à chaque tour (donc après chaque action adverse)."""

from __future__ import annotations

from ..etat import Etat
from ..recherche import HEURISTIQUES, ProblemeChemin, astar
from ..regles import Jeu
from .base import Agent


class AgentAStar(Agent):
    """Suit le premier pas du plus court chemin calculé par A*.

    L'adversaire est vu comme un obstacle fixe à sa position actuelle. Si
    l'adversaire bloque tous les chemins, l'agent planifie en l'ignorant et
    joue le premier pas si celui-ci est légal ; sinon il joue une action
    légale au hasard (ou passe).
    """

    def __init__(self, heuristique: str = "cles"):
        super().__init__()
        self.heuristique = heuristique
        self.nom = f"astar-{heuristique}"
        self.dernier_plan: list[str] | None = None

    def choisir(self, jeu: Jeu, etat: Etat) -> str:
        legales = jeu.actions_legales(etat)
        h = HEURISTIQUES[self.heuristique](jeu.carte)
        pb = ProblemeChemin.depuis_etat(jeu.carte, etat, etat.joueur)
        r = astar(pb, h)
        self.noeuds = r.noeuds_developpes
        if not r.trouve:
            pb.obstacle = None  # l'adversaire bouchera peut-être le passage plus tard
            r = astar(pb, h)
            self.noeuds += r.noeuds_developpes
        self.dernier_plan = r.actions
        if r.actions and r.actions[0] in legales:
            return r.actions[0]
        return self.rng.choice(legales)
