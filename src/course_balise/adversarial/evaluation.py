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

Borne : |E| <= 400 + 50 + 0.8 pas < 1000 - Tmax, donc une
victoire ou une défaite certaine prime toujours sur l'heuristique.

Évaluation améliorée E+ (``course=True``). Elle estime l'issue de la
« course » si les deux robots filaient vers G sans se gêner. Avec le trait,
Bleu fait son dB-ième pas au demi-coup 2 dB - 1 et Rouge au demi-coup 2 dR,
donc :
    Bleu arrive le premier  <=>  dB <= dR  si Bleu a le trait,
                                 dB <  dR  si Rouge a le trait.
Le terme de distance est alors remplacé par

    E+ = ± (400 + 50 - pas * d_gagnant)   (+ termes clé et mobilité)

La valeur ne dépend plus que de la distance du robot qui gagne la course :
avancer l'améliore toujours. Avec E, ouvrir une porte peut faire chuter
l'évaluation (la porte ouverte rapproche aussi l'adversaire, qui n'a plus
besoin de clé), et à faible profondeur l'agent refuse d'ouvrir alors que
la victoire est à 3 coups : effet d'horizon observé sur salle_fermee.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from ..carte import DIRECTIONS, Carte, Pos
from ..etat import BLEU, ROUGE, Etat
from ..recherche.heuristiques import distances_bfs
from ..regles import deplacement

AMPLITUDE_DISTANCE = 400
BONUS_COURSE = 50
# Pas maximal : 400 / 3 (Dcap >= 3). Borne de |E| tous termes compris.
BORNE_EVALUATION = AMPLITUDE_DISTANCE + 0.8 * AMPLITUDE_DISTANCE / 3 + BONUS_COURSE


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
    course: bool = False  # True : évaluation améliorée E+


POIDS_BASE = Poids()
POIDS_AMELIORES = Poids(course=True)


class Evaluation:
    """E(s) du point de vue de Bleu. Instance appelable : ``evaluation(etat)``."""

    def __init__(self, carte: Carte, poids: Poids = POIDS_BASE):
        self.carte = carte
        self.poids = poids
        self.distances = Distances(carte)
        self.pas = AMPLITUDE_DISTANCE / self.distances.infini
        self.nom = "E+" if poids.course else "E"

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
        if self.poids.course and min(d_b, d_r) < self.distances.infini:
            bleu_premier = d_b <= d_r if etat.joueur == BLEU else d_b < d_r
            d_gagnant = d_b if bleu_premier else d_r
            valeur = AMPLITUDE_DISTANCE + BONUS_COURSE - pas * d_gagnant
            termes["distance"] = valeur if bleu_premier else -valeur
        return termes

    def __call__(self, etat: Etat) -> float:
        t = self.termes(etat)
        return t["distance"] + t["cle"] + t["mobilite"]
