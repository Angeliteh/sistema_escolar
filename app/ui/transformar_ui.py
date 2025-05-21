"""
Interfaz para transformar constancias
"""
import os
import tempfile
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFileDialog, QGroupBox,
    QRadioButton, QButtonGroup, QCheckBox, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.ui.pdf_viewer import PDFViewer
from app.core.pdf_extractor import PDFExtractor
from app.core.pdf_generator import PDFGenerator
from app.core.service_provider import ServiceProvider
from app.core.utils import open_file_with_default_app

class TransformarWindow(QMainWindow):
    """Ventana para transformar constancias"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transformar Constancia")
        self.setMinimumSize(1200, 800)  # Aumentamos el tamaño mínimo de la ventana

        self.pdf_path = None
        self.pdf_data = None

        # Usar el proveedor de servicios
        service_provider = ServiceProvider.get_instance()
        self.constancia_service = service_provider.constancia_service

        self.pdf_generator = PDFGenerator()
        self.temp_preview_dir = None  # Para almacenar la ruta del directorio temporal de vista previa
        self.tiene_calificaciones = False  # Por defecto, asumimos que no tiene calificaciones

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Barra superior con botón de volver y título
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # Botón para volver al menú principal
        self.btn_volver = QPushButton("← Volver")
        self.btn_volver.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: bold;
                text-align: center;
                max-width: 100px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        self.btn_volver.setCursor(Qt.PointingHandCursor)
        self.btn_volver.clicked.connect(self.volver_menu_principal)

        # Título
        title_label = QLabel("Transformar Constancia")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        top_bar_layout.addWidget(self.btn_volver)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.setStretch(0, 1)  # El botón ocupa menos espacio
        top_bar_layout.setStretch(1, 3)  # El título ocupa más espacio

        main_layout.addWidget(top_bar)

        # Contenedor principal
        content_layout = QHBoxLayout()

        # Panel izquierdo: Opciones
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)  # Reducimos el espacio entre elementos
        left_layout.setContentsMargins(5, 5, 5, 5)  # Reducimos los márgenes

        # Botón para seleccionar archivo
        self.setup_file_selector(left_layout)

        # Opciones de tipo de constancia
        self.setup_certificate_options(left_layout)

        # Opciones adicionales
        self.setup_additional_options(left_layout)

        # Botones de acción
        self.setup_action_buttons(left_layout)

        # No añadimos espacio flexible al final para aprovechar todo el espacio

        # Panel derecho: Vista previa
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        preview_label = QLabel("Vista Previa")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_font = QFont()
        preview_font.setPointSize(16)
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        preview_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        right_layout.addWidget(preview_label)

        # Visor de PDF
        self.pdf_viewer = PDFViewer()
        right_layout.addWidget(self.pdf_viewer)

        # Añadir paneles al layout principal
        content_layout.addWidget(left_panel, 2)  # Aumentamos el espacio para el panel izquierdo
        content_layout.addWidget(right_panel, 3)

        main_layout.addLayout(content_layout)

    def setup_file_selector(self, parent_layout):
        """Configura el selector de archivos"""
        file_group = QGroupBox("Paso 1: Seleccionar Constancia")
        file_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(10)
        file_layout.setContentsMargins(10, 10, 10, 10)

        # Botón grande para seleccionar archivo
        self.btn_browse = QPushButton("Seleccionar PDF")
        self.btn_browse.setMinimumHeight(50)
        self.btn_browse.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_browse.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_browse.clicked.connect(self.browse_file)

        # Etiqueta para mostrar el archivo seleccionado
        self.lbl_file = QLabel("Ningún archivo seleccionado")
        self.lbl_file.setAlignment(Qt.AlignCenter)
        self.lbl_file.setStyleSheet("""
            QLabel {
                padding: 5px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #ddd;
                font-size: 12px;
            }
        """)
        self.lbl_file.setWordWrap(True)

        file_layout.addWidget(self.btn_browse)
        file_layout.addWidget(self.lbl_file)

        parent_layout.addWidget(file_group)

    def setup_certificate_options(self, parent_layout):
        """Configura las opciones de tipo de constancia"""
        options_group = QGroupBox("Paso 2: Elegir Tipo de Constancia")
        options_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #2ecc71;
            }
        """)

        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)
        options_layout.setContentsMargins(10, 10, 10, 10)

        # Botones de radio para tipos de constancia
        self.radio_estudio = QRadioButton("Constancia de Estudios")
        self.radio_calificaciones = QRadioButton("Constancia con Calificaciones")
        self.radio_traslado = QRadioButton("Constancia de Traslado")

        # Estilo para los botones de radio
        radio_style = """
            QRadioButton {
                font-size: 13px;
                padding: 8px;
                border-radius: 5px;
                background-color: #f8f9fa;
                margin: 3px;
            }
            QRadioButton:checked {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
            }
            QRadioButton:hover {
                background-color: #27ae60;
                color: white;
            }
        """

        self.radio_estudio.setStyleSheet(radio_style)
        self.radio_calificaciones.setStyleSheet(radio_style)
        self.radio_traslado.setStyleSheet(radio_style)

        # Seleccionar el primero por defecto
        self.radio_estudio.setChecked(True)

        # Agrupar los botones
        self.tipo_group = QButtonGroup()
        self.tipo_group.addButton(self.radio_estudio, 1)
        self.tipo_group.addButton(self.radio_calificaciones, 2)
        self.tipo_group.addButton(self.radio_traslado, 3)
        self.tipo_group.buttonClicked.connect(self.update_preview)

        options_layout.addWidget(self.radio_estudio)
        options_layout.addWidget(self.radio_calificaciones)
        options_layout.addWidget(self.radio_traslado)

        parent_layout.addWidget(options_group)

    def setup_additional_options(self, parent_layout):
        """Configura opciones adicionales"""
        options_group = QGroupBox("Paso 3: Opciones Adicionales")
        options_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #e74c3c;
            }
        """)

        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)
        options_layout.setContentsMargins(10, 10, 10, 10)

        # Opciones adicionales
        self.check_foto = QCheckBox("Incluir foto si está disponible")
        self.check_guardar = QCheckBox("Guardar alumno en la base de datos")

        # Estilo para los checkboxes
        checkbox_style = """
            QCheckBox {
                font-size: 13px;
                padding: 8px;
                border-radius: 5px;
                background-color: #f8f9fa;
                margin: 3px;
            }
            QCheckBox:checked {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
            }
            QCheckBox:hover {
                background-color: #c0392b;
                color: white;
            }
        """

        self.check_foto.setStyleSheet(checkbox_style)
        self.check_guardar.setStyleSheet(checkbox_style)

        # Seleccionar por defecto
        self.check_foto.setChecked(True)
        self.check_guardar.setChecked(True)

        # Conectar señales
        self.check_foto.stateChanged.connect(self.update_preview)

        options_layout.addWidget(self.check_foto)
        options_layout.addWidget(self.check_guardar)

        parent_layout.addWidget(options_group)

    def setup_action_buttons(self, parent_layout):
        """Configura los botones de acción"""
        action_group = QGroupBox("Paso 4: Generar Constancia")
        action_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #9b59b6;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #9b59b6;
            }
        """)

        action_layout = QVBoxLayout(action_group)
        action_layout.setContentsMargins(10, 10, 10, 10)

        # Layout para los botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        # Botón para guardar datos sin generar constancia
        self.btn_guardar_datos = QPushButton("GUARDAR DATOS EN BD")
        self.btn_guardar_datos.setMinimumHeight(60)
        self.btn_guardar_datos.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_guardar_datos.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #a9cce3;
            }
        """)
        self.btn_guardar_datos.clicked.connect(self.guardar_datos_alumno)
        self.btn_guardar_datos.setEnabled(False)

        # Botón grande para transformar
        self.btn_transformar = QPushButton("TRANSFORMAR CONSTANCIA")
        self.btn_transformar.setMinimumHeight(60)
        self.btn_transformar.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_transformar.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #d7bde2;
            }
        """)
        self.btn_transformar.clicked.connect(self.transform_constancia)
        self.btn_transformar.setEnabled(False)

        buttons_layout.addWidget(self.btn_guardar_datos)
        buttons_layout.addWidget(self.btn_transformar)

        action_layout.addLayout(buttons_layout)

        parent_layout.addWidget(action_group)

    def browse_file(self):
        """Abre un diálogo para seleccionar un archivo PDF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Constancia PDF", "", "Archivos PDF (*.pdf)"
        )

        if file_path:
            self.pdf_path = file_path
            self.lbl_file.setText(os.path.basename(file_path))
            self.extract_data()

    def extract_data(self):
        """Extrae los datos del PDF"""
        if not self.pdf_path:
            return

        try:
            # Extraer datos del PDF
            extractor = PDFExtractor(self.pdf_path)

            # Verificar si la constancia tiene calificaciones
            tiene_calificaciones = extractor.tiene_calificaciones()

            # Guardar esta información para usarla más tarde
            self.tiene_calificaciones = tiene_calificaciones

            # Actualizar la interfaz según si tiene calificaciones o no
            self.actualizar_opciones_segun_calificaciones(tiene_calificaciones)

            # Usar el tipo de constancia seleccionado actualmente
            tipo_constancia = self.get_selected_type()
            incluir_foto = self.check_foto.isChecked()

            # Extraer todos los datos
            self.pdf_data = extractor.extraer_todos_datos(
                incluir_foto=incluir_foto,
                tipo_constancia_solicitado=tipo_constancia
            )

            # Habilitar botones
            self.btn_transformar.setEnabled(True)
            self.btn_guardar_datos.setEnabled(True)

            # Actualizar vista previa
            self.update_preview()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al extraer datos del PDF: {str(e)}")
            self.btn_transformar.setEnabled(False)
            self.btn_guardar_datos.setEnabled(False)

    def get_selected_type(self):
        """Obtiene el tipo de constancia seleccionado"""
        if self.radio_estudio.isChecked():
            return "estudio"
        elif self.radio_calificaciones.isChecked():
            return "calificaciones"
        elif self.radio_traslado.isChecked():
            return "traslado"
        return "estudio"  # Por defecto

    def actualizar_opciones_segun_calificaciones(self, tiene_calificaciones):
        """
        Actualiza las opciones de la interfaz según si la constancia tiene calificaciones o no

        Args:
            tiene_calificaciones: True si la constancia tiene calificaciones, False en caso contrario
        """
        # Nota: No necesitamos verificar el tipo actual, ya que la interfaz se actualiza automáticamente

        # Si no tiene calificaciones, deshabilitar la opción de constancia con calificaciones
        if not tiene_calificaciones:
            # Deshabilitar la opción de constancia con calificaciones
            self.radio_calificaciones.setEnabled(False)
            self.radio_calificaciones.setToolTip("La constancia original no contiene calificaciones")

            # Si estaba seleccionada la opción de calificaciones, cambiar a estudio
            if self.radio_calificaciones.isChecked():
                self.radio_estudio.setChecked(True)

            # Mostrar un mensaje informativo
            QMessageBox.information(
                self,
                "Constancia sin calificaciones",
                "La constancia cargada no contiene calificaciones.\n\n"
                "No se podrá generar una constancia con calificaciones a partir de ella."
            )
        else:
            # Si tiene calificaciones, habilitar todas las opciones
            self.radio_calificaciones.setEnabled(True)
            self.radio_calificaciones.setToolTip("")

        # Siempre habilitar las opciones de estudio y traslado
        self.radio_estudio.setEnabled(True)
        self.radio_traslado.setEnabled(True)

    def update_preview(self):
        """Actualiza la vista previa de la constancia"""
        if not self.pdf_data:
            return

        self.generate_preview()

    def generate_preview(self):
        """Genera una vista previa de la constancia"""
        if not self.pdf_path or not self.pdf_data:
            return

        tipo_constancia = self.get_selected_type()
        incluir_foto = self.check_foto.isChecked()

        try:
            # Crear un directorio temporal específico para esta vista previa
            temp_dir = tempfile.mkdtemp(prefix="constancia_preview_")

            # Generar constancia en un archivo temporal
            temp_output = os.path.join(temp_dir, f"preview_{tipo_constancia}.pdf")

            # Crear una copia de los datos para no modificar los originales
            preview_data = self.pdf_data.copy()

            # Actualizar datos según opciones seleccionadas
            preview_data['mostrar_calificaciones'] = tipo_constancia in ["traslado", "calificaciones"]

            # Manejar correctamente la opción de foto
            if incluir_foto:
                # Si se quiere incluir foto y hay una disponible
                if 'has_photo' in preview_data and preview_data['has_photo']:
                    preview_data['has_photo'] = True
                    preview_data['show_placeholder'] = True
                else:
                    # Si no hay foto pero se solicitó incluirla, mostrar un espacio para foto
                    preview_data['has_photo'] = False
                    preview_data['show_placeholder'] = True
            else:
                # Si el usuario no quiere incluir foto, asegurarse de que no se muestre
                preview_data['has_photo'] = False
                preview_data['show_placeholder'] = False

            # Generar PDF de vista previa en el directorio temporal
            output_path = self.pdf_generator.generar_constancia(
                tipo_constancia, preview_data,
                output_dir=temp_dir,
                output_path=temp_output,
                filename_prefix="preview_"
            )

            if output_path and os.path.exists(output_path):
                # Cargar PDF en el visor
                self.pdf_viewer.load_pdf(output_path)

                # Guardar la ruta del directorio temporal para limpiarlo después
                self.temp_preview_dir = temp_dir
                return True

            # Limpiar el directorio temporal si algo falló
            self._clean_temp_dir(temp_dir)
            return False

        except Exception as e:
            print(f"Error al generar vista previa: {e}")
            return False

    def _clean_temp_dir(self, temp_dir):
        """Limpia un directorio temporal y todos sus contenidos"""
        try:
            if os.path.exists(temp_dir):
                # Eliminar todos los archivos en el directorio
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(f"Error al eliminar archivo temporal {file_path}: {e}")

                # Eliminar el directorio
                os.rmdir(temp_dir)
        except Exception as e:
            print(f"Error al limpiar directorio temporal {temp_dir}: {e}")

    def transform_constancia(self):
        """Transforma la constancia"""
        if not self.pdf_path or not self.pdf_data:
            QMessageBox.warning(self, "Error", "Por favor, seleccione un archivo PDF válido.")
            return

        tipo_constancia = self.get_selected_type()
        incluir_foto = self.check_foto.isChecked()
        guardar_alumno = self.check_guardar.isChecked()

        # Verificar si se está intentando generar una constancia con calificaciones sin tenerlas
        if tipo_constancia == "calificaciones" and not self.tiene_calificaciones:
            QMessageBox.warning(
                self,
                "Error",
                "No se puede generar una constancia con calificaciones porque la constancia original no las contiene.\n\n"
                "Por favor, seleccione otro tipo de constancia o cargue un PDF que contenga calificaciones."
            )
            return

        try:
            # Crear una copia de los datos para no modificar los originales
            transform_data = self.pdf_data.copy()

            # Actualizar datos según opciones seleccionadas
            transform_data['mostrar_calificaciones'] = tipo_constancia in ["traslado", "calificaciones"]

            # Verificar si se necesitan calificaciones pero no están disponibles
            if transform_data['mostrar_calificaciones'] and not self.tiene_calificaciones:
                # Para constancias de traslado, podemos usar calificaciones de ejemplo
                if tipo_constancia == "traslado":
                    # Mostrar advertencia
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        "La constancia original no contiene calificaciones, pero se generará una constancia de traslado "
                        "con calificaciones de ejemplo.\n\n"
                        "Esto es solo para fines de demostración y no refleja las calificaciones reales del alumno."
                    )
                else:
                    # Para otros tipos que requieren calificaciones, mostrar error
                    QMessageBox.critical(
                        self,
                        "Error",
                        "No se puede generar una constancia que requiere calificaciones porque la constancia original no las contiene."
                    )
                    return

            # Manejar correctamente la opción de foto
            if incluir_foto:
                # Si se quiere incluir foto y hay una disponible
                if 'has_photo' in transform_data and transform_data['has_photo']:
                    transform_data['has_photo'] = True
                    transform_data['show_placeholder'] = True
                else:
                    # Si no hay foto pero se solicitó incluirla, mostrar un espacio para foto
                    transform_data['has_photo'] = False
                    transform_data['show_placeholder'] = True
            else:
                # Si el usuario no quiere incluir foto, asegurarse de que no se muestre
                transform_data['has_photo'] = False
                transform_data['show_placeholder'] = False

            # Generar la constancia
            success, message, data = self.constancia_service.generar_constancia_desde_pdf(
                self.pdf_path, tipo_constancia, incluir_foto, guardar_alumno=guardar_alumno
            )

            if success:
                # Primero, cargar el PDF generado en el visor
                if data and "ruta_archivo" in data:
                    self.pdf_viewer.load_pdf(data["ruta_archivo"])

                # Preguntar si desea ver los detalles del alumno
                if guardar_alumno and data and "alumno" in data and data["alumno"]["id"]:
                    reply = QMessageBox.question(
                        self, "¡Constancia Transformada!",
                        f"{message}\n\n¿Desea ver los detalles del alumno?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                    )

                    if reply == QMessageBox.Yes:
                        # Mostrar detalles del alumno
                        from app.ui.buscar_ui import DetallesAlumnoDialog
                        dialog = DetallesAlumnoDialog(self, alumno_id=data["alumno"]["id"])
                        dialog.setWindowTitle("Datos del Alumno - Constancia Transformada")
                        dialog.exec_()

                # Preguntar si desea abrir la constancia
                if data and "ruta_archivo" in data:
                    reply = QMessageBox.question(
                        self, "¡Constancia Transformada!",
                        f"¿Desea abrir la constancia generada?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                    )

                    if reply == QMessageBox.Yes:
                        open_file_with_default_app(data["ruta_archivo"])
            else:
                QMessageBox.warning(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al transformar constancia: {str(e)}")

    def guardar_datos_alumno(self):
        """Muestra los datos extraídos del PDF para confirmar antes de guardarlos"""
        if not self.pdf_path or not self.pdf_data:
            QMessageBox.warning(self, "Error", "Por favor, seleccione un archivo PDF válido.")
            return

        incluir_foto = self.check_foto.isChecked()

        try:
            # Crear una copia de los datos para no modificar los originales
            datos_alumno = self.pdf_data.copy()

            # Crear un diálogo personalizado para mostrar y confirmar los datos
            from app.ui.confirmar_datos_dialog import ConfirmarDatosDialog
            dialog = ConfirmarDatosDialog(self, datos_alumno, self.pdf_path, incluir_foto)
            dialog.setWindowTitle("Confirmar Datos del Alumno")

            # Ejecutar el diálogo y procesar el resultado
            if dialog.exec_() == QDialog.Accepted:
                # El usuario confirmó los datos, mostrar mensaje de éxito
                QMessageBox.information(
                    self, "Datos Guardados",
                    "Los datos del alumno han sido guardados correctamente en la base de datos."
                )

                # Actualizar la interfaz si es necesario
                self.check_guardar.setChecked(False)  # Ya no es necesario guardar el alumno al transformar

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar datos del alumno: {str(e)}")

    def volver_menu_principal(self):
        """Cierra esta ventana y vuelve al menú principal"""
        self.close()

    def closeEvent(self, event):
        """Evento que se ejecuta al cerrar la ventana"""
        # Limpiar archivos temporales
        if hasattr(self, 'temp_preview_dir') and self.temp_preview_dir:
            self._clean_temp_dir(self.temp_preview_dir)

        # Cerrar servicios
        if hasattr(self, 'constancia_service'):
            self.constancia_service.close()

        # Continuar con el evento de cierre
        super().closeEvent(event)

def main():
    """Función principal"""
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = TransformarWindow()
    window.show()
    sys.exit(app.exec_())
