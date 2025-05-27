#!/usr/bin/env python
"""
Generador de Sistemas para Escuelas
Crea versiones personalizadas del sistema para diferentes escuelas
"""

import os
import json
import shutil
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
import argparse

class SchoolSystemGenerator:
    """Generador automático de sistemas personalizados para escuelas"""
    
    def __init__(self, base_system_path: str = "./"):
        self.base_path = os.path.abspath(base_system_path)
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging básico"""
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def generate_school_system(self, school_data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Genera un sistema completo personalizado para una escuela
        
        Args:
            school_data: Datos de la escuela
            output_path: Directorio donde crear el sistema
            
        Returns:
            Diccionario con el resultado de la generación
        """
        
        self.logger.info(f"🏫 Generando sistema para: {school_data.get('name', 'Escuela sin nombre')}")
        
        try:
            # 1. Crear directorio de salida
            os.makedirs(output_path, exist_ok=True)
            
            # 2. Copiar sistema base
            self._copy_base_system(output_path)
            
            # 3. Crear configuración específica de la escuela
            self._create_school_config(school_data, output_path)
            
            # 4. Personalizar plantillas HTML
            self._customize_templates(school_data, output_path)
            
            # 5. Crear base de datos inicial
            self._setup_database(school_data, output_path)
            
            # 6. Configurar recursos (logos, etc.)
            self._setup_resources(school_data, output_path)
            
            # 7. Crear scripts de inicio personalizados
            self._create_startup_scripts(school_data, output_path)
            
            # 8. Crear documentación específica
            self._create_documentation(school_data, output_path)
            
            result = {
                "status": "success",
                "school_name": school_data.get("name", ""),
                "school_cct": school_data.get("cct", ""),
                "output_path": output_path,
                "files_created": self._count_files(output_path),
                "generation_date": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Sistema generado exitosamente en: {output_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error al generar sistema: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "school_name": school_data.get("name", ""),
                "output_path": output_path
            }
    
    def _copy_base_system(self, output_path: str):
        """Copia el sistema base al directorio de salida"""
        
        # Elementos a copiar del sistema base
        items_to_copy = [
            "app/",
            "resources/templates/",
            "resources/images/logos/",  # Logos base
            "main.py",
            "ai_chat.py", 
            "requirements.txt",
            ".env.example"
        ]
        
        self.logger.info("📁 Copiando sistema base...")
        
        for item in items_to_copy:
            source = os.path.join(self.base_path, item)
            dest = os.path.join(output_path, item)
            
            if os.path.isdir(source):
                # Copiar directorio completo
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
                self.logger.info(f"  📁 Copiado directorio: {item}")
            elif os.path.isfile(source):
                # Copiar archivo individual
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(source, dest)
                self.logger.info(f"  📄 Copiado archivo: {item}")
    
    def _create_school_config(self, school_data: Dict[str, Any], output_path: str):
        """Crea el archivo de configuración específico de la escuela"""
        
        self.logger.info("⚙️ Creando configuración de escuela...")
        
        # Plantilla base de configuración
        config_template = {
            "school_info": {
                "name": school_data.get("name", "ESCUELA EJEMPLO"),
                "cct": school_data.get("cct", "00DPR0000X"),
                "director": school_data.get("director", "DIRECTOR EJEMPLO"),
                "address": school_data.get("address", "DIRECCIÓN EJEMPLO"),
                "phone": school_data.get("phone", ""),
                "email": school_data.get("email", ""),
                "zone": school_data.get("zone", "ZONA ESCOLAR 01"),
                "sector": school_data.get("sector", "SECTOR 01")
            },
            "academic_info": {
                "current_year": school_data.get("current_year", "2024-2025"),
                "grades": school_data.get("grades", [1, 2, 3, 4, 5, 6]),
                "groups": school_data.get("groups", ["A", "B"]),
                "shifts": school_data.get("shifts", ["MATUTINO"]),
                "education_level": school_data.get("education_level", "PRIMARIA")
            },
            "location_info": {
                "city": school_data.get("city", "CIUDAD EJEMPLO"),
                "state": school_data.get("state", "ESTADO EJEMPLO"),
                "country": "MÉXICO"
            },
            "customization": {
                "logo_file": f"logo_{school_data.get('cct', 'ejemplo').lower()}.png",
                "primary_color": school_data.get("primary_color", "#2C3E50"),
                "secondary_color": school_data.get("secondary_color", "#3498DB"),
                "use_custom_templates": school_data.get("use_custom_templates", False),
                "show_photos": school_data.get("show_photos", True)
            },
            "features": {
                "enable_photos": school_data.get("enable_photos", True),
                "enable_grades": school_data.get("enable_grades", True),
                "enable_transfer": school_data.get("enable_transfer", True),
                "enable_ai_chat": school_data.get("enable_ai_chat", True),
                "enable_pdf_transform": school_data.get("enable_pdf_transform", True)
            },
            "system_info": {
                "version": "1.0.0",
                "created_date": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "generated_by": "SchoolSystemGenerator"
            }
        }
        
        # Guardar configuración
        config_path = os.path.join(output_path, "school_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_template, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"  ✅ Configuración creada: school_config.json")
    
    def _customize_templates(self, school_data: Dict[str, Any], output_path: str):
        """Personaliza las plantillas HTML con datos específicos de la escuela"""
        
        self.logger.info("🎨 Personalizando plantillas HTML...")
        
        templates_path = os.path.join(output_path, "resources/templates")
        
        # Reemplazos a realizar en las plantillas
        replacements = {
            "{{SCHOOL_NAME}}": school_data.get("name", "ESCUELA EJEMPLO"),
            "{{SCHOOL_CCT}}": school_data.get("cct", "00DPR0000X"),
            "{{DIRECTOR_NAME}}": school_data.get("director", "DIRECTOR EJEMPLO"),
            "{{CURRENT_YEAR}}": school_data.get("current_year", "2024-2025"),
            "{{CITY}}": school_data.get("city", "CIUDAD EJEMPLO"),
            "{{STATE}}": school_data.get("state", "ESTADO EJEMPLO"),
            "{{SCHOOL_ADDRESS}}": school_data.get("address", "DIRECCIÓN EJEMPLO")
        }
        
        # Procesar cada plantilla HTML
        for template_file in os.listdir(templates_path):
            if template_file.endswith('.html'):
                template_path = os.path.join(templates_path, template_file)
                
                # Leer contenido
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar reemplazos
                for placeholder, value in replacements.items():
                    content = content.replace(placeholder, value)
                
                # Guardar contenido modificado
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.info(f"  ✅ Plantilla personalizada: {template_file}")
    
    def _setup_database(self, school_data: Dict[str, Any], output_path: str):
        """Crea la base de datos inicial para la escuela"""
        
        self.logger.info("🗄️ Configurando base de datos...")
        
        # Crear directorio de datos
        db_dir = os.path.join(output_path, "resources/data")
        os.makedirs(db_dir, exist_ok=True)
        
        db_path = os.path.join(db_dir, "alumnos.db")
        
        # Crear base de datos con estructura
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tablas principales
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curp TEXT UNIQUE,
            nombre TEXT NOT NULL,
            matricula TEXT,
            fecha_nacimiento TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS datos_escolares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            ciclo_escolar TEXT,
            grado INTEGER,
            grupo TEXT,
            turno TEXT,
            escuela TEXT,
            cct TEXT,
            calificaciones TEXT,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS constancias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER,
            tipo TEXT,
            fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archivo_path TEXT,
            FOREIGN KEY (alumno_id) REFERENCES alumnos (id)
        )
        ''')
        
        # Tabla de configuración de la escuela
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracion_escuela (
            id INTEGER PRIMARY KEY,
            nombre_escuela TEXT,
            cct TEXT,
            director TEXT,
            ciclo_actual TEXT,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Insertar configuración inicial
        cursor.execute('''
        INSERT OR REPLACE INTO configuracion_escuela 
        (id, nombre_escuela, cct, director, ciclo_actual)
        VALUES (1, ?, ?, ?, ?)
        ''', (
            school_data.get("name", "ESCUELA EJEMPLO"),
            school_data.get("cct", "00DPR0000X"),
            school_data.get("director", "DIRECTOR EJEMPLO"),
            school_data.get("current_year", "2024-2025")
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"  ✅ Base de datos creada: alumnos.db")
    
    def _setup_resources(self, school_data: Dict[str, Any], output_path: str):
        """Configura recursos específicos (logos, fotos, etc.)"""
        
        self.logger.info("🖼️ Configurando recursos...")
        
        # Crear directorios necesarios
        photos_dir = os.path.join(output_path, "resources/images/photos")
        output_dir = os.path.join(output_path, "resources/output")
        
        os.makedirs(photos_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Copiar logo específico si se proporciona
        if "logo_path" in school_data and os.path.exists(school_data["logo_path"]):
            logo_dest = os.path.join(
                output_path, 
                "resources/images/logos", 
                f"logo_{school_data.get('cct', 'ejemplo').lower()}.png"
            )
            shutil.copy2(school_data["logo_path"], logo_dest)
            self.logger.info(f"  ✅ Logo copiado: {os.path.basename(logo_dest)}")
        
        # Crear archivo README en directorio de fotos
        readme_path = os.path.join(photos_dir, "README.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""Directorio de Fotos - {school_data.get('name', 'Escuela')}

Instrucciones:
1. Las fotos deben nombrarse con la CURP del alumno
2. Formato: CURP.jpg (ejemplo: ABCD123456HDFRRL01.jpg)
3. Tamaño recomendado: 300x400 píxeles
4. Formato soportado: JPG, PNG

Generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}
""")
        
        self.logger.info(f"  ✅ Directorios de recursos configurados")
    
    def _create_startup_scripts(self, school_data: Dict[str, Any], output_path: str):
        """Crea scripts de inicio personalizados"""
        
        self.logger.info("🚀 Creando scripts de inicio...")
        
        school_name_clean = school_data.get("name", "escuela").replace(" ", "_").lower()
        cct_clean = school_data.get("cct", "ejemplo").lower()
        
        # Script principal personalizado
        script_content = f'''#!/usr/bin/env python
"""
Sistema de Constancias - {school_data.get("name", "Escuela")}
CCT: {school_data.get("cct", "00DPR0000X")}
Director: {school_data.get("director", "Director")}

Generado automáticamente el {datetime.now().strftime('%d/%m/%Y')}
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la aplicación principal
from main import main

if __name__ == "__main__":
    print("🏫 Iniciando Sistema de Constancias")
    print(f"   Escuela: {school_data.get('name', 'Escuela')}")
    print(f"   CCT: {school_data.get('cct', '00DPR0000X')}")
    print()
    
    exit_code = main()
    sys.exit(exit_code)
'''
        
        # Guardar script principal
        script_path = os.path.join(output_path, f"iniciar_{cct_clean}.py")
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Script batch para Windows
        batch_content = f'''@echo off
title Sistema de Constancias - {school_data.get("name", "Escuela")}
echo Iniciando Sistema de Constancias...
echo Escuela: {school_data.get("name", "Escuela")}
echo CCT: {school_data.get("cct", "00DPR0000X")}
echo.
python iniciar_{cct_clean}.py
pause
'''
        
        batch_path = os.path.join(output_path, f"iniciar_{cct_clean}.bat")
        with open(batch_path, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        self.logger.info(f"  ✅ Scripts creados: iniciar_{cct_clean}.py/.bat")
    
    def _create_documentation(self, school_data: Dict[str, Any], output_path: str):
        """Crea documentación específica para la escuela"""
        
        self.logger.info("📚 Creando documentación...")
        
        readme_content = f"""# Sistema de Constancias - {school_data.get('name', 'Escuela')}

## Información de la Escuela
- **Nombre**: {school_data.get('name', 'Escuela')}
- **CCT**: {school_data.get('cct', '00DPR0000X')}
- **Director**: {school_data.get('director', 'Director')}
- **Ciclo Escolar**: {school_data.get('current_year', '2024-2025')}

## Inicio Rápido

### Windows
Hacer doble clic en: `iniciar_{school_data.get('cct', 'ejemplo').lower()}.bat`

### Línea de comandos
```bash
python iniciar_{school_data.get('cct', 'ejemplo').lower()}.py
```

## Configuración

El sistema está preconfigurado para esta escuela. Los datos se encuentran en:
- **Configuración**: `school_config.json`
- **Base de datos**: `resources/data/alumnos.db`
- **Plantillas**: `resources/templates/`

## Características Habilitadas
- ✅ Chat con IA
- ✅ Generación de constancias
- ✅ Transformación de PDFs
- ✅ Gestión de fotos
- ✅ Base de datos integrada

## Soporte
Para soporte técnico, consultar la documentación completa en la carpeta `docs/`.

---
*Sistema generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}*
"""
        
        readme_path = os.path.join(output_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.logger.info(f"  ✅ Documentación creada: README.md")
    
    def _count_files(self, directory: str) -> int:
        """Cuenta el número total de archivos creados"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count
    
    def generate_multiple_schools(self, schools_data: List[Dict[str, Any]], output_base_dir: str) -> List[Dict[str, Any]]:
        """Genera sistemas para múltiples escuelas"""
        
        self.logger.info(f"🏫 Generando sistemas para {len(schools_data)} escuelas...")
        
        results = []
        
        for i, school_data in enumerate(schools_data, 1):
            self.logger.info(f"📋 Procesando escuela {i}/{len(schools_data)}")
            
            # Crear directorio específico para la escuela
            school_cct = school_data.get('cct', f'escuela_{i}').lower()
            school_dir = os.path.join(output_base_dir, f"sistema_{school_cct}")
            
            # Generar sistema
            result = self.generate_school_system(school_data, school_dir)
            results.append(result)
        
        # Crear resumen
        self._create_batch_summary(results, output_base_dir)
        
        return results
    
    def _create_batch_summary(self, results: List[Dict[str, Any]], output_base_dir: str):
        """Crea un resumen de la generación masiva"""
        
        summary = {
            "generation_date": datetime.now().isoformat(),
            "total_schools": len(results),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "schools": results
        }
        
        summary_path = os.path.join(output_base_dir, "generation_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Resumen creado: generation_summary.json")


def main():
    """Función principal para uso desde línea de comandos"""
    parser = argparse.ArgumentParser(description="Generador de Sistemas para Escuelas")
    parser.add_argument("--school-name", required=True, help="Nombre de la escuela")
    parser.add_argument("--cct", required=True, help="CCT de la escuela")
    parser.add_argument("--director", required=True, help="Nombre del director")
    parser.add_argument("--output", required=True, help="Directorio de salida")
    parser.add_argument("--city", default="Ciudad", help="Ciudad de la escuela")
    parser.add_argument("--state", default="Estado", help="Estado de la escuela")
    parser.add_argument("--logo", help="Ruta al logo de la escuela")
    
    args = parser.parse_args()
    
    # Crear datos de la escuela
    school_data = {
        "name": args.school_name,
        "cct": args.cct,
        "director": args.director,
        "city": args.city,
        "state": args.state,
        "current_year": "2024-2025"
    }
    
    if args.logo:
        school_data["logo_path"] = args.logo
    
    # Generar sistema
    generator = SchoolSystemGenerator()
    result = generator.generate_school_system(school_data, args.output)
    
    if result["status"] == "success":
        print(f"✅ Sistema generado exitosamente para {args.school_name}")
        print(f"📁 Ubicación: {args.output}")
    else:
        print(f"❌ Error al generar sistema: {result['error_message']}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
