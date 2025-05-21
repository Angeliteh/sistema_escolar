#!/usr/bin/env python
"""
Script para ejecutar la interfaz de búsqueda de alumnos
"""
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.buscar_ui import BuscarWindow

def main():
    """Función principal"""
    app = QApplication(sys.argv)

    # Establecer estilo global
    app.setStyle("Fusion")

    window = BuscarWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
