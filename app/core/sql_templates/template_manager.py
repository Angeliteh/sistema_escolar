"""
SQLTemplateManager - Sistema de plantillas SQL predefinidas
Reemplaza la generación dinámica de SQL con plantillas probadas y confiables
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class SQLTemplate:
    """Representa una plantilla SQL con sus metadatos"""
    name: str
    description: str
    sql: str
    parameters: List[str]
    returns_multiple: bool = True
    requires_exact_match: bool = False

@dataclass
class TemplateSelection:
    """Resultado de la selección de plantilla"""
    template: SQLTemplate
    parameters: Dict[str, Any]
    confidence: float

class SQLTemplateManager:
    """
    Gestor de plantillas SQL predefinidas
    Permite al LLM seleccionar plantillas apropiadas en lugar de generar SQL
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates = self._initialize_templates()
        self.logger.info(f"✅ SQLTemplateManager inicializado con {len(self.templates)} plantillas")

    def _initialize_templates(self) -> Dict[str, SQLTemplate]:
        """Inicializa todas las plantillas SQL disponibles"""

        templates = {}

        # 🔍 BÚSQUEDA UNIFICADA DE ALUMNO (SIEMPRE INFORMACIÓN COMPLETA)
        templates["buscar_alumno"] = SQLTemplate(
            name="buscar_alumno",
            description="Busca alumno por nombre con información completa",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct,
                       de.calificaciones
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE a.nombre LIKE '%{nombre}%'
                ORDER BY a.nombre
            """,
            parameters=["nombre"],
            returns_multiple=True
        )

        # 🎯 BÚSQUEDA EXACTA POR NOMBRE COMPLETO
        templates["buscar_alumno_exacto"] = SQLTemplate(
            name="buscar_alumno_exacto",
            description="Busca alumno por nombre exacto",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct,
                       de.calificaciones
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE UPPER(a.nombre) = UPPER('{nombre}')
                ORDER BY a.nombre
            """,
            parameters=["nombre"],
            returns_multiple=False,
            requires_exact_match=True
        )

        # 📋 FILTRAR POR GRADO
        templates["filtrar_por_grado"] = SQLTemplate(
            name="filtrar_por_grado",
            description="Lista alumnos de un grado específico",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE de.grado = {grado}
                ORDER BY a.nombre
            """,
            parameters=["grado"],
            returns_multiple=True
        )

        # 🏫 FILTRAR POR TURNO
        templates["filtrar_por_turno"] = SQLTemplate(
            name="filtrar_por_turno",
            description="Lista alumnos de un turno específico",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE UPPER(de.turno) = UPPER('{turno}')
                ORDER BY de.grado, de.grupo, a.nombre
            """,
            parameters=["turno"],
            returns_multiple=True
        )

        # 🎯 FILTRAR POR GRADO Y TURNO
        templates["filtrar_grado_turno"] = SQLTemplate(
            name="filtrar_grado_turno",
            description="Lista alumnos de un grado y turno específicos",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE de.grado = {grado} AND UPPER(de.turno) = UPPER('{turno}')
                ORDER BY de.grupo, a.nombre
            """,
            parameters=["grado", "turno"],
            returns_multiple=True
        )

        # 📊 CONTAR ALUMNOS TOTAL
        templates["contar_alumnos_total"] = SQLTemplate(
            name="contar_alumnos_total",
            description="Cuenta el total de alumnos registrados",
            sql="""
                SELECT COUNT(*) as total_alumnos
                FROM alumnos
            """,
            parameters=[],
            returns_multiple=False
        )

        # 📈 ESTADÍSTICAS POR GRADO
        templates["estadisticas_por_grado"] = SQLTemplate(
            name="estadisticas_por_grado",
            description="Muestra estadísticas de alumnos agrupados por grado",
            sql="""
                SELECT de.grado, COUNT(*) as total_alumnos,
                       COUNT(CASE WHEN de.turno = 'MATUTINO' THEN 1 END) as matutino,
                       COUNT(CASE WHEN de.turno = 'VESPERTINO' THEN 1 END) as vespertino
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE de.grado IS NOT NULL
                GROUP BY de.grado
                ORDER BY de.grado
            """,
            parameters=[],
            returns_multiple=True
        )

        # 🔍 BÚSQUEDA POR CURP
        templates["buscar_por_curp"] = SQLTemplate(
            name="buscar_por_curp",
            description="Busca alumno por CURP específico",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct,
                       de.calificaciones
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE UPPER(a.curp) = UPPER('{curp}')
            """,
            parameters=["curp"],
            returns_multiple=False
        )

        # 🎫 BÚSQUEDA POR MATRÍCULA
        templates["buscar_por_matricula"] = SQLTemplate(
            name="buscar_por_matricula",
            description="Busca alumno por matrícula específica",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct,
                       de.calificaciones
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE UPPER(a.matricula) = UPPER('{matricula}')
            """,
            parameters=["matricula"],
            returns_multiple=False
        )

        # 📚 FILTRAR POR GRUPO
        templates["filtrar_por_grupo"] = SQLTemplate(
            name="filtrar_por_grupo",
            description="Lista alumnos de un grupo específico",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE UPPER(de.grupo) = UPPER('{grupo}')
                ORDER BY de.grado, a.nombre
            """,
            parameters=["grupo"],
            returns_multiple=True
        )

        # 🎯 FILTRAR GRADO + GRUPO
        templates["filtrar_grado_grupo"] = SQLTemplate(
            name="filtrar_grado_grupo",
            description="Lista alumnos de un grado y grupo específicos",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE de.grado = {grado} AND UPPER(de.grupo) = UPPER('{grupo}')
                ORDER BY a.nombre
            """,
            parameters=["grado", "grupo"],
            returns_multiple=True
        )

        # 📊 ALUMNOS CON CALIFICACIONES
        templates["alumnos_con_calificaciones"] = SQLTemplate(
            name="alumnos_con_calificaciones",
            description="Lista alumnos que tienen calificaciones registradas",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE de.calificaciones IS NOT NULL
                  AND de.calificaciones != ''
                  AND de.calificaciones != '[]'
                ORDER BY de.grado, de.grupo, a.nombre
            """,
            parameters=[],
            returns_multiple=True
        )

        # ❌ ALUMNOS SIN CALIFICACIONES
        templates["alumnos_sin_calificaciones"] = SQLTemplate(
            name="alumnos_sin_calificaciones",
            description="Lista alumnos que NO tienen calificaciones registradas",
            sql="""
                SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento, a.fecha_registro,
                       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.escuela, de.cct
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE de.calificaciones IS NULL
                   OR de.calificaciones = ''
                   OR de.calificaciones = '[]'
                ORDER BY de.grado, de.grupo, a.nombre
            """,
            parameters=[],
            returns_multiple=True
        )

        return templates

    def get_available_templates(self) -> List[str]:
        """Retorna lista de plantillas disponibles"""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Optional[SQLTemplate]:
        """Obtiene información de una plantilla específica"""
        return self.templates.get(template_name)

    def select_template_for_query(self, user_query: str) -> Optional[TemplateSelection]:
        """
        Selecciona la plantilla más apropiada para una consulta de usuario
        Esta función será mejorada con LLM en la siguiente iteración
        """

        query_lower = user_query.lower()

        # 🔍 DETECCIÓN MEJORADA POR PALABRAS CLAVE

        # 🎯 PRIORIDAD 1: Filtros por grado + grupo (COMBINADO) - DETECTAR PRIMERO
        grado = self._extract_grade_from_query(user_query)
        grupo = self._extract_grupo_from_query(user_query)

        if grado and grupo:
            return TemplateSelection(
                template=self.templates["filtrar_grado_grupo"],
                parameters={"grado": grado, "grupo": grupo},
                confidence=0.9
            )

        # Filtros por grado solo
        if "grado" in query_lower and grado:
            return TemplateSelection(
                template=self.templates["filtrar_por_grado"],
                parameters={"grado": grado},
                confidence=0.8
            )

        # 🎯 DETECTAR PATRONES COMO "2do A", "3er B", etc.
        if grado and not "grado" in query_lower:
            # Si detectó grado sin la palabra "grado", probablemente es "2do A"
            if grupo:
                return TemplateSelection(
                    template=self.templates["filtrar_grado_grupo"],
                    parameters={"grado": grado, "grupo": grupo},
                    confidence=0.85
                )
            else:
                return TemplateSelection(
                    template=self.templates["filtrar_por_grado"],
                    parameters={"grado": grado},
                    confidence=0.8
                )

        # Filtros por turno
        if any(word in query_lower for word in ["turno", "matutino", "vespertino"]):
            turno = self._extract_turno_from_query(user_query)
            if turno:
                return TemplateSelection(
                    template=self.templates["filtrar_por_turno"],
                    parameters={"turno": turno},
                    confidence=0.8
                )

        # Búsqueda por CURP
        if "curp" in query_lower:
            curp = self._extract_curp_from_query(user_query)
            if curp:
                return TemplateSelection(
                    template=self.templates["buscar_por_curp"],
                    parameters={"curp": curp},
                    confidence=0.9
                )

        # Búsqueda por matrícula
        if any(word in query_lower for word in ["matricula", "matrícula"]):
            matricula = self._extract_matricula_from_query(user_query)
            if matricula:
                return TemplateSelection(
                    template=self.templates["buscar_por_matricula"],
                    parameters={"matricula": matricula},
                    confidence=0.9
                )

        # Filtros por grupo
        if "grupo" in query_lower:
            grupo = self._extract_grupo_from_query(user_query)
            grado = self._extract_grade_from_query(user_query)

            if grupo and grado:
                return TemplateSelection(
                    template=self.templates["filtrar_grado_grupo"],
                    parameters={"grado": grado, "grupo": grupo},
                    confidence=0.8
                )
            elif grupo:
                return TemplateSelection(
                    template=self.templates["filtrar_por_grupo"],
                    parameters={"grupo": grupo},
                    confidence=0.8
                )

        # Alumnos con/sin calificaciones
        if any(phrase in query_lower for phrase in ["con calificaciones", "tienen calificaciones"]):
            return TemplateSelection(
                template=self.templates["alumnos_con_calificaciones"],
                parameters={},
                confidence=0.8
            )

        if any(phrase in query_lower for phrase in ["sin calificaciones", "no tienen calificaciones"]):
            return TemplateSelection(
                template=self.templates["alumnos_sin_calificaciones"],
                parameters={},
                confidence=0.8
            )

        # Conteos
        if any(word in query_lower for word in ["cuántos", "total", "cantidad"]):
            return TemplateSelection(
                template=self.templates["contar_alumnos_total"],
                parameters={},
                confidence=0.7
            )

        # 🎯 ÚLTIMA PRIORIDAD: BÚSQUEDAS DE ALUMNOS POR NOMBRE (GENÉRICO)
        # Detectar cualquier búsqueda de alumno y usar plantilla unificada
        nombre = self._extract_name_from_query(user_query)
        if nombre:
            # 🔧 LÓGICA SIMPLIFICADA: Una sola plantilla para todas las búsquedas
            confidence = 0.95 if any(word in query_lower for word in ["información de", "datos de", "detalles de"]) else 0.9

            return TemplateSelection(
                template=self.templates["buscar_alumno"],
                parameters={"nombre": nombre},
                confidence=confidence
            )

        return None

    def _extract_name_from_query(self, query: str) -> Optional[str]:
        """Extrae nombre de la consulta (mejorado)"""
        words = query.split()

        # 🔍 PATRONES MEJORADOS DE BÚSQUEDA DE NOMBRES

        # Patrón 1: "busca a NOMBRE", "información de NOMBRE", etc.
        keywords = ["busca", "información", "datos", "de", "a", "buscar", "encuentra"]
        for i, word in enumerate(words):
            if word.lower() in keywords and i + 1 < len(words):
                name_parts = []
                for j in range(i + 1, len(words)):
                    # 🔧 MEJORADO: Aceptar cualquier palabra que parezca nombre
                    if len(words[j]) > 2 and words[j].isalpha():  # Palabra alfabética de 3+ caracteres
                        name_parts.append(words[j].upper())  # Convertir a mayúsculas
                    else:
                        break
                if name_parts:
                    return " ".join(name_parts)

        # Patrón 2: "alumnos llamados NOMBRE", "estudiantes con nombre NOMBRE"
        llamados_keywords = ["llamados", "llamadas", "nombre", "apellido"]
        for i, word in enumerate(words):
            if word.lower() in llamados_keywords and i + 1 < len(words):
                name_parts = []
                for j in range(i + 1, len(words)):
                    # 🔧 MEJORADO: Aceptar cualquier palabra que parezca nombre
                    if len(words[j]) > 2 and words[j].isalpha():
                        name_parts.append(words[j].upper())
                    else:
                        break
                if name_parts:
                    return " ".join(name_parts)

        # Patrón 3: Buscar nombres en cualquier parte (como último recurso)
        name_parts = []
        for word in words:
            # 🔧 MEJORADO: Buscar palabras que parezcan nombres
            if len(word) > 3 and word.isalpha() and not word.lower() in ["busca", "buscar", "alumnos", "estudiantes", "información", "datos"]:
                name_parts.append(word.upper())

        # Solo retornar si encontramos 2+ palabras (nombre + apellido mínimo)
        if len(name_parts) >= 2:
            return " ".join(name_parts)

        return None

    def _extract_grade_from_query(self, query: str) -> Optional[int]:
        """Extrae grado de la consulta"""
        import re

        query_lower = query.lower()

        # Buscar patrones de grado
        grade_patterns = [
            r'\b([1-6])(?:to|er|do|ro)?\s*grado\b',  # "4to grado", "1er grado", etc.
            r'\bgrado\s*([1-6])\b',                   # "grado 4"
            r'\b([1-6])(?:to|er|do|ro)\b',           # "2do", "3er", "4to", etc. (SIN grado)
            r'\b([1-6])\b'                            # solo número
        ]

        for pattern in grade_patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                return int(matches[0])

        return None

    def _extract_turno_from_query(self, query: str) -> Optional[str]:
        """Extrae turno de la consulta"""
        query_lower = query.lower()
        if "matutino" in query_lower:
            return "MATUTINO"
        elif "vespertino" in query_lower:
            return "VESPERTINO"
        return None

    def _extract_curp_from_query(self, query: str) -> Optional[str]:
        """Extrae CURP de la consulta"""
        import re
        # CURP tiene formato específico: 18 caracteres alfanuméricos
        curp_pattern = r'\b([A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d)\b'
        matches = re.findall(curp_pattern, query.upper())
        if matches:
            return matches[0]
        return None

    def _extract_matricula_from_query(self, query: str) -> Optional[str]:
        """Extrae matrícula de la consulta"""
        words = query.split()

        # Buscar después de palabras clave
        keywords = ["matricula", "matrícula", "con", "número"]
        for i, word in enumerate(words):
            if word.lower() in keywords and i + 1 < len(words):
                # La siguiente palabra podría ser la matrícula
                potential_matricula = words[i + 1]
                # Verificar que no sea una palabra común
                if len(potential_matricula) > 2 and not potential_matricula.lower() in ["de", "del", "la", "el"]:
                    return potential_matricula

        return None

    def _extract_grupo_from_query(self, query: str) -> Optional[str]:
        """Extrae grupo de la consulta"""
        import re

        # Buscar patrones de grupo (A, B, C, etc.)
        grupo_patterns = [
            r'\bgrupo\s*([A-Z])\b',  # "grupo A"
            r'\b([A-Z])\s*grupo\b',  # "A grupo"
            r'\b([A-Z])\b'           # solo letra
        ]

        for pattern in grupo_patterns:
            matches = re.findall(pattern, query.upper())
            if matches:
                grupo = matches[0]
                # Verificar que sea una letra válida para grupo
                if grupo in ['A', 'B', 'C', 'D', 'E', 'F']:
                    return grupo

        return None
