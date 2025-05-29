# app/core/school_config.py
import os
import json
from typing import Dict, Any, Optional
from app.core.logging import get_logger
from app.core.executable_paths import get_path_manager

class SchoolConfig:
    """Configuración específica de cada escuela (separada del sistema base)"""

    _instance = None

    def __init__(self, config_file: str = "school_config.json"):
        if SchoolConfig._instance is not None:
            raise Exception("SchoolConfig es singleton. Usar get_instance()")

        self.config_file = config_file
        self.logger = get_logger(__name__)
        self._school_data = None
        self._load_school_config()

    @classmethod
    def get_instance(cls, config_file: str = "school_config.json"):
        """Obtiene la instancia única de configuración de escuela"""
        if cls._instance is None:
            cls._instance = SchoolConfig(config_file)
        return cls._instance

    def _load_school_config(self):
        """Carga la configuración específica de la escuela"""
        try:
            # Usar gestor de rutas para obtener la ubicación correcta
            path_manager = get_path_manager()
            config_path = path_manager.get_config_path()

            config_found = False
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self._school_data = json.load(f)
                self.logger.info(f"Configuración de escuela cargada desde: {config_path}")
                config_found = True
            else:
                # Fallback: buscar en ubicaciones tradicionales para compatibilidad
                fallback_paths = [
                    self.config_file,  # Directorio actual
                    os.path.join("config", self.config_file),  # Carpeta config
                    os.path.join(os.path.dirname(__file__), "..", "..", self.config_file)  # Raíz del proyecto
                ]

                for fallback_path in fallback_paths:
                    if os.path.exists(fallback_path):
                        with open(fallback_path, 'r', encoding='utf-8') as f:
                            self._school_data = json.load(f)
                        self.logger.info(f"Configuración de escuela cargada desde fallback: {fallback_path}")
                        config_found = True
                        break

            if not config_found:
                self.logger.warning("No se encontró configuración de escuela, usando valores por defecto")
                self._school_data = self._get_default_config()

        except Exception as e:
            self.logger.error(f"Error al cargar configuración de escuela: {e}")
            self._school_data = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto (escuela actual)"""
        return {
            "school_info": {
                "name": "PROF. MAXIMO GAMIZ FERNANDEZ",
                "cct": "10DPR0392H",
                "director": "JOSE ANGEL ALVARADO SOSA",
                "address": "VICTORIA DE DURANGO, DURANGO",
                "phone": "",
                "email": "",
                "zone": "ZONA ESCOLAR 01",
                "sector": "SECTOR 01"
            },
            "academic_info": {
                "current_year": "2024-2025",
                "grades": [1, 2, 3, 4, 5, 6],
                "groups": ["A", "B", "C"],
                "shifts": ["MATUTINO", "VESPERTINO"],
                "education_level": "PRIMARIA"
            },
            "location_info": {
                "city": "VICTORIA DE DURANGO",
                "state": "DURANGO",
                "country": "MÉXICO"
            },
            "customization": {
                "logo_file": "logo_educacion.png",
                "primary_color": "#2C3E50",
                "secondary_color": "#3498DB",
                "use_custom_templates": False,
                "show_photos": True
            },
            "features": {
                "enable_photos": True,
                "enable_grades": True,
                "enable_transfer": True,
                "enable_ai_chat": True,
                "enable_pdf_transform": True
            },
            "system_info": {
                "version": "1.0.0",
                "created_date": "2024-12-01",
                "last_updated": "2024-12-01"
            }
        }

    # Propiedades de acceso rápido para información de la escuela
    @property
    def school_name(self) -> str:
        return self._school_data["school_info"]["name"]

    @property
    def school_cct(self) -> str:
        return self._school_data["school_info"]["cct"]

    @property
    def director_name(self) -> str:
        return self._school_data["school_info"]["director"]

    @property
    def school_address(self) -> str:
        return self._school_data["school_info"]["address"]

    @property
    def current_year(self) -> str:
        return self._school_data["academic_info"]["current_year"]

    @property
    def city(self) -> str:
        return self._school_data["location_info"]["city"]

    @property
    def state(self) -> str:
        return self._school_data["location_info"]["state"]

    @property
    def logo_file(self) -> str:
        return self._school_data["customization"]["logo_file"]

    @property
    def primary_color(self) -> str:
        return self._school_data["customization"]["primary_color"]

    @property
    def available_grades(self) -> list:
        return self._school_data["academic_info"]["grades"]

    @property
    def available_groups(self) -> list:
        return self._school_data["academic_info"]["groups"]

    @property
    def available_shifts(self) -> list:
        return self._school_data["academic_info"]["shifts"]

    # Métodos para obtener configuraciones completas
    def get_school_info(self) -> Dict[str, Any]:
        """Obtiene toda la información de la escuela"""
        return self._school_data["school_info"]

    def get_academic_info(self) -> Dict[str, Any]:
        """Obtiene información académica"""
        return self._school_data["academic_info"]

    def get_location_info(self) -> Dict[str, Any]:
        """Obtiene información de ubicación"""
        return self._school_data["location_info"]

    def get_customization_info(self) -> Dict[str, Any]:
        """Obtiene información de personalización"""
        return self._school_data["customization"]

    def get_features_info(self) -> Dict[str, Any]:
        """Obtiene información de características habilitadas"""
        return self._school_data["features"]

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Verifica si una característica está habilitada"""
        return self._school_data["features"].get(feature_name, False)

    # Métodos para actualizar configuración
    def update_school_info(self, **kwargs):
        """Actualiza información de la escuela"""
        for key, value in kwargs.items():
            if key in self._school_data["school_info"]:
                self._school_data["school_info"][key] = value

    def update_academic_info(self, **kwargs):
        """Actualiza información académica"""
        for key, value in kwargs.items():
            if key in self._school_data["academic_info"]:
                self._school_data["academic_info"][key] = value

    def save_config(self, config_path: Optional[str] = None):
        """Guarda la configuración actual en un archivo"""
        if config_path is None:
            # Usar gestor de rutas para obtener la ubicación correcta
            path_manager = get_path_manager()
            config_path = path_manager.get_config_path()

        try:
            # Crear directorio si no existe
            if isinstance(config_path, str):
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
            else:
                # Es un Path object
                config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._school_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Configuración guardada en: {config_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error al guardar configuración: {e}")
            return False

    def create_school_config_template(self, output_path: str, school_data: Dict[str, Any]):
        """Crea un archivo de configuración para una nueva escuela"""
        template = self._get_default_config()

        # Actualizar con datos específicos de la escuela
        if "school_info" in school_data:
            template["school_info"].update(school_data["school_info"])

        if "academic_info" in school_data:
            template["academic_info"].update(school_data["academic_info"])

        if "location_info" in school_data:
            template["location_info"].update(school_data["location_info"])

        # Actualizar fecha de creación
        from datetime import datetime
        template["system_info"]["created_date"] = datetime.now().isoformat()
        template["system_info"]["last_updated"] = datetime.now().isoformat()

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Plantilla de configuración creada: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error al crear plantilla: {e}")
            return False

    def get_template_data_for_pdf(self) -> Dict[str, Any]:
        """Obtiene datos formateados para usar en plantillas PDF"""
        return {
            "escuela": self.school_name,
            "cct": self.school_cct,
            "director": self.director_name,
            "ciclo": self.current_year,
            "ciudad": self.city,
            "estado": self.state,
            "direccion": self.school_address,
            "logo": self.logo_file,
            "color_primario": self.primary_color
        }

    def __str__(self):
        return f"SchoolConfig(name='{self.school_name}', cct='{self.school_cct}')"

    def __repr__(self):
        return self.__str__()
