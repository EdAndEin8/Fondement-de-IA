"""Algorithmes de recherche dans un espace d'états : BFS, DFS, UCS, A*.

Tous implémentent une recherche en graphe (états déjà rencontrés mémorisés
dans un dictionnaire), ce qui est possible car les états sont hashables.
"""

from __future__ import annotations

import heapq
import time
from collections import deque
from collections.abc import Callable
from itertools import count

from .probleme import EtatRecherche, ProblemeChemin, ResultatRecherche

type Heuristique = Callable[[EtatRecherche], float]
type Parents = dict[EtatRecherche, tuple[EtatRecherche | None, str | None]]


def _reconstruire(parents: Parents, but: EtatRecherche):
    actions, etats = [], [but]
    s = but
    while (p := parents[s])[0] is not None:
        s, a = p
        actions.append(a)
        etats.append(s)
    return actions[::-1], etats[::-1]


def _resultat(nom, parents, but, cout, stats, debut) -> ResultatRecherche:
    r = ResultatRecherche(nom, None, None, None, temps=time.perf_counter() - debut, **stats)
    if but is not None:
        r.actions, r.etats = _reconstruire(parents, but)
        r.cout = cout
    return r


# --------------------------------------------------------------------- BFS
def bfs(probleme: ProblemeChemin) -> ResultatRecherche:
    """Largeur d'abord. Test de but à la génération : optimal à coût unitaire."""
    debut = time.perf_counter()
    s0 = probleme.depart
    parents: Parents = {s0: (None, None)}
    stats = dict(noeuds_developpes=0, noeuds_generes=0, frontiere_max=1, memoire_noeuds=1)
    if probleme.est_but(s0):
        return _resultat("BFS", parents, s0, 0, stats, debut)

    frontiere = deque([s0])
    profondeur = {s0: 0}
    while frontiere:
        s = frontiere.popleft()
        stats["noeuds_developpes"] += 1
        for a, s2, _ in probleme.successeurs(s):
            stats["noeuds_generes"] += 1
            if s2 in parents:
                continue
            parents[s2] = (s, a)
            profondeur[s2] = profondeur[s] + 1
            if probleme.est_but(s2):
                return _resultat("BFS", parents, s2, profondeur[s2], stats, debut)
            frontiere.append(s2)
        stats["frontiere_max"] = max(stats["frontiere_max"], len(frontiere))
        stats["memoire_noeuds"] = max(stats["memoire_noeuds"], len(parents))
    return _resultat("BFS", parents, None, None, stats, debut)


# --------------------------------------------------------------------- DFS
def dfs(probleme: ProblemeChemin, limite: int | None = None) -> ResultatRecherche:
    """Profondeur d'abord (graphe, pile explicite). Complet sur un espace fini,
    mais non optimal. ``limite`` borne éventuellement la profondeur."""
    debut = time.perf_counter()
    parents: Parents = {}
    profondeur: dict[EtatRecherche, int] = {}
    pile: list[tuple[EtatRecherche, EtatRecherche | None, str | None, int]] = [
        (probleme.depart, None, None, 0)
    ]
    stats = dict(noeuds_developpes=0, noeuds_generes=0, frontiere_max=1, memoire_noeuds=1)
    while pile:
        s, parent, a, d = pile.pop()
        if s in parents:
            continue
        parents[s] = (parent, a)
        profondeur[s] = d
        if probleme.est_but(s):
            return _resultat("DFS", parents, s, d, stats, debut)
        stats["noeuds_developpes"] += 1
        if limite is not None and d >= limite:
            continue
        # Empilés en ordre inverse : le premier successeur est exploré en premier.
        succ = list(probleme.successeurs(s))
        stats["noeuds_generes"] += len(succ)
        for a2, s2, _ in reversed(succ):
            if s2 not in parents:
                pile.append((s2, s, a2, d + 1))
        stats["frontiere_max"] = max(stats["frontiere_max"], len(pile))
        stats["memoire_noeuds"] = max(stats["memoire_noeuds"], len(pile) + len(parents))
    return _resultat("DFS", parents, None, None, stats, debut)


# --------------------------------------------------------------- UCS et A*
def _meilleur_d_abord(probleme: ProblemeChemin, h: Heuristique, nom: str) -> ResultatRecherche:
    """Recherche meilleur-d'abord sur f = g + h. Avec h = 0, c'est UCS.

    Départage des ex æquo sur f : plus petit h d'abord (on préfère les nœuds
    les plus avancés), puis ordre d'insertion (déterminisme).
    """
    debut = time.perf_counter()
    s0 = probleme.depart
    compteur = count()
    g: dict[EtatRecherche, float] = {s0: 0}
    parents: Parents = {s0: (None, None)}
    h0 = h(s0)
    frontiere = [(h0, h0, next(compteur), s0)]
    fermes: set[EtatRecherche] = set()
    stats = dict(noeuds_developpes=0, noeuds_generes=0, frontiere_max=1, memoire_noeuds=1)

    while frontiere:
        _, _, _, s = heapq.heappop(frontiere)
        if s in fermes:
            continue  # entrée périmée (un meilleur g a été trouvé depuis)
        if probleme.est_but(s):
            return _resultat(nom, parents, s, g[s], stats, debut)
        fermes.add(s)
        stats["noeuds_developpes"] += 1
        for a, s2, cout in probleme.successeurs(s):
            stats["noeuds_generes"] += 1
            g2 = g[s] + cout
            if s2 in fermes and g2 >= g[s2]:
                continue
            if g2 < g.get(s2, float("inf")):
                h2 = h(s2)
                if h2 == float("inf"):
                    continue  # état sans issue : élagué
                g[s2] = g2
                parents[s2] = (s, a)
                fermes.discard(s2)  # réouverture (inutile si h est cohérente)
                heapq.heappush(frontiere, (g2 + h2, h2, next(compteur), s2))
        stats["frontiere_max"] = max(stats["frontiere_max"], len(frontiere))
        stats["memoire_noeuds"] = max(stats["memoire_noeuds"], len(frontiere) + len(g))
    return _resultat(nom, parents, None, None, stats, debut)


def ucs(probleme: ProblemeChemin) -> ResultatRecherche:
    """Coût uniforme (Dijkstra) : test de but au retrait de la file."""
    return _meilleur_d_abord(probleme, lambda s: 0, "UCS")


def astar(probleme: ProblemeChemin, h: Heuristique, nom: str = "A*") -> ResultatRecherche:
    """A* : optimal si h est admissible (et sans réouverture si h est cohérente)."""
    return _meilleur_d_abord(probleme, h, nom)
