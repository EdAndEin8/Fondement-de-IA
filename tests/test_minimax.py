"""Tests de Min-Max et Alpha-Bêta (Partie III)."""

from course_balise.adversarial.minimax import minimax
from course_balise.carte import Carte, charger_carte
from course_balise.recherche.heuristiques import distances_bfs
from course_balise.regles import Jeu


def evaluation_simple(jeu: Jeu):
    """Évaluation minimale (écart de distance BFS à G), pour tester les
    algorithmes indépendamment de la fonction d'évaluation du projet."""
    d = distances_bfs(jeu.carte, jeu.carte.balise)
    return lambda s: d.get(s.pr, 99) - d.get(s.pb, 99)


def test_victoire_immediate_trouvee():
    jeu = Jeu(Carte.depuis_texte("B.G..\n.....\n....R"))
    s = jeu.etat_initial().avec(pb=(1, 0))
    d = minimax(jeu, s, 4, evaluation_simple(jeu))
    assert d.action == "E" and d.valeur == 999


def test_rouge_minimise():
    jeu = Jeu(Carte.depuis_texte("B....\n.....\n..G.R"))
    s = jeu.etat_initial().avec(pr=(3, 2), joueur="R")
    d = minimax(jeu, s, 3, evaluation_simple(jeu))
    assert d.action == "O" and d.valeur == -999


def test_victoire_rapide_preferee():
    """Grâce à l'ajustement par la profondeur, la victoire la plus courte est choisie."""
    jeu = Jeu(Carte.depuis_texte("B.G\n...\n..R"))
    d = minimax(jeu, jeu.etat_initial(), 5, evaluation_simple(jeu))
    assert d.valeur == 1000 - 3 and d.action == "E"


def test_gagner_avant_l_adversaire():
    """Les deux robots sont à un pas de G : Bleu, qui a le trait, doit y
    entrer tout de suite (sinon Rouge gagne au demi-coup suivant)."""
    #   . . . # .
    #   . # B G R
    #   . . . # .
    jeu = Jeu(Carte.depuis_texte("B..#.\n.#.G.\n...#R"))
    s = jeu.etat_initial().avec(pb=(2, 1), pr=(4, 1))
    d = minimax(jeu, s, 2, evaluation_simple(jeu))
    assert d.action == "E" and d.valeur == 999  # Bleu entre sur G le premier


def test_valeur_terminale_prime_sur_l_evaluation():
    jeu = Jeu(Carte.depuis_texte("BG...\n.....\n....R"))
    enorme = lambda s: 500  # même une évaluation très favorable reste sous 1000
    assert minimax(jeu, jeu.etat_initial(), 3, enorme).action == "E"
