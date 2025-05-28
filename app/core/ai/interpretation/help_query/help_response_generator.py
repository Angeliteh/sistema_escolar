"""
Generador de respuestas de ayuda con auto-reflexión
Especializado en crear respuestas naturales y contextuales
🆕 AHORA USA HelpPromptManager centralizado
"""

from typing import Dict, Any, Optional
from app.core.logging import get_logger
from app.core.ai.prompts.help_prompt_manager import HelpPromptManager

class HelpResponseGenerator:
    """
    Clase especializada en generar respuestas de ayuda con auto-reflexión
    Implementa el PROMPT 3 del patrón estándar
    🆕 PROMPTS CENTRALIZADOS en HelpPromptManager
    """

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.prompt_manager = HelpPromptManager()  # 🆕 PROMPT MANAGER CENTRALIZADO

    def generate_response_with_reflection(self, user_query: str, help_content: Dict) -> Optional[Dict]:
        """
        Genera respuesta natural con auto-reflexión para continuaciones
        PROMPT 3 del patrón estándar

        Args:
            user_query: Consulta original del usuario
            help_content: Contenido de ayuda generado

        Returns:
            Dict con respuesta_usuario y reflexion_conversacional
        """
        try:
            self.logger.debug("Generando respuesta con auto-reflexión")

            # 🆕 USAR PROMPT MANAGER CENTRALIZADO
            response_prompt = self.prompt_manager.get_help_response_prompt(user_query, help_content)

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(response_prompt)

            if response:
                # Parsear respuesta con auto-reflexión
                response_data = self._parse_response_with_reflection(response)

                if response_data:
                    self.logger.debug("Respuesta con auto-reflexión generada exitosamente")
                    return response_data
                else:
                    self.logger.warning("No se pudo parsear respuesta con auto-reflexión")
                    return self._create_fallback_response(user_query, help_content)
            else:
                self.logger.warning("No hay respuesta del LLM")
                return self._create_fallback_response(user_query, help_content)

        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return self._create_fallback_response(user_query, help_content)

    # 🗑️ MÉTODO ELIMINADO: _build_response_prompt()
    # RAZÓN: Duplicado - ya existe versión centralizada en HelpPromptManager
    # USO: self.prompt_manager.get_help_response_prompt()

    def _parse_response_with_reflection(self, response: str) -> Optional[Dict]:
        """Parsea la respuesta JSON con auto-reflexión"""
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
                        response_data = json.loads(matches[0])

                        # Validar estructura esperada
                        if "respuesta_usuario" in response_data:
                            self.logger.debug("Respuesta con auto-reflexión parseada exitosamente")
                            return response_data
                        else:
                            self.logger.warning("Respuesta no tiene estructura esperada")
                            continue

                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON válido, intentar parsear directamente
            try:
                response_data = json.loads(clean_response)
                if "respuesta_usuario" in response_data:
                    return response_data
            except json.JSONDecodeError:
                pass

            self.logger.warning(f"No se pudo parsear respuesta: {clean_response[:100]}...")
            return None

        except Exception as e:
            self.logger.error(f"Error parseando respuesta: {e}")
            return None

    def _create_fallback_response(self, user_query: str, help_content: Dict) -> Dict:
        """Crea respuesta de fallback cuando el LLM falla"""
        try:
            # Extraer información básica del contenido
            content_type = help_content.get("tipo_contenido", "ayuda_general")

            # Generar respuesta básica según el tipo
            if content_type == "solucion_problema":
                fallback_message = f"He analizado tu consulta sobre problemas. {self._extract_basic_info(help_content)}"
            elif content_type == "ejemplo_practico":
                fallback_message = f"Aquí tienes ejemplos prácticos para tu consulta. {self._extract_basic_info(help_content)}"
            else:
                fallback_message = f"He generado información de ayuda para tu consulta: '{user_query}'. {self._extract_basic_info(help_content)}"

            return {
                "respuesta_usuario": fallback_message,
                "reflexion_conversacional": {
                    "espera_continuacion": True,
                    "tipo_esperado": "exploracion_funcionalidad",
                    "datos_recordar": {
                        "funcionalidad_explicada": "ayuda_general",
                        "nivel_detalle_proporcionado": "basico",
                        "ejemplos_mencionados": [],
                        "temas_relacionados": []
                    },
                    "razonamiento": "Respuesta de fallback - probablemente el usuario necesite más detalles"
                }
            }

        except Exception as e:
            self.logger.error(f"Error creando fallback: {e}")
            return {
                "respuesta_usuario": "He procesado tu consulta de ayuda. ¿Hay algo específico en lo que pueda ayudarte más?",
                "reflexion_conversacional": {
                    "espera_continuacion": True,
                    "tipo_esperado": "exploracion_funcionalidad",
                    "datos_recordar": {},
                    "razonamiento": "Error en procesamiento - solicitar más información"
                }
            }

    def _extract_basic_info(self, help_content: Dict) -> str:
        """Extrae información básica del contenido para fallback"""
        try:
            if "contenido_principal" in help_content:
                return help_content["contenido_principal"][:200] + "..."
            elif "ejemplos" in help_content and help_content["ejemplos"]:
                return f"Incluye ejemplos como: {', '.join(help_content['ejemplos'][:2])}"
            elif "puntos_clave" in help_content and help_content["puntos_clave"]:
                return f"Puntos clave: {', '.join(help_content['puntos_clave'][:2])}"
            else:
                return "¿Te gustaría que profundice en algún aspecto específico?"

        except Exception:
            return "¿Hay algo específico en lo que pueda ayudarte más?"

    def format_help_response(self, help_content: Dict, response_type: str = "general") -> str:
        """
        Formatea contenido de ayuda en respuesta legible
        Método auxiliar para casos donde no se usa LLM
        """
        try:
            if response_type == "capabilities":
                return self._format_capabilities_response(help_content)
            elif response_type == "tutorial":
                return self._format_tutorial_response(help_content)
            else:
                return self._format_general_response(help_content)

        except Exception as e:
            self.logger.error(f"Error formateando respuesta: {e}")
            return "Información de ayuda procesada. ¿Necesitas más detalles?"

    def _format_capabilities_response(self, content: Dict) -> str:
        """Formatea respuesta de capacidades"""
        response = "🎯 **Capacidades del Sistema:**\n\n"

        if "capacidades_principales" in content:
            response += "**Funcionalidades principales:**\n"
            for cap in content["capacidades_principales"]:
                response += f"• {cap}\n"
            response += "\n"

        if "ejemplos_practicos" in content:
            response += "**Ejemplos prácticos:**\n"
            for ejemplo in content["ejemplos_practicos"]:
                response += f"• {ejemplo}\n"
            response += "\n"

        response += "¿Te gustaría que profundice en alguna funcionalidad específica?"
        return response

    def _format_tutorial_response(self, content: Dict) -> str:
        """Formatea respuesta de tutorial"""
        response = "📚 **Tutorial paso a paso:**\n\n"

        if "pasos" in content:
            for i, paso in enumerate(content["pasos"], 1):
                response += f"{i}. {paso}\n"
            response += "\n"

        response += "¿Necesitas que explique algún paso con más detalle?"
        return response

    def _format_general_response(self, content: Dict) -> str:
        """Formatea respuesta general"""
        response = "ℹ️ **Información de ayuda:**\n\n"

        if "contenido_principal" in content:
            response += f"{content['contenido_principal']}\n\n"

        if "puntos_clave" in content:
            response += "**Puntos importantes:**\n"
            for punto in content["puntos_clave"]:
                response += f"• {punto}\n"

        return response
