"""États de test variés pour les tests de la Partie III."""

import random

from course_balise.agents import AgentAleatoire
from course_balise.carte import charger_carte
from course_balise.etat import BLEU, ROUGE, Etat
from course_balise.regles import Jeu


def etats_de_test(nom: str, n: int = 12, graine: int = 0) -> list[Etat]:
    """Les deux états initiaux, puis des états atteints par des parties aléatoires."""
    jeu = Jeu(charger_carte(nom))
    rng = random.Random(graine)
    agent = AgentAleatoire()
    agent.reinitialiser(graine)
    res = [jeu.etat_initial(), jeu.etat_initial(ROUGE)]
    while len(res) < n:
        s = jeu.etat_initial(rng.choice([BLEU, ROUGE]))
        for _ in range(rng.randint(1, 25)):
            if jeu.terminal(s):
                break
            s = jeu.transition(s, agent.choisir(jeu, s))
        if not jeu.terminal(s):
            res.append(s)
    return res
