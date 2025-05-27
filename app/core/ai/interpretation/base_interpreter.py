"""
Sistema base de interpretación para comandos de IA
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class InterpretationContext:
    """Contexto para la interpretación de comandos"""
    user_message: str
    current_pdf: Optional[str] = None
    conversation_state: Dict[str, Any] = None
    user_preferences: Dict[str, Any] = None

    def __post_init__(self):
        if self.conversation_state is None:
            self.conversation_state = {}
        if self.user_preferences is None:
            self.user_preferences = {}

@dataclass
class InterpretationResult:
    """Resultado de la interpretación"""
    action: str
    parameters: Dict[str, Any]
    confidence: float = 1.0
    requires_confirmation: bool = False
    context_updates: Dict[str, Any] = None

    def __post_init__(self):
        if self.context_updates is None:
            self.context_updates = {}

class BaseInterpreter(ABC):
    """Clase base para interpretadores de comandos"""

    def __init__(self, name: str, priority: int = 0):
        """
        Inicializa el interpretador

        Args:
            name: Nombre del interpretador
            priority: Prioridad (mayor número = mayor prioridad)
        """
        self.name = name
        self.priority = priority
        self.supported_actions = self._get_supported_actions()

    @abstractmethod
    def _get_supported_actions(self) -> List[str]:
        """Retorna la lista de acciones que este interpretador puede manejar"""
        pass

    @abstractmethod
    def can_handle(self, context: InterpretationContext) -> bool:
        """
        Determina si este interpretador puede manejar el contexto dado

        Args:
            context: Contexto de interpretación

        Returns:
            True si puede manejar el contexto
        """
        pass

    @abstractmethod
    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        Interpreta el contexto y retorna un resultado

        Args:
            context: Contexto de interpretación

        Returns:
            Resultado de interpretación o None si no puede interpretar
        """
        pass

    def get_prompt_template(self, context: InterpretationContext) -> str:
        """
        Genera el template de prompt específico para este interpretador

        Args:
            context: Contexto de interpretación

        Returns:
            Template de prompt
        """
        return self._create_base_prompt(context)

    def _create_base_prompt(self, context: InterpretationContext) -> str:
        """Crea el prompt base común"""
        actions_list = "\n".join([f"- {action}" for action in self.supported_actions])

        return f"""
        Eres un asistente especializado en {self.name}.

        Acciones disponibles:
        {actions_list}

        Usuario dice: "{context.user_message}"

        Responde ÚNICAMENTE con JSON:
        {{
            "accion": "nombre_accion",
            "parametros": {{"param": "valor"}},
            "confianza": 0.9
        }}
        """

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Valida los parámetros para una acción específica

        Args:
            action: Acción a validar
            parameters: Parámetros a validar

        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Implementación base - los interpretadores específicos pueden sobrescribir
        return True, ""

    def post_process_result(self, result: InterpretationResult, context: InterpretationContext) -> InterpretationResult:
        """
        Post-procesa el resultado de interpretación

        Args:
            result: Resultado original
            context: Contexto de interpretación

        Returns:
            Resultado post-procesado
        """
        # Implementación base - los interpretadores específicos pueden sobrescribir
        return result

class CompositeInterpreter:
    """Interpretador compuesto que maneja múltiples interpretadores"""

    def __init__(self):
        self.interpreters: List[BaseInterpreter] = []

    def register_interpreter(self, interpreter: BaseInterpreter):
        """Registra un nuevo interpretador"""
        self.interpreters.append(interpreter)
        # Ordenar por prioridad (mayor prioridad primero)
        self.interpreters.sort(key=lambda x: x.priority, reverse=True)

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        Intenta interpretar usando todos los interpretadores registrados

        Args:
            context: Contexto de interpretación

        Returns:
            Primer resultado exitoso o None
        """
        for interpreter in self.interpreters:
            if interpreter.can_handle(context):
                try:
                    result = interpreter.interpret(context)
                    if result:
                        return interpreter.post_process_result(result, context)
                except Exception as e:
                    # Error en interpretador - usar logging si está disponible
                    try:
                        from app.core.logging import get_logger
                        logger = get_logger(__name__)
                        logger.error(f"Error en interpretador {interpreter.name}: {str(e)}")
                    except ImportError:
                        print(f"Error en interpretador {interpreter.name}: {str(e)}")
                    continue

        return None

    def get_all_supported_actions(self) -> Dict[str, str]:
        """Retorna todas las acciones soportadas por interpretador"""
        actions = {}
        for interpreter in self.interpreters:
            for action in interpreter.supported_actions:
                actions[action] = interpreter.name
        return actions
