"""Problème de recherche mono-agent (Partie I).

L'adversaire est considéré comme un obstacle fixe. L'état de recherche inclut
la possession de clé, les clés restantes et les portes ouvertes : la position
seule ne suffit pas, car ramasser une clé ou ouvrir une porte change les
déplacements possibles par la suite.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from ..carte import DIRECTIONS, Carte, Pos
from ..etat import Etat, adversaire
from ..regles import deplacement


@dataclass(frozen=True, slots=True)
class EtatRecherche:
    pos: Pos
    cle: int
    cles_sol: frozenset[Pos]
    portes_ouvertes: frozenset[Pos]


class ProblemeChemin:
    """Atteindre la balise depuis ``depart`` ; coût unitaire par déplacement."""

    def __init__(self, carte: Carte, depart: EtatRecherche, obstacle: Pos | None = None):
        self.carte = carte
        self.depart = depart
        self.obstacle = obstacle

    @classmethod
    def depuis_etat(cls, carte: Carte, etat: Etat, joueur: str) -> ProblemeChemin:
        """Problème vu par ``joueur`` dans l'état de jeu ``etat``."""
        depart = EtatRecherche(
            pos=etat.position(joueur),
            cle=etat.cle(joueur),
            cles_sol=etat.cles_sol,
            portes_ouvertes=etat.portes_ouvertes,
        )
        return cls(carte, depart, obstacle=etat.position(adversaire(joueur)))

    def est_but(self, s: EtatRecherche) -> bool:
        return s.pos == self.carte.balise

    def successeurs(self, s: EtatRecherche) -> Iterator[tuple[str, EtatRecherche, int]]:
        for d in DIRECTIONS:
            r = deplacement(self.carte, s.pos, s.cle, s.cles_sol, s.portes_ouvertes,
                            d, obstacle=self.obstacle)
            if r is not None:
                yield d, EtatRecherche(r.position, r.cle, r.cles_sol, r.portes_ouvertes), 1


@dataclass
class ResultatRecherche:
    algorithme: str
    actions: list[str] | None          # None si aucun chemin
    etats: list[EtatRecherche] | None  # états du chemin, départ inclus
    cout: float | None
    noeuds_developpes: int = 0         # états retirés de la frontière et développés
    noeuds_generes: int = 0            # successeurs produits
    frontiere_max: int = 0
    memoire_noeuds: int = 0            # max(|frontière| + |mémorisés|) : estimation mémoire
    temps: float = 0.0                 # secondes
    extra: dict = field(default_factory=dict)

    @property
    def trouve(self) -> bool:
        return self.actions is not None

    @property
    def longueur(self) -> int | None:
        return None if self.actions is None else len(self.actions)

    def positions(self) -> list[Pos]:
        return [] if self.etats is None else [s.pos for s in self.etats]
