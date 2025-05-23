"""
Interfaz para buscar alumnos y generar constancias
"""
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDialog, QComboBox, QCheckBox, QLineEdit, QGroupBox, QScrollArea, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor

from app.core.service_provider import ServiceProvider
from app.core.utils import open_file_with_default_app, format_curp
from app.ui.pdf_viewer import PDFViewer


class DetallesAlumnoDialog(QDialog):
    """Diálogo para mostrar los detalles completos de un alumno"""

    def __init__(self, parent=None, alumno_id=None):
        super().__init__(parent)
        self.setWindowTitle("Detalles del Alumno")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.alumno_id = alumno_id

        # Usar el proveedor de servicios
        service_provider = ServiceProvider.get_instance()
        self.alumno_service = service_provider.alumno_service

        self.setup_ui()
        self.cargar_datos_alumno()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        self.title_label = QLabel("Detalles del Alumno")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        main_layout.addWidget(self.title_label)

        # Área de desplazamiento para los detalles
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        # Sección de datos personales
        datos_personales = QGroupBox("Datos Personales")
        datos_personales.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        datos_personales_layout = QVBoxLayout(datos_personales)
        datos_personales_layout.setSpacing(10)

        # Campos para datos personales
        self.lbl_nombre = self.crear_campo_detalle("Nombre completo:")
        self.lbl_curp = self.crear_campo_detalle("CURP:")
        self.lbl_matricula = self.crear_campo_detalle("Matrícula:")
        self.lbl_fecha_nacimiento = self.crear_campo_detalle("Fecha de nacimiento:")

        datos_personales_layout.addWidget(self.lbl_nombre)
        datos_personales_layout.addWidget(self.lbl_curp)
        datos_personales_layout.addWidget(self.lbl_matricula)
        datos_personales_layout.addWidget(self.lbl_fecha_nacimiento)

        # Sección de datos escolares
        datos_escolares = QGroupBox("Datos Escolares")
        datos_escolares.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #2ecc71;
            }
        """)

        datos_escolares_layout = QVBoxLayout(datos_escolares)
        datos_escolares_layout.setSpacing(10)

        # Campos para datos escolares
        self.lbl_grado = self.crear_campo_detalle("Grado:")
        self.lbl_grupo = self.crear_campo_detalle("Grupo:")
        self.lbl_turno = self.crear_campo_detalle("Turno:")
        self.lbl_ciclo = self.crear_campo_detalle("Ciclo escolar:")
        self.lbl_escuela = self.crear_campo_detalle("Escuela:")
        self.lbl_cct = self.crear_campo_detalle("CCT:")

        datos_escolares_layout.addWidget(self.lbl_grado)
        datos_escolares_layout.addWidget(self.lbl_grupo)
        datos_escolares_layout.addWidget(self.lbl_turno)
        datos_escolares_layout.addWidget(self.lbl_ciclo)
        datos_escolares_layout.addWidget(self.lbl_escuela)
        datos_escolares_layout.addWidget(self.lbl_cct)



        # Sección de calificaciones
        self.calificaciones_group = QGroupBox("Calificaciones")
        self.calificaciones_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #e74c3c;
            }
        """)

        calificaciones_layout = QVBoxLayout(self.calificaciones_group)

        # Etiqueta para mostrar si hay calificaciones
        self.lbl_estado_calificaciones = QLabel()
        self.lbl_estado_calificaciones.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        calificaciones_layout.addWidget(self.lbl_estado_calificaciones)

        # Tabla para mostrar las calificaciones
        self.tabla_calificaciones = QTableWidget()
        self.tabla_calificaciones.setColumnCount(5)
        self.tabla_calificaciones.setHorizontalHeaderLabels(["Materia", "P1", "P2", "P3", "Promedio"])

        # Configurar la tabla
        self.tabla_calificaciones.setAlternatingRowColors(True)
        self.tabla_calificaciones.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_calificaciones.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Materia (se estira)
        self.tabla_calificaciones.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # P1
        self.tabla_calificaciones.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # P2
        self.tabla_calificaciones.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # P3
        self.tabla_calificaciones.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Promedio

        # Desactivar la barra de desplazamiento vertical para mostrar todas las filas
        self.tabla_calificaciones.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Ajustar el tamaño de la tabla para mostrar todas las filas
        self.tabla_calificaciones.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Estilo de la tabla
        self.tabla_calificaciones.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e74c3c;
                border-radius: 8px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #f9e4e4;
                selection-color: #c0392b;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: #f9e4e4;
                color: #c0392b;
            }
            QHeaderView::section {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 6px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 6px;
            }
        """)

        calificaciones_layout.addWidget(self.tabla_calificaciones)

        # Añadir secciones al layout del scroll
        scroll_layout.addWidget(datos_personales)
        scroll_layout.addWidget(datos_escolares)
        scroll_layout.addWidget(self.calificaciones_group)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        # Botón de cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_cerrar.setMinimumHeight(40)
        btn_cerrar.clicked.connect(self.accept)

        # Centrar el botón
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cerrar)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def crear_campo_detalle(self, etiqueta):
        """Crea un campo de detalle con formato que es de solo lectura"""
        # Crear un widget contenedor para la etiqueta y el campo de solo lectura
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Etiqueta del campo
        label = QLabel(etiqueta)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
                max-width: 150px;
            }
        """)

        # Campo de solo lectura
        edit = QLineEdit()
        edit.setReadOnly(True)  # Hacer el campo de solo lectura
        edit.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;  /* Fondo más claro para indicar que es de solo lectura */
            }
        """)

        layout.addWidget(label)
        layout.addWidget(edit, 1)  # El campo ocupa el espacio restante

        # Guardar referencia al campo
        container.campo_editable = edit
        container.etiqueta = etiqueta

        return container

    def cargar_datos_alumno(self):
        """Carga los datos del alumno"""
        if not self.alumno_id:
            self.title_label.setText("Error: No se especificó un alumno")
            return

        try:
            # Obtener datos del alumno
            self.alumno_data = self.alumno_service.get_alumno_by_id(self.alumno_id)
            if not self.alumno_data:
                self.title_label.setText("Error: Alumno no encontrado")
                return

            # Actualizar título
            self.title_label.setText(f"Detalles de {self.alumno_data.get('nombre', 'Alumno')}")

            # Actualizar datos personales
            self.lbl_nombre.campo_editable.setText(self.alumno_data.get('nombre', ''))

            curp = self.alumno_data.get('curp', '')
            curp_formateado = format_curp(curp) if curp else ''
            self.lbl_curp.campo_editable.setText(curp_formateado)

            self.lbl_matricula.campo_editable.setText(self.alumno_data.get('matricula', ''))
            self.lbl_fecha_nacimiento.campo_editable.setText(self.alumno_data.get('fecha_nacimiento', ''))

            # Actualizar datos escolares
            self.lbl_grado.campo_editable.setText(str(self.alumno_data.get('grado', '')))
            self.lbl_grupo.campo_editable.setText(self.alumno_data.get('grupo', ''))
            self.lbl_turno.campo_editable.setText(self.alumno_data.get('turno', ''))
            self.lbl_ciclo.campo_editable.setText(self.alumno_data.get('ciclo_escolar', ''))
            self.lbl_escuela.campo_editable.setText(self.alumno_data.get('escuela', ''))
            self.lbl_cct.campo_editable.setText(self.alumno_data.get('cct', ''))

            # Cargar calificaciones
            self.cargar_calificaciones()

        except Exception as e:
            self.title_label.setText("Error al cargar datos")
            QMessageBox.critical(self, "Error", f"Error al cargar datos del alumno: {str(e)}")

    def cargar_calificaciones(self):
        """Carga y muestra las calificaciones del alumno"""
        # Limpiar la tabla de calificaciones
        self.tabla_calificaciones.setRowCount(0)

        # Verificar si hay calificaciones
        calificaciones = self.alumno_data.get('calificaciones', [])

        if calificaciones and len(calificaciones) > 0:
            # Mostrar mensaje de que hay calificaciones
            self.lbl_estado_calificaciones.setText("El alumno tiene calificaciones registradas.")
            self.lbl_estado_calificaciones.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #d5f5e3;
                    color: #27ae60;
                }
            """)

            # Llenar la tabla con las calificaciones
            self.tabla_calificaciones.setRowCount(len(calificaciones))

            for row, cal in enumerate(calificaciones):
                # Nombre de la materia
                nombre_item = QTableWidgetItem(cal.get('nombre', ''))
                self.tabla_calificaciones.setItem(row, 0, nombre_item)

                # Calificaciones por periodo
                p1_item = QTableWidgetItem(str(cal.get('i', '')))
                p1_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_calificaciones.setItem(row, 1, p1_item)

                p2_item = QTableWidgetItem(str(cal.get('ii', '')))
                p2_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_calificaciones.setItem(row, 2, p2_item)

                p3_item = QTableWidgetItem(str(cal.get('iii', '')))
                p3_item.setTextAlignment(Qt.AlignCenter)
                self.tabla_calificaciones.setItem(row, 3, p3_item)

                # Promedio
                promedio_item = QTableWidgetItem(str(cal.get('promedio', '')))
                promedio_item.setTextAlignment(Qt.AlignCenter)
                promedio_item.setForeground(QBrush(QColor("#e74c3c")))  # Color rojo para el promedio
                promedio_item.setFont(QFont("Arial", 10, QFont.Bold))
                self.tabla_calificaciones.setItem(row, 4, promedio_item)

            # Ajustar altura de las filas
            for row in range(self.tabla_calificaciones.rowCount()):
                self.tabla_calificaciones.setRowHeight(row, 30)

            # Ajustar la altura total de la tabla para mostrar todas las filas
            header_height = self.tabla_calificaciones.horizontalHeader().height()
            content_height = sum(self.tabla_calificaciones.rowHeight(row) for row in range(self.tabla_calificaciones.rowCount()))
            total_height = header_height + content_height + 4  # +4 para el borde y un poco de espacio extra

            # Limitar la altura máxima a 300px para evitar que la tabla sea demasiado grande
            max_height = 300
            if total_height > max_height and self.tabla_calificaciones.rowCount() > 5:
                # Si hay muchas filas, permitir scroll vertical
                self.tabla_calificaciones.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                self.tabla_calificaciones.setFixedHeight(max_height)
            else:
                # Si hay pocas filas, mostrar todas sin scroll
                self.tabla_calificaciones.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.tabla_calificaciones.setFixedHeight(total_height)

            # Mostrar la tabla
            self.tabla_calificaciones.show()
            self.calificaciones_group.show()
        else:
            # Mostrar mensaje de que no hay calificaciones
            self.lbl_estado_calificaciones.setText("El alumno no tiene calificaciones registradas.")
            self.lbl_estado_calificaciones.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #fadbd8;
                    color: #c0392b;
                }
            """)

            # Ocultar la tabla
            self.tabla_calificaciones.hide()
            self.calificaciones_group.show()



class GenerarConstanciaDialog(QDialog):
    """Diálogo para generar una constancia"""

    def __init__(self, parent=None, alumno_id=None, alumno_nombre=None):
        super().__init__(parent)
        self.setWindowTitle("Generar Constancia")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        self.alumno_id = alumno_id
        self.alumno_nombre = alumno_nombre

        # Usar el proveedor de servicios
        service_provider = ServiceProvider.get_instance()
        self.constancia_service = service_provider.constancia_service

        self.preview_file = None

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout()  # Cambiado a vertical para poner la vista previa debajo
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Panel superior (opciones)
        top_panel = QWidget()
        top_layout = QVBoxLayout(top_panel)
        top_layout.setSpacing(20)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Título con nombre del alumno
        if self.alumno_nombre:
            title_label = QLabel(f"Generar Constancia para: {self.alumno_nombre}")
            title_label.setAlignment(Qt.AlignCenter)
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

            top_layout.addWidget(title_label)

        # Contenedor para opciones en horizontal
        options_container = QWidget()
        options_layout = QHBoxLayout(options_container)
        options_layout.setSpacing(20)

        # Tipo de constancia
        tipo_group = QGroupBox("Tipo de Constancia")
        tipo_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        tipo_layout = QVBoxLayout(tipo_group)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["estudio", "calificaciones", "traslado"])
        self.combo_tipo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
            QComboBox::down-arrow {
                width: 15px;
                height: 15px;
            }
        """)
        self.combo_tipo.setMinimumHeight(50)
        self.combo_tipo.currentIndexChanged.connect(self.generar_vista_previa)

        tipo_layout.addWidget(self.combo_tipo)

        # Opciones adicionales
        options_group = QGroupBox("Opciones")
        options_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #2ecc71;
            }
        """)

        options_layout_inner = QVBoxLayout(options_group)

        self.check_foto = QCheckBox("Incluir foto si está disponible")
        self.check_foto.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                background-color: #f8f9fa;
                margin: 5px;
            }
            QCheckBox:checked {
                background-color: #d5f5e3;
                font-weight: bold;
            }
            QCheckBox:hover {
                background-color: #eafaf1;
            }
        """)
        self.check_foto.setChecked(False)  # Cambiado a False por defecto
        self.check_foto.stateChanged.connect(self.generar_vista_previa)

        options_layout_inner.addWidget(self.check_foto)

        # Añadir grupos a la fila de opciones
        options_layout.addWidget(tipo_group, 1)
        options_layout.addWidget(options_group, 1)

        top_layout.addWidget(options_container)

        # Botones
        buttons_layout = QHBoxLayout()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_cancelar.setMinimumHeight(50)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_generar = QPushButton("Generar Constancia")
        self.btn_generar.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_generar.setMinimumHeight(50)
        self.btn_generar.clicked.connect(self.generar_constancia)
        self.btn_generar.setDefault(True)

        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_generar)

        top_layout.addLayout(buttons_layout)

        # Añadir panel superior al layout principal
        main_layout.addWidget(top_panel)

        # Panel inferior (vista previa)
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("Vista Previa")
        preview_label.setAlignment(Qt.AlignCenter)
        preview_font = QFont()
        preview_font.setPointSize(16)
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        preview_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        self.pdf_viewer = PDFViewer()
        self.pdf_viewer.setStyleSheet("""
            QScrollArea {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)
        self.pdf_viewer.setMinimumHeight(400)  # Altura mínima para la vista previa

        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(self.pdf_viewer)

        # Añadir panel de vista previa al layout principal
        main_layout.addWidget(preview_panel)

        self.setLayout(main_layout)

        # Generar vista previa inicial
        self.generar_vista_previa()

    def generar_vista_previa(self):
        """Genera una vista previa de la constancia"""
        if not self.alumno_id:
            return

        tipo_constancia = self.combo_tipo.currentText()
        incluir_foto = self.check_foto.isChecked()

        try:
            # Crear un archivo temporal para la vista previa
            if self.preview_file:
                # Limpiar el archivo temporal anterior si existe
                try:
                    self.pdf_viewer.close_pdf()
                    if os.path.exists(self.preview_file):
                        os.remove(self.preview_file)
                except:
                    pass

            # Generar vista previa
            success, message, data = self.constancia_service.generar_constancia_para_alumno(
                self.alumno_id, tipo_constancia, incluir_foto, preview_mode=True
            )

            if success and data and "ruta_archivo" in data:
                self.preview_file = data["ruta_archivo"]
                self.pdf_viewer.load_pdf(self.preview_file)
            else:
                # Mostrar mensaje de error en la vista previa
                self.pdf_viewer.page_label.setText(f"Error al generar vista previa: {message}")
                self.pdf_viewer.page_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")

        except Exception as e:
            self.pdf_viewer.page_label.setText(f"Error al generar vista previa: {str(e)}")
            self.pdf_viewer.page_label.setStyleSheet("color: red; font-size: 16px; padding: 20px;")

    def generar_constancia(self):
        """Genera una constancia para el alumno"""
        if not self.alumno_id:
            QMessageBox.warning(self, "Error", "No se ha seleccionado un alumno.")
            return

        tipo_constancia = self.combo_tipo.currentText()
        incluir_foto = self.check_foto.isChecked()

        try:
            success, message, data = self.constancia_service.generar_constancia_para_alumno(
                self.alumno_id, tipo_constancia, incluir_foto
            )

            if success:
                reply = QMessageBox.information(
                    self, "¡Constancia Generada!",
                    f"{message}\n\n¿Desea abrir la constancia?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                )

                if reply == QMessageBox.Yes and data and "ruta_archivo" in data:
                    open_file_with_default_app(data["ruta_archivo"])

                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar constancia: {str(e)}")

    def closeEvent(self, event):
        """Limpia los archivos temporales al cerrar el diálogo"""
        try:
            self.pdf_viewer.close_pdf()
            if self.preview_file and os.path.exists(self.preview_file):
                os.remove(self.preview_file)
        except:
            pass
        super().closeEvent(event)

class BuscarWindow(QMainWindow):
    """Ventana para buscar alumnos y generar constancias"""

    def __init__(self):
        super().__init__()

        # Usar el proveedor de servicios
        service_provider = ServiceProvider.get_instance()
        self.alumno_service = service_provider.alumno_service

        self.setWindowTitle("Buscar y Generar Constancias")
        self.setMinimumSize(900, 700)

        self.setup_ui()
        self.load_alumnos()

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
        title_label = QLabel("Buscar y Generar Constancias")
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

        # Barra de búsqueda y filtros
        search_group = QGroupBox("Buscar y Filtrar Alumnos")
        search_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(15)

        # Búsqueda principal
        main_search_layout = QHBoxLayout()
        main_search_layout.setSpacing(15)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Ingrese nombre o CURP del alumno...")
        self.txt_search.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
        """)
        self.txt_search.setMinimumHeight(50)
        self.txt_search.returnPressed.connect(self.search_alumnos)

        self.btn_search = QPushButton("Buscar")
        self.btn_search.setStyleSheet("""
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
        self.btn_search.setMinimumHeight(50)
        self.btn_search.setMinimumWidth(120)
        self.btn_search.clicked.connect(self.search_alumnos)

        self.btn_clear = QPushButton("Limpiar")
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_clear.setMinimumHeight(50)
        self.btn_clear.setMinimumWidth(120)
        self.btn_clear.clicked.connect(self.clear_search)

        main_search_layout.addWidget(self.txt_search)
        main_search_layout.addWidget(self.btn_search)
        main_search_layout.addWidget(self.btn_clear)

        search_layout.addLayout(main_search_layout)

        # Filtros adicionales
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(15)

        # Filtro por grado
        grado_layout = QHBoxLayout()
        grado_label = QLabel("Grado:")
        grado_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.combo_grado = QComboBox()
        self.combo_grado.addItem("Todos", -1)
        for i in range(1, 7):
            self.combo_grado.addItem(f"{i}°", i)
        self.combo_grado.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-width: 100px;
            }
        """)
        self.combo_grado.currentIndexChanged.connect(self.apply_filters)

        grado_layout.addWidget(grado_label)
        grado_layout.addWidget(self.combo_grado)

        # Filtro por grupo
        grupo_layout = QHBoxLayout()
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.combo_grupo = QComboBox()
        self.combo_grupo.addItem("Todos", "")
        for grupo in ["A", "B", "C", "D"]:
            self.combo_grupo.addItem(grupo, grupo)
        self.combo_grupo.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-width: 100px;
            }
        """)
        self.combo_grupo.currentIndexChanged.connect(self.apply_filters)

        grupo_layout.addWidget(grupo_label)
        grupo_layout.addWidget(self.combo_grupo)

        # Ordenamiento
        orden_layout = QHBoxLayout()
        orden_label = QLabel("Ordenar por:")
        orden_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.combo_orden = QComboBox()
        self.combo_orden.addItem("Nombre (A-Z)", "nombre_asc")
        self.combo_orden.addItem("Nombre (Z-A)", "nombre_desc")
        self.combo_orden.addItem("Grado (Asc)", "grado_asc")
        self.combo_orden.addItem("Grado (Desc)", "grado_desc")
        self.combo_orden.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-width: 150px;
            }
        """)
        self.combo_orden.currentIndexChanged.connect(self.apply_filters)

        orden_layout.addWidget(orden_label)
        orden_layout.addWidget(self.combo_orden)

        # Añadir todos los filtros al layout
        filters_layout.addLayout(grado_layout)
        filters_layout.addLayout(grupo_layout)
        filters_layout.addLayout(orden_layout)
        filters_layout.addStretch()

        search_layout.addLayout(filters_layout)

        main_layout.addWidget(search_group)

        # Tabla de alumnos
        results_group = QGroupBox("Resultados")
        results_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #2ecc71;
            }
        """)

        results_layout = QVBoxLayout(results_group)

        self.table_alumnos = QTableWidget()
        self.table_alumnos.setColumnCount(4)  # Reducido de 5 a 4 columnas
        self.table_alumnos.setHorizontalHeaderLabels([
            "Nombre", "CURP", "Grado/Grupo", "Acciones"
        ])

        # Ocultar el encabezado vertical (números de fila)
        self.table_alumnos.verticalHeader().setVisible(False)

        # Establecer altura mínima para la tabla
        self.table_alumnos.setMinimumHeight(400)

        # Configurar fuente para la tabla
        table_font = QFont()
        table_font.setPointSize(11)
        self.table_alumnos.setFont(table_font)

        # Configurar fuente para el encabezado
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        self.table_alumnos.horizontalHeader().setFont(header_font)

        # Altura de las filas - aumentada significativamente
        self.table_alumnos.verticalHeader().setDefaultSectionSize(65)

        # Hacer que el encabezado horizontal sea fijo y no se pueda mover
        self.table_alumnos.horizontalHeader().setSectionsClickable(False)
        self.table_alumnos.horizontalHeader().setSectionsMovable(False)

        # Configurar el ancho de las columnas para que se adapten al tamaño de la ventana

        # Hacer que las columnas principales se estiren proporcionalmente
        self.table_alumnos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Nombre (se estira)
        self.table_alumnos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # CURP (se estira)

        # Columnas con ancho proporcional pero no fijo
        self.table_alumnos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Grado/Grupo

        # La columna de acciones debe tener un ancho fijo
        self.table_alumnos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)  # Acciones
        self.table_alumnos.setColumnWidth(3, 250)  # Acciones (más ancho para los botones)

        self.table_alumnos.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_alumnos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_alumnos.setAlternatingRowColors(True)

        # Estilo de la tabla
        self.table_alumnos.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #d6eaf8;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
                font-size: 11pt;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #3498db;
                font-size: 12pt;
                font-weight: bold;
            }
            QHeaderView::section:first {
                border-top-left-radius: 5px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 5px;
                border-right: none;
            }
        """)

        results_layout.addWidget(self.table_alumnos)

        main_layout.addWidget(results_group, 1)

        # Botones de acción
        action_layout = QHBoxLayout()

        self.btn_refresh = QPushButton("Actualizar Lista")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.btn_refresh.setMinimumHeight(50)
        self.btn_refresh.clicked.connect(self.load_alumnos)

        action_layout.addStretch()
        action_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(action_layout)

    def load_alumnos(self):
        """Carga la lista de alumnos"""
        try:
            alumnos = self.alumno_service.listar_alumnos(limit=100)
            self.alumnos_data = alumnos  # Guardar los datos originales
            self.apply_filters()  # Aplicar filtros a los datos cargados
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar alumnos: {str(e)}")

    def search_alumnos(self):
        """Busca alumnos por nombre o CURP"""
        query = self.txt_search.text().strip()
        if not query:
            self.load_alumnos()
            return

        try:
            alumnos = self.alumno_service.buscar_alumnos(query)
            self.alumnos_data = alumnos  # Guardar los datos de búsqueda
            self.apply_filters()  # Aplicar filtros a los resultados de búsqueda
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar alumnos: {str(e)}")

    def clear_search(self):
        """Limpia la búsqueda y los filtros"""
        self.txt_search.clear()
        self.combo_grado.setCurrentIndex(0)  # "Todos"
        self.combo_grupo.setCurrentIndex(0)  # "Todos"
        self.combo_orden.setCurrentIndex(0)  # "Nombre (A-Z)"
        self.load_alumnos()

    def apply_filters(self):
        """Aplica filtros y ordenamiento a los datos"""
        if not hasattr(self, 'alumnos_data'):
            return

        # Obtener valores de filtros
        grado_index = self.combo_grado.currentIndex()
        grado_value = self.combo_grado.itemData(grado_index)

        grupo_index = self.combo_grupo.currentIndex()
        grupo_value = self.combo_grupo.itemData(grupo_index)

        orden_index = self.combo_orden.currentIndex()
        orden_value = self.combo_orden.itemData(orden_index)

        # Filtrar datos
        filtered_data = self.alumnos_data.copy()

        # Filtrar por grado
        if grado_value != -1:  # Si no es "Todos"
            filtered_data = [a for a in filtered_data if a.get('grado') == grado_value]

        # Filtrar por grupo
        if grupo_value:  # Si no es "Todos"
            filtered_data = [a for a in filtered_data if a.get('grupo') == grupo_value]

        # Ordenar datos
        if orden_value == "nombre_asc":
            filtered_data.sort(key=lambda x: x.get('nombre', '').lower())
        elif orden_value == "nombre_desc":
            filtered_data.sort(key=lambda x: x.get('nombre', '').lower(), reverse=True)
        elif orden_value == "grado_asc":
            filtered_data.sort(key=lambda x: (x.get('grado', 0), x.get('grupo', ''), x.get('nombre', '').lower()))
        elif orden_value == "grado_desc":
            filtered_data.sort(key=lambda x: (x.get('grado', 0), x.get('grupo', ''), x.get('nombre', '').lower()), reverse=True)

        # Mostrar resultados
        self.populate_table(filtered_data)

    def populate_table(self, alumnos):
        """Rellena la tabla con los datos de los alumnos"""
        self.table_alumnos.setRowCount(0)

        for row, alumno in enumerate(alumnos):
            self.table_alumnos.insertRow(row)

            # Guardamos el ID como dato de usuario en el primer elemento
            # pero no lo mostramos como columna separada

            # Nombre
            nombre_item = QTableWidgetItem(alumno["nombre"])
            nombre_item.setData(Qt.UserRole, alumno["id"])  # Guardamos el ID aquí
            nombre_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 0, nombre_item)

            # CURP
            curp_item = QTableWidgetItem(alumno["curp"])
            curp_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 1, curp_item)

            # Grado/Grupo
            grado_grupo = f"{alumno.get('grado', '')}° {alumno.get('grupo', '')}"
            grado_grupo_item = QTableWidgetItem(grado_grupo)
            grado_grupo_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 2, grado_grupo_item)

            # Botones de acción
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)  # Cambiado a horizontal
            action_layout.setContentsMargins(2, 10, 2, 10)
            action_layout.setSpacing(20)  # Mayor espaciado
            action_layout.setAlignment(Qt.AlignCenter)  # Centrar los botones

            # Botón para ver detalles
            btn_detalles = QPushButton("Detalles")
            btn_detalles.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_detalles.setProperty("alumno_id", alumno["id"])
            btn_detalles.setProperty("alumno_nombre", alumno["nombre"])
            btn_detalles.clicked.connect(self.ver_detalles_alumno)

            # Botón para generar constancia
            btn_generar = QPushButton("Generar")
            btn_generar.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            btn_generar.setProperty("alumno_id", alumno["id"])
            btn_generar.setProperty("alumno_nombre", alumno["nombre"])
            btn_generar.clicked.connect(self.open_generar_dialog)

            action_layout.addWidget(btn_detalles)
            action_layout.addWidget(btn_generar)

            self.table_alumnos.setCellWidget(row, 3, action_widget)

            # Ajustar altura de la fila para acomodar los botones horizontales
            self.table_alumnos.setRowHeight(row, 65)

    def open_generar_dialog(self):
        """Abre el diálogo para generar una constancia"""
        btn = self.sender()
        alumno_id = btn.property("alumno_id")
        alumno_nombre = btn.property("alumno_nombre")

        dialog = GenerarConstanciaDialog(self, alumno_id=alumno_id, alumno_nombre=alumno_nombre)
        dialog.exec_()

    def ver_detalles_alumno(self):
        """Abre el diálogo para ver los detalles del alumno"""
        btn = self.sender()
        alumno_id = btn.property("alumno_id")

        dialog = DetallesAlumnoDialog(self, alumno_id=alumno_id)
        dialog.exec_()

    def volver_menu_principal(self):
        """Cierra esta ventana y vuelve al menú principal"""
        self.close()

def main():
    """Función principal"""
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = BuscarWindow()
    window.show()
    sys.exit(app.exec_())
