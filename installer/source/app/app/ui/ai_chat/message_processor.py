"""
Procesador de mensajes y comandos para la interfaz de chat
VERSIÓN SIMPLIFICADA CON SISTEMA DE PLANTILLAS SQL
"""
import random
from datetime import datetime
from typing import Dict, Any
from app.core.config import Config
from app.core.logging import get_logger

class MessageProcessor:
    """Procesador de mensajes simplificado con sistema de plantillas SQL"""

    def __init__(self, gemini_client=None, pdf_panel=None):
        """Inicializa el procesador de mensajes"""
        self.gemini_client = gemini_client
        self.pdf_panel = pdf_panel

        # 🆕 LOGGING CENTRALIZADO
        self.logger = get_logger(__name__)

        # 🎯 INICIALIZAR MASTER INTERPRETER AL CARGAR EL SISTEMA
        self.logger.info("🎯 [MESSAGEPROCESSOR] Inicializando MasterInterpreter al cargar sistema...")
        from app.core.ai.interpretation.master_interpreter import MasterInterpreter
        self.master_interpreter = MasterInterpreter(self.gemini_client)
        self.logger.info("✅ [MESSAGEPROCESSOR] MasterInterpreter inicializado y listo")

        # CONTEXTO CONVERSACIONAL SIMPLE
        self.conversation_history = []
        self.last_query_results = None

        # 🔧 ATRIBUTOS REQUERIDOS PARA COMPATIBILIDAD
        self.conversation_stack = []
        self.awaiting_continuation = False

        # 🆕 FRASES DESDE CONFIGURACIÓN CENTRALIZADA
        self.greeting_phrases = Config.RESPONSES['greeting_phrases']
        self.success_phrases = Config.RESPONSES['success_phrases']

        # 🎯 CONFIGURACIÓN INTELIGENTE: ACCIONES → VISUALIZACIÓN
        self.action_display_config = {
            # SIEMPRE mostrar datos (distribuciones, estadísticas)
            "CALCULAR_ESTADISTICA": "always",

            # CONDICIONAL según cantidad (búsquedas, listas)
            "BUSCAR_UNIVERSAL": "conditional",
            "consulta_sql_exitosa": "conditional",

            # NUNCA mostrar datos técnicos (solo respuesta humana)
            "OBTENER_ALUMNO_EXACTO": "never",
            "GENERAR_CONSTANCIA_COMPLETA": "never",
            "ayuda_proporcionada": "never",
            "ayuda_funcionalidades": "never",
            "conversacion_general": "never",

            # ESPECIALES (manejan su propia visualización)
            "constancia_preview": "special",
            "transformation_preview": "special",
            "solicitar_aclaracion": "special"
        }

        # 🎯 UMBRALES CONFIGURABLES
        self.display_thresholds = {
            "max_auto_display": 50,      # Máximo para mostrar automáticamente
            "large_list_limit": 25,      # Límite para listas grandes
            "summary_threshold": 100     # Umbral para mostrar solo resumen
        }

        self.logger.info("✅ MessageProcessor inicializado con MasterInterpreter cargado")

    def should_display_data(self, action: str, data_count: int) -> bool:
        """
        🎯 DECISIÓN INTELIGENTE: ¿Mostrar datos estructurados?

        Args:
            action: Acción ejecutada (ej: CALCULAR_ESTADISTICA, BUSCAR_UNIVERSAL)
            data_count: Cantidad de registros en los datos

        Returns:
            bool: True si debe mostrar datos estructurados
        """
        # Obtener configuración para esta acción
        display_mode = self.action_display_config.get(action, "conditional")

        if display_mode == "always":
            self.logger.info(f"🎯 [DISPLAY_DECISION] {action} → ALWAYS → Mostrar datos ({data_count} registros)")
            return True
        elif display_mode == "never":
            self.logger.info(f"🎯 [DISPLAY_DECISION] {action} → NEVER → Solo respuesta humana")
            return False
        elif display_mode == "special":
            self.logger.info(f"🎯 [DISPLAY_DECISION] {action} → SPECIAL → Manejo específico")
            return False  # Las acciones especiales manejan su propia visualización
        elif display_mode == "conditional":
            # Decisión basada en cantidad de datos
            should_show = data_count <= self.display_thresholds["max_auto_display"]
            decision = "Mostrar" if should_show else "Solo resumen"
            self.logger.info(f"🎯 [DISPLAY_DECISION] {action} → CONDITIONAL → {decision} ({data_count} registros)")
            return should_show
        else:
            # Fallback: comportamiento por defecto
            self.logger.info(f"🎯 [DISPLAY_DECISION] {action} → DEFAULT → Condicional ({data_count} registros)")
            return data_count <= self.display_thresholds["max_auto_display"]





    def process_command(self, command_data, current_pdf=None, original_query=None, conversation_context=None):
        """Procesa un comando y devuelve el resultado"""
        if not command_data:
            return False, "No se pudo entender tu solicitud. ¿Podrías reformularla?", {}

        # Añadir consulta original para el bypass SQL
        if original_query and isinstance(command_data, dict):
            command_data["original_query"] = original_query

        # NUEVO: Añadir contexto conversacional
        if conversation_context and isinstance(command_data, dict):
            command_data["conversation_context"] = conversation_context

        # Procesar el comando
        accion = command_data.get("accion", "desconocida")
        parametros = command_data.get("parametros", {})

        # Si es una transformación y hay un PDF cargado, manejarla especialmente
        if accion == "transformar_constancia" and current_pdf:
            # Verificar si el usuario quiere guardar los datos
            if "guardar" in parametros and parametros["guardar"]:
                parametros["guardar_alumno"] = True
            elif "guardar_alumno" in parametros and parametros["guardar_alumno"]:
                # Asegurarse de que el valor sea booleano
                parametros["guardar_alumno"] = True

            # Si hay un PDF cargado, usar esa ruta
            if not parametros.get("ruta_archivo"):
                parametros["ruta_archivo"] = current_pdf

            # Para transformaciones, devolver directamente el comando sin ejecutar
            # El ChatWindow se encargará de manejar la transformación
            return True, "Iniciando transformación de constancia...", {
                "accion": "transformar_constancia",
                "parametros": parametros
            }

        # Si es guardar alumno desde PDF y hay un PDF cargado, usar esa ruta
        if accion == "guardar_alumno_pdf" and current_pdf:
            if not parametros.get("ruta_archivo"):
                parametros["ruta_archivo"] = current_pdf

            command_data["parametros"] = parametros

        # Ejecutar con MasterInterpreter
        return self._execute_with_master_interpreter(command_data, current_pdf=current_pdf)

    def _execute_with_master_interpreter(self, command_data, current_pdf=None):
        """Ejecuta comando con sistema de plantillas SQL (simplificado)"""
        try:
            accion = command_data.get("accion", "")
            parametros = command_data.get("parametros", {})
            original_query = command_data.get("original_query", "")
            conversation_context = command_data.get("conversation_context", {})

            self.logger.debug(f"Procesando: {accion}")
            self.logger.debug(f"Query original: {original_query}")

            # Preparar consulta para procesar
            consulta_para_procesar = original_query or parametros.get("consulta_original", "")

            if not consulta_para_procesar:
                return False, "No se pudo determinar la consulta a procesar", {}

            # 🎯 FLUJO PRINCIPAL: MASTERINTERPRETER
            self.logger.info("🎯 [MESSAGEPROCESSOR] Procesando con MasterInterpreter (ya inicializado)")

            self.logger.debug(f"Enviando a MasterInterpreter: '{consulta_para_procesar}'")

            # Crear contexto de interpretación
            from app.core.ai.interpretation.base_interpreter import InterpretationContext

            context = InterpretationContext(
                user_message=consulta_para_procesar,
                conversation_state=conversation_context.get("conversation_state", {}),
                user_preferences={}
            )

            # 🆕 AGREGAR PDF_PANEL AL CONTEXTO PARA TRANSFORMACIONES
            if hasattr(self, 'pdf_panel') and self.pdf_panel:
                context.pdf_panel = self.pdf_panel

            # CORREGIDO: Agregar historial conversacional desde self.conversation_history
            if self.conversation_history:
                context.conversation_history = self.conversation_history
                self.logger.debug(f"Pasando {len(self.conversation_history)} mensajes de contexto conversacional")

            # También agregar resultados de última consulta para referencias
            if self.last_query_results:
                context.last_query_results = self.last_query_results
                self.logger.debug(f"Pasando resultados de última consulta: '{self.last_query_results['user_query']}'")

            # Mantener contexto externo si existe
            if conversation_context.get("conversation_history"):
                context.external_conversation_history = conversation_context["conversation_history"]
            if conversation_context.get("recent_messages"):
                context.recent_messages = conversation_context["recent_messages"]

            # 🎯 PROCESAMIENTO CON CONTEXTO CONVERSACIONAL ACTIVADO
            conversation_stack = self.conversation_stack  # ← USAR PILA REAL

            # 🛑 PAUSA ESTRATÉGICA #6: CONVERSATION_STACK ANTES DE PROCESAR
            import os
            if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                print(f"\n🛑 [CONVERSATION_STACK] ESTADO ANTES DE PROCESAR:")
                print(f"    ├── 📝 Consulta: '{consulta_para_procesar}'")
                print(f"    ├── 📊 Niveles en stack: {len(conversation_stack)}")
                print(f"    ├── 🧠 Nueva Arquitectura: MASTER decide TODO sobre contexto")

                if conversation_stack:
                    print(f"    ├── 📋 CONTEXTO DISPONIBLE PARA MASTER:")
                    for i, nivel in enumerate(conversation_stack, 1):
                        query = nivel.get('query', 'N/A')
                        data_count = nivel.get('row_count', 0)
                        awaiting = nivel.get('awaiting', 'N/A')
                        action_type = nivel.get('action_type', 'N/A')
                        query_type = nivel.get('query_type', 'N/A')

                        print(f"    │   NIVEL {i}: '{query}'")
                        print(f"    │   ├── Elementos: {data_count}")
                        print(f"    │   ├── Esperando: {awaiting}")
                        print(f"    │   ├── Tipo acción: {action_type}")
                        print(f"    │   ├── Tipo query: {query_type}")

                        if nivel.get('data') and len(nivel['data']) <= 3:
                            print(f"    │   └── Datos disponibles:")
                            for j, item in enumerate(nivel['data'][:3], 1):
                                nombre = item.get('nombre', 'N/A')
                                id_alumno = item.get('id', item.get('alumno_id', 'N/A'))
                                print(f"    │       {j}. {nombre} (ID: {id_alumno})")
                        elif nivel.get('data') and len(nivel['data']) > 3:
                            print(f"    │   └── Lista grande: {data_count} elementos (regenerable)")
                        print(f"    │")
                else:
                    print(f"    └── Stack VACÍO - Primera consulta")

                print(f"    └── Presiona ENTER para que Master analice contexto...")
                input()

            # 🔧 CRÍTICO: Agregar conversation_stack al context para que llegue al Student
            context.conversation_stack = conversation_stack

            if conversation_stack:
                self.logger.info(f"🎯 CONTEXTO ACTIVO - {len(conversation_stack)} niveles disponibles")
            else:
                self.logger.info("🎯 CONTEXTO VACÍO - Procesando consulta individual")



            result = self.master_interpreter.interpret(context, conversation_stack, current_pdf=current_pdf)

            if result:
                # 🔍 [DEBUG] RASTREO COMPLETO DEL FLUJO
                self.logger.info(f"🔍 [DEBUG] Resultado recibido: action='{result.action}'")

                # 🎯 DECISIÓN INTELIGENTE BASADA EN CONFIGURACIÓN DE ACCIONES
                data = result.parameters.get("data", [])
                data_count = len(data) if isinstance(data, list) else 0
                self.logger.info(f"🔍 [DEBUG] Datos extraídos: {data_count} elementos")

                if self.should_display_data(result.action, data_count):
                    self.logger.info(f"🔍 [DEBUG] Entrando en should_display_data=True para '{result.action}'")
                    message = result.parameters.get("human_response",
                                                   result.parameters.get("message", "Consulta procesada"))

                    # 🎓 [STUDENT] Reporte procesado - Master decide contexto



                    # 🧠 NUEVA ARQUITECTURA: MASTER COMO CEREBRO CENTRAL DEL CONTEXTO
                    # ================================================================
                    # - MASTER decide TODO sobre el conversation_stack
                    # - Student solo reporta lo que hizo
                    # - Master usa contexto completo para análisis inicial y respuesta final
                    # - Sincronización perfecta entre análisis y respuesta
                    # - SIEMPRE agregar resultados relevantes al contexto
                    # ================================================================

                    # Preparar datos para el stack
                    stack_data = {
                        "data": data,
                        "row_count": len(data),
                        "sql_executed": result.parameters.get("sql_executed", ""),
                        "action_type": result.action,
                        "query_type": "search_results"
                    }

                    # Determinar tipo de continuación esperada basado en los datos
                    if len(data) == 1:
                        awaiting_type = "action"  # Un elemento específico - probable acción
                    elif len(data) > 1 and len(data) <= 50:
                        awaiting_type = "filter"  # Lista manejable - probable filtro
                    else:
                        awaiting_type = "analysis"  # Lista grande - probable análisis

                    self.logger.info(f"🧠 [MASTER DECIDE] Agregando {len(data)} resultados al contexto (esperando: {awaiting_type})")

                    # SIEMPRE agregar al conversation_stack
                    self.add_to_conversation_stack(
                        consulta_para_procesar,
                        stack_data,
                        awaiting_type
                    )

                    # 🎯 CONFIGURAR DATOS ESTRUCTURADOS PARA DATADISPLAYMANAGER
                    # (data ya extraído arriba)
                    row_count = result.parameters.get("row_count", data_count)

                    # Si hay datos, configurar para mostrar con DataDisplayManager
                    if data and data_count > 0:
                        self.logger.info(f"🎯 Datos estructurados detectados ({row_count} registros) - Configurando para DataDisplayManager")

                        # Configurar parámetros para DataDisplayManager
                        formatted_parameters = result.parameters.copy()
                        formatted_parameters["action"] = "show_data"

                        # Mantener datos en formato original para que DataDisplayManager los detecte
                        # No necesitamos agregar clave "alumnos" - DataDisplayManager lo detecta automáticamente

                        # NUEVO: Guardar conversación con resultados formateados
                        self.logger.debug(f"Guardando conversación con datos estructurados: '{consulta_para_procesar}' -> '{message[:50]}...'")
                        self.add_to_conversation(consulta_para_procesar, message, formatted_parameters)
                        self.logger.debug(f"Total mensajes en historial: {len(self.conversation_history)}")



                        return True, message, formatted_parameters

                    else:
                        # Sin datos estructurados, procesar normalmente
                        # NUEVO: Guardar conversación con resultados
                        self.logger.debug(f"Guardando conversación: '{consulta_para_procesar}' -> '{message[:50]}...'")
                        self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                        self.logger.debug(f"Total mensajes en historial: {len(self.conversation_history)}")

                        return True, message, result.parameters

                elif result.action in ["ayuda_proporcionada", "ayuda_funcionalidades", "ayuda_solucion", "ayuda_ejemplo",
                                     "conversacion_general", "estadisticas_generadas",
                                     "constancia_generada", "constancia_requiere_aclaracion"]:
                    self.logger.info(f"🔍 [DEBUG] Entrando en condición ayuda/conversación para '{result.action}'")
                    # 🛠️ USAR EL MENSAJE REAL GENERADO POR EL HELPINTERPRETER
                    message = result.parameters.get("message",
                                                   result.parameters.get("mensaje", "Respuesta procesada"))

                    # NUEVO: Guardar conversación
                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)

                    return True, message, result.parameters

                # 🆕 NUEVAS ACCIONES DE CONSTANCIA
                elif result.action == "constancia_preview":
                    self.logger.info("🎯 [DEBUG] CONSTANCIA_PREVIEW DETECTADA - Procesando...")
                    message = result.parameters.get("message", "Vista previa de constancia generada")

                    # 🧠 MASTER DECIDE - SIEMPRE AGREGAR CONSTANCIAS AL CONVERSATION_STACK
                    # Extraer información del alumno para el contexto
                    raw_data = result.parameters.get("data", {})

                    # 🔧 MANEJAR TANTO DICT COMO LIST
                    alumno_data = None
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        # Si es lista, tomar el primer elemento
                        first_item = raw_data[0]
                        if isinstance(first_item, dict) and "data" in first_item:
                            # Estructura: [{"data": {"alumno": {...}, "ruta_archivo": "..."}}]
                            alumno_data = first_item["data"].get("alumno", {})
                            ruta_archivo = first_item["data"].get("ruta_archivo", "")
                        elif isinstance(first_item, dict) and "alumno" in first_item:
                            # Estructura: [{"alumno": {...}, "ruta_archivo": "..."}]
                            alumno_data = first_item.get("alumno", {})
                            ruta_archivo = first_item.get("ruta_archivo", "")
                    elif isinstance(raw_data, dict):
                        # Si es dict directo
                        if "alumno" in raw_data:
                            alumno_data = raw_data.get("alumno", {})
                            ruta_archivo = raw_data.get("ruta_archivo", "")
                        else:
                            alumno_data = raw_data
                            ruta_archivo = raw_data.get("ruta_archivo", "")

                    self.logger.info(f"🔧 [DEBUG] Estructura detectada - raw_data type: {type(raw_data)}, alumno_data: {bool(alumno_data)}")

                    if alumno_data and isinstance(alumno_data, dict) and alumno_data.get("nombre"):
                        # Crear datos para el conversation_stack
                        stack_data = {
                            "data": [alumno_data],  # Lista con el alumno específico
                            "row_count": 1,
                            "sql_executed": f"Constancia generada para {alumno_data.get('nombre')}",
                            "action_type": "constancia_preview",
                            "query_type": "constancia_generated"
                        }

                        self.logger.info(f"🧠 [MASTER DECIDE] Agregando constancia al contexto: {alumno_data.get('nombre')} (ID: {alumno_data.get('id')})")
                        self.add_to_conversation_stack(
                            consulta_para_procesar,
                            stack_data,
                            "action"  # Espera acción sobre este alumno específico
                        )
                        # Nota: La pausa #9 se ejecuta automáticamente en add_to_conversation_stack()

                    # 🎯 AGREGAR ACCIÓN Y ARCHIVO A LOS PARÁMETROS PARA QUE LLEGUE AL CHATENGINE
                    parameters_with_action = result.parameters.copy()
                    parameters_with_action["action"] = result.action  # ← PRESERVAR ACCIÓN

                    # 🔧 CRÍTICO: Preservar ruta_archivo y alumno para que ChatEngine pueda mostrar PDF
                    if alumno_data and isinstance(alumno_data, dict):
                        # Preservar datos del alumno para el contexto del panel
                        parameters_with_action["alumno"] = alumno_data
                        self.logger.info(f"🔧 [DEBUG] Datos del alumno agregados para contexto del panel: {alumno_data.get('nombre')}")

                        # Buscar ruta_archivo en la estructura original
                        if isinstance(raw_data, list) and len(raw_data) > 0:
                            first_item = raw_data[0]
                            if isinstance(first_item, dict) and "data" in first_item and "ruta_archivo" in first_item["data"]:
                                parameters_with_action["ruta_archivo"] = first_item["data"]["ruta_archivo"]
                                self.logger.info(f"🔧 [DEBUG] Archivo PDF agregado a parámetros: {first_item['data']['ruta_archivo']}")
                            elif isinstance(first_item, dict) and "ruta_archivo" in first_item:
                                parameters_with_action["ruta_archivo"] = first_item["ruta_archivo"]
                                self.logger.info(f"🔧 [DEBUG] Archivo PDF agregado a parámetros: {first_item['ruta_archivo']}")
                    else:
                        self.logger.warning(f"🚨 [DEBUG] NO se encontró alumno_data válido: {raw_data}")

                    # 🛑 PAUSA ESTRATÉGICA #7: CONVERSATION_STACK DESPUÉS DE PROCESAR
                    import os
                    if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                        print(f"\n🛑 [CONVERSATION_STACK] ESTADO DESPUÉS DE PROCESAR:")
                        print(f"    ├── 📝 Consulta procesada: '{consulta_para_procesar}'")
                        print(f"    ├── 🎯 Acción ejecutada: {result.action}")
                        print(f"    ├── 📊 Niveles en stack: {len(self.conversation_stack)}")
                        print(f"    ├── 🧠 Master decidió agregar resultado al contexto")

                        if self.conversation_stack:
                            print(f"    ├── 📋 CONTEXTO ACTUALIZADO:")
                            for i, nivel in enumerate(self.conversation_stack, 1):
                                query = nivel.get('query', 'N/A')
                                data_count = nivel.get('row_count', 0)
                                awaiting = nivel.get('awaiting', 'N/A')
                                action_type = nivel.get('action_type', 'N/A')
                                query_type = nivel.get('query_type', 'N/A')

                                print(f"    │   NIVEL {i}: '{query}'")
                                print(f"    │   ├── Elementos: {data_count}")
                                print(f"    │   ├── Esperando: {awaiting}")
                                print(f"    │   ├── Tipo acción: {action_type}")
                                print(f"    │   ├── Tipo query: {query_type}")

                                if nivel.get('data') and len(nivel['data']) <= 3:
                                    print(f"    │   └── Datos disponibles:")
                                    for j, item in enumerate(nivel['data'][:3], 1):
                                        nombre = item.get('nombre', 'N/A')
                                        id_alumno = item.get('id', item.get('alumno_id', 'N/A'))
                                        print(f"    │       {j}. {nombre} (ID: {id_alumno})")
                                elif nivel.get('data') and len(nivel['data']) > 3:
                                    print(f"    │   └── Lista grande: {data_count} elementos")
                                print(f"    │")
                        else:
                            print(f"    └── Stack VACÍO")

                        print(f"    └── 🎯 PRÓXIMA CONSULTA podrá usar ESTE contexto")
                        print(f"    └── Presiona ENTER para continuar...")
                        input()

                    self.add_to_conversation(consulta_para_procesar, message, parameters_with_action)
                    return True, message, parameters_with_action

                elif result.action in ["constancia_confirmada", "constancia_abierta", "constancia_cancelada"]:
                    message = result.parameters.get("message", "Acción de constancia completada")

                    # Limpiar pila conversacional después de acción de constancia
                    self.clear_conversation_stack()

                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    return True, message, result.parameters

                elif result.action == "transformar_constancia":
                    # Manejar transformación de constancia
                    data_with_action = result.parameters.copy()
                    data_with_action["accion"] = "transformar_constancia"
                    return True, result.parameters.get("message", "Transformación iniciada"), data_with_action

                elif result.action == "constancia_error":
                    # 🆕 USAR MENSAJE AMIGABLE EN LUGAR DE ERROR TÉCNICO
                    error_message = result.parameters.get("message", "Error al procesar constancia")
                    return False, error_message, result.parameters

                elif result.action == "transformation_preview":
                    # 🆕 MANEJAR VISTA PREVIA DE TRANSFORMACIÓN
                    message = result.parameters.get("message", "Vista previa de transformación generada")

                    # 🎯 AGREGAR ACCIÓN A LOS PARÁMETROS PARA QUE LLEGUE AL CHATENGINE
                    parameters_with_action = result.parameters.copy()
                    parameters_with_action["action"] = result.action  # ← PRESERVAR ACCIÓN



                    self._handle_transformation_preview(parameters_with_action)
                    return True, message, parameters_with_action

                elif result.action == "transformation_error":
                    # 🆕 MANEJAR ERRORES DE TRANSFORMACIÓN
                    error_message = result.parameters.get("message", "Error al transformar PDF")
                    return False, error_message, result.parameters

                # NUEVO: Manejar resultados del sistema conversacional
                elif result.action == "seleccion_realizada":
                    message = result.parameters.get("message", "Selección realizada")

                    # Agregar a la pila conversacional si es necesario
                    elemento_seleccionado = result.parameters.get("elemento_seleccionado", {})
                    if elemento_seleccionado:
                        self.add_to_conversation_stack(
                            consulta_para_procesar,
                            {"data": [elemento_seleccionado], "row_count": 1, "message": message},
                            "action"  # Espera acción sobre el elemento seleccionado
                        )

                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    return True, message, result.parameters

                elif result.action in ["accion_realizada", "confirmacion_realizada", "especificacion_realizada"]:
                    message = result.parameters.get("message", "Acción procesada")
                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    return True, message, result.parameters

                elif result.action == "continuacion_error":
                    # Error en continuación - limpiar pila y proceder normalmente
                    self.clear_conversation_stack()
                    error_message = result.parameters.get("message", "Error en continuación conversacional")
                    return False, error_message, result.parameters

                elif result.action == "continuacion_inteligente":
                    # NUEVO: Manejo de continuación inteligente
                    message = result.parameters.get("message", "Continuación procesada")

                    # 🧠 MASTER DECIDE - Agregar continuaciones inteligentes al contexto
                    # Las continuaciones inteligentes siempre se agregan para mantener contexto
                    stack_data = {
                        "data": result.parameters.get("data", []),
                        "row_count": result.parameters.get("row_count", 0),
                        "sql_executed": result.parameters.get("sql_executed", "Continuación inteligente"),
                        "action_type": result.action,
                        "query_type": "intelligent_continuation"
                    }

                    self.logger.info(f"🧠 [MASTER DECIDE] Agregando continuación inteligente al contexto")
                    self.add_to_conversation_stack(consulta_para_procesar, stack_data, "action")

                    # 🔧 IMPORTANTE: Agregar return que faltaba
                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    return True, message, result.parameters

                elif result.action == "solicitar_aclaracion":
                    # 🔄 COMUNICACIÓN BIDIRECCIONAL: Master solicita aclaración al usuario
                    message = result.parameters.get("message", "Necesito más información")

                    # 🎯 AGREGAR ACCIÓN A LOS PARÁMETROS PARA QUE LLEGUE AL CHATENGINE
                    parameters_with_action = result.parameters.copy()
                    parameters_with_action["action"] = result.action  # ← PRESERVAR ACCIÓN

                    # 🔄 GUARDAR ESTADO DE ESPERA DE CLARIFICACIÓN
                    # Crear conversation_context si no existe
                    if not hasattr(self, 'conversation_context'):
                        self.conversation_context = {}
                    self.conversation_context["waiting_for"] = "clarification"
                    self.conversation_context["clarification_info"] = result.parameters

                    self.logger.info(f"🔄 [MESSAGEPROCESSOR] Solicitando aclaración al usuario")
                    return True, message, parameters_with_action

                else:
                    self.logger.info(f"🔍 [DEBUG] Entrando en condición ELSE (otros resultados) para '{result.action}'")
                    # Otros tipos de resultado
                    message = result.parameters.get("mensaje",
                                                   result.parameters.get("message", "Consulta procesada"))

                    # 🧠 MASTER DECIDE - Evaluar si otros resultados necesitan contexto
                    # Solo agregar al stack si hay datos relevantes
                    data = result.parameters.get("data", [])
                    if data and len(data) > 0:
                        stack_data = {
                            "data": data,
                            "row_count": len(data),
                            "sql_executed": result.parameters.get("sql_executed", f"Resultado: {result.action}"),
                            "action_type": result.action,
                            "query_type": "other_result"
                        }

                        self.logger.info(f"🧠 [MASTER DECIDE] Agregando resultado '{result.action}' al contexto ({len(data)} elementos)")
                        self.add_to_conversation_stack(consulta_para_procesar, stack_data, "action")

                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    return True, message, result.parameters
            else:
                return False, "No se pudo procesar la consulta", {}

        except Exception as e:
            self.logger.error(f"Error en _execute_with_master_interpreter: {str(e)}")
            return False, f"Error procesando consulta: {str(e)}", {}





    def get_current_time(self):
        """Obtiene la hora actual en formato HH:MM"""
        now = datetime.now()
        return now.strftime("%H:%M")

    def get_random_greeting(self):
        """Devuelve un saludo aleatorio"""
        return random.choice(self.greeting_phrases)

    def get_random_success_phrase(self):
        """Devuelve una frase de éxito aleatoria"""
        return random.choice(self.success_phrases)

    def add_to_conversation_stack(self, query, result_data, awaiting_type):
        """
        Agrega nivel a la pila conversacional según PROTOCOLO_COMUNICACION_BIDIRECCIONAL.md

        Args:
            query (str): Consulta del usuario que generó estos datos
            result_data (dict): Datos del resultado (data, row_count, sql_executed)
            awaiting_type (str): Tipo de continuación esperada (analysis, action, confirmation, selection)
        """
        from datetime import datetime



        # 🔧 NORMALIZAR DATOS: SIEMPRE LISTA
        raw_data = result_data.get("data", [])
        if isinstance(raw_data, dict):
            # Si es diccionario, convertir a lista con un elemento
            normalized_data = [raw_data]
            self.logger.info(f"🔧 [STACK] Normalizando diccionario a lista: {list(raw_data.keys())}")
        elif isinstance(raw_data, list):
            # Si ya es lista, usar tal como está
            normalized_data = raw_data
        else:
            # Si es otro tipo, crear lista vacía
            normalized_data = []
            self.logger.warning(f"🔧 [STACK] Tipo de datos no reconocido: {type(raw_data)}")

        # Estructura según PROTOCOLO_COMUNICACION_BIDIRECCIONAL.md
        level = {
            "id": len(self.conversation_stack) + 1,
            "query": query,
            "data": normalized_data,  # ✅ SIEMPRE LISTA
            "row_count": result_data.get("row_count", len(normalized_data)),
            "sql_executed": result_data.get("sql_executed", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "awaiting": awaiting_type,
            "active": True,
            "context_available": {
                "positions": len(normalized_data) > 0,  # "el segundo", "el tercero"
                "names": len(normalized_data) > 0,      # "FRANCO", "VALERIA"
                "actions": awaiting_type in ["confirmation", "action"],  # "constancia para"
                "filters": awaiting_type in ["analysis", "selection"]    # "que tengan"
            },
            "priority": 0.9  # Más reciente = mayor prioridad
        }

        # Actualizar prioridades de niveles anteriores
        for existing_level in self.conversation_stack:
            existing_level["priority"] *= 0.7  # Reducir prioridad

        self.conversation_stack.append(level)
        self.awaiting_continuation = True

        self.logger.info(f"📋 [CONVERSATION_STACK] Nivel agregado:")
        self.logger.info(f"    ├── Query: '{query}'")
        self.logger.info(f"    ├── Datos: {len(result_data.get('data', []))} elementos")
        self.logger.info(f"    ├── Esperando: {awaiting_type}")
        self.logger.info(f"    └── Total niveles: {len(self.conversation_stack)}")

        # 🔔 VERIFICAR SALUD DE LA SESIÓN
        session_warning = self._check_session_health()
        if session_warning:
            self.logger.info(f"🔔 [SESSION_HEALTH] {session_warning['type'].upper()}: {session_warning['message']}")
            self._show_session_warning(session_warning)

            # 🧹 LIMPIEZA AUTOMÁTICA EN CASO CRÍTICO
            if session_warning['type'] == 'critical':
                self._auto_cleanup_context()

        # 🛑 PAUSA ESPECÍFICA PARA AGREGAR AL CONVERSATION_STACK
        import os
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            print(f"\n🛑 [CONVERSATION_STACK] NUEVO NIVEL AGREGADO:")
            print(f"    ├── 📝 Query: '{query}'")
            print(f"    ├── 📊 Datos: {len(result_data.get('data', []))} elementos")
            print(f"    ├── 🎯 Esperando: {awaiting_type}")
            print(f"    ├── 📋 Total niveles: {len(self.conversation_stack)}")
            print(f"    ├── 🧠 NUEVA ARQUITECTURA: Master decidió agregar este resultado")

            # Mostrar el nivel que se acaba de agregar
            if result_data.get('data'):
                action_type = result_data.get('action_type', 'N/A')
                query_type = result_data.get('query_type', 'N/A')
                print(f"    ├── 🔧 Tipo acción: {action_type}")
                print(f"    ├── 🔧 Tipo query: {query_type}")
                print(f"    ├── 📋 Datos agregados:")

                for i, item in enumerate(result_data['data'][:3], 1):
                    nombre = item.get('nombre', 'N/A')
                    id_alumno = item.get('id', item.get('alumno_id', 'N/A'))
                    print(f"    │   {i}. {nombre} (ID: {id_alumno})")

                if len(result_data['data']) > 3:
                    print(f"    │   ... y {len(result_data['data']) - 3} más")

            print(f"    ├── 🎯 PRÓXIMAS CONSULTAS podrán usar este contexto")
            print(f"    └── Presiona ENTER para continuar...")
            input()



    def _check_session_health(self):
        """
        🔔 VERIFICAR SALUD DE LA SESIÓN
        Analiza el estado del conversation_stack y genera avisos apropiados
        """
        try:
            levels = len(self.conversation_stack)

            # Calcular tamaño aproximado del contexto
            context_size_kb = self._estimate_context_size()

            if levels >= 20:
                return {
                    "type": "critical",
                    "message": f"🚨 Esta sesión está muy cargada ({levels} niveles, {context_size_kb:.1f}KB). Te recomiendo crear una nueva sesión para mejor rendimiento.",
                    "action": "suggest_new_session",
                    "levels": levels,
                    "size_kb": context_size_kb
                }
            elif levels >= 15:
                return {
                    "type": "warning",
                    "message": f"⚠️ Esta sesión tiene mucho contexto ({levels} niveles, {context_size_kb:.1f}KB). ¿Quieres continuar o prefieres una nueva sesión?",
                    "action": "offer_choice",
                    "levels": levels,
                    "size_kb": context_size_kb
                }
            elif levels >= 12:
                return {
                    "type": "info",
                    "message": f"💡 Esta sesión está acumulando contexto ({levels} niveles). Considera crear nueva sesión para consultas independientes.",
                    "action": "gentle_suggestion",
                    "levels": levels,
                    "size_kb": context_size_kb
                }

            return None

        except Exception as e:
            self.logger.error(f"Error verificando salud de sesión: {e}")
            return None

    def _estimate_context_size(self):
        """Estima el tamaño del contexto en KB"""
        try:
            import sys
            total_size = 0

            # Tamaño del conversation_stack
            for level in self.conversation_stack:
                total_size += sys.getsizeof(str(level))

            # Tamaño del conversation_history
            for message in self.conversation_history:
                total_size += sys.getsizeof(str(message))

            return total_size / 1024  # Convertir a KB

        except Exception as e:
            self.logger.error(f"Error estimando tamaño de contexto: {e}")
            return 0.0

    def _show_session_warning(self, warning_data):
        """
        🔔 MOSTRAR AVISO DE SESIÓN EN EL CHAT
        Agrega un mensaje del sistema informando sobre el estado de la sesión
        """
        try:
            # Crear mensaje del sistema con el aviso
            warning_message = {
                "role": "system",
                "content": warning_data["message"],
                "timestamp": datetime.now().isoformat(),
                "type": "session_warning",
                "warning_type": warning_data["type"],
                "metadata": {
                    "levels": warning_data.get("levels", 0),
                    "size_kb": warning_data.get("size_kb", 0.0),
                    "action": warning_data.get("action", "none")
                }
            }

            # Agregar al historial conversacional
            self.conversation_history.append(warning_message)

            self.logger.info(f"🔔 [SESSION_WARNING] Aviso mostrado en chat: {warning_data['type']}")

        except Exception as e:
            self.logger.error(f"Error mostrando aviso de sesión: {e}")

    def clear_conversation_stack(self):
        """Limpiar pila conversacional"""
        niveles_eliminados = len(self.conversation_stack)



        self.conversation_stack = []
        self.awaiting_continuation = False

        self.logger.info(f"🗑️ [CONVERSATION_STACK] Limpiado - {niveles_eliminados} niveles eliminados")

    def _auto_cleanup_context(self):
        """
        🧹 LIMPIEZA AUTOMÁTICA DEL CONTEXTO
        Mantiene solo los niveles más recientes cuando se alcanza el límite
        """
        try:
            max_levels = 15
            if len(self.conversation_stack) > max_levels:
                # Mantener solo los últimos 10 niveles
                keep_levels = 10
                removed_levels = len(self.conversation_stack) - keep_levels

                self.conversation_stack = self.conversation_stack[-keep_levels:]

                self.logger.info(f"🧹 [AUTO_CLEANUP] Contexto optimizado: {removed_levels} niveles antiguos eliminados, {keep_levels} mantenidos")

                # Mostrar aviso de limpieza automática
                cleanup_message = {
                    "role": "system",
                    "content": f"🧹 Contexto optimizado automáticamente. Mantuve los últimos {keep_levels} niveles de conversación para mejor rendimiento.",
                    "timestamp": datetime.now().isoformat(),
                    "type": "auto_cleanup",
                    "metadata": {
                        "removed_levels": removed_levels,
                        "kept_levels": keep_levels
                    }
                }

                self.conversation_history.append(cleanup_message)

        except Exception as e:
            self.logger.error(f"Error en limpieza automática: {e}")



    def add_to_conversation(self, user_message, system_response, query_results=None):
        """Agregar intercambio al historial conversacional"""
        from datetime import datetime

        # Agregar mensaje del usuario
        self.conversation_history.append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })

        # Agregar respuesta del sistema
        self.conversation_history.append({
            'role': 'system',
            'content': system_response,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })

        # Guardar resultados de la última consulta para referencias
        if query_results:
            self.last_query_results = {
                'user_query': user_message,
                'results': query_results,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }

        # Mantener solo últimos 10 intercambios (20 mensajes)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def _get_conversation_context(self):
        """Genera contexto conversacional inteligente"""
        if not self.conversation_history:
            return ""

        # Últimos 3 intercambios (6 mensajes)
        recent_messages = self.conversation_history[-6:]

        if not recent_messages:
            return ""

        context = """

=== CONTEXTO CONVERSACIONAL RECIENTE ===
📝 HISTORIAL DE LA SESIÓN ACTUAL:
"""

        for msg in recent_messages:
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            # Truncar respuestas largas del sistema
            content = msg['content']
            if msg['role'] == 'system' and len(content) > 150:
                content = content[:150] + "..."

            context += f"{role_emoji} {msg['role'].title()}: {content}\n"

        # Agregar información de últimos resultados si existen
        if self.last_query_results:
            context += f"""
📊 ÚLTIMA CONSULTA REALIZADA:
- Consulta: "{self.last_query_results['user_query']}"
- Resultados disponibles para referencias
"""

        context += """
🧠 INSTRUCCIONES PARA USO INTELIGENTE DEL CONTEXTO:
- USA el contexto SOLO si la consulta actual hace referencia a información anterior
- Si el usuario dice "el primero", "ese", "él", "ella" → busca en el contexto
- Si dice "y cuántos...", "también...", "además..." → relaciona con consulta anterior
- Si es una consulta completamente nueva → IGNORA el contexto
- Si hay dudas sobre referencias → pregunta al usuario para aclarar

EJEMPLOS DE CUÁNDO USAR CONTEXTO:
✅ "CURP del tercero" (después de mostrar lista)
✅ "constancia para él" (después de mostrar alumno específico)
✅ "y del turno vespertino" (después de consulta de grado)
❌ "cuántos alumnos hay" (consulta independiente)
❌ "buscar García" (consulta nueva)
"""

        return context

    def _handle_transformation_preview(self, parameters: Dict[str, Any]):
        """Maneja vista previa de transformación de PDF"""
        try:
            files = parameters.get("files", [])
            if files and self.pdf_panel:
                pdf_path = files[0]
                self.logger.info(f"Cargando vista previa de transformación: {pdf_path}")

                # Cargar PDF transformado en el panel
                self.pdf_panel.show_pdf(pdf_path)

                # Establecer contexto de transformación completada
                alumno_data = parameters.get("alumno", {})
                transformation_info = parameters.get("transformation_info", {})

                if hasattr(self.pdf_panel, 'set_transformation_completed_context'):
                    self.pdf_panel.set_transformation_completed_context(
                        original_data=self.pdf_panel.pdf_data,
                        transformed_data=parameters.get("data", {}),
                        alumno_data=alumno_data
                    )

                self.logger.debug(f"Vista previa de transformación cargada: {transformation_info.get('tipo_transformacion', 'N/A')}")

        except Exception as e:
            self.logger.error(f"Error manejando vista previa de transformación: {e}")

    # ==========================================
    # MÉTODOS DE GESTIÓN DE PILA CONVERSACIONAL
    # ==========================================





    # 🗑️ MÉTODOS DEL SISTEMA DE MEMORIA PROBLEMÁTICO ELIMINADOS
    # El sistema de plantillas SQL los reemplaza completamente
