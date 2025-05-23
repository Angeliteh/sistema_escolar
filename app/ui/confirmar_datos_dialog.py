"""
Diálogo para confirmar los datos extraídos de un PDF antes de guardarlos
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QScrollArea, QWidget, QFrame,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from app.services.constancia_service import ConstanciaService
from app.core.utils import format_curp
from app.core.config import Config

class ConfirmarDatosDialog(QDialog):
    """Diálogo para confirmar los datos extraídos de un PDF antes de guardarlos"""

    def __init__(self, parent=None, datos=None, pdf_path=None, incluir_foto=False, tiene_calificaciones=False):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Datos")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        self.datos = datos or {}
        self.pdf_path = pdf_path
        self.incluir_foto = incluir_foto
        self.tiene_calificaciones = tiene_calificaciones
        self.constancia_service = ConstanciaService()

        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("Confirmar Datos del Alumno")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")

        main_layout.addWidget(title_label)

        # Instrucciones
        instrucciones = QLabel("Por favor, revise y corrija los datos extraídos del PDF antes de guardarlos en la base de datos.")
        instrucciones.setWordWrap(True)
        instrucciones.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 10px;")
        main_layout.addWidget(instrucciones)

        # Área de desplazamiento para los campos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)

        # Sección de datos personales
        datos_personales = QGroupBox("Datos Personales")
        datos_personales.setStyleSheet("""
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

        datos_personales_layout = QVBoxLayout(datos_personales)
        datos_personales_layout.setSpacing(10)

        # Campos para datos personales
        self.nombre_edit = self.crear_campo_editable("Nombre completo:")
        self.curp_edit = self.crear_campo_editable("CURP:")
        self.matricula_edit = self.crear_campo_editable("Matrícula:")
        self.fecha_nacimiento_edit = self.crear_campo_editable("Fecha de nacimiento:")

        datos_personales_layout.addWidget(self.nombre_edit)
        datos_personales_layout.addWidget(self.curp_edit)
        datos_personales_layout.addWidget(self.matricula_edit)
        datos_personales_layout.addWidget(self.fecha_nacimiento_edit)

        # Sección de datos escolares
        datos_escolares = QGroupBox("Datos Escolares")
        datos_escolares.setStyleSheet("""
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

        datos_escolares_layout = QVBoxLayout(datos_escolares)
        datos_escolares_layout.setSpacing(10)

        # Campos para datos escolares
        self.grado_edit = self.crear_campo_editable("Grado:")
        self.grupo_edit = self.crear_campo_editable("Grupo:")
        self.turno_edit = self.crear_campo_editable("Turno:")
        self.ciclo_edit = self.crear_campo_editable("Ciclo escolar:")
        self.escuela_edit = self.crear_campo_editable("Escuela:")
        self.cct_edit = self.crear_campo_editable("CCT:")

        datos_escolares_layout.addWidget(self.grado_edit)
        datos_escolares_layout.addWidget(self.grupo_edit)
        datos_escolares_layout.addWidget(self.turno_edit)
        datos_escolares_layout.addWidget(self.ciclo_edit)
        datos_escolares_layout.addWidget(self.escuela_edit)
        datos_escolares_layout.addWidget(self.cct_edit)

        # Sección de calificaciones (solo si están disponibles)
        self.calificaciones_group = QGroupBox("Calificaciones")
        self.calificaciones_group.setStyleSheet("""
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

        calificaciones_layout = QVBoxLayout(self.calificaciones_group)

        # Etiqueta para mostrar si hay calificaciones
        self.lbl_estado_calificaciones = QLabel()
        self.lbl_estado_calificaciones.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
        """)
        calificaciones_layout.addWidget(self.lbl_estado_calificaciones)

        # Contenedor para la lista de calificaciones
        self.calificaciones_container = QWidget()
        self.calificaciones_container_layout = QVBoxLayout(self.calificaciones_container)
        calificaciones_layout.addWidget(self.calificaciones_container)

        # Añadir secciones al layout del scroll
        scroll_layout.addWidget(datos_personales)
        scroll_layout.addWidget(datos_escolares)
        scroll_layout.addWidget(self.calificaciones_group)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        # Botón de cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_cancelar.setMinimumHeight(40)
        btn_cancelar.clicked.connect(self.reject)

        # Botón de guardar
        self.btn_guardar = QPushButton("Guardar en Base de Datos")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_guardar.setMinimumHeight(40)
        self.btn_guardar.clicked.connect(self.guardar_datos)

        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(self.btn_guardar)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def crear_campo_editable(self, etiqueta):
        """Crea un campo editable con etiqueta"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Etiqueta
        label = QLabel(etiqueta)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
                max-width: 150px;
            }
        """)

        # Campo editable
        edit = QLineEdit()
        edit.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f0f9ff;
            }
        """)

        layout.addWidget(label)
        layout.addWidget(edit, 1)

        # Guardar referencia al campo editable
        container.campo_editable = edit
        container.etiqueta = etiqueta

        return container

    def cargar_datos(self):
        """Carga los datos extraídos en los campos editables"""
        if not self.datos:
            return

        # Cargar datos personales
        self.nombre_edit.campo_editable.setText(self.datos.get('nombre', ''))

        curp = self.datos.get('curp', '')
        curp_formateado = format_curp(curp) if curp else ''
        self.curp_edit.campo_editable.setText(curp_formateado)

        self.matricula_edit.campo_editable.setText(self.datos.get('matricula', ''))
        self.fecha_nacimiento_edit.campo_editable.setText(self.datos.get('nacimiento', ''))

        # Cargar datos escolares
        self.grado_edit.campo_editable.setText(str(self.datos.get('grado', '')))
        self.grupo_edit.campo_editable.setText(self.datos.get('grupo', ''))
        self.turno_edit.campo_editable.setText(self.datos.get('turno', 'MATUTINO'))
        self.ciclo_edit.campo_editable.setText(self.datos.get('ciclo', Config.CURRENT_SCHOOL_YEAR))
        self.escuela_edit.campo_editable.setText(self.datos.get('escuela', Config.SCHOOL_NAME))
        self.cct_edit.campo_editable.setText(self.datos.get('cct', Config.SCHOOL_CCT))

        # Cargar calificaciones si están disponibles
        self.cargar_calificaciones()

    def cargar_calificaciones(self):
        """Carga y muestra las calificaciones si están disponibles"""
        # Limpiar el contenedor de calificaciones
        for i in reversed(range(self.calificaciones_container_layout.count())):
            widget = self.calificaciones_container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Verificar si hay calificaciones
        calificaciones = self.datos.get('calificaciones', [])

        if self.tiene_calificaciones:
            # Mostrar mensaje de que hay calificaciones
            self.lbl_estado_calificaciones.setText("El PDF contiene calificaciones que se guardarán en la base de datos.")
            self.lbl_estado_calificaciones.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #d5f5e3;
                    color: #27ae60;
                }
            """)

            # Crear tabla de calificaciones
            for calificacion in calificaciones:
                # Crear widget para cada calificación
                cal_widget = QWidget()
                cal_layout = QHBoxLayout(cal_widget)
                cal_layout.setContentsMargins(0, 0, 0, 0)

                # Nombre de la materia
                lbl_materia = QLabel(calificacion.get('nombre', ''))
                lbl_materia.setStyleSheet("font-weight: bold; min-width: 250px;")

                # Calificaciones por periodo
                lbl_p1 = QLabel(f"P1: {calificacion.get('i', 0)}")
                lbl_p2 = QLabel(f"P2: {calificacion.get('ii', 0)}")
                lbl_p3 = QLabel(f"P3: {calificacion.get('iii', 0)}")

                # Promedio
                lbl_promedio = QLabel(f"Promedio: {calificacion.get('promedio', 0)}")
                lbl_promedio.setStyleSheet("font-weight: bold; color: #e74c3c;")

                # Añadir a layout
                cal_layout.addWidget(lbl_materia)
                cal_layout.addWidget(lbl_p1)
                cal_layout.addWidget(lbl_p2)
                cal_layout.addWidget(lbl_p3)
                cal_layout.addWidget(lbl_promedio)

                # Añadir al contenedor
                self.calificaciones_container_layout.addWidget(cal_widget)
        else:
            # Mostrar mensaje de que no hay calificaciones
            self.lbl_estado_calificaciones.setText("El PDF no contiene calificaciones. No se guardarán calificaciones en la base de datos.")
            self.lbl_estado_calificaciones.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #fadbd8;
                    color: #c0392b;
                }
            """)

    def guardar_datos(self):
        """Guarda los datos en la base de datos"""
        try:
            # Recopilar los datos de los campos editables
            datos_actualizados = {
                'nombre': self.nombre_edit.campo_editable.text(),
                'curp': self.curp_edit.campo_editable.text().replace('-', '').replace(' ', ''),
                'matricula': self.matricula_edit.campo_editable.text(),
                'nacimiento': self.fecha_nacimiento_edit.campo_editable.text(),
                'grado': self.grado_edit.campo_editable.text(),
                'grupo': self.grupo_edit.campo_editable.text(),
                'turno': self.turno_edit.campo_editable.text(),
                'ciclo': self.ciclo_edit.campo_editable.text(),
                'escuela': self.escuela_edit.campo_editable.text(),
                'cct': self.cct_edit.campo_editable.text(),
                'tiene_calificaciones': self.tiene_calificaciones
            }

            # Asegurarse de que las calificaciones se incluyan si están disponibles
            if self.tiene_calificaciones and 'calificaciones' in self.datos:
                datos_actualizados['calificaciones'] = self.datos['calificaciones']

            # Validar datos básicos
            if not datos_actualizados['nombre']:
                QMessageBox.warning(self, "Error", "El nombre del alumno no puede estar vacío.")
                return

            if not datos_actualizados['curp'] or len(datos_actualizados['curp']) != 18:
                QMessageBox.warning(self, "Error", "La CURP debe tener 18 caracteres.")
                return

            # Guardar los datos en la base de datos
            success, message, _ = self.constancia_service.guardar_alumno_desde_pdf(
                self.pdf_path,
                incluir_foto=self.incluir_foto,
                datos_override=datos_actualizados
            )

            if success:
                self.accept()  # Cerrar el diálogo con éxito
            else:
                QMessageBox.warning(self, "Error", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar los datos: {str(e)}")
