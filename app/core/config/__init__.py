"""
Módulo de configuración centralizada del sistema
"""

# 🔧 IMPORTAR Config DESDE SU UBICACIÓN ORIGINAL
import os

# Importar Config desde app/core/config.py (archivo hermano)
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("config_module", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    Config = config_module.Config
except Exception as e:
    # Fallback: Config básico
    class Config:
        DB_PATH = "resources/data/alumnos.db"

        @classmethod
        def get_db_path(cls):
            return cls.DB_PATH

# Importar SchoolConfigManager
from .school_config_manager import SchoolConfigManager, get_school_config_manager

# Importar MateriaManager
from .materia_manager import MateriaManager, get_materia_manager

__all__ = ['Config', 'SchoolConfigManager', 'get_school_config_manager', 'MateriaManager', 'get_materia_manager']
