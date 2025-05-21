"""
Comandos relacionados con constancias
"""
from typing import Dict, Any, Tuple, List, Optional
import os
from app.core.service_provider import ServiceProvider
from app.core.commands.base_command import Command
from app.core.utils import open_file_with_default_app

class GenerarConstanciaCommand(Command):
    """Comando para generar una constancia"""
    
    def __init__(self, alumno_id: int, tipo_constancia: str, incluir_foto: bool = False, abrir_archivo: bool = True):
        """
        Inicializa el comando
        
        Args:
            alumno_id: ID del alumno
            tipo_constancia: Tipo de constancia (estudio, calificaciones, traslado)
            incluir_foto: Si se debe incluir la foto del alumno
            abrir_archivo: Si se debe abrir el archivo generado
        """
        self.alumno_id = alumno_id
        self.tipo_constancia = tipo_constancia
        self.incluir_foto = incluir_foto
        self.abrir_archivo = abrir_archivo
        self.service_provider = ServiceProvider.get_instance()
    
    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando
        
        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Validar tipo de constancia
            tipos_validos = ["estudio", "calificaciones", "traslado"]
            if self.tipo_constancia not in tipos_validos:
                return False, f"Tipo de constancia no válido. Debe ser uno de: {', '.join(tipos_validos)}", {}
            
            # Generar constancia
            success, message, data = self.service_provider.constancia_service.generar_constancia_para_alumno(
                self.alumno_id, self.tipo_constancia, self.incluir_foto
            )
            
            if success and self.abrir_archivo and data and "ruta_archivo" in data:
                # Abrir el archivo generado
                open_file_with_default_app(data["ruta_archivo"])
            
            return success, message, data or {}
        except Exception as e:
            return False, f"Error al generar constancia: {str(e)}", {}

class TransformarConstanciaCommand(Command):
    """Comando para transformar una constancia"""
    
    def __init__(self, pdf_path: str, tipo_constancia: str, incluir_foto: bool = False, 
                 guardar_alumno: bool = False, abrir_archivo: bool = True):
        """
        Inicializa el comando
        
        Args:
            pdf_path: Ruta al archivo PDF de la constancia original
            tipo_constancia: Tipo de constancia a generar
            incluir_foto: Si se debe incluir la foto del alumno
            guardar_alumno: Si se deben guardar los datos del alumno
            abrir_archivo: Si se debe abrir el archivo generado
        """
        self.pdf_path = pdf_path
        self.tipo_constancia = tipo_constancia
        self.incluir_foto = incluir_foto
        self.guardar_alumno = guardar_alumno
        self.abrir_archivo = abrir_archivo
        self.service_provider = ServiceProvider.get_instance()
    
    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando
        
        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Validar que el archivo exista
            if not os.path.exists(self.pdf_path):
                return False, f"El archivo {self.pdf_path} no existe", {}
            
            # Validar tipo de constancia
            tipos_validos = ["estudio", "calificaciones", "traslado"]
            if self.tipo_constancia not in tipos_validos:
                return False, f"Tipo de constancia no válido. Debe ser uno de: {', '.join(tipos_validos)}", {}
            
            # Transformar constancia
            success, message, data = self.service_provider.constancia_service.generar_constancia_desde_pdf(
                self.pdf_path, self.tipo_constancia, self.incluir_foto, self.guardar_alumno
            )
            
            if success and self.abrir_archivo and data and "ruta_archivo" in data:
                # Abrir el archivo generado
                open_file_with_default_app(data["ruta_archivo"])
            
            return success, message, data or {}
        except Exception as e:
            return False, f"Error al transformar constancia: {str(e)}", {}

class ListarConstanciasCommand(Command):
    """Comando para listar las constancias de un alumno"""
    
    def __init__(self, alumno_id: int):
        """
        Inicializa el comando
        
        Args:
            alumno_id: ID del alumno
        """
        self.alumno_id = alumno_id
        self.service_provider = ServiceProvider.get_instance()
    
    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando
        
        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Verificar que el alumno exista
            alumno = self.service_provider.alumno_service.get_alumno(self.alumno_id)
            if not alumno:
                return False, f"No se encontró el alumno con ID {self.alumno_id}", {}
            
            # Obtener constancias
            constancias = self.service_provider.alumno_service.get_constancias(self.alumno_id)
            
            return True, f"Se encontraron {len(constancias)} constancias para {alumno.get('nombre', '')}", {
                "alumno": alumno,
                "constancias": constancias
            }
        except Exception as e:
            return False, f"Error al listar constancias: {str(e)}", {}
