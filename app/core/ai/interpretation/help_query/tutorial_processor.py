"""
Procesador de tutoriales paso a paso
Especializado en generar guías detalladas
🆕 AHORA USA HelpPromptManager centralizado
"""

from typing import Dict, Any, Optional, List
from app.core.logging import get_logger
from app.core.ai.prompts.help_prompt_manager import HelpPromptManager

class TutorialProcessor:
    """
    Clase especializada en generar tutoriales paso a paso
    🆕 PROMPTS CENTRALIZADOS en HelpPromptManager
    """

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.prompt_manager = HelpPromptManager()  # 🆕 PROMPT MANAGER CENTRALIZADO
        self.tutorial_templates = self._load_tutorial_templates()

    def generate_tutorial(self, user_query: str, detected_entities: Dict) -> Optional[Dict]:
        """
        Genera tutorial paso a paso usando LLM

        Args:
            user_query: Consulta original del usuario
            detected_entities: Entidades detectadas

        Returns:
            Dict con el tutorial generado
        """
        try:
            self.logger.debug(f"Generando tutorial para: {user_query}")

            # Determinar tipo de tutorial
            tutorial_type = self._determine_tutorial_type(user_query, detected_entities)

            # Generar tutorial usando LLM
            tutorial_content = self._generate_tutorial_with_llm(user_query, tutorial_type, detected_entities)

            if tutorial_content:
                self.logger.debug(f"Tutorial generado: {tutorial_type}")
                return tutorial_content
            else:
                # Fallback a template predefinido
                self.logger.info("Usando template predefinido como fallback")
                return self._get_template_tutorial(tutorial_type)

        except Exception as e:
            self.logger.error(f"Error generando tutorial: {e}")
            return None

    def _determine_tutorial_type(self, user_query: str, detected_entities: Dict) -> str:
        """Determina qué tipo de tutorial necesita el usuario"""
        query_lower = user_query.lower()

        # Mapeo de palabras clave a tipos de tutorial
        tutorial_keywords = {
            "consultas": ["consultar", "buscar", "alumnos", "estudiantes", "información"],
            "constancias": ["constancia", "documento", "certificado", "generar", "crear"],
            "sistema": ["usar", "funciona", "sistema", "empezar", "comenzar"],
            "navegacion": ["interfaz", "chat", "navegar", "usar"],
            "ejemplos": ["ejemplo", "muestra", "demo", "práctica"]
        }

        # Buscar coincidencias
        for tutorial_type, keywords in tutorial_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return tutorial_type

        # Default
        return "sistema"

    def _generate_tutorial_with_llm(self, user_query: str, tutorial_type: str, detected_entities: Dict) -> Optional[Dict]:
        """Genera tutorial usando LLM"""
        try:
            # 🆕 USAR PROMPT MANAGER CENTRALIZADO
            tutorial_prompt = self.prompt_manager.get_tutorial_prompt(user_query, tutorial_type, detected_entities)

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(tutorial_prompt)

            if response:
                # Parsear respuesta
                tutorial_data = self._parse_tutorial_response(response)
                return tutorial_data
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error con LLM en tutorial: {e}")
            return None

    # 🗑️ MÉTODO ELIMINADO: _build_tutorial_prompt()
    # RAZÓN: Duplicado - ya existe versión centralizada en HelpPromptManager
    # USO: self.prompt_manager.get_tutorial_prompt()

    # 🗑️ MÉTODO ELIMINADO: _get_tutorial_examples()
    # RAZÓN: Duplicado - ya existe versión centralizada en HelpPromptManager
    # USO: self.prompt_manager._get_tutorial_examples()

    def _parse_tutorial_response(self, response: str) -> Optional[Dict]:
        """Parsea la respuesta del tutorial del LLM"""
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
                        tutorial_data = json.loads(matches[0])

                        # Validar estructura mínima
                        if "pasos" in tutorial_data and tutorial_data["pasos"]:
                            self.logger.debug("Tutorial parseado exitosamente")
                            return tutorial_data
                        else:
                            self.logger.warning("Tutorial no tiene estructura válida")
                            continue

                    except json.JSONDecodeError:
                        continue

            self.logger.warning(f"No se pudo parsear tutorial: {clean_response[:100]}...")
            return None

        except Exception as e:
            self.logger.error(f"Error parseando tutorial: {e}")
            return None

    def _get_template_tutorial(self, tutorial_type: str) -> Dict:
        """Obtiene tutorial predefinido como fallback"""
        return self.tutorial_templates.get(tutorial_type, self.tutorial_templates["sistema"])

    def _load_tutorial_templates(self) -> Dict:
        """Carga templates predefinidos de tutoriales"""
        return {
            "consultas": {
                "tipo_tutorial": "consultas",
                "titulo": "Cómo hacer consultas de alumnos",
                "descripcion": "Aprende a buscar información de estudiantes usando lenguaje natural",
                "pasos": [
                    {
                        "numero": 1,
                        "titulo": "Escribe tu consulta",
                        "descripcion": "Describe qué información necesitas en español natural",
                        "ejemplo": "cuántos alumnos hay en total",
                        "consejos": ["Usa palabras simples", "No necesitas comandos técnicos"]
                    },
                    {
                        "numero": 2,
                        "titulo": "Revisa la respuesta",
                        "descripcion": "El sistema te dará la información solicitada",
                        "ejemplo": "Respuesta: 211 alumnos registrados",
                        "consejos": ["Lee toda la información", "Puedes hacer preguntas de seguimiento"]
                    }
                ],
                "ejemplos_completos": [
                    {
                        "titulo": "Buscar alumno específico",
                        "descripcion": "Encontrar información de un estudiante",
                        "pasos_ejemplo": ["Escribir: buscar García", "Ver lista de resultados", "Seleccionar alumno específico"]
                    }
                ],
                "problemas_comunes": [
                    {
                        "problema": "No encuentra al alumno",
                        "solucion": "Verifica la ortografía o usa solo el apellido"
                    }
                ],
                "consejos_adicionales": ["Puedes combinar criterios", "Usa referencias como 'del segundo'"],
                "siguientes_pasos": ["Probar consultas más específicas", "Generar constancias para alumnos encontrados"]
            },
            "constancias": {
                "tipo_tutorial": "constancias",
                "titulo": "Cómo generar constancias",
                "descripcion": "Aprende a crear documentos oficiales para estudiantes",
                "pasos": [
                    {
                        "numero": 1,
                        "titulo": "Busca al alumno",
                        "descripcion": "Primero encuentra al estudiante específico",
                        "ejemplo": "buscar Juan Pérez",
                        "consejos": ["Usa nombre completo si es posible", "Verifica que sea el alumno correcto"]
                    },
                    {
                        "numero": 2,
                        "titulo": "Solicita la constancia",
                        "descripcion": "Especifica el tipo de constancia necesaria",
                        "ejemplo": "constancia de estudios para Juan Pérez",
                        "consejos": ["Especifica el tipo: estudios, calificaciones, traslado", "Menciona si necesita foto"]
                    }
                ],
                "ejemplos_completos": [
                    {
                        "titulo": "Constancia completa",
                        "descripcion": "Proceso completo de generación",
                        "pasos_ejemplo": ["Buscar alumno", "Solicitar constancia", "Revisar vista previa", "Descargar PDF"]
                    }
                ],
                "problemas_comunes": [
                    {
                        "problema": "Alumno sin calificaciones",
                        "solucion": "Solo se pueden generar constancias de estudios"
                    }
                ],
                "consejos_adicionales": ["Revisa siempre la vista previa", "Guarda el PDF en lugar seguro"],
                "siguientes_pasos": ["Generar más constancias", "Explorar otros tipos de documentos"]
            },
            "sistema": {
                "tipo_tutorial": "sistema",
                "titulo": "Cómo usar el sistema",
                "descripcion": "Guía básica para empezar a usar el sistema escolar",
                "pasos": [
                    {
                        "numero": 1,
                        "titulo": "Entiende la interfaz",
                        "descripcion": "El sistema funciona como un chat conversacional",
                        "ejemplo": "Escribe preguntas en español normal",
                        "consejos": ["No uses comandos técnicos", "Habla como si fuera una persona"]
                    },
                    {
                        "numero": 2,
                        "titulo": "Haz tu primera consulta",
                        "descripcion": "Prueba con una consulta simple",
                        "ejemplo": "cuántos alumnos hay",
                        "consejos": ["Empieza con consultas simples", "Lee las respuestas completas"]
                    }
                ],
                "ejemplos_completos": [
                    {
                        "titulo": "Primera sesión",
                        "descripcion": "Qué hacer en tu primera vez",
                        "pasos_ejemplo": ["Hacer consulta simple", "Probar búsqueda", "Pedir ayuda específica"]
                    }
                ],
                "problemas_comunes": [
                    {
                        "problema": "No entiendo la respuesta",
                        "solucion": "Pide que te explique con más detalle"
                    }
                ],
                "consejos_adicionales": ["Experimenta con diferentes consultas", "Pide ayuda cuando la necesites"],
                "siguientes_pasos": ["Explorar consultas de alumnos", "Aprender a generar constancias"]
            }
        }
