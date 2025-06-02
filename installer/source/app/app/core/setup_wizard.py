"""
Asistente de configuración inicial para el Sistema de Constancias Escolares
Guía al usuario a través de la configuración completa del sistema
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Optional, Tuple
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                             QFormLayout, QLineEdit, QTextEdit, QComboBox,
                             QCheckBox, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QProgressBar, QGroupBox, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from app.core.logging.logger_manager import get_logger
from app.core.system_detector import SystemConfigurationDetector

class SetupProgressWorker(QThread):
    """Worker thread para tareas de configuración que pueden tomar tiempo"""
    progress_updated = pyqtSignal(int, str)
    setup_completed = pyqtSignal(bool, str)
    
    def __init__(self, config_data):
        super().__init__()
        self.config_data = config_data
        self.logger = get_logger(__name__)
    
    def run(self):
        """Ejecuta el proceso de configuración"""
        try:
            # Paso 1: Crear configuración de escuela
            self.progress_updated.emit(20, "Creando configuración de escuela...")
            self.create_school_config()
            
            # Paso 2: Configurar base de datos
            self.progress_updated.emit(40, "Configurando base de datos...")
            self.setup_database()
            
            # Paso 3: Copiar recursos
            self.progress_updated.emit(60, "Copiando recursos...")
            self.copy_resources()
            
            # Paso 4: Crear archivo de versión
            self.progress_updated.emit(80, "Finalizando configuración...")
            self.create_version_file()
            
            # Paso 5: Validar configuración
            self.progress_updated.emit(100, "Validando configuración...")
            self.validate_setup()
            
            self.setup_completed.emit(True, "Configuración completada exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error en configuración: {e}")
            self.setup_completed.emit(False, f"Error en configuración: {str(e)}")
    
    def create_school_config(self):
        """Crea el archivo de configuración de la escuela"""
        config = {
            "school_info": {
                "name": self.config_data.get("school_name", ""),
                "cct": self.config_data.get("school_cct", ""),
                "director": self.config_data.get("school_director", ""),
                "address": self.config_data.get("school_address", ""),
                "phone": self.config_data.get("school_phone", ""),
                "email": self.config_data.get("school_email", ""),
                "zone": self.config_data.get("school_zone", ""),
                "sector": self.config_data.get("school_sector", "")
            },
            "academic_info": {
                "current_year": self.config_data.get("academic_year", "2024-2025"),
                "grades": self.config_data.get("grades", [1, 2, 3, 4, 5, 6]),
                "groups": self.config_data.get("groups", ["A", "B"]),
                "shifts": self.config_data.get("shifts", ["MATUTINO"]),
                "education_level": "PRIMARIA"
            },
            "location_info": {
                "city": self.config_data.get("city", ""),
                "state": self.config_data.get("state", ""),
                "country": "MÉXICO"
            },
            "customization": {
                "logo_file": "logo_educacion.png",
                "primary_color": self.config_data.get("primary_color", "#2C3E50"),
                "secondary_color": self.config_data.get("secondary_color", "#3498DB"),
                "use_custom_templates": False,
                "show_photos": self.config_data.get("show_photos", True)
            },
            "features": {
                "enable_photos": True,
                "enable_grades": True,
                "enable_transfer": True,
                "enable_ai_chat": True,
                "enable_pdf_transform": True
            },
            "system_info": {
                "version": "2.0.0",
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "configured_by": "setup_wizard"
            }
        }
        
        with open("school_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def setup_database(self):
        """Configura la base de datos inicial"""
        # Por ahora, verificar que existe la base de datos
        db_path = "resources/data/alumnos.db"
        if not os.path.exists(db_path):
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            # Aquí se podría crear una base de datos vacía
            # Por ahora, solo crear el directorio
    
    def copy_resources(self):
        """Copia recursos necesarios"""
        # Verificar que existan los directorios de recursos
        directories = [
            "resources/images/logos",
            "resources/images/photos",
            "resources/output/logos",
            "resources/output/fotos",
            "resources/templates",
            "logs"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_version_file(self):
        """Crea el archivo de versión del sistema"""
        detector = SystemConfigurationDetector()
        detector.mark_as_configured(self.config_data.get("school_name", "Escuela"))
    
    def validate_setup(self):
        """Valida que la configuración sea correcta"""
        detector = SystemConfigurationDetector()
        state = detector.detect_system_state()
        
        if not state["is_configured"]:
            raise Exception("La configuración no se completó correctamente")

class SchoolInfoPage(QWizardPage):
    """Página para información básica de la escuela"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Información de la Escuela")
        self.setSubTitle("Ingrese los datos básicos de su institución educativa")
        
        layout = QFormLayout()
        
        # Campos de información
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
        
        # Agregar campos al layout
        layout.addRow("Nombre de la Escuela *:", self.name_edit)
        layout.addRow("Clave de Centro de Trabajo (CCT) *:", self.cct_edit)
        layout.addRow("Director(a) *:", self.director_edit)
        layout.addRow("Dirección:", self.address_edit)
        layout.addRow("Teléfono:", self.phone_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Zona Escolar:", self.zone_edit)
        layout.addRow("Sector:", self.sector_edit)
        
        # Nota sobre campos obligatorios
        note_label = QLabel("* Campos obligatorios")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addRow(note_label)
        
        self.setLayout(layout)
        
        # Registrar campos para validación
        self.registerField("school_name*", self.name_edit)
        self.registerField("school_cct*", self.cct_edit)
        self.registerField("school_director*", self.director_edit)
        self.registerField("school_address", self.address_edit, "plainText")
        self.registerField("school_phone", self.phone_edit)
        self.registerField("school_email", self.email_edit)
        self.registerField("school_zone", self.zone_edit)
        self.registerField("school_sector", self.sector_edit)

class LocationInfoPage(QWizardPage):
    """Página para información de ubicación"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Ubicación")
        self.setSubTitle("Especifique la ubicación geográfica de la escuela")
        
        layout = QFormLayout()
        
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
        
        layout.addRow("Ciudad *:", self.city_edit)
        layout.addRow("Estado *:", self.state_combo)
        
        self.setLayout(layout)
        
        # Registrar campos
        self.registerField("city*", self.city_edit)
        self.registerField("state", self.state_combo, "currentText")

class AcademicInfoPage(QWizardPage):
    """Página para información académica"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Información Académica")
        self.setSubTitle("Configure los parámetros académicos de su escuela")
        
        layout = QVBoxLayout()
        
        # Ciclo escolar
        year_group = QGroupBox("Ciclo Escolar")
        year_layout = QFormLayout()
        
        self.year_edit = QLineEdit()
        self.year_edit.setText("2024-2025")
        year_layout.addRow("Ciclo Escolar Actual:", self.year_edit)
        
        year_group.setLayout(year_layout)
        layout.addWidget(year_group)
        
        # Grados y grupos
        grades_group = QGroupBox("Grados y Grupos")
        grades_layout = QFormLayout()
        
        self.min_grade_spin = QSpinBox()
        self.min_grade_spin.setRange(1, 6)
        self.min_grade_spin.setValue(1)
        
        self.max_grade_spin = QSpinBox()
        self.max_grade_spin.setRange(1, 6)
        self.max_grade_spin.setValue(6)
        
        self.groups_edit = QLineEdit()
        self.groups_edit.setText("A,B")
        self.groups_edit.setPlaceholderText("Separar con comas: A,B,C")
        
        grades_layout.addRow("Grado Mínimo:", self.min_grade_spin)
        grades_layout.addRow("Grado Máximo:", self.max_grade_spin)
        grades_layout.addRow("Grupos Disponibles:", self.groups_edit)
        
        grades_group.setLayout(grades_layout)
        layout.addWidget(grades_group)
        
        # Turnos
        shifts_group = QGroupBox("Turnos")
        shifts_layout = QVBoxLayout()
        
        self.morning_check = QCheckBox("Matutino")
        self.morning_check.setChecked(True)
        self.afternoon_check = QCheckBox("Vespertino")
        
        shifts_layout.addWidget(self.morning_check)
        shifts_layout.addWidget(self.afternoon_check)
        
        shifts_group.setLayout(shifts_layout)
        layout.addWidget(shifts_group)
        
        self.setLayout(layout)
        
        # Registrar campos
        self.registerField("academic_year", self.year_edit)
        self.registerField("min_grade", self.min_grade_spin)
        self.registerField("max_grade", self.max_grade_spin)
        self.registerField("groups_text", self.groups_edit)
        self.registerField("morning_shift", self.morning_check)
        self.registerField("afternoon_shift", self.afternoon_check)

class CustomizationPage(QWizardPage):
    """Página para personalización visual"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Personalización")
        self.setSubTitle("Configure la apariencia de las constancias")
        
        layout = QVBoxLayout()
        
        # Colores
        colors_group = QGroupBox("Esquema de Colores")
        colors_layout = QFormLayout()
        
        self.primary_color_edit = QLineEdit()
        self.primary_color_edit.setText("#2C3E50")
        
        self.secondary_color_edit = QLineEdit()
        self.secondary_color_edit.setText("#3498DB")
        
        colors_layout.addRow("Color Primario:", self.primary_color_edit)
        colors_layout.addRow("Color Secundario:", self.secondary_color_edit)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        # Opciones
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout()
        
        self.show_photos_check = QCheckBox("Incluir fotos en constancias")
        self.show_photos_check.setChecked(True)
        
        options_layout.addWidget(self.show_photos_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        self.setLayout(layout)
        
        # Registrar campos
        self.registerField("primary_color", self.primary_color_edit)
        self.registerField("secondary_color", self.secondary_color_edit)
        self.registerField("show_photos", self.show_photos_check)

class SetupProgressPage(QWizardPage):
    """Página de progreso de configuración"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Configurando Sistema")
        self.setSubTitle("Por favor espere mientras se configura el sistema...")
        
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        
        self.status_label = QLabel("Iniciando configuración...")
        
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        self.setup_completed = False
    
    def initializePage(self):
        """Se ejecuta cuando se muestra la página"""
        # Recopilar datos del wizard
        config_data = {}
        
        # Información de escuela
        config_data["school_name"] = self.wizard().field("school_name")
        config_data["school_cct"] = self.wizard().field("school_cct")
        config_data["school_director"] = self.wizard().field("school_director")
        config_data["school_address"] = self.wizard().field("school_address")
        config_data["school_phone"] = self.wizard().field("school_phone")
        config_data["school_email"] = self.wizard().field("school_email")
        config_data["school_zone"] = self.wizard().field("school_zone")
        config_data["school_sector"] = self.wizard().field("school_sector")
        
        # Ubicación
        config_data["city"] = self.wizard().field("city")
        config_data["state"] = self.wizard().field("state")
        
        # Información académica
        config_data["academic_year"] = self.wizard().field("academic_year")
        min_grade = self.wizard().field("min_grade")
        max_grade = self.wizard().field("max_grade")
        config_data["grades"] = list(range(min_grade, max_grade + 1))
        
        groups_text = self.wizard().field("groups_text")
        config_data["groups"] = [g.strip() for g in groups_text.split(",") if g.strip()]
        
        shifts = []
        if self.wizard().field("morning_shift"):
            shifts.append("MATUTINO")
        if self.wizard().field("afternoon_shift"):
            shifts.append("VESPERTINO")
        config_data["shifts"] = shifts
        
        # Personalización
        config_data["primary_color"] = self.wizard().field("primary_color")
        config_data["secondary_color"] = self.wizard().field("secondary_color")
        config_data["show_photos"] = self.wizard().field("show_photos")
        
        # Iniciar configuración
        self.worker = SetupProgressWorker(config_data)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.setup_completed.connect(self.on_setup_completed)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def on_setup_completed(self, success, message):
        """Maneja la finalización de la configuración"""
        self.setup_completed = success
        if success:
            self.status_label.setText("✅ " + message)
            self.wizard().next()
        else:
            self.status_label.setText("❌ " + message)
            QMessageBox.critical(self, "Error de Configuración", message)
    
    def isComplete(self):
        """Determina si la página está completa"""
        return self.setup_completed

class SetupWizard(QWizard):
    """Asistente principal de configuración"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.setup_ui()
        self.add_pages()
    
    def setup_ui(self):
        """Configura la interfaz del wizard"""
        self.setWindowTitle("Asistente de Configuración - Sistema de Constancias")
        self.setFixedSize(600, 500)
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Configurar botones
        self.setButtonText(QWizard.NextButton, "Siguiente >")
        self.setButtonText(QWizard.BackButton, "< Anterior")
        self.setButtonText(QWizard.FinishButton, "Finalizar")
        self.setButtonText(QWizard.CancelButton, "Cancelar")
    
    def add_pages(self):
        """Agrega las páginas al wizard"""
        self.addPage(SchoolInfoPage())
        self.addPage(LocationInfoPage())
        self.addPage(AcademicInfoPage())
        self.addPage(CustomizationPage())
        self.addPage(SetupProgressPage())
    
    def accept(self):
        """Se ejecuta cuando el wizard se completa exitosamente"""
        QMessageBox.information(
            self,
            "Configuración Completada",
            "El sistema ha sido configurado exitosamente.\n\n"
            "Ahora puede usar todas las funcionalidades del sistema."
        )
        super().accept()


def run_setup_wizard():
    """Función para ejecutar el asistente de configuración"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    wizard = SetupWizard()
    result = wizard.exec_()
    
    return result == QWizard.Accepted
