"""
Modelo para representar datos escolares de un alumno
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import json

@dataclass
class DatosEscolares:
    """Clase que representa los datos escolares de un alumno"""
    alumno_id: int
    ciclo_escolar: str
    grado: int
    grupo: str
    turno: str = "MATUTINO"
    escuela: Optional[str] = None
    cct: Optional[str] = None
    calificaciones: List[Dict[str, Any]] = field(default_factory=list)
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario"""
        return {
            "id": self.id,
            "alumno_id": self.alumno_id,
            "ciclo_escolar": self.ciclo_escolar,
            "grado": self.grado,
            "grupo": self.grupo,
            "turno": self.turno,
            "escuela": self.escuela,
            "cct": self.cct,
            "calificaciones": self.calificaciones
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatosEscolares':
        """Crea un objeto DatosEscolares a partir de un diccionario"""
        # Manejar calificaciones que pueden venir como JSON
        calificaciones = data.get("calificaciones", [])
        if isinstance(calificaciones, str):
            try:
                calificaciones = json.loads(calificaciones)
            except json.JSONDecodeError:
                calificaciones = []
        
        return cls(
            id=data.get("id"),
            alumno_id=data.get("alumno_id", 0),
            ciclo_escolar=data.get("ciclo_escolar", ""),
            grado=data.get("grado", 0),
            grupo=data.get("grupo", ""),
            turno=data.get("turno", "MATUTINO"),
            escuela=data.get("escuela"),
            cct=data.get("cct"),
            calificaciones=calificaciones
        )
    
    def __str__(self) -> str:
        """Representación en cadena de los datos escolares"""
        return f"{self.grado}° {self.grupo} - {self.ciclo_escolar}"
