"""
Visor de PDF para la aplicación
"""
import fitz  # PyMuPDF
import os
import sys
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

# Configurar el nivel de registro para PyMuPDF
fitz.TOOLS.mupdf_display_errors(False)  # Desactivar mensajes de error de MuPDF

# Función para suprimir salidas de consola
class SuppressOutput:
    """Clase para suprimir salidas a stdout y stderr"""
    def __init__(self):
        self.devnull = None
        self.old_stdout = None
        self.old_stderr = None

    def __enter__(self):
        self.devnull = open(os.devnull, "w")
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = self.devnull
        sys.stderr = self.devnull
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        if self.devnull:
            self.devnull.close()

class PDFViewer(QScrollArea):
    """Visor de PDF integrado en la aplicación"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0  # Zoom predeterminado al 100%
        self.zoom_step = 0.05   # Incremento de zoom más pequeño para cambios más graduales

        # Crear un widget principal que contendrá todo
        self.main_widget = QWidget(parent)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # Configurar el área de desplazamiento (este widget)
        self.setWidgetResizable(True)  # Cambiar a True para que el contenido se ajuste al área visible
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # Siempre mostrar barras de desplazamiento
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # No establecer un tamaño fijo para permitir que se adapte al espacio disponible
        # En su lugar, establecer un tamaño mínimo para evitar que se comprima demasiado
        self.setMinimumSize(400, 400)  # Tamaño mínimo para el visor

        # Contenedor para la página del PDF
        self.container = QWidget()
        self.container.setStyleSheet("background-color: white;")
        container_layout = QVBoxLayout(self.container)
        container_layout.setAlignment(Qt.AlignCenter)

        # Etiqueta para mostrar la página del PDF
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        container_layout.addWidget(self.page_label)

        # Establecer el widget del área de desplazamiento
        self.setWidget(self.container)

        # Crear controles de navegación y zoom
        self.setup_controls()

        # 🆕 REORGANIZAR LAYOUT: Área de visualización arriba, controles abajo
        self.main_layout.addWidget(self)  # Añadir el área de desplazamiento primero
        self.main_layout.addWidget(self.controls_widget)  # Controles abajo

    def setup_controls(self):
        """Configura los controles de navegación y zoom"""
        # Widget contenedor para los controles
        self.controls_widget = QWidget()
        controls_layout = QHBoxLayout(self.controls_widget)
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Botón página anterior
        self.prev_btn = QPushButton("◀ Anterior")
        self.prev_btn.setEnabled(False)
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)

        # Etiqueta de información de página
        self.page_info = QLabel("0 / 0")
        self.page_info.setAlignment(Qt.AlignCenter)
        self.page_info.setStyleSheet("font-weight: bold; color: #2C3E50; min-width: 60px;")

        # Botón página siguiente
        self.next_btn = QPushButton("Siguiente ▶")
        self.next_btn.setEnabled(False)
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)

        # Etiqueta de zoom
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("font-weight: bold; color: #2C3E50;")

        # Slider de zoom
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(25)  # 25%
        self.zoom_slider.setMaximum(300)  # 300%
        self.zoom_slider.setValue(100)  # 100% por defecto
        self.zoom_slider.setEnabled(False)
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        self.zoom_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #BDC3C7;
                height: 8px;
                background: #ECF0F1;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498DB;
                border: 1px solid #2980B9;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #2980B9;
            }
        """)

        # Etiqueta de porcentaje de zoom
        self.zoom_percentage = QLabel("100%")
        self.zoom_percentage.setStyleSheet("font-weight: bold; color: #2C3E50; min-width: 40px;")

        # Botones para ver PDF original y transformado (inicialmente ocultos)
        self.view_original_btn = QPushButton("📄 Ver Original")
        self.view_original_btn.setVisible(False)
        self.view_original_btn.setStyleSheet("""
            QPushButton {
                background-color: #E67E22;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #D35400;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)

        self.view_transformed_btn = QPushButton("🔄 Ver Transformado")
        self.view_transformed_btn.setVisible(False)
        self.view_transformed_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)

        # 🆕 OCULTAR BOTONES DE NAVEGACIÓN (no necesarios para un solo PDF)
        self.prev_btn.setVisible(False)
        self.next_btn.setVisible(False)
        self.page_info.setVisible(False)

        # 🆕 AÑADIR SOLO CONTROLES DE ZOOM Y VISTA (centrados)
        controls_layout.addStretch()  # Espacio flexible izquierdo
        controls_layout.addWidget(zoom_label)
        controls_layout.addWidget(self.zoom_slider)
        controls_layout.addWidget(self.zoom_percentage)
        controls_layout.addStretch()  # Espacio flexible central
        controls_layout.addWidget(self.view_original_btn)
        controls_layout.addWidget(self.view_transformed_btn)
        controls_layout.addStretch()  # Espacio flexible derecho

    def load_pdf(self, pdf_path, maintain_state=False, zoom=None, page=None):
        """
        Carga un archivo PDF

        Args:
            pdf_path: Ruta al archivo PDF
            maintain_state: Si se debe mantener el estado actual (zoom y página)
            zoom: Factor de zoom a aplicar (si maintain_state es True)
            page: Página a mostrar (si maintain_state es True)
        """
        try:
            # Guardar el estado actual si es necesario
            if maintain_state:
                current_zoom = zoom if zoom is not None else self.zoom_factor
                current_page = page if page is not None else self.current_page
            else:
                # Valores por defecto
                current_zoom = 1.0  # Zoom inicial al 100%
                current_page = 0

            # Usar el contexto para suprimir mensajes de consola
            with SuppressOutput():
                self.current_pdf = fitz.open(pdf_path)
                self.total_pages = len(self.current_pdf)

                # Establecer la página actual
                if maintain_state and current_page < self.total_pages:
                    self.current_page = current_page
                else:
                    self.current_page = 0

            # Establecer el factor de zoom
            self.zoom_factor = current_zoom

            # Actualizar el slider de zoom
            self.zoom_slider.setValue(int(self.zoom_factor * 100))

            # 🆕 SOLO HABILITAR CONTROLES DE ZOOM (botones de navegación están ocultos)
            self.zoom_slider.setEnabled(True)

            # 🆕 MANTENER FUNCIONALIDAD DE NAVEGACIÓN INTERNA (para PDFs multipágina)
            # pero sin mostrar los botones al usuario
            self.prev_btn.setEnabled(self.current_page > 0)
            self.next_btn.setEnabled(self.current_page < self.total_pages - 1)

            # Mostrar la página actual
            self.show_page(self.current_page)

            # Hacer visible el contenedor si estaba oculto
            self.page_label.setVisible(True)

            return True
        except Exception as e:
            print(f"Error al cargar PDF: {e}")
            return False

    def show_page(self, page_num):
        """Muestra una página específica del PDF"""
        if not self.current_pdf or page_num < 0 or page_num >= self.total_pages:
            return

        try:
            # Usar el contexto para suprimir mensajes de consola
            with SuppressOutput():
                # Obtener la página
                page = self.current_pdf.load_page(page_num)

                # Obtener el tamaño original de la página
                page_rect = page.rect
                page_width = page_rect.width
                page_height = page_rect.height

                # Obtener el tamaño del área de visualización
                viewport_width = self.viewport().width()

                # Calcular el zoom efectivo para que se ajuste al ancho del viewport
                # y luego aplicar el zoom del usuario
                fit_width_zoom = viewport_width / page_width
                effective_zoom = fit_width_zoom * self.zoom_factor

                # Crear la matriz de transformación
                mat = fitz.Matrix(effective_zoom, effective_zoom)

                # Renderizar la página como imagen
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")

                # Convertir a QImage y luego a QPixmap
                qimg = QImage.fromData(img_data)
                pixmap = QPixmap.fromImage(qimg)

                # Mostrar la imagen en la etiqueta
                self.page_label.setPixmap(pixmap)

                # Ajustar el tamaño del contenedor
                self.container.setFixedSize(pixmap.size())

            # Actualizar información de página
            self.page_info.setText(f"{page_num + 1} / {self.total_pages}")

            # Actualizar página actual
            self.current_page = page_num

            # Actualizar estado de los botones
            self.prev_btn.setEnabled(page_num > 0)
            self.next_btn.setEnabled(page_num < self.total_pages - 1)

            # Actualizar estado del slider de zoom
            self.zoom_slider.setEnabled(True)

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

    def on_zoom_slider_changed(self, value):
        """Maneja el cambio en el slider de zoom"""
        self.zoom_factor = value / 100.0
        self.zoom_percentage.setText(f"{value}%")

        # Volver a mostrar la página actual con el nuevo zoom
        if self.current_pdf:
            self.show_page(self.current_page)

    def close_pdf(self):
        """Cierra el PDF actual"""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None

        # Limpiar la vista
        self.page_label.clear()
        self.page_label.setVisible(False)

        # Restablecer controles
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0
        self.page_info.setText("0 / 0")
        self.zoom_slider.setValue(100)
        self.zoom_percentage.setText("100%")

        # 🆕 DESHABILITAR SOLO CONTROLES VISIBLES
        self.zoom_slider.setEnabled(False)

        # 🆕 MANTENER ESTADO DE BOTONES OCULTOS
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
