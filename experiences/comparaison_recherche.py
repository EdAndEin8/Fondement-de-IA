"""Partie I — Comparaison expérimentale des algorithmes de recherche.

Pour chaque carte et chaque robot, mesure : longueur du chemin, nœuds
développés et générés, taille maximale de la frontière, temps d'exécution
(médiane de plusieurs répétitions) et pic mémoire (tracemalloc, mesuré dans
une exécution séparée car tracemalloc ralentit le programme).

Usage :
    uv run python experiences/comparaison_recherche.py [--repetitions 15]

Sorties : resultats/recherche.csv et resultats/recherche.md
"""

from __future__ import annotations

import argparse
import csv
import statistics
import time
import tracemalloc
from pathlib import Path

from course_balise.carte import charger_carte, lister_cartes
from course_balise.etat import BLEU, NOMS, ROUGE
from course_balise.recherche import HEURISTIQUES, ProblemeChemin, astar, bfs, dfs, ucs
from course_balise.regles import Jeu

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "resultats"

ALGOS = {
    "BFS": lambda pb: bfs(pb),
    "UCS": lambda pb: ucs(pb),
    "DFS": lambda pb: dfs(pb),
    "A* Manhattan": lambda pb: astar(pb, HEURISTIQUES["manhattan"](pb.carte), "A* Manhattan"),
    "A* relaxée": lambda pb: astar(pb, HEURISTIQUES["relaxee"](pb.carte), "A* relaxée"),
    "A* clés": lambda pb: astar(pb, HEURISTIQUES["cles"](pb.carte), "A* clés"),
}


def mesurer(algo, pb, repetitions: int) -> dict:
    temps = []
    for _ in range(repetitions):
        debut = time.perf_counter()
        r = algo(pb)
        temps.append(time.perf_counter() - debut)
    tracemalloc.start()
    algo(pb)
    _, pic = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return dict(
        longueur=r.longueur if r.trouve else "",
        developpes=r.noeuds_developpes,
        generes=r.noeuds_generes,
        frontiere_max=r.frontiere_max,
        memoire_noeuds=r.memoire_noeuds,
        temps_ms=round(statistics.median(temps) * 1000, 4),
        pic_memoire_kio=round(pic / 1024, 1),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=15)
    args = parser.parse_args()
    SORTIE.mkdir(exist_ok=True)

    lignes = []
    for nom in lister_cartes():
        carte = charger_carte(nom)
        etat = Jeu(carte).etat_initial()
        for joueur in (BLEU, ROUGE):
            pb = ProblemeChemin.depuis_etat(carte, etat, joueur)
            for nom_algo, algo in ALGOS.items():
                m = mesurer(algo, pb, args.repetitions)
                lignes.append(dict(carte=nom, robot=NOMS[joueur], algorithme=nom_algo, **m))

    champs = list(lignes[0])
    with open(SORTIE / "recherche.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)

    entetes = ["Carte", "Robot", "Algorithme", "Longueur", "Développés", "Générés",
               "Frontière max", "Mémoire (nœuds)", "Temps (ms)", "Pic mémoire (Kio)"]
    md = [f"# Comparaison des algorithmes de recherche\n",
          f"Temps : médiane de {args.repetitions} exécutions. "
          "Pic mémoire : tracemalloc (exécution séparée).\n",
          "| " + " | ".join(entetes) + " |",
          "|" + "---|" * len(entetes)]
    for l in lignes:
        md.append("| " + " | ".join(str(v) for v in l.values()) + " |")
    (SORTIE / "recherche.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
