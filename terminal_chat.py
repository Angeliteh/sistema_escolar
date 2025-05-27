#!/usr/bin/env python3
"""
Chat de Terminal - Interfaz de línea de comandos
Mantiene toda la funcionalidad del chat gráfico pero en terminal
"""

import os
import sys
import subprocess
from typing import Optional

from app.core.chat_engine import ChatEngine, ChatInterface, ChatResponse
from app.core.logging import get_logger

class TerminalChatInterface(ChatInterface):
    """Interfaz de chat para terminal"""
    
    def __init__(self):
        # Handlers específicos para terminal
        chat_engine = ChatEngine(
            file_handler=self._handle_file,
            confirmation_handler=self._handle_confirmation
        )
        super().__init__(chat_engine)
        
        self.running = False
        self.logger = get_logger(__name__)
    
    def _handle_file(self, file_path: str) -> bool:
        """Maneja archivos en terminal"""
        try:
            if os.path.exists(file_path):
                print(f"📁 Archivo generado: {file_path}")
                
                # Preguntar si abrir el archivo
                response = input("¿Abrir archivo? (s/n): ").strip().lower()
                if response in ['s', 'sí', 'si', 'y', 'yes']:
                    self._open_file(file_path)
                    return True
            else:
                print(f"❌ Archivo no encontrado: {file_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error manejando archivo: {str(e)}")
            return False
    
    def _open_file(self, file_path: str):
        """Abre un archivo usando el programa por defecto del sistema"""
        try:
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
            
            print(f"✅ Archivo abierto: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"❌ Error abriendo archivo: {str(e)}")
    
    def _handle_confirmation(self, message: str) -> bool:
        """Maneja confirmaciones en terminal"""
        print(f"\n⚠️  {message}")
        response = input("¿Continuar? (s/n): ").strip().lower()
        return response in ['s', 'sí', 'si', 'y', 'yes']
    
    def handle_response(self, response: ChatResponse):
        """Maneja la respuesta del chat en terminal"""
        
        # Mostrar texto principal
        print(f"\n🤖 {response.text}")
        
        # Manejar archivos generados
        if response.files:
            for file_path in response.files:
                self._handle_file(file_path)
        
        # Manejar confirmaciones
        if response.requires_confirmation:
            confirmed = self._handle_confirmation("¿Proceder con la acción?")
            if not confirmed:
                print("❌ Acción cancelada por el usuario")
        
        # Manejar datos estructurados
        if response.action == "show_data" and response.data:
            print("\n📊 Datos adicionales:")
            for key, value in response.data.items():
                print(f"   {key}: {value}")
    
    def start(self):
        """Inicia el chat de terminal"""
        self.running = True
        
        print("🎯 CHAT DE TERMINAL - Sistema de Constancias")
        print("=" * 50)
        print("💡 Comandos especiales:")
        print("   /help    - Mostrar ayuda")
        print("   /stats   - Estadísticas del chat")
        print("   /history - Mostrar historial")
        print("   /clear   - Limpiar historial")
        print("   /export  - Exportar conversación")
        print("   /quit    - Salir")
        print("=" * 50)
        print("🤖 ¡Hola! Soy tu asistente de constancias. ¿En qué puedo ayudarte?")
        
        while self.running:
            try:
                # Leer mensaje del usuario
                user_input = input("\n👤 Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Manejar comandos especiales
                if user_input.startswith('/'):
                    self._handle_special_command(user_input)
                    continue
                
                # Procesar mensaje normal
                response = self.send_message(user_input)
                self.handle_response(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                self.running = False
            except EOFError:
                print("\n\n👋 ¡Hasta luego!")
                self.running = False
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
    
    def _handle_special_command(self, command: str):
        """Maneja comandos especiales del terminal"""
        
        if command == '/help':
            self._show_help()
        elif command == '/stats':
            self._show_stats()
        elif command == '/history':
            self._show_history()
        elif command == '/clear':
            self._clear_history()
        elif command == '/export':
            self._export_conversation()
        elif command == '/quit':
            self.running = False
            print("👋 ¡Hasta luego!")
        else:
            print(f"❌ Comando desconocido: {command}")
            print("💡 Usa /help para ver comandos disponibles")
    
    def _show_help(self):
        """Muestra ayuda del sistema"""
        print("\n📚 AYUDA DEL SISTEMA")
        print("=" * 30)
        print("🔍 Búsquedas:")
        print("   'cuántos alumnos hay'")
        print("   'buscar Juan'")
        print("   'alumnos de primer grado'")
        print("   'estudiantes del grupo A'")
        print()
        print("📄 Constancias:")
        print("   'genera constancia de estudios para [nombre]'")
        print("   'crea constancia de calificaciones para [nombre]'")
        print("   'constancia de traslado para [nombre]'")
        print()
        print("📊 Estadísticas:")
        print("   'estadísticas de la base de datos'")
        print("   'alumnos por grado'")
        print("   'alumnos por turno'")
        print()
        print("⚙️ Comandos especiales:")
        print("   /help    - Esta ayuda")
        print("   /stats   - Estadísticas del chat")
        print("   /history - Historial de conversación")
        print("   /clear   - Limpiar historial")
        print("   /export  - Exportar conversación")
        print("   /quit    - Salir")
    
    def _show_stats(self):
        """Muestra estadísticas del chat"""
        stats = self.chat_engine.get_stats()
        print("\n📊 ESTADÍSTICAS DEL CHAT")
        print("=" * 25)
        print(f"💬 Total mensajes: {stats['total_messages']}")
        print(f"👤 Mensajes usuario: {stats['user_messages']}")
        print(f"🤖 Mensajes asistente: {stats['assistant_messages']}")
        print(f"📝 Tamaño contexto: {stats['context_size']}")
        if stats['session_start']:
            print(f"⏰ Sesión iniciada: {stats['session_start']}")
    
    def _show_history(self):
        """Muestra historial de conversación"""
        history = self.chat_engine.get_conversation_history()
        
        if not history:
            print("\n📝 No hay historial de conversación")
            return
        
        print(f"\n📝 HISTORIAL ({len(history)} mensajes)")
        print("=" * 30)
        
        for i, msg in enumerate(history[-10:], 1):  # Últimos 10 mensajes
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            timestamp = msg["timestamp"][:19]  # Solo fecha y hora
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"{i:2d}. {role_icon} [{timestamp}] {content}")
        
        if len(history) > 10:
            print(f"\n... y {len(history) - 10} mensajes más")
    
    def _clear_history(self):
        """Limpia el historial de conversación"""
        confirm = input("¿Seguro que quieres limpiar el historial? (s/n): ").strip().lower()
        if confirm in ['s', 'sí', 'si', 'y', 'yes']:
            self.chat_engine.clear_history()
            print("✅ Historial limpiado")
        else:
            print("❌ Operación cancelada")
    
    def _export_conversation(self):
        """Exporta la conversación a un archivo"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversacion_{timestamp}.json"
        
        if self.chat_engine.export_conversation(filename):
            print(f"✅ Conversación exportada a: {filename}")
        else:
            print("❌ Error exportando conversación")
    
    def stop(self):
        """Detiene el chat"""
        self.running = False

def main():
    """Función principal"""
    try:
        chat = TerminalChatInterface()
        chat.start()
        return 0
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
