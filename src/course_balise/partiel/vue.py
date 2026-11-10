"""Vue locale d'un robot (Partie IV).

Un robot ne perçoit que les cases à une distance de Manhattan au plus égale
à ``rayon`` (1 dans l'énoncé) de sa position. Pour chaque case vue, il
observe son contenu immobile ou modifiable :

=====  ==============================================================
``#``  mur
``.``  case ordinaire (y compris une porte déjà ouverte)
``D``  porte encore fermée
``K``  clé au sol
``G``  balise
=====  ==============================================================

Il voit aussi l'adversaire si celui-ci se trouve dans le champ de vision.
On suppose les dimensions du plateau connues : les cases hors grille ne sont
jamais proposées à la vue.

:func:`vue_locale` est le **seul** accès des agents partiels à l'état réel :
tout ce qu'ils savent passe par une observation.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..carte import Carte, Pos
from ..etat import Etat, adversaire


@dataclass(frozen=True, slots=True)
class Observation:
    """Ce qu'un robot perçoit à un instant donné."""

    tour: int
    joueur: str
    position: Pos
    cle: int                      # le robot sait s'il possède une clé
    cases: dict[Pos, str]         # contenu des cases vues
    adversaire: Pos | None        # position de l'adversaire s'il est visible


def contenu(carte: Carte, etat: Etat, p: Pos) -> str:
    """Symbole observé sur la case ``p`` (hors robots)."""
    if p in carte.murs:
        return "#"
    if p == carte.balise:
        return "G"
    if etat.porte_fermee(carte, p):
        return "D"
    if p in etat.cles_sol:
        return "K"
    return "."


def cases_visibles(carte: Carte, centre: Pos, rayon: int = 1) -> list[Pos]:
    """Cases de la grille à distance de Manhattan au plus ``rayon`` de ``centre``."""
    x0, y0 = centre
    res = []
    for dy in range(-rayon, rayon + 1):
        reste = rayon - abs(dy)
        for dx in range(-reste, reste + 1):
            p = (x0 + dx, y0 + dy)
            if carte.dans_grille(p):
                res.append(p)
    return res


def vue_locale(carte: Carte, etat: Etat, joueur: str, rayon: int = 1) -> Observation:
    """Observation de ``joueur`` dans ``etat``."""
    pos = etat.position(joueur)
    visibles = cases_visibles(carte, pos, rayon)
    adv = etat.position(adversaire(joueur))
    return Observation(
        tour=etat.t,
        joueur=joueur,
        position=pos,
        cle=etat.cle(joueur),
        cases={p: contenu(carte, etat, p) for p in visibles},
        adversaire=adv if adv in visibles else None,
    )
