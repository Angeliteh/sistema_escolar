"""
Modelo para representar una constancia
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class Constancia:
    """Clase que representa una constancia"""
    alumno_id: int
    tipo: str  # "traslado", "estudio", "calificaciones"
    ruta_archivo: str
    id: Optional[int] = None
    fecha_generacion: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario"""
        return {
            "id": self.id,
            "alumno_id": self.alumno_id,
            "tipo": self.tipo,
            "ruta_archivo": self.ruta_archivo,
            "fecha_generacion": self.fecha_generacion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Constancia':
        """Crea un objeto Constancia a partir de un diccionario"""
        return cls(
            id=data.get("id"),
            alumno_id=data.get("alumno_id", 0),
            tipo=data.get("tipo", ""),
            ruta_archivo=data.get("ruta_archivo", ""),
            fecha_generacion=data.get("fecha_generacion")
        )
    
    def __str__(self) -> str:
        """Representación en cadena de la constancia"""
        return f"Constancia de {self.tipo} - {self.fecha_generacion}"
