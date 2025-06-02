"""
Módulo de logging centralizado del sistema
"""
from .logger_manager import (
    LoggerManager,
    get_logger,
    is_detailed_debug_enabled,
    debug_detailed,
    debug_separator,
    debug_pause_if_enabled
)

__all__ = [
    'LoggerManager',
    'get_logger',
    'is_detailed_debug_enabled',
    'debug_detailed',
    'debug_separator',
    'debug_pause_if_enabled'
]
