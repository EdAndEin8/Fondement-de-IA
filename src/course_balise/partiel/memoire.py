"""Mémoire des observations d'un robot (Partie IV).

La mémoire est une carte partielle : pour chaque case déjà vue, le dernier
contenu observé ; les autres cases sont inconnues. Une case vue reste
connue. Le contenu peut toutefois devenir faux sans que le robot le sache :
une clé ramassée par l'adversaire ou une porte qu'il a ouverte hors du
champ de vision. La mémoire est corrigée à la prochaine observation.

À partir de la mémoire, on construit :

- la **frontière** : cases connues praticables qui ont au moins une voisine
  inconnue ; c'est là qu'il faut aller pour découvrir la carte ;
- une **carte supposée** (:class:`~course_balise.carte.Carte`) où les cases
  inconnues sont considérées comme libres (hypothèse optimiste) ou comme
  des murs (hypothèse pessimiste). Les algorithmes des Parties I et III
  s'appliquent alors sans modification à cette carte.
"""

from __future__ import annotations

from collections import deque

from ..carte import DIRECTIONS, Carte, Pos
from .vue import Observation

INCONNU = "?"


class Memoire:
    """Carte partielle d'un robot, mise à jour à chaque observation."""

    def __init__(self, largeur: int, hauteur: int):
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases: dict[Pos, str] = {}
        #: Dernière observation de l'adversaire : (tour, position), oubliée
        #: dès que l'on voit sa case vide.
        self.adversaire_vu: tuple[int, Pos] | None = None
        self.derniere: Observation | None = None
        self.observations = 0
        #: Cases visitées par le dernier appel à :meth:`chemin_vers`.
        self.noeuds_bfs = 0

    # --------------------------------------------------------------- mise à jour
    def observer(self, obs: Observation) -> None:
        self.cases.update(obs.cases)
        if obs.adversaire is not None:
            self.adversaire_vu = (obs.tour, obs.adversaire)
        elif self.adversaire_vu is not None and self.adversaire_vu[1] in obs.cases:
            self.adversaire_vu = None  # on voit que l'adversaire est parti
        self.derniere = obs
        self.observations += 1

    # ----------------------------------------------------------------- requêtes
    def dans_grille(self, p: Pos) -> bool:
        return 0 <= p[0] < self.largeur and 0 <= p[1] < self.hauteur

    def adversaire_suppose(self) -> Pos | None:
        """Dernière position connue de l'adversaire, tant qu'on n'a pas vu
        qu'il l'a quittée (il est supposé immobile hors du champ de vision)."""
        return None if self.adversaire_vu is None else self.adversaire_vu[1]

    def contenu(self, p: Pos) -> str:
        return self.cases.get(p, INCONNU)

    def connue(self, p: Pos) -> bool:
        return p in self.cases

    def nb_connues(self) -> int:
        return len(self.cases)

    def balise(self) -> Pos | None:
        for p, c in self.cases.items():
            if c == "G":
                return p
        return None

    def cles(self) -> frozenset[Pos]:
        return frozenset(p for p, c in self.cases.items() if c == "K")

    def portes_fermees(self) -> frozenset[Pos]:
        return frozenset(p for p, c in self.cases.items() if c == "D")

    def voisins(self, p: Pos) -> list[tuple[str, Pos]]:
        """Voisins dans la grille, avec la direction (contenu quelconque)."""
        res = []
        for nom, (dx, dy) in DIRECTIONS.items():
            q = (p[0] + dx, p[1] + dy)
            if self.dans_grille(q):
                res.append((nom, q))
        return res

    def frontiere(self) -> set[Pos]:
        """Cases connues praticables ayant au moins une voisine inconnue."""
        return {
            p for p, c in self.cases.items()
            if c != "#" and any(not self.connue(q) for _, q in self.voisins(p))
        }

    def actions_possibles(self, position: Pos, cle: int,
                          adversaire: Pos | None) -> list[str]:
        """Déplacements légaux déduits des seules observations.

        Avec un rayon de vue d'au moins 1, les quatre voisines du robot sont
        toujours connues : ces actions coïncident avec ``jeu.actions_legales``
        (vérifié par test).
        """
        res = []
        for nom, q in self.voisins(position):
            c = self.contenu(q)
            if c in ("#", INCONNU) or q == adversaire:
                continue
            if c == "D" and not cle:
                continue
            res.append(nom)
        return res

    # --------------------------------------------------------- carte supposée
    def carte_supposee(self, depart_bleu: Pos, depart_rouge: Pos,
                       optimiste: bool = True) -> Carte | None:
        """Carte complète déduite de la mémoire, ou ``None`` si G est inconnue.

        Optimiste : les cases inconnues sont libres. Pessimiste : ce sont des
        murs (on ne planifie qu'à travers des cases déjà vues).
        """
        g = self.balise()
        if g is None:
            return None
        murs = {p for p, c in self.cases.items() if c == "#"}
        if not optimiste:
            murs |= {(x, y) for y in range(self.hauteur) for x in range(self.largeur)
                     if (x, y) not in self.cases}
        murs -= {depart_bleu, depart_rouge}
        return Carte(
            largeur=self.largeur,
            hauteur=self.hauteur,
            murs=frozenset(murs),
            portes=self.portes_fermees(),
            cles=self.cles(),
            balise=g,
            depart_bleu=depart_bleu,
            depart_rouge=depart_rouge,
            nom="supposee",
        )

    def chemin_vers(self, depart: Pos, cibles: set[Pos], cle: int,
                    obstacle: Pos | None = None) -> list[str] | None:
        """Plus court chemin (BFS) vers la cible la plus proche, en ne
        traversant que des cases connues praticables (portes fermées
        seulement avec une clé). L'ordre N, S, O, E départage les ex æquo."""
        self.noeuds_bfs = 0
        if not cibles:
            return None
        parents: dict[Pos, tuple[Pos, str] | None] = {depart: None}
        file = deque([depart])
        while file:
            p = file.popleft()
            self.noeuds_bfs += 1
            if p in cibles and p != depart:
                actions = []
                while parents[p] is not None:
                    p, a = parents[p][0], parents[p][1]
                    actions.append(a)
                return actions[::-1]
            for nom, q in self.voisins(p):
                c = self.contenu(q)
                if q in parents or q == obstacle or c in ("#", INCONNU):
                    continue
                if c == "D" and not cle:
                    continue
                parents[q] = (p, nom)
                file.append(q)
        return None

    # ---------------------------------------------------------------- affichage
    def afficher(self, position: Pos | None = None) -> str:
        """Carte telle que le robot la connaît (``?`` : case inconnue)."""
        lignes = ["   " + " ".join(str(x % 10) for x in range(self.largeur))]
        for y in range(self.hauteur):
            cases = []
            for x in range(self.largeur):
                p = (x, y)
                cases.append("@" if p == position else self.contenu(p))
            lignes.append(f"{y:>2} " + " ".join(cases))
        return "\n".join(lignes)
