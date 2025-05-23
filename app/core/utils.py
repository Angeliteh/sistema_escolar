import os
import shutil
import tempfile
import platform
import subprocess
import fnmatch
import unicodedata
import re
from datetime import datetime, timedelta
from app.core.config import Config

def ensure_directories_exist():
    """Asegura que todos los directorios necesarios existan"""
    for directory in [Config.TEMPLATES_DIR, Config.LOGOS_DIR, Config.PHOTOS_DIR, Config.OUTPUT_DIR]:
        os.makedirs(directory, exist_ok=True)

def copy_file_safely(source, destination):
    """Copia un archivo de forma segura, creando directorios si es necesario"""
    try:
        # Crear directorio de destino si no existe
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        # Copiar el archivo
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        print(f"Error al copiar archivo {source} a {destination}: {e}")
        return False

def generate_timestamp():
    """Genera un timestamp para nombres de archivo"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def open_file_with_default_app(file_path):
    """Abre un archivo con la aplicación predeterminada del sistema"""
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', file_path))
        else:  # Linux
            subprocess.call(('xdg-open', file_path))
        return True
    except Exception as e:
        print(f"Error al abrir archivo {file_path}: {e}")
        return False

def create_temp_file(content, suffix=".html"):
    """Crea un archivo temporal con el contenido especificado"""
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w", encoding="utf-8") as temp_file:
            temp_file.write(content)
            return temp_file.name
    except Exception as e:
        print(f"Error al crear archivo temporal: {e}")
        return None

def format_curp(curp):
    """Formatea un CURP para asegurar que esté en mayúsculas y sin espacios"""
    if curp:
        return curp.strip().upper()
    return ""

def format_name(name, uppercase=False, remove_accents=False):
    """
    Formatea un nombre para mostrar

    Args:
        name: Nombre a formatear
        uppercase: Si se debe convertir a mayúsculas
        remove_accents: Si se deben eliminar los acentos

    Returns:
        Nombre formateado
    """
    if not name:
        return ""

    result = name

    # Eliminar acentos si se solicita
    if remove_accents:
        # Normalizar caracteres Unicode (NFD descompone los caracteres acentuados)
        result = unicodedata.normalize('NFD', result)
        # Eliminar los caracteres no ASCII (como los acentos)
        result = ''.join(c for c in result if not unicodedata.combining(c))

    if uppercase:
        # Convertir a mayúsculas
        return result.upper()
    else:
        # Capitalizar cada palabra, respetando espacios
        return " ".join(word.capitalize() for word in result.split())

def normalize_text(text):
    """
    Normaliza un texto eliminando acentos y convirtiéndolo a minúsculas
    para facilitar búsquedas insensibles a acentos y mayúsculas/minúsculas
    """
    if not text:
        return ""

    # Convertir a minúsculas
    text = text.lower()

    # Normalizar caracteres Unicode (NFD descompone los caracteres acentuados)
    text = unicodedata.normalize('NFD', text)

    # Eliminar los caracteres no ASCII (como los acentos)
    text = ''.join(c for c in text if not unicodedata.combining(c))

    return text

def tokenize_name(name):
    """
    Divide un nombre en tokens (palabras) y los normaliza

    Args:
        name: Nombre a tokenizar

    Returns:
        Lista de tokens normalizados
    """
    if not name:
        return []

    # Normalizar el nombre
    normalized_name = normalize_text(name)

    # Dividir en palabras y filtrar palabras vacías
    tokens = [token for token in normalized_name.split() if token]

    return tokens

def is_name_match(query, full_name, partial_match=True):
    """
    Verifica si una consulta coincide con un nombre completo

    Args:
        query: Consulta a buscar
        full_name: Nombre completo donde buscar
        partial_match: Si se permite coincidencia parcial

    Returns:
        True si hay coincidencia, False en caso contrario
    """
    # Tokenizar la consulta y el nombre completo
    query_tokens = tokenize_name(query)
    name_tokens = tokenize_name(full_name)

    if not query_tokens or not name_tokens:
        return False

    if partial_match:
        # Verificar si todos los tokens de la consulta están en el nombre completo
        return all(any(query_token in name_token for name_token in name_tokens) or
                  any(query_token == name_token for name_token in name_tokens)
                  for query_token in query_tokens)
    else:
        # Para coincidencia exacta, verificar si los conjuntos de tokens son iguales
        # o si la consulta normalizada es igual al nombre normalizado
        return set(query_tokens) == set(name_tokens) or normalize_text(query) == normalize_text(full_name)

def is_valid_curp(curp):
    """Verifica si un CURP tiene el formato correcto"""
    if not curp:
        return False

    # Patrón básico de CURP (18 caracteres alfanuméricos)
    pattern = r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]\d$'
    return bool(re.match(pattern, curp))

def backup_database():
    """Crea una copia de seguridad de la base de datos"""
    try:
        # Crear directorio de respaldos si no existe
        backup_dir = os.path.join(Config.BASE_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        # Generar nombre de archivo con timestamp
        timestamp = generate_timestamp()
        backup_file = os.path.join(backup_dir, f"alumnos_backup_{timestamp}.db")

        # Copiar la base de datos
        shutil.copy2(Config.DB_PATH, backup_file)

        print(f"Respaldo creado: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"Error al crear respaldo de la base de datos: {e}")
        return None

def clean_temp_files(directory=None, max_age_days=7, file_patterns=None):
    """
    Limpia archivos temporales en un directorio

    Args:
        directory: Directorio a limpiar (por defecto, el directorio de salida)
        max_age_days: Edad máxima de los archivos en días
        file_patterns: Lista de patrones de nombre de archivo a eliminar (por defecto, archivos HTML)

    Returns:
        Número de archivos eliminados
    """
    try:
        # Usar el directorio de salida por defecto si no se especifica otro
        if not directory:
            directory = Config.OUTPUT_DIR

        # Patrones de archivo por defecto
        if not file_patterns:
            file_patterns = ["*.html", "preview_*.pdf"]

        # Calcular la fecha límite
        now = datetime.now()
        max_age = now - timedelta(days=max_age_days)

        # Contador de archivos eliminados
        deleted_count = 0

        # Recorrer todos los archivos en el directorio
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                # Verificar si el archivo coincide con alguno de los patrones
                if any(fnmatch.fnmatch(file, pattern) for pattern in file_patterns):
                    # Verificar la fecha de modificación
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < max_age:
                        try:
                            os.unlink(file_path)
                            deleted_count += 1
                            print(f"Archivo temporal eliminado: {file_path}")
                        except Exception as e:
                            print(f"Error al eliminar archivo temporal {file_path}: {e}")

        return deleted_count
    except Exception as e:
        print(f"Error al limpiar archivos temporales: {e}")
        return 0
