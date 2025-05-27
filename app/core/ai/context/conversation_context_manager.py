"""
Gestor centralizado de contexto conversacional
Centraliza toda la lógica de contexto que antes estaba dispersa
"""
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.core.ai.interpretation.base_interpreter import InterpretationContext
from app.core.logging import get_logger


@dataclass
class ContextAnalysis:
    """Resultado del análisis contextual"""
    is_continuation: bool
    continuation_type: Optional[str]  # "confirmacion", "aclaracion", "seleccion", "pregunta_relacionada"
    confidence: float
    reasoning: str
    should_handle_contextually: bool


class ConversationContextManager:
    """
    Gestor centralizado de contexto conversacional

    Responsabilidades:
    - Mantener historial de conversación
    - Gestionar estado conversacional
    - Analizar si mensajes son continuaciones
    - Proporcionar contexto optimizado para intérpretes
    """

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.history = []
        self.state = {
            "waiting_for": None,
            "last_error": None,
            "last_suggestion": None,
            "last_action": None,
            "context_data": {},
            "session_start": datetime.now().isoformat()
        }
        self.max_history = 50

    def add_message(self, role: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """
        Agrega un mensaje al historial conversacional

        Args:
            role: "user" o "assistant"
            message: Contenido del mensaje
            metadata: Información adicional (acción, datos, etc.)
        """
        entry = {
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.history.append(entry)

        # Mantener límite de historial
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Actualiza el estado conversacional

        Args:
            updates: Diccionario con las actualizaciones del estado
        """
        self.state.update(updates)



    def analyze_message(self, message: str) -> ContextAnalysis:
        """
        Analiza si un mensaje es continuación de la conversación previa

        Args:
            message: Mensaje del usuario a analizar

        Returns:
            ContextAnalysis con el resultado del análisis
        """
        try:
            # Si no hay contexto previo, no es continuación
            if not self.state.get("waiting_for") and len(self.history) <= 1:
                return ContextAnalysis(
                    is_continuation=False,
                    continuation_type=None,
                    confidence=1.0,
                    reasoning="No hay contexto previo",
                    should_handle_contextually=False
                )

            # Formatear contexto para el LLM
            context_prompt = self._build_analysis_prompt(message)

            # Obtener análisis del LLM
            response = self.gemini_client.send_prompt_sync(context_prompt)
            if response:
                analysis_data = self.gemini_client.parse_json_response(response)
                if analysis_data:
                    return ContextAnalysis(
                        is_continuation=analysis_data.get("es_continuacion", False),
                        continuation_type=analysis_data.get("tipo_continuacion"),
                        confidence=analysis_data.get("confianza", 0.0),
                        reasoning=analysis_data.get("razonamiento", ""),
                        should_handle_contextually=analysis_data.get("es_continuacion", False)
                    )

            # Fallback si LLM falla
            return ContextAnalysis(
                is_continuation=False,
                continuation_type=None,
                confidence=0.0,
                reasoning="Error en análisis LLM",
                should_handle_contextually=False
            )

        except Exception as e:
            self.logger.error(f"Error en análisis contextual: {e}")
            return ContextAnalysis(
                is_continuation=False,
                continuation_type=None,
                confidence=0.0,
                reasoning=f"Error: {str(e)}",
                should_handle_contextually=False
            )

    def _build_analysis_prompt(self, message: str) -> str:
        """
        Construye el prompt para análisis contextual
        """
        recent_history = self._format_recent_history()

        return f"""
Eres un experto en análisis conversacional. Determina si el mensaje del usuario es una CONTINUACIÓN de la conversación previa o una CONSULTA NUEVA.

MENSAJE ACTUAL: "{message}"

CONTEXTO CONVERSACIONAL:
- Sistema está esperando: {self.state.get('waiting_for', 'nada')}
- Última sugerencia: {self.state.get('last_suggestion', 'ninguna')}
- Último error: {self.state.get('last_error', 'ninguno')}
- Datos relevantes: {self.state.get('context_data', {})}

HISTORIAL RECIENTE:
{recent_history}

TIPOS DE CONTINUACIÓN:
- "confirmacion": Usuario confirma una sugerencia del sistema
- "aclaracion": Usuario proporciona información adicional solicitada
- "seleccion": Usuario selecciona de opciones mostradas
- "pregunta_relacionada": Usuario hace pregunta sobre el contexto actual

EJEMPLOS DE CONTINUACIÓN:
- Sistema sugiere constancia de estudios → Usuario: "sí", "perfecto", "hazla", "mejor esa"
- Sistema muestra múltiples alumnos → Usuario: "el segundo", "Juan Pérez", "más detalles del primero"
- Sistema pregunta algo → Usuario responde directamente
- Sistema da error → Usuario: "¿por qué?", "¿cómo puedo solucionarlo?"

EJEMPLOS DE CONSULTA NUEVA:
- Usuario cambia completamente de tema
- Usuario hace nueva búsqueda sin relación al contexto
- Usuario inicia nueva tarea

RESPONDE ÚNICAMENTE con JSON:
{{
    "es_continuacion": true/false,
    "tipo_continuacion": "confirmacion|aclaracion|seleccion|pregunta_relacionada|null",
    "confianza": 0.0-1.0,
    "razonamiento": "Explicación breve de la decisión"
}}
"""

    def _format_recent_history(self) -> str:
        """
        Formatea el historial reciente para el prompt
        """
        if not self.history:
            return "Sin historial previo"

        # Tomar últimos 4 mensajes
        recent = self.history[-4:]
        formatted = []

        for msg in recent:
            role = "Usuario" if msg.get('role') == 'user' else "Sistema"
            message = msg.get('message', '')[:200]  # Limitar longitud
            formatted.append(f"{role}: {message}")

        return "\n".join(formatted)

    def get_context_for_interpreter(self, user_message: str) -> InterpretationContext:
        """
        Crea un InterpretationContext optimizado para los intérpretes

        Args:
            user_message: Mensaje actual del usuario

        Returns:
            InterpretationContext con todo el contexto necesario
        """
        context = InterpretationContext(
            user_message=user_message,
            conversation_state=self.state.copy(),
            user_preferences={}
        )

        # Agregar atributos adicionales
        context.conversation_history = self.history.copy()
        context.recent_messages = self.history[-10:] if self.history else []

        return context

    def handle_error_with_context(self, error_message: str) -> None:
        """
        Maneja errores específicos y actualiza el estado conversacional

        Args:
            error_message: Mensaje de error recibido
        """
        # Detectar errores específicos y actualizar estado
        if "calificaciones registradas" in error_message:
            alumno_nombre = self._extract_student_name_from_error(error_message)
            self.update_state({
                "last_error": "calificaciones_faltantes",
                "last_suggestion": "constancia_estudios",
                "waiting_for": "confirmacion_constancia_estudios",
                "context_data": {"alumno": alumno_nombre} if alumno_nombre else {}
            })
        elif "datos escolares" in error_message:
            self.update_state({
                "last_error": "datos_escolares_faltantes",
                "last_suggestion": "verificar_datos",
                "waiting_for": "aclaracion_datos"
            })

    def _extract_student_name_from_error(self, error_message: str) -> Optional[str]:
        """
        Extrae el nombre del alumno del mensaje de error
        """
        import re

        # Buscar patrón "para [NOMBRE]" en el mensaje
        pattern = r"para\s+([A-ZÁÉÍÓÚÑ\s]+):"
        match = re.search(pattern, error_message)
        if match:
            return match.group(1).strip()

        # Si no se encuentra, buscar en historial reciente
        if self.history:
            for msg in reversed(self.history):
                if msg.get('role') == 'user':
                    last_message = msg.get('message', '')
                    name_pattern = r"([A-ZÁÉÍÓÚÑ]{2,}\s+[A-ZÁÉÍÓÚÑ\s]+[A-ZÁÉÍÓÚÑ]{2,})"
                    match = re.search(name_pattern, last_message)
                    if match:
                        return match.group(1).strip()
                    break

        return None

    def clear_session(self) -> None:
        """
        Limpia el contexto para una nueva sesión
        """
        self.history.clear()
        self.state = {
            "waiting_for": None,
            "last_error": None,
            "last_suggestion": None,
            "last_action": None,
            "context_data": {},
            "session_start": datetime.now().isoformat()
        }


    def get_state_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado actual para debugging
        """
        return {
            "history_length": len(self.history),
            "current_state": self.state,
            "last_messages": self.history[-3:] if self.history else []
        }
