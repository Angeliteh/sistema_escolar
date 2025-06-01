"""
Sistema de logging centralizado para toda la aplicación
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path


class LoggerManager:
    """
    Gestor centralizado de logging para toda la aplicación
    
    Características:
    - Logging a archivo con rotación automática
    - Diferentes niveles de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Formato consistente en toda la aplicación
    - Configuración centralizada
    - Logging tanto a archivo como a consola (configurable)
    """
    
    _instance: Optional['LoggerManager'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            LoggerManager._initialized = True
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        # Importar Config aquí para evitar importaciones circulares
        from app.core.config import Config
        
        # Crear directorio de logs
        self.log_dir = Path(Config.BASE_DIR) / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar el logger raíz
        self.root_logger = logging.getLogger()
        self.root_logger.setLevel(logging.DEBUG)
        
        # Limpiar handlers existentes
        self.root_logger.handlers.clear()
        
        # Crear formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Configurar handler de archivo con rotación
        self._setup_file_handler()
        
        # Configurar handler de consola
        self._setup_console_handler()
        
        # Log inicial
        logger = self.get_logger(__name__)
        logger.info("Sistema de logging inicializado correctamente")
        logger.info(f"Logs guardados en: {self.log_dir}")
    
    def _setup_file_handler(self):
        """Configura el handler de archivo con rotación"""
        log_file = self.log_dir / "app.log"
        
        # Handler con rotación (10MB máximo, 5 archivos de backup)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.detailed_formatter)
        
        self.root_logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Configura el handler de consola"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Solo INFO y superior en consola
        console_handler.setFormatter(self.simple_formatter)
        
        self.root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtiene un logger para un módulo específico
        
        Args:
            name: Nombre del módulo (usar __name__)
            
        Returns:
            Logger configurado para el módulo
            
        Example:
            logger = LoggerManager().get_logger(__name__)
            logger.info("Mensaje de información")
        """
        return logging.getLogger(name)
    
    def set_level(self, level: str):
        """
        Cambia el nivel de logging globalmente
        
        Args:
            level: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Nivel de logging inválido: {level}')
        
        self.root_logger.setLevel(numeric_level)
        
        # Actualizar handlers de consola para mostrar el nuevo nivel
        for handler in self.root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(numeric_level)
    
    def enable_debug_mode(self):
        """Habilita modo debug (muestra DEBUG en consola también)"""
        for handler in self.root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(self.detailed_formatter)
    
    def disable_console_logging(self):
        """Deshabilita logging en consola (solo archivo)"""
        handlers_to_remove = []
        for handler in self.root_logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handlers_to_remove.append(handler)
        
        for handler in handlers_to_remove:
            self.root_logger.removeHandler(handler)
    
    def get_log_stats(self) -> dict:
        """
        Obtiene estadísticas de los archivos de log
        
        Returns:
            Diccionario con estadísticas de logs
        """
        stats = {
            'log_directory': str(self.log_dir),
            'log_files': [],
            'total_size_mb': 0
        }
        
        for log_file in self.log_dir.glob("*.log*"):
            size_mb = log_file.stat().st_size / (1024 * 1024)
            stats['log_files'].append({
                'name': log_file.name,
                'size_mb': round(size_mb, 2),
                'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
            })
            stats['total_size_mb'] += size_mb
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats


# Función de conveniencia para obtener logger rápidamente
def get_logger(name: str) -> logging.Logger:
    """
    Función de conveniencia para obtener un logger

    Args:
        name: Nombre del módulo (usar __name__)

    Returns:
        Logger configurado

    Example:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Mensaje")
    """
    return LoggerManager().get_logger(name)


# 🔍 FUNCIONES HELPER PARA DEBUG CONDICIONAL
def is_detailed_debug_enabled() -> bool:
    """
    Verifica si el modo de debug detallado está activado

    Returns:
        True si DEBUG_PAUSES está activado, False en caso contrario
    """
    return os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true'


def debug_detailed(logger: logging.Logger, message: str, *args, **kwargs):
    """
    Log detallado que solo aparece cuando DEBUG_PAUSES está activado

    Args:
        logger: Logger a usar
        message: Mensaje a loggear
        *args, **kwargs: Argumentos adicionales para el logger
    """
    if is_detailed_debug_enabled():
        logger.info(message, *args, **kwargs)
    # 🚫 Si DEBUG_PAUSES no está activado, NO hacer nada (no loggear)


def debug_separator(logger: logging.Logger, title: str = "", length: int = 80):
    """
    Separador visual que solo aparece en modo debug detallado

    Args:
        logger: Logger a usar
        title: Título opcional para el separador
        length: Longitud del separador
    """
    if is_detailed_debug_enabled():
        if title:
            logger.info(f"{'=' * length}")
            logger.info(f"🔍 {title}")
            logger.info(f"{'=' * length}")
        else:
            logger.info(f"{'=' * length}")
    # 🚫 Si DEBUG_PAUSES no está activado, NO hacer nada (no loggear)


def debug_pause_if_enabled(message: str):
    """
    Pausa solo si DEBUG_PAUSES está activado

    Args:
        message: Mensaje a mostrar en la pausa
    """
    if is_detailed_debug_enabled():
        input(f"🛑 {message}")
