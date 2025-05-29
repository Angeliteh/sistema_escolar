"""
Ejecutor de consultas SQL generadas por IA
"""
import sqlite3
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from app.core.logging import get_logger

@dataclass
class QueryResult:
    """Resultado de una consulta SQL"""
    success: bool
    data: List[Dict[str, Any]]
    message: str
    query_executed: str
    row_count: int

class SQLExecutor:
    """Ejecutor seguro de consultas SQL"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger(__name__)

        # Palabras clave permitidas (solo SELECT)
        self.allowed_keywords = {
            'select', 'from', 'where', 'join', 'left', 'right', 'inner', 'outer',
            'on', 'and', 'or', 'like', 'in', 'not', 'null', 'is', 'order', 'by',
            'group', 'having', 'limit', 'offset', 'as', 'distinct', 'union',
            'case', 'when', 'then', 'else', 'end'
        }

        # Palabras clave prohibidas (modificación de datos)
        self.forbidden_keywords = {
            'insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate',
            'replace', 'merge', 'exec', 'execute', 'sp_', 'xp_'
        }

    def execute_query(self, sql_query: str, limit: int = 100) -> QueryResult:
        """
        Ejecuta una consulta SQL de forma segura

        Args:
            sql_query: Consulta SQL a ejecutar
            limit: Límite máximo de resultados

        Returns:
            QueryResult con los resultados
        """
        try:
            # Validar seguridad de la consulta
            is_safe, error_msg = self._validate_query_safety(sql_query)
            if not is_safe:
                return QueryResult(
                    success=False,
                    data=[],
                    message=f"Consulta no segura: {error_msg}",
                    query_executed="",
                    row_count=0
                )

            # Añadir LIMIT si no existe
            sql_query = self._ensure_limit(sql_query, limit)

            # Ejecutar consulta
            self.logger.info(f"Ejecutando SQL en: {self.db_path}")
            self.logger.debug(f"SQL Query: {sql_query}")

            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(sql_query)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            data = [dict(row) for row in rows]

            self.logger.info(f"Resultados obtenidos: {len(data)}")
            self.logger.debug(f"Datos: {data}")

            conn.close()

            return QueryResult(
                success=True,
                data=data,
                message=f"Consulta ejecutada exitosamente. {len(data)} resultados.",
                query_executed=sql_query,
                row_count=len(data)
            )

        except sqlite3.Error as e:
            return QueryResult(
                success=False,
                data=[],
                message=f"Error SQL: {str(e)}",
                query_executed=sql_query,
                row_count=0
            )
        except Exception as e:
            return QueryResult(
                success=False,
                data=[],
                message=f"Error inesperado: {str(e)}",
                query_executed=sql_query,
                row_count=0
            )

    def _validate_query_safety(self, sql_query: str) -> Tuple[bool, str]:
        """Valida que la consulta sea segura (solo SELECT)"""
        # Convertir a minúsculas para análisis
        query_lower = sql_query.lower().strip()

        # Debe empezar con SELECT
        if not query_lower.startswith('select'):
            return False, "Solo se permiten consultas SELECT"

        # Buscar palabras clave prohibidas
        words = re.findall(r'\b\w+\b', query_lower)
        for word in words:
            if word in self.forbidden_keywords:
                return False, f"Palabra clave prohibida: {word}"

        # Verificar que no haya múltiples statements
        if ';' in sql_query and not sql_query.strip().endswith(';'):
            return False, "No se permiten múltiples statements"

        # Verificar que no haya comentarios maliciosos
        if '--' in sql_query or '/*' in sql_query:
            return False, "No se permiten comentarios en las consultas"

        return True, ""

    def _ensure_limit(self, sql_query: str, max_limit: int) -> str:
        """Asegura que la consulta tenga un LIMIT apropiado"""
        query_lower = sql_query.lower()

        # NO añadir LIMIT a consultas COUNT, SUM, AVG, etc.
        if any(func in query_lower for func in ['count(', 'sum(', 'avg(', 'max(', 'min(']):
            return sql_query.rstrip(';')

        # Si ya tiene LIMIT, verificar que no sea excesivo
        if 'limit' in query_lower:
            # Extraer el valor del LIMIT existente
            limit_match = re.search(r'limit\s+(\d+)', query_lower)
            if limit_match:
                existing_limit = int(limit_match.group(1))
                if existing_limit > max_limit:
                    # Reemplazar con el límite máximo
                    sql_query = re.sub(r'limit\s+\d+', f'LIMIT {max_limit}', sql_query, flags=re.IGNORECASE)
            return sql_query

        # Si no tiene LIMIT, añadirlo (solo para consultas SELECT normales)
        sql_query = sql_query.rstrip(';')
        return f"{sql_query} LIMIT {max_limit}"

    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    def generate_statistics(self, user_query: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Genera estadísticas básicas del sistema escolar
        """
        try:
            print("📊 Generando estadísticas del sistema...")

            # Ejecutar consultas para estadísticas básicas
            stats_queries = {
                "total_alumnos": "SELECT COUNT(*) as total FROM alumnos",
                "por_grado": """
                    SELECT de.grado, COUNT(*) as cantidad
                    FROM datos_escolares de
                    GROUP BY de.grado
                    ORDER BY de.grado
                """,
                "por_turno": """
                    SELECT de.turno, COUNT(*) as cantidad
                    FROM datos_escolares de
                    GROUP BY de.turno
                """,
                "con_calificaciones": """
                    SELECT COUNT(*) as total
                    FROM datos_escolares
                    WHERE calificaciones IS NOT NULL
                    AND calificaciones != ''
                    AND calificaciones != '[]'
                """,
                "sin_calificaciones": """
                    SELECT COUNT(*) as total
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NULL
                    OR de.calificaciones = ''
                    OR de.calificaciones = '[]'
                """
            }

            # Ejecutar todas las consultas
            stats_results = {}
            for stat_name, query in stats_queries.items():
                try:
                    result = self.execute_query(query)
                    if result.success:
                        stats_results[stat_name] = result.data
                    else:
                        print(f"Error en consulta {stat_name}: {result.message}")
                        stats_results[stat_name] = []
                except Exception as e:
                    print(f"Error en consulta {stat_name}: {e}")
                    stats_results[stat_name] = []

            # Formatear respuesta de estadísticas
            response = self._format_statistics_response(stats_results)
            return True, response, {"statistics": stats_results}

        except Exception as e:
            print(f"Error generando estadísticas: {e}")
            return False, "No pude generar las estadísticas del sistema en este momento. ¿Te gustaría consultar información específica de alumnos?", {}

    def _format_statistics_response(self, stats_results: Dict[str, List[Dict]]) -> str:
        """
        Formatea los resultados de estadísticas en una respuesta natural
        """
        try:
            # Extraer datos básicos
            total_alumnos = 0
            if stats_results.get("total_alumnos") and len(stats_results["total_alumnos"]) > 0:
                total_alumnos = stats_results["total_alumnos"][0].get("total", 0)

            # Estadísticas por grado
            grados_info = []
            if stats_results.get("por_grado"):
                for row in stats_results["por_grado"]:
                    grado = row.get("grado", "?")
                    cantidad = row.get("cantidad", 0)
                    grados_info.append(f"{grado}° ({cantidad})")

            # Estadísticas por turno
            turnos_info = []
            if stats_results.get("por_turno"):
                for row in stats_results["por_turno"]:
                    turno = row.get("turno", "?")
                    cantidad = row.get("cantidad", 0)
                    turnos_info.append(f"{turno.title()} ({cantidad})")

            # Calificaciones
            con_calificaciones = 0
            sin_calificaciones = 0
            if stats_results.get("con_calificaciones") and len(stats_results["con_calificaciones"]) > 0:
                con_calificaciones = stats_results["con_calificaciones"][0].get("total", 0)
            if stats_results.get("sin_calificaciones") and len(stats_results["sin_calificaciones"]) > 0:
                sin_calificaciones = stats_results["sin_calificaciones"][0].get("total", 0)

            # Calcular porcentajes
            porcentaje_con_calif = 0
            porcentaje_sin_calif = 0
            if total_alumnos > 0:
                porcentaje_con_calif = (con_calificaciones / total_alumnos) * 100
                porcentaje_sin_calif = (sin_calificaciones / total_alumnos) * 100

            # Formatear respuesta
            response = f"""📊 ESTADÍSTICAS DEL SISTEMA ESCOLAR 2024-2025:

👥 Total de alumnos: {total_alumnos} estudiantes registrados
📚 Distribución por grado: {', '.join(grados_info) if grados_info else 'No disponible'}
🕐 Distribución por turno: {', '.join(turnos_info) if turnos_info else 'No disponible'}

📋 Estado de calificaciones:
✅ Con calificaciones: {con_calificaciones} alumnos ({porcentaje_con_calif:.1f}%)
❌ Sin calificaciones: {sin_calificaciones} alumnos ({porcentaje_sin_calif:.1f}%)

Esta información te ayuda a tener una visión general del estado académico de la escuela PROF. MAXIMO GAMIZ FERNANDEZ. ¿Te gustaría consultar información específica de algún grado o generar constancias individuales?"""

            return response

        except Exception as e:
            print(f"Error formateando estadísticas: {e}")
            return "📊 Estadísticas básicas disponibles. ¿Te gustaría consultar información específica de alumnos?"

class SQLQueryBuilder:
    """Constructor de consultas SQL basado en patrones comunes"""

    @staticmethod
    def build_search_by_name(name: str) -> str:
        """Construye consulta para buscar por nombre"""
        return f"""
        SELECT a.id, a.nombre, a.curp, a.matricula, a.fecha_nacimiento,
               de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela
        FROM alumnos a
        LEFT JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE a.nombre LIKE '%{name}%'
        ORDER BY a.nombre
        """

    @staticmethod
    def build_search_by_criteria(criterio: str, valor: str) -> str:
        """Construye consulta para buscar por criterio específico"""
        return f"""
        SELECT a.id, a.nombre, a.curp, a.matricula,
               de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela
        FROM alumnos a
        JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE de.{criterio} = '{valor}'
        ORDER BY a.nombre
        """

    @staticmethod
    def build_student_details(name: str) -> str:
        """Construye consulta para detalles completos de un alumno"""
        return f"""
        SELECT a.*, de.ciclo_escolar, de.grado, de.grupo, de.turno,
               de.escuela, de.cct, de.calificaciones
        FROM alumnos a
        LEFT JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE a.nombre LIKE '%{name}%'
        ORDER BY de.id DESC
        LIMIT 1
        """

    @staticmethod
    def build_list_all_students() -> str:
        """Construye consulta para listar todos los alumnos"""
        return """
        SELECT a.id, a.nombre, a.curp, a.matricula,
               de.grado, de.grupo, de.turno, de.ciclo_escolar
        FROM alumnos a
        LEFT JOIN datos_escolares de ON a.id = de.alumno_id
        ORDER BY a.nombre
        """

# 🆕 INSTANCIAS POR HILO PARA EVITAR PROBLEMAS DE SQLITE THREADING
import threading
_thread_local_executors = threading.local()

def get_sql_executor(db_path: str = None) -> SQLExecutor:
    """🆕 OBTIENE INSTANCIA DEL EJECUTOR SQL ESPECÍFICA PARA CADA HILO"""

    # Verificar si ya existe una instancia para este hilo
    if not hasattr(_thread_local_executors, 'executor'):
        # Crear nueva instancia para este hilo
        if db_path is None:
            from app.core.config import Config
            db_path = Config.DB_PATH

        _thread_local_executors.executor = SQLExecutor(db_path)

        # Log para debugging
        try:
            from app.core.logging import get_logger
            logger = get_logger(__name__)
            logger.debug(f"🔄 Nueva instancia SQLExecutor creada para hilo {threading.current_thread().ident}")
        except:
            pass

    return _thread_local_executors.executor
