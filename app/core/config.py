import os
import json
from datetime import datetime

class Config:
    """Configuración centralizada del sistema"""

    # Rutas de directorios
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    TEMPLATES_DIR = os.path.join(BASE_DIR, "resources/templates")
    LOGOS_DIR = os.path.join(BASE_DIR, "resources/images/logos")
    PHOTOS_DIR = os.path.join(BASE_DIR, "resources/images/photos")
    OUTPUT_DIR = os.path.join(BASE_DIR, "resources/output")

    # Configuración de base de datos
    DB_PATH = os.path.join(BASE_DIR, "resources/data/alumnos.db")

    # Configuración de la escuela
    SCHOOL_NAME = "PROF. MAXIMO GAMIZ FERNANDEZ"
    SCHOOL_CCT = "10DPR0392H"
    SCHOOL_DIRECTOR = "JOSE ANGEL ALVARADO SOSA"
    CURRENT_SCHOOL_YEAR = "2024-2025"

    # Valores por defecto para alumnos
    DEFAULT_GRADE = 1
    DEFAULT_GROUP = "A"
    DEFAULT_SHIFT = "MATUTINO"

    # Versión del sistema
    VERSION = "1.0.0"

    # Fecha actual formateada
    @staticmethod
    def get_current_date_formatted():
        """Devuelve la fecha actual formateada"""
        now = datetime.now()
        return now.strftime("%d días del mes de %B de %Y").capitalize()

    # Cargar configuración personalizada si existe
    @classmethod
    def load_custom_config(cls, config_file="config.json"):
        """Carga configuración personalizada desde un archivo JSON"""
        config_path = os.path.join(cls.BASE_DIR, config_file)
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    custom_config = json.load(f)

                # Actualizar atributos con valores personalizados
                for key, value in custom_config.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)

                print(f"Configuración personalizada cargada desde {config_file}")
            except Exception as e:
                print(f"Error al cargar configuración personalizada: {e}")

# Cargar configuración personalizada al importar
Config.load_custom_config()
