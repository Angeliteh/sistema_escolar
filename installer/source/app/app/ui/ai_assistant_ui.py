"""
Interfaz de asistente de IA
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# CommandExecutor eliminado - ahora usamos MessageProcessor directamente

class AIAssistantPanel(QWidget):
    """Panel de asistente de IA"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # OBSOLETO: CommandExecutor eliminado - usar MessageProcessor directamente
        # self.command_executor = CommandExecutor()
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel("Asistente de IA")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        # Área de chat
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        # Entrada de texto
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe un comando (ej: buscar alumno Juan Pérez)")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.input_field.returnPressed.connect(self.process_input)

        self.send_button = QPushButton("Enviar")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.send_button.clicked.connect(self.process_input)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)

        # Área de resultados
        self.results_area = QWidget()
        self.results_layout = QVBoxLayout(self.results_area)
        self.results_layout.setContentsMargins(0, 0, 0, 0)

        # Añadir widgets al layout principal
        layout.addWidget(title_label)
        layout.addWidget(self.chat_area, 1)  # El área de chat ocupa más espacio
        layout.addLayout(input_layout)
        layout.addWidget(self.results_area)

        # Mensaje de bienvenida
        self.add_message("Asistente", "¡Hola! Soy tu asistente de constancias. ¿En qué puedo ayudarte?")
        self.add_message("Asistente", "Puedes pedirme cosas como:")
        self.add_message("Asistente", "- Buscar alumno Juan Pérez")
        self.add_message("Asistente", "- Generar constancia de estudios para María Rodríguez")
        self.add_message("Asistente", "- Registrar nuevo alumno llamado Carlos López con CURP LOPC010101HDFXXX01")

    def process_input(self):
        """Procesa la entrada del usuario"""
        text = self.input_field.text().strip()
        if not text:
            return

        # Mostrar mensaje del usuario
        self.add_message("Tú", text)
        self.input_field.clear()

        success, message, data = False, "Interfaz obsoleta - usar terminal_chat.py", {}

        if success:
            # Mostrar resultado
            self.add_message("Asistente", message)

            # Si hay datos, mostrarlos
            if data:
                if "alumnos" in data:
                    self.show_alumnos(data["alumnos"])
                if "alumno" in data:
                    self.show_alumno(data["alumno"])
                if "constancias" in data:
                    self.show_constancias(data["constancias"])
                if "ruta_archivo" in data:
                    self.add_message("Asistente", f"Archivo generado: {data['ruta_archivo']}")
        else:
            # Mostrar error
            self.add_message("Asistente", f"Error: {message}")
            self.add_message("Asistente", "Puedes pedirme cosas como:")
            self.add_message("Asistente", "- Buscar alumno Juan Pérez")
            self.add_message("Asistente", "- Generar constancia de estudios para María Rodríguez")

    def add_message(self, sender, text):
        """Añade un mensaje al área de chat"""
        self.chat_area.append(f"<b>{sender}:</b> {text}")
        self.chat_area.append("")  # Línea en blanco

        # Desplazar al final
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_alumnos(self, alumnos):
        """Muestra una lista de alumnos"""
        if not alumnos:
            self.add_message("Asistente", "No se encontraron alumnos.")
            return

        # Limpiar área de resultados
        self._clear_results_area()

        # Crear tabla
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Nombre", "CURP", "Grado/Grupo", "ID"])

        # Configurar tabla
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # Rellenar tabla
        for row, alumno in enumerate(alumnos):
            table.insertRow(row)

            # Nombre
            nombre_item = QTableWidgetItem(alumno["nombre"])
            table.setItem(row, 0, nombre_item)

            # CURP
            curp_item = QTableWidgetItem(alumno["curp"])
            table.setItem(row, 1, curp_item)

            # Grado/Grupo
            grado_grupo = f"{alumno.get('grado', '')}° {alumno.get('grupo', '')}"
            grado_grupo_item = QTableWidgetItem(grado_grupo)
            table.setItem(row, 2, grado_grupo_item)

            # ID
            id_item = QTableWidgetItem(str(alumno["id"]))
            table.setItem(row, 3, id_item)

        # Añadir tabla al área de resultados
        self.results_layout.addWidget(table)

    def show_alumno(self, alumno):
        """Muestra los detalles de un alumno"""
        if not alumno:
            return

        # Añadir mensaje con detalles
        self.add_message("Asistente", f"Detalles del alumno:")
        self.add_message("Asistente", f"- Nombre: {alumno.get('nombre', '')}")
        self.add_message("Asistente", f"- CURP: {alumno.get('curp', '')}")
        self.add_message("Asistente", f"- Matrícula: {alumno.get('matricula', '')}")
        self.add_message("Asistente", f"- Grado: {alumno.get('grado', '')}")
        self.add_message("Asistente", f"- Grupo: {alumno.get('grupo', '')}")
        self.add_message("Asistente", f"- ID: {alumno.get('id', '')}")

    def show_constancias(self, constancias):
        """Muestra una lista de constancias"""
        if not constancias:
            self.add_message("Asistente", "No se encontraron constancias.")
            return

        # Añadir mensaje con lista de constancias
        self.add_message("Asistente", f"Constancias generadas:")
        for i, constancia in enumerate(constancias, 1):
            self.add_message("Asistente", f"{i}. {constancia.get('tipo', 'Desconocido')} - {constancia.get('fecha_generacion', '')}")

    def _clear_results_area(self):
        """Limpia el área de resultados"""
        # Eliminar todos los widgets del área de resultados
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
