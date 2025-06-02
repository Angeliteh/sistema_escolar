"""
System Builder - Generador de sistemas personalizados para múltiples escuelas
Permite crear sistemas independientes con configuración específica por escuela
"""

import os
import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import zipfile

from app.core.logging.logger_manager import get_logger

class SystemBuilder:
    """
    Generador de sistemas personalizados para escuelas
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.base_system_path = Path(".")
        self.output_dir = Path("build/generated_systems")
        self.templates_dir = Path("build/templates")
        self.temp_dir = None

        # Crear directorios necesarios
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def create_system_for_school(self, school_data: Dict) -> Dict:
        """
        Crea un sistema completo personalizado para una escuela específica

        Args:
            school_data: Diccionario con datos de la escuela

        Returns:
            Dict con información del sistema generado
        """
        try:
            self.logger.info(f"🏭 Iniciando generación de sistema para: {school_data.get('name', 'Escuela')}")

            # Validar datos de entrada
            validation_result = self._validate_school_data(school_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Datos inválidos: {validation_result['errors']}",
                    "system_path": None
                }

            # Crear directorio temporal
            self.temp_dir = tempfile.mkdtemp(prefix="system_build_")
            self.logger.info(f"📁 Directorio temporal: {self.temp_dir}")

            # Paso 1: Copiar sistema base
            self.logger.info("📋 Paso 1: Copiando sistema base...")
            base_copy_path = self._copy_base_system()

            # Paso 2: Personalizar configuración
            self.logger.info("⚙️ Paso 2: Personalizando configuración...")
            self._customize_configuration(base_copy_path, school_data)

            # Paso 3: Personalizar plantillas
            self.logger.info("🎨 Paso 3: Personalizando plantillas...")
            self._customize_templates(base_copy_path, school_data)

            # Paso 4: Configurar base de datos
            self.logger.info("🗄️ Paso 4: Configurando base de datos...")
            self._setup_database(base_copy_path, school_data)

            # Paso 5: Crear ejecutable
            self.logger.info("📦 Paso 5: Creando ejecutable...")
            executable_path = self._create_executable(base_copy_path, school_data)

            # Paso 6: Crear paquete final
            self.logger.info("🎁 Paso 6: Creando paquete final...")
            final_package = self._create_final_package(executable_path, school_data)

            # Limpiar directorio temporal
            self._cleanup_temp_directory()

            self.logger.info(f"✅ Sistema generado exitosamente: {final_package}")

            return {
                "success": True,
                "system_path": final_package,
                "school_name": school_data.get("name"),
                "generated_at": datetime.now().isoformat(),
                "package_size": self._get_file_size(final_package)
            }

        except Exception as e:
            self.logger.error(f"❌ Error generando sistema: {e}")
            self._cleanup_temp_directory()
            return {
                "success": False,
                "error": str(e),
                "system_path": None
            }

    def _validate_school_data(self, school_data: Dict) -> Dict:
        """Valida los datos de la escuela"""
        errors = []

        # Campos obligatorios
        required_fields = ["name", "cct", "director"]
        for field in required_fields:
            if not school_data.get(field):
                errors.append(f"Campo obligatorio faltante: {field}")

        # Validaciones específicas
        if school_data.get("cct") and len(school_data["cct"]) != 10:
            errors.append("CCT debe tener exactamente 10 caracteres")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _copy_base_system(self) -> Path:
        """Copia el sistema base al directorio temporal"""
        base_copy_path = Path(self.temp_dir) / "system_base"

        # Archivos y directorios a copiar
        items_to_copy = [
            "app/",
            "resources/",
            "hybrid_launcher.py",
            "dev_launcher.py",
            "ai_chat.py",
            "main_qt.py",
            "database_admin.py",
            "requirements.txt"
        ]

        base_copy_path.mkdir(exist_ok=True)

        for item in items_to_copy:
            source = self.base_system_path / item
            target = base_copy_path / item

            if source.exists():
                if source.is_dir():
                    shutil.copytree(source, target, dirs_exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)

                self.logger.debug(f"   ✅ Copiado: {item}")

        return base_copy_path

    def _customize_configuration(self, system_path: Path, school_data: Dict):
        """Personaliza la configuración del sistema"""

        # Crear configuración personalizada
        config = {
            "school_info": {
                "name": school_data.get("name", "").upper(),
                "cct": school_data.get("cct", "").upper(),
                "director": school_data.get("director", "").upper(),
                "address": school_data.get("address", ""),
                "phone": school_data.get("phone", ""),
                "email": school_data.get("email", ""),
                "zone": school_data.get("zone", ""),
                "sector": school_data.get("sector", "")
            },
            "academic_info": {
                "current_year": school_data.get("academic_year", "2024-2025"),
                "grades": school_data.get("grades", [1, 2, 3, 4, 5, 6]),
                "groups": school_data.get("groups", ["A", "B"]),
                "shifts": school_data.get("shifts", ["MATUTINO"]),
                "education_level": "PRIMARIA"
            },
            "location_info": {
                "city": school_data.get("city", ""),
                "state": school_data.get("state", ""),
                "country": "MÉXICO"
            },
            "customization": {
                "logo_file": school_data.get("logo_file", "logo_educacion.png"),
                "primary_color": school_data.get("primary_color", "#2C3E50"),
                "secondary_color": school_data.get("secondary_color", "#3498DB"),
                "use_custom_templates": school_data.get("use_custom_templates", False),
                "show_photos": school_data.get("show_photos", True)
            },
            "features": {
                "enable_photos": True,
                "enable_grades": True,
                "enable_transfer": True,
                "enable_ai_chat": True,
                "enable_pdf_transform": True
            },
            "system_info": {
                "version": "2.0.0",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "configured_by": "system_builder",
                "school_id": self._generate_school_id(school_data),
                "build_type": "commercial"
            }
        }

        # Guardar configuración
        config_path = system_path / "school_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Crear archivo de versión
        version_info = {
            "version": "2.0.0",
            "build_date": datetime.now().isoformat(),
            "configuration_date": datetime.now().isoformat(),
            "school_name": school_data.get("name"),
            "school_id": self._generate_school_id(school_data),
            "configured": True,
            "build_type": "commercial"
        }

        version_path = system_path / "version.json"
        with open(version_path, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)

    def _customize_templates(self, system_path: Path, school_data: Dict):
        """Personaliza las plantillas de constancias"""
        templates_path = system_path / "resources" / "templates"

        if not templates_path.exists():
            return

        # Personalizar cada plantilla
        for template_file in templates_path.glob("*.html"):
            self._customize_single_template(template_file, school_data)

    def _customize_single_template(self, template_path: Path, school_data: Dict):
        """Personaliza una plantilla específica"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Aplicar personalizaciones de colores
            primary_color = school_data.get("primary_color", "#2C3E50")
            secondary_color = school_data.get("secondary_color", "#3498DB")

            # Reemplazar colores en CSS
            content = content.replace("#2C3E50", primary_color)
            content = content.replace("#3498DB", secondary_color)

            # Guardar plantilla personalizada
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.logger.debug(f"   ✅ Plantilla personalizada: {template_path.name}")

        except Exception as e:
            self.logger.warning(f"   ⚠️ Error personalizando plantilla {template_path.name}: {e}")

    def _setup_database(self, system_path: Path, school_data: Dict):
        """Configura la base de datos inicial"""
        db_dir = system_path / "resources" / "data"
        db_dir.mkdir(parents=True, exist_ok=True)

        # Copiar base de datos base (vacía o con datos de ejemplo)
        source_db = self.base_system_path / "resources" / "data" / "alumnos.db"
        target_db = db_dir / "alumnos.db"

        if source_db.exists():
            shutil.copy2(source_db, target_db)
            self.logger.debug("   ✅ Base de datos copiada")
        else:
            # Crear base de datos vacía si no existe
            target_db.touch()
            self.logger.debug("   ✅ Base de datos vacía creada")

    def _create_executable(self, system_path: Path, school_data: Dict) -> Path:
        """Crea el ejecutable del sistema"""
        school_name_safe = self._sanitize_filename(school_data.get("name", "Escuela"))
        executable_name = f"Sistema_Constancias_{school_name_safe}"

        # Crear directorio con sistema completo + ejecutable
        executable_dir = self.output_dir / executable_name

        if executable_dir.exists():
            shutil.rmtree(executable_dir)

        # Copiar sistema base
        shutil.copytree(system_path, executable_dir)

        # Copiar ejecutable desde dist/ si existe
        dist_dir = Path("dist")
        if dist_dir.exists():
            for exe_file in dist_dir.glob("*.exe"):
                target_exe = executable_dir / "SistemaConstancias.exe"
                shutil.copy2(exe_file, target_exe)
                self.logger.info(f"Ejecutable copiado: {exe_file.name} -> SistemaConstancias.exe")
                break

        # Crear script de inicio alternativo
        startup_script = executable_dir / "iniciar.bat"
        with open(startup_script, "w", encoding="utf-8") as f:
            f.write(f"""@echo off
title Sistema de Constancias - {school_data.get('name', 'Escuela')}
echo Iniciando Sistema de Constancias...
echo Escuela: {school_data.get('name', 'Escuela')}
echo.

REM Intentar ejecutar el ejecutable
if exist "SistemaConstancias.exe" (
    echo Ejecutando version compilada...
    SistemaConstancias.exe
) else (
    REM Fallback a Python si no hay ejecutable
    echo Ejecutando version Python...
    if exist "hybrid_launcher.py" (
        python hybrid_launcher.py
    ) else (
        echo ERROR: No se encontro el sistema
        pause
    )
)
""")

        return executable_dir

    def _create_final_package(self, executable_path: Path, school_data: Dict) -> Path:
        """Crea el paquete final para distribución"""
        school_name_safe = self._sanitize_filename(school_data.get("name", "Escuela"))
        package_name = f"Sistema_Constancias_{school_name_safe}_{datetime.now().strftime('%Y%m%d')}.zip"
        package_path = self.output_dir / package_name

        # Crear archivo ZIP
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in executable_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(executable_path)
                    zipf.write(file_path, arcname)

        return package_path

    def _generate_school_id(self, school_data: Dict) -> str:
        """Genera un ID único para la escuela"""
        import hashlib

        # Usar CCT y nombre para generar ID único
        data = f"{school_data.get('cct', '')}{school_data.get('name', '')}"
        return hashlib.md5(data.encode()).hexdigest()[:8].upper()

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza un nombre para uso como nombre de archivo"""
        import re

        # Remover caracteres especiales y espacios
        sanitized = re.sub(r'[^\w\s-]', '', filename)
        sanitized = re.sub(r'[-\s]+', '_', sanitized)
        return sanitized.strip('_')

    def _get_file_size(self, file_path: Path) -> str:
        """Obtiene el tamaño de un archivo en formato legible"""
        size_bytes = file_path.stat().st_size

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} TB"

    def _cleanup_temp_directory(self):
        """Limpia el directorio temporal"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.debug(f"🗑️ Directorio temporal limpiado: {self.temp_dir}")
            except Exception as e:
                self.logger.warning(f"⚠️ Error limpiando directorio temporal: {e}")

    def list_generated_systems(self) -> List[Dict]:
        """Lista todos los sistemas generados"""
        systems = []

        for item in self.output_dir.iterdir():
            if item.is_file() and item.suffix == '.zip':
                systems.append({
                    "name": item.stem,
                    "path": str(item),
                    "size": self._get_file_size(item),
                    "created": datetime.fromtimestamp(item.stat().st_ctime).isoformat()
                })

        return sorted(systems, key=lambda x: x["created"], reverse=True)


def create_system_for_current_school() -> Dict:
    """
    Función de conveniencia para crear un sistema para la escuela actual
    """
    # Leer configuración actual
    try:
        with open("school_config.json", 'r', encoding='utf-8') as f:
            current_config = json.load(f)

        # Extraer datos necesarios
        school_data = {
            "name": current_config["school_info"]["name"],
            "cct": current_config["school_info"]["cct"],
            "director": current_config["school_info"]["director"],
            "address": current_config["school_info"].get("address", ""),
            "phone": current_config["school_info"].get("phone", ""),
            "email": current_config["school_info"].get("email", ""),
            "zone": current_config["school_info"].get("zone", ""),
            "sector": current_config["school_info"].get("sector", ""),
            "city": current_config["location_info"].get("city", ""),
            "state": current_config["location_info"].get("state", ""),
            "academic_year": current_config["academic_info"].get("current_year", "2024-2025"),
            "grades": current_config["academic_info"].get("grades", [1, 2, 3, 4, 5, 6]),
            "groups": current_config["academic_info"].get("groups", ["A", "B"]),
            "shifts": current_config["academic_info"].get("shifts", ["MATUTINO"]),
            "primary_color": current_config["customization"].get("primary_color", "#2C3E50"),
            "secondary_color": current_config["customization"].get("secondary_color", "#3498DB"),
            "show_photos": current_config["customization"].get("show_photos", True)
        }

        # Crear sistema
        builder = SystemBuilder()
        return builder.create_system_for_school(school_data)

    except Exception as e:
        return {
            "success": False,
            "error": f"Error leyendo configuración actual: {str(e)}",
            "system_path": None
        }
