"""Partie I — Pourquoi le plus court chemin calculé sans adversaire devient
sous-optimal pendant une vraie partie.

Chaque robot calcule une seule fois, au début, son plus court chemin
(A*, l'adversaire étant un obstacle fixe à sa position initiale), puis
l'exécute aveuglément. On observe ce qui se passe quand l'autre robot
bouge, et on compare avec un agent qui replanifie à chaque tour.

Usage :
    uv run python experiences/plan_fige.py [carte]
"""

from __future__ import annotations

import sys

from course_balise.affichage import afficher
from course_balise.agents import AgentAStar
from course_balise.carte import charger_carte
from course_balise.etat import BLEU, NOMS, ROUGE
from course_balise.jeu import jouer
from course_balise.recherche import HEURISTIQUES, ProblemeChemin, astar
from course_balise.regles import PASSER, Jeu


def partie_plans_figes(nom_carte: str) -> None:
    carte = charger_carte(nom_carte)
    jeu = Jeu(carte)
    etat = jeu.etat_initial()
    h = HEURISTIQUES["cles"](carte)
    plans = {}
    for j in (BLEU, ROUGE):
        r = astar(ProblemeChemin.depuis_etat(carte, etat, j), h)
        plans[j] = list(r.actions)
        print(f"Plan initial de {NOMS[j]} ({r.longueur} coups) : {' '.join(r.actions)}")
    print()
    print(afficher(etat, carte, couleurs=False))

    while not jeu.terminal(etat):
        j = etat.joueur
        legales = jeu.actions_legales(etat)
        prevue = plans[j].pop(0) if plans[j] else None
        if prevue in legales:
            action = prevue
        else:
            action = PASSER if legales == [PASSER] else legales[0]
            print(f"\nt={etat.t} : l'action prévue par {NOMS[j]} ({prevue}) est illégale "
                  f"(légales : {legales}). Le plan figé est caduc.")
            print(afficher(etat, carte, couleurs=False))
            print(f"=> {NOMS[j]} doit improviser (ici : {action}) : sans "
                  "replanification, son plan ne mène plus nulle part.")
            return
        etat = jeu.transition(etat, action)
    print(f"\nFin : {jeu.raison_fin(etat)} en {etat.t} tours.")


def main() -> None:
    nom = sys.argv[1] if len(sys.argv) > 1 else "salle_fermee"
    print(f"=== Plans figés sur {nom} ===")
    partie_plans_figes(nom)
    r = jouer(AgentAStar(), AgentAStar(), charger_carte(nom))
    print(f"\n=== Agents A* qui replanifient à chaque tour ===\n"
          f"{r.raison} en {r.tours} tours")


if __name__ == "__main__":
    main()
