"""
Generador de contenido de ayuda
Especializado en crear contenido educativo sobre el sistema
🆕 AHORA USA HelpPromptManager centralizado
"""

from typing import Dict, Any, Optional
from app.core.logging import get_logger
from app.core.ai.prompts.help_prompt_manager import HelpPromptManager

class HelpContentGenerator:
    """
    Clase especializada en generar contenido de ayuda usando LLM
    🆕 PROMPTS CENTRALIZADOS en HelpPromptManager
    """

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.prompt_manager = HelpPromptManager()  # 🆕 PROMPT MANAGER CENTRALIZADO

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

            # 🆕 USAR PROMPT MANAGER CENTRALIZADO
            content_prompt = self.prompt_manager.get_help_content_prompt(user_query, help_type, detected_entities)

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

    # 🗑️ MÉTODO ELIMINADO: _build_content_prompt()
    # RAZÓN: Duplicado - ya existe versión centralizada en HelpPromptManager
    # USO: self.prompt_manager.get_help_content_prompt()

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

    # 🗑️ MÉTODO ELIMINADO: _build_system_context()
    # RAZÓN: Duplicado - ya existe versión centralizada en HelpPromptManager
    # USO: self.prompt_manager.system_context
