"""Outils partagés par les scripts d'expériences."""

from __future__ import annotations

import csv
import random
from pathlib import Path

from course_balise.agents import AgentAleatoire
from course_balise.carte import charger_carte
from course_balise.etat import BLEU, ROUGE, Etat
from course_balise.regles import Jeu

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "resultats"


def etats_varies(nom_carte: str, n: int, graine: int = 2026) -> list[Etat]:
    """État initial puis n - 1 états de milieu de partie, obtenus en jouant
    entre 2 et 20 coups aléatoires (graine fixée, donc reproductible)."""
    jeu = Jeu(charger_carte(nom_carte))
    rng = random.Random(graine)
    agent = AgentAleatoire()
    agent.reinitialiser(graine)
    etats = [jeu.etat_initial()]
    while len(etats) < n:
        s = jeu.etat_initial(rng.choice([BLEU, ROUGE]))
        for _ in range(rng.randint(2, 20)):
            if jeu.terminal(s):
                break
            s = jeu.transition(s, agent.choisir(jeu, s))
        if not jeu.terminal(s) and s not in etats:
            etats.append(s)
    return etats


def ecrire_csv(chemin: Path, lignes: list[dict]) -> None:
    chemin.parent.mkdir(exist_ok=True)
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)


def tableau_md(entetes: list[str], lignes: list[list]) -> str:
    md = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    md += ["| " + " | ".join(str(v) for v in l) + " |" for l in lignes]
    return "\n".join(md)
