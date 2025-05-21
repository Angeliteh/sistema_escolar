import sqlite3
import os
import json
from datetime import datetime
from app.core.config import Config

class DBManager:
    """
    Clase para gestionar la base de datos de alumnos
    """
    
    def __init__(self, db_path=None):
        """Inicializa el gestor de base de datos"""
        self.db_path = db_path or Config.DB_PATH
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Conecta a la base de datos"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Crea las tablas necesarias si no existen"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curp TEXT UNIQUE,
            nombre TEXT,
            matricula TEXT,
            fecha_nacimiento TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS datos_escolares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            ciclo_escolar TEXT,
            grado INTEGER,
            grupo TEXT,
            turno TEXT,
            escuela TEXT,
            cct TEXT,
            calificaciones TEXT,  -- JSON con calificaciones
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id)
        )
        ''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS constancias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            tipo TEXT,
            ruta_archivo TEXT,
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id)
        )
        ''')
        
        self.conn.commit()
    
    def guardar_alumno(self, datos):
        """
        Guarda o actualiza los datos de un alumno
        
        Args:
            datos: Diccionario con los datos del alumno
            
        Returns:
            ID del alumno en la base de datos
        """
        try:
            # Verificar si el alumno ya existe
            self.cursor.execute("SELECT id FROM alumnos WHERE curp = ?", (datos["curp"],))
            alumno = self.cursor.fetchone()
            
            if alumno:
                # Actualizar datos del alumno
                self.cursor.execute("""
                UPDATE alumnos 
                SET nombre = ?, matricula = ?, fecha_nacimiento = ?
                WHERE curp = ?
                """, (
                    datos["nombre"],
                    datos["matricula"],
                    datos["nacimiento"],
                    datos["curp"]
                ))
                alumno_id = alumno["id"]
            else:
                # Insertar nuevo alumno
                self.cursor.execute("""
                INSERT INTO alumnos (curp, nombre, matricula, fecha_nacimiento)
                VALUES (?, ?, ?, ?)
                """, (
                    datos["curp"],
                    datos["nombre"],
                    datos["matricula"],
                    datos["nacimiento"]
                ))
                alumno_id = self.cursor.lastrowid
            
            # Guardar datos escolares
            calificaciones_json = json.dumps(datos.get("calificaciones", []))
            
            self.cursor.execute("""
            INSERT INTO datos_escolares 
            (alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alumno_id,
                datos.get("ciclo", ""),
                datos.get("grado", ""),
                datos.get("grupo", ""),
                datos.get("turno", ""),
                datos.get("escuela", ""),
                datos.get("cct", ""),
                calificaciones_json
            ))
            
            self.conn.commit()
            return alumno_id
            
        except Exception as e:
            print(f"Error al guardar alumno: {e}")
            self.conn.rollback()
            return None
    
    def registrar_constancia(self, alumno_id, tipo, ruta_archivo):
        """
        Registra una constancia generada
        
        Args:
            alumno_id: ID del alumno
            tipo: Tipo de constancia (traslado, estudio, calificaciones)
            ruta_archivo: Ruta al archivo PDF generado
            
        Returns:
            ID de la constancia en la base de datos
        """
        try:
            self.cursor.execute("""
            INSERT INTO constancias (alumno_id, tipo, ruta_archivo)
            VALUES (?, ?, ?)
            """, (alumno_id, tipo, ruta_archivo))
            
            self.conn.commit()
            return self.cursor.lastrowid
            
        except Exception as e:
            print(f"Error al registrar constancia: {e}")
            self.conn.rollback()
            return None
    
    def buscar_alumno_por_curp(self, curp):
        """
        Busca un alumno por su CURP
        
        Args:
            curp: CURP del alumno
            
        Returns:
            Diccionario con los datos del alumno o None si no existe
        """
        try:
            self.cursor.execute("""
            SELECT a.*, de.ciclo_escolar, de.grado, de.grupo, de.turno, 
                   de.escuela, de.cct, de.calificaciones
            FROM alumnos a
            LEFT JOIN datos_escolares de ON a.id = de.alumno_id
            WHERE a.curp = ?
            ORDER BY de.id DESC
            LIMIT 1
            """, (curp,))
            
            alumno = self.cursor.fetchone()
            
            if not alumno:
                return None
                
            # Convertir a diccionario
            datos = dict(alumno)
            
            # Convertir calificaciones de JSON a lista
            if datos.get("calificaciones"):
                datos["calificaciones"] = json.loads(datos["calificaciones"])
            else:
                datos["calificaciones"] = []
                
            return datos
            
        except Exception as e:
            print(f"Error al buscar alumno: {e}")
            return None
    
    def listar_alumnos(self, limit=100):
        """
        Lista los alumnos registrados
        
        Args:
            limit: Límite de resultados
            
        Returns:
            Lista de diccionarios con los datos de los alumnos
        """
        try:
            self.cursor.execute("""
            SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento,
                   MAX(de.ciclo_escolar) as ciclo_escolar, 
                   MAX(de.grado) as grado,
                   MAX(de.grupo) as grupo
            FROM alumnos a
            LEFT JOIN datos_escolares de ON a.id = de.alumno_id
            GROUP BY a.id
            ORDER BY a.nombre
            LIMIT ?
            """, (limit,))
            
            alumnos = self.cursor.fetchall()
            
            # Convertir a lista de diccionarios
            return [dict(alumno) for alumno in alumnos]
            
        except Exception as e:
            print(f"Error al listar alumnos: {e}")
            return []
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
