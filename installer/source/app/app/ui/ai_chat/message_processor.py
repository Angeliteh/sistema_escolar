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

        # NUEVO FLUJO DIRECTO: Sin CommandExecutor, directo a MasterInterpreter
        return self._execute_with_master_interpreter(command_data)

    def _execute_with_master_interpreter(self, command_data):
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

            # 🔧 CRÍTICO: Agregar conversation_stack al context para que llegue al Student
            context.conversation_stack = conversation_stack



            if conversation_stack:
                self.logger.info(f"🎯 CONTEXTO ACTIVO - {len(conversation_stack)} niveles disponibles")
            else:
                self.logger.info("🎯 CONTEXTO VACÍO - Procesando consulta individual")



            result = self.master_interpreter.interpret(context, conversation_stack)

            if result:


                # 🎯 DECISIÓN INTELIGENTE BASADA EN CONFIGURACIÓN DE ACCIONES
                data = result.parameters.get("data", [])
                data_count = len(data) if isinstance(data, list) else 0

                if self.should_display_data(result.action, data_count):
                    message = result.parameters.get("human_response",
                                                   result.parameters.get("message", "Consulta procesada"))

                    # NUEVO: Procesar auto-reflexión del LLM
                    # Para BUSCAR_UNIVERSAL, la auto-reflexión está en 'reflexion_conversacional'
                    auto_reflexion = result.parameters.get("reflexion_conversacional",
                                                          result.parameters.get("auto_reflexion", {}))

                    # 🔧 DEBUG: Verificar si auto-reflexión está llegando
                    self.logger.info(f"🧠 DEBUG - Auto-reflexión recibida: {auto_reflexion}")



                    # 🎯 CONTEXTO ACTIVADO - Evaluar auto-reflexión para conversation_stack
                    if auto_reflexion.get("espera_continuacion", False):
                        tipo_esperado = auto_reflexion.get("tipo_esperado", "analysis")
                        datos_recordar = auto_reflexion.get("datos_recordar", {})

                        self.logger.info(f"🎯 CONTEXTO ACTIVADO - Auto-reflexión detecta continuación esperada: {tipo_esperado}")

                        # Agregar a conversation_stack
                        self.add_to_conversation_stack(
                            consulta_para_procesar,
                            {**result.parameters, **datos_recordar},
                            tipo_esperado
                        )
                    else:
                        self.logger.info("🎯 CONTEXTO EVALUADO - No se espera continuación para esta consulta")

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
                    # 🛠️ USAR EL MENSAJE REAL GENERADO POR EL HELPINTERPRETER
                    message = result.parameters.get("message",
                                                   result.parameters.get("mensaje", "Respuesta procesada"))

                    # NUEVO: Guardar conversación
                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)

                    return True, message, result.parameters

                # 🆕 NUEVAS ACCIONES DE CONSTANCIA
                elif result.action == "constancia_preview":
                    message = result.parameters.get("message", "Vista previa de constancia generada")

                    # Procesar auto-reflexión para constancias
                    auto_reflexion = result.parameters.get("auto_reflexion", {})
                    if auto_reflexion.get("espera_continuacion", False):
                        datos_recordar = auto_reflexion.get("datos_recordar", {})

                        self.logger.debug(f"Constancia con auto-reflexión: {auto_reflexion.get('razonamiento', '')}")
                        self.add_to_conversation_stack(
                            consulta_para_procesar,
                            {**result.parameters, **datos_recordar},
                            "confirmation"  # Espera confirmación para constancia
                        )

                    # 🎯 AGREGAR ACCIÓN A LOS PARÁMETROS PARA QUE LLEGUE AL CHATENGINE
                    parameters_with_action = result.parameters.copy()
                    parameters_with_action["action"] = result.action  # ← PRESERVAR ACCIÓN

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

                    # 🔍 DEBUG: Verificar que la acción se está agregando
                    self.logger.info(f"🔍 [DEBUG] TRANSFORMATION_PREVIEW - Acción agregada: {parameters_with_action.get('action')}")
                    self.logger.info(f"🔍 [DEBUG] TRANSFORMATION_PREVIEW - Mensaje: {message}")
                    self.logger.info(f"🔍 [DEBUG] TRANSFORMATION_PREVIEW - Parameters keys: {list(parameters_with_action.keys())}")

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

                    # Procesar auto-reflexión si está disponible
                    auto_reflexion = result.parameters.get("auto_reflexion", {})
                    if auto_reflexion.get("espera_continuacion", False):
                        tipo_esperado = auto_reflexion.get("tipo_esperado", "action")
                        datos_recordar = auto_reflexion.get("datos_recordar", {})

                        self.logger.debug(f"Continuación inteligente con auto-reflexión: {auto_reflexion.get('razonamiento', '')}")
                        self.add_to_conversation_stack(consulta_para_procesar, {**result.parameters, **datos_recordar}, tipo_esperado)
                    else:
                        self.logger.debug(f"Continuación inteligente completada: {result.parameters.get('razonamiento', '')}")

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
                    # Otros tipos de resultado
                    message = result.parameters.get("mensaje",
                                                   result.parameters.get("message", "Consulta procesada"))

                    # NUEVO: Procesar auto-reflexión si está disponible (para otros tipos de resultado)
                    auto_reflexion = result.parameters.get("auto_reflexion", {})
                    if auto_reflexion.get("espera_continuacion", False):
                        tipo_esperado = auto_reflexion.get("tipo_esperado", "action")
                        datos_recordar = auto_reflexion.get("datos_recordar", {})

                        self.logger.debug(f"Auto-reflexión en resultado '{result.action}': {auto_reflexion.get('razonamiento', '')}")
                        self.add_to_conversation_stack(consulta_para_procesar, {**result.parameters, **datos_recordar}, tipo_esperado)

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



        # Estructura según PROTOCOLO_COMUNICACION_BIDIRECCIONAL.md
        level = {
            "id": len(self.conversation_stack) + 1,
            "query": query,
            "data": result_data.get("data", []),
            "row_count": result_data.get("row_count", 0),
            "sql_executed": result_data.get("sql_executed", ""),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "awaiting": awaiting_type,
            "active": True,
            "context_available": {
                "positions": len(result_data.get("data", [])) > 0,  # "el segundo", "el tercero"
                "names": len(result_data.get("data", [])) > 0,      # "FRANCO", "VALERIA"
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



    def clear_conversation_stack(self):
        """Limpiar pila conversacional"""
        niveles_eliminados = len(self.conversation_stack)



        self.conversation_stack = []
        self.awaiting_continuation = False

        self.logger.info(f"🗑️ [CONVERSATION_STACK] Limpiado - {niveles_eliminados} niveles eliminados")



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

