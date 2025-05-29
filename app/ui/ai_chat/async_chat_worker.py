"""
Worker thread para procesamiento asíncrono de mensajes de chat
"""

from PyQt5.QtCore import QThread, pyqtSignal, QObject
from app.core.chat_engine import ChatEngine, ChatResponse
from app.core.logging import get_logger
import traceback
import threading

class AsyncChatWorker(QThread):
    """
    Worker thread para procesar mensajes de chat de forma asíncrona
    sin bloquear la interfaz de usuario
    """

    # Señales para comunicación con la UI
    message_processed = pyqtSignal(object)  # ChatResponse
    processing_started = pyqtSignal()
    processing_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, chat_engine: ChatEngine, parent=None):
        """
        Inicializa el worker

        Args:
            chat_engine: Instancia del motor de chat
            parent: Widget padre
        """
        super().__init__(parent)
        self.chat_engine = chat_engine
        self.message_to_process = None
        self.logger = get_logger(__name__)

    def set_message(self, message: str):
        """
        Establece el mensaje a procesar

        Args:
            message: Mensaje del usuario
        """
        self.message_to_process = message

    def run(self):
        """
        Ejecuta el procesamiento del mensaje en el hilo separado
        """
        try:
            if not self.message_to_process:
                self.error_occurred.emit("No hay mensaje para procesar")
                return

            self.logger.info(f"🔄 Iniciando procesamiento asíncrono: {self.message_to_process}")
            self.processing_started.emit()

            # 🆕 CREAR CHATENGINE ESPECÍFICO PARA ESTE HILO
            # Esto evita problemas de SQLite threading
            thread_chat_engine = self._create_thread_chat_engine()

            # 🆕 GUARDAR REFERENCIA PARA SINCRONIZACIÓN POSTERIOR
            self.last_thread_engine = thread_chat_engine

            # 🆕 LOGGING DETALLADO ANTES DEL PROCESAMIENTO
            self.logger.debug(f"🔄 Procesando mensaje en worker thread: '{self.message_to_process}'")
            self.logger.debug(f"   - Thread ID: {threading.current_thread().ident}")
            self.logger.debug(f"   - PDF Panel disponible: {thread_chat_engine.pdf_panel is not None}")

            if thread_chat_engine.pdf_panel:
                self.logger.debug(f"   - PDF cargado: {hasattr(thread_chat_engine.pdf_panel, 'original_pdf') and thread_chat_engine.pdf_panel.original_pdf}")

            # Procesar mensaje usando ChatEngine del hilo
            response = thread_chat_engine.process_message(self.message_to_process)

            self.logger.info("✅ Procesamiento completado")

            # Emitir respuesta
            self.message_processed.emit(response)

        except Exception as e:
            self.logger.error(f"❌ Error en procesamiento asíncrono: {e}")
            self.logger.error(traceback.format_exc())
            self.error_occurred.emit(str(e))

        finally:
            self.processing_finished.emit()

    def _create_thread_chat_engine(self):
        """
        🆕 CREA UN CHATENGINE ESPECÍFICO PARA ESTE HILO
        Esto resuelve problemas de SQLite threading
        """
        try:
            # Importar aquí para evitar problemas de importación circular
            from app.core.chat_engine import ChatEngine

            # 🆕 FORZAR RECREACIÓN DE COMPONENTES SQL EN ESTE HILO
            self._force_recreate_sql_components()

            # 🆕 OBTENER PDF_PANEL DEL CHAT ENGINE ORIGINAL
            original_pdf_panel = getattr(self.chat_engine, 'pdf_panel', None)

            # Crear nuevo ChatEngine con las mismas configuraciones
            # pero conexiones SQLite independientes para este hilo
            thread_engine = ChatEngine(
                file_handler=self.chat_engine.file_handler,
                confirmation_handler=self.chat_engine.confirmation_handler,
                pdf_panel=original_pdf_panel
            )

            # 🆕 VERIFICAR Y TRANSFERIR ESTADO DEL PDF PANEL
            if original_pdf_panel:
                self.logger.debug("🔄 Verificando estado del PDF panel...")

                # Verificar si hay PDF cargado
                if hasattr(original_pdf_panel, 'original_pdf') and original_pdf_panel.original_pdf:
                    self.logger.debug(f"   ✅ PDF cargado detectado: {original_pdf_panel.original_pdf}")

                    # Verificar si hay datos extraídos
                    if hasattr(original_pdf_panel, 'extracted_data') and original_pdf_panel.extracted_data:
                        self.logger.debug(f"   ✅ Datos extraídos disponibles: {len(original_pdf_panel.extracted_data)} campos")
                    else:
                        self.logger.debug("   ⚠️ No hay datos extraídos del PDF")
                else:
                    self.logger.debug("   ⚠️ No hay PDF cargado en el panel")
            else:
                self.logger.debug("   ⚠️ No hay PDF panel disponible")

            # 🆕 COPIAR CONTEXTO DEL CHAT ENGINE PRINCIPAL
            if hasattr(self.chat_engine, 'context'):
                thread_engine.context = self.chat_engine.context.copy()

            # 🆕 COPIAR HISTORIAL CONVERSACIONAL COMPLETO
            if hasattr(self.chat_engine, 'message_processor'):
                self.logger.debug("🔄 Copiando contexto conversacional al worker thread...")

                # Copiar conversation_history
                if hasattr(self.chat_engine.message_processor, 'conversation_history'):
                    original_history = self.chat_engine.message_processor.conversation_history
                    if original_history:
                        thread_engine.message_processor.conversation_history = original_history.copy()
                        self.logger.debug(f"   ✅ conversation_history copiado: {len(original_history)} mensajes")
                    else:
                        thread_engine.message_processor.conversation_history = []
                        self.logger.debug("   ⚠️ conversation_history estaba vacío")

                # 🆕 COPIAR CONVERSATION_STACK (CRÍTICO PARA CONTEXTO)
                if hasattr(self.chat_engine.message_processor, 'conversation_stack'):
                    original_stack = self.chat_engine.message_processor.conversation_stack
                    if original_stack:
                        thread_engine.message_processor.conversation_stack = original_stack.copy()
                        self.logger.debug(f"   ✅ conversation_stack copiado: {len(original_stack)} niveles")

                        # 🆕 LOG DETALLADO DEL STACK PARA DEBUGGING
                        for i, level in enumerate(original_stack):
                            self.logger.debug(f"      Nivel {i}: {level.get('tipo_esperado', 'N/A')} - {level.get('context', 'N/A')}")
                    else:
                        thread_engine.message_processor.conversation_stack = []
                        self.logger.debug("   ⚠️ conversation_stack estaba vacío")

                # Copiar last_query_results
                if hasattr(self.chat_engine.message_processor, 'last_query_results'):
                    original_results = self.chat_engine.message_processor.last_query_results
                    if original_results:
                        thread_engine.message_processor.last_query_results = original_results
                        self.logger.debug("   ✅ last_query_results copiado")
                    else:
                        self.logger.debug("   ⚠️ last_query_results estaba vacío")
            else:
                self.logger.warning("❌ No se encontró message_processor en chat_engine original")

            self.logger.debug("✅ ChatEngine específico del hilo creado con componentes SQL recreados")
            return thread_engine

        except Exception as e:
            self.logger.error(f"❌ Error creando ChatEngine del hilo: {e}")
            # Fallback al ChatEngine original (puede fallar con SQLite)
            return self.chat_engine

    def _force_recreate_sql_components(self):
        """
        🆕 FUERZA LA RECREACIÓN DE COMPONENTES SQL EN ESTE HILO
        """
        try:
            # Limpiar instancias singleton que pueden tener conexiones SQLite del hilo principal
            from app.core.service_provider import ServiceProvider
            from app.core.database_manager import DatabaseManager

            # Forzar recreación del ServiceProvider en este hilo
            if hasattr(ServiceProvider, '_instance'):
                ServiceProvider._instance = None
                self.logger.debug("🔄 ServiceProvider instance cleared for thread")

            # Forzar recreación del DatabaseManager en este hilo
            if hasattr(DatabaseManager, '_instance'):
                DatabaseManager._instance = None
                self.logger.debug("🔄 DatabaseManager instance cleared for thread")

            # También limpiar cualquier cache de conexiones SQLite
            import sqlite3
            # Nota: SQLite no tiene un cache global que limpiar, pero esto asegura
            # que las nuevas conexiones se creen en este hilo

            self.logger.debug("✅ Componentes SQL preparados para recreación en hilo")

        except Exception as e:
            self.logger.error(f"❌ Error forzando recreación de componentes SQL: {e}")

class LoadingIndicator(QObject):
    """
    Indicador de carga para mostrar mientras se procesa el mensaje
    """

    def __init__(self, chat_list, parent=None):
        """
        Inicializa el indicador de carga

        Args:
            chat_list: Lista de chat donde mostrar el indicador
            parent: Objeto padre
        """
        super().__init__(parent)
        self.chat_list = chat_list
        self.loading_message_id = None
        self.dots_count = 0
        self.max_dots = 3

        # Timer para animar los puntos
        from PyQt5.QtCore import QTimer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_loading_animation)

    def show_loading(self):
        """
        Muestra el indicador de carga
        """
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")

        # Agregar mensaje de carga inicial
        loading_text = "🤖 Procesando tu mensaje"
        self.loading_message_id = self.chat_list.add_assistant_message(
            loading_text,
            current_time,
            is_loading=True
        )

        # Iniciar animación
        self.dots_count = 0
        self.animation_timer.start(500)  # Actualizar cada 500ms

    def hide_loading(self):
        """
        Oculta el indicador de carga
        """
        # Detener animación
        self.animation_timer.stop()

        # Remover mensaje de carga si existe
        if self.loading_message_id is not None:
            self.chat_list.remove_message(self.loading_message_id)
            self.loading_message_id = None

    def _update_loading_animation(self):
        """
        Actualiza la animación de puntos del indicador de carga
        """
        if self.loading_message_id is None:
            return

        # Ciclar entre 0 y max_dots
        self.dots_count = (self.dots_count + 1) % (self.max_dots + 1)

        # Crear texto con puntos animados
        dots = "." * self.dots_count
        spaces = " " * (self.max_dots - self.dots_count)
        loading_text = f"🤖 Procesando tu mensaje{dots}{spaces}"

        # Actualizar mensaje
        self.chat_list.update_message(self.loading_message_id, loading_text)

class TypingIndicator(QObject):
    """
    Indicador de escritura más sofisticado
    """

    def __init__(self, chat_list, parent=None):
        super().__init__(parent)
        self.chat_list = chat_list
        self.typing_message_id = None
        self.animation_state = 0

        from PyQt5.QtCore import QTimer
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self._update_typing_animation)

    def show_typing(self):
        """
        Muestra indicador de que la IA está escribiendo
        """
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")

        # Mensaje inicial de escritura
        typing_html = """
        <div style="display: flex; align-items: center; padding: 8px;">
            <span style="color: #3498DB; margin-right: 8px;">🤖</span>
            <span style="color: #BDC3C7; font-style: italic;">La IA está escribiendo</span>
            <span id="typing-dots" style="color: #3498DB; margin-left: 4px;">●</span>
        </div>
        """

        self.typing_message_id = self.chat_list.add_assistant_message(
            typing_html,
            current_time,
            is_loading=True
        )

        # Iniciar animación
        self.animation_state = 0
        self.typing_timer.start(600)  # Cambiar cada 600ms

    def hide_typing(self):
        """
        Oculta el indicador de escritura
        """
        self.typing_timer.stop()

        if self.typing_message_id is not None:
            self.chat_list.remove_message(self.typing_message_id)
            self.typing_message_id = None

    def _update_typing_animation(self):
        """
        Actualiza la animación de escritura
        """
        if self.typing_message_id is None:
            return

        # Diferentes estados de animación
        animations = [
            "●○○",
            "●●○",
            "●●●",
            "○●●",
            "○○●",
            "○○○"
        ]

        dots = animations[self.animation_state % len(animations)]
        self.animation_state += 1

        typing_html = f"""
        <div style="display: flex; align-items: center; padding: 8px;">
            <span style="color: #3498DB; margin-right: 8px;">🤖</span>
            <span style="color: #BDC3C7; font-style: italic;">La IA está escribiendo</span>
            <span style="color: #3498DB; margin-left: 8px; font-family: monospace;">{dots}</span>
        </div>
        """

        self.chat_list.update_message(self.typing_message_id, typing_html)
