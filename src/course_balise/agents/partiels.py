"""Agents à information partielle (Partie IV).

Ces agents ne lisent jamais l'état réel directement : à chaque tour, ils
reçoivent la vue locale de leur robot (:func:`partiel.vue_locale`), la
mémorisent, et décident à partir de leur seule mémoire.

- :class:`AgentExplorateur` : si la balise est connue (vue, ou donnée
  d'emblée avec ``balise_connue``, comme si elle émettait un signal), planification
  **optimiste** par A* sur la carte supposée (cases inconnues libres) ;
  sinon, exploration de la **frontière** la plus proche. Le plan est
  recalculé à chaque tour, donc corrigé dès qu'une observation le contredit.
  L'adversaire est un obstacle à sa dernière position connue, tant qu'on n'a
  pas vu qu'il en est parti.
- :class:`AgentAlphaBetaOptimiste` : même comportement, mais quand
  l'adversaire est visible et la balise connue, joue Alpha-Bêta sur le jeu
  supposé (carte supposée, adversaire à sa position observée, supposé sans
  clé). C'est une approximation explicite : on ne résout pas le jeu à
  information imparfaite.
"""

from __future__ import annotations

from ..adversarial.evaluation import POIDS_AMELIORES, Evaluation
from ..adversarial.minimax import alphabeta
from ..etat import BLEU, Etat
from ..partiel import Memoire, Observation, vue_locale
from ..recherche import HEURISTIQUES, EtatRecherche, ProblemeChemin, astar
from ..regles import PASSER, Jeu
from .base import Agent


def _suffixe(rayon: int, balise_connue: bool) -> str:
    return ("" if rayon == 1 else f"-r{rayon}") + ("-g" if balise_connue else "")


class AgentExplorateur(Agent):
    """Exploration des frontières, puis planification optimiste vers G."""

    def __init__(self, rayon: int = 1, balise_connue: bool = False,
                 heuristique: str = "cles"):
        super().__init__()
        self.rayon = rayon
        self.balise_connue = balise_connue
        self.heuristique = heuristique
        self.nom = "explorateur" + _suffixe(rayon, balise_connue)
        self.memoire: Memoire | None = None
        self.mode = ""
        #: Nombre de décisions prises dans chaque mode pendant la partie.
        self.modes: dict[str, int] = {}

    def reinitialiser(self, graine: int) -> None:
        super().reinitialiser(graine)
        self.memoire = None
        self.modes = {}

    # ------------------------------------------------------------ décision
    def choisir(self, jeu: Jeu, etat: Etat) -> str:
        if self.memoire is None:
            # Seules les dimensions du plateau sont supposées connues.
            self.memoire = Memoire(jeu.carte.largeur, jeu.carte.hauteur)
            if self.balise_connue:
                # Variante : seule la position de G est donnée au départ.
                self.memoire.cases[jeu.carte.balise] = "G"
        obs = vue_locale(jeu.carte, etat, etat.joueur, self.rayon)
        self.memoire.observer(obs)
        self.noeuds = 0
        legales = self.memoire.actions_possibles(obs.position, obs.cle, obs.adversaire)
        if not legales:
            self._noter("bloque")
            return PASSER
        action = self.decider(obs, etat.t, etat.p)
        if action not in legales:
            self._noter("hasard")
            return self.rng.choice(legales)
        return action

    def _noter(self, mode: str) -> None:
        self.mode = mode
        self.modes[mode] = self.modes.get(mode, 0) + 1

    def decider(self, obs: Observation, tour: int, passes: int) -> str | None:
        return self.vers_balise(obs) or self.explorer(obs)

    def vers_balise(self, obs: Observation) -> str | None:
        """Premier pas d'un plus court chemin optimiste vers G, si G est connue."""
        mem = self.memoire
        carte = mem.carte_supposee(obs.position, obs.position)
        if carte is None:
            return None
        depart = EtatRecherche(obs.position, obs.cle, mem.cles(), frozenset())
        h = HEURISTIQUES[self.heuristique](carte)
        for obstacle in (mem.adversaire_suppose(), None):
            r = astar(ProblemeChemin(carte, depart, obstacle), h)
            self.noeuds += r.noeuds_developpes
            if r.trouve and r.actions:
                self._noter("balise")
                return r.actions[0]
            if obstacle is None:
                break
        return None

    def explorer(self, obs: Observation) -> str | None:
        """Premier pas vers la case de frontière la plus proche.

        Sans clé, une clé connue est aussi une cible : elle permet ensuite de
        franchir les portes, derrière lesquelles se trouve souvent la balise.
        """
        mem = self.memoire
        cibles = mem.frontiere()
        if not obs.cle:
            cibles |= mem.cles()
        for obstacle in (mem.adversaire_suppose(), None):
            chemin = mem.chemin_vers(obs.position, cibles - {obstacle}, obs.cle, obstacle)
            self.noeuds += mem.noeuds_bfs
            if chemin:
                self._noter("exploration")
                return chemin[0]
            if obstacle is None:
                break
        return None


class AgentAlphaBetaOptimiste(AgentExplorateur):
    """Alpha-Bêta sur le jeu supposé quand l'adversaire est visible."""

    def __init__(self, profondeur: int = 4, rayon: int = 1, balise_connue: bool = False):
        super().__init__(rayon, balise_connue)
        self.profondeur = profondeur
        self.nom = f"optimiste-d{profondeur}" + _suffixe(rayon, balise_connue)

    def decider(self, obs: Observation, tour: int, passes: int) -> str | None:
        if obs.adversaire is not None:
            action = self.alphabeta_suppose(obs, tour, passes)
            if action is not None:
                return action
        return super().decider(obs, tour, passes)

    def alphabeta_suppose(self, obs: Observation, tour: int, passes: int) -> str | None:
        mem = self.memoire
        moi, adv = obs.position, obs.adversaire
        bleu = obs.joueur == BLEU
        pb, pr = (moi, adv) if bleu else (adv, moi)
        carte = mem.carte_supposee(pb, pr)
        if carte is None:
            return None
        jeu = Jeu(carte)
        etat = Etat(
            pb=pb, pr=pr, joueur=obs.joueur,
            kb=obs.cle if bleu else 0,      # clé de l'adversaire inconnue :
            kr=0 if bleu else obs.cle,      # supposée absente (hypothèse optimiste)
            cles_sol=mem.cles(),
            portes_ouvertes=frozenset(),
            t=tour, p=passes,
        )
        if jeu.terminal(etat):
            return None
        dec = alphabeta(jeu, etat, self.profondeur, Evaluation(carte, POIDS_AMELIORES))
        self.noeuds += dec.stats.noeuds
        self._noter("alphabeta")
        return dec.action
