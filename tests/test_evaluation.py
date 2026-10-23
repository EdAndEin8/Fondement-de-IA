"""Tests de la fonction d'évaluation (Partie III)."""

import pytest
from etats import etats_de_test

from course_balise.adversarial.evaluation import BORNE_EVALUATION, Evaluation
from course_balise.carte import Carte, charger_carte, lister_cartes
from course_balise.etat import BLEU, ROUGE
from course_balise.recherche import ProblemeChemin, bfs
from course_balise.regles import Jeu


def test_evaluation_symetrique_au_depart():
    for nom in ["exemple_7x7", "salle_fermee", "labyrinthe_11x11"]:
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
    ev = Evaluation(carte)
    for s in etats_de_test(nom, 20):
        assert abs(ev(s)) <= BORNE_EVALUATION < 1000 - 80
