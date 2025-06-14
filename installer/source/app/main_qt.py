#!/usr/bin/env python
"""
Script para ejecutar la aplicación de constancias escolares
"""
import sys
from PyQt5.QtWidgets import QApplication
from app.ui.menu_principal import MenuPrincipal
from app.core.utils import clean_temp_files, ensure_directories_exist
from app.core.logging import get_logger

def main():
    """Función principal"""
    # Inicializar logger
    logger = get_logger(__name__)

    # Asegurar que los directorios necesarios existan
    ensure_directories_exist()

    # Limpiar archivos temporales antiguos (más de 3 días)
    deleted_count = clean_temp_files(max_age_days=3)
    if deleted_count > 0:
        logger.info(f"Se eliminaron {deleted_count} archivos temporales antiguos")

    # Verificar si ya hay una aplicación QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Establecer estilo global
    app.setStyle("Fusion")

    window = MenuPrincipal()
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
