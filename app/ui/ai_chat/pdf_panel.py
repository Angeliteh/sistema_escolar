"""
Panel para visualización de PDFs con soporte para drag and drop
"""
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QFrame, QMessageBox, QApplication, QDialog,
    QScrollArea, QTextEdit, QCheckBox
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

        # NUEVO: Variables para contexto del botón "Ver Datos"
        self.data_context = "extracted"  # "extracted" o "constancia_generada"
        self.alumno_data = None  # Datos del alumno para constancias generadas

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

        # Establecer contexto de PDF cargado (si no está ya establecido)
        if not hasattr(self, 'data_context') or self.data_context != "constancia_generada":
            self.set_pdf_external_context()

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
        print(f"🔧 DEBUG: _update_component_visibility - Contexto: {self.data_context}")
        self.preview_container.setVisible(True)
        self.no_pdf_message.setVisible(False)

        # Si es contexto de constancia, actualizar etiquetas específicas
        if self.data_context == "constancia_generada":
            print(f"✅ DEBUG: Preservando contexto de constancia generada")
            # Mantener el texto del botón y etiquetas específicas para constancia
            filename = os.path.basename(self.current_pdf) if self.current_pdf else "constancia"
            self.preview_label.setText(f"🔄 Vista Previa de Constancia: {filename}")
            self.current_pdf_label.setText("✓ Vista previa de constancia generada")
            self.current_pdf_label.setStyleSheet("font-size: 12px; color: #27AE60; margin-top: 5px; font-weight: bold;")
            self.drop_label.setText("✓ Vista previa de constancia generada")
            self.drop_label.setStyleSheet("color: #27AE60; font-weight: bold;")

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
        self.ver_datos_btn = QPushButton("📋 Ver Datos Extraídos")
        self.ver_datos_btn.setToolTip("Extraer y mostrar los datos del PDF")
        self.ver_datos_btn.setCursor(Qt.PointingHandCursor)
        self.ver_datos_btn.setStyleSheet("""
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
        self.ver_datos_btn.clicked.connect(self._show_data_dialog)

        # Configurar los botones para ver PDF original y transformado
        self.pdf_viewer.view_original_btn.clicked.connect(self.show_original_pdf)
        self.pdf_viewer.view_transformed_btn.clicked.connect(self.show_transformed_pdf)

        # Crear un layout para el encabezado con título
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.preview_label, 1)  # 1 = stretch factor

        # 🆕 BOTÓN MEJORADO PARA ABRIR EN NAVEGADOR (CON INDICACIÓN DE IMPRESIÓN)
        self.open_browser_btn = QPushButton("🌐 Abrir en Navegador / Imprimir")
        self.open_browser_btn.setToolTip("Abrir el PDF en el navegador web donde puedes verlo e imprimirlo fácilmente (Ctrl+P)")
        self.open_browser_btn.setCursor(Qt.PointingHandCursor)
        self.open_browser_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 5px;
                margin-bottom: 5px;
                min-width: 180px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)
        self.open_browser_btn.clicked.connect(self._open_in_browser)

        # 🔧 LAYOUT SIMPLIFICADO DE BOTONES (2 FILAS)
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)

        # Primera fila: botones principales
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(10)

        # Segunda fila: botón de navegador/imprimir
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(10)

        # Establecer anchos mínimos
        self.ver_datos_btn.setMinimumWidth(120)
        cancel_button.setMinimumWidth(120)
        self.open_browser_btn.setMinimumWidth(180)

        # Añadir botones a las filas
        first_row_layout.addWidget(self.ver_datos_btn)
        first_row_layout.addWidget(cancel_button)

        second_row_layout.addWidget(self.open_browser_btn)

        # Añadir las filas al layout principal
        button_layout.addLayout(first_row_layout)
        button_layout.addLayout(second_row_layout)

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

    def _open_in_browser(self):
        """Abre el PDF actual en el navegador web"""
        if not self.current_pdf:
            QMessageBox.warning(self, "Sin PDF", "No hay ningún PDF cargado para abrir.")
            return

        try:
            import webbrowser
            import os

            # Convertir a URL de archivo para el navegador
            file_url = f"file:///{os.path.abspath(self.current_pdf).replace(os.sep, '/')}"
            webbrowser.open(file_url)

            # Mostrar mensaje de confirmación mejorado con estilo claro
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("PDF Abierto")
            msg_box.setText(f"✅ El PDF se ha abierto en tu navegador web.\n\n"
                           f"📄 Archivo: {os.path.basename(self.current_pdf)}\n\n"
                           f"💡 Para imprimir: Usa Ctrl+P en el navegador")
            msg_box.setIcon(QMessageBox.Information)

            # 🔧 APLICAR ESTILO CLARO AL MENSAJE
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #2C3E50;
                    font-size: 14px;
                    border: 1px solid #BDC3C7;
                    border-radius: 8px;
                }
                QMessageBox QLabel {
                    color: #2C3E50;
                    font-size: 14px;
                    background-color: transparent;
                }
                QMessageBox QPushButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                    font-size: 13px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #2980B9;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #1F618D;
                }
            """)

            msg_box.exec_()
        except Exception as e:
            # Mensaje de error con estilo claro
            error_box = QMessageBox(self)
            error_box.setWindowTitle("Error")
            error_box.setText(f"No se pudo abrir el PDF en el navegador:\n{str(e)}")
            error_box.setIcon(QMessageBox.Critical)

            # 🔧 APLICAR ESTILO CLARO AL MENSAJE DE ERROR
            error_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: #2C3E50;
                    font-size: 14px;
                    border: 1px solid #E74C3C;
                    border-radius: 8px;
                }
                QMessageBox QLabel {
                    color: #2C3E50;
                    font-size: 14px;
                    background-color: transparent;
                }
                QMessageBox QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                    font-size: 13px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #C0392B;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #A93226;
                }
            """)

            error_box.exec_()



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

        # NUEVO: Restablecer contexto del botón
        self.data_context = "extracted"
        self.alumno_data = None
        self.ver_datos_btn.setText("📋 Ver Datos Extraídos")
        self.ver_datos_btn.setToolTip("Extraer y mostrar los datos del PDF")

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

    def _show_data_dialog(self):
        """Muestra datos según el contexto actual - UNIFICADO para usar siempre el mismo formato"""
        if self.data_context == "constancia_generada":
            self._show_alumno_data_dialog()
        elif self.data_context == "transformacion_pendiente":
            self._show_transformation_pending_dialog()
        else:
            # 🎯 UNIFICADO: Siempre usar el método que funciona bien
            # Esto incluye: pdf_externo, transformacion_completada, pdf_transformado, y cualquier otro
            self.extract_and_show_data()

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

        # 🆕 VERIFICAR SI HAY FOTO EXTRAÍDA
        foto_path = None
        if self.pdf_data.get('foto_path'):
            foto_path = self.pdf_data.get('foto_path')

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

        # 🆕 AGREGAR INFORMACIÓN DE FOTO (SOLO TEXTO)
        if foto_path:
            import os
            if os.path.exists(foto_path):
                mensaje += """
                    <p style="margin: 5px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Foto:</span>
                        <span style="color: #27AE60;">✅ Extraída correctamente (30x40px)</span>
                    </p>
                """
            else:
                mensaje += """
                    <p style="margin: 5px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Foto:</span>
                        <span style="color: #E74C3C;">❌ Archivo no encontrado</span>
                    </p>
                """
        else:
            mensaje += """
                <p style="margin: 5px 0;">
                    <span style="font-weight: bold; color: #2C3E50;">Foto:</span>
                    <span style="color: #95A5A6;">No disponible</span>
                </p>
            """

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

        mensaje += """
        </div>
        """

        # Mostrar el mensaje en un diálogo informativo con opción de guardar
        self._show_legacy_data_dialog_with_save_option(mensaje)

    def _show_legacy_data_dialog_with_save_option(self, mensaje):
        """Muestra el diálogo de datos con opción de guardar en BD (método legacy)"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QCheckBox

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
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
            QPushButton#save_button {
                background-color: #27AE60;
            }
            QPushButton#save_button:hover {
                background-color: #229954;
            }
            QPushButton#save_button:pressed {
                background-color: #1E8449;
            }
            QCheckBox {
                font-size: 14px;
                color: #2C3E50;
                padding: 5px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #BDC3C7;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #27AE60;
                background-color: #27AE60;
                border-radius: 3px;
            }
            QTextBrowser {
                border: none;
                background-color: white;
                font-size: 14px;
            }
        """)

        # Crear layout principal
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

        # Checkbox para guardar en BD
        save_checkbox = QCheckBox("💾 Guardar estos datos en la base de datos")
        save_checkbox.setToolTip("Marca esta opción para registrar al alumno en la base de datos")

        # Layout para botones
        button_layout = QHBoxLayout()

        # Botón de guardar en BD
        save_button = QPushButton("💾 Guardar en BD")
        save_button.setObjectName("save_button")
        save_button.setEnabled(False)  # Inicialmente deshabilitado
        save_button.setToolTip("Guardar los datos extraídos en la base de datos")

        # Botón de cerrar
        close_button = QPushButton("Cerrar")

        # Conectar checkbox con botón
        save_checkbox.toggled.connect(save_button.setEnabled)

        # Conectar botones
        close_button.clicked.connect(dialog.accept)
        save_button.clicked.connect(lambda: self._save_pdf_data_to_database(dialog, save_checkbox))

        # 🆕 AGREGAR FOTO COMO WIDGET SEPARADO SI EXISTE
        foto_path = None
        if self.pdf_data and self.pdf_data.get('foto_path'):
            foto_path = self.pdf_data.get('foto_path')

        if foto_path:
            import os
            from PyQt5.QtWidgets import QLabel
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtCore import Qt

            if os.path.exists(foto_path):
                # Crear contenedor para la foto
                foto_container = QLabel()
                foto_container.setAlignment(Qt.AlignCenter)
                foto_container.setStyleSheet("""
                    QLabel {
                        background-color: #F8F9FA;
                        border: 2px solid #3498DB;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 10px;
                    }
                """)

                # Cargar y redimensionar la imagen
                pixmap = QPixmap(foto_path)
                if not pixmap.isNull():
                    # Redimensionar a 60x80 píxeles
                    scaled_pixmap = pixmap.scaled(60, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    foto_container.setPixmap(scaled_pixmap)
                    foto_container.setToolTip("Foto extraída del PDF")

                    # Agregar la foto al layout
                    layout.addWidget(foto_container)

        # Añadir widgets al layout
        layout.addWidget(text_browser)
        layout.addWidget(save_checkbox)

        button_layout.addWidget(save_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Mostrar el diálogo
        dialog.exec_()

    def _save_pdf_data_to_database(self, dialog, checkbox):
        """Guarda los datos del PDF en la base de datos"""
        if not checkbox.isChecked():
            return

        if not self.pdf_data:
            QMessageBox.warning(dialog, "Error", "No hay datos para guardar.")
            return

        try:
            # 🆕 EXTRAER Y GUARDAR FOTO AUTOMÁTICAMENTE
            foto_guardada = False
            if self.pdf_data.get('foto_path') and self.pdf_data.get('curp'):
                try:
                    import os
                    import shutil
                    foto_origen = self.pdf_data.get('foto_path')
                    curp = self.pdf_data.get('curp')

                    # Crear directorio de fotos si no existe
                    photos_dir = os.path.join("resources", "photos")
                    os.makedirs(photos_dir, exist_ok=True)

                    # Ruta destino: {CURP}.jpg
                    foto_destino = os.path.join(photos_dir, f"{curp}.jpg")

                    # Copiar foto si no existe o es diferente
                    if os.path.exists(foto_origen):
                        if not os.path.exists(foto_destino) or os.path.getsize(foto_origen) != os.path.getsize(foto_destino):
                            shutil.copy2(foto_origen, foto_destino)
                            foto_guardada = True
                            print(f"✅ Foto guardada: {foto_destino}")
                        else:
                            foto_guardada = True
                            print(f"ℹ️ Foto ya existe: {foto_destino}")

                except Exception as e:
                    print(f"⚠️ Error guardando foto: {e}")

            # Usar el servicio de constancias para guardar los datos
            success, message, _ = self.constancia_service.guardar_alumno_desde_pdf(
                self.original_pdf,
                incluir_foto=True
            )

            if success:
                # 🆕 MENSAJE MEJORADO CON INFORMACIÓN DE FOTO
                mensaje_exito = "✅ Los datos han sido guardados correctamente en la base de datos."
                if foto_guardada:
                    mensaje_exito += f"\n📸 Foto del alumno guardada como {self.pdf_data.get('curp', 'N/A')}.jpg"

                QMessageBox.information(dialog, "Éxito", mensaje_exito)
                dialog.accept()  # Cerrar el diálogo
            else:
                QMessageBox.warning(dialog, "Error", f"❌ Error al guardar: {message}")

        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"❌ Error inesperado: {str(e)}")

    def _show_transformation_pending_dialog(self):
        """Muestra diálogo para transformación pendiente con comparación de datos"""
        if not self.pdf_data:
            QMessageBox.warning(self, "Error", "No hay datos del PDF para comparar.")
            return

        # Crear diálogo de comparación
        dialog = QDialog(self)
        dialog.setWindowTitle("🔄 Comparar Datos - Transformación Pendiente")
        dialog.setModal(True)
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        # Título
        title_label = QLabel("🔄 Comparación de Datos para Transformación")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Crear widget de comparación
        comparison_widget = self._create_comparison_widget()
        layout.addWidget(comparison_widget)

        # Botones de acción
        button_layout = QHBoxLayout()

        transform_btn = QPushButton("🔄 Transformar PDF")
        transform_btn.setStyleSheet("QPushButton { background-color: #3498DB; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px; }")
        transform_btn.clicked.connect(lambda: self._initiate_transformation(dialog))

        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.setStyleSheet("QPushButton { background-color: #95A5A6; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px; }")
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addWidget(transform_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        dialog.exec_()

    def _show_transformation_comparison_dialog(self):
        """Muestra diálogo con comparación entre PDF original y transformado"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📊 Comparación - Transformación Completada")
        dialog.setModal(True)
        dialog.resize(900, 700)

        layout = QVBoxLayout(dialog)

        # Título
        title_label = QLabel("📊 Comparación: PDF Original vs Transformado")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27AE60; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Widget de comparación detallada
        comparison_widget = self._create_detailed_comparison_widget()
        layout.addWidget(comparison_widget)

        # Botón de cerrar
        close_btn = QPushButton("✅ Cerrar")
        close_btn.setStyleSheet("QPushButton { background-color: #27AE60; color: white; font-weight: bold; padding: 8px 16px; border-radius: 5px; }")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec_()

    def _show_alumno_data_dialog(self):
        """Muestra datos completos del alumno desde la base de datos"""
        if not self.alumno_data:
            QMessageBox.information(self, "Sin datos", "No hay datos del alumno disponibles.")
            return

        # Crear diálogo con datos completos del alumno
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("Datos Completos del Alumno")
        dialog.setMinimumSize(600, 500)

        # Establecer estilo para el diálogo
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1E8449;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)

        # Crear contenido con datos completos del alumno
        content = self._format_alumno_data_for_display(self.alumno_data)

        text_edit = QTextEdit()
        text_edit.setHtml(content)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                padding: 10px;
            }
        """)

        layout.addWidget(text_edit)

        # 🆕 AGREGAR FOTO COMO WIDGET SEPARADO SI EXISTE
        if self.alumno_data and self.alumno_data.get('curp'):
            import os
            from PyQt5.QtWidgets import QLabel
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtCore import Qt

            foto_path = os.path.join("resources", "photos", f"{self.alumno_data.get('curp')}.jpg")

            if os.path.exists(foto_path):
                # Crear contenedor para la foto
                foto_container = QLabel()
                foto_container.setAlignment(Qt.AlignCenter)
                foto_container.setStyleSheet("""
                    QLabel {
                        background-color: #F8F9FA;
                        border: 2px solid #27AE60;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 10px;
                    }
                """)

                # Cargar y redimensionar la imagen
                pixmap = QPixmap(foto_path)
                if not pixmap.isNull():
                    # Redimensionar a 60x80 píxeles
                    scaled_pixmap = pixmap.scaled(60, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    foto_container.setPixmap(scaled_pixmap)
                    foto_container.setToolTip("Foto del alumno desde la base de datos")

                    # Agregar la foto al layout
                    layout.addWidget(foto_container)

        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, 0, Qt.AlignCenter)

        dialog.exec_()







    def _show_extracted_data_with_save_option(self):
        """Muestra datos extraídos usando el método que funciona + opción de guardar"""
        if not self.original_pdf:
            QMessageBox.information(self, "Sin datos", "No hay PDF cargado.")
            return

        try:
            # 🎯 USAR EL MISMO MÉTODO QUE FUNCIONA BIEN
            # Extraer datos del PDF original (igual que extract_and_show_data)
            extractor = PDFExtractor(self.original_pdf)
            self.tiene_calificaciones = extractor.tiene_calificaciones()

            try:
                # Extraer todos los datos (mismo código que funciona)
                self.pdf_data = extractor.extraer_todos_datos(
                    incluir_foto=True,
                    tipo_constancia_solicitado=None  # No eliminar calificaciones
                )
            except ValueError as ve:
                QMessageBox.warning(self, "Advertencia", str(ve))
                return

            # 🆕 MOSTRAR DIÁLOGO CON OPCIÓN DE GUARDAR
            self._show_data_dialog_with_save_option()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al extraer datos del PDF: {str(e)}")

    def _show_data_dialog_with_save_option(self):
        """Muestra el diálogo de datos con opción de guardar (reutiliza mostrar_info_contenido_pdf)"""
        if not self.pdf_data:
            return

        # Crear diálogo personalizado
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Datos Extraídos del PDF")
        dialog.setModal(True)
        dialog.resize(700, 800)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title_label = QLabel("📋 Datos Extraídos del PDF Original")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2C3E50; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 🎯 USAR EL MISMO FORMATO QUE FUNCIONA (mostrar_info_contenido_pdf)
        mensaje = self._get_formatted_pdf_info()

        # Área de scroll para mostrar los datos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #BDC3C7;
                border-radius: 8px;
                background-color: white;
            }
        """)

        # Widget para mostrar el contenido
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)

        # Mostrar datos usando QLabel (igual que mostrar_info_contenido_pdf)
        data_label = QLabel(mensaje)
        data_label.setWordWrap(True)
        data_label.setStyleSheet("font-size: 14px; line-height: 1.5;")
        content_layout.addWidget(data_label)

        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)

        # 🆕 SECCIÓN DE GUARDADO
        save_section = QFrame()
        save_section.setFrameStyle(QFrame.StyledPanel)
        save_section.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        save_layout = QVBoxLayout(save_section)
        save_layout.setSpacing(10)

        # Título de guardado
        save_title = QLabel("💾 Opciones de Guardado")
        save_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #495057; margin-bottom: 5px;")
        save_layout.addWidget(save_title)

        # Checkbox para guardar
        self.save_checkbox = QCheckBox("Guardar este alumno en la base de datos")
        self.save_checkbox.setStyleSheet("font-size: 14px; color: #495057;")
        save_layout.addWidget(self.save_checkbox)

        # Info adicional
        info_label = QLabel("ℹ️ Si el alumno ya existe en la BD, se actualizarán sus datos.")
        info_label.setStyleSheet("font-size: 12px; color: #6C757D; font-style: italic;")
        save_layout.addWidget(info_label)

        layout.addWidget(save_section)

        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Botón Guardar
        save_btn = QPushButton("💾 Guardar")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1E7E34; }
        """)
        save_btn.clicked.connect(lambda: self._handle_save_action(dialog))

        # Botón Cerrar
        close_btn = QPushButton("❌ Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #5A6268; }
            QPushButton:pressed { background-color: #545B62; }
        """)
        close_btn.clicked.connect(dialog.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        dialog.exec_()




    def _format_transformation_comparison(self, original_data, transformed_data):
        """Formatea la comparación entre datos originales y transformados"""
        html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6;">
            <h2 style="color: #E67E22; margin-top: 0; margin-bottom: 20px; text-align: center; font-size: 22px;">
                🔄 Comparación: Original vs Transformado
            </h2>

            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1; background-color: #FDF2E9; border-left: 4px solid #E67E22; padding: 15px; border-radius: 4px;">
                    <h3 style="color: #D35400; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                        📄 Datos Originales (PDF)
                    </h3>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Nombre:</span>
                        <span style="color: #34495E;">{original_data.get('nombre', 'No disponible')}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">CURP:</span>
                        <span style="color: #34495E;">{original_data.get('curp', 'No disponible')}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Tipo Original:</span>
                        <span style="color: #34495E;">{original_data.get('tipo_constancia', 'No disponible')}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Tenía Foto:</span>
                        <span style="color: #34495E;">{'Sí' if original_data.get('has_photo', False) else 'No'}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Calificaciones:</span>
                        <span style="color: #34495E;">{'Sí' if original_data.get('calificaciones') else 'No'}</span>
                    </p>
                </div>

                <div style="flex: 1; background-color: #E8F8F5; border-left: 4px solid #27AE60; padding: 15px; border-radius: 4px;">
                    <h3 style="color: #1E8449; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                        ✨ Datos Transformados
                    </h3>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Nombre:</span>
                        <span style="color: #34495E;">{transformed_data.get('nombre', 'No disponible')}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">CURP:</span>
                        <span style="color: #34495E;">{transformed_data.get('curp', 'No disponible')}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Tipo Nuevo:</span>
                        <span style="color: #34495E; font-weight: bold;">{transformed_data.get('tipo_constancia', 'No disponible')}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Incluye Foto:</span>
                        <span style="color: #34495E; font-weight: bold;">{'Sí' if transformed_data.get('incluir_foto', False) else 'No'}</span>
                    </p>
                    <p style="margin: 8px 0;">
                        <span style="font-weight: bold; color: #2C3E50;">Guardado en BD:</span>
                        <span style="color: #34495E; font-weight: bold;">{'Sí' if transformed_data.get('guardar_alumno', False) else 'No'}</span>
                    </p>
                </div>
            </div>

            <div style="background-color: #FEF9E7; border-left: 4px solid #F39C12; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <h3 style="color: #D68910; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    ℹ️ Información de Transformación
                </h3>
                <p style="margin: 8px 0; color: #7D6608;">
                    <strong>Proceso:</strong> PDF original → Extracción de datos → Nueva constancia
                </p>
                <p style="margin: 8px 0; color: #7D6608;">
                    <strong>Estado:</strong> Vista previa temporal (confirma para guardar)
                </p>
                <p style="margin: 8px 0; color: #7D6608;">
                    <strong>Opciones:</strong> Guardar definitivamente, abrir en navegador, o cancelar
                </p>
            </div>
        </div>
        """
        return html

    def _format_alumno_data_for_display(self, alumno_data):
        """Formatea los datos del alumno para mostrar en el diálogo"""

        # 🔍 VERIFICAR SI TIENE FOTO
        foto_info = self._check_alumno_photo(alumno_data.get('curp'))

        # 🔍 VERIFICAR SI TIENE CALIFICACIONES
        tiene_calificaciones = bool(alumno_data.get('calificaciones'))

        html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; line-height: 1.6;">
            <h2 style="color: #27AE60; margin-top: 0; margin-bottom: 20px; text-align: center; font-size: 22px;">
                📋 Información Completa del Alumno
            </h2>

            <div style="background-color: #E8F8F5; border-left: 4px solid #27AE60; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <h3 style="color: #1E8449; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    👤 Datos Personales
                </h3>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Nombre:</span>
                    <span style="color: #34495E;">{alumno_data.get('nombre', 'No registrado')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">CURP:</span>
                    <span style="color: #34495E;">{alumno_data.get('curp', 'No registrado')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Matrícula:</span>
                    <span style="color: #34495E;">{alumno_data.get('matricula', 'No registrada')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Fecha de Nacimiento:</span>
                    <span style="color: #34495E;">{alumno_data.get('fecha_nacimiento', 'No registrada')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Foto:</span>
                    <span style="color: {foto_info['color']};">{foto_info['texto']}</span>
                </p>
            </div>

            <div style="background-color: #EBF5FB; border-left: 4px solid #3498DB; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <h3 style="color: #2874A6; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    🏫 Datos Escolares
                </h3>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Grado:</span>
                    <span style="color: #34495E;">{self._format_field_value(alumno_data.get('grado'), 'grado')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Grupo:</span>
                    <span style="color: #34495E;">{self._format_field_value(alumno_data.get('grupo'), 'grupo')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Turno:</span>
                    <span style="color: #34495E;">{self._format_field_value(alumno_data.get('turno'), 'turno')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Ciclo Escolar:</span>
                    <span style="color: #34495E;">{alumno_data.get('ciclo_escolar', '2024-2025')}</span>
                </p>
                <p style="margin: 8px 0;">
                    <span style="font-weight: bold; color: #2C3E50; min-width: 120px; display: inline-block;">Escuela:</span>
                    <span style="color: #34495E;">PROF. MAXIMO GAMIZ FERNANDEZ</span>
                </p>
            </div>

            <div style="background-color: {('#E8F8F5' if tiene_calificaciones else '#FDEDEC')}; border-left: 4px solid {('#1ABC9C' if tiene_calificaciones else '#E74C3C')}; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <h3 style="color: {('#16A085' if tiene_calificaciones else '#C0392B')}; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    📊 Calificaciones <span style="color: {('#27AE60' if tiene_calificaciones else '#E74C3C')};">{'✓' if tiene_calificaciones else '✗'}</span>
                </h3>
                <p style="margin: 8px 0; color: {('#16A085' if tiene_calificaciones else '#C0392B')};">
                    {('Se pueden generar constancias de calificaciones y traslado.' if tiene_calificaciones else 'Solo se pueden generar constancias de estudios.')}
                </p>
            </div>"""

        # Agregar calificaciones si están disponibles
        if 'calificaciones' in alumno_data and alumno_data['calificaciones']:
            html += f"""
            <div style="background-color: #FDF2E9; border-left: 4px solid #E67E22; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <h3 style="color: #D35400; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    📊 Calificaciones
                </h3>
                <div style="margin-top: 15px; margin-bottom: 15px;">
                    <h4 style="color: #D35400; margin-top: 0; margin-bottom: 10px; font-size: 15px; text-align: center;">
                        Tabla de Calificaciones
                    </h4>
                    <div style="box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px; background-color: white;">
                            <thead>
                                <tr style="background-color: #E67E22; color: white;">
                                    <th style="padding: 12px 15px; text-align: left; border: 1px solid #F5B041; font-weight: bold;">Materia</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041; font-weight: bold;">Periodo 1</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041; font-weight: bold;">Periodo 2</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041; font-weight: bold;">Periodo 3</th>
                                    <th style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041; font-weight: bold; background-color: #D35400;">Promedio</th>
                                </tr>
                            </thead>
                            <tbody>
            """

            for i, cal in enumerate(alumno_data['calificaciones']):
                bg_color = "#FEF9E7" if i % 2 == 0 else "#FDF2E9"
                promedio_color = "#27AE60" if cal.get('promedio', 0) >= 8 else "#F39C12" if cal.get('promedio', 0) >= 6 else "#E74C3C"

                html += f"""
                                <tr style="background-color: {bg_color};">
                                    <td style="padding: 12px 15px; border: 1px solid #F5B041; font-weight: bold;">{cal.get('nombre', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041;">{cal.get('i', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041;">{cal.get('ii', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; border: 1px solid #F5B041;">{cal.get('iii', '')}</td>
                                    <td style="padding: 12px 15px; text-align: center; font-weight: bold; border: 1px solid #F5B041; color: {promedio_color};">{cal.get('promedio', '')}</td>
                                </tr>
                """

            html += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            """

        html += f"""
            <div style="background-color: #FEF9E7; border-left: 4px solid #F39C12; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                <h3 style="color: #D68910; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    ℹ️ Información Adicional
                </h3>
                <p style="margin: 8px 0; color: #7D6608;">
                    <strong>Fuente de datos:</strong> Base de datos del sistema escolar
                </p>
                <p style="margin: 8px 0; color: #7D6608;">
                    <strong>Contexto:</strong> Datos utilizados para generar la constancia
                </p>
                <p style="margin: 8px 0; color: #7D6608;">
                    <strong>Última actualización:</strong> Información actual del sistema
                </p>
            </div>
        </div>
        """
        return html

    def _check_alumno_photo(self, curp):
        """Verifica si el alumno tiene foto guardada"""
        if not curp:
            return {"texto": "❌ No disponible (sin CURP)", "color": "#95A5A6"}

        import os
        foto_path = os.path.join("resources", "photos", f"{curp}.jpg")

        if os.path.exists(foto_path):
            return {"texto": "✅ Disponible (30x40px)", "color": "#27AE60"}
        else:
            return {"texto": "❌ No registrada", "color": "#E74C3C"}

    def _format_field_value(self, value, field_type):
        """Formatea valores de campos con mensajes apropiados"""
        if value is None or value == "" or str(value).strip() == "":
            if field_type == "grado":
                return "No registrado"
            elif field_type == "grupo":
                return "No registrado"
            elif field_type == "turno":
                return "No registrado"
            else:
                return "No registrado"

        # Si tiene valor, formatearlo apropiadamente
        if field_type == "grado":
            return f"{value}°"
        elif field_type == "turno":
            return value.upper() if isinstance(value, str) else str(value)
        else:
            return str(value)

    def set_constancia_context(self, alumno_data):
        """Establece el contexto para vista previa de constancia generada"""
        # Establecer contexto
        self.data_context = "constancia_generada"
        self.alumno_data = alumno_data

        # Actualizar botón
        self.ver_datos_btn.setText("📋 Ver Datos del Alumno")
        self.ver_datos_btn.setToolTip("Ver información completa del alumno desde la base de datos")

    def set_pdf_context(self):
        """Establece el contexto para PDF cargado normal (método legacy)"""
        self.set_pdf_external_context()

    def set_pdf_external_context(self):
        """Establece el contexto para PDF externo cargado"""
        self.data_context = "pdf_externo"
        self.alumno_data = None
        self.transformation_data = None
        self._update_button_for_context()

    def set_transformation_pending_context(self, alumno_bd_data=None):
        """Establece el contexto cuando hay transformación pendiente"""
        self.data_context = "transformacion_pendiente"
        self.alumno_data = alumno_bd_data
        self._update_button_for_context()

    def set_transformation_completed_context(self, original_data, transformed_data, alumno_data=None):
        """Establece el contexto cuando la transformación está completada"""
        self.data_context = "transformacion_completada"
        self.original_data = original_data
        self.transformed_data = transformed_data
        self.alumno_data = alumno_data
        self._update_button_for_context()

    def _update_button_for_context(self):
        """Actualiza el botón según el contexto actual"""
        if self.data_context == "pdf_externo":
            self.ver_datos_btn.setText("📄 Ver Datos del PDF")
            self.ver_datos_btn.setToolTip("Mostrar datos extraídos del PDF cargado")
        elif self.data_context == "constancia_generada":
            self.ver_datos_btn.setText("👤 Ver Datos del Alumno")
            self.ver_datos_btn.setToolTip("Mostrar datos completos del alumno desde la base de datos")
        elif self.data_context == "transformacion_pendiente":
            self.ver_datos_btn.setText("🔄 Comparar Datos")
            self.ver_datos_btn.setToolTip("Comparar datos del PDF con datos de la base de datos")
        elif self.data_context == "transformacion_completada":
            self.ver_datos_btn.setText("📋 Ver Datos + Guardar")
            self.ver_datos_btn.setToolTip("Ver datos extraídos del PDF y opcionalmente guardar en BD")
        else:
            # Fallback para contextos legacy
            self.ver_datos_btn.setText("📋 Ver Datos Extraídos")
            self.ver_datos_btn.setToolTip("Extraer y mostrar los datos del PDF")

    def set_transformation_context(self, original_data, transformed_data):
        """Establece el contexto para PDF transformado"""
        # Establecer contexto
        self.data_context = "pdf_transformado"
        self.original_data = original_data
        self.transformed_data = transformed_data

        # Actualizar botón
        self.ver_datos_btn.setText("📋 Ver Datos")
        self.ver_datos_btn.setToolTip("Ver datos extraídos del PDF original")

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
