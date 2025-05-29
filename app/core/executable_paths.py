"""
Gestión de rutas para ejecutables
Maneja diferencias entre desarrollo y distribución
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
import tempfile

from app.core.logging.logger_manager import get_logger

class ExecutablePathManager:
    """Gestor de rutas para ejecutables y desarrollo"""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.is_executable = getattr(sys, 'frozen', False)
        self.is_development = not self.is_executable

        # Determinar directorios base
        if self.is_executable:
            # Ejecutable: usar directorio del usuario
            self.app_name = "SistemaConstancias"
            self.user_data_dir = Path.home() / f"{self.app_name}_Data"
            self.executable_dir = Path(sys.executable).parent
            self.temp_dir = Path(tempfile.gettempdir()) / self.app_name
        else:
            # Desarrollo: usar directorio actual
            self.user_data_dir = Path(".")
            self.executable_dir = Path(".")
            self.temp_dir = Path("temp")

        # Crear directorios necesarios
        self._ensure_directories()

        # Inicializar archivos si es necesario
        if self.is_executable:
            self._initialize_user_data()

    def _ensure_directories(self):
        """Crea directorios necesarios"""
        directories = [
            self.get_data_dir(),
            self.get_logs_dir(),
            self.get_output_dir(),
            self.get_temp_dir(),
            self.get_database_dir(),
            self.get_templates_dir(),
            self.get_images_dir()
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Directorio asegurado: {directory}")

    def _initialize_user_data(self):
        """Inicializa datos del usuario en ejecutables"""
        if not self.is_executable:
            return

        try:
            # Copiar base de datos inicial si no existe
            user_db = self.get_database_path()
            if not user_db.exists():
                # Buscar base de datos en recursos del ejecutable
                bundled_db = self._get_bundled_resource("resources/data/alumnos.db")
                if bundled_db and bundled_db.exists():
                    shutil.copy2(bundled_db, user_db)
                    self.logger.info(f"Base de datos inicial copiada a: {user_db}")
                else:
                    # Crear base de datos vacía
                    user_db.touch()
                    self.logger.info(f"Base de datos vacía creada: {user_db}")

            # Copiar configuración si no existe
            user_config = self.get_config_path()
            if not user_config.exists():
                bundled_config = self._get_bundled_resource("school_config.json")
                if bundled_config and bundled_config.exists():
                    shutil.copy2(bundled_config, user_config)
                    self.logger.info(f"Configuración inicial copiada a: {user_config}")

            # Copiar plantillas si no existen
            user_templates = self.get_templates_dir()
            if not any(user_templates.iterdir()):
                bundled_templates = self._get_bundled_resource("resources/templates")
                if bundled_templates and bundled_templates.exists():
                    for template_file in bundled_templates.glob("*.html"):
                        shutil.copy2(template_file, user_templates)
                    self.logger.info(f"Plantillas copiadas a: {user_templates}")

        except Exception as e:
            self.logger.error(f"Error inicializando datos de usuario: {e}")

    def _get_bundled_resource(self, resource_path: str) -> Optional[Path]:
        """Obtiene ruta de recurso empaquetado en ejecutable"""
        if not self.is_executable:
            return Path(resource_path)

        # En ejecutables, los recursos están en _MEIPASS
        if hasattr(sys, '_MEIPASS'):
            bundled_path = Path(sys._MEIPASS) / resource_path
            if bundled_path.exists():
                return bundled_path

        # Fallback: buscar en directorio del ejecutable
        exe_path = self.executable_dir / resource_path
        if exe_path.exists():
            return exe_path

        return None

    # Métodos públicos para obtener rutas

    def get_data_dir(self) -> Path:
        """Directorio principal de datos"""
        return self.user_data_dir

    def get_database_dir(self) -> Path:
        """Directorio de base de datos"""
        return self.user_data_dir / "data"

    def get_database_path(self) -> Path:
        """Ruta de la base de datos"""
        if self.is_development:
            # En desarrollo, usar la ruta tradicional
            return Path("resources/data/alumnos.db")
        else:
            # En ejecutable, usar directorio de datos del usuario
            return self.get_database_dir() / "alumnos.db"

    def get_config_path(self) -> Path:
        """Ruta del archivo de configuración"""
        if self.is_development:
            return Path("school_config.json")
        else:
            return self.user_data_dir / "school_config.json"

    def get_version_path(self) -> Path:
        """Ruta del archivo de versión"""
        if self.is_development:
            return Path("version.json")
        else:
            return self.user_data_dir / "version.json"

    def get_env_path(self) -> Path:
        """Ruta del archivo .env"""
        if self.is_development:
            return Path(".env")
        else:
            return self.user_data_dir / ".env"



    def get_temp_dir(self) -> Path:
        """Directorio temporal"""
        return self.temp_dir

    def get_templates_dir(self) -> Path:
        """Directorio de plantillas"""
        if self.is_development:
            return Path("resources/templates")
        else:
            return self.user_data_dir / "templates"

    def get_images_dir(self) -> Path:
        """Directorio de imágenes"""
        if self.is_development:
            return Path("resources/images")
        else:
            return self.user_data_dir / "images"

    def get_logs_dir(self) -> Path:
        """Directorio de logs"""
        if self.is_development:
            return Path("logs")
        else:
            return self.user_data_dir / "logs"

    def get_output_dir(self) -> Path:
        """Directorio de archivos generados"""
        if self.is_development:
            return Path("output")
        else:
            return self.user_data_dir / "output"

    def get_pdf_output_dir(self) -> Path:
        """Directorio para PDFs generados"""
        return self.get_output_dir() / "pdfs"

    def get_photos_dir(self) -> Path:
        """Directorio de fotos de alumnos"""
        return self.get_images_dir() / "photos"

    def get_logos_dir(self) -> Path:
        """Directorio de logos"""
        return self.get_images_dir() / "logos"

    # Métodos de utilidad

    def is_first_run(self) -> bool:
        """Determina si es la primera ejecución"""
        if self.is_development:
            return False

        return not self.get_config_path().exists()

    def get_system_info(self) -> dict:
        """Información del sistema de archivos"""
        return {
            "is_executable": self.is_executable,
            "is_development": self.is_development,
            "user_data_dir": str(self.user_data_dir),
            "database_path": str(self.get_database_path()),
            "config_path": str(self.get_config_path()),
            "logs_dir": str(self.get_logs_dir()),
            "is_first_run": self.is_first_run()
        }

    def create_portable_package(self, output_dir: Path):
        """Crea un paquete portable con todos los datos"""
        try:
            package_dir = output_dir / f"{self.app_name}_Portable"
            package_dir.mkdir(parents=True, exist_ok=True)

            # Copiar datos del usuario
            if self.user_data_dir.exists():
                shutil.copytree(
                    self.user_data_dir,
                    package_dir / "data",
                    dirs_exist_ok=True
                )

            # Crear script de inicio
            startup_script = package_dir / "iniciar.bat"
            with open(startup_script, "w") as f:
                f.write(f"""@echo off
cd /d "%~dp0"
set SISTEMA_CONSTANCIAS_DATA=%cd%\\data
{self.app_name}.exe
""")

            self.logger.info(f"Paquete portable creado en: {package_dir}")
            return str(package_dir)

        except Exception as e:
            self.logger.error(f"Error creando paquete portable: {e}")
            return None


# Instancia global
_path_manager = None

def get_path_manager() -> ExecutablePathManager:
    """Obtiene la instancia global del gestor de rutas"""
    global _path_manager
    if _path_manager is None:
        _path_manager = ExecutablePathManager()
    return _path_manager

# Funciones de conveniencia
def get_database_path() -> Path:
    """Obtiene la ruta de la base de datos"""
    return get_path_manager().get_database_path()

def get_config_path() -> Path:
    """Obtiene la ruta de configuración"""
    return get_path_manager().get_config_path()

def get_logs_dir() -> Path:
    """Obtiene el directorio de logs"""
    return get_path_manager().get_logs_dir()

def get_output_dir() -> Path:
    """Obtiene el directorio de salida"""
    return get_path_manager().get_output_dir()

def is_executable() -> bool:
    """Determina si se está ejecutando como ejecutable"""
    return get_path_manager().is_executable

def is_development() -> bool:
    """Determina si se está ejecutando en desarrollo"""
    return get_path_manager().is_development
