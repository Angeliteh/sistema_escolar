"""
Sistema centralizado de gestión de temas y estilos
Proporciona una interfaz unificada para todos los estilos del sistema
"""

from typing import Dict
from app.core.school_config import SchoolConfig


class ThemeManager:
    """
    Gestor centralizado de temas y estilos

    CARACTERÍSTICAS:
    - Centraliza todos los colores y estilos
    - Soporte para múltiples temas
    - Integración con configuración escolar
    - Fácil mantenimiento y modificación
    """

    def __init__(self):
        # 🎯 USAR SINGLETON PATTERN CORRECTO
        self.school_config = SchoolConfig.get_instance()
        self._load_theme_colors()

    def _load_theme_colors(self):
        """Carga colores desde la configuración escolar"""
        customization = self.school_config.get_customization_info()

        # Colores base del tema oscuro
        self.colors = {
            # Colores principales desde configuración escolar
            'primary': customization.get('primary_color', '#2C3E50'),
            'secondary': customization.get('secondary_color', '#3498DB'),

            # Paleta de colores del tema oscuro
            'background': {
                'main': '#1A1A2E',           # Fondo principal
                'secondary': '#16213E',      # Fondo secundario
                'panel': '#2C3E50',          # Paneles
                'card': '#1E3A5F',           # Tarjetas/burbujas
                'hover': '#2C4F7C',          # Estados hover
            },

            'text': {
                'primary': '#FFFFFF',        # Texto principal
                'secondary': '#D3D3D3',      # Texto secundario
                'muted': '#A4B0BE',          # Texto deshabilitado
                'accent': '#88CCFF',         # Texto de acento
            },

            'border': {
                'primary': '#2C4F7C',        # Bordes principales
                'secondary': '#34495E',      # Bordes secundarios
                'accent': '#3498DB',         # Bordes de acento
                'subtle': 'rgba(255,255,255,0.3)',  # Bordes sutiles
            },

            'status': {
                'success': '#27ae60',        # Verde éxito
                'error': '#e74c3c',          # Rojo error
                'warning': '#f39c12',        # Naranja advertencia
                'info': '#3498db',           # Azul información
            },

            'chat': {
                'user_bg': '#1E3A5F',        # Fondo mensaje usuario
                'assistant_bg': '#2C3E50',   # Fondo mensaje asistente
                'system_bg': '#2F3542',      # Fondo mensaje sistema
                'user_border': '#2C4F7C',    # Borde mensaje usuario
                'assistant_border': '#34495E', # Borde mensaje asistente
                'system_border': '#3C4451',  # Borde mensaje sistema
            }
        }

    def get_color(self, category: str, name: str = None) -> str:
        """
        Obtiene un color específico del tema

        Args:
            category: Categoría del color (background, text, border, etc.)
            name: Nombre específico del color (opcional)

        Returns:
            Código de color hexadecimal
        """
        if name is None:
            return self.colors.get(category, '#FFFFFF')

        category_colors = self.colors.get(category, {})
        return category_colors.get(name, '#FFFFFF')

    def get_chat_bubble_style(self, message_type: str) -> Dict[str, str]:
        """
        Obtiene estilos específicos para burbujas de chat

        Args:
            message_type: Tipo de mensaje (user, assistant, system)

        Returns:
            Diccionario con colores para la burbuja
        """
        if message_type == 'user':
            return {
                'bg_color': self.colors['chat']['user_bg'],
                'text_color': self.colors['text']['primary'],
                'border_color': self.colors['chat']['user_border'],
                'header_color': self.colors['text']['accent'],
            }
        elif message_type == 'assistant':
            return {
                'bg_color': self.colors['chat']['assistant_bg'],
                'text_color': self.colors['text']['primary'],
                'border_color': self.colors['chat']['assistant_border'],
                'header_color': self.colors['text']['accent'],
            }
        else:  # system
            return {
                'bg_color': self.colors['chat']['system_bg'],
                'text_color': self.colors['text']['secondary'],
                'border_color': self.colors['chat']['system_border'],
                'header_color': self.colors['text']['muted'],
            }

    def get_main_window_style(self) -> str:
        """Obtiene CSS para ventana principal"""
        return f"""
            QMainWindow {{
                background-color: {self.colors['background']['main']};
                color: {self.colors['text']['primary']};
            }}
            QLabel {{
                color: {self.colors['text']['primary']};
            }}
        """

    def get_chat_list_style(self) -> str:
        """Obtiene CSS para lista de chat"""
        return f"""
            QListWidget {{
                background-color: {self.colors['background']['main']};
                border: none;
                padding: 6px;
            }}
            QListWidget::item {{
                border: none;
                padding: 2px 0;
                margin: 1px 0;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.colors['background']['secondary']};
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['secondary']};
                min-height: 30px;
                border-radius: 5px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['border']['accent']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: {self.colors['status']['info']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                border: none;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

    def get_input_field_style(self) -> str:
        """Obtiene CSS para campo de entrada"""
        return f"""
            QLineEdit {{
                border: 1px solid {self.colors['border']['primary']};
                border-radius: 20px;
                padding: 12px 18px;
                font-size: 15px;
                background-color: {self.colors['background']['secondary']};
                color: {self.colors['text']['primary']};
                selection-background-color: {self.colors['border']['accent']};
            }}
            QLineEdit::placeholder {{
                color: rgba(255, 255, 255, 0.6);
            }}
            QLineEdit:focus {{
                border: 1px solid {self.colors['border']['accent']};
                background-color: {self.colors['background']['panel']};
            }}
            QLineEdit:hover {{
                border: 1px solid {self.colors['text']['accent']};
            }}
        """

    def get_button_style(self, button_type: str = 'primary') -> str:
        """Obtiene CSS para botones"""
        if button_type == 'primary':
            bg_color = self.colors['secondary']
            hover_color = self.colors['border']['accent']
            pressed_color = self.colors['status']['info']
        else:
            bg_color = self.colors['background']['panel']
            hover_color = self.colors['background']['hover']
            pressed_color = self.colors['border']['primary']

        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: {self.colors['text']['primary']};
                border-radius: 20px;
                padding: 12px 24px;
                font-size: 15px;
                font-weight: bold;
                border: 1px solid {self.colors['border']['accent']};
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 1px solid {self.colors['text']['accent']};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """

    def get_response_formatter_styles(self) -> Dict[str, str]:
        """Obtiene estilos para el formateador de respuestas - CENTRALIZADOS Y CONFIGURABLES"""
        return {
            'help_border': f"border-left: 3px solid {self.colors['border']['subtle']};",
            'data_border': f"border-left: 3px solid {self.colors['border']['subtle']};",
            'error_border': f"border-left: 3px solid {self.colors['status']['error']};",
            'success_border': f"border-left: 3px solid {self.colors['status']['success']};",
            'number_highlight': f"border: 1px solid {self.colors['border']['subtle']}; padding: 2px 4px; border-radius: 3px;",

            # 🎯 CONFIGURACIÓN CENTRALIZADA DE ESPACIADO
            'enable_wrappers': False,  # CONTROLA SI SE USAN WRAPPERS HTML
            'wrapper_margin': '0px 0',  # Margen de wrappers (cuando están habilitados)
            'wrapper_padding': '0px',   # Padding de wrappers (cuando están habilitados)
            'line_height': '1.4',       # Line-height estándar
            'font_size': '15px',        # Tamaño de fuente estándar
        }

    def get_chat_bubble_layout_styles(self) -> Dict[str, any]:
        """Obtiene configuración centralizada para layouts de burbujas de chat"""
        return {
            'bubble_margin_top': 8,      # Margen superior de burbuja
            'bubble_margin_bottom': 8,   # Margen inferior de burbuja
            'bubble_padding_left': 18,   # Padding izquierdo interno
            'bubble_padding_right': 15,  # Padding derecho interno
            'bubble_spacing': 2,         # Espaciado entre elementos
            'content_margin': 0,         # Margen del contenido
            'content_padding': 0,        # Padding del contenido
            'border_radius': 12,         # Radio de bordes
            'header_font_size': 12,      # Tamaño fuente header
            'copy_button_size': (24, 12), # Tamaño botón copy
        }


# Instancia global del gestor de temas
theme_manager = ThemeManager()
