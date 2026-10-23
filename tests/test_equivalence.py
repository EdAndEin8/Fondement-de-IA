"""Min-Max et Alpha-Bêta doivent renvoyer la même valeur (énoncé, 5.2)."""

import pytest
from etats import etats_de_test

from course_balise.adversarial.evaluation import Evaluation
from course_balise.adversarial.minimax import alphabeta, minimax
from course_balise.adversarial.ordre import ORDRES
from course_balise.carte import charger_carte, lister_cartes
from course_balise.regles import Jeu


@pytest.mark.parametrize("nom", lister_cartes())
@pytest.mark.parametrize("ordre", list(ORDRES))
def test_alphabeta_meme_valeur_que_minimax(nom, ordre):
    jeu = Jeu(charger_carte(nom))
    ev = Evaluation(jeu.carte)
    for s in etats_de_test(nom, 6, graine=len(ordre)):
        for d in (1, 2, 3, 4):
            mm = minimax(jeu, s, d, ev, ordre=ordre)
            ab = alphabeta(jeu, s, d, ev, ordre=ordre)
            assert ab.valeur == mm.valeur, (nom, ordre, d, s)
            assert ab.stats.noeuds <= mm.stats.noeuds
            # Le coup d'Alpha-Bêta est l'un des coups optimaux de Min-Max
            # (les deux peuvent départager différemment les ex æquo).
            assert mm.valeurs_racine[ab.action] == mm.valeur


@pytest.mark.parametrize("nom", ["exemple_7x7", "arene_9x9"])
def test_meme_valeur_a_profondeur_6(nom):
    jeu = Jeu(charger_carte(nom))
    ev = Evaluation(jeu.carte)
    for s in etats_de_test(nom, 4, graine=7):
        assert minimax(jeu, s, 6, ev).valeur == alphabeta(jeu, s, 6, ev).valeur
