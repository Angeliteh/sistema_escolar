"""
Interfaz de chat para interactuar con el sistema de constancias mediante IA
"""
import os
import sys
import json
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QFileDialog,
    QScrollArea, QFrame, QSplitter, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QTextCursor

import google.generativeai as genai
from dotenv import load_dotenv

from app.core.ai.command_executor import CommandExecutor
from app.core.utils import open_file_with_default_app
from app.ui.pdf_viewer import PDFViewer

# Cargar variables de entorno
load_dotenv()

class GeminiThread(QThread):
    """Hilo para ejecutar consultas a Gemini sin bloquear la interfaz"""
    response_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, models, prompt):
        super().__init__()
        self.models = models
        self.prompt = prompt

    def run(self):
        try:
            # Intentar con Gemini 2.0 Flash primero
            if self.models["gemini-2.0-flash"]:
                try:
                    response = self.models["gemini-2.0-flash"].generate_content(self.prompt)
                    self.response_ready.emit(response)
                    return
                except Exception as e:
                    # Si falla, intentar con el modelo de respaldo
                    pass

            # Intentar con Gemini 1.5 Flash como respaldo
            if self.models["gemini-1.5-flash"]:
                try:
                    response = self.models["gemini-1.5-flash"].generate_content(self.prompt)
                    self.response_ready.emit(response)
                    return
                except Exception as e:
                    self.error_occurred.emit(f"Error con Gemini 1.5 Flash: {str(e)}")
            else:
                self.error_occurred.emit("No hay modelos disponibles")

        except Exception as e:
            self.error_occurred.emit(f"Error en el hilo: {str(e)}")

class AIChatWindow(QMainWindow):
    """Ventana principal de la interfaz de chat con IA"""

    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Asistente de Constancias con IA")
        self.setMinimumSize(1200, 800)

        # Inicializar variables
        self.current_pdf = None
        self.command_executor = CommandExecutor()

        # Variables para el manejo de estados
        self.waiting_for_file_open_response = False
        self.last_generated_file = None

        # Frases de variación para respuestas más naturales
        self.greeting_phrases = [
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Buen día! ¿Qué necesitas hacer?",
            "¡Saludos! Estoy listo para asistirte.",
            "¿En qué puedo ayudarte con las constancias hoy?",
            "Estoy aquí para ayudarte. ¿Qué necesitas?"
        ]

        self.success_phrases = [
            "¡Listo! He completado la tarea con éxito.",
            "¡Perfecto! La operación se ha realizado correctamente.",
            "¡Excelente! Todo ha salido bien.",
            "¡Tarea completada! Todo en orden.",
            "¡Genial! He terminado lo que me pediste."
        ]

        self.setup_gemini()

        # Configurar la interfaz
        self.setup_ui()

    def setup_gemini(self):
        """Configura la API de Gemini"""
        # Obtener la API key de las variables de entorno
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key or api_key == "tu-api-key-aquí":
            QMessageBox.critical(
                self,
                "Error de API Key",
                "No se encontró una API key válida de Gemini.\n\n"
                "Configura la API key en el archivo .env antes de usar el asistente."
            )
            sys.exit(1)

        # Configurar Gemini
        genai.configure(api_key=api_key)

        # Crear modelos con mecanismo de respaldo
        self.models = {
            "gemini-2.0-flash": None,  # Primera opción (principal)
            "gemini-1.5-flash": None   # Segunda opción (respaldo)
        }

        # Inicializar Gemini 2.0 Flash
        try:
            self.models["gemini-2.0-flash"] = genai.GenerativeModel('gemini-2.0-flash')
            print("Modelo Gemini 2.0 Flash inicializado correctamente.")
        except Exception as e:
            print(f"No se pudo inicializar Gemini 2.0 Flash: {str(e)}")

        # Inicializar Gemini 1.5 Flash
        try:
            self.models["gemini-1.5-flash"] = genai.GenerativeModel('gemini-1.5-flash')
            print("Modelo Gemini 1.5 Flash (respaldo) inicializado correctamente.")
        except Exception as e:
            print(f"No se pudo inicializar Gemini 1.5 Flash: {str(e)}")

        # Verificar que al menos un modelo esté disponible
        if not any(self.models.values()):
            QMessageBox.critical(
                self,
                "Error de Modelo",
                "No se pudo inicializar ningún modelo de Gemini.\n\n"
                "Verifica tu API key y la disponibilidad de los modelos."
            )
            sys.exit(1)

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Título
        title_label = QLabel("Asistente de Constancias con IA")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        main_layout.addWidget(title_label)

        # Splitter para dividir la pantalla
        splitter = QSplitter(Qt.Horizontal)

        # Panel izquierdo (chat)
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(10)

        # Área de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dfe1e5;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        # Mensaje de bienvenida
        self.add_system_message("¡Bienvenido al Asistente de Constancias con IA!")
        self.add_system_message("Puedes pedirme que busque alumnos, genere constancias o transforme PDFs.")
        self.add_system_message("Para transformar un PDF, primero cárgalo usando el botón 'Cargar PDF'.")

        # Área de entrada
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe tu mensaje aquí...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe1e5;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)

        send_button = QPushButton("Enviar")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3367d6;
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
                border: 1px solid #dfe1e5;
                border-radius: 5px;
                text-align: center;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #4285f4;
            }
        """)

        # Añadir widgets al layout del chat
        chat_layout.addWidget(self.chat_area, 1)
        chat_layout.addWidget(self.progress_bar)
        chat_layout.addWidget(input_container)

        # Panel derecho (PDF y vista previa)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Sección de carga de PDF
        pdf_upload_group = QFrame()
        pdf_upload_group.setFrameShape(QFrame.StyledPanel)
        pdf_upload_group.setStyleSheet("""
            QFrame {
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
                padding: 10px;
            }
        """)

        pdf_upload_layout = QVBoxLayout(pdf_upload_group)

        pdf_upload_label = QLabel("Cargar PDF para Transformación")
        pdf_upload_label.setAlignment(Qt.AlignCenter)
        pdf_upload_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")

        pdf_upload_button = QPushButton("Cargar PDF")
        pdf_upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        pdf_upload_button.clicked.connect(self.load_pdf)

        self.current_pdf_label = QLabel("Ningún PDF cargado")
        self.current_pdf_label.setAlignment(Qt.AlignCenter)
        self.current_pdf_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        self.current_pdf_label.setWordWrap(True)

        pdf_upload_layout.addWidget(pdf_upload_label)
        pdf_upload_layout.addWidget(pdf_upload_button)
        pdf_upload_layout.addWidget(self.current_pdf_label)

        # Sección de vista previa
        self.preview_container = QWidget()
        preview_container_layout = QVBoxLayout(self.preview_container)
        preview_container_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("Vista Previa")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2ecc71;")

        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.setStyleSheet("""
            QScrollArea {
                border: 2px solid #2ecc71;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)

        # Añadir widgets al contenedor de vista previa
        preview_container_layout.addWidget(self.preview_label)
        preview_container_layout.addWidget(self.pdf_viewer)

        # Ocultar el contenedor de vista previa inicialmente
        self.preview_container.setVisible(False)

        # Añadir mensaje informativo en el panel derecho cuando no hay PDF
        self.no_pdf_message = QLabel("No hay PDF cargado.\nUtiliza el botón 'Cargar PDF' para cargar un archivo.")
        self.no_pdf_message.setAlignment(Qt.AlignCenter)
        self.no_pdf_message.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                padding: 20px;
                background-color: #f5f5f5;
                border: 1px dashed #bdc3c7;
                border-radius: 10px;
                margin-top: 20px;
            }
        """)
        right_layout.addWidget(self.no_pdf_message, 1)

        # Añadir widgets al layout derecho
        right_layout.addWidget(pdf_upload_group)
        right_layout.addWidget(self.preview_container, 1)

        # Añadir paneles al splitter
        splitter.addWidget(chat_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])  # Tamaño inicial de los paneles

        # Añadir splitter al layout principal
        main_layout.addWidget(splitter, 1)

    def add_system_message(self, text):
        """Añade un mensaje del sistema al área de chat"""
        # Obtener la hora actual
        hora = self._get_current_time()

        # Crear HTML mejorado para mensajes del sistema
        html = f"""
        <div style="margin: 15px 0; text-align: center;">
            <table align="center" style="background-color: #F2F2F2; border-radius: 8px; border-collapse: collapse; max-width: 80%;">
                <tr>
                    <td style="padding: 10px;">
                        <div style="font-size: 16px; color: #7f8c8d; font-style: italic;">
                            <span style="font-size: 18px;">🔔</span> {text}
                        </div>
                        <div style="font-size: 10px; color: #95a5a6; text-align: right; margin-top: 5px;">
                            {hora}
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """

        self.chat_area.append(html)

        # Desplazar al final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)

    def add_user_message(self, text):
        """Añade un mensaje del usuario al área de chat"""
        # Obtener la hora actual
        hora = self._get_current_time()

        # Crear HTML mejorado para mensajes del usuario
        html = f"""
        <div style="margin: 15px 0; text-align: right;">
            <table align="right" style="background-color: #DCF8C6; border-radius: 12px; border-collapse: collapse; max-width: 80%;">
                <tr>
                    <td style="padding: 12px;">
                        <div style="font-size: 12px; color: #2980b9; font-weight: bold; margin-bottom: 5px;">
                            👤 Tú
                        </div>
                        <div style="font-size: 15px; color: #000000;">
                            {text}
                        </div>
                        <div style="font-size: 10px; color: #7f8c8d; text-align: right; margin-top: 5px;">
                            {hora}
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """

        self.chat_area.append(html)

        # Desplazar al final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)

    def add_ai_message(self, text):
        """Añade un mensaje de la IA al área de chat"""
        # Obtener la hora actual
        hora = self._get_current_time()

        # Crear HTML mejorado para mensajes del asistente
        html = f"""
        <div style="margin: 15px 0; text-align: left;">
            <table align="left" style="background-color: #E8F5FD; border-radius: 12px; border-collapse: collapse; max-width: 80%; border: 1px solid #BDE0FD;">
                <tr>
                    <td style="padding: 12px;">
                        <div style="font-size: 12px; color: #1976D2; font-weight: bold; margin-bottom: 5px;">
                            🤖 Asistente
                        </div>
                        <div style="font-size: 15px; color: #000000;">
                            {text}
                        </div>
                        <div style="font-size: 10px; color: #7f8c8d; text-align: right; margin-top: 5px;">
                            {hora}
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        """

        self.chat_area.append(html)

        # Desplazar al final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)

    def _get_current_time(self):
        """Obtiene la hora actual en formato HH:MM"""
        import datetime
        now = datetime.datetime.now()
        return now.strftime("%H:%M")

    def load_pdf(self):
        """Carga un PDF para transformación"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Archivos PDF (*.pdf)")
        file_dialog.setWindowTitle("Seleccionar PDF para transformación")

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                pdf_path = selected_files[0]
                self.current_pdf = pdf_path
                self.current_pdf_label.setText(f"PDF cargado: {os.path.basename(pdf_path)}")

                # Mostrar el PDF en el visor
                self.pdf_viewer.load_pdf(pdf_path)

                # Mostrar el área de vista previa y ocultar el mensaje
                self.preview_container.setVisible(True)
                self.no_pdf_message.setVisible(False)

                # Informar al usuario
                self.add_system_message(f"PDF cargado: {os.path.basename(pdf_path)}")

                # Extraer y mostrar datos del PDF
                self.mostrar_datos_pdf(pdf_path)

                # Informar al usuario sobre las opciones
                self.add_system_message("Ahora puedes:")
                self.add_system_message("1. Transformar el PDF a otro formato de constancia")
                self.add_system_message("2. Guardar los datos del alumno en la base de datos")
                self.add_system_message("3. Hacer ambas cosas (transformar y guardar)")

    def mostrar_datos_pdf(self, pdf_path):
        """Muestra los datos extraídos del PDF"""
        try:
            from app.core.pdf_extractor import PDFExtractor
            extractor = PDFExtractor(pdf_path)

            # Extraer datos básicos
            datos = extractor.extraer_datos_basicos()
            tiene_calificaciones = extractor.tiene_calificaciones()

            # Crear una tabla HTML para los datos personales
            info = """
            <div style="background-color: #f8f9fa; border: 1px solid #dfe1e5; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                <h3 style="color: #3498db; margin-top: 0; margin-bottom: 10px;">📄 Datos Extraídos del PDF</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold; width: 30%;">Nombre:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 8px; font-weight: bold;">CURP:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Matrícula:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 8px; font-weight: bold;">Grado:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Grupo:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                    <tr style="background-color: #f2f2f2;">
                        <td style="padding: 8px; font-weight: bold;">Turno:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold;">Tiene calificaciones:</td>
                        <td style="padding: 8px;">{}</td>
                    </tr>
                </table>
            </div>
            """.format(
                datos.get('nombre', 'No disponible'),
                datos.get('curp', 'No disponible'),
                datos.get('matricula', 'No disponible'),
                datos.get('grado', 'No disponible'),
                datos.get('grupo', 'No disponible'),
                datos.get('turno', 'No disponible'),
                '✅ Sí' if tiene_calificaciones else '❌ No'
            )

            # Mostrar la tabla de datos personales
            self.chat_area.append(info)

            # Si tiene calificaciones, mostrarlas en una tabla HTML
            if tiene_calificaciones:
                calificaciones = extractor.extraer_calificaciones()
                if calificaciones and len(calificaciones) > 0:
                    # Crear una tabla HTML para las calificaciones
                    cal_info = """
                    <div style="background-color: #f8f9fa; border: 1px solid #dfe1e5; border-radius: 8px; padding: 15px; margin-top: 10px; margin-bottom: 10px;">
                        <h3 style="color: #e74c3c; margin-top: 0; margin-bottom: 10px;">📊 Calificaciones Encontradas</h3>
                        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                            <tr style="background-color: #e74c3c; color: white;">
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Materia</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P1</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P2</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P3</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Promedio</th>
                            </tr>
                    """

                    # Añadir filas para cada calificación
                    for i, cal in enumerate(calificaciones):
                        bg_color = "#f2f2f2" if i % 2 == 0 else "white"
                        cal_info += f"""
                            <tr style="background-color: {bg_color};">
                                <td style="padding: 8px; border: 1px solid #ddd;">{cal.get('nombre', '')}</td>
                                <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('i', '-')}</td>
                                <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('ii', '-')}</td>
                                <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('iii', '-')}</td>
                                <td style="padding: 8px; text-align: center; font-weight: bold; color: #e74c3c; border: 1px solid #ddd;">{cal.get('promedio', '-')}</td>
                            </tr>
                        """

                    # Cerrar la tabla
                    cal_info += """
                        </table>
                    </div>
                    """

                    # Mostrar la tabla de calificaciones
                    self.chat_area.append(cal_info)

                    # Añadir línea en blanco
                    self.chat_area.append("")

                    # Informar sobre las opciones de constancias disponibles
                    opciones_info = """
                    <div style="background-color: #d5f5e3; border: 1px solid #2ecc71; border-radius: 8px; padding: 15px; margin-top: 10px; margin-bottom: 10px;">
                        <h3 style="color: #27ae60; margin-top: 0; margin-bottom: 10px;">✅ Opciones Disponibles</h3>
                        <p>Este PDF contiene calificaciones, por lo que puedes generar constancias de:</p>
                        <ul>
                            <li>Estudios</li>
                            <li>Calificaciones</li>
                            <li>Traslado</li>
                        </ul>
                    </div>
                    """
                    self.chat_area.append(opciones_info)
                else:
                    self.add_system_message("⚠️ No se pudieron extraer las calificaciones correctamente.")
            else:
                # Informar sobre las opciones limitadas
                opciones_info = """
                <div style="background-color: #fadbd8; border: 1px solid #e74c3c; border-radius: 8px; padding: 15px; margin-top: 10px; margin-bottom: 10px;">
                    <h3 style="color: #c0392b; margin-top: 0; margin-bottom: 10px;">⚠️ Opciones Limitadas</h3>
                    <p>Este PDF no contiene calificaciones, solo puedes generar constancias de:</p>
                    <ul>
                        <li>Estudios</li>
                    </ul>
                </div>
                """
                self.chat_area.append(opciones_info)

            # Añadir línea en blanco
            self.chat_area.append("")

            # Desplazar al final
            cursor = self.chat_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_area.setTextCursor(cursor)

        except Exception as e:
            self.add_system_message(f"❌ Error al extraer datos del PDF: {str(e)}")

    def create_prompt(self, user_text):
        """Crea un prompt para Gemini"""
        # Añadir información sobre el PDF cargado si existe
        pdf_info = ""
        if self.current_pdf:
            pdf_info = f"\nEl usuario ha cargado un PDF: {self.current_pdf}"

        return f"""
        Eres un asistente especializado en un sistema de gestión de constancias escolares para una escuela primaria.

        El sistema permite:
        - Buscar alumnos por nombre o CURP
        - Buscar alumnos por criterios como grado, grupo, turno, etc.
        - Registrar nuevos alumnos
        - Generar constancias (de estudio, calificaciones o traslado)
        - Transformar constancias existentes
        - Gestionar datos de alumnos{pdf_info}

        El usuario te ha pedido: "{user_text}"

        Analiza lo que quiere hacer y responde ÚNICAMENTE con un JSON que siga este formato:

        {{
            "accion": "nombre_de_la_accion",
            "parametros": {{
                "param1": "valor1",
                "param2": "valor2"
            }}
        }}

        Acciones disponibles y sus parámetros:

        0. mostrar_ayuda
           - No requiere parámetros
           - Usa esta acción cuando el usuario pregunte qué puede hacer el sistema, pida ayuda, o solicite información sobre las funcionalidades disponibles
           - Ejemplos de consultas: "¿Qué puedes hacer?", "Ayuda", "Muéstrame las funciones", "¿Cómo te uso?"

        1. buscar_alumno
           - nombre: Nombre del alumno a buscar (puede ser nombre parcial)
           - curp: CURP del alumno (opcional)
           - busqueda_exacta: true para buscar coincidencias exactas, false para buscar coincidencias parciales (opcional, por defecto false)

        2. buscar_alumnos_por_criterio
           - criterio: Campo por el que se va a buscar ("grado", "grupo", "turno", "ciclo_escolar", "escuela")
           - valor: Valor a buscar

        3. registrar_alumno
           - nombre: Nombre completo del alumno
           - curp: CURP del alumno
           - matricula: Matrícula escolar (opcional)
           - grado: Grado escolar (1-6)
           - grupo: Grupo (A-F)
           - turno: MATUTINO o VESPERTINO

        4. generar_constancia
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
           - tipo: "estudio", "calificaciones" o "traslado"
           - incluir_foto: true o false

        5. transformar_constancia
           - ruta_archivo: Ruta al archivo PDF (usa el PDF cargado si está disponible)
           - tipo_destino: "estudio", "calificaciones" o "traslado"
           - incluir_foto: true o false
           - guardar_alumno: true o false (si se deben guardar los datos del alumno en la base de datos)

        6. guardar_alumno_pdf
           - ruta_archivo: Ruta al archivo PDF (usa el PDF cargado si está disponible)

        7. actualizar_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
           - datos: Objeto con los datos a actualizar (nombre, curp, grado, etc.)

        8. eliminar_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        9. listar_constancias
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        10. detalles_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        11. obtener_dato_especifico
           - nombre: Nombre del alumno para buscar (opcional si se proporciona alumno_id)
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - campo: Campo específico a consultar ("curp", "grado", "grupo", "turno", "matricula", "fecha_nacimiento", "escuela", "cct")
           - Usa esta acción cuando el usuario pregunte por un dato específico de un alumno
           - Ejemplos de consultas: "¿Cuál es la CURP de Juan?", "¿En qué grado está María?", "¿A qué grupo pertenece el alumno con ID 5?"

        Responde ÚNICAMENTE con el JSON, sin texto adicional.
        """

    def extract_json_from_response(self, response_text):
        """Extrae el JSON de la respuesta de Gemini"""
        try:
            # Buscar el primer { y el último }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)

            return None
        except Exception as e:
            print(f"Error al extraer JSON: {str(e)}")
            print(f"Respuesta original: {response_text}")
            return None

    def send_message(self):
        """Envía un mensaje al asistente"""
        # Obtener el texto del mensaje
        message_text = self.input_field.text().strip()
        if not message_text:
            return

        # Limpiar el campo de entrada
        self.input_field.clear()

        # Añadir el mensaje del usuario al chat
        self.add_user_message(message_text)

        # Verificar si estamos esperando una respuesta para abrir un archivo
        if self.waiting_for_file_open_response and self.last_generated_file:
            # Manejar la respuesta directamente
            if message_text.lower() in ["sí", "si", "yes", "s", "y"]:
                # Abrir el archivo
                try:
                    open_file_with_default_app(self.last_generated_file)
                    self.add_ai_message("Abriendo el archivo para ti. ¡Espero que te sea útil!")
                except Exception as e:
                    self.add_ai_message(f"No pude abrir el archivo: {str(e)}")
            else:
                # No abrir el archivo
                self.add_ai_message("De acuerdo, no abriré el archivo. ¿Hay algo más en lo que pueda ayudarte?")

            # Restablecer el estado
            self.waiting_for_file_open_response = False
            return

        # Para mensajes normales, continuar con el flujo habitual
        # Mostrar la barra de progreso
        self.progress_bar.setVisible(True)

        # Crear el prompt
        prompt = self.create_prompt(message_text)

        # Crear y ejecutar el hilo para Gemini
        self.gemini_thread = GeminiThread(self.models, prompt)
        self.gemini_thread.response_ready.connect(self.handle_gemini_response)
        self.gemini_thread.error_occurred.connect(self.handle_gemini_error)
        self.gemini_thread.start()

    def mostrar_ayuda(self):
        """Muestra información de ayuda sobre el sistema"""
        ayuda_html = """
        <div style="background-color: #f8f9fa; border: 1px solid #dfe1e5; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
            <h3 style="color: #3498db; margin-top: 0; margin-bottom: 10px;">🤖 ¿Qué puedo hacer por ti?</h3>

            <h4 style="color: #2980b9; margin-top: 15px;">Gestión de Alumnos</h4>
            <ul>
                <li><b>Buscar alumnos</b> por nombre o CURP: "Busca al alumno Juan Pérez" o "Busca CURP ABCD123456"</li>
                <li><b>Buscar por criterios</b>: "Muestra alumnos de primer grado" o "Alumnos del grupo B"</li>
                <li><b>Registrar alumnos</b>: "Registra un nuevo alumno con nombre..."</li>
                <li><b>Actualizar datos</b>: "Actualiza los datos del alumno Juan Pérez..."</li>
                <li><b>Eliminar alumnos</b>: "Elimina al alumno con ID 5"</li>
            </ul>

            <h4 style="color: #2980b9; margin-top: 15px;">Constancias</h4>
            <ul>
                <li><b>Generar constancias</b>: "Genera constancia de estudios para Juan Pérez"</li>
                <li><b>Transformar PDFs</b>: Carga un PDF y pide "Transforma este PDF a constancia de estudios"</li>
            </ul>

            <h4 style="color: #2980b9; margin-top: 15px;">Consultas</h4>
            <ul>
                <li><b>Información específica</b>: "¿Cuál es la CURP de Juan Pérez?" o "¿En qué grado está María?"</li>
                <li><b>Detalles completos</b>: "Muestra los detalles del alumno Juan Pérez"</li>
            </ul>
        </div>
        """
        self.chat_area.append(ayuda_html)

        # Desplazar al final
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_area.setTextCursor(cursor)

    def handle_gemini_response(self, response):
        """Maneja la respuesta de Gemini"""
        # Ocultar la barra de progreso
        self.progress_bar.setVisible(False)

        # Extraer JSON de la respuesta
        command_data = self.extract_json_from_response(response.text)

        if not command_data:
            self.add_ai_message("No pude entender tu solicitud. ¿Podrías reformularla?")
            return

        # Procesar el comando
        accion = command_data.get("accion", "desconocida")
        parametros = command_data.get("parametros", {})

        # Manejar acción de ayuda
        if accion == "mostrar_ayuda":
            self.mostrar_ayuda()
            return

        # Manejar acción de obtener dato específico
        if accion == "obtener_dato_especifico":
            self.obtener_dato_especifico(
                alumno_id=parametros.get("alumno_id"),
                nombre=parametros.get("nombre"),
                campo=parametros.get("campo")
            )
            return

        # Si es una transformación y hay un PDF cargado, usar esa ruta
        if accion == "transformar_constancia":
            # Verificar si el usuario quiere guardar los datos
            if "guardar" in parametros and parametros["guardar"]:
                parametros["guardar_alumno"] = True
            elif "guardar_alumno" in parametros and parametros["guardar_alumno"]:
                # Asegurarse de que el valor sea booleano
                parametros["guardar_alumno"] = True

            # Si hay un PDF cargado, usar esa ruta
            if self.current_pdf and not parametros.get("ruta_archivo"):
                parametros["ruta_archivo"] = self.current_pdf

            command_data["parametros"] = parametros

        # Ejecutar el comando
        success, message, data = self.command_executor.execute_command(command_data)

        # Mostrar el resultado
        if success:
            # Usar frases variadas para respuestas más naturales
            import random
            if "generada" in message or "generado" in message:
                # Para constancias generadas, usar una frase de éxito
                self.add_ai_message(random.choice(self.success_phrases))

            # Mostrar el mensaje original
            self.add_ai_message(message)

            # Mostrar datos adicionales según el tipo de comando
            if "alumno" in data:
                # Mostrar detalles de un solo alumno
                self.mostrar_detalle_alumno(data["alumno"])
            elif "alumnos" in data:
                alumnos = data["alumnos"]
                if alumnos:
                    # Mostrar alumnos en formato tabular
                    self.mostrar_alumnos_tabla(alumnos)

            # Si se generó un archivo, mostrarlo en el visor
            if "ruta_archivo" in data:
                ruta_archivo = data["ruta_archivo"]
                self.add_ai_message(f"Archivo generado: {os.path.basename(ruta_archivo)}")

                # Cargar el PDF en el visor
                self.pdf_viewer.load_pdf(ruta_archivo)

                # Mostrar el área de vista previa si estaba oculta y ocultar el mensaje
                if not self.preview_container.isVisible():
                    self.preview_container.setVisible(True)
                    self.no_pdf_message.setVisible(False)

                # Preguntar si desea abrir el archivo
                self.add_ai_message("¿Deseas abrir el archivo? Responde 'sí' o 'no'.")

                # Guardar el archivo actual para posible apertura
                self.last_generated_file = ruta_archivo

                # Establecer el estado de espera de respuesta
                self.waiting_for_file_open_response = True
        else:
            self.add_ai_message(f"Error: {message}")

    def mostrar_alumnos_tabla(self, alumnos):
        """Muestra los alumnos en formato tabular"""
        try:
            # Crear encabezado
            html = """
            <div style="background-color: #f8f9fa; border: 1px solid #dfe1e5; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                <h3 style="color: #3498db; margin-top: 0; margin-bottom: 10px;">🔍 Alumnos Encontrados</h3>
            """

            # Si hay muchos alumnos, mostrar solo la lista básica
            if len(alumnos) > 3:
                html += """
                <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                    <tr style="background-color: #3498db; color: white;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">ID</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Nombre</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">CURP</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Grado</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Grupo</th>
                    </tr>
                """

                # Añadir filas para cada alumno
                for i, alumno in enumerate(alumnos):
                    bg_color = "#f2f2f2" if i % 2 == 0 else "white"
                    html += f"""
                    <tr style="background-color: {bg_color};">
                        <td style="padding: 8px; border: 1px solid #ddd;">{alumno.get('id', '')}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{alumno.get('nombre', '').upper()}</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{alumno.get('curp', '')}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{alumno.get('grado', '')}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{alumno.get('grupo', '')}</td>
                    </tr>
                    """

                html += """
                </table>
                <p style="margin-top: 10px; color: #7f8c8d;">Para ver detalles completos de un alumno específico, solicita: "Muestra los detalles del alumno [nombre o ID]"</p>
                """
            else:
                # Para pocos alumnos, mostrar detalles completos de cada uno
                for i, alumno in enumerate(alumnos):
                    # Determinar si tiene calificaciones
                    tiene_calificaciones = alumno.get('calificaciones') and len(alumno.get('calificaciones', [])) > 0

                    # Crear tarjeta para cada alumno
                    html += f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; margin-bottom: 15px; padding: 0;">
                        <div style="background-color: #3498db; color: white; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                            <h4 style="margin: 0;">{alumno.get('nombre', '').upper()} (ID: {alumno.get('id', '')})</h4>
                        </div>
                        <div style="padding: 15px;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px; font-weight: bold; width: 30%;">CURP:</td>
                                    <td style="padding: 8px;">{alumno.get('curp', 'No disponible')}</td>
                                </tr>
                                <tr style="background-color: #f2f2f2;">
                                    <td style="padding: 8px; font-weight: bold;">Matrícula:</td>
                                    <td style="padding: 8px;">{alumno.get('matricula', 'No disponible')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Fecha de Nacimiento:</td>
                                    <td style="padding: 8px;">{alumno.get('fecha_nacimiento', 'No disponible')}</td>
                                </tr>
                                <tr style="background-color: #f2f2f2;">
                                    <td style="padding: 8px; font-weight: bold;">Grado:</td>
                                    <td style="padding: 8px;">{alumno.get('grado', 'No disponible')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Grupo:</td>
                                    <td style="padding: 8px;">{alumno.get('grupo', 'No disponible')}</td>
                                </tr>
                                <tr style="background-color: #f2f2f2;">
                                    <td style="padding: 8px; font-weight: bold;">Turno:</td>
                                    <td style="padding: 8px;">{alumno.get('turno', 'No disponible')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">Ciclo Escolar:</td>
                                    <td style="padding: 8px;">{alumno.get('ciclo_escolar', 'No disponible')}</td>
                                </tr>
                                <tr style="background-color: #f2f2f2;">
                                    <td style="padding: 8px; font-weight: bold;">Escuela:</td>
                                    <td style="padding: 8px;">{alumno.get('escuela', 'No disponible')}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px; font-weight: bold;">CCT:</td>
                                    <td style="padding: 8px;">{alumno.get('cct', 'No disponible')}</td>
                                </tr>
                                <tr style="background-color: #f2f2f2;">
                                    <td style="padding: 8px; font-weight: bold;">Tiene calificaciones:</td>
                                    <td style="padding: 8px;">{'✅ Sí' if tiene_calificaciones else '❌ No'}</td>
                                </tr>
                            </table>
                    """

                    # Si tiene calificaciones, mostrarlas
                    if tiene_calificaciones:
                        calificaciones = alumno.get('calificaciones', [])
                        if calificaciones:
                            html += """
                            <div style="margin-top: 15px;">
                                <h4 style="color: #e74c3c; margin-top: 0; margin-bottom: 10px;">📊 Calificaciones</h4>
                                <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                                    <tr style="background-color: #e74c3c; color: white;">
                                        <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Materia</th>
                                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P1</th>
                                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P2</th>
                                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P3</th>
                                        <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Promedio</th>
                                    </tr>
                            """

                            # Añadir filas para cada calificación
                            for j, cal in enumerate(calificaciones):
                                bg_color = "#f2f2f2" if j % 2 == 0 else "white"
                                html += f"""
                                <tr style="background-color: {bg_color};">
                                    <td style="padding: 8px; border: 1px solid #ddd;">{cal.get('nombre', '')}</td>
                                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('i', '-')}</td>
                                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('ii', '-')}</td>
                                    <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('iii', '-')}</td>
                                    <td style="padding: 8px; text-align: center; font-weight: bold; color: #e74c3c; border: 1px solid #ddd;">{cal.get('promedio', '-')}</td>
                                </tr>
                                """

                            html += """
                                </table>
                            </div>
                            """

                    # Cerrar la tarjeta del alumno
                    html += """
                        </div>
                    </div>
                    """

            # Cerrar el contenedor principal
            html += """
            </div>
            """

            # Mostrar el HTML en el chat
            self.chat_area.append(html)

            # Desplazar al final
            cursor = self.chat_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_area.setTextCursor(cursor)

        except Exception as e:
            # Si hay algún error, mostrar los alumnos en formato simple
            alumnos_text = "Alumnos encontrados:\n"
            for i, alumno in enumerate(alumnos, 1):
                alumnos_text += f"{i}. {alumno.get('nombre', '').upper()} (ID: {alumno.get('id', '')})\n"
            self.add_ai_message(alumnos_text)
            print(f"Error al mostrar alumnos en tabla: {str(e)}")

    def mostrar_detalle_alumno(self, alumno):
        """Muestra los detalles de un solo alumno"""
        try:
            # Verificar si el alumno existe
            if not alumno:
                self.add_ai_message("No se encontraron detalles del alumno.")
                return

            # Determinar si tiene calificaciones
            tiene_calificaciones = alumno.get('calificaciones') and len(alumno.get('calificaciones', [])) > 0

            # Crear HTML para mostrar los detalles del alumno
            html = f"""
            <div style="background-color: #f8f9fa; border: 1px solid #dfe1e5; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                <div style="background-color: #3498db; color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="margin: 0;">📋 Detalles del Alumno</h3>
                </div>

                <div style="border: 1px solid #ddd; border-radius: 8px; margin-bottom: 15px; padding: 0;">
                    <div style="background-color: #3498db; color: white; padding: 10px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
                        <h4 style="margin: 0;">{alumno.get('nombre', 'Sin nombre').upper()} (ID: {alumno.get('id', 'N/A')})</h4>
                    </div>
                    <div style="padding: 15px;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold; width: 30%;">CURP:</td>
                                <td style="padding: 8px;">{alumno.get('curp', 'No disponible')}</td>
                            </tr>
                            <tr style="background-color: #f2f2f2;">
                                <td style="padding: 8px; font-weight: bold;">Matrícula:</td>
                                <td style="padding: 8px;">{alumno.get('matricula', 'No disponible')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Fecha de Nacimiento:</td>
                                <td style="padding: 8px;">{alumno.get('fecha_nacimiento', 'No disponible')}</td>
                            </tr>
                            <tr style="background-color: #f2f2f2;">
                                <td style="padding: 8px; font-weight: bold;">Grado:</td>
                                <td style="padding: 8px;">{alumno.get('grado', 'No disponible')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Grupo:</td>
                                <td style="padding: 8px;">{alumno.get('grupo', 'No disponible')}</td>
                            </tr>
                            <tr style="background-color: #f2f2f2;">
                                <td style="padding: 8px; font-weight: bold;">Turno:</td>
                                <td style="padding: 8px;">{alumno.get('turno', 'No disponible')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">Ciclo Escolar:</td>
                                <td style="padding: 8px;">{alumno.get('ciclo_escolar', 'No disponible')}</td>
                            </tr>
                            <tr style="background-color: #f2f2f2;">
                                <td style="padding: 8px; font-weight: bold;">Escuela:</td>
                                <td style="padding: 8px;">{alumno.get('escuela', 'No disponible')}</td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">CCT:</td>
                                <td style="padding: 8px;">{alumno.get('cct', 'No disponible')}</td>
                            </tr>
                            <tr style="background-color: #f2f2f2;">
                                <td style="padding: 8px; font-weight: bold;">Tiene calificaciones:</td>
                                <td style="padding: 8px;">{'✅ Sí' if tiene_calificaciones else '❌ No'}</td>
                            </tr>
                        </table>
            """

            # Si tiene calificaciones, mostrarlas
            if tiene_calificaciones:
                calificaciones = alumno.get('calificaciones', [])
                if calificaciones:
                    html += """
                    <div style="margin-top: 15px;">
                        <h4 style="color: #e74c3c; margin-top: 0; margin-bottom: 10px;">📊 Calificaciones</h4>
                        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
                            <tr style="background-color: #e74c3c; color: white;">
                                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Materia</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P1</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P2</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">P3</th>
                                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Promedio</th>
                            </tr>
                    """

                    # Añadir filas para cada calificación
                    for j, cal in enumerate(calificaciones):
                        bg_color = "#f2f2f2" if j % 2 == 0 else "white"
                        html += f"""
                        <tr style="background-color: {bg_color};">
                            <td style="padding: 8px; border: 1px solid #ddd;">{cal.get('nombre', '')}</td>
                            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('i', '-')}</td>
                            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('ii', '-')}</td>
                            <td style="padding: 8px; text-align: center; border: 1px solid #ddd;">{cal.get('iii', '-')}</td>
                            <td style="padding: 8px; text-align: center; font-weight: bold; color: #e74c3c; border: 1px solid #ddd;">{cal.get('promedio', '-')}</td>
                        </tr>
                        """

                    html += """
                        </table>
                    </div>
                    """

            # Eliminamos la sección de constancias generadas para simplificar la interfaz
            # y enfocarnos en la practicidad, como solicitó el usuario

            # Cerrar la tarjeta del alumno y el contenedor principal
            html += """
                    </div>
                </div>

                <div style="background-color: #d5f5e3; border: 1px solid #2ecc71; border-radius: 8px; padding: 15px; margin-top: 10px;">
                    <h4 style="color: #27ae60; margin-top: 0; margin-bottom: 10px;">✅ Acciones Disponibles</h4>
                    <ul>
                        <li>Generar constancia de estudios</li>
            """

            # Añadir opciones según si tiene calificaciones
            if tiene_calificaciones:
                html += """
                        <li>Generar constancia de calificaciones</li>
                        <li>Generar constancia de traslado</li>
                """

            html += """
                        <li>Actualizar datos del alumno</li>
                        <li>Eliminar alumno</li>
                    </ul>
                </div>
            </div>
            """

            # Mostrar el HTML en el chat
            self.chat_area.append(html)

            # Desplazar al final
            cursor = self.chat_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_area.setTextCursor(cursor)

        except Exception as e:
            # Si hay algún error, mostrar los datos del alumno en formato simple
            alumno_text = f"Detalles del alumno:\n"
            alumno_text += f"Nombre: {alumno.get('nombre', 'No disponible').upper()}\n"
            alumno_text += f"CURP: {alumno.get('curp', 'No disponible')}\n"
            alumno_text += f"Grado: {alumno.get('grado', 'No disponible')}\n"
            alumno_text += f"Grupo: {alumno.get('grupo', 'No disponible')}\n"
            alumno_text += f"Turno: {alumno.get('turno', 'No disponible')}\n"
            self.add_ai_message(alumno_text)
            print(f"Error al mostrar detalles del alumno: {str(e)}")

    def obtener_dato_especifico(self, alumno_id=None, nombre=None, campo=None):
        """Obtiene y muestra un dato específico de un alumno"""
        from app.services.alumno_service import AlumnoService
        import unicodedata

        if not campo:
            self.add_ai_message("No se especificó qué dato consultar.")
            return

        try:
            # Inicializar servicio
            alumno_service = AlumnoService()

            # Buscar alumno por ID o nombre
            alumno = None
            if alumno_id:
                alumno = alumno_service.get_alumno_by_id(alumno_id)
            elif nombre:
                # Obtener todos los alumnos para búsqueda flexible
                todos_alumnos = alumno_service.listar_alumnos(limit=100)

                # Normalizar el nombre de búsqueda (eliminar acentos y convertir a minúsculas)
                def normalizar_texto(texto):
                    if not texto:
                        return ""
                    # Convertir a minúsculas
                    texto = texto.lower()
                    # Normalizar caracteres Unicode (NFD descompone los caracteres acentuados)
                    texto = unicodedata.normalize('NFD', texto)
                    # Eliminar los caracteres no ASCII (como los acentos)
                    texto = ''.join(c for c in texto if not unicodedata.combining(c))
                    return texto

                nombre_normalizado = normalizar_texto(nombre)

                # Buscar coincidencias
                alumnos = []
                for a in todos_alumnos:
                    nombre_alumno = a.get('nombre', '')
                    nombre_alumno_normalizado = normalizar_texto(nombre_alumno)

                    # Verificar si el nombre normalizado está contenido en el nombre del alumno normalizado
                    if nombre_normalizado in nombre_alumno_normalizado:
                        alumnos.append(a)

                if alumnos and len(alumnos) == 1:
                    alumno = alumnos[0]
                elif alumnos and len(alumnos) > 1:
                    # Si hay múltiples coincidencias, mostrar mensaje específico
                    self.add_ai_message(f"Encontré varios alumnos con ese nombre. Por favor, sé más específico o usa el ID del alumno.")
                    # Mostrar lista de alumnos encontrados
                    self.mostrar_alumnos_tabla(alumnos)
                    return
                else:
                    self.add_ai_message("No encontré ningún alumno con ese nombre.")
                    return

            if not alumno:
                self.add_ai_message("No encontré ningún alumno con ese nombre o ID.")
                return

            # Mapeo de nombres de campos amigables a las claves en el diccionario
            campo_mapping = {
                "curp": "curp",
                "nombre": "nombre",
                "matricula": "matricula",
                "fecha de nacimiento": "fecha_nacimiento",
                "fecha_nacimiento": "fecha_nacimiento",
                "grado": "grado",
                "grupo": "grupo",
                "turno": "turno",
                "ciclo escolar": "ciclo_escolar",
                "ciclo_escolar": "ciclo_escolar",
                "escuela": "escuela",
                "cct": "cct"
            }

            # Normalizar el campo (convertir a minúsculas y buscar en el mapeo)
            campo_normalizado = campo.lower()
            campo_real = campo_mapping.get(campo_normalizado)

            if not campo_real or campo_real not in alumno:
                self.add_ai_message(f"No pude encontrar el dato '{campo}' para este alumno. Los campos disponibles son: nombre, CURP, matrícula, fecha de nacimiento, grado, grupo, turno, ciclo escolar, escuela y CCT.")
                return

            # Obtener el valor del campo
            valor = alumno.get(campo_real, "No disponible")

            # Nombres amigables para los campos (para mostrar en la respuesta)
            nombres_amigables = {
                "curp": "CURP",
                "nombre": "nombre",
                "matricula": "matrícula",
                "fecha_nacimiento": "fecha de nacimiento",
                "grado": "grado",
                "grupo": "grupo",
                "turno": "turno",
                "ciclo_escolar": "ciclo escolar",
                "escuela": "escuela",
                "cct": "CCT"
            }

            nombre_amigable = nombres_amigables.get(campo_real, campo)

            # Crear una respuesta amigable con formato HTML
            html = f"""
            <div style="background-color: #f8f9fa; border: 1px solid #dfe1e5; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #3498db; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; margin-right: 15px;">
                        <span style="font-size: 20px;">ℹ️</span>
                    </div>
                    <h3 style="margin: 0; color: #3498db;">Información Solicitada</h3>
                </div>

                <p style="font-size: 16px; margin-top: 15px; margin-bottom: 5px;">
                    El <b>{nombre_amigable}</b> de <b>{alumno.get('nombre')}</b> es:
                </p>

                <div style="background-color: #e8f4f8; border-left: 4px solid #3498db; padding: 10px 15px; margin-top: 10px; font-size: 18px;">
                    {valor}
                </div>
            </div>
            """

            # Mostrar la respuesta
            self.chat_area.append(html)

            # Desplazar al final
            cursor = self.chat_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.chat_area.setTextCursor(cursor)

        except Exception as e:
            self.add_ai_message(f"Error al obtener el dato específico: {str(e)}")
        finally:
            # Cerrar conexión
            if 'alumno_service' in locals():
                alumno_service.close()

    def handle_gemini_error(self, error_message):
        """Maneja errores en la comunicación con Gemini"""
        # Ocultar la barra de progreso
        self.progress_bar.setVisible(False)

        # Mostrar mensaje de error
        self.add_ai_message(f"Lo siento, ocurrió un error: {error_message}")
        self.add_ai_message("Por favor, intenta de nuevo más tarde.")

# Función para iniciar la aplicación
def run_ai_chat():
    app = QApplication(sys.argv)
    window = AIChatWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_ai_chat()
