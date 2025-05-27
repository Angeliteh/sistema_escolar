from app.core.pdf_extractor import PDFExtractor
from app.core.pdf_generator import PDFGenerator
from app.services.alumno_service import AlumnoService
from app.services.constancia_service import ConstanciaService
from app.data.models.constancia import Constancia
from app.core.config import Config
from app.core.logging import get_logger
import os
import sys
import json
import sqlite3

# Logger para este módulo
logger = get_logger(__name__)

def mostrar_datos_detallados(datos):
    """Muestra todos los datos extraídos en detalle"""
    print("\n=== DATOS EXTRAÍDOS (DETALLADOS) ===")

    # Convertir a formato JSON para mejor visualización
    datos_json = json.dumps(datos, indent=4, ensure_ascii=False)
    print(datos_json)

    print("\n=== ANÁLISIS DE DATOS CRÍTICOS ===")

    # Verificar datos críticos
    print(f"Nombre: {datos.get('nombre', 'NO ENCONTRADO')} (Tipo: {type(datos.get('nombre', '')).__name__})")
    print(f"CURP: {datos.get('curp', 'NO ENCONTRADO')} (Tipo: {type(datos.get('curp', '')).__name__})")
    print(f"Matrícula: {datos.get('matricula', 'NO ENCONTRADO')} (Tipo: {type(datos.get('matricula', '')).__name__})")

    # Verificar específicamente grado y grupo
    print(f"Grado: {datos.get('grado', 'NO ENCONTRADO')} (Tipo: {type(datos.get('grado', '')).__name__})")
    print(f"Grupo: {datos.get('grupo', 'NO ENCONTRADO')} (Tipo: {type(datos.get('grupo', '')).__name__})")
    print(f"Turno: {datos.get('turno', 'NO ENCONTRADO')} (Tipo: {type(datos.get('turno', '')).__name__})")

    # Verificar calificaciones
    if 'calificaciones' in datos and datos['calificaciones']:
        print("Calificaciones: ENCONTRADAS")
        print(f"Tipo de calificaciones: {type(datos['calificaciones']).__name__}")
        if isinstance(datos['calificaciones'], dict):
            print("Materias encontradas:")
            for materia, calificacion in datos['calificaciones'].items():
                print(f"  - {materia}: {calificacion}")
    else:
        print("Calificaciones: NO ENCONTRADAS")

def simular_guardado_en_db(datos):
    """Simula el proceso de guardado en la base de datos para depuración"""
    print("\n=== SIMULACIÓN DE GUARDADO EN BASE DE DATOS ===")

    # Simular creación de objeto Alumno
    print("Creando objeto Alumno con:")
    print(f"  - curp: {datos.get('curp', 'NO DISPONIBLE')}")
    print(f"  - nombre: {datos.get('nombre', 'NO DISPONIBLE')}")
    print(f"  - matricula: {datos.get('matricula', 'NO DISPONIBLE')}")
    print(f"  - fecha_nacimiento: {datos.get('nacimiento', 'NO DISPONIBLE')}")

    # Simular creación de objeto DatosEscolares
    print("\nCreando objeto DatosEscolares con:")
    print(f"  - grado: {datos.get('grado', 'NO DISPONIBLE')}")
    print(f"  - grupo: {datos.get('grupo', 'NO DISPONIBLE')}")
    print(f"  - turno: {datos.get('turno', 'NO DISPONIBLE')}")
    print(f"  - ciclo_escolar: {datos.get('ciclo', 'NO DISPONIBLE')}")
    print(f"  - escuela: {datos.get('escuela', 'NO DISPONIBLE')}")
    print(f"  - cct: {datos.get('cct', 'NO DISPONIBLE')}")

    # Verificar si los tipos de datos son correctos
    print("\nVerificación de tipos de datos para la base de datos:")

    # Verificar grado (debe ser un entero)
    grado = datos.get('grado')
    if grado is not None:
        try:
            grado_int = int(grado)
            print(f"  - Grado convertido a entero: {grado_int} (OK)")
        except (ValueError, TypeError):
            print(f"  - ERROR: No se puede convertir el grado '{grado}' a entero")
    else:
        print("  - ERROR: Grado no disponible")

    # Verificar grupo (debe ser una cadena)
    grupo = datos.get('grupo')
    if grupo is not None:
        if isinstance(grupo, str):
            print(f"  - Grupo es una cadena: '{grupo}' (OK)")
        else:
            print(f"  - ADVERTENCIA: Grupo no es una cadena, es {type(grupo).__name__}")
    else:
        print("  - ERROR: Grupo no disponible")

def main():
    """Ejecuta el programa en modo consola para depuración"""
    # Verificar argumentos
    if len(sys.argv) < 2:
        logger.info("Uso: python main.py <archivo_pdf> [tipo_constancia] [--con-foto=si|no|auto] [--debug]")
        logger.info("Tipos disponibles: traslado, estudio, calificaciones (por defecto: traslado)")
        logger.info("Opciones:")
        logger.info("  --con-foto=si    Incluir foto en la constancia (si está disponible)")
        logger.info("  --con-foto=no    No incluir foto en la constancia")
        logger.info("  --con-foto=auto  Detectar automáticamente (por defecto)")
        logger.info("  --debug          Mostrar información detallada para depuración")
        logger.info("  --solo-extraer   Solo extraer datos, no generar constancia")
        return

    # Obtener argumentos
    pdf_path = sys.argv[1]

    # Tipo de constancia (opcional, por defecto traslado)
    tipo_constancia = "traslado"
    if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
        tipo_constancia = sys.argv[2]

    # Procesar opciones
    incluir_foto = None  # Auto por defecto
    debug_mode = False
    solo_extraer = False

    for arg in sys.argv[2:]:
        if arg.startswith("--con-foto="):
            opcion_foto = arg.split("=")[1].lower()
            if opcion_foto == "si":
                incluir_foto = True
            elif opcion_foto == "no":
                incluir_foto = False
            elif opcion_foto == "auto":
                incluir_foto = None
            else:
                logger.error(f"Error: Valor no válido para --con-foto. Opciones: si, no, auto")
                return
        elif arg == "--debug":
            debug_mode = True
        elif arg == "--solo-extraer":
            solo_extraer = True

    # Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        logger.error(f"Error: El archivo {pdf_path} no existe")
        return

    # Verificar tipo de constancia
    tipos_validos = ["traslado", "estudio", "calificaciones"]
    if tipo_constancia not in tipos_validos:
        logger.error(f"Error: Tipo de constancia no válido. Opciones: {', '.join(tipos_validos)}")
        return

    # Extraer datos
    logger.info(f"Extrayendo datos de {pdf_path}...")
    extractor = PDFExtractor(pdf_path)

    # Pasar el tipo de constancia solicitado para que se respete en la extracción
    datos = extractor.extraer_todos_datos(incluir_foto, tipo_constancia)

    # Mostrar datos extraídos (versión básica) - Mantener prints para interfaz de consola
    print("\nDatos extraídos (resumen):")
    print(f"Nombre: {datos.get('nombre', '')}")
    print(f"CURP: {datos.get('curp', '')}")
    print(f"Matrícula: {datos.get('matricula', '')}")
    print(f"Grado: {datos.get('grado', '')} Grupo: {datos.get('grupo', '')} Turno: {datos.get('turno', '')}")

    # Mostrar si se incluirán calificaciones
    if datos.get("mostrar_calificaciones", False):
        print("Calificaciones: Se incluirán en la constancia")
    else:
        print("Calificaciones: No se incluirán en la constancia")

    # Mostrar estado de la foto
    if datos.get("has_photo", False):
        print("Foto: Incluida")
    else:
        if incluir_foto is False:
            print("Foto: No incluida (por elección del usuario)")
        else:
            print("Foto: No disponible")

    # Log para debugging interno
    logger.debug(f"Datos extraídos: {datos.keys()}")

    # Si estamos en modo debug, mostrar información detallada
    if debug_mode:
        mostrar_datos_detallados(datos)
        simular_guardado_en_db(datos)

    # Si solo queremos extraer datos, terminamos aquí
    if solo_extraer:
        return

    # Generar constancia
    logger.info(f"Generando constancia de {tipo_constancia}...")
    generator = PDFGenerator()
    output_path = generator.generar_constancia(tipo_constancia, datos)

    if output_path:
        logger.info(f"Constancia generada con éxito: {output_path}")

        # Preguntar si guardar en base de datos
        respuesta = input("\n¿Desea guardar los datos del alumno en la base de datos? (s/n): ")
        if respuesta.lower() == "s":
            # Crear conexión a la base de datos
            conn = sqlite3.connect(Config.DB_PATH)
            conn.row_factory = sqlite3.Row

            # Crear servicios
            alumno_service = AlumnoService(conn)
            constancia_service = ConstanciaService(conn)

            # Guardar alumno y constancia
            try:
                # Preparar datos para registrar alumno
                datos_alumno = {
                    "curp": datos.get('curp', ''),
                    "nombre": datos.get('nombre', ''),
                    "matricula": datos.get('matricula', ''),
                    "fecha_nacimiento": datos.get('nacimiento', ''),
                    "grado": datos.get('grado', 1),
                    "grupo": datos.get('grupo', 'A'),
                    "turno": datos.get('turno', 'MATUTINO'),
                    "ciclo_escolar": datos.get('ciclo', Config.get_current_year()),
                    "escuela": datos.get('escuela', Config.get_school_name()),
                    "cct": datos.get('cct', Config.get_school_cct()),
                    "calificaciones": datos.get('calificaciones', {})
                }

                # Registrar alumno (este método también guarda los datos escolares)
                success, message, alumno = alumno_service.registrar_alumno(datos_alumno)

                if success and alumno and alumno.id:
                    logger.info(f"Alumno registrado correctamente con ID: {alumno.id}")
                    logger.info(f"Mensaje: {message}")

                    # Registrar constancia
                    try:
                        # Crear constancia
                        constancia = Constancia(
                            alumno_id=alumno.id,
                            tipo=tipo_constancia,
                            ruta_archivo=output_path
                        )

                        # Guardar constancia
                        constancia = constancia_service.constancia_repository.save(constancia)

                        if constancia and constancia.id:
                            logger.info(f"Constancia registrada con ID: {constancia.id}")
                            logger.info("Todos los datos guardados correctamente en la base de datos")
                        else:
                            logger.error("Error al registrar la constancia")
                    except Exception as e:
                        logger.error(f"Error al registrar la constancia: {str(e)}")
                else:
                    logger.error(f"Error al registrar el alumno: {message}")

            except Exception as e:
                logger.error(f"Error al guardar en la base de datos: {str(e)}")

            finally:
                # Cerrar conexión
                conn.close()
    else:
        logger.error("Error al generar constancia")

if __name__ == "__main__":
    # Este script ejecuta el modo consola para depuración
    main()
