#!/usr/bin/env python3
"""
Script para explorar y probar la base de datos de alumnos.
Este script permite ver la estructura de las tablas, listar alumnos,
ver detalles de un alumno específico, ver constancias generadas y
agregar un alumno de prueba.
"""

import sqlite3
import json
import os
from datetime import datetime
import argparse

class DBExplorer:
    """Clase para explorar la base de datos de alumnos"""
    
    def __init__(self, db_path="alumnos.db"):
        """Inicializa el explorador de base de datos"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Conecta a la base de datos"""
        if not os.path.exists(self.db_path):
            print(f"La base de datos {self.db_path} no existe.")
            return False
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
        self.cursor = self.conn.cursor()
        return True
    
    def show_tables(self):
        """Muestra las tablas existentes en la base de datos"""
        if not self.conn:
            return
        
        print("\n=== TABLAS EN LA BASE DE DATOS ===")
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        
        if not tables:
            print("No hay tablas en la base de datos.")
            return
        
        for table in tables:
            print(f"- {table['name']}")
    
    def show_table_structure(self, table_name):
        """Muestra la estructura de una tabla específica"""
        if not self.conn:
            return
        
        print(f"\n=== ESTRUCTURA DE LA TABLA '{table_name}' ===")
        self.cursor.execute(f"PRAGMA table_info({table_name});")
        columns = self.cursor.fetchall()
        
        if not columns:
            print(f"La tabla '{table_name}' no existe o no tiene columnas.")
            return
        
        print(f"{'Nombre':<20} {'Tipo':<15} {'PK':<5} {'Nulo':<5} {'Default':<15}")
        print("-" * 60)
        
        for col in columns:
            print(f"{col['name']:<20} {col['type']:<15} {col['pk']:<5} {col['notnull']:<5} {str(col['dflt_value']):<15}")
    
    def list_students(self, limit=10):
        """Lista los alumnos registrados"""
        if not self.conn:
            return
        
        print(f"\n=== LISTADO DE ALUMNOS (máximo {limit}) ===")
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
        
        if not alumnos:
            print("No hay alumnos registrados en la base de datos.")
            return
        
        print(f"{'ID':<5} {'CURP':<20} {'Nombre':<30} {'Matrícula':<15} {'Grado/Grupo':<10} {'Ciclo':<10}")
        print("-" * 90)
        
        for alumno in alumnos:
            grado_grupo = f"{alumno['grado'] or '-'}{alumno['grupo'] or '-'}"
            print(f"{alumno['id']:<5} {alumno['curp']:<20} {alumno['nombre']:<30} {alumno['matricula']:<15} {grado_grupo:<10} {alumno['ciclo_escolar'] or '-':<10}")
    
    def show_student_details(self, student_id):
        """Muestra los detalles de un alumno específico"""
        if not self.conn:
            return
        
        print(f"\n=== DETALLES DEL ALUMNO (ID: {student_id}) ===")
        self.cursor.execute("""
        SELECT a.*, de.ciclo_escolar, de.grado, de.grupo, de.turno, 
               de.escuela, de.cct, de.calificaciones, de.id as datos_id
        FROM alumnos a
        LEFT JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE a.id = ?
        ORDER BY de.id DESC
        LIMIT 1
        """, (student_id,))
        
        alumno = self.cursor.fetchone()
        
        if not alumno:
            print(f"No se encontró ningún alumno con ID {student_id}.")
            return
        
        print("INFORMACIÓN BÁSICA:")
        print(f"- Nombre: {alumno['nombre']}")
        print(f"- CURP: {alumno['curp']}")
        print(f"- Matrícula: {alumno['matricula']}")
        print(f"- Fecha de nacimiento: {alumno['fecha_nacimiento']}")
        print(f"- Fecha de registro: {alumno['fecha_registro']}")
        
        print("\nINFORMACIÓN ESCOLAR:")
        print(f"- Ciclo escolar: {alumno['ciclo_escolar'] or 'No disponible'}")
        print(f"- Grado: {alumno['grado'] or 'No disponible'}")
        print(f"- Grupo: {alumno['grupo'] or 'No disponible'}")
        print(f"- Turno: {alumno['turno'] or 'No disponible'}")
        print(f"- Escuela: {alumno['escuela'] or 'No disponible'}")
        print(f"- CCT: {alumno['cct'] or 'No disponible'}")
        
        if alumno['calificaciones']:
            print("\nCALIFICACIONES:")
            try:
                calificaciones = json.loads(alumno['calificaciones'])
                if calificaciones:
                    print(f"{'Materia':<40} {'P1':<5} {'P2':<5} {'P3':<5} {'Prom':<5}")
                    print("-" * 60)
                    for cal in calificaciones:
                        print(f"{cal['nombre']:<40} {cal['i']:<5} {cal['ii']:<5} {cal['iii']:<5} {cal['promedio']:<5}")
                else:
                    print("No hay calificaciones registradas.")
            except json.JSONDecodeError:
                print("Error al decodificar las calificaciones.")
        else:
            print("\nNo hay calificaciones registradas.")
        
        # Mostrar constancias generadas
        self.cursor.execute("""
        SELECT id, tipo, ruta_archivo, fecha_generacion
        FROM constancias
        WHERE alumno_id = ?
        ORDER BY fecha_generacion DESC
        """, (student_id,))
        
        constancias = self.cursor.fetchall()
        
        print("\nCONSTANCIAS GENERADAS:")
        if constancias:
            print(f"{'ID':<5} {'Tipo':<15} {'Fecha':<20} {'Ruta':<50}")
            print("-" * 90)
            for c in constancias:
                print(f"{c['id']:<5} {c['tipo']:<15} {c['fecha_generacion']:<20} {c['ruta_archivo']:<50}")
        else:
            print("No hay constancias generadas para este alumno.")
    
    def list_certificates(self, limit=10):
        """Lista las constancias generadas"""
        if not self.conn:
            return
        
        print(f"\n=== LISTADO DE CONSTANCIAS (máximo {limit}) ===")
        self.cursor.execute("""
        SELECT c.id, c.tipo, c.fecha_generacion, c.ruta_archivo, a.nombre, a.curp
        FROM constancias c
        JOIN alumnos a ON c.alumno_id = a.id
        ORDER BY c.fecha_generacion DESC
        LIMIT ?
        """, (limit,))
        
        constancias = self.cursor.fetchall()
        
        if not constancias:
            print("No hay constancias registradas en la base de datos.")
            return
        
        print(f"{'ID':<5} {'Tipo':<15} {'Fecha':<20} {'Alumno':<30} {'CURP':<20}")
        print("-" * 90)
        
        for c in constancias:
            print(f"{c['id']:<5} {c['tipo']:<15} {c['fecha_generacion']:<20} {c['nombre']:<30} {c['curp']:<20}")
    
    def add_test_student(self):
        """Agrega un alumno de prueba a la base de datos"""
        if not self.conn:
            return
        
        print("\n=== AGREGAR ALUMNO DE PRUEBA ===")
        
        # Generar datos de prueba
        import random
        import string
        
        # Generar CURP aleatorio
        curp = ''.join(random.choices(string.ascii_uppercase, k=4))
        curp += ''.join(random.choices(string.digits, k=6))
        curp += ''.join(random.choices(string.ascii_uppercase, k=8))
        
        nombre = "Alumno de Prueba"
        matricula = f"MAT-{random.randint(1000, 9999)}"
        fecha_nacimiento = "2010-01-01"
        
        # Insertar alumno
        self.cursor.execute("""
        INSERT INTO alumnos (curp, nombre, matricula, fecha_nacimiento)
        VALUES (?, ?, ?, ?)
        """, (curp, nombre, matricula, fecha_nacimiento))
        
        alumno_id = self.cursor.lastrowid
        
        # Insertar datos escolares
        ciclo_escolar = "2024-2025"
        grado = random.randint(1, 6)
        grupo = random.choice(["A", "B", "C"])
        turno = random.choice(["MATUTINO", "VESPERTINO"])
        escuela = "PROF. MAXIMO GAMIZ FERNANDEZ"
        cct = "10DPR0392H"
        
        # Generar calificaciones aleatorias
        calificaciones = [
            {"nombre": "LENGUAJES", "i": random.randint(6, 10), "ii": random.randint(6, 10), "iii": random.randint(6, 10), "promedio": 0},
            {"nombre": "SABERES Y PENSAMIENTOS CIENTÍFICOS", "i": random.randint(6, 10), "ii": random.randint(6, 10), "iii": random.randint(6, 10), "promedio": 0},
            {"nombre": "ETICA, NATURALEZA Y SOCIEDADES", "i": random.randint(6, 10), "ii": random.randint(6, 10), "iii": random.randint(6, 10), "promedio": 0},
            {"nombre": "DE LO HUMANO Y LO COMUNITARIO", "i": random.randint(6, 10), "ii": random.randint(6, 10), "iii": random.randint(6, 10), "promedio": 0},
        ]
        
        # Calcular promedios
        for cal in calificaciones:
            cal["promedio"] = round((cal["i"] + cal["ii"] + cal["iii"]) / 3, 1)
        
        calificaciones_json = json.dumps(calificaciones)
        
        self.cursor.execute("""
        INSERT INTO datos_escolares 
        (alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alumno_id,
            ciclo_escolar,
            grado,
            grupo,
            turno,
            escuela,
            cct,
            calificaciones_json
        ))
        
        # Insertar constancia de prueba
        tipo_constancia = random.choice(["traslado", "estudio", "calificaciones"])
        ruta_archivo = f"salidas/constancia_{tipo_constancia}_{curp}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        self.cursor.execute("""
        INSERT INTO constancias (alumno_id, tipo, ruta_archivo)
        VALUES (?, ?, ?)
        """, (alumno_id, tipo_constancia, ruta_archivo))
        
        self.conn.commit()
        
        print(f"Alumno de prueba agregado con éxito. ID: {alumno_id}, CURP: {curp}")
        return alumno_id
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Explorador de base de datos de alumnos")
    parser.add_argument("--db", default="alumnos.db", help="Ruta a la base de datos")
    parser.add_argument("--action", choices=["tables", "structure", "students", "details", "certificates", "add"], 
                        default="tables", help="Acción a realizar")
    parser.add_argument("--table", help="Nombre de la tabla (para action=structure)")
    parser.add_argument("--id", type=int, help="ID del alumno (para action=details)")
    parser.add_argument("--limit", type=int, default=10, help="Límite de resultados")
    
    args = parser.parse_args()
    
    explorer = DBExplorer(args.db)
    
    if args.action == "tables":
        explorer.show_tables()
        # Mostrar estructura de todas las tablas
        explorer.show_table_structure("alumnos")
        explorer.show_table_structure("datos_escolares")
        explorer.show_table_structure("constancias")
    
    elif args.action == "structure":
        if not args.table:
            print("Error: Debe especificar el nombre de la tabla con --table")
            return
        explorer.show_table_structure(args.table)
    
    elif args.action == "students":
        explorer.list_students(args.limit)
    
    elif args.action == "details":
        if not args.id:
            print("Error: Debe especificar el ID del alumno con --id")
            return
        explorer.show_student_details(args.id)
    
    elif args.action == "certificates":
        explorer.list_certificates(args.limit)
    
    elif args.action == "add":
        student_id = explorer.add_test_student()
        if student_id:
            explorer.show_student_details(student_id)
    
    explorer.close()

if __name__ == "__main__":
    main()
