"""
Ventana principal de la interfaz de chat con IA.

Este módulo implementa la ventana principal de la interfaz de chat con IA,
que permite interactuar con el asistente virtual para generar constancias,
buscar alumnos y transformar PDFs.

La interfaz incluye un panel de chat y un panel para visualizar PDFs,
así como funcionalidades para cargar, transformar y guardar constancias.
"""
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QSplitter, QProgressBar,
    QToolBar, QAction
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor

from app.ui.ai_chat.chat_list import ChatList
from app.ui.ai_chat.gemini_client import GeminiClient
from app.ui.ai_chat.pdf_panel import PDFPanel
from app.ui.ai_chat.message_processor import MessageProcessor
from app.core.utils import open_file_with_default_app

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
        message_processor (MessageProcessor): Procesador de mensajes para el chat.
        gemini_client (GeminiClient): Cliente para comunicación con la API de Gemini.
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
        self.last_generated_file = None              # Último archivo generado
        self.temp_transformed_file = None            # Archivo temporal transformado
        self.transformation_data = None              # Datos de transformación

        # Inicializar componentes principales
        self.message_processor = MessageProcessor()  # Procesador de mensajes
        self.gemini_client = GeminiClient()          # Cliente para API de Gemini

        # Conectar señales del cliente Gemini
        self.gemini_client.response_ready.connect(self.handle_gemini_response)
        self.gemini_client.error_occurred.connect(self.handle_gemini_error)

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

        # Mensaje de bienvenida - todo en un solo mensaje para evitar espacios innecesarios
        mensaje_bienvenida = """¡Bienvenido al Asistente de Constancias con IA!

Puedes pedirme que busque alumnos, genere constancias o transforme PDFs.
Para transformar un PDF:
1. Haz clic en el botón "🔄 Transformación de PDF" en la barra superior
2. Carga un PDF arrastrándolo o usando el botón "Seleccionar PDF"
3. Escribe en el chat: "Transforma este PDF a constancia de estudios"

Escribe "ayuda" para ver todas las funciones disponibles."""

        self.chat_list.add_system_message(mensaje_bienvenida, self.message_processor.get_current_time())

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
                padding: 10px 15px;
                font-size: 14px;
                background-color: #16213E;
                color: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.6);
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)

        send_button = QPushButton("Enviar")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #2C4F7C;
            }
            QPushButton:hover {
                background-color: #2C4F7C;
            }
            QPushButton:pressed {
                background-color: #3A6095;
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

        # Crear el panel de PDF
        self.pdf_panel = PDFPanel()

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

        # Añadir el mensaje del usuario al chat
        self.chat_list.add_user_message(message_text, self.message_processor.get_current_time())

        # Manejar diferentes estados de la conversación
        if self.waiting_for_save_confirmation and self.temp_transformed_file and self.transformation_data:
            # Estamos esperando una respuesta sobre qué hacer con el archivo transformado
            self._handle_save_confirmation_response(message_text)
            return
        elif self.waiting_for_file_open_response and self.last_generated_file:
            # Estamos esperando una respuesta sobre si abrir un archivo
            self._handle_file_open_response(message_text)
            return

        # Para mensajes normales, continuar con el flujo habitual
        self._process_normal_message(message_text)

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
            self.chat_list.add_assistant_message(
                f"✅ Archivo guardado correctamente en: {dest_path}",
                self.message_processor.get_current_time()
            )

            # Actualizar la ruta del archivo para posible apertura
            self.last_generated_file = dest_path

            # Preguntar si desea abrir el archivo
            self.chat_list.add_assistant_message(
                "¿Deseas abrir el archivo? Responde 'sí' o 'no'.",
                self.message_processor.get_current_time()
            )
            self.waiting_for_file_open_response = True
        except Exception as e:
            self.chat_list.add_assistant_message(
                f"❌ Error al guardar el archivo: {str(e)}",
                self.message_processor.get_current_time()
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

            # En Windows, usar el comando predeterminado para abrir (que permite imprimir)
            if platform.system() == "Windows":
                subprocess.Popen(['start', '', self.temp_transformed_file], shell=True)
                self.chat_list.add_assistant_message(
                    "✅ Abriendo el archivo en el navegador. Desde allí puedes verlo o imprimirlo.",
                    self.message_processor.get_current_time()
                )
                self.chat_list.add_assistant_message(
                    "Recuerda que este archivo es temporal y se eliminará al cerrar la aplicación.",
                    self.message_processor.get_current_time()
                )
            else:  # macOS o Linux
                from app.core.utils import open_file_with_default_app
                open_file_with_default_app(self.temp_transformed_file)
                self.chat_list.add_assistant_message(
                    "✅ Abriendo el archivo en el navegador. Desde allí puedes verlo o imprimirlo.",
                    self.message_processor.get_current_time()
                )
                self.chat_list.add_assistant_message(
                    "Recuerda que este archivo es temporal y se eliminará al cerrar la aplicación.",
                    self.message_processor.get_current_time()
                )
        except Exception as e:
            self.chat_list.add_assistant_message(
                f"❌ Error al abrir el archivo: {str(e)}",
                self.message_processor.get_current_time()
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
                    self.message_processor.get_current_time()
                )

                # Si hay datos del alumno, mostrarlos
                if "alumno" in data:
                    self.mostrar_detalle_alumno(data["alumno"])
            else:
                self.chat_list.add_assistant_message(
                    f"❌ Error al guardar los datos: {message}",
                    self.message_processor.get_current_time()
                )
        except Exception as e:
            self.chat_list.add_assistant_message(
                f"❌ Error al guardar los datos: {str(e)}",
                self.message_processor.get_current_time()
            )

    def _do_nothing_with_file(self):
        """No hace nada con el archivo, solo mantiene la vista previa"""
        self.chat_list.add_assistant_message(
            "✅ De acuerdo, no guardaré el archivo ni los datos. La vista previa seguirá disponible hasta que cierres la aplicación o cargues otro PDF.",
            self.message_processor.get_current_time()
        )

    def _show_invalid_option_message(self):
        """Muestra un mensaje de error por opción no válida"""
        # Mensaje de error si la opción no es reconocida
        self.chat_list.add_assistant_message("""
        <div style="background-color: #E74C3C; border: 1px solid #C0392B; border-radius: 8px; padding: 10px; color: white;">
        <p><b>⚠️ Opción no reconocida</b></p>
        <p>Por favor, responde con un número del 1 al 4 o con el nombre de una de las opciones disponibles.</p>
        </div>
        """, self.message_processor.get_current_time())

        # Mostrar nuevamente las opciones con un mensaje más simple
        self.chat_list.add_assistant_message("""<div style="background-color: #2C3E50; border: 1px solid #34495E; border-radius: 8px; padding: 15px; color: #FFFFFF;">
<p>Por favor, selecciona una de estas opciones:</p>
<p><b style="color: #88CCFF;">1.</b> Guardar archivo</p>
<p><b style="color: #88CCFF;">2.</b> Abrir/Imprimir</p>
<p><b style="color: #88CCFF;">3.</b> Guardar datos</p>
<p><b style="color: #88CCFF;">4.</b> Nada</p>
</div>""", self.message_processor.get_current_time())

    def _handle_file_open_response(self, message_text):
        """Maneja la respuesta del usuario sobre si abrir un archivo"""
        if message_text.lower() in ["sí", "si", "yes", "s", "y"]:
            # Abrir el archivo
            try:
                open_file_with_default_app(self.last_generated_file)
                self.chat_list.add_assistant_message(
                    "Abriendo el archivo para ti. ¡Espero que te sea útil!",
                    self.message_processor.get_current_time()
                )
            except Exception as e:
                self.chat_list.add_assistant_message(
                    f"No pude abrir el archivo: {str(e)}",
                    self.message_processor.get_current_time()
                )
        else:
            # No abrir el archivo
            self.chat_list.add_assistant_message(
                "De acuerdo, no abriré el archivo. ¿Hay algo más en lo que pueda ayudarte?",
                self.message_processor.get_current_time()
            )

        # Restablecer el estado
        self.waiting_for_file_open_response = False

    def _process_normal_message(self, message_text):
        """Procesa un mensaje normal del usuario"""
        # Mostrar la barra de progreso
        self.progress_bar.setVisible(True)

        # Crear el prompt
        current_pdf = self.pdf_panel.get_current_pdf()
        prompt = self.message_processor.create_prompt(message_text, current_pdf)

        # Enviar el prompt a Gemini
        self.gemini_client.send_prompt(prompt)

    def handle_gemini_response(self, response):
        """Maneja la respuesta de Gemini.

        Este método procesa la respuesta recibida del modelo de IA Gemini.
        Extrae los comandos en formato JSON de la respuesta y los ejecuta según su tipo.

        Args:
            response: Objeto de respuesta de Gemini que contiene el texto generado.

        Returns:
            None
        """
        # Ocultar la barra de progreso cuando se recibe la respuesta
        self.progress_bar.setVisible(False)

        # Extraer el comando JSON de la respuesta de texto
        # El formato esperado es un objeto JSON con campos 'accion' y 'parametros'
        command_data = self.message_processor.extract_json_from_response(response.text)

        # Si no se pudo extraer un comando válido, informar al usuario
        if not command_data:
            self.chat_list.add_assistant_message(
                "No pude entender tu solicitud. ¿Podrías reformularla?",
                self.message_processor.get_current_time()
            )
            return

        # Obtener la acción y parámetros del comando
        accion = command_data.get("accion", "desconocida")
        parametros = command_data.get("parametros", {})

        # FLUJO DE DECISIÓN:
        # 1. Si es una solicitud de ayuda, mostrar la ayuda
        if accion == "mostrar_ayuda":
            self.mostrar_ayuda()
            return

        # 2. Si es una transformación de constancia, manejarla de forma especial
        # Las transformaciones requieren un flujo diferente porque implican
        # la creación de archivos temporales y opciones de guardado
        if accion == "transformar_constancia":
            self._handle_transform_constancia(parametros)
            return

        # 3. Para cualquier otro tipo de comando (búsqueda, generación, etc.)
        # procesarlo con el flujo estándar
        self._process_standard_command(command_data)

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
        # Sin un PDF, no podemos realizar ninguna transformación
        current_pdf = self.pdf_panel.get_current_pdf()
        if not current_pdf:
            self.chat_list.add_assistant_message(
                "Error: No hay ningún PDF cargado para transformar.",
                self.message_processor.get_current_time()
            )
            return

        # PASO 2: Preparar el entorno para la transformación
        # Crear un directorio temporal y configurar los parámetros
        temp_dir, tipo_destino, incluir_foto = self._setup_transformation_params(parametros, current_pdf)

        # PASO 3: Informar al usuario sobre la transformación que se va a realizar
        # Esto proporciona retroalimentación inmediata mientras se procesa
        self._show_transformation_info(tipo_destino, incluir_foto)

        # PASO 4: Ejecutar la transformación real del PDF
        # Llamar al servicio que realiza la conversión del formato
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
        self.chat_list.add_assistant_message(info_message, self.message_processor.get_current_time())

    def _execute_transformation(self, current_pdf, temp_dir):
        """Ejecuta la transformación de la constancia"""
        from app.core.service_provider import ServiceProvider

        constancia_service = ServiceProvider.get_instance().constancia_service

        # Generar vista previa (preview_mode=True)
        return constancia_service.generar_constancia_desde_pdf(
            current_pdf,
            self.transformation_data["tipo_destino"],
            self.transformation_data["incluir_foto"],
            guardar_alumno=False,
            preview_mode=True,
            output_dir=temp_dir
        )

    def _handle_successful_transformation(self, data):
        """Maneja una transformación exitosa"""
        # Guardar la ruta del archivo temporal
        self.temp_transformed_file = data["ruta_archivo"]

        # Mostrar mensaje de éxito
        self.chat_list.add_assistant_message(
            self.message_processor.get_random_success_phrase(),
            self.message_processor.get_current_time()
        )
        self.chat_list.add_assistant_message(
            "He generado una vista previa de la constancia transformada.",
            self.message_processor.get_current_time()
        )

        # Cargar el PDF en el visor
        self.pdf_panel.show_pdf(self.temp_transformed_file)

        # Mostrar opciones y esperar confirmación
        self._show_transformation_options()

    def _show_transformation_options(self):
        """Muestra las opciones disponibles después de transformar una constancia"""
        options_message = """<div style="background-color: #2C3E50; border: 1px solid #34495E; border-radius: 8px; padding: 15px; margin-bottom: 10px; color: #FFFFFF;">
<h3 style="color: #7FB3D5; margin-top: 0; margin-bottom: 10px;">¿Qué deseas hacer con esta constancia?</h3>
<div style="margin-top: 5px; margin-bottom: 5px;">
<p><b style="color: #88CCFF;">1. Guardar archivo</b>: Guardar la constancia como PDF permanente</p>
<p><b style="color: #88CCFF;">2. Abrir/Imprimir</b>: Abrir en navegador para ver o imprimir (sin guardar)</p>
<p><b style="color: #88CCFF;">3. Guardar datos</b>: Registrar los datos extraídos del PDF original en la base de datos</p>
<p><b style="color: #88CCFF;">4. Nada</b>: Solo ver la vista previa (se eliminará al cerrar la aplicación)</p>
</div>
<p style="margin-top: 10px;">Responde con el número (1-4) o el nombre de la opción.</p>
<p style="margin-top: 5px; font-size: 12px; color: #7FB3D5;">Nota: Para ver los datos que se registrarán, usa el botón "Ver Datos" en el panel del PDF original.</p>
</div>"""
        self.chat_list.add_assistant_message(options_message, self.message_processor.get_current_time())

        # Establecer el estado de espera de confirmación
        self.waiting_for_save_confirmation = True

    def _handle_failed_transformation(self, message):
        """Maneja una transformación fallida"""
        error_msg = message if message else "Error al transformar la constancia."
        self.chat_list.add_assistant_message(
            f"Error: {error_msg}",
            self.message_processor.get_current_time()
        )

    def _process_standard_command(self, command_data):
        """Procesa comandos estándar (no transformaciones)"""
        current_pdf = self.pdf_panel.get_current_pdf()
        accion = command_data.get("accion", "")
        success, message, data = self.message_processor.process_command(command_data, current_pdf)

        if success:
            self._handle_successful_command(accion, message, data)
        else:
            self._handle_failed_command(message)

    def _handle_successful_command(self, accion, message, data):
        """Maneja un comando exitoso"""
        # Usar frases variadas para respuestas más naturales
        if "generada" in message or "generado" in message:
            # Para constancias generadas, usar una frase de éxito
            self.chat_list.add_assistant_message(
                self.message_processor.get_random_success_phrase(),
                self.message_processor.get_current_time()
            )

        # Mostrar el mensaje original
        self.chat_list.add_assistant_message(message, self.message_processor.get_current_time())

        # Mostrar datos adicionales según el tipo de comando
        self._display_additional_data(data)

        # Manejar archivos generados
        if "ruta_archivo" in data and accion != "transformar_constancia":
            self._handle_generated_file(data["ruta_archivo"])

    def _display_additional_data(self, data):
        """Muestra datos adicionales según el tipo de comando"""
        if "alumno" in data:
            # Mostrar detalles de un solo alumno
            self.mostrar_detalle_alumno(data["alumno"])
        elif "alumnos" in data:
            alumnos = data["alumnos"]
            if alumnos:
                # Mostrar alumnos en formato tabular
                self.mostrar_alumnos_tabla(alumnos)

    def _handle_generated_file(self, ruta_archivo):
        """Maneja un archivo generado"""
        import os
        self.chat_list.add_assistant_message(
            f"Archivo generado: {os.path.basename(ruta_archivo)}",
            self.message_processor.get_current_time()
        )

        # Cargar el PDF en el visor
        self.pdf_panel.show_pdf(ruta_archivo)

        # Preguntar si desea abrir el archivo
        self.chat_list.add_assistant_message(
            "¿Deseas abrir el archivo? Responde 'sí' o 'no'.",
            self.message_processor.get_current_time()
        )

        # Guardar el archivo actual para posible apertura
        self.last_generated_file = ruta_archivo

        # Establecer el estado de espera de respuesta
        self.waiting_for_file_open_response = True

    def _handle_failed_command(self, message):
        """Maneja un comando fallido"""
        self.chat_list.add_assistant_message(
            f"Error: {message}",
            self.message_processor.get_current_time()
        )

    def handle_gemini_error(self, error_message):
        """Maneja errores en la comunicación con Gemini"""
        # Ocultar la barra de progreso
        self.progress_bar.setVisible(False)

        # Mostrar mensaje de error
        self.chat_list.add_assistant_message(f"Lo siento, ocurrió un error: {error_message}", self.message_processor.get_current_time())
        self.chat_list.add_assistant_message("Por favor, intenta de nuevo más tarde.", self.message_processor.get_current_time())

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
        self.chat_list.add_assistant_message(ayuda_html, self.message_processor.get_current_time())

    def mostrar_alumnos_tabla(self, alumnos):
        """Muestra los alumnos en formato tabular"""
        # Implementación simplificada - se puede expandir según necesidades
        html = "<table border='1' style='width:100%; border-collapse: collapse; color: white; border-color: #34495E;'>"
        html += "<tr style='background-color: #1E3A5F; color: white;'><th>ID</th><th>Nombre</th><th>CURP</th><th>Grado</th><th>Grupo</th></tr>"

        for i, alumno in enumerate(alumnos):
            # Alternar colores de fondo para las filas
            bg_color = "#2C3E50" if i % 2 == 0 else "#34495E"
            html += f"<tr style='background-color: {bg_color};'>"
            html += f"<td>{alumno.get('id', '')}</td>"
            html += f"<td>{alumno.get('nombre', '').upper()}</td>"
            html += f"<td>{alumno.get('curp', '')}</td>"
            html += f"<td>{alumno.get('grado', '')}</td>"
            html += f"<td>{alumno.get('grupo', '')}</td>"
            html += f"</tr>"

        html += "</table>"

        self.chat_list.add_assistant_message(html, self.message_processor.get_current_time())

    def mostrar_detalle_alumno(self, alumno):
        """Muestra los detalles de un solo alumno"""
        # Implementación simplificada - se puede expandir según necesidades
        html = "<div style='border: 1px solid #3498DB; padding: 15px; border-radius: 8px; background-color: #2C3E50; color: white;'>"
        html += f"<h3 style='color: #7FB3D5; margin-top: 0;'>{alumno.get('nombre', '').upper()}</h3>"
        html += f"<p><b style='color: #88CCFF;'>CURP:</b> {alumno.get('curp', '')}</p>"
        html += f"<p><b style='color: #88CCFF;'>Matrícula:</b> {alumno.get('matricula', '')}</p>"
        html += f"<p><b style='color: #88CCFF;'>Grado:</b> {alumno.get('grado', '')}</p>"
        html += f"<p><b style='color: #88CCFF;'>Grupo:</b> {alumno.get('grupo', '')}</p>"
        html += f"<p><b style='color: #88CCFF;'>Turno:</b> {alumno.get('turno', '')}</p>"
        html += "</div>"

        self.chat_list.add_assistant_message(html, self.message_processor.get_current_time())

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
                print(f"Error al limpiar archivos temporales: {str(e)}")
