"""
Analizador de esquema de base de datos para generar contexto SQL
"""
import sqlite3
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class ColumnInfo:
    """Información de una columna"""
    name: str
    type: str
    nullable: bool
    default_value: Any
    primary_key: bool
    foreign_key: str = None

@dataclass
class TableInfo:
    """Información de una tabla"""
    name: str
    columns: List[ColumnInfo]
    foreign_keys: List[Tuple[str, str, str]]  # (column, ref_table, ref_column)
    sample_data: List[Dict[str, Any]]

class DatabaseAnalyzer:
    """Analizador de esquema de base de datos"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.tables_info = {}
    
    def analyze_database(self) -> Dict[str, TableInfo]:
        """Analiza toda la base de datos y retorna información completa"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Obtener lista de tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table_name in tables:
                self.tables_info[table_name] = self._analyze_table(cursor, table_name)
            
            conn.close()
            return self.tables_info
            
        except Exception as e:
            print(f"Error analizando base de datos: {e}")
            return {}
    
    def _analyze_table(self, cursor, table_name: str) -> TableInfo:
        """Analiza una tabla específica"""
        # Obtener información de columnas
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_data = cursor.fetchall()
        
        columns = []
        for col_data in columns_data:
            column = ColumnInfo(
                name=col_data['name'],
                type=col_data['type'],
                nullable=not col_data['notnull'],
                default_value=col_data['dflt_value'],
                primary_key=bool(col_data['pk'])
            )
            columns.append(column)
        
        # Obtener foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fk_data = cursor.fetchall()
        foreign_keys = [(fk['from'], fk['table'], fk['to']) for fk in fk_data]
        
        # Obtener datos de muestra (máximo 5 registros)
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_data = [dict(row) for row in cursor.fetchall()]
        
        return TableInfo(
            name=table_name,
            columns=columns,
            foreign_keys=foreign_keys,
            sample_data=sample_data
        )
    
    def generate_sql_context(self) -> str:
        """Genera contexto SQL para el LLM"""
        if not self.tables_info:
            self.analyze_database()
        
        context_parts = []
        context_parts.append("=== ESTRUCTURA DE LA BASE DE DATOS ===\n")
        
        for table_name, table_info in self.tables_info.items():
            context_parts.append(f"TABLA: {table_name}")
            context_parts.append("-" * 40)
            
            # Columnas
            context_parts.append("COLUMNAS:")
            for col in table_info.columns:
                pk_marker = " (PK)" if col.primary_key else ""
                nullable_marker = " NULL" if col.nullable else " NOT NULL"
                context_parts.append(f"  • {col.name}: {col.type}{pk_marker}{nullable_marker}")
            
            # Foreign Keys
            if table_info.foreign_keys:
                context_parts.append("\nRELACIONES:")
                for fk in table_info.foreign_keys:
                    context_parts.append(f"  • {fk[0]} → {fk[1]}.{fk[2]}")
            
            # Datos de muestra
            if table_info.sample_data:
                context_parts.append("\nDATO DE MUESTRA:")
                sample = table_info.sample_data[0]
                for key, value in sample.items():
                    if value is not None:
                        context_parts.append(f"  • {key}: {value}")
            
            context_parts.append("\n")
        
        return "\n".join(context_parts)
    
    def get_table_relationships(self) -> str:
        """Genera descripción de relaciones entre tablas"""
        if not self.tables_info:
            self.analyze_database()
        
        relationships = []
        relationships.append("=== RELACIONES ENTRE TABLAS ===")
        
        # Relación principal: alumnos ← datos_escolares
        relationships.append("• alumnos (1) ← datos_escolares (N)")
        relationships.append("  Un alumno puede tener múltiples registros escolares (por ciclo)")
        
        # Relación: alumnos ← constancias  
        relationships.append("• alumnos (1) ← constancias (N)")
        relationships.append("  Un alumno puede tener múltiples constancias generadas")
        
        # Consultas típicas
        relationships.append("\n=== CONSULTAS TÍPICAS ===")
        relationships.append("• Buscar alumnos por nombre:")
        relationships.append("  SELECT * FROM alumnos WHERE nombre LIKE '%nombre%'")
        
        relationships.append("• Buscar por grado/grupo/turno:")
        relationships.append("  SELECT a.*, de.* FROM alumnos a")
        relationships.append("  JOIN datos_escolares de ON a.id = de.alumno_id")
        relationships.append("  WHERE de.grado = X AND de.grupo = 'Y'")
        
        relationships.append("• Datos completos de un alumno:")
        relationships.append("  SELECT a.*, de.* FROM alumnos a")
        relationships.append("  LEFT JOIN datos_escolares de ON a.id = de.alumno_id")
        relationships.append("  WHERE a.nombre LIKE '%nombre%'")
        relationships.append("  ORDER BY de.id DESC LIMIT 1")
        
        return "\n".join(relationships)
    
    def get_common_queries_examples(self) -> str:
        """Genera ejemplos de consultas comunes"""
        examples = []
        examples.append("=== EJEMPLOS DE CONSULTAS SQL ===")
        
        examples.append("\n1. BUSCAR ALUMNOS POR NOMBRE:")
        examples.append("   Entrada: 'buscar a José María'")
        examples.append("   SQL: SELECT a.*, de.grado, de.grupo, de.turno")
        examples.append("        FROM alumnos a")
        examples.append("        LEFT JOIN datos_escolares de ON a.id = de.alumno_id")
        examples.append("        WHERE a.nombre LIKE '%José María%'")
        
        examples.append("\n2. ALUMNOS POR GRADO:")
        examples.append("   Entrada: 'alumnos de 3er grado'")
        examples.append("   SQL: SELECT a.*, de.*")
        examples.append("        FROM alumnos a")
        examples.append("        JOIN datos_escolares de ON a.id = de.alumno_id")
        examples.append("        WHERE de.grado = 3")
        
        examples.append("\n3. ALUMNOS POR GRUPO:")
        examples.append("   Entrada: 'estudiantes del grupo C'")
        examples.append("   SQL: SELECT a.*, de.*")
        examples.append("        FROM alumnos a")
        examples.append("        JOIN datos_escolares de ON a.id = de.alumno_id")
        examples.append("        WHERE de.grupo = 'C'")
        
        examples.append("\n4. ALUMNOS POR TURNO:")
        examples.append("   Entrada: 'alumnos del turno matutino'")
        examples.append("   SQL: SELECT a.*, de.*")
        examples.append("        FROM alumnos a")
        examples.append("        JOIN datos_escolares de ON a.id = de.alumno_id")
        examples.append("        WHERE de.turno = 'MATUTINO'")
        
        examples.append("\n5. DETALLES COMPLETOS:")
        examples.append("   Entrada: 'detalles de José María'")
        examples.append("   SQL: SELECT a.*, de.*, c.calificaciones")
        examples.append("        FROM alumnos a")
        examples.append("        LEFT JOIN datos_escolares de ON a.id = de.alumno_id")
        examples.append("        WHERE a.nombre LIKE '%José María%'")
        examples.append("        ORDER BY de.id DESC LIMIT 1")
        
        return "\n".join(examples)

# Instancia global del analizador
database_analyzer = None

def get_database_analyzer(db_path: str = None) -> DatabaseAnalyzer:
    """Obtiene la instancia global del analizador de BD"""
    global database_analyzer
    
    if database_analyzer is None:
        if db_path is None:
            from app.config import Config
            db_path = Config.DB_PATH
        database_analyzer = DatabaseAnalyzer(db_path)
    
    return database_analyzer
