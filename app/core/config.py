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

    # Configuración de la escuela - AHORA DINÁMICO
    # Estos valores se obtienen de SchoolConfig
    @classmethod
    def get_school_config(cls):
        """Obtiene la configuración de la escuela actual"""
        from app.core.school_config import SchoolConfig
        return SchoolConfig.get_instance()

    @classmethod
    def get_school_name(cls):
        return cls.get_school_config().school_name

    @classmethod
    def get_school_cct(cls):
        return cls.get_school_config().school_cct

    @classmethod
    def get_director_name(cls):
        return cls.get_school_config().director_name

    @classmethod
    def get_current_year(cls):
        return cls.get_school_config().current_year

    # Valores por defecto para alumnos
    DEFAULT_GRADE = 1
    DEFAULT_GROUP = "A"
    DEFAULT_SHIFT = "MATUTINO"

    # Versión del sistema
    VERSION = "1.0.0"

    # Configuración de logging
    LOGGING = {
        'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        'max_file_size_mb': 10,
        'backup_count': 5,
        'console_enabled': True,
        'debug_mode': False
    }

    # Configuración de UI
    UI = {
        'main_window': {'min_width': 1200, 'min_height': 800},
        'search_window': {'min_width': 900, 'min_height': 700},
        'chat_window': {'min_width': 1000, 'min_height': 700},
        'menu_window': {'min_width': 1200, 'min_height': 800},

        # 🎯 CONFIGURACIÓN DE ESTILOS CENTRALIZADOS
        'theme': {
            'use_centralized_styles': True,
            'theme_name': 'dark_blue',
            'font_family': 'Inter, "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'font_size_base': 15,
            'border_radius': 8,
            'padding_standard': 12,
        }
    }

    # Configuración de archivos y limpieza
    FILES = {
        'temp_cleanup_days': 3,
        'max_file_size_mb': 50,
        'allowed_extensions': ['.pdf', '.jpg', '.png'],
        'temp_file_patterns': ["*.html", "preview_*.pdf", "constancia_*.html"],
        'backup_interval_hours': 24
    }

    # Configuración de AI/LLM
    AI = {
        'max_context_length': 1000000,
        'fallback_confidence_threshold': 0.5,
        'retry_attempts': 3,
        'timeout_seconds': 30,
        'max_tokens': 4096
    }

    # 🎯 CONFIGURACIÓN SIMPLIFICADA DE GEMINI - SOLO 2 MODELOS
    GEMINI = {
        'primary_model': 'gemini-2.0-flash',  # ✅ CORREGIDO: Sin -exp
        'fallback_model': 'gemini-1.5-flash',
        'enable_fallback': True,
        'max_retries': 1,  # Solo 1 retry: 2.0 → 1.5
        'timeout_seconds': 30,

        # 🎯 SOLO 2 API KEYS
        'api_keys': {
            'primary': 'GEMINI_API_KEY',      # Variable de entorno principal
            'secondary': 'GEMINI_API_KEY_2'   # Variable de entorno secundaria
        },

        # 🎯 ESTRATEGIA SIMPLE: SOLO 2 INTENTOS
        'fallback_strategy': [
            {'model': 'gemini-2.0-flash', 'api_key': 'primary'},  # ✅ CORREGIDO
            {'model': 'gemini-1.5-flash', 'api_key': 'primary'}
        ]
    }

    # 🆕 CONFIGURACIÓN DE INTERPRETACIÓN Y DETECCIÓN
    INTERPRETATION = {
        'confidence_thresholds': {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.3,
            'fallback': 0.1
        },
        'intention_types': [
            'consulta_alumnos',
            'transformacion_pdf',
            'ayuda_sistema',
            'conversacion_general'
        ],
        'max_conversation_history': 50,
        'conversation_timeout_minutes': 30
    }

    # 🆕 CONFIGURACIÓN DE RESPUESTAS Y FRASES
    RESPONSES = {
        'greeting_phrases': [
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Buen día! ¿Qué necesitas hacer?",
            "¡Saludos! Estoy listo para asistirte.",
            "¿En qué puedo ayudarte con las constancias hoy?",
            "Estoy aquí para ayudarte. ¿Qué necesitas?"
        ],
        'success_phrases': [
            "¡Listo! He completado la tarea con éxito.",
            "¡Perfecto! La operación se ha realizado correctamente.",
            "¡Excelente! Todo ha salido bien.",
            "¡Tarea completada! Todo en orden.",
            "¡Genial! He terminado lo que me pediste."
        ],
        'confirmation_words': [
            "sí", "si", "yes", "ok", "dale", "perfecto",
            "hazla", "me parece bien", "adelante", "correcto"
        ],
        'error_messages': {
            'parsing_failed': "No se pudo interpretar la respuesta. Por favor, reformula tu consulta.",
            'system_error': "Ocurrió un error al procesar tu consulta. Por favor, intenta de nuevo.",
            'no_results': "No se encontraron resultados para tu consulta.",
            'invalid_input': "La entrada no es válida. Por favor, verifica e intenta de nuevo."
        }
    }



    # Configuración de base de datos
    DATABASE = {
        'connection_timeout': 30,
        'max_connections': 10,
        'query_limit_default': 300,
        'backup_on_startup': True
    }

    # Configuración de PDF
    PDF = {
        'wkhtmltopdf_paths': [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"/usr/local/bin/wkhtmltopdf",
            r"/usr/bin/wkhtmltopdf"
        ],
        'default_options': {
            'page-size': 'Letter',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8'
        }
    }

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

                # Usar logging si está disponible, sino print como fallback
                try:
                    from app.core.logging import get_logger
                    logger = get_logger(__name__)
                    logger.info(f"Configuración personalizada cargada desde {config_file}")
                except ImportError:
                    print(f"Configuración personalizada cargada desde {config_file}")
            except Exception as e:
                # Usar logging si está disponible, sino print como fallback
                try:
                    from app.core.logging import get_logger
                    logger = get_logger(__name__)
                    logger.error(f"Error al cargar configuración personalizada: {e}")
                except ImportError:
                    print(f"Error al cargar configuración personalizada: {e}")

# Cargar configuración personalizada al importar
Config.load_custom_config()
