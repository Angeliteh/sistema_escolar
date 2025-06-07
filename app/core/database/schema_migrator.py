"""
🗄️ MIGRADOR DE ESQUEMA DE BASE DE DATOS
Maneja la creación y migración de tablas para sistema escolar completo
"""

import sqlite3
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from app.core.logging import get_logger

class SchemaMigrator:
    """
    🗄️ MIGRADOR DE ESQUEMA DE BASE DE DATOS
    
    Responsabilidades:
    - Crear nuevas tablas para sistema escolar completo
    - Migrar datos existentes sin pérdida
    - Mantener compatibilidad con código actual
    - Validar integridad de datos
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger(__name__)
        self.conn = None
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")  # Habilitar foreign keys
            self.logger.info(f"✅ Conectado a base de datos: {self.db_path}")
        except Exception as e:
            self.logger.error(f"❌ Error conectando a BD: {e}")
            raise
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def get_current_schema_version(self) -> int:
        """Obtiene la versión actual del esquema"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)
            
            cursor.execute("SELECT MAX(version) FROM schema_version")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
            
        except Exception as e:
            self.logger.error(f"Error obteniendo versión de esquema: {e}")
            return 0
    
    def set_schema_version(self, version: int, description: str):
        """Establece la versión del esquema"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO schema_version (version, description)
                VALUES (?, ?)
            """, (version, description))
            self.conn.commit()
            self.logger.info(f"✅ Esquema actualizado a versión {version}: {description}")
        except Exception as e:
            self.logger.error(f"Error estableciendo versión de esquema: {e}")
            raise
    
    def migrate_to_latest(self) -> bool:
        """Migra la base de datos a la última versión"""
        try:
            if not self.conn:
                self.connect()
            
            current_version = self.get_current_schema_version()
            self.logger.info(f"🔍 Versión actual del esquema: {current_version}")
            
            migrations = [
                (1, "Crear tablas básicas del sistema escolar", self._migrate_to_v1),
                (2, "Agregar índices y optimizaciones", self._migrate_to_v2),
                (3, "Agregar campos adicionales", self._migrate_to_v3)
            ]
            
            for version, description, migration_func in migrations:
                if current_version < version:
                    self.logger.info(f"🚀 Aplicando migración v{version}: {description}")
                    success = migration_func()
                    if success:
                        self.set_schema_version(version, description)
                    else:
                        self.logger.error(f"❌ Falló migración v{version}")
                        return False
            
            self.logger.info("✅ Todas las migraciones aplicadas exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en migración: {e}")
            return False
    
    def _migrate_to_v1(self) -> bool:
        """Migración v1: Crear tablas básicas del sistema escolar"""
        try:
            cursor = self.conn.cursor()

            # 0. Crear tablas básicas existentes si no existen
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alumnos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    curp TEXT UNIQUE,
                    nombre TEXT NOT NULL,
                    matricula TEXT,
                    fecha_nacimiento DATE,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS datos_escolares (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    ciclo_escolar TEXT,
                    grado INTEGER,
                    grupo TEXT,
                    turno TEXT,
                    escuela TEXT,
                    cct TEXT,
                    calificaciones TEXT,
                    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS constancias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    tipo_constancia TEXT,
                    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    archivo_path TEXT,
                    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
                )
            """)

            # 1. Tabla de maestros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maestros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    curp TEXT UNIQUE,
                    rfc TEXT,
                    especialidad TEXT,
                    telefono TEXT,
                    email TEXT,
                    activo BOOLEAN DEFAULT 1,
                    fecha_ingreso DATE,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Tabla de materias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS materias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    clave TEXT UNIQUE,
                    descripcion TEXT,
                    grado INTEGER,
                    activa BOOLEAN DEFAULT 1,
                    orden_display INTEGER DEFAULT 0
                )
            """)
            
            # 3. Tabla de grupos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS grupos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    grado INTEGER NOT NULL,
                    grupo TEXT NOT NULL,
                    ciclo_escolar TEXT NOT NULL,
                    turno TEXT DEFAULT 'MATUTINO',
                    maestro_titular_id INTEGER,
                    aula TEXT,
                    capacidad_maxima INTEGER DEFAULT 30,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (maestro_titular_id) REFERENCES maestros(id),
                    UNIQUE(grado, grupo, ciclo_escolar, turno)
                )
            """)
            
            # 4. Tabla de calificaciones normalizadas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calificaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    materia_id INTEGER NOT NULL,
                    grupo_id INTEGER NOT NULL,
                    ciclo_escolar TEXT NOT NULL,
                    periodo_1 REAL,
                    periodo_2 REAL,
                    periodo_3 REAL,
                    promedio REAL,
                    observaciones TEXT,
                    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
                    FOREIGN KEY (materia_id) REFERENCES materias(id),
                    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
                    UNIQUE(alumno_id, materia_id, ciclo_escolar)
                )
            """)
            
            # 5. Tabla de asignaciones maestro-materia-grupo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS asignaciones_maestros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    maestro_id INTEGER NOT NULL,
                    materia_id INTEGER NOT NULL,
                    grupo_id INTEGER NOT NULL,
                    ciclo_escolar TEXT NOT NULL,
                    activa BOOLEAN DEFAULT 1,
                    fecha_asignacion DATE DEFAULT CURRENT_DATE,
                    FOREIGN KEY (maestro_id) REFERENCES maestros(id),
                    FOREIGN KEY (materia_id) REFERENCES materias(id),
                    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
                    UNIQUE(materia_id, grupo_id, ciclo_escolar)
                )
            """)
            
            # 6. Tabla de inscripciones alumno-grupo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inscripciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alumno_id INTEGER NOT NULL,
                    grupo_id INTEGER NOT NULL,
                    ciclo_escolar TEXT NOT NULL,
                    fecha_inscripcion DATE DEFAULT CURRENT_DATE,
                    fecha_baja DATE,
                    motivo_baja TEXT,
                    activa BOOLEAN DEFAULT 1,
                    FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
                    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
                    UNIQUE(alumno_id, ciclo_escolar)
                )
            """)
            
            self.conn.commit()
            self.logger.info("✅ Tablas básicas creadas exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en migración v1: {e}")
            self.conn.rollback()
            return False
    
    def _migrate_to_v2(self) -> bool:
        """Migración v2: Agregar índices y optimizaciones"""
        try:
            cursor = self.conn.cursor()
            
            # Índices para mejorar rendimiento
            indices = [
                "CREATE INDEX IF NOT EXISTS idx_alumnos_nombre ON alumnos(nombre)",
                "CREATE INDEX IF NOT EXISTS idx_alumnos_curp ON alumnos(curp)",
                "CREATE INDEX IF NOT EXISTS idx_datos_escolares_alumno ON datos_escolares(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_datos_escolares_grado_grupo ON datos_escolares(grado, grupo)",
                "CREATE INDEX IF NOT EXISTS idx_calificaciones_alumno ON calificaciones(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_calificaciones_materia ON calificaciones(materia_id)",
                "CREATE INDEX IF NOT EXISTS idx_inscripciones_alumno ON inscripciones(alumno_id)",
                "CREATE INDEX IF NOT EXISTS idx_inscripciones_grupo ON inscripciones(grupo_id)",
                "CREATE INDEX IF NOT EXISTS idx_asignaciones_maestro ON asignaciones_maestros(maestro_id)",
                "CREATE INDEX IF NOT EXISTS idx_grupos_grado_grupo ON grupos(grado, grupo)"
            ]
            
            for indice in indices:
                cursor.execute(indice)
            
            self.conn.commit()
            self.logger.info("✅ Índices creados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en migración v2: {e}")
            self.conn.rollback()
            return False
    
    def _migrate_to_v3(self) -> bool:
        """Migración v3: Agregar campos adicionales"""
        try:
            cursor = self.conn.cursor()
            
            # Agregar campos adicionales si no existen
            campos_adicionales = [
                ("alumnos", "foto_path", "TEXT"),
                ("alumnos", "direccion", "TEXT"),
                ("alumnos", "telefono_contacto", "TEXT"),
                ("maestros", "foto_path", "TEXT"),
                ("grupos", "horario_inicio", "TIME"),
                ("grupos", "horario_fin", "TIME")
            ]
            
            for tabla, campo, tipo in campos_adicionales:
                try:
                    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {campo} {tipo}")
                    self.logger.info(f"✅ Campo {campo} agregado a tabla {tabla}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        self.logger.info(f"ℹ️ Campo {campo} ya existe en tabla {tabla}")
                    else:
                        raise
            
            self.conn.commit()
            self.logger.info("✅ Campos adicionales agregados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error en migración v3: {e}")
            self.conn.rollback()
            return False
    
    def populate_initial_data(self, school_config: Dict) -> bool:
        """Poblar datos iniciales basados en configuración escolar"""
        try:
            cursor = self.conn.cursor()
            
            # 1. Crear materias basadas en configuración
            materias_config = school_config.get("academic_info", {}).get("materias_por_grado", {})
            
            for grado_str, materias in materias_config.items():
                grado = int(grado_str)
                for i, materia in enumerate(materias):
                    cursor.execute("""
                        INSERT OR IGNORE INTO materias (nombre, clave, grado, orden_display)
                        VALUES (?, ?, ?, ?)
                    """, (materia, f"{grado}_{materia.replace(' ', '_').upper()}", grado, i))
            
            # 2. Crear grupos basados en configuración
            grados = school_config.get("academic_info", {}).get("grades", [])
            grupos_letras = school_config.get("academic_info", {}).get("groups", ["A"])
            turnos = school_config.get("academic_info", {}).get("shifts", ["MATUTINO"])
            ciclo_actual = school_config.get("academic_info", {}).get("current_year", "2024-2025")
            
            for grado in grados:
                for grupo in grupos_letras:
                    for turno in turnos:
                        cursor.execute("""
                            INSERT OR IGNORE INTO grupos (grado, grupo, ciclo_escolar, turno)
                            VALUES (?, ?, ?, ?)
                        """, (grado, grupo, ciclo_actual, turno))
            
            self.conn.commit()
            self.logger.info("✅ Datos iniciales poblados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error poblando datos iniciales: {e}")
            self.conn.rollback()
            return False
    
    def validate_schema(self) -> Dict[str, bool]:
        """Valida que el esquema esté correcto"""
        try:
            cursor = self.conn.cursor()
            
            # Verificar que todas las tablas existan
            tablas_requeridas = [
                "alumnos", "datos_escolares", "maestros", "materias", 
                "grupos", "calificaciones", "asignaciones_maestros", "inscripciones"
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas_existentes = [row[0] for row in cursor.fetchall()]
            
            validacion = {}
            for tabla in tablas_requeridas:
                validacion[tabla] = tabla in tablas_existentes
            
            return validacion
            
        except Exception as e:
            self.logger.error(f"Error validando esquema: {e}")
            return {}


def migrate_database(db_path: str, school_config: Dict = None) -> bool:
    """
    Función principal para migrar base de datos
    
    Args:
        db_path: Ruta a la base de datos
        school_config: Configuración escolar para datos iniciales
        
    Returns:
        True si la migración fue exitosa
    """
    migrator = SchemaMigrator(db_path)
    
    try:
        migrator.connect()
        
        # Aplicar migraciones
        if not migrator.migrate_to_latest():
            return False
        
        # Poblar datos iniciales si se proporciona configuración
        if school_config:
            if not migrator.populate_initial_data(school_config):
                return False
        
        # Validar esquema final
        validacion = migrator.validate_schema()
        tablas_faltantes = [tabla for tabla, existe in validacion.items() if not existe]
        
        if tablas_faltantes:
            migrator.logger.error(f"❌ Tablas faltantes: {tablas_faltantes}")
            return False
        
        migrator.logger.info("✅ Migración completada exitosamente")
        return True
        
    except Exception as e:
        migrator.logger.error(f"❌ Error en migración: {e}")
        return False
    
    finally:
        migrator.disconnect()
