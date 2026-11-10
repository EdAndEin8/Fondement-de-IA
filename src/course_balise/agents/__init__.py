"""Agents joueurs. Chaque agent implémente :class:`Agent`."""

from .adversariaux import (AgentAlphaBeta, AgentAlphaBetaAmeliore, AgentAlphaBetaIteratif,
                           AgentMinMax)
from .base import Agent, AgentAleatoire
from .partiels import AgentAlphaBetaOptimiste, AgentExplorateur
from .planificateur import AgentAStar

__all__ = [
    "Agent", "AgentAleatoire", "AgentAStar",
    "AgentMinMax", "AgentAlphaBeta", "AgentAlphaBetaAmeliore", "AgentAlphaBetaIteratif",
    "AgentExplorateur", "AgentAlphaBetaOptimiste",
]
