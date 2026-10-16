"""Heuristiques pour A*.

Toutes sont des bornes inférieures du nombre de déplacements restants
(admissibles) et cohérentes ; chacune est obtenue en relâchant des
contraintes du problème réel :

=====================  ====================================================
``manhattan``          relâche murs, portes et adversaire (énoncé)
``distance_relaxee``   garde les murs, relâche portes et adversaire
``distance_cles``      garde les murs ; si la balise n'est accessible qu'à
                       travers une porte fermée et que le robot n'a pas de
                       clé, impose le détour par la clé la plus avantageuse
=====================  ====================================================
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable

from ..carte import Carte, Pos
from .probleme import EtatRecherche

INF = float("inf")
type Heuristique = Callable[[EtatRecherche], float]


def distances_bfs(carte: Carte, source: Pos, bloquees: Iterable[Pos] = ()) -> dict[Pos, int]:
    """Distances (en pas) depuis ``source`` en évitant les murs et ``bloquees``."""
    bloquees = set(bloquees)
    dist = {source: 0}
    file = deque([source])
    while file:
        p = file.popleft()
        for _, q in carte.voisins(p):
            if q not in dist and q not in bloquees:
                dist[q] = dist[p] + 1
                file.append(q)
    return dist


def nulle(carte: Carte | None = None) -> Heuristique:
    return lambda s: 0


def manhattan(carte: Carte) -> Heuristique:
    xg, yg = carte.balise

    def h(s: EtatRecherche) -> float:
        x, y = s.pos
        return abs(x - xg) + abs(y - yg)

    return h


def distance_relaxee(carte: Carte) -> Heuristique:
    """Vraie distance sur la carte où toutes les portes seraient ouvertes."""
    d = distances_bfs(carte, carte.balise)
    return lambda s: d.get(s.pos, INF)


def distance_cles(carte: Carte) -> Heuristique:
    d_rel = distances_bfs(carte, carte.balise)
    d_depuis_cle = {k: distances_bfs(carte, k) for k in carte.cles}
    cache_fermees: dict[frozenset[Pos], dict[Pos, int]] = {}

    def d_portes_fermees(ouvertes: frozenset[Pos]) -> dict[Pos, int]:
        if ouvertes not in cache_fermees:
            cache_fermees[ouvertes] = distances_bfs(carte, carte.balise,
                                                    carte.portes - ouvertes)
        return cache_fermees[ouvertes]

    def h(s: EtatRecherche) -> float:
        base = d_rel.get(s.pos, INF)
        if s.cle or base == INF:
            return base
        if s.pos in d_portes_fermees(s.portes_ouvertes):
            return base  # un chemin évite toutes les portes fermées
        # Toute solution franchit une porte fermée, donc passe d'abord par une clé.
        return min(
            (d_depuis_cle[k].get(s.pos, INF) + d_rel.get(k, INF) for k in s.cles_sol),
            default=INF,
        )

    return h


HEURISTIQUES: dict[str, Callable[[Carte], Heuristique]] = {
    "nulle": nulle,
    "manhattan": manhattan,
    "relaxee": distance_relaxee,
    "cles": distance_cles,
}
