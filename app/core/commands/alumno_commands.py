"""
Comandos relacionados con alumnos
"""
from typing import Dict, Any, Tuple, List, Optional
from app.core.service_provider import ServiceProvider
from app.core.commands.base_command import Command
from app.core.utils import format_curp, is_valid_curp

class BuscarAlumnoCommand(Command):
    """Comando para buscar alumnos"""

    def __init__(self, query: str, limit: int = 100, busqueda_exacta: bool = False):
        """
        Inicializa el comando

        Args:
            query: Texto de búsqueda (nombre o CURP)
            limit: Límite de resultados
            busqueda_exacta: Si es True, busca coincidencias exactas; si es False, busca coincidencias parciales
        """
        self.query = query
        self.limit = limit
        self.busqueda_exacta = busqueda_exacta
        self.service_provider = ServiceProvider.get_instance()

    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Si la búsqueda no es exacta y la consulta tiene al menos 3 caracteres,
            # intentamos buscar coincidencias parciales
            if not self.busqueda_exacta and len(self.query) >= 3:
                # Primero intentamos una búsqueda exacta
                alumnos_exactos = self.service_provider.alumno_service.buscar_alumnos(self.query, self.limit)

                # Si encontramos resultados exactos, los devolvemos
                if alumnos_exactos:
                    return True, f"Se encontraron {len(alumnos_exactos)} alumnos", {"alumnos": alumnos_exactos}

                # Si no hay resultados exactos, intentamos una búsqueda parcial
                # Esto depende de la implementación del servicio, pero podemos hacer una búsqueda
                # más flexible aquí si el servicio no lo soporta
                alumnos = []

                # Buscar por nombre parcial (implementación básica)
                todos_alumnos = self.service_provider.alumno_service.buscar_alumnos("", self.limit)
                query_lower = self.query.lower()

                for alumno in todos_alumnos:
                    nombre = alumno.get('nombre', '').lower()
                    if query_lower in nombre:
                        alumnos.append(alumno)

                        # Limitar resultados
                        if len(alumnos) >= self.limit:
                            break

                return True, f"Se encontraron {len(alumnos)} alumnos", {"alumnos": alumnos}
            else:
                # Búsqueda exacta normal
                alumnos = self.service_provider.alumno_service.buscar_alumnos(self.query, self.limit)
                return True, f"Se encontraron {len(alumnos)} alumnos", {"alumnos": alumnos}
        except Exception as e:
            return False, f"Error al buscar alumnos: {str(e)}", {}

class RegistrarAlumnoCommand(Command):
    """Comando para registrar un nuevo alumno"""

    def __init__(self, datos: Dict[str, Any]):
        """
        Inicializa el comando

        Args:
            datos: Diccionario con los datos del alumno
        """
        self.datos = datos
        self.service_provider = ServiceProvider.get_instance()

    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Validar datos básicos
            if not self.datos.get('nombre'):
                return False, "El nombre del alumno es obligatorio", {}

            # Formatear y validar CURP
            curp = format_curp(self.datos.get('curp', ''))
            if not curp:
                return False, "La CURP es obligatoria", {}

            if not is_valid_curp(curp):
                return False, "La CURP no tiene un formato válido", {}

            # Actualizar la CURP formateada
            self.datos['curp'] = curp

            # Registrar alumno
            success, message, data = self.service_provider.alumno_service.registrar_alumno(self.datos)
            return success, message, data or {}
        except Exception as e:
            return False, f"Error al registrar alumno: {str(e)}", {}

class ActualizarAlumnoCommand(Command):
    """Comando para actualizar un alumno existente"""

    def __init__(self, alumno_id: int, datos: Dict[str, Any]):
        """
        Inicializa el comando

        Args:
            alumno_id: ID del alumno a actualizar
            datos: Diccionario con los datos a actualizar
        """
        self.alumno_id = alumno_id
        self.datos = datos
        self.service_provider = ServiceProvider.get_instance()

    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Validar datos básicos
            if not self.datos.get('nombre'):
                return False, "El nombre del alumno es obligatorio", {}

            # Formatear y validar CURP si está presente
            if 'curp' in self.datos:
                curp = format_curp(self.datos['curp'])
                if curp and not is_valid_curp(curp):
                    return False, "La CURP no tiene un formato válido", {}
                self.datos['curp'] = curp

            # Actualizar alumno
            success = self.service_provider.alumno_service.actualizar_alumno(self.alumno_id, self.datos)

            if success:
                return True, f"Alumno con ID {self.alumno_id} actualizado correctamente", {}
            else:
                return False, f"No se pudo actualizar el alumno con ID {self.alumno_id}", {}
        except Exception as e:
            return False, f"Error al actualizar alumno: {str(e)}", {}

class EliminarAlumnoCommand(Command):
    """Comando para eliminar un alumno"""

    def __init__(self, alumno_id: int):
        """
        Inicializa el comando

        Args:
            alumno_id: ID del alumno a eliminar
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
            # Obtener datos del alumno antes de eliminarlo
            alumno = self.service_provider.alumno_service.get_alumno(self.alumno_id)
            if not alumno:
                return False, f"No se encontró el alumno con ID {self.alumno_id}", {}

            # Eliminar alumno
            success = self.service_provider.alumno_service.eliminar_alumno(self.alumno_id)

            if success:
                return True, f"Alumno {alumno.get('nombre', '')} eliminado correctamente", {"alumno": alumno}
            else:
                return False, f"No se pudo eliminar el alumno con ID {self.alumno_id}", {}
        except Exception as e:
            return False, f"Error al eliminar alumno: {str(e)}", {}
