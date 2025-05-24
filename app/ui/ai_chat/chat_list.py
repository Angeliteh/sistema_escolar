"""
Componente para mostrar una lista de mensajes de chat
"""
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, QSize

from app.ui.ai_chat.chat_bubble import ChatBubble

class ChatList(QListWidget):
    """Widget para mostrar una lista de mensajes de chat"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QListWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)

        # Estilo para la lista - estilo modo oscuro con tonos azules
        self.setStyleSheet("""
            QListWidget {
                background-color: #1A1A2E;  /* Fondo azul muy oscuro */
                border: none;
                padding: 6px;
            }
            QListWidget::item {
                border: none;
                padding: 2px 0;
                margin: 1px 0;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #16213E;  /* Azul oscuro para el fondo de la barra */
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #0F3460;  /* Azul más oscuro para el manejador */
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #1E3A5F;  /* Azul un poco más claro al pasar el mouse */
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def add_message(self, message_type, text, timestamp=None):
        """Añade un mensaje a la lista de chat"""
        # Crear burbuja de chat (el procesamiento de texto se hace dentro de ChatBubble)
        bubble = ChatBubble(message_type, text, timestamp)

        # Crear item para la lista
        item = QListWidgetItem()

        # Establecer tamaño para el item basado en el contenido
        # Usar el ancho de la lista menos un margen, y la altura sugerida por la burbuja
        size_hint = bubble.sizeHint()

        # Usar el ancho sugerido por la burbuja, pero asegurarse de que no sea demasiado ancho
        # para mantener la legibilidad y que no sea demasiado estrecho para mostrar todo el contenido
        width = min(self.width() - 40, max(size_hint.width(), int(self.width() * 0.7)))

        # Añadir un pequeño espacio extra en altura para asegurar que todo el contenido sea visible
        # pero sin dejar demasiado espacio vacío
        item.setSizeHint(QSize(width, size_hint.height() + 10))  # Aumentar el espacio extra

        # Añadir item a la lista
        self.addItem(item)
        self.setItemWidget(item, bubble)

        # Ajustar el tamaño del item después de añadirlo
        # Esto es importante para que se adapte correctamente al contenido
        self.updateGeometries()

        # Desplazar al final
        self.scrollToBottom()

    def add_user_message(self, text, timestamp=None):
        """Añade un mensaje del usuario"""
        self.add_message(ChatBubble.TYPE_USER, text, timestamp)

    def add_assistant_message(self, text, timestamp=None):
        """Añade un mensaje del asistente"""
        self.add_message(ChatBubble.TYPE_ASSISTANT, text, timestamp)

    def add_system_message(self, text, timestamp=None):
        """Añade un mensaje del sistema"""
        self.add_message(ChatBubble.TYPE_SYSTEM, text, timestamp)

    def resizeEvent(self, event):
        """Maneja el evento de cambio de tamaño de la ventana"""
        super().resizeEvent(event)

        # Ajustar el tamaño de todos los items cuando cambia el tamaño de la ventana
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget:
                # Obtener el tamaño sugerido por el widget
                size_hint = widget.sizeHint()

                # Calcular un ancho apropiado que aproveche el espacio horizontal
                # pero que no sea demasiado ancho para mantener la legibilidad
                width = min(self.width() - 40, max(size_hint.width(), int(self.width() * 0.7)))

                # Ajustar el tamaño del item
                # Añadir un pequeño espacio extra en altura, pero sin exceso
                item.setSizeHint(QSize(width, size_hint.height() + 10))  # Aumentar el espacio extra

                # Forzar la actualización del widget para asegurar que se muestre correctamente
                widget.updateGeometry()

        # Actualizar la geometría de la lista
        self.updateGeometries()
