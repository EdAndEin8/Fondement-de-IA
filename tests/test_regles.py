"""Tests des règles R1 à R8 et des propriétés de l'état."""

import pytest

from course_balise.carte import Carte, CarteInvalide, charger_carte
from course_balise.etat import BLEU, ROUGE, Etat
from course_balise.regles import PASSER, Jeu


def jeu_de(texte: str, **kw) -> Jeu:
    return Jeu(Carte.depuis_texte(texte), **kw)


# --------------------------------------------------------------------- carte
def test_parseur_carte_exemple():
    c = charger_carte("exemple_7x7")
    assert (c.largeur, c.hauteur) == (7, 7)
    assert c.depart_bleu == (0, 0) and c.depart_rouge == (6, 6)
    assert c.balise == (3, 3)
    assert c.cles == {(2, 2), (5, 6)}
    assert c.portes == {(3, 4)}
    assert (3, 0) in c.murs and len(c.murs) == 10


@pytest.mark.parametrize(
    "texte",
    ["B.G\n..", "B..\n...", "BB.\nRG.", "B.X\nRG."],
)
def test_carte_invalide(texte):
    with pytest.raises(CarteInvalide):
        Carte.depuis_texte(texte)


# --------------------------------------------------------------------- état
def test_etat_hashable_et_comparable():
    jeu = Jeu(charger_carte("exemple_7x7"))
    s1, s2 = jeu.etat_initial(), jeu.etat_initial()
    assert s1 == s2 and hash(s1) == hash(s2)
    assert len({s1, s2}) == 1
    assert {s1: "ok"}[s2] == "ok"


def test_transition_ne_modifie_pas_l_etat():
    jeu = Jeu(charger_carte("exemple_7x7"))
    s = jeu.etat_initial()
    s2 = jeu.transition(s, "E")
    assert s.pb == (0, 0) and s.t == 0 and s.joueur == BLEU
    assert s2.pb == (1, 0) and s2.t == 1 and s2.joueur == ROUGE
    with pytest.raises(AttributeError):
        s.pb = (5, 5)  # type: ignore[misc]


# --------------------------------------------------------------------- R1/R2
def test_alternance_et_premier_joueur():
    jeu = Jeu(charger_carte("couloir_5x5"))
    s = jeu.etat_initial()
    assert s.joueur == BLEU
    s = jeu.transition(s, "E")
    assert s.joueur == ROUGE
    assert jeu.etat_initial(premier=ROUGE).joueur == ROUGE


def test_pas_de_diagonale_ni_sortie_de_grille():
    jeu = Jeu(charger_carte("couloir_5x5"))
    s = jeu.etat_initial()  # Bleu en (0,0)
    assert set(jeu.actions_legales(s)) == {"E", "S"}
    with pytest.raises(ValueError):
        jeu.transition(s, "NE")
    with pytest.raises(ValueError):
        jeu.transition(s, "N")


# --------------------------------------------------------------------- R3
def test_murs_infranchissables():
    jeu = jeu_de("B#G\n..R")
    s = jeu.etat_initial()
    assert "E" not in jeu.actions_legales(s)
    with pytest.raises(ValueError):
        jeu.transition(s, "E")


def test_collision_avec_adversaire():
    jeu = jeu_de("BR.\n#.G")
    s = jeu.etat_initial()
    assert jeu.actions_legales(s) == [PASSER]  # Bleu coincé entre mur, bord et Rouge
    s_r = jeu.transition(s, PASSER)
    assert "O" not in jeu.actions_legales(s_r)  # Rouge ne peut pas entrer sur Bleu


# --------------------------------------------------------------------- R4
def test_ramassage_de_cle():
    jeu = jeu_de("BK.\n..R\nG..")
    s = jeu.transition(jeu.etat_initial(), "E")
    assert s.kb == 1 and (1, 0) not in s.cles_sol


def test_une_seule_cle_par_robot():
    jeu = jeu_de("BKK.\n...R\nG...")
    s = jeu.transition(jeu.etat_initial(), "E")       # Bleu ramasse (1,0)
    s = jeu.transition(s, "N")                        # Rouge
    s = jeu.transition(s, "E")                        # Bleu passe sur (2,0)
    assert s.kb == 1 and s.cles_sol == {(2, 0)}       # la seconde clé reste au sol


def test_cle_ramassee_disparait_pour_l_adversaire():
    jeu = jeu_de("BK.R\n#..#\nG...")
    s = jeu.transition(jeu.etat_initial(), "E")       # Bleu ramasse
    assert s.kb == 1 and not s.cles_sol
    s = jeu.transition(s, "O")                        # Rouge en (2,0)
    assert s.kr == 0


# --------------------------------------------------------------------- R5
def test_porte_interdite_sans_cle():
    jeu = jeu_de("BD.\n###\nR.G")
    s = jeu.etat_initial()
    assert jeu.actions_legales(s) == [PASSER]


def test_ouverture_de_porte_consomme_la_cle():
    jeu = jeu_de("BKD.\n####\nR..G")
    s = jeu.transition(jeu.etat_initial(), "E")       # clé
    s = jeu.transition(s, "E")                        # Rouge
    assert "E" in jeu.actions_legales(s)
    s = jeu.transition(s, "E")                        # Bleu ouvre la porte
    assert s.pb == (2, 0) and s.kb == 0
    assert s.portes_ouvertes == {(2, 0)}


def test_porte_ouverte_reste_ouverte_pour_les_deux():
    jeu = jeu_de("RKD.B\n####.\n...G.")
    # Rouge commence pour ouvrir la porte, puis Bleu l'emprunte sans clé.
    s = jeu.etat_initial(premier=ROUGE)
    s = jeu.transition(s, "E")      # R ramasse
    s = jeu.transition(s, "S")      # B (4,1)
    s = jeu.transition(s, "E")      # R ouvre (2,0)
    s = jeu.transition(s, "N")      # B (4,0)
    s = jeu.transition(s, "E")      # R (3,0)
    s = jeu.transition(s, "S")      # B (4,1)
    s = jeu.transition(s, "O")      # R (2,0) : retour sur la porte ouverte, sans clé
    assert s.pr == (2, 0) and s.kr == 0


# --------------------------------------------------------------------- R6
def test_victoire_immediate():
    jeu = jeu_de("BG.\n..R")
    s = jeu.transition(jeu.etat_initial(), "E")
    assert jeu.terminal(s)
    assert jeu.gagnant(s) == BLEU
    assert jeu.utilite(s, BLEU) == 1000 and jeu.utilite(s, ROUGE) == -1000
    assert jeu.actions_legales(s) == []
    with pytest.raises(ValueError):
        jeu.transition(s, "E")


def test_victoire_rouge():
    jeu = jeu_de("B..\n.GR")
    s = jeu.transition(jeu.etat_initial(), "E")
    s = jeu.transition(s, "O")
    assert jeu.gagnant(s) == ROUGE and jeu.utilite(s, BLEU) == -1000


# --------------------------------------------------------------------- R7
def test_deux_passes_consecutives_match_nul():
    jeu = jeu_de("BD#\nRD#\n##G")
    s = jeu.etat_initial()
    assert jeu.actions_legales(s) == [PASSER]
    s = jeu.transition(s, PASSER)
    assert s.p == 1 and not jeu.terminal(s)
    s = jeu.transition(s, PASSER)
    assert s.p == 2 and jeu.terminal(s)
    assert jeu.utilite(s, BLEU) == 0


def test_passe_interdite_si_un_coup_existe():
    jeu = Jeu(charger_carte("couloir_5x5"))
    with pytest.raises(ValueError):
        jeu.transition(jeu.etat_initial(), PASSER)


def test_un_deplacement_remet_les_passes_a_zero():
    jeu = jeu_de("BD..\n###.\nG.#R")
    s = jeu.transition(jeu.etat_initial(), PASSER)
    assert s.p == 1
    s = jeu.transition(s, "N")
    assert s.p == 0


# --------------------------------------------------------------------- R8
def test_limite_de_tours():
    jeu = jeu_de("B...\n####\nG..R", tmax=4)
    s = jeu.etat_initial()
    for a in ["E", "O", "O", "E"]:
        s = jeu.transition(s, a)
    assert s.t == 4 and jeu.terminal(s) and jeu.gagnant(s) is None
    assert jeu.raison_fin(s) == "nul (limite de tours)"


def test_tmax_par_defaut():
    assert Jeu(charger_carte("couloir_5x5")).tmax == 80


def test_etat_construit_a_la_main():
    jeu = jeu_de("B..\n.G.\n..R")
    s = Etat(pb=(1, 0), pr=(2, 2), joueur=BLEU, kb=0, kr=0,
             cles_sol=frozenset(), portes_ouvertes=frozenset())
    assert jeu.gagnant(jeu.transition(s, "S")) == BLEU
