"""
Generador de contenido de ayuda
Especializado en crear contenido educativo sobre el sistema
"""

from typing import Dict, Any, Optional
from app.core.logging import get_logger

class HelpContentGenerator:
    """
    Clase especializada en generar contenido de ayuda usando LLM
    """
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.system_context = self._build_system_context()
    
    def generate_content(self, user_query: str, help_type: str, detected_entities: Dict) -> Optional[Dict]:
        """
        Genera contenido de ayuda específico usando LLM
        
        Args:
            user_query: Consulta original del usuario
            help_type: Tipo de ayuda solicitada
            detected_entities: Entidades detectadas
            
        Returns:
            Dict con el contenido de ayuda generado
        """
        try:
            self.logger.debug(f"Generando contenido de ayuda: {help_type}")
            
            # Crear prompt especializado según el tipo
            content_prompt = self._build_content_prompt(user_query, help_type, detected_entities)
            
            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(content_prompt)
            
            if response:
                # Parsear respuesta del LLM
                content_data = self._parse_content_response(response)
                
                if content_data:
                    self.logger.debug(f"Contenido generado exitosamente: {help_type}")
                    return content_data
                else:
                    self.logger.warning("No se pudo parsear respuesta de contenido")
                    return None
            else:
                self.logger.warning("No hay respuesta del LLM para contenido")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generando contenido: {e}")
            return None
    
    def _build_content_prompt(self, user_query: str, help_type: str, detected_entities: Dict) -> str:
        """Construye el prompt para generar contenido específico"""
        
        base_prompt = f"""
Eres un especialista en generar CONTENIDO DE AYUDA para sistema escolar.

CONTEXTO COMPLETO DEL SISTEMA:
{self.system_context}

CONSULTA DEL USUARIO: "{user_query}"
TIPO DE AYUDA: {help_type}
ENTIDADES DETECTADAS: {detected_entities}

INSTRUCCIONES ESPECÍFICAS PARA {help_type.upper()}:
"""
        
        if help_type == "solucion_problema":
            return base_prompt + """
1. IDENTIFICA el problema específico del usuario
2. PROPORCIONA soluciones paso a paso
3. INCLUYE alternativas si la primera solución no funciona
4. OFRECE prevención para evitar el problema en el futuro

FORMATO DE RESPUESTA:
{
    "tipo_contenido": "solucion_problema",
    "problema_identificado": "Descripción del problema",
    "soluciones": [
        {
            "titulo": "Solución principal",
            "pasos": ["paso1", "paso2", "paso3"],
            "consejos": ["consejo1", "consejo2"]
        }
    ],
    "alternativas": ["alternativa1", "alternativa2"],
    "prevencion": ["tip1", "tip2"],
    "ejemplos_practicos": ["ejemplo1", "ejemplo2"]
}
"""
        
        elif help_type == "ejemplo_practico":
            return base_prompt + """
1. GENERA ejemplos reales y específicos del sistema
2. INCLUYE casos de uso comunes y útiles
3. PROPORCIONA pasos detallados para cada ejemplo
4. MUESTRA resultados esperados

FORMATO DE RESPUESTA:
{
    "tipo_contenido": "ejemplo_practico",
    "ejemplos": [
        {
            "titulo": "Ejemplo 1",
            "descripcion": "Qué hace este ejemplo",
            "pasos": ["paso1", "paso2", "paso3"],
            "comando_ejemplo": "texto exacto a escribir",
            "resultado_esperado": "qué verá el usuario"
        }
    ],
    "casos_uso_comunes": ["caso1", "caso2"],
    "consejos_practicos": ["consejo1", "consejo2"]
}
"""
        
        else:  # Contenido general
            return base_prompt + """
1. ANALIZA qué información específica necesita el usuario
2. ESTRUCTURA el contenido de manera clara y útil
3. INCLUYE ejemplos prácticos cuando sea apropiado
4. PROPORCIONA pasos específicos si es necesario

FORMATO DE RESPUESTA:
{
    "tipo_contenido": "ayuda_general",
    "contenido_principal": "Explicación principal",
    "puntos_clave": ["punto1", "punto2", "punto3"],
    "ejemplos": ["ejemplo1", "ejemplo2"],
    "pasos_recomendados": ["paso1", "paso2"],
    "informacion_adicional": "Información extra útil"
}

RESPONDE ÚNICAMENTE CON EL JSON, sin explicaciones adicionales.
"""
    
    def _parse_content_response(self, response: str) -> Optional[Dict]:
        """Parsea la respuesta JSON del LLM"""
        try:
            import json
            import re
            
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
                        content_data = json.loads(matches[0])
                        self.logger.debug(f"Contenido parseado exitosamente")
                        return content_data
                    except json.JSONDecodeError:
                        continue
            
            # Si no encuentra JSON, intentar parsear directamente
            try:
                content_data = json.loads(clean_response)
                return content_data
            except json.JSONDecodeError:
                self.logger.warning(f"No se pudo parsear JSON: {clean_response[:100]}...")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parseando contenido: {e}")
            return None
    
    def _build_system_context(self) -> str:
        """Construye el contexto completo del sistema para el LLM"""
        return """
SISTEMA: Gestión Escolar Inteligente
ESCUELA: "PROF. MAXIMO GAMIZ FERNANDEZ"
CICLO: 2024-2025

MÓDULOS DISPONIBLES:
1. CONSULTAS DE ALUMNOS:
   - Búsquedas por nombre, grado, grupo, turno
   - Conteos y estadísticas automáticas
   - Información específica (CURP, matrícula, etc.)
   - Ejemplos: "cuántos alumnos hay", "buscar García", "alumnos de 2do"

2. GENERACIÓN DE CONSTANCIAS:
   - Constancias de estudios, calificaciones, traslado
   - Formato oficial con datos de la escuela
   - Vista previa antes de generar
   - Ejemplos: "constancia de estudios para Juan"

3. SISTEMA DE AYUDA:
   - Explicaciones de funcionalidades
   - Tutoriales paso a paso
   - Ejemplos prácticos
   - Solución de problemas

CARACTERÍSTICAS:
- Interfaz conversacional en español natural
- Comprensión contextual avanzada
- Respuestas inmediatas y precisas
- Mantenimiento de contexto conversacional
- Auto-reflexión para continuaciones

DATOS DISPONIBLES:
- 211 alumnos registrados
- Grados: 1°, 2°, 3°, 4°, 5°, 6°
- Grupos: A, B, C
- Turnos: Matutino, Vespertino
- Información completa: nombres, CURPs, matrículas, calificaciones
"""
