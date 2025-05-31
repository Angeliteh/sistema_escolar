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

# 🆕 IMPORTAR NUEVO SISTEMA DE ORQUESTACIÓN (OPCIONAL)
try:
    from app.core.ai.orchestration.master_orchestrator import MasterOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

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
                 pdf_panel = None,
                 use_orchestrator: bool = False):
        """
        Args:
            file_handler: Función para manejar archivos (abrir PDFs, etc.)
            confirmation_handler: Función para manejar confirmaciones
            pdf_panel: Panel de PDF para transformaciones
            use_orchestrator: Si usar el nuevo sistema de orquestación (experimental)
        """
        self.logger = get_logger(__name__)
        self.service_provider = ServiceProvider.get_instance()
        self.gemini_client = GeminiClient()

        # 🆕 GUARDAR PDF_PANEL COMO ATRIBUTO PARA ACCESO EN WORKER THREADS
        self.pdf_panel = pdf_panel

        # 🆕 SISTEMA DE ORQUESTACIÓN OPCIONAL
        self.use_orchestrator = use_orchestrator and ORCHESTRATOR_AVAILABLE
        if self.use_orchestrator:
            self.master_orchestrator = MasterOrchestrator()
            self.logger.info("🎯 MasterOrchestrator habilitado")
        else:
            self.master_orchestrator = None

        self.message_processor = MessageProcessor(self.gemini_client, pdf_panel)

        # Handlers opcionales para diferentes interfaces
        self.file_handler = file_handler or self._default_file_handler
        self.confirmation_handler = confirmation_handler or self._default_confirmation_handler

        # Estado del chat (historial manejado por MessageProcessor)
        self.context = {}

        orchestrator_status = "con MasterOrchestrator" if self.use_orchestrator else "sistema tradicional"
        self.logger.info(f"ChatEngine inicializado ({orchestrator_status})")

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
            # 🎯 NUEVO: USAR ORCHESTRATOR SI ESTÁ HABILITADO
            if self.use_orchestrator and self.master_orchestrator:
                return self._process_with_orchestrator(message)

            # 🔄 FLUJO TRADICIONAL: Sin create_prompt, directo a MasterInterpreter
            # Crear comando directo para el MessageProcessor
            command_data = {
                "accion": "consulta_directa",
                "parametros": {"consulta_original": message}
            }

            # 4. Procesar comando
            success, response_text, data = self.message_processor.process_command(
                command_data,
                None,  # current_pdf
                message,  # original_query
                self.context  # conversation_context
            )

            # 5. Analizar respuesta para determinar acciones
            return self._analyze_ai_response(response_text, data, success)

        except Exception as e:
            self.logger.error(f"Error en procesamiento IA: {str(e)}")
            return ChatResponse(
                text=f"❌ Error en el servicio de IA: {str(e)}",
                success=False
            )

    def _process_with_orchestrator(self, message: str) -> ChatResponse:
        """🎯 NUEVO: Procesa con MasterOrchestrator"""
        try:
            self.logger.info(f"🎯 [ORCHESTRATOR] Procesando: {message[:50]}...")

            # TODO: Crear contexto apropiado para el orchestrator
            # Por ahora, usar un contexto básico
            from app.core.ai.interpretation.base_interpreter import InterpretationContext

            context = InterpretationContext(
                user_message=message,
                conversation_stack=getattr(self.message_processor, 'conversation_stack', []),
                additional_context=self.context
            )

            # Procesar con orchestrator
            result = self.master_orchestrator.process_query(message, context)

            # Convertir resultado a ChatResponse
            return ChatResponse(
                text=result.get('message', result.get('text', 'Procesado por orchestrator')),
                success=result.get('success', True),
                action=result.get('action'),
                data=result.get('data', {}),
                files=result.get('files', [])
            )

        except Exception as e:
            self.logger.error(f"❌ [ORCHESTRATOR] Error: {e}")
            # Fallback al sistema tradicional
            self.logger.info("🔄 Fallback al sistema tradicional")
            return self._process_with_traditional_system(message)

    def _process_with_traditional_system(self, message: str) -> ChatResponse:
        """🔄 Sistema tradicional como fallback"""
        command_data = {
            "accion": "consulta_directa",
            "parametros": {"consulta_original": message}
        }

        success, response_text, data = self.message_processor.process_command(
            command_data,
            None,  # current_pdf
            message,  # original_query
            self.context  # conversation_context
        )

        return self._analyze_ai_response(response_text, data, success)

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

        # 🎯 DETECCIÓN INTELIGENTE DE PDF - SOLO PARA CONSTANCIAS GENERADAS
        # Solo buscar archivos PDF si command_data indica que se generó una constancia
        if (command_data and isinstance(command_data, dict) and
            (command_data.get('action') == 'constancia_preview' or
             'constancia' in str(command_data.get('message', '')).lower() or
             'ruta_archivo' in command_data)):

            import tempfile
            import time

            temp_dir = tempfile.gettempdir()
            current_time = time.time()

            # Buscar archivos PDF recientes SOLO cuando se generó una constancia
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.pdf') and 'constancia' in file.lower():
                        file_path = os.path.join(root, file)
                        try:
                            # Verificar si el archivo es muy reciente (últimos 5 segundos)
                            file_time = os.path.getmtime(file_path)
                            if current_time - file_time < 5:
                                if file_path not in generated_files:
                                    generated_files.append(file_path)
                                    action = "open_file"
                                    self.logger.info(f"Archivo PDF de constancia detectado: {file_path}")
                        except:
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
                            if "alumno" in command_data:
                                action = "constancia_preview"  # Vista previa de constancia generada
                            else:
                                action = "pdf_transformation"  # Transformación de PDF
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
            action = action or command_data["action"]
            self.logger.info(f"🔧 Usando action de command_data: {action}")

        # Fallback: detectar por contenido de respuesta
        if not action and ("📊" in ai_response or "📋" in ai_response):
            action = "show_data"

        # 🔧 MENSAJE CONSOLIDADO Y LIMPIO para archivos generados
        final_text = ai_response
        if generated_files:
            # Usar el mensaje del ConstanciaProcessor si está disponible
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
            action = "constancia_generated"  # Acción específica para constancias

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


