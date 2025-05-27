from jinja2 import FileSystemLoader, Environment
import os
from datetime import datetime
import subprocess
import tempfile
import platform
from app.core.config import Config
from app.core.utils import ensure_directories_exist, copy_file_safely
from app.core.logging import get_logger

class PDFGenerator:
    """
    Clase para generar diferentes tipos de constancias en PDF
    usando wkhtmltopdf
    """

    def __init__(self, template_dir=None):
        """Inicializa el generador con el directorio de plantillas"""
        self.template_dir = template_dir or Config.TEMPLATES_DIR
        self.output_dir = Config.OUTPUT_DIR

        # Inicializar logger
        self.logger = get_logger(__name__)

        # Crear directorio de salida si no existe
        ensure_directories_exist()

        # Configurar entorno Jinja2
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

        # Verificar si wkhtmltopdf está instalado
        self.wkhtmltopdf_path = self._find_wkhtmltopdf()

    def _find_wkhtmltopdf(self):
        """Busca la ruta al ejecutable wkhtmltopdf"""
        # Rutas comunes donde podría estar instalado wkhtmltopdf
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
                r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
                # Ubicaciones adicionales comunes en Windows
                r"C:\wkhtmltopdf\bin\wkhtmltopdf.exe",
                r"C:\wkhtmltopdf\wkhtmltopdf.exe",
                # Buscar en el directorio actual
                os.path.join(os.getcwd(), "wkhtmltopdf.exe"),
                os.path.join(os.getcwd(), "bin", "wkhtmltopdf.exe"),
                # Si está en el PATH
                r"wkhtmltopdf.exe"
            ]
        else:
            paths = [
                "/usr/bin/wkhtmltopdf",
                "/usr/local/bin/wkhtmltopdf",
                "wkhtmltopdf"  # Si está en el PATH
            ]

        # Verificar cada ruta
        for path in paths:
            try:
                # Intentar ejecutar wkhtmltopdf con la opción --version
                print(f"Verificando wkhtmltopdf en: {path}")
                result = subprocess.run([path, "--version"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               check=False)  # Cambiado a False para no lanzar excepción

                if result.returncode == 0:
                    print(f"wkhtmltopdf encontrado en: {path}")
                    self.logger.info(f"wkhtmltopdf encontrado en: {path}")
                    return path
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                self.logger.debug(f"No se encontró wkhtmltopdf en: {path} - Error: {str(e)}")
                continue

        # Si no se encuentra, devolver None
        self.logger.warning("No se encontró wkhtmltopdf en ninguna ubicación. Solo se generarán archivos HTML.")
        return None

    def generar_constancia(self, tipo_constancia, datos, output_path=None, output_dir=None, filename_prefix=""):
        """
        Genera una constancia del tipo especificado con los datos proporcionados

        Args:
            tipo_constancia: Tipo de constancia a generar (traslado, estudio, calificaciones)
            datos: Diccionario con los datos a incluir en la constancia
            output_path: Ruta personalizada donde guardar el PDF (opcional)
            output_dir: Directorio personalizado donde guardar el PDF (opcional)
            filename_prefix: Prefijo para el nombre del archivo (opcional)

        Returns:
            Ruta al archivo PDF generado
        """

        # Seleccionar la plantilla adecuada
        template_file = f"constancia_{tipo_constancia}.html"

        # Configurar mostrar_calificaciones según el tipo de constancia
        if tipo_constancia == "estudio":
            # Para constancia de estudios, NUNCA incluir calificaciones
            datos["mostrar_calificaciones"] = False
            datos["calificaciones"] = []  # Vaciar las calificaciones para asegurarnos

        elif tipo_constancia in ["calificaciones", "traslado"]:
            # Verificar si se debe mostrar calificaciones (respetando el valor que viene de la interfaz)
            if "mostrar_calificaciones" not in datos:
                # Si no se especificó, verificar si hay calificaciones disponibles
                if "tiene_calificaciones" in datos:
                    datos["mostrar_calificaciones"] = datos["tiene_calificaciones"]
                else:
                    # Si no se especificó si tiene calificaciones, verificar si hay calificaciones en los datos
                    datos["mostrar_calificaciones"] = "calificaciones" in datos and datos["calificaciones"] and len(datos["calificaciones"]) > 0

            # Asegurarse de que haya una lista de calificaciones (aunque sea vacía)
            if "calificaciones" not in datos:
                datos["calificaciones"] = []

        try:
            # Cargar la plantilla
            try:
                template = self.env.get_template(template_file)
            except Exception as e:
                print(f"Error al cargar la plantilla {template_file}: {str(e)}")
                return None

            # Renderizar HTML
            try:
                html_out = template.render(**datos)
            except Exception as e:
                print(f"Error al renderizar HTML con los datos proporcionados: {str(e)}")
                return None

            # Generar nombre de archivo de salida
            curp = datos.get("curp", "sin_curp")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Determinar el directorio de salida
            output_directory = output_dir if output_dir else self.output_dir

            # Usar la ruta personalizada si se proporciona, de lo contrario generar una
            if output_path:
                output_filename = output_path
            else:
                output_filename = os.path.join(
                    output_directory,
                    f"{filename_prefix}constancia_{tipo_constancia}_{curp}_{timestamp}.pdf"
                )

            # Crear un archivo HTML temporal (que se eliminará después)
            html_output_filename = os.path.join(
                tempfile.gettempdir(),
                f"{filename_prefix}constancia_{tipo_constancia}_{curp}_{timestamp}.html"
            )

            # Crear carpetas para imágenes en la carpeta de salida
            salida_logos_dir = os.path.join(output_directory, "logos")
            salida_fotos_dir = os.path.join(output_directory, "fotos")
            try:
                os.makedirs(salida_logos_dir, exist_ok=True)
                os.makedirs(salida_fotos_dir, exist_ok=True)
            except Exception as e:
                print(f"Error al crear directorios para imágenes: {str(e)}")
                # Continuar a pesar del error

            # Copiar el logo si existe
            logo_origen = os.path.join(Config.LOGOS_DIR, "logo_educacion.png")
            logo_destino = os.path.join(salida_logos_dir, "logo_educacion.png")
            if os.path.exists(logo_origen):
                copy_file_safely(logo_origen, logo_destino)

            # Copiar la foto del alumno si existe
            foto_origen = os.path.join(Config.PHOTOS_DIR, f"{curp}.jpg")
            foto_destino = os.path.join(salida_fotos_dir, f"{curp}.jpg")
            if os.path.exists(foto_origen):
                copy_file_safely(foto_origen, foto_destino)

            # Modificar el HTML para usar rutas absolutas para las imágenes en la vista del navegador
            # Usar rutas absolutas para los directorios de salida
            output_logos_dir = os.path.abspath(salida_logos_dir)
            output_fotos_dir = os.path.abspath(salida_fotos_dir)

            # Reemplazar las rutas en el HTML
            html_for_browser = html_out.replace('src="logos/', f'src="file:///{output_logos_dir}/')
            html_for_browser = html_for_browser.replace('src="fotos/', f'src="file:///{output_fotos_dir}/')

            # Verificar si existe la foto del alumno
            curp = datos.get("curp", "")
            foto_path = os.path.join(Config.PHOTOS_DIR, f"{curp}.jpg")
            if not os.path.exists(foto_path) and "has_photo" in datos and datos["has_photo"] == True:
                # Si la foto no existe pero se supone que debería tenerla, intentar copiarla desde foto_path
                if "foto_path" in datos and datos["foto_path"] and os.path.exists(datos["foto_path"]):
                    copy_file_safely(datos["foto_path"], foto_path)

            # Guardar el HTML modificado
            try:
                with open(html_output_filename, "w", encoding="utf-8") as f:
                    f.write(html_for_browser)
                self.logger.info(f"Archivo HTML guardado en: {html_output_filename}")
            except Exception as e:
                self.logger.error(f"Error al guardar el archivo HTML: {str(e)}")
                return None

            # Generar PDF usando wkhtmltopdf si está disponible
            if self.wkhtmltopdf_path:
                self.logger.info(f"Generando PDF con wkhtmltopdf: {self.wkhtmltopdf_path}")
                # Crear archivo HTML temporal
                try:
                    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as temp_html:
                        temp_html.write(html_out)
                        temp_html_path = temp_html.name
                    self.logger.debug(f"Archivo HTML temporal creado en: {temp_html_path}")
                except Exception as e:
                    self.logger.error(f"Error al crear archivo HTML temporal: {str(e)}")
                    return html_output_filename

                try:
                    # Modificar el HTML para usar rutas absolutas para las imágenes
                    with open(temp_html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    # Obtener rutas absolutas para los directorios de imágenes
                    output_logos_dir = os.path.abspath(salida_logos_dir)
                    output_fotos_dir = os.path.abspath(salida_fotos_dir)

                    # Reemplazar rutas relativas con rutas absolutas
                    html_content = html_content.replace('src="logos/', f'src="file:///{output_logos_dir}/')
                    html_content = html_content.replace('src="fotos/', f'src="file:///{output_fotos_dir}/')

                    # Guardar el HTML modificado
                    with open(temp_html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)

                    # Ejecutar wkhtmltopdf para convertir HTML a PDF
                    self.logger.info(f"Ejecutando wkhtmltopdf para generar PDF: {output_filename}")
                    result = subprocess.run([
                        self.wkhtmltopdf_path,
                        "--enable-local-file-access",  # Permitir acceso a archivos locales (imágenes)
                        "--page-size", "Letter",
                        "--margin-top", "5mm",
                        "--margin-bottom", "5mm",
                        "--margin-left", "5mm",
                        "--margin-right", "5mm",
                        temp_html_path,
                        output_filename
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

                    self.logger.debug(f"wkhtmltopdf ejecutado exitosamente. Salida: {result.stdout.decode('utf-8', errors='ignore')}")

                    # Eliminar archivos HTML temporales
                    os.unlink(temp_html_path)

                    # También eliminar el HTML de salida si existe
                    if os.path.exists(html_output_filename):
                        try:
                            os.unlink(html_output_filename)
                        except Exception as e:
                            self.logger.warning(f"No se pudo eliminar el archivo HTML temporal: {e}")

                    self.logger.info(f"PDF generado exitosamente: {output_filename}")
                    return output_filename

                except subprocess.SubprocessError as e:
                    self.logger.error(f"Error al ejecutar wkhtmltopdf: {str(e)}")
                    # Intentar capturar la salida de error
                    if hasattr(e, 'stderr') and e.stderr:
                        self.logger.error(f"Error de wkhtmltopdf: {e.stderr.decode('utf-8', errors='ignore')}")
                    # Eliminar archivo HTML temporal en caso de error
                    try:
                        os.unlink(temp_html_path)
                    except:
                        pass
                    return html_output_filename
                except Exception as e:
                    self.logger.error(f"Error inesperado al generar PDF: {str(e)}")
                    # Eliminar archivo HTML temporal en caso de error
                    try:
                        os.unlink(temp_html_path)
                    except:
                        pass
                    return html_output_filename
            else:
                self.logger.info("wkhtmltopdf no está disponible. Generando solo archivo HTML.")
                return html_output_filename

        except Exception as e:
            self.logger.error(f"Error general en generar_constancia: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    def crear_todas_plantillas(self):
        """Crea todas las plantillas si no existen"""
        # Verificar que el directorio de plantillas exista
        if not os.path.exists(self.template_dir):
            print(f"Creando directorio de plantillas: {self.template_dir}")
            os.makedirs(self.template_dir, exist_ok=True)

        # Las plantillas ya existen como archivos físicos, no es necesario crearlas
        # Solo verificamos que existan
        plantillas = {
            "constancia_estudio.html": "constancia de estudios",
            "constancia_calificaciones.html": "constancia de calificaciones",
            "constancia_traslado.html": "constancia de traslado"
        }

        for archivo, descripcion in plantillas.items():
            ruta_completa = os.path.join(self.template_dir, archivo)
            if not os.path.exists(ruta_completa):
                print(f"Advertencia: No se encontró la plantilla de {descripcion} ({ruta_completa})")
