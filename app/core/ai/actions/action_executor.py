"""
🎯 EJECUTOR DE ACCIONES DE ALTO NIVEL

Este módulo ejecuta las acciones seleccionadas por el LLM
de manera confiable y predecible.

RESPONSABILIDADES:
- Interpretar solicitudes de acción del LLM
- Ejecutar acciones usando código confiable
- Combinar múltiples acciones cuando sea necesario
- Retornar resultados estructurados
"""

from typing import Dict, Any, Optional
import logging
import os
from .action_catalog import ActionCatalog
from .field_mapper import FieldMapper

class ActionExecutor:
    """
    🎯 EJECUTOR CENTRAL DE ACCIONES

    Toma las decisiones del LLM (en forma de acciones) y las ejecuta
    usando código Python confiable y predecible.
    """

    def __init__(self, sql_executor, student_finder=None):
        self.logger = logging.getLogger(__name__)
        self.catalog = ActionCatalog()
        self.sql_executor = sql_executor
        self.student_finder = student_finder
        # 🆕 OBTENER DB_PATH DEL SQL_EXECUTOR PARA VALIDACIÓN DINÁMICA
        self.db_path = getattr(sql_executor, 'db_path', 'resources/data/alumnos.db')
        # 🎯 INICIALIZAR MAPEADOR CENTRALIZADO DE CAMPOS
        self.field_mapper = FieldMapper(self.db_path)

    def _debug_pause_if_enabled(self, message: str):
        """🛑 PAUSA DE DEBUG CONTROLADA POR VARIABLE DE ENTORNO"""
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            input(f"🛑 {message}")

    def _debug_pause_sql_construction(self, action: str, criteria: list, sql_query: str):
        """🛑 PAUSA ESPECÍFICA PARA CONSTRUCCIÓN DE SQL"""
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            print(f"\n🛑 [ACTION_EXECUTOR] CONSTRUCCIÓN SQL:")
            print(f"    ├── Action: {action}")
            print(f"    ├── Criteria count: {len(criteria)}")
            for i, criterion in enumerate(criteria[:3], 1):
                print(f"    │   {i}. {criterion.get('campo', 'N/A')} {criterion.get('operador', '=')} {criterion.get('valor', 'N/A')}")
            if len(criteria) > 3:
                print(f"    │   ... y {len(criteria) - 3} más")
            print(f"    ├── SQL generado: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")
            print(f"    └── Presiona ENTER para ejecutar SQL...")
            input()

    def execute_action_request(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una solicitud de acción del LLM

        Args:
            action_request: {
                "estrategia": "simple|combinada|secuencial",
                "accion_principal": "NOMBRE_ACCION",
                "parametros": {"param1": "valor1"},
                "acciones_adicionales": [...],
                "razonamiento": "..."
            }

        Returns:
            {
                "success": bool,
                "data": Any,
                "row_count": int,
                "action_used": str,
                "message": str
            }
        """
        try:


            # 🔧 LIMPIAR NOMBRE DE ACCIÓN ANTES DE VALIDAR
            action_name_raw = action_request.get("accion_principal", "")
            if action_name_raw:
                action_request["accion_principal"] = self._clean_action_name(action_name_raw)
                self.logger.info(f"🔧 Nombre de acción limpiado: '{action_name_raw}' → '{action_request['accion_principal']}'")

            # Validar solicitud
            is_valid, validation_message = self.catalog.validate_action_request(action_request)
            if not is_valid:
                return self._error_result(f"Solicitud inválida: {validation_message}")

            estrategia = action_request.get("estrategia", "simple").lower()

            if estrategia == "simple":
                return self._execute_single_action(action_request)
            elif estrategia == "combinada":
                return self._execute_combined_actions(action_request)
            elif estrategia == "secuencial":
                return self._execute_sequential_actions(action_request)
            else:
                return self._error_result(f"Estrategia desconocida: {estrategia}")

        except Exception as e:
            self.logger.error(f"Error ejecutando acción: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _clean_action_name(self, action_name: str) -> str:
        """
        🔧 LIMPIAR NOMBRE DE ACCIÓN
        Remueve emojis, espacios extra y caracteres especiales
        """
        import re
        # Remover emojis y caracteres especiales, mantener solo letras, números y guiones bajos
        cleaned = re.sub(r'[^\w_]', '', action_name)
        return cleaned.strip().upper()

    def _execute_single_action(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una sola acción"""

        action_name = action_request["accion_principal"]  # Ya está limpio
        params = action_request.get("parametros", {})

        self.logger.info(f"🎯 Ejecutando acción: {action_name}")
        self.logger.info(f"   Parámetros: {params}")

        # Validar que la acción existe en el catálogo
        self.catalog.get_action_definition(action_name)

        # Ejecutar según el tipo de acción
        if action_name == "BUSCAR_UNIVERSAL":
            return self._execute_buscar_universal(params)
        elif action_name == "CONTAR_UNIVERSAL":
            return self._execute_contar_universal(params)
        elif action_name == "BUSCAR_Y_FILTRAR":
            return self._execute_buscar_y_filtrar(params)
        elif action_name == "CONTAR_ALUMNOS":
            return self._execute_contar_alumnos(params)
        elif action_name == "CALCULAR_ESTADISTICA":
            return self._execute_calcular_estadistica(params)
        elif action_name == "GENERAR_LISTADO_COMPLETO":
            return self._execute_listado_completo(params)
        elif action_name == "PREPARAR_DATOS_CONSTANCIA":
            return self._execute_preparar_constancia(params)
        elif action_name == "GENERAR_CONSTANCIA_COMPLETA":
            return self._execute_generar_constancia_completa(params)
        elif action_name == "FILTRAR_POR_CALIFICACIONES":
            return self._execute_filtrar_por_calificaciones(params)
        else:
            return self._error_result(f"Acción no implementada: {action_name}")



    def _execute_buscar_universal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🆕 EJECUTA BÚSQUEDA UNIVERSAL DINÁMICA (CORREGIDO)
        Reemplaza múltiples acciones con una sola acción flexible

        🔧 CORRECCIÓN: Maneja criterio_secundario y criterio_terciario
        """
        try:
            # 🎯 EXTRAER PARÁMETROS
            criterio_principal = params.get("criterio_principal", {})
            filtros_adicionales = params.get("filtros_adicionales", [])
            join_logic = params.get("join_logic", "LEFT")
            limit = params.get("limit", None)

            # 🔧 NUEVA LÓGICA: Convertir criterio_secundario y criterio_terciario a filtros_adicionales
            criterio_secundario = params.get("criterio_secundario")
            criterio_terciario = params.get("criterio_terciario")

            if criterio_secundario:
                filtros_adicionales.append(criterio_secundario)
                self.logger.info(f"   ✅ Agregado criterio_secundario a filtros: {criterio_secundario}")

            if criterio_terciario:
                filtros_adicionales.append(criterio_terciario)
                self.logger.info(f"   ✅ Agregado criterio_terciario a filtros: {criterio_terciario}")

            self.logger.info(f"🎯 Ejecutando BUSCAR_UNIVERSAL:")
            self.logger.info(f"   - Criterio principal: {criterio_principal}")
            self.logger.info(f"   - Filtros adicionales ({len(filtros_adicionales)}): {filtros_adicionales}")
            self.logger.info(f"   - Join logic: {join_logic}")

            # 🔍 ANÁLISIS DE FILTROS DE PROMEDIO (SIN PAUSA)
            self.logger.info("🔍 Analizando filtros adicionales...")
            self.logger.info(f"   ├── Filtros adicionales recibidos: {len(filtros_adicionales)}")

            # 🔧 FILTRAR CRITERIOS DE PROMEDIO ANTES DE GENERAR SQL
            filtros_sql = []
            filtros_promedio = []

            for filtro in filtros_adicionales:
                campo = filtro.get("campo", "")
                if "promedio" in campo.lower():
                    filtros_promedio.append(filtro)
                    self.logger.info(f"🧠 Criterio de promedio detectado en filtros - se manejará en filtros dinámicos: {filtro}")
                else:
                    filtros_sql.append(filtro)

            # Verificar si el criterio principal también es de promedio
            campo_principal = criterio_principal.get("campo", "") if criterio_principal else ""
            if "promedio" in campo_principal.lower():
                filtros_promedio.append(criterio_principal)
                self.logger.info(f"🧠 Criterio principal de promedio detectado - se manejará en filtros dinámicos: {criterio_principal}")

                # Si el criterio principal es de promedio, usar el primer filtro SQL como principal
                if filtros_sql:
                    criterio_principal = filtros_sql[0]
                    filtros_sql = filtros_sql[1:]
                    self.logger.info(f"✅ Nuevo criterio principal: {criterio_principal}")
                else:
                    return self._error_result("No hay criterios válidos para SQL después de filtrar criterios de promedio")

            # Usar filtros SQL filtrados
            filtros_adicionales = filtros_sql
            self.logger.info(f"✅ Filtros SQL finales: {len(filtros_adicionales)} criterios, {len(filtros_promedio)} criterios de promedio filtrados")

            # 🔒 VALIDAR CRITERIO PRINCIPAL
            if not criterio_principal:
                return self._error_result("criterio_principal es requerido")

            # 🎯 VALIDACIÓN Y MAPEO CENTRALIZADO DE CRITERIO PRINCIPAL
            criterio_principal_mapeado = self._validate_and_map_criterion(criterio_principal)
            if not criterio_principal_mapeado:
                return self._error_result(f"No se pudo mapear criterio principal: {criterio_principal}")

            # Usar criterio mapeado
            criterio_principal = criterio_principal_mapeado

            # 🎯 VALIDACIÓN Y MAPEO CENTRALIZADO DE FILTROS ADICIONALES
            filtros_adicionales_mapeados = []
            for filtro in filtros_adicionales:
                filtro_mapeado = self._validate_and_map_criterion(filtro)
                if filtro_mapeado:
                    filtros_adicionales_mapeados.append(filtro_mapeado)
                else:
                    self.logger.warning(f"⚠️ Filtro ignorado (no se pudo mapear): {filtro}")

            # Usar filtros mapeados
            filtros_adicionales = filtros_adicionales_mapeados

            # 🔧 CONSTRUIR SQL DINÁMICAMENTE
            sql = self._build_dynamic_sql(criterio_principal, filtros_adicionales, join_logic, limit)

            self.logger.info(f"🔧 SQL generado: {sql}")

            # 🛑 PAUSA ESTRATÉGICA #5: ACTIONEXECUTOR SQL FINAL GENERADO
            import os
            if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
                print(f"\n🛑 [ACTIONEXECUTOR] SQL FINAL GENERADO:")
                print(f"    ├── 🎯 Acción: BUSCAR_UNIVERSAL")
                print(f"    ├── 📊 Criterio principal: {criterio_principal}")
                print(f"    ├── 🔍 Filtros adicionales: {len(filtros_adicionales)}")
                print(f"    ├── 🗃️ SQL generado:")
                for line in sql.split('\n'):
                    if line.strip():
                        print(f"    │   {line.strip()}")
                print(f"    └── Presiona ENTER para ejecutar consulta en base de datos...")
                input()

            # 🚀 EJECUTAR CONSULTA CON LÍMITE APROPIADO
            # Para BUSCAR_UNIVERSAL, usar límite alto o el especificado en parámetros
            query_limit = limit if limit else 1000  # Límite alto por defecto para búsquedas
            result = self.sql_executor.execute_query(sql, query_limit)



            if result.success:
                self.logger.info(f"✅ Búsqueda universal completada: {result.row_count} resultado(s)")
                return {
                    "success": True,
                    "data": result.data,
                    "row_count": result.row_count,
                    "action_used": "BUSCAR_UNIVERSAL",
                    "message": f"Búsqueda universal completada: {result.row_count} resultado(s)",
                    "sql_executed": sql  # 🆕 AGREGAR SQL PARA ANÁLISIS DINÁMICO
                }
            else:
                return self._error_result(f"Error en búsqueda universal: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en búsqueda universal: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_contar_universal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎯 CONTAR_UNIVERSAL: Conteo flexible con múltiples criterios

        Usa la MISMA lógica que BUSCAR_UNIVERSAL pero devuelve COUNT en lugar de datos.
        Acepta los mismos parámetros que BUSCAR_UNIVERSAL.
        """
        try:
            self.logger.info("🎯 Ejecutando CONTAR_UNIVERSAL")
            self.logger.info(f"   Parámetros: {params}")

            # Usar la misma lógica de construcción SQL que BUSCAR_UNIVERSAL
            criterio_principal = params.get("criterio_principal", {})
            filtros_adicionales = params.get("filtros_adicionales", [])
            join_logic = params.get("join_logic", "LEFT")

            if not criterio_principal:
                return self._error_result("Se requiere al menos un criterio_principal para contar")

            tabla_principal = criterio_principal.get("tabla", "alumnos")
            campo_principal = criterio_principal.get("campo", "")
            valor_principal = criterio_principal.get("valor", "")

            if not campo_principal or not valor_principal:
                return self._error_result(f"criterio_principal incompleto: {criterio_principal}")

            # 🎯 CONSTRUIR SQL DE CONTEO (MISMA LÓGICA QUE BUSCAR_UNIVERSAL)
            sql = f"""
            SELECT COUNT(*) as total
            FROM alumnos a
            {join_logic} JOIN datos_escolares de ON a.id = de.alumno_id
            WHERE 1=1
            """

            # Agregar criterio principal con operadores avanzados
            sql += self._build_where_condition(tabla_principal, campo_principal, criterio_principal.get("operador", "="), valor_principal)

            # Agregar filtros adicionales con operadores avanzados
            for filtro in filtros_adicionales:
                tabla_filtro = filtro.get("tabla", "datos_escolares")
                campo_filtro = filtro.get("campo", "")
                valor_filtro = filtro.get("valor", "")
                operador_filtro = filtro.get("operador", "=")

                if campo_filtro and valor_filtro:
                    sql += self._build_where_condition(tabla_filtro, campo_filtro, operador_filtro, valor_filtro)

            self.logger.info(f"🔧 SQL de conteo generado: {sql}")

            # 🚀 EJECUTAR CONSULTA DE CONTEO
            result = self.sql_executor.execute_query(sql)

            if result.success:
                total = result.data[0]['total'] if result.data else 0
                self.logger.info(f"✅ Conteo universal completado: {total} resultado(s)")
                return {
                    "success": True,
                    "data": [{"total": total}],
                    "row_count": 1,
                    "action_used": "CONTAR_UNIVERSAL",
                    "message": f"Conteo universal completado: {total} resultado(s)",
                    "sql_executed": sql
                }
            else:
                return self._error_result(f"Error en conteo universal: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en conteo universal: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _build_where_condition(self, tabla: str, campo: str, operador: str, valor: str) -> str:
        """
        🎯 CONSTRUYE CONDICIONES WHERE CON OPERADORES AVANZADOS

        Soporta: =, LIKE, >, <, >=, <=, BETWEEN, IS_NULL, IS_NOT_NULL,
                STARTS_WITH, ENDS_WITH, NOT_IN, IN
        """
        try:
            # Determinar prefijo de tabla
            tabla_prefix = "a" if tabla == "alumnos" else "de"

            # Limpiar valores para evitar inyección SQL
            valor_limpio = str(valor).replace("'", "''") if valor else ""

            # Construir condición según operador
            if operador.upper() == "=":
                # Manejo especial para calificaciones
                if campo == "calificaciones" and valor_limpio == "[]":
                    # SIN CALIFICACIONES
                    return f" AND ({tabla_prefix}.{campo} IS NULL OR {tabla_prefix}.{campo} = '' OR {tabla_prefix}.{campo} = '[]')"
                else:
                    return f" AND {tabla_prefix}.{campo} = '{valor_limpio}'"

            elif operador.upper() == "LIKE":
                return f" AND {tabla_prefix}.{campo} LIKE '%{valor_limpio}%'"

            elif operador.upper() == "STARTS_WITH":
                return f" AND {tabla_prefix}.{campo} LIKE '{valor_limpio}%'"

            elif operador.upper() == "ENDS_WITH":
                return f" AND {tabla_prefix}.{campo} LIKE '%{valor_limpio}'"

            elif operador.upper() in [">", "<", ">=", "<="]:
                return f" AND {tabla_prefix}.{campo} {operador} '{valor_limpio}'"

            elif operador.upper() == "BETWEEN":
                # Valor debe ser "valor1,valor2"
                if "," in valor_limpio:
                    valor1, valor2 = valor_limpio.split(",", 1)
                    return f" AND {tabla_prefix}.{campo} BETWEEN '{valor1.strip()}' AND '{valor2.strip()}'"
                else:
                    self.logger.warning(f"BETWEEN requiere formato 'valor1,valor2', recibido: {valor}")
                    return f" AND {tabla_prefix}.{campo} = '{valor_limpio}'"

            elif operador.upper() == "IS_NULL":
                return f" AND {tabla_prefix}.{campo} IS NULL"

            elif operador.upper() == "IS_NOT_NULL":
                return f" AND {tabla_prefix}.{campo} IS NOT NULL"

            elif operador.upper() == "IN":
                # Valor debe ser "valor1,valor2,valor3" o "[valor1,valor2,valor3]"
                if valor_limpio.startswith("[") and valor_limpio.endswith("]"):
                    # Formato lista JSON
                    valores = valor_limpio[1:-1].split(",")
                else:
                    # Formato separado por comas
                    valores = valor_limpio.split(",")

                valores_formateados = [f"'{v.strip()}'" for v in valores if v.strip()]
                if valores_formateados:
                    return f" AND {tabla_prefix}.{campo} IN ({','.join(valores_formateados)})"
                else:
                    return f" AND {tabla_prefix}.{campo} = '{valor_limpio}'"

            elif operador.upper() == "NOT_IN":
                # Similar a IN pero con NOT
                if valor_limpio.startswith("[") and valor_limpio.endswith("]"):
                    valores = valor_limpio[1:-1].split(",")
                else:
                    valores = valor_limpio.split(",")

                valores_formateados = [f"'{v.strip()}'" for v in valores if v.strip()]
                if valores_formateados:
                    return f" AND {tabla_prefix}.{campo} NOT IN ({','.join(valores_formateados)})"
                else:
                    return f" AND {tabla_prefix}.{campo} != '{valor_limpio}'"

            elif operador.upper() == "!=":
                # Manejo especial para calificaciones
                if campo == "calificaciones" and valor_limpio == "[]":
                    # CON CALIFICACIONES
                    return f" AND {tabla_prefix}.{campo} IS NOT NULL AND {tabla_prefix}.{campo} != '' AND {tabla_prefix}.{campo} != '[]'"
                else:
                    return f" AND {tabla_prefix}.{campo} != '{valor_limpio}'"

            else:
                # Operador no reconocido, usar = por defecto
                self.logger.warning(f"Operador no reconocido: {operador}, usando = por defecto")
                return f" AND {tabla_prefix}.{campo} = '{valor_limpio}'"

        except Exception as e:
            self.logger.error(f"Error construyendo condición WHERE: {e}")
            # Fallback seguro
            tabla_prefix = "a" if tabla == "alumnos" else "de"
            return f" AND {tabla_prefix}.{campo} = '{valor}'"

    def _execute_buscar_y_filtrar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔄 EJECUTA BUSCAR_Y_FILTRAR REDIRIGIENDO A BUSCAR_UNIVERSAL
        Convierte parámetros de BUSCAR_Y_FILTRAR al formato de BUSCAR_UNIVERSAL
        """
        try:
            self.logger.info("🔄 Ejecutando BUSCAR_Y_FILTRAR → BUSCAR_UNIVERSAL")
            self.logger.info(f"🔍 Parámetros recibidos: {params}")

            # Extraer parámetros de BUSCAR_Y_FILTRAR (múltiples formatos soportados)
            criterio_principal = params.get("criterio_principal")
            filtros_adicionales = params.get("filtros_adicionales", [])
            criterios = params.get("criterios", [])
            nombre_parcial = params.get("nombre_parcial", "")

            self.logger.info(f"   🎯 Criterio principal: {criterio_principal}")
            self.logger.info(f"   🔧 Filtros adicionales: {filtros_adicionales}")
            self.logger.info(f"   📋 Criterios: {criterios}")
            self.logger.info(f"   📝 Nombre parcial: '{nombre_parcial}'")

            # Convertir a formato BUSCAR_UNIVERSAL
            universal_params = {}

            if criterio_principal:
                # Formato directo de BUSCAR_UNIVERSAL
                universal_params["criterio_principal"] = criterio_principal
                universal_params["filtros_adicionales"] = filtros_adicionales
                self.logger.info("✅ Usando formato directo BUSCAR_UNIVERSAL")
            elif nombre_parcial:
                # Si hay nombre, usarlo como criterio principal
                universal_params["criterio_principal"] = {
                    "tabla": "alumnos",
                    "campo": "nombre",
                    "operador": "LIKE",
                    "valor": nombre_parcial.upper()
                }
                universal_params["filtros_adicionales"] = filtros_adicionales or criterios
                self.logger.info("✅ Usando nombre como criterio principal")
            elif criterios:
                # Si no hay nombre pero hay criterios, FILTRAR criterios de promedio
                criterios_sql = []
                criterios_promedio = []

                for criterio in criterios:
                    campo = criterio.get("campo", "")
                    if "promedio" in campo.lower():
                        criterios_promedio.append(criterio)
                        self.logger.info(f"🧠 Criterio de promedio detectado - se manejará en filtros dinámicos: {criterio}")
                    else:
                        criterios_sql.append(criterio)

                if not criterios_sql:
                    return self._error_result("No hay criterios válidos para SQL después de filtrar criterios de promedio")

                # Usar el primero como principal
                universal_params["criterio_principal"] = criterios_sql[0]
                universal_params["filtros_adicionales"] = criterios_sql[1:] if len(criterios_sql) > 1 else []
                self.logger.info(f"✅ Usando lista de criterios SQL: {len(criterios_sql)} criterios, {len(criterios_promedio)} criterios de promedio filtrados")
            elif filtros_adicionales:
                # Si solo hay filtros adicionales, usar el primero como principal
                universal_params["criterio_principal"] = filtros_adicionales[0]
                universal_params["filtros_adicionales"] = filtros_adicionales[1:] if len(filtros_adicionales) > 1 else []
                self.logger.info("✅ Usando filtros adicionales")
            else:
                return self._error_result("BUSCAR_Y_FILTRAR requiere al menos un criterio de búsqueda")

            self.logger.info(f"🎯 Parámetros convertidos para BUSCAR_UNIVERSAL: {universal_params}")

            # Ejecutar BUSCAR_UNIVERSAL con parámetros convertidos
            return self._execute_buscar_universal(universal_params)

        except Exception as e:
            self.logger.error(f"Error en BUSCAR_Y_FILTRAR: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _validate_and_map_criterion(self, criterion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        🎯 VALIDACIÓN Y MAPEO CENTRALIZADO DE CRITERIOS

        Usa FieldMapper para validar y mapear campos antes de cualquier consulta SQL.
        Este método se ejecuta SIEMPRE antes de construir SQL.

        Args:
            criterion: Criterio con formato {"tabla": "...", "campo": "...", "operador": "...", "valor": "..."}

        Returns:
            Criterio validado y mapeado, o None si no se puede mapear
        """
        try:
            self.logger.info(f"🎯 [FIELD_MAPPER] Validando criterio: {criterion}")

            # 🔍 VALIDACIÓN DE CRITERIO (Student ya hizo el mapeo)
            self.logger.info(f"🔍 Validando criterio ya mapeado por Student: {criterion}")

            # Usar FieldMapper centralizado para validar y mapear
            mapped_criterion = self.field_mapper.validate_and_map_criterion(criterion)

            if mapped_criterion:
                self.logger.info(f"✅ [FIELD_MAPPER] Criterio mapeado exitosamente: {mapped_criterion}")
                return mapped_criterion
            else:
                self.logger.warning(f"❌ [FIELD_MAPPER] No se pudo mapear criterio: {criterion}")

                # Proporcionar sugerencias útiles
                campo = criterion.get("campo", "")
                tabla = criterion.get("tabla", "alumnos")
                suggestions = self.field_mapper.suggest_fields(campo, tabla)
                if suggestions:
                    self.logger.info(f"💡 [FIELD_MAPPER] Campos sugeridos para '{campo}': {suggestions}")

                return None

        except Exception as e:
            self.logger.error(f"Error en validación y mapeo de criterio: {e}")
            return None

    def _validate_field_dynamically(self, tabla: str, campo: str) -> bool:
        """
        🔒 VALIDAR CAMPO DINÁMICAMENTE CONTRA ESTRUCTURA DE BD
        """
        try:
            # Importar DatabaseAnalyzer dinámicamente para evitar dependencias circulares
            from app.core.database.database_analyzer import DatabaseAnalyzer

            analyzer = DatabaseAnalyzer(self.db_path)
            estructura = analyzer.get_database_structure()

            # Validar que la tabla existe
            if tabla not in estructura.get("tables", {}):
                self.logger.warning(f"Tabla '{tabla}' no encontrada")
                return False

            # Validar que el campo existe en la tabla
            campos_validos = estructura.get("tables", {}).get(tabla, {}).get("columns", {})
            if campo not in campos_validos:
                self.logger.warning(f"Campo '{campo}' no encontrado en tabla '{tabla}'")
                self.logger.info(f"Campos válidos: {list(campos_validos.keys())}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validando campo dinámicamente: {e}")
            return False

    def _build_dynamic_sql(self, criterio_principal: Dict, filtros_adicionales: list, join_logic: str, limit: int = None) -> str:
        """
        🔧 CONSTRUIR SQL DINÁMICAMENTE BASADO EN CRITERIOS
        """
        # Base query con JOINs automáticos
        sql = f"""
        SELECT a.*, de.*
        FROM alumnos a
        {join_logic} JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE 1=1
        """

        # 🎯 AGREGAR CRITERIO PRINCIPAL CON OPERADORES AVANZADOS
        tabla_principal = criterio_principal.get("tabla", "alumnos")
        campo_principal = criterio_principal.get("campo")
        operador_principal = criterio_principal.get("operador", "=")
        valor_principal = criterio_principal.get("valor")

        # Manejar operadores especiales JSON primero
        if operador_principal.upper() == "JSON_PROMEDIO":
            # Filtrar por promedio general de calificaciones (promedio de todos los promedios)
            tabla_prefix = "a" if tabla_principal == "alumnos" else "de"
            promedio_minimo = float(valor_principal)
            sql += f"""
            AND (
                SELECT AVG(CAST(json_extract(value, '$.promedio') AS REAL))
                FROM json_each({tabla_prefix}.{campo_principal})
                WHERE json_extract(value, '$.promedio') IS NOT NULL
                AND json_extract(value, '$.promedio') != 0
            ) > {promedio_minimo}"""
        elif operador_principal.upper() == "JSON_MATERIA":
            # Filtrar por promedio de materia específica (formato: "MATEMATICAS:8.0")
            tabla_prefix = "a" if tabla_principal == "alumnos" else "de"
            materia, promedio = valor_principal.split(":")
            promedio_minimo = float(promedio)
            sql += f"""
            AND EXISTS (
                SELECT 1 FROM json_each({tabla_prefix}.{campo_principal})
                WHERE json_extract(value, '$.nombre') = '{materia.upper()}'
                AND json_extract(value, '$.promedio') > {promedio_minimo}
            )"""
        else:
            # Usar el nuevo método para operadores estándar y avanzados
            sql += self._build_where_condition(tabla_principal, campo_principal, operador_principal, valor_principal)

        # 🎯 AGREGAR FILTROS ADICIONALES CON OPERADORES AVANZADOS
        for filtro in filtros_adicionales:
            tabla_filtro = filtro.get("tabla", "alumnos")
            campo_filtro = filtro.get("campo")
            operador_filtro = filtro.get("operador", "=")
            valor_filtro = filtro.get("valor")

            if not campo_filtro or not valor_filtro:
                continue

            # Manejar operadores especiales JSON primero
            if operador_filtro.upper() == "JSON_CONTAINS":
                tabla_prefix = "a" if tabla_filtro == "alumnos" else "de"
                sql += f" AND {tabla_prefix}.{campo_filtro} LIKE '%{valor_filtro}%'"
            else:
                # Usar el nuevo método para operadores estándar y avanzados
                sql += self._build_where_condition(tabla_filtro, campo_filtro, operador_filtro, valor_filtro)

        # 🎯 AGREGAR LÍMITE SI SE ESPECIFICA
        if limit:
            sql += f" LIMIT {limit}"

        return sql.strip()

    def _parse_filter_string_to_criteria(self, filter_string: str) -> Dict[str, Any]:
        """
        🔧 CONVERTIR STRING DE FILTRO A CRITERIOS ESTRUCTURADOS
        Convierte "Grado = 2 AND Grupo = 'A'" a formato BUSCAR_UNIVERSAL
        """
        try:
            self.logger.info(f"🔧 Parseando filtro string: '{filter_string}'")

            # Normalizar string
            filter_lower = filter_string.lower().strip()

            criterios = []

            # Detectar grado (CORREGIDO - SOPORTA COMILLAS Y MÚLTIPLES FORMATOS)
            if 'grado' in filter_lower:
                import re
                # Buscar patrones: "grado = 2", "grado: 2", "grado = '2'", "grado: '2'"
                grado_match = re.search(r"grado\s*[:=]\s*['\"]?(\d+)['\"]?", filter_lower)
                if grado_match:
                    grado = grado_match.group(1)
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "grado",
                        "operador": "=",
                        "valor": grado
                    }
                    criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado grado: {criterio}")

            # Detectar grupo (CORREGIDO - SOPORTA FORMATO "Grupo: A")
            if 'grupo' in filter_lower:
                import re
                # Buscar patrones: "grupo = A", "grupo: A", "grupo A"
                grupo_match = re.search(r"grupo\s*[:=]\s*['\"]?([abc])['\"]?", filter_lower)
                if grupo_match:
                    grupo = grupo_match.group(1).upper()
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "grupo",
                        "operador": "=",
                        "valor": grupo
                    }
                    criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado grupo: {criterio}")

            if criterios:
                result = {
                    "criterio_principal": criterios[0],
                    "filtros_adicionales": criterios[1:] if len(criterios) > 1 else []
                }
                self.logger.info(f"🎯 Criterios parseados: {result}")
                return result
            else:
                self.logger.warning(f"❌ No se pudieron parsear criterios de: '{filter_string}'")
                return {}

        except Exception as e:
            self.logger.error(f"Error parseando filtro string: {e}")
            return {}

    def _extract_criteria_from_context(self, conversation_stack: list) -> Dict[str, Any]:
        """
        🧠 EXTRAER CRITERIOS DEL CONTEXTO CONVERSACIONAL (SIMPLIFICADO)
        SOLO usa criterios básicos de nombres - el resto debe venir del Master

        🔧 SIMPLIFICACIÓN: Eliminado código hardcodeado, dependemos del Master
        """
        try:
            if not conversation_stack:
                self.logger.info("🔍 No hay pila conversacional disponible")
                return {}

            self.logger.info(f"🔍 Analizando pila conversacional con {len(conversation_stack)} niveles")

            # 🎯 SOLO EXTRAER CRITERIOS BÁSICOS DE NOMBRES (LO MÍNIMO NECESARIO)
            all_criterios = []

            for i, context in enumerate(conversation_stack):
                if not isinstance(context, dict):
                    continue

                query = context.get('query', '').lower()
                self.logger.info(f"🔍 Nivel {i+1}: Analizando query '{query}'")

                level_criterios = []

                # SOLO NOMBRES (lo básico para mantener contexto de búsqueda)
                nombres_comunes = ['garcia', 'martinez', 'lopez', 'hernandez', 'franco', 'natalia', 'mario']
                for name in nombres_comunes:
                    if name in query:
                        criterio = {
                            "tabla": "alumnos",
                            "campo": "nombre",
                            "operador": "LIKE",
                            "valor": name.upper()
                        }
                        level_criterios.append(criterio)
                        self.logger.info(f"   ✅ Detectado criterio nombre: {criterio}")
                        break

                # 🚫 TODO EL RESTO DEBE VENIR DEL MASTER - NO MÁS CÓDIGO HARDCODEADO
                # El Master debe detectar grado, grupo, turno, calificaciones, etc.

                # Agregar criterios de este nivel
                all_criterios.extend(level_criterios)
                self.logger.info(f"   📊 Nivel {i+1} contribuyó con {len(level_criterios)} criterios")

            # 🔧 ELIMINAR DUPLICADOS MANTENIENDO ORDEN
            unique_criterios = []
            seen = set()
            for criterio in all_criterios:
                key = f"{criterio['tabla']}.{criterio['campo']}.{criterio['operador']}.{criterio['valor']}"
                if key not in seen:
                    unique_criterios.append(criterio)
                    seen.add(key)

            self.logger.info(f"🧠 Total criterios únicos extraídos del contexto: {len(unique_criterios)}")
            for i, criterio in enumerate(unique_criterios):
                self.logger.info(f"   {i+1}. {criterio}")

            if unique_criterios:
                result = {
                    "criterio_principal": unique_criterios[0],
                    "filtros_adicionales": unique_criterios[1:] if len(unique_criterios) > 1 else []
                }
                self.logger.info(f"🎯 Estructura final del contexto: criterio_principal={result['criterio_principal']}, filtros_adicionales={len(result['filtros_adicionales'])}")
                return result

            self.logger.info("❌ No se encontraron criterios en el contexto")
            return {}

        except Exception as e:
            self.logger.error(f"Error extrayendo criterios del contexto: {e}")
            return {}

    def _extract_criteria_from_query(self, query: str) -> Dict[str, Any]:
        """
        🧠 EXTRAER CRITERIOS DE LA CONSULTA ACTUAL (MEJORADO)
        PRIORIDAD 1: Usar filtros del Master (LLM inteligente)
        PRIORIDAD 2: Detección hardcodeada como fallback

        🔧 MEJORA: Usa información del Master antes que regex
        """
        try:
            criterios = []

            self.logger.info(f"🔍 Analizando consulta actual: '{query}'")

            # 🧠 PRIORIDAD 1: USAR FILTROS DEL MASTER (LLM INTELIGENTE)
            master_filters = self._get_master_filters()
            if master_filters:
                self.logger.info(f"🧠 Usando filtros del Master (LLM): {master_filters}")
                for filtro in master_filters:
                    if ':' in filtro:
                        campo, valor = filtro.split(':', 1)
                        campo = campo.strip().lower()
                        valor = valor.strip()

                        if campo == 'grado':
                            criterio = {
                                "tabla": "datos_escolares",
                                "campo": "grado",
                                "operador": "=",
                                "valor": valor
                            }
                            criterios.append(criterio)
                            self.logger.info(f"   ✅ Criterio del Master - grado: {criterio}")
                        elif campo == 'grupo':
                            criterio = {
                                "tabla": "datos_escolares",
                                "campo": "grupo",
                                "operador": "=",
                                "valor": valor.upper()
                            }
                            criterios.append(criterio)
                            self.logger.info(f"   ✅ Criterio del Master - grupo: {criterio}")
                        elif campo == 'turno':
                            criterio = {
                                "tabla": "datos_escolares",
                                "campo": "turno",
                                "operador": "=",
                                "valor": valor.upper()
                            }
                            criterios.append(criterio)
                            self.logger.info(f"   ✅ Criterio del Master - turno: {criterio}")

                # Si el Master proporcionó filtros, usar solo esos
                if criterios:
                    self.logger.info(f"🧠 Usando {len(criterios)} criterios del Master (LLM inteligente)")
                    return criterios

            # 🚫 SIN FILTROS DEL MASTER: Error - el sistema debe depender del Master
            self.logger.warning("⚠️ No se encontraron filtros del Master - el sistema debe depender del LLM")
            self.logger.info(f"🧠 Total criterios extraídos: {len(criterios)} (solo del Master)")
            for i, criterio in enumerate(criterios):
                self.logger.info(f"   {i+1}. {criterio}")

            return criterios

        except Exception as e:
            self.logger.error(f"Error extrayendo criterios de la consulta: {e}")
            return []

    def _get_master_filters(self) -> list:
        """
        🧠 OBTENER FILTROS DEL MASTER
        Accede a la información que el Master ya detectó con LLM
        """
        try:
            # Acceder al Student que nos creó
            if hasattr(self, 'student_interpreter') and self.student_interpreter:
                master_intention = getattr(self.student_interpreter, 'master_intention', {})
                if master_intention:
                    detected_entities = master_intention.get('detected_entities', {})
                    filtros = detected_entities.get('filtros', [])
                    if filtros:
                        self.logger.info(f"🧠 Filtros del Master encontrados: {filtros}")
                        return filtros

            self.logger.info("🔍 No se encontraron filtros del Master, usando detección hardcodeada")
            return []

        except Exception as e:
            self.logger.error(f"Error obteniendo filtros del Master: {e}")
            return []

    def build_buscar_universal_with_master_filters(self, query: str, conversation_stack: list = None, master_filters: list = None) -> Dict[str, Any]:
        """
        🧠 CONSTRUIR PARÁMETROS PARA BUSCAR_UNIVERSAL USANDO FILTROS DEL MASTER
        Usa directamente los filtros que el Master ya detectó con LLM
        """
        try:
            self.logger.info(f"🧠 Construyendo parámetros con filtros del Master")
            self.logger.info(f"   📝 Query: '{query}'")
            self.logger.info(f"   🧠 Master filters: {master_filters}")
            self.logger.info(f"   📚 Stack size: {len(conversation_stack or [])}")

            # 🎯 USAR FILTROS DEL MASTER DIRECTAMENTE
            all_criterios = []

            # 1. AGREGAR CRITERIOS DEL CONTEXTO (solo nombres básicos)
            context_criteria = self._extract_criteria_from_context(conversation_stack or [])
            if context_criteria:
                all_criterios.append(context_criteria["criterio_principal"])
                all_criterios.extend(context_criteria.get("filtros_adicionales", []))
                self.logger.info(f"   ✅ Agregados {1 + len(context_criteria.get('filtros_adicionales', []))} criterios del contexto")

            # 2. AGREGAR FILTROS DEL MASTER (LLM inteligente con contexto estructural)
            if master_filters:
                for filtro in master_filters:
                    if ':' in filtro:
                        campo, valor = filtro.split(':', 1)
                        campo = campo.strip()
                        valor = valor.strip()

                        # 🎯 USAR CRITERIO DIRECTAMENTE - STUDENT YA HIZO EL MAPEO
                        criterio = {
                            "tabla": "alumnos",  # Default, Student debería especificar
                            "campo": campo,
                            "operador": "LIKE" if campo.lower() in ['nombre', 'apellido'] else "=",
                            "valor": valor
                        }
                        all_criterios.append(criterio)
                        self.logger.info(f"   ✅ Filtro del Master procesado: {filtro} → {criterio}")

            # 3. ELIMINAR DUPLICADOS
            unique_criterios = []
            seen = set()
            for criterio in all_criterios:
                key = f"{criterio['tabla']}.{criterio['campo']}.{criterio['operador']}.{criterio['valor']}"
                if key not in seen:
                    unique_criterios.append(criterio)
                    seen.add(key)

            self.logger.info(f"   📊 Total criterios únicos: {len(unique_criterios)}")

            if unique_criterios:
                params = {
                    "criterio_principal": unique_criterios[0],
                    "filtros_adicionales": unique_criterios[1:] if len(unique_criterios) > 1 else []
                }

                self.logger.info(f"🎯 PARÁMETROS FINALES CONSTRUIDOS:")
                self.logger.info(f"   🎯 Criterio principal: {params['criterio_principal']}")
                self.logger.info(f"   🔧 Filtros adicionales ({len(params['filtros_adicionales'])}):")
                for i, filtro in enumerate(params['filtros_adicionales']):
                    self.logger.info(f"      {i+1}. {filtro}")

                return params
            else:
                # FALLBACK: búsqueda genérica
                self.logger.warning("⚠️ No se encontraron criterios, usando fallback")
                params = {
                    "criterio_principal": {
                        "tabla": "alumnos",
                        "campo": "nombre",
                        "operador": "LIKE",
                        "valor": ""
                    }
                }
                self.logger.info(f"🎯 Parámetros fallback: {params}")
                return params

        except Exception as e:
            self.logger.error(f"❌ Error construyendo parámetros con filtros del Master: {e}")
            return {
                "criterio_principal": {
                    "tabla": "alumnos",
                    "campo": "nombre",
                    "operador": "LIKE",
                    "valor": ""
                }
            }

    def _map_field_with_database_context(self, campo: str, valor: str, filtro_original: str) -> Optional[Dict[str, Any]]:
        """
        🧠 MAPEO INTELIGENTE DE CAMPOS USANDO CONTEXTO ESTRUCTURAL COMPLETO

        Usa LLM con acceso completo a la estructura de la base de datos para mapear
        campos del usuario a campos reales de la DB.

        Args:
            campo: Campo del usuario (ej: "apellido", "nombre")
            valor: Valor a buscar (ej: "Martinez")
            filtro_original: Filtro original completo para contexto

        Returns:
            Criterio mapeado o None si no se puede mapear
        """
        try:
            # 🧠 USAR LLM PARA MAPEO INTELIGENTE
            mapping_prompt = f"""
TAREA: Mapear campo del usuario a estructura real de base de datos.

ESTRUCTURA DE BASE DE DATOS:
- Tabla 'alumnos': id, curp, nombre, matricula, fecha_nacimiento
- Tabla 'datos_escolares': alumno_id, grado, grupo, turno, ciclo_escolar, calificaciones

EJEMPLOS DE DATOS:
- alumnos.nombre: "JUAN GARCIA LOPEZ" (nombre completo con apellidos)
- datos_escolares.grado: 1, 2, 3, 4, 5, 6
- datos_escolares.grupo: "A", "B", "C"
- datos_escolares.turno: "MATUTINO", "VESPERTINO"

FILTRO DEL USUARIO: "{filtro_original}"
- Campo: "{campo}"
- Valor: "{valor}"

INSTRUCCIONES:
1. Analiza dónde está la información que busca el usuario
2. Si busca "apellido", la info está en alumnos.nombre (nombre completo)
3. Si busca "grado", está en datos_escolares.grado
4. Determina tabla, campo, operador y valor correctos

RESPONDE SOLO EN FORMATO JSON:
{{
    "tabla": "nombre_tabla",
    "campo": "nombre_campo",
    "operador": "LIKE|=|>|<",
    "valor": "valor_procesado",
    "razonamiento": "explicación breve"
}}
"""

            # Llamar al LLM
            from app.core.ai.llm_client import LLMClient
            llm_client = LLMClient()

            response = llm_client.generate_response(mapping_prompt)

            # Parsear respuesta JSON
            import json
            try:
                mapping_result = json.loads(response.strip())

                # Validar que tiene los campos requeridos
                required_fields = ['tabla', 'campo', 'operador', 'valor']
                if all(field in mapping_result for field in required_fields):
                    self.logger.info(f"🧠 Mapeo LLM exitoso: {campo} → {mapping_result}")
                    return mapping_result
                else:
                    self.logger.warning(f"⚠️ Respuesta LLM incompleta: {mapping_result}")
                    return self._fallback_mapping(campo, valor)

            except json.JSONDecodeError as e:
                self.logger.warning(f"⚠️ Error parseando respuesta LLM: {e}")
                return self._fallback_mapping(campo, valor)

        except Exception as e:
            self.logger.error(f"❌ Error en mapeo inteligente: {e}")
            return self._fallback_mapping(campo, valor)

    def _fallback_mapping(self, campo: str, valor: str) -> Optional[Dict[str, Any]]:
        """
        🔧 FALLBACK MÍNIMO CUANDO LLM FALLA COMPLETAMENTE
        Solo devuelve None para forzar el uso del LLM
        """
        self.logger.error(f"❌ FALLBACK ACTIVADO: LLM falló mapeando '{campo}': '{valor}'")
        self.logger.error(f"❌ ESTO NO DEBERÍA PASAR - REVISAR CONFIGURACIÓN LLM")

        # 🚫 NO HARDCODEAR NADA - FORZAR USO DE LLM
        return None

    def build_buscar_universal_with_context(self, query: str, conversation_stack: list = None) -> Dict[str, Any]:
        """
        🎯 CONSTRUIR PARÁMETROS PARA BUSCAR_UNIVERSAL CON CONTEXTO (CORREGIDO)
        Combina criterios del contexto conversacional con la nueva consulta

        🔧 CORRECCIÓN: Mejor lógica de composición y logging detallado
        """
        try:
            self.logger.info(f"🎯 Construyendo parámetros BUSCAR_UNIVERSAL con contexto")
            self.logger.info(f"   📝 Query: '{query}'")
            self.logger.info(f"   📚 Stack size: {len(conversation_stack or [])}")

            # EXTRAER CRITERIOS DEL CONTEXTO
            context_criteria = self._extract_criteria_from_context(conversation_stack or [])
            self.logger.info(f"   🧠 Criterios del contexto: {context_criteria}")

            # EXTRAER CRITERIOS DE LA CONSULTA ACTUAL
            query_criteria = self._extract_criteria_from_query(query)
            self.logger.info(f"   🔍 Criterios de la consulta: {query_criteria}")

            # 🔧 NUEVA LÓGICA DE COMPOSICIÓN
            all_criterios = []

            # Agregar criterios del contexto
            if context_criteria:
                all_criterios.append(context_criteria["criterio_principal"])
                all_criterios.extend(context_criteria.get("filtros_adicionales", []))
                self.logger.info(f"   ✅ Agregados {1 + len(context_criteria.get('filtros_adicionales', []))} criterios del contexto")

            # Agregar criterios de la consulta actual
            all_criterios.extend(query_criteria)
            self.logger.info(f"   ✅ Agregados {len(query_criteria)} criterios de la consulta")

            # 🔧 ELIMINAR DUPLICADOS MANTENIENDO ORDEN
            unique_criterios = []
            seen = set()
            for criterio in all_criterios:
                key = f"{criterio['tabla']}.{criterio['campo']}.{criterio['operador']}.{criterio['valor']}"
                if key not in seen:
                    unique_criterios.append(criterio)
                    seen.add(key)
                else:
                    self.logger.info(f"   🔄 Criterio duplicado eliminado: {criterio}")

            self.logger.info(f"   📊 Total criterios únicos: {len(unique_criterios)}")

            if unique_criterios:
                params = {
                    "criterio_principal": unique_criterios[0],
                    "filtros_adicionales": unique_criterios[1:] if len(unique_criterios) > 1 else []
                }

                self.logger.info(f"🎯 PARÁMETROS FINALES CONSTRUIDOS:")
                self.logger.info(f"   🎯 Criterio principal: {params['criterio_principal']}")
                self.logger.info(f"   🔧 Filtros adicionales ({len(params['filtros_adicionales'])}):")
                for i, filtro in enumerate(params['filtros_adicionales']):
                    self.logger.info(f"      {i+1}. {filtro}")

                return params
            else:
                # FALLBACK: búsqueda genérica
                self.logger.warning("⚠️ No se encontraron criterios, usando fallback")
                params = {
                    "criterio_principal": {
                        "tabla": "alumnos",
                        "campo": "nombre",
                        "operador": "LIKE",
                        "valor": ""
                    }
                }
                self.logger.info(f"🎯 Parámetros fallback: {params}")
                return params

        except Exception as e:
            self.logger.error(f"❌ Error construyendo parámetros BUSCAR_UNIVERSAL: {e}")
            return {
                "criterio_principal": {
                    "tabla": "alumnos",
                    "campo": "nombre",
                    "operador": "LIKE",
                    "valor": ""
                }
            }

    def _execute_contar_alumnos(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔄 EJECUTA CONTAR_ALUMNOS REDIRIGIENDO A CONTAR_UNIVERSAL
        Convierte parámetros de CONTAR_ALUMNOS al formato de CONTAR_UNIVERSAL
        """
        try:
            self.logger.info("🔄 Ejecutando CONTAR_ALUMNOS → CONTAR_UNIVERSAL")
            self.logger.info(f"🔍 Parámetros recibidos: {params}")

            criterio_campo = params.get("criterio_campo")
            criterio_valor = params.get("criterio_valor")

            # Convertir a formato CONTAR_UNIVERSAL
            if criterio_campo and criterio_valor:
                # Manejar valores especiales para calificaciones
                if criterio_campo.lower() == "calificaciones":
                    if criterio_valor.upper() == "NOT NULL":
                        operador = "!="
                        valor = "[]"
                    elif criterio_valor.upper() == "NULL":
                        operador = "="
                        valor = "[]"
                    else:
                        operador = "="
                        valor = criterio_valor.upper()
                else:
                    operador = "="
                    valor = criterio_valor.upper()

                universal_params = {
                    "criterio_principal": {
                        "tabla": "datos_escolares",
                        "campo": criterio_campo,
                        "operador": operador,
                        "valor": valor
                    }
                }
            else:
                # Conteo sin criterios específicos - contar todos
                universal_params = {
                    "criterio_principal": {
                        "tabla": "alumnos",
                        "campo": "id",
                        "operador": ">",
                        "valor": "0"
                    }
                }

            self.logger.info(f"🎯 Parámetros convertidos para CONTAR_UNIVERSAL: {universal_params}")

            # Ejecutar CONTAR_UNIVERSAL con parámetros convertidos
            result = self._execute_contar_universal(universal_params)

            # Cambiar el action_used para mantener compatibilidad
            if result.get("success"):
                result["action_used"] = "CONTAR_ALUMNOS"

            return result

        except Exception as e:
            self.logger.error(f"Error en CONTAR_ALUMNOS: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_calcular_estadistica(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta cálculo estadístico"""

        tipo = params.get("tipo", "conteo")
        if tipo:
            tipo = tipo.lower()
        else:
            tipo = "conteo"

        agrupar_por = params.get("agrupar_por", "")

        # 🎯 MANEJAR FILTRO QUE PUEDE VENIR COMO STRING JSON
        filtro_raw = params.get("filtro", {})
        if isinstance(filtro_raw, str):
            try:
                import json
                filtro = json.loads(filtro_raw)
            except:
                filtro = {}
        else:
            filtro = filtro_raw if filtro_raw else {}

        incluir_detalles_raw = params.get("incluir_detalles", "false")
        if incluir_detalles_raw:
            incluir_detalles = str(incluir_detalles_raw).lower() in ['true', '1', 'yes', 'sí']
        else:
            incluir_detalles = False

        try:
            # 🎯 NIVEL 1: ESTADÍSTICAS BÁSICAS
            if tipo == "conteo":
                return self._calcular_conteo(agrupar_por, filtro, incluir_detalles)
            elif tipo == "distribucion":
                return self._calcular_distribucion(agrupar_por, filtro, incluir_detalles)
            # 🎯 NIVEL 2: PROMEDIOS IMPLEMENTADOS
            elif tipo == "promedio":
                return self._calcular_promedio(agrupar_por, filtro, params)
            elif tipo == "ranking":
                return self._error_result("Rankings en desarrollo")
            elif tipo == "comparacion":
                return self._error_result("Comparaciones en desarrollo")
            else:
                return self._error_result(f"Tipo de estadística no soportado: {tipo}")

        except Exception as e:
            self.logger.error(f"Error calculando estadística: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _calcular_conteo(self, agrupar_por: str, filtro: dict, incluir_detalles: bool) -> Dict[str, Any]:
        """Calcula conteos, opcionalmente agrupados"""

        try:
            if agrupar_por:
                # 🎯 CASO ESPECIAL: AGRUPAR POR CALIFICACIONES (CON vs SIN)
                if agrupar_por.lower() == "calificaciones":
                    sql = """
                    SELECT
                        CASE
                            WHEN de.calificaciones IS NOT NULL AND de.calificaciones != '' AND de.calificaciones != '[]'
                            THEN 'CON_CALIFICACIONES'
                            ELSE 'SIN_CALIFICACIONES'
                        END as grupo_calificaciones,
                        COUNT(*) as cantidad
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE 1=1
                    """

                    # Aplicar filtros si existen
                    if isinstance(filtro, dict):
                        for campo, valor in filtro.items():
                            if campo in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                                sql += f" AND de.{campo} = '{str(valor).upper()}'"
                            elif campo in ['nombre', 'curp', 'matricula']:
                                sql += f" AND a.{campo} LIKE '%{str(valor).upper()}%'"

                    sql += " GROUP BY grupo_calificaciones ORDER BY grupo_calificaciones"
                else:
                    # 📊 CONTEO AGRUPADO NORMAL (ej: por grado, por turno)
                    sql = f"""
                    SELECT {agrupar_por}, COUNT(*) as cantidad
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE 1=1
                    """

                    # Aplicar filtros si existen
                    if isinstance(filtro, dict):
                        for campo, valor in filtro.items():
                            if campo in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                                sql += f" AND de.{campo} = '{str(valor).upper()}'"
                            elif campo in ['nombre', 'curp', 'matricula']:
                                sql += f" AND a.{campo} LIKE '%{str(valor).upper()}%'"

                    sql += f" GROUP BY {agrupar_por} ORDER BY {agrupar_por}"

                result = self.sql_executor.execute_query(sql)
                if result.success:
                    # Formatear resultados agrupados
                    estadisticas = {}
                    total = 0
                    for row in result.data:
                        # 🔧 MANEJAR CASO ESPECIAL DE CALIFICACIONES
                        if agrupar_por.lower() == "calificaciones":
                            grupo = row['grupo_calificaciones']
                        else:
                            grupo = row[agrupar_por]
                        cantidad = row['cantidad']
                        estadisticas[str(grupo)] = cantidad
                        total += cantidad

                    return {
                        "success": True,
                        "data": [estadisticas],  # Lista para compatibilidad
                        "row_count": len(estadisticas),
                        "action_used": "CALCULAR_ESTADISTICA",
                        "message": f"Conteo por {agrupar_por}: {len(estadisticas)} grupos, {total} total",
                        "sql_executed": sql,
                        "estadistica_tipo": "conteo_agrupado",
                        "total_elementos": total,
                        "grupos": len(estadisticas)
                    }
                else:
                    return self._error_result(f"Error en consulta agrupada: {result.message}")

            else:
                # 📊 CONTEO SIMPLE (total de alumnos)
                sql = """
                SELECT COUNT(*) as total
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE 1=1
                """

                # Aplicar filtros si existen
                if isinstance(filtro, dict):
                    for campo, valor in filtro.items():
                        if campo in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                            sql += f" AND de.{campo} = '{str(valor).upper()}'"
                        elif campo in ['nombre', 'curp', 'matricula']:
                            sql += f" AND a.{campo} LIKE '%{str(valor).upper()}%'"

                result = self.sql_executor.execute_query(sql)
                if result.success and result.data:
                    total = result.data[0]['total']
                    return {
                        "success": True,
                        "data": [{"total": total}],
                        "row_count": 1,
                        "action_used": "CALCULAR_ESTADISTICA",
                        "message": f"Total de alumnos: {total}",
                        "sql_executed": sql,
                        "estadistica_tipo": "conteo_simple",
                        "total_elementos": total
                    }
                else:
                    return self._error_result(f"Error en conteo simple: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en _calcular_conteo: {e}")
            return self._error_result(f"Error calculando conteo: {str(e)}")

    def _calcular_distribucion(self, agrupar_por: str, filtro: dict, incluir_detalles: bool) -> Dict[str, Any]:
        """Calcula distribución porcentual"""

        try:
            # Primero obtener el conteo agrupado
            conteo_result = self._calcular_conteo(agrupar_por, filtro, incluir_detalles)

            if not conteo_result.get("success"):
                return conteo_result

            # Calcular porcentajes
            estadisticas = conteo_result["data"][0]
            total = conteo_result.get("total_elementos", 0)

            if total == 0:
                return self._error_result("No hay datos para calcular distribución")

            distribucion = {}
            for grupo, cantidad in estadisticas.items():
                porcentaje = round((cantidad / total) * 100, 1)
                distribucion[grupo] = {
                    "cantidad": cantidad,
                    "porcentaje": porcentaje
                }

            return {
                "success": True,
                "data": [distribucion],
                "row_count": len(distribucion),
                "action_used": "CALCULAR_ESTADISTICA",
                "message": f"Distribución por {agrupar_por}: {len(distribucion)} grupos",
                "sql_executed": conteo_result.get("sql_executed", ""),
                "estadistica_tipo": "distribucion",
                "total_elementos": total,
                "grupos": len(distribucion)
            }

        except Exception as e:
            self.logger.error(f"Error en _calcular_distribucion: {e}")
            return self._error_result(f"Error calculando distribución: {str(e)}")

    def _calcular_promedio(self, agrupar_por: str, filtro: dict, params: dict) -> Dict[str, Any]:
        """Calcula promedios, especialmente de edad calculada desde fecha_nacimiento"""

        try:
            campo = params.get("campo", "edad")

            if campo == "edad":
                # 🎯 CALCULAR EDAD DESDE FECHA_NACIMIENTO
                if agrupar_por:
                    # Promedio de edad agrupado
                    sql = f"""
                    SELECT de.{agrupar_por},
                           AVG((julianday('now') - julianday(a.fecha_nacimiento)) / 365.25) as promedio_edad
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE a.fecha_nacimiento IS NOT NULL
                    """

                    # Aplicar filtros si existen
                    if isinstance(filtro, dict):
                        for campo_filtro, valor in filtro.items():
                            if campo_filtro in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                                sql += f" AND de.{campo_filtro} = '{str(valor).upper()}'"

                    sql += f" GROUP BY de.{agrupar_por} ORDER BY de.{agrupar_por}"

                    result = self.sql_executor.execute_query(sql)
                    if result.success:
                        # Formatear resultados agrupados
                        promedios = {}
                        for row in result.data:
                            grupo = row[agrupar_por]
                            promedio = round(row['promedio_edad'], 1)
                            promedios[str(grupo)] = promedio

                        return {
                            "success": True,
                            "data": [promedios],
                            "row_count": len(promedios),
                            "action_used": "CALCULAR_ESTADISTICA",
                            "message": f"Promedio de edad por {agrupar_por}: {len(promedios)} grupos",
                            "sql_executed": sql,
                            "estadistica_tipo": "promedio_agrupado",
                            "campo_calculado": "edad",
                            "grupos": len(promedios)
                        }
                    else:
                        return self._error_result(f"Error en consulta de promedio: {result.message}")
                else:
                    # Promedio general de edad
                    sql = """
                    SELECT AVG((julianday('now') - julianday(a.fecha_nacimiento)) / 365.25) as promedio_edad
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE a.fecha_nacimiento IS NOT NULL
                    """

                    # Aplicar filtros si existen
                    if isinstance(filtro, dict):
                        for campo_filtro, valor in filtro.items():
                            if campo_filtro in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                                sql += f" AND de.{campo_filtro} = '{str(valor).upper()}'"

                    result = self.sql_executor.execute_query(sql)
                    if result.success and result.data:
                        promedio = round(result.data[0]['promedio_edad'], 1)
                        return {
                            "success": True,
                            "data": [{"promedio_edad": promedio}],
                            "row_count": 1,
                            "action_used": "CALCULAR_ESTADISTICA",
                            "message": f"Promedio general de edad: {promedio} años",
                            "sql_executed": sql,
                            "estadistica_tipo": "promedio_simple",
                            "campo_calculado": "edad"
                        }
                    else:
                        return self._error_result(f"Error calculando promedio general: {result.message}")
            elif campo == "calificaciones":
                # 🎯 CALCULAR PROMEDIO GENERAL DE CALIFICACIONES
                if agrupar_por:
                    # Promedio de calificaciones agrupado
                    sql = f"""
                    SELECT de.{agrupar_por},
                           AVG(
                               (SELECT AVG(CAST(json_extract(value, '$.promedio') AS REAL))
                                FROM json_each(de.calificaciones)
                                WHERE json_extract(value, '$.promedio') IS NOT NULL
                                AND json_extract(value, '$.promedio') != 0)
                           ) as promedio_calificaciones
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NOT NULL
                      AND de.calificaciones != '[]'
                      AND de.calificaciones != ''
                    """

                    # Aplicar filtros si existen
                    if isinstance(filtro, dict):
                        for campo_filtro, valor in filtro.items():
                            if campo_filtro in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                                sql += f" AND de.{campo_filtro} = '{str(valor).upper()}'"

                    sql += f" GROUP BY de.{agrupar_por} ORDER BY de.{agrupar_por}"

                    result = self.sql_executor.execute_query(sql)
                    if result.success:
                        # Formatear resultados agrupados
                        promedios = {}
                        for row in result.data:
                            grupo = row[agrupar_por]
                            promedio = round(row['promedio_calificaciones'], 2) if row['promedio_calificaciones'] else 0
                            promedios[str(grupo)] = promedio

                        return {
                            "success": True,
                            "data": [promedios],
                            "row_count": len(promedios),
                            "action_used": "CALCULAR_ESTADISTICA",
                            "message": f"Promedio de calificaciones por {agrupar_por}: {len(promedios)} grupos",
                            "sql_executed": sql,
                            "estadistica_tipo": "promedio_agrupado",
                            "campo_calculado": "calificaciones",
                            "grupos": len(promedios)
                        }
                    else:
                        return self._error_result(f"Error en consulta de promedio: {result.message}")
                else:
                    # Promedio general de calificaciones
                    sql = """
                    SELECT AVG(
                        (SELECT AVG(CAST(json_extract(value, '$.promedio') AS REAL))
                         FROM json_each(de.calificaciones)
                         WHERE json_extract(value, '$.promedio') IS NOT NULL
                         AND json_extract(value, '$.promedio') != 0)
                    ) as promedio_general
                    FROM alumnos a
                    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NOT NULL
                      AND de.calificaciones != '[]'
                      AND de.calificaciones != ''
                    """

                    # Aplicar filtros si existen
                    if isinstance(filtro, dict):
                        for campo_filtro, valor in filtro.items():
                            if campo_filtro in ['grado', 'grupo', 'turno', 'ciclo_escolar']:
                                sql += f" AND de.{campo_filtro} = '{str(valor).upper()}'"

                    result = self.sql_executor.execute_query(sql)
                    if result.success and result.data:
                        promedio = round(result.data[0]['promedio_general'], 2) if result.data[0]['promedio_general'] else 0
                        return {
                            "success": True,
                            "data": [{"promedio_general": promedio}],
                            "row_count": 1,
                            "action_used": "CALCULAR_ESTADISTICA",
                            "message": f"Promedio general de calificaciones: {promedio}",
                            "sql_executed": sql,
                            "estadistica_tipo": "promedio_simple",
                            "campo_calculado": "calificaciones"
                        }
                    else:
                        return self._error_result(f"Error calculando promedio general: {result.message}")
            else:
                return self._error_result(f"Campo '{campo}' no soportado para promedios. Campos disponibles: 'edad', 'calificaciones'.")

        except Exception as e:
            self.logger.error(f"Error en _calcular_promedio: {e}")
            return self._error_result(f"Error calculando promedio: {str(e)}")

    def _execute_listado_completo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        📋 EJECUTA LISTADO COMPLETO
        Genera un listado completo de alumnos con filtros opcionales
        """
        try:
            criterio_filtro = params.get("criterio_filtro", {})
            ordenar_por = params.get("ordenar_por", "nombre")
            incluir_calificaciones = params.get("incluir_calificaciones", True)

            self.logger.info(f"📋 Ejecutando LISTADO COMPLETO:")
            self.logger.info(f"   - Criterio filtro: {criterio_filtro}")
            self.logger.info(f"   - Ordenar por: {ordenar_por}")
            self.logger.info(f"   - Incluir calificaciones: {incluir_calificaciones}")

            # Si hay criterio de filtro, convertir a formato BUSCAR_UNIVERSAL
            if criterio_filtro:
                # Si es string, convertir a criterios estructurados
                if isinstance(criterio_filtro, str):
                    criterios = self._parse_filter_string_to_criteria(criterio_filtro)
                    if criterios:
                        return self._execute_buscar_universal(criterios)
                elif isinstance(criterio_filtro, dict):
                    return self._execute_buscar_universal(criterio_filtro)

            # Si no hay filtro, obtener todos los alumnos
            sql = """
            SELECT a.*, de.*
            FROM alumnos a
            LEFT JOIN datos_escolares de ON a.id = de.alumno_id
            ORDER BY a.nombre
            """

            self.logger.info(f"🔧 SQL generado: {sql}")

            # Ejecutar consulta
            result = self.sql_executor.execute_query(sql)

            if result.success:
                self.logger.info(f"✅ Listado completo generado: {result.row_count} resultado(s)")
                return {
                    "success": True,
                    "data": result.data,
                    "row_count": result.row_count,
                    "action_used": "GENERAR_LISTADO_COMPLETO",
                    "message": f"Listado completo generado: {result.row_count} resultado(s)"
                }
            else:
                return self._error_result(f"Error en listado completo: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en listado completo: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_preparar_constancia(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta preparación de datos para constancia"""

        alumno_identificador = params.get("alumno_identificador", "")
        tipo_constancia = params.get("tipo_constancia", "estudio")

        try:
            # 🎯 USAR SISTEMA EXISTENTE DE CONSTANCIAS
            from app.core.service_provider import ServiceProvider
            from app.core.ai.interpretation.student_query.constancia_processor import ConstanciaProcessor

            # Obtener servicios
            service_provider = ServiceProvider.get_instance()
            constancia_processor = ConstanciaProcessor()

            # 1. Buscar alumno por identificador
            if alumno_identificador.isdigit():
                # Buscar por ID
                alumno = service_provider.alumno_service.get_by_id(int(alumno_identificador))
                if not alumno:
                    return self._error_result(f"No se encontró alumno con ID {alumno_identificador}")
                alumno_dict = alumno.to_dict()
            else:
                # Buscar por nombre o CURP
                sql = f"""
                SELECT a.*, de.grado, de.grupo, de.turno, de.ciclo_escolar
                FROM alumnos a
                LEFT JOIN datos_escolares de ON a.id = de.alumno_id
                WHERE a.nombre LIKE '%{alumno_identificador.upper()}%'
                   OR a.curp LIKE '%{alumno_identificador.upper()}%'
                LIMIT 1
                """

                result = self.sql_executor.execute_query(sql, 10)  # Límite bajo para búsqueda individual
                if not result.success or result.row_count == 0:
                    return self._error_result(f"No se encontró alumno: {alumno_identificador}")

                alumno_dict = result.data[0]

            # 2. Validar datos para el tipo de constancia
            validation_result = constancia_processor._validate_student_data(alumno_dict, tipo_constancia)
            if not validation_result['valid']:
                return self._error_result(f"Validación falló: {validation_result['message']}")

            # 3. Preparar datos completos para constancia
            datos_preparados = {
                "alumno": alumno_dict,
                "tipo_constancia": tipo_constancia,
                "validacion": validation_result,
                "puede_generar": True,
                "requisitos_cumplidos": validation_result.get('requirements_met', []),
                "datos_faltantes": validation_result.get('missing_data', [])
            }

            return {
                "success": True,
                "data": [datos_preparados],  # Lista para compatibilidad
                "row_count": 1,
                "action_used": "PREPARAR_DATOS_CONSTANCIA",
                "message": f"Datos preparados para constancia de {tipo_constancia}",
                "sql_executed": f"Preparación de datos para {alumno_dict.get('nombre', 'N/A')}"
            }

        except Exception as e:
            self.logger.error(f"Error preparando datos de constancia: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_generar_constancia_completa(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta generación completa de constancia"""

        alumno_identificador = params.get("alumno_identificador", "")
        tipo_constancia = params.get("tipo_constancia", "estudio")
        incluir_foto = params.get("incluir_foto", False)
        preview_mode = params.get("preview_mode", True)

        try:
            # 🎯 USAR SISTEMA EXISTENTE DE CONSTANCIAS DIRECTAMENTE
            from app.core.ai.interpretation.student_query.constancia_processor import ConstanciaProcessor

            # 1. Buscar alumno (reutilizar lógica de PREPARAR_DATOS_CONSTANCIA)
            preparar_result = self._execute_preparar_constancia({
                "alumno_identificador": alumno_identificador,
                "tipo_constancia": tipo_constancia,
                "incluir_calificaciones": tipo_constancia == "calificaciones"
            })

            if not preparar_result.get("success"):
                return preparar_result  # Retornar error de preparación

            # 2. Obtener datos del alumno
            datos_preparados = preparar_result["data"][0]
            alumno_dict = datos_preparados["alumno"]

            # 3. Generar constancia usando ConstanciaProcessor
            constancia_processor = ConstanciaProcessor()

            # Convertir incluir_foto a boolean si es string
            if isinstance(incluir_foto, str):
                incluir_foto = incluir_foto.lower() in ['true', '1', 'yes', 'sí']
            if isinstance(preview_mode, str):
                preview_mode = preview_mode.lower() in ['true', '1', 'yes', 'sí']

            # Simular user_query para detección de foto
            user_query = f"constancia de {tipo_constancia} para {alumno_dict.get('nombre', '')}"
            if incluir_foto:
                user_query += " con foto"

            # Generar constancia
            result = constancia_processor.process_constancia_request(
                alumno_dict, tipo_constancia, user_query
            )

            if result and result.action == "constancia_preview":
                # 🎯 PRESERVAR LA ACCIÓN ORIGINAL PARA QUE LLEGUE AL UI
                return {
                    "success": True,
                    "data": [result.parameters],  # Lista para compatibilidad
                    "row_count": 1,
                    "action_used": "constancia_preview",  # ← PRESERVAR ACCIÓN ORIGINAL
                    "message": f"Constancia de {tipo_constancia} generada para {alumno_dict.get('nombre', 'N/A')}",
                    "sql_executed": f"Generación completa de constancia",
                    "original_action": "GENERAR_CONSTANCIA_COMPLETA",  # ← ACCIÓN TÉCNICA
                    "constancia_result": result  # Resultado completo para procesamiento posterior
                }
            else:
                return self._error_result(f"Error generando constancia: {result.parameters.get('message', 'Error desconocido') if result else 'No se pudo procesar'}")

        except Exception as e:
            self.logger.error(f"Error generando constancia completa: {e}")
            return self._error_result(f"Error interno: {str(e)}")



    def _execute_filtrar_por_calificaciones(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta filtrado por calificaciones"""

        tiene_calificaciones = params.get("tiene_calificaciones", "true")
        mostrar_detalles = params.get("mostrar_detalles", "true")

        # Convertir strings a boolean
        tiene_cal_bool = str(tiene_calificaciones).lower() in ['true', '1', 'yes', 'sí']
        mostrar_detalles_bool = str(mostrar_detalles).lower() in ['true', '1', 'yes', 'sí']

        try:
            if mostrar_detalles_bool:
                # Mostrar lista de alumnos
                if tiene_cal_bool:
                    # Alumnos CON calificaciones
                    sql = """
                    SELECT a.*, de.*
                    FROM alumnos a
                    JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NOT NULL
                      AND de.calificaciones != ''
                      AND de.calificaciones != '[]'
                    ORDER BY a.nombre
                    """
                    mensaje = "Alumnos con calificaciones registradas"
                else:
                    # Alumnos SIN calificaciones
                    sql = """
                    SELECT a.*, de.*
                    FROM alumnos a
                    JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NULL
                       OR de.calificaciones = ''
                       OR de.calificaciones = '[]'
                    ORDER BY a.nombre
                    """
                    mensaje = "Alumnos sin calificaciones registradas"
            else:
                # Solo conteo
                if tiene_cal_bool:
                    sql = """
                    SELECT COUNT(*) as total
                    FROM alumnos a
                    JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NOT NULL
                      AND de.calificaciones != ''
                      AND de.calificaciones != '[]'
                    """
                    mensaje = "Conteo de alumnos con calificaciones"
                else:
                    sql = """
                    SELECT COUNT(*) as total
                    FROM alumnos a
                    JOIN datos_escolares de ON a.id = de.alumno_id
                    WHERE de.calificaciones IS NULL
                       OR de.calificaciones = ''
                       OR de.calificaciones = '[]'
                    """
                    mensaje = "Conteo de alumnos sin calificaciones"

            # 🚀 USAR LÍMITE ALTO PARA OBTENER TODOS LOS RESULTADOS
            query_limit = 1000  # Mismo límite que BUSCAR_UNIVERSAL
            result = self.sql_executor.execute_query(sql, query_limit)

            if result.success:
                return {
                    "success": True,
                    "data": result.data,
                    "row_count": result.row_count,
                    "action_used": "FILTRAR_POR_CALIFICACIONES",
                    "message": f"{mensaje}: {result.row_count} resultado(s)",
                    "sql_executed": sql,  # 🆕 AGREGAR SQL PARA ANÁLISIS DINÁMICO
                    "filtro_aplicado": "con_calificaciones" if tiene_cal_bool else "sin_calificaciones"
                }
            else:
                return self._error_result(f"Error filtrando por calificaciones: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en _execute_filtrar_por_calificaciones: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_sequential_actions(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Estrategia secuencial no implementada - usar estrategia simple"""
        return self._error_result("Estrategia secuencial no implementada. Use estrategia 'simple'.")

    def _execute_combined_actions(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Estrategia combinada no implementada - usar estrategia simple"""
        return self._error_result("Estrategia combinada no implementada. Use estrategia 'simple'.")

    def _error_result(self, message: str) -> Dict[str, Any]:
        """Genera resultado de error estándar"""
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "action_used": "ERROR",
            "message": message
        }
