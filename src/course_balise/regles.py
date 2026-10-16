"""Règles de la version de référence (R1 à R8).

La logique d'un déplacement individuel est isolée dans :func:`deplacement`
afin d'être partagée par le jeu à deux joueurs et par les problèmes de
recherche mono-agent (Partie I) : une seule source de vérité pour les règles.
"""

from __future__ import annotations

from dataclasses import dataclass

from .carte import DIRECTIONS, Carte, Pos
from .etat import BLEU, ROUGE, Etat, adversaire, etat_initial

PASSER = "PASSER"
TMAX = 80

UTILITE_VICTOIRE = 1000
UTILITE_NUL = 0


@dataclass(frozen=True, slots=True)
class ResultatDeplacement:
    position: Pos
    cle: int
    cles_sol: frozenset[Pos]
    portes_ouvertes: frozenset[Pos]


def deplacement(
    carte: Carte,
    position: Pos,
    cle: int,
    cles_sol: frozenset[Pos],
    portes_ouvertes: frozenset[Pos],
    direction: str,
    obstacle: Pos | None = None,
) -> ResultatDeplacement | None:
    """Applique un déplacement d'un robot, ou renvoie ``None`` s'il est illégal.

    - R2 : un pas orthogonal ;
    - R3 : murs et case de l'adversaire (``obstacle``) infranchissables ;
    - R4 : ramassage automatique d'une clé si le robot n'en a pas ;
    - R5 : entrer sur une porte fermée exige une clé, la consomme et ouvre la porte.
    """
    dx, dy = DIRECTIONS[direction]
    q = (position[0] + dx, position[1] + dy)
    if not carte.praticable(q) or q == obstacle:
        return None

    if q in carte.portes and q not in portes_ouvertes:  # R5
        if not cle:
            return None
        cle = 0
        portes_ouvertes = portes_ouvertes | {q}
    elif q in cles_sol and not cle:  # R4
        cle = 1
        cles_sol = cles_sol - {q}

    return ResultatDeplacement(q, cle, cles_sol, portes_ouvertes)


class Jeu:
    """Le jeu sur une carte donnée : opérations demandées par l'énoncé."""

    def __init__(self, carte: Carte, tmax: int = TMAX):
        self.carte = carte
        self.tmax = tmax

    def etat_initial(self, premier: str = BLEU) -> Etat:
        return etat_initial(self.carte, premier)

    # ----------------------------------------------------------- actions
    def _resultat(self, etat: Etat, direction: str) -> ResultatDeplacement | None:
        j = etat.joueur
        return deplacement(
            self.carte,
            etat.position(j),
            etat.cle(j),
            etat.cles_sol,
            etat.portes_ouvertes,
            direction,
            obstacle=etat.position(adversaire(j)),
        )

    def actions_legales(self, etat: Etat) -> list[str]:
        """Déplacements légaux du joueur courant ; ``[PASSER]`` s'il est bloqué (R7)."""
        if self.terminal(etat):
            return []
        actions = [d for d in DIRECTIONS if self._resultat(etat, d) is not None]
        return actions or [PASSER]

    def transition(self, etat: Etat, action: str) -> Etat:
        """Nouvel état après ``action`` (l'état d'entrée n'est pas modifié)."""
        if self.terminal(etat):
            raise ValueError("la partie est terminée")
        suivant = adversaire(etat.joueur)  # R1 : alternance

        if action == PASSER:
            if self.actions_legales(etat) != [PASSER]:
                raise ValueError("passer n'est autorisé que si le joueur est bloqué")
            return etat.avec(joueur=suivant, t=etat.t + 1, p=etat.p + 1)

        if action not in DIRECTIONS:
            raise ValueError(f"action inconnue : {action!r}")
        r = self._resultat(etat, action)
        if r is None:
            raise ValueError(f"action illégale : {action} pour {etat.joueur}")

        changements = dict(
            joueur=suivant,
            cles_sol=r.cles_sol,
            portes_ouvertes=r.portes_ouvertes,
            t=etat.t + 1,
            p=0,
        )
        if etat.joueur == BLEU:
            changements.update(pb=r.position, kb=r.cle)
        else:
            changements.update(pr=r.position, kr=r.cle)
        return etat.avec(**changements)

    # ----------------------------------------------------------- fin de partie
    def gagnant(self, etat: Etat) -> str | None:
        """R6 : le premier robot sur G gagne (les deux ne peuvent pas y être)."""
        if etat.pb == self.carte.balise:
            return BLEU
        if etat.pr == self.carte.balise:
            return ROUGE
        return None

    def terminal(self, etat: Etat) -> bool:
        return (
            self.gagnant(etat) is not None
            or etat.p >= 2          # R7 : deux passes consécutives
            or etat.t >= self.tmax  # R8 : limite de tours
        )

    def utilite(self, etat: Etat, joueur: str = BLEU) -> int:
        """+1000 si ``joueur`` gagne, -1000 s'il perd, 0 sinon (match nul)."""
        g = self.gagnant(etat)
        if g is None:
            return UTILITE_NUL
        return UTILITE_VICTOIRE if g == joueur else -UTILITE_VICTOIRE

    def raison_fin(self, etat: Etat) -> str:
        if (g := self.gagnant(etat)) is not None:
            return f"victoire {g}"
        if etat.p >= 2:
            return "nul (deux passes)"
        if etat.t >= self.tmax:
            return "nul (limite de tours)"
        return "en cours"
