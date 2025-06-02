"""
Clase base para comandos
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class Command(ABC):
    """Clase base para todos los comandos"""
    
    @abstractmethod
    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando
        
        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        pass
