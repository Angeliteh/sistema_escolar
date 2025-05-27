"""
Detector de continuaciones conversacionales
Responsabilidad: Determinar si una consulta se refiere a elementos previos de la conversación
"""
import json
import re
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger


class ContinuationDetector:
    """Detecta y clasifica continuaciones conversacionales usando LLM"""
    
    def __init__(self, gemini_client=None):
        self.logger = get_logger(__name__)
        self.gemini_client = gemini_client
    
    def detect_continuation(self, user_query: str, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        Detecta si la consulta es una continuación de la conversación anterior
        
        Returns:
            Dict con información de continuación o None si no es continuación
        """
        try:
            if not conversation_stack:
                return {"es_continuacion": False, "tipo_continuacion": "none"}
            
            # Formatear contexto para el LLM
            stack_context = self._format_conversation_stack(conversation_stack)
            
            # Crear prompt de detección
            continuation_prompt = self._build_continuation_prompt(user_query, stack_context)
            
            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(continuation_prompt)
            
            if response:
                continuation_info = self._parse_json_response(response)
                if continuation_info:
                    self.logger.debug(f"Continuación detectada: {continuation_info}")
                    return continuation_info
                else:
                    self.logger.warning("No se pudo parsear respuesta de continuación")
                    return {"es_continuacion": False, "tipo_continuacion": "none"}
            else:
                self.logger.warning("No hay respuesta del LLM para detección de continuación")
                return {"es_continuacion": False, "tipo_continuacion": "none"}
                
        except Exception as e:
            self.logger.error(f"Error en detección de continuación: {e}")
            return {"es_continuacion": False, "tipo_continuacion": "none"}
    
    def _format_conversation_stack(self, conversation_stack: list) -> str:
        """Formatea la pila conversacional para el LLM"""
        if not conversation_stack:
            return "PILA VACÍA"
        
        context = ""
        for i, level in enumerate(conversation_stack, 1):
            context += f"""
NIVEL {i}:
- Consulta: "{level.get('query', 'N/A')}"
- Datos disponibles: {level.get('row_count', 0)} elementos
- Esperando: {level.get('awaiting', 'N/A')}
- Timestamp: {level.get('timestamp', 'N/A')}
"""
            # Mostrar algunos datos de ejemplo si hay
            if level.get('data') and len(level.get('data', [])) > 0:
                context += f"- Primeros elementos: {level['data'][:3]}\n"
        
        return context
    
    def _build_continuation_prompt(self, user_query: str, stack_context: str) -> str:
        """Construye el prompt para detección de continuación"""
        return f"""
Eres un analizador conversacional inteligente para un sistema escolar.

PILA CONVERSACIONAL ACTUAL:
{stack_context}

NUEVA CONSULTA DEL USUARIO: "{user_query}"

INSTRUCCIONES CRÍTICAS:
Analiza si la nueva consulta se refiere ESPECÍFICAMENTE a algún elemento de la pila conversacional.

PATRONES DE CONTINUACIÓN VERDADERA (REFERENCIAS DIRECTAS):
1. SELECCIÓN: "del primero", "número 5", "el quinto", "para él", "ese alumno", "del tercero"
2. ACCIÓN: "constancia para él", "CURP de ese", "información del tercero", "datos de ese"
3. CONFIRMACIÓN: "sí", "correcto", "está bien", "proceder", "adelante", "continúa"
4. ESPECIFICACIÓN: "de qué tipo", "con foto", "sin foto", "más detalles"

PATRONES QUE NO SON CONTINUACIÓN (CONSULTAS NUEVAS):
- Consultas específicas nuevas: "alumnos de tercer grado", "buscar García", "nombre de un alumno"
- Cambios de tema: "ayuda del sistema", "estadísticas generales"
- Solicitudes específicas: "dame el nombre de...", "cuántos alumnos...", "información de..."

REGLA CRÍTICA:
- Si la consulta especifica NUEVOS criterios (grado, nombre, etc.) → NO es continuación
- Si la consulta se refiere a elementos YA MOSTRADOS → SÍ es continuación

RESPONDE ÚNICAMENTE con un JSON:
{{
    "es_continuacion": true|false,
    "tipo_continuacion": "selection|action|confirmation|specification|none",
    "nivel_referenciado": 1|2|3...|null,
    "elemento_referenciado": numero_del_elemento|null,
    "razonamiento": "Explicación de por qué es/no es continuación",
    "confianza": 0.0-1.0
}}

EJEMPLOS CORRECTOS:
- "CURP del quinto" → es_continuacion: true, tipo: "selection", elemento_referenciado: 5
- "constancia para él" → es_continuacion: true, tipo: "action", nivel_referenciado: último
- "sí, adelante" → es_continuacion: true, tipo: "confirmation"
- "dame el nombre de un alumno de tercer grado" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "alumnos de segundo grado" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "cuántos alumnos hay" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
"""
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parsea respuesta JSON del LLM"""
        try:
            # Limpiar la respuesta
            clean_response = response.strip()
            
            # Buscar JSON en la respuesta
            json_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```',
                r'(\{.*?\})'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, clean_response, re.DOTALL)
                if matches:
                    try:
                        return json.loads(matches[0])
                    except json.JSONDecodeError:
                        continue
            
            # Intentar parsear directamente
            try:
                return json.loads(clean_response)
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            self.logger.error(f"Error parseando JSON: {e}")
            return None
