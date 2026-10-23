"""Tests de Min-Max et Alpha-Bêta (Partie III)."""

from course_balise.adversarial.minimax import alphabeta, minimax
from course_balise.adversarial.ordre import ORDRES
from course_balise.carte import Carte, charger_carte
from course_balise.etat import BLEU
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
    for f in (minimax, alphabeta):
        d = f(jeu, s, 4, evaluation_simple(jeu))
        assert d.action == "E" and d.valeur == 999


def test_rouge_minimise():
    jeu = Jeu(Carte.depuis_texte("B....\n.....\n..G.R"))
    s = jeu.etat_initial().avec(pr=(3, 2), joueur="R")
    for f in (minimax, alphabeta):
        d = f(jeu, s, 3, evaluation_simple(jeu))
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
    for f in (minimax, alphabeta):
        d = f(jeu, s, 2, evaluation_simple(jeu))
        assert d.action == "E" and d.valeur == 999  # Bleu entre sur G le premier


def test_valeur_terminale_prime_sur_l_evaluation():
    jeu = Jeu(Carte.depuis_texte("BG...\n.....\n....R"))
    enorme = lambda s: 500  # même une évaluation très favorable reste sous 1000
    assert minimax(jeu, jeu.etat_initial(), 3, enorme).action == "E"


def test_alphabeta_visite_moins_de_noeuds():
    jeu = Jeu(charger_carte("exemple_7x7"))
    ev = evaluation_simple(jeu)
    s = jeu.etat_initial()
    for d in (2, 4, 6):
        mm, ab = minimax(jeu, s, d, ev), alphabeta(jeu, s, d, ev)
        assert ab.valeur == mm.valeur and ab.stats.noeuds <= mm.stats.noeuds
    assert ab.stats.coupures > 0


def test_statistiques():
    jeu = Jeu(charger_carte("exemple_7x7"))
    d = minimax(jeu, jeu.etat_initial(), 2, evaluation_simple(jeu))
    assert d.stats.noeuds == 1 + 2 + d.stats.feuilles  # racine, 2 fils de Bleu, feuilles
    assert d.profondeur == 2 and d.stats.temps > 0


def test_bon_ordre_reduit_les_noeuds():
    from course_balise.adversarial.evaluation import Evaluation
    jeu = Jeu(charger_carte("arene_9x9"))
    ev = Evaluation(jeu.carte)
    s = jeu.etat_initial()
    n = {o: alphabeta(jeu, s, 6, ev, ordre=o).stats.noeuds for o in ORDRES}
    assert n["evaluation"] < n["naturel"] < n["pire"]


def test_ordre_aleatoire_reproductible():
    jeu = Jeu(charger_carte("arene_9x9"))
    s = jeu.etat_initial()
    o = ORDRES["aleatoire"]
    assert o(jeu, s, ["N", "S", "O", "E"], None) == o(jeu, s, ["N", "S", "O", "E"], None)
    assert s.joueur == BLEU
