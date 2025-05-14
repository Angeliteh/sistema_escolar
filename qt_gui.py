import sys
import os
import platform
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QFormLayout, QLineEdit,
    QScrollArea, QTabWidget,
    QGridLayout, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QColor, QPalette, QIcon

# Para el visor de PDF
import fitz  # PyMuPDF

from pdf_extractor import PDFExtractor
from pdf_generator import PDFGenerator
from PIL import Image

class SelectionCard(QFrame):
    """Tarjeta de selección para tipos de constancia"""
    clicked = pyqtSignal()

    def __init__(self, title, description, requires_grades=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.requires_grades = requires_grades
        self.is_selected = False
        self.is_enabled = True
        self.value = ""

        # Configurar apariencia
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(100)  # Altura suficiente para el contenido
        self.setMinimumWidth(200)   # Ancho mínimo para legibilidad

        # Layout con márgenes adecuados
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)  # Márgenes para legibilidad
        layout.setSpacing(6)  # Espacio adecuado entre elementos

        # Crear una única etiqueta con todo el contenido usando HTML
        html_content = f"""
            <div style="text-align: center;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px;">{title}</div>
                <div style="color: #555; font-size: 12px; margin-bottom: 6px;">{description}</div>
                {"<div style='color: #e74c3c; font-style: italic; font-size: 11px;'>Requiere calificaciones</div>" if requires_grades else ""}
            </div>
        """

        self.content_label = QLabel()
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setTextInteractionFlags(Qt.NoTextInteraction)  # No seleccionable
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setText(html_content)

        # Asegurarse de que el texto se ajuste correctamente
        self.content_label.setWordWrap(True)

        # Agregar la etiqueta al layout
        layout.addWidget(self.content_label)

        # Aplicar estilo inicial
        self.update_style()

        # Instalar filtro de eventos para capturar eventos de los hijos
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Filtro de eventos para capturar clics en los hijos y evitar selección de texto"""
        # Capturar clics del mouse
        if event.type() == event.MouseButtonPress:
            # Emitir señal de clic si está habilitado y es botón izquierdo
            if event.button() == Qt.LeftButton and self.is_enabled:
                self.clicked.emit()
            return True

        # Capturar eventos de selección de texto
        elif event.type() == event.MouseMove:
            return True  # Bloquear movimiento del mouse para evitar selección

        # Capturar eventos de teclado para evitar copiar/pegar
        elif event.type() in [event.KeyPress, event.KeyRelease]:
            return True

        return super().eventFilter(obj, event)

    def update_style(self):
        """Actualiza el estilo según el estado"""
        if not self.is_enabled:
            # Estilo para tarjeta deshabilitada
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: #f5f5f5;
                    padding: 10px;
                    opacity: 0.7;
                }
            """)

            # Actualizar el HTML con colores deshabilitados
            html_content = f"""
                <div style="text-align: center;">
                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #999;">{self.title}</div>
                    <div style="color: #999; font-size: 12px; margin-bottom: 6px;">{self.description}</div>
                    {"<div style='color: #999; font-style: italic; font-size: 11px;'>Requiere calificaciones</div>" if self.requires_grades else ""}
                </div>
            """
            self.content_label.setText(html_content)

        elif self.is_selected:
            # Estilo para tarjeta seleccionada - más destacada
            self.setStyleSheet("""
                QFrame {
                    border: 3px solid #2980b9;
                    border-radius: 8px;
                    background-color: #d6eaf8;
                    padding: 10px;
                }
            """)

            # HTML con colores más vivos para la selección
            html_content = f"""
                <div style="text-align: center;">
                    <div style="font-weight: bold; font-size: 15px; margin-bottom: 8px; color: #2c3e50;">{self.title}</div>
                    <div style="color: #34495e; font-size: 12px; margin-bottom: 6px;">{self.description}</div>
                    {"<div style='color: #c0392b; font-weight: bold; font-style: italic; font-size: 11px;'>Requiere calificaciones</div>" if self.requires_grades else ""}
                </div>
            """
            self.content_label.setText(html_content)

        else:
            # Estilo para tarjeta normal con mejor hover
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    background-color: white;
                    padding: 10px;
                }
                QFrame:hover {
                    border-color: #3498db;
                    background-color: #f8f9fa;
                }
            """)

            # HTML normal
            html_content = f"""
                <div style="text-align: center;">
                    <div style="font-weight: bold; font-size: 14px; margin-bottom: 8px; color: #2c3e50;">{self.title}</div>
                    <div style="color: #34495e; font-size: 12px; margin-bottom: 6px;">{self.description}</div>
                    {"<div style='color: #e74c3c; font-style: italic; font-size: 11px;'>Requiere calificaciones</div>" if self.requires_grades else ""}
                </div>
            """
            self.content_label.setText(html_content)

    def set_selected(self, selected):
        """Establece si la tarjeta está seleccionada"""
        self.is_selected = selected
        self.update_style()

    def set_enabled(self, enabled):
        """Establece si la tarjeta está habilitada"""
        self.is_enabled = enabled
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ForbiddenCursor)
        self.update_style()

    def mousePressEvent(self, event):
        """Maneja el clic en la tarjeta"""
        if self.is_enabled and event.button() == Qt.LeftButton:
            self.clicked.emit()

class PDFViewer(QScrollArea):
    """Visor de PDF integrado en la aplicación"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0

        # Configurar el área de desplazamiento
        self.setWidgetResizable(True)

        # Contenedor principal
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)

        # Área para mostrar la página del PDF
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("background-color: white;")

        # Controles de navegación
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Anterior")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)

        self.page_info = QLabel("Página 0 de 0")
        self.page_info.setAlignment(Qt.AlignCenter)

        self.next_btn = QPushButton("Siguiente")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_info)
        nav_layout.addWidget(self.next_btn)

        # Agregar widgets al layout
        self.layout.addWidget(self.page_label)
        self.layout.addLayout(nav_layout)

        # Establecer el widget contenedor
        self.setWidget(self.container)

    def load_pdf(self, pdf_path):
        """Carga un archivo PDF"""
        try:
            self.current_pdf = fitz.open(pdf_path)
            self.total_pages = len(self.current_pdf)
            self.current_page = 0

            # Habilitar/deshabilitar botones según corresponda
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(self.total_pages > 1)

            # Mostrar la primera página
            self.show_page(0)

            return True
        except Exception as e:
            print(f"Error al cargar PDF: {e}")
            return False

    def show_page(self, page_num):
        """Muestra una página específica del PDF"""
        if not self.current_pdf or page_num < 0 or page_num >= self.total_pages:
            return

        try:
            # Obtener la página
            page = self.current_pdf.load_page(page_num)

            # Renderizar la página a una imagen
            zoom = 1.5  # Factor de zoom para mejor calidad
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)

            # Convertir a QPixmap
            img_data = pix.tobytes("ppm")
            qimg = QPixmap()
            qimg.loadFromData(img_data)

            # Mostrar en el QLabel
            self.page_label.setPixmap(qimg)

            # Actualizar información de página
            self.page_info.setText(f"Página {page_num + 1} de {self.total_pages}")

            # Actualizar página actual
            self.current_page = page_num

            # Actualizar estado de los botones
            self.prev_btn.setEnabled(page_num > 0)
            self.next_btn.setEnabled(page_num < self.total_pages - 1)

        except Exception as e:
            print(f"Error al mostrar página: {e}")

    def next_page(self):
        """Avanza a la siguiente página"""
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)

    def previous_page(self):
        """Retrocede a la página anterior"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def close_pdf(self):
        """Cierra el PDF actual"""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None
            self.current_page = 0
            self.total_pages = 0
            self.page_label.clear()
            self.page_info.setText("Página 0 de 0")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)

class ConstanciasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Constancias Escolares")
        self.setMinimumSize(1200, 800)  # Aumentamos el tamaño mínimo de la ventana

        # Variables para almacenar datos
        self.pdf_path = None
        self.datos_alumno = None
        self.tiene_calificaciones = False
        self.tiene_foto = False
        self.foto_path = None

        # Configurar la interfaz
        self.setup_ui()

        # Configurar la barra de estado
        self.statusBar().showMessage("Listo")

    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Título con mejor estilo
        title_label = QLabel("Sistema de Constancias Escolares")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 15px;
            color: #2c3e50;
            padding: 10px;
            border-bottom: 2px solid #3498db;
        """)
        main_layout.addWidget(title_label)

        # Sección de carga de PDF
        self.setup_pdf_loader(main_layout)

        # Contenedor principal con pestañas
        self.tabs = QTabWidget()

        # Pestaña de datos
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        self.setup_student_data(data_layout)
        self.tabs.addTab(data_tab, "Datos del Alumno")

        # Pestaña de generación
        generation_tab = QWidget()
        generation_layout = QVBoxLayout(generation_tab)
        self.setup_certificate_options(generation_layout)
        self.tabs.addTab(generation_tab, "Generar Constancia")

        # Crear pestaña de vista previa con el visor de PDF
        preview_tab = QWidget()
        preview_layout = QVBoxLayout(preview_tab)
        self.pdf_viewer = PDFViewer()
        preview_layout.addWidget(self.pdf_viewer)
        self.tabs.addTab(preview_tab, "Vista Previa")

        main_layout.addWidget(self.tabs)

    def setup_pdf_loader(self, parent_layout):
        # Crear un panel compacto para cargar archivos
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f8f8f8;
                padding: 8px;
                margin-bottom: 10px;
            }
        """)

        # Layout horizontal para el panel
        panel_layout = QHBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(15)

        # Botón para cargar PDF
        load_btn = QPushButton("Cargar Constancia")
        load_btn.setIcon(QIcon.fromTheme("document-open"))
        load_btn.setMinimumHeight(36)
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_btn.clicked.connect(self.open_file_dialog)
        panel_layout.addWidget(load_btn)

        # Separador vertical
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ddd;")
        panel_layout.addWidget(separator)

        # Información del archivo
        file_info = QHBoxLayout()
        file_icon = QLabel("📄")
        file_icon.setStyleSheet("font-size: 18px; color: #3498db;")
        self.file_label = QLabel("Ningún archivo seleccionado")
        self.file_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 13px;")

        file_info.addWidget(file_icon)
        file_info.addWidget(self.file_label)
        file_info.addStretch()

        panel_layout.addLayout(file_info, 3)

        # Indicadores de estado
        status_layout = QHBoxLayout()

        # Indicador de foto
        photo_box = QHBoxLayout()
        photo_icon = QLabel("🖼️")
        photo_icon.setStyleSheet("font-size: 18px; color: #e74c3c;")
        self.photo_indicator = QLabel("Foto: No")
        self.photo_indicator.setStyleSheet("color: #7f8c8d; font-size: 12px;")

        photo_box.addWidget(photo_icon)
        photo_box.addWidget(self.photo_indicator)
        status_layout.addLayout(photo_box)

        status_layout.addSpacing(15)

        # Indicador de calificaciones
        grades_box = QHBoxLayout()
        grades_icon = QLabel("📊")
        grades_icon.setStyleSheet("font-size: 18px; color: #2ecc71;")
        self.grades_indicator = QLabel("Calificaciones: No")
        self.grades_indicator.setStyleSheet("color: #7f8c8d; font-size: 12px;")

        grades_box.addWidget(grades_icon)
        grades_box.addWidget(self.grades_indicator)
        status_layout.addLayout(grades_box)

        panel_layout.addLayout(status_layout, 2)

        # Agregar el panel al layout principal
        parent_layout.addWidget(panel)

    def open_file_dialog(self):
        """Abre un diálogo para seleccionar un archivo PDF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Constancia PDF", "", "Archivos PDF (*.pdf);;Todos los archivos (*)"
        )
        if file_path:
            self.load_pdf(file_path)

    def setup_student_data(self, parent_layout):
        # Crear un área de scroll para contener los datos del alumno
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setMaximumHeight(250)  # Limitar altura para no interferir con calificaciones

        # Widget contenedor para el scroll
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Layout para datos y foto
        data_layout = QHBoxLayout()
        data_layout.setSpacing(10)

        # Formulario de datos
        form_group = QGroupBox("Información del Alumno")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(8)

        # Campos de datos
        self.data_fields = {}
        fields = [
            ("nombre", "Nombre:"),
            ("curp", "CURP:"),
            ("matricula", "Matrícula:"),
            ("grado", "Grado:"),
            ("grupo", "Grupo:"),
            ("turno", "Turno:"),
            ("nacimiento", "Fecha de Nacimiento:")
        ]

        for field_id, label in fields:
            field = QLineEdit()
            field.setReadOnly(True)
            field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #f9f9f9;
                }
            """)
            form_layout.addRow(label, field)
            self.data_fields[field_id] = field

        data_layout.addWidget(form_group, 3)

        # Foto del alumno
        photo_group = QGroupBox("Foto")
        photo_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 5px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        photo_layout = QVBoxLayout(photo_group)

        self.photo_label = QLabel("Sin foto")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setMinimumSize(150, 180)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
        """)

        photo_layout.addWidget(self.photo_label)
        data_layout.addWidget(photo_group, 1)

        # Añadir el layout de datos al contenido del scroll
        scroll_layout.addLayout(data_layout)

        # Configurar el área de scroll
        scroll_area.setWidget(scroll_content)
        parent_layout.addWidget(scroll_area)

        # Tabla de calificaciones
        grades_group = QGroupBox("Calificaciones")
        grades_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        grades_layout = QVBoxLayout(grades_group)

        # Aumentamos el tamaño mínimo del grupo de calificaciones
        grades_group.setMinimumHeight(250)

        self.grades_table = QTableWidget(0, 5)
        self.grades_table.setHorizontalHeaderLabels(["Materia", "Periodo 1", "Periodo 2", "Periodo 3", "Promedio"])
        self.grades_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.grades_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.grades_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.grades_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.grades_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # Aumentamos el tamaño de las filas y mejoramos el estilo
        self.grades_table.verticalHeader().setDefaultSectionSize(30)  # Altura de las filas
        self.grades_table.setAlternatingRowColors(True)  # Filas alternadas para mejor legibilidad

        self.grades_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #e0e0e0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e8f4fc;
                color: #000;
            }
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)

        grades_layout.addWidget(self.grades_table)

        parent_layout.addWidget(grades_group)

    def setup_certificate_options(self, parent_layout):
        # Opciones de constancia
        options_group = QGroupBox("Tipo de Constancia")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        options_layout = QHBoxLayout(options_group)
        options_layout.setSpacing(15)  # Más espacio entre tarjetas
        options_layout.setContentsMargins(15, 20, 15, 15)  # Márgenes para el grupo

        # Definir tipos de constancias
        types = [
            ("estudio", "Constancia de Estudios", "Constancia básica con datos del alumno", False),
            ("calificaciones", "Constancia con Calificaciones", "Incluye calificaciones del alumno", True),
            ("traslado", "Constancia de Traslado", "Para traslado a otra institución", True)
        ]

        # Crear tarjetas de selección
        self.cert_cards = []
        self.selected_cert_type = "estudio"  # Valor predeterminado

        for value, title, description, requires_grades in types:
            card = SelectionCard(title, description, requires_grades)
            card.value = value

            # Seleccionar la primera tarjeta por defecto
            if value == "estudio":
                card.set_selected(True)

            # Conectar señal de clic
            card.clicked.connect(lambda c=card: self.on_card_selected(c))

            # Agregar a la cuadrícula con proporción igual
            options_layout.addWidget(card, 1)  # Proporción 1 para todas las tarjetas
            self.cert_cards.append(card)

            # Guardar referencias a tarjetas específicas
            if value == "calificaciones":
                self.grades_card = card
            elif value == "traslado":
                self.transfer_card = card

        parent_layout.addWidget(options_group)

        # Espacio para instrucciones
        info_group = QGroupBox("Instrucciones")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        info_layout = QVBoxLayout(info_group)

        # Texto de instrucciones
        instructions = QLabel(
            "1. Seleccione el tipo de constancia que desea generar.\n"
            "2. Haga clic en 'Vista Previa' para ver cómo quedará la constancia.\n"
            "3. Si está conforme, haga clic en 'Generar Constancia' para crear el PDF final."
        )
        instructions.setStyleSheet("color: #555; padding: 10px;")
        instructions.setWordWrap(True)
        info_layout.addWidget(instructions)

        parent_layout.addWidget(info_group)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Botón de vista previa
        self.preview_btn = QPushButton("Actualizar Vista Previa")
        self.preview_btn.setEnabled(False)
        self.preview_btn.setMinimumHeight(30)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        self.preview_btn.clicked.connect(self.update_preview)
        buttons_layout.addWidget(self.preview_btn)

        # Botón de generar constancia
        self.generate_btn = QPushButton("Generar Constancia")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setMinimumHeight(30)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #999;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_certificate)
        buttons_layout.addWidget(self.generate_btn)

        # Botón de limpiar
        reset_btn = QPushButton("Limpiar")
        reset_btn.setMinimumHeight(30)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        reset_btn.clicked.connect(self.reset)
        buttons_layout.addWidget(reset_btn)

        parent_layout.addLayout(buttons_layout)

    def on_card_selected(self, selected_card):
        """Maneja la selección de una tarjeta de tipo de constancia"""
        # Deseleccionar todas las tarjetas
        for card in self.cert_cards:
            card.set_selected(False)

        # Seleccionar la tarjeta clickeada
        selected_card.set_selected(True)
        self.selected_cert_type = selected_card.value



    def load_pdf(self, file_path):
        """Carga un archivo PDF y extrae sus datos"""
        self.pdf_path = file_path
        self.file_label.setText(os.path.basename(file_path))
        self.statusBar().showMessage(f"Cargando datos de {os.path.basename(file_path)}...")

        try:
            # Extraer datos del PDF
            self.extractor = PDFExtractor(file_path)

            # Preguntar si desea incluir foto
            include_photo = QMessageBox.question(
                self, "Incluir Foto",
                "¿Desea incluir la foto del alumno en la constancia?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            ) == QMessageBox.Yes

            # Extraer datos básicos primero (sin foto)
            self.datos_alumno = self.extractor.extraer_todos_datos(False)
            self.tiene_calificaciones = self.datos_alumno.get("tiene_calificaciones", False)
            self.tiene_foto = False
            self.foto_path = None

            # Actualizar UI con datos básicos
            self.update_ui_with_data()

            # Habilitar botones
            self.generate_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)

            # Si se solicitó incluir foto, mostrar las imágenes disponibles
            if include_photo:
                self.extract_images_for_selection()
            else:
                self.statusBar().showMessage("Datos cargados correctamente (sin foto)")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar el PDF: {str(e)}")
            self.statusBar().showMessage("Error al cargar el PDF")

    def extract_images_for_selection(self):
        """Extrae las imágenes del PDF y las muestra para selección"""
        try:
            # Crear directorio temporal para imágenes extraídas
            temp_dir = "temp_images"
            os.makedirs(temp_dir, exist_ok=True)

            # Extraer todas las imágenes del PDF
            imagenes_extraidas = self.extractor._extraer_todas_imagenes(temp_dir)

            if not imagenes_extraidas:
                QMessageBox.information(self, "Información", "No se encontraron imágenes en el PDF.")
                self.statusBar().showMessage("Datos cargados correctamente (sin foto)")
                return

            # Crear una ventana para mostrar las imágenes
            self.create_image_selection_window(imagenes_extraidas)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al extraer imágenes: {str(e)}")
            self.statusBar().showMessage("Error al extraer imágenes")

    def create_image_selection_window(self, images):
        """Crea una ventana para seleccionar la foto del alumno"""
        # Crear una ventana flotante
        self.image_window = QDialog(self)
        self.image_window.setWindowTitle("Seleccionar Foto del Alumno")
        self.image_window.setMinimumSize(600, 400)

        # Layout principal
        layout = QVBoxLayout(self.image_window)

        # Instrucciones
        label = QLabel("Seleccione la foto del alumno:")
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(label)

        # Área de scroll para las imágenes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout(content)

        # Crear grid para las imágenes
        row, col = 0, 0
        max_cols = 3

        for i, img_path in enumerate(images):
            try:
                # Crear frame para cada imagen
                frame = QFrame()
                frame.setFrameShape(QFrame.StyledPanel)
                frame.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; padding: 5px;")
                frame_layout = QVBoxLayout(frame)

                # Cargar y mostrar imagen
                pixmap = QPixmap(img_path)
                pixmap = pixmap.scaled(120, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)

                # Botón de selección
                select_btn = QPushButton(f"Imagen {i+1}")
                # Usar una función normal en lugar de lambda para evitar problemas
                select_btn.setProperty("img_path", img_path)
                select_btn.clicked.connect(self.on_image_selected)

                frame_layout.addWidget(image_label)
                frame_layout.addWidget(select_btn)

                grid.addWidget(frame, row, col)

                # Actualizar posición en el grid
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            except Exception as e:
                print(f"Error al cargar imagen {img_path}: {e}")

        # Opción para no seleccionar ninguna foto
        no_photo_frame = QFrame()
        no_photo_frame.setFrameShape(QFrame.StyledPanel)
        no_photo_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; padding: 5px;")
        no_photo_layout = QVBoxLayout(no_photo_frame)

        no_photo_label = QLabel("Sin foto")
        no_photo_label.setAlignment(Qt.AlignCenter)
        no_photo_label.setStyleSheet("font-size: 14px; color: #777;")

        no_photo_btn = QPushButton("No usar foto")
        no_photo_btn.clicked.connect(self.on_no_photo)

        no_photo_layout.addWidget(no_photo_label)
        no_photo_layout.addWidget(no_photo_btn)

        grid.addWidget(no_photo_frame, row+1, 0, 1, max_cols)

        content.setLayout(grid)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Botones de acción
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.on_no_photo)
        layout.addWidget(buttons)

        # Mostrar la ventana
        self.image_window.show()

    def on_image_selected(self):
        """Maneja la selección de una imagen"""
        sender = self.sender()
        photo_path = sender.property("img_path")

        if photo_path:
            self.process_selected_photo(photo_path)

        # Cerrar la ventana de selección
        self.image_window.close()

    def on_no_photo(self):
        """Maneja la opción de no usar foto"""
        # Cerrar la ventana de selección
        self.image_window.close()
        self.statusBar().showMessage("Datos cargados correctamente (sin foto)")

    def process_selected_photo(self, photo_path):
        """Procesa la foto seleccionada"""
        try:
            # Crear directorio de fotos si no existe
            fotos_dir = "fotos"
            os.makedirs(fotos_dir, exist_ok=True)

            # Obtener el CURP del alumno
            curp = self.datos_alumno.get("curp", "")

            if not curp:
                # Si no hay CURP, usar un nombre basado en el nombre del archivo
                base_name = os.path.basename(self.pdf_path)
                curp = os.path.splitext(base_name)[0]

            # Ruta donde se guardará la foto final
            img_path = os.path.join(fotos_dir, f"{curp}.jpg")

            # Copiar la imagen seleccionada
            try:
                # Método 1: Leer y escribir el contenido del archivo
                with open(photo_path, 'rb') as src_file:
                    contenido = src_file.read()

                with open(img_path, 'wb') as dst_file:
                    dst_file.write(contenido)

                print(f"Imagen copiada exitosamente a {img_path}")
            except Exception as e:
                print(f"Error al copiar imagen: {e}")
                # Intentar con PIL
                try:
                    img = Image.open(photo_path)
                    img.save(img_path, format="JPEG")
                    print(f"Imagen copiada con PIL a {img_path}")
                except Exception as e2:
                    print(f"Error al copiar con PIL: {e2}")
                    raise e2

            # Actualizar datos con la foto
            self.datos_alumno["foto_path"] = img_path
            self.datos_alumno["has_photo"] = True
            self.tiene_foto = True
            self.foto_path = img_path

            # Actualizar UI
            self.update_ui_with_data()

            # Actualizar estado
            self.statusBar().showMessage("Datos cargados correctamente (con foto)")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar la foto: {str(e)}")
            self.statusBar().showMessage("Error al procesar la foto")

    def update_ui_with_data(self):
        """Actualiza la interfaz con los datos extraídos"""
        # Actualizar indicadores
        self.photo_indicator.setText(f"Foto: {'Sí' if self.tiene_foto else 'No'}")
        self.grades_indicator.setText(f"Calificaciones: {'Sí' if self.tiene_calificaciones else 'No'}")

        # Actualizar campos de datos
        self.data_fields["nombre"].setText(self.datos_alumno.get("nombre", ""))
        self.data_fields["curp"].setText(self.datos_alumno.get("curp", ""))
        self.data_fields["matricula"].setText(self.datos_alumno.get("matricula", ""))
        self.data_fields["grado"].setText(self.datos_alumno.get("grado", ""))
        self.data_fields["grupo"].setText(self.datos_alumno.get("grupo", ""))
        self.data_fields["turno"].setText(self.datos_alumno.get("turno", ""))
        self.data_fields["nacimiento"].setText(self.datos_alumno.get("nacimiento", ""))

        # Actualizar foto si está disponible
        if self.tiene_foto and self.foto_path:
            try:
                pixmap = QPixmap(self.foto_path)
                pixmap = pixmap.scaled(150, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(pixmap)
            except Exception as e:
                print(f"Error al mostrar foto: {e}")
                self.photo_label.setText("Error al cargar foto")
        else:
            self.photo_label.setText("Sin foto")
            self.photo_label.setPixmap(QPixmap())

        # Actualizar tabla de calificaciones
        self.update_grades_table()

        # Habilitar/deshabilitar opciones según datos disponibles
        self.update_certificate_options()

        # No actualizamos la vista previa aquí para evitar bucles infinitos
        # La vista previa se actualizará cuando el usuario haga clic en el botón correspondiente

    def update_grades_table(self):
        """Actualiza la tabla de calificaciones"""
        # Limpiar tabla
        self.grades_table.setRowCount(0)

        # Si hay calificaciones, agregarlas a la tabla
        if self.tiene_calificaciones and "calificaciones" in self.datos_alumno:
            calificaciones = self.datos_alumno["calificaciones"]
            self.grades_table.setRowCount(len(calificaciones))

            for i, materia in enumerate(calificaciones):
                self.grades_table.setItem(i, 0, QTableWidgetItem(materia["nombre"]))
                self.grades_table.setItem(i, 1, QTableWidgetItem(str(materia["i"])))
                self.grades_table.setItem(i, 2, QTableWidgetItem(str(materia["ii"])))
                self.grades_table.setItem(i, 3, QTableWidgetItem(str(materia["iii"])))
                self.grades_table.setItem(i, 4, QTableWidgetItem(str(materia["promedio"])))

    def update_certificate_options(self):
        """Actualiza las opciones de constancia según los datos disponibles"""
        # Si no hay calificaciones, deshabilitar opciones que las requieren
        if not self.tiene_calificaciones:
            # Deshabilitar constancia de calificaciones
            self.grades_card.set_enabled(False)

            # Deshabilitar constancia de traslado (también requiere calificaciones)
            self.transfer_card.set_enabled(False)

            # Si la opción actual es calificaciones o traslado, cambiar a estudios
            if self.selected_cert_type in ["calificaciones", "traslado"]:
                # Deseleccionar todas las tarjetas
                for card in self.cert_cards:
                    card.set_selected(False)

                # Seleccionar la tarjeta de estudios
                for card in self.cert_cards:
                    if card.value == "estudio":
                        card.set_selected(True)
                        self.selected_cert_type = "estudio"
                        break
        else:
            # Habilitar todas las opciones
            self.grades_card.set_enabled(True)
            self.transfer_card.set_enabled(True)

    def update_preview(self):
        """Genera un PDF temporal y lo muestra en el visor integrado"""
        if not self.datos_alumno:
            return

        try:
            # Obtener tipo de constancia seleccionado
            cert_type = self.selected_cert_type

            # Verificar si se puede generar el tipo seleccionado
            if cert_type in ["calificaciones", "traslado"] and not self.tiene_calificaciones:
                QMessageBox.warning(self, "Advertencia", f"No se puede generar constancia de {cert_type} sin calificaciones")
                return

            # Asegurarse de que no haya calificaciones en constancias que no deben tenerlas
            datos_a_usar = self.datos_alumno.copy()
            if cert_type == "estudio":
                datos_a_usar["mostrar_calificaciones"] = False
                datos_a_usar["calificaciones"] = []
            elif cert_type in ["calificaciones", "traslado"]:
                datos_a_usar["mostrar_calificaciones"] = True

            # Crear directorio temporal si no existe
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)

            # Generar un nombre de archivo temporal para la vista previa
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"preview_{cert_type}_{timestamp}.pdf"
            preview_path = os.path.join(temp_dir, preview_filename)

            # Generar el PDF temporal
            generator = PDFGenerator()
            output_path = generator.generar_constancia(cert_type, datos_a_usar, preview_path)

            # Mostrar mensaje informativo
            self.statusBar().showMessage(f"Vista previa generada: {output_path}")

            # Cargar el PDF en el visor
            if self.pdf_viewer.load_pdf(output_path):
                # Cambiar a la pestaña de vista previa
                self.tabs.setCurrentIndex(2)  # Índice de la pestaña de vista previa
            else:
                # Si falla, intentar abrir con el visor predeterminado del sistema
                QMessageBox.warning(self, "Advertencia", "No se pudo cargar el PDF en el visor integrado. Se abrirá con el visor predeterminado.")
                if platform.system() == 'Windows':
                    os.startfile(output_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', output_path))
                else:  # Linux
                    subprocess.call(('xdg-open', output_path))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar vista previa: {str(e)}")
            self.statusBar().showMessage("Error al generar vista previa")

    def generate_certificate(self, cert_type=None):
        """Genera la constancia seleccionada"""
        if not self.datos_alumno:
            return

        try:
            # Si no se especificó un tipo, obtener el seleccionado en la interfaz
            if cert_type is None:
                cert_type = self.selected_cert_type

            # Verificar si se puede generar el tipo seleccionado
            if cert_type in ["calificaciones", "traslado"] and not self.tiene_calificaciones:
                QMessageBox.warning(self, "Advertencia", f"No se puede generar constancia de {cert_type} sin calificaciones")
                return

            # Generar constancia
            generator = PDFGenerator()

            # Asegurarse de que no haya calificaciones en constancias que no deben tenerlas
            datos_a_usar = self.datos_alumno.copy()
            if cert_type == "estudio":
                datos_a_usar["mostrar_calificaciones"] = False
                datos_a_usar["calificaciones"] = []
            elif cert_type in ["calificaciones", "traslado"]:
                datos_a_usar["mostrar_calificaciones"] = True

            # Generar la constancia con los datos adecuados
            output_path = generator.generar_constancia(cert_type, datos_a_usar)

            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Éxito", f"Constancia generada correctamente: {output_path}")

            # Preguntar si desea abrir la constancia
            if QMessageBox.question(
                self, "Abrir Constancia",
                "¿Desea abrir la constancia generada?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            ) == QMessageBox.Yes:
                if platform.system() == 'Windows':
                    os.startfile(output_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', output_path))
                else:  # Linux
                    subprocess.call(('xdg-open', output_path))

            self.statusBar().showMessage("Constancia generada correctamente")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar constancia: {str(e)}")
            self.statusBar().showMessage("Error al generar constancia")

    def reset(self):
        """Reinicia la aplicación"""
        # Confirmar acción
        if QMessageBox.question(
            self, "Confirmar",
            "¿Está seguro de que desea limpiar todos los datos?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        ) != QMessageBox.Yes:
            return

        # Reiniciar variables
        self.pdf_path = None
        self.datos_alumno = None
        self.tiene_calificaciones = False
        self.tiene_foto = False
        self.foto_path = None

        # Reiniciar UI
        self.file_label.setText("Ningún archivo seleccionado")
        self.photo_indicator.setText("Foto: No")
        self.grades_indicator.setText("Calificaciones: No")

        # Limpiar campos de datos
        for field in self.data_fields.values():
            field.clear()

        # Limpiar tabla de calificaciones
        self.grades_table.setRowCount(0)

        # Limpiar foto
        self.photo_label.setText("Sin foto")
        self.photo_label.setPixmap(QPixmap())

        # Deshabilitar botones
        self.generate_btn.setEnabled(False)
        self.preview_btn.setEnabled(False)

        # Habilitar todas las opciones de constancia
        for card in self.cert_cards:
            card.set_enabled(True)
            card.set_selected(card.value == "estudio")

        # Reiniciar tipo de constancia seleccionado
        self.selected_cert_type = "estudio"

        # No es necesario limpiar la vista previa ya que ahora se muestra en una ventana separada

        # Actualizar estado
        self.statusBar().showMessage("Datos limpiados")

# Iniciar la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Establecer estilo global
    app.setStyle("Fusion")

    # Aplicar paleta de colores moderna
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = ConstanciasApp()
    window.show()
    sys.exit(app.exec_())
