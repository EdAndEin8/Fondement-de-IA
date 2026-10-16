"""Agents joueurs. Chaque agent implémente :class:`Agent`."""

from .base import Agent, AgentAleatoire
from .planificateur import AgentAStar

__all__ = ["Agent", "AgentAleatoire", "AgentAStar"]
