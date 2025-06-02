"""
Gestor de base de datos para operaciones administrativas
"""
import os
import sqlite3
import shutil
import json
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from app.core.config import Config
from app.core.executable_paths import get_path_manager

class DatabaseManager:
    """Gestor de base de datos para operaciones administrativas"""

    def __init__(self, db_path=None):
        """
        Inicializa el gestor de base de datos

        Args:
            db_path: Ruta a la base de datos (opcional)
        """
        if db_path:
            self.db_path = db_path
        else:
            # Usar gestor de rutas para obtener la ruta correcta
            path_manager = get_path_manager()
            self.db_path = str(path_manager.get_database_path())

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def get_all_tables(self) -> List[str]:
        """
        Obtiene todas las tablas de la base de datos

        Returns:
            Lista de nombres de tablas
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene información sobre una tabla

        Args:
            table_name: Nombre de la tabla

        Returns:
            Lista de diccionarios con información de las columnas
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in self.cursor.fetchall():
            columns.append({
                'cid': row['cid'],
                'name': row['name'],
                'type': row['type'],
                'notnull': row['notnull'],
                'dflt_value': row['dflt_value'],
                'pk': row['pk']
            })
        return columns

    def get_table_row_count(self, table_name: str) -> int:
        """
        Obtiene el número de filas en una tabla

        Args:
            table_name: Nombre de la tabla

        Returns:
            Número de filas
        """
        self.cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        return self.cursor.fetchone()['count']

    def truncate_table(self, table_name: str) -> Tuple[bool, str]:
        """
        Elimina todos los registros de una tabla

        Args:
            table_name: Nombre de la tabla

        Returns:
            Tupla con (éxito, mensaje)
        """
        try:
            self.cursor.execute(f"DELETE FROM {table_name}")

            # Reiniciar el contador de autoincremento si existe
            self.cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")

            self.conn.commit()
            return True, f"Tabla {table_name} vaciada correctamente"
        except Exception as e:
            return False, f"Error al vaciar tabla {table_name}: {str(e)}"

    def reset_database(self) -> List[Tuple[str, bool, str]]:
        """
        Elimina todos los registros de todas las tablas

        Returns:
            Lista de tuplas con (tabla, éxito, mensaje)
        """
        tables = self.get_all_tables()
        results = []

        for table in tables:
            success, message = self.truncate_table(table)
            results.append((table, success, message))

        return results

    def backup_database(self) -> Tuple[bool, str, Optional[str]]:
        """
        Crea una copia de seguridad de la base de datos

        Returns:
            Tupla con (éxito, mensaje, ruta_backup)
        """
        try:
            # Usar gestor de rutas para directorio de backups
            path_manager = get_path_manager()
            backup_dir = path_manager.get_data_dir() / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"alumnos_backup_{timestamp}.db"

            # Cerrar la conexión actual para evitar problemas
            self.close()

            # Copiar la base de datos
            shutil.copy2(self.db_path, str(backup_file))

            # Reabrir la conexión
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

            return True, f"Respaldo creado: {backup_file}", str(backup_file)
        except Exception as e:
            return False, f"Error al crear respaldo: {str(e)}", None

    def restore_database(self, backup_path: str) -> Tuple[bool, str]:
        """
        Restaura la base de datos desde una copia de seguridad

        Args:
            backup_path: Ruta al archivo de respaldo

        Returns:
            Tupla con (éxito, mensaje)
        """
        try:
            # Verificar que el archivo de respaldo existe
            if not os.path.exists(backup_path):
                return False, f"El archivo de respaldo {backup_path} no existe"

            # Cerrar la conexión actual
            self.close()

            # Hacer una copia de seguridad antes de restaurar
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = os.path.join(
                os.path.dirname(self.db_path),
                "backups",
                f"pre_restore_backup_{timestamp}.db"
            )
            os.makedirs(os.path.dirname(pre_restore_backup), exist_ok=True)
            shutil.copy2(self.db_path, pre_restore_backup)

            # Restaurar la base de datos
            shutil.copy2(backup_path, self.db_path)

            # Reabrir la conexión
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

            return True, f"Base de datos restaurada desde {backup_path}"
        except Exception as e:
            return False, f"Error al restaurar base de datos: {str(e)}"

    def get_database_info(self) -> Dict[str, Any]:
        """
        Obtiene información general sobre la base de datos

        Returns:
            Diccionario con información de la base de datos
        """
        tables = self.get_all_tables()
        table_info = {}

        for table in tables:
            columns = self.get_table_info(table)
            row_count = self.get_table_row_count(table)

            table_info[table] = {
                'columns': columns,
                'row_count': row_count
            }

        # Información del archivo
        file_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        file_size_kb = file_size / 1024
        file_modified = datetime.fromtimestamp(os.path.getmtime(self.db_path)).strftime("%Y-%m-%d %H:%M:%S")

        return {
            'tables': table_info,
            'file_path': self.db_path,
            'file_size': f"{file_size_kb:.2f} KB",
            'file_modified': file_modified
        }

    def close(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
