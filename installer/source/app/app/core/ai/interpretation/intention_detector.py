"""
Detector de intención maestro - Clasifica consultas para dirigir a diferentes intérpretes
"""
import json
import re
from typing import Dict, Any
from dataclasses import dataclass
from app.core.logging import get_logger
from app.core.ai.prompts.master_prompt_manager import MasterPromptManager

@dataclass
class IntentionResult:
    """Resultado de la detección de intención CONSOLIDADO"""
    intention_type: str  # "consulta_alumnos", "ayuda_sistema", "conversacion_general"
    sub_intention: str   # "busqueda_simple", "generar_constancia", "transformar_pdf", "consulta_avanzada", etc.
    confidence: float
    reasoning: str
    detected_entities: Dict[str, Any]
    # 🆕 CATEGORIZACIÓN ESPECÍFICA (del Student Prompt 1 eliminado)
    categoria: str = ""           # busqueda|estadistica|reporte|constancia|transformacion|continuacion
    sub_tipo: str = ""            # simple|complejo|listado|conteo|generacion|conversion|referencia|confirmacion
    complejidad: str = ""         # baja|media|alta
    requiere_contexto: bool = False
    flujo_optimo: str = ""        # sql_directo|analisis_datos|listado_completo|generacion_docs|procesamiento_contexto

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
        PROMPT MAESTRO CONSOLIDADO: Detección de intenciones + categorización específica
        🧹 SIN FALLBACKS - Una sola implementación limpia
        """
        # 🆕 USAR PROMPT MANAGER CENTRALIZADO
        conversation_context = self.prompt_manager.format_conversation_context(conversation_stack)
        master_prompt = self.prompt_manager.get_intention_detection_prompt(user_query, conversation_context)

        # Enviar al LLM
        response = self.gemini_client.send_prompt_sync(master_prompt)

        # 🧠 [MASTER] Analizando intención con LLM
        intention_data = self._parse_intention_response(response)

        # 🆕 EXTRAER CATEGORIZACIÓN ESPECÍFICA
        student_cat = intention_data.get('student_categorization', {})

        return IntentionResult(
            intention_type=intention_data.get('intention_type'),
            sub_intention=intention_data.get('sub_intention'),
            confidence=intention_data.get('confidence'),
            reasoning=intention_data.get('reasoning'),
            detected_entities=intention_data.get('detected_entities', {}),
            # 🆕 CATEGORIZACIÓN ESPECÍFICA CONSOLIDADA
            categoria=student_cat.get('categoria'),
            sub_tipo=student_cat.get('sub_tipo'),
            complejidad=student_cat.get('complejidad'),
            requiere_contexto=student_cat.get('requiere_contexto', False),
            flujo_optimo=student_cat.get('flujo_optimo')
        )

    def _parse_intention_response(self, response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta JSON del detector de intención
        🧹 SIN FALLBACKS - Si falla, que falle claramente para debugging
        """
        # Limpiar la respuesta
        clean_response = response.strip()

        # Buscar JSON en la respuesta con patrones
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'(\{.*?\})'
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, clean_response, re.DOTALL)
            if matches:
                intention_data = json.loads(matches[0])
                return intention_data

        # Si no encuentra patrones, intentar parsear directamente
        self.logger.info(f"🔍 [PARSE] Intentando parseo directo")
        intention_data = json.loads(clean_response)
        self.logger.info(f"✅ [PARSE] Parseo directo exitoso: {intention_data}")
        return intention_data


