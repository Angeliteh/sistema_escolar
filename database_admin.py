#!/usr/bin/env python
"""
Script para ejecutar la interfaz de administración de la base de datos
"""
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.database_admin_ui import DatabaseAdminWindow

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Establecer estilo global
    app.setStyle("Fusion")
    
    window = DatabaseAdminWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
