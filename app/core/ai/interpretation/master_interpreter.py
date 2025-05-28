"""
Intérprete maestro - Coordina todos los módulos de interpretación
"""
from typing import Optional
from app.core.ai.interpretation.base_interpreter import InterpretationContext, InterpretationResult
from app.core.ai.interpretation.intention_detector import IntentionDetector
from app.core.ai.interpretation.student_query_interpreter import StudentQueryInterpreter
from app.core.logging import get_logger
from app.core.config import Config

class MasterInterpreter:
    """Intérprete maestro que coordina todos los módulos especializados"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # Inicializar detector de intención maestro
        self.intention_detector = IntentionDetector(gemini_client)

        # Inicializar intérpretes especializados
        # Obtener la ruta de la base de datos desde la configuración
        from app.core.config import Config
        db_path = Config.DB_PATH

        self.student_interpreter = StudentQueryInterpreter(db_path, gemini_client)

        # Inicializar intérprete de ayuda
        from app.core.ai.interpretation.help_interpreter import HelpInterpreter
        self.help_interpreter = HelpInterpreter(gemini_client)



        # 🆕 SOLO INTÉRPRETES IMPLEMENTADOS (sin placeholders)

    def interpret(self, context: InterpretationContext, conversation_stack=None) -> Optional[InterpretationResult]:
        """
        Interpreta la consulta usando el flujo modular con análisis contextual + pila conversacional
        """
        try:
            self.logger.debug(f"Iniciando interpretación maestro para: '{context.user_message}'")

            # NUEVO: Agregar pila conversacional al contexto si está disponible
            if conversation_stack is not None:
                context.conversation_stack = conversation_stack
                self.logger.debug(f"Pila conversacional agregada al contexto: {len(conversation_stack)} niveles")

            # NUEVO: PASO 1 - Análisis contextual usando Context Manager
            # Nota: El análisis contextual ahora se hace en el Context Manager
            # antes de llegar aquí, por lo que este código se simplifica

            # Si el contexto tiene información de continuación, manejarla
            conversation_state = getattr(context, 'conversation_state', {})
            if conversation_state.get('waiting_for'):
                # Verificar si el mensaje actual es una respuesta esperada
                contextual_result = self._handle_expected_response(context, conversation_state)
                if contextual_result:
                    return contextual_result

            # PASO 2: Detectar intención global CON CONTEXTO CONVERSACIONAL
            intention = self.intention_detector.detect_intention(context.user_message, conversation_stack)

            self.logger.debug(f"Intención detectada: {intention.intention_type} | Sub-intención: {intention.sub_intention} (confianza: {intention.confidence})")
            self.logger.debug(f"Razonamiento: {intention.reasoning}")
            self.logger.debug(f"Entidades detectadas: {intention.detected_entities}")

            # 🆕 AGREGAR INFORMACIÓN DE INTENCIÓN AL CONTEXTO
            context.intention_info = {
                'intention_type': intention.intention_type,
                'sub_intention': intention.sub_intention,
                'detected_entities': intention.detected_entities,
                'confidence': intention.confidence
            }

            # PASO 3: Dirigir al intérprete especializado
            if intention.intention_type == "consulta_alumnos":
                self.logger.info(f"🎯 [MASTER] Dirigiendo a StudentQueryInterpreter")
                self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
                self.logger.info(f"   └── Entidades: {len(intention.detected_entities)} detectadas")

                result = self.student_interpreter.interpret(context)
                self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")
                return result



            elif intention.intention_type == "generar_constancia":
                self.logger.info("🎯 [MASTER] Dirigiendo a StudentQueryInterpreter (constancia)")
                self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
                self.logger.info(f"   └── Entidades: {len(intention.detected_entities)} detectadas")

                result = self.student_interpreter.interpret(context)
                self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")
                return result

            elif intention.intention_type == "transformacion_pdf":
                self.logger.debug("Dirigiendo a intérprete de transformación PDF")
                # Usar el StudentQueryInterpreter para manejar transformaciones
                # ya que tiene la lógica para detectar parámetros de constancias
                return self.student_interpreter.interpret(context)

            elif intention.intention_type == "ayuda_sistema":
                self.logger.debug("Dirigiendo a intérprete de ayuda")
                return self.help_interpreter.interpret(context)

            elif intention.intention_type == "conversacion_general":
                self.logger.debug("Dirigiendo a chat general")
                # 🔧 ARREGLADO: No hay general_interpreter, usar respuesta directa
                return InterpretationResult(
                    action="conversacion_general",
                    parameters={
                        "mensaje": "Hola, soy tu asistente del sistema escolar. Estoy aquí para ayudarte con consultas sobre alumnos y gestión académica. ¿En qué puedo ayudarte?",
                        "tipo_solicitado": "conversacion_general"
                    },
                    confidence=0.7
                )

            else:
                # Fallback a conversación general
                self.logger.info("Intención no reconocida, usando fallback")
                return InterpretationResult(
                    action="conversacion_general",
                    parameters={
                        "mensaje": "No estoy seguro de cómo ayudarte con eso. Puedo ayudarte con consultas sobre alumnos, como buscar estudiantes o generar constancias. ¿Podrías reformular tu pregunta?",
                        "tipo_solicitado": "fallback"
                    },
                    confidence=Config.INTERPRETATION['confidence_thresholds']['medium']
                )

        except Exception as e:
            self.logger.error(f"Error en intérprete maestro: {e}")
            return InterpretationResult(
                action="error_sistema",
                parameters={
                    "mensaje": Config.RESPONSES['error_messages']['system_error'],
                    "error": str(e)
                },
                confidence=Config.INTERPRETATION['confidence_thresholds']['fallback']
            )

    def _handle_expected_response(self, context: InterpretationContext, conversation_state: dict) -> Optional[InterpretationResult]:
        """
        Maneja respuestas esperadas basadas en el estado conversacional
        Versión simplificada que usa el Context Manager
        """
        waiting_for = conversation_state.get('waiting_for')
        user_message = context.user_message.lower().strip()

        # 🆕 DETECTAR CONFIRMACIONES DESDE CONFIGURACIÓN CENTRALIZADA
        confirmations = Config.RESPONSES['confirmation_words']

        if waiting_for == "confirmacion_constancia_estudios" and user_message in confirmations:
            return self._handle_confirmation(context, conversation_state)

        # Aquí se pueden agregar otros tipos de respuestas esperadas
        # elif waiting_for == "seleccion_alumno":
        #     return self._handle_selection(context, conversation_state)

        return None

    def _handle_confirmation(self, context: InterpretationContext, conversation_state: dict) -> Optional[InterpretationResult]:
        """
        Maneja confirmaciones del usuario para diferentes tipos de acciones pendientes
        """
        waiting_for = conversation_state.get('waiting_for')
        context_data = conversation_state.get('context_data', {})

        if waiting_for == "confirmacion_constancia_estudios":
            # Usuario confirmó generar constancia de estudios como alternativa
            alumno_nombre = context_data.get('alumno')
            if alumno_nombre:
                self.logger.info(f"Confirmación recibida: generar constancia de estudios para {alumno_nombre}")

                # Crear consulta para generar constancia de estudios
                constancia_query = f"generar constancia de estudios para {alumno_nombre}"
                new_context = InterpretationContext(user_message=constancia_query)
                return self.student_interpreter.interpret(new_context)

        # Aquí se pueden agregar otros tipos de confirmación:
        # elif waiting_for == "confirmacion_eliminar_alumno":
        #     return self._handle_delete_confirmation(context_data)
        # elif waiting_for == "confirmacion_actualizar_datos":
        #     return self._handle_update_confirmation(context_data)

        return None

    def _handle_clarification(self, context: InterpretationContext, conversation_state: dict) -> Optional[InterpretationResult]:
        """Maneja solicitudes de aclaración del usuario"""
        return self.student_interpreter.interpret(context)

    def _handle_selection(self, context: InterpretationContext, conversation_state: dict) -> Optional[InterpretationResult]:
        """Maneja selecciones del usuario cuando hay múltiples opciones"""
        return self.student_interpreter.interpret(context)

    def _handle_related_question(self, context: InterpretationContext, conversation_state: dict) -> Optional[InterpretationResult]:
        """Maneja preguntas relacionadas al contexto actual de la conversación"""
        if self.help_interpreter:
            return self.help_interpreter.interpret(context)
        return self.student_interpreter.interpret(context)

    def get_available_modules(self) -> dict:
        """Retorna información sobre los módulos disponibles"""
        return {
            "consulta_alumnos": {
                "disponible": True,
                "descripcion": "Consultas sobre información de estudiantes",
                "ejemplos": ["cuántos alumnos hay", "buscar a Juan", "alumnos de 3er grado"]
            },
            "transformacion_pdf": {
                "disponible": True,
                "descripcion": "Transformación de constancias entre formatos",
                "ejemplos": ["convertir constancia", "cambiar formato PDF", "transformar a estudios"]
            },
            "ayuda_sistema": {
                "disponible": True,
                "descripcion": "Ayuda sobre el uso del sistema",
                "ejemplos": ["cómo usar el sistema", "qué puedo hacer", "ayuda con consultas"]
            },
            "conversacion_general": {
                "disponible": False,
                "descripcion": "Chat general y conversación casual",
                "ejemplos": ["hola", "¿cómo estás?"]
            }
        }
