"""Tests de l'approfondissement itératif."""

from course_balise.adversarial.evaluation import Evaluation
from course_balise.adversarial.iteratif import approfondissement_iteratif
from course_balise.adversarial.minimax import TempsEcoule, alphabeta
from course_balise.carte import Carte, charger_carte
from course_balise.regles import Jeu


def test_iteratif_renvoie_toujours_une_action_legale():
    jeu = Jeu(charger_carte("grand_labyrinthe_25x25"))
    s = jeu.etat_initial()
    res = approfondissement_iteratif(jeu, s, Evaluation(jeu.carte), budget=0.0)
    assert res.action in jeu.actions_legales(s)


def test_iteratif_respecte_le_budget():
    jeu = Jeu(charger_carte("labyrinthe_11x11"))
    res = approfondissement_iteratif(jeu, jeu.etat_initial(), Evaluation(jeu.carte), 0.05)
    assert res.temps < 0.05 + 0.03
    assert res.profondeur >= 3


def test_iteratif_meme_valeur_que_alphabeta_a_profondeur_egale():
    jeu = Jeu(charger_carte("exemple_7x7"))
    ev = Evaluation(jeu.carte)
    s = jeu.etat_initial()
    res = approfondissement_iteratif(jeu, s, ev, budget=10, profondeur_max=5)
    assert res.profondeur == 5
    assert res.valeur == alphabeta(jeu, s, 5, ev).valeur


def test_iteratif_s_arrete_sur_victoire_forcee():
    jeu = Jeu(Carte.depuis_texte("B.G\n...\n..R"))
    res = approfondissement_iteratif(jeu, jeu.etat_initial(), Evaluation(jeu.carte), 10)
    assert res.valeur == 997 and res.profondeur == 3


def test_echeance_depassee_leve_une_exception():
    jeu = Jeu(charger_carte("arene_9x9"))
    try:
        alphabeta(jeu, jeu.etat_initial(), 12, Evaluation(jeu.carte), echeance=0.0)
    except TempsEcoule:
        pass
    else:
        raise AssertionError("TempsEcoule attendue")
