"""Affichage ASCII du plateau, avec couleurs ANSI optionnelles et animation."""

from __future__ import annotations

import os
import sys
import time

from .carte import Carte, Pos
from .etat import NOMS, Etat

# Codes ANSI (désactivables avec couleurs=False ou la variable NO_COLOR).
_C = {
    "B": "\033[1;34m",
    "R": "\033[1;31m",
    "G": "\033[1;32m",
    "K": "\033[1;33m",
    "D": "\033[33m",
    "#": "\033[90m",
    "*": "\033[36m",
    "fin": "\033[0m",
}

EFFACER_ECRAN = "\033[H\033[2J"


def _symbole(carte: Carte, etat: Etat, p: Pos, chemin: set[Pos]) -> str:
    if p == etat.pb:
        return "B"
    if p == etat.pr:
        return "R"
    if p in carte.murs:
        return "#"
    if p == carte.balise:
        return "G"
    if etat.porte_fermee(carte, p):
        return "D"
    if p in etat.cles_sol:
        return "K"
    if p in chemin:
        return "*"
    return "."


def afficher(
    etat: Etat,
    carte: Carte,
    couleurs: bool | None = None,
    chemin: list[Pos] | None = None,
    entete: bool = True,
) -> str:
    """Représentation lisible du plateau (renvoie une chaîne).

    ``chemin`` permet de surligner une suite de cases (résultat d'une recherche).
    """
    if couleurs is None:
        couleurs = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    chemin_set = set(chemin or [])

    def peindre(c: str) -> str:
        if couleurs and c in _C:
            return f"{_C[c]}{c}{_C['fin']}"
        return c

    lignes = []
    if entete:
        lignes.append(
            f"Tour {etat.t:>2} | trait : {NOMS[etat.joueur]:<5} | "
            f"clé Bleu : {etat.kb} | clé Rouge : {etat.kr} | passes : {etat.p}"
        )
    lignes.append("   " + " ".join(str(x % 10) for x in range(carte.largeur)))
    for y in range(carte.hauteur):
        cases = " ".join(peindre(_symbole(carte, etat, (x, y), chemin_set))
                         for x in range(carte.largeur))
        lignes.append(f"{y:>2} {cases}")
    return "\n".join(lignes)


def animer(etat: Etat, carte: Carte, legende: str = "", delai: float = 0.3) -> None:
    """Efface le terminal puis affiche le plateau (animation ASCII simple)."""
    sortie = EFFACER_ECRAN + afficher(etat, carte)
    if legende:
        sortie += "\n" + legende
    print(sortie, flush=True)
    if delai > 0:
        time.sleep(delai)


def legende_symboles() -> str:
    return "B Bleu  R Rouge  G balise  K clé  D porte fermée  # mur  * chemin"


__all__ = ["afficher", "animer", "legende_symboles"]
