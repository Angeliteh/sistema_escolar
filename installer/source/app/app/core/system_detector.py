"""
Sistema de detección de configuración para el sistema híbrido
Detecta si el sistema está configurado o necesita configuración inicial
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime

class SystemConfigurationDetector:
    """
    Detecta el estado de configuración del sistema y determina qué acciones son necesarias
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_file = "school_config.json"
        self.version_file = "version.json"
        self.database_file = "resources/data/alumnos.db"
        
    def detect_system_state(self) -> Dict[str, any]:
        """
        Detecta el estado completo del sistema
        
        Returns:
            Dict con información del estado del sistema
        """
        state = {
            "is_configured": False,
            "needs_setup": True,
            "config_exists": False,
            "database_exists": False,
            "version_info": None,
            "school_info": None,
            "setup_required": [],
            "warnings": [],
            "errors": []
        }
        
        try:
            # Verificar archivo de configuración
            config_status = self._check_configuration_file()
            state.update(config_status)
            
            # Verificar base de datos
            db_status = self._check_database()
            state.update(db_status)
            
            # Verificar versión
            version_status = self._check_version_info()
            state.update(version_status)
            
            # Determinar si el sistema está completamente configurado
            state["is_configured"] = (
                state["config_exists"] and 
                state["database_exists"] and
                len(state["errors"]) == 0
            )
            
            state["needs_setup"] = not state["is_configured"]
            
            self.logger.info(f"Estado del sistema detectado: {'Configurado' if state['is_configured'] else 'Requiere configuración'}")
            
        except Exception as e:
            self.logger.error(f"Error al detectar estado del sistema: {e}")
            state["errors"].append(f"Error de detección: {str(e)}")
            
        return state
    
    def _check_configuration_file(self) -> Dict[str, any]:
        """Verifica el archivo de configuración de la escuela"""
        result = {
            "config_exists": False,
            "school_info": None
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Verificar que tenga la estructura mínima requerida
                required_sections = ["school_info", "academic_info", "location_info"]
                missing_sections = [section for section in required_sections if section not in config_data]
                
                if missing_sections:
                    result["warnings"] = [f"Secciones faltantes en configuración: {', '.join(missing_sections)}"]
                else:
                    result["config_exists"] = True
                    result["school_info"] = config_data.get("school_info", {})
                    
                    # Verificar datos críticos
                    school_info = config_data.get("school_info", {})
                    critical_fields = ["name", "cct", "director"]
                    missing_critical = [field for field in critical_fields if not school_info.get(field)]
                    
                    if missing_critical:
                        result["warnings"] = result.get("warnings", []) + [
                            f"Campos críticos faltantes: {', '.join(missing_critical)}"
                        ]
            else:
                result["setup_required"] = ["Crear configuración de escuela"]
                
        except json.JSONDecodeError as e:
            result["errors"] = [f"Error en formato de configuración: {str(e)}"]
        except Exception as e:
            result["errors"] = [f"Error al leer configuración: {str(e)}"]
            
        return result
    
    def _check_database(self) -> Dict[str, any]:
        """Verifica la base de datos"""
        result = {
            "database_exists": False,
            "database_info": None
        }
        
        try:
            if os.path.exists(self.database_file):
                # Verificar que el archivo no esté vacío y sea accesible
                file_size = os.path.getsize(self.database_file)
                if file_size > 0:
                    result["database_exists"] = True
                    result["database_info"] = {
                        "path": self.database_file,
                        "size": file_size,
                        "modified": datetime.fromtimestamp(os.path.getmtime(self.database_file)).isoformat()
                    }
                else:
                    result["warnings"] = ["Base de datos existe pero está vacía"]
            else:
                result["setup_required"] = ["Crear base de datos inicial"]
                
        except Exception as e:
            result["errors"] = [f"Error al verificar base de datos: {str(e)}"]
            
        return result
    
    def _check_version_info(self) -> Dict[str, any]:
        """Verifica información de versión del sistema"""
        result = {
            "version_info": None
        }
        
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                result["version_info"] = version_data
            else:
                # Crear archivo de versión por defecto
                default_version = {
                    "version": "2.0.0",
                    "build_date": datetime.now().isoformat(),
                    "configuration_date": None,
                    "last_update": None
                }
                result["version_info"] = default_version
                
        except Exception as e:
            result["warnings"] = result.get("warnings", []) + [f"Error al leer versión: {str(e)}"]
            
        return result
    
    def is_first_run(self) -> bool:
        """Determina si es la primera ejecución del sistema"""
        return not os.path.exists(self.config_file) or not os.path.exists(self.database_file)
    
    def get_setup_requirements(self) -> list:
        """Obtiene lista de requisitos de configuración pendientes"""
        state = self.detect_system_state()
        requirements = []
        
        if not state["config_exists"]:
            requirements.append("Configurar información de la escuela")
            
        if not state["database_exists"]:
            requirements.append("Configurar base de datos inicial")
            
        if state["errors"]:
            requirements.extend([f"Resolver error: {error}" for error in state["errors"]])
            
        return requirements
    
    def create_version_file(self, additional_info: Optional[Dict] = None) -> bool:
        """Crea archivo de versión del sistema"""
        try:
            version_data = {
                "version": "2.0.0",
                "build_date": datetime.now().isoformat(),
                "configuration_date": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat(),
                "system_type": "hybrid",
                "configured_by": "setup_wizard"
            }
            
            if additional_info:
                version_data.update(additional_info)
                
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info("Archivo de versión creado exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al crear archivo de versión: {e}")
            return False
    
    def mark_as_configured(self, school_name: str) -> bool:
        """Marca el sistema como configurado"""
        try:
            version_info = {
                "school_name": school_name,
                "configuration_date": datetime.now().isoformat(),
                "configured": True
            }
            return self.create_version_file(version_info)
            
        except Exception as e:
            self.logger.error(f"Error al marcar sistema como configurado: {e}")
            return False


def get_system_state() -> Dict[str, any]:
    """Función de conveniencia para obtener el estado del sistema"""
    detector = SystemConfigurationDetector()
    return detector.detect_system_state()


def is_system_configured() -> bool:
    """Función de conveniencia para verificar si el sistema está configurado"""
    detector = SystemConfigurationDetector()
    state = detector.detect_system_state()
    return state["is_configured"]


def needs_setup() -> bool:
    """Función de conveniencia para verificar si necesita configuración"""
    detector = SystemConfigurationDetector()
    state = detector.detect_system_state()
    return state["needs_setup"]
