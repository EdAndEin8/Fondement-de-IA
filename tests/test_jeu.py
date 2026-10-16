"""Tests de la boucle de partie et de l'affichage."""

from course_balise.affichage import afficher
from course_balise.agents import AgentAleatoire
from course_balise.carte import charger_carte, lister_cartes
from course_balise.etat import ROUGE
from course_balise.jeu import jouer
from course_balise.regles import Jeu


def test_affichage_plateau_initial():
    carte = charger_carte("exemple_7x7")
    texte = afficher(Jeu(carte).etat_initial(), carte, couleurs=False, entete=False)
    lignes = texte.splitlines()
    assert lignes[1] == " 0 B . . # . . ."
    assert lignes[7] == " 6 . . . . . K R"
    assert "G" in lignes[4] and "D" in lignes[5]


def test_partie_reproductible():
    carte = charger_carte("exemple_7x7")
    r1 = jouer(AgentAleatoire(), AgentAleatoire(), carte, graine=42)
    r2 = jouer(AgentAleatoire(), AgentAleatoire(), carte, graine=42)
    assert [c.action for c in r1.coups] == [c.action for c in r2.coups]
    assert r1.gagnant == r2.gagnant and r1.tours == r2.tours


def test_parties_terminent_sur_toutes_les_cartes():
    for nom in lister_cartes():
        carte = charger_carte(nom)
        for g in range(5):
            r = jouer(AgentAleatoire(), AgentAleatoire(), carte, graine=g)
            assert r.tours <= 80
            assert r.raison != "en cours"


def test_rouge_peut_commencer():
    carte = charger_carte("couloir_5x5")
    r = jouer(AgentAleatoire(), AgentAleatoire(), carte, graine=1, premier=ROUGE)
    assert r.coups[0].joueur == ROUGE
