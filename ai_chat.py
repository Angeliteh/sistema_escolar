"""
Script para iniciar la interfaz de chat con IA para el sistema de constancias
"""
import sys
import argparse
import os
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

# Importar la nueva ventana de chat
from app.ui.ai_chat.chat_window import ChatWindow

# Cargar variables de entorno
load_dotenv()

def main():
    """Función principal para la interfaz de chat con IA"""
    # 🎯 CONFIGURAR ARGUMENTOS DE LÍNEA DE COMANDOS
    parser = argparse.ArgumentParser(description='Sistema de Constancias - Chat con IA')
    parser.add_argument('--debug-pauses', action='store_true',
                       help='Activar pausas de debug en puntos críticos del sistema')
    parser.add_argument('--no-debug-pauses', action='store_true',
                       help='Desactivar pausas de debug (por defecto)')

    args = parser.parse_args()

    # 🔧 CONFIGURAR VARIABLE DE ENTORNO PARA PAUSAS DEBUG
    if args.debug_pauses:
        os.environ['DEBUG_PAUSES'] = 'true'
        print("🛑 DEBUG: Pausas de debug ACTIVADAS")
        print("   ├── El sistema se pausará en puntos críticos")
        print("   ├── Presiona ENTER en cada pausa para continuar")
        print("   ├── Útil para análisis detallado del flujo")
        print("   └── PUNTOS CRÍTICOS MONITOREADOS:")
        print("       ├── 🧠 Master: Razonamiento inicial completo")
        print("       ├── 🎓 Student: Recibe información del Master")
        print("       ├── 🔍 Master: Detección inteligente de continuación (LLM)")
        print("       ├── 🗃️ Student: Mapeo de campos con contexto DB")
        print("       ├── 🔧 ActionExecutor: SQL final generado")
        print("       ├── 📋 ConversationStack: Estado ANTES de procesar (contexto completo)")
        print("       ├── 📋 ConversationStack: Estado DESPUÉS de procesar (contexto actualizado)")
        print("       ├── 📋 ConversationStack: NUEVO NIVEL agregado (Master decide)")
        print("       └── 🔍 Master: Análisis de contexto para referencias (completo)")
        print("   🎯 NUEVA ARQUITECTURA: Master como cerebro central del contexto")
        print("       ├── Master decide TODO sobre conversation_stack")
        print("       ├── Student solo reporta resultados")
        print("       ├── SIEMPRE agregar datos relevantes al contexto")
        print("       └── Sincronización perfecta análisis ↔ respuesta\n")
    elif args.no_debug_pauses:
        os.environ['DEBUG_PAUSES'] = 'false'
        print("⚡ DEBUG: Pausas de debug DESACTIVADAS")
        print("   └── El sistema funcionará sin interrupciones\n")
    else:
        # Por defecto, sin pausas
        os.environ.setdefault('DEBUG_PAUSES', 'false')

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
