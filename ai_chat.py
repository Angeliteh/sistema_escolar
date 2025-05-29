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

def main():
    """Función principal para la interfaz de chat con IA"""
    # Verificar si ya hay una aplicación QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = ChatWindow()
    window.show()

    # Asegurar que la aplicación termine cuando se cierre la ventana
    app.setQuitOnLastWindowClosed(True)

    # Solo llamar exec_() si somos la aplicación principal
    if app.thread() == window.thread():
        sys.exit(app.exec_())
    else:
        # Si somos llamados desde otro proceso, solo mostrar la ventana
        return window

if __name__ == "__main__":
    main()
