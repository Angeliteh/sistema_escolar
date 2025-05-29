"""
Comandos relacionados con alumnos
"""
from typing import Dict, Any, Tuple
from app.core.service_provider import ServiceProvider
from app.core.commands.base_command import Command
from app.core.utils import format_curp, is_valid_curp

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

            # Convertir el nombre a mayúsculas
            if 'nombre' in self.datos:
                self.datos['nombre'] = self.datos['nombre'].upper()

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
            # No validamos el nombre aquí, ya que estamos actualizando por ID
            # y el nombre podría no estar entre los datos a actualizar

            # Convertir el nombre a mayúsculas si está presente
            if 'nombre' in self.datos:
                self.datos['nombre'] = self.datos['nombre'].upper()

            # Formatear y validar CURP si está presente
            if 'curp' in self.datos:
                curp = format_curp(self.datos['curp'])
                if curp and not is_valid_curp(curp):
                    return False, "La CURP no tiene un formato válido", {}
                self.datos['curp'] = curp

            # Actualizar alumno
            success = self.service_provider.alumno_service.actualizar_alumno(self.alumno_id, self.datos)

            if success:
                # Obtener datos actualizados del alumno
                alumno = self.service_provider.alumno_service.get_alumno(self.alumno_id)
                return True, f"Alumno con ID {self.alumno_id} actualizado correctamente", {"alumno": alumno}
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


class DetallesAlumnoCommand(Command):
    """Comando para obtener los detalles completos de un alumno"""

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
            # Obtener datos completos del alumno
            alumno = self.service_provider.alumno_service.get_alumno(self.alumno_id)
            if not alumno:
                return False, f"No se encontró el alumno con ID {self.alumno_id}", {}

            # Obtener constancias del alumno
            constancias = self.service_provider.alumno_service.get_constancias(self.alumno_id)

            # Añadir constancias a los datos del alumno
            alumno["constancias"] = constancias

            return True, f"Detalles del alumno {alumno.get('nombre', '')}", {"alumno": alumno}
        except Exception as e:
            return False, f"Error al obtener detalles del alumno: {str(e)}", {}


class BuscarAlumnosPorCriterioCommand(Command):
    """Comando para buscar alumnos por criterios específicos como grado, grupo, etc."""

    def __init__(self, criterio: str, valor: Any, limit: int = 100):
        """
        Inicializa el comando

        Args:
            criterio: Campo por el que se va a buscar (grado, grupo, turno, etc.)
            valor: Valor a buscar
            limit: Límite de resultados
        """
        self.criterio = criterio.lower()
        self.valor = valor
        self.limit = limit
        self.service_provider = ServiceProvider.get_instance()

    def execute(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta el comando

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Obtener todos los alumnos
            todos_alumnos = self.service_provider.alumno_service.buscar_alumnos("", self.limit)

            # Filtrar por el criterio especificado
            alumnos_filtrados = []

            # Convertir el valor a string para comparaciones más flexibles
            valor_str = str(self.valor).lower()

            for alumno in todos_alumnos:
                # Obtener el valor del alumno para el criterio especificado
                valor_alumno = alumno.get(self.criterio)

                # Si el valor es None, continuar con el siguiente alumno
                if valor_alumno is None:
                    continue

                # Convertir el valor del alumno a string para comparación
                valor_alumno_str = str(valor_alumno).lower()

                # Comparar los valores
                if valor_alumno_str == valor_str:
                    alumnos_filtrados.append(alumno)

                    # Limitar resultados
                    if len(alumnos_filtrados) >= self.limit:
                        break

            # Mensaje personalizado según el criterio
            mensaje = f"Se encontraron {len(alumnos_filtrados)} alumnos"
            if self.criterio == "grado":
                mensaje = f"Se encontraron {len(alumnos_filtrados)} alumnos en {self.criterio} {self.valor}"
            elif self.criterio == "grupo":
                mensaje = f"Se encontraron {len(alumnos_filtrados)} alumnos en el grupo {self.valor}"
            elif self.criterio == "turno":
                mensaje = f"Se encontraron {len(alumnos_filtrados)} alumnos en el turno {self.valor}"

            return True, mensaje, {"alumnos": alumnos_filtrados}
        except Exception as e:
            return False, f"Error al buscar alumnos por {self.criterio}: {str(e)}", {}
