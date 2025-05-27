"""
Componente personalizado para burbujas de chat
"""
import re
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QPushButton, QApplication
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QColor, QFont, QFontMetrics

class ChatBubble(QWidget):
    """Widget personalizado para mostrar burbujas de chat"""

    # Tipos de mensaje
    TYPE_USER = "user"
    TYPE_ASSISTANT = "assistant"
    TYPE_SYSTEM = "system"

    # Constantes de configuración
    FONT_FAMILY = 'Inter, "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    FONT_SIZE = 15
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

    def _get_text_width(self, text):
        """Calcula el ancho real que necesita un texto con la fuente configurada"""
        font = QFont(self.FONT_FAMILY, self.FONT_SIZE)
        font_metrics = QFontMetrics(font)
        return font_metrics.horizontalAdvance(text)

    def _copy_message(self):
        """Copia el contenido del mensaje al portapapeles"""
        clipboard = QApplication.clipboard()
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
        """Configura los colores según el tipo de mensaje - estilo modo oscuro con tonos azules"""
        if self.message_type == self.TYPE_USER:
            # Estilo usuario - azul oscuro
            self.bg_color = QColor("#1E3A5F")
            self.text_color = QColor("#FFFFFF")
            self.border_color = QColor("#2C4F7C")
            self.header_color = QColor("#88CCFF")
            self.align = Qt.AlignRight
        elif self.message_type == self.TYPE_ASSISTANT:
            # Estilo asistente - gris azulado oscuro
            self.bg_color = QColor("#2C3E50")
            self.text_color = QColor("#FFFFFF")
            self.border_color = QColor("#34495E")
            self.header_color = QColor("#7FB3D5")
            self.align = Qt.AlignLeft
        else:  # System
            # Estilo sistema - gris oscuro
            self.bg_color = QColor("#2F3542")
            self.text_color = QColor("#D3D3D3")
            self.border_color = QColor("#3C4451")
            self.header_color = QColor("#A4B0BE")
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
        bubble_layout.setContentsMargins(18, 10, 15, 18)  # left, top, right, bottom
        bubble_layout.setSpacing(4)  # Pequeño espacio entre header y contenido

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

        # Estilo SIMPLE pero legible
        self.content_label.setStyleSheet(f"""
            QLabel {{
                color: {self.text_color.name()};
                background-color: transparent;
                margin: 0px;
                padding: 3px 0px;  /* Padding vertical para evitar cortes */
                border: none;
                font-size: {self.FONT_SIZE}px;
                line-height: 1.6;  /* Mejor line-height para mayor legibilidad */
                letter-spacing: 0.3px;  /* Espaciado entre caracteres para mejor legibilidad */
                font-family: '{self.FONT_FAMILY}', Arial, sans-serif;
            }}
        """)

        # SIN configuraciones de tamaño complejas
        self.content_label.setContentsMargins(0, 0, 0, 0)

        bubble_layout.addWidget(self.content_label)

        # Estilo SIMPLE del contenedor - padding viene del layout contentsMargins
        bubble_container.setStyleSheet(f"""
            #bubbleContainer {{
                background-color: {self.bg_color.name()};
                border: 1px solid {self.border_color.name()};
                border-radius: 8px;
                margin: 0px;
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
