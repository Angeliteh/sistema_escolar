"""
Componente personalizado para burbujas de chat
"""
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QTextBrowser
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont

class ChatBubble(QWidget):
    """Widget personalizado para mostrar burbujas de chat"""

    TYPE_USER = "user"
    TYPE_ASSISTANT = "assistant"
    TYPE_SYSTEM = "system"

    def __init__(self, message_type, text, timestamp=None, parent=None):
        super().__init__(parent)
        self.message_type = message_type

        # Preprocesar el texto para eliminar saltos de línea no deseados
        if message_type == self.TYPE_USER:
            # Para mensajes del usuario, eliminar todos los saltos de línea
            self.text = text.replace("\n", " ").replace("\r", " ")
        else:
            # Para otros mensajes, mantener el texto original
            self.text = text

        self.timestamp = timestamp

        # Configurar colores según el tipo de mensaje
        self._configure_colors()

        # Configurar layout
        self._setup_ui()

    def _configure_colors(self):
        """Configura los colores según el tipo de mensaje - estilo modo oscuro con tonos azules"""
        if self.message_type == self.TYPE_USER:
            # Estilo usuario - azul oscuro
            self.bg_color = QColor("#1E3A5F")       # Azul oscuro
            self.bg_gradient_start = self.bg_color  # Sin gradiente
            self.bg_gradient_end = self.bg_color    # Sin gradiente
            self.text_color = QColor("#FFFFFF")     # Texto blanco
            self.border_color = QColor("#2C4F7C")   # Borde azul un poco más claro
            self.header_color = QColor("#88CCFF")   # Azul claro para el encabezado
            self.align = Qt.AlignRight
        elif self.message_type == self.TYPE_ASSISTANT:
            # Estilo asistente - gris azulado oscuro
            self.bg_color = QColor("#2C3E50")       # Gris azulado oscuro
            self.bg_gradient_start = self.bg_color  # Sin gradiente
            self.bg_gradient_end = self.bg_color    # Sin gradiente
            self.text_color = QColor("#FFFFFF")     # Texto blanco
            self.border_color = QColor("#34495E")   # Borde un poco más claro
            self.header_color = QColor("#7FB3D5")   # Azul claro para el encabezado
            self.align = Qt.AlignLeft
        else:  # System
            # Estilo sistema - gris oscuro
            self.bg_color = QColor("#2F3542")       # Gris oscuro
            self.bg_gradient_start = self.bg_color  # Sin gradiente
            self.bg_gradient_end = self.bg_color    # Sin gradiente
            self.text_color = QColor("#D3D3D3")     # Texto gris claro
            self.border_color = QColor("#3C4451")   # Borde un poco más claro
            self.header_color = QColor("#A4B0BE")   # Gris claro para el encabezado
            self.align = Qt.AlignCenter

    def _setup_ui(self):
        """Configura la interfaz del widget"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 3, 5, 3)  # Reducir márgenes
        main_layout.setSpacing(0)  # Reducir espacio entre elementos

        # Contenedor para la burbuja
        bubble_container = QWidget()
        bubble_container.setObjectName("bubbleContainer")
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(8, 8, 8, 8)  # Reducir padding
        bubble_layout.setSpacing(0)  # Eliminar espacio entre elementos para evitar huecos

        # Configurar políticas de tamaño para adaptarse al contenido
        bubble_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        # Encabezado (remitente)
        header_text = ""
        if self.message_type == self.TYPE_USER:
            header_text = "👤 Tú"
        elif self.message_type == self.TYPE_ASSISTANT:
            header_text = "🤖 Asistente"
        elif self.message_type == self.TYPE_SYSTEM:
            header_text = "🔔 Sistema"

        if header_text:
            header_label = QLabel(header_text)
            header_font = QFont()
            header_font.setBold(True)
            header_font.setPointSize(11)  # Aumentado de 9 a 11
            header_label.setFont(header_font)
            header_label.setStyleSheet(f"""
                color: {self.header_color.name()};
                margin-bottom: 4px;
                font-family: 'Söhne', 'Segoe UI', Arial, sans-serif;
                font-weight: 500;  /* Semi-bold */
                background-color: {self.bg_color.name()};  /* Mismo color de fondo que la burbuja */
                padding: 2px;
            """)
            bubble_layout.addWidget(header_label)

        # Contenido del mensaje usando QLabel para una visualización más simple y directa
        # Esto evita problemas con el procesamiento de texto en QTextBrowser
        if self.message_type == self.TYPE_USER:
            # Para mensajes del usuario, usar un QLabel simple
            self.content_label = QLabel(self.text)
            self.content_label.setWordWrap(True)
            self.content_label.setTextFormat(Qt.PlainText)  # Usar texto plano para evitar problemas de formato
            self.content_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Estilo para el QLabel
            self.content_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.text_color.name()};
                    font-size: 14px;
                    padding: 5px;
                    background-color: {self.bg_color.name()};
                    border: none;
                    margin: 0px;
                    line-height: 160%;
                    font-family: 'Söhne', 'Segoe UI', Arial, sans-serif;
                }}
            """)
        else:
            # Para mensajes del asistente y sistema, usar QTextBrowser para permitir HTML
            self.content_label = QTextBrowser()

            # Establecer el texto como HTML
            if self.text.startswith("<") and (">" in self.text):
                # Si parece HTML, usarlo directamente
                self.content_label.setHtml(self.text)
            else:
                # Si es texto plano, convertirlo a HTML simple
                # Usar un estilo de ajuste de texto que preserve los saltos de línea
                wrap_style = "white-space: pre-wrap; word-wrap: break-word; word-break: normal;"
                self.content_label.setHtml(f"<div style='{wrap_style}'>{self.text}</div>")

        # Configuración específica para QTextBrowser (solo para mensajes del asistente y sistema)
        if self.message_type != self.TYPE_USER:
            # Configurar el QTextBrowser para que se parezca a un QLabel pero con scrollbar cuando sea necesario
            self.content_label.setFrameStyle(QLabel().frameStyle())  # Sin marco

            # Determinar si el texto es lo suficientemente largo para necesitar scrollbar
            char_count = len(self.text)
            line_count = self.text.count("\n") + 1

            # Mostrar scrollbar solo para mensajes extremadamente largos
            if char_count > 1000 or line_count > 20:  # Para mensajes muy largos
                # Mostrar scrollbar vertical solo cuando sea necesario
                self.content_label.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                # Limitar la altura máxima para forzar el scrollbar
                self.content_label.setMaximumHeight(400)
            else:
                # Para mensajes normales, no mostrar scrollbar y mostrar todo el contenido
                self.content_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                self.content_label.setMaximumHeight(16777215)  # Valor máximo para Qt

            self.content_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.content_label.setReadOnly(True)
            self.content_label.setOpenExternalLinks(True)
            self.content_label.setLineWrapMode(QTextBrowser.WidgetWidth)

            # Aplicar estilos para QTextBrowser
            self.content_label.setStyleSheet(f"""
                QTextBrowser {{
                    color: {self.text_color.name()};
                    font-size: 14px;
                    padding: 5px;
                    background-color: {self.bg_color.name()};
                    border: none;
                    selection-color: white;
                    selection-background-color: #3498DB;
                    margin: 0px;
                    line-height: 160%;
                    font-family: 'Söhne', 'Segoe UI', Arial, sans-serif;
                }}
                QTextBrowser a {{
                    color: #7FB3D5;
                    text-decoration: underline;
                    font-weight: bold;
                }}

                /* Estilo para la barra de desplazamiento */
                QScrollBar:vertical {{
                    background: {self.bg_color.name()};
                    width: 8px;
                    margin: 0px;
                }}

                QScrollBar::handle:vertical {{
                    background: rgba(255, 255, 255, 0.3);
                    min-height: 20px;
                    border-radius: 4px;
                }}

                QScrollBar::handle:vertical:hover {{
                    background: rgba(255, 255, 255, 0.5);
                }}

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """)

        # Configurar políticas de tamaño para el contenido
        self.content_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Configuración específica según el tipo de widget
        if self.message_type == self.TYPE_USER:
            # Para QLabel, configurar tamaños adecuados
            self.content_label.setMinimumWidth(200)
            self.content_label.setMaximumWidth(600)

            # Asegurarse de que todo el texto sea visible
            # Usar un tamaño mínimo generoso para evitar cortes
            self.content_label.setMinimumHeight(50)

            # Ajustar el tamaño según el contenido
            self.content_label.adjustSize()
        else:
            # Para QTextBrowser, configurar el documento
            # Calcular un ancho adecuado basado en el contenido
            char_count = len(self.text)
            word_count = len(self.text.split())

            # Calcular un ancho aproximado basado en el número de caracteres por palabra
            avg_chars_per_word = char_count / max(1, word_count)

            # Ajustar el ancho según la longitud del texto
            if char_count < 50:  # Mensajes muy cortos
                text_width = max(300, min(500, char_count * 8))
            elif char_count < 100:  # Mensajes cortos
                text_width = max(350, min(550, char_count * 7))
            elif char_count < 300:  # Mensajes medianos
                text_width = max(400, min(600, char_count * 5))
            else:  # Mensajes largos
                text_width = max(500, min(700, char_count * 3))

            # Establecer ancho mínimo y máximo
            self.content_label.setMinimumWidth(300)
            self.content_label.setMaximumWidth(700)

            # Ajustar el documento para que se adapte mejor al contenido
            self.content_label.document().setDocumentMargin(10)
            self.content_label.document().setTextWidth(text_width)

            # Calcular la altura basada en el contenido
            # Asegurarse de que todo el texto sea visible
            doc_height = int(self.content_label.document().size().height()) + 20
            self.content_label.setMinimumHeight(doc_height)

        bubble_layout.addWidget(self.content_label)

        # Timestamp
        if self.timestamp:
            time_label = QLabel(self.timestamp)
            time_label.setAlignment(Qt.AlignRight)
            time_label.setStyleSheet(f"""
                color: rgba(255, 255, 255, 0.6);  /* Blanco semi-transparente para modo oscuro */
                font-size: 10px;
                margin-top: 4px;
                font-family: 'Söhne', 'Segoe UI', Arial, sans-serif;
                font-style: italic;
                background-color: {self.bg_color.name()};  /* Mismo color de fondo que la burbuja */
                padding: 2px;
            """)
            bubble_layout.addWidget(time_label)

        # Aplicar estilo al contenedor de la burbuja - estilo minimalista tipo ChatGPT
        bubble_container.setStyleSheet(f"""
            #bubbleContainer {{
                background-color: {self.bg_color.name()};
                border: 1px solid {self.border_color.name()};
                border-radius: 8px;  /* Bordes menos redondeados, más formal */
                color: {self.text_color.name()};
            }}
        """)

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

        # Configurar ancho máximo y mínimo de la burbuja
        # Usar un porcentaje del ancho disponible para adaptarse mejor
        available_width = 800  # Ancho estimado de la ventana

        # Ancho mínimo adaptado a la longitud del texto
        char_count = len(self.text)
        if char_count < 50:  # Mensajes muy cortos
            min_width = max(200, min(400, char_count * 6))
        elif char_count < 100:  # Mensajes cortos
            min_width = max(250, min(450, char_count * 5))
        else:  # Mensajes más largos
            min_width = max(350, min(600, char_count * 3))

        bubble_container.setMinimumWidth(min_width)

        # Limitar el ancho máximo para evitar burbujas demasiado anchas
        bubble_container.setMaximumWidth(int(available_width * 0.85))  # 85% del ancho disponible

    def sizeHint(self):
        """Sugerencia de tamaño para el widget"""
        # Calcular el ancho basado en el contenido
        char_count = len(self.text)

        # Usar anchos más generosos para asegurar que todo el texto sea visible
        if char_count < 50:  # Mensajes muy cortos
            base_width = max(300, min(500, char_count * 8))
        elif char_count < 100:  # Mensajes cortos
            base_width = max(350, min(550, char_count * 7))
        elif char_count < 300:  # Mensajes medianos
            base_width = max(400, min(600, char_count * 5))
        else:  # Mensajes largos
            base_width = max(500, min(700, char_count * 3))

        # Añadir margen para los bordes de la burbuja
        width = base_width + 100  # Margen más amplio

        # Calcular la altura según el tipo de widget
        if self.message_type == self.TYPE_USER:
            # Para QLabel, usar el tamaño sugerido por el widget
            label_size = self.content_label.sizeHint()
            content_height = label_size.height() + 20  # Añadir margen extra
        else:
            # Para QTextBrowser, calcular la altura basada en el documento
            doc = self.content_label.document()
            doc.setTextWidth(base_width)  # Establecer el ancho para calcular la altura correctamente
            content_height = int(doc.size().height()) + 30  # Añadir margen extra

        # Añadir margen para encabezado y timestamp
        header_height = 30  # Margen para el encabezado
        timestamp_height = 20 if self.timestamp else 0
        height = content_height + header_height + timestamp_height + 20  # Margen adicional

        # Asegurar tamaños mínimos generosos
        width = max(width, 350)
        height = max(height, 100)  # Altura mínima aumentada

        # Asegurarse de que los valores sean enteros
        return QSize(int(width), int(height))
