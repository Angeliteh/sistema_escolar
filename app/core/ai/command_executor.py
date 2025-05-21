"""
Ejecutor de comandos para IA
"""
from typing import Dict, Any, Tuple, Optional
import json

from app.core.service_provider import ServiceProvider
from app.core.commands.alumno_commands import (
    BuscarAlumnoCommand, RegistrarAlumnoCommand,
    ActualizarAlumnoCommand, EliminarAlumnoCommand
)
from app.core.commands.constancia_commands import (
    GenerarConstanciaCommand, TransformarConstanciaCommand,
    ListarConstanciasCommand
)

class CommandExecutor:
    """Ejecutor de comandos para IA"""

    def __init__(self):
        """Inicializa el ejecutor de comandos"""
        self.service_provider = ServiceProvider.get_instance()

    def execute_command(self, command_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Ejecuta un comando a partir de los datos interpretados

        Args:
            command_data: Diccionario con los datos del comando

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Verificar que los datos del comando sean válidos
            if not command_data or not isinstance(command_data, dict):
                return False, "Datos de comando inválidos", {}

            # Obtener la acción y los parámetros
            accion = command_data.get("accion")
            parametros = command_data.get("parametros", {})

            if not accion:
                return False, "No se especificó una acción", {}

            # Ejecutar la acción correspondiente
            if accion == "buscar_alumno":
                return self._ejecutar_buscar_alumno(parametros)
            elif accion == "registrar_alumno":
                return self._ejecutar_registrar_alumno(parametros)
            elif accion == "actualizar_alumno":
                return self._ejecutar_actualizar_alumno(parametros)
            elif accion == "eliminar_alumno":
                return self._ejecutar_eliminar_alumno(parametros)
            elif accion == "generar_constancia":
                return self._ejecutar_generar_constancia(parametros)
            elif accion == "transformar_constancia":
                return self._ejecutar_transformar_constancia(parametros)
            elif accion == "listar_constancias":
                return self._ejecutar_listar_constancias(parametros)
            elif accion == "desconocida":
                mensaje = parametros.get("mensaje", "Acción desconocida")
                return False, f"No se pudo ejecutar el comando: {mensaje}", {}
            else:
                return False, f"Acción no soportada: {accion}", {}

        except Exception as e:
            return False, f"Error al ejecutar el comando: {str(e)}", {}

    def _ejecutar_buscar_alumno(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de búsqueda de alumno"""
        try:
            # Obtener parámetros
            nombre = parametros.get("nombre", "")
            curp = parametros.get("curp", "")
            busqueda_exacta = parametros.get("busqueda_exacta", False)

            # Crear query de búsqueda
            query = curp if curp else nombre

            if not query:
                return False, "Se requiere un nombre o CURP para buscar", {}

            # Crear y ejecutar el comando
            # Si es una CURP, hacemos búsqueda exacta
            if curp:
                command = BuscarAlumnoCommand(query, busqueda_exacta=True)
            else:
                # Para nombres, permitimos búsqueda parcial
                command = BuscarAlumnoCommand(query, busqueda_exacta=busqueda_exacta)

            return command.execute()

        except Exception as e:
            return False, f"Error al buscar alumno: {str(e)}", {}

    def _ejecutar_registrar_alumno(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de registro de alumno"""
        try:
            # Verificar parámetros mínimos
            if not parametros.get("nombre"):
                return False, "Se requiere un nombre para registrar al alumno", {}

            if not parametros.get("curp"):
                return False, "Se requiere una CURP para registrar al alumno", {}

            # Crear y ejecutar el comando
            command = RegistrarAlumnoCommand(parametros)
            return command.execute()

        except Exception as e:
            return False, f"Error al registrar alumno: {str(e)}", {}

    def _ejecutar_actualizar_alumno(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de actualización de alumno"""
        try:
            # Obtener parámetros
            alumno_id = parametros.get("alumno_id")
            datos = parametros.get("datos", {})

            # Verificar parámetros
            if not alumno_id:
                return False, "Se requiere un ID de alumno para actualizar", {}

            if not datos:
                return False, "Se requieren datos para actualizar al alumno", {}

            # Crear y ejecutar el comando
            command = ActualizarAlumnoCommand(alumno_id, datos)
            return command.execute()

        except Exception as e:
            return False, f"Error al actualizar alumno: {str(e)}", {}

    def _ejecutar_eliminar_alumno(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de eliminación de alumno"""
        try:
            # Obtener parámetros
            alumno_id = parametros.get("alumno_id")

            # Verificar parámetros
            if not alumno_id:
                return False, "Se requiere un ID de alumno para eliminar", {}

            # Si el ID es una CURP, buscar el alumno primero
            if isinstance(alumno_id, str) and len(alumno_id) > 10:
                # Probablemente es una CURP
                buscar_command = BuscarAlumnoCommand(alumno_id)
                success, _, data = buscar_command.execute()

                if success and data.get("alumnos"):
                    # Usar el primer alumno encontrado
                    alumno_id = data["alumnos"][0]["id"]
                else:
                    return False, f"No se encontró un alumno con CURP {alumno_id}", {}

            # Crear y ejecutar el comando
            command = EliminarAlumnoCommand(alumno_id)
            return command.execute()

        except Exception as e:
            return False, f"Error al eliminar alumno: {str(e)}", {}

    def _ejecutar_generar_constancia(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de generación de constancia"""
        try:
            # Obtener parámetros
            alumno_id = parametros.get("alumno_id")
            nombre = parametros.get("nombre", "")
            tipo = parametros.get("tipo", "estudio")
            incluir_foto = parametros.get("incluir_foto", False)

            # Si no hay ID pero hay un nombre, buscar el alumno primero
            if not alumno_id and nombre:
                # Intentar búsqueda exacta primero
                buscar_command = BuscarAlumnoCommand(nombre, busqueda_exacta=True)
                success, _, data = buscar_command.execute()

                # Si no hay resultados exactos, intentar búsqueda parcial
                if not success or not data.get("alumnos"):
                    buscar_command = BuscarAlumnoCommand(nombre, busqueda_exacta=False)
                    success, _, data = buscar_command.execute()

                if success and data.get("alumnos"):
                    # Si hay múltiples coincidencias, mostrar información
                    if len(data["alumnos"]) > 1:
                        alumnos_info = []
                        for i, alumno in enumerate(data["alumnos"], 1):
                            alumnos_info.append(f"{i}. {alumno.get('nombre', '')} (ID: {alumno.get('id', '')})")

                        alumnos_str = "\n".join(alumnos_info)
                        return False, f"Se encontraron múltiples alumnos con ese nombre. Por favor, especifica el ID:\n{alumnos_str}", {"alumnos": data["alumnos"]}

                    # Usar el primer alumno encontrado
                    alumno_id = data["alumnos"][0]["id"]
                    alumno_nombre = data["alumnos"][0].get("nombre", "")
                else:
                    return False, f"No se encontró un alumno con nombre '{nombre}'", {}

            # Verificar parámetros
            if not alumno_id:
                return False, "Se requiere un ID o nombre de alumno para generar la constancia", {}

            # Validar tipo de constancia
            tipos_validos = ["estudio", "calificaciones", "traslado"]
            if tipo not in tipos_validos:
                return False, f"Tipo de constancia no válido. Debe ser uno de: {', '.join(tipos_validos)}", {}

            # Crear y ejecutar el comando
            command = GenerarConstanciaCommand(alumno_id, tipo, incluir_foto)
            return command.execute()

        except Exception as e:
            return False, f"Error al generar constancia: {str(e)}", {}

    def _ejecutar_transformar_constancia(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de transformación de constancia"""
        try:
            # Obtener parámetros
            ruta_archivo = parametros.get("ruta_archivo")
            tipo_destino = parametros.get("tipo_destino", "estudio")
            incluir_foto = parametros.get("incluir_foto", False)
            guardar_alumno = parametros.get("guardar_alumno", False)

            # Verificar parámetros
            if not ruta_archivo:
                return False, "Se requiere una ruta de archivo para transformar la constancia", {}

            # Validar tipo de constancia
            tipos_validos = ["estudio", "calificaciones", "traslado"]
            if tipo_destino not in tipos_validos:
                return False, f"Tipo de constancia no válido. Debe ser uno de: {', '.join(tipos_validos)}", {}

            # Crear y ejecutar el comando
            command = TransformarConstanciaCommand(ruta_archivo, tipo_destino, incluir_foto, guardar_alumno)
            return command.execute()

        except Exception as e:
            return False, f"Error al transformar constancia: {str(e)}", {}

    def _ejecutar_listar_constancias(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Ejecuta el comando de listar constancias"""
        try:
            # Obtener parámetros
            alumno_id = parametros.get("alumno_id")
            nombre = parametros.get("nombre", "")

            # Si no hay ID pero hay un nombre, buscar el alumno primero
            if not alumno_id and nombre:
                # Intentar búsqueda exacta primero
                buscar_command = BuscarAlumnoCommand(nombre, busqueda_exacta=True)
                success, _, data = buscar_command.execute()

                # Si no hay resultados exactos, intentar búsqueda parcial
                if not success or not data.get("alumnos"):
                    buscar_command = BuscarAlumnoCommand(nombre, busqueda_exacta=False)
                    success, _, data = buscar_command.execute()

                if success and data.get("alumnos"):
                    # Si hay múltiples coincidencias, mostrar información
                    if len(data["alumnos"]) > 1:
                        alumnos_info = []
                        for i, alumno in enumerate(data["alumnos"], 1):
                            alumnos_info.append(f"{i}. {alumno.get('nombre', '')} (ID: {alumno.get('id', '')})")

                        alumnos_str = "\n".join(alumnos_info)
                        return False, f"Se encontraron múltiples alumnos con ese nombre. Por favor, especifica el ID:\n{alumnos_str}", {"alumnos": data["alumnos"]}

                    # Usar el primer alumno encontrado
                    alumno_id = data["alumnos"][0]["id"]
                else:
                    return False, f"No se encontró un alumno con nombre '{nombre}'", {}

            # Verificar parámetros
            if not alumno_id:
                return False, "Se requiere un ID o nombre de alumno para listar constancias", {}

            # Crear y ejecutar el comando
            command = ListarConstanciasCommand(alumno_id)
            return command.execute()

        except Exception as e:
            return False, f"Error al listar constancias: {str(e)}", {}
