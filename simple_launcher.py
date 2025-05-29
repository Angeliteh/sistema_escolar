"""
Launcher simple y confiable para el sistema de constancias
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configura el entorno para que funcione desde cualquier ubicación"""
    # Obtener directorio del script
    if getattr(sys, 'frozen', False):
        # Ejecutable
        app_dir = Path(sys.executable).parent
    else:
        # Desarrollo
        app_dir = Path(__file__).parent
    
    # Agregar al path
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    
    # Cambiar directorio de trabajo
    os.chdir(app_dir)
    
    return app_dir

def check_dependencies():
    """Verifica que las dependencias estén disponibles"""
    required_modules = [
        'PyQt5',
        'sqlite3',
        'json',
        'pathlib'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return missing

def launch_ai_interface():
    """Lanza la interfaz de IA"""
    try:
        from app.ui.ai_chat.chat_window import ChatWindow
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = ChatWindow()
        window.show()
        
        return app.exec_()
        
    except Exception as e:
        print(f"Error lanzando interfaz IA: {e}")
        return 1

def launch_traditional_interface():
    """Lanza la interfaz tradicional"""
    try:
        from app.ui.menu_principal import MenuPrincipal
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = MenuPrincipal()
        window.show()
        
        return app.exec_()
        
    except Exception as e:
        print(f"Error lanzando interfaz tradicional: {e}")
        return 1

def show_interface_selector():
    """Muestra selector de interfaz"""
    try:
        from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel
        from PyQt5.QtCore import Qt
        
        app = QApplication(sys.argv)
        
        dialog = QDialog()
        dialog.setWindowTitle("Sistema de Constancias")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Selecciona la interfaz:")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Botón IA
        btn_ai = QPushButton("🤖 Interfaz con IA")
        btn_ai.setStyleSheet("padding: 10px; font-size: 12px;")
        btn_ai.clicked.connect(lambda: dialog.done(1))
        layout.addWidget(btn_ai)
        
        # Botón tradicional
        btn_traditional = QPushButton("📋 Interfaz Tradicional")
        btn_traditional.setStyleSheet("padding: 10px; font-size: 12px;")
        btn_traditional.clicked.connect(lambda: dialog.done(2))
        layout.addWidget(btn_traditional)
        
        dialog.setLayout(layout)
        
        result = dialog.exec_()
        app.quit()
        
        return result
        
    except Exception as e:
        print(f"Error mostrando selector: {e}")
        return 0

def main():
    """Función principal"""
    print("🚀 Iniciando Sistema de Constancias...")
    
    # Configurar entorno
    app_dir = setup_environment()
    print(f"📁 Directorio de aplicación: {app_dir}")
    
    # Verificar dependencias
    missing = check_dependencies()
    if missing:
        print(f"❌ Dependencias faltantes: {', '.join(missing)}")
        input("Presiona Enter para continuar...")
        return 1
    
    print("✅ Dependencias verificadas")
    
    # Verificar archivos críticos
    critical_files = [
        "school_config.json",
        "resources/data/alumnos.db"
    ]
    
    missing_files = []
    for file in critical_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos críticos faltantes: {', '.join(missing_files)}")
        input("Presiona Enter para continuar...")
        return 1
    
    print("✅ Archivos críticos verificados")
    
    # Determinar interfaz a lanzar
    if len(sys.argv) > 1:
        interface = sys.argv[1].lower()
        if interface == "ai":
            return launch_ai_interface()
        elif interface == "traditional":
            return launch_traditional_interface()
    
    # Mostrar selector
    choice = show_interface_selector()
    
    if choice == 1:
        print("🤖 Lanzando interfaz con IA...")
        return launch_ai_interface()
    elif choice == 2:
        print("📋 Lanzando interfaz tradicional...")
        return launch_traditional_interface()
    else:
        print("❌ Cancelado por el usuario")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para continuar...")
        sys.exit(1)
