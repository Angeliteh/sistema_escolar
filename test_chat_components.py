"""
Script para probar los componentes de chat
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

from app.ui.ai_chat.chat_bubble import ChatBubble
from app.ui.ai_chat.chat_list import ChatList

class TestWindow(QMainWindow):
    """Ventana de prueba para los componentes de chat"""

    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Prueba de Componentes de Chat")
        self.setMinimumSize(800, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)

        # Lista de chat
        self.chat_list = ChatList()

        # Botones de prueba
        button_layout = QHBoxLayout()

        add_user_button = QPushButton("Añadir Mensaje de Usuario")
        add_user_button.clicked.connect(self.add_user_message)

        add_assistant_button = QPushButton("Añadir Mensaje de Asistente")
        add_assistant_button.clicked.connect(self.add_assistant_message)

        add_system_button = QPushButton("Añadir Mensaje de Sistema")
        add_system_button.clicked.connect(self.add_system_message)

        button_layout.addWidget(add_user_button)
        button_layout.addWidget(add_assistant_button)
        button_layout.addWidget(add_system_button)

        # Añadir widgets al layout principal
        main_layout.addWidget(self.chat_list, 1)
        main_layout.addLayout(button_layout)

    def add_user_message(self):
        """Añade un mensaje de usuario de prueba"""
        self.chat_list.add_user_message("Este es un mensaje de prueba del usuario. Estoy escribiendo un texto más largo para probar cómo se ajusta el contenido en la burbuja de chat.", "12:34")

    def add_assistant_message(self):
        """Añade un mensaje de asistente de prueba"""
        self.chat_list.add_assistant_message("""Este es un mensaje de prueba del asistente. Puede ser más largo para probar cómo se ajusta el texto en la burbuja de chat.

        Incluso puede contener múltiples párrafos y elementos HTML como <b>texto en negrita</b>, <i>texto en cursiva</i>, o <a href='https://www.example.com'>enlaces</a>.

        También puede contener listas:
        <ul>
            <li>Elemento 1</li>
            <li>Elemento 2</li>
            <li>Elemento 3 con texto más largo para ver cómo se ajusta en la burbuja</li>
        </ul>
        """, "12:35")

    def add_system_message(self):
        """Añade un mensaje de sistema de prueba"""
        self.chat_list.add_system_message("Este es un mensaje de sistema. Los mensajes del sistema suelen ser más cortos y concisos, pero también pueden contener información importante para el usuario.", "12:36")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
