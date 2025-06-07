"""
🏫 GESTOR DE CONFIGURACIÓN ESCOLAR DINÁMICO

Centraliza toda la información específica de la escuela para hacer el sistema
completamente dinámico y reutilizable para cualquier institución educativa.

ELIMINA HARDCODE DE:
- Nombres de escuela
- Cantidad de alumnos
- Grados disponibles
- Turnos y grupos
- Información específica

PERMITE:
- Cambiar de escuela solo cambiando school_config.json
- Adaptar automáticamente todos los prompts
- Detectar estructura de BD automáticamente
- Sistema 100% reutilizable
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from app.core.logging import get_logger


class SchoolConfigManager:
    """
    🎯 GESTOR CENTRALIZADO DE CONFIGURACIÓN ESCOLAR
    
    Hace el sistema completamente dinámico eliminando todo hardcode
    específico de la escuela actual.
    """
    
    def __init__(self, config_path: str = "school_config.json", db_path: str = None):
        self.logger = get_logger(__name__)
        self.config_path = Path(config_path)
        self.db_path = db_path
        self._config_cache = None
        self._db_stats_cache = None
        
        # Cargar configuración
        self._load_config()
        
        # Auto-detectar estadísticas de BD si está disponible
        if db_path:
            self._detect_database_stats()
    
    def _load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                self.logger.info(f"✅ Configuración escolar cargada desde: {self.config_path}")
            else:
                self.logger.warning(f"⚠️ Archivo de configuración no encontrado: {self.config_path}")
                self._config_cache = self._get_default_config()
        except Exception as e:
            self.logger.error(f"❌ Error cargando configuración: {e}")
            self._config_cache = self._get_default_config()
    
    def _detect_database_stats(self):
        """Auto-detecta estadísticas de la base de datos"""
        if not self.db_path or not Path(self.db_path).exists():
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Detectar cantidad de alumnos
            cursor.execute("SELECT COUNT(*) FROM alumnos")
            total_students = cursor.fetchone()[0]
            
            # Detectar grados disponibles
            cursor.execute("SELECT DISTINCT grado FROM datos_escolares ORDER BY grado")
            grades = [str(row[0]) for row in cursor.fetchall()]
            
            # Detectar grupos disponibles
            cursor.execute("SELECT DISTINCT grupo FROM datos_escolares ORDER BY grupo")
            groups = [row[0] for row in cursor.fetchall()]
            
            # Detectar turnos disponibles
            cursor.execute("SELECT DISTINCT turno FROM datos_escolares ORDER BY turno")
            shifts = [row[0] for row in cursor.fetchall()]
            
            self._db_stats_cache = {
                "total_students": total_students,
                "available_grades": grades,
                "available_groups": groups,
                "available_shifts": shifts
            }
            
            self.logger.info(f"✅ Estadísticas de BD detectadas: {total_students} alumnos, grados {grades}")
            conn.close()
            
        except Exception as e:
            self.logger.error(f"❌ Error detectando estadísticas de BD: {e}")
            self._db_stats_cache = {}
    
    def get_school_name(self) -> str:
        """Obtiene el nombre de la escuela"""
        return self._config_cache.get("school_info", {}).get("name", "ESCUELA SIN NOMBRE")
    
    def get_school_cct(self) -> str:
        """Obtiene la CCT de la escuela"""
        return self._config_cache.get("school_info", {}).get("cct", "")
    
    def get_director_name(self) -> str:
        """Obtiene el nombre del director"""
        return self._config_cache.get("school_info", {}).get("director", "")
    
    def get_school_address(self) -> str:
        """Obtiene la dirección de la escuela"""
        return self._config_cache.get("school_info", {}).get("address", "")
    
    def get_current_year(self) -> str:
        """Obtiene el ciclo escolar actual"""
        return self._config_cache.get("academic_info", {}).get("current_year", "2024-2025")
    
    def get_education_level(self) -> str:
        """Obtiene el nivel educativo"""
        return self._config_cache.get("academic_info", {}).get("education_level", "PRIMARIA")
    
    def get_available_grades(self) -> List[str]:
        """Obtiene los grados disponibles (dinámico desde BD o config)"""
        # Priorizar datos de BD si están disponibles
        if self._db_stats_cache and "available_grades" in self._db_stats_cache:
            return self._db_stats_cache["available_grades"]
        
        # Fallback a configuración
        grades = self._config_cache.get("academic_info", {}).get("grades", [1, 2, 3, 4, 5, 6])
        return [str(g) for g in grades]
    
    def get_available_groups(self) -> List[str]:
        """Obtiene los grupos disponibles (dinámico desde BD o config)"""
        # Priorizar datos de BD si están disponibles
        if self._db_stats_cache and "available_groups" in self._db_stats_cache:
            return self._db_stats_cache["available_groups"]
        
        # Fallback a configuración
        return self._config_cache.get("academic_info", {}).get("groups", ["A", "B", "C"])
    
    def get_available_shifts(self) -> List[str]:
        """Obtiene los turnos disponibles (dinámico desde BD o config)"""
        # Priorizar datos de BD si están disponibles
        if self._db_stats_cache and "available_shifts" in self._db_stats_cache:
            return self._db_stats_cache["available_shifts"]
        
        # Fallback a configuración
        return self._config_cache.get("academic_info", {}).get("shifts", ["MATUTINO", "VESPERTINO"])
    
    def get_total_students(self) -> int:
        """Obtiene el total de estudiantes (dinámico desde BD)"""
        # Priorizar datos de BD si están disponibles
        if self._db_stats_cache and "total_students" in self._db_stats_cache:
            return self._db_stats_cache["total_students"]
        
        # Fallback a estimación
        return 0
    
    def get_school_identity_text(self) -> str:
        """Genera texto de identidad dinámico para prompts"""
        school_name = self.get_school_name()
        education_level = self.get_education_level().lower()
        total_students = self.get_total_students()
        
        return f"""🤖 IDENTIDAD DEL SISTEMA:
Soy el ASISTENTE INTELIGENTE de la escuela {education_level} "{school_name}".
No soy una herramienta, soy el cerebro digital de la escuela que conoce a todos los estudiantes.

🎯 MI PROPÓSITO:
- Gestionar información de {total_students} estudiantes registrados
- Generar constancias y documentos oficiales
- Proporcionar estadísticas y análisis académicos
- Facilitar consultas rápidas y precisas sobre cualquier alumno

🧠 MIS CAPACIDADES PRINCIPALES:
- Búsqueda inteligente por nombre, CURP, matrícula o cualquier criterio
- Generación automática de constancias oficiales
- Análisis estadístico y distribuciones por grado, grupo, turno
- Transformación de documentos PDF
- Respuestas contextuales basadas en datos reales"""
    
    def get_school_context_text(self) -> str:
        """Genera texto de contexto escolar dinámico para prompts"""
        school_name = self.get_school_name()
        education_level = self.get_education_level().lower()
        current_year = self.get_current_year()
        total_students = self.get_total_students()
        grades = self.get_available_grades()
        groups = self.get_available_groups()
        shifts = self.get_available_shifts()
        
        grades_text = "°, ".join(grades) + "°"
        groups_text = ", ".join(groups)
        shifts_text = ", ".join(shifts)
        
        return f"""🏫 CONTEXTO DE LA ESCUELA:
- Escuela {education_level} "{school_name}"
- Ciclo escolar {current_year}
- {total_students} estudiantes registrados en grados {grades_text}
- Grupos disponibles: {groups_text}
- Turnos: {shifts_text}
- Sistema integral de gestión académica y administrativa
- Base de datos completa con información académica y personal"""
    
    def get_data_scope_text(self) -> str:
        """Genera texto de alcance de datos dinámico"""
        total_students = self.get_total_students()
        grades = self.get_available_grades()
        shifts = self.get_available_shifts()
        
        grades_text = "°, ".join(grades) + "°"
        shifts_text = "/".join([s.lower() for s in shifts])
        
        return f"{total_students} alumnos activos, grados {grades_text}, turnos {shifts_text}"
    
    def refresh_database_stats(self):
        """Refresca las estadísticas de la base de datos"""
        if self.db_path:
            self._detect_database_stats()

    def get_materias_por_grado(self) -> Dict[str, List[str]]:
        """Obtiene configuración de materias por grado"""
        return self.get_config_value("academic_info.materias_por_grado", {})

    def get_materias_for_grade(self, grado: int) -> List[str]:
        """Obtiene materias para un grado específico"""
        materias_config = self.get_materias_por_grado()
        return materias_config.get(str(grado), [])

    def get_evaluation_config(self) -> Dict:
        """Obtiene configuración de evaluación"""
        return self.get_config_value("academic_info.evaluacion_config", {})

    def get_periodos_evaluacion(self) -> List[str]:
        """Obtiene periodos de evaluación configurados"""
        return self.get_evaluation_config().get("periodos", ["Periodo 1", "Periodo 2", "Periodo 3"])

    def get_escala_calificaciones(self) -> Dict:
        """Obtiene configuración de escala de calificaciones"""
        return self.get_evaluation_config().get("escala_calificaciones", {
            "minima": 5.0,
            "maxima": 10.0,
            "aprobatoria": 6.0,
            "decimales": 1
        })

    def _get_default_config(self) -> Dict:
        """Configuración por defecto si no se encuentra el archivo"""
        return {
            "school_info": {
                "name": "ESCUELA EJEMPLO",
                "cct": "",
                "director": "",
                "address": ""
            },
            "academic_info": {
                "current_year": "2024-2025",
                "grades": [1, 2, 3, 4, 5, 6],
                "groups": ["A", "B"],
                "shifts": ["MATUTINO"],
                "education_level": "PRIMARIA"
            }
        }


# Instancia global para uso en todo el sistema
_school_config_manager = None

def get_school_config_manager(db_path: str = None) -> SchoolConfigManager:
    """
    Obtiene la instancia global del SchoolConfigManager
    
    Args:
        db_path: Ruta a la base de datos (opcional, para auto-detección)
    
    Returns:
        Instancia del SchoolConfigManager
    """
    global _school_config_manager
    
    if _school_config_manager is None:
        _school_config_manager = SchoolConfigManager(db_path=db_path)
    elif db_path and _school_config_manager.db_path != db_path:
        # Actualizar ruta de BD si cambió
        _school_config_manager.db_path = db_path
        _school_config_manager.refresh_database_stats()
    
    return _school_config_manager
