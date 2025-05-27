"""
Módulo especializado para interpretación de consultas de alumnos
Arquitectura modular con responsabilidades separadas
"""

# Importaciones principales para compatibilidad
from .continuation_detector import ContinuationDetector
from .student_identifier import StudentIdentifier
from .constancia_processor import ConstanciaProcessor
from .data_normalizer import DataNormalizer
from .response_generator import ResponseGenerator

__all__ = [
    'ContinuationDetector',
    'StudentIdentifier', 
    'ConstanciaProcessor',
    'DataNormalizer',
    'ResponseGenerator'
]
