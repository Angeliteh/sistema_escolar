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
        """Formatea la pila conversacional para el LLM incluyendo nota estratégica"""
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
            # 🎯 INCLUIR NOTA ESTRATÉGICA DE STUDENT
            auto_reflexion = level.get('auto_reflexion', {})
            nota_para_master = auto_reflexion.get('nota_para_master', '')
            if nota_para_master:
                context += f"- NOTA ESTRATÉGICA: {nota_para_master}\n"

            # Mostrar algunos datos de ejemplo si hay
            if level.get('data') and len(level.get('data', [])) > 0:
                context += f"- Primeros elementos: {level['data'][:3]}\n"

        return context

    def _build_continuation_prompt(self, user_query: str, stack_context: str) -> str:
        """Construye el prompt para detección inteligente de continuación usando nota estratégica"""

        # Extraer nota estratégica del último nivel si existe
        nota_estrategica = "No hay nota estratégica disponible"
        if stack_context and "NOTA ESTRATÉGICA:" in stack_context:
            try:
                lines = stack_context.split('\n')
                for line in lines:
                    if "NOTA ESTRATÉGICA:" in line:
                        nota_estrategica = line.split("NOTA ESTRATÉGICA:", 1)[1].strip()
                        break
            except:
                pass

        return f"""
Eres un detector inteligente de continuaciones conversacionales para un sistema escolar.

CONTEXTO CONVERSACIONAL ANTERIOR:
{stack_context}

NOTA ESTRATÉGICA DE STUDENT (Predicciones de continuación):
{nota_estrategica}

NUEVA CONSULTA DEL USUARIO: "{user_query}"

INSTRUCCIONES PARA DETECCIÓN INTELIGENTE:
Analiza si la nueva consulta se refiere al contexto anterior usando la nota estratégica como guía principal.

TIPOS DE CONTINUACIÓN INTELIGENTE (REQUIEREN REFERENCIA EXPLÍCITA):
1. POSICIÓN: "del primero", "el último", "del cuarto" → se refiere a posición en lista anterior
2. FILTRO CON REFERENCIA: "de esos los de segundo", "de ellos los del turno matutino" → filtrar datos anteriores
3. ACCIÓN: "constancia para él", "información del tercero" → acción sobre elemento específico
4. CONTEO CON REFERENCIA: "cuántos de esos son de [criterio]" → contar con filtro sobre datos anteriores
5. ESTADÍSTICAS CON REFERENCIA: "distribución de ellos", "estadísticas de ese grupo" → análisis de datos anteriores
6. CONFIRMACIÓN: "sí", "correcto", "proceder" → confirmar acción sugerida

REFERENCIAS EXPLÍCITAS QUE INDICAN CONTINUACIÓN (OBLIGATORIAS):
- "de esos", "de ellos", "del grupo anterior", "de la lista", "entre ellos"
- "ese alumno", "esa estudiante", "del que muestras", "de los que aparecen"
- "ahora de esos dame", "de ellos necesito", "de esos quiero"
- "cuántos de esos son", "estadísticas de ellos", "distribución de esos"

CONSULTAS COMPLETAMENTE NUEVAS (Sin contexto):
- Consultas específicas nuevas: "alumnos de tercer grado", "buscar García", "nombre de un alumno"
- Cambios de tema: "ayuda del sistema", "estadísticas generales"
- Solicitudes específicas: "dame el nombre de...", "cuántos alumnos...", "información de..."
- ESTADÍSTICAS GLOBALES: "promedio general de la escuela", "total de alumnos", "estadísticas de toda la escuela"
- CONSULTAS DE TODA LA ESCUELA: "de toda la escuela", "general de la escuela", "en total"

REGLAS CRÍTICAS REDISEÑADAS:
- Si la consulta SELECCIONA UN ELEMENTO ESPECÍFICO por posición/referencia → SÍ es continuación tipo "selection"
- Si la consulta pide ACCIÓN sobre UN ELEMENTO ESPECÍFICO → SÍ es continuación tipo "action"
- Si la consulta ANALIZA/FILTRA/CALCULA sobre MÚLTIPLES elementos del contexto → SÍ es continuación tipo "analysis"
- Si la consulta usa referencias como "de todos ellos", "de esos", "entre ellos" → SÍ es continuación tipo "analysis"
- Si la consulta especifica NUEVOS criterios sin referencia al contexto → NO es continuación (nueva consulta)

RESPONDE ÚNICAMENTE con un JSON:
{{
    "es_continuacion": true|false,
    "tipo_continuacion": "selection|action|confirmation|specification|analysis|none",
    "nivel_referenciado": 1|2|3...|null,
    "elemento_referenciado": numero_del_elemento|null,
    "razonamiento": "Explicación de por qué es/no es continuación",
    "confianza": 0.0-1.0
}}

EJEMPLOS CORRECTOS:

CONTINUACIONES VERDADERAS (Referencias al contexto):
- "CURP del quinto" → es_continuacion: true, tipo: "selection", elemento_referenciado: 5
- "constancia para él" → es_continuacion: true, tipo: "action", nivel_referenciado: último
- "información del tercero" → es_continuacion: true, tipo: "selection", elemento_referenciado: 3
- "sí, adelante" → es_continuacion: true, tipo: "confirmation"
- "de todos ellos quienes tienen calificaciones" → es_continuacion: true, tipo: "analysis"
- "de todos ellos quienes tienen calificaciones?" → es_continuacion: true, tipo: "analysis"
- "cuántos de ellos son de turno matutino" → es_continuacion: true, tipo: "analysis"
- "entre esos alumnos cuáles tienen mejor promedio" → es_continuacion: true, tipo: "analysis"

CONSULTAS COMPLETAMENTE NUEVAS (Sin referencia al contexto):
- "alumnos de tercer grado" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "buscar García" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "cuántos alumnos hay en total" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "ayuda del sistema" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)

CONSULTAS COMPLETAMENTE NUEVAS (Sin contexto):
- "dame el nombre de un alumno de tercer grado" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "alumnos de segundo grado" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "cuántos alumnos hay" → es_continuacion: false, tipo: "none" (NUEVA CONSULTA)
- "dame el promedio general de calificaciones de la escuela" → es_continuacion: false, tipo: "none" (ESTADÍSTICA GLOBAL)
- "total de alumnos en la escuela" → es_continuacion: false, tipo: "none" (ESTADÍSTICA GLOBAL)
- "estadísticas generales de toda la escuela" → es_continuacion: false, tipo: "none" (ESTADÍSTICA GLOBAL)
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
