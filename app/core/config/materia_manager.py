"""
🎓 GESTOR DE MATERIAS DINÁMICO
Maneja configuración de materias por escuela y grado
"""

from typing import List, Dict, Optional, Any
from app.core.logging import get_logger

class MateriaManager:
    """
    🎓 GESTOR DE MATERIAS DINÁMICO
    
    Responsabilidades:
    - Obtener materias configuradas por grado
    - Validar estructura de calificaciones
    - Generar plantillas de calificaciones
    - Calcular promedios según configuración
    """
    
    def __init__(self, school_config_manager=None):
        self.logger = get_logger(__name__)
        if school_config_manager:
            self.school_config = school_config_manager
        else:
            from app.core.config.school_config_manager import get_school_config_manager
            self.school_config = get_school_config_manager()
    
    def get_materias_for_grade(self, grado: int) -> List[str]:
        """
        🎯 OBTENER MATERIAS PARA UN GRADO ESPECÍFICO
        
        Args:
            grado: Número de grado (1-6 primaria, 1-3 secundaria, etc.)
            
        Returns:
            Lista de nombres de materias configuradas para ese grado
        """
        try:
            materias_config = self.school_config.get_config_value(
                "academic_info.materias_por_grado", {}
            )
            
            materias = materias_config.get(str(grado), [])
            
            if not materias:
                self.logger.warning(f"No hay materias configuradas para grado {grado}")
                # Fallback: materias básicas
                materias = self._get_default_materias_for_grade(grado)
            
            self.logger.info(f"📚 Materias para grado {grado}: {len(materias)} materias")
            return materias
            
        except Exception as e:
            self.logger.error(f"Error obteniendo materias para grado {grado}: {e}")
            return self._get_default_materias_for_grade(grado)
    
    def _get_default_materias_for_grade(self, grado: int) -> List[str]:
        """Materias por defecto si no hay configuración"""
        education_level = self.school_config.get_education_level().upper()
        
        if education_level == "PRIMARIA":
            if grado <= 2:
                return ["Matemáticas", "Español", "Conocimiento del Medio"]
            else:
                return ["Matemáticas", "Español", "Ciencias Naturales", "Historia"]
        elif education_level == "SECUNDARIA":
            return ["Matemáticas", "Español", "Ciencias", "Historia", "Geografía"]
        else:
            return ["Área 1", "Área 2", "Área 3"]
    
    def validate_calificaciones_structure(self, grado: int, calificaciones: List[Dict]) -> Dict[str, Any]:
        """
        ✅ VALIDAR ESTRUCTURA DE CALIFICACIONES
        
        Args:
            grado: Grado del alumno
            calificaciones: Lista de calificaciones a validar
            
        Returns:
            Dict con resultado de validación y detalles
        """
        try:
            materias_esperadas = set(self.get_materias_for_grade(grado))
            materias_recibidas = set(cal.get('nombre', cal.get('materia', '')) for cal in calificaciones)
            
            # Verificar materias faltantes y extras
            materias_faltantes = materias_esperadas - materias_recibidas
            materias_extras = materias_recibidas - materias_esperadas
            
            is_valid = len(materias_faltantes) == 0
            
            result = {
                "is_valid": is_valid,
                "materias_esperadas": list(materias_esperadas),
                "materias_recibidas": list(materias_recibidas),
                "materias_faltantes": list(materias_faltantes),
                "materias_extras": list(materias_extras),
                "total_esperadas": len(materias_esperadas),
                "total_recibidas": len(materias_recibidas)
            }
            
            if is_valid:
                self.logger.info(f"✅ Calificaciones válidas para grado {grado}")
            else:
                self.logger.warning(f"⚠️ Calificaciones incompletas para grado {grado}: faltan {materias_faltantes}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validando calificaciones para grado {grado}: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "materias_esperadas": [],
                "materias_recibidas": []
            }
    
    def generate_empty_calificaciones_template(self, grado: int) -> List[Dict]:
        """
        📋 GENERAR PLANTILLA VACÍA DE CALIFICACIONES
        
        Args:
            grado: Grado para el cual generar la plantilla
            
        Returns:
            Lista de diccionarios con estructura de calificaciones vacía
        """
        try:
            materias = self.get_materias_for_grade(grado)
            periodos = self.school_config.get_config_value(
                "academic_info.evaluacion_config.periodos", 
                ["Periodo 1", "Periodo 2", "Periodo 3"]
            )
            
            calificaciones = []
            for materia in materias:
                cal_materia = {
                    "nombre": materia,
                    "materia": materia  # Alias para compatibilidad
                }
                
                # Agregar campos por periodo
                for i, periodo in enumerate(periodos, 1):
                    cal_materia[f"periodo_{i}"] = None
                
                # Campo de promedio
                cal_materia["promedio"] = None
                
                calificaciones.append(cal_materia)
            
            self.logger.info(f"📋 Plantilla generada para grado {grado}: {len(calificaciones)} materias")
            return calificaciones
            
        except Exception as e:
            self.logger.error(f"Error generando plantilla para grado {grado}: {e}")
            return []
    
    def calculate_promedio_materia(self, calificacion_materia: Dict) -> Optional[float]:
        """
        🧮 CALCULAR PROMEDIO DE UNA MATERIA
        
        Args:
            calificacion_materia: Dict con calificaciones de una materia
            
        Returns:
            Promedio calculado o None si no se puede calcular
        """
        try:
            periodos = self.school_config.get_config_value(
                "academic_info.evaluacion_config.periodos", 
                ["Periodo 1", "Periodo 2", "Periodo 3"]
            )
            
            calificaciones_validas = []
            for i in range(1, len(periodos) + 1):
                cal = calificacion_materia.get(f"periodo_{i}")
                if cal is not None and isinstance(cal, (int, float)) and cal > 0:
                    calificaciones_validas.append(float(cal))
            
            if len(calificaciones_validas) > 0:
                promedio = sum(calificaciones_validas) / len(calificaciones_validas)
                
                # Aplicar redondeo según configuración
                decimales = self.school_config.get_config_value(
                    "academic_info.evaluacion_config.escala_calificaciones.decimales", 1
                )
                
                return round(promedio, decimales)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculando promedio de materia: {e}")
            return None
    
    def get_evaluation_config(self) -> Dict[str, Any]:
        """
        ⚙️ OBTENER CONFIGURACIÓN DE EVALUACIÓN
        
        Returns:
            Dict con configuración de evaluación (periodos, escala, etc.)
        """
        return self.school_config.get_config_value(
            "academic_info.evaluacion_config",
            {
                "periodos": ["Periodo 1", "Periodo 2", "Periodo 3"],
                "escala_calificaciones": {
                    "minima": 5.0,
                    "maxima": 10.0,
                    "aprobatoria": 6.0,
                    "decimales": 1
                },
                "mostrar_promedio_general": True,
                "calcular_promedio_automatico": True
            }
        )
    
    def get_all_materias_configured(self) -> Dict[str, List[str]]:
        """
        📚 OBTENER TODAS LAS MATERIAS CONFIGURADAS
        
        Returns:
            Dict con materias por grado
        """
        return self.school_config.get_config_value("academic_info.materias_por_grado", {})
    
    def is_materia_valid_for_grade(self, materia: str, grado: int) -> bool:
        """
        ✅ VERIFICAR SI UNA MATERIA ES VÁLIDA PARA UN GRADO
        
        Args:
            materia: Nombre de la materia
            grado: Grado a verificar
            
        Returns:
            True si la materia es válida para el grado
        """
        materias_grado = self.get_materias_for_grade(grado)
        return materia in materias_grado


# 🌟 INSTANCIA GLOBAL
_materia_manager = None

def get_materia_manager() -> MateriaManager:
    """
    Obtiene la instancia global del MateriaManager
    
    Returns:
        Instancia del MateriaManager
    """
    global _materia_manager
    
    if _materia_manager is None:
        _materia_manager = MateriaManager()
    
    return _materia_manager
