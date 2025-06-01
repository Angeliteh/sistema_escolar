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

            # 🎯 PROCESAMIENTO CON CONTEXTO CONVERSACIONAL ACTIVADO
            context.conversation_stack = conversation_stack or []
            if context.conversation_stack:
                self.logger.info(f"🎯 [MASTER] Procesando con contexto - {len(context.conversation_stack)} niveles disponibles")
            else:
                self.logger.info("🎯 [MASTER] Procesando consulta individual")

            # PASO 1: DETECTAR INTENCIÓN DIRECTA
            intention = self._detect_intention_direct(context.user_message)

            # 🎯 LOGS DE DEPURACIÓN DE INTENCIÓN CONSOLIDADA
            self.logger.info(f"🎯 [MASTER] INTENCIÓN CONSOLIDADA DETECTADA:")
            self.logger.info(f"   ├── Tipo: {intention.intention_type}")
            self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
            self.logger.info(f"   ├── Confianza: {intention.confidence}")
            self.logger.info(f"   ├── 🆕 Categoría: {intention.categoria}")
            self.logger.info(f"   ├── 🆕 Sub-tipo: {intention.sub_tipo}")
            self.logger.info(f"   ├── 🆕 Complejidad: {intention.complejidad}")
            self.logger.info(f"   ├── 🆕 Requiere contexto: {intention.requiere_contexto}")
            self.logger.info(f"   ├── 🆕 Flujo óptimo: {intention.flujo_optimo}")
            self.logger.info(f"   └── Razonamiento: {intention.reasoning}")

            # PASO 3: VALIDAR INTENCIÓN CON SISTEMA MAP
            validated_intention = self._validate_intention_with_system_map(intention)
            if validated_intention != intention:
                self.logger.info(f"🔧 [MASTER] Intención corregida por system_map")

            # PASO 3: VERIFICAR AMBIGÜEDADES ANTES DE DELEGAR
            ambiguity_check = self._check_for_ambiguities(context.user_message, validated_intention)

            # 🛑 PAUSA ESTRATÉGICA #1: MASTER RAZONAMIENTO INICIAL COMPLETO
            import os
            if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                print(f"\n🛑 [MASTER] ANÁLISIS INICIAL:")
                print(f"    ├── 📝 Consulta: '{context.user_message}'")
                print(f"    ├── 🧠 Intención detectada: {intention.intention_type}/{intention.sub_intention}")
                print(f"    ├── 📊 Confianza: {intention.confidence}")
                print(f"    ├── 🎯 Entidades extraídas: {list(intention.detected_entities.keys())}")
                for key, value in intention.detected_entities.items():
                    if isinstance(value, list) and len(value) > 2:
                        print(f"    │   ├── {key}: {value[:2]}... (+{len(value)-2} más)")
                    else:
                        print(f"    │   ├── {key}: {value}")
                print(f"    ├── 💭 Razonamiento: {intention.reasoning[:100]}...")
                print(f"    ├── 🔍 Necesita clarificación: {ambiguity_check.get('needs_clarification', False)}")
                if ambiguity_check.get('needs_clarification'):
                    print(f"    │   ├── Términos ambiguos: {ambiguity_check.get('ambiguous_terms', [])}")
                    print(f"    │   └── Opciones disponibles: {len(ambiguity_check.get('options', []))}")
                print(f"    └── Presiona ENTER para delegar a Student...")
                input()

            if ambiguity_check.get("needs_clarification"):
                # COMUNICACIÓN BIDIRECCIONAL: Preguntar al usuario
                return self._handle_ambiguous_query(context, validated_intention, ambiguity_check)

            # PASO 4: DIRIGIR AL ESPECIALISTA DIRECTAMENTE (sin ambigüedades)
            result = self._delegate_to_specialist_direct(context, validated_intention)

            # PASO 5: ANALIZAR RESULTADOS Y DECIDIR SI NECESITA COMUNICACIÓN BIDIRECCIONAL
            if result and self._should_ask_user_about_results(result, context.user_message):
                return self._handle_results_analysis(context, validated_intention, result)

            # PASO 6: PROCESAR RETROALIMENTACIÓN DEL ESPECIALISTA
            self._process_specialist_feedback(validated_intention, result)

            return result

        except Exception as e:
            self.logger.error(f"❌ [MASTER] Error en interpretación: {e}")
            return None

    def _detect_intention_direct(self, user_message: str):
        """🎯 DETECTAR INTENCIÓN DIRECTA SIN CONTEXTO"""
        try:
            return self.intention_detector.detect_intention(user_message)
        except Exception as e:
            self.logger.error(f"❌ Error detectando intención: {e}")
            # Fallback básico
            from app.core.ai.interpretation.intention_detector import IntentionResult
            return IntentionResult(
                intention_type="consulta_alumnos",
                sub_intention="busqueda_simple",
                confidence=0.5,
                reasoning="Fallback por error en detección",
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

    def _delegate_to_specialist_direct(self, context: InterpretationContext, intention):
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

            # 🎯 DEBUG ESTRATÉGICO: LO QUE MASTER ENVÍA A STUDENT (CONSOLIDADO)
            self.logger.info("=" * 60)
            self.logger.info("🎯 [DEBUG] MASTER → STUDENT COMMUNICATION (CONSOLIDADO):")
            self.logger.info("=" * 60)
            self.logger.info(f"📤 CONSULTA ORIGINAL: '{context.user_message}'")
            self.logger.info(f"📤 INTENCIÓN DETECTADA: {intention.intention_type}/{intention.sub_intention}")
            self.logger.info(f"📤 CONFIANZA: {intention.confidence}")
            self.logger.info(f"📤 🆕 CATEGORÍA: {intention.categoria}")
            self.logger.info(f"📤 🆕 SUB-TIPO: {intention.sub_tipo}")
            self.logger.info(f"📤 🆕 COMPLEJIDAD: {intention.complejidad}")
            self.logger.info(f"📤 🆕 FLUJO ÓPTIMO: {intention.flujo_optimo}")
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



                # 🎯 MASTER COMO VOCERO: Generar respuesta final
                if result:
                    final_result = self._generate_master_response(result, context.user_message)
                    self.logger.info(f"🗣️ [MASTER] Respuesta final generada como vocero")
                    return final_result

                return result

            elif intention.intention_type == "generar_constancia":
                self.logger.info("🎯 [MASTER] Dirigiendo a StudentQueryInterpreter (constancia)")
                self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
                self.logger.info(f"   └── Entidades: {len(intention.detected_entities)} detectadas")

                result = self.student_interpreter.interpret(context)
                self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")

                # 🎯 MASTER COMO VOCERO: Generar respuesta final
                if result:
                    final_result = self._generate_master_response(result, context.user_message)
                    self.logger.info(f"🗣️ [MASTER] Respuesta final generada como vocero")
                    return final_result

                return result

            elif intention.intention_type == "transformacion_pdf":
                self.logger.info("🎯 [MASTER] Dirigiendo a StudentQueryInterpreter (transformación PDF)")
                self.logger.info(f"   ├── Sub-intención: {intention.sub_intention}")
                self.logger.info(f"   └── Entidades: {len(intention.detected_entities)} detectadas")

                result = self.student_interpreter.interpret(context)
                self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")

                # 🎯 MASTER COMO VOCERO: Generar respuesta final
                if result:
                    final_result = self._generate_master_response(result, context.user_message)
                    self.logger.info(f"🗣️ [MASTER] Respuesta final generada como vocero")
                    return final_result

                return result

            elif intention.intention_type == "ayuda_sistema":
                self.logger.info("🎯 [MASTER] Dirigiendo a HelpInterpreter")
                result = self.help_interpreter.interpret(context)
                self.logger.info(f"📊 [MASTER] Resultado: {result.action if result else 'None'}")

                # 🎯 MASTER COMO VOCERO: Generar respuesta final
                if result:
                    final_result = self._generate_master_response(result, context.user_message)
                    self.logger.info(f"🗣️ [MASTER] Respuesta final generada como vocero")
                    return final_result

                return result

            else:
                # 🧹 SIN FALLBACKS - Que falle claramente para debugging
                self.logger.error(f"❌ [MASTER] Intención no reconocida: {intention.intention_type}")
                raise ValueError(f"Intención no reconocida: {intention.intention_type}")

        except Exception as e:
            self.logger.error(f"❌ Error delegando al especialista: {e}")
            # 🧹 SIN FALLBACKS - Que falle claramente para debugging
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

    def _check_for_ambiguities(self, user_message: str, intention) -> dict:
        """
        🧠 RAZONAMIENTO INTERNO DEL MASTER: Verificar ambigüedades
        Analiza si la consulta es ambigua ANTES de enviar al Student
        """
        try:
            self.logger.info(f"🧠 [MASTER] Verificando ambigüedades en: '{user_message}'")

            # Crear prompt de análisis de ambigüedades
            ambiguity_prompt = self._create_ambiguity_analysis_prompt(user_message, intention)

            # Enviar al LLM para análisis
            response = self.gemini_client.send_prompt_sync(ambiguity_prompt)

            if response:
                ambiguity_data = self._parse_ambiguity_response(response)
                self.logger.info(f"🧠 [MASTER] Análisis de ambigüedad: {ambiguity_data}")
                return ambiguity_data
            else:
                self.logger.warning("⚠️ [MASTER] No se pudo analizar ambigüedad")
                return {"needs_clarification": False}

        except Exception as e:
            self.logger.error(f"❌ Error verificando ambigüedades: {e}")
            return {"needs_clarification": False}

    def _handle_ambiguous_query(self, context, intention, ambiguity_check) -> 'InterpretationResult':
        """
        🔄 COMUNICACIÓN BIDIRECCIONAL: Manejar consulta ambigua
        Pregunta al usuario para aclarar la ambigüedad
        """
        try:
            self.logger.info(f"🔄 [MASTER] Manejando consulta ambigua")

            # Generar pregunta de aclaración
            clarification_question = self._generate_clarification_question(ambiguity_check)

            # Crear resultado que solicita aclaración al usuario
            from app.core.ai.interpretation import InterpretationResult
            return InterpretationResult(
                action="solicitar_aclaracion",
                parameters={
                    "message": clarification_question,
                    "ambiguity_options": ambiguity_check.get("options", []),
                    "original_query": context.user_message,
                    "waiting_for": "clarification",
                    "ambiguity_type": ambiguity_check.get("type", "general")
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"❌ Error manejando consulta ambigua: {e}")
            # Fallback: continuar sin aclaración
            return self._delegate_to_specialist_direct(context, intention)

    def _get_specialist_for_intention(self, intention_type: str) -> str:
        """🎯 OBTENER ESPECIALISTA PARA INTENCIÓN"""
        for specialist, config in self.system_map.items():
            if intention_type in config["handles"]:
                return specialist
        return "Unknown"

    def _create_ambiguity_analysis_prompt(self, user_message: str, intention) -> str:
        """Crea prompt para analizar ambigüedades en la consulta"""
        return f"""
Analiza si esta consulta del usuario es REALMENTE ambigua y requiere aclaración:

CONSULTA: "{user_message}"

INTENCIÓN DETECTADA: {intention.intention_type}
ENTIDADES DETECTADAS: {intention.detected_entities}

CONTEXTO DEL SISTEMA:
- Sistema de gestión escolar
- Campos disponibles: grado (1-6), grupo (A,B,C), turno (MATUTINO/VESPERTINO)

REGLAS IMPORTANTES:
1. **SÉ PERMISIVO**: Solo marca como ambiguo si es REALMENTE confuso
2. **CONSULTAS COMUNES SON CLARAS**: "buscar garcia" = buscar por apellido García (CLARO)
3. **SOLO AMBIGUO SI HAY MÚLTIPLES INTERPRETACIONES VÁLIDAS**: "segundo" puede ser grado 2 o grupo 2
4. **NOMBRES/APELLIDOS SON CLAROS**: García, López, Juan, etc. son búsquedas directas

EJEMPLOS:
- "buscar garcia" → NO ambiguo (buscar apellido García)
- "buscar juan" → NO ambiguo (buscar nombre Juan)
- "alumnos de segundo" → SÍ ambiguo (¿grado 2 o grupo 2?)
- "constancia para juan" → PUEDE ser ambiguo si hay múltiples Juan

ANALIZA:
1. ¿La consulta tiene UNA interpretación obvia y natural?
2. ¿Hay términos que REALMENTE podrían confundir al usuario?
3. ¿Es necesario preguntar o se puede proceder directamente?

RESPONDE EN JSON:
{{
    "needs_clarification": true/false,
    "ambiguous_terms": ["término1", "término2"],
    "type": "field_ambiguity|value_ambiguity|context_ambiguity",
    "options": [
        {{"label": "Opción 1", "value": "valor1", "description": "Descripción"}},
        {{"label": "Opción 2", "value": "valor2", "description": "Descripción"}}
    ],
    "reasoning": "Explicación del análisis"
}}
"""

    def _parse_ambiguity_response(self, response: str) -> dict:
        """Parsea la respuesta del análisis de ambigüedad"""
        try:
            import json
            import re

            # Buscar JSON en la respuesta
            json_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```',
                r'(\{.*?\})'
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, response, re.DOTALL)
                if matches:
                    return json.loads(matches[0])

            # Intentar parseo directo
            return json.loads(response.strip())

        except Exception as e:
            self.logger.error(f"Error parseando respuesta de ambigüedad: {e}")
            return {"needs_clarification": False}

    def _generate_clarification_question(self, ambiguity_check: dict) -> str:
        """Genera pregunta de aclaración para el usuario"""
        try:
            ambiguous_terms = ambiguity_check.get("ambiguous_terms", [])
            options = ambiguity_check.get("options", [])

            if not options:
                return "Tu consulta es un poco ambigua. ¿Podrías ser más específico?"

            question = f"🤔 Tu consulta tiene algunas ambigüedades. "

            if len(options) == 2:
                question += f"¿Te refieres a:\n\n"
                for i, option in enumerate(options, 1):
                    question += f"**{i}.** {option['label']} - {option['description']}\n"
            else:
                question += f"¿Podrías especificar qué necesitas?\n\n"
                for i, option in enumerate(options, 1):
                    question += f"**{i}.** {option['label']}\n"

            question += f"\n💡 Responde con el número de la opción que necesitas."

            return question

        except Exception as e:
            self.logger.error(f"Error generando pregunta de aclaración: {e}")
            return "Tu consulta necesita más detalles. ¿Podrías ser más específico?"

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

            for item in data[:5]:  # Máximo 5 candidatos
                candidates.append({
                    'nombre': item.get('nombre', 'N/A'),
                    'grado': f"{item.get('grado', 'N/A')}°{item.get('grupo', '')}"
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

    # 🗑️ MÉTODOS OBSOLETOS ELIMINADOS: COMUNICACIÓN BIDIRECCIONAL LEGACY
    # RAZÓN: Student ya no envía feedback bidireccional - Master analiza resultados directamente
    #
    # Métodos eliminados:
    # - _needs_bidirectional_communication() → Reemplazado por _should_ask_user_about_results()
    # - _handle_student_feedback() → Ya no es necesario, Student no envía feedback
    # - _handle_multiple_results_feedback() → Integrado en _handle_results_analysis()
    # - _handle_multiple_candidates_feedback() → Integrado en _create_candidate_selection_question()
    # - _handle_ambiguity_feedback() → Manejado en análisis previo
    # - _handle_validation_feedback() → Integrado en _handle_results_analysis()
    # - _handle_generic_feedback() → Ya no es necesario

    # 🗑️ MÉTODOS OBSOLETOS ELIMINADOS: FEEDBACK HANDLERS LEGACY
    # RAZÓN: Student ya no envía feedback bidireccional - Master analiza resultados directamente
    #
    # Métodos eliminados:
    # - _handle_multiple_results_feedback() → Integrado en _create_filter_suggestion_question()
    # - _handle_multiple_candidates_feedback() → Integrado en _create_candidate_selection_question()
    # - _handle_ambiguity_feedback() → Manejado en análisis previo con _check_for_ambiguities()
    # - _handle_validation_feedback() → Integrado en _create_no_results_help_question()
    # - _handle_generic_feedback() → Ya no es necesario

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

            # 🎯 EXTRAER CRITERIOS DE BÚSQUEDA DINÁMICAMENTE DESPUÉS DE LA EJECUCIÓN
            search_criteria = self._extract_search_criteria_for_display(student_data)

            # 🎯 AGREGAR CRITERIOS A STUDENT_DATA PARA LAS FUNCIONES DE RESPUESTA
            student_data["search_criteria"] = search_criteria

            # 🎯 MASTER GENERA RESPUESTA FINAL USANDO PROMPT ESPECIALIZADO
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
            # 🔍 DEBUG: Ver qué datos llegan
            self.logger.info(f"🔍 [DEBUG] student_data keys: {list(student_data.keys())}")

            # 🚀 ENFOQUE DINÁMICO: Analizar el SQL real que se ejecutó
            sql_query = student_data.get("sql_executed", "") or student_data.get("sql_query", "")
            search_description = ""
            relevant_fields = []

            self.logger.info(f"🔍 [DEBUG] sql_query encontrado: '{sql_query}'")
            self.logger.info(f"🔍 [DEBUG] ¿sql_executed existe? {'sql_executed' in student_data}")
            self.logger.info(f"🔍 [DEBUG] ¿sql_query existe? {'sql_query' in student_data}")

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

                self.logger.info(f"🔍 [DYNAMIC] SQL analizado: {sql_query[:100]}...")
                self.logger.info(f"🔍 [DYNAMIC] Campos extraídos: {relevant_fields}")
                self.logger.info(f"🔍 [DYNAMIC] Descripción: {search_description.strip()}")

            # Si no hay SQL o no se encontraron patrones, usar fallback inteligente
            if not relevant_fields:
                # Analizar parámetros de la acción como fallback
                action_params = student_data.get("action_params", {})
                criterio_principal = action_params.get("criterio_principal", {})
                campo = criterio_principal.get("campo", "")

                if campo:
                    relevant_fields.append(campo)
                    search_description = f"búsqueda por {campo}"
                    self.logger.info(f"🔍 [FALLBACK] Campo del criterio principal: {campo}")

            # Siempre incluir campos básicos
            basic_fields = ['nombre', 'curp']
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

    # 🗑️ MÉTODO ELIMINADO: _generate_count_response
    # RAZÓN: Ahora el Student genera respuestas dinámicas directamente con el prompt mejorado

    # 🗑️ MÉTODO ELIMINADO: _generate_count_response_from_filters
    # RAZÓN: Ahora el Student genera respuestas dinámicas directamente con el prompt mejorado

    # 🗑️ MÉTODO ELIMINADO: _generate_search_response
    # RAZÓN: Ahora el Student genera respuestas dinámicas directamente con el prompt mejorado



    def _generate_master_response_with_llm(self, student_data: dict, user_query: str, action_used: str) -> str:
        """
        🎯 GENERA RESPUESTA FINAL USANDO LLM ESPECIALIZADO DEL MASTER

        El Master usa su propio prompt especializado en comunicación para generar
        respuestas humanizadas basándose en los datos técnicos del Student.
        """
        try:
            # Crear prompt especializado para respuesta del Master
            master_prompt = self._create_master_response_prompt(student_data, user_query, action_used)

            # Llamar al LLM para generar respuesta humanizada
            response = self.gemini_client.send_prompt_sync(master_prompt)

            if response and response.strip():
                self.logger.info(f"✅ Master generó respuesta humanizada exitosamente")
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
            return f"El conteo se completó exitosamente: {row_count} elementos."
        else:
            return "Consulta procesada exitosamente."

    def _create_master_response_prompt(self, student_data: dict, user_query: str, action_used: str) -> str:
        """
        🎯 CREA PROMPT ESPECIALIZADO DINÁMICO SEGÚN TIPO DE CONSULTA

        Diferentes tipos de consulta requieren diferentes enfoques de respuesta.
        """
        # Detectar tipo de consulta
        query_type = self._detect_query_type(action_used, student_data, user_query)

        # Crear prompt específico según el tipo
        if query_type == "search":
            return self._create_search_response_prompt(student_data, user_query, action_used)
        elif query_type == "constancia":
            return self._create_constancia_response_prompt(student_data, user_query, action_used)
        elif query_type == "transformation":
            return self._create_transformation_response_prompt(student_data, user_query, action_used)
        elif query_type == "statistics":
            return self._create_statistics_response_prompt(student_data, user_query, action_used)
        else:
            return self._create_generic_response_prompt(student_data, user_query, action_used)

    def _detect_query_type(self, action_used: str, student_data: dict, user_query: str) -> str:
        """Detecta el tipo específico de consulta para usar el prompt correcto"""
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

        # 🔧 MANEJO SEGURO DE DATOS - verificar que data sea una lista
        data_context = ""
        if data and isinstance(data, list) and len(data) > 0:
            if len(data) <= 3:
                data_context = "RESULTADOS ENCONTRADOS:\n"
                for i, item in enumerate(data, 1):
                    if isinstance(item, dict):
                        nombre = item.get("nombre", "N/A")
                        grado = item.get("grado", "N/A")
                        grupo = item.get("grupo", "N/A")
                        data_context += f"{i}. {nombre} - {grado}° {grupo}\n"
            else:
                data_context = f"PRIMEROS 3 DE {len(data)} RESULTADOS:\n"
                for i in range(min(3, len(data))):
                    item = data[i]
                    if isinstance(item, dict):
                        nombre = item.get("nombre", "N/A")
                        grado = item.get("grado", "N/A")
                        grupo = item.get("grupo", "N/A")
                        data_context += f"{i+1}. {nombre} - {grado}° {grupo}\n"

        # Detectar si hay contexto conversacional previo
        reflexion = student_data.get("auto_reflexion", {})
        datos_recordar = reflexion.get("datos_recordar", {})
        conversation_context = datos_recordar.get("context", "")
        query_anterior = datos_recordar.get("query", "")

        # Determinar si es continuación
        es_continuacion = bool(conversation_context and query_anterior)

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

        return f"""
Eres el asistente de la escuela especializado en ESTADÍSTICAS Y CONTEOS.

🎯 SITUACIÓN:
- CONSULTA: "{user_query}"
- RESULTADO: {row_count}
- TIPO: Estadística/Conteo

🎯 TU TAREA ESPECÍFICA PARA ESTADÍSTICAS:
Generar una respuesta ENFOCADA EN NÚMEROS que:

1. 📊 PRESENTE el resultado claramente
2. 🔍 CONTEXTUALICE el número (qué significa)
3. 💡 SUGIERA análisis relacionados
4. 🎯 MANTENGA enfoque en datos

🚫 NO MENCIONES:
- Panel PDF
- Constancias
- Transformaciones

✅ SÍ ENFÓCATE EN:
- Resultado numérico claro
- Contexto del conteo
- Sugerencias de análisis adicional

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

    def _handle_user_interaction_request(self, action_used: str, student_data: dict, base_response: str) -> str:
        """
        🎯 MANEJA SOLICITUDES DE INTERACCIÓN CON EL USUARIO

        Mejora la respuesta del Student cuando necesita interacción,
        agregando contexto y opciones claras para el usuario.
        """
        reflexion = student_data.get("reflexion_conversacional", {})
        continuation_type = reflexion.get("tipo_esperado", "")

        # MEJORAR RESPUESTA SEGÚN EL TIPO DE INTERACCIÓN NECESARIA
        if continuation_type == "confirmation":
            return f"{base_response}\n\n💡 **Responde 'sí' o 'no' para continuar.**"

        elif continuation_type == "specification":
            return f"{base_response}\n\n💡 **Por favor especifica los detalles que necesitas.**"

        elif continuation_type == "selection":
            data = student_data.get("data", [])
            if data and len(data) > 1:
                return f"{base_response}\n\n💡 **Puedes referenciar por posición (ej: 'el segundo', 'número 3') o por nombre.**"
            else:
                return f"{base_response}\n\n💡 **Por favor especifica cuál necesitas.**"

        else:
            # Caso genérico - agregar instrucción de ayuda
            return f"{base_response}\n\n💡 **¿Necesitas ayuda con algo específico?**"

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
