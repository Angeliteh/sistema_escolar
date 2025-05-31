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
    """
    🎯 INTÉRPRETE MAESTRO - LÍDER INTELIGENTE DEL SISTEMA

    RESPONSABILIDADES:
    - Detectar intenciones con contexto estratégico completo
    - Dirigir al especialista correcto con información precisa
    - Mantener memoria de interacciones para retroalimentación
    - Comunicación bidireccional con especialistas
    """

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # 🎯 CONTEXTO ESTRATÉGICO DEL SISTEMA (SEGÚN INTENCIONES_ACCIONES_DEFINITIVAS.md)
        self.system_map = {
            "StudentQueryInterpreter": {
                "handles": ["consulta_alumnos"],
                "sub_intentions": ["busqueda_simple", "busqueda_compleja", "estadisticas", "generar_constancia", "transformacion_pdf"],
                "capabilities": "Consultas de BD, documentos, análisis de 211 alumnos",
                "description": "Especialista en datos de alumnos y generación de documentos"
            },
            "HelpInterpreter": {
                "handles": ["ayuda_sistema"],
                "sub_intentions": ["pregunta_capacidades", "pregunta_tecnica"],
                "capabilities": "Ayuda y soporte técnico del sistema",
                "description": "Especialista en ayuda y explicaciones del sistema"
            }
        }

        # 💭 MEMORIA DE INTERACCIONES (RETROALIMENTACIÓN)
        self.interaction_memory = {
            "last_specialist": None,
            "last_result_summary": None,
            "conversation_flow": None,
            "specialist_feedback": None,
            "awaiting_continuation": False,
            "continuation_type": None
        }

        # 🔧 INICIALIZAR COMPONENTES
        self.intention_detector = IntentionDetector(gemini_client)

        # 🎯 LOGS DE DEPURACIÓN FORZADOS - CONTEXTO ESTRATÉGICO COMPLETO
        self.logger.info("🎯 [MASTER] INICIALIZADO CON CONTEXTO ESTRATÉGICO")
        self.logger.info(f"   ├── Especialistas disponibles: {len(self.system_map)}")
        self.logger.info(f"   ├── StudentQueryInterpreter: {self.system_map['StudentQueryInterpreter']['capabilities']}")
        self.logger.info(f"   └── HelpInterpreter: {self.system_map['HelpInterpreter']['capabilities']}")

        # 🔍 DEBUG DETALLADO DEL CONTEXTO ESTRATÉGICO
        # Puedes cambiar esto a False para desactivar logs detallados
        self.debug_detailed_context = True
        if self.debug_detailed_context:
            self._log_detailed_strategic_context()

        # 🎯 INICIALIZAR ESPECIALISTAS (DESPUÉS DE MOSTRAR CONTEXTO MASTER)
        self.logger.info("🎯 [MASTER] Inicializando especialistas...")
        from app.core.config import Config
        db_path = Config.DB_PATH
        self.student_interpreter = StudentQueryInterpreter(db_path, gemini_client)

        from app.core.ai.interpretation.help_interpreter import HelpInterpreter
        self.help_interpreter = HelpInterpreter(gemini_client)
        self.logger.info("✅ [MASTER] Especialistas inicializados correctamente")

    def interpret(self, context: InterpretationContext, conversation_stack=None) -> Optional[InterpretationResult]:
        """
        🎯 INTERPRETACIÓN MAESTRO CON CONTEXTO ESTRATÉGICO COMPLETO

        FLUJO MEJORADO:
        1. Análisis con contexto estratégico completo
        2. Detección de intención con memoria de interacciones
        3. Delegación inteligente al especialista correcto
        4. Comunicación bidireccional y retroalimentación
        """
        try:
            # 🎯 LOGS DE DEPURACIÓN FORZADOS
            self.logger.info("🎯 [MASTER] INICIANDO INTERPRETACIÓN CON CONTEXTO ESTRATÉGICO")
            self.logger.info(f"   ├── Consulta: '{context.user_message}'")
            self.logger.info(f"   ├── Conversation_stack: {len(conversation_stack) if conversation_stack else 0} niveles")
            self.logger.info(f"   └── Memoria anterior: {self.interaction_memory}")

            # PASO 1: PREPARAR CONTEXTO ESTRATÉGICO COMPLETO
            strategic_context = self._prepare_strategic_context(context, conversation_stack)
            self.logger.info(f"🧠 [MASTER] Contexto estratégico preparado: {len(strategic_context)} elementos")

            # PASO 2: DETECTAR INTENCIÓN CON CONTEXTO ESTRATÉGICO
            intention = self._detect_intention_with_strategic_context(
                context.user_message, conversation_stack, strategic_context
            )

            # 🎯 LOGS DE DEPURACIÓN DE INTENCIÓN
            self.logger.info(f"🎯 [MASTER] INTENCIÓN DETECTADA:")
            self.logger.info(f"   ├── Tipo: {intention.intention_type}")
            self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
            self.logger.info(f"   ├── Confianza: {intention.confidence}")
            self.logger.info(f"   └── Razonamiento: {intention.reasoning}")

            # PASO 3: VALIDAR INTENCIÓN CON SISTEMA MAP
            validated_intention = self._validate_intention_with_system_map(intention)
            if validated_intention != intention:
                self.logger.info(f"🔧 [MASTER] Intención corregida por system_map")

            # PASO 4: DIRIGIR AL ESPECIALISTA CON CONTEXTO COMPLETO
            result = self._delegate_to_specialist_with_context(
                context, validated_intention, strategic_context
            )

            # PASO 5: PROCESAR RETROALIMENTACIÓN DEL ESPECIALISTA
            self._process_specialist_feedback(validated_intention, result)

            return result

        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error en interpretación: {e}")
            return None

    def _prepare_strategic_context(self, context: InterpretationContext, conversation_stack) -> dict:
        """🎯 PREPARAR CONTEXTO ESTRATÉGICO COMPLETO"""
        try:
            # Agregar conversation_stack al contexto
            if conversation_stack is not None:
                context.conversation_stack = conversation_stack

            strategic_context = {
                "system_map": self.system_map,
                "interaction_memory": self.interaction_memory,
                "conversation_stack": conversation_stack or [],
                "available_specialists": list(self.system_map.keys())
            }

            self.logger.info(f"🧠 [MASTER] Contexto estratégico incluye:")
            self.logger.info(f"   ├── System map: {len(self.system_map)} especialistas")
            self.logger.info(f"   ├── Memoria: {bool(self.interaction_memory.get('last_specialist'))}")
            self.logger.info(f"   └── Stack conversacional: {len(conversation_stack) if conversation_stack else 0}")

            return strategic_context

        except Exception as e:
            self.logger.error(f"❌ Error preparando contexto estratégico: {e}")
            return {"system_map": self.system_map}

    def _detect_intention_with_strategic_context(self, user_message: str, conversation_stack, strategic_context: dict):
        """🎯 DETECTAR INTENCIÓN CON CONTEXTO ESTRATÉGICO"""
        try:
            # Usar el detector existente pero con contexto mejorado
            intention = self.intention_detector.detect_intention(user_message, conversation_stack)

            # 🎯 FORZAR LOGS DE DEPURACIÓN
            self.logger.info(f"🔍 [MASTER] Detector original devolvió:")
            self.logger.info(f"   ├── Intención: {intention.intention_type}")
            self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
            self.logger.info(f"   └── Confianza: {intention.confidence}")

            return intention

        except Exception as e:
            self.logger.error(f"❌ Error en detección de intención: {e}")
            # Fallback básico
            from app.core.ai.interpretation.intention_detector import IntentionResult
            return IntentionResult(
                intention_type="conversacion_general",
                sub_intention="chat_casual",
                confidence=0.1,
                reasoning=f"Error en detección: {e}",
                detected_entities={}
            )

    def _validate_intention_with_system_map(self, intention):
        """🎯 VALIDAR INTENCIÓN CON SYSTEM MAP"""
        try:
            intention_type = intention.intention_type

            # Verificar si la intención es manejada por algún especialista
            for specialist, config in self.system_map.items():
                if intention_type in config["handles"]:
                    self.logger.info(f"✅ [MASTER] Intención '{intention_type}' validada para {specialist}")
                    return intention

            # Si no se encuentra, log de advertencia pero continuar
            self.logger.warning(f"⚠️ [MASTER] Intención '{intention_type}' no encontrada en system_map")
            return intention

        except Exception as e:
            self.logger.error(f"❌ Error validando intención: {e}")
            return intention

    def _delegate_to_specialist_with_context(self, context: InterpretationContext, intention, strategic_context: dict):
        """🎯 DELEGAR AL ESPECIALISTA CON CONTEXTO COMPLETO"""
        try:
            # Agregar información de intención al contexto
            context.intention_info = {
                'intention_type': intention.intention_type,
                'sub_intention': intention.sub_intention,
                'confidence': intention.confidence,
                'reasoning': intention.reasoning,
                'detected_entities': intention.detected_entities
            }

            # 🎯 DEBUG ESTRATÉGICO: LO QUE MASTER ENVÍA A STUDENT
            self.logger.info("=" * 60)
            self.logger.info("🎯 [DEBUG] MASTER → STUDENT COMMUNICATION:")
            self.logger.info("=" * 60)
            self.logger.info(f"📤 CONSULTA ORIGINAL: '{context.user_message}'")
            self.logger.info(f"📤 INTENCIÓN DETECTADA: {intention.intention_type}/{intention.sub_intention}")
            self.logger.info(f"📤 CONFIANZA: {intention.confidence}")
            self.logger.info(f"📤 ENTIDADES DETECTADAS: {len(intention.detected_entities)} elementos")
            for key, value in intention.detected_entities.items():
                self.logger.info(f"     ├── {key}: {value}")
            self.logger.info(f"📤 RAZONAMIENTO MASTER: {intention.reasoning}")
            self.logger.info("=" * 60)

            # Dirigir según la intención
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
                self.logger.info("🎯 [MASTER] Dirigiendo a StudentQueryInterpreter (transformación PDF)")
                self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
                self.logger.info(f"   └── Entidades: {len(intention.detected_entities)} detectadas")

                result = self.student_interpreter.interpret(context)
                self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")
                return result

            elif intention.intention_type == "ayuda_sistema":
                self.logger.info("🎯 [MASTER] Dirigiendo a HelpInterpreter")
                return self.help_interpreter.interpret(context)

            else:
                # Fallback a conversación general
                self.logger.info(f"🎯 [MASTER] Intención no reconocida: {intention.intention_type}")
                return InterpretationResult(
                    action="conversacion_general",
                    parameters={
                        "mensaje": "No estoy seguro de cómo ayudarte con eso. Puedo ayudarte con consultas sobre alumnos, como buscar estudiantes o generar constancias. ¿Podrías reformular tu pregunta?",
                        "tipo_solicitado": "fallback"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"❌ Error delegando al especialista: {e}")
            return None

    def _process_specialist_feedback(self, intention, result):
        """🎯 PROCESAR RETROALIMENTACIÓN DEL ESPECIALISTA"""
        try:
            if result:
                # Actualizar memoria de interacciones
                self.interaction_memory.update({
                    "last_specialist": self._get_specialist_for_intention(intention.intention_type),
                    "last_result_summary": f"Acción: {result.action}",
                    "conversation_flow": f"{intention.intention_type} → {result.action}",
                    "specialist_feedback": "Completado exitosamente",
                    "awaiting_continuation": getattr(result, 'awaiting_continuation', False),
                    "continuation_type": getattr(result, 'continuation_type', None)
                })

                self.logger.info(f"🔄 [MASTER] Memoria actualizada:")
                self.logger.info(f"   ├── Especialista: {self.interaction_memory['last_specialist']}")
                self.logger.info(f"   ├── Resultado: {self.interaction_memory['last_result_summary']}")
                self.logger.info(f"   └── Flujo: {self.interaction_memory['conversation_flow']}")
            else:
                self.logger.warning(f"⚠️ [MASTER] No se recibió resultado del especialista")

        except Exception as e:
            self.logger.error(f"❌ Error procesando retroalimentación: {e}")

    def _get_specialist_for_intention(self, intention_type: str) -> str:
        """🎯 OBTENER ESPECIALISTA PARA INTENCIÓN"""
        for specialist, config in self.system_map.items():
            if intention_type in config["handles"]:
                return specialist
        return "Unknown"

    def _log_detailed_strategic_context(self):
        """🔍 MOSTRAR CONTEXTO ESTRATÉGICO COMPLETO EN LOGS"""
        try:
            self.logger.info("=" * 80)
            self.logger.info("🔍 [MASTER] CONTEXTO ESTRATÉGICO DETALLADO:")
            self.logger.info("=" * 80)

            # 1. SYSTEM MAP COMPLETO
            self.logger.info("📋 1. SYSTEM MAP (Especialistas y Capacidades):")
            for specialist, config in self.system_map.items():
                self.logger.info(f"   🎯 {specialist}:")
                self.logger.info(f"      ├── Rol: {config.get('description', 'No definido')}")
                self.logger.info(f"      ├── Maneja: {config.get('handles', [])}")
                self.logger.info(f"      ├── Sub-intenciones: {config.get('sub_intentions', [])}")
                self.logger.info(f"      └── Capacidades: {config.get('capabilities', 'No definidas')}")

            # 2. MEMORIA DE INTERACCIONES
            self.logger.info("")
            self.logger.info("💭 2. MEMORIA DE INTERACCIONES:")
            for key, value in self.interaction_memory.items():
                self.logger.info(f"      ├── {key}: {value}")

            # 3. CONTEXTO DEL SISTEMA ESCOLAR
            sistema_context = {
                "tipo": "Dirección de Escuela Primaria PROF. MAXIMO GAMIZ FERNANDEZ",
                "estudiantes_total": 211,
                "areas_disponibles": ["Consultas de Alumnos", "Ayuda Técnica"]
            }
            self.logger.info("")
            self.logger.info("🏫 3. CONTEXTO DEL SISTEMA ESCOLAR:")
            for key, value in sistema_context.items():
                self.logger.info(f"      ├── {key}: {value}")

            # 4. TIPOS DE CONSULTAS ESPERADAS
            tipos_consultas = {
                "busquedas": "buscar García, alumnos de 2do A, estudiantes matutinos",
                "estadisticas": "cuántos alumnos hay, promedio general, distribuciones",
                "documentos": "constancia para Juan, certificado de calificaciones",
                "transformaciones": "convertir constancia, cambiar formato",
                "ayuda": "qué puedes hacer, cómo buscar alumnos"
            }
            self.logger.info("")
            self.logger.info("📝 4. TIPOS DE CONSULTAS ESPERADAS:")
            for tipo, ejemplos in tipos_consultas.items():
                self.logger.info(f"      ├── {tipo}: {ejemplos}")

            # 5. ESTADO DE INICIALIZACIÓN (COMPONENTES BÁSICOS)
            self.logger.info("")
            self.logger.info("✅ 5. ESTADO DE INICIALIZACIÓN:")
            self.logger.info(f"      ├── Gemini Client: {'✅ Conectado' if self.gemini_client else '❌ No disponible'}")
            self.logger.info(f"      ├── Intention Detector: {'✅ Inicializado' if self.intention_detector else '❌ No disponible'}")
            self.logger.info(f"      ├── Student Interpreter: ⏳ Se inicializará después")
            self.logger.info(f"      └── Help Interpreter: ⏳ Se inicializará después")

            self.logger.info("=" * 80)
            self.logger.info("🎯 [MASTER] CONTEXTO ESTRATÉGICO CARGADO Y VERIFICADO")
            self.logger.info("=" * 80)

        except Exception as e:
            self.logger.error(f"❌ Error mostrando contexto detallado: {e}")

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
