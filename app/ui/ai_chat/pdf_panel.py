"""
Panel para visualización de PDFs con soporte para drag and drop
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QFrame, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from app.ui.pdf_viewer import PDFViewer
from app.core.pdf_extractor import PDFExtractor
from app.core.service_provider import ServiceProvider

class PDFPanel(QWidget):
    """Panel para visualización y gestión de PDFs con soporte para drag and drop"""

    # Señal emitida cuando se carga un PDF
    pdf_loaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pdf = None  # PDF actualmente mostrado en el visor
        self.original_pdf = None  # Referencia al PDF original cargado
        self.transformed_pdf = None  # Referencia al PDF transformado (si existe)
        self.pdf_data = None  # Datos extraídos del PDF original
        self.tiene_calificaciones = False
        self.setAcceptDrops(True)  # Habilitar soporte para drag and drop

        # Obtener el servicio de constancias
        service_provider = ServiceProvider.get_instance()
        self.constancia_service = service_provider.constancia_service

        self.setup_ui()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Maneja el evento de arrastrar un archivo sobre el widget"""
        # Verificar si lo que se está arrastrando es un archivo PDF
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Maneja el evento de soltar un archivo en el widget"""
        # Procesar el primer archivo PDF que se suelte
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.process_dropped_file(file_path)
                event.acceptProposedAction()
                return
        event.ignore()

    def process_dropped_file(self, file_path):
        """Procesa un archivo PDF soltado en el widget"""
        if not self._validate_pdf_file(file_path):
            return False

        # Guardar referencias al PDF
        self._set_pdf_references(file_path)

        # Actualizar la interfaz de usuario
        self._update_ui_for_loaded_pdf(file_path)

        # Extraer datos del PDF automáticamente
        self._extract_pdf_data()

        # Emitir señal de PDF cargado
        self.pdf_loaded.emit()

        return True

    def _validate_pdf_file(self, file_path):
        """Valida que el archivo sea un PDF válido"""
        return os.path.exists(file_path) and file_path.lower().endswith('.pdf')

    def _set_pdf_references(self, file_path):
        """Establece las referencias al PDF cargado"""
        self.current_pdf = file_path
        self.original_pdf = file_path  # Guardar referencia al PDF original
        self.transformed_pdf = None  # Reiniciar referencia al PDF transformado

    def _update_ui_for_loaded_pdf(self, file_path):
        """Actualiza la interfaz de usuario para mostrar el PDF cargado"""
        filename = os.path.basename(file_path)

        # Actualizar etiqueta de PDF cargado
        self._update_pdf_label(filename)

        # Mostrar el PDF en el visor
        self.pdf_viewer.load_pdf(file_path)

        # Configurar la visibilidad de los componentes
        self._update_component_visibility()

        # Actualizar el estilo del área de drop
        self._update_drop_area_style()

    def _update_pdf_label(self, filename):
        """Actualiza las etiquetas relacionadas con el PDF"""
        # Etiqueta de PDF cargado
        self.current_pdf_label.setText(f"✓ PDF cargado: {filename}")
        self.current_pdf_label.setStyleSheet("font-size: 12px; color: #7FB3D5; margin-top: 5px; font-weight: bold;")

        # Título de la vista previa
        self.preview_label.setText(f"Vista Previa: {filename}")

        # Texto del área de drop
        self.drop_label.setText("✓ PDF cargado correctamente")
        self.drop_label.setStyleSheet("color: #2ECC71; font-weight: bold;")

    def _update_component_visibility(self):
        """Actualiza la visibilidad de los componentes de la interfaz"""
        # Ocultar los botones de navegación entre PDFs
        self.pdf_viewer.view_original_btn.setVisible(False)
        self.pdf_viewer.view_transformed_btn.setVisible(False)

        # Mostrar el área de vista previa y ocultar el mensaje
        self.preview_container.setVisible(True)
        self.no_pdf_message.setVisible(False)

    def _update_drop_area_style(self):
        """Actualiza el estilo del área de drop para indicar éxito"""
        self.drop_area.setStyleSheet("""
            QFrame {
                border: 1px solid #2ECC71;
                border-radius: 8px;
                background-color: #1E3A5F;
                padding: 8px;
            }
        """)

    def _extract_pdf_data(self):
        """Extrae los datos del PDF cargado"""
        try:
            # Extraer datos del PDF original
            extractor = PDFExtractor(self.original_pdf)

            # Verificar si la constancia tiene calificaciones
            self.tiene_calificaciones = extractor.tiene_calificaciones()

            # Extraer todos los datos
            self.pdf_data = extractor.extraer_todos_datos(
                incluir_foto=True,
                tipo_constancia_solicitado=None  # Usar None para no eliminar las calificaciones
            )
        except Exception as e:
            print(f"Error al extraer datos del PDF: {e}")
            # No mostrar mensaje de error aquí para no interrumpir la carga

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar el widget principal con fondo oscuro
        self.setStyleSheet("background-color: #1A1A2E;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Sección de carga de PDF con área de drop - estilo modo oscuro
        self.drop_area = QFrame()
        self.drop_area.setFrameShape(QFrame.StyledPanel)
        self.drop_area.setStyleSheet("""
            QFrame {
                border: 1px dashed #3498DB;
                border-radius: 8px;
                background-color: #1E3A5F;
                padding: 15px;
                margin-bottom: 5px;
            }
        """)
        self.drop_area.setMinimumHeight(120)  # Altura mínima para el área de drop

        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignCenter)

        # Título del área de drop
        self.drop_label = QLabel("Arrastra y suelta un PDF aquí")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #7FB3D5; margin-bottom: 10px;")

        # Icono o indicador visual
        drop_icon_label = QLabel("📄")
        drop_icon_label.setAlignment(Qt.AlignCenter)
        drop_icon_label.setStyleSheet("font-size: 24px; color: #3498DB; margin: 5px;")

        # Instrucciones adicionales
        drop_instructions = QLabel("o haz clic en el botón para seleccionar un archivo")
        drop_instructions.setAlignment(Qt.AlignCenter)
        drop_instructions.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.7);")

        # Botón de carga
        pdf_upload_button = QPushButton("Seleccionar PDF")
        pdf_upload_button.setCursor(Qt.PointingHandCursor)  # Cambiar cursor al pasar sobre el botón
        pdf_upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 5px;
                border: none;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 10px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        pdf_upload_button.clicked.connect(self.load_pdf)

        # Etiqueta para mostrar el archivo actual
        self.current_pdf_label = QLabel("Ningún PDF cargado")
        self.current_pdf_label.setAlignment(Qt.AlignCenter)
        self.current_pdf_label.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.7); margin-top: 5px;")
        self.current_pdf_label.setWordWrap(True)
        self.current_pdf_label.setVisible(False)  # Ocultar inicialmente

        # Añadir widgets al layout del área de drop
        drop_layout.addWidget(self.drop_label)
        drop_layout.addWidget(drop_icon_label)
        drop_layout.addWidget(drop_instructions)
        drop_layout.addWidget(pdf_upload_button, 0, Qt.AlignCenter)
        drop_layout.addWidget(self.current_pdf_label)

        # Sección de vista previa
        self.preview_container = QWidget()
        preview_container_layout = QVBoxLayout(self.preview_container)
        preview_container_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("Vista Previa")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #7FB3D5; margin-bottom: 5px;")

        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.setStyleSheet("""
            QScrollArea {
                border: 1px solid #2C4F7C;
                border-radius: 8px;
                background-color: #16213E;
            }
            QScrollBar:vertical {
                background: #16213E;
                width: 12px;  /* Más ancho para facilitar su uso */
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.4);  /* Más visible */
                min-height: 30px;  /* Más alto para facilitar su uso */
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.7);  /* Más visible al pasar el mouse */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #16213E;
                height: 12px;  /* Más alto para facilitar su uso */
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(255, 255, 255, 0.4);  /* Más visible */
                min-width: 30px;  /* Más ancho para facilitar su uso */
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(255, 255, 255, 0.7);  /* Más visible al pasar el mouse */
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        # Crear un botón para cancelar/quitar el PDF cargado
        cancel_button = QPushButton("❌ Quitar PDF")
        cancel_button.setToolTip("Quitar el PDF actual y cargar otro")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;  /* Aumentar el padding para botones más grandes */
                font-size: 13px;    /* Aumentar el tamaño de fuente */
                font-weight: bold;
                margin-top: 5px;
                margin-bottom: 5px;
                min-width: 120px;   /* Establecer un ancho mínimo */
                min-height: 35px;   /* Establecer una altura mínima */
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
            QPushButton:pressed {
                background-color: #A93226;
            }
        """)
        cancel_button.clicked.connect(self.clear_pdf)

        # Crear un botón para extraer y mostrar los datos del PDF
        extract_button = QPushButton("📋 Ver Datos")
        extract_button.setToolTip("Extraer y mostrar los datos del PDF")
        extract_button.setCursor(Qt.PointingHandCursor)
        extract_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;  /* Aumentar el padding para botones más grandes */
                font-size: 13px;    /* Aumentar el tamaño de fuente */
                font-weight: bold;
                margin-top: 5px;
                margin-bottom: 5px;
                min-width: 120px;   /* Establecer un ancho mínimo */
                min-height: 35px;   /* Establecer una altura mínima */
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        extract_button.clicked.connect(self.extract_and_show_data)

        # Configurar los botones para ver PDF original y transformado
        self.pdf_viewer.view_original_btn.clicked.connect(self.show_original_pdf)
        self.pdf_viewer.view_transformed_btn.clicked.connect(self.show_transformed_pdf)

        # Crear un layout para el encabezado con título
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.preview_label, 1)  # 1 = stretch factor

        # Crear un layout para los botones de acción
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # Aumentar el espacio entre botones

        # Establecer un ancho mínimo para los botones para evitar que se compriman
        extract_button.setMinimumWidth(120)
        cancel_button.setMinimumWidth(120)

        # Añadir los botones al layout de botones
        button_layout.addWidget(extract_button)
        button_layout.addWidget(cancel_button)

        # Crear un layout vertical para el encabezado y los botones
        top_layout = QVBoxLayout()
        top_layout.setSpacing(5)  # Reducir el espacio entre el encabezado y los botones
        top_layout.addLayout(header_layout)
        top_layout.addLayout(button_layout)

        # Añadir widgets al contenedor de vista previa
        preview_container_layout.addLayout(top_layout)
        preview_container_layout.addWidget(self.pdf_viewer.main_widget)  # Usar el widget principal que contiene todo

        # Ocultar el contenedor de vista previa inicialmente
        self.preview_container.setVisible(False)

        # Añadir mensaje informativo cuando no hay PDF - estilo modo oscuro
        self.no_pdf_message = QLabel("""
            <div style='text-align: center;'>
                <p style='font-size: 16px; color: #7FB3D5; margin-bottom: 15px;'>
                    <b>Instrucciones para transformar un PDF</b>
                </p>
                <p style='color: rgba(255, 255, 255, 0.8); margin-bottom: 10px;'>
                    1. Carga un PDF usando el área de arriba
                </p>
                <p style='color: rgba(255, 255, 255, 0.8); margin-bottom: 10px;'>
                    2. Escribe en el chat: "Transforma este PDF a constancia de estudios"
                </p>
                <p style='color: rgba(255, 255, 255, 0.8);'>
                    3. El asistente extraerá la información y generará la constancia
                </p>
            </div>
        """)
        self.no_pdf_message.setAlignment(Qt.AlignCenter)
        self.no_pdf_message.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #16213E;
                border: 1px solid #2C4F7C;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)

        # Añadir widgets al layout principal
        main_layout.addWidget(self.drop_area)
        main_layout.addWidget(self.no_pdf_message, 1)
        main_layout.addWidget(self.preview_container, 1)

    def load_pdf(self):
        """Carga un PDF para transformación"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Archivos PDF (*.pdf)")
        file_dialog.setWindowTitle("Seleccionar PDF para transformación")

        # Intentar aplicar estilo al diálogo de archivos
        try:
            file_dialog.setStyleSheet("""
                QFileDialog {
                    background-color: #1A1A2E;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #1E3A5F;
                    color: white;
                    border: 1px solid #2C4F7C;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2C4F7C;
                }
                QLineEdit, QComboBox {
                    background-color: #16213E;
                    color: white;
                    border: 1px solid #2C4F7C;
                    border-radius: 4px;
                    padding: 3px;
                }
            """)
        except:
            # Algunos sistemas pueden no soportar estilizar el QFileDialog
            pass

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                pdf_path = selected_files[0]
                # Procesar el archivo usando el método común
                self.process_dropped_file(pdf_path)

                return pdf_path, True

        return None, False

    def clear_pdf(self):
        """Quita el PDF actual y restablece el panel"""
        # Cerrar el PDF en el visor
        self.pdf_viewer.close_pdf()

        # Restablecer todas las referencias a PDFs
        self.current_pdf = None
        self.original_pdf = None
        self.transformed_pdf = None
        self.pdf_data = None
        self.tiene_calificaciones = False

        # Ocultar los botones de navegación entre PDFs
        self.pdf_viewer.view_original_btn.setVisible(False)
        self.pdf_viewer.view_transformed_btn.setVisible(False)

        # Actualizar la interfaz
        self.current_pdf_label.setText("Ningún PDF cargado")
        self.current_pdf_label.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.7); margin-top: 5px;")
        self.current_pdf_label.setVisible(False)

        # Restablecer el área de drop
        self.drop_label.setText("Arrastra y suelta un PDF aquí")
        self.drop_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #7FB3D5; margin-bottom: 10px;")
        self.drop_area.setStyleSheet("""
            QFrame {
                border: 1px dashed #3498DB;
                border-radius: 8px;
                background-color: #1E3A5F;
                padding: 15px;
                margin-bottom: 5px;
            }
        """)

        # Ocultar el área de vista previa y mostrar el mensaje
        self.preview_container.setVisible(False)
        self.no_pdf_message.setVisible(True)

        # Emitir señal de que se ha quitado el PDF (opcional)
        # Podríamos añadir una señal pdf_removed si fuera necesario

    def extract_and_show_data(self):
        """Extrae y muestra los datos del PDF cargado"""
        if not self.original_pdf:
            QMessageBox.warning(self, "Error", "No hay ningún PDF cargado.")
            return

        try:
            # Siempre extraer datos del PDF original, no del transformado
            extractor = PDFExtractor(self.original_pdf)

            # Verificar si la constancia tiene calificaciones
            self.tiene_calificaciones = extractor.tiene_calificaciones()

            # Extraer todos los datos
            try:
                # No especificamos tipo_constancia_solicitado para que no elimine las calificaciones
                self.pdf_data = extractor.extraer_todos_datos(
                    incluir_foto=True,
                    tipo_constancia_solicitado=None  # Usar None para no eliminar las calificaciones
                )
            except ValueError as ve:
                # Si hay un error específico de validación, mostrar mensaje
                QMessageBox.warning(self, "Advertencia", str(ve))
                return

            # Mostrar información sobre el contenido del PDF
            self.mostrar_info_contenido_pdf()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al extraer datos del PDF: {str(e)}")

    def mostrar_info_contenido_pdf(self):
        """Muestra información sobre el contenido del PDF cargado"""
        if not self.pdf_data:
            return

        # Crear un mensaje con la información del PDF en un estilo más moderno y legible
        mensaje = """
        <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.5;">
            <h2 style="color: #3498DB; margin-top: 0; margin-bottom: 15px; text-align: center; font-size: 20px;">
                Información Extraída del PDF
            </h2>

            <div style="background-color: #EBF5FB; border-left: 4px solid #3498DB; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
                <h3 style="color: #2874A6; margin-top: 0; margin-bottom: 10px; font-size: 16px;">
                    Datos Personales
                </h3>
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Nombre:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">CURP:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
        """.format(
            self.pdf_data.get('nombre', 'No disponible'),
            self.pdf_data.get('curp', 'No disponible')
        )

        if self.pdf_data.get('matricula'):
            mensaje += """
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Matrícula:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
            """.format(self.pdf_data.get('matricula'))

        if self.pdf_data.get('nacimiento'):
            mensaje += """
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Fecha de nacimiento:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
            """.format(self.pdf_data.get('nacimiento'))

        mensaje += """
            </div>

            <div style="background-color: #E8F8F5; border-left: 4px solid #1ABC9C; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
                <h3 style="color: #16A085; margin-top: 0; margin-bottom: 10px; font-size: 16px;">
                    Datos Escolares
                </h3>
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Grado:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Grupo:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Turno:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Ciclo escolar:</span>
                    <span style="color: #34495E;">{}</span>
                </p>
            </div>
        """.format(
            self.pdf_data.get('grado', 'No disponible'),
            self.pdf_data.get('grupo', 'No disponible'),
            self.pdf_data.get('turno', 'No disponible'),
            self.pdf_data.get('ciclo', 'No disponible')
        )

        # Información sobre calificaciones
        if self.tiene_calificaciones:
            mensaje += """
            <div style="background-color: #EBF5FB; border-left: 4px solid #3498DB; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
                <h3 style="color: #2874A6; margin-top: 0; margin-bottom: 10px; font-size: 16px;">
                    Calificaciones <span style="color: #27AE60;">✓</span>
                </h3>
                <p style="margin: 5px 0; color: #27AE60;">
                    Se podrán generar constancias de calificaciones y traslado.
                </p>
            """

            # Mostrar resumen de calificaciones
            calificaciones = self.pdf_data.get('calificaciones', [])
            if calificaciones:
                # Crear una tabla más clara y visible para las calificaciones
                mensaje += """
                <div style="margin-top: 15px; margin-bottom: 15px;">
                    <h4 style="color: #2874A6; margin-top: 0; margin-bottom: 10px; font-size: 15px; text-align: center;">
                        Tabla de Calificaciones
                    </h4>
                    <div style="box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px; background-color: white;">
                            <thead>
                                <tr style="background-color: #3498DB; color: white;">
                                    <th style="padding: 12px 15px; text-align: left; border: 1px solid #AED6F1; font-weight: bold;">Materia</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #AED6F1; font-weight: bold;">Periodo 1</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #AED6F1; font-weight: bold;">Periodo 2</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #AED6F1; font-weight: bold;">Periodo 3</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #AED6F1; font-weight: bold; background-color: #2874A6;">Promedio</th>
                                </tr>
                            </thead>
                            <tbody>
                """

                for i, cal in enumerate(calificaciones):
                    bg_color = "#F8FBFD" if i % 2 == 0 else "#EBF5FB"
                    promedio_color = "#27AE60" if cal.get('promedio', 0) >= 8 else "#F39C12" if cal.get('promedio', 0) >= 6 else "#E74C3C"

                    mensaje += f"""
                                <tr style="background-color: {bg_color};">
                                    <td style="padding: 12px 15px; border: 1px solid #D6EAF8; font-weight: bold;">{cal.get('nombre', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; border: 1px solid #D6EAF8;">{cal.get('i', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; border: 1px solid #D6EAF8;">{cal.get('ii', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; border: 1px solid #D6EAF8;">{cal.get('iii', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; font-weight: bold; border: 1px solid #D6EAF8; color: {promedio_color};">{cal.get('promedio', '')}</td>
                                </tr>
                    """

                mensaje += """
                            </tbody>
                        </table>
                    </div>
                </div>
                """

            mensaje += """
            </div>
            """
        else:
            mensaje += """
            <div style="background-color: #FDEDEC; border-left: 4px solid #E74C3C; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
                <h3 style="color: #C0392B; margin-top: 0; margin-bottom: 10px; font-size: 16px;">
                    Calificaciones <span style="color: #E74C3C;">✗</span>
                </h3>
                <p style="margin: 5px 0; color: #C0392B;">
                    No se encontraron calificaciones. Solo se podrán generar constancias de estudios.
                </p>
            </div>
            """

        # Añadir opciones para guardar en la base de datos
        mensaje += """
            <div style="background-color: #F4F6F7; border-left: 4px solid #7F8C8D; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
                <h3 style="color: #566573; margin-top: 0; margin-bottom: 10px; font-size: 16px;">
                    Opciones Disponibles
                </h3>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li style="margin-bottom: 5px;">
                        Para guardar estos datos en la base de datos, escribe en el chat:
                        <span style="font-style: italic; color: #2980B9;">"Guardar datos del PDF en la base de datos"</span>
                    </li>
                    <li style="margin-bottom: 5px;">
                        Para transformar el PDF, escribe en el chat:
                        <span style="font-style: italic; color: #2980B9;">"Transformar este PDF a constancia de estudios"</span>
                    </li>
                </ul>
            </div>
        </div>
        """

        # Mostrar el mensaje en un diálogo informativo
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton

        # Crear un diálogo personalizado
        dialog = QDialog(self)
        dialog.setWindowTitle("Datos Extraídos del PDF")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        # Establecer estilo para el diálogo
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)

        # Crear layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)

        # Crear un QTextBrowser para mostrar el HTML
        text_browser = QTextBrowser()
        text_browser.setHtml(mensaje)
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: white;
                font-size: 14px;
            }
        """)

        # Botón de cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)

        # Añadir widgets al layout
        layout.addWidget(text_browser)
        layout.addWidget(close_button, 0, Qt.AlignCenter)

        # Mostrar el diálogo
        dialog.exec_()

    def get_current_pdf(self):
        """Devuelve la ruta del PDF actual mostrado en el visor"""
        return self.current_pdf

    def get_original_pdf(self):
        """Devuelve la ruta del PDF original cargado"""
        return self.original_pdf

    def get_pdf_data(self):
        """Devuelve los datos extraídos del PDF"""
        return self.pdf_data

    def show_original_pdf(self):
        """Muestra el PDF original en el visor"""
        if not self.original_pdf or not os.path.exists(self.original_pdf):
            return False

        # Guardar el estado actual del visor
        current_zoom = self.pdf_viewer.zoom_factor
        current_page = self.pdf_viewer.current_page

        # Guardar la posición de desplazamiento actual
        h_value = self.pdf_viewer.horizontalScrollBar().value()
        v_value = self.pdf_viewer.verticalScrollBar().value()

        # Calcular la posición relativa (porcentaje) del centro de la vista
        viewport_width = self.pdf_viewer.viewport().width()
        viewport_height = self.pdf_viewer.viewport().height()
        content_width = self.pdf_viewer.container.width()
        content_height = self.pdf_viewer.container.height()

        # Evitar división por cero
        if content_width > 0 and content_height > 0:
            center_x_percent = (h_value + viewport_width / 2) / content_width
            center_y_percent = (v_value + viewport_height / 2) / content_height
        else:
            center_x_percent = 0.5
            center_y_percent = 0.5

        # Cambiar al PDF original
        self.current_pdf = self.original_pdf

        # Cargar el PDF pero mantener el zoom y la página
        self.pdf_viewer.load_pdf(self.original_pdf, maintain_state=True,
                                zoom=current_zoom, page=current_page)

        # Actualizar el título
        filename = os.path.basename(self.original_pdf)
        self.preview_label.setText(f"Vista Previa (Original): {filename}")

        # Actualizar los botones
        self.pdf_viewer.view_original_btn.setEnabled(False)
        self.pdf_viewer.view_transformed_btn.setEnabled(self.transformed_pdf is not None)

        # Esperar a que se actualice la interfaz
        QApplication.processEvents()

        # Restaurar la posición de desplazamiento
        new_content_width = self.pdf_viewer.container.width()
        new_content_height = self.pdf_viewer.container.height()

        if new_content_width > 0 and new_content_height > 0:
            new_h_value = max(0, (center_x_percent * new_content_width) - (viewport_width / 2))
            new_v_value = max(0, (center_y_percent * new_content_height) - (viewport_height / 2))

            # Aplicar las nuevas posiciones de desplazamiento
            self.pdf_viewer.horizontalScrollBar().setValue(int(new_h_value))
            self.pdf_viewer.verticalScrollBar().setValue(int(new_v_value))

        return True

    def show_transformed_pdf(self):
        """Muestra el PDF transformado en el visor"""
        if not self.transformed_pdf or not os.path.exists(self.transformed_pdf):
            return False

        # Guardar el estado actual del visor
        current_zoom = self.pdf_viewer.zoom_factor
        current_page = self.pdf_viewer.current_page

        # Guardar la posición de desplazamiento actual
        h_value = self.pdf_viewer.horizontalScrollBar().value()
        v_value = self.pdf_viewer.verticalScrollBar().value()

        # Calcular la posición relativa (porcentaje) del centro de la vista
        viewport_width = self.pdf_viewer.viewport().width()
        viewport_height = self.pdf_viewer.viewport().height()
        content_width = self.pdf_viewer.container.width()
        content_height = self.pdf_viewer.container.height()

        # Evitar división por cero
        if content_width > 0 and content_height > 0:
            center_x_percent = (h_value + viewport_width / 2) / content_width
            center_y_percent = (v_value + viewport_height / 2) / content_height
        else:
            center_x_percent = 0.5
            center_y_percent = 0.5

        # Cambiar al PDF transformado
        self.current_pdf = self.transformed_pdf

        # Cargar el PDF pero mantener el zoom y la página
        self.pdf_viewer.load_pdf(self.transformed_pdf, maintain_state=True,
                                zoom=current_zoom, page=current_page)

        # Actualizar el título
        filename = os.path.basename(self.transformed_pdf)
        self.preview_label.setText(f"Vista Previa (Transformado): {filename}")

        # Actualizar los botones
        self.pdf_viewer.view_original_btn.setEnabled(True)
        self.pdf_viewer.view_transformed_btn.setEnabled(False)

        # Esperar a que se actualice la interfaz
        QApplication.processEvents()

        # Restaurar la posición de desplazamiento
        new_content_width = self.pdf_viewer.container.width()
        new_content_height = self.pdf_viewer.container.height()

        if new_content_width > 0 and new_content_height > 0:
            new_h_value = max(0, (center_x_percent * new_content_width) - (viewport_width / 2))
            new_v_value = max(0, (center_y_percent * new_content_height) - (viewport_height / 2))

            # Aplicar las nuevas posiciones de desplazamiento
            self.pdf_viewer.horizontalScrollBar().setValue(int(new_h_value))
            self.pdf_viewer.verticalScrollBar().setValue(int(new_v_value))

        return True

    def show_pdf(self, pdf_path):
        """Muestra un PDF en el visor"""
        if pdf_path and os.path.exists(pdf_path):
            # Cerrar el PDF actual si hay uno abierto
            self.pdf_viewer.close_pdf()

            # Si es un PDF transformado, guardarlo como tal
            if self.original_pdf and pdf_path != self.original_pdf:
                self.transformed_pdf = pdf_path
                self.current_pdf = pdf_path

                # Cargar el PDF transformado en el visor
                if self.pdf_viewer.load_pdf(pdf_path):
                    # Actualizar el título de la vista previa
                    filename = os.path.basename(pdf_path)
                    self.preview_label.setText(f"Vista Previa (Transformado): {filename}")

                    # Mostrar los botones de navegación entre PDFs
                    self.pdf_viewer.view_original_btn.setEnabled(True)
                    self.pdf_viewer.view_original_btn.setVisible(True)
                    self.pdf_viewer.view_transformed_btn.setEnabled(False)
                    self.pdf_viewer.view_transformed_btn.setVisible(True)

                    # Mostrar el área de vista previa
                    self.preview_container.setVisible(True)
                    self.no_pdf_message.setVisible(False)

                    return True
            else:
                # Si es un PDF nuevo, procesarlo como un nuevo archivo
                return self.process_dropped_file(pdf_path)

        return False

    def show_original_pdf(self):
        """Muestra el PDF original en el visor"""
        if self.original_pdf and os.path.exists(self.original_pdf):
            self.current_pdf = self.original_pdf

            # Cargar el PDF original en el visor
            if self.pdf_viewer.load_pdf(self.original_pdf):
                # Actualizar el título de la vista previa
                filename = os.path.basename(self.original_pdf)
                self.preview_label.setText(f"Vista Previa (Original): {filename}")

                # Actualizar los botones de navegación si hay un PDF transformado
                if self.transformed_pdf:
                    self.pdf_viewer.view_original_btn.setEnabled(False)
                    self.pdf_viewer.view_original_btn.setVisible(True)
                    self.pdf_viewer.view_transformed_btn.setEnabled(True)
                    self.pdf_viewer.view_transformed_btn.setVisible(True)
                else:
                    self.pdf_viewer.view_original_btn.setVisible(False)
                    self.pdf_viewer.view_transformed_btn.setVisible(False)

                # Mostrar el área de vista previa
                self.preview_container.setVisible(True)
                self.no_pdf_message.setVisible(False)

                return True

        return False

    def extract_pdf_data(self, pdf_path=None):
        """Extrae datos del PDF actual o del especificado"""
        # Priorizar el PDF original para extraer datos
        path = pdf_path or self.original_pdf or self.current_pdf

        if not path or not os.path.exists(path):
            return None

        try:
            extractor = PDFExtractor(path)
            datos = extractor.extraer_datos_basicos()
            tiene_calificaciones = extractor.tiene_calificaciones()

            result = {
                "datos_basicos": datos,
                "tiene_calificaciones": tiene_calificaciones
            }

            if tiene_calificaciones:
                result["calificaciones"] = extractor.extraer_calificaciones()

            return result
        except Exception as e:
            print(f"Error al extraer datos del PDF: {str(e)}")
            return None
