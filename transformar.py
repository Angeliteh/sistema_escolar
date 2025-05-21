#!/usr/bin/env python
"""
Script para ejecutar la interfaz de transformación de constancias
"""
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.transformar_ui import TransformarWindow

def main():
    """Función principal"""
    app = QApplication(sys.argv)

    # Establecer estilo global
    app.setStyle("Fusion")

    window = TransformarWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
