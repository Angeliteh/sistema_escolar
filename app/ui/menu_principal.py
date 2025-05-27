"""
Menú principal de la aplicación
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSizePolicy, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from app.ui.alumno_ui import AlumnoManagerWindow
from app.ui.buscar_ui import BuscarWindow
from app.ui.transformar_ui import TransformarWindow
from app.ui.database_admin_ui import DatabaseAdminWindow
from app.core.config import Config

class MenuPrincipal(QMainWindow):
    """Ventana del menú principal"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Sistema de Constancias Escolares v{Config.VERSION}")
        self.setMinimumSize(1200, 800)  # Ventana más grande

        # Establecer estilo modo oscuro para toda la aplicación
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1A2E;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Crear un layout principal con márgenes más amplios
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)

        # Contenedor para el encabezado con efecto de sombra
        header_container = QWidget()
        header_container.setObjectName("headerContainer")
        header_container.setStyleSheet("""
            #headerContainer {
                background-color: #16213E;
                border-radius: 15px;
                padding: 20px;
                border: 1px solid #2C4F7C;
            }
        """)

        # Aplicar sombra al contenedor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        header_container.setGraphicsEffect(shadow)

        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(10)

        # Título con estilo moderno
        title_label = QLabel("Sistema de Constancias Escolares")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFFFFF; text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);")

        # Subtítulo con estilo moderno
        subtitle_label = QLabel(f"Escuela Primaria {Config.get_school_name()}")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Segoe UI", 16)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #7FB3D5;")

        # Línea divisoria
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #2C4F7C; max-height: 1px;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(divider)

        main_layout.addWidget(header_container)

        # Contenedor para los botones con efecto de sombra
        buttons_container = QWidget()
        buttons_container.setObjectName("buttonsContainer")
        buttons_container.setStyleSheet("""
            #buttonsContainer {
                background-color: #16213E;
                border-radius: 15px;
                padding: 40px;
                border: 1px solid #2C4F7C;
            }
        """)

        # Aplicar sombra al contenedor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        buttons_container.setGraphicsEffect(shadow)

        # Layout horizontal para los botones con más espacio
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(50)  # Mayor espacio entre botones
        buttons_layout.setContentsMargins(30, 30, 30, 30)  # Márgenes más amplios

        # Botón Transformar Constancia
        self.btn_transformar = self.create_menu_button(
            "Transformar Constancia",
            "Convertir un PDF existente a formato estandarizado",
            "#3498db",
            "transform"
        )
        self.btn_transformar.clicked.connect(self.open_transformar_dialog)

        # Botón Buscar y Generar
        self.btn_buscar = self.create_menu_button(
            "Buscar y Generar",
            "Buscar alumnos registrados y generar constancias",
            "#2ecc71",
            "search"
        )
        self.btn_buscar.clicked.connect(self.open_buscar_alumno)

        # Botón Gestionar Alumnos
        self.btn_gestionar = self.create_menu_button(
            "Gestionar Alumnos",
            "Agregar, modificar o eliminar alumnos y sus datos",
            "#e74c3c",
            "database"
        )
        self.btn_gestionar.clicked.connect(self.open_gestionar_alumnos)

        buttons_layout.addWidget(self.btn_transformar)
        buttons_layout.addWidget(self.btn_buscar)
        buttons_layout.addWidget(self.btn_gestionar)

        main_layout.addWidget(buttons_container)

        # Contenedor para el pie de página con efecto de sombra
        footer_container = QWidget()
        footer_container.setObjectName("footerContainer")
        footer_container.setStyleSheet("""
            #footerContainer {
                background-color: #16213E;
                border-radius: 15px;
                padding: 15px;
                border: 1px solid #2C4F7C;
            }
        """)

        # Aplicar sombra al contenedor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        footer_container.setGraphicsEffect(shadow)

        footer_layout = QVBoxLayout(footer_container)

        # Pie de página con estilo moderno
        footer_label = QLabel(f"Versión {Config.VERSION} - Desarrollado para {Config.get_school_name()}")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_font = QFont("Segoe UI", 10)
        footer_label.setFont(footer_font)
        footer_label.setStyleSheet("color: #7FB3D5;")

        # Layout para el pie de página con botón de administración
        footer_bottom_layout = QHBoxLayout()

        # Botón discreto para administración de base de datos
        self.btn_db_admin = QPushButton("DB")
        self.btn_db_admin.setToolTip("Administración de Base de Datos (Solo para desarrolladores)")
        self.btn_db_admin.setFixedSize(30, 20)
        self.btn_db_admin.setStyleSheet("""
            QPushButton {
                background-color: #1E3A5F;
                color: #7FB3D5;
                border: 1px solid #2C4F7C;
                border-radius: 3px;
                font-size: 8px;
            }
            QPushButton:hover {
                background-color: #2C4F7C;
            }
            QPushButton:pressed {
                background-color: #3A6095;
            }
        """)
        self.btn_db_admin.clicked.connect(self.open_database_admin)

        # Añadir espaciador para empujar el botón a la derecha
        footer_bottom_layout.addStretch()
        footer_bottom_layout.addWidget(self.btn_db_admin)

        footer_layout.addWidget(footer_label)
        footer_layout.addLayout(footer_bottom_layout)
        main_layout.addWidget(footer_container)

    def create_menu_button(self, text, description, color, icon_type=""):
        """Crea un botón para el menú principal con estilo moderno y creativo"""
        # Crear un botón simple pero atractivo
        button = QPushButton()
        button.setObjectName(f"btn_{icon_type}")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumSize(300, 300)  # Tamaño fijo para evitar problemas
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Crear layout para el contenido del botón
        button_layout = QVBoxLayout(button)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 30, 20, 30)

        # Círculo con la inicial
        circle_label = QLabel()
        circle_label.setFixedSize(80, 80)
        circle_label.setAlignment(Qt.AlignCenter)
        circle_label.setText(text[0].upper())

        # Fuente para la inicial
        circle_font = QFont("Arial", 30)
        circle_font.setBold(True)
        circle_label.setFont(circle_font)

        # Estilo para el círculo
        circle_label.setStyleSheet(f"""
            background-color: #1A1A2E;
            color: {color};
            border-radius: 40px;
            border: 2px solid {color};
            font-weight: bold;
        """)

        # Título del botón
        title_label = QLabel(text)
        title_font = QFont("Arial", 16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white;")

        # Línea divisoria
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedWidth(150)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")

        # Descripción del botón
        desc_label = QLabel(description)
        desc_font = QFont("Arial", 12)
        desc_label.setFont(desc_font)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: white;")

        # Añadir widgets al layout
        button_layout.addWidget(circle_label, 0, Qt.AlignCenter)
        button_layout.addWidget(title_label)
        button_layout.addWidget(divider, 0, Qt.AlignCenter)
        button_layout.addWidget(desc_label)

        # Estilo del botón
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 15px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {color};
                border: 3px solid white;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {color};
                border: 3px solid white;
            }}
        """)

        # Aplicar sombra al botón
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 5)
        button.setGraphicsEffect(shadow)

        return button

    def open_transformar_dialog(self):
        """Abre la ventana para transformar constancias"""
        self.transformar_window = TransformarWindow()
        self.transformar_window.show()

    def open_buscar_alumno(self):
        """Abre la ventana de búsqueda de alumnos"""
        self.buscar_window = BuscarWindow()
        self.buscar_window.show()

    def open_gestionar_alumnos(self):
        """Abre la ventana de gestión de alumnos"""
        self.admin_window = AlumnoManagerWindow()
        self.admin_window.show()

    def open_database_admin(self):
        """Abre la ventana de administración de la base de datos con protección de contraseña"""
        from PyQt5.QtWidgets import QInputDialog, QLineEdit

        # Solicitar contraseña
        password, ok = QInputDialog.getText(
            self,
            "Acceso Restringido",
            "Ingrese la contraseña de desarrollador:",
            QLineEdit.Password
        )

        # Verificar contraseña (simple, solo para disuadir a usuarios no técnicos)
        if ok and password == "admin123":  # Contraseña simple para desarrollo
            self.db_admin_window = DatabaseAdminWindow()
            self.db_admin_window.show()
        elif ok:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Acceso Denegado",
                "Contraseña incorrecta. Esta función es solo para desarrolladores."
            )

def main():
    """Función principal"""
    app = QApplication(sys.argv)

    # Establecer estilo global
    app.setStyle("Fusion")

    window = MenuPrincipal()
    window.show()

    sys.exit(app.exec_())
