"""
Repositorio para acceso a datos escolares
"""
import sqlite3
import json
from typing import List, Optional, Dict, Any
from app.data.models.datos_escolares import DatosEscolares
from app.core.config import Config

class DatosEscolaresRepository:
    """Repositorio para acceso a datos escolares"""

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

    def get_by_id(self, datos_id: int) -> Optional[DatosEscolares]:
        """
        Obtiene datos escolares por su ID

        Args:
            datos_id: ID de los datos escolares

        Returns:
            Objeto DatosEscolares o None si no existe
        """
        self.cursor.execute("""
        SELECT id, alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones
        FROM datos_escolares
        WHERE id = ?
        """, (datos_id,))

        row = self.cursor.fetchone()
        if not row:
            return None

        # Convertir calificaciones de JSON a lista
        calificaciones = []
        if row['calificaciones']:
            try:
                calificaciones = json.loads(row['calificaciones'])
            except json.JSONDecodeError:
                pass

        return DatosEscolares(
            id=row['id'],
            alumno_id=row['alumno_id'],
            ciclo_escolar=row['ciclo_escolar'],
            grado=row['grado'],
            grupo=row['grupo'],
            turno=row['turno'],
            escuela=row['escuela'],
            cct=row['cct'],
            calificaciones=calificaciones
        )

    def get_by_alumno(self, alumno_id: int, latest_only: bool = False) -> List[DatosEscolares]:
        """
        Obtiene datos escolares por ID de alumno

        Args:
            alumno_id: ID del alumno
            latest_only: Si es True, devuelve solo el registro más reciente

        Returns:
            Lista de objetos DatosEscolares
        """
        if latest_only:
            self.cursor.execute("""
            SELECT id, alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones
            FROM datos_escolares
            WHERE alumno_id = ?
            ORDER BY id DESC
            LIMIT 1
            """, (alumno_id,))

            row = self.cursor.fetchone()
            if not row:
                return []

            # Convertir calificaciones de JSON a lista
            calificaciones = []
            if row['calificaciones']:
                try:
                    calificaciones = json.loads(row['calificaciones'])
                except json.JSONDecodeError:
                    pass

            return [DatosEscolares(
                id=row['id'],
                alumno_id=row['alumno_id'],
                ciclo_escolar=row['ciclo_escolar'],
                grado=row['grado'],
                grupo=row['grupo'],
                turno=row['turno'],
                escuela=row['escuela'],
                cct=row['cct'],
                calificaciones=calificaciones
            )]
        else:
            self.cursor.execute("""
            SELECT id, alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones
            FROM datos_escolares
            WHERE alumno_id = ?
            ORDER BY id DESC
            """, (alumno_id,))

            rows = self.cursor.fetchall()
            result = []

            for row in rows:
                # Convertir calificaciones de JSON a lista
                calificaciones = []
                if row['calificaciones']:
                    try:
                        calificaciones = json.loads(row['calificaciones'])
                    except json.JSONDecodeError:
                        pass

                result.append(DatosEscolares(
                    id=row['id'],
                    alumno_id=row['alumno_id'],
                    ciclo_escolar=row['ciclo_escolar'],
                    grado=row['grado'],
                    grupo=row['grupo'],
                    turno=row['turno'],
                    escuela=row['escuela'],
                    cct=row['cct'],
                    calificaciones=calificaciones
                ))

            return result

    def save(self, datos: DatosEscolares) -> DatosEscolares:
        """
        Guarda datos escolares en la base de datos

        Args:
            datos: Objeto DatosEscolares a guardar

        Returns:
            Objeto DatosEscolares con ID actualizado
        """
        # Convertir calificaciones a JSON
        calificaciones_json = json.dumps(datos.calificaciones)

        if datos.id:
            # Actualizar datos existentes
            self.cursor.execute("""
            UPDATE datos_escolares
            SET alumno_id = ?, ciclo_escolar = ?, grado = ?, grupo = ?,
                turno = ?, escuela = ?, cct = ?, calificaciones = ?
            WHERE id = ?
            """, (
                datos.alumno_id,
                datos.ciclo_escolar,
                datos.grado,
                datos.grupo,
                datos.turno,
                datos.escuela,
                datos.cct,
                calificaciones_json,
                datos.id
            ))
        else:
            # Insertar nuevos datos
            self.cursor.execute("""
            INSERT INTO datos_escolares
            (alumno_id, ciclo_escolar, grado, grupo, turno, escuela, cct, calificaciones)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos.alumno_id,
                datos.ciclo_escolar,
                datos.grado,
                datos.grupo,
                datos.turno,
                datos.escuela,
                datos.cct,
                calificaciones_json
            ))
            datos.id = self.cursor.lastrowid

        self.conn.commit()
        return datos

    def delete(self, datos_id: int) -> bool:
        """
        Elimina datos escolares de la base de datos

        Args:
            datos_id: ID de los datos escolares a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            self.cursor.execute("DELETE FROM datos_escolares WHERE id = ?", (datos_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar datos escolares: {e}")
            return False

    def delete_by_alumno(self, alumno_id: int) -> bool:
        """
        Elimina todos los datos escolares de un alumno

        Args:
            alumno_id: ID del alumno

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            self.cursor.execute("DELETE FROM datos_escolares WHERE alumno_id = ?", (alumno_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar datos escolares del alumno {alumno_id}: {e}")
            return False

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
