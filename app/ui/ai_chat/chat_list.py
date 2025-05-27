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
                background: #16213E;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #2980B9;
                min-height: 30px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3498DB;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #1B4F72;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
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

        # Usar el ancho sugerido por la burbuja, respetando su tamaño adaptativo
        # Permitir que las burbujas usen su ancho natural, pero con límites sensatos
        available_width = self.width() - 40  # Margen para scrollbar y bordes

        # Respetar el ancho sugerido por la burbuja, pero limitarlo al espacio disponible
        width = min(size_hint.width(), available_width)

        # SIN espacio extra en altura
        item.setSizeHint(QSize(width, size_hint.height()))  # SIN espacio extra

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

                # Respetar el ancho adaptativo de la burbuja
                available_width = self.width() - 40  # Margen para scrollbar y bordes
                width = min(size_hint.width(), available_width)

                # Ajustar el tamaño del item
                # SIN espacio extra en altura
                item.setSizeHint(QSize(width, size_hint.height()))  # SIN espacio extra

                # Forzar la actualización del widget para asegurar que se muestre correctamente
                widget.updateGeometry()

        # Actualizar la geometría de la lista
        self.updateGeometries()
