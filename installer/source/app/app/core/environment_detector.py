"""
Detector de entorno para determinar si estamos en desarrollo o producción
"""

import os
import sys
from pathlib import Path

class EnvironmentDetector:
    """Detecta el entorno de ejecución del sistema"""
    
    def __init__(self):
        self.is_development = self._detect_development_environment()
        self.is_production = not self.is_development
        self.is_executable = self._is_running_as_executable()
        
    def _detect_development_environment(self) -> bool:
        """Detecta si estamos en entorno de desarrollo"""
        
        # Indicadores de desarrollo
        development_indicators = [
            # Variables de entorno de desarrollo
            os.getenv('DEBUG') == 'True',
            os.getenv('DEVELOPMENT') == 'True',
            os.getenv('DEV_MODE') == 'True',
            
            # Archivos de desarrollo presentes
            os.path.exists('.git'),
            os.path.exists('requirements.txt'),
            os.path.exists('test_system_detector.py'),
            os.path.exists('test_launcher_fixes.py'),
            
            # Ejecutándose desde código fuente
            __file__.endswith('.py') and not self._is_running_as_executable(),
            
            # Directorio actual contiene archivos de desarrollo
            os.path.exists('app') and os.path.exists('resources'),
        ]
        
        # Si cualquier indicador es True, estamos en desarrollo
        return any(development_indicators)
    
    def _is_running_as_executable(self) -> bool:
        """Detecta si estamos ejecutándose como ejecutable compilado"""
        return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    
    def get_launch_mode(self) -> str:
        """Obtiene el modo de lanzamiento recomendado"""
        if self.is_development:
            return "attached"  # Con terminal visible para debugging
        else:
            return "detached"  # Sin terminal para experiencia profesional
    
    def should_show_console(self) -> bool:
        """Determina si se debe mostrar la consola"""
        return self.is_development
    
    def get_log_level(self) -> str:
        """Obtiene el nivel de log recomendado"""
        if self.is_development:
            return "DEBUG"
        else:
            return "INFO"
    
    def get_environment_info(self) -> dict:
        """Obtiene información completa del entorno"""
        return {
            "is_development": self.is_development,
            "is_production": self.is_production,
            "is_executable": self.is_executable,
            "launch_mode": self.get_launch_mode(),
            "show_console": self.should_show_console(),
            "log_level": self.get_log_level(),
            "python_executable": sys.executable,
            "working_directory": os.getcwd(),
            "script_path": __file__ if not self.is_executable else "executable"
        }


# Instancia global para uso en todo el sistema
ENV = EnvironmentDetector()


def is_development() -> bool:
    """Función de conveniencia para verificar si estamos en desarrollo"""
    return ENV.is_development


def is_production() -> bool:
    """Función de conveniencia para verificar si estamos en producción"""
    return ENV.is_production


def get_launch_mode() -> str:
    """Función de conveniencia para obtener el modo de lanzamiento"""
    return ENV.get_launch_mode()


def should_show_console() -> bool:
    """Función de conveniencia para determinar si mostrar consola"""
    return ENV.should_show_console()


def print_environment_info():
    """Imprime información del entorno para debugging"""
    info = ENV.get_environment_info()
    print("🔍 INFORMACIÓN DEL ENTORNO:")
    print("-" * 40)
    for key, value in info.items():
        print(f"   {key}: {value}")
    print("-" * 40)


if __name__ == "__main__":
    # Prueba del detector
    print_environment_info()
