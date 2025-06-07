"""
Intérprete maestro - Coordina todos los módulos de interpretación
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from app.core.ai.interpretation.base_interpreter import InterpretationContext, InterpretationResult
from app.core.ai.interpretation.student_query_interpreter import StudentQueryInterpreter
from app.core.ai.interpretation.master_knowledge import MasterKnowledge
from app.core.logging import get_logger
from app.core.config import Config

@dataclass
class IntentionResult:
    """Resultado de la detección de intención (LOCAL - reemplaza intention_detector obsoleto)"""
    intention_type: str  # "consulta_alumnos", "ayuda_sistema", "conversacion_general"
    sub_intention: str   # "busqueda_simple", "generar_constancia", etc.
    confidence: float
    reasoning: str
    detected_entities: Dict[str, Any]
    categoria: str = ""           # busqueda|estadistica|reporte|constancia|transformacion|continuacion
    sub_tipo: str = ""            # simple|complejo|listado|conteo|generacion|conversion
    complejidad: str = ""         # baja|media|alta
    requiere_contexto: bool = False
    flujo_optimo: str = ""        # sql_directo|analisis_datos|listado_completo

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

        # 🧠 INICIALIZAR CEREBRO DEL MASTER (CONOCIMIENTO PROFUNDO)
        self.knowledge = MasterKnowledge()
        self.logger.info("🧠 [MASTER] Cerebro inicializado con conocimiento profundo del sistema")

        # 🎯 INICIALIZAR PROMPT MANAGER PARA ROUTING FORZADO
        from app.core.ai.prompts.master_prompt_manager import MasterPromptManager
        self.prompt_manager = MasterPromptManager()
        self.logger.info("🎯 [MASTER] PromptManager inicializado para routing forzado")

        # 🎯 CONTEXTO ESTRATÉGICO DEL SISTEMA (SEGÚN INTENCIONES_ACCIONES_DEFINITIVAS.md)
        self.system_map = {
            "StudentQueryInterpreter": {
                "handles": ["consulta_alumnos"],  # ✅ Solo intención principal
                "sub_intentions": ["busqueda_simple", "busqueda_compleja", "estadisticas", "generar_constancia", "transformacion_pdf"],
                "capabilities": "Consultas de BD, documentos, análisis de alumnos",
                "description": "Especialista en datos de alumnos y generación de documentos"
            },
            "HelpInterpreter": {
                "handles": ["ayuda_sistema"],
                "sub_intentions": [
                    "explicacion_general", "tutorial_funciones", "sobre_creador",
                    "auto_consciencia", "ventajas_sistema", "casos_uso_avanzados",
                    "limitaciones_honestas", "pregunta_capacidades", "pregunta_tecnica"
                ],
                "capabilities": "Asistente de IA consciente, persuasivo y experto en el sistema",
                "description": "Especialista en explicar el sistema con personalidad y conocimiento sobre Angel"
            },
            "MasterInterpreter": {
                "handles": ["aclaracion_requerida"],
                "sub_intentions": ["multiple_interpretations", "incomplete_query", "ambiguous_reference"],
                "capabilities": "Detección de ambigüedades y comunicación directa con usuario",
                "description": "Master se delega a sí mismo para consultas ambiguas"
            },
            "GeneralInterpreter": {
                "handles": ["conversacion_general"],
                "sub_intentions": ["saludo", "chat_casual", "despedida", "redireccion_educada"],
                "capabilities": "Conversación natural, saludos, temas no escolares",
                "description": "Especialista en conversación general con identidad escolar sutil"
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

        # 🔧 COMPONENTES ELIMINADOS: IntentionDetector (ahora todo es unificado en _analyze_and_delegate_intelligently)

        # 🎯 LOGS DE DEPURACIÓN FORZADOS - CONTEXTO ESTRATÉGICO COMPLETO
        self.logger.info("🎯 [MASTER] INICIALIZADO CON CONTEXTO ESTRATÉGICO")
        self.logger.info(f"   ├── Especialistas disponibles: {len(self.system_map)}")
        self.logger.info(f"   ├── StudentQueryInterpreter: {self.system_map['StudentQueryInterpreter']['capabilities']}")
        self.logger.info(f"   ├── HelpInterpreter: {self.system_map['HelpInterpreter']['capabilities']}")
        self.logger.info(f"   └── GeneralInterpreter: {self.system_map['GeneralInterpreter']['capabilities']}")

        # 🧠 [MASTER] Contexto estratégico inicializado
        self._log_strategic_context()

        # 🎯 INICIALIZAR ESPECIALISTAS (DESPUÉS DE MOSTRAR CONTEXTO MASTER)
        self.logger.info("🎯 [MASTER] Inicializando especialistas...")
        from app.core.config import Config
        db_path = Config.DB_PATH

        # 🎯 INICIALIZAR SCHOOL CONFIG MANAGER CON BD PARA AUTO-DETECCIÓN
        from app.core.config.school_config_manager import get_school_config_manager
        school_config = get_school_config_manager(db_path=db_path)
        self.logger.info(f"🏫 [MASTER] Configuración escolar: {school_config.get_school_name()} ({school_config.get_total_students()} alumnos)")

        self.student_interpreter = StudentQueryInterpreter(db_path, gemini_client)

        from app.core.ai.interpretation.help_interpreter import HelpInterpreter
        self.help_interpreter = HelpInterpreter(gemini_client)

        from app.core.ai.interpretation.general_interpreter import GeneralInterpreter
        self.general_interpreter = GeneralInterpreter(gemini_client)

        self.logger.info("✅ [MASTER] Especialistas inicializados correctamente (Student, Help, General)")

    def interpret(self, context: InterpretationContext, conversation_stack=None, current_pdf=None) -> Optional[InterpretationResult]:
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

            # 🎯 ALMACENAR CONVERSATION_STACK PARA USO EN RESPUESTA FINAL
            self.current_conversation_stack = conversation_stack or []

            # 🎯 PROCESAMIENTO CON CONTEXTO CONVERSACIONAL ACTIVADO
            context.conversation_stack = conversation_stack or []
            if context.conversation_stack:
                self.logger.info(f"🎯 [MASTER] Procesando con contexto - {len(context.conversation_stack)} niveles disponibles")
            else:
                self.logger.info("🎯 [MASTER] Procesando consulta individual")

            # 🧠 ANÁLISIS UNIFICADO MAESTRO - UN SOLO PROMPT PARA TODO
            # Reemplaza: detección de intención + resolución de contexto + análisis
            analysis_result = self._analyze_and_delegate_intelligently(context.user_message, context.conversation_stack)

            if not analysis_result:
                self.logger.error("❌ [MASTER] Error en análisis unificado")
                return None

            # Convertir análisis unificado a IntentionResult para compatibilidad
            intention = self._convert_analysis_to_intention(analysis_result)

            # 🧠 [MASTER] Intención detectada y categorizada
            self.logger.info(f"🧠 [MASTER] Analizando: \"{context.user_message}\" → {intention.intention_type} ({intention.confidence})")

            # 🔧 DEBUG: Información detallada solo en modo debug
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [MASTER] Detalles: {intention.intention_type}/{intention.sub_intention}")
            debug_detailed(self.logger, f"🔧 [MASTER] Categoría: {intention.categoria}, Sub-tipo: {intention.sub_tipo}")
            debug_detailed(self.logger, f"🔧 [MASTER] Complejidad: {intention.complejidad}, Flujo: {intention.flujo_optimo}")

            # PASO 3: VALIDAR INTENCIÓN CON SISTEMA MAP
            validated_intention = self._validate_intention_with_system_map(intention)
            if validated_intention != intention:
                self.logger.info(f"🔧 [MASTER] Intención corregida por system_map")

            # 🧠 PASO 2: ANÁLISIS DE CONOCIMIENTO (¿PUEDO HACERLO?)
            feasibility = self._validate_feasibility_with_knowledge(validated_intention, context.user_message)

            # Si no es factible, crear respuesta de limitación inmediatamente
            if not feasibility["can_handle"]:
                return self._create_limitation_response(feasibility, context.user_message)

            # 🧠 PASO 3: ANÁLISIS DE CONTEXTO (¿HAY INFORMACIÓN PREVIA RELEVANTE?)
            context_analysis = self._analyze_context_relevance(validated_intention, context.conversation_stack, context.user_message)

            # PASO 4: VERIFICAR SI NECESITA ACLARACIÓN
            # 🔧 ARREGLO: Verificar si es InterpretationResult con action aclaracion_requerida
            if hasattr(validated_intention, 'action') and validated_intention.action == "aclaracion_requerida":
                return validated_intention
            elif hasattr(validated_intention, 'intention_type') and validated_intention.intention_type == "aclaracion_requerida":
                return self._handle_ambiguous_query(context, validated_intention)

            # PASO 5: DIRIGIR AL ESPECIALISTA DIRECTAMENTE
            result = self._delegate_to_specialist_direct(context, validated_intention, current_pdf)

            # PASO 5: ANALIZAR RESULTADOS Y DECIDIR SI NECESITA COMUNICACIÓN BIDIRECCIONAL
            # 🔧 ARREGLO: Solo si validated_intention no es InterpretationResult
            if (result and hasattr(validated_intention, 'intention_type') and
                self._should_ask_user_about_results(result, context.user_message)):
                return self._handle_results_analysis(context, validated_intention, result)

            # PASO 6: PROCESAR RETROALIMENTACIÓN DEL ESPECIALISTA
            # 🔧 ARREGLO: Solo si validated_intention no es InterpretationResult
            if hasattr(validated_intention, 'intention_type'):
                self._process_specialist_feedback(validated_intention, result)

            return result

        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error en interpretación: {e}")
            return None

    def _convert_analysis_to_intention(self, analysis_result: dict):
        """
        🔧 CONVERTIR ANÁLISIS UNIFICADO A INTENTIONRESULT
        Mantiene compatibilidad con el resto del sistema
        """
        try:
            # Usar IntentionResult local (reemplaza intention_detector obsoleto)

            # Extraer información del análisis
            intention_type = analysis_result.get('intention_type', 'consulta_alumnos')
            sub_intention = analysis_result.get('sub_intention', 'busqueda_simple')
            usar_contexto = analysis_result.get('usar_contexto', False)
            alumno_resuelto = analysis_result.get('detected_entities', {}).get('alumno_resuelto')

            # 🔧 NORMALIZAR INTENCIONES: Convertir a minúsculas para compatibilidad con system_map
            intention_type = intention_type.lower() if intention_type else 'consulta_alumnos'
            sub_intention = sub_intention.lower() if sub_intention else 'busqueda_simple'

            self.logger.info(f"🔧 [MASTER] Análisis convertido: {intention_type}/{sub_intention} (contexto: {usar_contexto})")

            # 🎯 TRANSFERIR TODAS LAS DETECTED_ENTITIES DEL LLM AL STUDENT
            detected_entities = analysis_result.get('detected_entities', {})

            # Agregar alumno_resuelto si existe (compatibilidad)
            if alumno_resuelto:
                detected_entities['alumno_resuelto'] = alumno_resuelto

            self.logger.info(f"🎯 [MASTER] Entidades transferidas al Student: {list(detected_entities.keys())}")
            if 'limite_resultados' in detected_entities:
                self.logger.info(f"🎯 [MASTER] Límite detectado: {detected_entities['limite_resultados']}")
            if 'filtros' in detected_entities:
                self.logger.info(f"🎯 [MASTER] Filtros detectados: {detected_entities['filtros']}")

            # Crear IntentionResult compatible
            intention = IntentionResult(
                intention_type=intention_type,
                sub_intention=sub_intention,
                confidence=0.95,  # Alta confianza del análisis unificado
                reasoning=analysis_result.get('reasoning', 'Análisis unificado del Master'),
                detected_entities=detected_entities,
                categoria="",  # No necesario en el flujo unificado
                sub_tipo="",
                complejidad="",
                requiere_contexto=usar_contexto,
                flujo_optimo=""
            )

            self.logger.info(f"🔧 [MASTER] Análisis convertido: {intention_type}/{sub_intention} (contexto: {usar_contexto})")
            return intention

        except Exception as e:
            self.logger.error(f"❌ Error convirtiendo análisis a intention: {e}")
            # Fallback básico usando IntentionResult local
            return IntentionResult(
                intention_type='consulta_alumnos',
                sub_intention='busqueda_simple',
                confidence=0.5,
                reasoning='Fallback por error en conversión',
                detected_entities={},
                requiere_contexto=False
            )

    # MÉTODO ELIMINADO: _detect_intention_with_context
    # Ahora todo se maneja en _analyze_and_delegate_intelligently (prompt unificado)

    # MÉTODO ELIMINADO: _resolve_contextual_references
    # Ahora todo se maneja directamente en el flujo principal con _analyze_and_delegate_intelligently

    # ✅ MÉTODO ELIMINADO: _force_area_selection() - Reemplazado por _analyze_and_delegate_intelligently()

    # ✅ MÉTODO ELIMINADO: _fallback_area_detection() - No se usa en flujo actual

    # ✅ MÉTODO ELIMINADO: _delegate_to_general() - No se usa en flujo actual

    # ✅ MÉTODO ELIMINADO: _convert_routing_to_student_format() - No se usa en flujo actual

    # ✅ MÉTODO ELIMINADO: _convert_routing_to_help_format() - No se usa en flujo actual

    # ✅ MÉTODO ELIMINADO: _update_interaction_memory() con routing - Reemplazado por actualización directa en flujo principal

    def _get_dynamic_intentions_section(self) -> str:
        """
        🎯 GENERAR SECCIÓN DINÁMICA DE INTENCIONES

        Usa SystemCatalog para generar la sección de intenciones
        que se inyecta en el prompt del Master.
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            return SystemCatalog.generate_intentions_section()
        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error generando sección de intenciones: {e}")
            # Fallback a sección básica
            return """
🎯 **CONSULTA_ALUMNOS** → StudentQueryInterpreter (Prioridad: 1)
   ├── DESCRIPCIÓN: TODO sobre alumnos de la escuela (211 alumnos activos)
   ├── SUB-INTENCIONES: busqueda_simple, estadisticas, generar_constancia

🎯 **AYUDA_SISTEMA** → HelpInterpreter (Prioridad: 2)
   ├── DESCRIPCIÓN: Ayuda sobre el sistema y capacidades
   ├── SUB-INTENCIONES: explicacion_general, sobre_creador, auto_consciencia
"""

    def _get_dynamic_mapping_examples(self) -> str:
        """
        🎯 GENERAR EJEMPLOS DINÁMICOS DE MAPEO

        Usa SystemCatalog para generar ejemplos de mapeo
        que ayudan al LLM a entender las intenciones.
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            return SystemCatalog.generate_mapping_examples()
        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error generando ejemplos de mapeo: {e}")
            # Fallback a ejemplos básicos
            return """
- "buscar García" → consulta_alumnos/busqueda_simple
- "cuántos alumnos" → consulta_alumnos/estadisticas
- "constancia para Juan" → consulta_alumnos/generar_constancia
- "qué puedes hacer" → ayuda_sistema/explicacion_general
- "quién te creó" → ayuda_sistema/sobre_creador
"""

    def _generate_humanized_response(self, result, user_query: str, routing_decision: dict):
        """
        🗣️ MASTER COMO VOCERO FINAL (PROMPT 4)

        Genera respuesta humanizada basada en el resultado del especialista.
        Equivale al PROMPT 4 del flujo tradicional Master-Student.

        Args:
            result: Resultado del especialista
            user_query: Consulta original del usuario
            routing_decision: Decisión del routing forzado

        Returns:
            InterpretationResult con respuesta humanizada
        """
        try:
            self.logger.info("🗣️ [MASTER] Generando respuesta final como vocero...")

            # Usar el método existente de generación de respuesta
            humanized_response = self._generate_master_response(result.parameters, user_query)

            if humanized_response:
                self.logger.info("✅ Master generó respuesta contextual exitosamente")
                self.logger.info(f"✅ [MASTER] Respuesta final: '{humanized_response[:50]}...'")

                # Crear nuevo resultado con respuesta humanizada
                from app.core.ai.interpretation.base_interpreter import InterpretationResult

                humanized_result = InterpretationResult(
                    action=result.action,
                    parameters={
                        **result.parameters,
                        "master_response": humanized_response,
                        "humanized": True,
                        "routing_info": routing_decision
                    },
                    confidence=result.confidence
                )

                self.logger.info("🗣️ [MASTER] Respuesta final generada como vocero")
                return humanized_result
            else:
                self.logger.warning("⚠️ [MASTER] No se pudo generar respuesta humanizada")
                return result

        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error generando respuesta humanizada: {e}")
            return result

    def _analyze_and_delegate_intelligently(self, user_query: str, conversation_stack: list):
        """
        🧠 ANÁLISIS INTELIGENTE UNIFICADO CON RAZONAMIENTO HUMANO
        Reemplaza análisis semántico + resolución de referencias

        🔄 AHORA USA MASTERPROMPTMANAGER MEJORADO
        """
        try:
            # 🔄 USAR MASTERPROMPTMANAGER EN LUGAR DE PROMPT HARDCODEADO
            conversation_context = self.prompt_manager.format_conversation_context(conversation_stack)
            prompt = self.prompt_manager.get_intention_detection_prompt(user_query, conversation_context)
            # 🔍 DEBUG: MOSTRAR PROMPT COMPLETO ENVIADO AL LLM
            if os.getenv('DEBUG_PAUSES') == 'true':
                print("\n🛑 [MASTER-DEBUG] PROMPT COMPLETO ENVIADO AL LLM:")
                print("=" * 80)
                print(prompt)
                print("=" * 80)
                print("└── Presiona ENTER para enviar al LLM...")
                input()

            # 🔍 DEBUG: Verificar si los ejemplos de constancia están en el prompt
            if "generale una constancia" in prompt:
                self.logger.info("✅ [DEBUG] Ejemplos de constancia encontrados en prompt")
            else:
                self.logger.error("❌ [DEBUG] Ejemplos de constancia NO encontrados en prompt")

            # 🔍 DEBUG: Verificar si hay contexto disponible
            if "Franco Alexander" in prompt:
                self.logger.info("✅ [DEBUG] Contexto de Franco Alexander encontrado en prompt")
            else:
                self.logger.info("🔍 [DEBUG] No se encontró contexto de Franco Alexander en prompt")

            if self.gemini_client:
                response = self.gemini_client.send_prompt_sync(prompt)

                # 🔍 DEBUG: MOSTRAR RESPUESTA CRUDA DEL LLM
                if os.getenv('DEBUG_PAUSES') == 'true':
                    print("\n🛑 [MASTER-DEBUG] RESPUESTA CRUDA DEL LLM:")
                    print("=" * 80)
                    print(response)
                    print("=" * 80)
                    print("└── Presiona ENTER para parsear JSON...")
                    input()

                if response:
                    import json
                    try:
                        # Limpiar respuesta JSON
                        clean_response = response.strip()
                        if clean_response.startswith('```json'):
                            clean_response = clean_response[7:]
                        if clean_response.startswith('```'):
                            clean_response = clean_response[3:]
                        if clean_response.endswith('```'):
                            clean_response = clean_response[:-3]
                        clean_response = clean_response.strip()

                        result = json.loads(clean_response)

                        # 🔍 DEBUG: MOSTRAR JSON PARSEADO
                        if os.getenv('DEBUG_PAUSES') == 'true':
                            print("\n🛑 [MASTER-DEBUG] JSON PARSEADO EXITOSAMENTE:")
                            print("=" * 80)
                            import json
                            print(json.dumps(result, indent=2, ensure_ascii=False))
                            print("=" * 80)
                            print("└── Presiona ENTER para continuar...")
                            input()

                        self.logger.info(f"🧠 [MASTER] Análisis unificado exitoso: {result.get('reasoning', '')[:100]}...")
                        return result

                    except json.JSONDecodeError as e:
                        self.logger.warning(f"🧠 [MASTER] Error parsing JSON: {e}")
                        self.logger.warning(f"🧠 [MASTER] Respuesta: {response}")

                        # 🔍 DEBUG: MOSTRAR ERROR DE PARSING
                        if os.getenv('DEBUG_PAUSES') == 'true':
                            print(f"\n🛑 [MASTER-DEBUG] ERROR PARSING JSON:")
                            print(f"Error: {e}")
                            print(f"Respuesta que falló: {response}")
                            print("└── Presiona ENTER para continuar...")
                            input()

            return None

        except Exception as e:
            self.logger.error(f"Error en análisis inteligente unificado: {e}")
            return None

        except Exception as e:
            self.logger.error(f"Error en análisis inteligente unificado: {e}")
            return None

    def _process_unified_analysis(self, analysis_result: dict, original_intention):
        """
        🔧 PROCESAR RESULTADO DEL ANÁLISIS UNIFICADO
        Convierte el análisis del LLM en intención actualizada
        """
        try:
            # Actualizar intención basada en el análisis
            original_intention.intention_type = analysis_result.get('intention_type', original_intention.intention_type)
            original_intention.sub_intention = analysis_result.get('sub_intention', original_intention.sub_intention)
            original_intention.requiere_contexto = analysis_result.get('usar_contexto', False)

            # 🎯 VALIDAR RESOLUCIÓN DE ALUMNO
            detected_entities = analysis_result.get('detected_entities', {})
            alumno_resuelto = detected_entities.get('alumno_resuelto')
            referencia_encontrada = analysis_result.get('referencia_encontrada', '')

            if alumno_resuelto and isinstance(alumno_resuelto, dict):
                alumno_id = alumno_resuelto.get('id')
                alumno_nombre = alumno_resuelto.get('nombre', '')

                # 🧠 CONFIAR EN EL ANÁLISIS INTELIGENTE DEL LLM
                # El LLM ya validó que tiene información suficiente para resolver
                if alumno_nombre and not alumno_nombre.startswith('identificar'):
                    # ✅ EL LLM ENCONTRÓ INFORMACIÓN VÁLIDA - CONFIAR EN ÉL
                    # 🎯 NOMBRE COMPLETO ES SUFICIENTE - Student manejará el mapeo técnico

                    # ✅ ACEPTAR LA RESOLUCIÓN DEL LLM (nombre completo es suficiente)
                    original_intention.detected_entities['alumno_resuelto'] = alumno_resuelto
                    original_intention.requiere_contexto = False  # Ya no necesita contexto, está resuelto
                    self.logger.info(f"✅ [MASTER] Información suficiente para Student: {alumno_nombre} → Student manejará mapeo técnico")

                    # ✅ MAPEAR SUB-INTENCIONES CORRECTAS PARA STUDENT
                    if analysis_result.get('sub_intention') in ['informacion_completa', 'busqueda_filtrada']:
                        original_intention.sub_intention = 'busqueda_simple'
                        self.logger.info(f"🔧 [MASTER] Mapeando '{analysis_result.get('sub_intention')}' → 'busqueda_simple' para alumno resuelto")
                    elif analysis_result.get('sub_intention') == 'generar_constancia':
                        # 🎯 CONSTANCIAS: Mantener como consulta_alumnos + generar_constancia
                        original_intention.intention_type = 'consulta_alumnos'
                        original_intention.sub_intention = 'generar_constancia'
                        self.logger.info(f"🔧 [MASTER] Mapeando 'generar_constancia' → 'consulta_alumnos/generar_constancia' para alumno resuelto")

                else:
                    # ❌ Solo rechazar si el nombre es claramente inválido o descriptivo
                    self.logger.warning(f"⚠️ [MASTER] Resolución inválida: Nombre inválido o descriptivo: '{alumno_nombre}'")
                    original_intention.requiere_contexto = True

            # 📊 LOG DEL ANÁLISIS COMPLETO
            razonamiento = analysis_result.get('reasoning', 'No especificado')
            contexto_analizado = analysis_result.get('contexto_analizado', 'No especificado')

            self.logger.info(f"🧠 [MASTER] Razonamiento: {razonamiento[:100]}...")
            self.logger.info(f"📊 [MASTER] Contexto analizado: {contexto_analizado}")
            self.logger.info(f"🔍 [MASTER] Referencia encontrada: {referencia_encontrada}")
            self.logger.info(f"🎯 [MASTER] Análisis unificado completado: {analysis_result.get('intention_type')}/{original_intention.sub_intention}")

            return original_intention

        except Exception as e:
            self.logger.error(f"Error procesando análisis unificado: {e}")
            return original_intention

    def _create_context_summary(self, conversation_stack: list) -> str:
        """
        📋 CREAR RESUMEN DEL CONTEXTO CONVERSACIONAL
        Genera un resumen inteligente del conversation_stack para el LLM
        """
        try:
            if not conversation_stack:
                return "Sin contexto conversacional previo."

            context_lines = []
            context_lines.append("CONTEXTO CONVERSACIONAL (niveles por prioridad, más reciente primero):")
            context_lines.append("")

            for i, nivel in enumerate(reversed(conversation_stack), 1):
                query = nivel.get('query', 'N/A')
                row_count = nivel.get('row_count', 0)
                awaiting = nivel.get('awaiting', 'N/A')
                data = nivel.get('data', [])

                context_lines.append(f"NIVEL {i}: '{query}'")

                if row_count == 1 and data:
                    # Información específica del alumno
                    alumno = data[0]
                    nombre = alumno.get('nombre', 'N/A')
                    id_alumno = alumno.get('id', 'N/A')
                    grado = alumno.get('grado', 'N/A')
                    grupo = alumno.get('grupo', 'N/A')
                    context_lines.append(f"→ Alumno específico: {nombre} (ID: {id_alumno}) - {grado}° {grupo}")

                elif row_count <= 10 and data:
                    # Lista pequeña con nombres
                    if isinstance(data, list):
                        nombres = [d.get('nombre', 'N/A') for d in data[:5]]
                        context_lines.append(f"→ Lista pequeña ({row_count} alumnos): {', '.join(nombres)}")
                        if row_count > 5:
                            context_lines.append(f"→ (y {row_count - 5} más...)")
                    else:
                        context_lines.append(f"→ Datos estructurados ({row_count} elementos)")

                elif row_count > 10:
                    # Lista grande - CONTEXTO COMPLETO PARA RESOLUCIÓN INTELIGENTE
                    context_lines.append(f"→ Lista grande: {row_count} alumnos disponibles")
                    if data:
                        # ✅ MOSTRAR SUFICIENTES ELEMENTOS PARA RESOLUCIÓN DINÁMICA
                        elementos_mostrar = min(10, len(data))  # Mostrar hasta 10 para referencias
                        context_lines.append(f"→ Primeros {elementos_mostrar} alumnos (para referencias posicionales, nombres, etc.):")
                        for j, alumno in enumerate(data[:elementos_mostrar], 1):
                            nombre = alumno.get('nombre', 'N/A')
                            id_alumno = alumno.get('id', 'N/A')
                            matricula = alumno.get('matricula', 'N/A')
                            grado = alumno.get('grado', 'N/A')
                            grupo = alumno.get('grupo', 'N/A')
                            context_lines.append(f"   {j}. {nombre} (ID: {id_alumno}, Mat: {matricula}, {grado}°{grupo})")

                        if row_count > elementos_mostrar:
                            context_lines.append(f"   ... y {row_count - elementos_mostrar} más disponibles")

                        # Detectar criterios comunes
                        primer_alumno = data[0]
                        if 'grado' in primer_alumno:
                            grado = primer_alumno.get('grado')
                            context_lines.append(f"→ Criterio detectado: {grado}° grado")
                        if 'turno' in primer_alumno:
                            turno = primer_alumno.get('turno')
                            context_lines.append(f"→ Turno: {turno}")

                        # ✅ INFORMACIÓN PARA RESOLUCIÓN DINÁMICA
                        context_lines.append(f"→ LISTA COMPLETA DISPONIBLE: Puedes referenciar por posición, nombre, matrícula, etc.")
                else:
                    context_lines.append(f"→ {row_count} resultados")

                context_lines.append(f"→ Esperando: {awaiting}")
                context_lines.append("")

            return "\n".join(context_lines)

        except Exception as e:
            self.logger.error(f"Error creando resumen de contexto: {e}")
            return "Error procesando contexto conversacional."

    def _handle_ambiguous_reference(self, user_query: str, intention, conversation_stack: list):
        """
        🚨 MANEJA REFERENCIAS AMBIGUAS DETECTADAS POR EL LLM
        Genera una respuesta de aclaración inteligente basada en el contexto
        """
        try:
            from app.core.ai.interpretation.base_interpreter import InterpretationResult

            # Obtener información del contexto para generar aclaración específica
            ultimo_nivel = conversation_stack[-1] if conversation_stack else None
            if not ultimo_nivel:
                return intention

            row_count = ultimo_nivel.get('row_count', 0)
            query_anterior = ultimo_nivel.get('query', 'consulta anterior')

            # Generar mensaje de aclaración específico
            if row_count > 1:
                human_response = f"🤔 Tu consulta '{user_query}' es ambigua. Encontré {row_count} alumnos en '{query_anterior}'. ¿Podrías especificar a cuál te refieres? Por ejemplo: 'el segundo', 'el tercero', o menciona el nombre específico."
            else:
                human_response = f"🤔 Tu consulta '{user_query}' no es lo suficientemente clara. ¿Podrías ser más específico sobre qué información necesitas?"

            # Crear resultado de aclaración
            result = InterpretationResult(
                action="aclaracion_requerida",
                parameters={
                    "message": human_response,
                    "original_query": user_query,
                    "human_response": human_response,
                    "context_info": {
                        "row_count": row_count,
                        "query_anterior": query_anterior
                    }
                },
                confidence=0.9
            )

            self.logger.info(f"🚨 [MASTER] Generada aclaración para referencia ambigua: {row_count} candidatos")
            return result

        except Exception as e:
            self.logger.error(f"❌ Error manejando referencia ambigua: {e}")
            return intention

    def _analyze_context_relevance(self, intention, conversation_stack: list, user_query: str) -> dict:
        """
        🧠 PASO 3: ANÁLISIS DE CONTEXTO COMO HUMANO EXPERTO
        Determina si hay información previa relevante para la consulta actual
        """
        try:
            # Si no hay contexto, es independiente
            if not conversation_stack:
                return {
                    "needs_context": False,
                    "analysis": "Sin contexto conversacional previo - consulta independiente",
                    "resolved_reference": None
                }

            # Análisis básico de referencias contextuales
            contextual_keywords = [
                "él", "ella", "ese", "esa", "este", "esta", "aquel", "aquella",
                "el anterior", "la anterior", "el primero", "el segundo", "el último",
                "sus datos", "su información", "de él", "para ella",
                "también", "además", "igualmente"
            ]

            needs_context = any(keyword in user_query.lower() for keyword in contextual_keywords)

            if needs_context:
                # Hay referencias contextuales - necesita análisis profundo
                return {
                    "needs_context": True,
                    "analysis": f"Detectadas referencias contextuales en: '{user_query}'",
                    "resolved_reference": "Requiere análisis LLM para resolución"
                }
            else:
                # Consulta independiente
                return {
                    "needs_context": False,
                    "analysis": "Consulta semánticamente independiente - no requiere contexto",
                    "resolved_reference": None
                }

        except Exception as e:
            self.logger.error(f"Error analizando relevancia de contexto: {e}")
            return {
                "needs_context": False,
                "analysis": "Error en análisis - procesando como independiente",
                "resolved_reference": None
            }

    def _analyze_query_semantic_independence(self, user_query: str, conversation_stack: list) -> bool:
        """
        🧠 ANALIZA SI LA CONSULTA ES SEMÁNTICAMENTE INDEPENDIENTE
        Usa razonamiento LLM para determinar si necesita contexto
        """
        try:
            # Si no hay contexto, obviamente es independiente
            if not conversation_stack:
                return True

            # Crear prompt para análisis semántico
            context_summary = self._create_context_summary(conversation_stack)

            prompt = f"""
🧠 ANÁLISIS CONTEXTUAL INTELIGENTE - MASTER DEL SISTEMA ESCOLAR

CONTEXTO CONVERSACIONAL COMPLETO:
{context_summary}

CONSULTA A ANALIZAR: "{user_query}"

🎯 MI IDENTIDAD Y CONOCIMIENTO COMPLETO:
- Sistema escolar "PROF. MAXIMO GAMIZ FERNANDEZ"
- Base de datos: 211 alumnos en grados 1° a 6°
- Especialistas: StudentQueryInterpreter, HelpInterpreter

🎯 ESPECIALISTAS QUE DIRIJO:
**StudentQueryInterpreter**:
- BUSCAR_UNIVERSAL: Búsquedas flexibles
- CONTAR_UNIVERSAL: Conteos y estadísticas
- GENERAR_CONSTANCIA_COMPLETA: Documentos PDF
- BUSCAR_Y_FILTRAR: Filtros sobre resultados

📋 NIVELES DE CONTEXTO:
- Nivel 1 = MÁS RECIENTE (más relevante)
- Listas grandes = "regenerables" (SQL + metadatos)
- Puedo usar CUALQUIER nivel para resolver referencias

🧠 RAZONAMIENTO INTELIGENTE:
1. ¿Qué solicita el usuario?
2. ¿Qué información tengo disponible?
3. ¿Puedo resolver con contexto?
4. ¿Hay referencias que resolver?

ELEMENTOS QUE INDICAN NECESIDAD DE CONTEXTO:
• Pronombres referenciales: "él", "ella", "ese", "esa", "este", "esta", "aquel", "aquella"
• Frases pronominales: "ese alumno", "esa estudiante", "ese chico", "esa persona"
• Referencias posicionales: "el primero", "el segundo", "el último", "la primera"
• Adjetivos demostrativos sin sustantivo: "ese", "esa", "este", "esta"
• Referencias implícitas: "sus datos", "su información", "de él", "para ella"
• Continuaciones: "también", "además", "igualmente", "del mismo modo"
• Filtros sobre resultados previos: "de esos", "entre ellos", "de los anteriores"

EJEMPLOS DE ANÁLISIS INTELIGENTE:
INDEPENDIENTES:
- "buscar García" → Nueva búsqueda completa
- "buscar JUAN PÉREZ LÓPEZ" → Nombre completo específico
- "constancia para MARÍA GONZÁLEZ" → Nombre específico
- "estadísticas de grupos" → Consulta general
- "cuántos alumnos hay en total" → Consulta global

NECESITAN CONTEXTO:
- "constancia para el segundo" → Referencia posicional
- "de esos cuántos son del turno matutino" → Filtro sobre anteriores
- "dame la curp de gabriela" → Nombre parcial, buscar en contexto
- "constancia para ella" → Pronombre, resolver referencia
- "también necesito su constancia" → Continuación con referencia

RESPUESTA: "INDEPENDIENTE" o "NECESITA_CONTEXTO"
"""

            response = self.gemini_client.send_prompt_sync(prompt)
            result = response.strip().upper() if response else ""

            is_independent = "INDEPENDIENTE" in result

            self.logger.info(f"🧠 [MASTER] Análisis semántico: '{user_query}' → {'INDEPENDIENTE' if is_independent else 'NECESITA_CONTEXTO'}")

            return is_independent

        except Exception as e:
            self.logger.error(f"Error en análisis semántico: {e}")
            # 🧠 FALLBACK SIMPLE: Si hay error, asumir que necesita contexto si hay contexto disponible
            if conversation_stack:
                self.logger.warning(f"🧠 [MASTER] Error en LLM, pero hay contexto disponible - asumiendo NECESITA_CONTEXTO")
                return False  # NECESITA CONTEXTO
            else:
                self.logger.warning(f"🧠 [MASTER] Error en LLM, sin contexto disponible - asumiendo INDEPENDIENTE")
                return True  # INDEPENDIENTE

    def _resolve_reference_with_llm(self, user_query: str, conversation_stack: list) -> dict:
        """
        🧠 RESOLUCIÓN INTELIGENTE DE REFERENCIAS CON LLM
        El LLM entiende CUALQUIER tipo de referencia sin listas hardcodeadas
        """
        try:
            if not conversation_stack:
                return None

            # Crear contexto para el LLM
            context_summary = self._create_detailed_context_for_reference(conversation_stack)

            prompt = f"""
🧠 RESOLUCIÓN INTELIGENTE DE REFERENCIAS - SISTEMA ESCOLAR

CONSULTA DEL USUARIO: "{user_query}"

CONTEXTO CONVERSACIONAL DISPONIBLE:
{context_summary}

🎯 TU TAREA:
Analiza si la consulta del usuario hace referencia a algún alumno específico del contexto.

🧠 REGLAS CRÍTICAS DE RAZONAMIENTO:
1. Si hay UNA SOLA persona en el contexto → Referencia clara
2. Si hay MÚLTIPLES personas CON OPERACIÓN DE FILTRO → Referencia clara a la lista completa
3. Si hay MÚLTIPLES personas SIN especificación ni operación → AMBIGUO, no asumir
4. Si hay posición específica ("el segundo") → Referencia clara
5. Si hay pronombre vago ("su") con lista múltiple SIN OPERACIÓN → AMBIGUO

TIPOS DE REFERENCIAS VÁLIDAS:
- Pronominales CLARAS: "su información" (cuando hay 1 alumno específico)
- Posicionales ESPECÍFICAS: "el segundo", "el tercero", "el último"
- Implícitas CLARAS: "también necesito" (cuando hay 1 alumno específico)
- OPERACIONES DE FILTRO: "de ellos los que...", "de esos cuántos...", "los García del turno..."

🎯 OPERACIONES DE FILTRO (SIEMPRE CLARAS):
- "de ellos dame los que esten en el turno matutino" → FILTRO sobre lista completa
- "de esos cuántos son de primer grado" → CONTEO sobre lista completa
- "los García del turno vespertino" → FILTRO sobre lista completa
- "cuántos de ellos tienen calificaciones" → ANÁLISIS sobre lista completa

❌ NO ASUMIR REFERENCIAS EN CASOS AMBIGUOS:
- "su información" con lista de 20+ alumnos SIN OPERACIÓN → AMBIGUO
- "él" con múltiples candidatos SIN ESPECIFICACIÓN → AMBIGUO
- Pronombres vagos sin contexto específico → AMBIGUO

FORMATO DE RESPUESTA JSON:
{{
    "tiene_referencia": true/false,
    "es_ambiguo": true/false,
    "alumno_referenciado": {{
        "id": número_id,
        "nombre": "NOMBRE COMPLETO",
        "razonamiento": "explicación específica"
    }},
    "motivo_ambiguedad": "explicación si es ambiguo"
}}

EJEMPLOS CORRECTOS:
- "su información" + 1 alumno específico → tiene_referencia: true
- "su información" + lista de 21 → es_ambiguo: true
- "el segundo" + lista → tiene_referencia: true (posición específica)
- "de ellos los del turno matutino" + lista de 49 → tiene_referencia: false (operación de filtro, NO referencia individual)
- "de esos cuántos son de primer grado" + lista → tiene_referencia: false (operación de conteo, NO referencia individual)

RESPONDE SOLO CON EL JSON:
"""

            if self.gemini_client:
                response = self.gemini_client.send_prompt_sync(prompt)
                if response:
                    import json
                    try:
                        # 🔧 LIMPIAR RESPUESTA: Remover bloques de código markdown
                        clean_response = response.strip()
                        if clean_response.startswith('```json'):
                            clean_response = clean_response[7:]  # Remover ```json
                        if clean_response.startswith('```'):
                            clean_response = clean_response[3:]   # Remover ```
                        if clean_response.endswith('```'):
                            clean_response = clean_response[:-3]  # Remover ``` final
                        clean_response = clean_response.strip()

                        result = json.loads(clean_response)

                        # Verificar si es ambiguo
                        if result.get("es_ambiguo"):
                            motivo = result.get("motivo_ambiguedad", "Referencia ambigua")
                            self.logger.info(f"🧠 [LLM] Referencia AMBIGUA detectada: {motivo}")
                            return None  # No resolver, que pida aclaración

                        # Si tiene referencia clara
                        if result.get("tiene_referencia") and result.get("alumno_referenciado"):
                            alumno = result["alumno_referenciado"]
                            self.logger.info(f"🧠 [LLM] Referencia CLARA detectada: {alumno.get('razonamiento')}")
                            return {
                                'id': alumno.get('id'),
                                'nombre': alumno.get('nombre'),
                                'posicion': 'resuelto por LLM'
                            }
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"🧠 [LLM] Error parsing JSON: {e}")
                        self.logger.warning(f"🧠 [LLM] Respuesta original: {response}")
                        self.logger.warning(f"🧠 [LLM] Respuesta limpia: {clean_response}")

            return None

        except Exception as e:
            self.logger.error(f"Error resolviendo referencia con LLM: {e}")
            return None

    def _create_detailed_context_for_reference(self, conversation_stack: list) -> str:
        """
        🧠 CONTEXTO DETALLADO PARA RESOLUCIÓN DE REFERENCIAS
        """
        try:
            if not conversation_stack:
                return "Sin contexto previo"

            context_parts = []

            for i, nivel in enumerate(reversed(conversation_stack), 1):
                query = nivel.get('query', 'N/A')
                data = nivel.get('data', [])
                row_count = nivel.get('row_count', 0)

                if data:
                    if row_count == 1:
                        alumno = data[0]
                        context_parts.append(f"""
NIVEL {i} (más reciente): "{query}"
→ Alumno específico: {alumno.get('nombre')} (ID: {alumno.get('id')})
→ Grado: {alumno.get('grado')}° {alumno.get('grupo')}, Turno: {alumno.get('turno')}
→ CURP: {alumno.get('curp')}""")
                    elif row_count <= 10:
                        if isinstance(data, list):
                            nombres = [f"{j+1}. {d.get('nombre')} (ID: {d.get('id')})" for j, d in enumerate(data[:5])]
                            context_parts.append(f"""
NIVEL {i}: "{query}"
→ Lista de {row_count} alumnos:
{chr(10).join(nombres)}""")
                        else:
                            context_parts.append(f"""
NIVEL {i}: "{query}"
→ Datos estructurados: {row_count} elementos""")
                    else:
                        context_parts.append(f"""
NIVEL {i}: "{query}"
→ Lista grande de {row_count} alumnos (primeros 3):
1. {data[0].get('nombre')} (ID: {data[0].get('id')})
2. {data[1].get('nombre')} (ID: {data[1].get('id')})
3. {data[2].get('nombre')} (ID: {data[2].get('id')})
... y {row_count-3} más""")

            return "\n".join(context_parts) if context_parts else "Sin contexto útil"

        except Exception as e:
            self.logger.error(f"Error creando contexto detallado: {e}")
            return "Error en contexto"



    def _resolve_positional_reference(self, user_query: str, conversation_stack: list) -> dict:
        """Resuelve referencias posicionales como 'segundo', 'tercero'"""
        try:
            if not conversation_stack:
                return None

            # Obtener datos del último nivel
            ultimo_nivel = conversation_stack[-1]
            data = ultimo_nivel.get('data', [])

            if not data:
                return None

            # Determinar posición
            position_index = None
            query_lower = user_query.lower()

            if 'primer' in query_lower or 'primero' in query_lower:
                position_index = 0
            elif 'segundo' in query_lower or 'segunda' in query_lower:
                position_index = 1
            elif 'tercer' in query_lower or 'tercero' in query_lower:
                position_index = 2
            elif 'cuarto' in query_lower or 'cuarta' in query_lower:
                position_index = 3
            elif 'quinto' in query_lower or 'quinta' in query_lower:
                position_index = 4
            elif 'último' in query_lower or 'última' in query_lower:
                position_index = len(data) - 1

            if position_index is not None and position_index < len(data):
                alumno = data[position_index]
                return {
                    'id': alumno.get('id') or alumno.get('alumno_id'),
                    'nombre': alumno.get('nombre'),
                    'posicion': f"posición {position_index + 1}"
                }

            return None

        except Exception as e:
            self.logger.error(f"Error resolviendo referencia posicional: {e}")
            return None

    def _resolve_pronominal_reference(self, conversation_stack: list) -> dict:
        """
        🧠 RESOLUCIÓN INTELIGENTE DE REFERENCIAS PRONOMINALES
        MEJORA: Busca en TODOS los niveles con lógica inteligente
        """
        try:
            if not conversation_stack:
                return None

            # 🧠 BUSCAR EN TODOS LOS NIVELES CON LÓGICA INTELIGENTE
            for nivel in reversed(conversation_stack):
                data = nivel.get('data', [])
                query = nivel.get('query', '').lower()

                if not data:
                    continue

                # CASO 1: Un solo alumno (ideal)
                if len(data) == 1:
                    alumno = data[0]
                    # Verificar que no sea consulta de campo específico
                    if not any(word in query for word in ['curp', 'matrícula', 'información']):
                        return {
                            'id': alumno.get('id') or alumno.get('alumno_id'),
                            'nombre': alumno.get('nombre'),
                            'posicion': 'último mencionado específicamente'
                        }

                # CASO 2: Múltiples alumnos - buscar referencia específica
                elif len(data) > 1:
                    # Si hay nombre específico en la query
                    for alumno in data:
                        nombre_completo = alumno.get('nombre', '').lower()
                        if any(part in query for part in nombre_completo.split()):
                            return {
                                'id': alumno.get('id') or alumno.get('alumno_id'),
                                'nombre': alumno.get('nombre'),
                                'posicion': 'referencia específica por nombre'
                            }

                    # Si no hay referencia específica, tomar el primero
                    alumno = data[0]
                    return {
                        'id': alumno.get('id') or alumno.get('alumno_id'),
                        'nombre': alumno.get('nombre'),
                        'posicion': 'primero de la lista anterior'
                    }

            return None

        except Exception as e:
            self.logger.error(f"Error resolviendo referencia pronominal: {e}")
            return None

    def _resolve_name_reference(self, nombre_detectado: str, conversation_stack: list) -> dict:
        """Resuelve referencias por nombre parcial como 'mario' → 'MARIO LOPEZ GONZALEZ'"""
        try:
            if not conversation_stack or not nombre_detectado:
                return None

            nombre_lower = nombre_detectado.lower()
            self.logger.info(f"🔍 [MASTER] Buscando referencia por nombre: '{nombre_detectado}'")

            # Buscar en todos los niveles del contexto
            for nivel in reversed(conversation_stack):
                data = nivel.get('data', [])
                if not data:
                    continue

                # Buscar coincidencia por nombre parcial
                for alumno in data:
                    nombre_completo = alumno.get('nombre', '').lower()

                    # Verificar si el nombre detectado está contenido en el nombre completo
                    if nombre_lower in nombre_completo:
                        alumno_id = alumno.get('id') or alumno.get('alumno_id')
                        self.logger.info(f"✅ [MASTER] COINCIDENCIA ENCONTRADA: '{nombre_detectado}' → '{alumno.get('nombre')}' (ID: {alumno_id})")
                        return {
                            'id': alumno_id,
                            'nombre': alumno.get('nombre'),
                            'posicion': 'referencia por nombre'
                        }

            self.logger.warning(f"❌ [MASTER] No se encontró referencia para: '{nombre_detectado}'")
            return None

        except Exception as e:
            self.logger.error(f"Error resolviendo referencia por nombre: {e}")
            return None

    def _get_student_id_by_name(self, nombre_completo: str) -> Optional[int]:
        """
        🚫 MÉTODO OBSOLETO - NO USAR
        RAZÓN: Master no debe buscar IDs, nombre completo es suficiente
        Student maneja el mapeo técnico a la base de datos
        """
        try:
            if not nombre_completo:
                return None

            self.logger.info(f"🔍 [MASTER] Buscando ID para: '{nombre_completo}'")

            # Usar el servicio de alumnos para buscar
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            alumno_service = service_provider.alumno_service

            # Buscar por nombre exacto
            alumnos_encontrados = alumno_service.buscar_alumnos(nombre_completo)

            if not alumnos_encontrados:
                self.logger.warning(f"❌ [MASTER] No se encontró alumno con nombre: '{nombre_completo}'")
                return None

            # Buscar coincidencia exacta
            for alumno in alumnos_encontrados:
                alumno_dict = alumno.to_dict() if hasattr(alumno, 'to_dict') else alumno
                if alumno_dict.get('nombre', '').upper() == nombre_completo.upper():
                    alumno_id = alumno_dict.get('id')
                    self.logger.info(f"✅ [MASTER] ID encontrado: '{nombre_completo}' → ID: {alumno_id}")
                    return alumno_id

            # Si no hay coincidencia exacta, tomar el primero si es muy similar
            primer_alumno = alumnos_encontrados[0]
            alumno_dict = primer_alumno.to_dict() if hasattr(primer_alumno, 'to_dict') else primer_alumno
            alumno_id = alumno_dict.get('id')

            self.logger.info(f"✅ [MASTER] Usando primer resultado similar: '{alumno_dict.get('nombre')}' → ID: {alumno_id}")
            return alumno_id

        except Exception as e:
            self.logger.error(f"Error buscando ID por nombre: {e}")
            return None

    def _validate_intention_with_system_map(self, intention):
        """🛡️ VALIDAR INTENCIÓN CON SYSTEM MAP Y CORREGIR AUTOMÁTICAMENTE"""
        try:
            intention_type = intention.intention_type

            # 🎯 LISTA DE INTENCIONES VÁLIDAS (SEGÚN SYSTEM_MAP)
            valid_intentions = []
            for specialist, config in self.system_map.items():
                valid_intentions.extend(config["handles"])

            # ✅ VERIFICAR SI LA INTENCIÓN ES VÁLIDA
            if intention_type in valid_intentions:
                for specialist, config in self.system_map.items():
                    if intention_type in config["handles"]:
                        self.logger.info(f"✅ [MASTER] Intención '{intention_type}' validada para {specialist}")
                        return intention

            # 🔧 CORRECCIÓN AUTOMÁTICA DE INTENCIONES INCORRECTAS
            self.logger.warning(f"⚠️ [MASTER] Intención '{intention_type}' no encontrada en system_map")

            # Mapeo automático para intenciones comunes mal detectadas
            incorrect_mappings = {
                "estadistica": "consulta_alumnos",
                "busqueda": "consulta_alumnos",
                "constancia": "consulta_alumnos",
                "transformacion": "transformacion_pdf",  # Corregir transformacion → transformacion_pdf
                "ayuda": "ayuda_sistema",
                "help": "ayuda_sistema"
            }

            if intention_type in incorrect_mappings:
                old_intention = intention_type
                intention.intention_type = incorrect_mappings[old_intention]
                self.logger.info(f"🔧 [MASTER] Auto-corrección: '{old_intention}' → '{intention.intention_type}'")
                return intention

            # ❌ ERROR SI NO SE PUEDE MAPEAR
            self.logger.error(f"❌ [MASTER] Intención no reconocida: {intention_type}")
            self.logger.error(f"❌ Intenciones válidas: {valid_intentions}")

            # Fallback a consulta_alumnos para mantener funcionalidad
            self.logger.info(f"🔧 [MASTER] Fallback: '{intention_type}' → 'consulta_alumnos'")
            intention.intention_type = "consulta_alumnos"
            return intention

        except Exception as e:
            self.logger.error(f"❌ Error validando intención: {e}")
            return intention

    def _delegate_to_specialist_direct(self, context: InterpretationContext, intention, current_pdf=None):
        """🎯 DELEGAR AL ESPECIALISTA CON CONTEXTO COMPLETO"""
        try:


            # Agregar información de intención consolidada al contexto
            context.intention_info = {
                'intention_type': intention.intention_type,
                'sub_intention': intention.sub_intention,
                'confidence': intention.confidence,
                'reasoning': intention.reasoning,
                'detected_entities': intention.detected_entities,
                # 🆕 CATEGORIZACIÓN ESPECÍFICA CONSOLIDADA
                'categoria': intention.categoria,
                'sub_tipo': intention.sub_tipo,
                'complejidad': intention.complejidad,
                'requiere_contexto': intention.requiere_contexto,
                'flujo_optimo': intention.flujo_optimo
            }

            # 🧠 [MASTER] Delegando a Student con instrucciones claras

            # 🎯 DELEGACIÓN CONSOLIDADA - Elimina duplicación masiva
            return self._execute_delegation_unified(intention, context, current_pdf=current_pdf)

        except Exception as e:
            self.logger.error(f"❌ Error delegando al especialista: {e}")
            # 🧹 SIN FALLBACKS - Que falle claramente para debugging
            raise

    def _execute_delegation_unified(self, intention, context: InterpretationContext, current_pdf=None):
        """
        🎯 DELEGACIÓN UNIFICADA - Elimina duplicación masiva de código

        Consolida la lógica de delegación que estaba duplicada 4 veces.
        Mantiene 100% la funcionalidad original pero sin repetición.
        """
        try:
            intention_type = intention.intention_type

            # 🎯 MAPEO DE INTENCIONES A ESPECIALISTAS
            specialist_map = {
                "consulta_alumnos": {
                    "interpreter": self.student_interpreter,
                    "name": "StudentQueryInterpreter",
                    "description": ""
                },
                "transformacion_pdf": {
                    "interpreter": self.student_interpreter,
                    "name": "StudentQueryInterpreter",
                    "description": " (transformación PDF)"
                },
                "ayuda_sistema": {
                    "interpreter": self.help_interpreter,
                    "name": "HelpInterpreter",
                    "description": ""
                },
                "conversacion_general": {
                    "interpreter": self.general_interpreter,
                    "name": "GeneralInterpreter",
                    "description": " (conversación natural)"
                }
            }

            # 🎯 OBTENER ESPECIALISTA PARA LA INTENCIÓN
            specialist_config = specialist_map.get(intention_type)
            if not specialist_config:
                self.logger.error(f"❌ [MASTER] Intención no reconocida: {intention_type}")
                raise ValueError(f"Intención no reconocida: {intention_type}")

            # 🎯 LOGS UNIFICADOS (MISMA ESTRUCTURA QUE ANTES)
            specialist_name = specialist_config["name"]
            description = specialist_config["description"]
            self.logger.info(f"🎯 [MASTER] Dirigiendo a {specialist_name}{description}")
            self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
            self.logger.info(f"   └── Entidades: {len(intention.detected_entities)} detectadas")

            # 🎯 EJECUTAR DELEGACIÓN
            specialist = specialist_config["interpreter"]
            # Verificar si el specialist acepta current_pdf
            if hasattr(specialist, 'interpret'):
                import inspect
                sig = inspect.signature(specialist.interpret)
                if 'current_pdf' in sig.parameters:
                    result = specialist.interpret(context, current_pdf=current_pdf)
                else:
                    result = specialist.interpret(context)
            else:
                result = specialist.interpret(context)
            self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")

            # 🎯 MASTER COMO VOCERO: Generar respuesta final (IGUAL QUE ANTES)
            if result:
                final_result = self._generate_master_response(result, context.user_message)
                self.logger.info(f"🗣️ [MASTER] Respuesta final generada como vocero")
                return final_result

            return result

        except Exception as e:
            self.logger.error(f"❌ Error en delegación unificada: {e}")
            raise

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

    def _handle_ambiguous_query(self, context: InterpretationContext, intention) -> Optional[InterpretationResult]:
        """
        🤔 MANEJA CONSULTAS AMBIGUAS - PIDE ACLARACIÓN AL USUARIO DE FORMA SIMPLE
        """
        try:
            self.logger.info("🤔 [MASTER] Consulta ambigua detectada - pidiendo aclaración simple")

            # Crear respuesta de aclaración simple
            from app.core.ai.interpretation.base_interpreter import InterpretationResult

            human_response = f"🤔 Tu consulta '{context.user_message}' no es lo suficientemente clara para mí. ¿Podrías ser más específico sobre qué información necesitas?"

            return InterpretationResult(
                action="aclaracion_requerida",
                parameters={
                    "message": human_response,
                    "original_query": context.user_message,
                    "human_response": human_response
                },
                confidence=intention.confidence
            )

        except Exception as e:
            self.logger.error(f"❌ Error manejando consulta ambigua: {e}")
            return None



    def _get_specialist_for_intention(self, intention_type: str) -> str:
        """🎯 OBTENER ESPECIALISTA PARA INTENCIÓN"""
        for specialist, config in self.system_map.items():
            if intention_type in config["handles"]:
                return specialist
        return "Unknown"

    def _should_ask_user_about_results(self, result: 'InterpretationResult', user_query: str) -> bool:
        """
        🧠 MASTER ANALIZA RESULTADOS: ¿Debería preguntar al usuario?
        Decide si los resultados del Student requieren aclaración del usuario
        """
        try:
            if not result or not result.parameters:
                return False

            row_count = result.parameters.get('row_count', 0)
            action = result.action

            # 🚨 CASOS DONDE EL MASTER DEBERÍA PREGUNTAR:

            # 1. Constancias con múltiples candidatos
            if 'constancia' in user_query.lower() and row_count > 1:
                self.logger.info(f"🔄 [MASTER] Constancia con {row_count} candidatos - necesita selección")
                return True

            # 2. Búsquedas muy amplias (más de 50 resultados)
            if 'buscar' in user_query.lower() and row_count > 50:
                self.logger.info(f"🔄 [MASTER] Búsqueda muy amplia ({row_count} resultados) - ofrecer filtros")
                return True

            # 3. Sin resultados - ofrecer ayuda
            if row_count == 0:
                self.logger.info(f"🔄 [MASTER] Sin resultados - ofrecer alternativas")
                return True

            # Para búsquedas normales como "buscar garcia" con 21 resultados: NO preguntar
            self.logger.info(f"🔄 [MASTER] Resultados normales ({row_count}) - mostrar directamente")
            return False

        except Exception as e:
            self.logger.error(f"Error analizando si preguntar al usuario: {e}")
            return False

    def _handle_results_analysis(self, context, intention, result: 'InterpretationResult') -> 'InterpretationResult':
        """
        🧠 MASTER MANEJA ANÁLISIS DE RESULTADOS
        Procesa los resultados del Student y decide qué preguntar al usuario
        """
        try:
            self.logger.info("🔄 [MASTER] Analizando resultados para comunicación")

            row_count = result.parameters.get('row_count', 0)
            user_query = context.user_message

            # Determinar tipo de pregunta basado en los resultados
            if 'constancia' in user_query.lower() and row_count > 1:
                return self._create_candidate_selection_question(result, context)
            elif 'buscar' in user_query.lower() and row_count > 50:
                return self._create_filter_suggestion_question(result, context)
            elif row_count == 0:
                return self._create_no_results_help_question(result, context)
            else:
                # No debería llegar aquí, pero por seguridad
                return result

        except Exception as e:
            self.logger.error(f"Error analizando resultados: {e}")
            return result

    def _create_candidate_selection_question(self, result: 'InterpretationResult', context) -> 'InterpretationResult':
        """Crea pregunta para seleccionar candidato para constancia"""
        try:
            data = result.parameters.get('data', [])
            candidates = []

            if isinstance(data, list):
                for item in data[:5]:  # Máximo 5 candidatos
                    candidates.append({
                        'nombre': item.get('nombre', 'N/A'),
                        'grado': f"{item.get('grado', 'N/A')}°{item.get('grupo', '')}"
                    })
            elif isinstance(data, dict):
                # Si data es un diccionario, tratarlo como un solo candidato
                candidates.append({
                    'nombre': data.get('nombre', 'N/A'),
                    'grado': f"{data.get('grado', 'N/A')}°{data.get('grupo', '')}"
                })

            message = f"🔍 Encontré {len(data)} candidatos para la constancia. ¿Cuál necesitas?\n\n"
            for i, candidate in enumerate(candidates, 1):
                message += f"**{i}.** {candidate['nombre']} ({candidate['grado']})\n"

            message += f"\n💡 Responde con el número de la opción que necesitas."

            return InterpretationResult(
                action="solicitar_seleccion_constancia",
                parameters={
                    "message": message,
                    "candidates": candidates,
                    "original_query": context.user_message,
                    "waiting_for": "selection",
                    "original_data": data
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error creando pregunta de selección: {e}")
            return result

    def _create_filter_suggestion_question(self, result: 'InterpretationResult', context) -> 'InterpretationResult':
        """Crea pregunta para sugerir filtros en búsquedas amplias"""
        try:
            row_count = result.parameters.get('row_count', 0)

            message = f"🔍 Encontré {row_count} resultados. ¿Buscabas a todos o necesitas filtrar por algo específico como grado, grupo o turno?"

            return InterpretationResult(
                action="solicitar_filtros",
                parameters={
                    "message": message,
                    "original_query": context.user_message,
                    "result_count": row_count,
                    "waiting_for": "filter_specification",
                    "original_data": result.parameters.get('data', [])
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error creando pregunta de filtros: {e}")
            return result

    def _create_no_results_help_question(self, result: 'InterpretationResult', context) -> 'InterpretationResult':
        """Crea pregunta de ayuda cuando no hay resultados"""
        try:
            message = f"🤔 No encontré resultados para '{context.user_message}'. ¿Quieres que busque con otros criterios o necesitas ayuda?"

            return InterpretationResult(
                action="solicitar_ayuda_busqueda",
                parameters={
                    "message": message,
                    "original_query": context.user_message,
                    "waiting_for": "search_help"
                },
                confidence=0.8
            )

        except Exception as e:
            self.logger.error(f"Error creando pregunta de ayuda: {e}")
            return result

    def _log_strategic_context(self):
        """🧠 [MASTER] Contexto estratégico del sistema"""
        try:
            self.logger.info("🧠 [MASTER] Sistema Master-Student inicializado")
            self.logger.info(f"🧠 [MASTER] Especialistas disponibles: {list(self.system_map.keys())}")
            self.logger.info("🧠 [MASTER] Listo para procesar consultas")



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

    def _generate_master_response(self, student_result: 'InterpretationResult', user_query: str) -> 'InterpretationResult':
        """
        🎯 MASTER COMO VOCERO: Genera respuesta final basada en reporte del Student

        Args:
            student_result: Resultado técnico del Student
            user_query: Consulta original del usuario

        Returns:
            InterpretationResult con respuesta final del Master
        """
        try:
            self.logger.info("🗣️ [MASTER] Generando respuesta final como vocero...")

            # Extraer datos técnicos del Student
            student_data = student_result.parameters
            action_used = student_result.action

            # 🔧 DEBUG: Mostrar reporte recibido del Student
            self._debug_pause("📥 [MASTER] RECIBIENDO REPORTE DEL STUDENT", {
                "action_recibida": action_used,
                "datos_tecnicos": list(student_data.keys()),
                "row_count": student_data.get('row_count', 0),
                "requiere_respuesta_master": student_data.get('requires_master_response', False),
                "sql_ejecutado": student_data.get('sql_executed', '')[:50] + "..." if student_data.get('sql_executed') else "N/A"
            })

            # 🎯 EXTRAER CRITERIOS DE BÚSQUEDA DINÁMICAMENTE DESPUÉS DE LA EJECUCIÓN
            search_criteria = self._extract_search_criteria_for_display(student_data)

            # 🎯 AGREGAR CRITERIOS A STUDENT_DATA PARA LAS FUNCIONES DE RESPUESTA
            student_data["search_criteria"] = search_criteria

            # 🎯 MASTER GENERA RESPUESTA FINAL USANDO PROMPT ESPECIALIZADO
            self._debug_pause("🧠 [MASTER] INTERPRETANDO REPORTE Y GENERANDO RESPUESTA", {
                "tipo_consulta": self._detect_query_type(action_used, student_data, user_query),
                "criterios_busqueda": len(search_criteria),
                "datos_disponibles": student_data.get('row_count', 0),
                "prompt_especializado": "Generando respuesta contextual con LLM"
            })

            master_response = self._generate_master_response_with_llm(student_data, user_query, action_used)

            # 🔧 CASOS ESPECIALES QUE REQUIEREN PROCESAMIENTO ADICIONAL
            if action_used == "seleccion_realizada":
                # Respuesta de selección - mostrar datos del elemento seleccionado
                elemento_seleccionado = student_data.get("elemento_seleccionado")
                posicion = student_data.get("posicion", "N/A")

                if elemento_seleccionado:
                    # Preparar datos para mostrar en la interfaz
                    nombre = elemento_seleccionado.get('nombre', 'N/A')
                    master_response = f"👤 Información del alumno en posición {posicion}: **{nombre}**"

                    # Agregar los datos del elemento seleccionado para que se muestren en la interfaz
                    student_data["data"] = [elemento_seleccionado]
                    student_data["row_count"] = 1
                    student_data["human_response"] = master_response
                else:
                    master_response = student_data.get("message", "Selección procesada exitosamente")

            elif action_used == "transformation_preview":
                # 🔄 RESPUESTA ESPECÍFICA PARA TRANSFORMACIONES (mantener por ahora)
                transformation_info = student_data.get("transformation_info", {})
                if transformation_info:
                    tipo_constancia = (transformation_info.get("tipo_constancia") or
                                     transformation_info.get("tipo_transformacion") or
                                     student_data.get("tipo_constancia", "constancia"))
                    alumno_info = (transformation_info.get("alumno") or
                                 student_data.get("alumno", {}))
                    alumno_nombre = alumno_info.get("nombre", "el alumno")

                    master_response = (f"✅ **Transformación completada exitosamente**\n\n"
                                     f"He convertido tu PDF a una constancia de **{tipo_constancia}** para **{alumno_nombre}**.\n\n"
                                     f"📄 **En el panel derecho puedes:**\n\n"
                                     f"Ver la vista previa, comparar con el original, revisar datos extraídos y abrir en navegador para imprimir.\n\n"
                                     f"💡 ¿Necesitas hacer algún ajuste o tienes otra consulta?")

            # 🎯 CREAR RESULTADO FINAL CON RESPUESTA DEL MASTER
            final_result = InterpretationResult(
                action=student_result.action,
                parameters={
                    **student_data,  # Mantener datos técnicos del Student
                    "human_response": master_response,  # Respuesta final del Master
                    "master_generated": True,  # Flag para indicar que Master generó la respuesta
                    "student_action": action_used,  # Acción original del Student
                    "search_criteria": search_criteria,  # 🆕 Criterios para mostrar en listado
                },
                confidence=student_result.confidence
            )

            self.logger.info(f"✅ [MASTER] Respuesta final: '{master_response[:50]}...'")
            return final_result

        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error generando respuesta final: {e}")
            # Fallback: retornar resultado original del Student
            return student_result

    def _extract_search_criteria_for_display(self, student_data: dict) -> dict:
        """🎯 EXTRAE CRITERIOS DE BÚSQUEDA DINÁMICAMENTE DEL SQL EJECUTADO"""
        try:
            # 🧠 [MASTER] Analizando SQL ejecutado para extraer criterios
            sql_query = student_data.get("sql_executed", "") or student_data.get("sql_query", "")
            search_description = ""
            relevant_fields = []

            self.logger.info(f"🧠 [MASTER] SQL encontrado: '{sql_query[:50]}...'" if sql_query else "🧠 [MASTER] No hay SQL disponible")

            if sql_query:
                # Extraer campos de WHERE clause dinámicamente
                import re

                # 🎯 PATRONES COMPLETOS PARA TODOS LOS CRITERIOS POSIBLES
                where_patterns = [
                    # 📅 FECHAS
                    (r'fecha_nacimiento\s+LIKE\s+[\'"]%(\d{4})%[\'"]', 'fecha_nacimiento', 'nacidos en {}'),
                    (r'fecha_nacimiento\s+BETWEEN\s+[\'"](\d{4}-\d{2}-\d{2})[\'"].*[\'"](\d{4}-\d{2}-\d{2})[\'"]', 'fecha_nacimiento', 'nacidos entre {} y {}'),
                    (r'fecha_nacimiento\s*=\s*[\'"]([^\'\"]+)[\'"]', 'fecha_nacimiento', 'nacidos el {}'),

                    # 🎓 DATOS ESCOLARES
                    (r'grado\s*=\s*[\'"](\w+)[\'"]', 'grado', '{}° grado'),
                    (r'grupo\s*=\s*[\'"](\w+)[\'"]', 'grupo', 'grupo {}'),
                    (r'turno\s*=\s*[\'"](\w+)[\'"]', 'turno', 'turno {}'),

                    # 👤 IDENTIFICADORES
                    (r'matricula\s*=\s*[\'"]([^\'\"]+)[\'"]', 'matricula', 'matrícula {}'),
                    (r'curp\s*=\s*[\'"]([^\'\"]+)[\'"]', 'curp', 'CURP {}'),
                    (r'nombre\s+LIKE\s+[\'"]%([^%\'\"]+)%[\'"]', 'nombre', 'con nombre que contiene "{}"'),
                    (r'nombre\s*=\s*[\'"]([^\'\"]+)[\'"]', 'nombre', 'llamado {}'),

                    # 📊 CALIFICACIONES
                    (r'calificaciones\s+IS\s+NOT\s+NULL', 'calificaciones_status', 'con calificaciones'),
                    (r'calificaciones\s+IS\s+NULL', 'calificaciones_status', 'sin calificaciones'),
                    (r'JSON_EXTRACT\([^,]+,\s*[\'"][^\'\"]*promedio[^\'\"]*[\'\"]\)\s*>\s*(\d+(?:\.\d+)?)', 'promedio', 'con promedio mayor a {}'),
                    (r'JSON_EXTRACT\([^,]+,\s*[\'"][^\'\"]*promedio[^\'\"]*[\'\"]\)\s*<\s*(\d+(?:\.\d+)?)', 'promedio', 'con promedio menor a {}'),
                    (r'JSON_EXTRACT\([^,]+,\s*[\'"][^\'\"]*promedio[^\'\"]*[\'\"]\)\s*=\s*(\d+(?:\.\d+)?)', 'promedio', 'con promedio de {}'),

                    # 🏠 DATOS PERSONALES
                    (r'telefono\s*=\s*[\'"]([^\'\"]+)[\'"]', 'telefono', 'con teléfono {}'),
                    (r'direccion\s+LIKE\s+[\'"]%([^%\'\"]+)%[\'"]', 'direccion', 'que viven en {}'),
                    (r'email\s*=\s*[\'"]([^\'\"]+)[\'"]', 'email', 'con email {}'),

                    # 🔢 RANGOS NUMÉRICOS
                    (r'edad\s*>\s*(\d+)', 'edad', 'mayores de {} años'),
                    (r'edad\s*<\s*(\d+)', 'edad', 'menores de {} años'),
                    (r'edad\s*=\s*(\d+)', 'edad', 'de {} años'),
                ]

                for pattern, field, description_template in where_patterns:
                    matches = re.findall(pattern, sql_query, re.IGNORECASE)
                    if matches:
                        relevant_fields.append(field)
                        if isinstance(matches[0], tuple):
                            # Múltiples grupos (ej: BETWEEN)
                            search_description += description_template.format(*matches[0]) + " "
                        else:
                            # Un solo grupo
                            search_description += description_template.format(matches[0]) + " "

                self.logger.info(f"🧠 [MASTER] Criterios extraídos: {len(relevant_fields)} campos")
                if search_description.strip():
                    self.logger.info(f"🧠 [MASTER] Descripción: {search_description.strip()}")

            # Si no hay SQL o no se encontraron patrones, usar fallback inteligente
            if not relevant_fields:
                # Analizar parámetros de la acción como fallback
                action_params = student_data.get("action_params", {})
                criterio_principal = action_params.get("criterio_principal", {})
                campo = criterio_principal.get("campo", "")

                if campo:
                    relevant_fields.append(campo)
                    search_description = f"búsqueda por {campo}"
                    self.logger.info(f"🧠 [MASTER] Campo principal: {campo}")

            # Incluir campos básicos dinámicamente desde configuración
            from app.core.config import Config
            basic_fields = getattr(Config, 'BASIC_DISPLAY_FIELDS', ['nombre', 'curp'])
            all_fields = basic_fields + [field for field in relevant_fields if field not in basic_fields]

            return {
                "fields_to_show": all_fields,
                "search_description": search_description.strip(),
                "has_specific_criteria": len(relevant_fields) > 0
            }

        except Exception as e:
            self.logger.error(f"Error extrayendo criterios dinámicamente: {e}")
            return {
                "fields_to_show": ['nombre', 'curp', 'turno'],  # Fallback por defecto
                "search_description": "",
                "has_specific_criteria": False
            }




    def _generate_master_response_with_llm(self, student_data: dict, user_query: str, action_used: str) -> str:
        """
        🗣️ MASTER GENERA RESPUESTA HUMANIZADA CON CONTEXTO CONVERSACIONAL

        MEJORA: Ahora incluye contexto conversacional para respuestas contextuales
        El Master usa su propio prompt especializado en comunicación para generar
        respuestas humanizadas basándose en los datos técnicos del Student.
        """
        try:
            # 🎯 OBTENER CONTEXTO CONVERSACIONAL COMPLETO (IGUAL QUE MASTER INICIAL)
            conversation_stack = getattr(self, 'current_conversation_stack', [])
            context_info = self._create_context_summary(conversation_stack)

            # Crear prompt con contexto completo
            master_prompt = self._create_master_response_prompt_with_context(
                student_data, user_query, action_used, context_info
            )

            # Llamar al LLM para generar respuesta humanizada
            response = self.gemini_client.send_prompt_sync(master_prompt)

            if response and response.strip():
                self.logger.info(f"✅ Master generó respuesta contextual exitosamente")
                return response.strip()
            else:
                self.logger.warning(f"❌ Master LLM no generó respuesta, usando fallback")
                return self._generate_fallback_response(student_data, action_used)

        except Exception as e:
            self.logger.error(f"Error generando respuesta con Master LLM: {e}")
            return self._generate_fallback_response(student_data, action_used)

    def _generate_fallback_response(self, student_data: dict, action_used: str) -> str:
        """Genera respuesta de fallback si el LLM del Master falla"""
        row_count = student_data.get("row_count", 0)

        if action_used in ["BUSCAR_UNIVERSAL", "GENERAR_LISTADO_COMPLETO"]:
            if row_count == 0:
                return "No encontré resultados para tu búsqueda. ¿Podrías intentar con otros criterios?"
            elif row_count == 1:
                return "Encontré un resultado que coincide con tu búsqueda."
            else:
                return f"Encontré {row_count} resultados que coinciden con tu búsqueda."
        elif action_used in ["CONTAR_ALUMNOS", "CONTAR_UNIVERSAL"]:
            # Extraer el valor real del conteo desde los datos
            data = student_data.get("data", [])
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                total_count = data[0].get("total", row_count)
                return f"El conteo se completó exitosamente: {total_count} elementos."
            else:
                return f"El conteo se completó exitosamente: {row_count} elementos."
        else:
            return "Consulta procesada exitosamente."

    def _create_master_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """
        🎯 CREA PROMPT ESPECIALIZADO DINÁMICO SEGÚN TIPO DE CONSULTA

        Diferentes tipos de consulta requieren diferentes enfoques de respuesta.
        INCLUYE INTERPRETACIÓN INTELIGENTE DEL REPORTE DEL STUDENT.
        """
        # 🧠 INTERPRETACIÓN INTELIGENTE DEL REPORTE
        intelligent_interpretation = self._interpret_student_report_intelligently(student_data, user_query)

        # 🛑 PAUSA ESTRATÉGICA #5: INTERPRETACIÓN INTELIGENTE DEL REPORTE
        import os
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            print(f"\n🛑 [MASTER-BRAIN] PASO 5: INTERPRETACIÓN INTELIGENTE DEL REPORTE")
            print(f"    ├── 🧠 PREGUNTA: ¿Qué pasó y cómo respondo al usuario?")
            print(f"    ├── 📝 Consulta original: '{user_query}'")
            print(f"    ├── ⚡ Acción ejecutada por Student: {action_used}")
            print(f"    ├── 📊 Resultados obtenidos: {student_data.get('row_count', 0)} elementos")
            print(f"    ├── ✅ Éxito de la operación: {student_data.get('success', True)}")
            print(f"    ├── 🧠 Interpretación del conocimiento:")
            print(f"    │   {intelligent_interpretation}")
            print(f"    ├── ⚡ DECISIÓN: Generar respuesta humanizada para el usuario")
            print(f"    └── Presiona ENTER para generar respuesta final...")
            input()

        # Detectar tipo de consulta
        query_type = self._detect_query_type(action_used, student_data, user_query)

        # Crear prompt específico según el tipo
        base_prompt = ""
        if query_type == "search":
            base_prompt = self._create_search_response_prompt(student_data, user_query, action_used)
        elif query_type == "constancia":
            base_prompt = self._create_constancia_response_prompt(student_data, user_query, action_used)
        elif query_type == "transformation":
            base_prompt = self._create_transformation_response_prompt(student_data, user_query, action_used)
        elif query_type == "statistics":
            base_prompt = self._create_statistics_response_prompt(student_data, user_query, action_used)
        elif query_type == "help":
            base_prompt = self._create_help_response_prompt(student_data, user_query, action_used)
        else:
            base_prompt = self._create_generic_response_prompt(student_data, user_query, action_used)

        # 🧠 AGREGAR INTERPRETACIÓN INTELIGENTE AL PROMPT
        enhanced_prompt = f"""
{base_prompt}

🧠 INTERPRETACIÓN INTELIGENTE DEL MASTER:
{intelligent_interpretation}

🎯 INSTRUCCIONES ADICIONALES:
- Usa la interpretación inteligente para mejorar tu respuesta
- Si hay sugerencias, incorpóralas naturalmente
- Si hay limitaciones, explícalas de manera empática
- Mantén un tono profesional pero amigable

RESPONDE ÚNICAMENTE con la respuesta conversacional final mejorada.
"""

        return enhanced_prompt

    def _create_master_response_prompt_with_context(self, student_data: dict, user_query: str, action_used: str, context_info: str) -> str:
        """
        🗣️ MASTER RESPUESTA CON CONTEXTO CONVERSACIONAL

        NUEVO: Prompt de respuesta que incluye contexto conversacional completo
        """
        # Detectar tipo de consulta
        query_type = self._detect_query_type(action_used, student_data, user_query)

        # Crear prompt base según el tipo
        base_prompt = self._create_master_response_prompt(student_data, user_query, action_used)

        # Agregar contexto conversacional al prompt
        contextual_prompt = f"""
🗣️ MASTER COMO VOCERO - RESPUESTA CONTEXTUAL INTELIGENTE

CONTEXTO CONVERSACIONAL:
{context_info}

CONSULTA ORIGINAL: "{user_query}"
RESULTADO DEL STUDENT: {action_used} - {student_data.get('row_count', 0)} resultados

🎯 GENERAR RESPUESTA NATURAL Y CONTEXTUAL:
1. Reconocer contexto conversacional cuando sea relevante
2. Comunicar resultado de manera clara
3. Mantener personalidad consistente
4. Conectar con consultas anteriores cuando sea natural

EJEMPLOS:
- Continuación: "Perfecto! Basándome en [contexto]..."
- Referencia resuelta: "He generado la constancia para [nombre resuelto]..."
- Filtro aplicado: "De los resultados anteriores, encontré..."

{base_prompt}

IMPORTANTE: Si hay contexto conversacional relevante, conéctalo naturalmente en tu respuesta.
"""

        return contextual_prompt

    def _detect_query_type(self, action_used: str, student_data: dict, user_query: str) -> str:
        """Detecta el tipo específico de consulta para usar el prompt correcto"""
        # 🎯 AYUDA DEL SISTEMA (SIMPLIFICADO A 2 ACCIONES)
        if action_used in ["AYUDA_CAPACIDADES", "AYUDA_TUTORIAL"] or student_data.get("query_category") == "ayuda_sistema":
            return "help"

        # Constancias
        if action_used in ["constancia_generada", "PREPARAR_DATOS_CONSTANCIA"] or "constancia" in user_query.lower():
            return "constancia"

        # Transformaciones
        if action_used in ["transformation_completed", "transformation_preview"] or "transform" in user_query.lower():
            return "transformation"

        # Estadísticas
        if action_used in ["CONTAR_ALUMNOS", "CONTAR_UNIVERSAL", "CALCULAR_ESTADISTICA"] or any(word in user_query.lower() for word in ["cuántos", "total", "estadística", "conteo"]):
            return "statistics"

        # Búsquedas (por defecto)
        return "search"

    def _create_search_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """Prompt especializado para búsquedas y listados"""
        row_count = student_data.get("row_count", 0)
        data = student_data.get("data", [])
        ambiguity_level = student_data.get("ambiguity_level", "low")

        # 🎯 MANEJO INTELIGENTE DE "NO ENCONTRADO" (row_count = 0)
        if row_count == 0:
            return self._create_no_results_response_prompt(student_data, user_query, action_used)

        # 🔧 MANEJO SEGURO DE DATOS - verificar que data sea una lista
        data_context = ""
        if data and isinstance(data, list) and len(data) > 0:
            if len(data) <= 3:
                data_context = "RESULTADOS ENCONTRADOS:\n"
                for i, item in enumerate(data, 1):
                    if isinstance(item, dict):
                        # 🎯 MANEJO DINÁMICO DE CAMPOS - usar los campos que realmente existen
                        item_info = []
                        if "nombre" in item:
                            item_info.append(item["nombre"])
                        if "matricula" in item:
                            item_info.append(f"Matrícula: {item['matricula']}")
                        if "grado" in item and "grupo" in item:
                            item_info.append(f"{item['grado']}° {item['grupo']}")
                        elif "grado" in item:
                            item_info.append(f"Grado: {item['grado']}")
                        elif "grupo" in item:
                            item_info.append(f"Grupo: {item['grupo']}")
                        if "curp" in item:
                            item_info.append(f"CURP: {item['curp']}")

                        # Si no hay campos reconocidos, mostrar todos los disponibles
                        if not item_info:
                            item_info = [f"{k}: {v}" for k, v in item.items() if v is not None]

                        data_context += f"{i}. {' - '.join(item_info)}\n"
            else:
                data_context = f"PRIMEROS 3 DE {len(data)} RESULTADOS:\n"
                for i in range(min(3, len(data))):
                    item = data[i]
                    if isinstance(item, dict):
                        # 🎯 MANEJO DINÁMICO DE CAMPOS - usar los campos que realmente existen
                        item_info = []
                        if "nombre" in item:
                            item_info.append(item["nombre"])
                        if "matricula" in item:
                            item_info.append(f"Matrícula: {item['matricula']}")
                        if "grado" in item and "grupo" in item:
                            item_info.append(f"{item['grado']}° {item['grupo']}")
                        elif "grado" in item:
                            item_info.append(f"Grado: {item['grado']}")
                        elif "grupo" in item:
                            item_info.append(f"Grupo: {item['grupo']}")
                        if "curp" in item:
                            item_info.append(f"CURP: {item['curp']}")

                        # Si no hay campos reconocidos, mostrar todos los disponibles
                        if not item_info:
                            item_info = [f"{k}: {v}" for k, v in item.items() if v is not None]

                        data_context += f"{i+1}. {' - '.join(item_info)}\n"

        # Detectar si hay contexto conversacional previo
        reflexion = student_data.get("auto_reflexion", {})
        datos_recordar = reflexion.get("datos_recordar", {})
        conversation_context = datos_recordar.get("context", "")
        query_anterior = datos_recordar.get("query", "")

        # 🎯 MEJORAR DETECCIÓN DE CONTINUACIÓN
        # Verificar múltiples fuentes para detectar continuación
        master_intention = student_data.get("master_intention", {})
        categoria_master = master_intention.get("categoria", "")

        # Es continuación si:
        # 1. Hay contexto conversacional previo, O
        # 2. El Master categorizó como "continuacion", O
        # 3. La consulta tiene palabras de referencia contextual
        palabras_continuacion = ["ellos", "esos", "esas", "de ellos", "de esas", "ahora", "también"]
        tiene_referencia = any(palabra in user_query.lower() for palabra in palabras_continuacion)

        es_continuacion = bool(
            conversation_context or
            query_anterior or
            categoria_master == "continuacion" or
            tiene_referencia
        )

        return f"""
Eres el asistente amigable y entusiasta de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ" 🏫

🎯 SITUACIÓN:
- CONSULTA: "{user_query}"
- RESULTADOS: {row_count} estudiantes encontrados
- AMBIGÜEDAD: {ambiguity_level}
- ES CONTINUACIÓN: {es_continuacion}
- CONTEXTO PREVIO: {conversation_context}
- CONSULTA ANTERIOR: {query_anterior}

{data_context}

🎭 TU PERSONALIDAD:
- Entusiasta y humano (usa emojis apropiados)
- Profesional pero cercano
- Empático y comprensivo
- Proactivo en sugerencias

🎯 TU TAREA PARA BÚSQUEDAS:
Generar una respuesta HUMANA y CONECTADA que:

1. 🎉 SALUDA con entusiasmo apropiado
2. 📊 PRESENTA los resultados de manera atractiva
3. 🔍 EXPLICA qué buscaste de forma natural
4. 🤔 MANEJA la ambigüedad con empatía
5. 💡 SUGIERE próximos pasos útiles
6. 🔄 CONECTA con el contexto conversacional si existe

🎯 MANEJO DE AMBIGÜEDAD CON EMPATÍA:
- HIGH (10+ resultados): "¡Encontré muchos estudiantes! 😊 Como [apellido] es común, te muestro todos para que encuentres al que necesitas. ¿Podrías ser más específico con el nombre o grado?"
- MEDIUM (4-9 resultados): "¡Perfecto! 👍 Encontré varios estudiantes que coinciden. ¿Necesitas información específica de alguno?"
- LOW (1-3 resultados): "¡Excelente! ✅ Aquí tienes [lo que encontré]..."

🔄 CONTINUIDAD CONVERSACIONAL (MUY IMPORTANTE):
- Si ES_CONTINUACIÓN = True: NUNCA digas "¡Hola!" - usa "¡Perfecto! 👍", "¡Excelente! ✅", "Siguiendo con tu búsqueda anterior..."
- Si ES_CONTINUACIÓN = False: Puedes saludar con "¡Hola! 👋"
- SIEMPRE conecta con la consulta anterior cuando hay contexto
- Menciona específicamente qué filtros se aplicaron sobre los datos previos

✅ ENFOQUE HUMANO:
- Resultados presentados con entusiasmo
- Criterios explicados naturalmente
- Sugerencias útiles y empáticas
- Tono conversacional y amigable

📝 FORMATO HUMANO:
- Saludo apropiado con emoji
- Máximo 3-4 líneas pero con personalidad
- Cierre que invite a continuar la conversación

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _create_no_results_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """
        🎯 PROMPT ESPECIALIZADO PARA CASOS DE "NO ENCONTRADO" (row_count = 0)

        Master interpreta inteligentemente cuando Student reporta 0 resultados
        y genera respuestas humanas con sugerencias útiles.
        """
        # Detectar tipo de búsqueda para respuesta específica
        search_criteria = student_data.get("search_criteria", "")

        # Detectar si es búsqueda por CURP
        is_curp_search = "curp" in user_query.lower() or "curp" in search_criteria.lower()

        # Detectar si es búsqueda por matrícula
        is_matricula_search = "matrícula" in user_query.lower() or "matricula" in user_query.lower()

        # Detectar si es búsqueda por nombre
        is_name_search = any(word in user_query.lower() for word in ["buscar", "encontrar", "dame", "información"]) and not is_curp_search and not is_matricula_search

        # Detectar contexto conversacional
        reflexion = student_data.get("auto_reflexion", {})
        datos_recordar = reflexion.get("datos_recordar", {})
        conversation_context = datos_recordar.get("context", "")
        es_continuacion = bool(conversation_context)

        return f"""
Eres el asistente empático y útil de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ" 🏫

🎯 SITUACIÓN CRÍTICA - NO SE ENCONTRARON RESULTADOS:
- CONSULTA: "{user_query}"
- CRITERIOS BUSCADOS: {search_criteria}
- RESULTADOS: 0 estudiantes encontrados
- ES CONTINUACIÓN: {es_continuacion}
- CONTEXTO PREVIO: {conversation_context}
- BÚSQUEDA POR CURP: {is_curp_search}
- BÚSQUEDA POR MATRÍCULA: {is_matricula_search}
- BÚSQUEDA POR NOMBRE: {is_name_search}

🎭 TU PERSONALIDAD EMPÁTICA:
- Comprensivo y útil (NO frustrante)
- Profesional pero humano
- Proactivo en soluciones
- Educativo sin ser condescendiente

🎯 TU TAREA ESPECÍFICA PARA "NO ENCONTRADO":
Generar una respuesta EMPÁTICA Y ÚTIL que:

1. 🤔 RECONOCE que no encontraste nada (sin culpar al usuario)
2. 💡 EXPLICA posibles causas de manera educativa
3. 🔍 SUGIERE alternativas específicas y útiles
4. 🎯 OFRECE próximos pasos concretos
5. 🔄 MANTIENE continuidad conversacional si existe

🎯 RESPUESTAS ESPECÍFICAS POR TIPO DE BÚSQUEDA:

**Para BÚSQUEDAS POR CURP:**
- "No encontré ningún alumno con esa CURP en nuestra base de datos."
- "Las CURPs tienen exactamente 18 caracteres. ¿Podrías verificar que esté completa?"
- "También puedes buscar por nombre si prefieres: 'buscar [nombre del alumno]'"

**Para BÚSQUEDAS POR MATRÍCULA:**
- "No encontré esa matrícula en nuestros registros."
- "¿Podrías verificar el número? También puedes buscar por nombre del alumno."

**Para BÚSQUEDAS POR NOMBRE:**
- "No encontré ningún alumno con ese nombre."
- "¿Podrías intentar con el apellido? Por ejemplo: 'buscar García'"
- "O puedes ser más específico: 'buscar María García de 3er grado'"

🔄 CONTINUIDAD CONVERSACIONAL:
- Si ES_CONTINUACIÓN = True: "Siguiendo con tu búsqueda anterior, no encontré..."
- Si ES_CONTINUACIÓN = False: "No encontré..."
- SIEMPRE ofrecer alternativas basadas en el contexto

✅ PATRONES DE RESPUESTA EMPÁTICA:
- "No encontré [lo que buscaste], pero puedes intentar..."
- "Hmm, no hay resultados para [criterio]. ¿Te ayudo de otra forma?"
- "No localicé [lo específico]. ¿Quieres que busque por [alternativa]?"

❌ EVITA RESPUESTAS TÉCNICAS O FRÍAS:
- "0 resultados encontrados"
- "La consulta no devolvió datos"
- "No hay coincidencias en la base de datos"

📝 FORMATO EMPÁTICO Y ÚTIL:
- Reconocimiento empático del problema
- Explicación breve y educativa
- 2-3 sugerencias concretas y específicas
- Invitación amigable a continuar
- Máximo 4-5 líneas con personalidad humana

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _create_constancia_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """Prompt especializado para constancias generadas"""
        # 🔧 MANEJO SEGURO DE DATOS - puede ser lista o string
        data = student_data.get("data", [])
        if isinstance(data, list) and len(data) > 0:
            alumno_data = data[0]
        elif isinstance(data, dict):
            alumno_data = data
        else:
            alumno_data = {}

        # Obtener nombre del alumno de múltiples fuentes posibles
        alumno_nombre = (
            alumno_data.get("nombre") or
            student_data.get("alumno", {}).get("nombre") if isinstance(student_data.get("alumno"), dict) else
            student_data.get("alumno") if isinstance(student_data.get("alumno"), str) else
            "el estudiante"
        )

        tipo_constancia = student_data.get("tipo_constancia", "constancia")

        # Detectar contexto conversacional
        reflexion = student_data.get("reflexion_conversacional", {})
        conversation_context = reflexion.get("datos_recordar", {}).get("context", "")

        return f"""
Eres el asistente amigable y entusiasta de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ" 🏫

🎯 SITUACIÓN:
- CONSTANCIA GENERADA: {tipo_constancia}
- PARA ESTUDIANTE: {alumno_nombre}
- CONSULTA ORIGINAL: "{user_query}"
- CONTEXTO PREVIO: {conversation_context}

🎭 TU PERSONALIDAD:
- Entusiasta y celebrativo (usa emojis de éxito)
- Profesional pero cercano
- Guía claro y útil
- Empático y comprensivo

🎯 TU TAREA PARA CONSTANCIAS:
Generar una respuesta HUMANA y CELEBRATIVA que:

1. 🎉 CELEBRA el éxito de la generación
2. 📱 EXPLICA el panel derecho de manera amigable
3. 🎛️ MENCIONA botones específicos útiles
4. 💡 GUÍA próximos pasos claramente
5. 🔄 CONECTA con contexto conversacional si existe

🎛️ FUNCIONALIDADES DEL PANEL (explica amigablemente):
- Botón superior izquierdo: "puedes abrir/cerrar el panel"
- Vista previa: "visor PDF con zoom para revisar tu constancia"
- "Ver datos del alumno": "revisa la información extraída"
- "Quitar PDF": "si quieres subir otro documento"
- "Abrir navegador/imprimir": "para guardar o imprimir"
- IMPORTANTE: "Solo vista previa - para guardar usa el navegador"

🔄 CONTINUIDAD CONVERSACIONAL:
- Si hay contexto previo, reconócelo: "¡Perfecto! Siguiendo con [contexto]..."
- Si es nueva constancia, celebra: "¡Excelente! 🎉"
- Siempre invita a continuar: "¿Necesitas algo más?"

📝 FORMATO HUMANO Y CELEBRATIVO:
- Confirmación entusiasta con emojis
- Explicación clara pero amigable del panel
- Máximo 4-5 líneas con personalidad
- Cierre que invite a continuar

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _create_transformation_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """Prompt especializado para transformaciones de PDF"""
        transformation_info = student_data.get("transformation_info", {})
        tipo_constancia = transformation_info.get("tipo_constancia", "constancia")
        alumno_info = transformation_info.get("alumno", {})
        alumno_nombre = alumno_info.get("nombre", "el alumno")

        return f"""
Eres el asistente de la escuela especializado en TRANSFORMACIÓN DE PDFs.

🎯 SITUACIÓN:
- TRANSFORMACIÓN COMPLETADA: PDF → {tipo_constancia}
- PARA ESTUDIANTE: {alumno_nombre}
- CONSULTA ORIGINAL: "{user_query}"

🎯 TU TAREA ESPECÍFICA PARA TRANSFORMACIONES:
Generar una respuesta ENFOCADA EN COMPARACIÓN que:

1. ✅ CONFIRME que la transformación se completó
2. 🔄 EXPLIQUE las funciones de comparación
3. 📱 MENCIONE botones específicos de transformación
4. 💡 GUÍE sobre cómo comparar y decidir

🔄 FUNCIONALIDADES ESPECÍFICAS DE TRANSFORMACIÓN:
- Todo lo del panel normal MÁS:
- "Ver PDF original": muestra el que subiste
- "Ver PDF transformado": muestra el resultado
- Comparación rápida: alternar entre ambos
- Misma lógica: solo vista previa, guardar desde navegador

📝 FORMATO PARA TRANSFORMACIONES:
- Confirmación de transformación exitosa
- Explicación de comparación
- Guía para decidir próximos pasos
- Máximo 4-5 líneas

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _create_statistics_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """Prompt especializado para estadísticas y conteos"""
        row_count = student_data.get("row_count", 0)

        # 🔍 DEBUG: Analizar datos recibidos del Student
        data = student_data.get("data", [])
        self.logger.info(f"🔍 [MASTER-STATS] Analizando datos del Student:")
        self.logger.info(f"    ├── row_count: {row_count}")
        self.logger.info(f"    ├── data type: {type(data)}")
        self.logger.info(f"    ├── data length: {len(data) if isinstance(data, list) else 'N/A'}")
        if isinstance(data, list) and len(data) > 0:
            self.logger.info(f"    ├── data[0]: {data[0]}")
            self.logger.info(f"    └── data[0] keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")

        # 🎯 DETECTAR TIPO DE ESTADÍSTICA BASADO EN ESTRUCTURA DE DATOS
        is_distribution = False
        total_sum = 0

        if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            # 🎯 DETECTAR DISTRIBUCIONES: múltiples registros con campo de agrupación + cantidad
            distribution_fields = ['grado', 'grupo', 'turno', 'ciclo_escolar']
            has_distribution_field = any(field in data[0] for field in distribution_fields)
            has_cantidad = 'cantidad' in data[0]

            if len(data) > 1 and has_distribution_field and has_cantidad:
                is_distribution = True
                total_sum = sum(item.get('cantidad', 0) for item in data)

                # Detectar tipo de distribución
                distribution_type = next((field for field in distribution_fields if field in data[0]), 'campo')
                self.logger.info(f"🔍 [MASTER-STATS] DISTRIBUCIÓN detectada: {len(data)} {distribution_type}s, {total_sum} alumnos total")
            else:
                # Conteo simple
                actual_count = data[0].get("total", row_count)
                self.logger.info(f"🔍 [MASTER-STATS] CONTEO SIMPLE: {actual_count}")
        else:
            actual_count = row_count
            self.logger.info(f"🔍 [MASTER-STATS] usando row_count como actual_count: {actual_count}")

        # Preparar datos para el prompt
        if is_distribution:
            # Para distribuciones, usar datos completos
            distribution_summary = f"{len(data)} grados con {total_sum} alumnos total"
            self.logger.info(f"🔍 [MASTER-STATS] Resumen distribución: {distribution_summary}")
        else:
            # Para conteos simples, usar valor individual
            total_alumnos = 211  # Valor conocido de la base de datos
            porcentaje = round((actual_count / total_alumnos) * 100, 1) if total_alumnos > 0 else 0

        if is_distribution:
            # 🎯 DETECTAR TIPO DE DISTRIBUCIÓN (SIN INCLUIR DATOS EN EL PROMPT)
            distribution_type = next((field for field in ['grado', 'grupo', 'turno', 'ciclo_escolar'] if field in data[0]), 'campo')

            return f"""
Eres el asistente amigable y entusiasta de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ" 🏫

🎯 SITUACIÓN:
- CONSULTA: "{user_query}"
- TIPO: DISTRIBUCIÓN por {distribution_type}s
- RESULTADOS: {len(data)} {distribution_type}s diferentes
- TOTAL ALUMNOS: {total_sum} estudiantes

🎭 TU PERSONALIDAD:
- Entusiasta y humano (usa emojis apropiados)
- Profesional pero cercano
- Empático y comprensivo
- Celebra los datos interesantes

🎯 TU TAREA PARA DISTRIBUCIONES:
Generar una respuesta HUMANA y ENTUSIASTA que:

1. 🎉 SALUDA con entusiasmo apropiado
2. 📊 PRESENTA la distribución de manera atractiva
3. 🔢 DESTACA datos interesantes (total de estudiantes y categorías)
4. 💡 INVITA a ver los detalles visuales abajo

✅ PATRONES DE RESPUESTA HUMANA:
- "¡Perfecto! 📊 Aquí tienes la distribución..."
- "¡Excelente consulta! 👍 Te muestro cómo se distribuyen..."
- "¡Genial! 🎯 Los {total_sum} estudiantes se reparten en {len(data)} categorías..."
- "¡Qué buena pregunta! 🤩 Aquí está la información..."

❌ EVITA LENGUAJE TÉCNICO:
- "La distribución de alumnos por [campo] nos muestra..."
- "Los datos detallados se presentan a continuación"
- "Tenemos un total de X [categorías] distintos"

📝 FORMATO HUMANO Y ENTUSIASTA:
- Saludo entusiasta con emoji apropiado
- Presentación natural de los números clave
- Invitación amigable a explorar los detalles
- Máximo 2-3 líneas con personalidad auténtica
- Adapta el lenguaje al tipo de distribución automáticamente

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""
        else:
            return f"""
Eres el asistente de la escuela especializado en ESTADÍSTICAS Y CONTEOS.

🎯 SITUACIÓN:
- CONSULTA: "{user_query}"
- RESULTADO: {actual_count} alumnos
- PORCENTAJE: {porcentaje}% del total ({total_alumnos} alumnos)
- TIPO: Conteo simple

🎯 TU TAREA ESPECÍFICA PARA CONTEOS:
Generar una respuesta ENFOCADA EN NÚMEROS que:

1. 📊 PRESENTE el resultado claramente
2. 🔍 CONTEXTUALICE el número (qué significa)
3. 💡 SUGIERA análisis relacionados
4. 🎯 MANTENGA enfoque en datos

📝 FORMATO CONCISO:
- Resultado directo
- Contexto breve
- Máximo 2-3 líneas

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _create_generic_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """Prompt genérico para casos no específicos"""
        message = student_data.get("message", "Consulta procesada exitosamente")

        return f"""
Eres el asistente de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ".

🎯 SITUACIÓN:
- CONSULTA: "{user_query}"
- ACCIÓN: {action_used}
- MENSAJE: {message}

🎯 TU TAREA:
Generar una respuesta profesional y útil basada en la información disponible.

📝 FORMATO:
- Respuesta clara y directa
- Tono profesional pero amigable
- Máximo 2-3 líneas

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _create_help_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """Prompt especializado para respuestas de ayuda del sistema"""
        help_data = student_data.get("data", {})
        help_type = help_data.get("tipo", "ayuda_general")
        titulo = help_data.get("titulo", "Ayuda del Sistema")
        contenido = help_data.get("contenido", {})

        # 🎯 EXTRAER INFORMACIÓN ESPECÍFICA DEL HELPINTERPRETER
        info_especifica = ""
        if help_type == "capacidades_sistema":
            # 🎯 EXTRAER TODAS LAS CAPACIDADES DETALLADAS
            busquedas_apellido = contenido.get("busquedas_por_apellido", {})
            busquedas_nombre = contenido.get("busquedas_por_nombre_completo", {})
            busquedas_criterios = contenido.get("busquedas_por_criterios_academicos", {})
            constancias = contenido.get("constancias_pdf_completas", {})
            estadisticas = contenido.get("estadisticas_y_conteos", {})
            continuaciones = contenido.get("continuaciones_contextuales", {})
            filtros_calif = contenido.get("filtros_de_calificaciones", {})

            info_especifica = f"""
📊 CAPACIDADES COMPLETAS DEL SISTEMA (PROBADAS):

🔍 **BÚSQUEDAS POR APELLIDO**: {busquedas_apellido.get('descripcion', '')}
  Ejemplos: {', '.join(busquedas_apellido.get('ejemplos_reales', [])[:2])}

👤 **BÚSQUEDAS POR NOMBRE COMPLETO**: {busquedas_nombre.get('descripcion', '')}
  Ejemplos: {', '.join(busquedas_nombre.get('ejemplos_reales', [])[:2])}

🎓 **BÚSQUEDAS POR CRITERIOS ACADÉMICOS**: {busquedas_criterios.get('descripcion', '')}
  Ejemplos: {', '.join(busquedas_criterios.get('ejemplos_reales', [])[:2])}

📄 **CONSTANCIAS PDF**: {constancias.get('descripcion', '')}
  Ejemplos: {', '.join(constancias.get('ejemplos_reales', [])[:2])}

📊 **ESTADÍSTICAS Y CONTEOS**: {estadisticas.get('descripcion', '')}
  Ejemplos: {', '.join(estadisticas.get('ejemplos_reales', [])[:2])}

🔄 **CONTINUACIONES CONTEXTUALES**: {continuaciones.get('descripcion', '')}
  Ejemplo: {continuaciones.get('ejemplos_reales', [''])[0] if continuaciones.get('ejemplos_reales') else ''}

📝 **FILTROS DE CALIFICACIONES**: {filtros_calif.get('descripcion', '')}
  Ejemplos: {', '.join(filtros_calif.get('ejemplos_reales', [])[:2])}
"""

        elif help_type == "tutorial_uso":
            pasos = contenido.get("pasos", [])
            consejos = contenido.get("consejos", [])

            pasos_info = ""
            for paso in pasos[:4]:  # Máximo 4 pasos
                titulo = paso.get("titulo", "")
                descripcion = paso.get("descripcion", "")
                ejemplos = paso.get("ejemplos_reales", [])
                pasos_info += f"- {titulo}: {descripcion}\n  Ejemplos: {', '.join(ejemplos[:2])}\n"

            info_especifica = f"""
📚 TUTORIAL PASO A PASO - CASOS REALES PROBADOS:
{pasos_info}
💡 CONSEJOS IMPORTANTES:
{chr(10).join(consejos[:3])}
"""

        # 🗑️ TIPOS ELIMINADOS - SOLO MANTENEMOS CAPACIDADES Y TUTORIAL

        return f"""
Eres el asistente amigable y experto de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ" 🏫

🎯 SITUACIÓN:
- CONSULTA: "{user_query}"
- TIPO DE AYUDA: {help_type}
- ACCIÓN: {action_used}
- TÍTULO: {titulo}

{info_especifica}

🎭 TU TAREA ESPECÍFICA:
Generar una respuesta ÚTIL Y ESPECÍFICA que:

1. 👋 SALUDA de manera apropiada
2. 📚 EXPLICA la información REAL con ejemplos específicos
3. 💡 USA ÚNICAMENTE los ejemplos concretos proporcionados arriba
4. 🎯 INVITA a probar con ejemplos específicos

✅ PATRONES DE RESPUESTA SEGÚN TIPO (SIMPLIFICADO):
**Para capacidades_sistema:**
- "¡Hola! 👋 ¡Perfecto! Te explico qué puedo hacer..."
- "¡Excelente pregunta! 🤔 Estas son mis capacidades principales..."

**Para tutorial_uso:**
- "¡Hola! 👋 ¡Perfecto! Te explico cómo usar el sistema paso a paso..."
- "¡Excelente! 🤔 Aquí tienes un tutorial con casos reales probados..."

📝 FORMATO ESPECÍFICO Y OBLIGATORIO:
- Saludo entusiasta apropiado
- ENUMERA TODAS las capacidades de la información específica arriba
- INCLUYE AL MENOS 1 EJEMPLO de cada tipo de búsqueda/funcionalidad
- MENCIONA los tipos específicos: apellido, nombre completo, criterios académicos, etc.
- USA los nombres reales de los ejemplos (MARTINEZ TORRES, SOPHIA ROMERO GARCIA, etc.)
- Menciona que son casos PROBADOS y validados
- Invitación a probar con ejemplos concretos específicos
- Tono conversacional y humano
- INCLUYE SALTOS DE LÍNEA entre cada capacidad para mejor legibilidad
- Máximo 8-10 líneas para incluir TODOS los tipos

🚨 OBLIGATORIO - INCLUYE TODOS LOS TIPOS CON SALTOS DE LÍNEA:
- BÚSQUEDAS POR APELLIDO: Al menos 1 ejemplo + SALTO DE LÍNEA
- BÚSQUEDAS POR NOMBRE COMPLETO: Al menos 1 ejemplo + SALTO DE LÍNEA
- BÚSQUEDAS POR CRITERIOS ACADÉMICOS: Al menos 1 ejemplo + SALTO DE LÍNEA
- CONSTANCIAS PDF: Al menos 1 ejemplo + SALTO DE LÍNEA
- ESTADÍSTICAS: Al menos 1 ejemplo + SALTO DE LÍNEA
- CONTINUACIONES: Al menos 1 ejemplo + SALTO DE LÍNEA
- FILTROS DE CALIFICACIONES: Al menos 1 ejemplo + SALTO DE LÍNEA
- FORMATEA con números (1., 2., 3., etc.) y SALTO DE LÍNEA después de cada punto

RESPONDE ÚNICAMENTE con la respuesta conversacional final.
"""

    def _detect_user_interaction_needed(self, action_used: str, student_data: dict) -> bool:
        """
        🎯 DETECTA SI EL STUDENT INDICA QUE NECESITA INTERACCIÓN CON EL USUARIO

        Analiza la respuesta del Student para determinar si requiere:
        - Aclaraciones
        - Confirmaciones
        - Selecciones
        - Especificaciones adicionales
        """
        # 1. ACCIONES QUE EXPLÍCITAMENTE REQUIEREN INTERACCIÓN
        interactive_actions = [
            "constancia_requiere_aclaracion",
            "seleccion_requerida",
            "confirmacion_requerida",
            "especificacion_requerida"
        ]

        if action_used in interactive_actions:
            return True

        # 2. VERIFICAR SI EL STUDENT INDICA ESPERA DE CONTINUACIÓN
        reflexion = student_data.get("reflexion_conversacional", {})
        if reflexion.get("espera_continuacion", False):
            continuation_type = reflexion.get("tipo_esperado", "")
            if continuation_type in ["confirmation", "specification", "selection"]:
                return True

        # 3. VERIFICAR PATRONES EN EL MENSAJE QUE INDICAN PREGUNTA
        message = student_data.get("human_response", "")
        question_patterns = [
            "¿cuál necesitas?",
            "¿te refieres a",
            "necesito que especifiques",
            "¿qué tipo de",
            "¿confirmas que",
            "¿estás seguro"
        ]

        for pattern in question_patterns:
            if pattern.lower() in message.lower():
                return True

        return False

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

    # 🧠 MÉTODOS DE CONOCIMIENTO PROFUNDO (FASE 2)

    def _validate_feasibility_with_knowledge(self, intention, user_query: str) -> dict:
        """
        🧠 VALIDAR FACTIBILIDAD CON CONOCIMIENTO PROFUNDO
        Usa MasterKnowledge para evaluar si la consulta es factible
        """
        try:
            query_details = {"original_query": user_query}

            feasibility = self.knowledge.can_handle_request(
                intention.intention_type,
                intention.sub_intention,
                query_details
            )

            if feasibility["can_handle"]:
                self.logger.info(f"✅ [MASTER-KNOWLEDGE] Consulta factible: {feasibility['explanation']}")
                if feasibility["limitations"]:
                    self.logger.info(f"⚠️ [MASTER-KNOWLEDGE] Limitaciones: {feasibility['limitations']}")
            else:
                self.logger.warning(f"❌ [MASTER-KNOWLEDGE] Consulta no factible: {feasibility['explanation']}")
                self.logger.info(f"💡 [MASTER-KNOWLEDGE] Alternativas: {feasibility['alternatives']}")

            return feasibility

        except Exception as e:
            self.logger.error(f"Error validando factibilidad: {e}")
            # Fallback: asumir que es factible
            return {
                "can_handle": True,
                "confidence": 0.5,
                "limitations": [],
                "alternatives": [],
                "explanation": "Validación de factibilidad falló, procediendo con precaución"
            }

    def _create_limitation_response(self, feasibility: dict, user_query: str) -> 'InterpretationResult':
        """
        💡 CREAR RESPUESTA INTELIGENTE CUANDO ALGO NO ES FACTIBLE
        """
        try:
            from app.core.ai.interpretation.base_interpreter import InterpretationResult

            explanation = feasibility.get("explanation", "Esta funcionalidad no está disponible")
            alternatives = feasibility.get("alternatives", [])

            # Crear respuesta empática con alternativas
            response_parts = [
                f"🤔 {explanation}.",
                "",
                "💡 **Pero puedo ayudarte con estas alternativas:**"
            ]

            for i, alternative in enumerate(alternatives, 1):
                response_parts.append(f"{i}. {alternative}")

            if not alternatives:
                response_parts.extend([
                    "",
                    "📋 **Capacidades disponibles:**",
                    "• Buscar información de alumnos",
                    "• Generar estadísticas básicas",
                    "• Crear constancias oficiales",
                    "• Transformar documentos PDF"
                ])

            response_parts.append("\n¿Te gustaría probar alguna de estas opciones? 😊")

            response_text = "\n".join(response_parts)

            self.logger.info(f"💡 [MASTER-KNOWLEDGE] Respuesta de limitación generada")

            return InterpretationResult(
                action="limitation_explanation",
                parameters={
                    "response": response_text,
                    "explanation": explanation,
                    "alternatives": alternatives,
                    "user_query": user_query,
                    "human_response": response_text,
                    "success": True
                },
                confidence=1.0,
                reasoning=f"Consulta no factible: {explanation}"
            )

        except Exception as e:
            self.logger.error(f"Error creando respuesta de limitación: {e}")
            return None

    def _debug_pause(self, title: str, data: dict):
        """Método de debug para mostrar información en --debug-pauses"""
        import os
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            print(f"\n🛑 {title}")
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 3:
                    print(f"    ├── {key}: {value[:3]}... ({len(value)} total)")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"    ├── {key}: {value[:50]}...")
                else:
                    print(f"    ├── {key}: {value}")
            print(f"    └── Presiona ENTER para continuar...")
            input()

    def _interpret_student_report_intelligently(self, student_data: dict, original_query: str) -> str:
        """
        🔍 INTERPRETAR REPORTES DEL STUDENT CON CONOCIMIENTO PROFUNDO
        Usa MasterKnowledge para analizar qué pasó y sugerir mejoras
        """
        try:
            interpretation = self.knowledge.interpret_student_report(student_data, original_query)

            user_explanation = interpretation.get("user_explanation", "")
            suggestions = interpretation.get("suggestions", [])

            self.logger.info(f"🔍 [MASTER-KNOWLEDGE] Interpretación: {interpretation.get('interpretation', '')}")

            if suggestions:
                self.logger.info(f"💡 [MASTER-KNOWLEDGE] Sugerencias: {suggestions}")

            return user_explanation

        except Exception as e:
            self.logger.error(f"Error interpretando reporte del Student: {e}")
            return "Operación completada."
