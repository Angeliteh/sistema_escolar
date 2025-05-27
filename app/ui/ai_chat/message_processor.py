"""
Procesador de mensajes y comandos para la interfaz de chat
"""
import random
from datetime import datetime
from typing import Dict, Any
from app.core.config import Config
from app.core.logging import get_logger

# CommandExecutor eliminado - ahora usamos MasterInterpreter directamente

class MessageProcessor:
    """Procesador de mensajes y comandos para la interfaz de chat"""

    def __init__(self, gemini_client=None, pdf_panel=None):
        """Inicializa el procesador de mensajes"""
        self.gemini_client = gemini_client
        self.pdf_panel = pdf_panel
        # NUEVO: Sin CommandExecutor, MasterInterpreter se inicializa cuando se necesita
        self.master_interpreter = None

        # NUEVO: Contexto conversacional inteligente
        self.conversation_history = []
        self.last_query_results = None  # Para referencias a resultados anteriores

        # NUEVO: Pila conversacional dinámica
        self.conversation_stack = []
        self.awaiting_continuation = False

        # 🆕 FRASES DESDE CONFIGURACIÓN CENTRALIZADA
        self.greeting_phrases = Config.RESPONSES['greeting_phrases']
        self.success_phrases = Config.RESPONSES['success_phrases']

        # 🆕 LOGGING CENTRALIZADO
        self.logger = get_logger(__name__)



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
        """Ejecuta comando directamente con MasterInterpreter (sin CommandExecutor)"""
        try:
            accion = command_data.get("accion", "")
            parametros = command_data.get("parametros", {})
            original_query = command_data.get("original_query", "")
            conversation_context = command_data.get("conversation_context", {})

            self.logger.debug(f"Procesando directamente: {accion}")
            self.logger.debug(f"Historial conversacional actual: {len(self.conversation_history)} mensajes")

            # Inicializar MasterInterpreter si no existe
            if not hasattr(self, 'master_interpreter') or self.master_interpreter is None:
                from app.core.ai.interpretation.master_interpreter import MasterInterpreter
                self.master_interpreter = MasterInterpreter(self.gemini_client)

            # Preparar consulta para procesar
            consulta_para_procesar = original_query or parametros.get("consulta_original", "")

            if not consulta_para_procesar:
                return False, "No se pudo determinar la consulta a procesar", {}

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

            # NUEVO: Ejecutar con MasterInterpreter pasando la pila conversacional
            result = self.master_interpreter.interpret(context, self.conversation_stack)

            if result:
                # Manejar diferentes tipos de resultados
                if result.action == "consulta_sql_exitosa":
                    message = result.parameters.get("human_response",
                                                   result.parameters.get("message", "Consulta procesada"))

                    # NUEVO: Procesar auto-reflexión del LLM
                    auto_reflexion = result.parameters.get("auto_reflexion", {})

                    # 🔧 DEBUG: Verificar si auto-reflexión está llegando
                    self.logger.info(f"🧠 DEBUG - Auto-reflexión recibida: {auto_reflexion}")

                    if auto_reflexion.get("espera_continuacion", False):
                        tipo_esperado = auto_reflexion.get("tipo_esperado", "selection")
                        datos_recordar = auto_reflexion.get("datos_recordar", {})
                        razonamiento = auto_reflexion.get("razonamiento", "")

                        self.logger.info(f"✅ LLM auto-reflexión detectó continuación esperada:")
                        self.logger.info(f"   - Tipo: {tipo_esperado}")
                        self.logger.info(f"   - Razonamiento: {razonamiento}")
                        self.logger.info(f"   - Datos a recordar: {datos_recordar}")

                        # Agregar automáticamente a la pila conversacional
                        self.add_to_conversation_stack(
                            consulta_para_procesar,
                            {
                                "data": result.parameters.get("data", []),
                                "row_count": result.parameters.get("row_count", 0),
                                "message": message,
                                "sql_query": result.parameters.get("sql_query", ""),
                                **datos_recordar  # Agregar datos adicionales de la reflexión
                            },
                            tipo_esperado
                        )

                        self.logger.info(f"📚 PILA CONVERSACIONAL ACTUALIZADA: {len(self.conversation_stack)} niveles")
                    else:
                        self.logger.info("❌ LLM auto-reflexión: No espera continuación")

                    # NUEVO: Guardar conversación con resultados
                    self.logger.debug(f"Guardando conversación: '{consulta_para_procesar}' -> '{message[:50]}...'")
                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    self.logger.debug(f"Total mensajes en historial: {len(self.conversation_history)}")

                    return True, message, result.parameters

                elif result.action in ["ayuda_proporcionada", "conversacion_general", "estadisticas_generadas",
                                     "constancia_generada", "constancia_requiere_aclaracion"]:
                    message = result.parameters.get("mensaje",
                                                   result.parameters.get("message", "Respuesta procesada"))

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

                    self.add_to_conversation(consulta_para_procesar, message, result.parameters)
                    return True, message, result.parameters

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
                    self._handle_transformation_preview(result.parameters)
                    return True, message, result.parameters

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

    def add_to_conversation_stack(self, query, result_data, awaiting_type):
        """Agregar nivel a la pila conversacional"""
        from datetime import datetime

        level = {
            "query": query,
            "data": result_data.get("data", []),
            "row_count": result_data.get("row_count", 0),
            "awaiting": awaiting_type,  # "selection", "action", "confirmation", "specification"
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "sql_query": result_data.get("sql_query", ""),
            "message": result_data.get("message", "")
        }

        self.conversation_stack.append(level)
        self.awaiting_continuation = True

        self.logger.debug(f"Agregado a pila conversacional: Nivel {len(self.conversation_stack)}")
        self.logger.debug(f"Tipo esperado: {awaiting_type}")
        self.logger.debug(f"Datos disponibles: {level['row_count']} elementos")

    def clear_conversation_stack(self):
        """Limpiar pila cuando se completa una acción o inicia consulta nueva"""
        stack_size = len(self.conversation_stack)
        self.conversation_stack = []
        self.awaiting_continuation = False
        self.logger.debug(f"Pila conversacional limpiada (tenía {stack_size} niveles)")

    def get_conversation_context_for_llm(self):
        """Formatear pila conversacional para el LLM"""
        if not self.conversation_stack:
            return ""

        context = "\n=== PILA CONVERSACIONAL ACTIVA ===\n"
        context += f"📚 NIVELES EN LA PILA: {len(self.conversation_stack)}\n"

        for i, level in enumerate(self.conversation_stack, 1):
            context += f"""
📋 NIVEL {i}:
- Consulta original: "{level['query']}"
- Datos disponibles: {level['row_count']} elementos
- Esperando del usuario: {level['awaiting']}
- SQL ejecutado: {level['sql_query'][:50]}{'...' if len(level['sql_query']) > 50 else ''}
- Timestamp: {level['timestamp']}
"""

        context += """
🧠 INSTRUCCIONES PARA USO DE LA PILA:
- Si la nueva consulta se refiere a algún nivel de la pila, USA esos datos
- NO generes nuevo SQL si puedes usar datos de la pila
- Ejemplos de referencias: "del primero", "número 5", "para él", "ese alumno"
- Si es consulta completamente nueva, ignora la pila

PATRONES DE CONTINUACIÓN:
✅ "CURP del quinto" → usar elemento 5 del último nivel con lista
✅ "constancia para él" → usar último alumno seleccionado
✅ "sí" → confirmar acción propuesta en el último nivel
❌ "cuántos alumnos hay" → consulta nueva, limpiar pila
"""

        return context

    def _detect_awaiting_continuation(self, response_message, result_data):
        """Detecta automáticamente si la respuesta espera continuación del usuario"""
        import re

        # Patrones que indican que se espera continuación
        continuation_indicators = [
            # Preguntas directas
            (r"¿.*información.*específica.*\?", "selection"),      # "¿información específica?"
            (r"¿.*necesitas.*\?", "action"),                       # "¿necesitas algo?"
            (r"¿.*te.*gustaría.*\?", "action"),                    # "¿te gustaría...?"
            (r"¿.*qué.*tipo.*\?", "specification"),                # "¿qué tipo de constancia?"
            (r"¿.*cuál.*\?", "selection"),                         # "¿cuál prefieres?"

            # Listas numeradas (indican selección posible)
            (r"\d+\.\s+[A-Z].*encontrados", "selection"),          # "1. NOMBRE... encontrados"
            (r"📋.*\(\d+.*encontrados\)", "selection"),            # "📋 LISTA (X encontrados)"

            # Ofertas de servicios
            (r"generar.*constancia", "action"),                    # Ofrece generar constancia
            (r"consultar.*información", "action"),                 # Ofrece consultar más
            (r"buscar.*criterios", "action"),                      # Ofrece buscar más
        ]

        for pattern, awaiting_type in continuation_indicators:
            if re.search(pattern, response_message, re.IGNORECASE):
                self.logger.debug(f"Patrón detectado: '{pattern}' → Tipo: {awaiting_type}")

                # Determinar tipo específico basado en contenido
                if awaiting_type == "selection" and result_data.get("row_count", 0) > 1:
                    return "selection"  # Lista con múltiples elementos
                elif "constancia" in response_message.lower():
                    return "action"     # Acción de constancia
                elif "tipo" in response_message.lower():
                    return "specification"  # Especificación de tipo
                else:
                    return awaiting_type

        # Verificar si hay datos de lista que podrían usarse después
        if result_data.get("row_count", 0) > 1:
            self.logger.debug(f"Lista de {result_data['row_count']} elementos detectada → Posible selección futura")
            return "selection"

        self.logger.debug("No se detectó patrón de continuación")
        return None  # No espera continuación