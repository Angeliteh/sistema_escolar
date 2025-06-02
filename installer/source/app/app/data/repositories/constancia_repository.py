"""
Repositorio para acceso a datos de constancias
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.data.models.constancia import Constancia
from app.core.config import Config

class ConstanciaRepository:
    """Repositorio para acceso a datos de constancias"""

    def __init__(self, db_connection=None):
        """
        Inicializa el repositorio

        Args:
            db_connection: Conexión a la base de datos (opcional)
        """
        if db_connection:
            self.conn = db_connection
        else:
            self.conn = sqlite3.connect(Config.DB_PATH)
            self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

    def get_by_id(self, constancia_id: int) -> Optional[Constancia]:
        """
        Obtiene una constancia por su ID

        Args:
            constancia_id: ID de la constancia

        Returns:
            Objeto Constancia o None si no existe
        """
        self.cursor.execute("""
        SELECT id, alumno_id, tipo, ruta_archivo, fecha_generacion
        FROM constancias
        WHERE id = ?
        """, (constancia_id,))

        row = self.cursor.fetchone()
        if not row:
            return None

        return Constancia(
            id=row['id'],
            alumno_id=row['alumno_id'],
            tipo=row['tipo'],
            ruta_archivo=row['ruta_archivo'],
            fecha_generacion=row['fecha_generacion']
        )

    def get_by_alumno(self, alumno_id: int) -> List[Constancia]:
        """
        Obtiene constancias por ID de alumno

        Args:
            alumno_id: ID del alumno

        Returns:
            Lista de objetos Constancia
        """
        self.cursor.execute("""
        SELECT id, alumno_id, tipo, ruta_archivo, fecha_generacion
        FROM constancias
        WHERE alumno_id = ?
        ORDER BY fecha_generacion DESC
        """, (alumno_id,))

        rows = self.cursor.fetchall()
        return [Constancia(
            id=row['id'],
            alumno_id=row['alumno_id'],
            tipo=row['tipo'],
            ruta_archivo=row['ruta_archivo'],
            fecha_generacion=row['fecha_generacion']
        ) for row in rows]

    def save(self, constancia: Constancia) -> Constancia:
        """
        Guarda una constancia en la base de datos

        Args:
            constancia: Objeto Constancia a guardar

        Returns:
            Objeto Constancia con ID actualizado
        """
        if constancia.id:
            # Actualizar constancia existente
            self.cursor.execute("""
            UPDATE constancias
            SET alumno_id = ?, tipo = ?, ruta_archivo = ?
            WHERE id = ?
            """, (
                constancia.alumno_id,
                constancia.tipo,
                constancia.ruta_archivo,
                constancia.id
            ))
        else:
            # Insertar nueva constancia
            self.cursor.execute("""
            INSERT INTO constancias (alumno_id, tipo, ruta_archivo)
            VALUES (?, ?, ?)
            """, (
                constancia.alumno_id,
                constancia.tipo,
                constancia.ruta_archivo
            ))
            constancia.id = self.cursor.lastrowid

        self.conn.commit()
        return constancia

    def delete(self, constancia_id: int) -> bool:
        """
        Elimina una constancia de la base de datos

        Args:
            constancia_id: ID de la constancia a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            self.cursor.execute("DELETE FROM constancias WHERE id = ?", (constancia_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar constancia: {e}")
            return False

    def list_recent(self, limit: int = 10) -> List[Constancia]:
        """
        Lista las constancias más recientes

        Args:
            limit: Límite de resultados

        Returns:
            Lista de objetos Constancia
        """
        self.cursor.execute("""
        SELECT id, alumno_id, tipo, ruta_archivo, fecha_generacion
        FROM constancias
        ORDER BY fecha_generacion DESC
        LIMIT ?
        """, (limit,))

        rows = self.cursor.fetchall()
        return [Constancia(
            id=row['id'],
            alumno_id=row['alumno_id'],
            tipo=row['tipo'],
            ruta_archivo=row['ruta_archivo'],
            fecha_generacion=row['fecha_generacion']
        ) for row in rows]

    def count_by_tipo(self) -> Dict[str, int]:
        """
        Cuenta el número de constancias por tipo

        Returns:
            Diccionario con el conteo por tipo
        """
        self.cursor.execute("""
        SELECT tipo, COUNT(*) as count
        FROM constancias
        GROUP BY tipo
        """)

        rows = self.cursor.fetchall()
        return {row['tipo']: row['count'] for row in rows}

    def delete_by_alumno(self, alumno_id: int) -> bool:
        """
        Elimina todas las constancias de un alumno

        Args:
            alumno_id: ID del alumno

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            self.cursor.execute("DELETE FROM constancias WHERE alumno_id = ?", (alumno_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar constancias del alumno {alumno_id}: {e}")
            return False

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
