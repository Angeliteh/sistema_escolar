"""
Interfaz gráfica para el System Builder
Permite generar sistemas personalizados para múltiples escuelas
"""

import sys
import os
import json
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QLineEdit, QTextEdit,
                             QComboBox, QCheckBox, QGroupBox, QFormLayout,
                             QProgressBar, QMessageBox, QFileDialog, QListWidget,
                             QListWidgetItem, QSplitter, QTabWidget, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.system_builder import SystemBuilder, create_system_for_current_school
from app.core.logging.logger_manager import get_logger

class SystemBuildWorker(QThread):
    """Worker thread para generar sistemas sin bloquear la UI"""
    progress_updated = pyqtSignal(int, str)
    build_completed = pyqtSignal(dict)
    
    def __init__(self, school_data):
        super().__init__()
        self.school_data = school_data
        self.logger = get_logger(__name__)
    
    def run(self):
        """Ejecuta la generación del sistema"""
        try:
            self.progress_updated.emit(10, "Inicializando System Builder...")
            builder = SystemBuilder()
            
            self.progress_updated.emit(30, "Validando datos de escuela...")
            
            self.progress_updated.emit(50, "Generando sistema personalizado...")
            result = builder.create_system_for_school(self.school_data)
            
            self.progress_updated.emit(100, "Sistema generado exitosamente")
            self.build_completed.emit(result)
            
        except Exception as e:
            self.logger.error(f"Error en worker: {e}")
            self.build_completed.emit({
                "success": False,
                "error": str(e),
                "system_path": None
            })

class SystemBuilderUI(QMainWindow):
    """Interfaz principal del System Builder"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.builder = SystemBuilder()
        self.setup_ui()
        self.load_generated_systems()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("System Builder - Generador de Sistemas Personalizados")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter para dividir la interfaz
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo - Formulario
        form_widget = self.create_form_panel()
        splitter.addWidget(form_widget)
        
        # Panel derecho - Sistemas generados
        systems_widget = self.create_systems_panel()
        splitter.addWidget(systems_widget)
        
        # Configurar proporciones del splitter
        splitter.setSizes([700, 500])
        
    def create_form_panel(self) -> QWidget:
        """Crea el panel del formulario"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title = QLabel("Generar Sistema Personalizado")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tabs para organizar el formulario
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Tab 1: Información básica
        basic_tab = self.create_basic_info_tab()
        tabs.addTab(basic_tab, "Información Básica")
        
        # Tab 2: Configuración académica
        academic_tab = self.create_academic_tab()
        tabs.addTab(academic_tab, "Configuración Académica")
        
        # Tab 3: Personalización
        custom_tab = self.create_customization_tab()
        tabs.addTab(custom_tab, "Personalización")
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.load_current_btn = QPushButton("📋 Cargar Escuela Actual")
        self.load_current_btn.clicked.connect(self.load_current_school)
        
        self.clear_btn = QPushButton("🗑️ Limpiar Formulario")
        self.clear_btn.clicked.connect(self.clear_form)
        
        self.generate_btn = QPushButton("🏭 Generar Sistema")
        self.generate_btn.clicked.connect(self.generate_system)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        buttons_layout.addWidget(self.load_current_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.generate_btn)
        
        layout.addLayout(buttons_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Label de estado
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)
        
        return widget
    
    def create_basic_info_tab(self) -> QWidget:
        """Crea el tab de información básica"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Campos básicos
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Ej: ESCUELA PRIMARIA BENITO JUÁREZ")
        
        self.cct_edit = QLineEdit()
        self.cct_edit.setPlaceholderText("Ej: 10DPR0392H")
        
        self.director_edit = QLineEdit()
        self.director_edit.setPlaceholderText("Ej: JOSÉ PÉREZ GONZÁLEZ")
        
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(60)
        self.address_edit.setPlaceholderText("Dirección completa de la escuela")
        
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Ej: 618-123-4567")
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Ej: escuela@educacion.gob.mx")
        
        self.zone_edit = QLineEdit()
        self.zone_edit.setPlaceholderText("Ej: ZONA ESCOLAR 01")
        
        self.sector_edit = QLineEdit()
        self.sector_edit.setPlaceholderText("Ej: SECTOR 01")
        
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("Ej: Victoria de Durango")
        
        self.state_combo = QComboBox()
        self.state_combo.addItems([
            "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
            "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Estado de México",
            "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "Michoacán", "Morelos",
            "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
            "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala",
            "Veracruz", "Yucatán", "Zacatecas", "Ciudad de México"
        ])
        self.state_combo.setCurrentText("Durango")
        
        # Agregar campos al layout
        layout.addRow("Nombre de la Escuela *:", self.name_edit)
        layout.addRow("CCT *:", self.cct_edit)
        layout.addRow("Director(a) *:", self.director_edit)
        layout.addRow("Dirección:", self.address_edit)
        layout.addRow("Teléfono:", self.phone_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Zona Escolar:", self.zone_edit)
        layout.addRow("Sector:", self.sector_edit)
        layout.addRow("Ciudad:", self.city_edit)
        layout.addRow("Estado:", self.state_combo)
        
        return widget
    
    def create_academic_tab(self) -> QWidget:
        """Crea el tab de configuración académica"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Ciclo escolar
        year_group = QGroupBox("Ciclo Escolar")
        year_layout = QFormLayout(year_group)
        
        self.year_edit = QLineEdit()
        self.year_edit.setText("2024-2025")
        year_layout.addRow("Ciclo Escolar:", self.year_edit)
        
        layout.addWidget(year_group)
        
        # Grados
        grades_group = QGroupBox("Grados")
        grades_layout = QFormLayout(grades_group)
        
        self.min_grade_spin = QSpinBox()
        self.min_grade_spin.setRange(1, 6)
        self.min_grade_spin.setValue(1)
        
        self.max_grade_spin = QSpinBox()
        self.max_grade_spin.setRange(1, 6)
        self.max_grade_spin.setValue(6)
        
        grades_layout.addRow("Grado Mínimo:", self.min_grade_spin)
        grades_layout.addRow("Grado Máximo:", self.max_grade_spin)
        
        layout.addWidget(grades_group)
        
        # Grupos
        groups_group = QGroupBox("Grupos")
        groups_layout = QFormLayout(groups_group)
        
        self.groups_edit = QLineEdit()
        self.groups_edit.setText("A,B")
        self.groups_edit.setPlaceholderText("Separar con comas: A,B,C")
        
        groups_layout.addRow("Grupos Disponibles:", self.groups_edit)
        
        layout.addWidget(groups_group)
        
        # Turnos
        shifts_group = QGroupBox("Turnos")
        shifts_layout = QVBoxLayout(shifts_group)
        
        self.morning_check = QCheckBox("Matutino")
        self.morning_check.setChecked(True)
        self.afternoon_check = QCheckBox("Vespertino")
        
        shifts_layout.addWidget(self.morning_check)
        shifts_layout.addWidget(self.afternoon_check)
        
        layout.addWidget(shifts_group)
        
        layout.addStretch()
        
        return widget
    
    def create_customization_tab(self) -> QWidget:
        """Crea el tab de personalización"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Colores
        colors_group = QGroupBox("Esquema de Colores")
        colors_layout = QFormLayout(colors_group)
        
        self.primary_color_edit = QLineEdit()
        self.primary_color_edit.setText("#2C3E50")
        
        self.secondary_color_edit = QLineEdit()
        self.secondary_color_edit.setText("#3498DB")
        
        colors_layout.addRow("Color Primario:", self.primary_color_edit)
        colors_layout.addRow("Color Secundario:", self.secondary_color_edit)
        
        layout.addWidget(colors_group)
        
        # Opciones
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout(options_group)
        
        self.show_photos_check = QCheckBox("Incluir fotos en constancias")
        self.show_photos_check.setChecked(True)
        
        self.custom_templates_check = QCheckBox("Usar plantillas personalizadas")
        
        options_layout.addWidget(self.show_photos_check)
        options_layout.addWidget(self.custom_templates_check)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        return widget
    
    def create_systems_panel(self) -> QWidget:
        """Crea el panel de sistemas generados"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title = QLabel("Sistemas Generados")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Lista de sistemas
        self.systems_list = QListWidget()
        layout.addWidget(self.systems_list)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.clicked.connect(self.load_generated_systems)
        
        self.open_folder_btn = QPushButton("📁 Abrir Carpeta")
        self.open_folder_btn.clicked.connect(self.open_systems_folder)
        
        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addWidget(self.open_folder_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def load_current_school(self):
        """Carga los datos de la escuela actual"""
        try:
            with open("school_config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Cargar información básica
            school_info = config.get("school_info", {})
            self.name_edit.setText(school_info.get("name", ""))
            self.cct_edit.setText(school_info.get("cct", ""))
            self.director_edit.setText(school_info.get("director", ""))
            self.address_edit.setPlainText(school_info.get("address", ""))
            self.phone_edit.setText(school_info.get("phone", ""))
            self.email_edit.setText(school_info.get("email", ""))
            self.zone_edit.setText(school_info.get("zone", ""))
            self.sector_edit.setText(school_info.get("sector", ""))
            
            # Cargar ubicación
            location_info = config.get("location_info", {})
            self.city_edit.setText(location_info.get("city", ""))
            state = location_info.get("state", "")
            if state:
                index = self.state_combo.findText(state)
                if index >= 0:
                    self.state_combo.setCurrentIndex(index)
            
            # Cargar información académica
            academic_info = config.get("academic_info", {})
            self.year_edit.setText(academic_info.get("current_year", "2024-2025"))
            
            grades = academic_info.get("grades", [1, 2, 3, 4, 5, 6])
            if grades:
                self.min_grade_spin.setValue(min(grades))
                self.max_grade_spin.setValue(max(grades))
            
            groups = academic_info.get("groups", ["A", "B"])
            self.groups_edit.setText(",".join(groups))
            
            shifts = academic_info.get("shifts", ["MATUTINO"])
            self.morning_check.setChecked("MATUTINO" in shifts)
            self.afternoon_check.setChecked("VESPERTINO" in shifts)
            
            # Cargar personalización
            customization = config.get("customization", {})
            self.primary_color_edit.setText(customization.get("primary_color", "#2C3E50"))
            self.secondary_color_edit.setText(customization.get("secondary_color", "#3498DB"))
            self.show_photos_check.setChecked(customization.get("show_photos", True))
            self.custom_templates_check.setChecked(customization.get("use_custom_templates", False))
            
            QMessageBox.information(self, "Éxito", "Datos de la escuela actual cargados correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando datos de escuela actual:\n{str(e)}")
    
    def clear_form(self):
        """Limpia el formulario"""
        # Limpiar campos básicos
        self.name_edit.clear()
        self.cct_edit.clear()
        self.director_edit.clear()
        self.address_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
        self.zone_edit.clear()
        self.sector_edit.clear()
        self.city_edit.clear()
        self.state_combo.setCurrentText("Durango")
        
        # Limpiar académicos
        self.year_edit.setText("2024-2025")
        self.min_grade_spin.setValue(1)
        self.max_grade_spin.setValue(6)
        self.groups_edit.setText("A,B")
        self.morning_check.setChecked(True)
        self.afternoon_check.setChecked(False)
        
        # Limpiar personalización
        self.primary_color_edit.setText("#2C3E50")
        self.secondary_color_edit.setText("#3498DB")
        self.show_photos_check.setChecked(True)
        self.custom_templates_check.setChecked(False)
    
    def generate_system(self):
        """Genera un nuevo sistema"""
        # Validar campos obligatorios
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "El nombre de la escuela es obligatorio")
            return
        
        if not self.cct_edit.text().strip():
            QMessageBox.warning(self, "Error", "El CCT es obligatorio")
            return
        
        if not self.director_edit.text().strip():
            QMessageBox.warning(self, "Error", "El nombre del director es obligatorio")
            return
        
        # Recopilar datos
        school_data = self.collect_form_data()
        
        # Mostrar progreso
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.generate_btn.setEnabled(False)
        
        # Iniciar worker
        self.worker = SystemBuildWorker(school_data)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.build_completed.connect(self.on_build_completed)
        self.worker.start()
    
    def collect_form_data(self) -> dict:
        """Recopila los datos del formulario"""
        # Turnos
        shifts = []
        if self.morning_check.isChecked():
            shifts.append("MATUTINO")
        if self.afternoon_check.isChecked():
            shifts.append("VESPERTINO")
        
        # Grados
        min_grade = self.min_grade_spin.value()
        max_grade = self.max_grade_spin.value()
        grades = list(range(min_grade, max_grade + 1))
        
        # Grupos
        groups_text = self.groups_edit.text().strip()
        groups = [g.strip() for g in groups_text.split(",") if g.strip()]
        
        return {
            "name": self.name_edit.text().strip(),
            "cct": self.cct_edit.text().strip(),
            "director": self.director_edit.text().strip(),
            "address": self.address_edit.toPlainText().strip(),
            "phone": self.phone_edit.text().strip(),
            "email": self.email_edit.text().strip(),
            "zone": self.zone_edit.text().strip(),
            "sector": self.sector_edit.text().strip(),
            "city": self.city_edit.text().strip(),
            "state": self.state_combo.currentText(),
            "academic_year": self.year_edit.text().strip(),
            "grades": grades,
            "groups": groups,
            "shifts": shifts,
            "primary_color": self.primary_color_edit.text().strip(),
            "secondary_color": self.secondary_color_edit.text().strip(),
            "show_photos": self.show_photos_check.isChecked(),
            "use_custom_templates": self.custom_templates_check.isChecked()
        }
    
    def update_progress(self, value, message):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def on_build_completed(self, result):
        """Maneja la finalización de la generación"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        if result["success"]:
            QMessageBox.information(
                self,
                "Éxito",
                f"Sistema generado exitosamente:\n\n"
                f"Escuela: {result['school_name']}\n"
                f"Archivo: {Path(result['system_path']).name}\n"
                f"Tamaño: {result['package_size']}"
            )
            self.load_generated_systems()
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Error generando sistema:\n\n{result['error']}"
            )
    
    def load_generated_systems(self):
        """Carga la lista de sistemas generados"""
        self.systems_list.clear()
        
        try:
            systems = self.builder.list_generated_systems()
            
            for system in systems:
                item_text = f"{system['name']} ({system['size']}) - {system['created'][:10]}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, system)
                self.systems_list.addItem(item)
                
        except Exception as e:
            self.logger.error(f"Error cargando sistemas: {e}")
    
    def open_systems_folder(self):
        """Abre la carpeta de sistemas generados"""
        systems_dir = Path("build/generated_systems")
        if systems_dir.exists():
            os.startfile(str(systems_dir))
        else:
            QMessageBox.information(self, "Información", "No hay sistemas generados aún")


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Configurar estilo
    app.setStyle("Fusion")
    
    window = SystemBuilderUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
