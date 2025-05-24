"""
Panel colapsable para contener otros widgets
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize, pyqtSignal


class CollapsiblePanel(QWidget):
    """
    Panel colapsable que puede expandirse y contraerse
    """
    # Señal emitida cuando el panel cambia de estado
    stateChanged = pyqtSignal(bool)  # True = expandido, False = contraído

    def __init__(self, title, content_widget=None, parent=None, expanded=False):
        """
        Inicializa el panel colapsable

        Args:
            title (str): Título que se mostrará en el encabezado
            content_widget (QWidget, optional): Widget que se mostrará cuando el panel esté expandido
                                               (puede ser None si solo se usa como botón)
            parent (QWidget, optional): Widget padre
            expanded (bool, optional): Si el panel debe estar expandido inicialmente
        """
        super().__init__(parent)
        self.title = title
        self.content_widget = content_widget
        self.is_expanded = expanded
        self.animation = None
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del panel"""
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Encabezado
        self.header = QFrame()
        self.header.setCursor(Qt.PointingHandCursor)  # Cambiar cursor al pasar sobre el encabezado
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 8, 10, 8)

        # Icono de PDF
        pdf_icon = QLabel("📄")
        pdf_icon.setStyleSheet("font-size: 16px; margin-right: 5px;")

        # Título
        self.title_label = QLabel(self.title)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Botón de alternancia
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(24, 24)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        # Añadir widgets al layout del encabezado
        header_layout.addWidget(pdf_icon)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.toggle_button)

        # Contenedor para el contenido (solo si hay un widget de contenido)
        if self.content_widget:
            self.content_container = QWidget()
            content_layout = QVBoxLayout(self.content_container)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.addWidget(self.content_widget)

            # Configurar visibilidad y tamaño inicial
            if not self.is_expanded:
                self.content_widget.setVisible(False)
                self.content_container.setFixedHeight(0)
                self.content_container.setMaximumHeight(0)
            else:
                self.content_widget.setVisible(True)
                self.content_container.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

            # Añadir el contenedor al layout principal
            self.main_layout.addWidget(self.content_container)
        else:
            # Si no hay widget de contenido, este panel solo funciona como un botón
            self.content_container = None

        self.update_toggle_button()

        # Añadir el encabezado al layout principal
        self.main_layout.addWidget(self.header)

        # Conectar señales
        self.header.mousePressEvent = self.header_clicked
        self.toggle_button.clicked.connect(self.toggle_expansion)

        # Aplicar estilos
        self.apply_styles()

    def apply_styles(self):
        """Aplica estilos al panel"""
        # Estilo para el encabezado
        self.header.setStyleSheet("""
            QFrame {
                background-color: #1E3A5F;
                border: 1px solid #2C4F7C;
                border-radius: 8px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #2C4F7C;
            }
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        # Añadir un tooltip al encabezado
        self.header.setToolTip("Haz clic para expandir/contraer el panel de transformación de PDF")

        # Estilo para el contenedor de contenido (si existe)
        if self.content_container:
            self.content_container.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                }
            """)

    def header_clicked(self, event):
        """Maneja el clic en el encabezado"""
        self.toggle_expansion()

    def toggle_expansion(self):
        """Alterna entre expandido y contraído"""
        self.is_expanded = not self.is_expanded

        # Ajustar la visibilidad y el tamaño del contenido (solo si hay contenido)
        if self.content_widget and self.content_container:
            if not self.is_expanded:
                # Cuando está contraído
                self.content_widget.setVisible(False)
                self.content_container.setFixedHeight(0)
                self.content_container.setMaximumHeight(0)
            else:
                # Cuando está expandido
                self.content_widget.setVisible(True)
                self.content_container.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
                self.content_container.setFixedHeight(self.content_widget.sizeHint().height())

        self.update_toggle_button()

        # Emitir señal de cambio de estado
        self.stateChanged.emit(self.is_expanded)

        # Forzar actualización del layout
        self.adjustSize()
        self.updateGeometry()

    def update_toggle_button(self):
        """Actualiza el texto del botón de alternancia según el estado"""
        if self.is_expanded:
            self.toggle_button.setText("▼")  # Flecha abajo cuando está expandido
            self.toggle_button.setToolTip("Contraer panel")
        else:
            self.toggle_button.setText("▶")  # Flecha derecha cuando está contraído
            self.toggle_button.setToolTip("Expandir panel")

    def set_expanded(self, expanded):
        """Establece el estado de expansión del panel"""
        if self.is_expanded != expanded:
            self.toggle_expansion()

    def sizeHint(self):
        """Sugerencia de tamaño para el widget"""
        # Devolver un tamaño mínimo para que el panel sea visible
        return QSize(200, 40)
