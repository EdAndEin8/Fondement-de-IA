"""Tests de la fonction d'évaluation (Partie III)."""

import pytest
from etats import etats_de_test

from course_balise.adversarial.evaluation import (BORNE_EVALUATION, POIDS_AMELIORES,
                                                  Evaluation)
from course_balise.adversarial.minimax import alphabeta
from course_balise.carte import Carte, charger_carte, lister_cartes
from course_balise.etat import BLEU, ROUGE
from course_balise.recherche import ProblemeChemin, bfs
from course_balise.regles import Jeu


def test_evaluation_symetrique_au_depart():
    for nom in ["exemple_7x7", "salle_fermee", "labyrinthe_11x11", "arene_9x9"]:
        jeu = Jeu(charger_carte(nom))
        assert Evaluation(jeu.carte)(jeu.etat_initial()) == 0


def test_distances_egales_a_la_recherche_sans_adversaire():
    """Sur les cartes à une seule clé, l'estimation de distance est exacte."""
    for nom in ["porte_raccourci", "salle_fermee", "couloir_5x5"]:
        carte = charger_carte(nom)
        ev = Evaluation(carte)
        for s in etats_de_test(nom, 15):
            for j in (BLEU, ROUGE):
                pb = ProblemeChemin.depuis_etat(carte, s, j)
                pb.obstacle = None
                vrai = bfs(pb).longueur
                if vrai is None:  # balise inaccessible : distance « infinie »
                    vrai = ev.distances.infini
                assert ev.distances.du_joueur(s, j) == vrai, (nom, s, j)


def test_avance_de_bleu_donne_une_evaluation_positive():
    jeu = Jeu(Carte.depuis_texte("B....G....R"))
    ev = Evaluation(jeu.carte)
    s = jeu.etat_initial()
    assert ev(s.avec(pb=(2, 0))) > ev(s) == 0
    assert ev(s.avec(pr=(7, 0))) < 0


def test_la_cle_compte_dans_la_distance():
    jeu = Jeu(charger_carte("salle_fermee"))
    ev = Evaluation(jeu.carte)
    s = jeu.etat_initial()
    s_cle = s.avec(pb=(4, 0), kb=1, cles_sol=frozenset())
    t = ev.termes(s_cle)
    assert t["dB"] < ev.termes(s)["dB"]
    assert t["dR"] == ev.distances.infini  # Rouge ne peut plus gagner
    assert ev(s_cle) > 0


@pytest.mark.parametrize("nom", lister_cartes())
def test_evaluation_bornee_sous_les_utilites(nom):
    carte = charger_carte(nom)
    for ev in (Evaluation(carte), Evaluation(carte, POIDS_AMELIORES)):
        for s in etats_de_test(nom, 20):
            assert abs(ev(s)) <= BORNE_EVALUATION < 1000 - 80


def test_avancer_reste_utile_quand_l_adversaire_est_bloque():
    """Rouge ne peut plus gagner (plus de clé) : avancer doit encore payer.

    Avec un écart de distance écrêté, toutes ces positions avaient la même
    valeur et Bleu ne cherchait plus à atteindre la balise."""
    jeu = Jeu(charger_carte("salle_fermee"))
    ev = Evaluation(jeu.carte)
    s = jeu.etat_initial().avec(pr=(0, 0), kb=1, cles_sol=frozenset())
    loin, pres = s.avec(pb=(8, 0)), s.avec(pb=(4, 6))
    assert ev(pres) > ev(loin)


def test_evaluation_amelioree_tient_compte_du_trait():
    jeu = Jeu(charger_carte("couloir_5x5"))
    ev = Evaluation(jeu.carte, POIDS_AMELIORES)
    s = jeu.etat_initial().avec(pb=(3, 1), pr=(2, 4))  # dB = dR = 2
    assert ev(s) > 0 > ev(s.avec(joueur=ROUGE))


def test_effet_d_horizon_porte_salle_fermee():
    """Bleu a la clé, devant la porte ; victoire en 3 coups (5 demi-coups).

    Avec E, ouvrir la porte fait chuter l'évaluation (Rouge n'a plus besoin
    de clé) : à profondeur 4, Bleu refuse d'ouvrir. E+ corrige ce cas.
    """
    jeu = Jeu(charger_carte("salle_fermee"))
    s = jeu.etat_initial().avec(pb=(4, 6), pr=(0, 0), kb=1, cles_sol=frozenset(), t=36)
    base, amelioree = Evaluation(jeu.carte), Evaluation(jeu.carte, POIDS_AMELIORES)
    assert alphabeta(jeu, s, 4, base).action != "N"
    assert alphabeta(jeu, s, 5, base).action == "N"
    assert alphabeta(jeu, s, 4, amelioree).action == "N"
    assert alphabeta(jeu, s, 2, amelioree).action == "N"
