"""
🎯 COORDINADOR PRINCIPAL DEL STUDENT QUERY INTERPRETER

RESPONSABILIDAD: Coordinar el flujo principal y delegar a componentes especializados
TAMAÑO OBJETIVO: ~200 líneas (solo coordinación)

ARQUITECTURA REFACTORIZADA:
├── StudentQueryInterpreter (COORDINADOR - este archivo)
├── QueryAnalyzer (Análisis de consultas)
├── ContinuationHandler (Manejo de continuaciones)
├── ResponseBuilder (Construcción de respuestas)
├── DataValidator (Validación de datos)
└── ConstanciaProcessor (Ya existe)

FLUJO PRINCIPAL:
1. Recibir instrucciones del Master
2. Delegar análisis a QueryAnalyzer
3. Ejecutar acciones via ActionExecutor
4. Construir respuesta via ResponseBuilder
5. Retornar resultado al Master
"""
import json
import re
import os
from typing import Dict, Any, Optional, List, Tuple

from .base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from .database_analyzer import DatabaseAnalyzer
from .sql_executor import SQLExecutor
from .response_parser import ResponseParser
from ..prompts.student_query_prompt_manager import StudentQueryPromptManager
from app.core.logging import get_logger

# ✅ CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR COMPLETADA)
# 🗑️ ELIMINADO: ContinuationDetector - Student ahora obedece decisiones del Master
from .student_query.student_identifier import StudentIdentifier
from .student_query.constancia_processor import ConstanciaProcessor
from .student_query.data_normalizer import DataNormalizer
from .student_query.response_generator import ResponseGenerator
from .utils.json_parser import JSONParser

# 🆕 NUEVOS COMPONENTES REFACTORIZADOS (ARQUITECTURA LIMPIA)
from .student_query.query_analyzer import QueryAnalyzer
from .student_query.continuation_handler import ContinuationHandler
from .student_query.response_builder import ResponseBuilder

class StudentQueryInterpreter(BaseInterpreter):
    """Interpretador especializado en consultas de alumnos/estudiantes usando LLM"""

    def __init__(self, db_path: str, gemini_client=None):
        super().__init__("SQL_Interpreter", priority=10)  # Alta prioridad

        # 🆕 LOGGING CENTRALIZADO
        self.logger = get_logger(__name__)

        self.db_path = db_path
        # 🆕 ANALIZADOR DINÁMICO DE BASE DE DATOS
        from app.core.database.database_analyzer import DatabaseAnalyzer
        self.database_analyzer = DatabaseAnalyzer(db_path)
        self.sql_executor = SQLExecutor(db_path)
        self.response_parser = ResponseParser()
        self.gemini_client = gemini_client

        # 🆕 FIELD MAPPER PARA MAPEO DINÁMICO DE CAMPOS
        from app.core.database.field_mapper import FieldMapper
        self.field_mapper = FieldMapper()

        # PromptManager centralizado para contexto escolar unificado
        self.prompt_manager = StudentQueryPromptManager()
        self.logger.debug("StudentQueryPromptManager inicializado")

        # Cache del contexto SQL
        self._sql_context = None

        # ✅ INICIALIZAR CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR COMPLETADA)
        # 🗑️ ELIMINADO: ContinuationDetector - Student ahora obedece decisiones del Master
        self.student_identifier = StudentIdentifier()
        self.constancia_processor = ConstanciaProcessor(gemini_client)
        self.data_normalizer = DataNormalizer()
        self.response_generator = ResponseGenerator(gemini_client, self.prompt_manager)
        self.json_parser = JSONParser()

        # 🆕 INICIALIZAR NUEVOS COMPONENTES REFACTORIZADOS
        self.query_analyzer = QueryAnalyzer(self.database_analyzer, gemini_client)
        self.continuation_handler = ContinuationHandler(self.database_analyzer, self.sql_executor, gemini_client)
        self.response_builder = ResponseBuilder(self.prompt_manager, gemini_client)

        self.logger.debug("✅ Clases especializadas inicializadas (Arquitectura modular completada)")
        self.logger.debug("✅ Nuevos componentes refactorizados inicializados")

        # 🎯 INICIALIZACIÓN COMPLETADA
        self.logger.info("🎯 [STUDENT] CONTEXTO TÉCNICO CARGADO Y VERIFICADO")

        # 🔍 DETECTAR SI DEBUG PAUSES ESTÁ HABILITADO
        import sys
        self.debug_pauses_enabled = '--debug-pauses' in sys.argv or os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true'

    def _debug_pause_if_enabled(self, message: str):
        """🛑 PAUSA DE DEBUG CONTROLADA POR VARIABLE DE ENTORNO"""
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            input(f"🛑 {message}")

    def _generate_contextual_response(self, user_query: str, total_count: int, filtered_count: int,
                                    filter_type: str, conversation_stack: list) -> str:
        """
        🆕 GENERA RESPUESTA CONTEXTUAL PARA ANÁLISIS SIN FILTROS
        """
        try:
            user_lower = user_query.lower()

            # Detectar tipo de análisis solicitado
            if 'promedio' in user_lower:
                if filtered_count == 0:
                    return f"De los **{total_count} estudiantes** del contexto anterior, ninguno tiene calificaciones registradas para calcular promedio. 📊"
                else:
                    return f"Analizando el promedio de calificaciones de los **{filtered_count} estudiantes** del contexto anterior... 📊"

            elif 'estadística' in user_lower or 'distribución' in user_lower:
                return f"Generando estadísticas de los **{filtered_count} estudiantes** del contexto anterior... 📈"

            elif 'análisis' in user_lower:
                return f"Realizando análisis de los **{filtered_count} estudiantes** del contexto anterior... 🔍"

            else:
                return f"Procesando información de los **{filtered_count} estudiantes** del contexto anterior... ✅"

        except Exception as e:
            self.logger.error(f"Error generando respuesta contextual: {e}")
            return f"Procesando información de {filtered_count} estudiantes... ✅"

    def _generate_dynamic_filter_response(self, user_query: str, total_count: int, filtered_count: int,
                                        filter_criteria: dict, conversation_stack: list) -> str:
        """
        🆕 GENERA RESPUESTA PARA FILTROS DINÁMICOS APLICADOS
        """
        try:
            # Extraer criterios aplicados para la respuesta
            criterios = filter_criteria.get('criterios', [])
            criterios_texto = []

            for criterio in criterios:
                campo = criterio.get('campo', '')
                operador = criterio.get('operador', '')
                valor = criterio.get('valor', '')

                if campo == 'promedio_general' and operador == 'mayor_que':
                    criterios_texto.append(f"promedio mayor a {valor}")
                elif campo == 'grupo':
                    criterios_texto.append(f"grupo {valor}")
                elif campo == 'turno':
                    criterios_texto.append(f"turno {valor.lower()}")
                elif campo == 'grado':
                    criterios_texto.append(f"{valor}° grado")
                else:
                    criterios_texto.append(f"{campo} {operador} {valor}")

            if criterios_texto:
                criterios_str = ", ".join(criterios_texto)
                if filtered_count == 0:
                    return f"De los **{total_count} estudiantes** del contexto anterior, ninguno cumple con los criterios: {criterios_str}. 📊"
                elif filtered_count == 1:
                    return f"De los **{total_count} estudiantes** del contexto anterior, encontré **1 estudiante** que cumple con: {criterios_str}. ✅"
                else:
                    return f"De los **{total_count} estudiantes** del contexto anterior, encontré **{filtered_count} estudiantes** que cumplen con: {criterios_str}. ✅"
            else:
                return f"Filtré los **{total_count} estudiantes** del contexto anterior y obtuve **{filtered_count} resultados**. ✅"

        except Exception as e:
            self.logger.error(f"Error generando respuesta de filtro dinámico: {e}")
            return f"De {total_count} estudiantes, {filtered_count} cumplen los criterios. ✅"

    def _get_supported_actions(self):
        """Método requerido por BaseInterpreter - mantenido por compatibilidad"""
        return ["consulta_sql_exitosa", "consulta_sql_fallida"]

    def can_handle(self, context: InterpretationContext) -> bool:
        """Método abstracto requerido - siempre True porque se usa desde MasterInterpreter"""
        return True  # El MasterInterpreter ya decidió que somos el intérprete correcto

    def interpret(self, context: InterpretationContext, current_pdf=None) -> Optional[InterpretationResult]:
        """
        🎯 MÉTODO PRINCIPAL SIMPLIFICADO - SOLO DIRIGE AL FLUJO UNIFICADO

        TODAS las consultas (búsquedas, estadísticas, constancias, continuaciones)
        usan el MISMO flujo principal unificado de 4 prompts.
        """
        try:
            # 🎓 [STUDENT] Recibiendo instrucciones del Master
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [STUDENT] Información del Master recibida:")
            if hasattr(context, 'intention_info') and context.intention_info:
                debug_detailed(self.logger, f"🔧 [STUDENT] Categoría: {context.intention_info.get('categoria', 'N/A')}")
                debug_detailed(self.logger, f"🔧 [STUDENT] Sub-tipo: {context.intention_info.get('sub_tipo', 'N/A')}")
                debug_detailed(self.logger, f"🔧 [STUDENT] Complejidad: {context.intention_info.get('complejidad', 'N/A')}")

            # 🛑 PAUSA ESTRATÉGICA #2: STUDENT RECIBE INFORMACIÓN DEL MASTER
            import os
            if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                print(f"\n🛑 [STUDENT] RECIBE DEL MASTER:")
                print(f"    ├── 📝 Consulta: '{context.user_message}'")
                print(f"    ├── 🎯 Intención: {context.intention_info.get('intention_type', 'N/A') if hasattr(context, 'intention_info') and context.intention_info else 'NO HAY'}")
                print(f"    ├── 🔍 Sub-intención: {context.intention_info.get('sub_intention', 'N/A') if hasattr(context, 'intention_info') and context.intention_info else 'NO HAY'}")
                if hasattr(context, 'intention_info') and context.intention_info:
                    entities = context.intention_info.get('detected_entities', {})
                    print(f"    ├── 📊 Entidades detectadas: {len(entities)}")
                    for key, value in entities.items():
                        if isinstance(value, list) and len(value) > 2:
                            print(f"    │   ├── {key}: {value[:2]}... (+{len(value)-2} más)")
                        else:
                            print(f"    │   ├── {key}: {value}")
                if hasattr(context, 'conversation_stack') and context.conversation_stack:
                    print(f"    ├── 🔍 Contexto conversacional: {len(context.conversation_stack)} niveles")
                    ultimo_nivel = context.conversation_stack[-1]
                    print(f"    │   └── Último: '{ultimo_nivel.get('query', 'N/A')}' ({ultimo_nivel.get('row_count', 0)} elementos)")
                else:
                    print(f"    ├── 🔍 Contexto conversacional: VACÍO (consulta nueva)")
                print(f"    └── Presiona ENTER para que Student procese...")
                input()

            self.logger.info(f"🔄 [STUDENT] Iniciando procesamiento: '{context.user_message}'")

            # 🎯 GUARDAR CONTEXTO PARA USO EN MÉTODOS INTERNOS
            self._current_context = context

            # 🗑️ ELIMINADO: Verificación de respuesta a aclaración
            # RAZÓN: El Master maneja todas las aclaraciones, Student solo obedece

            # 🆕 INICIALIZAR ESTRUCTURAS SI NO EXISTEN
            if not hasattr(context, 'conversation_history') or context.conversation_history is None:
                context.conversation_history = []
            if not hasattr(context, 'conversation_stack') or context.conversation_stack is None:
                context.conversation_stack = []

            # 🎯 PROCESAMIENTO CON CONTEXTO CONVERSACIONAL PRESERVADO
            # 🎓 [STUDENT] Procesando consulta
            from app.core.logging import debug_detailed
            if context.conversation_stack:
                debug_detailed(self.logger, f"🔧 [STUDENT] PROCESANDO CON CONTEXTO - {len(context.conversation_stack)} niveles disponibles")
            else:
                debug_detailed(self.logger, "🔧 [STUDENT] PROCESANDO CONSULTA INDIVIDUAL")

            # PREPARAR CONTEXTO CONVERSACIONAL
            conversation_context = ""
            if context.conversation_stack:
                conversation_context = self._format_conversation_stack_for_llm(context.conversation_stack)
                debug_detailed(self.logger, f"🔧 [STUDENT] Contexto conversacional disponible: {len(context.conversation_stack)} niveles")

            # 🆕 USAR INFORMACIÓN CONSOLIDADA DEL MASTER
            # Ya no necesitamos detectar intención específica - viene del Master
            master_intention = context.intention_info
            if not master_intention:
                self.logger.error("   └── ❌ No se recibió información de intención del Master")
                return None

            self.logger.info(f"   ├── ✅ Información del Master recibida:")
            self.logger.info(f"   ├──    Categoría: {master_intention.get('categoria')}")
            self.logger.info(f"   ├──    Sub-tipo: {master_intention.get('sub_tipo')}")
            self.logger.info(f"   └──    Complejidad: {master_intention.get('complejidad')}")

            categoria = master_intention.get('categoria', 'busqueda')
            flujo_optimo = master_intention.get('flujo_optimo', 'sql_directo')
            self.logger.info(f"   └── ✅ Intención consolidada: {categoria} → {flujo_optimo}")

            # 🎓 [STUDENT] Iniciando procesamiento con información del Master
            self._debug_pause("🎓 [STUDENT] RECIBIENDO ORDEN DEL MASTER", {
                "categoria": categoria,
                "sub_tipo": master_intention.get('sub_tipo'),
                "complejidad": master_intention.get('complejidad'),
                "flujo_optimo": flujo_optimo,
                "entidades_detectadas": len(master_intention.get('detected_entities', {}))
            })

            return self._execute_main_3_prompt_flow(context, master_intention, conversation_context, current_pdf)

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

    # 🎯 FLUJO PRINCIPAL UNIFICADO DE 4 PROMPTS

    def _execute_main_3_prompt_flow(self, context, master_intention: Dict[str, Any], conversation_context: str, current_pdf=None) -> Optional[InterpretationResult]:
        """
        🎯 FLUJO PRINCIPAL OPTIMIZADO DE 3 PROMPTS (PROMPT 1 ELIMINADO)

        PROPÓSITO: Maneja TODAS las consultas usando información consolidada del Master
        ARQUITECTURA: PROMPT 2 → EJECUCIÓN → PROMPT 3
        EJEMPLOS: "buscar garcia", "promedio de calificaciones", "constancia para luis"

        FLUJO OPTIMIZADO:
        - INFORMACIÓN DEL MASTER: Categoría, sub-tipo, complejidad ya detectados
        - PROMPT 2: Selección de acciones (BUSCAR_UNIVERSAL, CALCULAR_ESTADISTICA, etc.)
        - EJECUCIÓN: ActionExecutor ejecuta la acción seleccionada
        - PROMPT 3: Validación + respuesta + auto-reflexión
        """
        try:
            # 🔧 CRÍTICO: Almacenar master_intention para que ActionExecutor pueda accederla
            self.master_intention = master_intention

            # 🎓 [STUDENT] Ejecutando flujo de 3 prompts con información del Master
            from app.core.logging import debug_detailed
            categoria = master_intention.get('categoria', 'busqueda')
            self.logger.info(f"🎓 [STUDENT] Ejecutando: {master_intention.get('flujo_optimo', 'procesamiento')}")
            debug_detailed(self.logger, f"🔧 [STUDENT] Categoría: {categoria} → {master_intention.get('flujo_optimo')}")

            # 🗑️ ELIMINADO: Verificación de transformación
            # RAZÓN: Los métodos _is_transformation_request, _is_external_pdf_loaded y _process_constancia_from_pdf
            # fueron eliminados porque violan el principio Master-Student

            # PROMPT 2: Selección de acciones (ahora es PROMPT 1 del Student)
            self.logger.info("   ├── PROMPT 1 (Student): Selección de acciones...")

            # 🛑 PAUSA ESTRATÉGICA #4: STUDENT MAPEO DE CAMPOS CON CONTEXTO DB
            import os
            if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                print(f"\n🛑 [STUDENT] MAPEO DE CAMPOS CON BASE DE DATOS:")
                print(f"    ├── 📝 Consulta: '{context.user_message}'")
                print(f"    ├── 🧠 Filtros del Master: {master_intention.get('detected_entities', {}).get('filtros', [])}")
                print(f"    ├── 🗃️ Estructura de DB disponible para mapeo:")

                # Mostrar estructura de DB
                if hasattr(self, 'database_analyzer'):
                    structure = self.database_analyzer.get_database_structure()
                    for table_name, table_info in structure.get('tables', {}).items():
                        if table_name in ['alumnos', 'datos_escolares']:
                            columns = list(table_info.get('columns', {}).keys())
                            print(f"    │   ├── {table_name}: {', '.join(columns[:6])}{'...' if len(columns) > 6 else ''}")
                else:
                    print(f"    │   ├── alumnos: id, curp, nombre, matricula, fecha_nacimiento")
                    print(f"    │   └── datos_escolares: grado, grupo, turno, ciclo_escolar")

                print(f"    ├── 🧠 Student analizará y mapeará campos inteligentemente")
                print(f"    └── Presiona ENTER para que Student procese con contexto DB...")
                input()

            # 🔧 PASAR CONVERSATION_STACK Y MASTER_INTENTION AL MÉTODO
            self.conversation_stack = context.conversation_stack  # ✅ ASIGNAR PARA QUE getattr() FUNCIONE
            # ✅ USAR INFORMACIÓN DEL MASTER CORRECTAMENTE
            self.master_intention = master_intention  # Ya tenemos master_intention como parámetro
            action_request = self._select_action_strategy(context.user_message, categoria, conversation_context)

            if not action_request:
                self.logger.error("   └── ❌ No se pudo determinar estrategia de acción")
                return None

            self.logger.info(f"   ├── ✅ Estrategia seleccionada: {action_request.get('estrategia')}")
            self.logger.info(f"   └── ✅ Acción principal: {action_request.get('accion_principal')}")

            # EJECUCIÓN: ActionExecutor
            self.logger.info("   ├── EJECUCIÓN: ActionExecutor...")
            execution_result = self._execute_selected_action(action_request, current_pdf)

            if not execution_result or not execution_result.get('success'):
                self.logger.error(f"   └── ❌ Error en ejecución: {execution_result.get('message') if execution_result else 'Sin resultado'}")
                return None

            self.logger.info(f"   ├── ✅ Ejecución exitosa: {execution_result.get('row_count')} resultados")

            # 🎯 STUDENT SOLO REPORTA RESULTADOS - NO TOMA DECISIONES DE COMUNICACIÓN
            # El Master decidirá si necesita comunicación bidireccional basado en los resultados

            # 🔧 VERIFICAR SI ES CONTINUACIÓN PROCESADA - NO LLAMAR _validate_and_generate_response()
            if action_request.get('accion_principal') == 'CONTINUACION_PROCESADA':
                self.logger.info("   ├── 🎯 CONTINUACIÓN PROCESADA - Usando resultado directo sin validación adicional")

                # Preparar resultado final
                final_result = InterpretationResult(
                    action=execution_result.get('action_used', 'seleccion_realizada'),
                    parameters={
                        # 🎯 PRESERVAR TODOS LOS PARÁMETROS DE LA CONVERSIÓN
                        **execution_result,  # Incluir TODOS los parámetros del execution_result
                        "master_intention": master_intention,
                        "execution_summary": f"Continuación procesada: {action_request.get('accion_principal')} → {execution_result.get('row_count', 0)} resultados",
                        "requires_master_response": True,
                        "student_action": action_request.get('accion_principal'),
                        "query_category": categoria
                    },
                    confidence=0.9
                )



                return final_result

            # PROMPT 3: Validación + respuesta + auto-reflexión (ahora es PROMPT 2 del Student)
            self.logger.info("   ├── PROMPT 2 (Student): Validación + respuesta...")
            final_response = self._validate_and_generate_response(
                context.user_message,
                execution_result.get('sql_executed', ''),
                execution_result.get('data', []),
                execution_result.get('row_count', 0),
                context.conversation_stack
            )

            if not final_response:
                self.logger.error("   └── ❌ No se pudo generar respuesta final")
                return None

            self.logger.info("   └── ✅ Respuesta final generada exitosamente")

            # Crear resultado final - SOLO DATOS TÉCNICOS PARA EL MASTER
            action_used = execution_result.get('action_used', 'consulta_procesada')

            # 🎯 CASO ESPECIAL: PRESERVAR PARÁMETROS DE TRANSFORMACIÓN
            if action_used == 'transformation_preview':
                # Preservar todos los parámetros específicos de transformación
                parameters = {
                    # 🎯 DATOS TÉCNICOS PARA EL MASTER (NO RESPUESTA FINAL)
                    "technical_response": final_response.get("respuesta_usuario", "Consulta procesada"),
                    "reflexion_conversacional": final_response.get("reflexion_conversacional", {}),
                    "data": execution_result.get('data', []),
                    "row_count": execution_result.get('row_count', 0),
                    "sql_executed": execution_result.get('sql_executed', ''),
                    "master_intention": master_intention,  # 🆕 Incluir información del Master
                    "execution_summary": f"Flujo de 3 prompts completado: {categoria} → {action_request.get('accion_principal')} → {execution_result.get('row_count')} resultados",
                    # 🚨 FLAG PARA MASTER: Indica que debe generar respuesta final
                    "requires_master_response": True,
                    "student_action": action_request.get('accion_principal'),
                    "query_category": categoria,
                    # 🎯 PRESERVAR PARÁMETROS ESPECÍFICOS DE TRANSFORMACIÓN
                    "files": execution_result.get('files', []),
                    "alumno": execution_result.get('alumno', {}),
                    "transformation_info": execution_result.get('transformation_info', {}),
                    "human_response": final_response.get("respuesta_usuario", "Vista previa de transformación generada")
                }
            else:
                # Parámetros normales para otras acciones
                parameters = {
                    # 🎯 DATOS TÉCNICOS PARA EL MASTER (NO RESPUESTA FINAL)
                    "technical_response": final_response.get("respuesta_usuario", "Consulta procesada"),
                    "reflexion_conversacional": final_response.get("reflexion_conversacional", {}),
                    "data": execution_result.get('data', []),
                    "row_count": execution_result.get('row_count', 0),
                    "sql_executed": execution_result.get('sql_executed', ''),
                    "master_intention": master_intention,  # 🆕 Incluir información del Master
                    "execution_summary": f"Flujo de 3 prompts completado: {categoria} → {action_request.get('accion_principal')} → {execution_result.get('row_count')} resultados",
                    # 🚨 FLAG PARA MASTER: Indica que debe generar respuesta final
                    "requires_master_response": True,
                    "student_action": action_request.get('accion_principal'),
                    "query_category": categoria
                }

            # 🔧 DEBUG: Mostrar reporte que se envía al Master
            self._debug_pause("📤 [STUDENT] ENVIANDO REPORTE AL MASTER", {
                "action_ejecutada": action_request.get('accion_principal'),
                "resultados_obtenidos": execution_result.get('row_count', 0),
                "sql_ejecutado": execution_result.get('sql_executed', '')[:100] + "..." if execution_result.get('sql_executed') else "N/A",
                "requiere_respuesta_master": True,
                "datos_tecnicos_incluidos": ["data", "row_count", "sql_executed", "master_intention"]
            })

            return InterpretationResult(
                action=action_used,
                parameters=parameters,
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"❌ Error en flujo de 3 prompts: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None



    # 🎯 MÉTODOS DEL SISTEMA DE ACCIONES

    def _select_action_strategy(self, user_query: str, categoria: str, conversation_context: str = "") -> Optional[Dict[str, Any]]:
        """
        🆕 NUEVO PROMPT 2: Selecciona estrategia de acciones
        REEMPLAZA: _generate_sql_with_strategy_centralized()
        🎯 NUEVA FUNCIONALIDAD: Detecta consultas de seguimiento y usa BUSCAR_UNIVERSAL con composición
        """
        try:
            # 🎯 PASO 1: OBEDECER DECISIÓN DEL MASTER SOBRE CONTEXTO
            # Obtener información del Master desde los atributos asignados previamente
            master_intention = getattr(self, 'master_intention', {})

            # 🔧 VERIFICACIÓN DE TIPO: Asegurar que master_intention es un diccionario
            if not isinstance(master_intention, dict):
                self.logger.warning(f"⚠️ master_intention no es dict: {type(master_intention)} - Usando diccionario vacío")
                master_intention = {}

            requiere_contexto = master_intention.get('requiere_contexto', False)

            conversation_stack = getattr(self, 'conversation_stack', [])

            # 🎯 STUDENT OBEDECE AL MASTER - NO TOMA DECISIONES PROPIAS
            # Normalizar el valor (puede venir como string o boolean)
            requiere_contexto_normalizado = bool(requiere_contexto)

            # 🎯 VERIFICAR SI MASTER YA RESOLVIÓ LA REFERENCIA
            detected_entities = master_intention.get('detected_entities', {})
            alumno_resuelto = detected_entities.get('alumno_resuelto')

            if alumno_resuelto:
                self.logger.info(f"✅ MASTER YA RESOLVIÓ ALUMNO: {alumno_resuelto['nombre']} (ID: {alumno_resuelto['id']})")
                # 🔧 CREAR ACTION_REQUEST PARA EL ALUMNO RESUELTO (NO EJECUTAR AQUÍ)
                sub_intention = master_intention.get('sub_intention')
                self.logger.info(f"🔍 Sub-intención para alumno resuelto: {sub_intention}")

                action_request = self._create_action_request_for_resolved_student(sub_intention, alumno_resuelto, detected_entities)
                if action_request:
                    self.logger.info(f"🎯 Action request creado para flujo normal: {action_request.get('accion_principal')} con parámetros: {action_request.get('parametros')}")
                    # 🎯 DEVOLVER ACTION_REQUEST PARA QUE EL FLUJO NORMAL LO EJECUTE
                    return action_request
                else:
                    self.logger.warning(f"❌ No se pudo crear action_request para sub_intention: {sub_intention}")
                    return None

            elif requiere_contexto_normalizado and conversation_stack:
                self.logger.info(f"✅ MASTER DECIDIÓ: Usar contexto - {len(conversation_stack)} niveles disponibles")
                return self._process_continuation_with_master_guidance(user_query, conversation_stack)

            else:
                self.logger.info("✅ MASTER DECIDIÓ: NO usar contexto - Procesando como consulta individual")

            # 🎯 CONSULTA NORMAL - USAR PROMPT TRADICIONAL
            # 🆕 INCLUIR INFORMACIÓN DEL MASTER EN EL PROMPT
            master_intention = getattr(self, 'master_intention', {})
            master_filters = master_intention.get('detected_entities', {}).get('filtros', [])

            # Construir información adicional del Master para el prompt
            master_info = ""
            if master_filters:
                master_info = f"""
🧠 INFORMACIÓN ADICIONAL DEL MASTER:
El Master detectó los siguientes filtros específicos en la consulta:
{master_filters}

🎯 IMPORTANTE: Usa estos filtros como criterios separados:
"""
                for filtro in master_filters:
                    if ':' in filtro:
                        campo, valor = filtro.split(':', 1)
                        campo = campo.strip()
                        valor = valor.strip()
                        # Mapeo dinámico de campos usando FieldMapper
                        mapped_field = self.field_mapper.map_user_field_to_db(campo.lower())
                        if mapped_field:
                            tabla = mapped_field.get('tabla', 'datos_escolares')
                            campo_db = mapped_field.get('campo', campo.lower())
                            master_info += f"- Criterio {campo}: {{'tabla': '{tabla}', 'campo': '{campo_db}', 'operador': '=', 'valor': '{valor.upper()}'}}\n"
                        else:
                            # Fallback para campos no mapeados
                            master_info += f"- Criterio {campo}: {{'tabla': 'datos_escolares', 'campo': '{campo.lower()}', 'operador': '=', 'valor': '{valor.upper()}'}}\n"

                master_info += "\n🔧 USAR ESTOS COMO CRITERIOS SEPARADOS, NO COMBINADOS.\n"

            # Usar nuevo prompt de selección de acciones con información del Master
            action_prompt = self.prompt_manager.get_action_selection_prompt(
                user_query, categoria, conversation_context + master_info,
                master_intention  # 🔧 PASAR INFORMACIÓN DEL MASTER
            )

            # 🎓 [STUDENT] Preparando prompt de selección de acciones
            self.logger.info("🧠 [STUDENT-RAZONAMIENTO] Iniciando análisis basado en descripciones")
            self.logger.info(f"   ├── Sub-intención recibida: {master_intention.get('sub_intention', 'N/A')}")
            self.logger.info(f"   ├── Consulta a analizar: '{user_query}'")
            self.logger.info(f"   └── Usando razonamiento humano (no ejemplos literales)")

            # 🎓 [STUDENT] Enviando prompt al LLM
            response = self.gemini_client.send_prompt_sync(action_prompt)

            if response:
                # 🔍 DEBUG: Mostrar respuesta del LLM para diagnosticar problema
                self.logger.info(f"🔍 [DEBUG] Respuesta del LLM: {response[:500]}...")
                action_request = self._parse_action_response(response)

                # 🔍 DEBUG: Verificar tipo de action_request
                self.logger.info(f"🔍 [DEBUG] Tipo de action_request: {type(action_request)}")
                if action_request:
                    self.logger.info(f"🔍 [DEBUG] action_request contenido: {action_request}")

                # 🧠 [STUDENT-RAZONAMIENTO] Analizar decisión del LLM
                if action_request and isinstance(action_request, dict):
                    campos_solicitados = action_request.get('parametros', {}).get('campos_solicitados', [])
                    if campos_solicitados:
                        self.logger.info(f"🧠 [STUDENT-RAZONAMIENTO] LLM decidió usar campos específicos: {campos_solicitados}")
                        self.logger.info("   ├── ⚠️ VERIFICAR: ¿Es esto correcto para 'información completa'?")
                        if any(campo.lower() in ['informacion_completa', 'datos_completos', 'toda_la_informacion'] for campo in campos_solicitados):
                            self.logger.warning("   └── ❌ ERROR: LLM interpretó mal - estos NO son campos reales de BD")
                    else:
                        self.logger.info("🧠 [STUDENT-RAZONAMIENTO] LLM NO especificó campos_solicitados")
                        self.logger.info("   └── ✅ CORRECTO: Para información completa, usar todos los campos")

                if action_request and isinstance(action_request, dict):
                    accion_principal = action_request.get('accion_principal', 'unknown')
                    estrategia = action_request.get('estrategia', 'simple')
                    razonamiento = action_request.get('razonamiento', 'N/A')
                    parametros = action_request.get('parametros', {})

                    # 🎓 [STUDENT] Estrategia seleccionada
                    self.logger.info(f"🎓 [STUDENT] Mapeando: \"{user_query}\" → {accion_principal} ({estrategia})")

                    # 🛑 PAUSA ESTRATÉGICA: MOSTRAR MAPEO INTELIGENTE
                    import os
                    if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                        criterio_principal = parametros.get('criterio_principal', {})
                        if criterio_principal:
                            print(f"\n🛑 [STUDENT] MAPEO INTELIGENTE REALIZADO:")
                            print(f"    ├── 📝 Filtros del Master: {master_info.split('filtros: ')[1].split('\\n')[0] if 'filtros: ' in master_info else 'N/A'}")
                            print(f"    ├── 🧠 Razonamiento: {razonamiento}")
                            print(f"    ├── 🎯 Mapeo resultante:")
                            print(f"    │   ├── Tabla: {criterio_principal.get('tabla', 'N/A')}")
                            print(f"    │   ├── Campo: {criterio_principal.get('campo', 'N/A')}")
                            print(f"    │   ├── Operador: {criterio_principal.get('operador', 'N/A')}")
                            print(f"    │   └── Valor: {criterio_principal.get('valor', 'N/A')}")
                            print(f"    └── Presiona ENTER para ejecutar acción...")
                            input()

                    return action_request
                elif action_request:
                    self.logger.error(f"❌ action_request no es un diccionario: {type(action_request)} - Contenido: {action_request}")
                    return None
                else:
                    self.logger.warning("❌ No se pudo parsear respuesta de selección de acción")
                    return None
            else:
                self.logger.warning("❌ No se recibió respuesta del LLM para selección de acción")
                return None

        except Exception as e:
            self.logger.error(f"Error seleccionando estrategia de acción: {e}")
            return None

    # 🗑️ MÉTODO ELIMINADO: _is_follow_up_query
    # RAZÓN: Hardcoding innecesario - Master ya decide si usar contexto con LLM

    # 🗑️ MÉTODO ELIMINADO: _analyze_context_relevance_with_llm
    # Ya no se usa - reemplazado por ContinuationDetector con LLM inteligente

    def _execute_selected_action(self, action_request: Dict[str, Any], current_pdf=None) -> Optional[Dict[str, Any]]:
        """
        🎯 Ejecuta la acción seleccionada por el LLM usando ActionExecutor
        """
        try:
            # 🔍 DEBUG: Solo mostrar con --debug-pauses
            if hasattr(self, 'debug_pauses_enabled') and self.debug_pauses_enabled:
                self.logger.info(f"🔍 [DEBUG] _execute_selected_action llamado:")
                self.logger.info(f"    ├── accion_principal: {action_request.get('accion_principal')}")
                self.logger.info(f"    └── resultado_directo existe: {bool(action_request.get('resultado_directo'))}")

            # 🎯 CASO ESPECIAL: CONTINUACIÓN YA PROCESADA
            if action_request.get('accion_principal') == 'CONTINUACION_PROCESADA':
                self.logger.info("🎯 CONTINUACIÓN YA PROCESADA - Extrayendo resultado directo")

                continuation_result = action_request.get('resultado_directo')

                if continuation_result and hasattr(continuation_result, 'parameters'):
                    # Convertir InterpretationResult a formato de execution result
                    result = {
                        "success": True,
                        "data": continuation_result.parameters.get('data', []),
                        "row_count": continuation_result.parameters.get('row_count', 0),
                        "action_used": continuation_result.action,
                        "message": continuation_result.parameters.get('message', 'Continuación procesada'),
                        "sql_executed": continuation_result.parameters.get('sql_executed', ''),
                        "human_response": continuation_result.parameters.get('human_response', '')
                    }

                    # 🔧 AGREGAR TODOS LOS PARÁMETROS ADICIONALES DEL RESULTADO ORIGINAL
                    for key, value in continuation_result.parameters.items():
                        if key not in result:  # No sobrescribir los ya establecidos
                            result[key] = value

                    return result
                else:
                    self.logger.error("❌ Resultado de continuación inválido")
                    return {
                        "success": False,
                        "data": [],
                        "row_count": 0,
                        "action_used": "CONTINUACION_ERROR",
                        "message": "Error procesando continuación"
                    }

            # 🎯 CASO NORMAL: EJECUTAR CON ACTIONEXECUTOR
            # Importar y crear ActionExecutor
            from app.core.ai.actions import ActionExecutor
            action_executor = ActionExecutor(self.sql_executor, self)

            # 🔧 AGREGAR LÍMITE DEL MASTER AL ACTION_REQUEST
            limite_master = self._get_master_limit()
            if limite_master and action_request.get("accion_principal") == "BUSCAR_UNIVERSAL":
                if "parametros" not in action_request:
                    action_request["parametros"] = {}
                action_request["parametros"]["limit"] = limite_master
                self.logger.info(f"✅ Límite del Master aplicado a BUSCAR_UNIVERSAL: {limite_master}")

            # Ejecutar la acción
            if current_pdf:
                action_request["current_pdf"] = current_pdf
                # Para TRANSFORMAR_PDF, agregar current_pdf a los parámetros de la acción
                if action_request.get("accion_principal") == "TRANSFORMAR_PDF":
                    if "parametros" not in action_request:
                        action_request["parametros"] = {}
                    action_request["parametros"]["current_pdf"] = current_pdf
                    self.logger.info(f"✅ current_pdf agregado a parámetros de TRANSFORMAR_PDF: {current_pdf[:50] if current_pdf else 'None'}...")
            result = action_executor.execute_action_request(action_request)

            # 📊 [RESULT] Acción ejecutada
            row_count = result.get('row_count', 0)
            action_used = result.get('action_used', 'N/A')
            self.logger.info(f"📊 [RESULT] {row_count} resultados encontrados")

            return result

        except Exception as e:
            self.logger.error(f"Error ejecutando acción seleccionada: {e}")
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "action_used": "ERROR",
                "message": f"Error interno: {str(e)}"
            }

    def _parse_action_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parsea la respuesta JSON del LLM para selección de acciones"""
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
                        action_request = json.loads(matches[0])
                        return action_request
                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON, intentar parsear directamente
            try:
                action_request = json.loads(clean_response)
                return action_request
            except json.JSONDecodeError:
                return None

        except Exception as e:
            self.logger.error(f"Error parseando respuesta de acción: {e}")
            return None

    # ✅ PLANTILLAS SQL ELIMINADAS - INTEGRADAS EN PROMPTS DEL PROMPTMANAGER

    def _process_continuation_with_master_guidance(self, user_query: str, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        🎯 PROCESA CONTINUACIÓN SIGUIENDO INSTRUCCIONES DEL MASTER
        Master ya resolvió el contexto, Student solo ejecuta
        """
        try:
            self.logger.info("🎯 PROCESANDO CONTINUACIÓN CON GUÍA DEL MASTER")

            # Obtener información del Master
            master_intention = getattr(self, 'master_intention', {})
            detected_entities = master_intention.get('detected_entities', {})
            sub_intention = master_intention.get('sub_intention', '')

            # 🎯 CASO 1: MASTER RESOLVIÓ ALUMNO ESPECÍFICO
            alumno_resuelto = detected_entities.get('alumno_resuelto')
            if alumno_resuelto:
                self.logger.info(f"✅ MASTER RESOLVIÓ ALUMNO: {alumno_resuelto}")
                # 🔧 DEVOLVER ACTION_REQUEST, NO RESULTADO EJECUTADO
                action_request = self._create_action_request_for_resolved_student(sub_intention, alumno_resuelto, detected_entities)
                self.logger.info(f"🎯 [DEBUG] Action request creado en _process_continuation_with_master_guidance: {action_request}")
                return action_request

            # 🗑️ ELIMINADO: Lógica hardcodeada de referencias posicionales
            # RAZÓN: VIOLA PRINCIPIO MASTER-STUDENT - Student no debe tomar decisiones hardcodeadas
            # El Master ya maneja todas las referencias con LLM semántico

            # 🎯 CASO 3: USAR BUSCAR_UNIVERSAL CON CONTEXTO PARA CONTINUACIÓN
            self.logger.info("🔄 USANDO BUSCAR_UNIVERSAL CON CONTEXTO PARA CONTINUACIÓN")

            # Crear action_request directamente para evitar bucle infinito
            # Usar BUSCAR_UNIVERSAL con los IDs del contexto
            if conversation_stack:
                ultimo_nivel = conversation_stack[-1]
                context_data = ultimo_nivel.get('data', [])

                if context_data:
                    # Extraer IDs del contexto
                    ids = []
                    for item in context_data:
                        if isinstance(item, dict) and item.get('id'):
                            ids.append(str(item['id']))

                    if ids:
                        # 🔧 USAR FILTROS DINÁMICOS DEL MASTER
                        filtros_master = self._get_master_filters()
                        filtros_adicionales = self._convert_master_filters_to_sql(filtros_master)

                        # 🔧 OBTENER LÍMITE DEL MASTER
                        limite_master = self._get_master_limit()

                        action_request = {
                            'accion_principal': 'BUSCAR_UNIVERSAL',
                            'estrategia': 'simple',
                            'parametros': {
                                'criterio_principal': {
                                    'tabla': 'alumnos',
                                    'campo': 'id',
                                    'operador': 'IN',
                                    'valor': f"({','.join(ids)})"
                                }
                            },
                            'razonamiento': f"Continuación con contexto: filtrar {len(ids)} alumnos del contexto usando filtros del Master: {filtros_master}"
                        }

                        # 🔧 AGREGAR FILTROS ADICIONALES SI EXISTEN
                        if filtros_adicionales:
                            action_request['parametros']['filtros_adicionales'] = filtros_adicionales
                            self.logger.info(f"✅ Filtros del Master aplicados: {filtros_adicionales}")

                        # 🔧 AGREGAR LÍMITE SI EXISTE
                        if limite_master:
                            action_request['parametros']['limit'] = limite_master
                            self.logger.info(f"✅ Límite del Master aplicado: {limite_master}")

                        return action_request

            self.logger.warning("No se pudo generar action_request para continuación con contexto")
            return None

        except Exception as e:
            self.logger.error(f"Error procesando continuación con Master: {e}")
            return None

    def _create_action_request_for_resolved_student(self, sub_intention: str, alumno_resuelto: Dict, detected_entities: Dict) -> Optional[Dict[str, Any]]:
        """Crea action_request para alumno ya resuelto por Master (NO ejecuta)"""
        try:
            if sub_intention == 'generar_constancia':
                # Normalizar tipo de constancia
                tipo_constancia_raw = detected_entities.get('tipo_constancia', 'estudios')
                tipo_constancia = 'estudio' if tipo_constancia_raw == 'estudios' else tipo_constancia_raw

                # 🎯 USAR NOMBRE COMPLETO COMO IDENTIFICADOR (Student mapea a BD)
                # ✅ PRIORIZAR NOMBRE - es más confiable que ID en contexto
                alumno_identificador = alumno_resuelto.get('nombre')

                if not alumno_identificador:
                    # Fallback solo si no hay nombre
                    alumno_id = alumno_resuelto.get('id')
                    if alumno_id:
                        alumno_identificador = str(alumno_id)
                    else:
                        self.logger.error(f"❌ alumno_resuelto no tiene nombre ni ID: {alumno_resuelto}")
                        return None

                action_request = {
                    'accion_principal': 'GENERAR_CONSTANCIA_COMPLETA',
                    'estrategia': 'simple',
                    'parametros': {
                        'alumno_identificador': alumno_identificador,
                        'tipo_constancia': tipo_constancia,
                        'incluir_foto': detected_entities.get('incluir_foto', 'false') == 'true',
                        'preview_mode': True
                    },
                    'razonamiento': f"Master resolvió alumno: {alumno_resuelto.get('nombre')} → usando nombre completo como identificador"
                }

                return action_request

            elif sub_intention == 'transformacion_pdf':
                # 🔧 NUEVO: Manejar transformación de PDF
                self.logger.info("🔄 TRANSFORMACIÓN PDF - Procesando con PDF cargado")

                # Normalizar tipo de constancia
                tipo_constancia_raw = detected_entities.get('tipo_constancia', 'estudios')
                tipo_constancia = 'estudio' if tipo_constancia_raw == 'estudios' else tipo_constancia_raw

                action_request = {
                    'accion_principal': 'TRANSFORMAR_PDF',  # ✅ CORRECTO
                    'estrategia': 'simple',
                    'parametros': {
                        'tipo_constancia': tipo_constancia,
                        'incluir_foto': detected_entities.get('incluir_foto', 'false') == 'true',
                        'guardar_alumno': detected_entities.get('guardar_alumno', 'false') == 'true'
                    },
                    'razonamiento': f"Transformando PDF cargado a constancia de {tipo_constancia}"
                }

                return action_request

            elif sub_intention == 'busqueda_simple':
                # 🎯 NUEVO: Manejar búsqueda simple para alumno específico resuelto
                self.logger.info("🔍 BÚSQUEDA SIMPLE - Información completa del alumno resuelto")
                action_request = {
                    'accion_principal': 'BUSCAR_UNIVERSAL',
                    'estrategia': 'simple',
                    'parametros': {
                        'criterio_principal': {
                            'tabla': 'alumnos',
                            'campo': 'id',
                            'operador': '=',
                            'valor': str(alumno_resuelto.get('id'))
                        }
                    },
                    'razonamiento': f"Master resolvió alumno específico: {alumno_resuelto.get('nombre')} (ID: {alumno_resuelto.get('id')}) - Obteniendo información completa"
                }
                return action_request

            else:
                self.logger.warning(f"Sub-intención no implementada para alumno resuelto: {sub_intention}")
                return None

        except Exception as e:
            self.logger.error(f"Error creando action_request para alumno resuelto: {e}")
            return None

    # 🗑️ MÉTODO ELIMINADO: _execute_action_for_resolved_student
    # RAZÓN: MÉTODO LEGACY que causaba doble ejecución
    # El flujo normal ya maneja todo correctamente con action_requests

   


    def _get_master_filters(self) -> list:
        """
        🧠 OBTENER FILTROS DEL MASTER
        Accede a la información que el Master ya detectó con LLM
        """
        try:
            master_intention = getattr(self, 'master_intention', {})
            if master_intention:
                detected_entities = master_intention.get('detected_entities', {})
                filtros = detected_entities.get('filtros', [])
                if filtros:
                    self.logger.info(f"🧠 Filtros del Master encontrados: {filtros}")
                    return filtros

            self.logger.info("🔍 No se encontraron filtros del Master")
            return []

        except Exception as e:
            self.logger.error(f"Error obteniendo filtros del Master: {e}")
            return []

    def _get_master_limit(self) -> int:
        """
        🧠 OBTENER LÍMITE DE RESULTADOS DEL MASTER
        Accede al límite que el Master detectó (ej: "dame 3 alumnos")
        """
        try:
            master_intention = getattr(self, 'master_intention', {})
            if master_intention:
                detected_entities = master_intention.get('detected_entities', {})
                limite = detected_entities.get('limite_resultados')
                if limite and str(limite).isdigit():
                    limite_num = int(limite)
                    self.logger.info(f"🧠 Límite del Master encontrado: {limite_num}")
                    return limite_num

            self.logger.info("🔍 No se encontró límite del Master")
            return None

        except Exception as e:
            self.logger.error(f"Error obteniendo límite del Master: {e}")
            return None

    def _convert_master_filters_to_sql(self, filtros_master: list) -> list:
        """
        🔧 CONVIERTE FILTROS DEL MASTER A FORMATO SQL
        Mapea filtros como ['grupo: A'] a [{'tabla': 'datos_escolares', 'campo': 'grupo', 'operador': '=', 'valor': 'A'}]
        """
        try:
            filtros_sql = []

            for filtro in filtros_master:
                if ':' in filtro:
                    campo, valor = filtro.split(':', 1)
                    campo = campo.strip().lower()
                    valor = valor.strip()

                    # 🔧 MAPEO DINÁMICO DE CAMPOS USANDO FIELD_MAPPER
                    mapped_field = self.field_mapper.map_user_field_to_db(campo)
                    if mapped_field:
                        tabla = mapped_field.get('tabla', 'datos_escolares')
                        campo_db = mapped_field.get('campo', campo)
                        filtros_sql.append({
                            'tabla': tabla,
                            'campo': campo_db,
                            'operador': '=',
                            'valor': valor.upper() if campo in ['turno', 'grupo'] else valor
                        })
                        self.logger.info(f"✅ Campo mapeado dinámicamente: {campo} → {tabla}.{campo_db}")
                    else:
                        # Fallback para campos no mapeados
                        filtros_sql.append({
                            'tabla': 'datos_escolares',
                            'campo': campo,
                            'operador': '=',
                            'valor': valor.upper()
                        })
                        self.logger.warning(f"⚠️ Campo no mapeado, usando fallback: {campo}")

            if filtros_sql:
                self.logger.info(f"✅ Filtros convertidos a SQL: {filtros_sql}")

            return filtros_sql

        except Exception as e:
            self.logger.error(f"Error convirtiendo filtros del Master a SQL: {e}")
            return []


    def _format_conversation_stack_for_llm(self, conversation_stack: list) -> str:
        """Formatea la pila conversacional para el LLM CON IDs PARA SQL"""
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
            # 🆕 MOSTRAR IDs ESPECÍFICOS PARA SQL
            if level.get('data') and len(level.get('data', [])) > 0:
                data_items = level['data']

                # 🔧 VERIFICAR TIPO DE DATOS ANTES DE HACER SLICE
                if isinstance(data_items, list):
                    context += f"- Total elementos: {len(data_items)}\n"
                    context += f"- Primeros 3 elementos: {data_items[:3]}\n"
                elif isinstance(data_items, dict):
                    context += f"- Datos estructurados: {len(data_items)} campos\n"
                    context += f"- Campos disponibles: {list(data_items.keys())[:3]}\n"
                else:
                    context += f"- Datos: {type(data_items).__name__}\n"
                    context += f"- Contenido: {str(data_items)[:100]}...\n"

                # 🎯 EXTRAER IDs PARA FILTROS SQL
                ids = []
                if isinstance(data_items, list):
                    for item in data_items:
                        if isinstance(item, dict) and item.get('id'):
                            ids.append(str(item['id']))
                elif isinstance(data_items, dict) and data_items.get('id'):
                    # Si data_items es un diccionario con ID directo
                    ids.append(str(data_items['id']))

                if ids:
                    # 🔧 MOSTRAR TODOS LOS IDs, NO SOLO LOS PRIMEROS 5
                    context += f"- IDs disponibles para filtros SQL: [{', '.join(ids)}]\n"
                    context += f"- Ejemplo SQL con contexto: WHERE a.id IN ({', '.join(ids)})\n"
                    # 🎓 [STUDENT] Contexto: IDs disponibles para nivel
                    self.logger.info(f"🎓 [STUDENT] Contexto: {len(ids)} IDs disponibles para nivel {i}")

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

            # 🔧 ELIMINADO: Detección hardcodeada de constancias
            # RAZÓN: VIOLA PRINCIPIO - Student no debe interpretar intenciones
            # El Master ya detectó la intención y tipo de constancia

            # 🎯 USAR INFORMACIÓN DEL MASTER DIRECTAMENTE
            detected_entities = self.master_intention.get('detected_entities', {})
            tipo_constancia = detected_entities.get('tipo_constancia', 'estudio')

            self.logger.info(f"🎯 USANDO TIPO DE CONSTANCIA DEL MASTER: {tipo_constancia}")
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

        except Exception as e:
            self.logger.error(f"Error en selección: {e}")
            return None



    def _identify_student_using_master_entities(self, context, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        🎯 IDENTIFICA ALUMNO USANDO ENTIDADES DEL MASTER

        Usa la información que ya detectó el Master en lugar de hacer extracción propia.
        Esta es la forma correcta de colaboración Master-Student.
        """
        try:
            # 🎯 OBTENER ENTIDADES DEL MASTER
            intention_info = getattr(context, 'intention_info', {})
            detected_entities = intention_info.get('detected_entities', {})
            nombres_master = detected_entities.get('nombres', [])

            if not nombres_master:
                self.logger.info("❌ Master no detectó nombres específicos")
                return None

            nombre_buscado = nombres_master[0]  # Primer nombre detectado por Master
            self.logger.info(f"🎯 Master detectó nombre: '{nombre_buscado}'")

            # 🔍 BUSCAR EN EL CONTEXTO CONVERSACIONAL
            if not conversation_stack:
                self.logger.warning("❌ No hay contexto conversacional disponible")
                return None

            # Buscar en el último nivel del contexto
            ultimo_nivel = conversation_stack[-1]
            context_data = ultimo_nivel.get('data', [])

            if not context_data:
                self.logger.warning("❌ No hay datos en el contexto")
                return None

            # 🎯 BUSCAR COINCIDENCIA POR NOMBRE EN EL CONTEXTO
            nombre_buscado_lower = nombre_buscado.lower()

            for alumno in context_data:
                alumno_normalizado = self._normalize_student_data_structure(alumno)
                if not alumno_normalizado:
                    continue

                nombre_alumno = alumno_normalizado.get('nombre', '').lower()

                # Buscar coincidencia parcial (nombre o apellido)
                if nombre_buscado_lower in nombre_alumno:
                    self.logger.info(f"✅ COINCIDENCIA ENCONTRADA: '{nombre_buscado}' → {alumno_normalizado.get('nombre')}")
                    return alumno_normalizado

            self.logger.warning(f"❌ No se encontró '{nombre_buscado}' en el contexto de {len(context_data)} alumnos")
            return None

        except Exception as e:
            self.logger.error(f"Error identificando alumno con entidades del Master: {e}")
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
            # 🧹 SIN FALLBACKS - Si no hay respuesta, que falle claramente
            return response.strip()

        except Exception as e:
            self.logger.error(f"Error en respuesta unificada: {e}")
            # 🧹 SIN FALLBACKS - Que falle claramente para debugging
            raise

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





    def _generate_initial_query_response(self, user_query: str, row_count: int,
                                       data: List[Dict], espera_continuacion: bool,
                                       conversation_stack: list = None) -> str:
        """
        🎯 GENERA RESPUESTA CONVERSACIONAL CON CONTEXTO CONVERSACIONAL

        Args:
            user_query: Consulta del usuario
            row_count: Cantidad de resultados
            data: Datos encontrados
            espera_continuacion: Si se espera continuación
            conversation_stack: Pila conversacional para contexto

        Returns:
            Respuesta conversacional natural con referencia al contexto
        """
        try:
            user_lower = user_query.lower()
            conversation_stack = conversation_stack or []

            is_follow_up = False  # Master ya decidió la estrategia

            # 🔍 DEBUG: Logging simplificado
            self.logger.info(f"🔍 DEBUG - _generate_initial_query_response:")
            self.logger.info(f"   - Query: '{user_query}'")
            self.logger.info(f"   - conversation_stack length: {len(conversation_stack)}")
            self.logger.info(f"   - Master ya decidió estrategia, Student obedece")

            if is_follow_up and conversation_stack:
                # 🎯 RESPUESTA PARA CONSULTA DE SEGUIMIENTO CON CONTEXTO
                self.logger.info(f"🎯 USANDO _generate_follow_up_response")
                return self._generate_follow_up_response(user_query, row_count, data, conversation_stack)

            # 🎯 DETECTAR TIPO DE CONSULTA Y GENERAR RESPUESTA APROPIADA

            if row_count == 0:
                # Sin resultados
                if "grado" in user_lower:
                    return "No encontré alumnos en ese grado. ¿Quizás te refieres a otro grado? 🤔"
                else:
                    return "No encontré alumnos que coincidan con tu búsqueda. ¿Podrías ser más específico? 🔍"

            elif row_count == 1:
                # 🔍 VERIFICAR SI ES RESULTADO DE CONTEO O ALUMNO INDIVIDUAL
                resultado = data[0] if data else {}

                # ✅ DETECTAR RESULTADO DE CONTEO
                if isinstance(resultado, dict) and 'total' in resultado:
                    cantidad = resultado['total']

                    # 🔧 RESPUESTA COMPLETAMENTE DINÁMICA
                    response = f"📊 Total de alumnos encontrados: **{cantidad}**"

                    # Agregar sugerencia útil dinámica
                    if cantidad > 0:
                        response += f"\n\n💡 Si necesitas ver la lista de estos alumnos, puedes preguntarme: 'muéstrame esos alumnos'"

                    return response

                # ✅ ALUMNO INDIVIDUAL (comportamiento original)
                else:
                    alumno = resultado
                    nombre = alumno.get('nombre', 'el alumno')
                    grado = alumno.get('grado', 'N/A')

                    tiene_calificaciones = (alumno.get('calificaciones') and
                                          alumno.get('calificaciones') not in ['', '[]', None])

                    if tiene_calificaciones:
                        response = f"Encontré a **{nombre}** de {grado}° grado con calificaciones registradas. 📊"
                        response += "\n\n¿Te gustaría generar una constancia o necesitas más información? 📄"
                    else:
                        response = f"Encontré a **{nombre}** de {grado}° grado, pero aún no tiene calificaciones registradas. 📝"
                        response += "\n\n¿Te gustaría generar una constancia de estudios? 📄"

                    return response

            else:
                # Múltiples alumnos - VERIFICAR SI ES SEGUIMIENTO PRIMERO
                if is_follow_up and conversation_stack:
                    # 🎯 ES CONSULTA DE SEGUIMIENTO - Usar respuesta contextual
                    return self._generate_follow_up_response(user_query, row_count, data, conversation_stack)
                else:
                    # 🎯 ES CONSULTA INICIAL - Detectar contexto específico
                    response = self._generate_specific_context_response(user_query, row_count, data)

                    # Agregar sugerencias basadas en la cantidad SOLO para consultas iniciales
                    if espera_continuacion:
                        if row_count <= 10:
                            response += "\n\n¿Necesitas información específica de alguno de ellos o quieres generar constancias? 🤔"
                        elif row_count <= 30:
                            response += "\n\n¿Quieres que filtre esta lista por algún criterio específico? Por ejemplo, por calificaciones, turno, o grupo. 🔍"
                        else:
                            response += "\n\n¿Te ayudo a filtrar esta lista? Puedo buscar por calificaciones, turno, grupo, o cualquier otro criterio. 🔍"
                    else:
                        response += "\n\n¿Necesitas algo más? 💭"

                    return response

        except Exception as e:
            self.logger.error(f"Error generando respuesta inicial: {e}")
            # Fallback a respuesta básica
            return f"✅ Encontré {row_count} alumnos que cumplen con tu consulta."

    def _get_sql_context(self) -> str:
        """Obtiene el contexto SQL (con cache)"""
        if self._sql_context is None:
            self._sql_context = self.database_analyzer.generate_sql_context()
        return self._sql_context



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

    def _validate_and_generate_response(self, user_query: str, sql_query: str, data: List[Dict], row_count: int, conversation_stack: list = None) -> Optional[Dict]:
        """
        PROMPT 3 SIMPLIFICADO: BUSCAR_UNIVERSAL ya hizo el trabajo, solo generar respuesta
        CON CONTEXTO CONVERSACIONAL para respuestas de seguimiento
        """
        try:
            # 🎯 BUSCAR_UNIVERSAL YA FILTRÓ CORRECTAMENTE - NO APLICAR FILTROS ADICIONALES
            filtered_data = data

            # 🎓 [STUDENT] Búsqueda completada exitosamente

            # BUSCAR_UNIVERSAL siempre resuelve la consulta correctamente
            # No aplicar filtros adicionales que puedan interferir

            # Usar los datos filtrados para el resto del proceso
            final_data = filtered_data
            final_row_count = len(filtered_data)

            # 🎯 AUTO-REFLEXIÓN INTELIGENTE SIN LLM EXTRA (rápida y efectiva)

            # Determinar si espera continuación basado en el tipo de consulta y resultados
            espera_continuacion, tipo_esperado, nota_estrategica = self._determine_continuation_expectation(
                user_query, final_row_count, final_data
            )

            # 🎯 GENERAR RESPUESTA CONVERSACIONAL CON CONTEXTO CORRECTO
            # USAR conversation_stack pasado como parámetro (viene del MessageProcessor)
            # self.conversation_stack NO EXISTE en StudentQueryInterpreter
            context_stack = conversation_stack if conversation_stack is not None else []

            # 🎓 [STUDENT] Validando y generando respuesta

            # 🎯 STUDENT RETORNA DATOS TÉCNICOS PARA EL MASTER
            technical_summary = f"Consulta procesada: {final_row_count} resultados obtenidos"

            self.logger.info(f"🎯 Datos técnicos preparados para Master: {final_row_count} resultados")

            return {
                "technical_response": technical_summary,  # 🎯 RESUMEN TÉCNICO PARA EL MASTER
                "reflexion_conversacional": {
                    "espera_continuacion": espera_continuacion,
                    "tipo_esperado": tipo_esperado,
                    "nota_para_master": nota_estrategica,  # 🎯 NOTA ESTRATÉGICA DETALLADA
                    "datos_recordar": {
                        "query": user_query,
                        "data": final_data,  # 🔧 USAR TODOS LOS DATOS para contexto conversacional
                        "row_count": final_row_count,
                        "context": f"Lista de {final_row_count} alumnos disponible",
                        "filter_applied": "N/A"
                    },
                    "razonamiento": nota_estrategica  # Mantener compatibilidad
                },
                "data": final_data,  # 🎯 DATOS COMPLETOS PARA EL MASTER
                "row_count": final_row_count,
                "sql_executed": sql_query,  # 🎯 SQL PARA QUE MASTER SEPA QUÉ CRITERIOS SE USARON
                "user_query": user_query,  # 🎯 CONSULTA ORIGINAL
                "query_type": "search" if final_row_count > 0 else "no_results",
                "ambiguity_level": "high" if final_row_count > 10 else "low" if final_row_count <= 3 else "medium"
            }

        except Exception as e:
            self.logger.error(f"Error en validación con auto-reflexión: {e}")
            return None

    def _determine_continuation_expectation(self, user_query: str, row_count: int, data: List[Dict]) -> tuple:
        """
        🧠 GENERA NOTA ESTRATÉGICA DETALLADA PARA MASTER

        Analiza la consulta y resultados para generar información estratégica
        que ayude a Master a detectar continuaciones inteligentemente.

        Returns:
            tuple: (espera_continuacion: bool, tipo_esperado: str, nota_estrategica: str)
        """
        try:
            # 🎯 GENERAR NOTA ESTRATÉGICA DETALLADA PARA MASTER

            # Analizar datos para generar información estratégica
            grados_disponibles = set()
            grupos_disponibles = set()
            turnos_disponibles = set()

            for alumno in data[:10]:  # Analizar primeros 10 para eficiencia
                if 'grado' in alumno and alumno['grado']:
                    grados_disponibles.add(str(alumno['grado']))
                if 'grupo' in alumno and alumno['grupo']:
                    grupos_disponibles.add(str(alumno['grupo']))
                if 'turno' in alumno and alumno['turno']:
                    turnos_disponibles.add(str(alumno['turno']))

            # Construir nota estratégica detallada
            if row_count >= 2:
                if row_count <= 10:
                    nota_estrategica = f"""Mostré lista de {row_count} alumnos. Usuario podría querer:
- POSICIÓN: 'del primero', 'el último', 'del cuarto'
- CONSTANCIA: 'constancia para [nombre/posición]'
- FILTRO: 'los de [grado/grupo/turno]'
- CONTEO: 'cuántos son de [criterio]'
Grados disponibles: {sorted(grados_disponibles)}
Grupos disponibles: {sorted(grupos_disponibles)}
Turnos disponibles: {sorted(turnos_disponibles)}"""
                    return (True, "selection", nota_estrategica)

                elif row_count <= 50:
                    nota_estrategica = f"""Mostré {row_count} alumnos (lista mediana). Usuario podría querer:
- FILTRAR: 'de esos los de [grado/grupo/turno específico]'
- ESTADÍSTICAS: 'cuántos son por grado', 'estadísticas de ese grupo'
- CONSTANCIA: 'constancia para [criterio específico]'
- ANÁLISIS: 'distribución por [criterio]'
Datos disponibles: grados {sorted(grados_disponibles)}, grupos {sorted(grupos_disponibles)}, turnos {sorted(turnos_disponibles)}"""
                    return (True, "filter", nota_estrategica)

                else:
                    nota_estrategica = f"""Mostré {row_count} alumnos (lista grande). Usuario muy probablemente querrá:
- FILTRAR: 'de esos los de [criterio]' para reducir cantidad
- ESTADÍSTICAS: 'cuántos son por [dimensión]'
- ANÁLISIS: 'distribución', 'estadísticas del grupo'
Dimensiones disponibles: {len(grados_disponibles)} grados, {len(grupos_disponibles)} grupos, {len(turnos_disponibles)} turnos"""
                    return (True, "filter", nota_estrategica)

            elif row_count == 1:
                alumno = data[0] if data else {}
                nombre = alumno.get('nombre', 'alumno')
                nota_estrategica = f"""Encontré 1 alumno específico ({nombre}). Usuario podría querer:
- CONSTANCIA: 'constancia para él/ella', 'generar constancia'
- INFORMACIÓN: 'datos completos', 'información adicional'
- ACCIÓN: 'CURP de ese alumno', 'grado de ese estudiante'
Datos disponibles: información completa del alumno"""
                return (True, "action", nota_estrategica)

            elif row_count == 0:
                nota_estrategica = f"""No encontré resultados para '{user_query}'. Usuario probablemente:
- REFORMULARÁ: con otros criterios de búsqueda
- PREGUNTARÁ: por ayuda o sugerencias
- CAMBIARÁ: estrategia de búsqueda"""
                return (False, "none", nota_estrategica)



            # 🎯 RESPUESTA DINÁMICA BASADA EN RESULTADOS
            nota_estrategica = f"""Consulta resuelta ({row_count} resultados). Usuario podría:
- Hacer nueva consulta independiente
- Continuar con estos resultados si son útiles
- Solicitar más información específica
Datos disponibles: {row_count} elementos procesados"""
            # Permitir continuación por defecto (Master decidirá si es apropiado)

            # Caso por defecto
            nota_estrategica = f"""Consulta general con {row_count} resultados. Contexto disponible para:
- REFERENCIAS: 'de esos', 'del grupo anterior', 'de la lista'
- FILTROS: aplicar criterios adicionales
- ACCIONES: sobre elementos específicos
Mantengo contexto activo para posibles continuaciones."""
            return (True, "analysis", nota_estrategica)

        except Exception as e:
            self.logger.error(f"Error determinando expectativa de continuación: {e}")
            # Fallback conservador: siempre esperar continuación
            return (True, "analysis",
                   f"Error en análisis, pero mantengo contexto disponible para {row_count} resultados.")

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


    def _process_constancia_as_direct_action(self, context) -> Optional[InterpretationResult]:
        """
        🎯 CONSTANCIA COMO ACCIÓN DIRECTA - SIN CÓDIGO REDUNDANTE
        Usa directamente las entidades del Master y delega al ConstanciaProcessor
        """
        try:
            # 🎯 OBTENER ENTIDADES DEL MASTER (YA DETECTADAS)
            intention_info = getattr(context, 'intention_info', {})
            detected_entities = intention_info.get('detected_entities', {})

            if not detected_entities:
                self.logger.error("❌ No hay entidades detectadas del Master")
                return InterpretationResult(
                    action="constancia_error",
                    parameters={"message": "❌ Error: No se detectaron entidades para la constancia"},
                    confidence=0.1
                )

            # 🎯 EXTRAER INFORMACIÓN NECESARIA
            nombre_alumno = detected_entities.get('nombres', [None])[0] if detected_entities.get('nombres') else None
            tipo_constancia = detected_entities.get('tipo_constancia', 'estudio')

            if not nombre_alumno:
                return InterpretationResult(
                    action="constancia_error",
                    parameters={"message": "❌ No se especificó el nombre del alumno"},
                    confidence=0.1
                )

            # 🎯 BUSCAR ALUMNO EN BASE DE DATOS
            alumno = self._find_student_by_name(nombre_alumno)
            if not alumno:
                return InterpretationResult(
                    action="constancia_error",
                    parameters={
                        "message": f"No encontré al alumno '{nombre_alumno}'. Verifica el nombre e intenta nuevamente.",
                        "error": "student_not_found"
                    },
                    confidence=0.3
                )

            # 🎯 NORMALIZAR TIPO DE CONSTANCIA
            tipo_normalizado = self._normalize_constancia_type(tipo_constancia)

            # 🚀 DELEGAR DIRECTAMENTE AL CONSTANCIA PROCESSOR
            self.logger.info(f"🚀 DELEGANDO A CONSTANCIA PROCESSOR: {alumno.get('nombre')} - {tipo_normalizado}")
            return self.constancia_processor.process_constancia_request(
                alumno, tipo_normalizado, context.user_message
            )

        except Exception as e:
            self.logger.error(f"Error en constancia como acción directa: {e}")
            return InterpretationResult(
                action="constancia_error",
                parameters={"message": "Error interno procesando la constancia"},
                confidence=0.1
            )


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

    
    def _create_standardized_report(self, action_executed: str, result: Dict[str, Any],
                                   user_query: str, error_info: Dict = None) -> Dict[str, Any]:
        """
        🔧 CREA REPORTE ESTANDARIZADO PARA EL MASTER

        Formato consistente que el Master puede interpretar fácilmente
        """
        try:
            # Determinar tipo de datos
            data = result.get('data', [])
            data_type = self._determine_data_type(action_executed, data)

            # Crear reporte estandarizado
            report = {
                "status": "error" if error_info else "success",
                "action_executed": action_executed,
                "technical_result": {
                    "data": data,
                    "row_count": result.get('row_count', len(data) if isinstance(data, list) else 1),
                    "sql_executed": result.get('sql_executed', ''),
                    "execution_time": result.get('execution_time', 'N/A')
                },
                "error_info": error_info,
                "metadata": {
                    "data_type": data_type,
                    "requires_user_action": self._requires_user_action(action_executed),
                    "original_query": user_query,
                    "context_ready": True
                }
            }

            self.logger.info(f"📊 [STUDENT REPORT] {action_executed}: {report['status']} - {report['technical_result']['row_count']} resultados")
            return report

        except Exception as e:
            self.logger.error(f"Error creando reporte estandarizado: {e}")
            return {
                "status": "error",
                "action_executed": action_executed,
                "error_info": {"type": "report_creation_error", "message": str(e)},
                "metadata": {"data_type": "error", "requires_user_action": False}
            }

    def _determine_data_type(self, action: str, data: Any = None) -> str:
        """Determina el tipo de datos para el Master"""
        if action in ["BUSCAR_UNIVERSAL", "BUSCAR_Y_FILTRAR"]:
            return "student_list"
        elif action in ["CALCULAR_ESTADISTICA", "CONTAR_UNIVERSAL"]:
            return "statistics"
        elif action in ["GENERAR_CONSTANCIA_COMPLETA"]:
            return "constancia_preview"
        elif action in ["TRANSFORMAR_PDF"]:
            return "transformation_preview"
        else:
            return "generic_data"

    def _requires_user_action(self, action: str) -> bool:
        """Determina si la acción requiere interacción del usuario"""
        return action in ["BUSCAR_UNIVERSAL", "CALCULAR_ESTADISTICA", "CONTAR_UNIVERSAL", "BUSCAR_Y_FILTRAR"]

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

