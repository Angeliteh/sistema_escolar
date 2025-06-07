#!/usr/bin/env python3
"""
🎓 PREPARAR SISTEMA PARA ENTREGA
Crear base de datos vacía lista para recibir alumnos gradualmente
"""

import os
import shutil
import sqlite3
from pathlib import Path
import json

def main():
    """Función principal de preparación"""
    print("🎓 PREPARANDO SISTEMA PARA ENTREGA")
    print("=" * 60)
    
    # 1. Crear backup de la base de datos actual
    print("💾 CREANDO BACKUP DE BASE DE DATOS ACTUAL:")
    
    db_paths = [
        "resources/data/alumnos.db", 
        "alumnos.db"
    ]
    
    found_db = None
    for path in db_paths:
        if os.path.exists(path):
            found_db = path
            break
    
    if found_db:
        backup_path = f"{found_db}.backup_entrega"
        shutil.copy2(found_db, backup_path)
        print(f"   ✅ Backup creado: {backup_path}")
        
        # Verificar datos actuales
        conn = sqlite3.connect(found_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        total_alumnos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM datos_escolares WHERE calificaciones IS NOT NULL AND calificaciones != ''")
        alumnos_con_calificaciones = cursor.fetchone()[0]
        
        print(f"   📊 Datos actuales:")
        print(f"      - Total alumnos: {total_alumnos}")
        print(f"      - Con calificaciones: {alumnos_con_calificaciones}")
        
        conn.close()
    else:
        print("   ⚠️ No se encontró base de datos actual")
        return False
    
    # 2. Crear base de datos vacía para entrega
    print(f"\n🗄️ CREANDO BASE DE DATOS VACÍA PARA ENTREGA:")
    
    db_entrega = "resources/data/alumnos_entrega.db"
    
    # Eliminar si existe
    if os.path.exists(db_entrega):
        os.remove(db_entrega)
    
    # Crear nueva base de datos vacía
    conn_entrega = sqlite3.connect(db_entrega)
    cursor_entrega = conn_entrega.cursor()
    
    # Crear tablas con la estructura actual
    cursor_entrega.execute("""
        CREATE TABLE alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curp TEXT UNIQUE,
            nombre TEXT NOT NULL,
            matricula TEXT,
            fecha_nacimiento DATE,
            fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor_entrega.execute("""
        CREATE TABLE datos_escolares (
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
    
    # Crear tabla constancias (opcional)
    cursor_entrega.execute("""
        CREATE TABLE constancias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            tipo_constancia TEXT,
            fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            archivo_path TEXT,
            FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
        )
    """)
    
    conn_entrega.commit()
    conn_entrega.close()
    
    print(f"   ✅ Base de datos vacía creada: {db_entrega}")
    print(f"   📋 Tablas creadas: alumnos, datos_escolares, constancias")
    
    # 3. Crear alumno de ejemplo con las nuevas materias
    print(f"\n👤 CREANDO ALUMNO DE EJEMPLO:")
    
    conn_ejemplo = sqlite3.connect(db_entrega)
    cursor_ejemplo = conn_ejemplo.cursor()
    
    # Insertar alumno de ejemplo
    cursor_ejemplo.execute("""
        INSERT INTO alumnos (curp, nombre, matricula, fecha_nacimiento)
        VALUES (?, ?, ?, ?)
    """, ("EJEMPLO123456HDFRNN01", "ALUMNO DE EJEMPLO", "2024001", "2015-01-01"))
    
    alumno_id = cursor_ejemplo.lastrowid
    
    # Crear calificaciones de ejemplo con las nuevas materias
    calificaciones_ejemplo = [
        {
            "nombre": "LENGUAJES",
            "periodo_1": 8.5,
            "periodo_2": 9.0,
            "periodo_3": 8.8,
            "promedio": 8.8
        },
        {
            "nombre": "SABERES Y PENSAMIENTO CIENTÍFICO",
            "periodo_1": 7.5,
            "periodo_2": 8.0,
            "periodo_3": 7.8,
            "promedio": 7.8
        },
        {
            "nombre": "ÉTICA NATURALEZA Y SOCIEDADES",
            "periodo_1": 9.0,
            "periodo_2": 8.5,
            "periodo_3": 8.8,
            "promedio": 8.8
        },
        {
            "nombre": "DE LO HUMANO Y LO COMUNITARIO",
            "periodo_1": 8.0,
            "periodo_2": 8.5,
            "periodo_3": 8.3,
            "promedio": 8.3
        }
    ]
    
    # Insertar datos escolares de ejemplo
    cursor_ejemplo.execute("""
        INSERT INTO datos_escolares (alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        alumno_id,
        "2024-2025",
        1,
        "A",
        "MATUTINO",
        "PROF. MAXIMO GAMIZ FERNANDEZ",
        "10DPR0392H",
        json.dumps(calificaciones_ejemplo)
    ))
    
    conn_ejemplo.commit()
    conn_ejemplo.close()
    
    print(f"   ✅ Alumno de ejemplo creado")
    print(f"   📚 Con calificaciones de las 4 materias nuevas")
    
    # 4. Limpiar directorios de fotos y PDFs
    print(f"\n🧹 LIMPIANDO DIRECTORIOS PARA ENTREGA:")
    
    # Crear backup de fotos actuales
    photos_dir = Path("resources/photos")
    if photos_dir.exists() and any(photos_dir.iterdir()):
        backup_photos = Path("backup_photos_entrega")
        if backup_photos.exists():
            shutil.rmtree(backup_photos)
        shutil.copytree(photos_dir, backup_photos)
        print(f"   💾 Backup de fotos: {backup_photos}")
        
        # Limpiar directorio de fotos (mantener solo ejemplo si existe)
        for foto in photos_dir.glob("*.jpg"):
            if foto.name != "EJEMPLO123456HDFRNN01.jpg":
                foto.unlink()
        
        print(f"   🧹 Directorio de fotos limpiado")
    
    # Limpiar PDFs generados
    output_dir = Path("output/pdfs")
    if output_dir.exists():
        backup_pdfs = Path("backup_pdfs_entrega")
        if backup_pdfs.exists():
            shutil.rmtree(backup_pdfs)
        shutil.copytree(output_dir, backup_pdfs)
        print(f"   💾 Backup de PDFs: {backup_pdfs}")
        
        # Limpiar directorio de PDFs
        for pdf in output_dir.glob("*.pdf"):
            pdf.unlink()
        
        print(f"   🧹 Directorio de PDFs limpiado")
    
    # 5. Verificar configuración escolar
    print(f"\n⚙️ VERIFICANDO CONFIGURACIÓN ESCOLAR:")
    
    with open("school_config.json", 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    materias_config = config.get("academic_info", {}).get("materias_por_grado", {})
    
    print(f"   📚 Materias configuradas:")
    for grado, materias in materias_config.items():
        print(f"      Grado {grado}: {len(materias)} materias")
        for materia in materias:
            print(f"         - {materia}")
    
    # 6. Crear instrucciones de uso
    print(f"\n📋 CREANDO INSTRUCCIONES DE USO:")
    
    instrucciones = """# 🎓 INSTRUCCIONES PARA RECIBIR ALUMNOS

## 🚀 INICIO RÁPIDO

### 1. VERIFICAR SISTEMA
```bash
python ai_chat.py
```
- Preguntar: "buscar alumnos de 1° grado"
- Debe mostrar el alumno de ejemplo

### 2. REGISTRAR NUEVO ALUMNO
1. **Arrastrar PDF** de constancia al área de carga
2. **Verificar datos** extraídos automáticamente
3. **Confirmar y guardar** en base de datos
4. **Foto incluida** automáticamente si está en el PDF

### 3. MATERIAS CONFIGURADAS
Todos los alumnos tendrán estas 4 materias:
- LENGUAJES
- SABERES Y PENSAMIENTO CIENTÍFICO  
- ÉTICA NATURALEZA Y SOCIEDADES
- DE LO HUMANO Y LO COMUNITARIO

### 4. PROCESO GRADUAL
- ✅ Sistema funciona desde el primer alumno
- ✅ Cada PDF agregado suma un alumno más
- ✅ Búsquedas y constancias disponibles inmediatamente
- ✅ Fotos y calificaciones incluidas automáticamente

## 🎯 COMANDOS ÚTILES

### Búsquedas:
- "alumnos de 3° A"
- "buscar por nombre Juan"
- "estudiantes del turno matutino"

### Constancias:
- "constancia de estudio para [nombre]"
- "constancia con calificaciones para [nombre]"
- "constancia de traslado para [nombre]"

## 📊 ESTADO INICIAL
- 📁 Base de datos: VACÍA (solo 1 ejemplo)
- 📸 Fotos: VACÍAS (listas para recibir)
- 📄 PDFs: VACÍOS (listos para generar)
- ⚙️ Configuración: LISTA para la escuela

¡Sistema listo para recibir alumnos gradualmente! 🎉
"""
    
    with open("INSTRUCCIONES_ENTREGA.md", 'w', encoding='utf-8') as f:
        f.write(instrucciones)
    
    print(f"   ✅ Instrucciones creadas: INSTRUCCIONES_ENTREGA.md")
    
    # 7. Resumen final
    print(f"\n🎉 SISTEMA PREPARADO PARA ENTREGA")
    print("=" * 60)
    
    print(f"📊 ESTADO FINAL:")
    print(f"   ✅ Base de datos vacía: {db_entrega}")
    print(f"   ✅ Alumno de ejemplo: 1 registro")
    print(f"   ✅ Materias actualizadas: 4 materias por grado")
    print(f"   ✅ Directorios limpios: fotos y PDFs")
    print(f"   ✅ Backups seguros: datos actuales preservados")
    print(f"   ✅ Instrucciones: INSTRUCCIONES_ENTREGA.md")
    
    print(f"\n🚀 PRÓXIMOS PASOS:")
    print(f"   1. Reemplazar base de datos actual con la de entrega")
    print(f"   2. Probar con: python ai_chat.py")
    print(f"   3. Verificar búsqueda del alumno ejemplo")
    print(f"   4. Probar carga de PDF para nuevo alumno")
    print(f"   5. ¡Entregar sistema listo!")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ PREPARACIÓN EXITOSA")
        
        respuesta = input(f"\n¿Reemplazar base de datos actual con la de entrega? (s/N): ").lower().strip()
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            # Reemplazar base de datos
            shutil.copy2("resources/data/alumnos_entrega.db", "resources/data/alumnos.db")
            print(f"✅ Base de datos reemplazada")
            print(f"🎯 Sistema listo para entregar")
        else:
            print(f"💾 Base de datos de entrega disponible en: resources/data/alumnos_entrega.db")
            print(f"🔧 Reemplazar manualmente cuando estés listo")
    else:
        print(f"\n❌ PREPARACIÓN FALLÓ")
    
    input("\nPresiona Enter para continuar...")
