"""Partie III — Min-Max contre Alpha-Bêta, et influence de l'ordre des coups.

Pour chaque carte, on prend 5 états (départ + 4 états de milieu de partie,
graine 2026) et, pour chaque profondeur, on mesure :
- les nœuds visités et le temps de Min-Max ;
- les nœuds visités et le temps d'Alpha-Bêta avec quatre ordres de coups
  (naturel N/S/O/E, aléatoire, meilleur d'abord selon E, pire d'abord) ;
- l'égalité des valeurs Min-Max / Alpha-Bêta (doit valoir 100 %).

Temps : médiane de 3 exécutions (calcul de l'agent seul, sans affichage).

Usage :
    uv run python experiences/minimax_alphabeta.py

Sorties : resultats/minimax_alphabeta.csv et resultats/minimax_alphabeta.md
"""

from __future__ import annotations

import statistics
import time

from commun import SORTIE, ecrire_csv, etats_varies, tableau_md

from course_balise.adversarial.evaluation import Evaluation
from course_balise.adversarial.minimax import alphabeta, minimax
from course_balise.carte import charger_carte
from course_balise.regles import Jeu

CARTES = ["exemple_7x7", "porte_raccourci", "salle_fermee", "labyrinthe_11x11", "arene_9x9"]
PROFONDEURS = [2, 4, 6, 8, 10]
ORDRES = ["naturel", "aleatoire", "evaluation", "pire"]
N_ETATS = 5
REPETITIONS = 3


def chrono(f, *args, **kw):
    temps, res = [], None
    for _ in range(REPETITIONS):
        t0 = time.perf_counter()
        res = f(*args, **kw)
        temps.append(time.perf_counter() - t0)
    return res, statistics.median(temps)


def main() -> None:
    lignes = []
    for nom in CARTES:
        jeu = Jeu(charger_carte(nom))
        ev = Evaluation(jeu.carte)
        for i, s in enumerate(etats_varies(nom, N_ETATS)):
            for d in PROFONDEURS:
                mm, t_mm = chrono(minimax, jeu, s, d, ev)
                ligne = dict(carte=nom, etat=i, profondeur=d,
                             mm_noeuds=mm.stats.noeuds, mm_ms=round(t_mm * 1000, 3))
                for o in ORDRES:
                    ab, t_ab = chrono(alphabeta, jeu, s, d, ev, ordre=o)
                    ligne[f"ab_{o}_noeuds"] = ab.stats.noeuds
                    ligne[f"ab_{o}_ms"] = round(t_ab * 1000, 3)
                    ligne[f"ab_{o}_egal"] = int(ab.valeur == mm.valeur)
                lignes.append(ligne)
        print(f"{nom} : fait")
    ecrire_csv(SORTIE / "minimax_alphabeta.csv", lignes)

    # Synthèse : moyennes par carte et profondeur.
    def moy(rows, cle):
        return statistics.mean(r[cle] for r in rows)

    synth, ordres = [], []
    egalites = sum(r[f"ab_{o}_egal"] for r in lignes for o in ORDRES)
    total = len(lignes) * len(ORDRES)
    for nom in CARTES:
        for d in PROFONDEURS:
            rows = [r for r in lignes if r["carte"] == nom and r["profondeur"] == d]
            mm_n, ab_n = moy(rows, "mm_noeuds"), moy(rows, "ab_evaluation_noeuds")
            synth.append([nom, d, round(mm_n), f"{moy(rows, 'mm_ms'):.2f}",
                          round(moy(rows, "ab_naturel_noeuds")), round(ab_n),
                          f"{moy(rows, 'ab_evaluation_ms'):.2f}",
                          f"{100 * (1 - ab_n / mm_n):.0f} %"])
            if d == 8:
                ordres.append([nom] + [round(moy(rows, f"ab_{o}_noeuds")) for o in ORDRES]
                              + [round(mm_n)])

    md = [
        "# Min-Max et Alpha-Bêta\n",
        f"{N_ETATS} états par carte (départ + milieux de partie, graine 2026). "
        f"Temps : médiane de {REPETITIONS} exécutions.\n",
        f"Valeurs identiques Min-Max / Alpha-Bêta : **{egalites}/{total}** "
        "(toutes cartes, profondeurs et ordres).\n",
        "## Nœuds visités et temps selon la profondeur (moyennes)\n",
        tableau_md(["Carte", "d", "MM nœuds", "MM ms", "AB naturel", "AB tri E",
                    "AB tri E ms", "Gain AB tri E"], synth),
        "\n## Influence de l'ordre des coups (Alpha-Bêta, d = 8, nœuds moyens)\n",
        tableau_md(["Carte", "Naturel", "Aléatoire", "Meilleur d'abord (E)",
                    "Pire d'abord", "Min-Max"], ordres),
    ]
    (SORTIE / "minimax_alphabeta.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
