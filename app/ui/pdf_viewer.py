"""
Visor de PDF para la aplicación
"""
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

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
