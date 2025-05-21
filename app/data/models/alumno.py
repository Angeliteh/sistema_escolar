"""
Modelo para representar un alumno
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class Alumno:
    """Clase que representa un alumno"""
    curp: str
    nombre: str
    matricula: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    id: Optional[int] = None
    fecha_registro: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario"""
        return {
            "id": self.id,
            "curp": self.curp,
            "nombre": self.nombre,
            "matricula": self.matricula,
            "fecha_nacimiento": self.fecha_nacimiento,
            "fecha_registro": self.fecha_registro
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alumno':
        """Crea un objeto Alumno a partir de un diccionario"""
        return cls(
            id=data.get("id"),
            curp=data.get("curp", ""),
            nombre=data.get("nombre", ""),
            matricula=data.get("matricula"),
            fecha_nacimiento=data.get("fecha_nacimiento"),
            fecha_registro=data.get("fecha_registro")
        )
    
    def __str__(self) -> str:
        """Representación en cadena del alumno"""
        return f"{self.nombre} ({self.curp})"
