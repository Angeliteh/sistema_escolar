"""
Módulo especializado para interpretación de consultas de ayuda
Arquitectura modular con responsabilidades separadas
"""

# Importaciones principales para compatibilidad
from .help_content_generator import HelpContentGenerator
from .help_response_generator import HelpResponseGenerator
from .tutorial_processor import TutorialProcessor
from .capability_analyzer import CapabilityAnalyzer

__all__ = [
    'HelpContentGenerator',
    'HelpResponseGenerator', 
    'TutorialProcessor',
    'CapabilityAnalyzer'
]
