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
import os
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
        # 🆕 ANALIZADOR DINÁMICO DE BASE DE DATOS
        from app.core.database.database_analyzer import DatabaseAnalyzer
        self.database_analyzer = DatabaseAnalyzer(db_path)
        self.sql_executor = SQLExecutor(db_path)
        self.response_parser = ResponseParser()
        self.gemini_client = gemini_client

        # PromptManager centralizado para contexto escolar unificado
        self.prompt_manager = StudentQueryPromptManager()
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

        # 🎯 LOGS DETALLADOS DE INICIALIZACIÓN
        self._log_detailed_technical_context()

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

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        🎯 MÉTODO PRINCIPAL SIMPLIFICADO - SOLO DIRIGE AL FLUJO UNIFICADO

        TODAS las consultas (búsquedas, estadísticas, constancias, continuaciones)
        usan el MISMO flujo principal unificado de 4 prompts.
        """
        try:
            # 🎯 DEBUG ESTRATÉGICO: LO QUE STUDENT RECIBE DEL MASTER
            self.logger.info("=" * 60)
            self.logger.info("🎯 [DEBUG] STUDENT RECIBE DEL MASTER:")
            self.logger.info("=" * 60)
            self.logger.info(f"📥 CONSULTA: '{context.user_message}'")

            # Verificar si tiene intention_info del Master
            if hasattr(context, 'intention_info') and context.intention_info:
                self.logger.info("📥 INFORMACIÓN DEL MASTER:")
                self.logger.info(f"     ├── Intención: {context.intention_info.get('intention_type', 'N/A')}")
                self.logger.info(f"     ├── Sub-intención: {context.intention_info.get('sub_intention', 'N/A')}")
                self.logger.info(f"     ├── Confianza: {context.intention_info.get('confidence', 'N/A')}")
                self.logger.info(f"     └── Entidades: {len(context.intention_info.get('detected_entities', {}))}")

                # Mostrar entidades detectadas por Master
                entities = context.intention_info.get('detected_entities', {})
                for key, value in entities.items():
                    self.logger.info(f"         ├── {key}: {value}")
            else:
                self.logger.info("❌ NO HAY INTENTION_INFO del Master")

            self.logger.info("=" * 60)
            self.logger.info("🧠 [STUDENT] INICIANDO RAZONAMIENTO...")
            self.logger.info("=" * 60)

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

            # 🔄 VERIFICAR SI ES RESPUESTA A ACLARACIÓN
            if self._is_clarification_response(context):
                return self._handle_clarification_response(context)

            # 🆕 INICIALIZAR ESTRUCTURAS SI NO EXISTEN
            if not hasattr(context, 'conversation_history') or context.conversation_history is None:
                context.conversation_history = []
            if not hasattr(context, 'conversation_stack') or context.conversation_stack is None:
                context.conversation_stack = []

            # 🎯 PROCESAMIENTO CON CONTEXTO CONVERSACIONAL PRESERVADO
            if context.conversation_stack:
                self.logger.info(f"🎯 PROCESANDO CON CONTEXTO - {len(context.conversation_stack)} niveles disponibles")
            else:
                self.logger.info("🎯 PROCESANDO CONSULTA INDIVIDUAL")

            # PREPARAR CONTEXTO CONVERSACIONAL
            conversation_context = ""
            if context.conversation_stack:
                conversation_context = self._format_conversation_stack_for_llm(context.conversation_stack)
                self.logger.info(f"   ├── Contexto conversacional disponible: {len(context.conversation_stack)} niveles")

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

            # 🎯 FLUJO PRINCIPAL UNIFICADO - MANEJA TODO
            self.logger.info("=" * 80)
            self.logger.info("🎯 [VERIFICACIÓN] USANDO FLUJO CONSOLIDADO DE 3 PROMPTS")
            self.logger.info("🎯 [VERIFICACIÓN] PROMPT 1 ELIMINADO - INFORMACIÓN VIENE DEL MASTER")
            self.logger.info("🎯 [VERIFICACIÓN] ARQUITECTURA: Master → Student Prompt 1 → Ejecución → Student Prompt 2")
            self.logger.info("🎯 [VERIFICACIÓN] SIN FALLBACKS - IMPLEMENTACIÓN ÚNICA")
            self.logger.info("=" * 80)
            return self._execute_main_3_prompt_flow(context, master_intention, conversation_context)

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

    def _execute_main_3_prompt_flow(self, context, master_intention: Dict[str, Any], conversation_context: str) -> Optional[InterpretationResult]:
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
            self.logger.info("🔍 [FLUJO OPTIMIZADO] Iniciando con información consolidada del Master...")
            self.logger.info("🔍 [VERIFICACIÓN] MÉTODO: _execute_main_3_prompt_flow")
            self.logger.info("🔍 [VERIFICACIÓN] STUDENT PROMPT 1 ELIMINADO - USANDO MASTER INFO")

            # 🚀 FLUJO DE 3 PROMPTS OPTIMIZADO: Selección → Ejecución → Respuesta
            self.logger.info("   ├── FLUJO DE 3 PROMPTS: Selección → Ejecución → Respuesta...")

            # Usar categoría del Master (ya no necesitamos detectarla)
            categoria = master_intention.get('categoria', 'busqueda')
            self.logger.info(f"   ├── [VERIFICACIÓN] Categoría del Master: {categoria}")
            self.logger.info(f"   ├── [VERIFICACIÓN] Sub-tipo del Master: {master_intention.get('sub_tipo')}")
            self.logger.info(f"   ├── [VERIFICACIÓN] Flujo óptimo del Master: {master_intention.get('flujo_optimo')}")

            # 🎯 VERIFICAR SI ES TRANSFORMACIÓN ANTES DE SELECCIONAR ACCIONES
            detected_entities = master_intention.get('detected_entities', {})
            if self._is_transformation_request({}, detected_entities):
                self.logger.info("🔄 DETECTADA TRANSFORMACIÓN - Usando flujo especializado")

                # Verificar que hay PDF cargado
                pdf_panel = getattr(context, 'pdf_panel', None)
                if pdf_panel and hasattr(pdf_panel, 'original_pdf') and pdf_panel.original_pdf:
                    if self._is_external_pdf_loaded(pdf_panel):
                        self.logger.info(f"✅ PDF externo detectado: {pdf_panel.original_pdf}")

                        # Usar flujo de transformación directamente
                        constancia_info = {
                            "tipo_constancia": detected_entities.get('tipo_constancia', 'estudio'),
                            "incluir_foto": detected_entities.get('incluir_foto', False)
                        }

                        return self._process_constancia_from_pdf(constancia_info, pdf_panel, master_intention)
                    else:
                        self.logger.warning("❌ No hay PDF externo cargado para transformar")
                        return InterpretationResult(
                            action="transformation_error",
                            parameters={
                                "message": "No hay ningún PDF cargado para transformar. Por favor, carga un PDF primero.",
                                "error": "no_pdf_loaded"
                            },
                            confidence=0.8
                        )
                else:
                    self.logger.warning("❌ No se puede acceder al panel PDF")
                    return InterpretationResult(
                        action="transformation_error",
                        parameters={
                            "message": "Error accediendo al panel PDF. Intenta nuevamente.",
                            "error": "pdf_panel_error"
                        },
                        confidence=0.8
                    )

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
            self.master_intention = master_intention  # ✅ ASIGNAR PARA QUE getattr() FUNCIONE
            action_request = self._select_action_strategy(context.user_message, categoria, conversation_context)

            if not action_request:
                self.logger.error("   └── ❌ No se pudo determinar estrategia de acción")
                return None

            self.logger.info(f"   ├── ✅ Estrategia seleccionada: {action_request.get('estrategia')}")
            self.logger.info(f"   └── ✅ Acción principal: {action_request.get('accion_principal')}")

            # EJECUCIÓN: ActionExecutor
            self.logger.info("   ├── EJECUCIÓN: ActionExecutor...")
            execution_result = self._execute_selected_action(action_request)

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
            return InterpretationResult(
                action=execution_result.get('action_used', 'consulta_procesada'),
                parameters={
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
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"❌ Error en flujo de 3 prompts: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    # 🗑️ MÉTODO ELIMINADO: _execute_main_4_prompt_flow
    # RAZÓN: Reemplazado por _execute_main_3_prompt_flow que usa información consolidada del Master

    def _execute_main_4_prompt_flow_ELIMINADO(self, context, specific_intention: Dict[str, Any], conversation_context: str) -> Optional[InterpretationResult]:
        """
        🎯 FLUJO PRINCIPAL UNIFICADO DE 4 PROMPTS

        PROPÓSITO: Maneja TODAS las consultas (búsquedas, estadísticas, constancias, etc.)
        ARQUITECTURA: PROMPT 2 → PROMPT 3 → EJECUCIÓN → PROMPT 4
        EJEMPLOS: "buscar garcia", "promedio de calificaciones", "constancia para luis"

        FLUJO UNIFICADO:
        - PROMPT 2: Selección de acciones (BUSCAR_UNIVERSAL, CALCULAR_ESTADISTICA, etc.)
        - EJECUCIÓN: ActionExecutor ejecuta la acción seleccionada
        - PROMPT 4: Validación + respuesta + auto-reflexión
        """
        try:
            self.logger.info("🔍 [FLUJO BÚSQUEDA OPTIMIZADO] Iniciando con prompt integrado...")

            # 🚀 FLUJO DE 4 PROMPTS OPTIMIZADO: Análisis → Selección → Ejecución → Respuesta
            self.logger.info("   ├── FLUJO DE 4 PROMPTS: Análisis → Selección → Ejecución → Respuesta...")

            # Detectar categoría para optimizar selección de acciones
            categoria = specific_intention.get('categoria', 'busqueda')

            # PROMPT 2: Selección de acciones
            self.logger.info("   ├── PROMPT 2: Selección de acciones...")



            action_request = self._select_action_strategy(context.user_message, categoria, conversation_context)

            if not action_request:
                self.logger.info("   └── ❌ No se pudo seleccionar acción")
                return None
            self.logger.info(f"   └── ✅ Acción seleccionada: {action_request.get('accion_principal')}")



            # PROMPT 3: Ejecutar acción seleccionada
            self.logger.info("   ├── EJECUTANDO ACCIÓN...")
            action_result = self._execute_selected_action(action_request)

            if not action_result or not action_result.get("success"):
                self.logger.info(f"   └── ❌ Ejecución de acción falló: {action_result.get('message', 'Error desconocido')}")
                return None
            self.logger.info(f"   └── ✅ Acción ejecutada: {action_result.get('row_count')} resultados")

            # PROMPT 4: Validar + Generar respuesta + Auto-reflexión
            self.logger.info("   ├── PROMPT 4: Validación + respuesta + auto-reflexión...")

            # Usar método especializado para estadísticas si es necesario
            action_used = action_result.get("action_used", "")
            if (categoria == "estadistica" or action_used == "CALCULAR_ESTADISTICA") and action_result.get("estadistica_tipo"):
                response_with_reflection = self._validate_and_generate_statistics_response(
                    context.user_message,
                    action_result.get("sql_executed", ""),
                    action_result.get("data", []),
                    action_result.get("row_count", 0),
                    action_result.get("estadistica_tipo", ""),
                    action_result.get("total_elementos", 0)
                )
            else:
                response_with_reflection = self._validate_and_generate_response(
                    context.user_message,
                    action_result.get("sql_executed", ""),
                    action_result.get("data", []),
                    action_result.get("row_count", 0),
                    context.conversation_stack  # ✅ USAR CONTEXTO CONVERSACIONAL DEL CONTEXT
                )

            if not response_with_reflection:
                self.logger.info("   └── ❌ Validación falló")
                return None
            self.logger.info("   └── ✅ Validación y respuesta completadas")

            # Extraer respuesta y reflexión
            human_response = response_with_reflection.get("respuesta_usuario", "Búsqueda completada")
            reflexion = response_with_reflection.get("reflexion_conversacional", {})

            # Preparar resultado final
            result = {
                "success": True,
                "data": action_result.get("data", []),
                "row_count": action_result.get("row_count", 0),
                "sql_executed": action_result.get("sql_executed", ""),
                "action_used": action_request.get('accion_principal', 'unknown'),
                "human_response": human_response,
                "auto_reflexion": reflexion
            }

            self.logger.info(f"   └── ✅ Flujo de 4 prompts completado: {result.get('row_count', 0)} resultados")

            # Preparar parámetros finales
            parameters = {
                "sql_query": result.get("sql_executed", ""),
                "data": result.get("data", []),
                "row_count": result.get("row_count", 0),
                "message": result.get("human_response", "Búsqueda completada"),
                "human_response": result.get("human_response", "Búsqueda completada"),
                "auto_reflexion": result.get("auto_reflexion", {}),
                "flow_type": "four_prompt_search",
                "action_used": result.get("action_used", "BUSCAR_UNIVERSAL"),
                "action_strategy": "four_prompts"
            }

            self.logger.info(f"📊 [FLUJO BÚSQUEDA OPTIMIZADO] Completado: {result.get('row_count', 0)} resultados")
            return InterpretationResult(
                action="consulta_sql_exitosa",
                parameters=parameters,
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"❌ Error en flujo de búsqueda optimizado: {e}")
            return InterpretationResult(
                action="consulta_sql_fallida",
                parameters={
                    "error": f"Error interno en búsqueda optimizada: {str(e)}",
                    "flow_type": "integrated_search"
                },
                confidence=0.1
            )

    # 🗑️ MÉTODOS ELIMINADOS: Todos los flujos paralelos ahora usan el flujo principal unificado

    # 🗑️ MÉTODOS ELIMINADOS: _handle_report_flow, _handle_constancia_flow, _handle_continuation_flow, _handle_search_flow_with_context
    # TODOS AHORA USAN EL FLUJO PRINCIPAL UNIFICADO

    # 🎯 MÉTODOS DEL SISTEMA DE ACCIONES

    def _select_action_strategy(self, user_query: str, categoria: str, conversation_context: str = "") -> Optional[Dict[str, Any]]:
        """
        🆕 NUEVO PROMPT 2: Selecciona estrategia de acciones
        REEMPLAZA: _generate_sql_with_strategy_centralized()
        🎯 NUEVA FUNCIONALIDAD: Detecta consultas de seguimiento y usa BUSCAR_UNIVERSAL con composición
        """
        try:
            # 🎯 PASO 1: VERIFICAR SI ES CONTINUACIÓN USANDO CONVERSATION_STACK
            conversation_stack = getattr(self, 'conversation_stack', [])

            if conversation_stack:
                self.logger.info(f"🎯 VERIFICANDO CONTINUACIÓN - {len(conversation_stack)} niveles disponibles")

                # Detectar si es continuación usando el detector especializado
                continuation_info = self._detect_continuation_query(user_query, conversation_stack)

                if continuation_info and continuation_info.get('es_continuacion', False):
                    self.logger.info(f"✅ CONTINUACIÓN DETECTADA: {continuation_info.get('tipo_continuacion')}")

                    # 🛑 PAUSA ESTRATÉGICA: DETECCIÓN INTELIGENTE DE CONTINUACIONES
                    import os
                    if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                        print(f"\n🛑 [MASTER] DETECCIÓN INTELIGENTE DE CONTINUACIÓN:")
                        print(f"    ├── 📝 Nueva consulta: '{user_query}'")
                        print(f"    ├── 🧠 LLM analizó contexto + nota estratégica")
                        print(f"    ├── ✅ Es continuación: {continuation_info.get('es_continuacion')}")
                        print(f"    ├── 🎯 Tipo detectado: {continuation_info.get('tipo_continuacion')}")
                        print(f"    ├── 📊 Elemento referenciado: {continuation_info.get('elemento_referenciado', 'N/A')}")
                        print(f"    ├── 🔍 Razonamiento LLM: {continuation_info.get('razonamiento', 'N/A')[:100]}...")
                        print(f"    ├── 📋 Contexto disponible: {len(conversation_stack)} niveles")

                        # Mostrar nota estratégica si existe
                        ultimo_nivel = conversation_stack[-1] if conversation_stack else {}
                        auto_reflexion = ultimo_nivel.get('auto_reflexion', {})
                        nota_para_master = auto_reflexion.get('nota_para_master', '')
                        if nota_para_master:
                            print(f"    ├── 💡 Nota estratégica usada: {nota_para_master[:100]}...")

                        print(f"    └── Presiona ENTER para procesar continuación...")
                        input()

                    # Procesar como continuación inteligente
                    continuation_result = self._process_intelligent_continuation(
                        user_query, continuation_info, conversation_stack, {}
                    )

                    if continuation_result:
                        self.logger.info("✅ CONTINUACIÓN PROCESADA EXITOSAMENTE")
                        # Convertir InterpretationResult a formato de action_request
                        return {
                            "accion_principal": "CONTINUACION_PROCESADA",
                            "estrategia": "context_based",
                            "razonamiento": f"Continuación {continuation_info.get('tipo_continuacion')} procesada usando conversation_stack",
                            "resultado_directo": continuation_result  # Resultado ya procesado
                        }
                    else:
                        self.logger.warning("❌ Error procesando continuación, fallback a consulta individual")
                else:
                    self.logger.info("❌ NO es continuación, procesando como consulta individual")
            else:
                self.logger.info("🎯 SIN CONTEXTO CONVERSACIONAL - Procesando consulta individual")

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
                        if campo.lower() == 'grado':
                            master_info += f"- Criterio grado: {{'tabla': 'datos_escolares', 'campo': 'grado', 'operador': '=', 'valor': '{valor}'}}\n"
                        elif campo.lower() == 'grupo':
                            master_info += f"- Criterio grupo: {{'tabla': 'datos_escolares', 'campo': 'grupo', 'operador': '=', 'valor': '{valor}'}}\n"
                        elif campo.lower() == 'turno':
                            master_info += f"- Criterio turno: {{'tabla': 'datos_escolares', 'campo': 'turno', 'operador': '=', 'valor': '{valor.upper()}'}}\n"

                master_info += "\n🔧 USAR ESTOS COMO CRITERIOS SEPARADOS, NO COMBINADOS.\n"

            # Usar nuevo prompt de selección de acciones con información del Master
            action_prompt = self.prompt_manager.get_action_selection_prompt(user_query, categoria, conversation_context + master_info)

            # 🔍 DEBUG: Logging del contexto que se envía al LLM
            self.logger.info(f"🔍 DEBUG - Contexto enviado al LLM (primeros 500 chars): {conversation_context[:500]}...")
            if "IDs disponibles" in conversation_context:
                # Extraer la línea de IDs para verificar
                lines = conversation_context.split('\n')
                for line in lines:
                    if "IDs disponibles" in line:
                        self.logger.info(f"🔍 DEBUG - Línea de IDs: {line}")
                        break

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(action_prompt)

            if response:
                # Parsear respuesta JSON
                action_request = self._parse_action_response(response)

                if action_request:
                    accion_principal = action_request.get('accion_principal', 'unknown')
                    estrategia = action_request.get('estrategia', 'simple')
                    razonamiento = action_request.get('razonamiento', 'N/A')

                    self.logger.info(f"🎯 ESTRATEGIA DE ACCIÓN SELECCIONADA:")
                    self.logger.info(f"   - Acción principal: {accion_principal}")
                    self.logger.info(f"   - Estrategia: {estrategia}")
                    self.logger.info(f"   - Razonamiento: {razonamiento}")

                    return action_request
                else:
                    self.logger.warning("❌ No se pudo parsear respuesta de selección de acción")
                    return None
            else:
                self.logger.warning("❌ No se recibió respuesta del LLM para selección de acción")
                return None

        except Exception as e:
            self.logger.error(f"Error seleccionando estrategia de acción: {e}")
            return None

    def _is_follow_up_query(self, user_query: str) -> bool:
        """
        🧠 DETECTAR SI ES CONSULTA DE SEGUIMIENTO INTELIGENTE
        Usa LLM para determinar si la consulta se refiere realmente al contexto previo
        """
        try:
            query_lower = user_query.lower()

            # 🎯 PATRONES EXPLÍCITOS DE SEGUIMIENTO (ALTA CONFIANZA)
            explicit_patterns = [
                "de estos", "de esos", "de ellos", "de las anteriores",
                "solo los", "solo las", "únicamente los", "únicamente las",
                "el primero", "el segundo", "el tercero", "la primera", "la segunda",
                "ese alumno", "esa alumna", "para él", "para ella"
            ]

            # Si tiene patrones explícitos, es seguimiento seguro
            for pattern in explicit_patterns:
                if pattern in query_lower:
                    self.logger.info(f"🔍 Patrón explícito de seguimiento detectado: '{pattern}'")
                    return True

            # 🧠 PATRONES AMBIGUOS QUE REQUIEREN ANÁLISIS LLM
            ambiguous_patterns = [
                "filtrar", "filtrar por", "que sean", "que tengan",
                "del turno", "de grado", "del grupo", "con calificaciones",
                "sin calificaciones", "que estudien", "que estén en"
            ]

            # Si tiene patrones ambiguos, usar LLM para decidir
            has_ambiguous = any(pattern in query_lower for pattern in ambiguous_patterns)

            if has_ambiguous:
                self.logger.info(f"🧠 Patrón ambiguo detectado, usando LLM para análisis inteligente...")
                return self._analyze_context_relevance_with_llm(user_query)

            # 🎯 PATRONES DE CONSULTA INDEPENDIENTE (ALTA CONFIANZA)
            independent_patterns = [
                "promedio general", "promedio de la escuela", "total de la escuela",
                "estadísticas de la escuela", "todos los alumnos", "cuántos alumnos hay",
                "dame el promedio", "estadísticas generales", "datos de la escuela"
            ]

            # Si tiene patrones independientes, NO es seguimiento
            for pattern in independent_patterns:
                if pattern in query_lower:
                    self.logger.info(f"🎯 Patrón independiente detectado: '{pattern}' - NO es seguimiento")
                    return False

            return False

        except Exception as e:
            self.logger.error(f"Error detectando consulta de seguimiento: {e}")
            return False

    def _analyze_context_relevance_with_llm(self, user_query: str) -> bool:
        """
        🧠 ANÁLISIS LLM: Determina si la consulta se refiere al contexto previo
        """
        try:
            # Obtener contexto conversacional
            conversation_stack = getattr(self, 'conversation_stack', [])

            if not conversation_stack:
                return False

            # Obtener la consulta anterior
            ultimo_nivel = conversation_stack[-1]
            consulta_anterior = ultimo_nivel.get('query', 'N/A')
            datos_anteriores = ultimo_nivel.get('row_count', 0)

            # Crear prompt para análisis de relevancia
            relevance_prompt = f"""
Eres un experto en análisis conversacional para sistemas escolares.

CONTEXTO PREVIO:
- Consulta anterior: "{consulta_anterior}"
- Resultados: {datos_anteriores} elementos

CONSULTA ACTUAL: "{user_query}"

TAREA: Determina si la consulta actual se refiere específicamente a los datos de la consulta anterior.

CRITERIOS:
✅ ES SEGUIMIENTO si:
- Se refiere a filtrar/seleccionar de los datos anteriores
- Usa criterios adicionales sobre la misma población
- Busca información específica de los elementos ya mostrados

❌ NO ES SEGUIMIENTO si:
- Solicita información general de toda la escuela
- Cambia completamente el ámbito de la consulta
- Pide estadísticas globales independientes del contexto

EJEMPLOS:
- "de esos dame los del turno matutino" → ES SEGUIMIENTO
- "dame el promedio general de la escuela" → NO ES SEGUIMIENTO
- "que tengan calificaciones" → ES SEGUIMIENTO (si contexto es lista de alumnos)
- "cuántos alumnos hay en total" → NO ES SEGUIMIENTO

RESPONDE SOLO: true o false
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(relevance_prompt)

            if response:
                is_follow_up = response.strip().lower() == 'true'
                self.logger.info(f"🧠 LLM determinó: {'ES' if is_follow_up else 'NO ES'} seguimiento")
                return is_follow_up
            else:
                self.logger.warning("❌ No se recibió respuesta del LLM para análisis de relevancia")
                return False

        except Exception as e:
            self.logger.error(f"Error en análisis LLM de relevancia: {e}")
            return False

    def _execute_selected_action(self, action_request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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

            # Ejecutar la acción
            result = action_executor.execute_action_request(action_request)

            self.logger.info(f"🎯 RESULTADO DE ACCIÓN:")
            self.logger.info(f"   - Success: {result.get('success')}")
            self.logger.info(f"   - Action used: {result.get('action_used')}")
            self.logger.info(f"   - Row count: {result.get('row_count')}")
            self.logger.info(f"   - Message: {result.get('message')}")

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

    def _validate_and_generate_statistics_response(self, user_query: str, sql_query: str, data: List[Dict], row_count: int, estadistica_tipo: str, total_elementos: int) -> Optional[Dict]:
        """
        PROMPT 3 ESPECIALIZADO PARA ESTADÍSTICAS: Valida + Genera respuesta estadística + Auto-reflexiona
        """
        try:
            # Para estadísticas agrupadas (por grado, turno, etc.)
            if estadistica_tipo == "conteo_agrupado" and data and len(data) > 0:
                estadisticas = data[0] if isinstance(data, list) else data

                if isinstance(estadisticas, dict):
                    # Formatear como tabla legible
                    respuesta_estadistica = "📊 Estadísticas de alumnos:\n\n"
                    for grupo, cantidad in estadisticas.items():
                        respuesta_estadistica += f"• {grupo}° grado: {cantidad} alumnos\n"
                    respuesta_estadistica += f"\n🎯 Total general: {total_elementos} alumnos"

                    reflexion = {
                        "espera_continuacion": False,
                        "tipo_esperado": "none",
                        "datos_recordar": {
                            "estadisticas": estadisticas,
                            "total": total_elementos,
                            "tipo": estadistica_tipo
                        },
                        "razonamiento": f"Se proporcionaron estadísticas de {len(estadisticas)} grupos con {total_elementos} elementos totales."
                    }

                    return {
                        "respuesta_usuario": respuesta_estadistica,
                        "reflexion_conversacional": reflexion,
                        "resuelve_consulta": True
                    }

            # Para conteos simples con filtros (ej: turno vespertino)
            elif estadistica_tipo in ["conteo", "conteo_simple"] and data and len(data) > 0:
                resultado = data[0] if isinstance(data, list) else data

                if isinstance(resultado, dict) and 'total' in resultado:
                    cantidad = resultado['total']

                    # Generar respuesta humanizada basada en la consulta
                    if "turno vespertino" in user_query.lower():
                        respuesta_estadistica = f"🌅 En el turno vespertino hay {cantidad} alumnos inscritos."
                    elif "turno matutino" in user_query.lower():
                        respuesta_estadistica = f"🌄 En el turno matutino hay {cantidad} alumnos inscritos."
                    elif "grado" in user_query.lower():
                        respuesta_estadistica = f"📚 Se encontraron {cantidad} alumnos que cumplen con el criterio de grado especificado."
                    elif "escuela" in user_query.lower() or "total" in user_query.lower():
                        respuesta_estadistica = f"🏫 La escuela tiene un total de {cantidad} alumnos inscritos."
                    else:
                        respuesta_estadistica = f"📊 Total de alumnos encontrados: {cantidad}"

                    # Agregar contexto útil si es relevante
                    if cantidad > 0:
                        respuesta_estadistica += f"\n\n💡 Si necesitas ver la lista de estos alumnos, puedes preguntarme: 'muéstrame los alumnos del turno vespertino'"

                    reflexion = {
                        "espera_continuacion": False,
                        "tipo_esperado": "none",
                        "datos_recordar": {
                            "conteo": cantidad,
                            "criterio": user_query,
                            "tipo": "conteo_simple"
                        },
                        "razonamiento": f"Se proporcionó un conteo simple de {cantidad} elementos."
                    }

                    return {
                        "respuesta_usuario": respuesta_estadistica,
                        "reflexion_conversacional": reflexion,
                        "resuelve_consulta": True
                    }

            # Para distribuciones (con porcentajes)
            elif estadistica_tipo == "distribucion" and data and len(data) > 0:
                distribucion = data[0] if isinstance(data, list) else data

                if isinstance(distribucion, dict):
                    respuesta_estadistica = "📊 Distribución de alumnos:\n\n"
                    for categoria, info in distribucion.items():
                        if isinstance(info, dict) and 'cantidad' in info and 'porcentaje' in info:
                            respuesta_estadistica += f"• {categoria}: {info['cantidad']} alumnos ({info['porcentaje']}%)\n"

                    reflexion = {
                        "espera_continuacion": False,
                        "tipo_esperado": "none",
                        "datos_recordar": {
                            "distribucion": distribucion,
                            "total": total_elementos,
                            "tipo": estadistica_tipo
                        },
                        "razonamiento": f"Se proporcionó una distribución con {len(distribucion)} categorías."
                    }

                    return {
                        "respuesta_usuario": respuesta_estadistica,
                        "reflexion_conversacional": reflexion,
                        "resuelve_consulta": True
                    }

            # Para promedios simples (ej: promedio general de calificaciones)
            elif estadistica_tipo == "promedio_simple" and data and len(data) > 0:
                resultado = data[0] if isinstance(data, list) else data

                if isinstance(resultado, dict):
                    # Detectar tipo de promedio
                    if 'promedio_general' in resultado:
                        promedio = resultado['promedio_general']
                        respuesta_estadistica = f"📊 El promedio general de calificaciones de la escuela es: **{promedio}**"

                        # Agregar contexto interpretativo
                        if promedio >= 9.0:
                            respuesta_estadistica += "\n\n🌟 ¡Excelente rendimiento académico!"
                        elif promedio >= 8.0:
                            respuesta_estadistica += "\n\n✅ Buen rendimiento académico general."
                        elif promedio >= 7.0:
                            respuesta_estadistica += "\n\n📈 Rendimiento académico satisfactorio."
                        else:
                            respuesta_estadistica += "\n\n📚 Hay oportunidades de mejora en el rendimiento académico."

                    elif 'promedio_edad' in resultado:
                        promedio = resultado['promedio_edad']
                        respuesta_estadistica = f"📊 La edad promedio de los alumnos es: **{promedio} años**"
                    else:
                        # Promedio genérico
                        campo_promedio = list(resultado.keys())[0]
                        valor_promedio = resultado[campo_promedio]
                        respuesta_estadistica = f"📊 Promedio calculado: **{valor_promedio}**"

                    reflexion = {
                        "espera_continuacion": False,
                        "tipo_esperado": "none",
                        "datos_recordar": {
                            "promedio": resultado,
                            "tipo": "promedio_simple",
                            "consulta": user_query
                        },
                        "razonamiento": f"Se proporcionó un promedio simple. Consulta resuelta completamente."
                    }

                    return {
                        "respuesta_usuario": respuesta_estadistica,
                        "reflexion_conversacional": reflexion,
                        "resuelve_consulta": True
                    }

            # Fallback: usar método normal si no es estadística reconocida
            return self._validate_and_generate_response(user_query, sql_query, data, row_count)

        except Exception as e:
            self.logger.error(f"Error generando respuesta estadística: {e}")
            return None

    def _detect_continuation_query(self, user_query: str, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        DETECTOR INTELIGENTE DE CONTINUACIÓN: Usa LLM + nota estratégica de Student
        ✅ MIGRADO: Usa ContinuationDetector centralizado con mejoras
        """
        try:
            self.logger.info(f"🔍 [DETECCIÓN INTELIGENTE] Analizando consulta: '{user_query}'")
            self.logger.info(f"🔍 [DETECCIÓN INTELIGENTE] Contexto disponible: {len(conversation_stack)} niveles")

            # Mostrar nota estratégica si existe
            if conversation_stack:
                ultimo_nivel = conversation_stack[-1]
                auto_reflexion = ultimo_nivel.get('auto_reflexion', {})
                nota_para_master = auto_reflexion.get('nota_para_master', '')
                if nota_para_master:
                    self.logger.info(f"🔍 [DETECCIÓN INTELIGENTE] Usando nota estratégica: {nota_para_master[:100]}...")

            result = self.continuation_detector.detect_continuation(user_query, conversation_stack)

            if result and result.get('es_continuacion', False):
                self.logger.info(f"✅ [DETECCIÓN INTELIGENTE] Continuación detectada:")
                self.logger.info(f"   ├── Tipo: {result.get('tipo_continuacion', 'unknown')}")
                self.logger.info(f"   ├── Elemento: {result.get('elemento_referenciado', 'N/A')}")
                self.logger.info(f"   ├── Confianza: {result.get('confianza', 'N/A')}")
                self.logger.info(f"   └── Razonamiento: {result.get('razonamiento', 'N/A')[:100]}...")
                return result
            else:
                self.logger.info(f"❌ [DETECCIÓN INTELIGENTE] No es continuación - procesando como consulta nueva")
                return {"es_continuacion": False, "tipo_continuacion": "none"}

        except Exception as e:
            self.logger.error(f"Error en detección inteligente: {e}")
            return {"es_continuacion": False, "tipo_continuacion": "none"}

    def _process_intelligent_continuation(self, user_query: str, continuation_info: Dict[str, Any], conversation_stack: list, detected_entities: Dict[str, Any]) -> Optional[InterpretationResult]:
        """
        🧠 PROCESADOR INTELIGENTE DE CONTINUACIÓN: Decide automáticamente si usar contexto o expandir búsqueda
        """
        try:
            tipo_continuacion = continuation_info.get('tipo_continuacion', 'none')
            self.logger.info(f"🧠 PROCESANDO CONTINUACIÓN INTELIGENTE: {tipo_continuacion}")

            # 🎯 GUARDAR CONTEXTO TEMPORALMENTE PARA USO EN MÉTODOS INTERNOS
            self._temp_context = getattr(self, '_current_context', None)

            # 1. ANALIZAR QUÉ INFORMACIÓN TENGO EN EL CONTEXTO
            available_data = self._analyze_available_context_data(conversation_stack)
            self.logger.info(f"🔍 Datos disponibles en contexto: {available_data}")

            # 2. ANALIZAR QUÉ INFORMACIÓN NECESITO PARA LA CONSULTA
            required_data = self._analyze_required_information(user_query, tipo_continuacion)
            self.logger.info(f"🎯 Información requerida: {required_data}")

            # 3. DECISIÓN INTELIGENTE: ¿TENGO SUFICIENTE INFORMACIÓN?
            decision = self._make_intelligent_decision(available_data, required_data, user_query)
            self.logger.info(f"🧠 DECISIÓN: {decision['action']} - {decision['reason']}")

            # 4. EJECUTAR ACCIÓN SEGÚN DECISIÓN
            if decision['action'] == 'use_context':
                # ✅ USAR CONTEXTO: Tengo suficiente información
                return self._process_continuation_with_context(user_query, continuation_info, conversation_stack)

            elif decision['action'] == 'expand_search':
                # 🔄 EXPANDIR BÚSQUEDA: Necesito más información
                return self._process_continuation_with_expansion(user_query, continuation_info, conversation_stack, detected_entities)

            else:
                # 🧹 SIN FALLBACKS - Si no se puede determinar la acción, que falle claramente
                self.logger.error(f"❌ Acción no reconocida en continuación: {decision.get('action')}")
                raise ValueError(f"Acción de continuación no reconocida: {decision.get('action')}")

        except Exception as e:
            self.logger.error(f"Error en continuación inteligente: {e}")
            # 🧹 SIN FALLBACKS - Que falle claramente para debugging
            raise
        finally:
            # 🧹 LIMPIAR CONTEXTO TEMPORAL
            self._temp_context = None

    def _analyze_available_context_data(self, conversation_stack: list) -> Dict[str, Any]:
        """🔍 ANALIZA QUÉ INFORMACIÓN ESTÁ DISPONIBLE EN EL CONTEXTO"""
        try:
            if not conversation_stack:
                return {"has_data": False, "fields": [], "count": 0}

            # Obtener el último nivel con datos
            ultimo_nivel = None
            for level in reversed(conversation_stack):
                if level.get('data') and len(level.get('data', [])) > 0:
                    ultimo_nivel = level
                    break

            if not ultimo_nivel:
                return {"has_data": False, "fields": [], "count": 0}

            data = ultimo_nivel.get('data', [])
            if not data:
                return {"has_data": False, "fields": [], "count": 0}

            # Analizar campos disponibles en el primer elemento
            first_item = data[0] if isinstance(data, list) else data
            available_fields = list(first_item.keys()) if isinstance(first_item, dict) else []

            return {
                "has_data": True,
                "fields": available_fields,
                "count": len(data) if isinstance(data, list) else 1,
                "data_type": "list" if isinstance(data, list) else "single",
                "sample_data": first_item
            }

        except Exception as e:
            self.logger.error(f"Error analizando contexto: {e}")
            return {"has_data": False, "fields": [], "count": 0}

    def _analyze_required_information(self, user_query: str, tipo_continuacion: str) -> Dict[str, Any]:
        """🎯 ANALIZA QUÉ INFORMACIÓN SE NECESITA PARA LA CONSULTA"""
        try:
            user_lower = user_query.lower()

            # Campos básicos que siempre se necesitan
            basic_fields = ['nombre', 'curp']

            # Detectar qué información específica se solicita
            required_fields = basic_fields.copy()
            detail_level = "basic"

            # Detectar solicitudes de detalles completos
            detail_keywords = ['detalles', 'información completa', 'todo', 'completo', 'datos completos']
            if any(keyword in user_lower for keyword in detail_keywords):
                required_fields.extend(['grado', 'grupo', 'turno', 'matricula', 'fecha_nacimiento'])
                detail_level = "complete"

            # Detectar solicitudes de constancias (requieren datos completos + calificaciones)
            constancia_keywords = ['constancia', 'certificado', 'genera', 'generar', 'crear', 'documento']
            if any(keyword in user_lower for keyword in constancia_keywords):
                required_fields.extend(['grado', 'grupo', 'turno', 'matricula', 'id'])
                detail_level = "constancia"

                # Si es constancia de calificaciones, necesita datos de calificaciones
                if 'calificaciones' in user_lower:
                    required_fields.append('calificaciones')

            # Detectar solicitudes específicas de campos
            field_requests = {
                'curp': ['curp'],
                'matricula': ['matricula', 'matrícula'],
                'grado': ['grado'],
                'grupo': ['grupo'],
                'turno': ['turno'],
                'calificaciones': ['calificaciones', 'notas', 'calificación']
            }

            for field, keywords in field_requests.items():
                if any(keyword in user_lower for keyword in keywords):
                    if field not in required_fields:
                        required_fields.append(field)

            return {
                "fields": required_fields,
                "detail_level": detail_level,
                "needs_database_search": detail_level in ["complete", "constancia"],
                "query_type": tipo_continuacion
            }

        except Exception as e:
            self.logger.error(f"Error analizando requerimientos: {e}")
            return {"fields": ['nombre', 'curp'], "detail_level": "basic", "needs_database_search": False}

    def _make_intelligent_decision(self, available_data: Dict, required_data: Dict, user_query: str) -> Dict[str, str]:
        """🧠 TOMA DECISIÓN INTELIGENTE: ¿Usar contexto o expandir búsqueda?"""
        try:
            # Si no hay datos disponibles, no se puede usar contexto
            if not available_data.get("has_data", False):
                return {
                    "action": "expand_search",
                    "reason": "No hay datos disponibles en el contexto"
                }

            available_fields = set(available_data.get("fields", []))
            required_fields = set(required_data.get("fields", []))

            # Verificar si tengo todos los campos necesarios
            missing_fields = required_fields - available_fields

            # DECISIÓN BASADA EN NIVEL DE DETALLE REQUERIDO
            detail_level = required_data.get("detail_level", "basic")

            if detail_level == "basic":
                # Para consultas básicas, si tengo nombre y CURP es suficiente
                if "nombre" in available_fields and ("curp" in available_fields or len(missing_fields) <= 1):
                    return {
                        "action": "use_context",
                        "reason": f"Tengo información suficiente para consulta básica. Campos disponibles: {list(available_fields)}"
                    }

            elif detail_level == "complete":
                # Para detalles completos, necesito expandir si faltan campos importantes
                important_fields = {"grado", "grupo", "turno", "matricula"}
                missing_important = important_fields - available_fields

                if len(missing_important) > 2:
                    return {
                        "action": "expand_search",
                        "reason": f"Faltan campos importantes para detalles completos: {list(missing_important)}"
                    }
                else:
                    return {
                        "action": "use_context",
                        "reason": f"Tengo suficientes campos para detalles. Solo faltan: {list(missing_fields)}"
                    }

            elif detail_level == "constancia":
                # Para constancias, siempre expandir para asegurar datos completos
                return {
                    "action": "expand_search",
                    "reason": "Las constancias requieren datos completos y verificados de la base de datos"
                }

            # DECISIÓN POR DEFECTO: Si faltan pocos campos, usar contexto
            if len(missing_fields) <= 2:
                return {
                    "action": "use_context",
                    "reason": f"Solo faltan {len(missing_fields)} campos: {list(missing_fields)}"
                }
            else:
                return {
                    "action": "expand_search",
                    "reason": f"Faltan demasiados campos: {list(missing_fields)}"
                }

        except Exception as e:
            self.logger.error(f"Error en decisión inteligente: {e}")
            return {
                "action": "use_context",
                "reason": "Error en análisis, usando contexto por defecto"
            }

    def _process_continuation_with_context(self, user_query: str, continuation_info: Dict[str, Any], conversation_stack: list) -> Optional[InterpretationResult]:
        """✅ PROCESAR USANDO CONTEXTO: Tengo suficiente información
        🎯 NUEVA LÓGICA: Usar tipo de continuación para decidir el método correcto
        """
        self.logger.info("✅ USANDO CONTEXTO: Información suficiente disponible")

        # 🎯 USAR TIPO DE CONTINUACIÓN PARA DECIDIR EL MÉTODO CORRECTO
        tipo_continuacion = continuation_info.get('tipo_continuacion', 'none')

        if tipo_continuacion == "selection":
            # ✅ SELECCIÓN: Extraer directamente del conversation_stack
            self.logger.info("🎯 CONTINUACIÓN DE SELECCIÓN - Extrayendo directamente del contexto")
            elemento_referenciado = continuation_info.get('elemento_referenciado')
            return self._process_selection_continuation(user_query, elemento_referenciado, conversation_stack)

        elif conversation_stack and self._is_follow_up_query(user_query):
            # 🔄 FOLLOW-UP: Usar BUSCAR_UNIVERSAL con composición
            self.logger.info("🔄 CONSULTA DE SEGUIMIENTO DETECTADA EN CONTEXTO - Usando BUSCAR_UNIVERSAL")
            return self._execute_search_with_context_composition(user_query, conversation_stack)

        # 🎯 FLUJO TRADICIONAL DE CONTEXTO
        self.logger.info("💬 Usando flujo tradicional de contexto...")
        return self._process_continuation_fallback(user_query, continuation_info, conversation_stack)

    def _execute_search_with_context_composition(self, user_query: str, conversation_stack: list) -> Optional[InterpretationResult]:
        """
        🔍 EJECUTAR BÚSQUEDA CON COMPOSICIÓN DE CONTEXTO
        Usa BUSCAR_UNIVERSAL con criterios del contexto + nueva consulta
        """
        try:
            self.logger.info("🔍 [BÚSQUEDA CON COMPOSICIÓN] Iniciando con BUSCAR_UNIVERSAL...")

            # 🎯 CONSTRUIR PARÁMETROS USANDO FILTROS DEL MASTER DIRECTAMENTE
            from app.core.ai.actions import ActionExecutor
            action_executor = ActionExecutor(self.sql_executor, self)

            # 🧠 OBTENER FILTROS DEL MASTER DIRECTAMENTE
            master_filters = self._get_master_filters()
            self.logger.info(f"🧠 Filtros del Master obtenidos: {master_filters}")

            # Construir parámetros usando filtros del Master + contexto
            universal_params = action_executor.build_buscar_universal_with_master_filters(
                user_query, conversation_stack, master_filters
            )

            # Crear action_request para BUSCAR_UNIVERSAL
            action_request = {
                "accion_principal": "BUSCAR_UNIVERSAL",
                "estrategia": "simple",
                "razonamiento": f"Consulta de seguimiento detectada. Combinando criterios del contexto con nueva consulta: '{user_query}'",
                "parametros": universal_params
            }

            self.logger.info(f"🎯 ESTRATEGIA DE ACCIÓN SELECCIONADA (COMPOSICIÓN):")
            self.logger.info(f"   - Acción principal: BUSCAR_UNIVERSAL")
            self.logger.info(f"   - Estrategia: simple")
            self.logger.info(f"   - Parámetros: {universal_params}")

            # 🆕 EJECUTAR ACCIÓN SELECCIONADA
            self.logger.info("   ├── EJECUTANDO ACCIÓN CON COMPOSICIÓN...")
            action_result = self._execute_selected_action(action_request)

            if not action_result or not action_result.get("success"):
                self.logger.info(f"   └── ❌ Ejecución de acción con composición falló: {action_result.get('message', 'Error desconocido')}")
                return InterpretationResult(
                    action="consulta_sql_fallida",
                    parameters={
                        "error": action_result.get('message', 'Error ejecutando acción con composición'),
                        "action_used": action_request.get('accion_principal', 'unknown')
                    },
                    confidence=0.2
                )
            self.logger.info(f"   └── ✅ Acción con composición ejecutada: {action_result.get('row_count')} resultados")

            # PROMPT 3: Validar + Generar respuesta + Auto-reflexión
            self.logger.info("   ├── PROMPT 3: Validación + respuesta + auto-reflexión...")
            response_with_reflection = self._validate_and_generate_response(
                user_query,
                action_result.get("sql_executed", ""),
                action_result.get("data", []),
                action_result.get("row_count", 0),
                conversation_stack  # ✅ USAR CONVERSATION_STACK DEL PARÁMETRO
            )

            if not response_with_reflection:
                self.logger.info("   └── ❌ Validación con composición falló")
                return InterpretationResult(
                    action="consulta_sql_fallida",
                    parameters={
                        "error": "La acción con composición no resolvió correctamente la solicitud",
                        "action_used": action_request.get('accion_principal', 'unknown')
                    },
                    confidence=0.2
                )
            self.logger.info("   └── ✅ Validación y respuesta con composición completadas")

            # Extraer respuesta y reflexión
            human_response = response_with_reflection.get("respuesta_usuario", "Respuesta procesada con composición")
            reflexion = response_with_reflection.get("reflexion_conversacional", {})

            # 🎯 USAR DATOS FILTRADOS si están disponibles en la respuesta
            filtered_data = response_with_reflection.get("datos_filtrados", action_result.get("data", []))
            filtered_count = response_with_reflection.get("cantidad_filtrada", action_result.get("row_count", 0))

            # Preparar parámetros con información de auto-reflexión
            parameters = {
                "sql_query": action_result.get("sql_executed", ""),
                "data": filtered_data,  # ✅ USAR DATOS FILTRADOS
                "row_count": filtered_count,  # ✅ USAR COUNT FILTRADO
                "message": human_response,
                "human_response": human_response,
                "auto_reflexion": reflexion,
                "flow_type": "search_with_composition",
                "action_used": action_request.get('accion_principal', 'unknown'),
                "action_strategy": action_request.get('estrategia', 'simple')
            }

            self.logger.info(f"📊 [BÚSQUEDA CON COMPOSICIÓN] Completado: {action_result.get('row_count', 0)} resultados")
            return InterpretationResult(
                action="consulta_sql_exitosa",
                parameters=parameters,
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"❌ Error en búsqueda con composición: {e}")
            return InterpretationResult(
                action="consulta_sql_fallida",
                parameters={
                    "error": f"Error interno en búsqueda con composición: {str(e)}",
                    "flow_type": "search_with_composition"
                },
                confidence=0.1
            )

    def _is_clarification_response(self, context: InterpretationContext) -> bool:
        """
        🔄 VERIFICAR SI ES RESPUESTA A ACLARACIÓN
        Detecta si el usuario está respondiendo a una pregunta de aclaración del Master
        """
        try:
            # Verificar si hay información de aclaración pendiente en el contexto
            if hasattr(context, 'intention_info') and context.intention_info:
                waiting_for = context.intention_info.get('waiting_for')
                if waiting_for == 'clarification':
                    self.logger.info("🔄 [STUDENT] Detectada respuesta a aclaración")
                    return True

            # Verificar en conversation_stack si hay aclaración pendiente
            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                ultimo_nivel = context.conversation_stack[-1]
                if ultimo_nivel.get('waiting_for') == 'clarification':
                    self.logger.info("🔄 [STUDENT] Detectada respuesta a aclaración en stack")
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error verificando respuesta de aclaración: {e}")
            return False

    def _handle_clarification_response(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        🔄 MANEJAR RESPUESTA DE ACLARACIÓN
        Procesa la respuesta del usuario a una pregunta de aclaración
        """
        try:
            self.logger.info("🔄 [STUDENT] Procesando respuesta de aclaración")

            user_response = context.user_message.strip()

            # Obtener información de la aclaración pendiente
            clarification_info = self._get_clarification_info(context)
            if not clarification_info:
                self.logger.error("❌ No se encontró información de aclaración pendiente")
                return None

            # Interpretar respuesta del usuario
            selected_option = self._interpret_user_clarification(user_response, clarification_info)
            if not selected_option:
                self.logger.warning("⚠️ No se pudo interpretar la respuesta del usuario")
                return InterpretationResult(
                    action="aclaracion_invalida",
                    parameters={
                        "message": "No entendí tu respuesta. Por favor, responde con el número de la opción que necesitas.",
                        "original_options": clarification_info.get("options", [])
                    },
                    confidence=0.5
                )

            # Procesar con la opción seleccionada
            return self._process_with_clarification(context, clarification_info, selected_option)

        except Exception as e:
            self.logger.error(f"Error manejando respuesta de aclaración: {e}")
            return None

    def _get_clarification_info(self, context: InterpretationContext) -> dict:
        """Obtiene información de la aclaración pendiente"""
        try:
            # Buscar en intention_info
            if hasattr(context, 'intention_info') and context.intention_info:
                if context.intention_info.get('waiting_for') == 'clarification':
                    return {
                        "original_query": context.intention_info.get('original_query'),
                        "options": context.intention_info.get('ambiguity_options', []),
                        "ambiguity_type": context.intention_info.get('ambiguity_type')
                    }

            # Buscar en conversation_stack
            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                ultimo_nivel = context.conversation_stack[-1]
                if ultimo_nivel.get('waiting_for') == 'clarification':
                    return ultimo_nivel.get('clarification_info', {})

            return {}

        except Exception as e:
            self.logger.error(f"Error obteniendo información de aclaración: {e}")
            return {}

    def _interpret_user_clarification(self, user_response: str, clarification_info: dict) -> dict:
        """Interpreta la respuesta del usuario a la aclaración"""
        try:
            options = clarification_info.get("options", [])
            if not options:
                return {}

            user_response = user_response.strip().lower()

            # Intentar interpretar como número
            try:
                option_number = int(user_response)
                if 1 <= option_number <= len(options):
                    selected_option = options[option_number - 1]
                    self.logger.info(f"✅ Opción seleccionada por número: {selected_option}")
                    return selected_option
            except ValueError:
                pass

            # Intentar interpretar por texto
            for option in options:
                label = option.get("label", "").lower()
                value = option.get("value", "").lower()
                description = option.get("description", "").lower()

                if (label in user_response or
                    value in user_response or
                    any(word in user_response for word in label.split()) or
                    any(word in user_response for word in description.split())):
                    self.logger.info(f"✅ Opción seleccionada por texto: {option}")
                    return option

            return {}

        except Exception as e:
            self.logger.error(f"Error interpretando respuesta del usuario: {e}")
            return {}

    def _process_with_clarification(self, context: InterpretationContext, clarification_info: dict, selected_option: dict) -> Optional[InterpretationResult]:
        """Procesa la consulta original con la aclaración del usuario"""
        try:
            self.logger.info(f"🔄 [STUDENT] Procesando con aclaración: {selected_option}")

            # Reconstruir consulta original con aclaración
            original_query = clarification_info.get("original_query", "")
            clarified_value = selected_option.get("value", "")

            # Crear nueva intención con la aclaración
            clarified_intention = {
                "intention_type": "consulta_alumnos",
                "sub_intention": "busqueda_con_filtros",
                "detected_entities": {
                    "filtros": [clarified_value],
                    "accion_principal": "buscar"
                },
                "categoria": "busqueda",
                "sub_tipo": "filtros",
                "complejidad": "baja",
                "flujo_optimo": "sql_directo"
            }

            # Actualizar contexto con la nueva intención
            context.intention_info = clarified_intention
            context.user_message = f"{original_query} ({selected_option.get('label', '')})"

            # Procesar normalmente con la aclaración
            conversation_context = ""
            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                conversation_context = self._format_conversation_stack_for_llm(context.conversation_stack)

            return self._execute_main_3_prompt_flow(context, clarified_intention, conversation_context)

        except Exception as e:
            self.logger.error(f"Error procesando con aclaración: {e}")
            return None

    # 🗑️ MÉTODOS ELIMINADOS: COMUNICACIÓN BIDIRECCIONAL DEL STUDENT
    # RAZÓN: Student ya no maneja comunicación bidireccional - es responsabilidad exclusiva del Master
    #
    # Métodos eliminados:
    # - _check_for_bidirectional_needs()
    # - _detect_execution_ambiguity()
    # - _check_multiple_interpretations()
    # - _analyze_execution_ambiguity()
    # - _detect_unexpected_results()
    # - _create_bidirectional_result()
    #
    # El Student ahora SOLO ejecuta y reporta datos al Master.
    # El Master decide si necesita comunicación bidireccional basado en los resultados.

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

    def _process_continuation_with_expansion(self, user_query: str, continuation_info: Dict[str, Any], conversation_stack: list, detected_entities: Dict[str, Any]) -> Optional[InterpretationResult]:
        """🔄 PROCESAR CON EXPANSIÓN: Necesito buscar más información"""
        self.logger.info("🔄 EXPANDIENDO BÚSQUEDA: Necesito más información de la base de datos")

        try:
            # 1. IDENTIFICAR ALUMNO DEL CONTEXTO
            alumno_identificado = self._identify_student_from_context(user_query, conversation_stack)

            if not alumno_identificado:
                self.logger.error("❌ No se pudo identificar alumno del contexto")
                raise ValueError("No se pudo identificar alumno del contexto para expansión")

            # 2. GENERAR SQL PARA OBTENER INFORMACIÓN COMPLETA
            sql_query = self._generate_expanded_sql_for_student(alumno_identificado, user_query)

            if not sql_query:
                self.logger.error("❌ No se pudo generar SQL expandido")
                raise ValueError("No se pudo generar SQL expandido para el alumno identificado")

            # 3. EJECUTAR CONSULTA EXPANDIDA
            self.logger.info(f"🔄 Ejecutando consulta expandida: {sql_query[:100]}...")
            result = self.sql_executor.execute_query(sql_query)

            if not result.success:
                self.logger.warning(f"❌ Consulta expandida falló: {result.message}")
                return self._process_continuation_fallback(user_query, continuation_info, conversation_stack)

            # 4. PROCESAR RESULTADOS EXPANDIDOS
            self.logger.info(f"✅ Consulta expandida exitosa: {result.row_count} resultados")

            # Generar respuesta con datos completos CON CONTEXTO
            response_with_reflection = self._validate_and_generate_response(
                user_query, sql_query, result.data, result.row_count, conversation_stack
            )

            if not response_with_reflection:
                self.logger.warning("❌ No se pudo generar respuesta expandida")
                return self._process_continuation_fallback(user_query, continuation_info, conversation_stack)

            # Preparar resultado con información expandida
            parameters = {
                "sql_query": result.query_executed,
                "data": result.data,
                "row_count": result.row_count,
                "message": response_with_reflection.get("respuesta_usuario", "Información expandida obtenida"),
                "human_response": response_with_reflection.get("respuesta_usuario", "Información expandida obtenida"),
                "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                "expansion_type": "intelligent_continuation"
            }

            return InterpretationResult(
                action="consulta_sql_exitosa",
                parameters=parameters,
                confidence=0.95
            )

        except Exception as e:
            self.logger.error(f"Error en expansión de búsqueda: {e}")
            return self._process_continuation_fallback(user_query, continuation_info, conversation_stack)

    def _generate_expanded_sql_for_student(self, alumno: Dict[str, Any], user_query: str) -> Optional[str]:
        """🔄 GENERA SQL PARA OBTENER INFORMACIÓN COMPLETA DEL ALUMNO"""
        try:
            # Usar nombre o CURP para identificar al alumno
            nombre = alumno.get('nombre', '')
            curp = alumno.get('curp', '')
            alumno_id = alumno.get('id', '')

            if not (nombre or curp or alumno_id):
                self.logger.warning("❌ No hay información suficiente para generar SQL expandido")
                return None

            # Construir condición WHERE
            where_conditions = []

            if alumno_id:
                where_conditions.append(f"a.id = {alumno_id}")
            elif curp:
                where_conditions.append(f"a.curp = '{curp}'")
            elif nombre:
                # Buscar por nombre (puede ser parcial)
                nombre_parts = nombre.upper().split()
                for part in nombre_parts:
                    if len(part) > 2:  # Solo usar partes significativas
                        where_conditions.append(f"a.nombre LIKE '%{part}%'")

            if not where_conditions:
                return None

            where_clause = " AND ".join(where_conditions)

            # Detectar si necesita calificaciones
            user_lower = user_query.lower()
            needs_grades = any(keyword in user_lower for keyword in ['calificaciones', 'notas', 'constancia'])

            if needs_grades:
                # SQL con JOIN para obtener calificaciones Y datos escolares
                sql_query = f"""
                SELECT DISTINCT
                    a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                    de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct,
                    c.id as calificacion_id, c.materia, c.i, c.ii, c.iii, c.promedio
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                LEFT JOIN calificaciones c ON a.id = c.alumno_id
                WHERE {where_clause}
                ORDER BY a.nombre, c.materia
                """
            else:
                # SQL con JOIN para datos escolares (sin calificaciones)
                sql_query = f"""
                SELECT
                    a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                    de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE {where_clause}
                LIMIT 1
                """

            self.logger.debug(f"SQL expandido generado: {sql_query}")
            return sql_query

        except Exception as e:
            self.logger.error(f"Error generando SQL expandido: {e}")
            return None

    def _process_continuation_fallback(self, user_query: str, continuation_info: Dict[str, Any], conversation_stack: list, context=None) -> Optional[InterpretationResult]:
        """🔧 FALLBACK: Usar método tradicional de continuación"""
        try:
            tipo_continuacion = continuation_info.get('tipo_continuacion', 'none')
            nivel_referenciado = continuation_info.get('nivel_referenciado')
            elemento_referenciado = continuation_info.get('elemento_referenciado')

            self.logger.debug(f"Procesando continuación fallback tipo: {tipo_continuacion}")

            if tipo_continuacion == "selection":
                return self._process_selection_continuation(user_query, elemento_referenciado, conversation_stack)
            elif tipo_continuacion == "action":
                return self._process_action_continuation(user_query, nivel_referenciado, conversation_stack, context)
            elif tipo_continuacion == "confirmation":
                return self._process_confirmation_continuation(user_query, conversation_stack)
            elif tipo_continuacion == "specification":
                return self._process_specification_continuation(user_query, conversation_stack)
            elif tipo_continuacion == "analysis":
                return self._process_analysis_continuation(user_query, conversation_stack)
            else:
                self.logger.warning(f"Tipo de continuación no reconocido: {tipo_continuacion}")
                return None

        except Exception as e:
            self.logger.error(f"Error procesando continuación fallback: {e}")
            return None

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
                context += f"- Total elementos: {len(data_items)}\n"
                context += f"- Primeros 3 elementos: {data_items[:3]}\n"

                # 🎯 EXTRAER IDs PARA FILTROS SQL
                ids = []
                for item in data_items:
                    if isinstance(item, dict) and item.get('id'):
                        ids.append(str(item['id']))

                if ids:
                    # 🔧 MOSTRAR TODOS LOS IDs, NO SOLO LOS PRIMEROS 5
                    context += f"- IDs disponibles para filtros SQL: [{', '.join(ids)}]\n"
                    context += f"- Ejemplo SQL con contexto: WHERE a.id IN ({', '.join(ids)})\n"
                    # 🔍 DEBUG: Logging para verificar cuántos IDs se están enviando
                    self.logger.info(f"🔍 DEBUG - Nivel {i}: Enviando {len(ids)} IDs al contexto: {ids[:10]}{'...' if len(ids) > 10 else ''}")

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

    def _process_action_continuation(self, user_query: str, nivel_referenciado: int, conversation_stack: list, context=None) -> Optional[InterpretationResult]:
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
                        # BUSCAR_UNIVERSAL ya filtró correctamente - NO aplicar filtros adicionales
                        filtered_data = result.data

                        # Generar respuesta con datos reales CON CONTEXTO
                        final_response = self._validate_and_generate_response(
                            user_query, new_sql, filtered_data, len(filtered_data), conversation_stack
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

                # 🎯 USAR ENTIDADES DEL MASTER PRIMERO, LUEGO CONTEXTO
                # Usar contexto temporal si está disponible
                context_to_use = context if context else getattr(self, '_temp_context', None)
                alumno_seleccionado = self._identify_student_using_master_entities(context_to_use, conversation_stack)

                if not alumno_seleccionado:
                    self.logger.warning("❌ No se pudo identificar alumno con entidades del Master, usando contexto")
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
                    # Generar respuesta final con los nuevos datos CON CONTEXTO
                    final_response = self._validate_and_generate_response(
                        f"{ultimo_nivel.get('query', '')} (continuación: {user_query})",
                        sql_query, result.data, result.row_count, conversation_stack
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

    def _process_analysis_continuation(self, user_query: str, conversation_stack: list) -> Optional[InterpretationResult]:
        """
        🔍 PROCESA CONTINUACIÓN DE TIPO ANALYSIS

        Para consultas como "de todos ellos quienes tienen calificaciones?"
        que analizan/filtran datos del contexto anterior.
        """
        try:
            self.logger.info("🔍 PROCESANDO CONTINUACIÓN TIPO ANALYSIS")

            # 1. OBTENER DATOS DEL CONTEXTO
            ultimo_nivel = conversation_stack[-1] if conversation_stack else None
            if not ultimo_nivel:
                self.logger.warning("❌ No hay contexto disponible para análisis")
                return None

            # 🎯 OBTENER TODOS LOS DATOS DEL CONTEXTO (no solo la muestra)
            context_data = ultimo_nivel.get('data', [])
            total_context_count = ultimo_nivel.get('row_count', len(context_data))

            # 🚨 PROBLEMA: Solo tenemos muestra de 5, necesitamos todos los datos
            if len(context_data) < total_context_count:
                self.logger.warning(f"⚠️ Solo tengo {len(context_data)} elementos en memoria de {total_context_count} totales")
                self.logger.info("🔄 Necesito obtener todos los datos del contexto desde la base de datos")

                # 🎯 DETECTAR GRADO DEL CONTEXTO AUTOMÁTICAMENTE
                grado = None
                if context_data and len(context_data) > 0:
                    grado = context_data[0].get('grado')

                if grado:
                    # Re-ejecutar consulta para obtener TODOS los datos del grado
                    from app.core.ai.actions import ActionExecutor
                    action_executor = ActionExecutor(self.sql_executor, self)

                    action_request = {
                        "estrategia": "simple",
                        "accion_principal": "LISTAR_POR_CRITERIO",
                        "parametros": {
                            "criterio_campo": "grado",
                            "criterio_valor": str(grado),
                            "filtro_calificaciones": None,
                            "incluir_datos_completos": True
                        },
                        "razonamiento": f"Obtener todos los datos del grado {grado} para análisis completo"
                    }

                    full_data_result = action_executor.execute_action_request(action_request)
                    if full_data_result.get("success", False):
                        context_data = full_data_result.get("data", [])
                        total_context_count = len(context_data)
                        self.logger.info(f"✅ Contexto expandido: {total_context_count} elementos del grado {grado}")
                    else:
                        self.logger.warning("❌ No se pudieron obtener todos los datos del contexto")
                else:
                    self.logger.warning("❌ No se pudo detectar el grado del contexto")

            if not context_data:
                self.logger.warning("❌ No hay datos en el contexto para analizar")
                return None

            self.logger.info(f"📊 Analizando {len(context_data)} elementos del contexto (total: {total_context_count})")

            # 2. USAR SISTEMA DE ACCIONES DIRECTAMENTE
            # Crear ActionExecutor dinámicamente (como en _execute_selected_action)
            from app.core.ai.actions import ActionExecutor
            action_executor = ActionExecutor(self.sql_executor, self)

            # 🎯 DETECTAR FILTROS COMBINADOS PRIMERO
            user_lower = user_query.lower()

            if ("vespertino" in user_lower and
                ("calificaciones" in user_lower or "que tienen calificaciones" in user_lower)):
                # 🎯 FILTRAR POR TURNO VESPERTINO + CALIFICACIONES (desde contexto previo)
                self.logger.info(f"🔍 Filtrando {len(context_data)} estudiantes del contexto por turno vespertino (de los que ya tienen calificaciones)")

                filtered_students = []
                for student in context_data:
                    turno = student.get('turno', '').upper()
                    if turno == 'VESPERTINO':
                        filtered_students.append(student)

                self.logger.info(f"✅ Filtrado completado: {len(filtered_students)} de {len(context_data)} estudiantes son del turno vespertino")

                # 🎯 GENERAR RESPUESTA CONVERSACIONAL
                conversational_response = self._generate_contextual_response(
                    user_query,
                    total_context_count,
                    len(filtered_students),
                    "turno_vespertino_con_calificaciones",
                    conversation_stack
                )

                self.logger.info(f"🎯 Respuesta conversacional generada: {conversational_response[:100]}...")

                # Crear resultado simulando la estructura de ActionExecutor
                action_result = {
                    "success": True,
                    "data": filtered_students,
                    "row_count": len(filtered_students),
                    "action_used": "FILTRAR_POR_TURNO_VESPERTINO_CON_CALIFICACIONES_CONTEXTO",
                    "message": conversational_response,
                    "sql_executed": "-- Filtrado en memoria usando contexto conversacional",
                    "filtro_aplicado": "turno_vespertino_con_calificaciones_contexto"
                }

            elif ("matutino" in user_lower and
                  ("calificaciones" in user_lower or "que tienen calificaciones" in user_lower)):
                # 🎯 FILTRAR POR TURNO MATUTINO + CALIFICACIONES (desde contexto previo)
                self.logger.info(f"🔍 Filtrando {len(context_data)} estudiantes del contexto por turno matutino (de los que ya tienen calificaciones)")

                filtered_students = []
                for student in context_data:
                    turno = student.get('turno', '').upper()
                    if turno == 'MATUTINO':
                        filtered_students.append(student)

                self.logger.info(f"✅ Filtrado completado: {len(filtered_students)} de {len(context_data)} estudiantes son del turno matutino")

                # 🎯 GENERAR RESPUESTA CONVERSACIONAL
                conversational_response = self._generate_contextual_response(
                    user_query,
                    total_context_count,
                    len(filtered_students),
                    "turno_matutino_con_calificaciones",
                    conversation_stack
                )

                self.logger.info(f"🎯 Respuesta conversacional generada: {conversational_response[:100]}...")

                # Crear resultado simulando la estructura de ActionExecutor
                action_result = {
                    "success": True,
                    "data": filtered_students,
                    "row_count": len(filtered_students),
                    "action_used": "FILTRAR_POR_TURNO_MATUTINO_CON_CALIFICACIONES_CONTEXTO",
                    "message": conversational_response,
                    "sql_executed": "-- Filtrado en memoria usando contexto conversacional",
                    "filtro_aplicado": "turno_matutino_con_calificaciones_contexto"
                }

            # 🚀 FILTRO DINÁMICO UNIVERSAL - ÚNICA IMPLEMENTACIÓN
            self.logger.info(f"🚀 Aplicando filtro dinámico para: {user_query}")

            # Extraer criterios usando LLM
            filter_criteria = self._extract_filter_criteria_with_llm(user_query, context_data)

            if filter_criteria and filter_criteria.get('tiene_filtros', False):
                # Aplicar filtro dinámico
                filtered_students = self._apply_dynamic_filter(context_data, filter_criteria)

                self.logger.info(f"✅ Filtro dinámico completado: {len(filtered_students)} de {len(context_data)} estudiantes cumplen los criterios")

                # Generar respuesta conversacional dinámica
                conversational_response = self._generate_dynamic_filter_response(
                    user_query,
                    total_context_count,
                    len(filtered_students),
                    filter_criteria,
                    conversation_stack
                )

                # Crear resultado con filtro dinámico aplicado
                action_result = {
                    "success": True,
                    "data": filtered_students,
                    "row_count": len(filtered_students),
                    "action_used": "FILTRAR_CONTEXTO_DINÁMICO",
                    "message": conversational_response,
                    "sql_executed": "-- Filtro dinámico aplicado en memoria usando LLM",
                    "filtro_aplicado": "filtro_dinamico_contexto"
                }
            else:
                # No se detectaron filtros válidos - usar contexto completo
                self.logger.warning(f"⚠️ No se detectaron criterios de filtro válidos para: {user_query}")
                filtered_students = context_data

                conversational_response = self._generate_contextual_response(
                    user_query,
                    total_context_count,
                    len(filtered_students),
                    "sin_filtro",
                    conversation_stack
                )

                action_result = {
                    "success": True,
                    "data": filtered_students,
                    "row_count": len(filtered_students),
                    "action_used": "SIN_FILTRO_CONTEXTO",
                    "message": conversational_response,
                    "sql_executed": "-- Sin filtro aplicado, usando contexto completo",
                    "filtro_aplicado": "sin_filtro_contexto"
                }

            if not action_result.get("success", False):
                self.logger.warning(f"❌ Acción falló: {action_result.get('message', 'Error desconocido')}")
                return None

            # 3. GENERAR RESULTADO CON RESPUESTA CONVERSACIONAL Y ACTUALIZAR CONTEXTO
            filtered_data = action_result.get("data", [])
            filtered_count = action_result.get("row_count", 0)

            # 🎯 ACTUALIZAR CONTEXTO CONVERSACIONAL PARA PRÓXIMAS CONTINUACIONES
            new_context_data = {
                "espera_continuacion": True,  # Permitir más continuaciones
                "tipo_esperado": "analysis",
                "datos_recordar": {
                    "query": user_query,  # La consulta actual, no la original
                    "data": filtered_data[:5] if filtered_count > 5 else filtered_data,
                    "row_count": filtered_count,
                    "context": f"Lista de {filtered_count} alumnos filtrada disponible",
                    "filter_applied": action_result.get("filtro_aplicado", "filtro_contexto")
                },
                "razonamiento": f"Filtré la lista anterior. El usuario podría querer aplicar más filtros a estos {filtered_count} resultados."
            }

            return InterpretationResult(
                action="consulta_sql_exitosa",
                parameters={
                    "sql_query": action_result.get("sql_executed", ""),
                    "data": filtered_data,
                    "row_count": filtered_count,
                    "message": action_result.get("message", "Análisis completado"),
                    "human_response": action_result.get("message", "Análisis completado"),  # 🎯 USAR RESPUESTA CONVERSACIONAL
                    "auto_reflexion": new_context_data,  # 🎯 CONTEXTO ACTUALIZADO
                    "flow_type": "analysis_continuation",
                    "action_used": action_result.get("action_used", "ANALYSIS"),
                    "action_strategy": "context_analysis"
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error procesando análisis de continuación: {e}")
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

            # 🧠 DETECTAR SI ES CONSULTA DE SEGUIMIENTO
            is_follow_up = self._is_follow_up_query(user_query) and len(conversation_stack) > 0

            # 🔍 DEBUG: Logging de detección de seguimiento
            self.logger.info(f"🔍 DEBUG - _generate_initial_query_response:")
            self.logger.info(f"   - Query: '{user_query}'")
            self.logger.info(f"   - is_follow_up: {is_follow_up}")
            self.logger.info(f"   - conversation_stack length: {len(conversation_stack)}")
            self.logger.info(f"   - _is_follow_up_query result: {self._is_follow_up_query(user_query)}")

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

                    # Generar respuesta para conteo
                    if "turno matutino" in user_lower:
                        response = f"🌄 En el turno matutino hay **{cantidad} alumnos** inscritos."
                    elif "turno vespertino" in user_lower:
                        response = f"🌅 En el turno vespertino hay **{cantidad} alumnos** inscritos."
                    elif "grado" in user_lower:
                        response = f"📚 Se encontraron **{cantidad} alumnos** que cumplen con el criterio de grado especificado."
                    elif "total" in user_lower or "cuántos" in user_lower:
                        response = f"🏫 La escuela tiene un total de **{cantidad} alumnos** inscritos."
                    else:
                        response = f"📊 Total de alumnos encontrados: **{cantidad}**"

                    # Agregar sugerencia útil
                    if cantidad > 0:
                        response += f"\n\n💡 Si necesitas ver la lista de estos alumnos, puedes preguntarme: 'muéstrame los alumnos del turno matutino'"

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

    # 🗑️ MÉTODO ELIMINADO: _detect_specific_student_intention
    # RAZÓN: Ahora usamos información consolidada del Master Prompt
    # La categorización específica viene directamente del Master

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

    def _generate_sql_with_strategy_centralized(self, user_query: str, conversation_context: str = "") -> Optional[str]:
        """
        PROMPT 2 CENTRALIZADO: Genera estrategia + SQL en un solo paso CON CONTEXTO CONVERSACIONAL
        REEMPLAZA: _generate_sql_with_strategy() (método eliminado)
        """
        try:
            # 🎯 USAR PROMPT MANAGER CENTRALIZADO CON CONTEXTO CONVERSACIONAL
            combined_prompt = self.prompt_manager.get_sql_generation_prompt(user_query, conversation_context)

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

    def _validate_and_generate_response(self, user_query: str, sql_query: str, data: List[Dict], row_count: int, conversation_stack: list = None) -> Optional[Dict]:
        """
        PROMPT 3 SIMPLIFICADO: BUSCAR_UNIVERSAL ya hizo el trabajo, solo generar respuesta
        CON CONTEXTO CONVERSACIONAL para respuestas de seguimiento
        """
        try:
            # 🎯 BUSCAR_UNIVERSAL YA FILTRÓ CORRECTAMENTE - NO APLICAR FILTROS ADICIONALES
            filtered_data = data

            self.logger.info(f"✅ BUSCAR_UNIVERSAL completado:")
            self.logger.info(f"   - Datos obtenidos: {len(data)} registros")
            self.logger.info(f"   - Acción: BUSCAR_UNIVERSAL (sin filtros adicionales)")
            self.logger.info(f"   - Datos finales: {len(filtered_data)} registros")
            self.logger.info(f"   - Estado: Consulta resuelta correctamente")

            # BUSCAR_UNIVERSAL siempre resuelve la consulta correctamente
            # No aplicar filtros adicionales que puedan interferir

            # Usar los datos filtrados para el resto del proceso
            final_data = filtered_data
            final_row_count = len(filtered_data)

            # 🎯 AUTO-REFLEXIÓN INTELIGENTE SIN LLM EXTRA (rápida y efectiva)
            self.logger.info(f"🧠 Generando auto-reflexión inteligente para {final_row_count} resultados...")

            # Determinar si espera continuación basado en el tipo de consulta y resultados
            espera_continuacion, tipo_esperado, nota_estrategica = self._determine_continuation_expectation(
                user_query, final_row_count, final_data
            )

            # 🎯 GENERAR RESPUESTA CONVERSACIONAL CON CONTEXTO CORRECTO
            # USAR conversation_stack pasado como parámetro (viene del MessageProcessor)
            # self.conversation_stack NO EXISTE en StudentQueryInterpreter
            context_stack = conversation_stack if conversation_stack is not None else []

            # 🔍 DEBUG: Verificar que el context_stack tenga datos
            self.logger.info(f"🔍 DEBUG - _validate_and_generate_response:")
            self.logger.info(f"   - conversation_stack recibido: {len(conversation_stack) if conversation_stack else 0} niveles")
            self.logger.info(f"   - context_stack final: {len(context_stack)} niveles")

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
            user_lower = user_query.lower()

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
- FILTRAR: 'de esos los de segundo grado', 'del turno matutino'
- ESTADÍSTICAS: 'cuántos son por grado', 'estadísticas de ese grupo'
- CONSTANCIA: 'constancia para [criterio específico]'
- ANÁLISIS: 'distribución por turnos'
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

            # Consultas específicas cerradas
            consultas_cerradas = ['cuántos', 'total', 'estadística', 'promedio', 'suma']
            if any(keyword in user_lower for keyword in consultas_cerradas):
                nota_estrategica = f"""Consulta específica resuelta ({row_count} como resultado). Usuario probablemente:
- SATISFECHO: con la información numérica/estadística
- PODRÍA: hacer nueva consulta independiente
- MENOS PROBABLE: continuación sobre este resultado"""
                return (False, "none", nota_estrategica)

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

    # 🗑️ MÉTODO DUPLICADO ELIMINADO: _parse_intention_response()
    # RAZÓN: Ya existe una versión idéntica arriba (línea 976)
    # MANTENER: Solo la primera versión



    # 🗑️ MÉTODO ELIMINADO: _intelligent_final_filter()
    # RAZÓN: Aplicaba filtros redundantes después de BUSCAR_UNIVERSAL
    # BUSCAR_UNIVERSAL ya hace todo el trabajo correctamente

    # 🗑️ MÉTODO ELIMINADO: _apply_multi_criteria_filter()
    # RAZÓN: También aplicaba filtros redundantes después de BUSCAR_UNIVERSAL
    # BUSCAR_UNIVERSAL ya maneja múltiples criterios correctamente

    # 🗑️ MÉTODO ELIMINADO: _extract_filter_criteria_with_llm_enhanced()
    # RAZÓN: Parte del sistema de filtros redundantes eliminado
    # BUSCAR_UNIVERSAL ya maneja criterios complejos correctamente

    # 🗑️ MÉTODO ELIMINADO: _normalize_criteria_with_db_info()
    # RAZÓN: Parte del sistema de filtros redundantes eliminado

    # 🗑️ MÉTODOS ELIMINADOS: _parse_filter_response() y _apply_filter_decision()
    # RAZÓN: Parte del sistema de filtros redundantes eliminado
    # BUSCAR_UNIVERSAL ya maneja todo correctamente












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

    # 🗑️ CÓDIGO OBSOLETO ELIMINADO COMPLETAMENTE
    # El método _process_constancia_request fue reemplazado por _process_constancia_as_direct_action
    # que es más eficiente y elimina duplicación de código


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

                # 🎯 USAR MENSAJE SIMPLE - DEJAR QUE EL MASTER GENERE EL MENSAJE CONVERSACIONAL
                return InterpretationResult(
                    action="transformation_preview",
                    parameters={
                        "message": f"Vista previa de transformación generada",  # ← MENSAJE SIMPLE
                        "data": data,
                        "files": [data.get("ruta_archivo")] if data.get("ruta_archivo") else [],
                        "alumno": alumno_info,
                        "tipo_constancia": tipo_constancia,
                        "transformation_info": {
                            "original_pdf": pdf_panel.original_pdf,
                            "transformed_pdf": data.get("ruta_archivo"),
                            "tipo_transformacion": tipo_constancia,
                            "alumno": alumno_info  # ← AGREGAR ALUMNO AQUÍ TAMBIÉN
                        }
                    },
                    confidence=0.95
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

    # ✅ SISTEMA DE MEMORIA ELIMINADO - USAR SOLO FLUJO PRINCIPAL DE 4 PROMPTS

    # 🚀 MÉTODOS DE FILTRO DINÁMICO UNIVERSAL - NUEVA FUNCIONALIDAD REVOLUCIONARIA

    def _extract_filter_criteria_with_llm(self, user_query: str, context_data: List[Dict]) -> Optional[Dict[str, Any]]:
        """
        🧠 EXTRAE CRITERIOS DE FILTRO USANDO LLM ESPECIALIZADO
        MANTIENE FILOSOFÍA: LLM ELIGE HERRAMIENTAS (ahora para filtros)

        Args:
            user_query: Consulta del usuario (ej: "del grupo A con promedio mayor a 8")
            context_data: Datos del contexto para analizar campos disponibles

        Returns:
            Dict con criterios extraídos o None si no hay filtros
        """
        try:
            # Obtener campos disponibles del contexto
            available_fields = []
            if context_data:
                sample_student = context_data[0]
                available_fields = list(sample_student.keys())

            # Crear prompt especializado para extracción de criterios
            filter_prompt = f"""
TAREA: Extraer criterios de filtro de la consulta del usuario.

CONSULTA DEL USUARIO: "{user_query}"

CAMPOS DISPONIBLES EN LOS DATOS:
{available_fields}

CAMPOS ESPECIALES CALCULADOS:
- promedio_general: Promedio de todas las materias (calculado dinámicamente)
- matematicas_promedio: Promedio solo de matemáticas (calculado dinámicamente)
- español_promedio: Promedio solo de español (calculado dinámicamente)
- espanol_promedio: Promedio solo de español (calculado dinámicamente)

OPERADORES SOPORTADOS:
- igual: Igualdad exacta
- diferente: No igual
- mayor_que: Valor numérico mayor
- menor_que: Valor numérico menor
- entre: Valor entre dos números
- contiene: Texto que contiene substring
- empieza_con: Texto que empieza con
- termina_con: Texto que termina con

EXTRAE los criterios en formato JSON:
{{
    "tiene_filtros": true|false,
    "criterios": [
        {{"campo": "grupo", "operador": "igual", "valor": "A"}},
        {{"campo": "promedio_general", "operador": "mayor_que", "valor": 8.0}},
        {{"campo": "turno", "operador": "igual", "valor": "MATUTINO"}}
    ],
    "logica": "AND"
}}

EJEMPLOS DE EXTRACCIÓN:
- "del grupo A" → {{"campo": "grupo", "operador": "igual", "valor": "A"}}
- "con promedio mayor a 8" → {{"campo": "promedio_general", "operador": "mayor_que", "valor": 8.0}}
- "buenos en matemáticas" → {{"campo": "matematicas_promedio", "operador": "mayor_que", "valor": 7.5}}
- "del turno matutino" → {{"campo": "turno", "operador": "igual", "valor": "MATUTINO"}}
- "nacidos en 2017" → {{"campo": "fecha_nacimiento", "operador": "contiene", "valor": "2017"}}

IMPORTANTE:
- Si no detectas filtros claros, devuelve "tiene_filtros": false
- Convierte valores a tipos apropiados (números para promedios, texto en mayúsculas para campos como turno/grupo)
- Para promedios académicos, usa umbrales razonables (7.5+ para "buenos", 8.5+ para "excelentes")
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(filter_prompt)

            if response:
                # Parsear respuesta JSON
                filter_criteria = self._parse_json_response(response)

                if filter_criteria:
                    self.logger.info(f"🧠 Criterios extraídos: {filter_criteria}")
                    return filter_criteria
                else:
                    self.logger.warning("❌ No se pudo parsear respuesta de criterios")
                    return {"tiene_filtros": False}
            else:
                self.logger.warning("❌ No se recibió respuesta del LLM para extracción de criterios")
                return {"tiene_filtros": False}

        except Exception as e:
            self.logger.error(f"Error extrayendo criterios con LLM: {e}")
            return {"tiene_filtros": False}

    def _apply_dynamic_filter(self, students: List[Dict], filter_criteria: Dict[str, Any]) -> List[Dict]:
        """
        🔧 APLICADOR UNIVERSAL DE FILTROS DINÁMICOS
        FUNCIONA CON CUALQUIER CAMPO Y OPERADOR

        Args:
            students: Lista de estudiantes a filtrar
            filter_criteria: Criterios extraídos por LLM

        Returns:
            Lista filtrada de estudiantes
        """
        try:
            if not filter_criteria.get('tiene_filtros', False):
                return students

            criterios = filter_criteria.get('criterios', [])
            logica = filter_criteria.get('logica', 'AND')

            filtered_students = []

            for student in students:
                if self._meets_all_criteria(student, criterios, logica):
                    filtered_students.append(student)

            self.logger.info(f"🔧 Filtro aplicado: {len(filtered_students)}/{len(students)} estudiantes cumplen criterios")
            return filtered_students

        except Exception as e:
            self.logger.error(f"Error aplicando filtro dinámico: {e}")
            return students  # Devolver datos originales en caso de error

    def _meets_all_criteria(self, student: Dict, criterios: List[Dict], logica: str = 'AND') -> bool:
        """
        🎯 EVALÚA SI UN ESTUDIANTE CUMPLE TODOS LOS CRITERIOS

        Args:
            student: Datos del estudiante
            criterios: Lista de criterios a evaluar
            logica: 'AND' o 'OR'

        Returns:
            True si cumple los criterios según la lógica especificada
        """
        try:
            if not criterios:
                return True

            results = []

            for criterio in criterios:
                result = self._evaluate_single_criterion(student, criterio)
                results.append(result)

            # Aplicar lógica AND/OR
            if logica.upper() == 'AND':
                return all(results)
            else:  # OR
                return any(results)

        except Exception as e:
            self.logger.error(f"Error evaluando criterios: {e}")
            return False

    def _evaluate_single_criterion(self, student: Dict, criterio: Dict) -> bool:
        """
        🔍 EVALÚA UN CRITERIO ESPECÍFICO DINÁMICAMENTE

        Args:
            student: Datos del estudiante
            criterio: Criterio individual a evaluar

        Returns:
            True si el estudiante cumple el criterio
        """
        try:
            campo = criterio.get('campo', '')
            operador = criterio.get('operador', 'igual')
            valor_esperado = criterio.get('valor', '')

            # Obtener valor del estudiante
            if campo == "promedio_general":
                student_value = self._calculate_general_average(student)
            elif campo.endswith("_promedio"):  # matematicas_promedio, español_promedio
                materia = campo.replace("_promedio", "").upper()
                if materia == "ESPANOL":
                    materia = "ESPAÑOL"  # Normalizar
                student_value = self._get_subject_average(student, materia)
            else:
                student_value = student.get(campo, "")

            # Aplicar operador
            if operador == "igual":
                return str(student_value).upper() == str(valor_esperado).upper()
            elif operador == "diferente":
                return str(student_value).upper() != str(valor_esperado).upper()
            elif operador == "mayor_que":
                try:
                    return float(student_value) > float(valor_esperado)
                except (ValueError, TypeError):
                    return False
            elif operador == "menor_que":
                try:
                    return float(student_value) < float(valor_esperado)
                except (ValueError, TypeError):
                    return False
            elif operador == "entre":
                try:
                    if isinstance(valor_esperado, list) and len(valor_esperado) == 2:
                        min_val, max_val = valor_esperado
                        return float(min_val) <= float(student_value) <= float(max_val)
                    return False
                except (ValueError, TypeError):
                    return False
            elif operador == "contiene":
                return str(valor_esperado).upper() in str(student_value).upper()
            elif operador == "empieza_con":
                return str(student_value).upper().startswith(str(valor_esperado).upper())
            elif operador == "termina_con":
                return str(student_value).upper().endswith(str(valor_esperado).upper())
            else:
                self.logger.warning(f"Operador no reconocido: {operador}")
                return False

        except Exception as e:
            self.logger.error(f"Error evaluando criterio {criterio}: {e}")
            return False

    def _calculate_general_average(self, student: Dict) -> float:
        """
        📊 CALCULA PROMEDIO GENERAL DE TODAS LAS MATERIAS

        Args:
            student: Datos del estudiante

        Returns:
            Promedio general o 0.0 si no hay calificaciones
        """
        try:
            calificaciones_str = student.get('calificaciones', '')
            if not calificaciones_str or calificaciones_str in ['', '[]']:
                return 0.0

            import json
            calificaciones = json.loads(calificaciones_str)

            if not calificaciones:
                return 0.0

            total_promedio = 0.0
            materias_count = 0

            for materia in calificaciones:
                promedio = materia.get('promedio', 0)
                if promedio > 0:
                    total_promedio += promedio
                    materias_count += 1

            return total_promedio / materias_count if materias_count > 0 else 0.0

        except Exception as e:
            self.logger.error(f"Error calculando promedio general: {e}")
            return 0.0

    def _get_subject_average(self, student: Dict, materia_nombre: str) -> float:
        """
        📚 OBTIENE PROMEDIO DE UNA MATERIA ESPECÍFICA

        Args:
            student: Datos del estudiante
            materia_nombre: Nombre de la materia (ej: "MATEMATICAS", "ESPAÑOL")

        Returns:
            Promedio de la materia o 0.0 si no existe
        """
        try:
            calificaciones_str = student.get('calificaciones', '')
            if not calificaciones_str or calificaciones_str in ['', '[]']:
                return 0.0

            import json
            calificaciones = json.loads(calificaciones_str)

            # Buscar la materia específica
            for materia in calificaciones:
                nombre_materia = materia.get('nombre', '').upper()

                # Coincidencia exacta o parcial
                if (materia_nombre.upper() in nombre_materia or
                    nombre_materia in materia_nombre.upper()):
                    return materia.get('promedio', 0.0)

            return 0.0

        except Exception as e:
            self.logger.error(f"Error obteniendo promedio de {materia_nombre}: {e}")
            return 0.0



    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        🔧 PARSEA RESPUESTA JSON DEL LLM

        Args:
            response: Respuesta del LLM

        Returns:
            Dict parseado o None si falla
        """
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
                        parsed_json = json.loads(matches[0])
                        return parsed_json
                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON, intentar parsear directamente
            try:
                parsed_json = json.loads(clean_response)
                return parsed_json
            except json.JSONDecodeError:
                return None

        except Exception as e:
            self.logger.error(f"Error parseando JSON: {e}")
            return None

    def _generate_follow_up_response(self, user_query: str, row_count: int,
                                   data: List[Dict], conversation_stack: list) -> str:
        """
        🎯 GENERA RESPUESTA ESPECÍFICA PARA CONSULTAS DE SEGUIMIENTO

        Args:
            user_query: Consulta del usuario
            row_count: Cantidad de resultados actuales
            data: Datos encontrados
            conversation_stack: Pila conversacional

        Returns:
            Respuesta conversacional que hace referencia al contexto anterior
        """
        try:
            # Obtener información del contexto anterior
            ultimo_nivel = conversation_stack[-1] if conversation_stack else {}
            consulta_anterior = ultimo_nivel.get('query', 'la consulta anterior')
            total_anterior = ultimo_nivel.get('row_count', 0)

            # Extraer criterios de la consulta actual
            user_lower = user_query.lower()

            # 🧠 USAR SISTEMA LLM INTELIGENTE PARA DETECTAR FILTROS
            filtros_detectados = []

            # Usar el sistema LLM existente para extracción inteligente
            filter_criteria = self._extract_filter_criteria_with_llm(user_query, data)

            if filter_criteria and filter_criteria.get('tiene_filtros', False):
                criterios = filter_criteria.get('criterios', [])
                for criterio in criterios:
                    campo = criterio.get('campo', '')
                    valor = criterio.get('valor', '')
                    operador = criterio.get('operador', '')

                    # Convertir criterios LLM a descripciones amigables
                    if campo == 'grado':
                        filtros_detectados.append(f'{valor}° grado')
                    elif campo == 'grupo':
                        filtros_detectados.append(f'grupo {valor}')
                    elif campo == 'turno':
                        filtros_detectados.append(f'turno {valor.lower()}')
                    elif campo == 'promedio_general' and operador == 'mayor_que':
                        filtros_detectados.append('promedio alto')
                    elif campo == 'promedio_general' and operador == 'menor_que':
                        filtros_detectados.append('promedio bajo')
                    elif 'calificaciones' in campo:
                        filtros_detectados.append('con calificaciones')
                    else:
                        # Descripción genérica para otros criterios
                        filtros_detectados.append(f'{campo}: {valor}')

            # 🔍 DEBUG: Logging de filtros detectados
            self.logger.info(f"🔍 DEBUG - Filtros detectados en '{user_query}': {filtros_detectados}")
            self.logger.info(f"🔍 DEBUG - Contexto anterior: '{consulta_anterior}' con {total_anterior} elementos")

            # 🎯 GENERAR RESPUESTA CONTEXTUAL
            if filtros_detectados:
                filtros_texto = ' y '.join(filtros_detectados)

                if row_count == total_anterior:
                    response = f"De los **{total_anterior} estudiantes** de {self._extract_context_description(consulta_anterior)}, **todos ({row_count}) estudian en {filtros_texto}**. ✅"
                elif row_count > 0:
                    otros = total_anterior - row_count
                    response = f"De los **{total_anterior} estudiantes** de {self._extract_context_description(consulta_anterior)}, encontré que **{row_count} estudian en {filtros_texto}** y {otros} en otros turnos/grupos. 🔍"
                else:
                    response = f"De los **{total_anterior} estudiantes** de {self._extract_context_description(consulta_anterior)}, **ninguno estudia en {filtros_texto}**. 🤔"
            else:
                # Filtro genérico
                if row_count > 0:
                    response = f"De los **{total_anterior} estudiantes** de {self._extract_context_description(consulta_anterior)}, **{row_count} cumplen con los criterios** que especificaste. ✅"
                else:
                    response = f"De los **{total_anterior} estudiantes** de {self._extract_context_description(consulta_anterior)}, **ninguno cumple con los criterios** especificados. 🤔"

            # Agregar sugerencias contextuales
            if row_count > 0:
                if row_count == 1:
                    response += "\n\n¿Te gustaría generar una constancia para este alumno? 📄"
                elif row_count <= 5:
                    response += "\n\n¿Necesitas más información sobre alguno de estos alumnos o quieres aplicar más filtros? 🤔"
                else:
                    response += "\n\n¿Quieres que filtre más esta lista o necesitas información específica de algún alumno? 🔍"
            else:
                response += "\n\n¿Te ayudo con otra consulta o quieres probar con criterios diferentes? 💭"

            return response

        except Exception as e:
            self.logger.error(f"Error generando respuesta de seguimiento: {e}")
            # Fallback a respuesta básica
            return f"✅ Encontré {row_count} alumnos que cumplen con los criterios especificados."

    def _extract_context_description(self, consulta_anterior: str) -> str:
        """
        🔍 EXTRAE DESCRIPCIÓN AMIGABLE DEL CONTEXTO ANTERIOR (MEJORADO)

        Args:
            consulta_anterior: Consulta anterior del usuario

        Returns:
            Descripción amigable del contexto
        """
        try:
            consulta_lower = consulta_anterior.lower()
            descripcion_partes = []

            # Detectar año de nacimiento
            for word in consulta_anterior.split():
                if word.isdigit() and len(word) == 4:
                    return f"estudiantes nacidos en {word}"

            # 🧠 USAR SISTEMA LLM INTELIGENTE PARA EXTRAER DESCRIPCIÓN
            # Crear datos dummy para el LLM (solo necesitamos los campos)
            dummy_data = [{'grado': 1, 'grupo': 'A', 'turno': 'MATUTINO', 'nombre': 'DUMMY'}]

            # Usar el sistema LLM para extraer criterios de la consulta anterior
            filter_criteria = self._extract_filter_criteria_with_llm(consulta_anterior, dummy_data)

            if filter_criteria and filter_criteria.get('tiene_filtros', False):
                criterios = filter_criteria.get('criterios', [])
                for criterio in criterios:
                    campo = criterio.get('campo', '')
                    valor = criterio.get('valor', '')

                    # Convertir criterios a descripciones amigables
                    if campo == 'grado':
                        descripcion_partes.append(f"{valor}° grado")
                    elif campo == 'grupo':
                        descripcion_partes.append(f"grupo {valor}")
                    elif campo == 'turno':
                        descripcion_partes.append(f"turno {valor.lower()}")
                    elif campo == 'nombre':
                        descripcion_partes.append(f"apellido {valor}")

            # Fallback: detectar patrones simples si el LLM no encuentra nada
            if not descripcion_partes:
                # Solo patrones muy específicos y seguros
                if 'garcia' in consulta_lower:
                    descripcion_partes.append("apellido García")
                elif 'martinez' in consulta_lower:
                    descripcion_partes.append("apellido Martínez")
                elif 'lopez' in consulta_lower:
                    descripcion_partes.append("apellido López")

            # Construir descripción final
            if descripcion_partes:
                return " ".join(descripcion_partes)
            else:
                return "la consulta anterior"

        except Exception as e:
            self.logger.error(f"Error extrayendo descripción del contexto: {e}")
            return "la consulta anterior"

    def _generate_specific_context_response(self, user_query: str, row_count: int, data: List[Dict]) -> str:
        """
        🎯 GENERA RESPUESTA ESPECÍFICA BASADA EN EL CONTEXTO DE LA CONSULTA

        Args:
            user_query: Consulta del usuario
            row_count: Cantidad de resultados
            data: Datos encontrados

        Returns:
            Respuesta específica con contexto detectado
        """
        try:
            user_lower = user_query.lower()

            # 🎯 DETECTAR AÑO DE NACIMIENTO
            año_detectado = None
            for word in user_query.split():
                if word.isdigit() and len(word) == 4 and word.startswith('20'):
                    año_detectado = word
                    break

            if año_detectado:
                return f"Encontré **{row_count} estudiantes nacidos en {año_detectado}**. 📅"

            # 🎯 DETECTAR MÚLTIPLES CRITERIOS COMBINADOS (GRADO + GRUPO + TURNO)
            criterios_detectados = []

            # Detectar grado
            if "grado" in user_lower or any(g in user_lower for g in ["1er", "2do", "3er", "4to", "5to", "6to"]):
                grado_detectado = "ese grado"
                for palabra in user_lower.split():
                    if "primer" in palabra or "1" in palabra:
                        grado_detectado = "primer grado"
                    elif "segundo" in palabra or "2" in palabra:
                        grado_detectado = "segundo grado"
                    elif "tercer" in palabra or "3" in palabra:
                        grado_detectado = "tercer grado"
                    elif "cuarto" in palabra or "4" in palabra:
                        grado_detectado = "cuarto grado"
                    elif "quinto" in palabra or "5" in palabra:
                        grado_detectado = "quinto grado"
                    elif "sexto" in palabra or "6" in palabra:
                        grado_detectado = "sexto grado"
                criterios_detectados.append(grado_detectado)

            # Detectar grupo específico (CORREGIDO: más específico)
            if "grupo a" in user_lower:
                criterios_detectados.append("grupo A")
            elif "grupo b" in user_lower:
                criterios_detectados.append("grupo B")
            elif "grupo c" in user_lower:
                criterios_detectados.append("grupo C")
            # Solo detectar letras aisladas si están claramente referenciando grupos
            elif re.search(r'\bgrupo\s+[abc]\b', user_lower):
                match = re.search(r'\bgrupo\s+([abc])\b', user_lower)
                if match:
                    criterios_detectados.append(f"grupo {match.group(1).upper()}")

            # Detectar turno
            if "vespertino" in user_lower:
                criterios_detectados.append("turno vespertino")
            elif "matutino" in user_lower:
                criterios_detectados.append("turno matutino")

            # Si se detectaron criterios múltiples, generar respuesta combinada
            if criterios_detectados:
                if len(criterios_detectados) == 1:
                    return f"Encontré **{row_count} alumnos de {criterios_detectados[0]}**. 🎓"
                else:
                    criterios_texto = " del ".join(criterios_detectados)
                    return f"Encontré **{row_count} alumnos de {criterios_texto}**. 🎓"

            # 🎯 DETECTAR TURNO INDIVIDUAL (solo si no se detectaron criterios múltiples arriba)
            if "vespertino" in user_lower:
                self.logger.info(f"🔍 DEBUG - _generate_specific_context_response: Detectado turno vespertino individual")
                return f"Encontré **{row_count} estudiantes del turno vespertino**. 🌇"
            elif "matutino" in user_lower:
                self.logger.info(f"🔍 DEBUG - _generate_specific_context_response: Detectado turno matutino individual")
                return f"Encontré **{row_count} estudiantes del turno matutino**. 🌅"

            # 🎯 DETECTAR PROMEDIO (PRIORIDAD ALTA)
            if "promedio" in user_lower:
                if "mayor" in user_lower or ">" in user_lower:
                    # Extraer número
                    import re
                    numbers = re.findall(r'\d+(?:\.\d+)?', user_lower)
                    if numbers:
                        valor = numbers[0]
                        return f"Encontré **{row_count} estudiantes con promedio mayor a {valor}**. 📊"
                elif "menor" in user_lower or "<" in user_lower:
                    import re
                    numbers = re.findall(r'\d+(?:\.\d+)?', user_lower)
                    if numbers:
                        valor = numbers[0]
                        return f"Encontré **{row_count} estudiantes con promedio menor a {valor}**. 📊"
                else:
                    return f"Encontré **{row_count} estudiantes** según el criterio de promedio especificado. 📊"

            # 🎯 DETECTAR GRUPO (PRIORIDAD MENOR)
            if "grupo a" in user_lower and "promedio" not in user_lower:
                return f"Encontré **{row_count} estudiantes del grupo A**. 📚"
            elif "grupo b" in user_lower and "promedio" not in user_lower:
                return f"Encontré **{row_count} estudiantes del grupo B**. 📚"
            elif "grupo c" in user_lower and "promedio" not in user_lower:
                return f"Encontré **{row_count} estudiantes del grupo C**. 📚"

            # 🎯 DETECTAR BÚSQUEDA POR NOMBRE
            if any(keyword in user_lower for keyword in ["nombre", "llamado", "llama"]):
                return f"Encontré **{row_count} estudiantes** que coinciden con el nombre especificado. 👤"

            # 🎯 DETECTAR BÚSQUEDA POR CALIFICACIONES CON CRITERIOS ESPECÍFICOS
            if any(keyword in user_lower for keyword in ["calificaciones", "notas", "promedio", "buenos"]):
                # Extraer criterios específicos de la consulta
                criterios_detectados = []

                # Detectar grado
                for grado in ["1", "2", "3", "4", "5", "6"]:
                    if f"{grado}do" in user_lower or f"grado {grado}" in user_lower:
                        criterios_detectados.append(f"{grado}° grado")
                        break

                # Detectar grupo (CORREGIDO: más específico)
                if "grupo a" in user_lower:
                    criterios_detectados.append("grupo A")
                elif "grupo b" in user_lower:
                    criterios_detectados.append("grupo B")
                elif "grupo c" in user_lower:
                    criterios_detectados.append("grupo C")
                # Solo detectar letras aisladas si están claramente referenciando grupos
                elif re.search(r'\bgrupo\s+[abc]\b', user_lower):
                    match = re.search(r'\bgrupo\s+([abc])\b', user_lower)
                    if match:
                        criterios_detectados.append(f"grupo {match.group(1).upper()}")

                # Detectar turno
                if "matutino" in user_lower:
                    criterios_detectados.append("turno matutino")
                elif "vespertino" in user_lower:
                    criterios_detectados.append("turno vespertino")

                # Detectar estado de calificaciones
                if "sin calificaciones" in user_lower or "no tengan calificaciones" in user_lower:
                    criterios_detectados.append("sin calificaciones registradas")
                elif "con calificaciones" in user_lower or "tengan calificaciones" in user_lower:
                    criterios_detectados.append("con calificaciones registradas")

                # Construir respuesta específica
                if criterios_detectados:
                    criterios_texto = ", ".join(criterios_detectados)
                    return f"Encontré **{row_count} estudiantes de {criterios_texto}**. 📊"
                else:
                    return f"Encontré **{row_count} estudiantes** que cumplen con los criterios de calificaciones. 📊"

            # 🎯 FALLBACK GENÉRICO MEJORADO
            # Intentar extraer criterios básicos para respuesta más específica
            criterios_basicos = []

            # Detectar grado en fallback
            for grado in ["1", "2", "3", "4", "5", "6"]:
                if f"{grado}do" in user_lower or f"grado {grado}" in user_lower:
                    criterios_basicos.append(f"{grado}° grado")
                    break

            # Detectar grupo en fallback (CORREGIDO: más específico)
            if "grupo a" in user_lower:
                criterios_basicos.append("grupo A")
            elif "grupo b" in user_lower:
                criterios_basicos.append("grupo B")
            elif "grupo c" in user_lower:
                criterios_basicos.append("grupo C")
            # Solo detectar letras aisladas si están claramente referenciando grupos
            elif re.search(r'\bgrupo\s+[abc]\b', user_lower):
                match = re.search(r'\bgrupo\s+([abc])\b', user_lower)
                if match:
                    criterios_basicos.append(f"grupo {match.group(1).upper()}")

            # Detectar turno en fallback
            if "matutino" in user_lower:
                criterios_basicos.append("turno matutino")
            elif "vespertino" in user_lower:
                criterios_basicos.append("turno vespertino")

            if criterios_basicos:
                criterios_texto = ", ".join(criterios_basicos)
                return f"Encontré **{row_count} alumnos de {criterios_texto}**. ✅"
            else:
                return f"Encontré **{row_count} alumnos** que coinciden con tu búsqueda. ✅"

        except Exception as e:
            self.logger.error(f"Error generando respuesta específica: {e}")
            return f"Encontré **{row_count} alumnos** que coinciden con tu búsqueda. ✅"

    def _log_detailed_technical_context(self):
        """🔍 MOSTRAR CONTEXTO TÉCNICO COMPLETO EN LOGS - COMO SECRETARIO ACADÉMICO"""
        try:
            self.logger.info("=" * 80)
            self.logger.info("🔍 [STUDENT] CONTEXTO TÉCNICO COMPLETO:")
            self.logger.info("=" * 80)

            # 1. ESTRUCTURA DE BASE DE DATOS
            self.logger.info("🗄️ 1. ESTRUCTURA DE BASE DE DATOS:")
            try:
                # Obtener estructura real de la BD
                db_structure = self.database_analyzer.get_database_structure()
                tables = db_structure.get("tables", {})

                for table_name, table_info in tables.items():
                    self.logger.info(f"   📋 TABLA: {table_name}")
                    columns = table_info.get("columns", {})
                    count = table_info.get("count", 0)

                    for col_name, col_type in columns.items():
                        self.logger.info(f"      ├── {col_name}: {col_type}")

                    self.logger.info(f"      └── Total registros: {count}")

                # Campos especiales críticos
                self.logger.info("")
                self.logger.info("⚠️ CAMPOS ESPECIALES CRÍTICOS:")
                self.logger.info("      ├── promedio: ❌ NO EXISTE como campo directo")
                self.logger.info("      ├── calificaciones: ✅ JSON con promedio por materia")
                self.logger.info("      └── Para promedio: usar JSON_EXTRACT o filtros dinámicos")

                # Ejemplos de registros reales
                self.logger.info("")
                self.logger.info("📄 EJEMPLOS DE REGISTROS REALES:")
                try:
                    # Obtener un ejemplo de cada tabla
                    import sqlite3
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()

                        # Ejemplo COMPLETO de alumno con TODOS los campos
                        cursor.execute("SELECT * FROM alumnos LIMIT 1")
                        alumno_ejemplo = cursor.fetchone()
                        if alumno_ejemplo:
                            self.logger.info("      📋 EJEMPLO COMPLETO ALUMNO:")
                            self.logger.info(f"         ├── ID: {alumno_ejemplo[0]}")
                            self.logger.info(f"         ├── CURP: {alumno_ejemplo[1]}")
                            self.logger.info(f"         ├── Nombre: {alumno_ejemplo[2]}")
                            self.logger.info(f"         ├── Matrícula: {alumno_ejemplo[3]}")
                            self.logger.info(f"         ├── Fecha Nacimiento: {alumno_ejemplo[4]}")
                            self.logger.info(f"         └── Fecha Registro: {alumno_ejemplo[5]}")

                        # Ejemplo COMPLETO de datos escolares con TODOS los campos
                        cursor.execute("SELECT * FROM datos_escolares WHERE calificaciones IS NOT NULL AND calificaciones != '[]' LIMIT 1")
                        datos_ejemplo = cursor.fetchone()
                        if datos_ejemplo:
                            self.logger.info("      📊 EJEMPLO COMPLETO DATOS ESCOLARES:")
                            self.logger.info(f"         ├── ID: {datos_ejemplo[0]}")
                            self.logger.info(f"         ├── Alumno_ID: {datos_ejemplo[1]} (FK → alumnos.id)")
                            self.logger.info(f"         ├── Ciclo Escolar: {datos_ejemplo[2]}")
                            self.logger.info(f"         ├── Grado: {datos_ejemplo[3]}")
                            self.logger.info(f"         ├── Grupo: {datos_ejemplo[4]}")
                            self.logger.info(f"         ├── Turno: {datos_ejemplo[5]}")
                            self.logger.info(f"         ├── Escuela: {datos_ejemplo[6]}")
                            self.logger.info(f"         ├── CCT: {datos_ejemplo[7]}")
                            self.logger.info(f"         └── Calificaciones: [JSON - ver estructura abajo]")

                            # Mostrar estructura COMPLETA de calificaciones JSON
                            if datos_ejemplo[8]:  # calificaciones
                                import json
                                try:
                                    califs = json.loads(datos_ejemplo[8])
                                    if califs and len(califs) > 0:
                                        self.logger.info("      🎯 ESTRUCTURA COMPLETA JSON CALIFICACIONES:")
                                        primer_materia = califs[0]
                                        self.logger.info(f"         ├── Materia: {primer_materia.get('nombre', 'N/A')}")
                                        self.logger.info(f"         ├── Bimestre I: {primer_materia.get('i', 'N/A')}")
                                        self.logger.info(f"         ├── Bimestre II: {primer_materia.get('ii', 'N/A')}")
                                        self.logger.info(f"         ├── Bimestre III: {primer_materia.get('iii', 'N/A')}")
                                        self.logger.info(f"         ├── Promedio: {primer_materia.get('promedio', 'N/A')}")
                                        self.logger.info(f"         └── Total materias: {len(califs)}")

                                        # Mostrar RELACIÓN entre tablas
                                        self.logger.info("      🔗 RELACIÓN ENTRE TABLAS:")
                                        self.logger.info(f"         ├── alumnos.id = {alumno_ejemplo[0] if alumno_ejemplo else 'N/A'}")
                                        self.logger.info(f"         ├── datos_escolares.alumno_id = {datos_ejemplo[1]}")
                                        self.logger.info(f"         ├── RELACIÓN: alumnos.id = datos_escolares.alumno_id")
                                        self.logger.info(f"         └── JOIN: LEFT JOIN datos_escolares de ON a.id = de.alumno_id")
                                except:
                                    self.logger.info("         └── Error parseando JSON de calificaciones")

                except Exception as e:
                    self.logger.info(f"      ❌ Error obteniendo ejemplos: {e}")

            except Exception as e:
                self.logger.info(f"      ❌ Error obteniendo estructura: {e}")

            # 2. ACCIONES DISPONIBLES
            self.logger.info("")
            self.logger.info("🔧 2. ACCIONES DISPONIBLES:")
            acciones_info = {
                "BUSCAR_UNIVERSAL": {
                    "proposito": "Búsqueda flexible con criterios múltiples",
                    "entrada": "criterios dinámicos",
                    "salida": "lista de alumnos",
                    "uso": "Cuando se necesita búsqueda con 1-3 criterios"
                },
                "OBTENER_ALUMNO_EXACTO": {
                    "proposito": "Obtener UN alumno específico",
                    "entrada": "identificador único (CURP, matrícula, ID)",
                    "salida": "datos completos de un alumno",
                    "uso": "Cuando se busca una persona específica"
                },
                "CALCULAR_ESTADISTICA": {
                    "proposito": "Cálculos y análisis de datos",
                    "entrada": "tipo de estadística, filtros opcionales",
                    "salida": "números, promedios, distribuciones",
                    "uso": "Para análisis numéricos y reportes"
                },
                "GENERAR_CONSTANCIA_COMPLETA": {
                    "proposito": "Generación de documentos oficiales",
                    "entrada": "datos del alumno, tipo de constancia",
                    "salida": "archivo PDF",
                    "uso": "Para documentos oficiales"
                }
            }

            for accion, info in acciones_info.items():
                self.logger.info(f"   🎯 {accion}:")
                self.logger.info(f"      ├── Propósito: {info['proposito']}")
                self.logger.info(f"      ├── Entrada: {info['entrada']}")
                self.logger.info(f"      ├── Salida: {info['salida']}")
                self.logger.info(f"      └── Uso: {info['uso']}")

            # 3. PLANTILLAS SQL DISPONIBLES
            self.logger.info("")
            self.logger.info("📋 3. PLANTILLAS SQL OPTIMIZADAS:")
            try:
                # Verificar si SQLTemplateManager está disponible (MOVIDO A future_implementations)
                from future_implementations.sql_templates.template_manager import SQLTemplateManager
                template_manager = SQLTemplateManager()
                templates = template_manager.get_available_templates()

                self.logger.info(f"      📊 Total plantillas disponibles: {len(templates)}")
                for template in templates:
                    template_info = template_manager.get_template_info(template)
                    if template_info:
                        self.logger.info(f"      ├── {template}: {template_info.description}")

                # Plantillas más importantes
                self.logger.info("")
                self.logger.info("      🎯 PLANTILLAS PRINCIPALES (NO USADAS EN FLUJO ACTUAL):")
                self.logger.info("      ├── buscar_alumno: Búsqueda por nombre con información completa")
                self.logger.info("      ├── filtrar_grado_grupo: Para filtros de grado y grupo específicos")
                self.logger.info("      ├── buscar_por_curp: Para identificadores únicos")
                self.logger.info("      └── contar_alumnos_total: Para estadísticas básicas")
                self.logger.info("      ⚠️ NOTA: Sistema actual usa SQL dinámico, no plantillas")

            except Exception as e:
                self.logger.info(f"      ❌ Plantillas SQL no disponibles (movidas a future_implementations): {e}")

            # 4. GUÍAS DE RAZONAMIENTO ESTRATÉGICO
            self.logger.info("")
            self.logger.info("🧠 4. GUÍAS DE RAZONAMIENTO ESTRATÉGICO:")
            guias = {
                "García": "apellido común → varios resultados → mostrar todos + preguntar",
                "CURP específico": "identificador único → un resultado → mostrar directo",
                "promedio > 8": "requiere JSON_EXTRACT → usar plantilla especial",
                "constancia para Juan": "documento oficial → verificar datos + generar PDF",
                "alumnos de 2do A": "filtro específico → usar criterios directos"
            }

            for caso, estrategia in guias.items():
                self.logger.info(f"      ├── '{caso}' → {estrategia}")

            # 5. COMPONENTES ESPECIALIZADOS
            self.logger.info("")
            self.logger.info("⚙️ 5. COMPONENTES ESPECIALIZADOS INICIALIZADOS:")
            componentes = {
                "DatabaseAnalyzer": "✅ Análisis de estructura de BD",
                "SQLExecutor": "✅ Ejecución de consultas SQL",
                "ResponseParser": "✅ Parseo de respuestas LLM",
                "PromptManager": "✅ Gestión de prompts especializados",
                "ContinuationDetector": "✅ Detección de continuaciones",
                "StudentIdentifier": "✅ Identificación de alumnos",
                "ConstanciaProcessor": "✅ Procesamiento de constancias",
                "DataNormalizer": "✅ Normalización de datos",
                "ResponseGenerator": "✅ Generación de respuestas",
                "JSONParser": "✅ Parseo de JSON"
            }

            for componente, estado in componentes.items():
                self.logger.info(f"      ├── {componente}: {estado}")

            # 6. PROCESO DE RAZONAMIENTO
            self.logger.info("")
            self.logger.info("🎯 6. PROCESO DE RAZONAMIENTO ESTRATÉGICO:")
            self.logger.info("      ├── ANÁLISIS: ¿Qué quiere realmente el usuario?")
            self.logger.info("      ├── PLANIFICACIÓN: ¿Qué acciones necesito y en qué orden?")
            self.logger.info("      ├── EJECUCIÓN: ¿Cómo combinar resultados?")
            self.logger.info("      └── COMUNICACIÓN: ¿Cómo explicar lo que encontré?")

            # 7. CAPACIDADES CONVERSACIONALES
            self.logger.info("")
            self.logger.info("💬 7. CAPACIDADES CONVERSACIONALES:")
            self.logger.info("      ├── Conversation_stack: ✅ Manejo de contexto conversacional")
            self.logger.info("      ├── Continuation_detector: ✅ Detección inteligente de seguimientos")
            self.logger.info("      ├── Auto-reflexión: ✅ Análisis de continuaciones esperadas")
            self.logger.info("      └── Memoria contextual: ✅ Recordar interacciones previas")

            self.logger.info("=" * 80)
            self.logger.info("🎯 [STUDENT] CONTEXTO TÉCNICO CARGADO Y VERIFICADO")
            self.logger.info("=" * 80)

        except Exception as e:
            self.logger.error(f"❌ Error mostrando contexto técnico detallado: {e}")
