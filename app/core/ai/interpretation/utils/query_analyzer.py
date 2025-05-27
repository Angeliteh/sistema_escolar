"""
Analizador de consultas
Responsabilidad: Analizar y clasificar consultas de usuarios
"""
import re
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger


class QueryAnalyzer:
    """Analiza y clasifica consultas de usuarios"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def analyze_query(self, user_query: str) -> Dict[str, Any]:
        """
        Analiza una consulta del usuario y extrae información relevante
        
        Args:
            user_query: Consulta del usuario
            
        Returns:
            Dict con información analizada de la consulta
        """
        try:
            analysis = {
                'original_query': user_query,
                'cleaned_query': self._clean_query(user_query),
                'keywords': self._extract_keywords(user_query),
                'entities': self._extract_entities(user_query),
                'intent_indicators': self._detect_intent_indicators(user_query),
                'query_type': self._classify_query_type(user_query),
                'complexity': self._assess_complexity(user_query)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analizando consulta: {e}")
            return {
                'original_query': user_query,
                'error': str(e)
            }
    
    def _clean_query(self, query: str) -> str:
        """Limpia la consulta removiendo caracteres innecesarios"""
        # Remover caracteres especiales y normalizar espacios
        cleaned = re.sub(r'[^\w\s]', ' ', query)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip().lower()
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extrae palabras clave relevantes de la consulta"""
        # Palabras clave comunes en consultas escolares
        school_keywords = [
            'alumno', 'alumnos', 'estudiante', 'estudiantes',
            'constancia', 'certificado', 'documento',
            'calificaciones', 'estudios', 'traslado',
            'grado', 'grupo', 'turno', 'nombre', 'curp'
        ]
        
        query_lower = query.lower()
        found_keywords = []
        
        for keyword in school_keywords:
            if keyword in query_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extrae entidades específicas de la consulta"""
        entities = {
            'numbers': re.findall(r'\b\d+\b', query),
            'grades': re.findall(r'\b[1-6](?:er|do|to|ro|vo|to)?\s*grado\b', query.lower()),
            'names': self._extract_possible_names(query),
            'positions': re.findall(r'\b(?:primer|segundo|tercer|cuarto|quinto|último)\b', query.lower())
        }
        
        return entities
    
    def _extract_possible_names(self, query: str) -> List[str]:
        """Extrae posibles nombres de personas de la consulta"""
        # Buscar palabras que podrían ser nombres (capitalizadas)
        words = query.split()
        possible_names = []
        
        for word in words:
            # Si la palabra está capitalizada y no es una palabra común
            if word[0].isupper() and len(word) > 2:
                common_words = ['El', 'La', 'De', 'Del', 'En', 'Con', 'Para', 'Por']
                if word not in common_words:
                    possible_names.append(word)
        
        return possible_names
    
    def _detect_intent_indicators(self, query: str) -> Dict[str, bool]:
        """Detecta indicadores de intención en la consulta"""
        query_lower = query.lower()
        
        indicators = {
            'search': any(word in query_lower for word in ['buscar', 'encontrar', 'dame', 'muestra']),
            'generate': any(word in query_lower for word in ['generar', 'crear', 'hacer', 'constancia']),
            'list': any(word in query_lower for word in ['lista', 'todos', 'cuántos', 'varios']),
            'specific': any(word in query_lower for word in ['específico', 'particular', 'ese', 'esa']),
            'question': query.strip().endswith('?'),
            'confirmation': any(word in query_lower for word in ['sí', 'si', 'correcto', 'está bien'])
        }
        
        return indicators
    
    def _classify_query_type(self, query: str) -> str:
        """Clasifica el tipo general de consulta"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['constancia', 'certificado', 'documento']):
            return 'constancia_request'
        elif any(word in query_lower for word in ['buscar', 'encontrar', 'dame', 'muestra']):
            return 'search_query'
        elif any(word in query_lower for word in ['cuántos', 'total', 'cantidad']):
            return 'count_query'
        elif any(word in query_lower for word in ['sí', 'si', 'correcto', 'está bien']):
            return 'confirmation'
        elif query.strip().endswith('?'):
            return 'question'
        else:
            return 'general'
    
    def _assess_complexity(self, query: str) -> str:
        """Evalúa la complejidad de la consulta"""
        word_count = len(query.split())
        
        if word_count <= 3:
            return 'simple'
        elif word_count <= 8:
            return 'medium'
        else:
            return 'complex'
    
    def has_continuation_indicators(self, query: str) -> bool:
        """Detecta si la consulta tiene indicadores de continuación"""
        continuation_words = [
            'él', 'ella', 'ese', 'esa', 'eso', 'este', 'esta', 'esto',
            'primero', 'segundo', 'tercero', 'último', 'anterior'
        ]
        
        query_lower = query.lower()
        return any(word in query_lower for word in continuation_words)
    
    def extract_reference_type(self, query: str) -> Optional[str]:
        """Extrae el tipo de referencia en la consulta"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['primero', 'primer', 'primera']):
            return 'first'
        elif any(word in query_lower for word in ['segundo', 'segunda']):
            return 'second'
        elif any(word in query_lower for word in ['tercero', 'tercer', 'tercera']):
            return 'third'
        elif any(word in query_lower for word in ['último', 'ultima']):
            return 'last'
        elif any(word in query_lower for word in ['él', 'ella', 'ese', 'esa']):
            return 'pronoun'
        
        return None
