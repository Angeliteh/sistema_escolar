"""
Parser de respuestas para el sistema de interpretación
"""
import json
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ParsedResponse:
    """Respuesta parseada del LLM"""
    action: str
    parameters: Dict[str, Any]
    confidence: float = 1.0
    raw_response: str = ""
    parsing_method: str = ""

class ResponseParser:
    """Parser para respuestas de LLM"""
    
    def __init__(self):
        self.parsing_methods = [
            self._parse_clean_json,
            self._parse_json_with_markdown,
            self._parse_json_with_text,
            self._parse_partial_json,
            self._parse_fallback
        ]
    
    def parse(self, response_text: str) -> Optional[ParsedResponse]:
        """
        Parsea una respuesta de texto del LLM
        
        Args:
            response_text: Texto de respuesta del LLM
            
        Returns:
            Respuesta parseada o None si no se pudo parsear
        """
        if not response_text or not response_text.strip():
            return None
        
        # Intentar diferentes métodos de parsing
        for method in self.parsing_methods:
            try:
                result = method(response_text)
                if result:
                    result.raw_response = response_text
                    return result
            except Exception as e:
                print(f"Error en método {method.__name__}: {str(e)}")
                continue
        
        return None
    
    def _parse_clean_json(self, text: str) -> Optional[ParsedResponse]:
        """Intenta parsear JSON limpio"""
        try:
            # Buscar JSON completo
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = text[start:end]
                data = json.loads(json_str)
                
                if self._is_valid_command_structure(data):
                    return ParsedResponse(
                        action=data.get("accion", "desconocida"),
                        parameters=data.get("parametros", {}),
                        confidence=data.get("confianza", 1.0),
                        parsing_method="clean_json"
                    )
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _parse_json_with_markdown(self, text: str) -> Optional[ParsedResponse]:
        """Parsea JSON dentro de bloques de markdown"""
        # Buscar bloques de código JSON
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                data = json.loads(match)
                if self._is_valid_command_structure(data):
                    return ParsedResponse(
                        action=data.get("accion", "desconocida"),
                        parameters=data.get("parametros", {}),
                        confidence=data.get("confianza", 1.0),
                        parsing_method="markdown_json"
                    )
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _parse_json_with_text(self, text: str) -> Optional[ParsedResponse]:
        """Parsea JSON mezclado con texto"""
        # Buscar múltiples posibles JSONs en el texto
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text)
        
        for match in matches:
            try:
                data = json.loads(match)
                if self._is_valid_command_structure(data):
                    return ParsedResponse(
                        action=data.get("accion", "desconocida"),
                        parameters=data.get("parametros", {}),
                        confidence=data.get("confianza", 1.0),
                        parsing_method="mixed_text_json"
                    )
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _parse_partial_json(self, text: str) -> Optional[ParsedResponse]:
        """Intenta reparar JSON parcial o malformado"""
        # Buscar patrones de acción y parámetros
        action_pattern = r'"accion"\s*:\s*"([^"]+)"'
        params_pattern = r'"parametros"\s*:\s*(\{[^}]*\})'
        
        action_match = re.search(action_pattern, text)
        if not action_match:
            return None
        
        action = action_match.group(1)
        parameters = {}
        
        params_match = re.search(params_pattern, text)
        if params_match:
            try:
                parameters = json.loads(params_match.group(1))
            except json.JSONDecodeError:
                # Intentar extraer parámetros manualmente
                parameters = self._extract_parameters_manually(text)
        
        return ParsedResponse(
            action=action,
            parameters=parameters,
            confidence=0.7,  # Menor confianza para JSON reparado
            parsing_method="partial_json"
        )
    
    def _parse_fallback(self, text: str) -> Optional[ParsedResponse]:
        """Método de fallback usando análisis de texto"""
        # Buscar palabras clave de acciones conocidas
        action_keywords = {
            "buscar": "buscar_alumno",
            "encontrar": "buscar_alumno",
            "detalles": "detalles_alumno",
            "información": "detalles_alumno",
            "generar": "generar_constancia",
            "crear": "generar_constancia",
            "transformar": "transformar_constancia",
            "convertir": "transformar_constancia",
            "guardar": "guardar_alumno_pdf",
            "extraer": "guardar_alumno_pdf",
            "registrar": "registrar_alumno",
            "ayuda": "mostrar_ayuda"
        }
        
        text_lower = text.lower()
        
        for keyword, action in action_keywords.items():
            if keyword in text_lower:
                # Intentar extraer parámetros básicos
                parameters = self._extract_basic_parameters(text, action)
                
                return ParsedResponse(
                    action=action,
                    parameters=parameters,
                    confidence=0.5,  # Baja confianza para fallback
                    parsing_method="fallback_keywords"
                )
        
        # Si no se encuentra nada, retornar acción desconocida
        return ParsedResponse(
            action="desconocida",
            parameters={"mensaje": text},
            confidence=0.3,
            parsing_method="fallback_unknown"
        )
    
    def _is_valid_command_structure(self, data: Dict[str, Any]) -> bool:
        """Valida que la estructura del comando sea válida"""
        if not isinstance(data, dict):
            return False
        
        # Debe tener al menos una acción
        if "accion" not in data:
            return False
        
        # Los parámetros deben ser un diccionario si existen
        if "parametros" in data and not isinstance(data["parametros"], dict):
            return False
        
        return True
    
    def _extract_parameters_manually(self, text: str) -> Dict[str, Any]:
        """Extrae parámetros manualmente del texto"""
        parameters = {}
        
        # Buscar patrones comunes
        patterns = {
            "nombre": r'"nombre"\s*:\s*"([^"]+)"',
            "curp": r'"curp"\s*:\s*"([^"]+)"',
            "tipo": r'"tipo"\s*:\s*"([^"]+)"',
            "grado": r'"grado"\s*:\s*"?([^",}]+)"?',
            "grupo": r'"grupo"\s*:\s*"([^"]+)"'
        }
        
        for param, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                parameters[param] = match.group(1).strip()
        
        return parameters
    
    def _extract_basic_parameters(self, text: str, action: str) -> Dict[str, Any]:
        """Extrae parámetros básicos según la acción"""
        parameters = {}
        
        if action in ["buscar_alumno", "detalles_alumno"]:
            # Buscar nombres en el texto
            name_patterns = [
                r'(?:de|para|alumno)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)',
                r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    parameters["nombre"] = match.group(1)
                    break
        
        elif action == "generar_constancia":
            # Buscar tipo de constancia
            if "calificaciones" in text.lower():
                parameters["tipo"] = "calificaciones"
            elif "traslado" in text.lower():
                parameters["tipo"] = "traslado"
            else:
                parameters["tipo"] = "estudio"
        
        return parameters
