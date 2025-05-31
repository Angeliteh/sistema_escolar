"""
🎯 CATÁLOGO DE ACCIONES DE ALTO NIVEL

Este módulo define todas las acciones disponibles que el LLM puede usar
para resolver consultas de manera predecible y combinable.

FILOSOFÍA:
- LLM elige ACCIONES, no genera código
- Cada acción es confiable y predecible
- Acciones se pueden combinar creativamente
- Abstrae la complejidad técnica del LLM
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ActionDefinition:
    """Definición de una acción disponible"""
    name: str
    description: str
    category: str
    input_params: Dict[str, str]
    output_type: str
    usage_example: str
    sql_template: Optional[str] = None
    requires_combination: bool = False

class ActionCatalog:
    """
    🎯 CATÁLOGO CENTRAL DE ACCIONES DISPONIBLES

    Proporciona al LLM un vocabulario estructurado de acciones
    que puede usar para resolver consultas de manera predecible.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._actions = self._initialize_actions()

    def _initialize_actions(self) -> Dict[str, ActionDefinition]:
        """Inicializa el catálogo completo de acciones"""

        actions = {}

        # 🔍 ACCIONES DE BÚSQUEDA








        # 🆕 ACCIÓN UNIVERSAL DE BÚSQUEDA (REEMPLAZA MÚLTIPLES ACCIONES)
        actions["BUSCAR_UNIVERSAL"] = ActionDefinition(
            name="BUSCAR_UNIVERSAL",
            description="Búsqueda universal dinámica por cualquier campo con múltiples criterios opcionales",
            category="busqueda",
            input_params={
                "criterio_principal": "Criterio principal: {'tabla': 'alumnos|datos_escolares', 'campo': 'campo_dinamico', 'operador': '=|LIKE|>|<', 'valor': 'valor_buscar'}",
                "filtros_adicionales": "Lista opcional de filtros extra con misma estructura que criterio_principal",
                "join_logic": "Tipo de JOIN (INNER|LEFT) - opcional, por defecto LEFT",
                "limit": "Límite de resultados - opcional"
            },
            output_type="alumno_o_lista_alumnos",
            usage_example="Para cualquier búsqueda: nombres, CURP, fechas, grados, turnos, criterios múltiples, etc.",
            sql_template="Generado dinámicamente basado en criterios y estructura de BD"
        )

        # 📊 ACCIONES DE ESTADÍSTICA
        actions["CONTAR_ALUMNOS"] = ActionDefinition(
            name="CONTAR_ALUMNOS",
            description="Cuenta alumnos que cumplen criterios específicos",
            category="estadistica",
            input_params={
                "criterio_campo": "Campo a filtrar (opcional)",
                "criterio_valor": "Valor del criterio (opcional)",
                "agrupar_por": "Campo para agrupar resultados (opcional)"
            },
            output_type="numero_o_tabla_conteos",
            usage_example="Para 'cuántos alumnos hay' o 'cuántos hay en cada grado'",
            sql_template="SELECT COUNT(*) as total FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.{criterio_campo} = '{criterio_valor}'"
        )

        actions["FILTRAR_POR_CALIFICACIONES"] = ActionDefinition(
            name="FILTRAR_POR_CALIFICACIONES",
            description="Filtra alumnos basándose en si tienen o no calificaciones registradas",
            category="busqueda",
            input_params={
                "tiene_calificaciones": "true para alumnos CON calificaciones, false para alumnos SIN calificaciones",
                "incluir_conteo": "Si incluir conteo de resultados (true/false)",
                "mostrar_detalles": "Si mostrar datos completos o solo conteo (true/false)"
            },
            output_type="lista_alumnos_filtrados_o_conteo",
            usage_example="Para 'alumnos con calificaciones', 'cuántos tienen calificaciones', 'estudiantes sin calificaciones'",
            sql_template="SELECT a.*, de.* FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE (de.calificaciones IS NOT NULL AND de.calificaciones != '[]' AND de.calificaciones != '') = {tiene_calificaciones}"
        )

        # 🗑️ ELIMINADA: Definición duplicada de CALCULAR_ESTADISTICA

        # 📋 ACCIONES DE REPORTE
        actions["GENERAR_LISTADO_COMPLETO"] = ActionDefinition(
            name="GENERAR_LISTADO_COMPLETO",
            description="Genera listado completo con todos los datos de alumnos",
            category="reporte",
            input_params={
                "criterio_filtro": "Criterios de filtrado (opcional)",
                "ordenar_por": "Campo para ordenar (nombre, grado, etc.)",
                "incluir_calificaciones": "Si incluir calificaciones (true/false)"
            },
            output_type="reporte_completo",
            usage_example="Para 'lista completa de 2do A' o 'reporte de todos los alumnos'",
            sql_template="SELECT a.*, de.*, c.* FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id LEFT JOIN calificaciones c ON a.id = c.alumno_id ORDER BY {ordenar_por}"
        )

        # 📄 ACCIONES DE CONSTANCIA
        actions["PREPARAR_DATOS_CONSTANCIA"] = ActionDefinition(
            name="PREPARAR_DATOS_CONSTANCIA",
            description="Obtiene todos los datos necesarios para generar una constancia",
            category="constancia",
            input_params={
                "alumno_identificador": "Nombre, ID o CURP del alumno",
                "tipo_constancia": "Tipo de constancia (estudio, calificaciones, traslado)",
                "incluir_calificaciones": "Si necesita datos de calificaciones"
            },
            output_type="datos_completos_alumno",
            usage_example="Para 'constancia de estudios para luis' o 'certificado de calificaciones'",
            requires_combination=False  # ✅ AHORA FUNCIONA INDEPENDIENTEMENTE
        )

        actions["GENERAR_CONSTANCIA_COMPLETA"] = ActionDefinition(
            name="GENERAR_CONSTANCIA_COMPLETA",
            description="Genera una constancia completa (busca alumno + valida + genera PDF)",
            category="constancia",
            input_params={
                "alumno_identificador": "Nombre, ID o CURP del alumno",
                "tipo_constancia": "Tipo de constancia (estudio, calificaciones, traslado)",
                "incluir_foto": "Si incluir foto del alumno (true/false)",
                "preview_mode": "Si generar solo vista previa (true/false)"
            },
            output_type="constancia_generada",
            usage_example="Para 'generar constancia de estudios para luis' o 'crear certificado'",
            requires_combination=False
        )

        actions["CALCULAR_ESTADISTICA"] = ActionDefinition(
            name="CALCULAR_ESTADISTICA",
            description="Calcula estadísticas AGREGADAS: distribuciones, promedios, rankings. USAR para comparaciones tipo 'X vs Y' (ej: con calificaciones vs sin calificaciones)",
            category="estadistica",
            input_params={
                "tipo": "Tipo de estadística (distribucion, promedio, ranking, comparacion). Usar 'distribucion' para comparar grupos como 'con/sin calificaciones'",
                "agrupar_por": "Campo para agrupar (grado, grupo, turno, ciclo_escolar, calificaciones) - REQUERIDO para distribuciones",
                "campo": "Campo a analizar (calificaciones, edad, matricula) - OPCIONAL para conteos",
                "filtro": "Criterios de filtrado como dict - OPCIONAL",
                "orden": "Orden para rankings (asc, desc) - OPCIONAL",
                "limite": "Límite de resultados para rankings - OPCIONAL",
                "incluir_detalles": "Si incluir datos detallados o solo resumen - OPCIONAL"
            },
            output_type="estadistica_calculada",
            usage_example="Para 'distribución por turno', 'cuántos tienen calificaciones vs cuántos no', 'promedio por grado', 'ranking de estudiantes'",
            requires_combination=False
        )

        # 🔄 ACCIONES COMBINADAS
        actions["BUSCAR_Y_FILTRAR"] = ActionDefinition(
            name="BUSCAR_Y_FILTRAR",
            description="Combina búsqueda por nombre con filtros adicionales (redirige a BUSCAR_UNIVERSAL)",
            category="combinada",
            input_params={
                "criterio_principal": "Criterio principal: {'tabla': 'alumnos|datos_escolares', 'campo': 'campo_dinamico', 'operador': '=|LIKE|>|<', 'valor': 'valor_buscar'}",
                "filtros_adicionales": "Lista opcional de filtros extra con misma estructura que criterio_principal",
                "criterios": "Lista de criterios (alternativo a criterio_principal + filtros_adicionales)",
                "nombre_parcial": "Parte del nombre a buscar (opcional)",
                "operador_logico": "Operador para combinar (AND, OR) - opcional"
            },
            output_type="lista_alumnos_filtrados",
            usage_example="Para 'garcia de 2do grado' o 'luis del turno matutino'",
            requires_combination=True
        )

        actions["ANALIZAR_Y_REPORTAR"] = ActionDefinition(
            name="ANALIZAR_Y_REPORTAR",
            description="Combina análisis estadístico con reporte detallado",
            category="combinada",
            input_params={
                "tipo_analisis": "Tipo de análisis a realizar",
                "criterios_reporte": "Criterios para el reporte detallado",
                "formato_salida": "Formato del reporte (tabla, resumen, etc.)"
            },
            output_type="reporte_analitico",
            usage_example="Para 'estadísticas de 2do grado con detalles' o 'análisis completo por turno'",
            requires_combination=True
        )

        return actions

    def get_actions_for_category(self, category: str) -> Dict[str, ActionDefinition]:
        """Obtiene todas las acciones disponibles para una categoría"""
        return {
            name: action for name, action in self._actions.items()
            if action.category == category or action.category == "combinada"
        }

    def get_all_actions(self) -> Dict[str, ActionDefinition]:
        """Obtiene todas las acciones disponibles"""
        return self._actions.copy()

    def get_action_definition(self, action_name: str) -> Optional[ActionDefinition]:
        """Obtiene la definición de una acción específica"""
        return self._actions.get(action_name)

    def format_actions_for_prompt(self, category: str = None) -> str:
        """Formatea las acciones para incluir en un prompt del LLM"""

        if category:
            actions = self.get_actions_for_category(category)
        else:
            actions = self.get_all_actions()

        formatted = "ACCIONES DISPONIBLES:\n\n"

        for name, action in actions.items():
            formatted += f"🎯 {name}:\n"
            formatted += f"   Descripción: {action.description}\n"
            formatted += f"   Parámetros: {action.input_params}\n"
            formatted += f"   Resultado: {action.output_type}\n"
            formatted += f"   Ejemplo: {action.usage_example}\n"
            if action.requires_combination:
                formatted += f"   ⚠️ Requiere combinación con otras acciones\n"
            formatted += "\n"

        return formatted

    def validate_action_request(self, action_request: Dict[str, Any]) -> tuple:
        """Valida que una solicitud de acción sea válida"""

        action_name = action_request.get("accion_principal")
        if not action_name:
            return False, "No se especificó acción principal"

        action_def = self.get_action_definition(action_name)
        if not action_def:
            return False, f"Acción '{action_name}' no existe"

        # Validar parámetros requeridos (solo algunos son obligatorios)
        params = action_request.get("parametros", {})

        # 🎯 PARÁMETROS REQUERIDOS POR ACCIÓN
        required_params = {
            "BUSCAR_UNIVERSAL": ["criterio_principal"],  # 🆕 ACCIÓN PRINCIPAL DE BÚSQUEDA
            "CONTAR_ALUMNOS": [],  # Sin parámetros requeridos
            "PREPARAR_DATOS_CONSTANCIA": ["alumno_identificador", "tipo_constancia"],
            "GENERAR_CONSTANCIA_COMPLETA": ["alumno_identificador", "tipo_constancia"],
            "CALCULAR_ESTADISTICA": ["tipo"],  # Solo tipo es requerido
            "BUSCAR_Y_FILTRAR": [],  # 🔧 CORREGIDO: Sin parámetros requeridos (acepta múltiples formatos)
            "ANALIZAR_Y_REPORTAR": ["tipo_analisis"],
            "GENERAR_LISTADO_COMPLETO": [],
            "FILTRAR_POR_CALIFICACIONES": ["tiene_calificaciones"]
        }

        required_for_action = required_params.get(action_name, [])
        for param_name in required_for_action:
            if param_name not in params:
                return False, f"Parámetro requerido '{param_name}' no proporcionado"

        return True, "Solicitud válida"
