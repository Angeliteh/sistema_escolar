"""
Detector de intención maestro - Clasifica consultas para dirigir a diferentes intérpretes
"""
import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.core.logging import get_logger
from app.core.config import Config

@dataclass
class IntentionResult:
    """Resultado de la detección de intención POTENCIADO"""
    intention_type: str  # "consulta_alumnos", "ayuda_sistema", "conversacion_general"
    sub_intention: str   # "busqueda_simple", "generar_constancia", "transformar_pdf", "consulta_avanzada", etc.
    confidence: float
    reasoning: str
    detected_entities: Dict[str, Any]

class IntentionDetector:
    """Detector maestro de intenciones para el sistema escolar"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

    def detect_intention(self, user_query: str) -> IntentionResult:
        """
        PROMPT MAESTRO POTENCIADO: Detecta intención + sub-intención + contexto completo
        """
        try:
            # Crear prompt maestro de detección POTENCIADO
            master_prompt = f"""
Eres un detector de intenciones maestro AVANZADO para un sistema escolar integral.
Tu trabajo es clasificar consultas Y extraer contexto completo para dirigir eficientemente a los módulos especializados.

🏫 CONTEXTO DEL SISTEMA:
- Escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ"
- Base de datos: 7 alumnos con información completa (nombres, CURPs, matrículas, grados, grupos, turnos)
- Capacidades: consultas SQL, generación de constancias, transformación de PDFs, ayuda contextual
- Usuarios: personal administrativo, maestros, directivos

📝 CONSULTA DEL USUARIO: "{user_query}"

🎯 CLASIFICACIÓN INTELIGENTE CON SUB-INTENCIONES:

1. "consulta_alumnos" - GESTIÓN COMPLETA DE ESTUDIANTES:

   SUB-INTENCIONES ESPECÍFICAS:
   a) "busqueda_simple" - Buscar información básica:
      - "buscar a Juan", "cuántos alumnos hay", "alumnos de 3er grado"
      - "dame la CURP de María", "estudiantes del turno matutino"

   b) "generar_constancia" - Crear documentos oficiales:
      - "constancia de estudios para Juan", "certificado de calificaciones"
      - "generar constancia de traslado", "necesito constancia para María"

   c) "transformar_pdf" - Convertir documentos existentes:
      - "transformar esta constancia", "convertir PDF al nuevo formato"
      - "cambiar formato de constancia", "actualizar documento"

   d) "consulta_avanzada" - Estadísticas y análisis:
      - "estadísticas por grado", "promedio de calificaciones"
      - "distribución por turnos", "análisis académico"

2. "ayuda_sistema" - COMPRENSIÓN DE CAPACIDADES:
   a) "entender_capacidades" - Qué puede hacer el sistema
   b) "tutorial_paso_a_paso" - Cómo usar funcionalidades
   c) "solucion_problema" - Resolver errores o problemas
   d) "ejemplo_practico" - Solicitar ejemplos específicos

3. "conversacion_general" - CHAT CASUAL:
   - "hola", "buenos días", "gracias", "¿cómo estás?"

🧠 ANÁLISIS CONTEXTUAL AVANZADO:
Para cada consulta, extrae:
- Nombres de alumnos mencionados
- Tipos de constancia solicitados (estudios, calificaciones, traslado)
- Acciones específicas (buscar, generar, transformar, consultar)
- Contexto de datos (desde BD, desde PDF, desde conversación previa)
- Parámetros adicionales (grados, grupos, turnos, fechas)



RESPONDE ÚNICAMENTE con un JSON siguiendo este formato:
{{
    "intention_type": "consulta_alumnos|ayuda_sistema|conversacion_general",
    "sub_intention": "busqueda_simple|generar_constancia|transformar_pdf|consulta_avanzada|entender_capacidades|tutorial_paso_a_paso|solucion_problema|ejemplo_practico|chat_casual",
    "confidence": 0.0-1.0,
    "reasoning": "Explicación específica del análisis realizado",
    "detected_entities": {{
        "nombres": ["lista de nombres detectados"],
        "tipo_constancia": "estudios|calificaciones|traslado|null",
        "accion_principal": "acción específica detectada",
        "fuente_datos": "base_datos|pdf_cargado|conversacion_previa|null",
        "contexto_especifico": "contexto adicional relevante",
        "filtros": ["filtros detectados como grado, grupo, turno"],
        "parametros_extra": {{"cualquier parámetro adicional relevante"}}
    }}
}}
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(master_prompt)

            if response:
                print(f"🎯 Respuesta detección maestro: {response}")

                # Parsear respuesta
                intention_data = self._parse_intention_response(response)

                if intention_data:
                    return IntentionResult(
                        intention_type=intention_data.get('intention_type', 'conversacion_general'),
                        sub_intention=intention_data.get('sub_intention', 'chat_casual'),  # ← NUEVO
                        confidence=intention_data.get('confidence', 0.5),
                        reasoning=intention_data.get('reasoning', ''),
                        detected_entities=intention_data.get('detected_entities', {})
                    )
                else:
                    # Fallback a conversación general
                    return IntentionResult(
                        intention_type='conversacion_general',
                        sub_intention='chat_casual',  # ← NUEVO
                        confidence=Config.INTERPRETATION['confidence_thresholds']['low'],
                        reasoning='No se pudo parsear la respuesta del detector',
                        detected_entities={}
                    )
            else:
                # Fallback a conversación general
                return IntentionResult(
                    intention_type='conversacion_general',
                    sub_intention='chat_casual',  # ← NUEVO
                    confidence=Config.INTERPRETATION['confidence_thresholds']['low'],
                    reasoning='No se recibió respuesta del detector',
                    detected_entities={}
                )

        except Exception as e:
            self.logger.error(f"Error en detección de intención: {e}")
            # Fallback a conversación general
            return IntentionResult(
                intention_type='conversacion_general',
                sub_intention='chat_casual',  # ← NUEVO
                confidence=Config.INTERPRETATION['confidence_thresholds']['fallback'],
                reasoning=f'Error en detección: {str(e)}',
                detected_entities={}
            )

    def _parse_intention_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parsea la respuesta JSON del detector de intención"""
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
                        intention_data = json.loads(matches[0])
                        print(f"✅ Intención parseada: {intention_data}")
                        return intention_data
                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON, intentar parsear directamente
            try:
                intention_data = json.loads(clean_response)
                return intention_data
            except json.JSONDecodeError:
                print(f"❌ No se pudo parsear JSON de intención: {clean_response}")
                return None

        except Exception as e:
            print(f"Error parseando intención: {e}")
            return None
