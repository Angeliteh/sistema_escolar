"""
Generador de respuestas de ayuda con auto-reflexión
Especializado en crear respuestas naturales y contextuales
🆕 AHORA USA HelpPromptManager centralizado
"""

from typing import Dict, Optional
from app.core.logging import get_logger
from app.core.ai.prompts.help_prompt_manager import HelpPromptManager
from app.core.ai.interpretation.utils.json_parser import JSONParser

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
        # 🛠️ USAR JSONParser CENTRALIZADO COMO STUDENT INTERPRETER
        self.json_parser = JSONParser()

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
                self.logger.info(f"🔍 Respuesta cruda del LLM: {response[:200]}...")

                # 🛠️ PARSEAR JSON MANUALMENTE CON LIMPIEZA DE ESCAPES
                try:
                    import json
                    import re

                    # Buscar el JSON en la respuesta
                    start = response.find('{')
                    end = response.rfind('}') + 1

                    if start >= 0 and end > start:
                        json_str = response[start:end]

                        # 🧹 LIMPIAR ESCAPES PROBLEMÁTICOS
                        # Reemplazar escapes inválidos comunes
                        json_str = json_str.replace('\\"', '"')  # Comillas escapadas
                        json_str = re.sub(r'\\(?!["\\/bfnrt])', r'\\\\', json_str)  # Escapes inválidos

                        response_data = json.loads(json_str)
                        self.logger.info(f"🔧 JSON parseado manualmente exitosamente")
                    else:
                        self.logger.warning("🔧 No se encontró JSON válido en la respuesta")
                        response_data = None
                except Exception as e:
                    self.logger.warning(f"🔧 Error parseando JSON manualmente: {e}")
                    # 🔄 INTENTAR EXTRAER SOLO EL MENSAJE PRINCIPAL CON REGEX MEJORADO
                    try:
                        # 🎯 REGEX MEJORADO PARA CAPTURAR MENSAJES LARGOS CON SALTOS DE LÍNEA
                        # Buscar desde "respuesta_usuario": hasta el siguiente campo o final
                        pattern = r'"respuesta_usuario":\s*"((?:[^"\\]|\\.)*)"\s*(?:,|\})'
                        match = re.search(pattern, response, re.DOTALL)

                        if match:
                            mensaje = match.group(1)
                            # 🧹 LIMPIAR ESCAPES EN EL MENSAJE
                            mensaje = mensaje.replace('\\"', '"')
                            mensaje = mensaje.replace('\\n', '\n')
                            mensaje = mensaje.replace('\\t', '\t')
                            mensaje = mensaje.replace('\\\\', '\\')

                            response_data = {"respuesta_usuario": mensaje}
                            self.logger.info("🔧 Mensaje extraído directamente con regex mejorado")
                            self.logger.info(f"📏 Longitud del mensaje: {len(mensaje)} caracteres")
                        else:
                            self.logger.warning("🔧 No se pudo extraer mensaje con regex")
                            # Fallback al JSONParser original
                            response_data = self.json_parser.parse_llm_response(response)
                    except Exception as e2:
                        self.logger.warning(f"🔧 Error en extracción con regex: {e2}")
                        response_data = self.json_parser.parse_llm_response(response)

                if response_data:
                    self.logger.info("✅ Respuesta con auto-reflexión generada exitosamente")
                    self.logger.info(f"🔍 Claves en response_data: {list(response_data.keys())}")
                    self.logger.info(f"📝 Mensaje generado: {response_data.get('respuesta_usuario', 'N/A')[:100]}...")

                    # 🛠️ VERIFICAR SI EL MENSAJE ESTÁ EN OTRA CLAVE
                    if not response_data.get('respuesta_usuario'):
                        self.logger.warning("⚠️ Campo 'respuesta_usuario' vacío o ausente")
                        self.logger.info(f"🔍 Contenido completo: {response_data}")

                    return response_data
                else:
                    self.logger.warning("❌ No se pudo parsear respuesta con auto-reflexión")
                    self.logger.info(f"🔍 Respuesta que falló al parsear: {response}")
                    return self._create_fallback_response(user_query, help_content)
            else:
                self.logger.warning("❌ No hay respuesta del LLM")
                return self._create_fallback_response(user_query, help_content)

        except Exception as e:
            self.logger.error(f"Error generando respuesta: {e}")
            return self._create_fallback_response(user_query, help_content)

    def _create_fallback_response(self, user_query: str, help_content: Dict) -> Dict:
        """Crea respuesta de fallback cuando el LLM falla"""
        try:
            # Extraer información básica del contenido
            content_type = help_content.get("tipo_contenido", "ayuda_general")

            # 🛠️ GENERAR RESPUESTA COMPLETA USANDO EL CONTENIDO DISPONIBLE
            basic_info = self._extract_basic_info(help_content)

            if content_type == "solucion_problema":
                fallback_message = f"He analizado tu consulta sobre problemas.\n\n{basic_info}"
            elif content_type == "ejemplo_practico":
                fallback_message = f"Aquí tienes ejemplos prácticos para tu consulta.\n\n{basic_info}"
            else:
                # Para ayuda general, usar directamente el contenido principal
                fallback_message = basic_info if basic_info and len(basic_info) > 50 else f"Hola! Soy tu asistente inteligente de la escuela primaria \"PROF. MAXIMO GAMIZ FERNANDEZ\". Puedo ayudarte con consultas de alumnos, generar constancias y más. {basic_info}"

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
                return help_content["contenido_principal"]  # 🛠️ SIN TRUNCAR
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
