"""Fonction d'évaluation E(s) pour la recherche tronquée (Partie III).

Toutes les valeurs sont exprimées du point de vue de Bleu (Bleu maximise,
Rouge minimise), comme l'utilité U(s) de l'énoncé.

Évaluation de base :

    E(s) = w1 (dR - dB) + w2 (kB - kR) + w3 (mB - mR)

- dB, dR : estimation du nombre de déplacements restants jusqu'à G. Elle
  tient compte des clés et des portes (voir :class:`Distances`) ; l'autre
  robot est ignoré, car il bouge.
- kB, kR : possession d'une clé (0 ou 1).
- mB, mR : mobilité, nombre de déplacements légaux (0 à 4).

Normalisation et poids (voir docs/seance2.md). Les trois termes sont
exprimés en « pas » puis multipliés par la valeur d'un pas :

    pas = 400 / Dcap,   Dcap = 2 * (plus grande distance à G sur la carte) + 1

    E(s) = pas * [ (dR - dB) + 0.4 (kB - kR) + 0.1 (mB - mR) ]

- Dcap majore toute distance finie (même avec le détour par une clé) et
  sert de distance pour un robot qui ne peut plus atteindre G : l'écart de
  distance reste dans [-Dcap, Dcap] et le terme principal dans [-400, 400].
- w1 = pas : la distance relative est le facteur principal.
- w2 = 0.4 pas : la clé est déjà prise en compte dans la distance (un robot
  sans clé doit faire le détour) ; ce terme ne fait que départager et vaut
  moins qu'un pas.
- w3 = 0.1 pas : la mobilité (0 à 4) départage les positions équivalentes
  et pénalise les culs-de-sac, sans jamais compenser un pas de retard.

Normaliser par la taille de la carte plutôt qu'écrêter l'écart est
important : avec un écart écrêté, dès que l'adversaire ne peut plus gagner
(il n'a plus de clé à prendre), l'écart reste au plafond quelle que soit la
position de l'agent, qui n'a plus aucune raison d'avancer et laisse filer
la partie jusqu'au nul (cas observé sur salle_fermee).

Borne : |E| <= 400 + 0.8 pas < 1000 - Tmax, donc une
victoire ou une défaite certaine prime toujours sur l'heuristique.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..carte import DIRECTIONS, Carte, Pos
from ..etat import BLEU, ROUGE, Etat
from ..recherche.heuristiques import distances_bfs
from ..regles import deplacement

AMPLITUDE_DISTANCE = 400
# Pas maximal : 400 / 3 (Dcap >= 3). Borne de |E| tous termes compris.
BORNE_EVALUATION = AMPLITUDE_DISTANCE + 0.8 * AMPLITUDE_DISTANCE / 3


class Distances:
    """Estimation de la distance à G d'un robot, avec clés et portes.

    - avec une clé : distance sur la carte où les portes sont franchissables ;
    - sans clé : minimum entre
        * la distance en évitant les portes encore fermées,
        * le détour par une clé au sol : d(pos, k) + d(k, G) avec portes
          franchissables (le robot aura alors une clé).

    Toutes les tables sont des BFS précalculés (mis en cache par ensemble de
    portes ouvertes), si bien qu'une évaluation ne coûte que quelques
    accès à des dictionnaires, ce qui compte quand Min-Max en fait des
    dizaines de milliers.
    """

    def __init__(self, carte: Carte):
        self.carte = carte
        self.d_relaxee = distances_bfs(carte, carte.balise)
        #: Majorant des distances finies, utilisé aussi pour « inaccessible ».
        self.infini = 2 * max(self.d_relaxee.values()) + 1
        self._fermees: dict[frozenset[Pos], dict[Pos, int]] = {}
        self._depuis_cle: dict[tuple[Pos, frozenset[Pos]], dict[Pos, int]] = {}

    def _sans_portes_fermees(self, ouvertes: frozenset[Pos]) -> dict[Pos, int]:
        d = self._fermees.get(ouvertes)
        if d is None:
            d = distances_bfs(self.carte, self.carte.balise, self.carte.portes - ouvertes)
            self._fermees[ouvertes] = d
        return d

    def _depuis(self, cle: Pos, ouvertes: frozenset[Pos]) -> dict[Pos, int]:
        d = self._depuis_cle.get((cle, ouvertes))
        if d is None:
            d = distances_bfs(self.carte, cle, self.carte.portes - ouvertes)
            self._depuis_cle[(cle, ouvertes)] = d
        return d

    def distance(self, pos: Pos, cle: int, cles_sol: Iterable[Pos],
                 ouvertes: frozenset[Pos]) -> int:
        inf = self.infini
        if cle:
            return self.d_relaxee.get(pos, inf)
        meilleure = self._sans_portes_fermees(ouvertes).get(pos, inf)
        for k in cles_sol:
            d = self._depuis(k, ouvertes).get(pos, inf) + self.d_relaxee.get(k, inf)
            if d < meilleure:
                meilleure = d
        return min(meilleure, inf)

    def du_joueur(self, etat: Etat, joueur: str) -> int:
        return self.distance(etat.position(joueur), etat.cle(joueur),
                             etat.cles_sol, etat.portes_ouvertes)


def mobilite(carte: Carte, etat: Etat, joueur: str) -> int:
    """Nombre de déplacements légaux de ``joueur`` (qu'il ait le trait ou non)."""
    adv = ROUGE if joueur == BLEU else BLEU
    pos, cle, obstacle = etat.position(joueur), etat.cle(joueur), etat.position(adv)
    return sum(
        deplacement(carte, pos, cle, etat.cles_sol, etat.portes_ouvertes, d, obstacle)
        is not None
        for d in DIRECTIONS
    )


@dataclass(frozen=True)
class Poids:
    """Poids relatifs, exprimés en « pas »."""
    distance: float = 1.0
    cle: float = 0.4
    mobilite: float = 0.1


POIDS_BASE = Poids()


class Evaluation:
    """E(s) du point de vue de Bleu. Instance appelable : ``evaluation(etat)``."""

    def __init__(self, carte: Carte, poids: Poids = POIDS_BASE):
        self.carte = carte
        self.poids = poids
        self.distances = Distances(carte)
        self.pas = AMPLITUDE_DISTANCE / self.distances.infini

    def termes(self, etat: Etat) -> dict[str, float]:
        """Détail des termes (utile pour comprendre une décision)."""
        d_b = self.distances.du_joueur(etat, BLEU)
        d_r = self.distances.du_joueur(etat, ROUGE)
        pas = self.pas
        termes = {
            "dB": d_b,
            "dR": d_r,
            "distance": pas * self.poids.distance * (d_r - d_b),
            "cle": pas * self.poids.cle * (etat.kb - etat.kr),
            "mobilite": pas * self.poids.mobilite * (mobilite(self.carte, etat, BLEU)
                                                     - mobilite(self.carte, etat, ROUGE)),
        }
        return termes

    def __call__(self, etat: Etat) -> float:
        t = self.termes(etat)
        return t["distance"] + t["cle"] + t["mobilite"]
