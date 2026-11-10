"""Chaînage avant sur une base de faits (Partie II).

Le moteur manipule des règles de la forme *si prémisses, alors conclusion*,
sous la forme de clauses de Horn à variables. Une **variable** est une chaîne
commençant par ``?`` (par exemple ``?r``, ``?c``) ; tout le reste est une
constante (nom de robot, position ``(x, y)``, nom de prédicat).

L'inférence est un chaînage avant monotone : on applique les règles tant
qu'elles produisent de nouveaux faits, jusqu'au point fixe. Chaque conclusion
déduite est accompagnée de sa **dérivation** (la règle qui l'a produite et les
prémisses instanciées utilisées), ce qui permet ensuite de justifier ou
d'interdire une action en remontant jusqu'aux faits observés.

Toutes les règles sont des clauses de Horn positives : il n'y a pas de
négation dans les prémisses. Les propriétés « négatives » utiles (une case
est ``libre``, un robot est ``sans_cle``) sont déjà fournies comme faits
positifs par :func:`faits.faits_de_etat`. Cela garde le chaînage avant simple
et sa conclusion indépendante de l'ordre d'application des règles.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass

from ..carte import Carte
from ..etat import Etat
from .faits import Fait, faits_de_etat, format_fait

type Motif = tuple
type Substitution = dict[str, object]


def est_variable(x) -> bool:
    return isinstance(x, str) and x.startswith("?")


def unifier(motif: Motif, fait: Fait, subst: Substitution) -> Substitution | None:
    """Étend ``subst`` pour que ``motif`` corresponde à ``fait``, ou ``None``.

    ``subst`` n'est pas modifié : une copie est renvoyée en cas de succès.
    """
    if len(motif) != len(fait):
        return None
    resultat = dict(subst)
    for m, f in zip(motif, fait):
        if est_variable(m):
            attendu = resultat.get(m)
            if attendu is None:
                resultat[m] = f
            elif attendu != f:
                return None
        elif m != f:
            return None
    return resultat


def substituer(motif: Motif, subst: Substitution) -> Fait:
    """Remplace les variables de ``motif`` par leur valeur dans ``subst``."""
    return tuple(subst[x] if est_variable(x) else x for x in motif)


@dataclass(frozen=True, slots=True)
class Regle:
    """Règle *si prémisses, alors conclusion*.

    Toute variable de la conclusion doit apparaître dans les prémisses, sans
    quoi la conclusion ne pourrait pas être entièrement instanciée.
    """

    nom: str
    premisses: tuple[Motif, ...]
    conclusion: Motif


@dataclass(frozen=True, slots=True)
class Derivation:
    """Trace de production d'un fait déduit."""

    regle: str
    premisses: tuple[Fait, ...]


def _index_par_predicat(faits: set[Fait]) -> dict[object, list[Fait]]:
    index: dict[object, list[Fait]] = defaultdict(list)
    for f in faits:
        index[f[0]].append(f)
    return index


def _correspondances(
    premisses: tuple[Motif, ...],
    index: dict[object, list[Fait]],
    subst: Substitution,
) -> Iterator[Substitution]:
    """Toutes les substitutions satisfaisant ``premisses`` dans ``index``."""
    if not premisses:
        yield subst
        return
    tete, *reste = premisses
    for fait in index.get(tete[0], ()):
        etendue = unifier(tete, fait, subst)
        if etendue is not None:
            yield from _correspondances(tuple(reste), index, etendue)


def chainage_avant(
    faits_base: set[Fait], regles: tuple[Regle, ...]
) -> tuple[set[Fait], dict[Fait, Derivation]]:
    """Sature ``faits_base`` par ``regles``.

    Renvoie l'ensemble de tous les faits (base + déduits) et, pour chaque fait
    déduit, la première dérivation qui l'a produit.
    """
    faits = set(faits_base)
    derivations: dict[Fait, Derivation] = {}
    change = True
    while change:
        change = False
        index = _index_par_predicat(faits)
        for regle in regles:
            for subst in _correspondances(regle.premisses, index, {}):
                conclusion = substituer(regle.conclusion, subst)
                if conclusion not in faits:
                    faits.add(conclusion)
                    derivations[conclusion] = Derivation(
                        regle.nom,
                        tuple(substituer(p, subst) for p in regle.premisses),
                    )
                    change = True
    return faits, derivations


# --------------------------------------------------------------------- règles
# Chaque règle précise ses conditions exactes sur l'état du jeu (R1–R8). Les
# variables ``?r`` (robot), ``?c`` (case courante), ``?d``/``?k``/``?g``
# (case cible) sont instanciées par le chaînage avant.
REGLES: tuple[Regle, ...] = (
    # Un robot qui a le trait peut se déplacer vers une case voisine libre.
    Regle(
        "deplacement",
        (("trait", "?r"), ("position", "?r", "?c"),
         ("voisine", "?c", "?d"), ("libre", "?d")),
        ("deplacement_possible", "?r", "?d"),
    ),
    # Avec une clé, il peut ouvrir une porte fermée voisine (R5).
    Regle(
        "ouverture",
        (("trait", "?r"), ("possede_cle", "?r"), ("position", "?r", "?c"),
         ("voisine", "?c", "?d"), ("porte_fermee", "?d")),
        ("peut_ouvrir", "?r", "?d"),
    ),
    # Ouvrir une porte est aussi un déplacement vers sa case.
    Regle(
        "franchissement",
        (("peut_ouvrir", "?r", "?d"),),
        ("deplacement_possible", "?r", "?d"),
    ),
    # Sans clé, entrer sur une case voisine contenant une clé la ramasse (R4).
    Regle(
        "ramassage",
        (("trait", "?r"), ("sans_cle", "?r"), ("position", "?r", "?c"),
         ("voisine", "?c", "?k"), ("cle", "?k"), ("libre", "?k")),
        ("peut_ramasser", "?r", "?k"),
    ),
    # Entrer sur la balise voisine gagne immédiatement (R6).
    Regle(
        "victoire",
        (("trait", "?r"), ("position", "?r", "?c"),
         ("voisine", "?c", "?g"), ("but", "?g"), ("libre", "?g")),
        ("coup_gagnant", "?r", "?g"),
    ),
    # Sans clé, une porte fermée voisine est un déplacement interdit (R5).
    Regle(
        "interdiction_porte",
        (("trait", "?r"), ("sans_cle", "?r"), ("position", "?r", "?c"),
         ("voisine", "?c", "?d"), ("porte_fermee", "?d")),
        ("interdit", "?r", "?d"),
    ),
    # Un mur est une case infranchissable (R3).
    Regle("infranchissable_mur", (("mur", "?c"),), ("infranchissable", "?c")),
    # La case d'un robot est infranchissable pour l'autre (R3).
    Regle("infranchissable_occupee", (("occupee", "?c"),), ("infranchissable", "?c")),
)


class BaseConnaissances:
    """Base de faits d'un état, saturée par chaînage avant.

    Sépare les faits observés (:attr:`faits_base`) des conclusions déduites et
    sait reconstruire la justification de n'importe quel fait déduit.
    """

    def __init__(self, carte: Carte, etat: Etat, regles: tuple[Regle, ...] = REGLES):
        self.carte = carte
        self.etat = etat
        self.regles = regles
        self.faits_base = faits_de_etat(carte, etat)
        self.faits, self.derivations = chainage_avant(self.faits_base, regles)

    def faits_deduits(self) -> set[Fait]:
        return self.faits - self.faits_base

    def contient(self, fait: Fait) -> bool:
        return fait in self.faits

    def requete(self, predicat: str) -> list[Fait]:
        """Faits d'un prédicat donné, triés pour un affichage stable."""
        return sorted(f for f in self.faits if f[0] == predicat)

    def expliquer(self, fait: Fait) -> str:
        """Justification d'un fait : arbre de dérivation jusqu'aux observations."""
        lignes: list[str] = []

        def tracer(f: Fait, profondeur: int, chemin: frozenset[Fait]) -> None:
            prefixe = "  " * profondeur
            if f in self.faits_base:
                lignes.append(f"{prefixe}{format_fait(f)}  [observé]")
                return
            d = self.derivations.get(f)
            if d is None:
                lignes.append(f"{prefixe}{format_fait(f)}  [fait absent]")
                return
            lignes.append(f"{prefixe}{format_fait(f)}  [règle {d.regle}]")
            for premisse in d.premisses:
                if premisse in chemin:
                    lignes.append(f"{prefixe}  {format_fait(premisse)}  [...]")
                else:
                    tracer(premisse, profondeur + 1, chemin | {f})

        tracer(fait, 0, frozenset())
        return "\n".join(lignes)
