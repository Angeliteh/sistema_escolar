"""
Componente para mostrar una lista de mensajes de chat
"""
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QScrollBar
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve

from app.ui.ai_chat.chat_bubble import ChatBubble
from app.ui.styles import theme_manager

class ChatList(QListWidget):
    """Widget para mostrar una lista de mensajes de chat"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QListWidget.NoSelection)
        self.setFocusPolicy(Qt.NoFocus)

        # 🆕 TRACKING DE MENSAJES PARA ACTUALIZACIÓN/ELIMINACIÓN
        self.message_counter = 0
        self.message_items = {}  # {message_id: QListWidgetItem}

        # 🎯 USAR THEMEMANAGER CENTRALIZADO para estilos
        self.setStyleSheet(theme_manager.get_chat_list_style())

    def add_message(self, message_type, text, timestamp=None, is_loading=False):
        """Añade un mensaje a la lista de chat"""
        # 🆕 GENERAR ID ÚNICO PARA EL MENSAJE
        self.message_counter += 1
        message_id = self.message_counter

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

        # 🆕 GUARDAR REFERENCIA PARA TRACKING
        self.message_items[message_id] = item

        # Ajustar el tamaño del item después de añadirlo
        # Esto es importante para que se adapte correctamente al contenido
        self.updateGeometries()

        # 🎨 SCROLL SUAVE AL FINAL
        self._smooth_scroll_to_bottom()

        # 🆕 RETORNAR ID PARA TRACKING
        return message_id

    def add_user_message(self, text, timestamp=None):
        """Añade un mensaje del usuario"""
        return self.add_message(ChatBubble.TYPE_USER, text, timestamp)

    def add_assistant_message(self, text, timestamp=None, is_loading=False):
        """Añade un mensaje del asistente"""
        return self.add_message(ChatBubble.TYPE_ASSISTANT, text, timestamp, is_loading)

    def add_system_message(self, text, timestamp=None):
        """Añade un mensaje del sistema"""
        return self.add_message(ChatBubble.TYPE_SYSTEM, text, timestamp)

    def remove_message(self, message_id):
        """Elimina un mensaje por su ID"""
        if message_id in self.message_items:
            item = self.message_items[message_id]
            row = self.row(item)
            if row >= 0:
                self.takeItem(row)
            del self.message_items[message_id]

    def update_message(self, message_id, new_text):
        """Actualiza el texto de un mensaje existente"""
        if message_id in self.message_items:
            item = self.message_items[message_id]
            widget = self.itemWidget(item)
            if widget and hasattr(widget, 'update_text'):
                widget.update_text(new_text)

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

    def _smooth_scroll_to_bottom(self):
        """🎨 SCROLL SUAVE AL FINAL DEL CHAT"""
        scrollbar = self.verticalScrollBar()

        # Solo hacer scroll suave si no estamos ya al final
        if scrollbar.value() < scrollbar.maximum() - 10:  # Margen de 10px
            # Crear animación de scroll
            self.scroll_animation = QPropertyAnimation(scrollbar, b"value")
            self.scroll_animation.setDuration(250)  # 250ms - rápido pero suave
            self.scroll_animation.setStartValue(scrollbar.value())
            self.scroll_animation.setEndValue(scrollbar.maximum())
            self.scroll_animation.setEasingCurve(QEasingCurve.OutCubic)

            # Iniciar animación
            self.scroll_animation.start()
        else:
            # Si ya estamos cerca del final, scroll inmediato
            self.scrollToBottom()

    def _update_scroll_after_resize(self):
        """🔄 ACTUALIZA EL SCROLL DESPUÉS DE CAMBIOS DE TAMAÑO EN BURBUJAS"""
        try:
            # Forzar recálculo del contenido
            self.updateGeometry()

            # Actualizar todos los items para recalcular tamaños
            for i in range(self.count()):
                item = self.item(i)
                if item:
                    # Forzar recálculo del tamaño del item
                    widget = self.itemWidget(item)
                    if widget:
                        widget.updateGeometry()
                        widget.adjustSize()

                    # Actualizar tamaño del item basado en el widget
                    if widget:
                        size_hint = widget.sizeHint()
                        item.setSizeHint(size_hint)

            # Forzar actualización del scroll
            scroll_bar = self.verticalScrollBar()
            if scroll_bar:
                scroll_bar.update()

            # Actualizar geometrías y el widget completo
            self.updateGeometries()
            self.update()

            print("🔄 [CHATLIST] Scroll actualizado después de cambio de tamaño")

        except Exception as e:
            print(f"❌ [CHATLIST] Error actualizando scroll: {e}")
