"""
TemplateExecutor - Ejecuta plantillas SQL de manera segura y eficiente
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .template_manager import SQLTemplateManager, TemplateSelection
from ..ai.interpretation.sql_executor import get_sql_executor

@dataclass
class TemplateResult:
    """Resultado de la ejecución de una plantilla"""
    success: bool
    data: Any = None
    row_count: int = 0
    message: str = ""
    template_used: str = ""
    parameters_used: Dict[str, Any] = None
    sql_executed: str = ""

class TemplateExecutor:
    """
    Ejecutor de plantillas SQL
    Combina SQLTemplateManager con SQLExecutor para ejecución segura
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.template_manager = SQLTemplateManager()
        self.sql_executor = get_sql_executor()
        self.logger.info("✅ TemplateExecutor inicializado")

    def execute_query(self, user_query: str) -> TemplateResult:
        """
        Ejecuta una consulta de usuario usando plantillas SQL

        Args:
            user_query: Consulta en lenguaje natural del usuario

        Returns:
            TemplateResult con los datos obtenidos
        """

        try:
            self.logger.info(f"🔍 Procesando consulta: '{user_query}'")

            # 1. Seleccionar plantilla apropiada
            template_selection = self.template_manager.select_template_for_query(user_query)

            if not template_selection:
                return TemplateResult(
                    success=False,
                    message="No se encontró plantilla apropiada para la consulta",
                    template_used="none"
                )

            self.logger.info(f"📋 Plantilla seleccionada: {template_selection.template.name}")
            self.logger.info(f"🎯 Confianza: {template_selection.confidence}")
            self.logger.info(f"📊 Parámetros: {template_selection.parameters}")

            # 2. Preparar SQL con parámetros
            sql_query = self._prepare_sql(template_selection)

            if not sql_query:
                return TemplateResult(
                    success=False,
                    message="Error al preparar consulta SQL",
                    template_used=template_selection.template.name
                )

            self.logger.info(f"🔍 SQL preparado: {sql_query}")

            # 3. Ejecutar SQL
            sql_result = self.sql_executor.execute_query(sql_query)

            if not sql_result.success:
                return TemplateResult(
                    success=False,
                    message=f"Error en ejecución SQL: {sql_result.message}",
                    template_used=template_selection.template.name,
                    sql_executed=sql_query
                )

            # 4. Procesar resultado
            processed_data = self._process_result(sql_result.data, template_selection.template)

            self.logger.info(f"✅ Consulta ejecutada exitosamente: {sql_result.row_count} resultados")

            return TemplateResult(
                success=True,
                data=processed_data,
                row_count=sql_result.row_count,
                message=f"Consulta ejecutada exitosamente usando {template_selection.template.name}",
                template_used=template_selection.template.name,
                parameters_used=template_selection.parameters,
                sql_executed=sql_query
            )

        except Exception as e:
            self.logger.error(f"❌ Error en TemplateExecutor: {e}")
            return TemplateResult(
                success=False,
                message=f"Error interno: {str(e)}",
                template_used="error"
            )

    def _prepare_sql(self, template_selection: TemplateSelection) -> Optional[str]:
        """
        Prepara el SQL de la plantilla con los parámetros proporcionados
        """

        try:
            template = template_selection.template
            parameters = template_selection.parameters

            # Verificar que todos los parámetros requeridos estén presentes
            missing_params = []
            for required_param in template.parameters:
                if required_param not in parameters:
                    missing_params.append(required_param)

            if missing_params:
                self.logger.error(f"❌ Parámetros faltantes: {missing_params}")
                return None

            # Formatear SQL con parámetros
            sql_query = template.sql.format(**parameters)

            # Limpiar espacios extra
            sql_query = " ".join(sql_query.split())

            return sql_query

        except Exception as e:
            self.logger.error(f"❌ Error preparando SQL: {e}")
            return None

    def _process_result(self, raw_data: Any, template: Any) -> Any:
        """
        Procesa los datos crudos según el tipo de plantilla
        """

        if not raw_data:
            return raw_data

        # Para plantillas que incluyen calificaciones, procesar JSON
        if template.name in ["buscar_alumno_completo", "buscar_alumno_exacto"]:
            return self._process_calificaciones_data(raw_data)

        return raw_data

    def _process_calificaciones_data(self, data: Any) -> Any:
        """
        Procesa datos que incluyen calificaciones en formato JSON
        """

        if not data:
            return data

        try:
            import json

            # Si es una lista de registros
            if isinstance(data, list):
                processed_data = []
                for record in data:
                    if isinstance(record, dict) and 'calificaciones' in record:
                        # Procesar calificaciones JSON
                        if record['calificaciones']:
                            try:
                                record['calificaciones'] = json.loads(record['calificaciones'])
                            except (json.JSONDecodeError, TypeError):
                                record['calificaciones'] = []
                        else:
                            record['calificaciones'] = []
                    processed_data.append(record)
                return processed_data

            # Si es un solo registro
            elif isinstance(data, dict) and 'calificaciones' in data:
                if data['calificaciones']:
                    try:
                        data['calificaciones'] = json.loads(data['calificaciones'])
                    except (json.JSONDecodeError, TypeError):
                        data['calificaciones'] = []
                else:
                    data['calificaciones'] = []
                return data

        except Exception as e:
            self.logger.warning(f"⚠️ Error procesando calificaciones: {e}")

        return data

    def get_available_templates(self) -> Dict[str, str]:
        """
        Retorna información de plantillas disponibles para debugging
        """

        templates_info = {}
        for name, template in self.template_manager.templates.items():
            templates_info[name] = template.description

        return templates_info

    def test_template(self, template_name: str, parameters: Dict[str, Any]) -> TemplateResult:
        """
        Prueba una plantilla específica con parámetros dados (para testing)
        """

        template = self.template_manager.get_template_info(template_name)
        if not template:
            return TemplateResult(
                success=False,
                message=f"Plantilla '{template_name}' no encontrada"
            )

        from .template_manager import TemplateSelection

        template_selection = TemplateSelection(
            template=template,
            parameters=parameters,
            confidence=1.0
        )

        # Preparar y ejecutar
        sql_query = self._prepare_sql(template_selection)
        if not sql_query:
            return TemplateResult(
                success=False,
                message="Error preparando SQL para testing"
            )

        sql_result = self.sql_executor.execute_query(sql_query)

        return TemplateResult(
            success=sql_result.success,
            data=sql_result.data,
            row_count=sql_result.row_count,
            message=sql_result.message,
            template_used=template_name,
            parameters_used=parameters,
            sql_executed=sql_query
        )

    def execute_template_with_params(self, template_name: str, params: Dict[str, Any]) -> TemplateResult:
        """🆕 EJECUTA PLANTILLA ESPECÍFICA CON PARÁMETROS DADOS (PARA SISTEMA UNIFICADO)"""
        try:
            self.logger.info(f"🎯 Ejecutando plantilla '{template_name}' con parámetros: {params}")

            # Verificar que la plantilla existe
            if template_name not in self.template_manager.templates:
                return TemplateResult(
                    success=False,
                    message=f"Plantilla '{template_name}' no encontrada",
                    data=[],
                    row_count=0,
                    sql_executed="",
                    template_used=template_name,
                    parameters_used=params
                )

            # Obtener plantilla
            template = self.template_manager.templates[template_name]

            # Preparar SQL con parámetros
            try:
                sql_query = template["sql"].format(**params)
            except KeyError as e:
                return TemplateResult(
                    success=False,
                    message=f"Parámetro faltante para plantilla '{template_name}': {e}",
                    data=[],
                    row_count=0,
                    sql_executed="",
                    template_used=template_name,
                    parameters_used=params
                )

            # Ejecutar SQL
            result = self.sql_executor.execute_query(sql_query)

            if result.success:
                self.logger.info(f"✅ Plantilla '{template_name}' ejecutada: {result.row_count} resultados")
                return TemplateResult(
                    success=True,
                    message=f"Plantilla ejecutada exitosamente",
                    data=result.data,
                    row_count=result.row_count,
                    sql_executed=sql_query,
                    template_used=template_name,
                    parameters_used=params
                )
            else:
                self.logger.error(f"❌ Error ejecutando plantilla '{template_name}': {result.message}")
                return TemplateResult(
                    success=False,
                    message=f"Error en SQL: {result.message}",
                    data=[],
                    row_count=0,
                    sql_executed=sql_query,
                    template_used=template_name,
                    parameters_used=params
                )

        except Exception as e:
            self.logger.error(f"Error ejecutando plantilla '{template_name}': {e}")
            return TemplateResult(
                success=False,
                message=f"Error interno: {str(e)}",
                data=[],
                row_count=0,
                sql_executed="",
                template_used=template_name,
                parameters_used=params
            )
