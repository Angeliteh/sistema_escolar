#!/usr/bin/env python3
"""
Script para crear una base de datos escolar expandida.
Este script crea una nueva base de datos con la estructura propuesta
para un sistema escolar completo.
"""

import sqlite3
import os
import json
from datetime import datetime
import random
import string

class SchoolDBCreator:
    """Clase para crear una base de datos escolar expandida"""
    
    def __init__(self, db_path="escuela_expandida.db"):
        """Inicializa el creador de base de datos"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Conecta a la base de datos"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Crea todas las tablas necesarias"""
        # Tablas existentes (modificadas para mayor flexibilidad)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curp TEXT UNIQUE,
            nombre TEXT,
            apellido_paterno TEXT,
            apellido_materno TEXT,
            matricula TEXT,
            fecha_nacimiento TEXT,
            genero TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
        ''')
        
        # Tabla para maestros
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS maestros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curp TEXT UNIQUE,
            nombre TEXT,
            apellido_paterno TEXT,
            apellido_materno TEXT,
            numero_empleado TEXT,
            especialidad TEXT,
            fecha_nacimiento TEXT,
            genero TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo BOOLEAN DEFAULT 1
        )
        ''')
        
        # Tabla para escuelas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS escuelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            cct TEXT UNIQUE,
            direccion TEXT,
            telefono TEXT,
            director_id INTEGER,
            nivel_educativo TEXT,
            FOREIGN KEY (director_id) REFERENCES maestros (id)
        )
        ''')
        
        # Tabla para ciclos escolares
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS ciclos_escolares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            activo BOOLEAN DEFAULT 0
        )
        ''')
        
        # Tabla para grados
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS grados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER,
            nivel TEXT,
            descripcion TEXT
        )
        ''')
        
        # Tabla para grupos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS grupos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            grado_id INTEGER,
            ciclo_escolar_id INTEGER,
            escuela_id INTEGER,
            turno TEXT,
            maestro_titular_id INTEGER,
            aula TEXT,
            capacidad INTEGER,
            FOREIGN KEY (grado_id) REFERENCES grados (id),
            FOREIGN KEY (ciclo_escolar_id) REFERENCES ciclos_escolares (id),
            FOREIGN KEY (escuela_id) REFERENCES escuelas (id),
            FOREIGN KEY (maestro_titular_id) REFERENCES maestros (id)
        )
        ''')
        
        # Tabla para inscripciones (relación alumno-grupo)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            grupo_id INTEGER,
            fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estatus TEXT DEFAULT 'activo',
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
        ''')
        
        # Tabla para materias
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            clave TEXT,
            descripcion TEXT,
            grado_id INTEGER,
            horas_semana INTEGER,
            FOREIGN KEY (grado_id) REFERENCES grados (id)
        )
        ''')
        
        # Tabla para asignaciones de materias a maestros
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS asignaciones_materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            maestro_id INTEGER,
            materia_id INTEGER,
            grupo_id INTEGER,
            ciclo_escolar_id INTEGER,
            FOREIGN KEY (maestro_id) REFERENCES maestros (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id),
            FOREIGN KEY (ciclo_escolar_id) REFERENCES ciclos_escolares (id)
        )
        ''')
        
        # Tabla para periodos de evaluación
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS periodos_evaluacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            ciclo_escolar_id INTEGER,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            FOREIGN KEY (ciclo_escolar_id) REFERENCES ciclos_escolares (id)
        )
        ''')
        
        # Tabla para calificaciones (más flexible que la actual)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS calificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            materia_id INTEGER,
            periodo_id INTEGER,
            calificacion REAL,
            observaciones TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id),
            FOREIGN KEY (materia_id) REFERENCES materias (id),
            FOREIGN KEY (periodo_id) REFERENCES periodos_evaluacion (id)
        )
        ''')
        
        # Tabla para asistencias
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            grupo_id INTEGER,
            fecha TEXT,
            estatus TEXT, -- presente, ausente, justificado, retardo
            observaciones TEXT,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id),
            FOREIGN KEY (grupo_id) REFERENCES grupos (id)
        )
        ''')
        
        # Tabla para constancias (modificada para mayor flexibilidad)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS constancias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            tipo TEXT,
            ciclo_escolar_id INTEGER,
            ruta_archivo TEXT,
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generado_por_id INTEGER, -- ID del usuario que generó la constancia
            motivo TEXT,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id),
            FOREIGN KEY (ciclo_escolar_id) REFERENCES ciclos_escolares (id)
        )
        ''')
        
        # Tabla para tutores
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tutores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido_paterno TEXT,
            apellido_materno TEXT,
            parentesco TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabla para relación alumno-tutor
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumno_tutor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            tutor_id INTEGER,
            es_principal BOOLEAN DEFAULT 0,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id),
            FOREIGN KEY (tutor_id) REFERENCES tutores (id)
        )
        ''')
        
        # Tabla para usuarios del sistema
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            nombre TEXT,
            rol TEXT, -- admin, director, maestro, secretaria, etc.
            maestro_id INTEGER, -- NULL si no es maestro
            ultimo_acceso TIMESTAMP,
            activo BOOLEAN DEFAULT 1,
            FOREIGN KEY (maestro_id) REFERENCES maestros (id)
        )
        ''')
        
        # Tabla para eventos escolares
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descripcion TEXT,
            fecha_inicio TIMESTAMP,
            fecha_fin TIMESTAMP,
            lugar TEXT,
            tipo TEXT, -- académico, deportivo, cultural, etc.
            responsable_id INTEGER,
            FOREIGN KEY (responsable_id) REFERENCES maestros (id)
        )
        ''')
        
        # Tabla para pagos y cuotas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            concepto TEXT,
            monto REAL,
            fecha_pago TIMESTAMP,
            metodo_pago TEXT,
            referencia TEXT,
            estatus TEXT, -- pagado, pendiente, cancelado
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id)
        )
        ''')
        
        self.conn.commit()
        print("Tablas creadas exitosamente.")
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()

def main():
    """Función principal"""
    print("Creando base de datos escolar expandida...")
    creator = SchoolDBCreator()
    creator.create_tables()
    creator.close()
    print(f"Base de datos creada exitosamente: {creator.db_path}")
    print("Puedes explorar la estructura con el comando:")
    print(f"python db_explorer.py --db {creator.db_path} --action tables")

if __name__ == "__main__":
    main()
