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

        # Layout para la página del PDF
        self.page_layout = QVBoxLayout(self.container)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.setAlignment(Qt.AlignCenter)

        # Área para mostrar la página del PDF
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumSize(300, 400)  # Tamaño mínimo para evitar que sea demasiado pequeño

        # Añadir el label al contenedor
        self.page_layout.addWidget(self.page_label)

        # Establecer el widget del área de desplazamiento
        self.setWidget(self.container)

        # Crear controles de navegación y zoom (fuera del área de desplazamiento)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(5, 5, 5, 5)

        # Botones de navegación
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setToolTip("Página anterior")
        self.prev_btn.clicked.connect(self.previous_page)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setFixedWidth(40)
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                border-radius: 4px;
                border: 1px solid #2C4F7C;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2C4F7C;
            }
            QPushButton:disabled {
                background-color: #16213E;
                color: #555555;
            }
        """)

        self.page_info = QLabel("Página 0 de 0")
        self.page_info.setAlignment(Qt.AlignCenter)
        self.page_info.setStyleSheet("color: white; font-size: 12px;")
        self.page_info.setMinimumWidth(100)

        self.next_btn = QPushButton("▶")
        self.next_btn.setToolTip("Página siguiente")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setEnabled(False)
        self.next_btn.setFixedWidth(40)
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #1E3A5F;
                color: white;
                border-radius: 4px;
                border: 1px solid #2C4F7C;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2C4F7C;
            }
            QPushButton:disabled {
                background-color: #16213E;
                color: #555555;
            }
        """)

        # Controles de zoom con slider
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: white; font-size: 12px;")

        self.zoom_info = QLabel("100%")
        self.zoom_info.setAlignment(Qt.AlignCenter)
        self.zoom_info.setStyleSheet("color: white; font-size: 12px;")
        self.zoom_info.setFixedWidth(50)

        # Crear slider para zoom
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(20, 300)  # 20% a 300%
        self.zoom_slider.setValue(100)      # Valor inicial 100%
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(25)  # Marcas más frecuentes
        self.zoom_slider.setFixedWidth(150)
        self.zoom_slider.setSingleStep(5)     # Paso más pequeño para movimientos más graduales
        self.zoom_slider.setPageStep(25)      # Paso de página más pequeño
        self.zoom_slider.valueChanged.connect(self.on_zoom_slider_changed)
        self.zoom_slider.setStyleSheet("""
            QSlider {
                height: 20px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #2C4F7C;
                height: 8px;
                background: #16213E;
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

        # Crear botón para ver el PDF original
        self.view_original_btn = QPushButton("📄 Original")
        self.view_original_btn.setToolTip("Ver el PDF original")
        self.view_original_btn.setCursor(Qt.PointingHandCursor)
        self.view_original_btn.setFixedWidth(100)
        self.view_original_btn.setVisible(False)  # Oculto por defecto
        self.view_original_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 4px;
                border: 1px solid #2980B9;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)

        # Crear botón para ver el PDF transformado
        self.view_transformed_btn = QPushButton("🔄 Transformado")
        self.view_transformed_btn.setToolTip("Ver el PDF transformado")
        self.view_transformed_btn.setCursor(Qt.PointingHandCursor)
        self.view_transformed_btn.setFixedWidth(120)
        self.view_transformed_btn.setVisible(False)  # Oculto por defecto
        self.view_transformed_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border-radius: 4px;
                border: 1px solid #8E44AD;
                padding: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #8E44AD;
            }
            QPushButton:pressed {
                background-color: #7D3C98;
            }
        """)

        # Añadir widgets al layout de controles
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addWidget(self.page_info)
        controls_layout.addWidget(self.next_btn)

        # Añadir botones para ver PDF original y transformado
        controls_layout.addWidget(self.view_original_btn)
        controls_layout.addWidget(self.view_transformed_btn)

        controls_layout.addStretch()
        controls_layout.addWidget(zoom_label)
        controls_layout.addWidget(self.zoom_slider)
        controls_layout.addWidget(self.zoom_info)

        # Añadir el área de desplazamiento y los controles al layout principal
        self.main_layout.addWidget(self)  # Añadir este QScrollArea al layout principal
        self.main_layout.addLayout(controls_layout)

        # Nota: Ya no necesitamos estas líneas porque:
        # 1. Ya añadimos el page_label al page_layout en la línea 46
        # 2. Ya establecimos el widget del área de desplazamiento en la línea 49
        # 3. Ya no usamos nav_layout, ahora usamos controls_layout

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

            # Habilitar/deshabilitar botones según corresponda
            self.prev_btn.setEnabled(self.current_page > 0)
            self.next_btn.setEnabled(self.current_page < self.total_pages - 1)
            self.zoom_slider.setEnabled(True)

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

                # Crear matriz de transformación con el zoom efectivo
                # Usar un DPI más alto para mejor calidad
                dpi_factor = 2.0  # Factor de mejora de DPI
                render_zoom = effective_zoom * dpi_factor
                mat = fitz.Matrix(render_zoom, render_zoom)

                # Renderizar con alta calidad
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # Convertir a QImage directamente para mejor calidad
                qimg = QImage(
                    pix.samples,
                    pix.width,
                    pix.height,
                    pix.stride,
                    QImage.Format_RGB888
                )

                # Escalar la imagen de vuelta al tamaño deseado con alta calidad
                scaled_width = int(page_width * effective_zoom)
                scaled_height = int(page_height * effective_zoom)

                # Escalar la imagen con alta calidad
                if dpi_factor > 1.0:
                    qimg = qimg.scaled(
                        scaled_width,
                        scaled_height,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

                # Convertir a QPixmap para mostrar
                pixmap = QPixmap.fromImage(qimg)

            # Mostrar en el QLabel y ajustar su tamaño
            self.page_label.setPixmap(pixmap)
            self.page_label.setAlignment(Qt.AlignCenter)  # Centrar la imagen

            # Asegurarnos de que el contenedor tenga el tamaño adecuado
            # para permitir el desplazamiento cuando sea necesario
            self.container.setMinimumSize(pixmap.size())

            # Actualizar información de página
            self.page_info.setText(f"Página {page_num + 1} de {self.total_pages}")

            # Actualizar información de zoom con precisión de 1 decimal
            zoom_percent = round(self.zoom_factor * 100)
            self.zoom_info.setText(f"{zoom_percent}%")

            # Actualizar el slider de zoom (sin disparar el evento valueChanged)
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(zoom_percent)
            self.zoom_slider.blockSignals(False)

            # Actualizar página actual
            self.current_page = page_num

            # Actualizar estado de los botones
            self.prev_btn.setEnabled(page_num > 0)
            self.next_btn.setEnabled(page_num < self.total_pages - 1)

            # Actualizar estado del slider de zoom
            self.zoom_slider.setEnabled(True)

            # No reiniciamos las barras de desplazamiento aquí para mantener la posición
            # cuando se cambia el zoom desde on_zoom_slider_changed

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
        """Maneja los cambios en el slider de zoom"""
        # Guardar la posición de desplazamiento actual
        h_value = self.horizontalScrollBar().value()
        v_value = self.verticalScrollBar().value()

        # Calcular la posición relativa (porcentaje) del centro de la vista
        viewport_width = self.viewport().width()
        viewport_height = self.viewport().height()
        content_width = self.container.width()
        content_height = self.container.height()

        # Evitar división por cero
        if content_width > 0 and content_height > 0:
            center_x_percent = (h_value + viewport_width / 2) / content_width
            center_y_percent = (v_value + viewport_height / 2) / content_height
        else:
            center_x_percent = 0.5
            center_y_percent = 0.5

        # Convertir el valor del slider (20-300) a un factor de zoom (0.2-3.0)
        self.zoom_factor = value / 100.0

        # Actualizar la etiqueta de información de zoom
        self.zoom_info.setText(f"{value}%")

        # Actualizar la vista con el nuevo zoom
        self.show_page(self.current_page)

        # Esperar a que se actualice la interfaz
        QApplication.processEvents()

        # Calcular la nueva posición de desplazamiento para mantener el centro
        new_content_width = self.container.width()
        new_content_height = self.container.height()

        # Calcular y establecer las nuevas posiciones de desplazamiento
        if new_content_width > 0 and new_content_height > 0:
            new_h_value = max(0, (center_x_percent * new_content_width) - (viewport_width / 2))
            new_v_value = max(0, (center_y_percent * new_content_height) - (viewport_height / 2))

            # Aplicar las nuevas posiciones de desplazamiento
            self.horizontalScrollBar().setValue(int(new_h_value))
            self.verticalScrollBar().setValue(int(new_v_value))

    def zoom_in(self):
        """Aumenta el nivel de zoom con incrementos más pequeños"""
        if self.zoom_factor < 3.0:  # Limitar zoom máximo
            self.zoom_factor += self.zoom_step
            # Redondear a 2 decimales para evitar errores de punto flotante
            self.zoom_factor = round(self.zoom_factor, 2)

            # Actualizar el slider
            self.zoom_slider.setValue(int(self.zoom_factor * 100))

            # La actualización de la vista se hará a través del evento valueChanged del slider

    def zoom_out(self):
        """Reduce el nivel de zoom con incrementos más pequeños"""
        if self.zoom_factor > 0.2:  # Limitar zoom mínimo
            self.zoom_factor -= self.zoom_step
            # Redondear a 2 decimales para evitar errores de punto flotante
            self.zoom_factor = round(self.zoom_factor, 2)

            # Actualizar el slider
            self.zoom_slider.setValue(int(self.zoom_factor * 100))

            # La actualización de la vista se hará a través del evento valueChanged del slider

    def reset_zoom(self):
        """Restablece el zoom al nivel predeterminado"""
        self.zoom_factor = 1.0

        # Actualizar el slider
        self.zoom_slider.setValue(100)

        # La actualización de la vista se hará a través del evento valueChanged del slider

    def close_pdf(self):
        """Cierra el PDF actual"""
        if self.current_pdf:
            # Usar el contexto para suprimir mensajes de consola
            with SuppressOutput():
                self.current_pdf.close()

            self.current_pdf = None
            self.current_page = 0
            self.total_pages = 0
            self.zoom_factor = 1.0  # Restablecer zoom
            self.page_label.clear()
            self.page_info.setText("Página 0 de 0")
            self.zoom_info.setText("100%")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.zoom_slider.setEnabled(False)

            # Actualizar el slider de zoom (sin disparar el evento valueChanged)
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(100)
            self.zoom_slider.blockSignals(False)
