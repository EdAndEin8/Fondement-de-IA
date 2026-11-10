"""Partie V — Campagne d'évaluation entre agents.

Agents : aléatoire, planificateur A* (replanifie à chaque tour), Min-Max,
Alpha-Bêta et Alpha-Bêta avec l'évaluation améliorée E+, tous à la même
profondeur ``D``.

1. Tournoi : chaque paire d'agents sur chaque carte, dans les 4
   configurations obtenues en inversant les couleurs (donc les positions de
   départ) et le joueur qui commence. Les parties contre l'agent aléatoire
   sont rejouées avec les graines 0 à 9 ; les autres agents sont
   déterministes, une partie par configuration suffit.
2. Min-Max contre Alpha-Bêta à profondeur identique (d = 2, 4, 6) : mêmes
   configurations, comparaison des résultats, des nœuds et des temps.
3. Parties où un agent adversarial ne gagne pas contre un agent plus
   faible, pour l'analyse des échecs.

Graines : dans ``jouer``, l'agent Bleu reçoit 2g et Rouge 2g + 1.
Temps : temps de calcul des agents, sans affichage.

Usage :
    uv run python experiences/campagne.py

Sorties : resultats/campagne.csv, resultats/campagne_minmax_alphabeta.csv
et resultats/campagne.md
"""

from __future__ import annotations

from itertools import combinations

from commun import SORTIE, ecrire_csv, tableau_md

from course_balise.agents import (AgentAleatoire, AgentAlphaBeta, AgentAlphaBetaAmeliore,
                                  AgentAStar, AgentMinMax)
from course_balise.carte import charger_carte
from course_balise.etat import BLEU, ROUGE
from course_balise.jeu import jouer

D = 4
# grand_labyrinthe_25x25 est exclue : 80 tours ne suffisent à aucun robot.
CARTES = ["couloir_5x5", "exemple_7x7", "porte_raccourci", "salle_fermee",
          "arene_9x9", "labyrinthe_11x11"]
GRAINES_ALEATOIRE = range(10)
PROFONDEURS_COMPARAISON = [2, 4, 6]

FABRIQUES = {
    "aleatoire": AgentAleatoire,
    "astar": AgentAStar,
    f"minmax-d{D}": lambda: AgentMinMax(D),
    f"alphabeta-d{D}": lambda: AgentAlphaBeta(D),
    f"alphabeta+-d{D}": lambda: AgentAlphaBetaAmeliore(D),
}
NOMS = list(FABRIQUES)
FORCE = {nom: i for i, nom in enumerate(NOMS)}  # ordre indicatif, du plus faible au plus fort


def configurations():
    for couleur_x in (BLEU, ROUGE):
        for premier in (BLEU, ROUGE):
            yield couleur_x, premier


def partie(nom_x, fab_x, nom_y, fab_y, carte, couleur_x, premier, graine) -> list[dict]:
    """Joue une partie et renvoie une ligne par agent (point de vue de chacun)."""
    x, y = fab_x(), fab_y()
    bleu, rouge = (x, y) if couleur_x == BLEU else (y, x)
    r = jouer(bleu, rouge, carte, graine=graine, premier=premier)
    lignes = []
    for nom, adv, couleur in ((nom_x, nom_y, couleur_x),
                              (nom_y, nom_x, ROUGE if couleur_x == BLEU else BLEU)):
        issue = ("nul" if r.gagnant is None else
                 "victoire" if r.gagnant == couleur else "defaite")
        coups = [c for c in r.coups if c.joueur == couleur]
        lignes.append(dict(
            agent=nom, adversaire=adv, carte=carte.nom, couleur=couleur, premier=premier,
            commence=premier == couleur, graine=graine, issue=issue, raison=r.raison,
            tours=r.tours, duree_ms=round(r.duree * 1000, 3), decisions=len(coups),
            temps_ms=round(sum(c.temps for c in coups) * 1000, 3),
            noeuds=sum(c.noeuds for c in coups)))
    return lignes


def tournoi() -> list[dict]:
    lignes = []
    for nom_x, nom_y in combinations(NOMS, 2):
        graines = GRAINES_ALEATOIRE if "aleatoire" in (nom_x, nom_y) else [0]
        for nom_carte in CARTES:
            carte = charger_carte(nom_carte)
            for couleur_x, premier in configurations():
                for g in graines:
                    lignes += partie(nom_x, FABRIQUES[nom_x], nom_y, FABRIQUES[nom_y],
                                     carte, couleur_x, premier, g)
    return lignes


def comparaison_minmax_alphabeta() -> list[dict]:
    lignes = []
    for d in PROFONDEURS_COMPARAISON:
        for nom_carte in CARTES:
            carte = charger_carte(nom_carte)
            for couleur_x, premier in configurations():
                lignes += partie(f"minmax-d{d}", lambda: AgentMinMax(d),
                                 f"alphabeta-d{d}", lambda: AgentAlphaBeta(d),
                                 carte, couleur_x, premier, 0)
    return lignes


# ------------------------------------------------------------------ synthèse
def taux(ls, issue) -> str:
    return f"{sum(l['issue'] == issue for l in ls) / len(ls):.0%}"


def moyenne(valeurs) -> float:
    valeurs = list(valeurs)
    return sum(valeurs) / len(valeurs) if valeurs else 0.0


def par_decision(ls, cle) -> float:
    return sum(l[cle] for l in ls) / max(1, sum(l["decisions"] for l in ls))


def bilan_agents(lignes) -> str:
    tab = []
    for nom in NOMS:
        ls = [l for l in lignes if l["agent"] == nom]
        tab.append([nom, len(ls), taux(ls, "victoire"), taux(ls, "nul"), taux(ls, "defaite"),
                    f"{moyenne(l['tours'] for l in ls):.1f}",
                    f"{moyenne(l['duree_ms'] for l in ls):.1f}",
                    f"{par_decision(ls, 'temps_ms'):.3f}",
                    f"{par_decision(ls, 'noeuds'):.0f}"])
    return tableau_md(["Agent", "Parties", "Victoires", "Nuls", "Défaites", "Tours moyens",
                       "Durée moyenne (ms)", "Temps par décision (ms)",
                       "Nœuds par décision"], tab)


def matrice(lignes) -> str:
    tab = []
    for x in NOMS:
        ligne = [x]
        for y in NOMS:
            ls = [l for l in lignes if l["agent"] == x and l["adversaire"] == y]
            if not ls:
                ligne.append("–")
            else:
                v = sum(l["issue"] == "victoire" for l in ls)
                n = sum(l["issue"] == "nul" for l in ls)
                ligne.append(f"{v}/{n}/{len(ls) - v - n}")
        tab.append(ligne)
    return tableau_md(["Agent \\ adversaire"] + NOMS, tab)


def par_carte(lignes) -> str:
    tab = []
    for nom_carte in CARTES:
        ligne = [nom_carte]
        for nom in NOMS:
            ls = [l for l in lignes if l["agent"] == nom and l["carte"] == nom_carte]
            ligne.append(f"{taux(ls, 'victoire')} / {taux(ls, 'nul')}")
        tab.append(ligne)
    return tableau_md(["Carte"] + NOMS, tab)


def premier_joueur(lignes) -> str:
    deterministes = [l for l in lignes
                     if "aleatoire" not in (l["agent"], l["adversaire"])]
    tab = []
    for nom in NOMS[1:]:
        ligne = [nom]
        for commence in (True, False):
            ls = [l for l in deterministes if l["agent"] == nom and l["commence"] == commence]
            ligne.append(f"{taux(ls, 'victoire')} / {taux(ls, 'nul')} / {taux(ls, 'defaite')}")
        tab.append(ligne)
    tous = [l for l in deterministes if l["commence"]]
    tab.append(["tous (point de vue du premier)",
                f"{taux(tous, 'victoire')} / {taux(tous, 'nul')} / {taux(tous, 'defaite')}",
                "–"])
    return tableau_md(["Agent", "Commence (V / N / D)", "Second (V / N / D)"], tab)


def tableau_comparaison(lignes) -> str:
    tab = []
    for d in PROFONDEURS_COMPARAISON:
        for nom_carte in CARTES:
            mm = [l for l in lignes if l["agent"] == f"minmax-d{d}" and l["carte"] == nom_carte]
            ab = [l for l in lignes if l["agent"] == f"alphabeta-d{d}" and l["carte"] == nom_carte]
            n_mm, n_ab = par_decision(mm, "noeuds"), par_decision(ab, "noeuds")
            t_mm, t_ab = par_decision(mm, "temps_ms"), par_decision(ab, "temps_ms")
            v = sum(l["issue"] == "victoire" for l in mm)
            nul = sum(l["issue"] == "nul" for l in mm)
            tab.append([d, nom_carte, f"{v}/{nul}/{len(mm) - v - nul}",
                        f"{n_mm:.0f}", f"{n_ab:.0f}", f"{1 - n_ab / n_mm:.0%}",
                        f"{t_mm:.2f}", f"{t_ab:.2f}"])
    return tableau_md(["d", "Carte", "Min-Max V/N/D", "Nœuds Min-Max", "Nœuds Alpha-Bêta",
                       "Économie", "ms Min-Max", "ms Alpha-Bêta"], tab)


def echecs_contre_aleatoire(lignes) -> str:
    """Parties non gagnées par un agent adversarial contre l'agent aléatoire."""
    tab = []
    for nom in NOMS[2:]:
        for nom_carte in CARTES:
            for couleur in (BLEU, ROUGE):
                ls = [l for l in lignes if l["agent"] == nom and l["adversaire"] == "aleatoire"
                      and l["carte"] == nom_carte and l["couleur"] == couleur]
                n = sum(l["issue"] == "nul" for l in ls)
                d = sum(l["issue"] == "defaite" for l in ls)
                if n or d:
                    tab.append([nom, nom_carte, couleur, len(ls), n, d])
    return tableau_md(["Agent", "Carte", "Couleur", "Parties", "Nuls", "Défaites"], tab)


def echecs_en_commencant(lignes) -> str:
    """Parties non gagnées en commençant contre un agent déterministe plus faible."""
    tab = []
    for l in lignes:
        if (l["agent"] in NOMS[2:] and l["commence"] and l["issue"] != "victoire"
                and l["adversaire"] != "aleatoire"
                and FORCE[l["adversaire"]] < FORCE[l["agent"]]):
            tab.append([l["agent"], l["adversaire"], l["carte"], l["couleur"],
                        l["issue"], l["raison"], l["tours"]])
    return tableau_md(["Agent", "Adversaire", "Carte", "Couleur", "Issue", "Raison",
                       "Tours"], tab)


def main() -> None:
    lignes = tournoi()
    comparaison = comparaison_minmax_alphabeta()
    ecrire_csv(SORTIE / "campagne.csv", lignes)
    ecrire_csv(SORTIE / "campagne_minmax_alphabeta.csv", comparaison)
    n_parties = len(lignes) // 2
    md = [
        "# Partie V — Campagne d'évaluation\n",
        "Script : `experiences/campagne.py`.\n",
        f"Agents : {', '.join(NOMS)} (profondeur {D}, évaluation E pour Min-Max et "
        "Alpha-Bêta, E+ pour Alpha-Bêta amélioré, coups triés par évaluation pour "
        "Alpha-Bêta). A* utilise l'heuristique « clés » et replanifie à chaque tour.\n",
        f"Cartes : {', '.join(CARTES)}. Chaque paire joue dans 4 configurations : couleurs "
        "(et donc positions de départ) inversées, et joueur qui commence inversé. "
        f"Graines {GRAINES_ALEATOIRE.start} à {GRAINES_ALEATOIRE.stop - 1} pour les parties "
        "contre l'agent aléatoire, graine 0 sinon (agents déterministes). "
        f"Total : {n_parties} parties.\n",
        "## 1. Bilan par agent\n",
        "Durée : temps total d'une partie (décisions des deux agents et transitions, sans "
        "affichage). Temps et nœuds : moyenne par décision de l'agent.\n",
        bilan_agents(lignes),
        "\n## 2. Résultats par paire\n",
        "Victoires / nuls / défaites de l'agent en ligne contre l'agent en colonne.\n",
        matrice(lignes),
        "\n## 3. Taux de victoire / nul par carte\n",
        par_carte(lignes),
        "\n## 4. Effet du joueur qui commence\n",
        "Parties entre agents déterministes seulement.\n",
        premier_joueur(lignes),
        "\n## 5. Min-Max contre Alpha-Bêta à profondeur identique\n",
        "Min-Max (ordre naturel) contre Alpha-Bêta (tri par E), même évaluation E, "
        "4 configurations par carte. V/N/D du point de vue de Min-Max ; nœuds et temps "
        "par décision.\n",
        tableau_comparaison(comparaison),
        "\n## 6. Échecs et décisions surprenantes\n",
        "### 6.1 Parties non gagnées contre l'agent aléatoire\n",
        "Toutes configurations confondues (premier joueur et graines).\n",
        echecs_contre_aleatoire(lignes),
        "\n### 6.2 Parties non gagnées en commençant, contre un agent déterministe "
        "plus faible\n",
        "Ordre indicatif des agents : " + " < ".join(NOMS) + ". Les défaites quand "
        "l'agent joue en second sont attendues (section 4) et ne sont pas listées.\n",
        echecs_en_commencant(lignes),
    ]
    (SORTIE / "campagne.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
