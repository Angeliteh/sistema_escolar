"""
Módulo de gestión centralizada de prompts para el sistema de constancias

Este módulo contiene los managers de prompts especializados por área:
- StudentQueryPromptManager: Prompts para consultas de estudiantes
- (Futuro) HelpPromptManager: Prompts para sistema de ayuda
- (Futuro) ConstanciaPromptManager: Prompts para generación de constancias

Filosofía:
- Centralización de contexto común
- Eliminación de duplicación
- Consistencia entre prompts similares
- Facilidad de mantenimiento
"""

from .student_query_prompt_manager import StudentQueryPromptManager
from .master_prompt_manager import MasterPromptManager

__all__ = [
    'StudentQueryPromptManager',
    'MasterPromptManager'
]
