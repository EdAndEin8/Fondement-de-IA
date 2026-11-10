"""Partie II — Représentation des connaissances et raisonnement.

Modules :
- ``faits``  : base de faits décrivant un état, et affichage d'un fait ;
- ``moteur`` : unification, règles, chaînage avant et base de connaissances.
"""

from .faits import ROBOT, Fait, faits_de_etat, format_fait
from .moteur import (REGLES, BaseConnaissances, Derivation, Regle,
                     chainage_avant, substituer, unifier)

__all__ = [
    "ROBOT",
    "Fait",
    "faits_de_etat",
    "format_fait",
    "REGLES",
    "BaseConnaissances",
    "Derivation",
    "Regle",
    "chainage_avant",
    "substituer",
    "unifier",
]
