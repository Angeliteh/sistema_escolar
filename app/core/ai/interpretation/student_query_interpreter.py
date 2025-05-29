"""
Interpretador especializado en consultas de alumnos/estudiantes usando LLM
Implementa la filosofía de SETs especializados con auto-reflexión integrada.

ARQUITECTURA MODULAR COMPLETADA:
- Clases especializadas implementadas y funcionando
- Código limpio y mantenible
- Responsabilidades separadas por componente
"""
import json
import re
from typing import Dict, Any, Optional, List, Tuple

from .base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from .database_analyzer import DatabaseAnalyzer
from .sql_executor import SQLExecutor
from .response_parser import ResponseParser
from ..prompts.student_query_prompt_manager import StudentQueryPromptManager
from app.core.logging import get_logger

# ✅ CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR COMPLETADA)
from .student_query.continuation_detector import ContinuationDetector
from .student_query.student_identifier import StudentIdentifier
from .student_query.constancia_processor import ConstanciaProcessor
from .student_query.data_normalizer import DataNormalizer
from .student_query.response_generator import ResponseGenerator
from .utils.json_parser import JSONParser

class StudentQueryInterpreter(BaseInterpreter):
    """Interpretador especializado en consultas de alumnos/estudiantes usando LLM"""

    def __init__(self, db_path: str, gemini_client=None):
        super().__init__("SQL_Interpreter", priority=10)  # Alta prioridad

        # 🆕 LOGGING CENTRALIZADO
        self.logger = get_logger(__name__)

        self.db_path = db_path
        self.database_analyzer = DatabaseAnalyzer(db_path)
        self.sql_executor = SQLExecutor(db_path)
        self.response_parser = ResponseParser()
        self.gemini_client = gemini_client

        # Analizar BD una vez al inicializar
        self.database_analyzer.analyze_database()

        # PromptManager centralizado para contexto escolar unificado
        self.prompt_manager = StudentQueryPromptManager(self.database_analyzer)
        self.logger.debug("StudentQueryPromptManager inicializado")

        # Cache del contexto SQL
        self._sql_context = None

        # ✅ INICIALIZAR CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR COMPLETADA)
        self.continuation_detector = ContinuationDetector(gemini_client)
        self.student_identifier = StudentIdentifier()
        self.constancia_processor = ConstanciaProcessor(gemini_client)
        self.data_normalizer = DataNormalizer()
        self.response_generator = ResponseGenerator(gemini_client, self.prompt_manager)
        self.json_parser = JSONParser()

        self.logger.debug("✅ Clases especializadas inicializadas (Arquitectura modular completada)")

    def _get_supported_actions(self):
        """Método requerido por BaseInterpreter - mantenido por compatibilidad"""
        return ["consulta_sql_exitosa", "consulta_sql_fallida"]

    def can_handle(self, context: InterpretationContext) -> bool:
        """Método abstracto requerido - siempre True porque se usa desde MasterInterpreter"""
        return True  # El MasterInterpreter ya decidió que somos el intérprete correcto

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """Interpreta la consulta usando el enfoque optimizado de 3 prompts + sistema conversacional"""
        try:
            self.logger.info(f"🎯 StudentQueryInterpreter INICIADO - Consulta: '{context.user_message}'")
            if hasattr(context, 'conversation_history') and context.conversation_history is not None:
                self.logger.debug(f"Contexto conversacional disponible: {len(context.conversation_history)} mensajes")
            else:
                self.logger.debug("NO hay contexto conversacional disponible")
                # 🆕 INICIALIZAR CONVERSATION_HISTORY SI ES NONE
                if not hasattr(context, 'conversation_history') or context.conversation_history is None:
                    context.conversation_history = []

            # 🆕 PASO 0: VERIFICAR INFORMACIÓN DE INTENCIÓN DEL MASTER
            intention_info = getattr(context, 'intention_info', {})
            sub_intention = intention_info.get('sub_intention', '')
            detected_entities = intention_info.get('detected_entities', {})

            # Información ya mostrada en logs arquitectónicos del Master

            # 🚀 FLUJO DIRECTO BASADO EN SUB-INTENCIÓN (PERO VERIFICANDO CONTEXTO PRIMERO)
            if sub_intention == "generar_constancia":
                self.logger.info("🎯 SUB-INTENCIÓN: GENERAR CONSTANCIA")

                # 🔧 VERIFICAR PILA CONVERSACIONAL PRIMERO (INCLUSO PARA CONSTANCIAS)
                # 🆕 ASEGURAR QUE CONVERSATION_STACK EXISTE
                if not hasattr(context, 'conversation_stack') or context.conversation_stack is None:
                    context.conversation_stack = []

                if hasattr(context, 'conversation_stack') and context.conversation_stack:
                    self.logger.info(f"📚 VERIFICANDO PILA CONVERSACIONAL: {len(context.conversation_stack)} niveles")

                    # Detectar si es continuación usando LLM
                    continuation_info = self._detect_continuation_query(context.user_message, context.conversation_stack)

                    if continuation_info and continuation_info.get('es_continuacion', False):
                        self.logger.info(f"✅ CONSTANCIA ES CONTINUACIÓN: {continuation_info.get('tipo_continuacion', 'unknown')}")
                        # Procesar usando la pila conversacional
                        return self._process_continuation(context.user_message, continuation_info, context.conversation_stack)
                    else:
                        self.logger.info(f"❌ CONSTANCIA NO ES CONTINUACIÓN: {continuation_info}")

                # Si no es continuación, procesar como constancia nueva
                self.logger.info("✅ PROCESANDO CONSTANCIA NUEVA...")
                simple_context = {
                    'pdf_panel': getattr(context, 'pdf_panel', None),
                    'user_message': context.user_message,
                    'detected_entities': detected_entities  # ← NUEVO: Pasar entidades detectadas
                }
                result = self._process_constancia_request(context.user_message, simple_context)
                self.logger.info(f"🎯 Resultado constancia: {result.action if result else 'None'}")
                return result

            elif sub_intention == "transformar_pdf":
                self.logger.info("✅ SUB-INTENCIÓN: TRANSFORMAR PDF - Procesando directamente...")
                simple_context = {
                    'pdf_panel': getattr(context, 'pdf_panel', None),
                    'user_message': context.user_message,
                    'detected_entities': detected_entities
                }
                result = self._process_constancia_request(context.user_message, simple_context)
                self.logger.info(f"🎯 Resultado transformación: {result.action if result else 'None'}")
                return result

            # PASO 1: Verificar si hay pila conversacional y detectar continuación
            # 🆕 INICIALIZAR CONVERSATION_STACK SI ES NONE
            if not hasattr(context, 'conversation_stack') or context.conversation_stack is None:
                context.conversation_stack = []

            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                self.logger.info(f"📚 PILA CONVERSACIONAL DISPONIBLE: {len(context.conversation_stack)} niveles")

                # Mostrar contenido de la pila de forma estructurada
                for i, level in enumerate(context.conversation_stack, 1):
                    self.logger.info(f"   📋 Nivel {i}: '{level.get('query', 'N/A')[:30]}...' - {level.get('row_count', 0)} elementos")

                # Detectar si es continuación usando LLM
                continuation_info = self._detect_continuation_query(context.user_message, context.conversation_stack)

                if continuation_info and continuation_info.get('es_continuacion', False):
                    self.logger.info(f"✅ CONTINUACIÓN DETECTADA: {continuation_info.get('tipo_continuacion', 'unknown')}")
                    # Procesar usando la pila conversacional (NO generar SQL)
                    return self._process_continuation(context.user_message, continuation_info, context.conversation_stack)
                else:
                    self.logger.info(f"❌ NO ES CONTINUACIÓN: {continuation_info}")
            else:
                self.logger.info("❌ NO HAY PILA CONVERSACIONAL disponible")

            # 🔄 [STUDENT] INICIANDO FLUJO DE 4 PROMPTS
            self.logger.info("🔄 [STUDENT] Iniciando flujo de 4 prompts")

            # PROMPT 1: Detectar intención específica (USANDO PROMPT MANAGER CENTRALIZADO CON CONTEXTO)
            self.logger.info("   ├── PROMPT 1: Análisis de intención específica...")

            # 🆕 PREPARAR CONTEXTO CONVERSACIONAL PARA PROMPT 1
            conversation_context = ""
            # 🆕 ASEGURAR QUE CONVERSATION_STACK EXISTE ANTES DE USARLO
            if not hasattr(context, 'conversation_stack') or context.conversation_stack is None:
                context.conversation_stack = []

            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                conversation_context = self._format_conversation_stack_for_llm(context.conversation_stack)
                self.logger.info(f"   ├── Contexto conversacional disponible: {len(context.conversation_stack)} niveles")

            is_student_query = self._detect_student_query_intention_centralized(context.user_message, conversation_context)
            if not is_student_query:
                self.logger.info("   └── ❌ No es consulta de alumnos")
                return None
            self.logger.info("   └── ✅ Consulta de alumnos confirmada")

            # 🆕 DETECCIÓN LIMPIA: Solo usar entidades del Master (SIN fallbacks)
            if (detected_entities and
                detected_entities.get('tipo_constancia') and
                detected_entities.get('tipo_constancia') != 'null'):

                self.logger.info("✅ CONSTANCIA DETECTADA POR MASTER - Procesando directamente")
                # 🆕 PASAR CONTEXTO COMPLETO CON INTENTION_INFO
                result = self._process_constancia_request(context.user_message, context)
                self.logger.info(f"📊 [STUDENT] Resultado constancia: {result.action if result else 'None'}")
                return result

            # PROMPT 2: Generar estrategia + SQL (USANDO PROMPT MANAGER CENTRALIZADO)
            self.logger.info("   ├── PROMPT 2: Generación SQL inteligente...")
            sql_query = self._generate_sql_with_strategy_centralized(context.user_message)

            if not sql_query:
                self.logger.info("   └── ❌ No se pudo generar SQL")
                return None
            self.logger.info("   └── ✅ SQL generado exitosamente")

            # Ejecutar consulta SQL
            result = self.sql_executor.execute_query(sql_query)

            if result.success:
                # PROMPT 3: Validar + Generar respuesta + Auto-reflexión
                self.logger.info("   ├── PROMPT 3: Validación + respuesta + auto-reflexión...")
                response_with_reflection = self._validate_and_generate_response(
                    context.user_message, sql_query, result.data, result.row_count
                )

                if not response_with_reflection:
                    self.logger.info("   └── ❌ Validación falló")
                    return InterpretationResult(
                        action="consulta_sql_fallida",
                        parameters={
                            "error": "La consulta SQL no resolvió correctamente la solicitud",
                            "sql_query": sql_query
                        },
                        confidence=0.2
                    )
                self.logger.info("   └── ✅ Validación y respuesta completadas")

                # Extraer respuesta y reflexión
                human_response = response_with_reflection.get("respuesta_usuario", "Respuesta procesada")
                reflexion = response_with_reflection.get("reflexion_conversacional", {})

                # PROMPT 4: Filtrado inteligente (implícito en validate_and_generate_response)
                self.logger.info("   └── PROMPT 4: Filtrado inteligente aplicado ✅")

                # Preparar parámetros con información de auto-reflexión
                parameters = {
                    "sql_query": result.query_executed,
                    "data": result.data,
                    "row_count": result.row_count,
                    "message": human_response,
                    "human_response": human_response,
                    "auto_reflexion": reflexion
                }

                self.logger.info(f"📊 [STUDENT] Flujo completado: {result.row_count} resultados encontrados")
                return InterpretationResult(
                    action="consulta_sql_exitosa",
                    parameters=parameters,
                    confidence=0.9
                )
            else:
                self.logger.info("   └── ❌ Ejecución SQL falló")
                return InterpretationResult(
                    action="consulta_sql_fallida",
                    parameters={
                        "error": result.message,
                        "sql_query": sql_query
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"❌ Error en StudentQueryInterpreter: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

            return InterpretationResult(
                action="consulta_sql_fallida",
                parameters={
                    "error": f"Error interno: {str(e)}",
                    "message": "❌ Error procesando tu consulta. Intenta reformularla.",
                    "exception": str(e)
                },
                confidence=0.1
            )



    def _detect_continuation_query(self, user_query: str, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        DETECTOR DE CONTINUACIÓN: Usa LLM para determinar si la consulta se refiere a la pila conversacional
        ✅ MIGRADO: Usa ContinuationDetector centralizado
        """
        try:
            result = self.continuation_detector.detect_continuation(user_query, conversation_stack)

            if result:
                self.logger.debug(f"✅ Continuación detectada exitosamente con ContinuationDetector: {result.get('tipo_continuacion', 'unknown')}")
                return result
            else:
                self.logger.warning(f"❌ ContinuationDetector no detectó continuación")
                return {"es_continuacion": False, "tipo_continuacion": "none"}

        except Exception as e:
            self.logger.error(f"Error usando ContinuationDetector: {e}")
            return {"es_continuacion": False, "tipo_continuacion": "none"}

    def _process_continuation(self, user_query: str, continuation_info: Dict[str, Any], conversation_stack: list) -> Optional[InterpretationResult]:
        """
        PROCESADOR DE CONTINUACIÓN: Procesa la consulta usando datos de la pila (NO genera SQL)
        """
        try:
            tipo_continuacion = continuation_info.get('tipo_continuacion', 'none')
            nivel_referenciado = continuation_info.get('nivel_referenciado')
            elemento_referenciado = continuation_info.get('elemento_referenciado')

            self.logger.debug(f"Procesando continuación tipo: {tipo_continuacion}")

            if tipo_continuacion == "selection":
                return self._process_selection_continuation(user_query, elemento_referenciado, conversation_stack)
            elif tipo_continuacion == "action":
                return self._process_action_continuation(user_query, nivel_referenciado, conversation_stack)
            elif tipo_continuacion == "confirmation":
                return self._process_confirmation_continuation(user_query, conversation_stack)
            elif tipo_continuacion == "specification":
                return self._process_specification_continuation(user_query, conversation_stack)
            else:
                self.logger.warning(f"Tipo de continuación no reconocido: {tipo_continuacion}")
                return None

        except Exception as e:
            self.logger.error(f"Error procesando continuación: {e}")
            return None

    def _format_conversation_stack_for_llm(self, conversation_stack: list) -> str:
        """Formatea la pila conversacional para el LLM"""
        if not conversation_stack:
            return "PILA VACÍA"

        context = ""
        for i, level in enumerate(conversation_stack, 1):
            context += f"""
NIVEL {i}:
- Consulta: "{level.get('query', 'N/A')}"
- Datos disponibles: {level.get('row_count', 0)} elementos
- Esperando: {level.get('awaiting', 'N/A')}
- Timestamp: {level.get('timestamp', 'N/A')}
"""
            # Mostrar algunos datos de ejemplo si hay
            if level.get('data') and len(level.get('data', [])) > 0:
                context += f"- Primeros elementos: {level['data'][:3]}\n"

        return context

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parsea respuesta JSON del LLM
        ✅ MIGRADO: Usa JSONParser centralizado
        """
        try:
            result = self.json_parser.parse_llm_response(response)

            if result:
                self.logger.debug(f"✅ JSON parseado exitosamente con JSONParser")
                return result
            else:
                self.logger.warning(f"❌ JSONParser no pudo parsear respuesta: {response[:100]}...")
                return None

        except Exception as e:
            self.logger.error(f"Error usando JSONParser: {e}")
            return None

    def _process_selection_continuation(self, user_query: str, elemento_referenciado: int, conversation_stack: list) -> Optional[InterpretationResult]:
        """Procesa continuación de tipo SELECCIÓN (ej: 'del quinto', 'número 3')"""
        try:
            # Obtener el último nivel con datos de lista
            ultimo_nivel = None
            for level in reversed(conversation_stack):
                if level.get('data') and len(level.get('data', [])) > 0:
                    ultimo_nivel = level
                    break

            if not ultimo_nivel:
                return InterpretationResult(
                    action="continuacion_error",
                    parameters={
                        "error": "No hay datos de lista disponibles en la pila conversacional",
                        "message": "No encuentro una lista previa para hacer la selección. ¿Podrías hacer una nueva consulta?"
                    },
                    confidence=0.3
                )

            # Verificar que el elemento existe
            datos = ultimo_nivel.get('data', [])
            if not elemento_referenciado or elemento_referenciado < 1 or elemento_referenciado > len(datos):
                return InterpretationResult(
                    action="continuacion_error",
                    parameters={
                        "error": f"Elemento {elemento_referenciado} no existe en la lista",
                        "message": f"La lista tiene {len(datos)} elementos. ¿Podrías especificar un número entre 1 y {len(datos)}?"
                    },
                    confidence=0.3
                )

            # Obtener el elemento seleccionado (índice base 1)
            elemento_seleccionado = datos[elemento_referenciado - 1]

            # 🎯 VERIFICAR SI ES SOLICITUD DE CONSTANCIA (IGUAL QUE EN ACTION)
            constancia_keywords = ["constancia", "certificado", "genera", "generar", "crear", "documento"]
            user_lower = user_query.lower()
            is_constancia_request = any(keyword in user_lower for keyword in constancia_keywords)

            if is_constancia_request:
                self.logger.info("🎯 SELECCIÓN + CONSTANCIA - Procesando DIRECTAMENTE...")

                # Extraer tipo de constancia del query
                tipo_constancia = "estudio"  # Por defecto
                if "calificaciones" in user_lower:
                    tipo_constancia = "calificaciones"
                elif "traslado" in user_lower:
                    tipo_constancia = "traslado"
                elif "estudios" in user_lower or "estudio" in user_lower:
                    tipo_constancia = "estudio"

                self.logger.info(f"   - Tipo detectado: {tipo_constancia}")
                self.logger.info(f"   - Alumno seleccionado: {elemento_seleccionado.get('nombre', 'N/A')}")

                # 🔧 OBTENER DATOS COMPLETOS DEL ALUMNO (incluyendo ID)
                alumno_completo = self._get_complete_student_data(elemento_seleccionado)

                if not alumno_completo:
                    return InterpretationResult(
                        action="constancia_error",
                        parameters={
                            "message": f"❌ No se pudieron obtener los datos completos de {elemento_seleccionado.get('nombre', 'N/A')}",
                            "error": "incomplete_student_data"
                        },
                        confidence=0.3
                    )

                # 🚀 GENERAR CONSTANCIA DIRECTAMENTE (SIN SQL)
                self.logger.info("🚀 GENERANDO CONSTANCIA DIRECTAMENTE DESDE SELECCIÓN")
                return self._generate_constancia_for_student(alumno_completo, tipo_constancia, user_query)

            # Si NO es constancia, usar respuesta unificada normal
            response_message = self._generate_unified_continuation_response(
                user_query, "selection", ultimo_nivel, conversation_stack
            )

            return InterpretationResult(
                action="seleccion_realizada",
                parameters={
                    "message": response_message,
                    "elemento_seleccionado": elemento_seleccionado,
                    "posicion": elemento_referenciado,
                    "consulta_original": ultimo_nivel.get('query', ''),
                    "tipo": "seleccion"
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error en selección: {e}")
            return None

    def _process_action_continuation(self, user_query: str, nivel_referenciado: int, conversation_stack: list) -> Optional[InterpretationResult]:
        """Procesa continuación de tipo ACCIÓN (ej: 'constancia para él', 'CURP de ese')"""
        try:
            # NOTA: nivel_referenciado no se usa actualmente, se mantiene por compatibilidad
            # Obtener el último alumno seleccionado o el último nivel con datos
            ultimo_alumno = None
            ultimo_nivel = None

            for level in reversed(conversation_stack):
                if level.get('data'):
                    # Si hay un solo elemento, es una selección previa
                    if len(level.get('data', [])) == 1:
                        ultimo_alumno = level['data'][0]
                        ultimo_nivel = level
                        break
                    # Si hay múltiples elementos, buscar si hay selección
                    elif len(level.get('data', [])) > 1:
                        ultimo_nivel = level
                        # Por ahora, tomar el primero como referencia
                        ultimo_alumno = level['data'][0]
                        break

            if not ultimo_alumno:
                return InterpretationResult(
                    action="continuacion_error",
                    parameters={
                        "error": "No hay alumno seleccionado previamente",
                        "message": "No encuentro un alumno seleccionado previamente. ¿Podrías especificar de qué alumno necesitas información?"
                    },
                    confidence=0.3
                )

            # 🧠 DETECTAR SI NECESITA NUEVA CONSULTA SQL
            needs_sql = self._detect_if_needs_sql_query(user_query, ultimo_nivel)

            if needs_sql:
                self.logger.debug("Acción requiere nueva consulta SQL")
                # Generar nueva consulta SQL basada en datos previos
                new_sql = self._generate_sql_for_action_continuation(user_query, ultimo_nivel)

                if new_sql:
                    self.logger.debug(f"SQL generado para continuación: {new_sql[:100]}...")

                    # Ejecutar la nueva consulta
                    result = self.sql_executor.execute_query(new_sql)

                    if result.success:
                        # Usar filtro inteligente en los nuevos datos
                        filtered_data, filter_decision = self._intelligent_final_filter(user_query, result.data, new_sql)

                        # Generar respuesta con datos reales
                        final_response = self._validate_and_generate_response(
                            user_query, new_sql, filtered_data, len(filtered_data)
                        )

                        if final_response:
                            return InterpretationResult(
                                action="consulta_sql_exitosa",
                                parameters={
                                    "sql_query": result.query_executed,
                                    "data": filtered_data,
                                    "row_count": len(filtered_data),
                                    "message": final_response.get("respuesta_usuario", "Información obtenida"),
                                    "human_response": final_response.get("respuesta_usuario", "Información obtenida"),
                                    "auto_reflexion": final_response.get("reflexion_conversacional", {}),
                                    "tipo": "accion_con_sql"
                                },
                                confidence=0.95
                            )

            # 🎯 VERIFICAR SI ES SOLICITUD DE CONSTANCIA
            constancia_keywords = ["constancia", "certificado", "genera", "generar", "crear", "documento"]
            user_lower = user_query.lower()
            is_constancia_request = any(keyword in user_lower for keyword in constancia_keywords)

            if is_constancia_request:
                self.logger.info("🎯 ACCIÓN DE CONTINUACIÓN ES CONSTANCIA - Procesando DIRECTAMENTE...")

                # Extraer tipo de constancia del query
                tipo_constancia = "estudio"  # Por defecto
                if "calificaciones" in user_lower:
                    tipo_constancia = "calificaciones"
                elif "traslado" in user_lower:
                    tipo_constancia = "traslado"
                elif "estudios" in user_lower or "estudio" in user_lower:
                    tipo_constancia = "estudio"

                self.logger.info(f"   - Tipo detectado: {tipo_constancia}")

                # 🔧 IDENTIFICAR ALUMNO CORRECTO USANDO CONTEXTO
                alumno_seleccionado = self._identify_student_from_context(user_query, conversation_stack)

                if not alumno_seleccionado:
                    self.logger.warning("❌ No se pudo identificar alumno desde el contexto")
                    alumno_seleccionado = ultimo_alumno  # Fallback al último alumno

                self.logger.info(f"   - Alumno identificado: {alumno_seleccionado.get('nombre', 'N/A')}")

                # 🔧 OBTENER DATOS COMPLETOS DEL ALUMNO (incluyendo ID)
                alumno_completo = self._get_complete_student_data(alumno_seleccionado)

                if not alumno_completo:
                    return InterpretationResult(
                        action="constancia_error",
                        parameters={
                            "message": f"❌ No se pudieron obtener los datos completos de {alumno_seleccionado.get('nombre', 'N/A')}",
                            "error": "incomplete_student_data"
                        },
                        confidence=0.3
                    )

                # 🚀 GENERAR CONSTANCIA DIRECTAMENTE (SIN SQL)
                self.logger.info("🚀 GENERANDO CONSTANCIA DIRECTAMENTE DESDE CONTEXTO")
                return self._generate_constancia_for_student(alumno_completo, tipo_constancia, user_query)

            # Si no necesita SQL o falló, usar respuesta LLM unificada
            self.logger.debug("Acción NO requiere SQL, usando respuesta LLM unificada")
            response_message = self._generate_unified_continuation_response(
                user_query, "action", ultimo_nivel, conversation_stack
            )

            return InterpretationResult(
                action="accion_realizada",
                parameters={
                    "message": response_message,
                    "alumno": ultimo_alumno,
                    "accion_solicitada": user_query,
                    "tipo": "accion"
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error en acción: {e}")
            return None

    def _identify_student_from_context(self, user_query: str, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        Identifica al alumno correcto usando el contexto conversacional y referencias en la consulta
        🆕 MIGRADO: Usa StudentIdentifier centralizado (Refactorización completada)
        """
        try:
            result = self.student_identifier.identify_student_from_context(
                user_query, conversation_stack
            )

            if result:
                self.logger.debug(f"✅ Alumno identificado exitosamente con StudentIdentifier: {result.get('nombre', 'N/A')}")
                return result
            else:
                self.logger.warning(f"❌ StudentIdentifier no pudo identificar alumno")
                return None

        except Exception as e:
            self.logger.error(f"Error usando StudentIdentifier: {e}")
            return None



    def _normalize_student_data_structure(self, item: Dict) -> Optional[Dict]:
        """
        Normaliza diferentes estructuras de datos de alumnos a un formato estándar
        ✅ MIGRADO: Usa DataNormalizer centralizado
        """
        try:
            result = self.data_normalizer.normalize_student_data(item)

            if result:
                self.logger.debug(f"✅ Datos normalizados exitosamente con DataNormalizer: {result.get('nombre', 'N/A')}")
                return result
            else:
                self.logger.warning(f"❌ DataNormalizer no pudo normalizar estructura: {list(item.keys())}")
                return None

        except Exception as e:
            self.logger.error(f"Error usando DataNormalizer: {e}")
            return None

    def _get_complete_student_data(self, alumno_parcial: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene los datos completos del alumno desde la base de datos"""
        try:
            # Si ya tiene ID, verificar que tenga todos los datos necesarios
            if alumno_parcial.get('id'):
                self.logger.info(f"✅ Alumno ya tiene ID: {alumno_parcial.get('id')}")
                return alumno_parcial

            # Si no tiene ID, buscar por nombre
            nombre_alumno = alumno_parcial.get('nombre', '')
            if not nombre_alumno:
                self.logger.warning("❌ No se puede buscar alumno sin nombre")
                return None

            self.logger.info(f"🔍 Buscando datos completos para: {nombre_alumno}")

            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            alumno_service = service_provider.alumno_service

            # Buscar alumno por nombre exacto
            alumnos_encontrados = alumno_service.buscar_alumnos(nombre_alumno)

            if not alumnos_encontrados:
                self.logger.warning(f"❌ No se encontró alumno con nombre: {nombre_alumno}")
                return None

            # Si hay múltiples coincidencias, buscar coincidencia exacta
            for alumno in alumnos_encontrados:
                alumno_dict = alumno.to_dict() if hasattr(alumno, 'to_dict') else alumno
                if alumno_dict.get('nombre', '').upper() == nombre_alumno.upper():
                    self.logger.info(f"✅ Datos completos obtenidos para: {alumno_dict.get('nombre')} (ID: {alumno_dict.get('id')})")
                    return alumno_dict

            # Si no hay coincidencia exacta, tomar el primero
            primer_alumno = alumnos_encontrados[0]
            alumno_dict = primer_alumno.to_dict() if hasattr(primer_alumno, 'to_dict') else primer_alumno

            self.logger.info(f"✅ Usando primer resultado: {alumno_dict.get('nombre')} (ID: {alumno_dict.get('id')})")
            return alumno_dict

        except Exception as e:
            self.logger.error(f"Error obteniendo datos completos del alumno: {e}")
            return None

    def _generate_constancia_for_student(self, alumno: Dict, tipo_constancia: str, user_query: str) -> InterpretationResult:
        """
        Genera constancia directamente para un alumno específico
        ✅ MIGRADO: Usa ConstanciaProcessor centralizado
        """
        try:
            result = self.constancia_processor.process_constancia_request(
                alumno, tipo_constancia, user_query
            )

            if result:
                self.logger.debug(f"✅ Constancia procesada exitosamente con ConstanciaProcessor: {result.action}")
                return result
            else:
                self.logger.warning(f"❌ ConstanciaProcessor no pudo procesar constancia")
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": f"❌ Error procesando constancia para {alumno.get('nombre', 'N/A')}",
                        "error": "processor_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error usando ConstanciaProcessor: {e}")
            return InterpretationResult(
                action="constancia_error",
                parameters={
                    "message": f"❌ Error interno procesando constancia para {alumno.get('nombre', 'N/A')}",
                    "error": "internal_error"
                },
                confidence=0.1
            )



    def _generate_unified_continuation_response(self, user_query: str, continuation_type: str,
                                              ultimo_nivel: Dict, conversation_stack: list) -> str:
        """
        ✅ IMPLEMENTADO: Respuesta unificada para continuaciones usando PromptManager

        REEMPLAZA:
        - _generate_action_response()
        - _generate_selection_response()

        TIPOS:
        - action: "constancia para él", "CURP de ese"
        - selection: "del segundo", "número 5"
        - confirmation: "sí", "correcto"
        """
        try:
            # 🆕 USAR PROMPT MANAGER para respuesta unificada
            continuation_prompt = self.prompt_manager.get_unified_continuation_prompt(
                user_query, continuation_type, ultimo_nivel, conversation_stack
            )

            response = self.gemini_client.send_prompt_sync(continuation_prompt)
            if response:
                return response.strip()
            else:
                # Respuesta de fallback
                return f"✅ Procesando {continuation_type} para: {user_query}"

        except Exception as e:
            self.logger.error(f"Error en respuesta unificada: {e}")
            return f"✅ Procesando solicitud: {user_query}"

    def _detect_if_needs_sql_query(self, user_query: str, ultimo_nivel: Dict) -> bool:
        """Detecta si la consulta de continuación necesita ejecutar SQL en lugar de solo usar LLM"""
        try:
            user_lower = user_query.lower()

            # 🎯 PRIORIDAD 1: Si es solicitud de CONSTANCIA, NO necesita SQL
            constancia_keywords = ["constancia", "certificado", "genera", "generar", "crear", "documento"]
            is_constancia_request = any(keyword in user_lower for keyword in constancia_keywords)

            if is_constancia_request:
                self.logger.debug(f"Es solicitud de constancia, NO necesita SQL: '{user_query}'")
                return False

            # Palabras clave que indican necesidad de consulta SQL
            sql_indicators = [
                "nombre", "nombres", "curp", "matrícula", "matricula", "grado", "grupo", "turno",
                "fecha", "dirección", "direccion", "teléfono", "telefono", "padre", "madre",
                "calificaciones", "promedio", "datos", "información", "informacion",
                "dame", "muestra", "dime", "cuál", "cual", "quién", "quien"
            ]

            # Si la consulta contiene indicadores de datos específicos
            if any(indicator in user_lower for indicator in sql_indicators):
                self.logger.debug(f"Detectado indicador SQL en: '{user_query}'")

                # Verificar si los datos previos son incompletos para responder
                previous_data = ultimo_nivel.get('data', [])

                if previous_data:
                    # Si los datos previos solo tienen fechas pero se piden nombres
                    if "nombre" in user_lower and all('nombre' not in str(item) for item in previous_data):
                        self.logger.debug("Datos previos no tienen nombres, necesita SQL")
                        return True

                    # Si se pide información específica que no está en los datos previos
                    if any(field in user_lower for field in ["curp", "matrícula", "grado", "grupo", "dirección"]):
                        # Verificar si esa información ya está disponible
                        has_requested_info = any(
                            any(field in str(item).lower() for item in previous_data)
                            for field in ["curp", "matrícula", "grado", "grupo", "dirección"]
                            if field in user_lower
                        )
                        if not has_requested_info:
                            self.logger.debug("Información específica no disponible, necesita SQL")
                            return True

                return True

            return False

        except Exception as e:
            self.logger.error(f"Error detectando necesidad SQL: {e}")
            return False

    def _generate_sql_for_action_continuation(self, user_query: str, ultimo_nivel: Dict) -> Optional[str]:
        """
        Genera SQL para continuación basándose en datos previos
        ✅ USA PromptManager centralizado
        """
        try:
            previous_data = ultimo_nivel.get('data', [])
            previous_query = ultimo_nivel.get('query', '')

            if not previous_data:
                return None

            # 🆕 USAR PROMPT MANAGER en lugar de prompt hardcodeado
            continuation_sql_prompt = self.prompt_manager.get_sql_continuation_prompt(
                user_query, previous_data, previous_query, self._get_sql_context()
            )

            response = self.gemini_client.send_prompt_sync(continuation_sql_prompt)

            if response:
                # Limpiar y extraer SQL
                sql_query = response.strip()

                # Remover markdown si existe
                if "```sql" in sql_query:
                    sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
                elif "```" in sql_query:
                    sql_query = sql_query.split("```")[1].strip()

                self.logger.debug(f"SQL de continuación generado: {sql_query}")
                return sql_query

            return None

        except Exception as e:
            self.logger.error(f"Error generando SQL de continuación: {e}")
            return None

    def _process_confirmation_continuation(self, user_query: str, conversation_stack: list) -> Optional[InterpretationResult]:
        """
        CONTINUACIÓN INTELIGENTE: El LLM razona qué acción ejecutar automáticamente
        """
        try:
            # Obtener el último nivel que espera confirmación
            ultimo_nivel = None
            for level in reversed(conversation_stack):
                if level.get('awaiting') in ['confirmation', 'action', 'specification']:
                    ultimo_nivel = level
                    break

            if not ultimo_nivel:
                return InterpretationResult(
                    action="continuacion_error",
                    parameters={
                        "error": "No hay acción pendiente de confirmación",
                        "message": "No encuentro ninguna acción pendiente de confirmación. ¿En qué puedo ayudarte?"
                    },
                    confidence=0.3
                )

            # 🆕 VERIFICAR SI ES CONFIRMACIÓN DE CONSTANCIA REAL (no solicitud directa)
            # CORREGIDO: Solo procesar como confirmación si realmente es una confirmación simple
            is_real_constancia_confirmation = (
                ultimo_nivel.get("estado") == "vista_previa_generada" and
                self._is_simple_confirmation(user_query)  # Solo "sí", "ok", "confirmar", etc.
            )

            if is_real_constancia_confirmation:
                self.logger.info(f"🎯 CONFIRMACIÓN SIMPLE DE CONSTANCIA DETECTADA")
                self.logger.info(f"   - Estado: {ultimo_nivel.get('estado', 'N/A')}")
                self.logger.info(f"   - Awaiting: {ultimo_nivel.get('awaiting', 'N/A')}")
                self.logger.info(f"   - Tipo constancia: {ultimo_nivel.get('tipo_constancia', 'N/A')}")

                confirmation_type = self._detect_confirmation_type(user_query, ultimo_nivel)
                self.logger.info(f"   - Tipo confirmación: {confirmation_type}")

                return self._process_constancia_confirmation(user_query, confirmation_type, ultimo_nivel)

            # 🧠 PROMPT INTELIGENTE: LLM decide qué hacer automáticamente
            intelligent_continuation_prompt = f"""
Eres el asistente inteligente de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ".

CONTEXTO CONVERSACIONAL:
- Consulta anterior del usuario: "{ultimo_nivel.get('query', 'N/A')}"
- Mi respuesta anterior: "{ultimo_nivel.get('message', 'N/A')[:200]}..."
- Tipo de continuación esperada: {ultimo_nivel.get('awaiting', 'N/A')}
- Datos disponibles: {ultimo_nivel.get('row_count', 0)} elementos

NUEVA CONSULTA DEL USUARIO: "{user_query}"

🧠 ANÁLISIS INTELIGENTE:
El usuario está confirmando/continuando con la acción anterior. Debo:

1. RAZONAR sobre qué acción específica ejecutar
2. GENERAR automáticamente la consulta SQL necesaria
3. ACTUAR sin preguntar más

EJEMPLOS DE RAZONAMIENTO:
- Si era "estadísticas" → Generar estadísticas detalladas por grado/turno/calificaciones
- Si era "lista de alumnos" → Proporcionar más detalles o servicios
- Si era "búsqueda" → Ofrecer acciones específicas para los resultados

ESTRUCTURA DE LA BASE DE DATOS:
{self._get_sql_context()}

INSTRUCCIONES:
1. Analiza qué quiere el usuario basado en el contexto
2. Genera la consulta SQL apropiada para completar la acción
3. NO preguntes más, EJECUTA la acción

RESPONDE CON:
{{
    "accion_a_ejecutar": "generar_sql|proporcionar_info|ofrecer_servicios",
    "sql_query": "SELECT ... (si aplica)",
    "razonamiento": "Por qué esta es la acción correcta",
    "mensaje_usuario": "Respuesta natural para el usuario"
}}
"""

            # Enviar al LLM para decisión inteligente
            response = self.gemini_client.send_prompt_sync(intelligent_continuation_prompt)
            continuation_decision = self._parse_json_response(response)

            if not continuation_decision:
                # Fallback: respuesta básica
                return InterpretationResult(
                    action="confirmacion_realizada",
                    parameters={
                        "message": f"Perfecto, continuando con la acción basada en: '{ultimo_nivel.get('query', 'consulta anterior')}'",
                        "accion_confirmada": ultimo_nivel.get('query', ''),
                        "tipo": "confirmacion"
                    },
                    confidence=0.6
                )

            # Ejecutar la acción decidida por el LLM
            accion = continuation_decision.get('accion_a_ejecutar', 'proporcionar_info')

            if accion == 'generar_sql' and continuation_decision.get('sql_query'):
                # 🚀 EJECUTAR SQL AUTOMÁTICAMENTE
                sql_query = continuation_decision.get('sql_query')
                self.logger.debug(f"LLM decidió ejecutar SQL: {sql_query[:100]}...")

                result = self.sql_executor.execute_query(sql_query)

                if result.success:
                    # Generar respuesta final con los nuevos datos
                    final_response = self._validate_and_generate_response(
                        f"{ultimo_nivel.get('query', '')} (continuación: {user_query})",
                        sql_query, result.data, result.row_count
                    )

                    if final_response:
                        return InterpretationResult(
                            action="consulta_sql_exitosa",
                            parameters={
                                "sql_query": result.query_executed,
                                "data": result.data,
                                "row_count": result.row_count,
                                "message": final_response.get("respuesta_usuario", continuation_decision.get('mensaje_usuario', 'Acción completada')),
                                "human_response": final_response.get("respuesta_usuario", continuation_decision.get('mensaje_usuario', 'Acción completada')),
                                "auto_reflexion": final_response.get("reflexion_conversacional", {}),
                                "tipo": "continuacion_inteligente"
                            },
                            confidence=0.9
                        )

            # Si no es SQL o falló, usar respuesta del LLM
            return InterpretationResult(
                action="continuacion_inteligente",
                parameters={
                    "message": continuation_decision.get('mensaje_usuario', 'Acción completada'),
                    "razonamiento": continuation_decision.get('razonamiento', ''),
                    "accion_confirmada": ultimo_nivel.get('query', ''),
                    "tipo": "continuacion"
                },
                confidence=0.8
            )

        except Exception as e:
            self.logger.error(f"Error en continuación inteligente: {e}")
            return None

    def _process_specification_continuation(self, user_query: str, conversation_stack: list) -> Optional[InterpretationResult]:
        """Procesa continuación de tipo ESPECIFICACIÓN (ej: 'de qué tipo', 'con foto')"""
        try:
            # Obtener el último nivel que espera especificación
            ultimo_nivel = None
            for level in reversed(conversation_stack):
                if level.get('awaiting') == 'specification':
                    ultimo_nivel = level
                    break

            if not ultimo_nivel:
                return InterpretationResult(
                    action="continuacion_error",
                    parameters={
                        "error": "No hay especificación pendiente",
                        "message": "No encuentro ninguna especificación pendiente. ¿Qué información específica necesitas?"
                    },
                    confidence=0.3
                )

            # Generar respuesta de especificación
            response_message = f"Entendido, procesando especificación '{user_query}' para: '{ultimo_nivel.get('query', 'consulta anterior')}'"

            return InterpretationResult(
                action="especificacion_realizada",
                parameters={
                    "message": response_message,
                    "especificacion": user_query,
                    "consulta_original": ultimo_nivel.get('query', ''),
                    "tipo": "especificacion"
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error en especificación: {e}")
            return None

    def _get_sql_context(self) -> str:
        """Obtiene el contexto SQL (con cache)"""
        if self._sql_context is None:
            self._sql_context = self.database_analyzer.generate_sql_context()
        return self._sql_context

    def _detect_student_query_intention_centralized(self, user_query: str, conversation_context: str = "") -> bool:
        """
        PROMPT 1 CENTRALIZADO: Detecta si la consulta es sobre alumnos/estudiantes
        🆕 MEJORADO: Ahora incluye contexto conversacional
        REEMPLAZA: _detect_student_query_intention() (método eliminado)
        """
        try:
            # 🎯 USAR PROMPT MANAGER CENTRALIZADO CON CONTEXTO CONVERSACIONAL
            intention_prompt = self.prompt_manager.get_student_query_intention_prompt(user_query, conversation_context)

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(intention_prompt)

            if response:
                # Parsear respuesta
                intention_result = self._parse_intention_response(response)

                if intention_result:
                    is_student_query = intention_result.get('es_consulta_alumnos', False)
                    query_type = intention_result.get('tipo_detectado', 'otro')
                    requires_context = intention_result.get('requiere_contexto', False)
                    continuation_type = intention_result.get('tipo_continuacion', 'nueva_consulta')

                    # Guardar información adicional para uso posterior
                    self._current_query_type = query_type
                    self._requires_context = requires_context
                    self._continuation_type = continuation_type

                    self.logger.info(f"🧠 ANÁLISIS CONVERSACIONAL:")
                    self.logger.info(f"   - Tipo detectado: {query_type}")
                    self.logger.info(f"   - Requiere contexto: {requires_context}")
                    self.logger.info(f"   - Tipo continuación: {continuation_type}")

                    return is_student_query
                else:
                    return False
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error detectando intención centralizada: {e}")
            return False

    def _parse_intention_response(self, intention_response: str) -> Optional[Dict[str, Any]]:
        """Parsea la respuesta de detección de intención"""
        try:
            # Limpiar la respuesta
            clean_response = intention_response.strip()

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
                        import json
                        intention = json.loads(matches[0])
                        return intention
                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON, intentar parsear directamente
            try:
                import json
                intention = json.loads(clean_response)
                return intention
            except json.JSONDecodeError:
                return None

        except Exception as e:
            return None

    def _generate_sql_with_strategy_centralized(self, user_query: str) -> Optional[str]:
        """
        PROMPT 2 CENTRALIZADO: Genera estrategia + SQL en un solo paso
        REEMPLAZA: _generate_sql_with_strategy() (método eliminado)
        """
        try:
            # 🎯 USAR PROMPT MANAGER CENTRALIZADO
            combined_prompt = self.prompt_manager.get_sql_generation_prompt(user_query)

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(combined_prompt)

            if response:
                # Extraer SQL de la respuesta
                sql_query = self._extract_sql_from_response(response)

                if sql_query:
                    return sql_query
                else:
                    return None
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error generando SQL centralizado: {e}")
            return None

    def _validate_and_generate_response(self, user_query: str, sql_query: str, data: List[Dict], row_count: int) -> Optional[Dict]:
        """
        PROMPT 3 CON AUTO-REFLEXIÓN + FILTRO INTELIGENTE: Filtra datos + Valida SQL + Genera respuesta + Auto-reflexiona sobre continuación
        🆕 AHORA USA PromptManager centralizado
        """
        try:
            # 🧠 PASO 1: APLICAR FILTRO INTELIGENTE FINAL
            filtered_data, filter_decision = self._intelligent_final_filter(user_query, data, sql_query)

            self.logger.debug(f"Filtro inteligente aplicado:")
            self.logger.debug(f"   - Datos originales: {len(data)} registros")
            self.logger.debug(f"   - Datos filtrados: {len(filtered_data)} registros")
            self.logger.debug(f"   - Resuelve consulta: {filter_decision.get('resuelve_consulta', 'N/A')}")

            # Si el filtro detectó que no resuelve la consulta, fallar temprano
            if not filter_decision.get('resuelve_consulta', True):
                self.logger.warning("Filtro inteligente detectó que los datos no resuelven la consulta")
                return None

            # Usar los datos filtrados para el resto del proceso
            final_data = filtered_data
            final_row_count = len(filtered_data)

            # Formatear los datos filtrados para el prompt de manera más clara
            data_summary = self._format_data_for_validation_prompt(final_data, final_row_count, sql_query)

            # 🆕 USAR PROMPT MANAGER en lugar de prompt hardcodeado
            validation_response_prompt = self.prompt_manager.get_validation_and_response_prompt(
                user_query, sql_query, data_summary, filter_decision, final_row_count, len(data)
            )

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(validation_response_prompt)

            if response:
                # Verificar si la validación falló
                if "VALIDACION_FALLIDA" in response.upper():
                    return None

                # Parsear respuesta JSON con auto-reflexión
                parsed_response = self._parse_json_response(response)
                if parsed_response and "respuesta_usuario" in parsed_response:
                    print(f"🧠 DEBUG - Auto-reflexión LLM: {parsed_response.get('reflexion_conversacional', {}).get('razonamiento', 'N/A')}")
                    return parsed_response
                else:
                    # Fallback: El LLM devolvió JSON crudo, extraer solo la respuesta del usuario
                    print(f"⚠️ DEBUG - Respuesta no es JSON válido, intentando extraer texto")

                    # Intentar extraer respuesta_usuario del JSON crudo
                    try:
                        # Buscar "respuesta_usuario" en el texto
                        match = re.search(r'"respuesta_usuario":\s*"([^"]*(?:\\.[^"]*)*)"', response, re.DOTALL)
                        if match:
                            respuesta_extraida = match.group(1).replace('\\"', '"').replace('\\n', '\n')
                            self.logger.debug("Respuesta extraída exitosamente")
                            return {
                                "respuesta_usuario": respuesta_extraida,
                                "reflexion_conversacional": {
                                    "espera_continuacion": False,
                                    "tipo_esperado": "none",
                                    "datos_recordar": {},
                                    "razonamiento": "Respuesta extraída de JSON crudo"
                                }
                            }
                    except Exception as e:
                        self.logger.error(f"Error extrayendo respuesta: {e}")

                    # Si todo falla, usar respuesta completa
                    return {
                        "respuesta_usuario": "Error procesando respuesta. Por favor, reformula tu consulta.",
                        "reflexion_conversacional": {
                            "espera_continuacion": False,
                            "tipo_esperado": "none",
                            "datos_recordar": {},
                            "razonamiento": "Error en procesamiento (fallback final)"
                        }
                    }
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error en validación con auto-reflexión: {e}")
            return None

    def _format_data_for_validation_prompt(self, data: List[Dict], row_count: int, sql_query: str) -> str:
        """
        Formatea los datos específicamente para el prompt de validación
        """
        try:
            # Detectar si es una consulta COUNT
            if 'count(' in sql_query.lower() or any(key.lower() in ['total', 'count(*)', 'count', 'cantidad'] for row in data for key in row.keys()):
                if data and len(data) > 0:
                    first_row = data[0]
                    for key, value in first_row.items():
                        if key.lower() in ['total', 'count(*)', 'count', 'cantidad']:
                            return f"""
TIPO DE CONSULTA: COUNT (conteo)
RESULTADO NUMÉRICO: {value}
INTERPRETACIÓN: La consulta devolvió un conteo de {value} alumnos
DATOS BRUTOS: {data}
"""

            # Para consultas SELECT normales
            return f"""
TIPO DE CONSULTA: SELECT (listado)
NÚMERO DE REGISTROS: {row_count}
DATOS OBTENIDOS: {data if row_count <= 15 else data[:10]}
{"... y " + str(row_count - 10) + " registros adicionales" if row_count > 10 else ""}
"""

        except Exception as e:
            self.logger.error(f"Error formateando datos para validación: {e}")
            return f"DATOS: {row_count} registros obtenidos"

    def _extract_sql_from_response(self, response: str) -> Optional[str]:
        """Extrae SQL de la respuesta del LLM"""
        try:
            # Limpiar la respuesta
            clean_response = response.strip()

            # Buscar SQL en markdown
            if "```sql" in clean_response:
                sql_query = clean_response.split("```sql")[1].split("```")[0].strip()
                return sql_query
            elif "```" in clean_response:
                sql_query = clean_response.split("```")[1].strip()
                return sql_query
            else:
                # Asumir que toda la respuesta es SQL
                return clean_response

        except Exception as e:
            self.logger.error(f"Error extrayendo SQL: {e}")
            return None

    # 🗑️ MÉTODO DUPLICADO ELIMINADO: _parse_intention_response()
    # RAZÓN: Ya existe una versión idéntica arriba (línea 976)
    # MANTENER: Solo la primera versión



    def _intelligent_final_filter(self, user_query: str, data: List[Dict], sql_query: str) -> Tuple[List[Dict], Dict[str, Any]]:
        """
        FILTRO INTELIGENTE FINAL: Asegura que los datos resuelvan exactamente la consulta original
        🆕 AHORA USA PromptManager centralizado
        """
        try:
            self.logger.debug("Aplicando filtro inteligente final")
            self.logger.debug(f"   - Consulta: {user_query}")
            self.logger.debug(f"   - Datos obtenidos: {len(data)} registros")

            # 🆕 USAR PROMPT MANAGER en lugar de prompt hardcodeado
            filter_prompt = self.prompt_manager.get_filter_prompt(user_query, data, sql_query)

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(filter_prompt)

            if response:
                # Parsear respuesta del filtro
                filter_decision = self._parse_filter_response(response)

                if filter_decision:
                    # Aplicar el filtrado según la decisión
                    filtered_data = self._apply_filter_decision(data, filter_decision)

                    self.logger.debug("Filtro aplicado:")
                    self.logger.debug(f"   - Acción: {filter_decision.get('accion_requerida')}")
                    self.logger.debug(f"   - Cantidad final: {filter_decision.get('cantidad_final')}")
                    self.logger.debug(f"   - Resuelve consulta: {filter_decision.get('resuelve_consulta')}")

                    return filtered_data, filter_decision
                else:
                    self.logger.warning("Error parseando decisión de filtro")
                    return data, {"accion_requerida": "mantener", "resuelve_consulta": True}
            else:
                self.logger.warning("Error en filtro inteligente, manteniendo datos originales")
                return data, {"accion_requerida": "mantener", "resuelve_consulta": True}

        except Exception as e:
            self.logger.error(f"Error en filtro inteligente: {e}")
            return data, {"accion_requerida": "mantener", "resuelve_consulta": True}

    def _parse_filter_response(self, filter_response: str) -> Optional[Dict[str, Any]]:
        """Parsea la respuesta del filtro inteligente"""
        try:
            # Limpiar la respuesta
            clean_response = filter_response.strip()

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
                        filter_decision = json.loads(matches[0])
                        return filter_decision
                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON, intentar parsear directamente
            try:
                filter_decision = json.loads(clean_response)
                return filter_decision
            except json.JSONDecodeError:
                return None

        except Exception as e:
            self.logger.error(f"Error parseando filtro: {e}")
            return None

    def _apply_filter_decision(self, data: List[Dict], filter_decision: Dict[str, Any]) -> List[Dict]:
        """Aplica la decisión del filtro a los datos"""
        try:
            # accion = filter_decision.get('accion_requerida', 'mantener')  # No se usa actualmente
            cantidad_final = filter_decision.get('cantidad_final', len(data))
            campos_incluir = filter_decision.get('campos_incluir', 'todos')
            registros_seleccionar = filter_decision.get('registros_seleccionar', 'todos')

            # Filtrar registros por cantidad
            if registros_seleccionar == 'todos':
                if isinstance(cantidad_final, int) and cantidad_final < len(data):
                    filtered_data = data[:cantidad_final]
                else:
                    filtered_data = data
            else:
                # Seleccionar registros específicos por índice
                filtered_data = []
                for idx in registros_seleccionar:
                    if 0 <= idx < len(data):
                        filtered_data.append(data[idx])

            # Filtrar campos si es necesario
            if campos_incluir != 'todos' and isinstance(campos_incluir, list):
                final_data = []
                for record in filtered_data:
                    filtered_record = {}
                    for campo in campos_incluir:
                        if campo in record:
                            filtered_record[campo] = record[campo]
                    final_data.append(filtered_record)
                return final_data
            else:
                return filtered_data

        except Exception as e:
            self.logger.error(f"Error aplicando filtro: {e}")
            return data








    def _process_constancia_request(self, user_query: str, context: Dict[str, Any] = None) -> Optional[InterpretationResult]:
        """
        🆕 PROCESA SOLICITUDES DE CONSTANCIAS DIRECTAMENTE
        Extrae nombre del alumno y tipo de constancia, luego genera vista previa
        """
        try:
            self.logger.info(f"🎯 _process_constancia_request INICIADO")
            self.logger.info(f"   - Query: '{user_query}'")
            self.logger.info(f"   - Context: {context is not None}")
            if context:
                self.logger.info(f"   - PDF Panel: {getattr(context, 'pdf_panel', None) is not None}")
                self.logger.info(f"   - Entidades detectadas: {getattr(context, 'detected_entities', {})}")

            # 🚀 USAR ENTIDADES DETECTADAS SI ESTÁN DISPONIBLES
            # 🆕 DEBUGGING PROFUNDO - RASTREAR DÓNDE ESTÁN LAS ENTIDADES
            self.logger.debug(f"🔍 DEBUGGING CONTEXTO COMPLETO:")
            self.logger.debug(f"   - Tipo de contexto: {type(context)}")
            self.logger.debug(f"   - Atributos del contexto: {dir(context)}")
            self.logger.debug(f"   - hasattr intention_info: {hasattr(context, 'intention_info')}")

            if hasattr(context, 'intention_info'):
                self.logger.debug(f"   - intention_info: {context.intention_info}")
                self.logger.debug(f"   - tipo intention_info: {type(context.intention_info)}")

            # 🆕 ACCESO CORRECTO A ENTIDADES DEL MASTER
            detected_entities = {}
            if hasattr(context, 'intention_info') and context.intention_info:
                detected_entities = context.intention_info.get('detected_entities', {})
                self.logger.debug(f"   - Entidades desde intention_info: {detected_entities}")

            # Fallback: buscar en contexto directo (compatibilidad)
            if not detected_entities and context:
                detected_entities = getattr(context, 'detected_entities', {})
                self.logger.debug(f"   - Entidades desde contexto directo: {detected_entities}")

            self.logger.debug(f"🔍 ENTIDADES FINALES DETECTADAS: {detected_entities}")

            # 🆕 SOLO USAR ENTIDADES DEL MASTER (sin fallbacks)
            if not detected_entities:
                self.logger.error("❌ No hay entidades detectadas del Master para constancia")
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": "❌ Error: No se detectaron entidades para la constancia",
                        "error": "no_entities_detected"
                    },
                    confidence=0.1
                )

            self.logger.info("🎯 USANDO ENTIDADES PRE-DETECTADAS DEL MASTER")
            constancia_info = {
                'es_solicitud_constancia': True,
                'nombre_alumno': detected_entities.get('nombres', [None])[0] if detected_entities.get('nombres') else None,
                'tipo_constancia': detected_entities.get('tipo_constancia'),
                'fuente_datos': detected_entities.get('fuente_datos', 'base_datos'),
                'contexto_especifico': detected_entities.get('contexto_especifico'),
                'incluir_foto': detected_entities.get('incluir_foto', False),  # 🆕 FOTO DEL MASTER
                'confianza': 0.95
            }
            self.logger.info(f"   - Info construida: {constancia_info}")

            if not constancia_info:
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": "No pude entender qué constancia necesitas. Por favor especifica el nombre del alumno y tipo de constancia.",
                        "error": "info_extraction_failed"
                    },
                    confidence=0.3
                )

            # 🆕 VERIFICAR SI HAY PDF CARGADO PARA TRANSFORMACIÓN
            pdf_panel = getattr(context, 'pdf_panel', None)
            if pdf_panel and hasattr(pdf_panel, 'original_pdf') and pdf_panel.original_pdf:
                # 🎯 DISTINGUIR ENTRE PDF EXTERNO VS VISTA PREVIA GENERADA
                is_external_pdf = self._is_external_pdf_loaded(pdf_panel)
                is_transformation_request = self._is_transformation_request(constancia_info, detected_entities)

                self.logger.info(f"📄 ANÁLISIS DE PDF:")
                self.logger.info(f"   - PDF cargado: {pdf_panel.original_pdf}")
                self.logger.info(f"   - Es PDF externo: {is_external_pdf}")
                self.logger.info(f"   - Es solicitud de transformación: {is_transformation_request}")

                # SOLO procesar como transformación si es PDF externo Y solicitud de transformación
                if is_external_pdf and is_transformation_request:
                    self.logger.info(f"🔄 TRANSFORMACIÓN: PDF externo + solicitud de transformación")
                    return self._process_constancia_from_pdf(constancia_info, pdf_panel, context)
                else:
                    self.logger.info(f"📊 NUEVA CONSTANCIA: Ignorando PDF de vista previa, generando nueva constancia desde BD")

            # FLUJO NORMAL: Buscar alumno por nombre en BD
            alumno = self._find_student_by_name(constancia_info.get("nombre_alumno", ""))

            if not alumno:
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": f"No encontré al alumno '{constancia_info.get('nombre_alumno', '')}'. Verifica el nombre e intenta nuevamente.",
                        "error": "student_not_found",
                        "searched_name": constancia_info.get('nombre_alumno', ''),
                        "suggestion": "Intenta con el nombre completo o usa 'buscar alumnos' para ver opciones disponibles."
                    },
                    confidence=0.3
                )

            # 🆕 VERIFICAR SI ES CASO DE DEMASIADAS COINCIDENCIAS
            if alumno.get('_too_many_matches'):
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": alumno.get('message', 'Demasiadas coincidencias encontradas.'),
                        "error": "too_many_matches",
                        "total_found": alumno.get('total_found', 0),
                        "search_term": alumno.get('search_term', ''),
                        "suggestion": f"Encontré {alumno.get('total_found', 0)} estudiantes. Intenta con nombre y apellido completos."
                    },
                    confidence=0.7
                )

            # 🆕 INFORMAR SOBRE MÚLTIPLES COINCIDENCIAS SI LAS HAY
            if alumno.get('_multiple_matches'):
                multiple_info = alumno['_multiple_matches']
                self.logger.info(f"📋 Se encontraron {multiple_info['total_found']} coincidencias para '{multiple_info['search_term']}'")
                self.logger.info(f"✅ Seleccionado: {multiple_info['selected']}")
                if len(multiple_info['options']) > 1:
                    self.logger.info(f"📝 Otras opciones: {', '.join(multiple_info['options'][1:])}")

                # Limpiar la información temporal antes de continuar
                del alumno['_multiple_matches']

            # Generar constancia en modo vista previa
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            constancia_service = service_provider.constancia_service

            # 🔧 NORMALIZAR TIPO DE CONSTANCIA
            tipo_raw = constancia_info.get("tipo_constancia", "estudio")
            tipo_constancia = self._normalize_constancia_type(tipo_raw)
            incluir_foto = constancia_info.get("incluir_foto", False)

            self.logger.info(f"🎯 GENERANDO CONSTANCIA:")
            self.logger.info(f"   - Tipo: {tipo_constancia}")
            self.logger.info(f"   - Alumno: {alumno.get('nombre')} (ID: {alumno.get('id')})")
            self.logger.info(f"   - Incluir foto: {incluir_foto}")
            self.logger.info(f"   - Preview mode: True")

            # Generar vista previa
            self.logger.info("🔄 Llamando a constancia_service.generar_constancia_para_alumno()...")
            success, message, data = constancia_service.generar_constancia_para_alumno(
                alumno.get("id"), tipo_constancia, incluir_foto, preview_mode=True
            )

            self.logger.info(f"📊 RESULTADO DEL SERVICIO:")
            self.logger.info(f"   - Success: {success}")
            self.logger.info(f"   - Message: {message}")
            self.logger.info(f"   - Data: {data is not None} ({'keys: ' + str(list(data.keys())) if data else 'None'})")

            if success and data:
                # Generar respuesta con AUTO-REFLEXIÓN sobre constancia
                self.logger.debug(f"🧠 Generando auto-reflexión para constancia de {tipo_constancia}")
                response_with_reflection = self._generate_constancia_response_with_reflection(
                    alumno, tipo_constancia, data
                )

                if response_with_reflection:
                    self.logger.debug(f"✅ Auto-reflexión generada: {response_with_reflection.get('reflexion_conversacional', {})}")
                    return InterpretationResult(
                        action="constancia_preview",  # Acción especial para ChatEngine
                        parameters={
                            "message": response_with_reflection.get("respuesta_usuario", "Vista previa generada"),
                            "data": data,
                            "files": [data.get("ruta_archivo")] if data.get("ruta_archivo") else [],
                            "alumno": alumno,
                            "tipo_constancia": tipo_constancia,
                            "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {})
                        },
                        confidence=0.95
                    )
                else:
                    self.logger.warning("❌ No se pudo generar auto-reflexión, usando respuesta simple")
                    return InterpretationResult(
                        action="constancia_preview",
                        parameters={
                            "message": f"Vista previa de constancia de {tipo_constancia} generada para {alumno.get('nombre')}",
                            "data": data,
                            "files": [data.get("ruta_archivo")] if data.get("ruta_archivo") else [],
                            "alumno": alumno,
                            "tipo_constancia": tipo_constancia
                        },
                        confidence=0.9
                    )
            else:
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": f"Error generando constancia: {message}",
                        "error": "generation_failed",
                        "service_message": message
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando constancia: {e}")
            return InterpretationResult(
                action="constancia_error",
                parameters={
                    "message": "Error interno procesando la constancia. Intenta nuevamente.",
                    "error": "internal_error",
                    "exception": str(e)
                },
                confidence=0.1
            )

    # 🗑️ MÉTODO ELIMINADO: _extract_constancia_info
    # RAZÓN: Ahora solo usamos entidades del Master, sin fallbacks LLM

    # 🗑️ MÉTODO ELIMINADO: _build_intelligent_context
    # RAZÓN: Ya no se usa, era parte del sistema LLM fallback eliminado

    def _normalize_constancia_type(self, tipo_raw: str) -> str:
        """Normaliza el tipo de constancia a los valores esperados por el servicio"""
        if not tipo_raw:
            return "estudio"

        tipo_lower = tipo_raw.lower().strip()

        # Mapeo de variaciones a tipos válidos
        tipo_mapping = {
            # Estudios/Estudio
            "estudios": "estudio",
            "estudio": "estudio",
            "de estudios": "estudio",
            "de estudio": "estudio",

            # Calificaciones
            "calificaciones": "calificaciones",
            "calificacion": "calificaciones",
            "notas": "calificaciones",
            "boleta": "calificaciones",

            # Traslado
            "traslado": "traslado",
            "transferencia": "traslado",
            "cambio": "traslado"
        }

        # Buscar coincidencia exacta
        if tipo_lower in tipo_mapping:
            normalized = tipo_mapping[tipo_lower]
            self.logger.debug(f"🔧 Tipo normalizado: '{tipo_raw}' → '{normalized}'")
            return normalized

        # Buscar coincidencia parcial
        for key, value in tipo_mapping.items():
            if key in tipo_lower:
                self.logger.debug(f"🔧 Tipo normalizado (parcial): '{tipo_raw}' → '{value}'")
                return value

        # Por defecto, estudio
        self.logger.warning(f"⚠️ Tipo de constancia no reconocido: '{tipo_raw}', usando 'estudio' por defecto")
        return "estudio"

    def _find_student_by_name(self, nombre: str) -> Optional[Dict[str, Any]]:
        """Busca alumno por nombre con manejo inteligente de múltiples coincidencias y tolerancia a errores"""
        try:
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            alumno_service = service_provider.alumno_service

            # 🎯 ESTRATEGIA 1: Búsqueda exacta
            alumnos = alumno_service.buscar_alumnos(nombre)

            if not alumnos:
                # 🎯 ESTRATEGIA 2: Búsqueda con tolerancia a errores tipográficos
                self.logger.info(f"🔍 No se encontró '{nombre}', intentando búsqueda con tolerancia a errores...")
                alumnos = self._fuzzy_search_students(nombre, alumno_service)

            if not alumnos:
                self.logger.debug(f"❌ No se encontraron alumnos con '{nombre}' (incluso con tolerancia a errores)")
                return None
            elif len(alumnos) == 1:
                # ✅ UNA SOLA COINCIDENCIA - PERFECTO
                self.logger.debug(f"✅ Alumno único encontrado: {alumnos[0].get('nombre', 'N/A')}")
                primer_alumno = alumnos[0]
                if hasattr(primer_alumno, 'to_dict'):
                    return primer_alumno.to_dict()
                else:
                    return primer_alumno
            else:
                # 🔍 MÚLTIPLES COINCIDENCIAS - MANEJAR INTELIGENTEMENTE
                return self._handle_multiple_students(alumnos, nombre)

        except Exception as e:
            self.logger.error(f"Error buscando alumno: {e}")
            return None

    def _fuzzy_search_students(self, nombre_buscado: str, alumno_service) -> List:
        """Búsqueda con tolerancia a errores tipográficos"""
        try:
            # 🎯 ESTRATEGIAS DE BÚSQUEDA TOLERANTE:

            # 1. Buscar por cada palabra del nombre
            palabras = nombre_buscado.split()
            candidatos = []

            for palabra in palabras:
                if len(palabra) >= 3:  # Solo palabras de 3+ caracteres
                    resultados = alumno_service.buscar_alumnos(palabra)
                    candidatos.extend(resultados)

            # 2. Buscar variaciones comunes de nombres
            variaciones = self._generate_name_variations(nombre_buscado)
            for variacion in variaciones:
                resultados = alumno_service.buscar_alumnos(variacion)
                candidatos.extend(resultados)

            # 3. Eliminar duplicados
            alumnos_unicos = []
            ids_vistos = set()

            for alumno in candidatos:
                alumno_dict = alumno.to_dict() if hasattr(alumno, 'to_dict') else alumno
                alumno_id = alumno_dict.get('id')
                if alumno_id not in ids_vistos:
                    ids_vistos.add(alumno_id)
                    alumnos_unicos.append(alumno_dict)

            # 4. Filtrar por similitud de nombre
            if alumnos_unicos:
                alumnos_filtrados = self._filter_by_name_similarity(nombre_buscado, alumnos_unicos)
                if alumnos_filtrados:
                    self.logger.info(f"✅ Encontrados {len(alumnos_filtrados)} candidatos con búsqueda tolerante")
                    return alumnos_filtrados

            return []

        except Exception as e:
            self.logger.error(f"Error en búsqueda tolerante: {e}")
            return []

    def _generate_name_variations(self, nombre: str) -> List[str]:
        """Genera variaciones comunes de nombres para búsqueda tolerante"""
        variaciones = []
        nombre_lower = nombre.lower()

        # Correcciones comunes de nombres
        correcciones = {
            'habriela': 'gabriela',
            'habriel': 'gabriel',
            'nataly': 'natalia',
            'nathalia': 'natalia',
            'maria': 'maría',
            'jose': 'josé',
            'jesus': 'jesús',
            'andres': 'andrés',
            'adrian': 'adrián',
            'sebastian': 'sebastián'
        }

        # Aplicar correcciones
        for error, correccion in correcciones.items():
            if error in nombre_lower:
                variacion = nombre_lower.replace(error, correccion)
                variaciones.append(variacion.title())

        # Variaciones sin acentos
        sin_acentos = nombre.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        if sin_acentos != nombre:
            variaciones.append(sin_acentos)

        # Variaciones con acentos comunes
        con_acentos = nombre.replace('a', 'á').replace('e', 'é').replace('i', 'í').replace('o', 'ó').replace('u', 'ú')
        if con_acentos != nombre:
            variaciones.append(con_acentos)

        return list(set(variaciones))  # Eliminar duplicados

    def _filter_by_name_similarity(self, nombre_buscado: str, alumnos: List[Dict]) -> List[Dict]:
        """Filtra alumnos por similitud de nombre usando algoritmo simple"""
        try:
            candidatos_con_score = []
            nombre_buscado_lower = nombre_buscado.lower()

            for alumno in alumnos:
                nombre_alumno = alumno.get('nombre', '').lower()

                # Calcular similitud simple
                score = self._calculate_name_similarity(nombre_buscado_lower, nombre_alumno)

                # Solo incluir si tiene similitud razonable (>= 0.6)
                if score >= 0.6:
                    candidatos_con_score.append((alumno, score))

            # Ordenar por score descendente
            candidatos_con_score.sort(key=lambda x: x[1], reverse=True)

            # Devolver solo los alumnos (sin scores)
            return [alumno for alumno, score in candidatos_con_score]

        except Exception as e:
            self.logger.error(f"Error filtrando por similitud: {e}")
            return alumnos

    def _calculate_name_similarity(self, nombre1: str, nombre2: str) -> float:
        """Calcula similitud entre dos nombres usando algoritmo simple"""
        try:
            # Algoritmo simple de similitud basado en caracteres comunes
            if not nombre1 or not nombre2:
                return 0.0

            # Convertir a conjuntos de caracteres
            chars1 = set(nombre1.replace(' ', ''))
            chars2 = set(nombre2.replace(' ', ''))

            # Calcular intersección y unión
            interseccion = len(chars1.intersection(chars2))
            union = len(chars1.union(chars2))

            # Similitud de Jaccard
            if union == 0:
                return 0.0

            jaccard = interseccion / union

            # Bonus por palabras comunes
            palabras1 = set(nombre1.split())
            palabras2 = set(nombre2.split())
            palabras_comunes = len(palabras1.intersection(palabras2))

            # Score final combinado
            score = jaccard + (palabras_comunes * 0.2)
            return min(score, 1.0)  # Máximo 1.0

        except Exception as e:
            self.logger.error(f"Error calculando similitud: {e}")
            return 0.0

    def _handle_multiple_students(self, alumnos: List, nombre_buscado: str) -> Optional[Dict[str, Any]]:
        """Maneja múltiples coincidencias de estudiantes de forma inteligente"""
        try:
            self.logger.info(f"🔍 Encontradas {len(alumnos)} coincidencias para '{nombre_buscado}'")

            # 🎯 ESTRATEGIA 1: Buscar coincidencia exacta (nombre completo)
            for alumno in alumnos:
                alumno_dict = alumno.to_dict() if hasattr(alumno, 'to_dict') else alumno
                nombre_completo = alumno_dict.get('nombre', '').upper()
                if nombre_completo == nombre_buscado.upper():
                    self.logger.info(f"✅ Coincidencia exacta encontrada: {nombre_completo}")
                    return alumno_dict

            # 🎯 ESTRATEGIA 2: Si hay pocas coincidencias (2-5), tomar la primera y avisar
            if len(alumnos) <= 5:
                primer_alumno = alumnos[0]
                alumno_dict = primer_alumno.to_dict() if hasattr(primer_alumno, 'to_dict') else primer_alumno

                # Crear lista de nombres para mostrar al usuario
                nombres_encontrados = []
                for alumno in alumnos[:5]:
                    alumno_temp = alumno.to_dict() if hasattr(alumno, 'to_dict') else alumno
                    nombres_encontrados.append(alumno_temp.get('nombre', 'N/A'))

                self.logger.info(f"⚠️ Múltiples coincidencias, usando primera: {alumno_dict.get('nombre', 'N/A')}")
                self.logger.info(f"📋 Opciones encontradas: {', '.join(nombres_encontrados)}")

                # Agregar información de múltiples coincidencias al alumno
                alumno_dict['_multiple_matches'] = {
                    'total_found': len(alumnos),
                    'options': nombres_encontrados,
                    'selected': alumno_dict.get('nombre', 'N/A'),
                    'search_term': nombre_buscado
                }

                return alumno_dict

            # 🎯 ESTRATEGIA 3: Si hay muchas coincidencias (6+), devolver información especial
            else:
                self.logger.warning(f"❌ Demasiadas coincidencias ({len(alumnos)}) para '{nombre_buscado}'. Se requiere nombre más específico.")

                # Devolver diccionario especial para indicar múltiples coincidencias
                return {
                    '_too_many_matches': True,
                    'total_found': len(alumnos),
                    'search_term': nombre_buscado,
                    'message': f"Encontré {len(alumnos)} estudiantes con '{nombre_buscado}'. Por favor, sé más específico con el nombre."
                }

        except Exception as e:
            self.logger.error(f"Error manejando múltiples estudiantes: {e}")
            # En caso de error, devolver el primero como fallback
            primer_alumno = alumnos[0] if alumnos else None
            if primer_alumno:
                return primer_alumno.to_dict() if hasattr(primer_alumno, 'to_dict') else primer_alumno
            return None

    def _is_external_pdf_loaded(self, pdf_panel) -> bool:
        """Determina si el PDF cargado es externo (no generado por vista previa)"""
        try:
            if not pdf_panel or not hasattr(pdf_panel, 'original_pdf'):
                return False

            pdf_path = pdf_panel.original_pdf

            # 🎯 CRITERIOS PARA DETECTAR PDF EXTERNO:
            # 1. NO está en directorio temporal del sistema
            # 2. NO contiene palabras de vista previa en el nombre
            # 3. Fue cargado por el usuario (no generado automáticamente)

            import tempfile

            temp_dir = tempfile.gettempdir()

            # Verificar si está en directorio temporal
            is_in_temp = pdf_path.startswith(temp_dir)

            # Verificar si contiene palabras de vista previa
            preview_keywords = ['preview', 'constancia_preview', 'vista_previa', 'temp_constancia']
            has_preview_keywords = any(keyword in pdf_path.lower() for keyword in preview_keywords)

            # Verificar si tiene atributo de origen (si el panel lo soporta)
            is_user_loaded = getattr(pdf_panel, 'is_user_loaded', True)  # Por defecto True si no existe el atributo

            self.logger.debug(f"🔍 ANÁLISIS PDF EXTERNO:")
            self.logger.debug(f"   - Ruta: {pdf_path}")
            self.logger.debug(f"   - En directorio temporal: {is_in_temp}")
            self.logger.debug(f"   - Tiene palabras de vista previa: {has_preview_keywords}")
            self.logger.debug(f"   - Cargado por usuario: {is_user_loaded}")

            # Es externo si NO está en temp Y NO tiene palabras de preview Y fue cargado por usuario
            is_external = not is_in_temp and not has_preview_keywords and is_user_loaded

            self.logger.debug(f"   - RESULTADO: Es PDF externo = {is_external}")
            return is_external

        except Exception as e:
            self.logger.error(f"Error verificando PDF externo: {e}")
            # En caso de error, asumir que es externo para ser conservadores
            return True

    def _is_transformation_request(self, constancia_info: Dict, detected_entities: Dict) -> bool:
        """Determina si la solicitud es para transformar un PDF existente"""
        try:
            # 🎯 CRITERIOS PARA DETECTAR TRANSFORMACIÓN:
            # 1. Sub-intención es "transformar_pdf"
            # 2. Acción principal contiene "transformar"
            # 3. Fuente de datos es "pdf_cargado"
            # 4. Contexto específico es "conversion_formato"

            sub_intention = detected_entities.get('sub_intention', '')
            accion_principal = detected_entities.get('accion_principal', '')
            fuente_datos = detected_entities.get('fuente_datos', '')
            contexto_especifico = detected_entities.get('contexto_especifico', '')

            # También verificar en constancia_info por compatibilidad
            fuente_info = constancia_info.get('fuente_datos', '') if constancia_info else ''

            is_transform_sub = sub_intention == 'transformar_pdf'
            is_transform_action = 'transformar' in accion_principal.lower()
            is_pdf_source = fuente_datos == 'pdf_cargado' or fuente_info == 'pdf_cargado'
            is_conversion_context = 'conversion' in contexto_especifico.lower()

            self.logger.debug(f"🔍 ANÁLISIS TRANSFORMACIÓN:")
            self.logger.debug(f"   - Sub-intención transformar: {is_transform_sub}")
            self.logger.debug(f"   - Acción transformar: {is_transform_action}")
            self.logger.debug(f"   - Fuente PDF: {is_pdf_source}")
            self.logger.debug(f"   - Contexto conversión: {is_conversion_context}")

            # Es transformación si cumple al menos 2 criterios
            transformation_score = sum([is_transform_sub, is_transform_action, is_pdf_source, is_conversion_context])
            is_transformation = transformation_score >= 2

            self.logger.debug(f"   - RESULTADO: Es transformación = {is_transformation} (score: {transformation_score}/4)")
            return is_transformation

        except Exception as e:
            self.logger.error(f"Error verificando transformación: {e}")
            # En caso de error, asumir que NO es transformación
            return False

    def _generate_constancia_response_with_reflection(self, alumno: Dict, tipo_constancia: str, data: Dict) -> Optional[Dict]:
        """Genera respuesta con auto-reflexión específica para constancias"""
        try:
            response_prompt = f"""
Eres un comunicador experto para sistema escolar con CAPACIDAD DE AUTO-REFLEXIÓN especializada en CONSTANCIAS.

CONTEXTO DE CONSTANCIA GENERADA:
- Alumno: {alumno.get('nombre', 'N/A')}
- Tipo: {tipo_constancia}
- Estado: Vista previa generada exitosamente
- Archivo: {data.get('ruta_archivo', 'N/A')}

INSTRUCCIONES PRINCIPALES:
1. Genera respuesta profesional informando sobre la vista previa
2. 🆕 AUTO-REFLEXIONA específicamente sobre constancias

🧠 AUTO-REFLEXIÓN ESPECIALIZADA EN CONSTANCIAS:
Después de generar tu respuesta, reflexiona como un secretario escolar experto en documentos:

ANÁLISIS REFLEXIVO ESPECÍFICO:
- ¿Acabo de mostrar una vista previa de constancia que requiere confirmación del usuario?
- ¿El usuario necesitará decidir qué hacer con esta constancia (confirmar, abrir, cancelar)?
- ¿Debería recordar los datos de esta constancia para futuras acciones?
- ¿Qué tipo de respuesta esperaría típicamente después de mostrar una vista previa?

DECISIÓN CONVERSACIONAL PARA CONSTANCIAS:
Si tu respuesta espera continuación, especifica:
- Tipo esperado: "confirmation" (confirmar/abrir/cancelar)
- Datos a recordar: información de la constancia y alumno
- Razonamiento: por qué esperas confirmación

FORMATO DE RESPUESTA:
{{
  "respuesta_usuario": "Tu respuesta profesional sobre la vista previa aquí",
  "reflexion_conversacional": {{
    "espera_continuacion": true|false,
    "tipo_esperado": "confirmation|none",
    "datos_recordar": {{
      "query": "constancia generada",
      "alumno": {{"id": {alumno.get('id')}, "nombre": "{alumno.get('nombre')}"}},
      "tipo_constancia": "{tipo_constancia}",
      "archivo_temporal": "{data.get('ruta_archivo', '')}",
      "estado": "vista_previa_generada",
      "acciones_disponibles": ["confirmar", "abrir", "cancelar"]
    }},
    "razonamiento": "Explicación de por qué esperas confirmación o no"
  }}
}}
"""

            response = self.gemini_client.send_prompt_sync(response_prompt)
            return self._parse_json_response(response)

        except Exception as e:
            self.logger.error(f"Error generando respuesta de constancia: {e}")
            return None

    def _is_simple_confirmation(self, user_query: str) -> bool:
        """Detecta si es una confirmación simple (sí, ok, confirmar) vs solicitud específica"""
        try:
            user_lower = user_query.lower().strip()

            # Confirmaciones simples
            simple_confirmations = [
                "sí", "si", "ok", "vale", "confirmar", "confirmo", "adelante",
                "procede", "continúa", "continua", "hazlo", "genérala", "generala"
            ]

            # Si es solo una palabra de confirmación simple
            if user_lower in simple_confirmations:
                return True

            # Si contiene palabras específicas de constancia, NO es confirmación simple
            constancia_keywords = [
                "constancia", "certificado", "documento", "estudios",
                "calificaciones", "traslado", "generar", "crear"
            ]

            for keyword in constancia_keywords:
                if keyword in user_lower:
                    return False  # Es solicitud específica, no confirmación simple

            return False

        except Exception as e:
            self.logger.error(f"Error detectando confirmación simple: {e}")
            return False

    def _detect_confirmation_type(self, user_query: str, context_item: Dict) -> str:
        """Detecta el tipo específico de confirmación para constancias"""
        try:
            user_lower = user_query.lower().strip()

            # Confirmaciones para guardar/finalizar
            if any(word in user_lower for word in ["confirmar", "sí", "si", "está bien", "correcto", "guardar", "finalizar"]):
                return "confirm"

            # Confirmaciones para abrir en navegador
            elif any(word in user_lower for word in ["abrir", "navegador", "browser", "ver", "mostrar"]):
                return "open"

            # Confirmaciones para cancelar
            elif any(word in user_lower for word in ["cancelar", "no", "cerrar", "salir", "descartar"]):
                return "cancel"

            # Por defecto, asumir confirmación
            else:
                return "confirm"

        except Exception as e:
            self.logger.error(f"Error detectando tipo de confirmación: {e}")
            return "confirm"

    def _process_constancia_confirmation(self, user_query: str, confirmation_type: str, context_item: Dict) -> Optional[InterpretationResult]:
        """Procesa confirmación específica para constancias con vista previa"""
        try:
            alumno = context_item.get("alumno", {})
            tipo_constancia = context_item.get("tipo_constancia", "estudio")
            archivo_temporal = context_item.get("archivo_temporal", "")

            self.logger.debug(f"Procesando confirmación de constancia: {confirmation_type}")

            if confirmation_type == "confirm":
                # Confirmar y generar constancia definitiva
                return self._confirm_constancia_final(alumno, tipo_constancia, archivo_temporal)

            elif confirmation_type == "open":
                # Abrir en navegador
                return self._open_constancia_in_browser(alumno, tipo_constancia, archivo_temporal)

            elif confirmation_type == "cancel":
                # Cancelar y limpiar archivos temporales
                return self._cancel_constancia(archivo_temporal)

            else:
                # Confirmación genérica
                return self._confirm_constancia_final(alumno, tipo_constancia, archivo_temporal)

        except Exception as e:
            self.logger.error(f"Error procesando confirmación de constancia: {e}")
            return None

    def _confirm_constancia_final(self, alumno: Dict, tipo_constancia: str, archivo_temporal: str) -> InterpretationResult:
        """Confirma y genera constancia definitiva"""
        try:
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            constancia_service = service_provider.constancia_service

            # Generar constancia definitiva (no preview)
            success, message, data = constancia_service.generar_constancia_para_alumno(
                alumno.get("id"), tipo_constancia, False, preview_mode=False
            )

            if success:
                response_text = f"✅ Constancia de {tipo_constancia} para {alumno.get('nombre')} generada y guardada exitosamente."

                return InterpretationResult(
                    action="constancia_confirmada",
                    parameters={
                        "message": response_text,
                        "alumno": alumno,
                        "tipo_constancia": tipo_constancia,
                        "archivo_final": data.get("ruta_archivo") if data else None,
                        "estado": "confirmada"
                    },
                    confidence=0.95
                )
            else:
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": f"❌ Error generando constancia definitiva: {message}",
                        "error": "generation_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error confirmando constancia: {e}")
            return InterpretationResult(
                action="constancia_error",
                parameters={
                    "message": "❌ Error interno confirmando constancia",
                    "error": "internal_error"
                },
                confidence=0.1
            )

    def _open_constancia_in_browser(self, alumno: Dict, tipo_constancia: str, archivo_temporal: str) -> InterpretationResult:
        """Abre constancia en navegador"""
        try:
            import webbrowser
            import os

            if archivo_temporal and os.path.exists(archivo_temporal):
                webbrowser.open(f"file://{os.path.abspath(archivo_temporal)}")
                response_text = f"🌐 Constancia de {tipo_constancia} para {alumno.get('nombre')} abierta en el navegador."
            else:
                response_text = f"❌ No se pudo abrir la constancia. Archivo no encontrado."

            return InterpretationResult(
                action="constancia_abierta",
                parameters={
                    "message": response_text,
                    "alumno": alumno,
                    "tipo_constancia": tipo_constancia,
                    "archivo": archivo_temporal,
                    "estado": "abierta"
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error abriendo constancia: {e}")
            return InterpretationResult(
                action="constancia_error",
                parameters={
                    "message": "❌ Error abriendo constancia en navegador",
                    "error": "open_failed"
                },
                confidence=0.3
            )

    def _cancel_constancia(self, archivo_temporal: str) -> InterpretationResult:
        """Cancela constancia y limpia archivos temporales"""
        try:
            import os

            # Limpiar archivo temporal si existe
            if archivo_temporal and os.path.exists(archivo_temporal):
                try:
                    os.remove(archivo_temporal)
                    self.logger.debug(f"Archivo temporal eliminado: {archivo_temporal}")
                except Exception as e:
                    self.logger.warning(f"No se pudo eliminar archivo temporal: {e}")

            response_text = "❌ Generación de constancia cancelada. Vista previa eliminada."

            return InterpretationResult(
                action="constancia_cancelada",
                parameters={
                    "message": response_text,
                    "estado": "cancelada"
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error cancelando constancia: {e}")
            return InterpretationResult(
                action="constancia_error",
                parameters={
                    "message": "❌ Error cancelando constancia",
                    "error": "cancel_failed"
                },
                confidence=0.3
            )

    def _process_constancia_from_pdf(self, constancia_info: Dict[str, Any], pdf_panel, context: Dict[str, Any]) -> InterpretationResult:
        """Procesa constancia desde PDF cargado (transformación)"""
        try:
            self.logger.info(f"🔄 Procesando transformación de PDF: {pdf_panel.original_pdf}")

            # Obtener información de la transformación
            tipo_constancia = constancia_info.get("tipo_constancia", "estudio")
            incluir_foto = constancia_info.get("incluir_foto", False)

            # Usar el servicio de constancias para transformar
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            constancia_service = service_provider.constancia_service

            # Crear directorio temporal para preview
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="transformation_preview_")

            # Ejecutar transformación en modo preview
            success, message, data = constancia_service.generar_constancia_desde_pdf(
                pdf_path=pdf_panel.original_pdf,
                tipo_constancia=tipo_constancia,
                incluir_foto=incluir_foto,
                guardar_alumno=False,  # No guardar en BD en preview
                preview_mode=True,
                output_dir=temp_dir
            )

            if success and data:
                # 🛠️ OBTENER INFORMACIÓN DEL ALUMNO - MANEJO SEGURO
                alumno_info = data.get("alumno", {})

                # 🆕 VERIFICAR QUE ALUMNO_INFO SEA UN DICCIONARIO
                if not isinstance(alumno_info, dict):
                    self.logger.warning(f"⚠️ alumno_info no es diccionario: {type(alumno_info)}, convirtiendo...")
                    # Si es una lista, tomar el primer elemento si existe
                    if isinstance(alumno_info, list) and len(alumno_info) > 0:
                        alumno_info = alumno_info[0] if isinstance(alumno_info[0], dict) else {}
                    else:
                        # Si no es lista o está vacía, usar diccionario vacío
                        alumno_info = {}

                # Actualizar contexto del panel para transformación
                if hasattr(pdf_panel, 'set_transformation_completed_context'):
                    pdf_panel.set_transformation_completed_context(
                        original_data=pdf_panel.pdf_data,
                        transformed_data=data,
                        alumno_data=alumno_info
                    )

                # Generar respuesta con auto-reflexión
                response_with_reflection = self._generate_constancia_response_with_reflection(
                    alumno_info, tipo_constancia, data
                )

                if response_with_reflection:
                    return InterpretationResult(
                        action="transformation_preview",
                        parameters={
                            "message": response_with_reflection.get("respuesta_usuario", "Vista previa de transformación generada"),
                            "data": data,
                            "files": [data.get("ruta_archivo")] if data.get("ruta_archivo") else [],
                            "alumno": alumno_info,
                            "tipo_constancia": tipo_constancia,
                            "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                            "transformation_info": {
                                "original_pdf": pdf_panel.original_pdf,
                                "transformed_pdf": data.get("ruta_archivo"),
                                "tipo_transformacion": tipo_constancia
                            }
                        },
                        confidence=0.95
                    )
                else:
                    return InterpretationResult(
                        action="transformation_preview",
                        parameters={
                            "message": f"Vista previa de constancia de {tipo_constancia} generada desde PDF",
                            "data": data,
                            "files": [data.get("ruta_archivo")] if data.get("ruta_archivo") else [],
                            "alumno": alumno_info,
                            "tipo_constancia": tipo_constancia,
                            "transformation_info": {
                                "original_pdf": pdf_panel.original_pdf,
                                "transformed_pdf": data.get("ruta_archivo"),
                                "tipo_transformacion": tipo_constancia
                            }
                        },
                        confidence=0.9
                    )
            else:
                return InterpretationResult(
                    action="transformation_error",
                    parameters={
                        "message": f"Error transformando PDF: {message}",
                        "error": "transformation_failed",
                        "service_message": message
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error en transformación de PDF: {e}")
            return InterpretationResult(
                action="transformation_error",
                parameters={
                    "message": "Error interno procesando la transformación. Intenta nuevamente.",
                    "error": "internal_error",
                    "exception": str(e)
                },
                confidence=0.1
            )
