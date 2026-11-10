"""Tests de la représentation des connaissances et du raisonnement (Partie II)."""

import pytest
from etats import etats_de_test

from course_balise.carte import Carte, charger_carte
from course_balise.etat import BLEU, ROUGE
from course_balise.raisonnement import (REGLES, BaseConnaissances, chainage_avant,
                                        faits_de_etat, substituer, unifier)
from course_balise.regles import Jeu

CARTES = ["exemple_7x7", "salle_fermee", "couloir_5x5", "arene_9x9",
          "porte_raccourci", "labyrinthe_11x11"]


# --------------------------------------------------------------- unification
def test_unification_lie_les_variables():
    assert unifier(("position", "?r", "?c"), ("position", "bleu", (1, 0)), {}) == {
        "?r": "bleu", "?c": (1, 0)}


def test_unification_variable_repetee():
    # ?c doit prendre la même valeur dans tout le motif.
    assert unifier(("voisine", "?c", "?c"), ("voisine", (1, 0), (1, 0)), {}) == {"?c": (1, 0)}
    assert unifier(("voisine", "?c", "?c"), ("voisine", (1, 0), (2, 0)), {}) is None


def test_unification_echoue_sur_constante_differente():
    assert unifier(("but", "?g"), ("mur", (0, 0)), {}) is None
    assert unifier(("trait", "bleu"), ("trait", "rouge"), {}) is None


def test_substituer_instancie_la_conclusion():
    assert substituer(("deplacement_possible", "?r", "?d"),
                      {"?r": "bleu", "?d": (2, 0)}) == ("deplacement_possible", "bleu", (2, 0))


# ------------------------------------------------------------- chaînage avant
def test_chainage_avant_atteint_un_point_fixe():
    jeu = Jeu(charger_carte("exemple_7x7"))
    base = faits_de_etat(jeu.carte, jeu.etat_initial())
    faits, _ = chainage_avant(base, REGLES)
    # Réappliquer les règles ne produit plus rien.
    faits2, _ = chainage_avant(faits, REGLES)
    assert faits2 == faits
    assert base <= faits


def test_faits_deduits_disjoints_des_faits_observes():
    jeu = Jeu(charger_carte("salle_fermee"))
    bc = BaseConnaissances(jeu.carte, jeu.etat_initial())
    assert bc.faits_deduits().isdisjoint(bc.faits_base)
    # deplacement_possible est une conclusion, jamais un fait observé.
    assert all(f[0] != "deplacement_possible" for f in bc.faits_base)
    assert any(f[0] == "deplacement_possible" for f in bc.faits_deduits())


# ------------------------------- cohérence avec les règles du jeu (R1–R8)
def cibles_legales(jeu: Jeu, etat) -> set:
    """Cases atteignables par un déplacement légal du joueur courant."""
    j = etat.joueur
    cibles = set()
    for a in jeu.actions_legales(etat):
        if a == "PASSER":
            continue
        cibles.add(jeu.transition(etat, a).position(j))
    return cibles


@pytest.mark.parametrize("nom", CARTES)
def test_deplacement_possible_coherent_avec_actions_legales(nom):
    jeu = Jeu(charger_carte(nom))
    for s in etats_de_test(nom, 12):
        bc = BaseConnaissances(jeu.carte, s)
        r = {BLEU: "bleu", ROUGE: "rouge"}[s.joueur]
        deduites = {f[2] for f in bc.faits
                    if f[0] == "deplacement_possible" and f[1] == r}
        assert deduites == cibles_legales(jeu, s), (nom, s)


# --------------------------------------------- scénarios justifier / interdire
def carte_porte():
    # B . D . G   (porte en (2,0) entre Bleu et la balise)
    # R . . . .
    return Carte.depuis_texte("B.D.G\nR....", nom="porte_test")


def test_justifier_ouverture_avec_cle():
    """Avec une clé devant la porte, ouvrir est un déplacement possible."""
    jeu = Jeu(carte_porte())
    s = jeu.etat_initial().avec(pb=(1, 0), kb=1)
    bc = BaseConnaissances(jeu.carte, s)
    assert bc.contient(("peut_ouvrir", "bleu", (2, 0)))
    assert bc.contient(("deplacement_possible", "bleu", (2, 0)))
    # La justification remonte jusqu'à des faits observés.
    explication = bc.expliquer(("deplacement_possible", "bleu", (2, 0)))
    assert "peut_ouvrir" in explication
    assert "[observé]" in explication


def test_interdire_porte_sans_cle():
    """Sans clé, la même porte est un déplacement interdit, pas possible."""
    jeu = Jeu(carte_porte())
    s = jeu.etat_initial().avec(pb=(1, 0))  # kb = 0
    bc = BaseConnaissances(jeu.carte, s)
    assert bc.contient(("interdit", "bleu", (2, 0)))
    assert not bc.contient(("peut_ouvrir", "bleu", (2, 0)))
    assert not bc.contient(("deplacement_possible", "bleu", (2, 0)))


def test_coup_gagnant_devant_la_balise():
    jeu = Jeu(carte_porte())
    s = jeu.etat_initial().avec(pb=(3, 0))  # voisin de G en (4,0)
    bc = BaseConnaissances(jeu.carte, s)
    assert bc.contient(("coup_gagnant", "bleu", (4, 0)))
    assert bc.contient(("deplacement_possible", "bleu", (4, 0)))


def test_peut_ramasser_une_cle_voisine():
    # B . K . G : la clé est en (2,0)
    jeu = Jeu(Carte.depuis_texte("B.K.G\nR....", nom="cle_test"))
    s = jeu.etat_initial().avec(pb=(1, 0))  # sans clé, voisin de la clé
    bc = BaseConnaissances(jeu.carte, s)
    assert bc.contient(("peut_ramasser", "bleu", (2, 0)))
    assert bc.contient(("deplacement_possible", "bleu", (2, 0)))
