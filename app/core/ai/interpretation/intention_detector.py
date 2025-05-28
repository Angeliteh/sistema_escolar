"""
Detector de intención maestro - Clasifica consultas para dirigir a diferentes intérpretes
"""
import json
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.core.logging import get_logger
from app.core.config import Config
from app.core.ai.prompts.master_prompt_manager import MasterPromptManager

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
        # 🆕 PROMPT MANAGER CENTRALIZADO
        self.prompt_manager = MasterPromptManager()
        self.logger.debug("MasterPromptManager inicializado")

    def detect_intention(self, user_query: str, conversation_stack: list = None) -> IntentionResult:
        """
        PROMPT MAESTRO POTENCIADO: Detecta intención + sub-intención + contexto completo
        """
        try:
            # 🆕 USAR PROMPT MANAGER CENTRALIZADO
            conversation_context = self.prompt_manager.format_conversation_context(conversation_stack)
            master_prompt = self.prompt_manager.get_intention_detection_prompt(user_query, conversation_context)

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


