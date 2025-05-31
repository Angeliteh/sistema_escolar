"""
🔍 ANALIZADOR DINÁMICO DE BASE DE DATOS
Proporciona información estructural en tiempo real para los LLMs
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

class DatabaseAnalyzer:
    """
    🔍 ANALIZADOR DINÁMICO DE ESTRUCTURA DE BASE DE DATOS
    
    Propósito:
    - Extraer estructura real de la BD en tiempo real
    - Proporcionar información a LLMs para criterios precisos
    - Normalizar nombres de campos y materias
    - Evitar errores de filtrado por nombres incorrectos
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._structure_cache = None
        self._materias_cache = None
    
    def get_database_structure(self) -> Dict[str, Any]:
        """
        📊 OBTENER ESTRUCTURA COMPLETA DE LA BASE DE DATOS
        """
        if self._structure_cache is None:
            self._structure_cache = self._analyze_structure()
        return self._structure_cache
    
    def get_available_materias(self) -> List[str]:
        """
        📚 OBTENER LISTA DE MATERIAS DISPONIBLES
        """
        if self._materias_cache is None:
            self._materias_cache = self._extract_materias()
        return self._materias_cache
    
    def get_field_info(self, table: str = "datos_escolares") -> Dict[str, str]:
        """
        🔧 OBTENER INFORMACIÓN DE CAMPOS DISPONIBLES
        """
        structure = self.get_database_structure()
        return structure.get("tables", {}).get(table, {}).get("columns", {})
    
    def normalize_materia_name(self, materia_input: str) -> Optional[str]:
        """
        🔄 NORMALIZAR NOMBRE DE MATERIA
        Convierte input del usuario al nombre real en la BD
        """
        materias_disponibles = self.get_available_materias()
        materia_lower = materia_input.lower()
        
        # Mapeo de nombres comunes a nombres reales
        mapeo_materias = {
            "matemáticas": "MATEMATICAS",
            "matematicas": "MATEMATICAS", 
            "español": "ESPANOL",
            "espanol": "ESPANOL",
            "lenguajes": "LENGUAJES",
            "ciencias": "CIENCIAS NATURALES",
            "ciencias naturales": "CIENCIAS NATURALES",
            "historia": "HISTORIA",
            "geografía": "GEOGRAFIA",
            "geografia": "GEOGRAFIA",
            "educación física": "EDUCACION FISICA",
            "educacion fisica": "EDUCACION FISICA",
            "formación cívica": "FORMACION CIVICA Y ETICA",
            "formacion civica": "FORMACION CIVICA Y ETICA",
            "inglés": "INGLES",
            "ingles": "INGLES"
        }
        
        # Buscar en mapeo
        if materia_lower in mapeo_materias:
            return mapeo_materias[materia_lower]
        
        # Buscar coincidencia parcial en materias disponibles
        for materia_real in materias_disponibles:
            if materia_lower in materia_real.lower():
                return materia_real
        
        return None
    
    def get_criteria_suggestions(self, user_query: str) -> Dict[str, Any]:
        """
        💡 SUGERIR CRITERIOS BASADOS EN ESTRUCTURA REAL
        """
        structure = self.get_database_structure()
        materias = self.get_available_materias()
        
        return {
            "campos_disponibles": list(structure.get("tables", {}).get("datos_escolares", {}).get("columns", {}).keys()),
            "materias_disponibles": materias,
            "valores_turno": ["MATUTINO", "VESPERTINO"],
            "grados_disponibles": list(range(1, 7)),
            "grupos_disponibles": ["A", "B", "C"]
        }
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """
        🔍 ANALIZAR ESTRUCTURA INTERNA
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                structure = {"tables": {}}
                
                for table in tables:
                    if table.startswith('sqlite_'):
                        continue
                    
                    # Obtener columnas
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = {row[1]: row[2] for row in cursor.fetchall()}
                    
                    # Obtener conteo
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    structure["tables"][table] = {
                        "columns": columns,
                        "count": count
                    }
                
                return structure
                
        except Exception as e:
            self.logger.error(f"Error analizando estructura: {e}")
            return {"tables": {}}
    
    def _extract_materias(self) -> List[str]:
        """
        📚 EXTRAER MATERIAS DE CALIFICACIONES REALES
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener todas las calificaciones no vacías
                cursor.execute("""
                    SELECT calificaciones 
                    FROM datos_escolares 
                    WHERE calificaciones != '[]' AND calificaciones IS NOT NULL
                    LIMIT 50
                """)
                
                materias_set = set()
                
                for row in cursor.fetchall():
                    try:
                        calificaciones = json.loads(row[0])
                        for cal in calificaciones:
                            if isinstance(cal, dict) and "nombre" in cal:
                                materias_set.add(cal["nombre"])
                    except (json.JSONDecodeError, TypeError):
                        continue
                
                return sorted(list(materias_set))
                
        except Exception as e:
            self.logger.error(f"Error extrayendo materias: {e}")
            return []
    
    def get_llm_context_info(self) -> str:
        """
        🧠 INFORMACIÓN ESTRUCTURADA PARA LLMs
        """
        structure = self.get_database_structure()
        materias = self.get_available_materias()
        
        return f"""
ESTRUCTURA REAL DE LA BASE DE DATOS:

📊 CAMPOS DISPONIBLES EN datos_escolares:
{', '.join(structure.get('tables', {}).get('datos_escolares', {}).get('columns', {}).keys())}

📚 MATERIAS REALES DISPONIBLES:
{', '.join(materias)}

🎯 VALORES VÁLIDOS:
- turno: MATUTINO, VESPERTINO
- grado: 1, 2, 3, 4, 5, 6
- grupo: A, B, C

⚠️ IMPORTANTE:
- Las calificaciones están en formato JSON
- Los nombres de materias son EXACTOS (sin tildes, en mayúsculas)
- Para filtrar por materia específica, usar el nombre EXACTO de la lista
"""
