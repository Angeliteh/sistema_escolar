"""
Script para iniciar la interfaz de chat con IA para el sistema de constancias
"""
import sys
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

# Importar la nueva ventana de chat
from app.ui.ai_chat.chat_window import ChatWindow

# Cargar variables de entorno
load_dotenv()

if __name__ == "__main__":
    # Iniciar la aplicación
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
