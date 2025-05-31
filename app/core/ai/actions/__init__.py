"""
🎯 SISTEMA DE ACCIONES DE ALTO NIVEL

Este módulo implementa un sistema de acciones que permite al LLM
trabajar con un vocabulario estructurado y predecible.

COMPONENTES:
- ActionCatalog: Define todas las acciones disponibles
- ActionExecutor: Ejecuta las acciones seleccionadas por el LLM

FILOSOFÍA:
- LLM elige acciones, no genera código
- Acciones son confiables y combinables
- Abstrae complejidad técnica del LLM
"""

from .action_catalog import ActionCatalog, ActionDefinition
from .action_executor import ActionExecutor

__all__ = ['ActionCatalog', 'ActionDefinition', 'ActionExecutor']
