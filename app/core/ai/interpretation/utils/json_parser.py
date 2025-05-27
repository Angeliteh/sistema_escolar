"""
Parser JSON centralizado
Responsabilidad: Parsear respuestas JSON de LLMs de manera consistente
"""
import json
import re
from typing import Dict, Any, Optional
from app.core.logging import get_logger


class JSONParser:
    """Parser centralizado para respuestas JSON de LLMs"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parsea respuesta JSON de un LLM con múltiples estrategias
        
        Args:
            response: Respuesta del LLM que puede contener JSON
            
        Returns:
            Dict parseado o None si no se puede parsear
        """
        try:
            if not response or not response.strip():
                return None
            
            # Limpiar la respuesta
            clean_response = response.strip()
            
            # Estrategia 1: Buscar JSON en bloques de código
            json_from_blocks = self._extract_json_from_code_blocks(clean_response)
            if json_from_blocks:
                return json_from_blocks
            
            # Estrategia 2: Buscar JSON con regex
            json_from_regex = self._extract_json_with_regex(clean_response)
            if json_from_regex:
                return json_from_regex
            
            # Estrategia 3: Intentar parsear directamente
            json_direct = self._parse_direct_json(clean_response)
            if json_direct:
                return json_direct
            
            # Estrategia 4: Limpiar y intentar nuevamente
            json_cleaned = self._parse_cleaned_json(clean_response)
            if json_cleaned:
                return json_cleaned
            
            self.logger.warning(f"No se pudo parsear JSON de respuesta: {clean_response[:100]}...")
            return None
            
        except Exception as e:
            self.logger.error(f"Error parseando respuesta JSON: {e}")
            return None
    
    def _extract_json_from_code_blocks(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrae JSON de bloques de código markdown"""
        try:
            # Patrones para bloques de código
            code_block_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```'
            ]
            
            for pattern in code_block_patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                if matches:
                    for match in matches:
                        try:
                            return json.loads(match.strip())
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extrayendo JSON de bloques de código: {e}")
            return None
    
    def _extract_json_with_regex(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrae JSON usando expresiones regulares"""
        try:
            # Patrones para encontrar objetos JSON
            json_patterns = [
                r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',  # JSON simple
                r'(\{.*?\})',  # JSON básico
                r'(\[.*?\])'   # Arrays JSON
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                if matches:
                    for match in matches:
                        try:
                            return json.loads(match.strip())
                        except json.JSONDecodeError:
                            continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extrayendo JSON con regex: {e}")
            return None
    
    def _parse_direct_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Intenta parsear directamente como JSON"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None
    
    def _parse_cleaned_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Limpia la respuesta y intenta parsear"""
        try:
            # Limpiar caracteres problemáticos
            cleaned = response.replace('\n', ' ').replace('\r', ' ')
            cleaned = re.sub(r'\s+', ' ', cleaned)  # Múltiples espacios a uno
            cleaned = cleaned.strip()
            
            # Buscar inicio y fin de objeto JSON
            start_idx = cleaned.find('{')
            end_idx = cleaned.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned[start_idx:end_idx + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error parseando JSON limpiado: {e}")
            return None
    
    def validate_json_structure(self, data: Dict[str, Any], required_keys: list) -> bool:
        """
        Valida que el JSON tenga la estructura esperada
        
        Args:
            data: Datos JSON parseados
            required_keys: Claves requeridas
            
        Returns:
            True si la estructura es válida
        """
        try:
            if not isinstance(data, dict):
                return False
            
            for key in required_keys:
                if key not in data:
                    self.logger.warning(f"Clave requerida '{key}' no encontrada en JSON")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando estructura JSON: {e}")
            return False
    
    def extract_value_safely(self, data: Dict[str, Any], key: str, default=None):
        """
        Extrae un valor de manera segura del JSON
        
        Args:
            data: Datos JSON
            key: Clave a extraer
            default: Valor por defecto
            
        Returns:
            Valor extraído o valor por defecto
        """
        try:
            return data.get(key, default)
        except Exception as e:
            self.logger.error(f"Error extrayendo valor '{key}': {e}")
            return default
    
    def format_json_for_logging(self, data: Dict[str, Any], max_length: int = 200) -> str:
        """
        Formatea JSON para logging de manera legible
        
        Args:
            data: Datos JSON
            max_length: Longitud máxima del string
            
        Returns:
            String formateado para logging
        """
        try:
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            if len(json_str) > max_length:
                return json_str[:max_length] + "..."
            return json_str
        except Exception as e:
            return f"Error formateando JSON: {e}"
