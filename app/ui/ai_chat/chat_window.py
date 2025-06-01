"""
Ventana principal de la interfaz de chat con IA.

Este módulo implementa la ventana principal de la interfaz de chat con IA,
que permite interactuar con el asistente virtual para generar constancias,
buscar alumnos y transformar PDFs.

La interfaz incluye un panel de chat y un panel para visualizar PDFs,
así como funcionalidades para cargar, transformar y guardar constancias.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QSplitter, QProgressBar,
    QToolBar, QAction
)
from PyQt5.QtCore import Qt, QSize

from app.ui.ai_chat.chat_list import ChatList
from app.ui.ai_chat.pdf_panel import PDFPanel
from app.ui.ai_chat.response_formatter import ResponseFormatter
from app.ui.ai_chat.async_chat_worker import AsyncChatWorker, TypingIndicator
from app.core.utils import open_file_with_default_app
from app.core.chat_engine import ChatEngine, ChatResponse
from app.core.logging import get_logger

class ChatWindow(QMainWindow):
    """Ventana principal de la interfaz de chat con IA.

    Esta clase implementa la ventana principal de la aplicación que contiene
    el chat con IA y el panel de visualización de PDFs. Permite interactuar
    con el asistente virtual para realizar diversas tareas relacionadas con
    la gestión de constancias y alumnos.

    Atributos:
        waiting_for_file_open_response (bool): Indica si se está esperando respuesta para abrir un archivo.
        waiting_for_save_confirmation (bool): Indica si se está esperando confirmación para guardar un archivo.
        last_generated_file (str): Ruta del último archivo generado.
        temp_transformed_file (str): Ruta del archivo temporal transformado.
        transformation_data (dict): Datos de la última transformación realizada.
        chat_engine (ChatEngine): Motor de chat centralizado para procesamiento de mensajes.
        chat_list (ChatList): Lista de mensajes del chat.
        pdf_panel (PDFPanel): Panel para visualización y gestión de PDFs.
        pdf_panel_expanded (bool): Indica si el panel de PDF está expandido.
    """

    def __init__(self):
        """Inicializa la ventana principal de la aplicación.

        Configura la ventana, inicializa las variables de estado, crea los componentes
        necesarios y establece las conexiones entre señales y slots.
        """
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Asistente de Constancias con IA")
        self.setMinimumSize(1200, 800)

        # Inicializar variables de estado
        self.waiting_for_file_open_response = False  # Esperando respuesta para abrir archivo
        self.waiting_for_save_confirmation = False   # Esperando confirmación para guardar
        self.waiting_for_constancia_confirmation = False  # Esperando confirmación de constancia
        self.last_generated_file = None              # Último archivo generado
        self.temp_transformed_file = None            # Archivo temporal transformado
        self.temp_constancia_file = None             # Archivo temporal de constancia
        self.transformation_data = None              # Datos de transformación

        # Crear el panel de PDF primero
        self.pdf_panel = PDFPanel()

        # 🆕 SISTEMA CENTRALIZADO: Usar ChatEngine como terminal_chat.py
        self.chat_engine = ChatEngine(
            file_handler=self._handle_file,
            confirmation_handler=self._handle_confirmation,
            pdf_panel=self.pdf_panel
        )

        # 🆕 LOGGING CENTRALIZADO
        self.logger = get_logger(__name__)

        # 🎯 FORMATEADOR DE RESPUESTAS PARA MEJOR PRESENTACIÓN
        self.response_formatter = ResponseFormatter()

        # 🎯 GESTOR CENTRALIZADO DE PRESENTACIÓN DE DATOS
        # Se inicializa después de crear chat_list en setup_ui()
        self.data_display_manager = None

        # 🆕 WORKER ASÍNCRONO PARA PROCESAMIENTO SIN BLOQUEO
        self.async_worker = AsyncChatWorker(self.chat_engine)
        self.async_worker.message_processed.connect(self._handle_async_response)
        self.async_worker.processing_started.connect(self._on_processing_started)
        self.async_worker.processing_finished.connect(self._on_processing_finished)
        self.async_worker.error_occurred.connect(self._on_processing_error)

        # 🆕 INDICADOR DE ESCRITURA
        self.typing_indicator = None  # Se inicializa después de crear chat_list

        self.logger.info("ChatWindow inicializado con ChatEngine centralizado y procesamiento asíncrono")

        # Configurar la interfaz de usuario
        self.setup_ui()

        # Crear una barra de estado
        self.statusBar().showMessage("Listo")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #1A1A2E;
                color: white;
                border-top: 1px solid #2C4F7C;
            }
        """)



    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Widget central - estilo modo oscuro
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1A1A2E;")  # Fondo azul muy oscuro
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Título - estilo modo oscuro
        title_label = QLabel("Asistente de Constancias con IA")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #FFFFFF; margin-bottom: 10px;")

        main_layout.addWidget(title_label)

        # Splitter para dividir la pantalla
        splitter = QSplitter(Qt.Horizontal)

        # Panel izquierdo (chat)
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(10)

        # Lista de chat
        self.chat_list = ChatList()

        # 🆕 INICIALIZAR INDICADOR DE ESCRITURA DESPUÉS DE CREAR CHAT_LIST
        self.typing_indicator = TypingIndicator(self.chat_list)

        # 🎯 INICIALIZAR GESTOR CENTRALIZADO DE PRESENTACIÓN DE DATOS
        from app.ui.ai_chat.data_display_manager import DataDisplayManager
        self.data_display_manager = DataDisplayManager(self.chat_list, self.response_formatter)

        # Mensaje de bienvenida - todo en un solo mensaje para evitar espacios innecesarios
        mensaje_bienvenida = """¡Bienvenido al Asistente de Constancias con IA!

Puedes pedirme que busque alumnos, genere constancias o transforme PDFs.
Para transformar un PDF:
1. Haz clic en el botón "🔄 Transformación de PDF" en la barra superior
2. Carga un PDF arrastrándolo o usando el botón "Seleccionar PDF"
3. Escribe en el chat: "Transforma este PDF a constancia de estudios"

Escribe "ayuda" para ver todas las funciones disponibles."""

        # 🆕 USAR MÉTODO CENTRALIZADO para timestamp
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.chat_list.add_system_message(mensaje_bienvenida, current_time)

        # Área de entrada
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe tu mensaje aquí...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #2C4F7C;
                border-radius: 20px;
                padding: 12px 18px;
                font-size: 15px;
                font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                letter-spacing: 0.3px;
                background-color: #16213E;
                color: #FFFFFF;
                selection-background-color: #3498DB;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
            QLineEdit:focus {
                border: 1px solid #3498DB;
                background-color: #1A2A4A;
            }
            QLineEdit:hover {
                border: 1px solid #5DADE2;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)

        send_button = QPushButton("Enviar")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #2980B9;
                color: white;
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 15px;
                font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                font-weight: bold;
                border: 1px solid #3498DB;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3498DB;
                border: 1px solid #5DADE2;
            }
            QPushButton:pressed {
                background-color: #1B4F72;
            }
        """)
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(send_button)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Modo indeterminado
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #2C4F7C;
                border-radius: 5px;
                text-align: center;
                height: 10px;
                background-color: #16213E;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
            }
        """)

        # Añadir widgets al layout del chat
        chat_layout.addWidget(self.chat_list, 1)
        chat_layout.addWidget(self.progress_bar)
        chat_layout.addWidget(input_container)

        # Inicialmente ocultar el panel de PDF
        self.pdf_panel.setVisible(False)

        # Variable para rastrear el estado
        self.pdf_panel_expanded = False

        # Crear una barra de herramientas
        toolbar = QToolBar("Herramientas")
        toolbar.setMovable(False)  # Fijar la barra de herramientas
        toolbar.setIconSize(QSize(24, 24))  # Tamaño de los iconos
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1A1A2E;
                border-bottom: 1px solid #2C4F7C;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: #1E3A5F;
                color: white;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
                font-size: 13px;
            }
            QToolButton:hover {
                background-color: #2C4F7C;
            }
            QToolButton:pressed {
                background-color: #3A6095;
            }
            QToolButton:checked {
                background-color: #3A6095;
            }
        """)

        # Crear una acción para la transformación de PDF
        self.pdf_action = QAction("🔄 Transformación de PDF", self)
        self.pdf_action.setToolTip("Mostrar/ocultar panel de transformación de PDF")
        self.pdf_action.setCheckable(True)  # Hacer que el botón sea "checkable"
        self.pdf_action.triggered.connect(self.toggle_pdf_panel_visibility)

        # Añadir la acción a la barra de herramientas
        toolbar.addAction(self.pdf_action)

        # Añadir la barra de herramientas a la ventana principal
        self.addToolBar(toolbar)

        # Conectar señal de cambio de estado para expandir automáticamente cuando se carga un PDF
        self.pdf_panel.pdf_loaded.connect(self.on_pdf_loaded)

        # Añadir el panel de chat al splitter
        splitter.addWidget(chat_panel)

        # Añadir el panel de PDF al splitter
        splitter.addWidget(self.pdf_panel)

        # Configurar el splitter para que el panel de PDF sea colapsable
        splitter.setCollapsible(1, True)  # El segundo widget (índice 1) es colapsable

        # Configurar el splitter con un ancho de divisor más visible
        splitter.setHandleWidth(10)  # Ancho suficiente para ser visible pero no confundirse con scrollbar

        # Estilo simple con líneas paralelas verticales para indicar que se puede arrastrar
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #1A1A2E;  /* Mismo color de fondo que la aplicación */
                border: none;
            }
            QSplitter::handle:horizontal {
                width: 10px;
                background-color: #1A1A2E;
                border-left: 1px solid #3498DB;
                border-right: 1px solid #3498DB;
                margin-left: 2px;
                margin-right: 2px;
            }
            QSplitter::handle:hover {
                background-color: #16213E;  /* Color ligeramente diferente al pasar el mouse */
            }
        """)

        # Crear un widget personalizado para el divisor que muestre líneas verticales
        from PyQt5.QtWidgets import QSplitterHandle
        from PyQt5.QtGui import QPainter, QColor

        class CustomSplitterHandle(QSplitterHandle):
            def __init__(self, orientation, parent):
                super().__init__(orientation, parent)
                self.setCursor(Qt.SizeHorCursor)

            def paintEvent(self, event):
                _ = event  # Parámetro requerido por Qt
                painter = QPainter(self)
                painter.fillRect(self.rect(), QColor("#1A1A2E"))  # Fondo

                # Dibujar dos líneas verticales muy juntas
                painter.setPen(QColor("#3498DB"))
                center_x = self.width() // 2
                painter.drawLine(center_x - 1, 5, center_x - 1, self.height() - 5)
                painter.drawLine(center_x + 1, 5, center_x + 1, self.height() - 5)

        # Reemplazar el método createHandle del splitter
        splitter.createHandle = lambda: CustomSplitterHandle(Qt.Horizontal, splitter)

        # La configuración del splitter ya se hizo arriba

        # Guardar referencia al splitter para usarla más tarde
        self.main_splitter = splitter

        # Establecer tamaños iniciales (panel de PDF oculto inicialmente)
        splitter.setSizes([1000, 0])  # Panel de PDF colapsado

        # Añadir el splitter al layout principal
        main_layout.addWidget(splitter, 1)

    def send_message(self):
        """Envía un mensaje al asistente.

        Este método se ejecuta cuando el usuario envía un mensaje a través del campo de entrada.
        Dependiendo del estado actual de la conversación, el mensaje puede ser procesado de
        diferentes maneras:

        1. Si se está esperando confirmación para guardar un archivo transformado, se maneja esa respuesta.
        2. Si se está esperando respuesta para abrir un archivo, se maneja esa respuesta.
        3. Para mensajes normales, se procesa el mensaje y se envía al asistente de IA.

        Returns:
            None
        """
        # Obtener el texto del mensaje
        message_text = self.input_field.text().strip()
        if not message_text:
            return

        # Limpiar el campo de entrada
        self.input_field.clear()

        # 🆕 USAR TIMESTAMP CENTRALIZADO
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")

        # Añadir el mensaje del usuario al chat
        self.chat_list.add_user_message(message_text, current_time)

        # Manejar diferentes estados de la conversación
        if self.waiting_for_save_confirmation and self.temp_transformed_file and self.transformation_data:
            # Estamos esperando una respuesta sobre qué hacer con el archivo transformado
            self._handle_save_confirmation_response(message_text)
            return
        elif self.waiting_for_constancia_confirmation and self.temp_constancia_file:
            # Estamos esperando confirmación sobre qué hacer con la constancia generada
            self._handle_constancia_confirmation_response(message_text)
            return
        # 🔧 ELIMINAR LÓGICA DE CONFIRMACIÓN PARA CONSTANCIAS
        # elif self.waiting_for_file_open_response and self.last_generated_file:
        #     # Estamos esperando una respuesta sobre si abrir un archivo
        #     self._handle_file_open_response(message_text)
        #     return

        # 🆕 USAR CHATENGINE CENTRALIZADO para mensajes normales
        self._process_message_with_chat_engine(message_text)

    def _handle_file(self, file_path: str) -> bool:
        """Handler para archivos generados por ChatEngine"""
        try:
            import os
            if os.path.exists(file_path):
                # 🔧 ELIMINAR MENSAJES DUPLICADOS - ChatEngine ya maneja el mensaje principal

                # Cargar el PDF en el visor si es un PDF
                if file_path.lower().endswith('.pdf'):
                    self.pdf_panel.show_pdf(file_path)

                    # Expandir panel de PDF si está oculto
                    if not self.pdf_panel_expanded:
                        self.toggle_pdf_panel_visibility()

                # 🔧 NO AGREGAR MENSAJES ADICIONALES - ChatEngine ya los maneja
                # 🎯 NO ESTABLECER ESTADO DE ESPERA PARA CONSTANCIAS

                self.last_generated_file = file_path
                # 🔧 ELIMINAR: self.waiting_for_file_open_response = True
                return True
            else:
                self.logger.error(f"Archivo no encontrado: {file_path}")
                return False

        except Exception as e:
            self.logger.error(f"Error manejando archivo: {e}")
            return False



    def _handle_confirmation(self, message: str) -> bool:
        """Handler para confirmaciones de ChatEngine"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")

        self.chat_list.add_assistant_message(
            f"⚠️ {message}",
            current_time
        )

        # En la interfaz gráfica, siempre confirmar por ahora
        # TODO: Implementar diálogo de confirmación real
        return True

    def _process_message_with_chat_engine(self, message_text: str):
        """🆕 PROCESA MENSAJE DE FORMA ASÍNCRONA SIN BLOQUEAR UI"""
        try:
            self.logger.info(f"🎯 [CHATWINDOW] Procesando: '{message_text}'")

            # 🆕 DESHABILITAR INPUT MIENTRAS SE PROCESA
            self.input_field.setEnabled(False)

            # 🆕 MOSTRAR INDICADOR DE ESCRITURA
            self.typing_indicator.show_typing()

            # 🆕 CONFIGURAR Y INICIAR WORKER ASÍNCRONO
            self.async_worker.set_message(message_text)
            self.async_worker.start()

        except Exception as e:
            self.logger.error(f"❌ Error iniciando procesamiento asíncrono: {e}")
            self._on_processing_error(str(e))

    def _handle_async_response(self, response: ChatResponse):
        """🆕 MANEJA RESPUESTA DEL WORKER ASÍNCRONO"""
        try:
            self.logger.info("✅ [CHATWINDOW] Respuesta recibida")

            # 🆕 SINCRONIZAR CONTEXTO DESPUÉS DEL PROCESAMIENTO ASÍNCRONO
            self._sync_context_from_async_worker()

            self._handle_chat_engine_response(response)
        except Exception as e:
            self.logger.error(f"❌ Error manejando respuesta asíncrona: {e}")
            self._on_processing_error(str(e))

    def _sync_context_from_async_worker(self):
        """🆕 SINCRONIZA CONTEXTO DEL WORKER ASÍNCRONO AL CHAT ENGINE PRINCIPAL"""
        try:
            # 🆕 OBTENER CONTEXTO ACTUALIZADO DEL WORKER
            # Nota: Por ahora, el worker no devuelve el contexto actualizado
            # pero podríamos implementar esto en el futuro para mantener
            # sincronización bidireccional completa

            # 🆕 VERIFICAR SI EL WORKER TIENE CONTEXTO ACTUALIZADO
            if hasattr(self.async_worker, 'last_thread_engine'):
                worker_engine = self.async_worker.last_thread_engine

                if hasattr(worker_engine, 'message_processor'):
                    worker_processor = worker_engine.message_processor
                    main_processor = self.chat_engine.message_processor

                    # Sincronizar conversation_stack si fue actualizado
                    if hasattr(worker_processor, 'conversation_stack'):
                        if worker_processor.conversation_stack:
                            main_processor.conversation_stack = worker_processor.conversation_stack.copy()
                            self.logger.debug(f"🔄 conversation_stack sincronizado: {len(worker_processor.conversation_stack)} niveles")

                    # Sincronizar last_query_results
                    if hasattr(worker_processor, 'last_query_results'):
                        if worker_processor.last_query_results:
                            main_processor.last_query_results = worker_processor.last_query_results
                            self.logger.debug("🔄 last_query_results sincronizado")

                    # ✅ CONTEXTO SINCRONIZADO

            self.logger.debug("✅ Contexto sincronizado desde worker")

        except Exception as e:
            self.logger.error(f"❌ Error sincronizando contexto: {e}")

    def _on_processing_started(self):
        """🆕 CALLBACK CUANDO INICIA EL PROCESAMIENTO"""
        self.statusBar().showMessage("Procesando mensaje...")

    def _on_processing_finished(self):
        """🆕 CALLBACK CUANDO TERMINA EL PROCESAMIENTO"""
        # 🆕 OCULTAR INDICADOR DE ESCRITURA
        self.typing_indicator.hide_typing()

        # 🆕 REHABILITAR INPUT
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

        # 🆕 ACTUALIZAR STATUS BAR
        self.statusBar().showMessage("Listo")

    def _on_processing_error(self, error_message: str):
        """🆕 CALLBACK CUANDO OCURRE ERROR EN PROCESAMIENTO"""
        self.logger.error(f"❌ Error en procesamiento: {error_message}")

        # 🆕 OCULTAR INDICADOR DE ESCRITURA
        self.typing_indicator.hide_typing()

        # 🆕 REHABILITAR INPUT
        self.input_field.setEnabled(True)
        self.input_field.setFocus()

        # 🆕 MOSTRAR ERROR EN CHAT
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.chat_list.add_assistant_message(
            f"❌ Error procesando mensaje: {error_message}",
            current_time
        )

        # 🆕 ACTUALIZAR STATUS BAR
        self.statusBar().showMessage("Error en procesamiento")

    def _handle_chat_engine_response(self, response: ChatResponse):
        """Maneja respuesta de ChatEngine con formateo automático mejorado"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")

        # 🔧 LOGS INFORMATIVOS - RESPUESTA RECIBIDA EN UI
        from app.core.logging import debug_detailed
        debug_detailed(self.logger, f"🔧 [UI] Respuesta recibida del ChatEngine:")
        debug_detailed(self.logger, f"   ├── Acción: {response.action}")
        debug_detailed(self.logger, f"   ├── Estado: {'✅ Exitosa' if response.success else '❌ Error'}")
        debug_detailed(self.logger, f"   ├── Contenido: {len(response.text)} caracteres")
        debug_detailed(self.logger, f"   └── Datos: {len(response.data.keys()) if response.data else 0} campos → Procesando para mostrar")

        # 🎨 FORMATEO AUTOMÁTICO - SIEMPRE MOSTRAR RESPUESTA DEL MASTER
        should_show_text = (
            response.text and (
                # ✅ SIEMPRE mostrar texto del Master cuando existe
                True or
                # SIEMPRE mostrar texto para constancias y transformaciones
                response.action in ["constancia_preview", "transformation_preview", "pdf_transformation"]
            )
        )

        if should_show_text:
            # 🆕 USAR FORMATEO AUTOMÁTICO CON DETECCIÓN INTELIGENTE
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [UI] Mostrando texto formateado ({len(response.text)} chars)")
            formatted_text = self.response_formatter.format_response(response.text, "auto")
            self.chat_list.add_assistant_message(formatted_text, current_time)
        else:
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [UI] Texto omitido → Priorizando datos estructurados")

        # 🆕 MANEJAR CONSTANCIAS GENERADAS
        if response.action == "constancia_preview" and response.data:
            self._handle_constancia_preview_from_engine(response.data, response.files)
        elif response.action in ["pdf_transformation", "transformation_preview"] and response.data:
            self._handle_transformation_preview_from_engine(response.data, response.files)
        # 🔧 MANEJAR ARCHIVOS SOLO SI CHATENGINE NO LOS PROCESÓ
        elif response.files and response.action != "open_file":
            # Solo procesar archivos si ChatEngine no los detectó como archivos generados
            for file_path in response.files:
                self._handle_file(file_path)
        elif response.action == "open_file" and response.files:
            # ChatEngine ya procesó el archivo y modificó el mensaje
            # Solo cargar en el visor y preguntar por apertura
            for file_path in response.files:
                self._handle_file(file_path)

        # Manejar datos estructurados
        if response.action == "show_data" and response.data:
            self._display_structured_data(response.data)

    def _display_structured_data(self, data: dict):
        """🎯 MUESTRA DATOS ESTRUCTURADOS USANDO GESTOR CENTRALIZADO"""
        try:
            # 🎯 USAR DATA DISPLAY MANAGER CENTRALIZADO
            success = self.data_display_manager.display_data(data)

            if not success:
                self.logger.warning("DataDisplayManager no pudo mostrar los datos, usando fallback")
                self._display_structured_data_fallback(data)

        except Exception as e:
            self.logger.error(f"Error en DataDisplayManager: {e}")
            self._display_structured_data_fallback(data)

    def _display_structured_data_fallback(self, data: dict):
        """🔧 FALLBACK PARA MOSTRAR DATOS SI FALLA EL GESTOR CENTRALIZADO"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")

        if "alumno" in data:
            # Mostrar detalles de un solo alumno
            self.mostrar_detalle_alumno(data["alumno"])
        elif "alumnos" in data:
            # Mostrar lista de alumnos
            alumnos = data["alumnos"]
            if alumnos:
                self.mostrar_alumnos_tabla(alumnos)
        else:
            # 🎯 DATOS GENÉRICOS - FORMATEAR MEJOR EN LUGAR DE MOSTRAR JSON CRUDO
            self._format_and_display_generic_data(data, current_time)

    def _format_and_display_generic_data(self, data: dict, current_time: str):
        """Formatea y muestra datos genéricos de manera visual atractiva"""
        try:
            # 🎯 FORMATEO INTELIGENTE SEGÚN EL TIPO DE DATOS

            # Si contiene información de ayuda/capacidades
            if 'capabilities' in data and 'auto_reflexion' in data:
                # NO MOSTRAR NADA ADICIONAL - La respuesta principal ya es completa
                return

            # Si contiene información de constancia
            elif 'constancia_info' in data:
                self._display_constancia_info(data['constancia_info'], current_time)

            # Si contiene estadísticas
            elif 'estadisticas' in data:
                self._display_statistics(data['estadisticas'], current_time)

            # Si contiene información de error específica
            elif 'error_details' in data:
                self._display_error_details(data['error_details'], current_time)

            # Para otros tipos de datos, mostrar de forma limpia
            else:
                self._display_clean_data_summary(data, current_time)

        except Exception as e:
            self.logger.error(f"Error formateando datos genéricos: {e}")
            # En caso de error, no mostrar nada en lugar de JSON crudo

    def _display_clean_data_summary(self, data: dict, current_time: str):
        """Muestra resumen limpio de datos sin JSON crudo"""
        try:
            # Extraer información relevante sin mostrar JSON
            summary_items = []

            if 'message' in data:
                # Ya se mostró el mensaje principal, no duplicar
                return

            if 'total_records' in data:
                summary_items.append(f"📊 Total de registros: {data['total_records']}")

            if 'query_type' in data:
                summary_items.append(f"🔍 Tipo de consulta: {data['query_type']}")

            if summary_items:
                summary_text = "\n".join(summary_items)
                self.chat_list.add_assistant_message(summary_text, current_time)

        except Exception as e:
            self.logger.error(f"Error en resumen de datos: {e}")

    def _determine_response_type(self, response: ChatResponse) -> str:
        """Determina el tipo de respuesta para aplicar el formato correcto"""
        try:
            # Validar que response.action no sea None
            action = response.action if response.action else ""

            # Determinar tipo basado en la acción
            if action in ["ayuda_funcionalidades", "ayuda_ejemplo", "ayuda_solucion"]:
                return "help"
            elif action == "show_data":
                return "data"
            elif action and "error" in action.lower():
                return "error"
            elif action in ["constancia_preview", "pdf_transformation", "transformation_preview"]:
                return "success"
            else:
                # Determinar por contenido del texto
                text_lower = response.text.lower() if response.text else ""

                if any(word in text_lower for word in ["error", "❌", "falló", "problema"]):
                    return "error"
                elif any(word in text_lower for word in ["✅", "éxito", "generado", "completado"]):
                    return "success"
                elif any(word in text_lower for word in ["ayuda", "puedo", "capacidades", "funciones"]):
                    return "help"
                elif any(word in text_lower for word in ["encontré", "resultados", "alumnos", "datos"]):
                    return "data"
                else:
                    return "general"

        except Exception as e:
            self.logger.error(f"Error determinando tipo de respuesta: {e}")
            return "general"

    def _handle_constancia_preview_from_engine(self, data: dict, files: list):
        """Maneja vista previa de constancia generada desde ChatEngine"""
        try:
            if files and len(files) > 0:
                constancia_file = files[0]

                # Guardar archivo temporal
                self.temp_constancia_file = constancia_file

                # Establecer contexto de constancia
                alumno_data = data.get("alumno", {})
                self.pdf_panel.set_constancia_context(alumno_data)

                # Mostrar PDF en el panel
                success = self.pdf_panel.show_pdf(constancia_file)

                if success:
                    # Expandir panel de PDF si está oculto
                    if not self.pdf_panel_expanded:
                        self.toggle_pdf_panel_visibility()

                    # Mostrar opciones de confirmación
                    self._show_constancia_preview_options()
                else:
                    self.logger.error(f"Error cargando vista previa de constancia: {constancia_file}")

        except Exception as e:
            self.logger.error(f"Error manejando vista previa de constancia: {e}")

    def _handle_transformation_preview_from_engine(self, data: dict, files: list):
        """Maneja vista previa de transformación PDF desde ChatEngine"""
        try:
            if files and len(files) > 0:
                transformed_file = files[0]

                # Guardar archivo temporal
                self.temp_transformed_file = transformed_file

                # Establecer contexto de transformación
                original_data = data.get("datos_originales", {})
                transformed_data = data.get("datos_transformados", {})
                self.pdf_panel.set_transformation_context(original_data, transformed_data)

                # Mostrar PDF en el panel
                success = self.pdf_panel.show_pdf(transformed_file)

                if success:
                    # Expandir panel de PDF si está oculto
                    if not self.pdf_panel_expanded:
                        self.toggle_pdf_panel_visibility()

                    # 🔧 NO MOSTRAR OPCIONES - EL MASTER YA GENERÓ EL MENSAJE COMPLETO
                    # self._show_transformation_options()  # ← COMENTADO
                else:
                    self.logger.error(f"Error cargando vista previa de transformación: {transformed_file}")

        except Exception as e:
            self.logger.error(f"Error manejando vista previa de transformación: {e}")

    def _handle_save_confirmation_response(self, message_text):
        """Maneja la respuesta del usuario sobre qué hacer con el archivo transformado.

        Analiza el mensaje del usuario para determinar qué acción realizar con el archivo
        PDF transformado. Las opciones son: guardar el archivo, abrirlo directamente,
        guardar los datos en la base de datos, o no hacer nada.

        Args:
            message_text (str): El mensaje del usuario con la respuesta.

        Returns:
            None
        """
        # Normalizar el texto del mensaje para facilitar la comparación
        normalized_text = message_text.lower().strip()

        # Manejar las diferentes opciones
        if normalized_text in ["1", "guardar", "guardar archivo", "guardar constancia", "guardar pdf"]:
            self._save_transformed_file()
        elif normalized_text in ["2", "abrir", "imprimir", "abrir/imprimir", "abrir e imprimir",
                                "abrir directamente", "abrir archivo", "abrir pdf",
                                "imprimir archivo", "imprimir constancia", "imprimir pdf"]:
            self._open_transformed_file()
        elif normalized_text in ["3", "guardar datos", "registrar", "base de datos",
                                "guardar en base de datos", "registrar datos"]:
            self._save_data_to_database()
        elif normalized_text in ["4", "nada", "no hacer nada", "solo ver", "vista previa"]:
            self._do_nothing_with_file()
        else:
            self._show_invalid_option_message()
            return  # No restablecer el estado para permitir otro intento

        # Restablecer el estado de confirmación
        self.waiting_for_save_confirmation = False

    def _save_transformed_file(self):
        """Guarda el archivo transformado permanentemente.

        Copia el archivo PDF transformado desde su ubicación temporal a una ubicación
        permanente en el directorio 'constancias'. El nombre del archivo incluye la
        fecha y hora actual para evitar sobrescrituras.

        Después de guardar el archivo, pregunta al usuario si desea abrirlo.

        Returns:
            None

        Raises:
            Exception: Si ocurre un error al copiar el archivo, se muestra un mensaje
                      de error en el chat pero no se propaga la excepción.
        """
        import os
        import shutil
        from datetime import datetime

        # Crear un nombre de archivo con fecha y hora
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"constancia_{now}.pdf"
        output_dir = os.path.join(os.getcwd(), "constancias")

        # Asegurarse de que el directorio exista
        os.makedirs(output_dir, exist_ok=True)

        # Ruta de destino
        dest_path = os.path.join(output_dir, filename)

        # Copiar el archivo temporal al destino permanente
        try:
            shutil.copy2(self.temp_transformed_file, dest_path)
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")

            self.chat_list.add_assistant_message(
                f"✅ Archivo guardado correctamente en: {dest_path}",
                current_time
            )

            # Actualizar la ruta del archivo para posible apertura
            self.last_generated_file = dest_path

            # Preguntar si desea abrir el archivo
            self.chat_list.add_assistant_message(
                "¿Deseas abrir el archivo? Responde 'sí' o 'no'.",
                current_time
            )
            self.waiting_for_file_open_response = True
        except Exception as e:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.chat_list.add_assistant_message(
                f"❌ Error al guardar el archivo: {str(e)}",
                current_time
            )

    def _open_transformed_file(self):
        """Abre el archivo transformado sin guardarlo.

        Abre el archivo PDF transformado con la aplicación predeterminada del sistema
        para visualización e impresión. El archivo permanece en su ubicación temporal
        y se eliminará cuando se cierre la aplicación.

        El método utiliza diferentes enfoques según el sistema operativo:
        - En Windows: Utiliza el comando 'start' para abrir el archivo.
        - En macOS/Linux: Utiliza la función open_file_with_default_app.

        Returns:
            None

        Raises:
            Exception: Si ocurre un error al abrir el archivo, se muestra un mensaje
                      de error en el chat pero no se propaga la excepción.
        """
        try:
            import subprocess
            import platform
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")

            # En Windows, usar el comando predeterminado para abrir (que permite imprimir)
            if platform.system() == "Windows":
                subprocess.Popen(['start', '', self.temp_transformed_file], shell=True)
                self.chat_list.add_assistant_message(
                    "✅ Abriendo el archivo en el navegador. Desde allí puedes verlo o imprimirlo.",
                    current_time
                )
                self.chat_list.add_assistant_message(
                    "Recuerda que este archivo es temporal y se eliminará al cerrar la aplicación.",
                    current_time
                )
            else:  # macOS o Linux
                from app.core.utils import open_file_with_default_app
                open_file_with_default_app(self.temp_transformed_file)
                self.chat_list.add_assistant_message(
                    "✅ Abriendo el archivo en el navegador. Desde allí puedes verlo o imprimirlo.",
                    current_time
                )
                self.chat_list.add_assistant_message(
                    "Recuerda que este archivo es temporal y se eliminará al cerrar la aplicación.",
                    current_time
                )
        except Exception as e:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.chat_list.add_assistant_message(
                f"❌ Error al abrir el archivo: {str(e)}",
                current_time
            )

    def _save_data_to_database(self):
        """Guarda los datos extraídos en la base de datos"""
        try:
            # Ejecutar el comando para guardar los datos
            from app.core.commands.constancia_commands import TransformarConstanciaCommand

            # Obtener los parámetros de la transformación
            ruta_archivo = self.temp_transformed_file
            tipo_destino = self.transformation_data.get("tipo_destino", "estudio")
            incluir_foto = self.transformation_data.get("incluir_foto", False)

            # Crear y ejecutar el comando con guardar_alumno=True
            command = TransformarConstanciaCommand(ruta_archivo, tipo_destino, incluir_foto, guardar_alumno=True)
            success, message, data = command.execute()

            if success:
                self.chat_list.add_assistant_message(
                    "✅ Datos guardados correctamente en la base de datos.",
                    self._get_current_time()
                )

                # Si hay datos del alumno, mostrarlos
                if "alumno" in data:
                    self.mostrar_detalle_alumno(data["alumno"])
            else:
                self.chat_list.add_assistant_message(
                    f"❌ Error al guardar los datos: {message}",
                    self._get_current_time()
                )
        except Exception as e:
            self.chat_list.add_assistant_message(
                f"❌ Error al guardar los datos: {str(e)}",
                self._get_current_time()
            )

    def _do_nothing_with_file(self):
        """No hace nada con el archivo, solo mantiene la vista previa"""
        self.chat_list.add_assistant_message(
            "✅ De acuerdo, no guardaré el archivo ni los datos. La vista previa seguirá disponible hasta que cierres la aplicación o cargues otro PDF.",
            self._get_current_time()
        )

    def _show_invalid_option_message(self):
        """Muestra un mensaje de error por opción no válida"""
        # Mensaje de error si la opción no es reconocida
        self.chat_list.add_assistant_message("""
        <div style="background-color: #E74C3C; border: 1px solid #C0392B; border-radius: 8px; padding: 10px; color: white;">
        <p><b>⚠️ Opción no reconocida</b></p>
        <p>Por favor, responde con un número del 1 al 4 o con el nombre de una de las opciones disponibles.</p>
        </div>
        """, self._get_current_time())

        # Mostrar nuevamente las opciones con un mensaje más simple
        self.chat_list.add_assistant_message("""<div style="background-color: #2C3E50; border: 1px solid #34495E; border-radius: 8px; padding: 15px; color: #FFFFFF;">
<p>Por favor, selecciona una de estas opciones:</p>
<p><b style="color: #88CCFF;">1.</b> Guardar archivo</p>
<p><b style="color: #88CCFF;">2.</b> Abrir/Imprimir</p>
<p><b style="color: #88CCFF;">3.</b> Guardar datos</p>
<p><b style="color: #88CCFF;">4.</b> Nada</p>
</div>""", self._get_current_time())

    def _handle_file_open_response(self, message_text):
        """Maneja la respuesta del usuario sobre si abrir un archivo"""
        if message_text.lower() in ["sí", "si", "yes", "s", "y"]:
            # Abrir el archivo
            try:
                open_file_with_default_app(self.last_generated_file)
                self.chat_list.add_assistant_message(
                    "Abriendo el archivo para ti. ¡Espero que te sea útil!",
                    self._get_current_time()
                )
            except Exception as e:
                self.chat_list.add_assistant_message(
                    f"No pude abrir el archivo: {str(e)}",
                    self._get_current_time()
                )
        else:
            # No abrir el archivo
            self.chat_list.add_assistant_message(
                "De acuerdo, no abriré el archivo. ¿Hay algo más en lo que pueda ayudarte?",
                self._get_current_time()
            )

        # Restablecer el estado
        self.waiting_for_file_open_response = False

    def _get_current_time(self):
        """Obtiene la hora actual en formato HH:MM:SS"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    # ❌ MÉTODO OBSOLETO - Eliminado: _process_normal_message
    # Ahora se usa _process_message_with_chat_engine

    # ❌ MÉTODO OBSOLETO - Eliminado: handle_gemini_response
    # Ahora se usa _handle_chat_engine_response

    def _handle_transform_constancia(self, parametros):
        """Maneja la transformación de una constancia.

        Este método coordina el proceso de transformación de un PDF de constancia
        a otro formato. El proceso incluye:
        1. Verificar que haya un PDF cargado
        2. Configurar los parámetros de transformación
        3. Ejecutar la transformación
        4. Manejar el resultado (éxito o fracaso)

        Args:
            parametros (dict): Diccionario con los parámetros de transformación.
                Puede incluir 'tipo_destino', 'incluir_foto', etc.

        Returns:
            None
        """
        # PASO 1: Verificar que haya un PDF cargado en el panel
        current_pdf = self.pdf_panel.get_current_pdf()
        if not current_pdf:
            self.chat_list.add_assistant_message(
                "Error: No hay ningún PDF cargado para transformar.",
                self._get_current_time()
            )
            return

        # PASO 2: Preparar el entorno para la transformación
        temp_dir, tipo_destino, incluir_foto = self._setup_transformation_params(parametros, current_pdf)

        # PASO 3: Informar al usuario sobre la transformación que se va a realizar
        self._show_transformation_info(tipo_destino, incluir_foto)

        # PASO 4: Ejecutar la transformación real del PDF
        success, message, data = self._execute_transformation(current_pdf, temp_dir)

        # PASO 5: Manejar el resultado según sea exitoso o no
        if success and "ruta_archivo" in data:
            # Si la transformación fue exitosa y tenemos un archivo resultante
            self._handle_successful_transformation(data)
        else:
            # Si hubo algún error durante la transformación
            self._handle_failed_transformation(message)

    def _setup_transformation_params(self, parametros, current_pdf):
        """Configura los parámetros para la transformación"""
        import tempfile

        # Crear un directorio temporal para la vista previa
        temp_dir = tempfile.mkdtemp(prefix="constancia_preview_")

        # Obtener los parámetros de transformación
        tipo_destino = parametros.get("tipo_destino", "estudio")

        # Determinar si se debe incluir foto (por defecto True para constancias de estudio)
        incluir_foto = parametros.get("incluir_foto")

        if incluir_foto is None:  # Si no se especificó, usar el valor predeterminado según el tipo
            incluir_foto = (tipo_destino.lower() == "estudio")

        # Guardar los parámetros originales para usarlos después
        self.transformation_data = {
            "tipo_destino": tipo_destino,
            "incluir_foto": incluir_foto,
            "guardar_alumno": parametros.get("guardar_alumno", False),
            "ruta_archivo": current_pdf
        }

        return temp_dir, tipo_destino, incluir_foto

    def _show_transformation_info(self, tipo_destino, incluir_foto):
        """Muestra información sobre la transformación que se va a realizar"""
        info_message = f"Transformando constancia a formato '{tipo_destino}'"
        if incluir_foto:
            info_message += " con foto"
        else:
            info_message += " sin foto"
        self.chat_list.add_assistant_message(info_message, self._get_current_time())

    def _execute_transformation(self, current_pdf, temp_dir):
        """Ejecuta la transformación de la constancia"""
        from app.core.service_provider import ServiceProvider

        constancia_service = ServiceProvider.get_instance().constancia_service

        # Generar vista previa (preview_mode=True)
        try:
            result = constancia_service.generar_constancia_desde_pdf(
                current_pdf,
                self.transformation_data["tipo_destino"],
                self.transformation_data["incluir_foto"],
                guardar_alumno=False,
                preview_mode=True,
                output_dir=temp_dir
            )
            return result
        except Exception as e:
            return False, f"Error en transformación: {str(e)}", {}

    def _handle_successful_transformation(self, data):
        """Maneja una transformación exitosa"""
        # Guardar la ruta del archivo temporal
        self.temp_transformed_file = data["ruta_archivo"]

        # Mostrar mensaje de éxito
        self.chat_list.add_assistant_message(
            "✅ Transformación completada exitosamente.",
            self._get_current_time()
        )
        self.chat_list.add_assistant_message(
            "He generado una vista previa de la constancia transformada.",
            self._get_current_time()
        )

        # Establecer contexto de transformación con datos originales y transformados
        original_data = data.get("datos_originales", {})
        transformed_data = {
            "tipo_constancia": self.transformation_data.get("tipo_destino", ""),
            "incluir_foto": self.transformation_data.get("incluir_foto", False),
            "guardar_alumno": self.transformation_data.get("guardar_alumno", False),
            "nombre": original_data.get("nombre", ""),
            "curp": original_data.get("curp", "")
        }

        self.pdf_panel.set_transformation_context(original_data, transformed_data)

        # Cargar el PDF en el visor
        success = self.pdf_panel.show_pdf(self.temp_transformed_file)
        self.logger.debug(f"Vista previa de transformación cargada: {success}")

        # Mostrar opciones y esperar confirmación
        self._show_transformation_options()

    def _handle_constancia_preview(self, data):
        """Maneja la vista previa de una constancia generada"""
        self.logger.debug("_handle_constancia_preview ejecutándose")
        self.logger.debug(f"Datos: {data}")

        # Guardar la ruta del archivo temporal
        self.temp_constancia_file = data["ruta_archivo"]
        self.logger.debug(f"Archivo temporal: {self.temp_constancia_file}")

        # Mostrar información del alumno
        if "alumno" in data:
            alumno = data["alumno"]
            self.chat_list.add_assistant_message(
                f"He generado una vista previa de la constancia para **{alumno.get('nombre', 'N/A')}**.",
                self._get_current_time()
            )

        # Establecer contexto de constancia generada
        self.pdf_panel.set_constancia_context(data.get("alumno", {}))

        # Cargar el PDF usando el método estándar
        success = self.pdf_panel.show_pdf(self.temp_constancia_file)

        self.logger.debug(f"Vista previa cargada: {success}")

        # Mostrar opciones de confirmación
        self._show_constancia_preview_options()

    def _show_constancia_preview_options(self):
        """
        🗑️ FUNCIÓN DESHABILITADA: Las opciones ya están en el panel derecho

        Anteriormente mostraba opciones duplicadas:
        - "Confirmar" - Guardar la constancia definitivamente
        - "Abrir en navegador" - Ver/imprimir sin guardar
        - "Cancelar" - Descartar la constancia

        Ahora solo usamos la respuesta humanizada del Student que menciona el panel.
        """
        # 🎯 SOLO MARCAR QUE ESTAMOS ESPERANDO CONFIRMACIÓN
        # No mostrar mensaje adicional - el Student ya generó respuesta humanizada
        self.waiting_for_constancia_confirmation = True

        self.logger.info("🎯 [CONSTANCIA] Esperando confirmación del usuario (sin mensaje adicional)")

    def _show_transformation_options(self):
        """
        🗑️ FUNCIÓN DESHABILITADA: Las opciones ya están en el panel derecho

        Anteriormente mostraba opciones duplicadas:
        - "Guardar archivo" - Guardar la constancia como PDF permanente
        - "Abrir/Imprimir" - Abrir en navegador para ver o imprimir
        - "Guardar datos" - Registrar los datos extraídos del PDF original
        - "Nada" - Solo ver la vista previa

        Ahora solo usamos la respuesta humanizada del Student que menciona el panel.
        """
        # 🎯 SOLO MARCAR QUE ESTAMOS ESPERANDO CONFIRMACIÓN
        # No mostrar mensaje adicional - el Student ya generó respuesta humanizada
        self.waiting_for_save_confirmation = True

        self.logger.info("🎯 [TRANSFORMACIÓN] Esperando confirmación del usuario (sin mensaje adicional)")

    def _handle_failed_transformation(self, message):
        """Maneja una transformación fallida"""
        error_msg = message if message else "Error al transformar la constancia."
        self.chat_list.add_assistant_message(
            f"Error: {error_msg}",
            self._get_current_time()
        )

    def _handle_constancia_confirmation_response(self, message_text):
        """Maneja la respuesta del usuario sobre qué hacer con la constancia generada"""
        normalized_text = message_text.lower().strip()

        if normalized_text in ["confirmar", "sí", "si", "yes", "guardar", "confirmo", "ok"]:
            self._save_constancia_definitively()
        elif normalized_text in ["abrir", "abrir en navegador", "ver", "imprimir"]:
            self._open_constancia_file()
        elif normalized_text in ["cancelar", "no", "descartar", "cancel"]:
            self._cancel_constancia()
        else:
            self.chat_list.add_assistant_message(
                "No entendí tu respuesta. Por favor responde 'confirmar', 'abrir en navegador' o 'cancelar'.",
                self._get_current_time()
            )
            return  # No restablecer el estado para permitir otro intento

        # Restablecer el estado de confirmación
        self.waiting_for_constancia_confirmation = False

    def _save_constancia_definitively(self):
        """Guarda la constancia definitivamente"""
        import os
        import shutil
        from datetime import datetime

        try:
            # Crear un nombre de archivo con fecha y hora
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"constancia_{now}.pdf"
            output_dir = os.path.join(os.getcwd(), "constancias")

            # Asegurarse de que el directorio exista
            os.makedirs(output_dir, exist_ok=True)

            # Ruta de destino
            dest_path = os.path.join(output_dir, filename)

            # Copiar el archivo temporal al destino permanente
            shutil.copy2(self.temp_constancia_file, dest_path)

            self.chat_list.add_assistant_message(
                f"✅ Constancia guardada correctamente en: {dest_path}",
                self._get_current_time()
            )

            # Preguntar si desea abrir el archivo
            self.chat_list.add_assistant_message(
                "¿Deseas abrir el archivo? Responde 'sí' o 'no'.",
                self._get_current_time()
            )
            self.last_generated_file = dest_path
            self.waiting_for_file_open_response = True

        except Exception as e:
            self.chat_list.add_assistant_message(
                f"❌ Error al guardar la constancia: {str(e)}",
                self._get_current_time()
            )

    def _open_constancia_file(self):
        """Abre la constancia temporal sin guardarla"""
        try:
            import subprocess
            import platform

            if platform.system() == "Windows":
                subprocess.Popen(['start', '', self.temp_constancia_file], shell=True)
            else:
                from app.core.utils import open_file_with_default_app
                open_file_with_default_app(self.temp_constancia_file)

            self.chat_list.add_assistant_message(
                "✅ Abriendo la constancia en el navegador. Desde allí puedes verla o imprimirla.",
                self._get_current_time()
            )
            self.chat_list.add_assistant_message(
                "Recuerda que este archivo es temporal y se eliminará al cerrar la aplicación.",
                self._get_current_time()
            )
        except Exception as e:
            self.chat_list.add_assistant_message(
                f"❌ Error al abrir la constancia: {str(e)}",
                self._get_current_time()
            )

    def _cancel_constancia(self):
        """Cancela la constancia generada"""
        self.chat_list.add_assistant_message(
            "✅ Constancia cancelada. El archivo temporal se eliminará automáticamente.",
            self._get_current_time()
        )





    def _display_additional_data(self, data):
        """Muestra datos adicionales según el tipo de comando"""
        if "alumno" in data:
            # Mostrar detalles de un solo alumno
            alumno = data["alumno"]

            # Si no tiene datos escolares completos, obtenerlos de la BD
            if not alumno.get('grado') or alumno.get('grado') == 'No disponible':
                try:
                    alumno_id = alumno.get('id')
                    if alumno_id:
                        # Obtener datos completos desde el servicio
                        from app.core.service_provider import ServiceProvider
                        service_provider = ServiceProvider.get_instance()
                        alumno_completo = service_provider.alumno_service.get_alumno(alumno_id)
                        if alumno_completo:
                            alumno = alumno_completo
                except Exception as e:
                    self.logger.error(f"Error al obtener datos completos del alumno: {e}")

            self.mostrar_detalle_alumno(alumno)
        elif "alumnos" in data:
            alumnos = data["alumnos"]
            if alumnos:
                # Mostrar alumnos en formato tabular
                self.mostrar_alumnos_tabla(alumnos)





    def handle_gemini_error(self, error_message):
        """Maneja errores en la comunicación con Gemini"""
        # Ocultar la barra de progreso
        self.progress_bar.setVisible(False)

        # Mostrar mensaje de error
        self.chat_list.add_assistant_message(f"Lo siento, ocurrió un error: {error_message}", self._get_current_time())
        self.chat_list.add_assistant_message("Por favor, intenta de nuevo más tarde.", self._get_current_time())

    def on_pdf_loaded(self):
        """Se llama cuando se carga un PDF en el panel"""
        # Mostrar el panel de PDF si está oculto
        if not self.pdf_panel_expanded:
            self.toggle_pdf_panel_visibility()

        # Mostrar un mensaje en la barra de estado (si existe)
        if hasattr(self, 'statusBar'):
            self.statusBar().showMessage("PDF cargado correctamente", 3000)

    def toggle_pdf_panel_visibility(self):
        """Muestra u oculta el panel de PDF"""
        # Cambiar el estado
        self.pdf_panel_expanded = not self.pdf_panel_expanded

        # Usar la referencia directa al splitter
        if not hasattr(self, 'main_splitter'):
            return

        # Asegurarse de que el panel de PDF esté visible
        self.pdf_panel.setVisible(True)

        # Obtener el ancho total disponible
        total_width = self.main_splitter.width()

        # Ajustar los tamaños según el estado
        if self.pdf_panel_expanded:
            # Expandir el panel de PDF con una proporción más adecuada
            # Asignar 60% al chat y 40% al panel de PDF
            chat_width = int(total_width * 0.6)
            pdf_width = total_width - chat_width

            # Establecer tamaños mínimos para evitar que se comprima demasiado
            if chat_width < 500:
                chat_width = 500
                pdf_width = max(300, total_width - chat_width)

            self.main_splitter.setSizes([chat_width, pdf_width])

            # Actualizar el estado del botón en la barra de herramientas
            self.pdf_action.setChecked(True)
            self.pdf_action.setText("✖ Cerrar panel de transformación")
        else:
            # Colapsar el panel de PDF
            self.main_splitter.setSizes([total_width, 0])

            # Actualizar el estado del botón en la barra de herramientas
            self.pdf_action.setChecked(False)
            self.pdf_action.setText("🔄 Transformación de PDF")

    def mostrar_ayuda(self):
        """Muestra información de ayuda sobre el sistema"""
        # Versión compacta del HTML sin espacios innecesarios
        ayuda_html = """<div style="background-color: #2C3E50; border: 1px solid #34495E; border-radius: 8px; padding: 15px; margin-bottom: 10px; color: #FFFFFF;">
<h3 style="color: #7FB3D5; margin-top: 0; margin-bottom: 10px;">🤖 ¿Qué puedo hacer por ti?</h3>
<h4 style="color: #88CCFF; margin-top: 15px;">Gestión de Alumnos</h4>
<ul style="margin-top: 5px; margin-bottom: 5px;">
<li><b>Buscar alumnos</b> por nombre o CURP: "Busca al alumno Juan Pérez" o "Busca CURP ABCD123456"</li>
<li><b>Buscar por criterios</b>: "Muestra alumnos de primer grado" o "Alumnos del grupo B"</li>
<li><b>Registrar alumnos</b>: "Registra un nuevo alumno con nombre..."</li>
<li><b>Actualizar datos</b>: "Actualiza los datos del alumno Juan Pérez..."</li>
<li><b>Eliminar alumnos</b>: "Elimina al alumno con ID 5"</li>
</ul>
<h4 style="color: #88CCFF; margin-top: 15px;">Constancias</h4>
<ul style="margin-top: 5px; margin-bottom: 5px;">
<li><b>Generar constancias</b>: "Genera constancia de estudios para Juan Pérez"</li>
<li><b>Transformar PDFs</b>: Haz clic en "🔄 Transformación de PDF" en la barra superior, carga un PDF y pide "Transforma este PDF a constancia de estudios"</li>
</ul>
<h4 style="color: #88CCFF; margin-top: 15px;">Consultas</h4>
<ul style="margin-top: 5px; margin-bottom: 5px;">
<li><b>Información específica</b>: "¿Cuál es la CURP de Juan Pérez?" o "¿En qué grado está María?"</li>
<li><b>Detalles completos</b>: "Muestra los detalles del alumno Juan Pérez"</li>
</ul>
</div>"""
        self.chat_list.add_assistant_message(ayuda_html, self._get_current_time())

    def mostrar_alumnos_tabla(self, alumnos):
        """Muestra los alumnos en formato tabular optimizado para grandes volúmenes"""
        if not alumnos:
            self.chat_list.add_assistant_message("No se encontraron alumnos.", self._get_current_time())
            return

        total_alumnos = len(alumnos)

        # Para muchos alumnos, usar formato compacto y paginación
        if total_alumnos > 50:
            self._mostrar_tabla_grande(alumnos)
        elif total_alumnos > 10:
            self._mostrar_tabla_mediana(alumnos)
        else:
            self._mostrar_tabla_pequena(alumnos)

    def _mostrar_tabla_grande(self, alumnos):
        """Muestra tabla optimizada para 50+ alumnos con paginación mejorada"""
        total = len(alumnos)
        limite_por_pagina = 25  # 🎯 REDUCIDO: Mejor legibilidad

        # 🎨 HEADER MEJORADO CON MEJOR FORMATO
        texto = f"""
📊 **RESULTADOS DE BÚSQUEDA**
{'═' * 60}
📈 **Total encontrados:** {total} alumnos
📋 **Mostrando:** Primeros {min(limite_por_pagina, total)} resultados

"""

        # 🎯 FORMATO MEJORADO PARA CADA ALUMNO
        for i, alumno in enumerate(alumnos[:limite_por_pagina], 1):
            nombre = alumno.get('nombre', '').upper()
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')[:3] if alumno.get('turno') else ''
            curp = alumno.get('curp', '')

            # 🎨 FORMATO VISUAL MEJORADO
            texto += f"**{i:2d}.** {nombre}\n"
            texto += f"     🎓 {grado}° {grupo} - {turno}  •  📋 {curp}\n\n"

        # 🎯 MENSAJE DE AYUDA MEJORADO
        if total > limite_por_pagina:
            restantes = total - limite_por_pagina
            texto += f"""{'─' * 60}
💡 **Hay {restantes} alumnos más disponibles**

**Para ver más resultados:**
• "Mostrar más alumnos" - Ver siguientes {min(25, restantes)}
• "Buscar [nombre específico]" - Encontrar alumno exacto
• "Alumnos de [grado]° [grupo]" - Filtrar por grado/grupo
• "Detalles de [nombre completo]" - Ver información completa

"""

        # 🎨 APLICAR FORMATEO AUTOMÁTICO (ahora es necesario porque no se formatea en _handle_chat_engine_response)
        formatted_texto = self.response_formatter.format_response(texto, "auto")
        self.chat_list.add_assistant_message(formatted_texto, self._get_current_time())

    def _mostrar_tabla_mediana(self, alumnos):
        """Muestra tabla estándar para 10-50 alumnos con formato mejorado"""
        total = len(alumnos)

        # 🎨 HEADER MEJORADO
        texto = f"""
🔍 **ALUMNOS ENCONTRADOS**
{'═' * 45}
📊 **Total:** {total} estudiantes

"""

        # 🎯 FORMATO MEJORADO PARA CADA ALUMNO
        for i, alumno in enumerate(alumnos, 1):
            nombre = alumno.get('nombre', '').upper()
            curp = alumno.get('curp', '')
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')[:3] if alumno.get('turno') else ''

            # 🎨 FORMATO VISUAL MEJORADO
            texto += f"**{i:2d}.** {nombre}\n"
            texto += f"     🎓 {grado}° {grupo} - {turno}  •  📋 {curp}\n\n"

        # 🎯 MENSAJE DE AYUDA PARA LISTAS MEDIANAS
        texto += f"""{'─' * 45}
💡 **Opciones disponibles:**
• "Detalles de [nombre]" - Ver información completa
• "Constancia para [nombre]" - Generar constancia
• "Número [X]" - Seleccionar alumno por posición

"""

        # 🎨 APLICAR FORMATEO AUTOMÁTICO (ahora es necesario porque no se formatea en _handle_chat_engine_response)
        formatted_texto = self.response_formatter.format_response(texto, "auto")
        self.chat_list.add_assistant_message(formatted_texto, self._get_current_time())

    def _mostrar_tabla_pequena(self, alumnos):
        """Muestra tabla detallada para pocos alumnos (≤10) con formato premium"""
        total = len(alumnos)
        plural = 's' if total > 1 else ''

        # 🎨 HEADER PREMIUM PARA POCOS ALUMNOS
        texto = f"""
👥 **{total} ALUMNO{plural.upper()} ENCONTRADO{plural.upper()}**
{'═' * 50}

"""

        # 🎯 FORMATO DETALLADO PARA CADA ALUMNO
        for i, alumno in enumerate(alumnos, 1):
            nombre = alumno.get('nombre', '').upper()
            curp = alumno.get('curp', '')
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')
            matricula = alumno.get('matricula', '')

            # 🎨 FORMATO PREMIUM CON MEJOR ESPACIADO
            texto += f"**{i}.** **{nombre}**\n"
            texto += f"   📋 **CURP:** {curp}\n"
            texto += f"   🎓 **Grado:** {grado}° {grupo} - {turno}\n"
            texto += f"   🆔 **Matrícula:** {matricula}\n\n"

        # 🎯 MENSAJE DE AYUDA ESPECÍFICO PARA POCOS ALUMNOS
        texto += f"""{'─' * 50}
💡 **Acciones rápidas disponibles:**
• "Detalles completos de [nombre]" - Ver toda la información
• "Constancia de estudios para [nombre]" - Generar constancia
• "Calificaciones de [nombre]" - Ver notas del alumno

"""

        # 🎨 APLICAR FORMATEO AUTOMÁTICO (ahora es necesario porque no se formatea en _handle_chat_engine_response)
        formatted_texto = self.response_formatter.format_response(texto, "auto")
        self.chat_list.add_assistant_message(formatted_texto, self._get_current_time())

    def mostrar_detalle_alumno(self, alumno):
        """Muestra los detalles completos de un solo alumno con calificaciones si las tiene"""
        try:
            # Verificar si el alumno existe
            if not alumno:
                self.chat_list.add_assistant_message("No se encontraron detalles del alumno.", self._get_current_time())
                return

            # Crear texto plano simple y legible
            texto = f"📋 DETALLES DEL ALUMNO\n"
            texto += "=" * 50 + "\n\n"

            # Datos personales
            texto += "👤 DATOS PERSONALES\n"
            texto += f"• Nombre: {alumno.get('nombre', 'No disponible').upper()}\n"
            texto += f"• CURP: {alumno.get('curp', 'No disponible')}\n"
            texto += f"• Matrícula: {alumno.get('matricula', 'No disponible')}\n"
            texto += f"• Fecha de Nacimiento: {alumno.get('fecha_nacimiento', 'No disponible')}\n\n"

            # Datos escolares
            texto += "🏫 DATOS ESCOLARES\n"
            texto += f"• Grado: {alumno.get('grado', 'No disponible')}\n"
            texto += f"• Grupo: {alumno.get('grupo', 'No disponible')}\n"
            texto += f"• Turno: {alumno.get('turno', 'No disponible')}\n"
            texto += f"• Ciclo Escolar: {alumno.get('ciclo_escolar', 'No disponible')}\n"
            texto += f"• Escuela: {alumno.get('escuela', 'No disponible')}\n\n"

            # Calificaciones
            calificaciones = alumno.get('calificaciones', [])
            if calificaciones and len(calificaciones) > 0:
                texto += "📊 CALIFICACIONES\n"
                texto += "-" * 30 + "\n"

                # Verificar si tienen periodos
                tiene_periodos = any(cal.get('i') is not None or cal.get('ii') is not None for cal in calificaciones)

                for i, cal in enumerate(calificaciones, 1):
                    materia = cal.get('nombre', cal.get('materia', 'No especificada'))
                    texto += f"\n{i}. {materia}\n"

                    if tiene_periodos:
                        # Formatear calificaciones por periodo
                        def format_grade(grade):
                            if isinstance(grade, (int, float)) and grade > 0:
                                return f"{grade:.1f}" if grade % 1 != 0 else str(int(grade))
                            return '-'

                        p1 = format_grade(cal.get('i', 0))
                        p2 = format_grade(cal.get('ii', 0))
                        p3 = format_grade(cal.get('iii', 0))
                        prom = format_grade(cal.get('promedio', 0))

                        texto += f"   Periodo I: {p1}  |  Periodo II: {p2}  |  Periodo III: {p3}\n"
                        texto += f"   ➤ PROMEDIO: {prom}\n"
                    else:
                        # Calificación simple
                        calificacion = cal.get('promedio', cal.get('calificacion', 'N/A'))
                        if isinstance(calificacion, (int, float)):
                            calificacion = f"{calificacion:.1f}" if calificacion % 1 != 0 else str(int(calificacion))
                        texto += f"   ➤ CALIFICACIÓN: {calificacion}\n"
            else:
                texto += "📊 CALIFICACIONES\n"
                texto += "ℹ️ Este alumno no tiene calificaciones registradas.\n"

            # Mostrar el texto plano en el chat
            self.chat_list.add_assistant_message(texto, self._get_current_time())

        except Exception as e:
            # Si hay algún error, mostrar los datos del alumno en formato simple
            alumno_text = f"Detalles del alumno:\n"
            alumno_text += f"Nombre: {alumno.get('nombre', 'No disponible').upper()}\n"
            alumno_text += f"CURP: {alumno.get('curp', 'No disponible')}\n"
            alumno_text += f"Grado: {alumno.get('grado', 'No disponible')}\n"
            alumno_text += f"Grupo: {alumno.get('grupo', 'No disponible')}\n"
            alumno_text += f"Turno: {alumno.get('turno', 'No disponible')}\n"
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M:%S")
            self.chat_list.add_assistant_message(alumno_text, current_time)
            self.logger.error(f"Error al mostrar detalles del alumno: {str(e)}")

    def closeEvent(self, event):
        """Se llama cuando se cierra la ventana"""
        # Limpiar archivos temporales
        self.cleanup_temp_files()

        # Continuar con el evento de cierre
        super().closeEvent(event)

    def cleanup_temp_files(self):
        """Limpia los archivos temporales generados durante la sesión"""
        import shutil
        import os
        import time

        # Limpiar el archivo temporal de transformación
        if self.temp_transformed_file and os.path.exists(self.temp_transformed_file):
            try:
                # Cerrar el PDF en el visor antes de intentar eliminarlo
                if self.pdf_panel and hasattr(self.pdf_panel, 'pdf_viewer'):
                    self.pdf_panel.pdf_viewer.close_pdf()

                # Esperar un momento para asegurarse de que el archivo se haya liberado
                time.sleep(0.5)

                # Intentar eliminar el archivo
                try:
                    os.remove(self.temp_transformed_file)

                    # Eliminar el directorio temporal si está vacío
                    temp_dir = os.path.dirname(self.temp_transformed_file)
                    if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                        shutil.rmtree(temp_dir)
                except PermissionError:
                    # Si no se puede eliminar ahora, programar para eliminación al salir
                    import atexit

                    def delete_on_exit(file_path, dir_path):
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            if os.path.exists(dir_path) and not os.listdir(dir_path):
                                shutil.rmtree(dir_path)
                        except Exception:
                            pass  # Ignorar errores al salir

                    # Registrar función para eliminar al salir
                    temp_dir = os.path.dirname(self.temp_transformed_file)
                    atexit.register(delete_on_exit, self.temp_transformed_file, temp_dir)
            except Exception as e:
                self.logger.error(f"Error al limpiar archivos temporales: {str(e)}")
