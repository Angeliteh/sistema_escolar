"""
Componente personalizado para burbujas de chat
"""
import re
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QPushButton, QApplication, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont, QFontMetrics
from app.ui.styles import theme_manager
from app.core.config import Config

class ChatBubble(QWidget):
    """Widget personalizado para mostrar burbujas de chat"""

    # Tipos de mensaje
    TYPE_USER = "user"
    TYPE_ASSISTANT = "assistant"
    TYPE_SYSTEM = "system"

    # Constantes de configuración - usando Config centralizado
    FONT_FAMILY = Config.UI['theme']['font_family']
    FONT_SIZE = Config.UI['theme']['font_size_base']
    MAX_SINGLE_LINE_WIDTH = 600
    PADDING_MARGIN = 59  # Margen total para padding del layout + bordes
    MAX_WIDTH = 800
    MIN_WIDTH = 80

    def __init__(self, message_type, text, timestamp=None, parent=None):
        super().__init__(parent)
        self.message_type = message_type

        # Preprocesar el texto para eliminar saltos de línea no deseados
        if message_type == self.TYPE_USER:
            # Para mensajes del usuario, limpiar completamente el texto
            # Eliminar saltos de línea y múltiples espacios
            cleaned = text.replace("\n", " ").replace("\r", " ")
            # Reemplazar múltiples espacios consecutivos con un solo espacio
            cleaned = re.sub(r'\s+', ' ', cleaned)
            # Eliminar espacios al inicio y final
            self.text = cleaned.strip()
        else:
            # Para otros mensajes, mantener el texto original
            self.text = text

        self.timestamp = timestamp

        # Configurar colores según el tipo de mensaje
        self._configure_colors()

        # Configurar layout
        self._setup_ui()

        # 🎨 ANIMACIÓN DE ENTRADA SUAVE
        self._animate_entrance()

    def _get_text_width(self, text):
        """Calcula el ancho real que necesita un texto con la fuente configurada"""
        font = QFont(self.FONT_FAMILY, self.FONT_SIZE)
        font_metrics = QFontMetrics(font)

        # 🎯 Si el texto contiene HTML, extraer solo el texto plano para calcular ancho
        if '<' in text and '>' in text:
            # Crear un QLabel temporal para extraer texto plano del HTML
            temp_label = QLabel(text)
            temp_label.setTextFormat(Qt.RichText)
            plain_text = temp_label.text()
            return font_metrics.horizontalAdvance(plain_text)
        else:
            return font_metrics.horizontalAdvance(text)

    def _copy_message(self):
        """Copia el contenido del mensaje al portapapeles (texto plano)"""
        clipboard = QApplication.clipboard()

        # 🎯 Si el texto contiene HTML, extraer solo el texto plano
        if '<' in self.text and '>' in self.text:
            # Usar el texto plano del QLabel que ya procesa el HTML
            plain_text = self.content_label.text()
            clipboard.setText(plain_text)
        else:
            clipboard.setText(self.text)

    def _position_copy_button(self):
        """Posiciona el botón copy como overlay en la esquina superior derecha"""
        if hasattr(self, 'copy_button') and self.copy_button.parent():
            parent = self.copy_button.parent()
            parent_width = parent.width()
            button_width = self.copy_button.width()
            # Posicionar considerando el padding CSS del contenedor
            x = parent_width - button_width - 10  # Margen desde el borde interno
            y = 8  # Margen desde arriba considerando el padding
            self.copy_button.move(x, y)

    def _configure_colors(self):
        """Configura los colores usando el ThemeManager centralizado"""
        # 🎯 USAR THEMEMANAGER CENTRALIZADO
        style_config = theme_manager.get_chat_bubble_style(self.message_type)

        self.bg_color = QColor(style_config['bg_color'])
        self.text_color = QColor(style_config['text_color'])
        self.border_color = QColor(style_config['border_color'])
        self.header_color = QColor(style_config['header_color'])

        # Configurar alineación según tipo de mensaje
        if self.message_type == self.TYPE_USER:
            self.align = Qt.AlignRight
        elif self.message_type == self.TYPE_ASSISTANT:
            self.align = Qt.AlignLeft
        else:  # System
            self.align = Qt.AlignCenter

    def _setup_ui(self):
        """Configura la interfaz del widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # SIN márgenes
        main_layout.setSpacing(0)  # SIN espacio entre elementos

        # Contenedor para la burbuja
        bubble_container = QWidget()
        bubble_container.setObjectName("bubbleContainer")
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(18, 8, 15, 8)  # left, top, right, bottom - REDUCIDO
        bubble_layout.setSpacing(2)  # Menos espacio entre header y contenido

        # Configurar políticas de tamaño para adaptarse al contenido
        bubble_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Encabezado ULTRA SIMPLE - SIN márgenes ni padding
        header_text = ""
        if self.message_type == self.TYPE_USER:
            header_text = "👤 Tú"
        elif self.message_type == self.TYPE_ASSISTANT:
            header_text = "🤖 Asistente"
        elif self.message_type == self.TYPE_SYSTEM:
            header_text = "🔔 Sistema"

        if header_text:
            # Header simple y unificado
            header_label = QLabel(header_text)
            header_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.header_color.name()};
                    background-color: transparent;
                    margin: 0px;
                    padding: 0px;
                    border: none;
                    font-weight: bold;
                    font-size: 12px;
                    font-family: '{self.FONT_FAMILY}', Arial, sans-serif;
                }}
            """)
            header_label.setContentsMargins(0, 0, 0, 0)
            bubble_layout.addWidget(header_label)

        # QLabel ADAPTATIVO - configurado para ajustarse al contenido
        self.content_label = QLabel(self.text)

        # 🎯 HABILITAR SOPORTE HTML PARA FORMATEO MEJORADO
        # Convertir saltos de línea a HTML para mejor renderizado
        if '\n' in self.text:
            # Convertir saltos de línea a <br> para HTML
            html_text = self.text.replace('\n', '<br>')
            self.content_label.setText(html_text)
        else:
            # Si no hay saltos de línea, usar el texto original
            self.content_label.setText(self.text)

        # Siempre usar RichText para consistencia
        self.content_label.setTextFormat(Qt.RichText)

        # Configurar la fuente ANTES de calcular el ancho
        font = QFont(self.FONT_FAMILY, self.FONT_SIZE)
        self.content_label.setFont(font)

        # Calcular el ancho real que necesita el texto SIN word wrap
        text_width = self._get_text_width(self.text)

        # Configurar el ancho mínimo basado en el texto real
        # Solo hacer word wrap si el texto es realmente muy largo
        if text_width <= self.MAX_SINGLE_LINE_WIDTH:
            # Texto cabe en una línea - no hacer word wrap
            self.content_label.setWordWrap(False)
            self.content_label.setMinimumWidth(text_width + 10)  # +10 para margen
        else:
            # Texto muy largo - permitir word wrap
            self.content_label.setWordWrap(True)
            self.content_label.setMinimumWidth(self.MAX_SINGLE_LINE_WIDTH)

        self.content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Hacer el texto seleccionable
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        # Estilo SIMPLE sin espaciado extra
        self.content_label.setStyleSheet(f"""
            QLabel {{
                color: {self.text_color.name()};
                background-color: transparent;
                margin: 0px;
                padding: 0px;  /* SIN padding para evitar espacios extra */
                border: none;
                font-size: {self.FONT_SIZE}px;
                line-height: 1.4;  /* Line-height normal */
                letter-spacing: 0.3px;
                font-family: '{self.FONT_FAMILY}', Arial, sans-serif;
            }}
        """)

        # SIN configuraciones de tamaño complejas
        self.content_label.setContentsMargins(0, 0, 0, 0)

        bubble_layout.addWidget(self.content_label)

        # 🎨 ESTILO MEJORADO CON GRADIENTES Y SOMBRAS SUTILES
        gradient_start = self.bg_color.lighter(105).name()  # 5% más claro
        gradient_end = self.bg_color.darker(102).name()     # 2% más oscuro

        bubble_container.setStyleSheet(f"""
            #bubbleContainer {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {gradient_start}, stop: 1 {gradient_end});
                border: 1px solid {self.border_color.name()};
                border-radius: 12px;
                margin: 1px;
            }}
            #bubbleContainer:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {self.bg_color.lighter(108).name()},
                    stop: 1 {self.bg_color.name()});
                border: 1px solid {self.border_color.lighter(115).name()};
            }}
        """)

        # Botón copy como overlay - hijo directo del contenedor, NO del layout
        self.copy_button = QPushButton("copy", bubble_container)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                color: rgba(255, 255, 255, 0.3);
                background-color: transparent;
                border: none;
                font-size: 8px;
                padding: 1px 3px;
                margin: 0px;
                font-family: '{self.FONT_FAMILY}', Arial, sans-serif;
            }}
            QPushButton:hover {{
                color: rgba(255, 255, 255, 0.6);
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 2px;
            }}
            QPushButton:pressed {{
                color: rgba(255, 255, 255, 0.8);
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        self.copy_button.setContentsMargins(0, 0, 0, 0)
        self.copy_button.clicked.connect(self._copy_message)
        self.copy_button.setFixedSize(24, 12)  # Pequeño y discreto
        self.copy_button.raise_()  # Asegurar que esté encima

        # Añadir el contenedor al layout principal con alineación
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)

        if self.align == Qt.AlignRight:
            container_layout.addStretch()
            container_layout.addWidget(bubble_container)
        elif self.align == Qt.AlignLeft:
            container_layout.addWidget(bubble_container)
            container_layout.addStretch()
        else:  # Center
            container_layout.addStretch()
            container_layout.addWidget(bubble_container)
            container_layout.addStretch()

        main_layout.addLayout(container_layout)

        # Timestamp fuera de la burbuja, abajo a la derecha - SIN afectar el ancho
        if self.timestamp:
            time_label = QLabel(self.timestamp)
            time_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.4);
                    background-color: transparent;
                    font-size: 9px;
                    margin: 0px;
                    padding: 0px;
                    border: none;
                    font-family: '{self.FONT_FAMILY}', Arial, sans-serif;
                }}
            """)
            time_label.setContentsMargins(0, 0, 0, 0)
            time_label.setAlignment(Qt.AlignRight)
            time_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

            # Añadir directamente sin layout horizontal que pueda expandir
            main_layout.addWidget(time_label, 0, Qt.AlignRight)

        # Dejar que el contenedor se adapte completamente al contenido
        # Sin restricciones de ancho

        # Posicionar el botón copy después de que todo esté renderizado
        QTimer.singleShot(0, self._position_copy_button)

    def sizeHint(self):
        """Sugerencia de tamaño ADAPTATIVO al contenido"""
        # Usar el tamaño del QLabel como base
        label_size = self.content_label.sizeHint()

        # Calcular el ancho real del texto usando la misma fuente
        text_width = self._get_text_width(self.text)

        # Usar el ancho real del texto o el del QLabel, el que sea mayor
        content_width = max(text_width, label_size.width())

        # Solo añadir margen para padding y bordes
        width = max(self.MIN_WIDTH, min(content_width + self.PADDING_MARGIN, self.MAX_WIDTH))

        # Calcular altura - incluir padding del layout y espaciado
        timestamp_height = 12 if self.timestamp else 0
        header_height = 20 if hasattr(self, 'content_label') else 0
        layout_padding_vertical = 28  # 10px top + 18px bottom del layout
        layout_spacing = 4

        height = label_size.height() + header_height + timestamp_height + layout_padding_vertical + layout_spacing

        return QSize(int(width), int(height))

    def resizeEvent(self, event):
        """Reposicionar el botón copy cuando cambia el tamaño"""
        super().resizeEvent(event)
        self._position_copy_button()

    def update_text(self, new_text: str):
        """🆕 ACTUALIZA EL TEXTO DEL MENSAJE (PARA ANIMACIONES DE CARGA)"""
        self.text = new_text
        if hasattr(self, 'content_label'):
            self.content_label.setText(new_text)
            self.updateGeometry()  # Forzar recálculo de tamaño

    def _animate_entrance(self):
        """🎨 ANIMACIÓN SUAVE DE ENTRADA PARA LA BURBUJA"""
        # Crear efecto de opacidad
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        # Configurar animación de fade-in
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)  # 300ms - rápido pero suave
        self.fade_animation.setStartValue(0.0)  # Invisible
        self.fade_animation.setEndValue(1.0)   # Completamente visible
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)  # Suave al final

        # Iniciar animación
        self.fade_animation.start()

        # Limpiar efecto después de la animación para mejor rendimiento
        self.fade_animation.finished.connect(self._cleanup_animation)

    def _cleanup_animation(self):
        """🧹 LIMPIA LOS EFECTOS DE ANIMACIÓN PARA MEJOR RENDIMIENTO"""
        # Remover el efecto gráfico para mejor rendimiento
        self.setGraphicsEffect(None)
        # Limpiar referencias
        if hasattr(self, 'opacity_effect'):
            del self.opacity_effect
        if hasattr(self, 'fade_animation'):
            del self.fade_animation
