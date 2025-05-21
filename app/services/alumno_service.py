"""
Servicio para gestión de alumnos
"""
import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from app.data.models.alumno import Alumno
from app.data.models.datos_escolares import DatosEscolares
from app.data.repositories.alumno_repository import AlumnoRepository
from app.data.repositories.datos_escolares_repository import DatosEscolaresRepository
from app.data.repositories.constancia_repository import ConstanciaRepository
from app.core.config import Config
from app.core.utils import format_curp, format_name, is_valid_curp

class AlumnoService:
    """Servicio para gestión de alumnos"""

    def __init__(self, db_connection=None):
        """
        Inicializa el servicio

        Args:
            db_connection: Conexión a la base de datos (opcional)
        """
        if db_connection:
            self.conn = db_connection
        else:
            self.conn = sqlite3.connect(Config.DB_PATH)
            self.conn.row_factory = sqlite3.Row

        self.alumno_repository = AlumnoRepository(self.conn)
        self.datos_escolares_repository = DatosEscolaresRepository(self.conn)
        self.constancia_repository = ConstanciaRepository(self.conn)

    def get_alumno(self, alumno_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un alumno con sus datos escolares

        Args:
            alumno_id: ID del alumno

        Returns:
            Diccionario con los datos del alumno y sus datos escolares
        """
        alumno = self.alumno_repository.get_by_id(alumno_id)
        if not alumno:
            return None

        # Obtener datos escolares más recientes
        datos_escolares = self.datos_escolares_repository.get_by_alumno(alumno_id, latest_only=True)

        result = alumno.to_dict()
        if datos_escolares:
            result.update(datos_escolares[0].to_dict())

        return result

    def get_alumno_by_curp(self, curp: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un alumno por su CURP

        Args:
            curp: CURP del alumno

        Returns:
            Diccionario con los datos del alumno y sus datos escolares
        """
        # Formatear CURP
        curp = format_curp(curp)

        alumno = self.alumno_repository.get_by_curp(curp)
        if not alumno:
            return None

        # Obtener datos escolares más recientes
        datos_escolares = self.datos_escolares_repository.get_by_alumno(alumno.id, latest_only=True)

        result = alumno.to_dict()
        if datos_escolares:
            result.update(datos_escolares[0].to_dict())

        return result

    def registrar_alumno(self, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[Alumno]]:
        """
        Registra un nuevo alumno

        Args:
            datos: Diccionario con los datos del alumno

        Returns:
            Tupla con (éxito, mensaje, alumno)
        """
        # Validar datos
        if not datos.get("curp"):
            return False, "La CURP es obligatoria", None

        if not datos.get("nombre"):
            return False, "El nombre es obligatorio", None

        # Formatear datos
        curp = format_curp(datos.get("curp", ""))
        nombre = format_name(datos.get("nombre", ""))

        # Validar CURP
        if not is_valid_curp(curp):
            return False, "La CURP no tiene un formato válido", None

        # Verificar si ya existe un alumno con esa CURP
        alumno_existente = self.alumno_repository.get_by_curp(curp)
        if alumno_existente:
            return False, f"Ya existe un alumno con la CURP {curp}", alumno_existente

        try:
            # Crear alumno
            alumno = Alumno(
                curp=curp,
                nombre=nombre,
                matricula=datos.get("matricula"),
                fecha_nacimiento=datos.get("fecha_nacimiento")
            )

            # Guardar alumno
            alumno = self.alumno_repository.save(alumno)

            # Si hay datos escolares, guardarlos
            if datos.get("grado") and datos.get("grupo"):
                datos_escolares = DatosEscolares(
                    alumno_id=alumno.id,
                    ciclo_escolar=datos.get("ciclo_escolar", Config.CURRENT_SCHOOL_YEAR),
                    grado=int(datos.get("grado", 1)),
                    grupo=datos.get("grupo", "A"),
                    turno=datos.get("turno", "MATUTINO"),
                    escuela=datos.get("escuela", Config.SCHOOL_NAME),
                    cct=datos.get("cct", Config.SCHOOL_CCT),
                    calificaciones=datos.get("calificaciones", [])
                )

                self.datos_escolares_repository.save(datos_escolares)

            return True, "Alumno registrado correctamente", alumno

        except Exception as e:
            return False, f"Error al registrar alumno: {str(e)}", None

    def actualizar_alumno_datos(self, alumno_id: int, datos: Dict[str, Any]) -> Tuple[bool, str, Optional[Alumno]]:
        """
        Actualiza los datos de un alumno

        Args:
            alumno_id: ID del alumno
            datos: Diccionario con los datos a actualizar

        Returns:
            Tupla con (éxito, mensaje, alumno)
        """
        # Obtener alumno
        alumno = self.alumno_repository.get_by_id(alumno_id)
        if not alumno:
            return False, f"No se encontró un alumno con ID {alumno_id}", None

        try:
            # Actualizar datos del alumno
            if "nombre" in datos:
                alumno.nombre = format_name(datos["nombre"])

            if "curp" in datos:
                curp = format_curp(datos["curp"])
                if not is_valid_curp(curp):
                    return False, "La CURP no tiene un formato válido", alumno

                # Verificar si ya existe otro alumno con esa CURP
                otro_alumno = self.alumno_repository.get_by_curp(curp)
                if otro_alumno and otro_alumno.id != alumno_id:
                    return False, f"Ya existe otro alumno con la CURP {curp}", alumno

                alumno.curp = curp

            if "matricula" in datos:
                alumno.matricula = datos["matricula"]

            if "fecha_nacimiento" in datos:
                alumno.fecha_nacimiento = datos["fecha_nacimiento"]

            # Guardar alumno
            alumno = self.alumno_repository.save(alumno)

            # Si hay datos escolares, actualizarlos o crear nuevos
            if any(key in datos for key in ["grado", "grupo", "ciclo_escolar", "turno"]):
                # Obtener datos escolares más recientes
                datos_escolares_list = self.datos_escolares_repository.get_by_alumno(alumno_id, latest_only=True)

                if datos_escolares_list:
                    datos_escolares = datos_escolares_list[0]

                    # Actualizar datos escolares
                    if "grado" in datos:
                        datos_escolares.grado = int(datos["grado"])

                    if "grupo" in datos:
                        datos_escolares.grupo = datos["grupo"]

                    if "ciclo_escolar" in datos:
                        datos_escolares.ciclo_escolar = datos["ciclo_escolar"]

                    if "turno" in datos:
                        datos_escolares.turno = datos["turno"]

                    if "escuela" in datos:
                        datos_escolares.escuela = datos["escuela"]

                    if "cct" in datos:
                        datos_escolares.cct = datos["cct"]

                    if "calificaciones" in datos:
                        datos_escolares.calificaciones = datos["calificaciones"]

                    self.datos_escolares_repository.save(datos_escolares)
                else:
                    # Crear nuevos datos escolares
                    datos_escolares = DatosEscolares(
                        alumno_id=alumno.id,
                        ciclo_escolar=datos.get("ciclo_escolar", Config.CURRENT_SCHOOL_YEAR),
                        grado=int(datos.get("grado", 1)),
                        grupo=datos.get("grupo", "A"),
                        turno=datos.get("turno", "MATUTINO"),
                        escuela=datos.get("escuela", Config.SCHOOL_NAME),
                        cct=datos.get("cct", Config.SCHOOL_CCT),
                        calificaciones=datos.get("calificaciones", [])
                    )

                    self.datos_escolares_repository.save(datos_escolares)

            return True, "Alumno actualizado correctamente", alumno

        except Exception as e:
            return False, f"Error al actualizar alumno: {str(e)}", None

    def eliminar_alumno(self, alumno_id: int) -> Tuple[bool, str]:
        """
        Elimina un alumno

        Args:
            alumno_id: ID del alumno

        Returns:
            Tupla con (éxito, mensaje)
        """
        # Obtener alumno
        alumno = self.alumno_repository.get_by_id(alumno_id)
        if not alumno:
            return False, f"No se encontró un alumno con ID {alumno_id}"

        try:
            # Primero, eliminar los datos escolares asociados
            self.datos_escolares_repository.delete_by_alumno(alumno_id)

            # Luego, eliminar las constancias asociadas
            self.constancia_repository.delete_by_alumno(alumno_id)

            # Finalmente, eliminar el alumno
            if self.alumno_repository.delete(alumno_id):
                return True, "Alumno y todos sus datos asociados eliminados correctamente"
            else:
                return False, "No se pudo eliminar el alumno"

        except Exception as e:
            return False, f"Error al eliminar alumno: {str(e)}"

    def buscar_alumnos(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Busca alumnos por nombre o CURP

        Args:
            query: Texto a buscar
            limit: Límite de resultados

        Returns:
            Lista de diccionarios con los datos de los alumnos
        """
        alumnos = self.alumno_repository.search(query, limit)

        result = []
        for alumno in alumnos:
            # Obtener datos escolares más recientes
            datos_escolares = self.datos_escolares_repository.get_by_alumno(alumno.id, latest_only=True)

            alumno_dict = alumno.to_dict()
            if datos_escolares:
                alumno_dict.update({
                    "ciclo_escolar": datos_escolares[0].ciclo_escolar,
                    "grado": datos_escolares[0].grado,
                    "grupo": datos_escolares[0].grupo,
                    "turno": datos_escolares[0].turno
                })

            result.append(alumno_dict)

        return result

    def listar_alumnos(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Lista todos los alumnos

        Args:
            limit: Límite de resultados
            offset: Desplazamiento para paginación

        Returns:
            Lista de diccionarios con los datos de los alumnos
        """
        alumnos = self.alumno_repository.list_all(limit, offset)

        result = []
        for alumno in alumnos:
            # Obtener datos escolares más recientes
            datos_escolares = self.datos_escolares_repository.get_by_alumno(alumno.id, latest_only=True)

            alumno_dict = alumno.to_dict()
            if datos_escolares:
                alumno_dict.update({
                    "ciclo_escolar": datos_escolares[0].ciclo_escolar,
                    "grado": datos_escolares[0].grado,
                    "grupo": datos_escolares[0].grupo,
                    "turno": datos_escolares[0].turno
                })

            result.append(alumno_dict)

        return result

    def get_alumno_by_id(self, alumno_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un alumno por su ID con todos sus datos

        Args:
            alumno_id: ID del alumno

        Returns:
            Diccionario con todos los datos del alumno
        """
        # Obtener datos básicos del alumno
        alumno = self.alumno_repository.get_by_id(alumno_id)
        if not alumno:
            return None

        # Obtener datos escolares más recientes
        datos_escolares = self.datos_escolares_repository.get_by_alumno(alumno_id, latest_only=True)

        # Crear diccionario con todos los datos
        result = alumno.to_dict()

        # Añadir datos escolares si existen
        if datos_escolares:
            datos_dict = datos_escolares[0].to_dict()
            # Eliminar campos redundantes
            if 'id' in datos_dict:
                del datos_dict['id']
            if 'alumno_id' in datos_dict:
                del datos_dict['alumno_id']

            result.update(datos_dict)

        return result

    def get_constancias_by_alumno_id(self, alumno_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene todas las constancias generadas para un alumno

        Args:
            alumno_id: ID del alumno

        Returns:
            Lista de constancias generadas
        """
        constancias = self.constancia_repository.get_by_alumno(alumno_id)
        return [c.to_dict() for c in constancias]

    def actualizar_alumno(self, alumno_id: int, datos_personales: Dict[str, Any], datos_escolares: Dict[str, Any] = None) -> bool:
        """
        Actualiza los datos de un alumno y sus datos escolares

        Args:
            alumno_id: ID del alumno
            datos_personales: Diccionario con los datos personales a actualizar
            datos_escolares: Diccionario con los datos escolares a actualizar

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Actualizar datos personales
            success, _, _ = self.actualizar_alumno_datos(alumno_id, datos_personales)
            if not success:
                return False

            # Si hay datos escolares, actualizarlos
            if datos_escolares:
                # Obtener datos escolares más recientes
                datos_escolares_list = self.datos_escolares_repository.get_by_alumno(alumno_id, latest_only=True)

                if datos_escolares_list:
                    # Actualizar datos escolares existentes
                    datos_esc = datos_escolares_list[0]

                    if 'grado' in datos_escolares and datos_escolares['grado']:
                        datos_esc.grado = int(datos_escolares['grado'])

                    if 'grupo' in datos_escolares and datos_escolares['grupo']:
                        datos_esc.grupo = datos_escolares['grupo']

                    if 'turno' in datos_escolares and datos_escolares['turno']:
                        datos_esc.turno = datos_escolares['turno']

                    if 'ciclo_escolar' in datos_escolares and datos_escolares['ciclo_escolar']:
                        datos_esc.ciclo_escolar = datos_escolares['ciclo_escolar']

                    if 'escuela' in datos_escolares and datos_escolares['escuela']:
                        datos_esc.escuela = datos_escolares['escuela']

                    if 'cct' in datos_escolares and datos_escolares['cct']:
                        datos_esc.cct = datos_escolares['cct']

                    self.datos_escolares_repository.save(datos_esc)
                else:
                    # Crear nuevos datos escolares
                    datos_esc = DatosEscolares(
                        alumno_id=alumno_id,
                        ciclo_escolar=datos_escolares.get('ciclo_escolar', Config.CURRENT_SCHOOL_YEAR),
                        grado=int(datos_escolares.get('grado', 1)),
                        grupo=datos_escolares.get('grupo', 'A'),
                        turno=datos_escolares.get('turno', 'MATUTINO'),
                        escuela=datos_escolares.get('escuela', Config.SCHOOL_NAME),
                        cct=datos_escolares.get('cct', Config.SCHOOL_CCT)
                    )

                    self.datos_escolares_repository.save(datos_esc)

            return True

        except Exception as e:
            print(f"Error al actualizar alumno: {e}")
            return False

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
