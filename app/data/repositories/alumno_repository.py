"""
Repositorio para acceso a datos de alumnos
"""
import sqlite3
from typing import List, Optional
from app.data.models.alumno import Alumno
from app.core.config import Config

class AlumnoRepository:
    """Repositorio para acceso a datos de alumnos"""

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

    def get_by_id(self, alumno_id: int) -> Optional[Alumno]:
        """
        Obtiene un alumno por su ID

        Args:
            alumno_id: ID del alumno

        Returns:
            Objeto Alumno o None si no existe
        """
        self.cursor.execute("""
        SELECT id, curp, nombre, matricula, fecha_nacimiento, fecha_registro
        FROM alumnos
        WHERE id = ?
        """, (alumno_id,))

        row = self.cursor.fetchone()
        if not row:
            return None

        return Alumno(
            id=row['id'],
            curp=row['curp'],
            nombre=row['nombre'],
            matricula=row['matricula'],
            fecha_nacimiento=row['fecha_nacimiento'],
            fecha_registro=row['fecha_registro']
        )

    def get_by_curp(self, curp: str) -> Optional[Alumno]:
        """
        Obtiene un alumno por su CURP

        Args:
            curp: CURP del alumno

        Returns:
            Objeto Alumno o None si no existe
        """
        self.cursor.execute("""
        SELECT id, curp, nombre, matricula, fecha_nacimiento, fecha_registro
        FROM alumnos
        WHERE curp = ?
        """, (curp,))

        row = self.cursor.fetchone()
        if not row:
            return None

        return Alumno(
            id=row['id'],
            curp=row['curp'],
            nombre=row['nombre'],
            matricula=row['matricula'],
            fecha_nacimiento=row['fecha_nacimiento'],
            fecha_registro=row['fecha_registro']
        )

    def save(self, alumno: Alumno) -> Alumno:
        """
        Guarda un alumno en la base de datos

        Args:
            alumno: Objeto Alumno a guardar

        Returns:
            Objeto Alumno con ID actualizado
        """
        if alumno.id:
            # Actualizar alumno existente
            self.cursor.execute("""
            UPDATE alumnos
            SET curp = ?, nombre = ?, matricula = ?, fecha_nacimiento = ?
            WHERE id = ?
            """, (
                alumno.curp,
                alumno.nombre,
                alumno.matricula,
                alumno.fecha_nacimiento,
                alumno.id
            ))
        else:
            # Insertar nuevo alumno
            self.cursor.execute("""
            INSERT INTO alumnos (curp, nombre, matricula, fecha_nacimiento)
            VALUES (?, ?, ?, ?)
            """, (
                alumno.curp,
                alumno.nombre,
                alumno.matricula,
                alumno.fecha_nacimiento
            ))
            alumno.id = self.cursor.lastrowid

        self.conn.commit()
        return alumno

    def delete(self, alumno_id: int) -> bool:
        """
        Elimina un alumno de la base de datos

        Args:
            alumno_id: ID del alumno a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            self.cursor.execute("DELETE FROM alumnos WHERE id = ?", (alumno_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar alumno: {e}")
            return False

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Alumno]:
        """
        Lista todos los alumnos

        Args:
            limit: Límite de resultados
            offset: Desplazamiento para paginación

        Returns:
            Lista de objetos Alumno
        """
        self.cursor.execute("""
        SELECT id, curp, nombre, matricula, fecha_nacimiento, fecha_registro
        FROM alumnos
        ORDER BY nombre
        LIMIT ? OFFSET ?
        """, (limit, offset))

        rows = self.cursor.fetchall()
        return [Alumno(
            id=row['id'],
            curp=row['curp'],
            nombre=row['nombre'],
            matricula=row['matricula'],
            fecha_nacimiento=row['fecha_nacimiento'],
            fecha_registro=row['fecha_registro']
        ) for row in rows]

    def search(self, query: str, limit: int = 100) -> List[Alumno]:
        """
        Busca alumnos por nombre o CURP

        Args:
            query: Texto a buscar
            limit: Límite de resultados

        Returns:
            Lista de objetos Alumno que coinciden con la búsqueda
        """
        # Preparar el término de búsqueda para LIKE
        search_term = f"%{query}%"

        self.cursor.execute("""
        SELECT id, curp, nombre, matricula, fecha_nacimiento, fecha_registro
        FROM alumnos
        WHERE nombre LIKE ? OR curp LIKE ?
        ORDER BY nombre
        LIMIT ?
        """, (search_term, search_term, limit))

        rows = self.cursor.fetchall()
        return [Alumno(
            id=row['id'],
            curp=row['curp'],
            nombre=row['nombre'],
            matricula=row['matricula'],
            fecha_nacimiento=row['fecha_nacimiento'],
            fecha_registro=row['fecha_registro']
        ) for row in rows]

    def count(self) -> int:
        """
        Cuenta el número total de alumnos

        Returns:
            Número total de alumnos
        """
        self.cursor.execute("SELECT COUNT(*) FROM alumnos")
        return self.cursor.fetchone()[0]

    def update(self, alumno: Alumno) -> Alumno:
        """
        Actualiza un alumno existente en la base de datos

        Args:
            alumno: Objeto Alumno a actualizar

        Returns:
            Objeto Alumno actualizado
        """
        if not alumno.id:
            raise ValueError("No se puede actualizar un alumno sin ID")

        self.cursor.execute("""
        UPDATE alumnos
        SET curp = ?, nombre = ?, matricula = ?, fecha_nacimiento = ?
        WHERE id = ?
        """, (
            alumno.curp,
            alumno.nombre,
            alumno.matricula,
            alumno.fecha_nacimiento,
            alumno.id
        ))

        self.conn.commit()
        return alumno

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
