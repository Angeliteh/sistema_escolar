"""
🎯 GESTOR CENTRALIZADO DE PRESENTACIÓN DE DATOS
Maneja TODA la lógica de formateo y presentación de datos estructurados
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.core.logging import get_logger
from app.ui.ai_chat.response_formatter import ResponseFormatter


class DataDisplayManager:
    """
    🎯 GESTOR CENTRALIZADO para presentación de datos estructurados

    RESPONSABILIDADES:
    - Detectar tipo de datos automáticamente
    - Aplicar formateo apropiado
    - Mantener consistencia visual
    - Centralizar toda la lógica de presentación
    """

    def __init__(self, chat_list, response_formatter: ResponseFormatter):
        self.chat_list = chat_list
        self.response_formatter = response_formatter
        self.logger = get_logger(__name__)

    def display_data(self, data: Dict[str, Any], context: Optional[str] = None) -> bool:
        """
        🎯 PUNTO DE ENTRADA ÚNICO para mostrar cualquier tipo de datos

        Args:
            data: Datos a mostrar
            context: Contexto adicional para mejorar presentación

        Returns:
            bool: True si se mostró correctamente
        """
        try:
            # 🔧 ANÁLISIS DE DATOS RECIBIDOS
            from app.core.logging import debug_detailed
            debug_detailed(self.logger, f"🔧 [DATA] Analizando datos recibidos:")
            debug_detailed(self.logger, f"   ├── Campos: {len(data.keys())} disponibles")

            if "data" in data:
                data_content = data["data"]
                if isinstance(data_content, list):
                    debug_detailed(self.logger, f"   ├── Registros: {len(data_content)} elementos")
                    if len(data_content) > 0 and isinstance(data_content[0], dict):
                        debug_detailed(self.logger, f"   └── Estructura: {len(data_content[0].keys())} campos por registro")
                    else:
                        debug_detailed(self.logger, f"   └── Estructura: Datos simples ({type(data_content[0]).__name__})")

            # 1. DETECTAR TIPO DE DATOS
            data_type = self._detect_data_type(data)
            debug_detailed(self.logger, f"🔧 [DATA] Tipo detectado: {data_type} → Aplicando formato específico")

            # 2. DELEGAR A MÉTODO ESPECÍFICO
            if data_type == "student_list":
                return self._display_student_list(data.get("alumnos", []), data)
            elif data_type == "single_student":
                # 🔧 CORREGIDO: Para single_student, el alumno puede estar en "alumno" o en "data[0]"
                alumno = data.get("alumno", {})
                # Si no hay "alumno", intentar obtener de "data[0]"
                if not alumno and "data" in data:
                    data_content = data["data"]
                    if isinstance(data_content, list) and len(data_content) > 0:
                        if isinstance(data_content[0], dict):
                            alumno = data_content[0]
                return self._display_single_student(alumno, data)
            elif data_type == "distribution":
                return self._display_distribution(data, context)
            elif data_type == "count_result":
                return self._display_count_result(data, context)
            elif data_type == "statistics":
                return self._display_statistics(data, context)
            elif data_type == "constancia_info":
                return self._display_constancia_info(data, context)
            elif data_type == "error_info":
                return self._display_error_info(data, context)
            else:
                return self._display_generic_data(data, context)

        except Exception as e:
            self.logger.error(f"Error mostrando datos: {e}")
            self._display_error_fallback(str(e))
            return False

    def _detect_data_type(self, data: Dict[str, Any]) -> str:
        """🔍 DETECTA EL TIPO DE DATOS AUTOMÁTICAMENTE"""

        # 🎯 PRIORIDAD 1: Detectar si "data" contiene lista de alumnos (caso más común)
        if "data" in data:
            data_content = data["data"]
            if isinstance(data_content, list) and len(data_content) > 0:
                if self._is_student_data(data_content):
                    # Si es solo 1 alumno, tratarlo como alumno individual
                    if len(data_content) == 1:
                        return "single_student"
                    else:
                        return "student_list"

        # 🎯 PRIORIDAD 2: Detectar lista de alumnos en clave "alumnos"
        if "alumnos" in data:
            alumnos = data["alumnos"]
            if isinstance(alumnos, list) and len(alumnos) > 0:
                if self._is_student_data(alumnos):
                    self.logger.debug(f"🔍 Detectado: student_list ({len(alumnos)} elementos en alumnos)")
                    return "student_list"

        # 🎯 PRIORIDAD 3: Detectar alumno individual en clave "alumno"
        if "alumno" in data:
            alumno = data["alumno"]
            if isinstance(alumno, dict) and self._is_single_student(alumno):
                self.logger.debug(f"🔍 Detectado: single_student (en clave alumno)")
                return "single_student"

        # 🎯 PRIORIDAD 4: Detectar distribuciones (COMPLETAMENTE GENÉRICO)
        if "data" in data:
            data_content = data["data"]
            if isinstance(data_content, list) and len(data_content) > 1:
                # 🎯 DETECTAR DISTRIBUCIONES AUTOMÁTICAMENTE
                if all(isinstance(item, dict) for item in data_content):
                    first_item = data_content[0]

                    # Una distribución tiene 'cantidad' + otro campo de agrupación
                    if 'cantidad' in first_item and len(first_item.keys()) >= 2:
                        # Encontrar el campo de agrupación (cualquier campo que no sea cantidad/porcentaje/total_referencia)
                        grouping_fields = [k for k in first_item.keys() if k not in ['cantidad', 'porcentaje', 'total_referencia']]

                        if len(grouping_fields) >= 1:
                            grouping_field = grouping_fields[0]  # Tomar el primer campo de agrupación
                            self.logger.info(f"🔍 [DATA_DISPLAY] Detectada DISTRIBUCIÓN: {len(data_content)} registros con {grouping_field}/cantidad")
                            return "distribution"

        # 🎯 PRIORIDAD 5: Detectar conteos simples (un solo registro)
        if "data" in data:
            data_content = data["data"]
            if isinstance(data_content, list) and len(data_content) == 1:
                first_item = data_content[0]
                if isinstance(first_item, dict):
                    # Detectar conteos (total_alumnos, count, etc.)
                    if any(key in first_item for key in ["total_alumnos", "count", "total", "cantidad"]):
                        # Detectado silenciosamente: count_result
                        return "count_result"

        # 🎯 PRIORIDAD 4.5: Detectar estadísticas específicas (promedios, etc.)
        if "data" in data:
            data_content = data["data"]
            if isinstance(data_content, list) and len(data_content) == 1:
                first_item = data_content[0]
                if isinstance(first_item, dict):
                    # Detectar promedios y estadísticas específicas
                    if any(key in first_item for key in ["promedio_general", "promedio_edad", "promedio_calificaciones"]):
                        return "statistics"

        # Detectar estadísticas tradicionales
        if any(key in data for key in ["estadisticas", "total_records", "promedio"]):
            self.logger.debug(f"🔍 Detectado: statistics")
            return "statistics"

        # 🎯 PRIORIDAD 5: Detectar información de constancia
        if any(key in data for key in ["constancia_info", "archivo_generado", "ruta_archivo"]):
            self.logger.debug(f"🔍 Detectado: constancia_info")
            return "constancia_info"

        # 🎯 PRIORIDAD 6: Detectar errores
        if any(key in data for key in ["error_details", "error_message"]) or data.get("success") is False:
            self.logger.debug(f"🔍 Detectado: error_info")
            return "error_info"

        # 🎯 FALLBACK: Si no se detecta nada específico
        self.logger.debug(f"🔍 Detectado: generic (claves: {list(data.keys())})")
        return "generic"

    def _is_student_data(self, data: List[Dict]) -> bool:
        """🔍 DETECTA SI ES LISTA DE DATOS DE ALUMNOS"""
        if not data or len(data) == 0:
            return False

        first_item = data[0]

        # 🔧 VALIDACIÓN SILENCIOSA DE ESTRUCTURA DE DATOS
        if not isinstance(first_item, dict):
            return False

        # Campos típicos de alumnos (más flexibles)
        student_fields = ['nombre', 'curp', 'grado', 'grupo', 'turno', 'matricula', 'id']
        matching_fields = sum(1 for field in student_fields if field in first_item)

        is_student = matching_fields >= 2  # Reducido de 3 a 2 para ser más flexible

        return is_student

    def _is_single_student(self, data: Dict) -> bool:
        """🔍 DETECTA SI ES UN ALUMNO INDIVIDUAL"""
        if not isinstance(data, dict):
            return False

        student_fields = ['nombre', 'curp', 'grado', 'grupo', 'turno']
        matching_fields = sum(1 for field in student_fields if field in data)

        return matching_fields >= 3

    def _display_student_list(self, alumnos: List[Dict], full_data: Dict) -> bool:
        """📋 MUESTRA LISTA DE ALUMNOS CON FORMATEO CENTRALIZADO"""
        # Si alumnos está vacío, intentar obtener de "data"
        if not alumnos and "data" in full_data:
            alumnos = full_data["data"]

        if not alumnos:
            self._show_message("No se encontraron alumnos.", "info")
            return False

        # 🚫 ELIMINADO: NO mostrar human_response aquí para evitar duplicación
        # La respuesta del Master ya se muestra en ChatWindow._handle_chat_engine_response()
        # Solo mostrar los datos estructurados aquí

        total_alumnos = len(alumnos)

        # 🆕 EXTRAER CRITERIOS DE BÚSQUEDA PARA CAMPOS DINÁMICOS
        search_criteria = full_data.get("search_criteria", {})
        fields_to_show = search_criteria.get("fields_to_show", ['nombre', 'curp', 'turno'])
        has_specific_criteria = search_criteria.get("has_specific_criteria", False)

        self.logger.info(f"🎯 [DATA_DISPLAY] Criterios de búsqueda detectados:")
        self.logger.info(f"   ├── Campos a mostrar: {fields_to_show}")
        self.logger.info(f"   └── Tiene criterios específicos: {has_specific_criteria}")

        # 🎯 MOSTRAR RESPUESTA HUMANIZADA DEL MASTER PRIMERO (SI EXISTE)
        if "human_response" in full_data and full_data["human_response"]:
            human_response = full_data["human_response"]
            formatted_human_response = self.response_formatter.format_response(human_response, "general")
            self._show_message(formatted_human_response, "formatted")

        # 🎯 DECISIÓN CENTRALIZADA DE FORMATO SEGÚN CANTIDAD (OPTIMIZADA)
        if total_alumnos > 50:
            content = self._format_large_student_list(alumnos, full_data, fields_to_show)
        elif total_alumnos > 25:  # 26-50: Lista mediana con primeros 20
            content = self._format_medium_student_list(alumnos, full_data, fields_to_show)
        else:  # ≤ 25: Lista completa detallada
            content = self._format_small_student_list(alumnos, full_data, fields_to_show)

        self.logger.info(f"🎯 [DATA_DISPLAY] Formato seleccionado para {total_alumnos} alumnos: {'large' if total_alumnos > 50 else 'medium' if total_alumnos > 25 else 'small'}")

        # APLICAR FORMATEO CENTRALIZADO
        formatted_content = self.response_formatter.format_response(content, "data")
        self._show_message(formatted_content, "formatted")

        return True

    def _format_large_student_list(self, alumnos: List[Dict], full_data: Dict, fields_to_show: List[str] = None) -> str:
        """📊 FORMATO PARA LISTAS GRANDES (50+ alumnos)"""
        total = len(alumnos)
        limite = 25

        content = f"""
📊 **RESULTADOS DE BÚSQUEDA**
{'═' * 60}
📈 **Total encontrados:** {total} alumnos
📋 **Mostrando:** Primeros {min(limite, total)} resultados

"""

        # Usar campos por defecto si no se especifican
        if not fields_to_show:
            fields_to_show = ['nombre', 'curp', 'turno']

        for i, alumno in enumerate(alumnos[:limite], 1):
            nombre = alumno.get('nombre', '').upper()
            content += f"**{i:2d}.** {nombre}\n"

            # 🎯 MOSTRAR CAMPOS DINÁMICOS BASADOS EN CRITERIOS DE BÚSQUEDA
            details = []

            # Siempre mostrar grado y grupo si están disponibles
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            if grado and grupo:
                turno = alumno.get('turno', '')[:3] if alumno.get('turno') else ''
                details.append(f"🎓 {grado}° {grupo} - {turno}")

            # Agregar campos específicos según criterios de búsqueda
            for field in fields_to_show:
                if field == 'curp':
                    curp = alumno.get('curp', '')
                    if curp:
                        details.append(f"📋 {curp}")
                elif field == 'fecha_nacimiento':
                    fecha = alumno.get('fecha_nacimiento', '')
                    if fecha:
                        details.append(f"📅 {fecha}")
                elif field == 'matricula':
                    matricula = alumno.get('matricula', '')
                    if matricula:
                        details.append(f"🆔 {matricula}")
                elif field == 'calificaciones_status':
                    # Verificar si tiene calificaciones
                    calificaciones = alumno.get('calificaciones', '')
                    if calificaciones and calificaciones not in ['', '[]']:
                        details.append(f"📊 Con calificaciones")
                    else:
                        details.append(f"📊 Sin calificaciones")

            # Mostrar detalles en una línea
            if details:
                content += f"     {' • '.join(details)}\n\n"
            else:
                content += "\n"

        if total > limite:
            restantes = total - limite
            content += f"""{'─' * 60}
📊 **Y {restantes} alumnos más disponibles...**

🔍 **CONTEXTO COMPLETO MANTENIDO:**
• Todos los {total} alumnos están disponibles para consultas
• "Alumno número [26-{total}]" - Acceder a cualquier posición
• "Mostrar todos" - Ver lista completa (puede ser muy larga)
• "Filtrar por [criterio]" - Refinar búsqueda

**Para ver más resultados:**
• "Mostrar más alumnos" - Ver siguientes {min(25, restantes)}
• "Buscar [nombre específico]" - Encontrar alumno exacto
• "Alumnos de [grado]° [grupo]" - Filtrar por grado/grupo
• "Número [X]" - Ver alumno en posición específica (1-{total})
"""

        return content

    def _format_medium_student_list(self, alumnos: List[Dict], full_data: Dict, fields_to_show: List[str] = None) -> str:
        """📋 FORMATO PARA LISTAS MEDIANAS (26-50 alumnos) - CONTEXTO COMPLETO"""
        total = len(alumnos)
        limite = 20  # Mostrar primeros 20

        content = f"""
🔍 **ALUMNOS ENCONTRADOS**
{'═' * 45}
📊 **Total:** {total} estudiantes (mostrando primeros {limite})

"""

        # Usar campos por defecto si no se especifican
        if not fields_to_show:
            fields_to_show = ['nombre', 'curp', 'turno']

        for i, alumno in enumerate(alumnos[:limite], 1):
            nombre = alumno.get('nombre', '').upper()
            content += f"**{i:2d}.** {nombre}\n"

            # 🎯 MOSTRAR CAMPOS DINÁMICOS BASADOS EN CRITERIOS DE BÚSQUEDA
            details = []

            # Siempre mostrar grado y grupo si están disponibles
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            if grado and grupo:
                turno = alumno.get('turno', '')[:3] if alumno.get('turno') else ''
                details.append(f"🎓 {grado}° {grupo} - {turno}")

            # Agregar campos específicos según criterios de búsqueda
            for field in fields_to_show:
                if field == 'curp':
                    curp = alumno.get('curp', '')
                    if curp:
                        details.append(f"📋 {curp}")
                elif field == 'fecha_nacimiento':
                    fecha = alumno.get('fecha_nacimiento', '')
                    if fecha:
                        details.append(f"📅 {fecha}")
                elif field == 'matricula':
                    matricula = alumno.get('matricula', '')
                    if matricula:
                        details.append(f"🆔 {matricula}")
                elif field == 'calificaciones_status':
                    # Verificar si tiene calificaciones
                    calificaciones = alumno.get('calificaciones', '')
                    if calificaciones and calificaciones not in ['', '[]']:
                        details.append(f"📊 Con calificaciones")
                    else:
                        details.append(f"📊 Sin calificaciones")

            # Mostrar detalles en una línea
            if details:
                content += f"     {' • '.join(details)}\n\n"
            else:
                content += "\n"

        restantes = total - limite
        content += f"""{'─' * 45}
📊 **Y {restantes} alumnos más disponibles...**

🔍 **CONTEXTO COMPLETO MANTENIDO:**
• Todos los {total} alumnos están disponibles para consultas
• "Alumno número [21-{total}]" - Acceder a cualquier posición
• "Mostrar todos" - Ver lista completa
• "Filtrar por [criterio]" - Refinar búsqueda

💡 **Opciones disponibles:**
• "Detalles de [nombre]" - Ver información completa
• "Constancia para [nombre]" - Generar constancia
• "Número [X]" - Seleccionar alumno por posición (1-{total})
"""

        return content

    def _format_small_student_list(self, alumnos: List[Dict], full_data: Dict, fields_to_show: List[str] = None) -> str:
        """👥 FORMATO PARA LISTAS PEQUEÑAS (≤10 alumnos)"""
        total = len(alumnos)
        plural = 's' if total > 1 else ''

        content = f"""
👥 **{total} ALUMNO{plural.upper()} ENCONTRADO{plural.upper()}**
{'═' * 50}

"""

        # Usar campos por defecto si no se especifican
        if not fields_to_show:
            fields_to_show = ['nombre', 'curp', 'turno']

        for i, alumno in enumerate(alumnos, 1):
            nombre = alumno.get('nombre', '').upper()
            content += f"**{i}.** **{nombre}**\n"

            # 🎯 MOSTRAR CAMPOS DINÁMICOS BASADOS EN CRITERIOS DE BÚSQUEDA
            if 'curp' in fields_to_show:
                curp = alumno.get('curp', '')
                content += f"   📋 **CURP:** {curp}\n"

            # Siempre mostrar grado y grupo si están disponibles
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')
            if grado and grupo:
                content += f"   🎓 **Grado:** {grado}° {grupo} - {turno}\n"

            if 'fecha_nacimiento' in fields_to_show:
                fecha = alumno.get('fecha_nacimiento', '')
                if fecha:
                    content += f"   📅 **Nacimiento:** {fecha}\n"

            if 'matricula' in fields_to_show:
                matricula = alumno.get('matricula', '')
                if matricula:
                    content += f"   🆔 **Matrícula:** {matricula}\n"

            if 'calificaciones_status' in fields_to_show:
                calificaciones = alumno.get('calificaciones', '')
                if calificaciones and calificaciones not in ['', '[]']:
                    content += f"   📊 **Estado:** Con calificaciones\n"
                else:
                    content += f"   📊 **Estado:** Sin calificaciones\n"

            content += "\n"

        content += f"""{'─' * 50}
💡 **Acciones rápidas disponibles:**
• "Detalles completos de [nombre]" - Ver toda la información
• "Constancia de estudios para [nombre]" - Generar constancia
• "Calificaciones de [nombre]" - Ver notas del alumno
"""

        return content

    def _display_single_student(self, alumno: Dict, full_data: Dict) -> bool:
        """👤 MUESTRA DETALLES DE UN ALUMNO INDIVIDUAL"""
        # Si alumno está vacío, intentar obtener de "data"
        if not alumno and "data" in full_data:
            data_content = full_data["data"]
            if isinstance(data_content, list) and len(data_content) > 0:
                alumno = data_content[0]  # Tomar el primer (y único) elemento

        if not alumno:
            self._show_message("No se encontraron detalles del alumno.", "error")
            return False

        # 🎯 SIEMPRE MOSTRAR RESPUESTA DEL MASTER PRIMERO (SI EXISTE)
        if "human_response" in full_data and full_data["human_response"]:
            human_response = full_data["human_response"]
            formatted_human_response = self.response_formatter.format_response(human_response, "general")
            self._show_message(formatted_human_response, "formatted")

            # 🎯 PARA CONSULTAS DE CAMPOS ESPECÍFICOS, SOLO MOSTRAR LA RESPUESTA DEL MASTER
            if self._is_specific_field_query(full_data):
                return True  # Solo mostrar la respuesta del Master para campos específicos

        # 🎯 PARA INFORMACIÓN COMPLETA, MOSTRAR TAMBIÉN LOS DATOS TÉCNICOS
        content = self._format_single_student_details(alumno)
        formatted_content = self.response_formatter.format_response(content, "data")
        self._show_message(formatted_content, "formatted")

        return True

    def _is_specific_field_query(self, full_data: Dict) -> bool:
        """
        🔧 DETECTA SI ES UNA CONSULTA DE CAMPO ESPECÍFICO

        Args:
            full_data: Datos completos de la respuesta

        Returns:
            bool: True si es consulta de campo específico
        """
        try:
            # Verificar si hay pocos datos (1-2 registros) con pocos campos
            if "data" in full_data:
                data_content = full_data["data"]
                if isinstance(data_content, list) and len(data_content) <= 2:
                    # Si cada registro tiene pocos campos (≤ 3), probablemente es campo específico
                    if data_content and isinstance(data_content[0], dict):
                        field_count = len(data_content[0].keys())
                        if field_count <= 3:  # id + campo solicitado + tal vez uno más
                            self.logger.info(f"🔧 [DATA_DISPLAY] Consulta de campo específico detectada: {field_count} campos, {len(data_content)} registros")
                            return True

            # Verificar patrones en la respuesta del Master
            if "human_response" in full_data:
                text_lower = full_data["human_response"].lower()
                specific_patterns = [
                    "matrícula de", "curp de", "grado de", "grupo de",
                    "fecha de nacimiento de", "turno de", "la matrícula es",
                    "el curp es", "el grado es", "encontré la matrícula"
                ]
                for pattern in specific_patterns:
                    if pattern in text_lower:
                        self.logger.info(f"🔧 [DATA_DISPLAY] Consulta de campo específico detectada por patrón: '{pattern}'")
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error detectando consulta de campo específico: {e}")
            return False

    def _format_single_student_details(self, alumno: Dict) -> str:
        """👤 FORMATO OPTIMIZADO PARA INFORMACIÓN COMPLETA"""

        # 🎯 DATOS PRINCIPALES
        nombre = alumno.get('nombre', 'No disponible')
        grado = alumno.get('grado', 'N/A')
        grupo = alumno.get('grupo', 'N/A')
        turno = alumno.get('turno', 'No disponible')

        # 🎯 FORMATO MEJORADO CON MEJOR ESPACIADO Y ESTRUCTURA
        content = f"""
═══════════════════════════════════════════
🎓 **{nombre}**
═══════════════════════════════════════════

📚 **INFORMACIÓN ACADÉMICA**
   • Grado: **{grado}°**
   • Grupo: **{grupo}**
   • Turno: **{turno.title()}**
   • Ciclo escolar: **{alumno.get('ciclo_escolar', 'No disponible')}**

📋 **DATOS PERSONALES**
   • CURP: **{alumno.get('curp', 'No disponible')}**
   • Matrícula: **{alumno.get('matricula', 'No disponible')}**
   • Fecha de nacimiento: **{alumno.get('fecha_nacimiento', 'No disponible')}**
   • Fecha de registro: **{alumno.get('fecha_registro', 'No disponible')}**

🏫 **INFORMACIÓN ESCOLAR**
   • Escuela: **{alumno.get('escuela', 'No disponible')}**
   • CCT: **{alumno.get('cct', 'No disponible')}**

═══════════════════════════════════════════"""

        # Agregar calificaciones si existen
        calificaciones_raw = alumno.get('calificaciones', [])
        calificaciones = []

        # 🔧 PROCESAR CALIFICACIONES (pueden estar como JSON string)
        if calificaciones_raw:
            if isinstance(calificaciones_raw, str):
                try:
                    import json
                    calificaciones = json.loads(calificaciones_raw)
                except (json.JSONDecodeError, TypeError):
                    calificaciones = []
            elif isinstance(calificaciones_raw, list):
                calificaciones = calificaciones_raw

        if calificaciones and len(calificaciones) > 0:
            content += "\n\n📊 **CALIFICACIONES**"

            # 🎯 FORMATO MEJORADO CON SEPARADORES VISUALES
            for cal in calificaciones:
                materia = cal.get('nombre', cal.get('materia', 'No especificada'))

                # Formatear calificaciones por periodo si existen
                if cal.get('i') is not None or cal.get('ii') is not None:
                    p1 = self._format_grade(cal.get('i', 0))
                    p2 = self._format_grade(cal.get('ii', 0))
                    p3 = self._format_grade(cal.get('iii', 0))
                    prom = self._format_grade(cal.get('promedio', 0))

                    content += f"\n   📚 **{materia}**"
                    content += f"\n      • Periodo 1: **{p1}**  |  Periodo 2: **{p2}**  |  Periodo 3: **{p3}**"
                    content += f"\n      • Promedio: **{prom}**"
                else:
                    calificacion = cal.get('promedio', cal.get('calificacion', 'N/A'))
                    if isinstance(calificacion, (int, float)):
                        calificacion = self._format_grade(calificacion)
                    content += f"\n   📚 **{materia}**: **{calificacion}**"

            # 🎯 RESUMEN FINAL CON SEPARACIÓN MEJORADA
            total_materias = len(calificaciones)
            promedio_general = sum(cal.get('promedio', 0) for cal in calificaciones if cal.get('promedio', 0) > 0) / total_materias if total_materias > 0 else 0

            content += f"\n\n═══════════════════════════════════════════"
            content += f"\n📈 **RESUMEN ACADÉMICO**"
            content += f"\n   • Promedio general: **{self._format_grade(promedio_general)}**"
            content += f"\n   • Total de materias: **{total_materias}**"
            content += f"\n═══════════════════════════════════════════"
        else:
            content += "\n\n📊 **CALIFICACIONES**"
            content += "\n   • Estado: **Sin registros disponibles**"
            content += "\n\n═══════════════════════════════════════════"

        # 🧹 LIMPIAR ESPACIOS EN BLANCO AL INICIO Y FINAL
        return content.strip()

    def _format_grade(self, grade) -> str:
        """📊 FORMATEA CALIFICACIONES CONSISTENTEMENTE"""
        if isinstance(grade, (int, float)) and grade > 0:
            return f"{grade:.1f}" if grade % 1 != 0 else str(int(grade))
        return '-'

    def _display_distribution(self, data: Dict, context: Optional[str]) -> bool:
        """📊 MUESTRA DISTRIBUCIONES (ej: por grado, turno, grupo)"""
        try:
            # 🎯 MOSTRAR RESPUESTA HUMANIZADA PRIMERO
            if "human_response" in data and data["human_response"]:
                human_response = data["human_response"]
                formatted_content = self.response_formatter.format_response(human_response, "data")
                self._show_message(formatted_content, "formatted")

            # 🎯 MOSTRAR TABLA DETALLADA DE LA DISTRIBUCIÓN
            data_content = data.get("data", [])
            if isinstance(data_content, list) and len(data_content) > 0:
                distribution_table = self._format_distribution_table(data_content)
                formatted_table = self.response_formatter.format_response(distribution_table, "data")
                self._show_message(formatted_table, "formatted")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error mostrando distribución: {e}")
            return False

    def _format_distribution_table(self, distribution_data: List[Dict]) -> str:
        """📊 FORMATEA TABLA DE DISTRIBUCIÓN"""
        try:
            # Detectar tipo de distribución basado en las claves
            first_item = distribution_data[0]

            if 'grado' in first_item:
                return self._format_grade_distribution(distribution_data)
            elif 'turno' in first_item:
                return self._format_turno_distribution(distribution_data)
            elif 'grupo' in first_item:
                return self._format_grupo_distribution(distribution_data)
            else:
                return self._format_generic_distribution(distribution_data)

        except Exception as e:
            self.logger.error(f"Error formateando tabla de distribución: {e}")
            return "Error formateando distribución"

    def _format_grade_distribution(self, data: List[Dict]) -> str:
        """📊 FORMATEA DISTRIBUCIÓN POR GRADOS"""
        content = """
📊 **DISTRIBUCIÓN DETALLADA POR GRADOS**
═══════════════════════════════════════════

"""
        total_alumnos = 0

        for item in data:
            grado = item.get('grado', 'N/A')
            cantidad = item.get('cantidad', 0)
            porcentaje = item.get('porcentaje', 0)
            total_alumnos += cantidad

            # Crear barra visual del porcentaje
            bar_length = int(porcentaje / 5)  # Cada 5% = 1 carácter
            bar = "█" * bar_length + "░" * (20 - bar_length)

            content += f"**{grado}° GRADO**\n"
            content += f"   👥 Alumnos: **{cantidad}**\n"
            content += f"   📊 Porcentaje: **{porcentaje:.1f}%**\n"
            content += f"   📈 {bar} {porcentaje:.1f}%\n\n"

        content += f"""═══════════════════════════════════════════
📈 **RESUMEN TOTAL**
   👥 **{total_alumnos} estudiantes** distribuidos en **{len(data)} grados**
   📊 Promedio por grado: **{total_alumnos/len(data):.1f} alumnos**

💡 **Análisis rápido:**
• Grado con más alumnos: **{max(data, key=lambda x: x.get('cantidad', 0)).get('grado', 'N/A')}°** ({max(item.get('cantidad', 0) for item in data)} estudiantes)
• Grado con menos alumnos: **{min(data, key=lambda x: x.get('cantidad', 0)).get('grado', 'N/A')}°** ({min(item.get('cantidad', 0) for item in data)} estudiantes)
"""
        return content

    def _format_turno_distribution(self, data: List[Dict]) -> str:
        """🕐 FORMATEA DISTRIBUCIÓN POR TURNOS"""
        content = """
🕐 **DISTRIBUCIÓN POR TURNOS**
═══════════════════════════════════

"""
        for item in data:
            turno = item.get('turno', 'N/A')
            cantidad = item.get('cantidad', 0)
            porcentaje = item.get('porcentaje', 0)

            content += f"**{turno.upper()}**\n"
            content += f"   👥 {cantidad} alumnos ({porcentaje:.1f}%)\n\n"

        return content

    def _format_grupo_distribution(self, data: List[Dict]) -> str:
        """📚 FORMATEA DISTRIBUCIÓN POR GRUPOS"""
        content = """
📚 **DISTRIBUCIÓN POR GRUPOS**
═══════════════════════════════════

"""
        for item in data:
            grupo = item.get('grupo', 'N/A')
            cantidad = item.get('cantidad', 0)
            porcentaje = item.get('porcentaje', 0)

            content += f"**GRUPO {grupo}**\n"
            content += f"   👥 {cantidad} alumnos ({porcentaje:.1f}%)\n\n"

        return content

    def _format_generic_distribution(self, data: List[Dict]) -> str:
        """📊 FORMATEA DISTRIBUCIÓN GENÉRICA"""
        content = """
📊 **DISTRIBUCIÓN DE DATOS**
═══════════════════════════════════

"""
        for item in data:
            # Obtener la primera clave que no sea 'cantidad' o 'porcentaje'
            key = next((k for k in item.keys() if k not in ['cantidad', 'porcentaje', 'total_referencia']), 'item')
            value = item.get(key, 'N/A')
            cantidad = item.get('cantidad', 0)
            porcentaje = item.get('porcentaje', 0)

            content += f"**{value}**\n"
            content += f"   👥 {cantidad} elementos ({porcentaje:.1f}%)\n\n"

        return content

    def _display_count_result(self, data: Dict, context: Optional[str]) -> bool:
        """📊 MUESTRA RESULTADOS DE CONTEO DE MANERA AMIGABLE"""
        # 🎯 USAR RESPUESTA HUMANIZADA DIRECTAMENTE
        if "human_response" in data and data["human_response"]:
            human_response = data["human_response"]
            formatted_content = self.response_formatter.format_response(human_response, "data")
            self._show_message(formatted_content, "formatted")
            return True

        # 🎯 SI NO HAY RESPUESTA HUMANIZADA, ERROR
        self._show_message("❌ Error: No hay respuesta humanizada para mostrar.", "error")
        return False

    def _display_statistics(self, data: Dict, context: Optional[str]) -> bool:
        """📊 MUESTRA ESTADÍSTICAS"""
        # 🎯 USAR RESPUESTA HUMANIZADA DIRECTAMENTE
        if "human_response" in data and data["human_response"]:
            human_response = data["human_response"]
            formatted_content = self.response_formatter.format_response(human_response, "statistics")
            self._show_message(formatted_content, "formatted")
            return True
        return False

    def _display_constancia_info(self, data: Dict, context: Optional[str]) -> bool:
        """📄 MUESTRA INFORMACIÓN DE CONSTANCIA"""
        # 🎯 USAR RESPUESTA HUMANIZADA DIRECTAMENTE
        if "human_response" in data and data["human_response"]:
            human_response = data["human_response"]
            formatted_content = self.response_formatter.format_response(human_response, "success")
            self._show_message(formatted_content, "formatted")
            return True
        return False

    def _display_error_info(self, data: Dict, context: Optional[str]) -> bool:
        """❌ MUESTRA INFORMACIÓN DE ERROR"""
        # 🎯 USAR RESPUESTA HUMANIZADA DIRECTAMENTE
        if "human_response" in data and data["human_response"]:
            human_response = data["human_response"]
            formatted_content = self.response_formatter.format_response(human_response, "error")
            self._show_message(formatted_content, "formatted")
            return True
        return False

    def _display_generic_data(self, data: Dict, context: Optional[str]) -> bool:
        """📋 MUESTRA DATOS GENÉRICOS"""
        # 🎯 USAR RESPUESTA HUMANIZADA DIRECTAMENTE
        if "human_response" in data and data["human_response"]:
            human_response = data["human_response"]
            formatted_content = self.response_formatter.format_response(human_response, "general")
            self._show_message(formatted_content, "formatted")
            return True
        return False

    def _display_error_fallback(self, error_msg: str):
        """❌ FALLBACK PARA ERRORES"""
        self._show_message(f"❌ Error mostrando datos: {error_msg}", "error")

    def _show_message(self, content: str, msg_type: str):
        """📤 MUESTRA MENSAJE EN EL CHAT"""
        current_time = datetime.now().strftime("%H:%M:%S")

        if msg_type == "formatted":
            # Ya está formateado, mostrar directamente
            self.chat_list.add_assistant_message(content, current_time)
        else:
            # Aplicar formateo según tipo
            formatted_content = self.response_formatter.format_response(content, msg_type)
            self.chat_list.add_assistant_message(formatted_content, current_time)
