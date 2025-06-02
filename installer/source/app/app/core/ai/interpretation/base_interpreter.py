"""
Clases base para el sistema de interpretación de IA
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class InterpretationContext:
    """
    Contexto para la interpretación de mensajes
    """
    user_message: str
    conversation_state: Dict[str, Any]
    user_preferences: Dict[str, Any]

    # Contexto conversacional
    conversation_history: Optional[List[Dict]] = None
    last_query_results: Optional[Dict] = None
    external_conversation_history: Optional[List[Dict]] = None
    recent_messages: Optional[List[Dict]] = None

    # Panel PDF para transformaciones
    pdf_panel: Optional[Any] = None

    # Timestamp
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class InterpretationResult:
    """
    Resultado de la interpretación
    """
    action: str
    parameters: Dict[str, Any]
    confidence: float = 1.0
    requires_confirmation: bool = False

    # Información adicional
    reasoning: Optional[str] = None
    suggested_followup: Optional[str] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}

class BaseInterpreter:
    """
    Clase base para todos los intérpretes
    """

    def __init__(self, name: str, priority: int = 0):
        """
        Inicializa el intérprete base

        Args:
            name: Nombre del intérprete
            priority: Prioridad del intérprete (mayor número = mayor prioridad)
        """
        self.name = name
        self.priority = priority
        self.logger = None

        # Inicializar logger si está disponible
        try:
            from app.core.logging import get_logger
            self.logger = get_logger(f"{__name__}.{name}")
        except ImportError:
            pass

    def can_handle(self, context: InterpretationContext) -> bool:
        """
        Determina si este intérprete puede manejar el contexto dado

        Args:
            context: Contexto de interpretación

        Returns:
            True si puede manejar, False en caso contrario
        """
        raise NotImplementedError("Subclases deben implementar can_handle")

    def interpret(self, context: InterpretationContext) -> InterpretationResult:
        """
        Interpreta el contexto y devuelve un resultado

        Args:
            context: Contexto de interpretación

        Returns:
            Resultado de la interpretación
        """
        raise NotImplementedError("Subclases deben implementar interpret")

    def _log_debug(self, message: str):
        """Registra mensaje de debug si el logger está disponible"""
        if self.logger:
            self.logger.debug(f"[{self.name}] {message}")

    def _log_info(self, message: str):
        """Registra mensaje de info si el logger está disponible"""
        if self.logger:
            self.logger.info(f"[{self.name}] {message}")

    def _log_error(self, message: str):
        """Registra mensaje de error si el logger está disponible"""
        if self.logger:
            self.logger.error(f"[{self.name}] {message}")

class InterpreterChain:
    """
    Cadena de intérpretes que procesa contextos en orden
    """

    def __init__(self):
        self.interpreters: List[BaseInterpreter] = []
        self.logger = None

        try:
            from app.core.logging import get_logger
            self.logger = get_logger(__name__)
        except ImportError:
            pass

    def add_interpreter(self, interpreter: BaseInterpreter):
        """
        Agrega un intérprete a la cadena

        Args:
            interpreter: Intérprete a agregar
        """
        self.interpreters.append(interpreter)
        if self.logger:
            self.logger.debug(f"Intérprete agregado: {interpreter.name}")

    def process(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        Procesa el contexto a través de la cadena de intérpretes

        Args:
            context: Contexto a procesar

        Returns:
            Resultado del primer intérprete que pueda manejar el contexto
        """
        for interpreter in self.interpreters:
            try:
                if interpreter.can_handle(context):
                    if self.logger:
                        self.logger.debug(f"Procesando con intérprete: {interpreter.name}")

                    result = interpreter.interpret(context)

                    if self.logger:
                        self.logger.debug(f"Resultado: {result.action}")

                    return result

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error en intérprete {interpreter.name}: {e}")
                continue

        if self.logger:
            self.logger.warning("Ningún intérprete pudo manejar el contexto")

        return None

# Utilidades para crear contextos y resultados comunes

def create_error_result(error_message: str, action: str = "error") -> InterpretationResult:
    """
    Crea un resultado de error estándar

    Args:
        error_message: Mensaje de error
        action: Tipo de acción (por defecto "error")

    Returns:
        Resultado de interpretación con error
    """
    return InterpretationResult(
        action=action,
        parameters={
            "message": error_message,
            "error": True
        },
        confidence=1.0
    )

def create_success_result(action: str, message: str, **kwargs) -> InterpretationResult:
    """
    Crea un resultado de éxito estándar

    Args:
        action: Tipo de acción
        message: Mensaje de éxito
        **kwargs: Parámetros adicionales

    Returns:
        Resultado de interpretación exitoso
    """
    parameters = {
        "message": message,
        "success": True,
        **kwargs
    }

    return InterpretationResult(
        action=action,
        parameters=parameters,
        confidence=1.0
    )

def extract_conversation_context(context: InterpretationContext) -> str:
    """
    Extrae el contexto conversacional en formato texto

    Args:
        context: Contexto de interpretación

    Returns:
        Contexto conversacional formateado
    """
    if not context.conversation_history:
        return ""

    formatted_context = "=== CONTEXTO CONVERSACIONAL ===\n"

    # Últimos mensajes
    recent_messages = context.conversation_history[-6:] if len(context.conversation_history) > 6 else context.conversation_history

    for msg in recent_messages:
        role_emoji = "👤" if msg.get('role') == 'user' else "🤖"
        content = msg.get('content', '')

        # Truncar mensajes largos
        if len(content) > 100:
            content = content[:100] + "..."

        formatted_context += f"{role_emoji} {msg.get('role', 'unknown').title()}: {content}\n"

    return formatted_context
