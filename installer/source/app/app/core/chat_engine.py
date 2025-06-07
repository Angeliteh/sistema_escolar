# app/core/chat_engine.py
"""
Motor de Chat Independiente de la Interfaz
Maneja toda la lógica de procesamiento sin depender de UI específica
"""

import os
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

from app.core.service_provider import ServiceProvider
from app.ui.ai_chat.gemini_client import GeminiClient
from app.ui.ai_chat.message_processor import MessageProcessor
from app.core.logging import get_logger



class ChatResponse:
    """Respuesta estructurada del chat"""

    def __init__(self,
                 text: str = "",
                 success: bool = True,
                 action: Optional[str] = None,
                 data: Optional[Dict] = None,
                 files: Optional[List[str]] = None,
                 requires_confirmation: bool = False):
        self.text = text
        self.success = success
        self.action = action  # "open_file", "show_data", "generate_pdf", etc.
        self.data = data or {}
        self.files = files or []
        self.requires_confirmation = requires_confirmation
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return {
            "text": self.text,
            "success": self.success,
            "action": self.action,
            "data": self.data,
            "files": self.files,
            "requires_confirmation": self.requires_confirmation,
            "timestamp": self.timestamp.isoformat()
        }

class ChatEngine:
    """Motor de chat independiente de la interfaz"""

    def __init__(self,
                 file_handler: Optional[Callable] = None,
                 confirmation_handler: Optional[Callable] = None,
                 pdf_panel = None):
        """
        Args:
            file_handler: Función para manejar archivos (abrir PDFs, etc.)
            confirmation_handler: Función para manejar confirmaciones
            pdf_panel: Panel de PDF para transformaciones
        """
        self.logger = get_logger(__name__)
        self.service_provider = ServiceProvider.get_instance()
        self.gemini_client = GeminiClient()

        # 🆕 GUARDAR PDF_PANEL COMO ATRIBUTO PARA ACCESO EN WORKER THREADS
        self.pdf_panel = pdf_panel

        self.message_processor = MessageProcessor(self.gemini_client, pdf_panel)

        # Handlers opcionales para diferentes interfaces
        self.file_handler = file_handler or self._default_file_handler
        self.confirmation_handler = confirmation_handler or self._default_confirmation_handler

        # Estado del chat (historial manejado por MessageProcessor)
        self.context = {}

        self.logger.info(f"ChatEngine inicializado (sistema tradicional)")

    def process_message(self, message: str, user_context: Optional[Dict] = None) -> ChatResponse:
        """
        Procesa un mensaje y devuelve una respuesta estructurada

        Args:
            message: Mensaje del usuario
            user_context: Contexto adicional del usuario

        Returns:
            ChatResponse con la respuesta procesada
        """
        try:
            self.logger.info(f"🎯 [CHATENGINE] Procesando: '{message[:50]}...'")

            # Actualizar contexto
            if user_context:
                self.context.update(user_context)

            # Procesar con IA (historial manejado por MessageProcessor)
            response = self._process_with_ai(message)

            return response

        except Exception as e:
            self.logger.error(f"Error procesando mensaje: {str(e)}")
            return ChatResponse(
                text=f"❌ Error procesando mensaje: {str(e)}",
                success=False
            )

    def _process_with_ai(self, message: str) -> ChatResponse:
        """Procesa el mensaje con el servicio de IA usando GeminiClient centralizado"""
        try:
            # Crear comando directo para el MessageProcessor
            command_data = {
                "accion": "consulta_directa",
                "parametros": {"consulta_original": message}
            }

            # 4. Procesar comando
            # Obtener PDF actual del panel si está disponible
            current_pdf = None
            if self.pdf_panel and hasattr(self.pdf_panel, 'get_current_pdf'):
                current_pdf = self.pdf_panel.get_current_pdf()

            success, response_text, data = self.message_processor.process_command(
                command_data,
                current_pdf,  # current_pdf del panel
                message,  # original_query
                self.context  # conversation_context
            )

            # 🔧 LOGS INFORMATIVOS - SIN CONTENIDO REPETITIVO
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [CHATENGINE] Respuesta del Master recibida:")
            debug_detailed(self.logger, f"   ├── Estado: {'✅ Exitosa' if success else '❌ Error'}")
            debug_detailed(self.logger, f"   ├── Datos: {len(data.keys()) if data else 0} campos")
            if data and 'human_response' in data:
                response_length = len(data['human_response']) if data['human_response'] else 0
                debug_detailed(self.logger, f"   └── Respuesta: {response_length} caracteres preparados")
            else:
                debug_detailed(self.logger, f"   └── Respuesta: Usando fallback ({len(response_text)} chars)")

            # 5. Analizar respuesta para determinar acciones
            chat_response = self._analyze_ai_response(response_text, data, success)

            # 🔧 LOGS INFORMATIVOS - RESPUESTA FINAL PREPARADA
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [CHATENGINE] Respuesta final preparada:")
            debug_detailed(self.logger, f"   ├── Acción: {chat_response.action}")
            debug_detailed(self.logger, f"   ├── Estado: {'✅ Lista' if chat_response.success else '❌ Error'}")
            debug_detailed(self.logger, f"   └── Contenido: {len(chat_response.text)} caracteres → Enviando a UI")

            return chat_response

        except Exception as e:
            self.logger.error(f"Error en procesamiento IA: {str(e)}")
            return ChatResponse(
                text=f"❌ Error en el servicio de IA: {str(e)}",
                success=False
            )



    def _analyze_ai_response(self, ai_response: str, command_data: dict, command_success: bool) -> ChatResponse:
        """Analiza la respuesta de IA para determinar acciones necesarias"""

        # Validar que ai_response no sea None
        if ai_response is None:
            self.logger.error("Error determinando tipo de respuesta: ai_response es None")
            ai_response = "Error procesando respuesta"

        # Detectar si se generó un archivo
        generated_files = []
        action = None

        # Buscar patrones de archivos generados en logs y respuesta

        # Buscar en la respuesta de IA
        if "PDF generado:" in ai_response or "Constancia generada:" in ai_response or "archivo:" in ai_response.lower():
            lines = ai_response.split('\n')
            for line in lines:
                if "PDF generado:" in line or "archivo:" in line.lower() or "constancia" in line.lower():
                    parts = line.split(':')
                    if len(parts) > 1:
                        file_path = parts[1].strip()
                        if os.path.exists(file_path):
                            generated_files.append(file_path)
                            action = "open_file"

        # 🎯 DETECCIÓN INTELIGENTE DE PDF - PARA CONSTANCIAS Y TRANSFORMACIONES
        # Solo buscar archivos PDF si command_data indica que se generó una constancia o transformación
        if (command_data and isinstance(command_data, dict) and
            (command_data.get('action') in ['constancia_preview', 'transformation_preview'] or
             'constancia' in str(command_data.get('message', '')).lower() or
             'transformación' in str(command_data.get('message', '')).lower() or
             'ruta_archivo' in command_data)):

            # Los archivos PDF se manejan directamente desde command_data
            # No necesitamos buscar en directorios temporales
            pass

        # 🆕 DETECTAR CONSTANCIAS EN COMMAND_DATA
        # (La integración completa con interpretadores se hará después)

        # Detectar archivos en command_data (método original)
        if command_data and isinstance(command_data, dict):
            # Buscar archivos en diferentes campos
            file_fields = ["archivo_generado", "ruta_archivo", "file_path"]
            for field in file_fields:
                if field in command_data:
                    file_path = command_data[field]
                    if file_path and os.path.exists(file_path):
                        generated_files.append(file_path)

                        # 🎯 DETECTAR TIPO DE ACCIÓN SEGÚN CONTEXTO
                        if "constancia" in file_path.lower() or "constancia" in ai_response.lower():
                            # Detectar si es transformación o constancia nueva
                            if command_data.get('action') == 'transformation_preview':
                                action = "transformation_preview"  # Vista previa de transformación
                            elif "alumno" in command_data:
                                action = "constancia_preview"  # Vista previa de constancia generada
                            else:
                                action = "pdf_transformation"  # Transformación de PDF (fallback)
                        else:
                            action = "open_file"

        # Detectar si necesita confirmación
        requires_confirmation = any(phrase in ai_response.lower() for phrase in [
            "¿confirmas?", "¿proceder?", "¿continuar?", "¿estás seguro?"
        ])

        # Detectar datos estructurados (listas, tablas)
        data = command_data if command_data else {}

        # 🔧 PRIORIZAR ACTION DE COMMAND_DATA (configurado por MessageProcessor)
        if command_data and isinstance(command_data, dict) and "action" in command_data:
            # 🎯 PRIORIDAD ABSOLUTA: command_data["action"] sobrescribe cualquier detección automática
            action = command_data["action"]  # ← USAR DIRECTAMENTE, NO "or"
            self.logger.info(f"🔧 [CHATENGINE] Usando action de command_data: {action}")
            # 🔧 Procesando datos de comando

            # 🤔 MANEJO ESPECIAL PARA ACLARACIONES
            if action == "aclaracion_requerida":
                self.logger.info("🤔 [CHATENGINE] Consulta ambigua detectada - configurando respuesta de aclaración")
                # Usar la respuesta humana generada por el Master
                if 'human_response' in command_data:
                    final_text = command_data['human_response']
                else:
                    final_text = command_data.get('message', 'Tu consulta necesita aclaración.')

                return ChatResponse(
                    text=final_text,
                    success=True,
                    action="aclaracion_requerida",
                    data=command_data,
                    requires_confirmation=False
                )
        else:
            # 🔧 No hay action específica en command_data
            pass

        # 🎯 DETECTAR DATOS ESTRUCTURADOS AUTOMÁTICAMENTE
        if command_data and isinstance(command_data, dict):
            # Si hay datos de alumnos, configurar show_data
            if ("data" in command_data and command_data["data"] and
                isinstance(command_data["data"], list) and len(command_data["data"]) > 0):
                if not action:  # Solo si no hay action ya configurada
                    action = "show_data"
                    from app.core.logging import debug_detailed
                    debug_detailed(self.logger, f"🔧 [CHATENGINE] Auto-detectado: show_data ({len(command_data['data'])} registros)")

        # Fallback: detectar por contenido de respuesta
        if not action and ("📊" in ai_response or "📋" in ai_response):
            action = "show_data"

        # 🔧 MENSAJE CONSOLIDADO Y LIMPIO - PRIORIZAR HUMAN_RESPONSE
        # 🎯 SOLUCIÓN: Usar human_response de data si está disponible
        if command_data and isinstance(command_data, dict) and 'human_response' in command_data:
            final_text = command_data['human_response']
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [CHATENGINE] Fuente: human_response ({len(final_text)} chars)")
        else:
            final_text = ai_response
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [CHATENGINE] Fuente: ai_response fallback ({len(final_text)} chars)")

        # Para archivos generados, ajustar mensaje si es necesario
        if generated_files:
            # 🎯 NO SOBRESCRIBIR SI YA HAY UN MENSAJE DEL MASTER
            if not final_text or final_text == ai_response:
                # Solo usar mensaje del ConstanciaProcessor si no hay mensaje del Master
                if hasattr(data, 'get') and data.get('message'):
                    final_text = data['message']
                else:
                    final_text = f"✅ Constancia generada exitosamente. La vista previa está disponible en el panel derecho."

            if not command_success:
                # Si el comando falló pero encontramos archivos, es éxito
                command_success = True

        # 🎯 CONSTANCIAS COMO ACCIONES COMPLETAS (NO REQUIEREN CONFIRMACIÓN)
        if generated_files and any(f.lower().endswith('.pdf') for f in generated_files):
            requires_confirmation = False  # Las constancias no requieren confirmación
            # 🔧 PRESERVAR ACCIONES ESPECÍFICAS - NO SOBRESCRIBIR
            if action not in ["constancia_preview", "transformation_preview"]:
                action = "constancia_generated"  # Solo usar fallback si no hay acción específica

        return ChatResponse(
            text=final_text,
            success=command_success,
            action=action,
            files=generated_files,
            requires_confirmation=requires_confirmation,
            data=data
        )

    def _default_file_handler(self, file_path: str) -> bool:
        """Handler por defecto para archivos (no hace nada)"""
        self.logger.info(f"Archivo generado: {file_path}")
        return True

    def _default_confirmation_handler(self, message: str) -> bool:
        """Handler por defecto para confirmaciones (siempre sí)"""
        self.logger.info(f"Confirmación requerida: {message}")
        return True

    def get_conversation_history(self) -> List[Dict]:
        """Obtiene el historial de conversación desde MessageProcessor"""
        return self.message_processor.conversation_history.copy()

    def clear_history(self):
        """Limpia el historial de conversación"""
        self.message_processor.conversation_history.clear()
        self.message_processor.conversation_stack.clear()
        self.context.clear()
        self.logger.info("Historial de conversación limpiado")

    def export_conversation(self, file_path: str) -> bool:
        """Exporta la conversación a un archivo JSON"""
        try:
            export_data = {
                "conversation": self.message_processor.conversation_history,
                "conversation_stack": self.message_processor.conversation_stack,
                "context": self.context,
                "exported_at": datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Conversación exportada a: {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error exportando conversación: {str(e)}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del chat"""
        conversation_history = self.message_processor.conversation_history
        return {
            "total_messages": len(conversation_history),
            "user_messages": len([m for m in conversation_history if m["role"] == "user"]),
            "assistant_messages": len([m for m in conversation_history if m["role"] in ["assistant", "system"]]),
            "context_size": len(self.context),
            "conversation_stack_size": len(self.message_processor.conversation_stack),
            "session_start": conversation_history[0]["timestamp"] if conversation_history else None
        }


