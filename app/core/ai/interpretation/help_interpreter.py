"""
Interpretador especializado en consultas de ayuda del sistema
Implementa la filosofía de dominios funcionales con auto-reflexión integrada.

DOMINIO: Sistema de Ayuda
- Explicación de funcionalidades
- Tutoriales paso a paso
- Solución de problemas
- Ejemplos prácticos
- Guías contextuales
"""

from typing import Optional, Dict
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger

# ✅ CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR)
from .help_query.help_content_generator import HelpContentGenerator
from .help_query.help_response_generator import HelpResponseGenerator
from .help_query.tutorial_processor import TutorialProcessor
from .help_query.capability_analyzer import CapabilityAnalyzer
from .utils.json_parser import JSONParser

class HelpInterpreter(BaseInterpreter):
    """Interpretador especializado en consultas de ayuda del sistema"""

    def __init__(self, gemini_client):
        super().__init__("HelpInterpreter")
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # ✅ INICIALIZAR CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR)
        self.help_content_generator = HelpContentGenerator(gemini_client)
        self.help_response_generator = HelpResponseGenerator(gemini_client)
        self.tutorial_processor = TutorialProcessor(gemini_client)
        self.capability_analyzer = CapabilityAnalyzer()
        self.json_parser = JSONParser()

        self.logger.debug("✅ HelpInterpreter inicializado con clases especializadas")

    def _get_supported_actions(self):
        """Acciones soportadas por el intérprete de ayuda"""
        return [
            "ayuda_funcionalidades",
            "ayuda_tutorial",
            "ayuda_ejemplo",
            "ayuda_solucion",
            "ayuda_error"
        ]

    def can_handle(self, context: InterpretationContext) -> bool:
        """El MasterInterpreter ya decidió que somos el intérprete correcto"""
        return True

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        Interpreta consultas de ayuda usando el flujo optimizado de 4 prompts
        ARQUITECTURA: PROMPT 0 → PROMPT 1 → PROMPT 2 → PROMPT 3
        """
        try:
            self.logger.info(f"🆘 HelpInterpreter INICIADO - Consulta: '{context.user_message}'")

            # 🎯 PROMPT 0: VERIFICAR SUB-INTENCIÓN DEL MASTER (PATRÓN OPTIMIZADO)
            intention_info = getattr(context, 'intention_info', {})
            sub_intention = intention_info.get('sub_intention', '')
            detected_entities = intention_info.get('detected_entities', {})

            self.logger.info(f"🎯 INFORMACIÓN DE INTENCIÓN RECIBIDA:")
            self.logger.info(f"   - Sub-intención: {sub_intention}")
            self.logger.info(f"   - Entidades detectadas: {detected_entities}")

            # 🚀 FLUJO DIRECTO USANDO ENTIDADES PRE-DETECTADAS
            if sub_intention == "entender_capacidades":
                self.logger.info("🎯 SUB-INTENCIÓN: ENTENDER CAPACIDADES")
                return self._process_capabilities_help(context.user_message, detected_entities)

            elif sub_intention == "tutorial_paso_a_paso":
                self.logger.info("🎯 SUB-INTENCIÓN: TUTORIAL PASO A PASO")
                return self._process_tutorial_help(context.user_message, detected_entities)

            elif sub_intention == "solucion_problema":
                self.logger.info("🎯 SUB-INTENCIÓN: SOLUCIÓN DE PROBLEMA")
                return self._process_problem_solution(context.user_message, detected_entities)

            elif sub_intention == "ejemplo_practico":
                self.logger.info("🎯 SUB-INTENCIÓN: EJEMPLO PRÁCTICO")
                return self._process_practical_example(context.user_message, detected_entities)

            # 🎯 PROMPT 1: DETECCIÓN DE CONTINUACIÓN (PATRÓN ESTÁNDAR)
            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                self.logger.info("📚 VERIFICANDO PILA CONVERSACIONAL DE AYUDA")
                continuation_info = self._detect_help_continuation(context.user_message, context.conversation_stack)

                if continuation_info and continuation_info.get('es_continuacion', False):
                    self.logger.info(f"✅ CONTINUACIÓN DE AYUDA DETECTADA: {continuation_info.get('tipo_continuacion', 'unknown')}")
                    return self._process_help_continuation(context.user_message, continuation_info, context.conversation_stack)
                else:
                    self.logger.info("❌ NO ES CONTINUACIÓN DE AYUDA")
            else:
                self.logger.info("❌ NO HAY PILA CONVERSACIONAL DE AYUDA disponible")

            # 🎯 PROMPT 2: GENERACIÓN DE CONTENIDO DE AYUDA
            help_content = self._generate_help_content(context.user_message, context)

            if not help_content:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ No pude generar contenido de ayuda para tu consulta. ¿Podrías ser más específico?",
                        "error": "content_generation_failed"
                    },
                    confidence=0.3
                )

            # 🎯 PROMPT 3: RESPUESTA + AUTO-REFLEXIÓN (PATRÓN ESTÁNDAR)
            response_with_reflection = self._validate_and_generate_help_response(
                context.user_message, help_content
            )

            if response_with_reflection:
                # Determinar tipo de acción basado en el contenido
                action_type = self._determine_help_action_type(help_content)

                return InterpretationResult(
                    action=action_type,
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Ayuda generada"),
                        "help_content": help_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "help_interpreter"
                    },
                    confidence=0.9
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ Error generando respuesta de ayuda. Intenta reformular tu pregunta.",
                        "error": "response_generation_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error en HelpInterpreter: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error interno procesando tu consulta de ayuda. Intenta nuevamente.",
                    "error": "internal_error",
                    "exception": str(e)
                },
                confidence=0.1
            )

    def _process_capabilities_help(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa consultas sobre capacidades del sistema usando entidades pre-detectadas"""
        try:
            self.logger.info("🎯 PROCESANDO CAPACIDADES DEL SISTEMA")

            # Usar CapabilityAnalyzer para generar contenido
            capabilities_content = self.capability_analyzer.analyze_system_capabilities(user_query, detected_entities)

            if capabilities_content:
                # Generar respuesta con auto-reflexión
                response_with_reflection = self._validate_and_generate_help_response(user_query, capabilities_content)

                return InterpretationResult(
                    action="ayuda_funcionalidades",
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Funcionalidades del sistema"),
                        "capabilities": capabilities_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "capabilities_direct"
                    },
                    confidence=0.95
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ No pude analizar las capacidades solicitadas",
                        "error": "capabilities_analysis_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando capacidades: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error analizando capacidades del sistema",
                    "error": "capabilities_error"
                },
                confidence=0.1
            )

    def _process_tutorial_help(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa solicitudes de tutoriales paso a paso"""
        try:
            self.logger.info("🎯 PROCESANDO TUTORIAL PASO A PASO")

            # Usar TutorialProcessor para generar tutorial
            tutorial_content = self.tutorial_processor.generate_tutorial(user_query, detected_entities)

            if tutorial_content:
                response_with_reflection = self._validate_and_generate_help_response(user_query, tutorial_content)

                return InterpretationResult(
                    action="ayuda_tutorial",
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Tutorial generado"),
                        "tutorial": tutorial_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "tutorial_direct"
                    },
                    confidence=0.95
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ No pude generar el tutorial solicitado",
                        "error": "tutorial_generation_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando tutorial: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error generando tutorial",
                    "error": "tutorial_error"
                },
                confidence=0.1
            )

    def _process_problem_solution(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa consultas de solución de problemas"""
        # Implementación similar a los métodos anteriores
        # Por ahora, usar el flujo general
        return self._process_general_help(user_query, detected_entities, "solucion_problema")

    def _process_practical_example(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa solicitudes de ejemplos prácticos"""
        # Implementación similar a los métodos anteriores
        # Por ahora, usar el flujo general
        return self._process_general_help(user_query, detected_entities, "ejemplo_practico")

    def _process_general_help(self, user_query: str, detected_entities: Dict, help_type: str) -> InterpretationResult:
        """Procesa consultas generales de ayuda"""
        try:
            self.logger.info(f"🎯 PROCESANDO AYUDA GENERAL: {help_type}")

            # Generar contenido usando HelpContentGenerator
            help_content = self.help_content_generator.generate_content(user_query, help_type, detected_entities)

            if help_content:
                response_with_reflection = self._validate_and_generate_help_response(user_query, help_content)

                action_map = {
                    "solucion_problema": "ayuda_solucion",
                    "ejemplo_practico": "ayuda_ejemplo"
                }

                return InterpretationResult(
                    action=action_map.get(help_type, "ayuda_funcionalidades"),
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Ayuda generada"),
                        "help_content": help_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": f"{help_type}_direct"
                    },
                    confidence=0.9
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": f"❌ No pude generar ayuda para {help_type}",
                        "error": f"{help_type}_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando ayuda general: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error procesando consulta de ayuda",
                    "error": "general_help_error"
                },
                confidence=0.1
            )

    def _detect_help_continuation(self, user_query: str, conversation_stack: list) -> Optional[Dict]:
        """Detecta si la consulta es continuación de ayuda previa"""
        # Por ahora, implementación básica
        # TODO: Implementar detección específica para ayuda
        return {"es_continuacion": False, "tipo_continuacion": "none"}

    def _process_help_continuation(self, user_query: str, continuation_info: Dict, conversation_stack: list) -> InterpretationResult:
        """Procesa continuaciones de ayuda"""
        # Por ahora, implementación básica
        # TODO: Implementar procesamiento de continuaciones
        return InterpretationResult(
            action="ayuda_funcionalidades",
            parameters={
                "message": f"Continuando con ayuda para: {user_query}",
                "origen": "continuation"
            },
            confidence=0.7
        )

    def _generate_help_content(self, user_query: str, context) -> Optional[Dict]:
        """Genera contenido de ayuda usando HelpContentGenerator"""
        try:
            # Determinar tipo de ayuda
            help_type = self._determine_help_type_from_query(user_query)

            # Usar HelpContentGenerator
            return self.help_content_generator.generate_content(user_query, help_type, {})

        except Exception as e:
            self.logger.error(f"Error generando contenido de ayuda: {e}")
            return None

    def _determine_help_type_from_query(self, user_query: str) -> str:
        """Determina el tipo de ayuda basado en la consulta"""
        query_lower = user_query.lower()

        if any(word in query_lower for word in ["problema", "error", "no funciona", "falla"]):
            return "solucion_problema"
        elif any(word in query_lower for word in ["ejemplo", "muestra", "demo"]):
            return "ejemplo_practico"
        elif any(word in query_lower for word in ["tutorial", "cómo", "paso a paso"]):
            return "tutorial_paso_a_paso"
        else:
            return "ayuda_general"

    def _validate_and_generate_help_response(self, user_query: str, help_content: Dict) -> Optional[Dict]:
        """Valida contenido y genera respuesta con auto-reflexión usando HelpResponseGenerator"""
        try:
            return self.help_response_generator.generate_response_with_reflection(user_query, help_content)
        except Exception as e:
            self.logger.error(f"Error generando respuesta de ayuda: {e}")
            return None

    def _determine_help_action_type(self, help_content: Dict) -> str:
        """Determina el tipo de acción basado en el contenido"""
        content_type = help_content.get("tipo_contenido", "ayuda_general")

        action_map = {
            "solucion_problema": "ayuda_solucion",
            "ejemplo_practico": "ayuda_ejemplo",
            "tutorial_paso_a_paso": "ayuda_tutorial",
            "ayuda_general": "ayuda_funcionalidades"
        }

        return action_map.get(content_type, "ayuda_funcionalidades")