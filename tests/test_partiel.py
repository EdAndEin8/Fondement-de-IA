"""Tests de l'information partielle (Partie IV)."""

import pytest
from etats import etats_de_test

from course_balise.agents import (AgentAleatoire, AgentAlphaBetaOptimiste, AgentAStar,
                                  AgentExplorateur)
from course_balise.carte import Carte, charger_carte
from course_balise.etat import BLEU, ROUGE
from course_balise.jeu import jouer
from course_balise.partiel import INCONNU, Memoire, vue_locale
from course_balise.partiel.solo import course_solo
from course_balise.partiel.vue import cases_visibles
from course_balise.regles import PASSER, Jeu

CARTES = ["exemple_7x7", "salle_fermee", "couloir_5x5", "arene_9x9",
          "porte_raccourci", "labyrinthe_11x11"]


# ----------------------------------------------------------------- vue locale
def test_vue_rayon_1_contient_la_case_et_ses_voisines():
    carte = charger_carte("arene_9x9")
    assert sorted(cases_visibles(carte, (4, 2), 1)) == [(3, 2), (4, 1), (4, 2), (4, 3), (5, 2)]
    # Dans un coin, les cases hors grille ne sont pas vues.
    assert sorted(cases_visibles(carte, (0, 0), 1)) == [(0, 0), (0, 1), (1, 0)]
    assert len(cases_visibles(carte, (4, 4), 2)) == 13


def test_vue_observe_le_contenu_des_cases():
    jeu = Jeu(charger_carte("salle_fermee"))
    s = jeu.etat_initial().avec(pb=(4, 6))
    obs = vue_locale(jeu.carte, s, BLEU)
    assert obs.cases[(4, 5)] == "D"
    assert obs.cases[(4, 6)] == "."
    assert obs.adversaire is None
    # Une fois la porte ouverte, elle est vue comme une case ordinaire.
    s2 = s.avec(portes_ouvertes=frozenset({(4, 5)}))
    assert vue_locale(jeu.carte, s2, BLEU).cases[(4, 5)] == "."


def test_adversaire_visible_seulement_dans_le_champ():
    jeu = Jeu(charger_carte("couloir_5x5"))
    s = jeu.etat_initial().avec(pb=(3, 4), pr=(4, 4))
    assert vue_locale(jeu.carte, s, BLEU).adversaire == (4, 4)
    assert vue_locale(jeu.carte, s.avec(pb=(2, 4)), BLEU).adversaire is None
    assert vue_locale(jeu.carte, s.avec(pb=(2, 4)), BLEU, rayon=2).adversaire == (4, 4)


# -------------------------------------------------------------------- mémoire
def test_une_case_vue_reste_connue_et_se_met_a_jour():
    jeu = Jeu(charger_carte("exemple_7x7"))
    mem = Memoire(jeu.carte.largeur, jeu.carte.hauteur)
    s = jeu.etat_initial().avec(pb=(2, 1))
    mem.observer(vue_locale(jeu.carte, s, BLEU))
    assert mem.contenu((2, 2)) == "K"
    # Bleu s'éloigne : la clé reste en mémoire.
    mem.observer(vue_locale(jeu.carte, s.avec(pb=(0, 0)), BLEU))
    assert mem.contenu((2, 2)) == "K"
    assert mem.contenu((6, 6)) == INCONNU
    # Rouge ramasse la clé hors de vue ; la mémoire n'est corrigée qu'en la revoyant.
    s3 = s.avec(pb=(2, 1), cles_sol=s.cles_sol - {(2, 2)})
    mem.observer(vue_locale(jeu.carte, s3, BLEU))
    assert mem.contenu((2, 2)) == "."


def test_frontiere_initiale():
    jeu = Jeu(charger_carte("arene_9x9"))
    mem = Memoire(jeu.carte.largeur, jeu.carte.hauteur)
    mem.observer(vue_locale(jeu.carte, jeu.etat_initial(), BLEU))
    # Bleu en (0, 0) voit (1, 0) et (0, 1), qui touchent des cases inconnues.
    assert mem.frontiere() == {(1, 0), (0, 1)}
    assert mem.nb_connues() == 3


def test_carte_supposee_optimiste_et_pessimiste():
    jeu = Jeu(charger_carte("couloir_5x5"))
    mem = Memoire(jeu.carte.largeur, jeu.carte.hauteur)
    s = jeu.etat_initial()
    assert mem.carte_supposee(s.pb, s.pr) is None  # balise inconnue
    mem.observer(vue_locale(jeu.carte, s.avec(pb=(2, 3)), BLEU))  # voit G en (2, 2)
    opt = mem.carte_supposee(s.pb, s.pr)
    pes = mem.carte_supposee(s.pb, s.pr, optimiste=False)
    assert opt.balise == pes.balise == (2, 2)
    assert (4, 0) not in opt.murs and (4, 0) in pes.murs  # case inconnue
    assert (1, 3) in opt.murs                             # mur observé


@pytest.mark.parametrize("nom", CARTES)
def test_actions_deduites_des_observations_sont_les_actions_legales(nom):
    jeu = Jeu(charger_carte(nom))
    for s in etats_de_test(nom, 12):
        mem = Memoire(jeu.carte.largeur, jeu.carte.hauteur)
        obs = vue_locale(jeu.carte, s, s.joueur)
        mem.observer(obs)
        possibles = mem.actions_possibles(obs.position, obs.cle, obs.adversaire) or [PASSER]
        assert sorted(possibles) == sorted(jeu.actions_legales(s)), (nom, s)


# --------------------------------------------------------------------- agents
def test_l_explorateur_ne_depend_que_de_ce_qu_il_voit():
    # Deux cartes identiques autour de Bleu, différentes ailleurs : mêmes coups.
    a = Carte.depuis_texte("B....\n.....\n..G..\n.....\n....R")
    b = Carte.depuis_texte("B....\n...#.\n.#G#.\n.....\n...KR")
    agent = AgentExplorateur()
    coups = []
    for carte in (a, b):
        agent.reinitialiser(0)
        coups.append(agent.choisir(Jeu(carte), Jeu(carte).etat_initial()))
    assert coups[0] == coups[1]


@pytest.mark.parametrize("nom", CARTES + ["grand_labyrinthe_25x25"])
@pytest.mark.parametrize("agent", [AgentExplorateur(), AgentExplorateur(2),
                                   AgentExplorateur(1, balise_connue=True)],
                         ids=str)
def test_l_explorateur_atteint_la_balise_seul(nom, agent):
    carte = charger_carte(nom)
    for joueur in (BLEU, ROUGE):
        r = course_solo(agent, carte, joueur)
        assert r.arrive, (nom, agent, joueur)
        # Il ne peut pas faire mieux qu'avec la carte complète.
        assert r.pas >= course_solo(AgentAStar(), carte, joueur).pas


@pytest.mark.parametrize("nom", CARTES)
def test_parties_sans_action_illegale(nom):
    carte = charger_carte(nom)
    for bleu, rouge in [(AgentExplorateur(), AgentAleatoire()),
                        (AgentAStar(), AgentAlphaBetaOptimiste(2, balise_connue=True)),
                        (AgentAlphaBetaOptimiste(2, rayon=2), AgentExplorateur(2))]:
        r = jouer(bleu, rouge, carte, graine=3)  # lève une erreur si un coup est illégal
        assert r.tours <= 80


def test_optimiste_joue_alphabeta_quand_l_adversaire_est_visible():
    # Bleu en (2, 1), Rouge juste à côté en (3, 1), balise en (3, 0) :
    # avec un rayon de 2, Bleu voit à la fois Rouge et la balise.
    carte = Carte.depuis_texte(".BRG.\n.....")
    jeu = Jeu(carte)
    s = jeu.etat_initial().avec(pb=(2, 1), pr=(3, 1))
    agent = AgentAlphaBetaOptimiste(4, rayon=2)
    agent.reinitialiser(0)
    action = agent.choisir(jeu, s)
    assert agent.mode == "alphabeta"
    assert action in jeu.actions_legales(s)
    assert agent.noeuds > 0
