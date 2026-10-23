"""Partie III — Approfondissement itératif sous budget de temps.

Pour plusieurs budgets par coup, on mesure sur 5 états par carte :
- la profondeur entièrement explorée (moyenne, min, max) ;
- le temps réellement consommé (le dépassement doit rester faible) ;
- la part des décisions où une itération a été abandonnée faute de temps ;
- la part des décisions identiques à Alpha-Bêta à profondeur fixe 6.

Le temps mesuré est celui de l'agent seul (pas d'affichage).

Usage :
    uv run python experiences/iteratif_budget.py

Sorties : resultats/iteratif.csv et resultats/iteratif.md
"""

from __future__ import annotations

import statistics

from commun import SORTIE, ecrire_csv, etats_varies, tableau_md

from course_balise.adversarial.evaluation import Evaluation
from course_balise.adversarial.iteratif import approfondissement_iteratif
from course_balise.adversarial.minimax import alphabeta
from course_balise.carte import charger_carte
from course_balise.regles import Jeu

CARTES = ["exemple_7x7", "salle_fermee", "labyrinthe_11x11", "arene_9x9",
          "grand_labyrinthe_25x25"]
BUDGETS_MS = [1, 5, 20, 100, 500]
N_ETATS = 5


def main() -> None:
    lignes = []
    for nom in CARTES:
        jeu = Jeu(charger_carte(nom))
        ev = Evaluation(jeu.carte)
        etats = etats_varies(nom, N_ETATS)
        reference = [alphabeta(jeu, s, 6, ev, ordre="evaluation") for s in etats]
        for b in BUDGETS_MS:
            for i, s in enumerate(etats):
                r = approfondissement_iteratif(jeu, s, ev, budget=b / 1000)
                assert r.action in jeu.actions_legales(s)
                lignes.append(dict(
                    carte=nom, budget_ms=b, etat=i, profondeur=r.profondeur,
                    temps_ms=round(r.temps * 1000, 3), noeuds=r.noeuds,
                    interrompue=int(r.interrompue),
                    valeur_ref_d6=reference[i].valeur,
                    valeur=r.valeur,
                ))
        print(f"{nom} : fait")
    ecrire_csv(SORTIE / "iteratif.csv", lignes)

    synth = []
    for nom in CARTES:
        for b in BUDGETS_MS:
            rows = [r for r in lignes if r["carte"] == nom and r["budget_ms"] == b]
            prof = [r["profondeur"] for r in rows]
            synth.append([
                nom, b, f"{statistics.mean(prof):.1f}", f"{min(prof)}–{max(prof)}",
                f"{statistics.mean(r['temps_ms'] for r in rows):.1f}",
                f"{max(r['temps_ms'] for r in rows):.1f}",
                f"{100 * statistics.mean(r['interrompue'] for r in rows):.0f} %",
                round(statistics.mean(r["noeuds"] for r in rows)),
            ])
    md = [
        "# Approfondissement itératif sous budget\n",
        f"{N_ETATS} états par carte (graine 2026), Alpha-Bêta avec tri par E, "
        "meilleur coup précédent en tête.\n",
        "Une action légale est renvoyée dans 100 % des cas, même avec 1 ms.\n",
        tableau_md(["Carte", "Budget (ms)", "Profondeur moy.", "Min–max", "Temps moy. (ms)",
                    "Temps max (ms)", "Itération abandonnée", "Nœuds"], synth),
        "\nUne profondeur moyenne qui plafonne avant le budget maximal signifie "
        "qu'une issue certaine (victoire ou défaite forcée) a été trouvée, ou que "
        "la profondeur atteint le nombre de tours restants.",
    ]
    (SORTIE / "iteratif.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
