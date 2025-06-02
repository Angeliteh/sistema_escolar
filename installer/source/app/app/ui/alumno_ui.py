"""
Interfaz de usuario para gestión de alumnos
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QSpinBox, QDateEdit,
    QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from app.core.service_provider import ServiceProvider
from app.core.config import Config
from app.core.utils import format_curp, is_valid_curp, open_file_with_default_app

class RegistroAlumnoDialog(QDialog):
    """Diálogo para registrar o editar un alumno"""

    def __init__(self, parent=None, alumno_id=None, alumno_service=None):
        super().__init__(parent)
        self.alumno_id = alumno_id

        # Usar el servicio proporcionado o obtenerlo del proveedor de servicios
        if alumno_service:
            self.alumno_service = alumno_service
        else:
            service_provider = ServiceProvider.get_instance()
            self.alumno_service = service_provider.alumno_service

        self.alumno_data = None

        if alumno_id:
            self.setWindowTitle("Editar Alumno")
            self.alumno_data = self.alumno_service.get_alumno(alumno_id)
        else:
            self.setWindowTitle("Registrar Nuevo Alumno")

        self.setup_ui()

        if self.alumno_data:
            self.populate_form()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setMinimumWidth(600)  # Ancho mínimo
        self.setMinimumHeight(600)  # Alto mínimo

        # Tamaño fijo más compacto
        self.setFixedSize(650, 650)

        # Evitar que la ventana se redimensione
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        layout = QVBoxLayout()
        layout.setSpacing(15)  # Espacio entre elementos
        layout.setContentsMargins(20, 20, 20, 20)  # Márgenes más pequeños

        # Título
        title_label = QLabel("Información del Alumno")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        layout.addWidget(title_label)

        # Datos personales
        group_personal = QGroupBox("Datos Personales")
        group_personal.setStyleSheet("""
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

        form_personal = QFormLayout()
        form_personal.setSpacing(20)  # Mayor espaciado
        form_personal.setLabelAlignment(Qt.AlignRight)
        form_personal.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # Permitir que los campos crezcan
        form_personal.setRowWrapPolicy(QFormLayout.WrapLongRows)  # Envolver filas largas

        # Estilo para las etiquetas
        label_style = """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
                padding: 3px;
                min-width: 120px;
                max-width: 120px;
            }
        """

        # Estilo para los campos de entrada
        input_style = """
            QLineEdit, QDateEdit, QSpinBox, QComboBox {
                font-size: 13px;
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 30px;
                margin: 3px;
                min-width: 250px;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
                background-color: #f0f9ff;
            }
            QDateEdit::drop-down, QSpinBox::up-button, QSpinBox::down-button, QComboBox::drop-down {
                width: 20px;
                height: 20px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
                border-left: 1px solid #bdc3c7;
            }
        """

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setStyleSheet(input_style)
        self.txt_nombre.setPlaceholderText("Nombre completo del alumno")

        self.txt_curp = QLineEdit()
        self.txt_curp.setStyleSheet(input_style)
        self.txt_curp.setPlaceholderText("CURP del alumno")

        self.txt_matricula = QLineEdit()
        self.txt_matricula.setStyleSheet(input_style)
        self.txt_matricula.setPlaceholderText("Número de matrícula")

        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setStyleSheet(input_style)
        self.date_nacimiento.setCalendarPopup(True)
        self.date_nacimiento.setDate(QDate.currentDate())

        nombre_label = QLabel("Nombre:")
        nombre_label.setStyleSheet(label_style)
        curp_label = QLabel("CURP:")
        curp_label.setStyleSheet(label_style)
        matricula_label = QLabel("Matrícula:")
        matricula_label.setStyleSheet(label_style)
        nacimiento_label = QLabel("Fecha de Nacimiento:")
        nacimiento_label.setStyleSheet(label_style)

        form_personal.addRow(nombre_label, self.txt_nombre)
        form_personal.addRow(curp_label, self.txt_curp)
        form_personal.addRow(matricula_label, self.txt_matricula)
        form_personal.addRow(nacimiento_label, self.date_nacimiento)

        group_personal.setLayout(form_personal)
        layout.addWidget(group_personal)

        # Datos escolares
        group_escolar = QGroupBox("Datos Escolares")
        group_escolar.setStyleSheet("""
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

        form_escolar = QFormLayout()
        form_escolar.setSpacing(20)  # Mayor espaciado
        form_escolar.setLabelAlignment(Qt.AlignRight)
        form_escolar.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)  # Permitir que los campos crezcan
        form_escolar.setRowWrapPolicy(QFormLayout.WrapLongRows)  # Envolver filas largas

        self.txt_ciclo = QLineEdit(Config.get_current_year())
        self.txt_ciclo.setStyleSheet(input_style)
        self.txt_ciclo.setPlaceholderText("Ejemplo: 2023-2024")

        self.spin_grado = QSpinBox()
        self.spin_grado.setStyleSheet(input_style)
        self.spin_grado.setMinimum(1)
        self.spin_grado.setMaximum(6)
        self.spin_grado.setValue(Config.DEFAULT_GRADE)

        self.combo_grupo = QComboBox()
        self.combo_grupo.setStyleSheet(input_style)
        for grupo in ["A", "B", "C", "D", "E", "F"]:
            self.combo_grupo.addItem(grupo)
        self.combo_grupo.setCurrentText(Config.DEFAULT_GROUP)

        self.combo_turno = QComboBox()
        self.combo_turno.setStyleSheet(input_style)
        self.combo_turno.addItems(["MATUTINO", "VESPERTINO"])
        self.combo_turno.setCurrentText(Config.DEFAULT_SHIFT)

        ciclo_label = QLabel("Ciclo Escolar:")
        ciclo_label.setStyleSheet(label_style)
        grado_label = QLabel("Grado:")
        grado_label.setStyleSheet(label_style)
        grupo_label = QLabel("Grupo:")
        grupo_label.setStyleSheet(label_style)
        turno_label = QLabel("Turno:")
        turno_label.setStyleSheet(label_style)

        form_escolar.addRow(ciclo_label, self.txt_ciclo)
        form_escolar.addRow(grado_label, self.spin_grado)
        form_escolar.addRow(grupo_label, self.combo_grupo)
        form_escolar.addRow(turno_label, self.combo_turno)

        group_escolar.setLayout(form_escolar)
        layout.addWidget(group_escolar)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #922b21;
            }
        """)
        self.btn_cancelar.setMinimumHeight(40)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_guardar = QPushButton("Guardar Alumno")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 140px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.btn_guardar.setMinimumHeight(40)
        self.btn_guardar.clicked.connect(self.save_alumno)
        self.btn_guardar.setDefault(True)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_cancelar)
        buttons_layout.addWidget(self.btn_guardar)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def populate_form(self):
        """Rellena el formulario con los datos del alumno"""
        if not self.alumno_data:
            return

        self.txt_nombre.setText(self.alumno_data.get("nombre", ""))
        self.txt_curp.setText(self.alumno_data.get("curp", ""))
        self.txt_matricula.setText(self.alumno_data.get("matricula", ""))

        # Fecha de nacimiento
        if self.alumno_data.get("fecha_nacimiento"):
            try:
                fecha = QDate.fromString(self.alumno_data["fecha_nacimiento"], "yyyy-MM-dd")
                if fecha.isValid():
                    self.date_nacimiento.setDate(fecha)
            except Exception:
                pass

        # Datos escolares
        if self.alumno_data.get("ciclo_escolar"):
            self.txt_ciclo.setText(self.alumno_data["ciclo_escolar"])

        if self.alumno_data.get("grado"):
            self.spin_grado.setValue(int(self.alumno_data["grado"]))

        if self.alumno_data.get("grupo"):
            self.combo_grupo.setCurrentText(self.alumno_data["grupo"])

        if self.alumno_data.get("turno"):
            self.combo_turno.setCurrentText(self.alumno_data["turno"])

    def save_alumno(self):
        """Guarda los datos del alumno"""
        # Validar datos
        nombre = self.txt_nombre.text().strip()
        curp = format_curp(self.txt_curp.text())

        if not nombre:
            QMessageBox.warning(self, "Datos Incompletos", "El nombre es obligatorio.")
            self.txt_nombre.setFocus()
            return

        if not curp:
            QMessageBox.warning(self, "Datos Incompletos", "La CURP es obligatoria.")
            self.txt_curp.setFocus()
            return

        if not is_valid_curp(curp):
            QMessageBox.warning(self, "CURP Inválida", "La CURP no tiene un formato válido.")
            self.txt_curp.setFocus()
            return

        # Preparar datos
        datos = {
            "nombre": nombre,
            "curp": curp,
            "matricula": self.txt_matricula.text().strip(),
            "fecha_nacimiento": self.date_nacimiento.date().toString("yyyy-MM-dd"),
            "ciclo_escolar": self.txt_ciclo.text().strip(),
            "grado": self.spin_grado.value(),
            "grupo": self.combo_grupo.currentText(),
            "turno": self.combo_turno.currentText()
        }

        try:
            if self.alumno_id:
                # Actualizar alumno existente
                # El método actualizar_alumno devuelve un booleano, no una tupla
                success = self.alumno_service.actualizar_alumno(self.alumno_id, datos)
                message = "Alumno actualizado correctamente" if success else "No se pudo actualizar el alumno"
            else:
                # Registrar nuevo alumno
                success, message, _ = self.alumno_service.registrar_alumno(datos)

            if success:
                QMessageBox.information(self, "Operación Exitosa", message)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar alumno: {str(e)}")

class AlumnoManagerWindow(QMainWindow):
    """Ventana principal para gestión de alumnos"""

    def __init__(self):
        super().__init__()

        # Usar el proveedor de servicios
        service_provider = ServiceProvider.get_instance()
        self.alumno_service = service_provider.alumno_service
        self.constancia_service = service_provider.constancia_service

        self.setWindowTitle("Gestión de Alumnos")
        self.setMinimumSize(900, 700)

        # Establecer tamaño inicial pero permitir redimensionar
        self.resize(1200, 800)

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
        title_label = QLabel("Administración de Base de Datos")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        top_bar_layout.addWidget(self.btn_volver)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.setStretch(0, 1)  # El botón ocupa menos espacio
        top_bar_layout.setStretch(1, 3)  # El título ocupa más espacio

        main_layout.addWidget(top_bar)

        # Barra de búsqueda
        search_group = QGroupBox("Buscar Alumno")
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

        search_layout = QHBoxLayout(search_group)
        search_layout.setSpacing(15)

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

        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_clear)

        main_layout.addWidget(search_group)

        # Tabla de alumnos
        table_group = QGroupBox("Lista de Alumnos")
        table_group.setStyleSheet("""
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

        table_layout = QVBoxLayout(table_group)

        self.table_alumnos = QTableWidget()
        self.table_alumnos.setColumnCount(6)  # Reducido de 7 a 6 columnas
        self.table_alumnos.setHorizontalHeaderLabels([
            "Nombre", "CURP", "Matrícula", "Grado", "Grupo", "Acciones"
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
        self.table_alumnos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Matrícula
        self.table_alumnos.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Grado
        self.table_alumnos.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Grupo

        # La columna de acciones debe tener un ancho fijo
        self.table_alumnos.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)  # Acciones
        self.table_alumnos.setColumnWidth(5, 250)  # Acciones (más ancho para los botones mejorados)

        # Configuración de selección y edición
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

        table_layout.addWidget(self.table_alumnos)

        main_layout.addWidget(table_group)

        # Botones de acción
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)

        self.btn_nuevo = QPushButton("Nuevo Alumno")
        self.btn_nuevo.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_nuevo.setMinimumHeight(50)
        self.btn_nuevo.clicked.connect(self.new_alumno)

        self.btn_refresh = QPushButton("Actualizar Lista")
        self.btn_refresh.setStyleSheet("""
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
        self.btn_refresh.setMinimumHeight(50)
        self.btn_refresh.clicked.connect(self.load_alumnos)

        action_layout.addStretch()
        action_layout.addWidget(self.btn_nuevo)
        action_layout.addWidget(self.btn_refresh)
        action_layout.addStretch()

        main_layout.addLayout(action_layout)

    def load_alumnos(self):
        """Carga la lista de alumnos"""
        try:
            alumnos = self.alumno_service.listar_alumnos(limit=100)
            self.populate_table(alumnos)
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
            self.populate_table(alumnos)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar alumnos: {str(e)}")

    def clear_search(self):
        """Limpia la búsqueda"""
        self.txt_search.clear()
        self.load_alumnos()

    def populate_table(self, alumnos):
        """Rellena la tabla con los datos de los alumnos"""
        self.table_alumnos.setRowCount(0)

        for row, alumno in enumerate(alumnos):
            self.table_alumnos.insertRow(row)

            # Nombre (con ID oculto como dato de usuario)
            nombre_item = QTableWidgetItem(alumno["nombre"])
            nombre_item.setData(Qt.UserRole, alumno["id"])  # Guardamos el ID aquí
            nombre_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 0, nombre_item)

            # CURP
            curp_item = QTableWidgetItem(alumno["curp"])
            curp_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 1, curp_item)

            # Matrícula
            matricula = alumno.get("matricula", "")
            matricula_item = QTableWidgetItem(matricula)
            matricula_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 2, matricula_item)

            # Grado
            grado = str(alumno.get("grado", ""))
            grado_item = QTableWidgetItem(grado)
            grado_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 3, grado_item)

            # Grupo
            grupo = alumno.get("grupo", "")
            grupo_item = QTableWidgetItem(grupo)
            grupo_item.setTextAlignment(Qt.AlignCenter)
            self.table_alumnos.setItem(row, 4, grupo_item)

            # Botones de acción
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 10, 2, 10)
            action_layout.setSpacing(20)  # Mayor espaciado entre botones
            action_layout.setAlignment(Qt.AlignCenter)  # Centrar los botones

            # Botón de editar mejorado
            btn_edit = QPushButton("Editar")
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 70px;
                    min-height: 25px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_edit.setProperty("alumno_id", alumno["id"])
            btn_edit.clicked.connect(self.edit_alumno)

            # Botón de eliminar mejorado
            btn_delete = QPushButton("Eliminar")
            btn_delete.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border-radius: 5px;
                    padding: 5px;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 80px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            btn_delete.setProperty("alumno_id", alumno["id"])
            btn_delete.clicked.connect(self.delete_alumno)


            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)

            self.table_alumnos.setCellWidget(row, 5, action_widget)

            # Ajustar altura de la fila para acomodar los botones horizontales
            self.table_alumnos.setRowHeight(row, 65)

    def new_alumno(self):
        """Abre el diálogo para registrar un nuevo alumno"""
        dialog = RegistroAlumnoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_alumnos()

    def edit_alumno(self):
        """Abre el diálogo para editar un alumno"""
        btn = self.sender()
        alumno_id = btn.property("alumno_id")

        dialog = RegistroAlumnoDialog(self, alumno_id=alumno_id)
        if dialog.exec_() == QDialog.Accepted:
            self.load_alumnos()

    def delete_alumno(self):
        """Elimina un alumno"""
        btn = self.sender()
        alumno_id = btn.property("alumno_id")

        # Buscar el nombre del alumno
        for row in range(self.table_alumnos.rowCount()):
            if self.table_alumnos.item(row, 0).data(Qt.UserRole) == alumno_id:
                nombre = self.table_alumnos.item(row, 0).text()
                break
        else:
            nombre = f"ID: {alumno_id}"

        # Confirmar eliminación
        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar al alumno {nombre}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success, message = self.alumno_service.eliminar_alumno(alumno_id)

                if success:
                    QMessageBox.information(self, "Operación Exitosa", message)
                    self.load_alumnos()
                else:
                    QMessageBox.warning(self, "Error", message)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar alumno: {str(e)}")

    def volver_menu_principal(self):
        """Cierra esta ventana y vuelve al menú principal"""
        self.close()

    def generate_constancia(self):
        """Genera una constancia para el alumno seleccionado"""
        # Verificar si hay un alumno seleccionado
        selected_rows = self.table_alumnos.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Selección Requerida", "Por favor, seleccione un alumno.")
            return

        # Obtener el ID del alumno seleccionado
        row = selected_rows[0].row()
        alumno_id = self.table_alumnos.item(row, 0).data(Qt.UserRole)

        # Abrir diálogo para seleccionar tipo de constancia
        dialog = QDialog(self)
        dialog.setWindowTitle("Generar Constancia")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(300)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("Generar Constancia")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        layout.addWidget(title_label)

        # Opciones
        options_group = QGroupBox("Opciones de Constancia")
        options_group.setStyleSheet("""
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

        form_layout = QFormLayout(options_group)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Estilo para las etiquetas
        label_style = """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #34495e;
            }
        """

        # Estilo para los campos de entrada
        input_style = """
            QComboBox {
                font-size: 13px;
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-height: 30px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QCheckBox {
                font-size: 13px;
                padding: 8px;
            }
            QCheckBox:checked {
                color: #2ecc71;
                font-weight: bold;
            }
        """

        combo_tipo = QComboBox()
        combo_tipo.addItems(["traslado", "estudio", "calificaciones"])
        combo_tipo.setStyleSheet(input_style)

        check_foto = QCheckBox("Incluir foto si está disponible")
        check_foto.setStyleSheet(input_style)
        check_foto.setChecked(False)  # Por defecto, no incluir foto

        tipo_label = QLabel("Tipo de constancia:")
        tipo_label.setStyleSheet(label_style)

        form_layout.addRow(tipo_label, combo_tipo)
        form_layout.addRow("", check_foto)

        layout.addWidget(options_group)

        # Botones
        buttons = QHBoxLayout()
        buttons.setSpacing(15)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancel.setMinimumHeight(40)
        btn_cancel.clicked.connect(dialog.reject)

        btn_generate = QPushButton("Generar Constancia")
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        btn_generate.setMinimumHeight(40)
        btn_generate.clicked.connect(dialog.accept)
        btn_generate.setDefault(True)

        buttons.addStretch()
        buttons.addWidget(btn_cancel)
        buttons.addWidget(btn_generate)

        layout.addLayout(buttons)

        if dialog.exec_() == QDialog.Accepted:
            tipo_constancia = combo_tipo.currentText()
            incluir_foto = check_foto.isChecked()

            try:
                success, message, data = self.constancia_service.generar_constancia_para_alumno(
                    alumno_id, tipo_constancia, incluir_foto
                )

                if success:
                    reply = QMessageBox.information(
                        self, "¡Constancia Generada!",
                        f"{message}\n\n¿Desea abrir la constancia?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
                    )

                    if reply == QMessageBox.Yes and data and "ruta_archivo" in data:
                        open_file_with_default_app(data["ruta_archivo"])
                else:
                    QMessageBox.warning(self, "Error", message)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al generar constancia: {str(e)}")

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    window = AlumnoManagerWindow()
    window.show()
    sys.exit(app.exec_())
