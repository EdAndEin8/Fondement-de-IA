"""Partie IV — Information partielle.

Modules :
- ``vue``     : vue locale d'un robot (cases à distance de Manhattan au plus r) ;
- ``memoire`` : mémoire des observations, frontières, carte supposée ;
- ``solo``    : course d'un robot seul, pour comparer carte complète et
  découverte progressive.

Les règles physiques du jeu ne changent pas : seul ce que l'agent sait de
l'état est restreint. Les agents correspondants sont dans
``agents/partiels.py``.
"""

from .memoire import INCONNU, Memoire
from .vue import Observation, vue_locale

__all__ = ["INCONNU", "Memoire", "Observation", "vue_locale"]
