"""Partie IV — Carte complète contre découverte progressive.

1. Course en solitaire (l'adversaire reste sur sa case de départ) : nombre
   de pas jusqu'à G pour A* avec la carte complète et pour l'explorateur
   (rayon de vue 1 ou 2, balise inconnue ou connue d'emblée), Bleu puis
   Rouge, sur toutes les cartes. On relève aussi la part de la carte
   découverte et le coût de calcul.

2. Parties : agents à information partielle contre un adversaire
   aléatoire, contre A* (carte complète) et contre l'explorateur, en
   inversant les couleurs et le joueur qui commence, graines 0 à 4.

Usage :
    uv run python experiences/information_partielle.py

Sorties : resultats/information_partielle.csv (course), resultats/information_partielle_parties.csv
(parties) et resultats/information_partielle.md
"""

from __future__ import annotations

from commun import SORTIE, ecrire_csv, tableau_md

from course_balise.agents import (AgentAleatoire, AgentAlphaBetaOptimiste, AgentAStar,
                                  AgentExplorateur)
from course_balise.carte import charger_carte
from course_balise.etat import BLEU, ROUGE
from course_balise.jeu import jouer
from course_balise.partiel.solo import course_solo

CARTES_SOLO = ["couloir_5x5", "exemple_7x7", "porte_raccourci", "salle_fermee",
               "arene_9x9", "labyrinthe_11x11", "grand_labyrinthe_25x25"]
CARTES_PARTIES = CARTES_SOLO[:-1]  # 80 tours ne suffisent pas sur le 25x25
GRAINES = range(5)


def agents_solo():
    return [AgentAStar(), AgentExplorateur(1), AgentExplorateur(2),
            AgentExplorateur(1, balise_connue=True), AgentExplorateur(2, balise_connue=True)]


def course() -> tuple[list[dict], list[str]]:
    lignes, md = [], []
    for nom in CARTES_SOLO:
        carte = charger_carte(nom)
        total = carte.largeur * carte.hauteur
        for joueur in (BLEU, ROUGE):
            reference = None
            for agent in agents_solo():
                r = course_solo(agent, carte, joueur)
                if reference is None:
                    reference = r.pas
                connues = (agent.memoire.nb_connues() / total
                           if isinstance(agent, AgentExplorateur) else 1.0)
                lignes.append(dict(
                    carte=nom, robot=joueur, agent=str(agent), arrive=r.arrive,
                    pas=r.pas, surcout=round(r.pas / reference, 2),
                    connues=round(connues, 2), noeuds=r.noeuds,
                    temps_ms=round(r.temps * 1000, 2)))
    md.append("## 1. Course en solitaire : pas jusqu'à G\n")
    md.append("Adversaire immobile sur sa case de départ. Entre parenthèses : rapport au "
              "nombre de pas avec la carte complète.\n")
    noms = [str(a) for a in agents_solo()]
    tab = []
    for nom in CARTES_SOLO:
        for joueur in (BLEU, ROUGE):
            ls = [l for l in lignes if l["carte"] == nom and l["robot"] == joueur]
            tab.append([nom, joueur] + [
                f"{l['pas']}" if l["agent"] == "astar-cles" else f"{l['pas']} ({l['surcout']})"
                for l in ls])
    md.append(tableau_md(["Carte", "Robot"] + noms, tab))
    md.append("\nPart de la carte découverte à l'arrivée (moyenne Bleu / Rouge) et nœuds "
              "développés en tout :\n")
    tab = []
    for nom in CARTES_SOLO:
        ligne = [nom]
        for a in noms[1:]:
            ls = [l for l in lignes if l["carte"] == nom and l["agent"] == a]
            c = sum(l["connues"] for l in ls) / len(ls)
            n = sum(l["noeuds"] for l in ls) / len(ls)
            ligne.append(f"{c:.0%} / {n:.0f}")
        ligne.append(f"{sum(l['noeuds'] for l in lignes if l['carte'] == nom and l['agent'] == 'astar-cles') / 2:.0f}")
        tab.append(ligne)
    md.append(tableau_md(["Carte"] + [f"{a} (connu / nœuds)" for a in noms[1:]]
                         + ["astar-cles (nœuds)"], tab))
    return lignes, md


def parties() -> tuple[list[dict], list[str]]:
    partiels = [lambda: AgentExplorateur(1), lambda: AgentExplorateur(1, True),
                lambda: AgentAlphaBetaOptimiste(4, 1), lambda: AgentAlphaBetaOptimiste(4, 1, True),
                lambda: AgentAlphaBetaOptimiste(4, 2, True)]
    adversaires = [AgentAleatoire, AgentAStar, lambda: AgentExplorateur(1)]
    lignes = []
    for fabrique in partiels:
        for fab_adv in adversaires:
            for nom in CARTES_PARTIES:
                carte = charger_carte(nom)
                for couleur in (BLEU, ROUGE):
                    for premier in (BLEU, ROUGE):
                        graines = GRAINES if fab_adv is AgentAleatoire else [0]
                        for g in graines:
                            agent, adv = fabrique(), fab_adv()
                            bleu, rouge = (agent, adv) if couleur == BLEU else (adv, agent)
                            r = jouer(bleu, rouge, carte, graine=g, premier=premier)
                            issue = ("nul" if r.gagnant is None else
                                     "victoire" if r.gagnant == couleur else "defaite")
                            lignes.append(dict(
                                agent=str(agent), adversaire=str(adv), carte=nom,
                                couleur=couleur, premier=premier, graine=g, issue=issue,
                                tours=r.tours,
                                alphabeta=agent.modes.get("alphabeta", 0),
                                decisions=sum(agent.modes.values())))
    md = ["\n## 2. Parties contre des adversaires\n",
          f"Cartes : {', '.join(CARTES_PARTIES)}. Couleurs et premier joueur inversés ; "
          "graines 0 à 4 contre l'aléatoire, une partie sinon (agents déterministes). "
          "Issue du point de vue de l'agent à information partielle.\n"]
    tab = []
    for agent in dict.fromkeys(l["agent"] for l in lignes):
        for adv in dict.fromkeys(l["adversaire"] for l in lignes):
            ls = [l for l in lignes if l["agent"] == agent and l["adversaire"] == adv]
            n = len(ls)
            v = sum(l["issue"] == "victoire" for l in ls)
            d = sum(l["issue"] == "defaite" for l in ls)
            ab = sum(l["alphabeta"] for l in ls) / max(1, sum(l["decisions"] for l in ls))
            tab.append([agent, adv, n, f"{v / n:.0%}", f"{(n - v - d) / n:.0%}",
                        f"{d / n:.0%}", f"{sum(l['tours'] for l in ls) / n:.1f}",
                        f"{ab:.1%}"])
    md.append(tableau_md(["Agent", "Adversaire", "Parties", "Victoires", "Nuls", "Défaites",
                          "Tours moyens", "Décisions Alpha-Bêta"], tab))
    return lignes, md


def main() -> None:
    l1, md1 = course()
    l2, md2 = parties()
    ecrire_csv(SORTIE / "information_partielle.csv", l1)
    ecrire_csv(SORTIE / "information_partielle_parties.csv", l2)
    texte = ["# Partie IV — Information partielle\n",
             "Script : `experiences/information_partielle.py`.\n"] + md1 + md2
    (SORTIE / "information_partielle.md").write_text("\n".join(texte) + "\n", encoding="utf-8")
    print("\n".join(texte))


if __name__ == "__main__":
    main()
