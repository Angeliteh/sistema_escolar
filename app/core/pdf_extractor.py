import pdfplumber
import re
import os
import io
import PyPDF2
from PIL import Image
from app.core.config import Config
from app.core.utils import ensure_directories_exist, copy_file_safely
from app.core.logging import get_logger

def is_number(s):
    """Verifica si una cadena es un número"""
    try:
        float(s)
        return True
    except ValueError:
        return False

class PDFExtractor:
    """
    Clase para extraer datos de diferentes tipos de constancias en PDF
    """

    def __init__(self, pdf_path):
        """Inicializa el extractor con la ruta al PDF"""
        self.pdf_path = pdf_path
        self.logger = get_logger(__name__)
        self.text = self._extract_text()
        self.tipo_constancia = self._determinar_tipo_constancia()
        self.has_photo = False  # Indica si se encontró una foto en el PDF

        # Asegurar que los directorios necesarios existan
        ensure_directories_exist()

    def _extract_text(self):
        """Extrae todo el texto del PDF"""
        with pdfplumber.open(self.pdf_path) as pdf:
            return "\n".join([page.extract_text() for page in pdf.pages])

    def _determinar_tipo_constancia(self):
        """Determina el tipo de constancia basado en el contenido"""
        text_lower = self.text.lower()

        if "traslado" in text_lower:
            return "traslado"
        elif "calificaciones" in text_lower:
            return "calificaciones"
        elif "estudio" in text_lower:
            return "estudio"
        else:
            return "desconocido"

    def _buscar(self, patron, default=""):
        """Busca un patrón en el texto y devuelve el valor encontrado"""
        for line in self.text.splitlines():
            if patron in line:
                # Intenta obtener el valor después de los dos puntos
                parts = line.split(":", 1)
                if len(parts) > 1:
                    return parts[1].strip()
                # Si no hay dos puntos, devuelve la línea completa
                return line.strip()
        return default

    def _buscar_regex(self, patron, default=""):
        """Busca un patrón usando expresiones regulares"""
        match = re.search(patron, self.text, re.IGNORECASE)
        if match and match.groups():
            return match.group(1).strip()
        return default

    def extraer_datos_basicos(self):
        """Extrae los datos básicos comunes a todos los tipos de constancias"""
        datos = {
            "tipo_constancia": self.tipo_constancia,
            "escuela": Config.get_school_name(),  # Valor dinámico desde configuración
            "cct": Config.get_school_cct(),  # Valor dinámico desde configuración
            "ciclo": Config.get_current_year(),  # Valor dinámico desde configuración
            "director": Config.get_director_name(),  # Valor dinámico desde configuración
            "fecha_actual": Config.get_current_date_formatted(),
        }

        # Extraer datos según el tipo de constancia
        if self.tipo_constancia == "traslado":
            self._extraer_datos_traslado(datos)
        elif self.tipo_constancia == "estudio":
            self._extraer_datos_estudios(datos)
        elif self.tipo_constancia == "calificaciones":
            self._extraer_datos_calificaciones(datos)
        else:
            # Método genérico para cualquier tipo
            self._extraer_datos_genericos(datos)

        return datos

    # Resto de métodos de extracción de datos...
    # (Aquí irían los métodos _extraer_datos_traslado, _extraer_datos_estudios, etc.)

    def _extraer_datos_traslado(self, datos):
        """Extrae datos específicos de constancias de traslado"""
        # En constancias de traslado, los datos suelen estar en un formato específico

        # Extraer nombre
        nombre = self._buscar_regex(r"NOMBRE:\s*([^C]+)CURP:", "")
        if not nombre:
            nombre_match = re.search(r"NOMBRE\s*:\s*(.*?)(?:CURP|MATRICULA|GRADO|$)", self.text, re.DOTALL)
            if nombre_match:
                nombre = nombre_match.group(1).strip()
                # Si el nombre contiene "CURP:", eliminar esa parte
                if "CURP:" in nombre:
                    nombre = nombre.split("CURP:")[0].strip()
            else:
                nombre = ""
        datos["nombre"] = nombre

        # Extraer CURP
        curp = self._buscar_regex(r"CURP:\s*([A-Z0-9]{18})", "")
        if not curp:
            curp = self._buscar_regex(r"CURP\s*:\s*([A-Z0-9]{18})", "")
        datos["curp"] = curp

        # Extraer matrícula
        matricula = self._buscar_regex(r"MATRICULA:\s*([A-Z0-9\-]+)", "")
        if not matricula:
            matricula = self._buscar_regex(r"MATRICULA\s*:\s*([A-Z0-9\-]+)", "")
        datos["matricula"] = matricula

        # Extraer fecha de nacimiento
        nacimiento = self._buscar_regex(r"FECHA DE NACIMIENTO\s*:\s*([^\n]+)", "")
        # Limpiar la fecha de nacimiento para eliminar cualquier texto de matrícula
        if nacimiento and "MATRICULA" in nacimiento:
            nacimiento = nacimiento.split("MATRICULA")[0].strip()
        datos["nacimiento"] = nacimiento

        # Extraer grado, grupo y turno
        grado_grupo_turno = self._buscar_regex(r"GRADO:\s*(\d+)\s+GRUPO:\s*([A-Z])\s+TURNO:\s*(\w+)", "")
        if grado_grupo_turno:
            match = re.search(r"GRADO:\s*(\d+)\s+GRUPO:\s*([A-Z])\s+TURNO:\s*(\w+)", self.text, re.IGNORECASE)
            if match:
                datos["grado"] = match.group(1)
                datos["grupo"] = match.group(2)
                datos["turno"] = match.group(3)
        else:
            # Intentar extraer individualmente
            datos["grado"] = self._buscar_regex(r"GRADO\s*:\s*(\d+)", "")
            datos["grupo"] = self._buscar_regex(r"GRUPO\s*:\s*([A-Z])", "")
            datos["turno"] = self._buscar_regex(r"TURNO\s*:\s*(\w+)", "MATUTINO")

    def _extraer_datos_estudios(self, datos):
        """Extrae datos específicos de constancias de estudios"""
        # Extraer nombre
        nombre = self._buscar("NOMBRE")
        if not nombre:
            nombre = self._buscar_regex(r"NOMBRE\s*:\s*([^\n]+)", "")
        datos["nombre"] = nombre

        # Extraer CURP
        curp = self._buscar("CURP")
        if not curp:
            curp = self._buscar_regex(r"CURP\s*:\s*([A-Z0-9]{18})", "")
        datos["curp"] = curp

        # Extraer matrícula
        matricula = self._buscar("MATRICULA")
        if not matricula:
            matricula = self._buscar_regex(r"MATRICULA\s*:\s*([A-Z0-9\-]+)", "")
        datos["matricula"] = matricula

        # Extraer fecha de nacimiento
        nacimiento = self._buscar("FECHA DE NACIMIENTO")
        if not nacimiento:
            nacimiento = self._buscar_regex(r"FECHA DE NACIMIENTO\s*:\s*([^\n]+)", "")
        datos["nacimiento"] = nacimiento

        # Extraer grado y grupo
        grado_grupo = self._buscar("GRADO Y GRUPO")
        if grado_grupo:
            # Intentar extraer grado y grupo del formato "1A MATUTINO"
            match = re.search(r"(\d+)([A-Z])\s+(\w+)", grado_grupo)
            if match:
                datos["grado"] = match.group(1)
                datos["grupo"] = match.group(2)
                datos["turno"] = match.group(3)
            else:
                datos["grado"] = grado_grupo
        else:
            datos["grado"] = self._buscar_regex(r"GRADO\s*:\s*(\d+)", "")
            datos["grupo"] = self._buscar_regex(r"GRUPO\s*:\s*([A-Z])", "")

        # Extraer turno si no se ha extraído antes
        if "turno" not in datos or not datos["turno"]:
            datos["turno"] = self._buscar_regex(r"TURNO\s*:\s*(\w+)", "MATUTINO")
            if not datos["turno"]:
                datos["turno"] = self._buscar_regex(r"MATUTINO|VESPERTINO", "MATUTINO")

    def _extraer_datos_calificaciones(self, datos):
        """Extrae datos específicos de constancias de calificaciones"""
        # Extraer nombre
        nombre = self._buscar("NOMBRE")
        if not nombre:
            nombre = self._buscar_regex(r"NOMBRE\s*:\s*([^\n]+)", "")
        datos["nombre"] = nombre

        # Extraer CURP
        curp = self._buscar("CURP")
        if not curp:
            curp = self._buscar_regex(r"CURP\s*:\s*([A-Z0-9]{18})", "")
        datos["curp"] = curp

        # Extraer matrícula
        matricula = self._buscar("MATRICULA")
        if not matricula:
            matricula = self._buscar_regex(r"MATRICULA\s*:\s*([A-Z0-9\-]+)", "")
        datos["matricula"] = matricula

        # Extraer fecha de nacimiento
        nacimiento = self._buscar("FECHA DE NACIMIENTO")
        if not nacimiento:
            nacimiento = self._buscar_regex(r"FECHA DE NACIMIENTO\s*:\s*([^\n]+)", "")
        datos["nacimiento"] = nacimiento

        # Extraer grado
        grado = self._buscar("GRADO")
        if not grado:
            grado = self._buscar_regex(r"GRADO\s*:\s*(\d+)", "")
            if not grado:
                # Buscar en formato "Cursa el 1er. grado"
                grado = self._buscar_regex(r"Cursa el (\d+)(?:er|do|to|vo)\. grado", "")
        datos["grado"] = grado

        # Extraer grupo
        grupo = self._buscar("GRUPO")
        if not grupo:
            grupo = self._buscar_regex(r"GRUPO\s*:\s*([A-Z])", "")
        datos["grupo"] = grupo

        # Extraer turno
        turno = self._buscar("TURNO")
        if not turno:
            turno = self._buscar_regex(r"TURNO\s*:\s*(\w+)", "MATUTINO")
        datos["turno"] = turno

    def _extraer_datos_genericos(self, datos):
        """Método genérico para extraer datos de cualquier tipo de constancia"""
        # Extraer nombre
        nombre = self._buscar("NOMBRE")
        if not nombre:
            nombre = self._buscar_regex(r"NOMBRE\s*:\s*([^\n]+)", "")
        if not nombre:
            nombre = self._buscar_regex(r"alumno[^:]*:\s*([^\n]+)", "")
        datos["nombre"] = nombre

        # Extraer CURP
        curp = self._buscar("CURP")
        if not curp:
            curp = self._buscar_regex(r"CURP\s*:\s*([A-Z0-9]{18})", "")
        datos["curp"] = curp

        # Extraer matrícula
        matricula = self._buscar("MATRICULA")
        if not matricula:
            matricula = self._buscar_regex(r"MATRICULA\s*:\s*([A-Z0-9\-]+)", "")
        datos["matricula"] = matricula

        # Extraer fecha de nacimiento
        nacimiento = self._buscar("FECHA DE NACIMIENTO")
        if not nacimiento:
            nacimiento = self._buscar_regex(r"FECHA DE NACIMIENTO\s*:\s*([^\n]+)", "")
        datos["nacimiento"] = nacimiento

        # Extraer grado
        grado = self._buscar("GRADO")
        if not grado:
            grado = self._buscar_regex(r"GRADO\s*:\s*(\d+)", "")
        datos["grado"] = grado

        # Extraer grupo
        grupo = self._buscar("GRUPO")
        if not grupo:
            grupo = self._buscar_regex(r"GRUPO\s*:\s*([A-Z])", "")
        datos["grupo"] = grupo

        # Extraer turno
        turno = self._buscar("TURNO")
        if not turno:
            turno = self._buscar_regex(r"TURNO\s*:\s*(\w+)", "MATUTINO")
        datos["turno"] = turno

    def tiene_calificaciones(self):
        """
        Verifica si el PDF contiene calificaciones

        Returns:
            True si el PDF contiene calificaciones, False en caso contrario
        """
        # Método 1: Verificar si el método extraer_calificaciones devuelve calificaciones
        calificaciones = self.extraer_calificaciones()
        if calificaciones and len(calificaciones) > 0:
            self.logger.debug(f"Detectadas {len(calificaciones)} calificaciones mediante extracción directa")
            return True

        # Método 2: Buscar sección de calificaciones con patrones más específicos
        # Patrón 1: Encabezado de tabla de calificaciones con MATERIAS
        match = re.search(r"MATERIAS\s+I\s+II\s+III\s+Promedio", self.text, re.DOTALL)
        if match:
            self.logger.debug("Detectadas calificaciones (patrón MATERIAS)")
            return True

        # Patrón 2: Encabezado de tabla de calificaciones con ASIGNATURA
        match = re.search(r"ASIGNATURA\s+P1\s+P2\s+P3\s+Promedio", self.text, re.DOTALL)
        if match:
            self.logger.debug("Detectadas calificaciones (patrón ASIGNATURA)")
            return True

        # Patrón 3: Buscar palabras clave específicas de materias seguidas de números
        materias_clave = [
            r"LENGUAJES\s+\d",
            r"SABERES Y PENSAMIENTOS\s+\d",
            r"ETICA, NATURALEZA\s+\d",
            r"DE LO HUMANO Y LO COMUNITARIO\s+\d",
            r"FORMACION CIVICA\s+\d"
        ]

        for patron in materias_clave:
            if re.search(patron, self.text, re.DOTALL):
                self.logger.debug(f"Detectadas calificaciones (patrón materia: {patron})")
                return True

        # Patrón 4: Buscar cualquier sección que pueda contener calificaciones
        # Buscar secciones con al menos 3 líneas que contengan 4 números entre 0 y 10
        calificaciones_pattern = r"((?:\w+\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?[\r\n]+){3,})"
        if re.search(calificaciones_pattern, self.text, re.DOTALL):
            self.logger.debug("Detectadas calificaciones (patrón de múltiples líneas con números)")
            return True

        # Patrón 5: Verificar si hay una sección que contiene múltiples números que podrían ser calificaciones
        # Buscar secciones con al menos 3 números entre 0 y 10 con decimales
        calificaciones_pattern = r"(\d(\.\d)?)\s+(\d(\.\d)?)\s+(\d(\.\d)?)\s+(\d(\.\d)?)"
        if re.search(calificaciones_pattern, self.text, re.DOTALL):
            # Verificar que no sea parte de una fecha o información no relacionada
            # Esto es un patrón más débil, así que verificamos que no esté en secciones conocidas
            if not re.search(r"INICIO DEL CICLO|FIN DEL CICLO|FECHA DE NACIMIENTO", self.text, re.DOTALL):
                self.logger.debug("Detectadas posibles calificaciones (patrón numérico)")
                return True

        self.logger.debug("No se detectaron calificaciones en el PDF")
        return False

    def extraer_calificaciones(self):
        """Extrae las calificaciones si están disponibles"""
        calificaciones = []

        # Buscar sección de calificaciones con diferentes patrones
        # Patrón 1: Formato tradicional
        match = re.search(r"MATERIAS\s+I\s+II\s+III\s+Promedio(.*?)(?:Se extiende|Se expide)", self.text, re.DOTALL)
        if not match:
            # Patrón 2: Formato con P1, P2, P3
            match = re.search(r"ASIGNATURA\s+P1\s+P2\s+P3\s+Promedio(.*?)(?:Se extiende|Se expide|Analiza|NIVELES)", self.text, re.DOTALL)
        if not match:
            # Patrón 3: Buscar sección específica de calificaciones
            match = re.search(r"CALIFICACIONES DE LAS ASIGNATURAS CURSADAS(.*?)(?:Analiza|Se extiende|Se expide)", self.text, re.DOTALL)
        if not match:
            # Patrón 4: Nuevo formato sin encabezados específicos
            match = re.search(r"MATERIAS(.*?)(?:Se extiende|Se expide)", self.text, re.DOTALL)
        if not match:
            # Patrón 5: Otro formato nuevo
            match = re.search(r"TURNO.*?MATUTINO\s*(.*?)(?:Se extiende|Se expide)", self.text, re.DOTALL)
        if not match:
            # Patrón 6: Buscar cualquier sección que pueda contener calificaciones
            match = re.search(r"((?:\w+\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?[\r\n]+){2,})", self.text, re.DOTALL)

        if match:
            materias_text = match.group(1).strip()

            # Procesar cada línea de materias
            for line in materias_text.splitlines():
                # Ignorar líneas vacías
                if not line.strip():
                    continue

                # Intentar extraer nombre de materia y calificaciones
                parts = re.split(r'\s+', line.strip())

                # Verificar si tenemos suficientes partes para ser una calificación
                if len(parts) >= 4:  # Al menos nombre + 2 calificaciones + promedio
                    # Intentar identificar el patrón de calificaciones
                    # Buscar desde el final números que podrían ser calificaciones
                    califs_indices = []
                    promedio_index = -1

                    # Buscar desde el final números que podrían ser calificaciones
                    # Primero, intentar identificar un patrón claro de calificaciones al final
                    # Buscamos 4 números consecutivos al final (3 calificaciones + promedio)
                    last_four = []  # Definir last_four aquí para que esté disponible en todo el ámbito

                    if len(parts) >= 4:
                        try:
                            # Verificar si los últimos 4 elementos son números válidos para calificaciones
                            for i in range(1, 5):
                                if i <= len(parts):
                                    val = float(parts[-i])
                                    if 0 <= val <= 10:  # Rango válido para calificaciones
                                        last_four.append(len(parts) - i)

                            # Si encontramos 4 números válidos al final, usarlos como calificaciones
                            if len(last_four) == 4:
                                promedio_index = last_four[0]  # El último es el promedio
                                califs_indices = last_four[1:]  # Los 3 anteriores son calificaciones
                            else:
                                # Si no encontramos 4 números consecutivos, usar el enfoque anterior
                                for i in range(len(parts) - 1, -1, -1):
                                    try:
                                        # Intentar convertir a float
                                        val = float(parts[i])
                                        if 0 <= val <= 10:  # Rango válido para calificaciones
                                            if promedio_index == -1:
                                                promedio_index = i  # El primer número desde el final es el promedio
                                            else:
                                                califs_indices.append(i)  # Los demás son calificaciones
                                    except ValueError:
                                        # No es un número, podría ser parte del nombre de la materia
                                        pass
                        except ValueError:
                            # Si hay error en la conversión, usar el enfoque anterior
                            for i in range(len(parts) - 1, -1, -1):
                                try:
                                    # Intentar convertir a float
                                    val = float(parts[i])
                                    if 0 <= val <= 10:  # Rango válido para calificaciones
                                        if promedio_index == -1:
                                            promedio_index = i  # El primer número desde el final es el promedio
                                        else:
                                            califs_indices.append(i)  # Los demás son calificaciones
                                except ValueError:
                                    # No es un número, podría ser parte del nombre de la materia
                                    pass

                    # Si encontramos al menos un promedio y una calificación
                    if promedio_index != -1 and len(califs_indices) > 0:
                        # El promedio es el último número
                        promedio = parts[promedio_index]

                        # Ordenar los índices de calificaciones
                        califs_indices.sort()

                        # Extraer las calificaciones
                        califs = [parts[i] for i in califs_indices]

                        # El nombre de la materia es todo lo que está antes de la primera calificación
                        # Ordenar los índices de calificaciones para asegurarnos de que tomamos el correcto
                        califs_indices.sort()

                        # Si estamos usando el patrón de 4 números consecutivos al final,
                        # podemos estar más seguros de que todo lo demás es el nombre de la materia
                        if len(last_four) == 4:
                            nombre_materia = " ".join(parts[:califs_indices[0]])
                        else:
                            # Si no, necesitamos ser más cuidadosos
                            # Verificar si hay algún número que podría ser parte del nombre de la materia
                            # (por ejemplo, "FORMACION CIVICA Y ETICA 1")
                            nombre_parts = []
                            for i in range(califs_indices[0]):
                                # Verificar si este elemento es un número pero no una calificación
                                try:
                                    val = float(parts[i])
                                    # Si es un número pero está seguido por texto, probablemente es parte del nombre
                                    if i < len(parts) - 1 and not is_number(parts[i+1]):
                                        nombre_parts.append(parts[i])
                                    # Si es un número pequeño (como 1, 2, 3) y está al final del nombre, probablemente es parte del nombre
                                    elif val <= 3 and i == califs_indices[0] - 1:
                                        nombre_parts.append(parts[i])
                                    # De lo contrario, podría ser una calificación, así que no lo incluimos
                                except ValueError:
                                    # No es un número, definitivamente es parte del nombre
                                    nombre_parts.append(parts[i])

                            nombre_materia = " ".join(nombre_parts)

                        # Asegurarse de que tenemos 3 calificaciones (rellenar con 0 si faltan)
                        while len(califs) < 3:
                            califs.append("0")

                        # Tomar solo las primeras 3 calificaciones si hay más
                        califs = califs[:3]

                        # Convertir calificaciones a números
                        try:
                            califs_num = [float(c) if c != "0" else 0 for c in califs]
                            promedio_num = float(promedio)

                            # Solo agregar si el nombre de la materia no está vacío
                            if nombre_materia.strip():
                                calificaciones.append({
                                    "nombre": nombre_materia,
                                    "i": califs_num[0],
                                    "ii": califs_num[1],
                                    "iii": califs_num[2],
                                    "promedio": promedio_num
                                })
                        except (ValueError, IndexError):
                            # Ignorar silenciosamente errores de conversión
                            pass

        # Devolver las calificaciones encontradas (o una lista vacía si no hay)
        # Ya no usamos datos de ejemplo

        return calificaciones

    def extraer_foto(self, guardar_en_directorio=True):
        """
        Extrae la foto del alumno del PDF si está disponible

        Args:
            guardar_en_directorio: Si es True, guarda la foto en el directorio de fotos

        Returns:
            Ruta a la foto guardada o None si no se encontró ninguna foto
        """
        # Asegurar que los directorios necesarios existan
        ensure_directories_exist()

        # Crear directorio temporal para imágenes extraídas
        temp_dir = os.path.join(Config.BASE_DIR, "temp_images")
        os.makedirs(temp_dir, exist_ok=True)

        # Obtener el CURP del alumno
        curp = self.extraer_datos_basicos().get("curp", "")
        if not curp:
            # Si no hay CURP, usar un nombre basado en el nombre del archivo
            base_name = os.path.basename(self.pdf_path)
            curp = os.path.splitext(base_name)[0]

        # Ruta donde se guardará la foto final
        img_path = os.path.join(Config.PHOTOS_DIR, f"{curp}.jpg")

        # Extraer todas las imágenes del PDF
        imagenes_extraidas = self._extraer_todas_imagenes(temp_dir)

        if not imagenes_extraidas:
            return None

        # Intentar identificar automáticamente la foto del alumno
        foto_alumno = self._identificar_foto_alumno(imagenes_extraidas)

        if foto_alumno:
            # En modo no interactivo, usar la foto identificada automáticamente
            try:
                self._copiar_imagen_segura(foto_alumno, img_path)
                self.has_photo = True
                return img_path
            except Exception:
                # Si falla, devolver None
                return None

        # Si no se pudo identificar automáticamente, devolver None
        # (la interfaz gráfica se encargará de mostrar las imágenes y permitir la selección)
        return None

    def _identificar_foto_alumno(self, imagenes):
        """
        Intenta identificar automáticamente la foto del alumno entre las imágenes extraídas

        Args:
            imagenes: Lista de rutas a las imágenes extraídas

        Returns:
            Ruta a la imagen identificada como foto del alumno o None si no se pudo identificar
        """
        # Verificar si hay una imagen con nombre page1_img3.jpg (la tercera imagen en la primera página)
        # Esta es la imagen que el usuario identificó como la foto del alumno
        for img_path in imagenes:
            if "page1_img3" in os.path.basename(img_path):
                return img_path

        # Buscar imágenes con proporción similar a la observada (aproximadamente 4:5)
        for img_path in imagenes:
            try:
                # Usar PIL para obtener las dimensiones, pero cerrar inmediatamente el archivo
                img = Image.open(img_path)
                width, height = img.size
                img.close()  # Cerrar explícitamente la imagen

                # Calcular la proporción
                aspect_ratio = width / height

                # Si la proporción es cercana a 0.8 (4:5), es un buen candidato
                if 0.75 <= aspect_ratio <= 0.85 and width >= 90 and height >= 115:
                    return img_path
            except Exception:
                pass

        # Si no encontramos ninguna imagen adecuada
        return None

    def _copiar_imagen_segura(self, origen, destino):
        """
        Copia una imagen de forma segura, con reintentos en caso de error

        Args:
            origen: Ruta de la imagen de origen
            destino: Ruta de destino

        Raises:
            Exception: Si no se pudo copiar la imagen después de varios intentos
        """
        # Usar la función centralizada para copiar archivos de forma segura
        if copy_file_safely(origen, destino):
            return

        # Si la función centralizada falla, intentar métodos alternativos

        # Método 1: Usar PIL para abrir y guardar la imagen
        try:
            # Abrir la imagen con PIL
            img = Image.open(origen)

            # Guardar la imagen en el destino
            img.save(destino, format="JPEG")

            # Cerrar la imagen
            img.close()
            return
        except Exception:
            pass

        # Método 2: Leer y escribir el contenido del archivo
        try:
            # Abrir la imagen de origen y leer su contenido
            with open(origen, 'rb') as src_file:
                contenido = src_file.read()

            # Escribir el contenido en el archivo de destino
            with open(destino, 'wb') as dst_file:
                dst_file.write(contenido)
            return
        except Exception:
            pass

        # Si llegamos aquí, todos los métodos fallaron
        raise Exception("No se pudo copiar la imagen después de intentar todos los métodos disponibles")

    def _extraer_todas_imagenes(self, output_dir):
        """
        Extrae todas las imágenes del PDF y las guarda en el directorio especificado

        Args:
            output_dir: Directorio donde guardar las imágenes

        Returns:
            Lista de rutas a las imágenes extraídas
        """
        imagenes_extraidas = []

        # Limpiar el directorio de imágenes temporales
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

        # Extraer imágenes con pdfplumber
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    for img_num, image in enumerate(page.images):
                        try:
                            img_bytes = image['stream'].get_data()
                            img = Image.open(io.BytesIO(img_bytes))

                            # Guardar la imagen
                            img_filename = f"page{page_num+1}_img{img_num+1}.jpg"
                            img_path = os.path.join(output_dir, img_filename)
                            img.save(img_path, "JPEG")
                            imagenes_extraidas.append(img_path)
                        except Exception:
                            pass
        except Exception:
            pass

        # Extraer imágenes con PyPDF2 (método alternativo)
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]

                    if '/Resources' in page and '/XObject' in page['/Resources']:
                        xobjects = page['/Resources']['/XObject']

                        for obj_num, (_, obj) in enumerate(xobjects.items()):
                            try:
                                if obj['/Subtype'] == '/Image':
                                    # Extraer datos de la imagen
                                    img_filename = f"pypdf_page{page_num+1}_img{obj_num+1}.jpg"
                                    img_path = os.path.join(output_dir, img_filename)

                                    try:
                                        if '/Filter' in obj and '/DCTDecode' in obj['/Filter']:
                                            # Imagen JPEG
                                            img_data = obj.get_data()
                                            with open(img_path, 'wb') as img_file:
                                                img_file.write(img_data)
                                            imagenes_extraidas.append(img_path)
                                        else:
                                            # Intentar convertir otros formatos a JPEG
                                            if '/Width' in obj and '/Height' in obj:
                                                width = obj['/Width']
                                                height = obj['/Height']

                                                # Crear una imagen PIL
                                                mode = "RGB" if '/ColorSpace' in obj and obj['/ColorSpace'] == '/DeviceRGB' else "P"

                                                img_data = obj.get_data()
                                                img = Image.frombytes(mode, (width, height), img_data)
                                                img.save(img_path, "JPEG")
                                                imagenes_extraidas.append(img_path)
                                    except Exception:
                                        pass
                            except Exception:
                                pass
        except Exception:
            pass

        return imagenes_extraidas

    def extraer_todos_datos(self, incluir_foto=None, tipo_constancia_solicitado=None):
        """
        Extrae todos los datos disponibles en el PDF

        Args:
            incluir_foto: Controla si se debe incluir la foto en la constancia
                - True: Incluir foto (si está disponible)
                - False: No incluir foto
                - None: Detectar automáticamente (comportamiento por defecto)
            tipo_constancia_solicitado: Tipo de constancia que se va a generar
                - Si es None, se usa el tipo detectado automáticamente
                - Si se especifica, se respeta este tipo para decidir qué datos incluir

        Returns:
            Diccionario con todos los datos extraídos
        """
        # Usar el tipo de constancia solicitado si se proporciona
        tipo_constancia_efectivo = tipo_constancia_solicitado if tipo_constancia_solicitado else self.tipo_constancia

        # Extraer datos básicos
        datos = self.extraer_datos_basicos()

        # Asegurarse de que el grado sea un entero
        if 'grado' in datos and datos['grado']:
            try:
                # Intentar convertir el grado a entero
                datos['grado'] = int(datos['grado'])
                self.logger.debug(f"Grado convertido a entero: {datos['grado']}")
            except (ValueError, TypeError):
                # Si no se puede convertir, usar el valor por defecto
                self.logger.warning(f"No se pudo convertir el grado '{datos['grado']}' a entero. Usando valor por defecto.")
                datos['grado'] = Config.DEFAULT_GRADE

        # Asegurarse de que el grupo sea una cadena
        if 'grupo' in datos and datos['grupo'] is not None:
            datos['grupo'] = str(datos['grupo'])
            self.logger.debug(f"Grupo convertido a cadena: '{datos['grupo']}'")

        # Verificar si la constancia original tiene calificaciones
        tiene_calificaciones = self.tiene_calificaciones()
        datos["tiene_calificaciones"] = tiene_calificaciones

        # Manejar las calificaciones según el tipo de constancia SOLICITADO
        # Esto es independiente del tipo detectado en el PDF original
        if tipo_constancia_efectivo == "estudio":
            # Para constancia de estudios, NUNCA incluir calificaciones, independientemente de si están disponibles
            datos["calificaciones"] = []
            datos["mostrar_calificaciones"] = False

        elif tipo_constancia_efectivo in ["calificaciones", "traslado"]:
            # Para constancias de calificaciones y traslado, incluir calificaciones si están disponibles
            datos["mostrar_calificaciones"] = tiene_calificaciones

            # Si la constancia original no tiene calificaciones y es de tipo calificaciones o traslado, devolver error
            if not tiene_calificaciones and tipo_constancia_efectivo in ["calificaciones", "traslado"]:
                # Para constancia de calificaciones y traslado, es obligatorio tener calificaciones
                raise ValueError(f"No se puede generar una constancia de {tipo_constancia_efectivo} sin calificaciones.")

            # Extraer calificaciones (sin usar datos de ejemplo)
            calificaciones = self.extraer_calificaciones()
            datos["calificaciones"] = calificaciones

        else:
            # Para otros tipos, incluir calificaciones vacías
            datos["calificaciones"] = []
            datos["mostrar_calificaciones"] = False

        # Añadir ID de alumno si está disponible
        datos["id_alumno"] = self._buscar_regex(r"ID ALUMNO\s*:\s*(\d+)", "")

        # Manejar la foto según la opción seleccionada
        if incluir_foto is False:
            # No incluir foto, independientemente de si está disponible
            datos["has_photo"] = False
            datos["foto_path"] = None
            datos["show_placeholder"] = False
        else:
            # Incluir foto si está disponible (True) o detectar automáticamente (None)
            foto_path = self.extraer_foto()

            if foto_path:
                datos["foto_path"] = foto_path
                datos["has_photo"] = True
            else:
                datos["has_photo"] = False

                # Si se solicitó explícitamente incluir foto pero no se encontró,
                # indicar que se debe mostrar el marcador de posición
                if incluir_foto is True:
                    datos["show_placeholder"] = True
                else:
                    # En modo automático, no mostrar ningún placeholder si no hay foto
                    datos["show_placeholder"] = False

        return datos
