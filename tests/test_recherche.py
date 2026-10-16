"""Tests de la Partie I : BFS, DFS, UCS, A* et heuristiques."""

import pytest

from course_balise.carte import Carte, charger_carte, lister_cartes
from course_balise.etat import BLEU, ROUGE
from course_balise.recherche import (HEURISTIQUES, ProblemeChemin, astar, bfs,
                                     dfs, ucs)
from course_balise.regles import Jeu

CARTES = lister_cartes()


def probleme(nom_ou_carte, joueur=BLEU):
    carte = nom_ou_carte if isinstance(nom_ou_carte, Carte) else charger_carte(nom_ou_carte)
    etat = Jeu(carte).etat_initial()
    return ProblemeChemin.depuis_etat(carte, etat, joueur)


def chemin_valide(pb: ProblemeChemin, actions) -> bool:
    """Rejoue les actions avec les règles et vérifie l'arrivée sur la balise."""
    s = pb.depart
    for a in actions:
        succ = {act: s2 for act, s2, _ in pb.successeurs(s)}
        if a not in succ:
            return False
        s = succ[a]
    return pb.est_but(s)


@pytest.mark.parametrize("nom", CARTES)
@pytest.mark.parametrize("joueur", [BLEU, ROUGE])
def test_tous_les_algorithmes_trouvent_un_chemin_valide(nom, joueur):
    pb = probleme(nom, joueur)
    resultats = [bfs(pb), ucs(pb), dfs(pb)] + [
        astar(pb, f(pb.carte), n) for n, f in HEURISTIQUES.items()
    ]
    for r in resultats:
        assert r.trouve, r.algorithme
        assert chemin_valide(pb, r.actions), r.algorithme
    optimal = resultats[0].longueur
    for r in resultats:
        if r.algorithme != "DFS":
            assert r.longueur == optimal, r.algorithme
        else:
            assert r.longueur >= optimal


def test_longueurs_connues():
    assert bfs(probleme("couloir_5x5")).longueur == 6
    assert bfs(probleme("couloir_5x5", ROUGE)).longueur == 4
    # Raccourci par la clé et la porte : 7 coups au lieu de 13.
    assert bfs(probleme("porte_raccourci")).longueur == 7
    # Salle fermée : il faut la clé (4 coups), puis faire le tour jusqu'à la porte.
    r = bfs(probleme("salle_fermee"))
    assert r.longueur == 4 + 4 + 6 + 4 + 1 + 2


def test_la_recherche_tient_compte_des_cles():
    r = bfs(probleme("porte_raccourci"))
    assert (2, 0) in r.positions() and (4, 1) in r.positions()
    assert r.etats[2].cle == 1 and r.etats[-1].cle == 0


def test_pas_de_chemin():
    carte = Carte.depuis_texte("B#G\n##.\nR..")
    r_bfs = bfs(probleme(carte))
    assert not r_bfs.trouve and r_bfs.longueur is None
    assert not astar(probleme(carte), HEURISTIQUES["cles"](carte)).trouve
    assert not dfs(probleme(carte)).trouve


def test_adversaire_obstacle_fixe():
    # Rouge bloque l'unique couloir de Bleu.
    carte = Carte.depuis_texte("B.R.G")
    assert not bfs(probleme(carte)).trouve


def test_depart_sur_un_but_trivial():
    carte = Carte.depuis_texte("BG\n.R")
    assert bfs(probleme(carte)).longueur == 1


@pytest.mark.parametrize("nom", CARTES)
@pytest.mark.parametrize("h_nom", ["manhattan", "relaxee", "cles"])
def test_heuristiques_admissibles(nom, h_nom):
    """h(s) <= h*(s) pour chaque état atteignable (h* calculé par BFS)."""
    pb0 = probleme(nom)
    h = HEURISTIQUES[h_nom](pb0.carte)
    # Énumère les états atteignables depuis le départ.
    vus, file = {pb0.depart}, [pb0.depart]
    while file:
        s = file.pop()
        for _, s2, _ in pb0.successeurs(s):
            if s2 not in vus:
                vus.add(s2)
                file.append(s2)
    for s in vus:
        pb = ProblemeChemin(pb0.carte, s, pb0.obstacle)
        vrai = bfs(pb).longueur
        if vrai is None:
            continue
        assert h(s) <= vrai, (s, h(s), vrai)


def test_heuristique_informee_developpe_moins():
    pb = probleme("labyrinthe_11x11")
    n_ucs = ucs(pb).noeuds_developpes
    n_man = astar(pb, HEURISTIQUES["manhattan"](pb.carte)).noeuds_developpes
    n_rel = astar(pb, HEURISTIQUES["relaxee"](pb.carte)).noeuds_developpes
    assert n_rel <= n_man <= n_ucs
