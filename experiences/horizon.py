"""Partie III — Effet d'horizon et évaluation améliorée.

1. Situation clé sur salle_fermee : Bleu a la clé et se trouve devant la
   porte, Rouge est loin. Ouvrir la porte (N) gagne en 3 coups, mais
   consomme la clé et ouvre aussi le passage à Rouge, qui n'a plus besoin
   de clé : avec l'évaluation E, la valeur chute. On affiche, pour chaque
   profondeur, le coup choisi et les valeurs de la racine, avec E et E+.

2. Conséquence en partie : Alpha-Bêta à différentes profondeurs, avec E et
   avec E+, contre un adversaire aléatoire (10 graines) et contre A*, sur
   salle_fermee et porte_raccourci, Bleu commençant.

Usage :
    uv run python experiences/horizon.py

Sortie : resultats/horizon.md
"""

from __future__ import annotations

from commun import SORTIE, tableau_md

from course_balise.adversarial.evaluation import POIDS_AMELIORES, Evaluation
from course_balise.adversarial.minimax import alphabeta
from course_balise.affichage import afficher
from course_balise.agents import (AgentAleatoire, AgentAlphaBeta, AgentAlphaBetaAmeliore,
                                  AgentAStar)
from course_balise.carte import charger_carte
from course_balise.jeu import jouer
from course_balise.regles import Jeu

GRAINES = range(10)


def situation_porte() -> list[str]:
    carte = charger_carte("salle_fermee")
    jeu = Jeu(carte)
    s = jeu.etat_initial().avec(pb=(4, 6), pr=(0, 0), kb=1, cles_sol=frozenset(), t=36)
    sortie = ["## 1. Bleu devant la porte, avec la clé (salle_fermee, tour 36)\n",
              "```", afficher(s, carte, couleurs=False), "```\n"]
    for nom, ev in (("E", Evaluation(carte)), ("E+", Evaluation(carte, POIDS_AMELIORES))):
        t = ev.termes(s)
        apres = ev.termes(jeu.transition(s, "N"))
        sortie.append(f"**{nom}** : E(s) = {ev(s):.0f} (dB = {t['dB']}, dR = {t['dR']}) ; "
                      f"après N : {ev(jeu.transition(s, 'N')):.0f} "
                      f"(dB = {apres['dB']}, dR = {apres['dR']})\n")
        lignes = []
        for d in range(1, 8):
            dec = alphabeta(jeu, s, d, ev)
            vals = ", ".join(f"{a} : {v:.0f}" for a, v in sorted(dec.valeurs_racine.items()))
            lignes.append([d, dec.action, f"{dec.valeur:.0f}", vals])
        sortie.append(tableau_md(["d", "Coup", "Valeur", "Valeurs à la racine "
                                  "(bornes pour les coups élagués)"], lignes))
        sortie.append("")
    return sortie


def bilan(agent_bleu, agent_rouge, carte, graines) -> str:
    v = n = p = 0
    tours = []
    for g in graines:
        r = jouer(agent_bleu, agent_rouge, carte, graine=g)
        tours.append(r.tours)
        if r.gagnant == "B":
            v += 1
        elif r.gagnant is None:
            n += 1
        else:
            p += 1
    return f"{v}/{n}/{p} ({sum(tours) / len(tours):.0f} t.)"


def parties() -> list[str]:
    sortie = ["## 2. En partie : victoires / nuls / défaites de Bleu (Alpha-Bêta)\n",
              f"Bleu commence. Contre l'aléatoire : {len(GRAINES)} graines (0 à "
              f"{GRAINES[-1]}) ; contre A* : partie déterministe. Entre parenthèses, "
              "le nombre moyen de tours.\n"]
    lignes = []
    for nom in ["salle_fermee", "porte_raccourci"]:
        carte = charger_carte(nom)
        for d in (2, 3, 4, 5, 6):
            for label, fabrique in (("E", AgentAlphaBeta), ("E+", AgentAlphaBetaAmeliore)):
                lignes.append([
                    nom, d, label,
                    bilan(fabrique(d), AgentAleatoire(), carte, GRAINES),
                    bilan(fabrique(d), AgentAStar(), carte, [0]),
                ])
    sortie.append(tableau_md(["Carte", "d", "Évaluation", "contre aléatoire",
                              "contre A*"], lignes))
    return sortie


def main() -> None:
    md = ["# Effet d'horizon\n"] + situation_porte() + parties()
    (SORTIE / "horizon.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
