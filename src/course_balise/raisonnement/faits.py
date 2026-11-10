"""Base de faits décrivant les propriétés d'un état (Partie II).

Un fait est un tuple ``(predicat, arg1, arg2, ...)`` immuable et hashable,
par exemple ``("possede_cle", "bleu")``, ``("porte_fermee", (2, 3))`` ou
``("voisine", (2, 2), (2, 3))``. Les positions sont des couples ``(x, y)``.

:func:`faits_de_etat` produit les **faits explicitement connus** d'un état
(ce que l'on observe directement sur le plateau). Les conclusions (coup
possible, coup gagnant, interdiction...) ne sont pas ici : elles sont
déduites par chaînage avant à partir de ces faits et des règles de
``moteur`` — c'est la distinction demandée entre faits connus et faits
déduits.

Prédicats de base émis :

- ``but(g)`` : position de la balise ;
- ``trait(r)`` : ``r`` est le joueur qui doit jouer ;
- ``position(r, c)`` : le robot ``r`` est en ``c`` ;
- ``possede_cle(r)`` / ``sans_cle(r)`` : possession d'une clé ;
- ``occupee(c)`` : un robot occupe ``c`` ;
- ``mur(c)`` : ``c`` est un mur ;
- ``porte_fermee(d)`` / ``porte_ouverte(d)`` : état d'une porte ;
- ``cle(k)`` : une clé est au sol en ``k`` ;
- ``voisine(c, c')`` : ``c`` et ``c'`` sont orthogonalement adjacentes et
  toutes deux praticables (ni hors grille, ni mur) ;
- ``libre(c)`` : ``c`` est praticable, inoccupée et n'est pas une porte
  encore fermée — autrement dit un robot peut y entrer sans clé.
"""

from __future__ import annotations

from ..carte import Carte
from ..etat import BLEU, ROUGE, Etat

type Fait = tuple

#: Noms de robots employés dans les faits (minuscules, comme dans l'énoncé).
ROBOT: dict[str, str] = {BLEU: "bleu", ROUGE: "rouge"}


def faits_de_etat(carte: Carte, etat: Etat) -> set[Fait]:
    """Ensemble des faits explicites décrivant ``etat`` sur ``carte``."""
    faits: set[Fait] = set()
    faits.add(("but", carte.balise))
    faits.add(("trait", ROBOT[etat.joueur]))

    occupe = {etat.pb, etat.pr}
    for j in (BLEU, ROUGE):
        r = ROBOT[j]
        pos = etat.position(j)
        faits.add(("position", r, pos))
        faits.add(("possede_cle", r) if etat.cle(j) else ("sans_cle", r))
        faits.add(("occupee", pos))

    portes_fermees = carte.portes - etat.portes_ouvertes
    for d in portes_fermees:
        faits.add(("porte_fermee", d))
    for d in etat.portes_ouvertes:
        faits.add(("porte_ouverte", d))
    for k in etat.cles_sol:
        faits.add(("cle", k))
    for m in carte.murs:
        faits.add(("mur", m))

    for c in carte.cases():
        if not carte.praticable(c):
            continue
        if c not in occupe and c not in portes_fermees:
            faits.add(("libre", c))
        for _, q in carte.voisins(c):
            faits.add(("voisine", c, q))
    return faits


def _formater_arg(a) -> str:
    if isinstance(a, tuple) and len(a) == 2 and all(isinstance(v, int) for v in a):
        return f"({a[0]},{a[1]})"
    return str(a)


def format_fait(fait: Fait) -> str:
    """Représentation lisible ``predicat(arg, ...)`` d'un fait."""
    predicat, *args = fait
    return f"{predicat}(" + ", ".join(_formater_arg(a) for a in args) + ")"
