"""
Interfaz para administración de la base de datos
"""
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFileDialog, QGroupBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QProgressBar, QComboBox, QSplitter, QTextEdit
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from app.core.database_manager import DatabaseManager

class DatabaseAdminWindow(QMainWindow):
    """Ventana para administración de la base de datos"""

    def __init__(self, parent=None):
        """
        Inicializa la ventana

        Args:
            parent: Widget padre (opcional)
        """
        super().__init__(parent)
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.load_database_info()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("Administración de Base de Datos")
        self.setMinimumSize(900, 700)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Barra superior con título y botón de volver
        top_bar = QWidget()
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)

        # Botón para volver al menú principal
        self.btn_volver = QPushButton("Volver al Menú Principal")
        self.btn_volver.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_volver.setMinimumHeight(40)
        self.btn_volver.clicked.connect(self.volver_menu_principal)

        # Título
        title_label = QLabel("Administración de Base de Datos")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)

        top_bar_layout.addWidget(self.btn_volver)
        top_bar_layout.addWidget(title_label)
        top_bar_layout.setStretch(0, 1)  # El botón ocupa menos espacio
        top_bar_layout.setStretch(1, 3)  # El título ocupa más espacio

        main_layout.addWidget(top_bar)

        # Tabs para diferentes secciones
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 10px 15px;
                margin-right: 2px;
                font-size: 14px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected {
                background-color: #d6eaf8;
            }
        """)

        # Tab de información general
        self.tab_info = QWidget()
        self.tabs.addTab(self.tab_info, "Información General")

        # Tab de administración de tablas
        self.tab_tables = QWidget()
        self.tabs.addTab(self.tab_tables, "Administrar Tablas")

        # Tab de respaldos
        self.tab_backups = QWidget()
        self.tabs.addTab(self.tab_backups, "Respaldos")

        # Configurar cada tab
        self.setup_info_tab()
        self.setup_tables_tab()
        self.setup_backups_tab()

        main_layout.addWidget(self.tabs)

    def setup_info_tab(self):
        """Configura la pestaña de información general"""
        layout = QVBoxLayout(self.tab_info)
        layout.setSpacing(15)

        # Información de la base de datos
        info_group = QGroupBox("Información de la Base de Datos")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        info_layout = QVBoxLayout(info_group)

        # Tabla de información
        self.info_table = QTableWidget()
        self.info_table.setColumnCount(2)
        self.info_table.setHorizontalHeaderLabels(["Propiedad", "Valor"])
        self.info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.info_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.info_table.verticalHeader().setVisible(False)
        self.info_table.setAlternatingRowColors(True)
        self.info_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.info_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #3498db;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        info_layout.addWidget(self.info_table)

        # Tablas en la base de datos
        tables_group = QGroupBox("Tablas en la Base de Datos")
        tables_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #2ecc71;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #2ecc71;
            }
        """)

        tables_layout = QVBoxLayout(tables_group)

        # Tabla de tablas
        self.tables_info_table = QTableWidget()
        self.tables_info_table.setColumnCount(2)
        self.tables_info_table.setHorizontalHeaderLabels(["Tabla", "Número de Registros"])
        self.tables_info_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tables_info_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tables_info_table.verticalHeader().setVisible(False)
        self.tables_info_table.setAlternatingRowColors(True)
        self.tables_info_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tables_info_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #2ecc71;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        tables_layout.addWidget(self.tables_info_table)

        # Botón para actualizar información
        btn_refresh = QPushButton("Actualizar Información")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_refresh.setMinimumHeight(40)
        btn_refresh.clicked.connect(self.load_database_info)

        layout.addWidget(info_group)
        layout.addWidget(tables_group)
        layout.addWidget(btn_refresh)

    def setup_tables_tab(self):
        """Configura la pestaña de administración de tablas"""
        layout = QVBoxLayout(self.tab_tables)
        layout.setSpacing(15)

        # Selector de tabla
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(10)

        selector_label = QLabel("Seleccionar Tabla:")
        selector_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        self.table_selector = QComboBox()
        self.table_selector.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #3498db;
                selection-color: white;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        self.table_selector.currentIndexChanged.connect(self.load_selected_table)

        btn_load_table = QPushButton("Cargar Tabla")
        btn_load_table.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_load_table.clicked.connect(self.load_selected_table)

        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.table_selector)
        selector_layout.addWidget(btn_load_table)
        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        # Contenido de la tabla
        table_group = QGroupBox("Contenido de la Tabla")
        table_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        table_layout = QVBoxLayout(table_group)

        # Tabla de datos
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.data_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                gridline-color: #ecf0f1;
                selection-background-color: #3498db;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                padding: 8px;
                border: none;
                border-right: 1px solid #3498db;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        table_layout.addWidget(self.data_table)

        layout.addWidget(table_group)

        # Botones de acción
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)

        btn_truncate = QPushButton("Vaciar Tabla")
        btn_truncate.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_truncate.setMinimumHeight(40)
        btn_truncate.clicked.connect(self.truncate_selected_table)

        btn_reset_all = QPushButton("Reiniciar Toda la Base de Datos")
        btn_reset_all.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_reset_all.setMinimumHeight(40)
        btn_reset_all.clicked.connect(self.reset_database)

        actions_layout.addStretch()
        actions_layout.addWidget(btn_truncate)
        actions_layout.addWidget(btn_reset_all)

        layout.addLayout(actions_layout)

    def setup_backups_tab(self):
        """Configura la pestaña de respaldos"""
        layout = QVBoxLayout(self.tab_backups)
        layout.setSpacing(15)

        # Crear respaldo
        backup_group = QGroupBox("Crear Respaldo")
        backup_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #3498db;
            }
        """)

        backup_layout = QVBoxLayout(backup_group)

        btn_create_backup = QPushButton("Crear Respaldo de la Base de Datos")
        btn_create_backup.setStyleSheet("""
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
        btn_create_backup.setMinimumHeight(40)
        btn_create_backup.clicked.connect(self.create_backup)

        backup_layout.addWidget(btn_create_backup)

        # Restaurar respaldo
        restore_group = QGroupBox("Restaurar Respaldo")
        restore_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px;
                color: #e74c3c;
            }
        """)

        restore_layout = QVBoxLayout(restore_group)

        btn_restore_backup = QPushButton("Seleccionar y Restaurar Respaldo")
        btn_restore_backup.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_restore_backup.setMinimumHeight(40)
        btn_restore_backup.clicked.connect(self.restore_backup)

        restore_layout.addWidget(btn_restore_backup)

        layout.addWidget(backup_group)
        layout.addWidget(restore_group)
        layout.addStretch()

    def load_database_info(self):
        """Carga la información de la base de datos"""
        try:
            # Obtener información de la base de datos
            db_info = self.db_manager.get_database_info()

            # Actualizar tabla de información general
            self.info_table.setRowCount(0)

            # Añadir información del archivo
            self.add_info_row("Ruta del archivo", db_info['file_path'])
            self.add_info_row("Tamaño del archivo", db_info['file_size'])
            self.add_info_row("Última modificación", db_info['file_modified'])
            self.add_info_row("Número de tablas", str(len(db_info['tables'])))

            # Actualizar tabla de tablas
            self.tables_info_table.setRowCount(0)

            # Actualizar selector de tablas
            self.table_selector.clear()

            for table_name, table_data in db_info['tables'].items():
                # Añadir a la tabla de información
                row = self.tables_info_table.rowCount()
                self.tables_info_table.insertRow(row)
                self.tables_info_table.setItem(row, 0, QTableWidgetItem(table_name))
                self.tables_info_table.setItem(row, 1, QTableWidgetItem(str(table_data['row_count'])))

                # Añadir al selector
                self.table_selector.addItem(table_name)

            # Seleccionar la primera tabla si hay alguna
            if self.table_selector.count() > 0:
                self.table_selector.setCurrentIndex(0)
                self.load_selected_table()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar información de la base de datos: {str(e)}")

    def add_info_row(self, property_name, value):
        """Añade una fila a la tabla de información"""
        row = self.info_table.rowCount()
        self.info_table.insertRow(row)
        self.info_table.setItem(row, 0, QTableWidgetItem(property_name))
        self.info_table.setItem(row, 1, QTableWidgetItem(value))

    def load_selected_table(self):
        """Carga los datos de la tabla seleccionada"""
        if self.table_selector.currentIndex() < 0:
            return

        table_name = self.table_selector.currentText()

        try:
            # Obtener estructura de la tabla
            columns = self.db_manager.get_table_info(table_name)

            # Configurar columnas de la tabla
            self.data_table.setColumnCount(len(columns))
            header_labels = [col['name'] for col in columns]
            self.data_table.setHorizontalHeaderLabels(header_labels)

            # Obtener datos de la tabla (limitados a 100 filas para rendimiento)
            self.db_manager.cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
            rows = self.db_manager.cursor.fetchall()

            # Llenar la tabla
            self.data_table.setRowCount(0)
            for row_data in rows:
                row = self.data_table.rowCount()
                self.data_table.insertRow(row)

                for col, value in enumerate(row_data):
                    self.data_table.setItem(row, col, QTableWidgetItem(str(value) if value is not None else ""))

            # Ajustar ancho de columnas
            for i in range(len(columns)):
                self.data_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar tabla {table_name}: {str(e)}")

    def truncate_selected_table(self):
        """Vacía la tabla seleccionada"""
        if self.table_selector.currentIndex() < 0:
            return

        table_name = self.table_selector.currentText()

        reply = QMessageBox.question(
            self, "Confirmar Acción",
            f"¿Está seguro de que desea vaciar la tabla {table_name}?\n\n"
            "Esta acción eliminará TODOS los registros de la tabla y no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success, message = self.db_manager.truncate_table(table_name)

                if success:
                    QMessageBox.information(self, "Operación Exitosa", message)
                    self.load_selected_table()
                    self.load_database_info()
                else:
                    QMessageBox.warning(self, "Error", message)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al vaciar tabla: {str(e)}")

    def reset_database(self):
        """Reinicia toda la base de datos"""
        reply = QMessageBox.question(
            self, "Confirmar Acción",
            "¿Está seguro de que desea reiniciar TODA la base de datos?\n\n"
            "Esta acción eliminará TODOS los registros de TODAS las tablas y no se puede deshacer.\n\n"
            "Se recomienda crear un respaldo antes de continuar.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Preguntar si desea crear un respaldo primero
            backup_reply = QMessageBox.question(
                self, "Crear Respaldo",
                "¿Desea crear un respaldo de la base de datos antes de reiniciarla?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
            )

            if backup_reply == QMessageBox.Yes:
                success, message, _ = self.db_manager.backup_database()
                if not success:
                    error_reply = QMessageBox.question(
                        self, "Error de Respaldo",
                        f"{message}\n\n¿Desea continuar con el reinicio de la base de datos sin respaldo?",
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                    )
                    if error_reply == QMessageBox.No:
                        return

            try:
                results = self.db_manager.reset_database()

                # Mostrar resultados
                success_count = sum(1 for _, success, _ in results if success)
                error_count = len(results) - success_count

                if error_count == 0:
                    QMessageBox.information(
                        self, "Operación Exitosa",
                        f"Base de datos reiniciada correctamente.\n\n"
                        f"Se vaciaron {success_count} tablas."
                    )
                else:
                    error_message = "Algunas tablas no pudieron ser vaciadas:\n\n"
                    for table, success, message in results:
                        if not success:
                            error_message += f"- {table}: {message}\n"

                    QMessageBox.warning(
                        self, "Operación Parcial",
                        f"Base de datos reiniciada parcialmente.\n\n"
                        f"Se vaciaron {success_count} tablas.\n"
                        f"No se pudieron vaciar {error_count} tablas.\n\n"
                        f"{error_message}"
                    )

                self.load_selected_table()
                self.load_database_info()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al reiniciar base de datos: {str(e)}")

    def create_backup(self):
        """Crea un respaldo de la base de datos"""
        try:
            success, message, backup_path = self.db_manager.backup_database()

            if success:
                QMessageBox.information(self, "Operación Exitosa", message)
            else:
                QMessageBox.warning(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear respaldo: {str(e)}")

    def restore_backup(self):
        """Restaura la base de datos desde un respaldo"""
        # Mostrar diálogo para seleccionar archivo
        backup_file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Archivo de Respaldo",
            os.path.join(os.path.dirname(self.db_manager.db_path), "backups"),
            "Archivos de Base de Datos (*.db);;Todos los Archivos (*)"
        )

        if not backup_file:
            return

        reply = QMessageBox.question(
            self, "Confirmar Restauración",
            f"¿Está seguro de que desea restaurar la base de datos desde el archivo:\n\n{backup_file}?\n\n"
            "Esta acción reemplazará TODOS los datos actuales y no se puede deshacer.\n\n"
            "Se creará un respaldo automático de la base de datos actual antes de restaurar.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success, message = self.db_manager.restore_database(backup_file)

                if success:
                    QMessageBox.information(self, "Operación Exitosa", message)
                    self.load_database_info()
                else:
                    QMessageBox.warning(self, "Error", message)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al restaurar base de datos: {str(e)}")

    def volver_menu_principal(self):
        """Cierra esta ventana y vuelve al menú principal"""
        self.close()

    def closeEvent(self, event):
        """Evento al cerrar la ventana"""
        self.db_manager.close()
        event.accept()
