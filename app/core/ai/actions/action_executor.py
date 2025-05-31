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

from typing import Dict, List, Any, Optional, Tuple
import logging
import os
from .action_catalog import ActionCatalog, ActionDefinition

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

    def _debug_pause_if_enabled(self, message: str):
        """🛑 PAUSA DE DEBUG CONTROLADA POR VARIABLE DE ENTORNO"""
        if os.environ.get('DEBUG_PAUSES', 'false').lower() == 'true':
            input(f"🛑 {message}")

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

        # Obtener definición de la acción
        action_def = self.catalog.get_action_definition(action_name)

        # Ejecutar según el tipo de acción
        if action_name == "BUSCAR_UNIVERSAL":
            return self._execute_buscar_universal(params)
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
        elif action_name == "CALCULAR_ESTADISTICA":
            return self._execute_calcular_estadistica(params)
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

            # 🛑 PAUSA CRÍTICA 3: ANÁLISIS DE FILTROS DE PROMEDIO
            self.logger.info("🛑 PAUSA CRÍTICA 3: ANÁLISIS DE FILTROS")
            self.logger.info(f"   ├── Filtros adicionales recibidos: {len(filtros_adicionales)}")
            for i, filtro in enumerate(filtros_adicionales):
                self.logger.info(f"   ├── Filtro {i+1}: {filtro}")
                campo = filtro.get("campo", "")
                self.logger.info(f"   │   ├── Campo: '{campo}'")
                self.logger.info(f"   │   └── ¿Contiene 'promedio'? {'SÍ' if 'promedio' in campo.lower() else 'NO'}")
            self._debug_pause_if_enabled("PAUSA 3: Presiona ENTER para continuar con filtrado de promedio...")

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

            tabla_principal = criterio_principal.get("tabla", "alumnos")
            campo_principal = criterio_principal.get("campo", "")
            operador_principal = criterio_principal.get("operador", "=")
            valor_principal = criterio_principal.get("valor", "")

            if not campo_principal or not valor_principal:
                return self._error_result("campo y valor son requeridos en criterio_principal")

            # 🔒 VALIDAR CAMPOS DINÁMICAMENTE
            if not self._validate_field_dynamically(tabla_principal, campo_principal):
                return self._error_result(f"Campo '{campo_principal}' no válido para tabla '{tabla_principal}'")

            # 🔧 CONSTRUIR SQL DINÁMICAMENTE
            sql = self._build_dynamic_sql(criterio_principal, filtros_adicionales, join_logic, limit)

            # 🛑 PAUSA CRÍTICA 4: SQL GENERADO
            self.logger.info("🛑 PAUSA CRÍTICA 4: SQL FINAL GENERADO")
            self.logger.info(f"   ├── Criterios SQL finales: {len(filtros_adicionales)}")
            self.logger.info(f"   ├── Criterios promedio filtrados: {len(filtros_promedio)}")
            self.logger.info(f"   └── SQL generado:")
            for line in sql.split('\n'):
                if line.strip():
                    self.logger.info(f"       {line.strip()}")
            self._debug_pause_if_enabled("PAUSA 4: Presiona ENTER para ejecutar SQL...")

            self.logger.info(f"🔧 SQL generado: {sql}")

            # 🚀 EJECUTAR CONSULTA
            result = self.sql_executor.execute_query(sql)

            if result.success:
                self.logger.info(f"✅ Búsqueda universal completada: {result.row_count} resultado(s)")
                return {
                    "success": True,
                    "data": result.data,
                    "row_count": result.row_count,
                    "action_used": "BUSCAR_UNIVERSAL",
                    "message": f"Búsqueda universal completada: {result.row_count} resultado(s)"
                }
            else:
                return self._error_result(f"Error en búsqueda universal: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en búsqueda universal: {e}")
            return self._error_result(f"Error interno: {str(e)}")

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

        # 🎯 AGREGAR CRITERIO PRINCIPAL
        tabla_principal = criterio_principal.get("tabla", "alumnos")
        campo_principal = criterio_principal.get("campo")
        operador_principal = criterio_principal.get("operador", "=")
        valor_principal = criterio_principal.get("valor")

        tabla_prefix = "a" if tabla_principal == "alumnos" else "de"

        # Manejar operadores especiales
        if operador_principal.upper() == "LIKE":
            sql += f" AND {tabla_prefix}.{campo_principal} LIKE '%{valor_principal}%'"
        elif operador_principal.upper() == "JSON_PROMEDIO":
            # Filtrar por promedio general de calificaciones (promedio de todos los promedios)
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
            materia, promedio = valor_principal.split(":")
            promedio_minimo = float(promedio)
            sql += f"""
            AND EXISTS (
                SELECT 1 FROM json_each({tabla_prefix}.{campo_principal})
                WHERE json_extract(value, '$.nombre') = '{materia.upper()}'
                AND json_extract(value, '$.promedio') > {promedio_minimo}
            )"""
        elif campo_principal == "calificaciones" and operador_principal == "!=":
            # 🔧 MANEJO ESPECIAL PARA CALIFICACIONES != "[]" (CON CALIFICACIONES)
            sql += f" AND {tabla_prefix}.{campo_principal} IS NOT NULL AND {tabla_prefix}.{campo_principal} != '' AND {tabla_prefix}.{campo_principal} != '[]'"
        elif campo_principal == "calificaciones" and operador_principal == "=":
            # 🔧 MANEJO ESPECIAL PARA CALIFICACIONES = "[]" (SIN CALIFICACIONES)
            sql += f" AND ({tabla_prefix}.{campo_principal} IS NULL OR {tabla_prefix}.{campo_principal} = '' OR {tabla_prefix}.{campo_principal} = '[]')"
        else:
            sql += f" AND {tabla_prefix}.{campo_principal} {operador_principal} '{valor_principal}'"

        # 🎯 AGREGAR FILTROS ADICIONALES
        for filtro in filtros_adicionales:
            tabla_filtro = filtro.get("tabla", "alumnos")
            campo_filtro = filtro.get("campo")
            operador_filtro = filtro.get("operador", "=")
            valor_filtro = filtro.get("valor")

            if not campo_filtro or not valor_filtro:
                continue

            tabla_prefix = "a" if tabla_filtro == "alumnos" else "de"

            # Manejar operadores especiales
            if operador_filtro.upper() == "JSON_CONTAINS":
                sql += f" AND {tabla_prefix}.{campo_filtro} LIKE '%{valor_filtro}%'"
            elif operador_filtro.upper() == "LIKE":
                sql += f" AND {tabla_prefix}.{campo_filtro} LIKE '%{valor_filtro}%'"
            elif operador_filtro.upper() == "IN":
                # 🔧 MANEJO ESPECIAL PARA OPERADOR IN - SIN COMILLAS ALREDEDOR DEL VALOR
                # Convertir '[2, 7, 8, 11, 16]' a '(2, 7, 8, 11, 16)'
                if isinstance(valor_filtro, str) and valor_filtro.startswith('[') and valor_filtro.endswith(']'):
                    # Convertir formato de lista string a formato SQL IN
                    valor_sql = valor_filtro.replace('[', '(').replace(']', ')')
                    sql += f" AND {tabla_prefix}.{campo_filtro} {operador_filtro} {valor_sql}"
                else:
                    sql += f" AND {tabla_prefix}.{campo_filtro} {operador_filtro} {valor_filtro}"
            elif campo_filtro == "calificaciones" and operador_filtro == "!=":
                # 🔧 MANEJO ESPECIAL PARA CALIFICACIONES != "[]" (CON CALIFICACIONES)
                sql += f" AND {tabla_prefix}.{campo_filtro} IS NOT NULL AND {tabla_prefix}.{campo_filtro} != '' AND {tabla_prefix}.{campo_filtro} != '[]'"
            elif campo_filtro == "calificaciones" and operador_filtro == "=":
                # 🔧 MANEJO ESPECIAL PARA CALIFICACIONES = "[]" (SIN CALIFICACIONES)
                sql += f" AND ({tabla_prefix}.{campo_filtro} IS NULL OR {tabla_prefix}.{campo_filtro} = '' OR {tabla_prefix}.{campo_filtro} = '[]')"
            else:
                sql += f" AND {tabla_prefix}.{campo_filtro} {operador_filtro} '{valor_filtro}'"

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
        🧠 EXTRAER CRITERIOS DEL CONTEXTO CONVERSACIONAL (CORREGIDO)
        Para construir BUSCAR_UNIVERSAL con filtros de consultas anteriores

        🔧 CORRECCIÓN: Ahora extrae criterios de TODAS las consultas anteriores
        """
        try:
            if not conversation_stack:
                self.logger.info("🔍 No hay pila conversacional disponible")
                return {}

            self.logger.info(f"🔍 Analizando pila conversacional con {len(conversation_stack)} niveles")

            # 🎯 EXTRAER CRITERIOS DE TODAS LAS CONSULTAS ANTERIORES
            all_criterios = []

            for i, context in enumerate(conversation_stack):
                if not isinstance(context, dict):
                    continue

                query = context.get('query', '').lower()
                self.logger.info(f"🔍 Nivel {i+1}: Analizando query '{query}'")

                level_criterios = []

                # FECHA DE NACIMIENTO
                for year in ['2013', '2014', '2015', '2016', '2017', '2018', '2019']:
                    if year in query:
                        criterio = {
                            "tabla": "alumnos",
                            "campo": "fecha_nacimiento",
                            "operador": "LIKE",
                            "valor": year
                        }
                        level_criterios.append(criterio)
                        self.logger.info(f"   ✅ Detectado criterio fecha: {criterio}")
                        break

                # GRADO (CORREGIDO - AGREGADOS PATRONES EN ESPAÑOL)
                grado_patterns = {
                    '1': ['primer', 'primero', '1er', '1°', 'grado 1', 'primer grado', 'primero grado'],
                    '2': ['segundo', '2do', '2°', 'grado 2', 'segundo grado'],
                    '3': ['tercer', 'tercero', '3er', '3°', 'grado 3', 'tercer grado', 'tercero grado'],
                    '4': ['cuarto', '4to', '4°', 'grado 4', 'cuarto grado'],
                    '5': ['quinto', '5to', '5°', 'grado 5', 'quinto grado'],
                    '6': ['sexto', '6to', '6°', 'grado 6', 'sexto grado']
                }

                for grado_num, patterns in grado_patterns.items():
                    if any(pattern in query for pattern in patterns):
                        criterio = {
                            "tabla": "datos_escolares",
                            "campo": "grado",
                            "operador": "=",
                            "valor": grado_num
                        }
                        level_criterios.append(criterio)
                        self.logger.info(f"   ✅ Detectado criterio grado: {criterio} (patrón: {[p for p in patterns if p in query]})")
                        break

                # TURNO
                if 'matutino' in query:
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "turno",
                        "operador": "=",
                        "valor": "MATUTINO"
                    }
                    level_criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio turno: {criterio}")
                elif 'vespertino' in query:
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "turno",
                        "operador": "=",
                        "valor": "VESPERTINO"
                    }
                    level_criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio turno: {criterio}")

                # GRUPO
                for grupo in ['A', 'B', 'C']:
                    if f'grupo {grupo.lower()}' in query or f'grupo {grupo}' in query or f'{grupo}' in query:
                        criterio = {
                            "tabla": "datos_escolares",
                            "campo": "grupo",
                            "operador": "=",
                            "valor": grupo
                        }
                        level_criterios.append(criterio)
                        self.logger.info(f"   ✅ Detectado criterio grupo: {criterio}")
                        break

                # SIN CALIFICACIONES (PRIORIDAD ALTA - DETECTAR PRIMERO)
                sin_calificaciones_patterns = [
                    'sin calificaciones', 'no tengan calificaciones', 'sin calificacion',
                    'que no tienen calificaciones', 'no tienen calificaciones'
                ]

                if any(pattern in query for pattern in sin_calificaciones_patterns):
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "calificaciones",
                        "operador": "=",
                        "valor": "[]"
                    }
                    level_criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio SIN calificaciones: {criterio}")
                else:
                    # CALIFICACIONES (SOLO SI NO SE DETECTÓ "SIN CALIFICACIONES")
                    calificaciones_patterns = [
                        'con calificaciones', 'tengan calificaciones',
                        'que tengan calificaciones', 'solo los que tengan calificaciones',
                        'con calificacion', 'que tienen calificaciones'
                    ]

                    if any(pattern in query for pattern in calificaciones_patterns):
                        criterio = {
                            "tabla": "datos_escolares",
                            "campo": "calificaciones",
                            "operador": "!=",
                            "valor": "[]"
                        }
                        level_criterios.append(criterio)
                        self.logger.info(f"   ✅ Detectado criterio CON calificaciones: {criterio}")

                # NOMBRE (búsquedas por nombre)
                if any(name in query for name in ['garcia', 'martinez', 'lopez', 'hernandez', 'franco', 'natalia', 'mario']):
                    for name in ['garcia', 'martinez', 'lopez', 'hernandez', 'franco', 'natalia', 'mario']:
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
        🧠 EXTRAER CRITERIOS DE LA CONSULTA ACTUAL (CORREGIDO)
        Para agregar como filtros adicionales

        🔧 CORRECCIÓN: Agregada detección de calificaciones y mejor logging
        """
        try:
            query_lower = query.lower()
            criterios = []

            self.logger.info(f"🔍 Analizando consulta actual: '{query}'")

            # TURNO
            if 'vespertino' in query_lower:
                criterio = {
                    "tabla": "datos_escolares",
                    "campo": "turno",
                    "operador": "=",
                    "valor": "VESPERTINO"
                }
                criterios.append(criterio)
                self.logger.info(f"   ✅ Detectado criterio turno: {criterio}")
            elif 'matutino' in query_lower:
                criterio = {
                    "tabla": "datos_escolares",
                    "campo": "turno",
                    "operador": "=",
                    "valor": "MATUTINO"
                }
                criterios.append(criterio)
                self.logger.info(f"   ✅ Detectado criterio turno: {criterio}")

            # GRADO (CORREGIDO - AGREGADOS PATRONES EN ESPAÑOL)
            grado_patterns = {
                '1': ['primer', 'primero', '1er', '1°', 'grado 1', 'primer grado', 'primero grado'],
                '2': ['segundo', '2do', '2°', 'grado 2', 'segundo grado'],
                '3': ['tercer', 'tercero', '3er', '3°', 'grado 3', 'tercer grado', 'tercero grado'],
                '4': ['cuarto', '4to', '4°', 'grado 4', 'cuarto grado'],
                '5': ['quinto', '5to', '5°', 'grado 5', 'quinto grado'],
                '6': ['sexto', '6to', '6°', 'grado 6', 'sexto grado']
            }

            for grado_num, patterns in grado_patterns.items():
                if any(pattern in query_lower for pattern in patterns):
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "grado",
                        "operador": "=",
                        "valor": grado_num
                    }
                    criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio grado: {criterio} (patrón: {[p for p in patterns if p in query_lower]})")
                    break

            # GRUPO
            for grupo in ['A', 'B', 'C']:
                if (f'grupo {grupo.lower()}' in query_lower or f'grupo {grupo}' in query_lower or
                    f' {grupo.lower()} ' in query_lower):
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "grupo",
                        "operador": "=",
                        "valor": grupo
                    }
                    criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio grupo: {criterio}")
                    break

            # SIN CALIFICACIONES (PRIORIDAD ALTA - DETECTAR PRIMERO)
            sin_calificaciones_patterns = [
                'sin calificaciones', 'no tengan calificaciones', 'sin calificacion',
                'que no tienen calificaciones', 'no tienen calificaciones'
            ]

            if any(pattern in query_lower for pattern in sin_calificaciones_patterns):
                criterio = {
                    "tabla": "datos_escolares",
                    "campo": "calificaciones",
                    "operador": "=",
                    "valor": "[]"
                }
                criterios.append(criterio)
                self.logger.info(f"   ✅ Detectado criterio SIN calificaciones: {criterio}")
            else:
                # CALIFICACIONES (SOLO SI NO SE DETECTÓ "SIN CALIFICACIONES")
                calificaciones_patterns = [
                    'con calificaciones', 'tengan calificaciones',
                    'que tengan calificaciones', 'solo los que tengan calificaciones',
                    'con calificacion', 'que tienen calificaciones'
                ]

                if any(pattern in query_lower for pattern in calificaciones_patterns):
                    criterio = {
                        "tabla": "datos_escolares",
                        "campo": "calificaciones",
                        "operador": "!=",
                        "valor": "[]"
                    }
                    criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio CON calificaciones: {criterio}")

            # PROMEDIO (CORREGIDO - NO AGREGAR A BUSCAR_UNIVERSAL)
            if 'promedio' in query_lower:
                # Los criterios de promedio se manejan en filtros dinámicos, no en SQL
                self.logger.info(f"   🧠 Criterio de promedio detectado - se manejará en filtros dinámicos LLM")
                # NO agregar a criterios SQL porque 'promedio_general' no existe en la base de datos

            # NOMBRE (búsquedas por nombre)
            nombres_comunes = ['garcia', 'martinez', 'lopez', 'hernandez', 'franco', 'natalia', 'mario', 'alexander']
            for name in nombres_comunes:
                if name in query_lower:
                    criterio = {
                        "tabla": "alumnos",
                        "campo": "nombre",
                        "operador": "LIKE",
                        "valor": name.upper()
                    }
                    criterios.append(criterio)
                    self.logger.info(f"   ✅ Detectado criterio nombre: {criterio}")
                    break

            self.logger.info(f"🧠 Total criterios extraídos de la consulta: {len(criterios)}")
            for i, criterio in enumerate(criterios):
                self.logger.info(f"   {i+1}. {criterio}")

            return criterios

        except Exception as e:
            self.logger.error(f"Error extrayendo criterios de la consulta: {e}")
            return []

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
        """Ejecuta conteo de alumnos"""

        criterio_campo = params.get("criterio_campo")
        criterio_valor = params.get("criterio_valor")
        agrupar_por = params.get("agrupar_por")

        if agrupar_por:
            # Conteo agrupado
            sql = f"""
            SELECT de.{agrupar_por}, COUNT(*) as total
            FROM alumnos a
            JOIN datos_escolares de ON a.id = de.alumno_id
            """
            if criterio_campo and criterio_valor:
                # 🔧 MANEJAR VALORES ESPECIALES PARA CALIFICACIONES (AGRUPADO)
                if criterio_campo.lower() == "calificaciones":
                    if criterio_valor.upper() == "NOT NULL":
                        sql += f" WHERE de.{criterio_campo} IS NOT NULL AND de.{criterio_campo} != '' AND de.{criterio_campo} != '[]'"
                    elif criterio_valor.upper() == "NULL":
                        sql += f" WHERE (de.{criterio_campo} IS NULL OR de.{criterio_campo} = '' OR de.{criterio_campo} = '[]')"
                    else:
                        sql += f" WHERE de.{criterio_campo} = '{criterio_valor.upper()}'"
                else:
                    sql += f" WHERE de.{criterio_campo} = '{criterio_valor.upper()}'"
            sql += f" GROUP BY de.{agrupar_por} ORDER BY de.{agrupar_por}"
        else:
            # Conteo simple
            sql = "SELECT COUNT(*) as total FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id"
            if criterio_campo and criterio_valor:
                # 🔧 MANEJAR VALORES ESPECIALES PARA CALIFICACIONES
                if criterio_campo.lower() == "calificaciones":
                    if criterio_valor.upper() == "NOT NULL":
                        sql += f" WHERE de.{criterio_campo} IS NOT NULL AND de.{criterio_campo} != '' AND de.{criterio_campo} != '[]'"
                    elif criterio_valor.upper() == "NULL":
                        sql += f" WHERE (de.{criterio_campo} IS NULL OR de.{criterio_campo} = '' OR de.{criterio_campo} = '[]')"
                    else:
                        sql += f" WHERE de.{criterio_campo} = '{criterio_valor.upper()}'"
                else:
                    # Para otros campos, usar comparación normal
                    sql += f" WHERE de.{criterio_campo} = '{criterio_valor.upper()}'"

        result = self.sql_executor.execute_query(sql)

        if result.success:
            return {
                "success": True,
                "data": result.data,
                "row_count": result.row_count,
                "action_used": "CONTAR_ALUMNOS",
                "message": f"Conteo completado: {result.row_count} resultado(s)",
                "sql_executed": result.query_executed
            }
        else:
            return self._error_result(f"Error en conteo: {result.message}")

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
        incluir_calificaciones = params.get("incluir_calificaciones", False)

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

                result = self.sql_executor.execute_query(sql)
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
                return {
                    "success": True,
                    "data": [result.parameters],  # Lista para compatibilidad
                    "row_count": 1,
                    "action_used": "GENERAR_CONSTANCIA_COMPLETA",
                    "message": f"Constancia de {tipo_constancia} generada para {alumno_dict.get('nombre', 'N/A')}",
                    "sql_executed": f"Generación completa de constancia",
                    "constancia_result": result  # Resultado completo para procesamiento posterior
                }
            else:
                return self._error_result(f"Error generando constancia: {result.parameters.get('message', 'Error desconocido') if result else 'No se pudo procesar'}")

        except Exception as e:
            self.logger.error(f"Error generando constancia completa: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_combined_actions(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta acciones combinadas"""
        # TODO: Implementar combinación de acciones
        return self._error_result("Acciones combinadas no implementadas aún")

    def _execute_sequential_actions(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta acciones secuenciales"""
        # TODO: Implementar acciones secuenciales
        return self._error_result("Acciones secuenciales no implementadas aún")

    def _execute_filtrar_por_calificaciones(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta filtrado por calificaciones"""

        tiene_calificaciones = params.get("tiene_calificaciones", "true")
        incluir_conteo = params.get("incluir_conteo", "false")
        mostrar_detalles = params.get("mostrar_detalles", "true")

        # Convertir strings a boolean
        tiene_cal_bool = str(tiene_calificaciones).lower() in ['true', '1', 'yes', 'sí']
        incluir_conteo_bool = str(incluir_conteo).lower() in ['true', '1', 'yes', 'sí']
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

            result = self.sql_executor.execute_query(sql)

            if result.success:
                return {
                    "success": True,
                    "data": result.data,
                    "row_count": result.row_count,
                    "action_used": "FILTRAR_POR_CALIFICACIONES",
                    "message": f"{mensaje}: {result.row_count} resultado(s)",
                    "sql_executed": result.query_executed,
                    "filtro_aplicado": "con_calificaciones" if tiene_cal_bool else "sin_calificaciones"
                }
            else:
                return self._error_result(f"Error filtrando por calificaciones: {result.message}")

        except Exception as e:
            self.logger.error(f"Error en _execute_filtrar_por_calificaciones: {e}")
            return self._error_result(f"Error interno: {str(e)}")

    def _execute_sequential_actions(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔄 EJECUTA ACCIONES SECUENCIALES
        El resultado de una acción alimenta la siguiente
        """
        try:
            # Por ahora, simplificar a estrategia simple
            # TODO: Implementar lógica secuencial completa en el futuro
            self.logger.warning("⚠️ Estrategia secuencial simplificada a 'simple'")

            # Cambiar estrategia a simple y ejecutar
            action_request_simple = action_request.copy()
            action_request_simple["estrategia"] = "simple"

            return self._execute_single_action(action_request_simple)

        except Exception as e:
            self.logger.error(f"Error en acciones secuenciales: {e}")
            return self._error_result(f"Error en estrategia secuencial: {str(e)}")

    def _execute_combined_actions(self, action_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔄 EJECUTA ACCIONES COMBINADAS
        Múltiples acciones trabajando juntas
        """
        try:
            # Por ahora, simplificar a estrategia simple
            # TODO: Implementar lógica combinada completa en el futuro
            self.logger.warning("⚠️ Estrategia combinada simplificada a 'simple'")

            # Cambiar estrategia a simple y ejecutar
            action_request_simple = action_request.copy()
            action_request_simple["estrategia"] = "simple"

            return self._execute_single_action(action_request_simple)

        except Exception as e:
            self.logger.error(f"Error en acciones combinadas: {e}")
            return self._error_result(f"Error en estrategia combinada: {str(e)}")

    def _error_result(self, message: str) -> Dict[str, Any]:
        """Genera resultado de error estándar"""
        return {
            "success": False,
            "data": [],
            "row_count": 0,
            "action_used": "ERROR",
            "message": message
        }
