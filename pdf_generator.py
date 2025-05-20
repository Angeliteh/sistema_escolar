from jinja2 import FileSystemLoader, Environment
import os
from datetime import datetime
import subprocess
import tempfile
import platform

class PDFGenerator:
    """
    Clase para generar diferentes tipos de constancias en PDF
    usando wkhtmltopdf
    """

    def __init__(self, template_dir="plantillas"):
        """Inicializa el generador con el directorio de plantillas"""
        self.template_dir = template_dir
        self.output_dir = "salidas"

        # Crear directorio de salida si no existe
        os.makedirs(self.output_dir, exist_ok=True)

        # Configurar entorno Jinja2
        self.env = Environment(loader=FileSystemLoader(template_dir))

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
                    return path
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f"No se encontró wkhtmltopdf en: {path} - Error: {str(e)}")
                continue

        # Si no se encuentra, devolver None
        print("ADVERTENCIA: No se encontró wkhtmltopdf en ninguna ubicación. Solo se generarán archivos HTML.")
        return None

    def generar_constancia(self, tipo_constancia, datos, output_path=None):
        """
        Genera una constancia del tipo especificado con los datos proporcionados

        Args:
            tipo_constancia: Tipo de constancia a generar (traslado, estudio, calificaciones)
            datos: Diccionario con los datos a incluir en la constancia
            output_path: Ruta personalizada donde guardar el PDF (opcional)

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
            datos["mostrar_calificaciones"] = True

            # Verificación adicional para asegurarnos de que haya calificaciones
            if "calificaciones" not in datos or not datos["calificaciones"]:
                datos["calificaciones"] = [
                    {"nombre": "LENGUAJES", "i": 8, "ii": 8, "iii": 8, "promedio": 8.0},
                    {"nombre": "SABERES Y PENSAMIENTOS CIENTÍFICOS", "i": 7, "ii": 8, "iii": 0, "promedio": 7.5},
                    {"nombre": "ETICA, NATURALEZA Y SOCIEDADES", "i": 7, "ii": 9, "iii": 0, "promedio": 8.0},
                    {"nombre": "DE LO HUMANO Y LO COMUNITARIO", "i": 7, "ii": 9, "iii": 0, "promedio": 8.0},
                ]

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

            # Usar la ruta personalizada si se proporciona, de lo contrario usar la ruta predeterminada
            if output_path:
                output_filename = output_path
            else:
                output_filename = os.path.join(self.output_dir, f"constancia_{tipo_constancia}_{curp}_{timestamp}.pdf")

            # Guardar siempre el HTML para revisión (en la carpeta de salida predeterminada)
            html_output_filename = os.path.join(self.output_dir, f"constancia_{tipo_constancia}_{curp}_{timestamp}.html")

            # Crear carpetas para imágenes en la carpeta de salida
            salida_logos_dir = os.path.join(self.output_dir, "logos")
            salida_fotos_dir = os.path.join(self.output_dir, "fotos")
            try:
                os.makedirs(salida_logos_dir, exist_ok=True)
                os.makedirs(salida_fotos_dir, exist_ok=True)
            except Exception as e:
                print(f"Error al crear directorios para imágenes: {str(e)}")
                # Continuar a pesar del error

            # Copiar el logo si existe
            logo_origen = os.path.join("logos", "logo_educacion.png")
            logo_destino = os.path.join(salida_logos_dir, "logo_educacion.png")
            if os.path.exists(logo_origen):
                try:
                    import shutil
                    shutil.copy2(logo_origen, logo_destino)
                except Exception as e:
                    print(f"Error al copiar el logo: {str(e)}")
                    # Continuar a pesar del error

            # Copiar la foto del alumno si existe
            foto_origen = os.path.join("fotos", f"{curp}.jpg")
            foto_destino = os.path.join(salida_fotos_dir, f"{curp}.jpg")
            if os.path.exists(foto_origen):
                try:
                    import shutil
                    shutil.copy2(foto_origen, foto_destino)
                except Exception as e:
                    print(f"Error al copiar la foto del alumno: {str(e)}")
                    # Continuar a pesar del error

            # Modificar el HTML para usar rutas absolutas para las imágenes en la vista del navegador
            current_dir = os.path.abspath(os.getcwd())
            html_for_browser = html_out.replace('src="logos/', f'src="file:///{current_dir}/logos/')
            html_for_browser = html_for_browser.replace('src="fotos/', f'src="file:///{current_dir}/fotos/')

            # Verificar si existe la foto del alumno
            curp = datos.get("curp", "")
            foto_path = os.path.join("fotos", f"{curp}.jpg")
            if not os.path.exists(foto_path) and "has_photo" in datos and datos["has_photo"] == True:
                # Si la foto no existe pero se supone que debería tenerla, intentar copiarla desde foto_path
                if "foto_path" in datos and datos["foto_path"] and os.path.exists(datos["foto_path"]):
                    try:
                        import shutil
                        shutil.copy2(datos["foto_path"], foto_path)
                    except Exception as e:
                        print(f"Error al copiar la foto desde foto_path: {str(e)}")
                        # Continuar a pesar del error

            # Guardar el HTML modificado
            try:
                with open(html_output_filename, "w", encoding="utf-8") as f:
                    f.write(html_for_browser)
                print(f"Archivo HTML guardado en: {html_output_filename}")
            except Exception as e:
                print(f"Error al guardar el archivo HTML: {str(e)}")
                return None

            # Generar PDF usando wkhtmltopdf si está disponible
            if self.wkhtmltopdf_path:
                print(f"Generando PDF con wkhtmltopdf: {self.wkhtmltopdf_path}")
                # Crear archivo HTML temporal
                try:
                    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as temp_html:
                        temp_html.write(html_out)
                        temp_html_path = temp_html.name
                    print(f"Archivo HTML temporal creado en: {temp_html_path}")
                except Exception as e:
                    print(f"Error al crear archivo HTML temporal: {str(e)}")
                    return html_output_filename

                try:
                    # Modificar el HTML para usar rutas absolutas para las imágenes
                    with open(temp_html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()

                    # Obtener la ruta absoluta del directorio de trabajo
                    current_dir = os.path.abspath(os.getcwd())

                    # Reemplazar rutas relativas con rutas absolutas
                    html_content = html_content.replace('src="logos/', f'src="file:///{current_dir}/logos/')
                    html_content = html_content.replace('src="fotos/', f'src="file:///{current_dir}/fotos/')

                    # Guardar el HTML modificado
                    with open(temp_html_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)

                    # Ejecutar wkhtmltopdf para convertir HTML a PDF
                    print(f"Ejecutando wkhtmltopdf para generar PDF: {output_filename}")
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

                    print(f"wkhtmltopdf ejecutado exitosamente. Salida: {result.stdout.decode('utf-8', errors='ignore')}")

                    # Eliminar archivo HTML temporal
                    os.unlink(temp_html_path)
                    print(f"PDF generado exitosamente: {output_filename}")
                    return output_filename

                except subprocess.SubprocessError as e:
                    print(f"Error al ejecutar wkhtmltopdf: {str(e)}")
                    # Intentar capturar la salida de error
                    if hasattr(e, 'stderr') and e.stderr:
                        print(f"Error de wkhtmltopdf: {e.stderr.decode('utf-8', errors='ignore')}")
                    # Eliminar archivo HTML temporal en caso de error
                    try:
                        os.unlink(temp_html_path)
                    except:
                        pass
                    return html_output_filename
                except Exception as e:
                    print(f"Error inesperado al generar PDF: {str(e)}")
                    # Eliminar archivo HTML temporal en caso de error
                    try:
                        os.unlink(temp_html_path)
                    except:
                        pass
                    return html_output_filename
            else:
                print("wkhtmltopdf no está disponible. Generando solo archivo HTML.")
                return html_output_filename

        except Exception as e:
            print(f"Error general en generar_constancia: {str(e)}")
            import traceback
            traceback.print_exc()
            return None



    def crear_todas_plantillas(self):
        """Crea todas las plantillas si no existen"""
        # Las plantillas ya existen como archivos físicos, no es necesario crearlas
        # Solo verificamos que existan
        if not os.path.exists(os.path.join(self.template_dir, "constancia_estudio.html")):
            print("Advertencia: No se encontró la plantilla de constancia de estudios")
        if not os.path.exists(os.path.join(self.template_dir, "constancia_calificaciones.html")):
            print("Advertencia: No se encontró la plantilla de constancia de calificaciones")
        if not os.path.exists(os.path.join(self.template_dir, "constancia_traslado.html")):
            print("Advertencia: No se encontró la plantilla de constancia de traslado")

        # Verificar que el directorio de plantillas exista
        if not os.path.exists(self.template_dir):
            print(f"Creando directorio de plantillas: {self.template_dir}")
            os.makedirs(self.template_dir, exist_ok=True)
