"""État du jeu : s = (PB, PR, j, KB, KR, Ksol, Douvert, t, p).

L'état est immuable (``frozen``) et hashable : il peut servir de clé de
dictionnaire ou d'élément d'ensemble (tables de transposition, ensembles
d'états explorés...). Les éléments immuables de la carte (murs, portes
initiales, balise) n'y figurent pas.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .carte import Carte, Pos

BLEU = "B"
ROUGE = "R"
JOUEURS = (BLEU, ROUGE)
NOMS = {BLEU: "Bleu", ROUGE: "Rouge"}


def adversaire(joueur: str) -> str:
    return ROUGE if joueur == BLEU else BLEU


@dataclass(frozen=True, slots=True)
class Etat:
    pb: Pos                         # PB : position de Bleu
    pr: Pos                         # PR : position de Rouge
    joueur: str                     # j  : joueur qui doit jouer ("B" ou "R")
    kb: int                         # KB : Bleu possède une clé (0/1)
    kr: int                         # KR : Rouge possède une clé (0/1)
    cles_sol: frozenset[Pos]        # Ksol : clés encore au sol
    portes_ouvertes: frozenset[Pos] # Douvert : portes déjà ouvertes
    t: int = 0                      # t  : nombre de tours (actions) joués
    p: int = 0                      # p  : passes consécutives

    # Accès symétriques par joueur ---------------------------------------
    def position(self, joueur: str) -> Pos:
        return self.pb if joueur == BLEU else self.pr

    def cle(self, joueur: str) -> int:
        return self.kb if joueur == BLEU else self.kr

    def avec(self, **changements) -> Etat:
        """Copie modifiée (l'état d'origine n'est jamais altéré)."""
        return replace(self, **changements)

    def porte_fermee(self, carte: Carte, p: Pos) -> bool:
        return p in carte.portes and p not in self.portes_ouvertes


def etat_initial(carte: Carte, premier: str = BLEU) -> Etat:
    """État de départ. ``premier`` permet d'inverser le joueur qui commence
    (utile pour la campagne d'évaluation) ; la version de référence est Bleu."""
    return Etat(
        pb=carte.depart_bleu,
        pr=carte.depart_rouge,
        joueur=premier,
        kb=0,
        kr=0,
        cles_sol=carte.cles,
        portes_ouvertes=frozenset(),
        t=0,
        p=0,
    )
