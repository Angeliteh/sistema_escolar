#!/usr/bin/env python3
"""
Script para analizar completamente la estructura de la base de datos
"""

import sqlite3
import os
import sys

def analyze_database():
    """Analiza la estructura completa de la base de datos"""
    
    db_path = 'resources/data/alumnos.db'
    
    if not os.path.exists(db_path):
        print(f"❌ ERROR: Base de datos no encontrada en {db_path}")
        return
    
    print("=" * 60)
    print("📊 ANÁLISIS COMPLETO DE LA BASE DE DATOS")
    print("=" * 60)
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Listar todas las tablas
        print("📋 TABLAS EXISTENTES:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("  ❌ No se encontraron tablas")
            return
        
        for table in tables:
            print(f"  ✅ {table[0]}")
        print()
        
        # 2. Analizar estructura de cada tabla
        for table in tables:
            table_name = table[0]
            print("=" * 50)
            print(f"📊 TABLA: {table_name.upper()}")
            print("=" * 50)
            
            # Estructura de la tabla
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("🔧 COLUMNAS:")
            for col in columns:
                pk = " (PK)" if col[5] else ""
                not_null = " NOT NULL" if col[3] else ""
                default = f" DEFAULT {col[4]}" if col[4] else ""
                print(f"  - {col[1]}: {col[2]}{pk}{not_null}{default}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"📈 TOTAL REGISTROS: {count}")
            
            # Mostrar algunos ejemplos si hay datos
            if count > 0:
                print("📋 MUESTRA DE DATOS (primeros 3 registros):")
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                
                # Obtener nombres de columnas
                column_names = [description[0] for description in cursor.description]
                
                for i, row in enumerate(sample_data, 1):
                    print(f"  📄 Registro {i}:")
                    for col_name, value in zip(column_names, row):
                        print(f"    {col_name}: {value}")
                    print()
            print()
        
        # 3. Verificar relaciones entre tablas
        print("=" * 50)
        print("🔗 ANÁLISIS DE RELACIONES")
        print("=" * 50)
        
        # Verificar si existe tabla calificaciones
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calificaciones'")
        calificaciones_exists = cursor.fetchone()
        
        if calificaciones_exists:
            print("✅ Tabla 'calificaciones' EXISTE")
        else:
            print("❌ Tabla 'calificaciones' NO EXISTE")
            
            # Buscar tablas que puedan contener calificaciones
            print("🔍 Buscando tablas que puedan contener calificaciones...")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Buscar columnas relacionadas con calificaciones
                grade_columns = []
                for col in columns:
                    col_name = col[1].lower()
                    if any(keyword in col_name for keyword in ['calificacion', 'nota', 'promedio', 'materia', 'i', 'ii', 'iii']):
                        grade_columns.append(col[1])
                
                if grade_columns:
                    print(f"  📊 {table_name}: {', '.join(grade_columns)}")
        
        # 4. Verificar integridad referencial
        print()
        print("🔍 VERIFICANDO INTEGRIDAD REFERENCIAL:")
        
        # Verificar relación alumnos -> datos_escolares
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='datos_escolares'")
        datos_escolares_exists = cursor.fetchone()
        
        if datos_escolares_exists:
            cursor.execute("SELECT COUNT(*) FROM alumnos")
            alumnos_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT alumno_id) FROM datos_escolares")
            datos_escolares_count = cursor.fetchone()[0]
            
            print(f"  📊 Alumnos: {alumnos_count}")
            print(f"  📊 Alumnos con datos escolares: {datos_escolares_count}")
            
            if alumnos_count == datos_escolares_count:
                print("  ✅ Todos los alumnos tienen datos escolares")
            else:
                print(f"  ⚠️ {alumnos_count - datos_escolares_count} alumnos sin datos escolares")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR al analizar la base de datos: {e}")

if __name__ == "__main__":
    analyze_database()
