#!/usr/bin/env python
"""
Script para ejecutar la interfaz de gestión de alumnos
"""
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.alumno_ui import AlumnoManagerWindow

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    window = AlumnoManagerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
