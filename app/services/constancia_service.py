"""
Servicio para gestión de constancias
"""
import sqlite3
import os
import tempfile
from typing import List, Optional, Dict, Any, Tuple
from app.data.models.alumno import Alumno
from app.data.models.constancia import Constancia
from app.data.models.datos_escolares import DatosEscolares
from app.data.repositories.alumno_repository import AlumnoRepository
from app.data.repositories.constancia_repository import ConstanciaRepository
from app.data.repositories.datos_escolares_repository import DatosEscolaresRepository
from app.core.pdf_extractor import PDFExtractor
from app.core.pdf_generator import PDFGenerator
from app.core.config import Config
from app.core.utils import ensure_directories_exist
from app.core.executable_paths import get_path_manager

class ConstanciaService:
    """Servicio para gestión de constancias"""

    def __init__(self, db_connection=None):
        """
        Inicializa el servicio

        Args:
            db_connection: Conexión a la base de datos (opcional)
        """
        if db_connection:
            self.conn = db_connection
        else:
            # Usar gestor de rutas para obtener la ruta correcta de la BD
            path_manager = get_path_manager()
            db_path = str(path_manager.get_database_path())
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row

        self.alumno_repository = AlumnoRepository(self.conn)
        self.constancia_repository = ConstanciaRepository(self.conn)
        self.datos_escolares_repository = DatosEscolaresRepository(self.conn)
        self.pdf_generator = PDFGenerator()

        # Asegurar que los directorios necesarios existan
        ensure_directories_exist()

    def generar_constancia_desde_pdf(self, pdf_path: str, tipo_constancia: str, incluir_foto: Optional[bool] = None, guardar_alumno: bool = True, preview_mode: bool = False, output_dir: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Genera una constancia a partir de un PDF existente

        Args:
            pdf_path: Ruta al archivo PDF
            tipo_constancia: Tipo de constancia a generar (traslado, estudio, calificaciones)
            incluir_foto: Si se debe incluir la foto del alumno
            guardar_alumno: Si se debe guardar el alumno en la base de datos
            preview_mode: Si es True, genera una vista previa temporal sin guardar en la base de datos
            output_dir: Directorio de salida para la constancia (opcional, solo usado en preview_mode)

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Verificar que el archivo exista
            if not os.path.exists(pdf_path):
                return False, f"El archivo {pdf_path} no existe", None

            # Verificar que el tipo de constancia sea válido
            if tipo_constancia not in ["traslado", "estudio", "calificaciones"]:
                return False, f"Tipo de constancia no válido: {tipo_constancia}", None

            # Extraer datos del PDF
            extractor = PDFExtractor(pdf_path)
            datos = extractor.extraer_todos_datos(incluir_foto=incluir_foto, tipo_constancia_solicitado=tipo_constancia)

            # Verificar que se hayan extraído los datos básicos
            if not datos.get("curp"):
                return False, "No se pudo extraer la CURP del alumno", None

            if not datos.get("nombre"):
                return False, "No se pudo extraer el nombre del alumno", None

            # 🎯 LÓGICA INTELIGENTE DE FOTO (DESDE PDF)
            if incluir_foto is False:
                # Usuario solicita explícitamente NO incluir foto
                datos['has_photo'] = False
                datos['show_placeholder'] = False
            elif incluir_foto is True:
                # Usuario solicita explícitamente incluir foto
                if 'has_photo' in datos and datos['has_photo']:
                    datos['has_photo'] = True
                    datos['show_placeholder'] = True
                else:
                    # Si no hay foto pero se solicitó incluirla, mostrar un espacio para foto
                    datos['has_photo'] = False
                    datos['show_placeholder'] = True
            else:
                # incluir_foto es None - COMPORTAMIENTO AUTOMÁTICO INTELIGENTE
                # ✅ Si existe la foto en el PDF, mostrarla automáticamente
                # ❌ Si no existe, no mostrar nada
                if 'has_photo' in datos and datos['has_photo']:
                    datos['has_photo'] = True
                    datos['show_placeholder'] = True
                else:
                    datos['has_photo'] = False
                    datos['show_placeholder'] = False

            # Buscar o crear alumno si se debe guardar (solo si no estamos en modo vista previa)
            alumno = None
            if not preview_mode and guardar_alumno:
                alumno = self.alumno_repository.get_by_curp(datos["curp"])
                if not alumno:
                    # Crear nuevo alumno con los datos extraídos
                    alumno = Alumno(
                        curp=datos["curp"],
                        nombre=datos["nombre"],
                        matricula=datos.get("matricula"),
                        fecha_nacimiento=datos.get("nacimiento")
                    )
                    alumno = self.alumno_repository.save(alumno)

                # Guardar o actualizar datos escolares si están disponibles
                if datos.get("grado") and datos.get("grupo"):
                    # Verificar si ya existen datos escolares para este alumno
                    datos_escolares_list = self.datos_escolares_repository.get_by_alumno(alumno.id, latest_only=True)

                    # Convertir calificaciones a lista si es necesario
                    calificaciones = datos.get("calificaciones", [])
                    if isinstance(calificaciones, dict):
                        calificaciones_list = []
                        for asignatura, calificacion in calificaciones.items():
                            calificaciones_list.append({
                                "asignatura": asignatura,
                                "calificacion": calificacion
                            })
                        calificaciones = calificaciones_list

                    if datos_escolares_list:
                        # Actualizar datos escolares existentes
                        datos_escolares = datos_escolares_list[0]
                        datos_escolares.ciclo_escolar = datos.get("ciclo", Config.get_current_year())
                        datos_escolares.grado = int(datos.get("grado", 1))
                        datos_escolares.grupo = datos.get("grupo", "A")
                        datos_escolares.turno = datos.get("turno", "MATUTINO")
                        datos_escolares.escuela = datos.get("escuela", Config.get_school_name())
                        datos_escolares.cct = datos.get("cct", Config.get_school_cct())
                        datos_escolares.calificaciones = calificaciones

                        self.datos_escolares_repository.save(datos_escolares)
                    else:
                        # Crear nuevos datos escolares
                        datos_escolares = DatosEscolares(
                            alumno_id=alumno.id,
                            ciclo_escolar=datos.get("ciclo", Config.get_current_year()),
                            grado=int(datos.get("grado", 1)),
                            grupo=datos.get("grupo", "A"),
                            turno=datos.get("turno", "MATUTINO"),
                            escuela=datos.get("escuela", Config.get_school_name()),
                            cct=datos.get("cct", Config.get_school_cct()),
                            calificaciones=calificaciones
                        )

                        self.datos_escolares_repository.save(datos_escolares)

            # Generar constancia
            if preview_mode and output_dir:
                # En modo vista previa, usar el directorio temporal proporcionado
                output_path = self.pdf_generator.generar_constancia(
                    tipo_constancia,
                    datos,
                    output_dir=output_dir,
                    filename_prefix="preview_"
                )
            else:
                # Generación normal
                output_path = self.pdf_generator.generar_constancia(tipo_constancia, datos)

            if not output_path:
                return False, "Error al generar la constancia", None

            # Registrar constancia en la base de datos si se debe guardar (solo si no estamos en modo vista previa)
            constancia = None
            if not preview_mode and guardar_alumno and alumno:
                constancia = Constancia(
                    alumno_id=alumno.id,
                    tipo=tipo_constancia,
                    ruta_archivo=output_path
                )
                constancia = self.constancia_repository.save(constancia)

            result_data = {
                "ruta_archivo": output_path
            }

            if alumno:
                result_data["alumno"] = alumno.to_dict()

            if constancia:
                result_data["constancia"] = constancia.to_dict()

            return True, "Constancia generada correctamente", result_data

        except Exception as e:
            return False, f"Error al generar constancia: {str(e)}", None

    def generar_constancia_para_alumno(self, alumno_id: int, tipo_constancia: str, incluir_foto: Optional[bool] = None, preview_mode: bool = False) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Genera una constancia para un alumno existente

        Args:
            alumno_id: ID del alumno
            tipo_constancia: Tipo de constancia a generar (traslado, estudio, calificaciones)
            incluir_foto: Si se debe incluir la foto del alumno
            preview_mode: Si es True, genera una vista previa temporal sin guardar en la base de datos

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Verificar que el tipo de constancia sea válido
            if tipo_constancia not in ["traslado", "estudio", "calificaciones"]:
                return False, f"Tipo de constancia no válido: {tipo_constancia}", None

            # Obtener alumno
            alumno = self.alumno_repository.get_by_id(alumno_id)
            if not alumno:
                return False, f"No se encontró un alumno con ID {alumno_id}", None

            # Obtener datos escolares más recientes
            datos_escolares_list = self.datos_escolares_repository.get_by_alumno(alumno_id, latest_only=True)

            # Para constancias de calificaciones o traslado, necesitamos datos escolares con calificaciones
            if tipo_constancia in ["calificaciones", "traslado"]:
                if not datos_escolares_list:
                    return False, f"No se encontraron datos escolares para el alumno con ID {alumno_id}", {
                        "alumno": alumno.to_dict(),
                        "error_tipo": "datos_escolares_faltantes"
                    }

                # Verificar que haya calificaciones
                datos_escolares = datos_escolares_list[0]
                if not datos_escolares.calificaciones or len(datos_escolares.calificaciones) == 0:
                    return False, f"El alumno no tiene calificaciones registradas, necesarias para constancias de {tipo_constancia}", {
                        "alumno": alumno.to_dict(),
                        "error_tipo": "calificaciones_faltantes"
                    }

            # Para otros tipos de constancias, podemos continuar con datos mínimos
            datos_escolares = None
            if datos_escolares_list:
                datos_escolares = datos_escolares_list[0]

            # Preparar datos para la constancia
            datos = {
                "curp": alumno.curp,
                "nombre": alumno.nombre,
                "matricula": alumno.matricula,
                "nacimiento": alumno.fecha_nacimiento,
                "mostrar_calificaciones": tipo_constancia in ["traslado", "calificaciones"],
                "has_photo": False  # Por defecto, no incluir foto
            }

            # Añadir datos escolares si están disponibles
            if datos_escolares:
                datos.update({
                    "grado": datos_escolares.grado,
                    "grupo": datos_escolares.grupo,
                    "turno": datos_escolares.turno,
                    "ciclo": datos_escolares.ciclo_escolar,
                    "escuela": datos_escolares.escuela or Config.get_school_name(),
                    "cct": datos_escolares.cct or Config.get_school_cct(),
                    "calificaciones": datos_escolares.calificaciones,
                    "tiene_calificaciones": bool(datos_escolares.calificaciones and len(datos_escolares.calificaciones) > 0)
                })
            else:
                # Valores predeterminados para datos escolares
                datos.update({
                    "grado": "",
                    "grupo": "",
                    "turno": "MATUTINO",
                    "ciclo": Config.get_current_year(),
                    "escuela": Config.get_school_name(),
                    "cct": Config.get_school_cct(),
                    "calificaciones": [],
                    "tiene_calificaciones": False
                })

            # Verificar si hay foto y si se debe incluir
            path_manager = get_path_manager()
            photos_dir = path_manager.get_photos_dir()
            foto_path = photos_dir / f"{alumno.curp}.jpg"

            # 🎯 LÓGICA INTELIGENTE DE FOTO
            if incluir_foto is False:
                # Usuario solicita explícitamente NO incluir foto
                datos["has_photo"] = False
                datos["show_placeholder"] = False
                # No asignar foto_path para asegurar que no se muestre
                if "foto_path" in datos:
                    del datos["foto_path"]
            elif incluir_foto is True:
                # Usuario solicita explícitamente incluir foto
                if foto_path.exists():
                    datos["has_photo"] = True
                    datos["foto_path"] = str(foto_path)
                    datos["show_placeholder"] = True
                else:
                    # Si no hay foto pero se solicitó incluirla, mostrar un espacio para foto
                    datos["has_photo"] = False
                    datos["show_placeholder"] = True
            else:
                # incluir_foto es None - COMPORTAMIENTO AUTOMÁTICO INTELIGENTE
                # ✅ Si existe la foto, mostrarla automáticamente
                # ❌ Si no existe, no mostrar nada
                if foto_path.exists():
                    datos["has_photo"] = True
                    datos["foto_path"] = str(foto_path)
                    datos["show_placeholder"] = True
                else:
                    datos["has_photo"] = False
                    datos["show_placeholder"] = False

            # Generar constancia
            if preview_mode:
                # Crear un directorio temporal para la vista previa
                temp_dir = tempfile.mkdtemp(prefix="constancia_preview_")
                output_path = self.pdf_generator.generar_constancia(
                    tipo_constancia,
                    datos,
                    output_dir=temp_dir,
                    filename_prefix="preview_"
                )

                # 🔧 OBTENER DATOS COMPLETOS DEL ALUMNO (incluyendo datos escolares)
                from app.services.alumno_service import AlumnoService
                alumno_service = AlumnoService(self.conn)
                alumno_completo = alumno_service.get_alumno(alumno.id)

                # No guardar en la base de datos, solo devolver la ruta
                return True, "Vista previa generada correctamente", {
                    "alumno": alumno_completo or alumno.to_dict(),  # ✅ Datos completos con escolares
                    "ruta_archivo": output_path
                }
            else:
                # Generar constancia normal
                output_path = self.pdf_generator.generar_constancia(tipo_constancia, datos)

                if not output_path:
                    return False, "Error al generar la constancia", None

                # Registrar constancia en la base de datos
                constancia = Constancia(
                    alumno_id=alumno.id,
                    tipo=tipo_constancia,
                    ruta_archivo=output_path
                )
                constancia = self.constancia_repository.save(constancia)

                # 🔧 OBTENER DATOS COMPLETOS DEL ALUMNO (incluyendo datos escolares)
                from app.services.alumno_service import AlumnoService
                alumno_service = AlumnoService(self.conn)
                alumno_completo = alumno_service.get_alumno(alumno.id)

                return True, "Constancia generada correctamente", {
                    "alumno": alumno_completo or alumno.to_dict(),  # ✅ Datos completos con escolares
                    "constancia": constancia.to_dict(),
                    "ruta_archivo": output_path
                }

        except Exception as e:
            return False, f"Error al generar constancia: {str(e)}", None

    def obtener_constancias_alumno(self, alumno_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene las constancias de un alumno

        Args:
            alumno_id: ID del alumno

        Returns:
            Lista de diccionarios con los datos de las constancias
        """
        constancias = self.constancia_repository.get_by_alumno(alumno_id)
        return [constancia.to_dict() for constancia in constancias]

    def obtener_constancias_recientes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene las constancias más recientes

        Args:
            limit: Límite de resultados

        Returns:
            Lista de diccionarios con los datos de las constancias
        """
        constancias = self.constancia_repository.list_recent(limit)

        result = []
        for constancia in constancias:
            # Obtener datos del alumno
            alumno = self.alumno_repository.get_by_id(constancia.alumno_id)
            if alumno:
                constancia_dict = constancia.to_dict()
                constancia_dict["alumno_nombre"] = alumno.nombre
                constancia_dict["alumno_curp"] = alumno.curp
                result.append(constancia_dict)

        return result

    def eliminar_constancia(self, constancia_id: int) -> Tuple[bool, str]:
        """
        Elimina una constancia

        Args:
            constancia_id: ID de la constancia

        Returns:
            Tupla con (éxito, mensaje)
        """
        # Obtener constancia
        constancia = self.constancia_repository.get_by_id(constancia_id)
        if not constancia:
            return False, f"No se encontró una constancia con ID {constancia_id}"

        try:
            # Eliminar archivo si existe
            if constancia.ruta_archivo and os.path.exists(constancia.ruta_archivo):
                os.remove(constancia.ruta_archivo)

            # Eliminar constancia de la base de datos
            if self.constancia_repository.delete(constancia_id):
                return True, "Constancia eliminada correctamente"
            else:
                return False, "No se pudo eliminar la constancia"

        except Exception as e:
            return False, f"Error al eliminar constancia: {str(e)}"

    def guardar_alumno_desde_pdf(self, pdf_path: str, incluir_foto: Optional[bool] = None, datos_override: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Guarda los datos de un alumno desde un PDF sin generar una constancia

        Args:
            pdf_path: Ruta al archivo PDF
            incluir_foto: Si se debe incluir la foto del alumno

        Returns:
            Tupla con (éxito, mensaje, datos)
        """
        try:
            # Verificar que el archivo exista
            if not os.path.exists(pdf_path):
                return False, f"El archivo {pdf_path} no existe", None

            # Si se proporcionaron datos personalizados, usarlos
            if datos_override:
                datos = datos_override
            else:
                # Extraer datos del PDF
                extractor = PDFExtractor(pdf_path)
                datos = extractor.extraer_todos_datos(incluir_foto=incluir_foto)

            # Verificar que se tengan los datos básicos
            if not datos.get("curp"):
                return False, "No se pudo obtener la CURP del alumno", None

            if not datos.get("nombre"):
                return False, "No se pudo obtener el nombre del alumno", None

            # Buscar si el alumno ya existe
            alumno = self.alumno_repository.get_by_curp(datos["curp"])

            if alumno:
                # Actualizar datos del alumno existente
                alumno.nombre = datos["nombre"]
                if datos.get("matricula"):
                    alumno.matricula = datos["matricula"]
                if datos.get("nacimiento"):
                    alumno.fecha_nacimiento = datos["nacimiento"]

                alumno = self.alumno_repository.update(alumno)
                mensaje = f"Datos del alumno {alumno.nombre} actualizados correctamente"
            else:
                # Crear nuevo alumno con los datos extraídos
                alumno = Alumno(
                    curp=datos["curp"],
                    nombre=datos["nombre"],
                    matricula=datos.get("matricula"),
                    fecha_nacimiento=datos.get("nacimiento")
                )
                alumno = self.alumno_repository.save(alumno)
                mensaje = f"Alumno {alumno.nombre} registrado correctamente"

            # Guardar o actualizar datos escolares si están disponibles
            if datos.get("grado") and datos.get("grupo"):
                # Verificar si ya existen datos escolares para este alumno
                datos_escolares_list = self.datos_escolares_repository.get_by_alumno(alumno.id, latest_only=True)

                # Asegurarse de que las calificaciones sean una lista válida
                calificaciones = datos.get("calificaciones", [])

                # Verificar si hay calificaciones pero están vacías o son None
                if not calificaciones and "tiene_calificaciones" in datos and datos["tiene_calificaciones"]:
                    # Intentar extraer calificaciones nuevamente
                    try:
                        extractor = PDFExtractor(pdf_path)
                        calificaciones = extractor.extraer_calificaciones()
                        print(f"Calificaciones extraídas nuevamente: {calificaciones}")
                    except Exception as e:
                        print(f"Error al extraer calificaciones: {e}")

                # Convertir calificaciones a lista si es necesario
                if isinstance(calificaciones, dict):
                    calificaciones_list = []
                    for asignatura, calificacion in calificaciones.items():
                        calificaciones_list.append({
                            "asignatura": asignatura,
                            "calificacion": calificacion
                        })
                    calificaciones = calificaciones_list

                # Asegurarse de que calificaciones sea una lista (no None o cadena vacía)
                if calificaciones is None:
                    calificaciones = []

                if datos_escolares_list:
                    # Actualizar datos escolares existentes
                    datos_escolares = datos_escolares_list[0]
                    datos_escolares.ciclo_escolar = datos.get("ciclo", Config.get_current_year())
                    datos_escolares.grado = int(datos.get("grado", 1))
                    datos_escolares.grupo = datos.get("grupo", "A")
                    datos_escolares.turno = datos.get("turno", "MATUTINO")
                    datos_escolares.escuela = datos.get("escuela", Config.get_school_name())
                    datos_escolares.cct = datos.get("cct", Config.get_school_cct())
                    datos_escolares.calificaciones = calificaciones

                    self.datos_escolares_repository.save(datos_escolares)
                    mensaje += " y sus datos escolares han sido actualizados"
                else:
                    # Crear nuevos datos escolares
                    datos_escolares = DatosEscolares(
                        alumno_id=alumno.id,
                        ciclo_escolar=datos.get("ciclo", Config.get_current_year()),
                        grado=int(datos.get("grado", 1)),
                        grupo=datos.get("grupo", "A"),
                        turno=datos.get("turno", "MATUTINO"),
                        escuela=datos.get("escuela", Config.get_school_name()),
                        cct=datos.get("cct", Config.get_school_cct()),
                        calificaciones=calificaciones
                    )

                    self.datos_escolares_repository.save(datos_escolares)
                    mensaje += " y sus datos escolares han sido registrados"

            # Manejar la foto si está disponible
            if incluir_foto and 'has_photo' in datos and datos['has_photo'] and 'foto_path' in datos:
                foto_origen = datos['foto_path']
                foto_destino = os.path.join(Config.PHOTOS_DIR, f"{alumno.curp}.jpg")

                # Copiar la foto al directorio de fotos
                from app.core.utils import copy_file_safely
                copy_file_safely(foto_origen, foto_destino)

            result_data = {
                "alumno": alumno.to_dict()
            }

            return True, mensaje, result_data

        except Exception as e:
            return False, f"Error al guardar datos del alumno: {str(e)}", None

    def close(self):
        """Cierra la conexión a la base de datos si es propia, no si es compartida"""
        # Solo cerrar la conexión si fue creada por este servicio (no compartida)
        if self.conn and not hasattr(self, 'shared_connection'):
            self.conn.close()
