#!/usr/bin/env python3
"""
Script para extraer ejemplos aleatorios de alumnos de la base de datos real
para usar en las pruebas de la batería Master-Student
"""

import sqlite3
import random
import json
from pathlib import Path

def extract_random_students():
    """Extrae ejemplos aleatorios de alumnos de la base de datos"""
    
    db_path = 'resources/data/alumnos.db'
    
    if not Path(db_path).exists():
        print(f"❌ ERROR: Base de datos no encontrada en {db_path}")
        return
    
    print("=" * 80)
    print("🎲 EXTRAYENDO EJEMPLOS ALEATORIOS DE ALUMNOS PARA TESTING")
    print("=" * 80)
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. OBTENER ESTADÍSTICAS GENERALES
        print("📊 ESTADÍSTICAS GENERALES:")
        print("-" * 40)
        
        # Total de alumnos
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        total_alumnos = cursor.fetchone()[0]
        print(f"📈 Total de alumnos: {total_alumnos}")
        
        # Total de datos escolares
        cursor.execute("SELECT COUNT(*) FROM datos_escolares")
        total_datos = cursor.fetchone()[0]
        print(f"📚 Total de registros escolares: {total_datos}")
        
        print()
        
        # 2. OBTENER EJEMPLOS ALEATORIOS DE APELLIDOS
        print("👥 APELLIDOS ALEATORIOS PARA TESTING:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN nombre LIKE '% %' THEN 
                    TRIM(SUBSTR(nombre, INSTR(nombre, ' ') + 1))
                ELSE nombre 
            END as apellido
        FROM alumnos 
        WHERE apellido IS NOT NULL AND apellido != ''
        ORDER BY RANDOM()
        LIMIT 10
        """)
        
        apellidos = cursor.fetchall()
        apellidos_list = []
        
        for i, row in enumerate(apellidos, 1):
            apellido = row['apellido']
            apellidos_list.append(apellido)
            
            # Contar cuántos alumnos tienen este apellido
            cursor.execute("""
            SELECT COUNT(*) FROM alumnos 
            WHERE nombre LIKE ?
            """, (f'%{apellido}%',))
            count = cursor.fetchone()[0]
            
            print(f"  {i:2d}. {apellido:<20} ({count} alumnos)")
        
        print()
        
        # 3. OBTENER NOMBRES COMPLETOS ALEATORIOS
        print("👤 NOMBRES COMPLETOS ALEATORIOS:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT nombre FROM alumnos 
        ORDER BY RANDOM()
        LIMIT 10
        """)
        
        nombres = cursor.fetchall()
        nombres_list = []
        
        for i, row in enumerate(nombres, 1):
            nombre = row['nombre']
            nombres_list.append(nombre)
            print(f"  {i:2d}. {nombre}")
        
        print()
        
        # 4. OBTENER INFORMACIÓN DE GRADOS Y GRUPOS
        print("🎓 GRADOS Y GRUPOS DISPONIBLES:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT DISTINCT grado, grupo, turno, COUNT(*) as cantidad
        FROM datos_escolares 
        WHERE grado IS NOT NULL AND grupo IS NOT NULL
        GROUP BY grado, grupo, turno
        ORDER BY grado, grupo, turno
        """)
        
        grados_grupos = cursor.fetchall()
        grados_list = []
        grupos_list = []
        turnos_list = []
        
        for row in grados_grupos:
            grado = row['grado']
            grupo = row['grupo']
            turno = row['turno']
            cantidad = row['cantidad']
            
            if grado not in grados_list:
                grados_list.append(grado)
            if grupo not in grupos_list:
                grupos_list.append(grupo)
            if turno not in turnos_list:
                turnos_list.append(turno)
            
            print(f"  📚 {grado}° {grupo} - {turno}: {cantidad} alumnos")
        
        print()
        
        # 5. OBTENER EJEMPLOS ESPECÍFICOS CON DATOS COMPLETOS
        print("🔍 EJEMPLOS ESPECÍFICOS CON DATOS COMPLETOS:")
        print("-" * 40)
        
        cursor.execute("""
        SELECT a.nombre, de.grado, de.grupo, de.turno, de.ciclo_escolar
        FROM alumnos a
        JOIN datos_escolares de ON a.id = de.alumno_id
        ORDER BY RANDOM()
        LIMIT 5
        """)
        
        ejemplos = cursor.fetchall()
        ejemplos_list = []
        
        for i, row in enumerate(ejemplos, 1):
            ejemplo = {
                'nombre': row['nombre'],
                'grado': row['grado'],
                'grupo': row['grupo'],
                'turno': row['turno'],
                'ciclo': row['ciclo_escolar']
            }
            ejemplos_list.append(ejemplo)
            
            print(f"  {i}. {row['nombre']}")
            print(f"     📚 {row['grado']}° {row['grupo']} - {row['turno']}")
            print(f"     📅 Ciclo: {row['ciclo_escolar']}")
            print()
        
        # 6. GENERAR ARCHIVO DE PLACEHOLDERS
        print("📝 GENERANDO PLACEHOLDERS PARA BATERÍA DE PRUEBAS:")
        print("-" * 40)
        
        placeholders = {
            "apellidos": apellidos_list[:5],
            "nombres_completos": nombres_list[:5],
            "grados": list(set(grados_list))[:3],
            "grupos": list(set(grupos_list))[:3],
            "turnos": list(set(turnos_list)),
            "ejemplos_completos": ejemplos_list,
            "estadisticas": {
                "total_alumnos": total_alumnos,
                "total_datos_escolares": total_datos
            }
        }
        
        # Guardar en archivo JSON
        with open('testing_placeholders.json', 'w', encoding='utf-8') as f:
            json.dump(placeholders, f, indent=2, ensure_ascii=False)
        
        print("✅ Placeholders guardados en: testing_placeholders.json")
        print()
        
        # 7. MOSTRAR RESUMEN PARA COPIAR A BATERÍA
        print("📋 RESUMEN PARA USAR EN BATERÍA DE PRUEBAS:")
        print("=" * 80)
        print()
        
        print("🏷️  APELLIDOS PARA TESTING:")
        for i, apellido in enumerate(apellidos_list[:5], 1):
            print(f"[APELLIDO_{i}] = {apellido}")
        print()
        
        print("👤 NOMBRES COMPLETOS PARA TESTING:")
        for i, nombre in enumerate(nombres_list[:5], 1):
            print(f"[NOMBRE_COMPLETO_{i}] = {nombre}")
        print()
        
        print("🎓 CRITERIOS ACADÉMICOS:")
        print(f"[GRADO] = {random.choice(grados_list)}")
        print(f"[GRUPO] = {random.choice(grupos_list)}")
        print(f"[TURNO] = {random.choice(turnos_list)}")
        print()
        
        conn.close()
        
        return placeholders
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

if __name__ == "__main__":
    extract_random_students()
