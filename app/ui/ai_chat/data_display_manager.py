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
            # 🔍 DEBUG: Mostrar estructura de datos recibidos
            self.logger.info(f"🔍 DEBUG - Datos recibidos: {list(data.keys())}")
            if "data" in data:
                data_content = data["data"]
                if isinstance(data_content, list):
                    self.logger.info(f"🔍 DEBUG - data es lista con {len(data_content)} elementos")
                    if len(data_content) > 0:
                        # 🔧 CORREGIDO: Verificar que el primer elemento sea un diccionario
                        if isinstance(data_content[0], dict):
                            self.logger.info(f"🔍 DEBUG - Primer elemento: {list(data_content[0].keys())}")
                        else:
                            self.logger.info(f"🔍 DEBUG - Primer elemento: {type(data_content[0])} - {data_content[0]}")

            # 1. DETECTAR TIPO DE DATOS
            data_type = self._detect_data_type(data)
            self.logger.info(f"🔍 Tipo de datos detectado: {data_type}")

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
                        self.logger.info(f"🔍 Detectado: single_student (1 elemento en data)")
                        return "single_student"
                    else:
                        self.logger.info(f"🔍 Detectado: student_list ({len(data_content)} elementos en data)")
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

        # 🎯 PRIORIDAD 4: Detectar conteos y estadísticas
        if "data" in data:
            data_content = data["data"]
            if isinstance(data_content, list) and len(data_content) == 1:
                first_item = data_content[0]
                if isinstance(first_item, dict):
                    # Detectar conteos (total_alumnos, count, etc.)
                    if any(key in first_item for key in ["total_alumnos", "count", "total", "cantidad"]):
                        self.logger.info(f"🔍 Detectado: count_result (conteo)")
                        return "count_result"

        # 🎯 PRIORIDAD 4.5: Detectar estadísticas específicas (promedios, etc.)
        if "data" in data:
            data_content = data["data"]
            if isinstance(data_content, list) and len(data_content) == 1:
                first_item = data_content[0]
                if isinstance(first_item, dict):
                    # Detectar promedios y estadísticas específicas
                    if any(key in first_item for key in ["promedio_general", "promedio_edad", "promedio_calificaciones"]):
                        self.logger.info(f"🔍 Detectado: statistics (promedio)")
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

        # 🔍 DEBUG CRÍTICO: Verificar exactamente qué tipo de dato recibimos
        self.logger.info(f"🔍 DEBUG - _is_student_data recibió:")
        self.logger.info(f"🔍 DEBUG - data type: {type(data)}")
        self.logger.info(f"🔍 DEBUG - data length: {len(data)}")
        self.logger.info(f"🔍 DEBUG - first_item type: {type(first_item)}")
        self.logger.info(f"🔍 DEBUG - first_item content: {first_item}")

        if not isinstance(first_item, dict):
            self.logger.info(f"🔍 DEBUG - ❌ first_item NO es dict, es {type(first_item)}")
            return False

        # Campos típicos de alumnos (más flexibles)
        student_fields = ['nombre', 'curp', 'grado', 'grupo', 'turno', 'matricula', 'id']
        matching_fields = sum(1 for field in student_fields if field in first_item)

        # 🔍 DEBUG: Mostrar qué campos coinciden
        matching_field_names = [field for field in student_fields if field in first_item]
        self.logger.info(f"🔍 DEBUG - Campos que coinciden: {matching_field_names} ({matching_fields}/{len(student_fields)})")

        is_student = matching_fields >= 2  # Reducido de 3 a 2 para ser más flexible
        self.logger.info(f"🔍 DEBUG - ¿Es datos de alumno? {is_student}")

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

        # 🎯 MOSTRAR RESPUESTA CONVERSACIONAL PRIMERO (SI EXISTE)
        if "human_response" in full_data and full_data["human_response"]:
            human_response = full_data["human_response"]
            formatted_human_response = self.response_formatter.format_response(human_response, "general")
            self._show_message(formatted_human_response, "formatted")

        total_alumnos = len(alumnos)

        # DECISIÓN CENTRALIZADA DE FORMATO SEGÚN CANTIDAD
        if total_alumnos > 50:
            content = self._format_large_student_list(alumnos, full_data)
        elif total_alumnos >= 10:  # ✅ CAMBIO: >= 10 para incluir exactamente 10
            content = self._format_medium_student_list(alumnos, full_data)
        else:
            content = self._format_small_student_list(alumnos, full_data)

        # APLICAR FORMATEO CENTRALIZADO
        formatted_content = self.response_formatter.format_response(content, "data")
        self._show_message(formatted_content, "formatted")

        return True

    def _format_large_student_list(self, alumnos: List[Dict], full_data: Dict) -> str:
        """📊 FORMATO PARA LISTAS GRANDES (50+ alumnos)"""
        total = len(alumnos)
        limite = 25

        content = f"""
📊 **RESULTADOS DE BÚSQUEDA**
{'═' * 60}
📈 **Total encontrados:** {total} alumnos
📋 **Mostrando:** Primeros {min(limite, total)} resultados

"""

        for i, alumno in enumerate(alumnos[:limite], 1):
            nombre = alumno.get('nombre', '').upper()
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')[:3] if alumno.get('turno') else ''
            curp = alumno.get('curp', '')

            content += f"**{i:2d}.** {nombre}\n"
            content += f"     🎓 {grado}° {grupo} - {turno}  •  📋 {curp}\n\n"

        if total > limite:
            restantes = total - limite
            content += f"""{'─' * 60}
💡 **Hay {restantes} alumnos más disponibles**

**Para ver más resultados:**
• "Mostrar más alumnos" - Ver siguientes {min(25, restantes)}
• "Buscar [nombre específico]" - Encontrar alumno exacto
• "Alumnos de [grado]° [grupo]" - Filtrar por grado/grupo
"""

        return content

    def _format_medium_student_list(self, alumnos: List[Dict], full_data: Dict) -> str:
        """📋 FORMATO PARA LISTAS MEDIANAS (10-50 alumnos)"""
        total = len(alumnos)

        content = f"""
🔍 **ALUMNOS ENCONTRADOS**
{'═' * 45}
📊 **Total:** {total} estudiantes

"""

        for i, alumno in enumerate(alumnos, 1):
            nombre = alumno.get('nombre', '').upper()
            curp = alumno.get('curp', '')
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')[:3] if alumno.get('turno') else ''

            content += f"**{i:2d}.** {nombre}\n"
            content += f"     🎓 {grado}° {grupo} - {turno}  •  📋 {curp}\n\n"

        content += f"""{'─' * 45}
💡 **Opciones disponibles:**
• "Detalles de [nombre]" - Ver información completa
• "Constancia para [nombre]" - Generar constancia
• "Número [X]" - Seleccionar alumno por posición
"""

        return content

    def _format_small_student_list(self, alumnos: List[Dict], full_data: Dict) -> str:
        """👥 FORMATO PARA LISTAS PEQUEÑAS (≤10 alumnos)"""
        total = len(alumnos)
        plural = 's' if total > 1 else ''

        content = f"""
👥 **{total} ALUMNO{plural.upper()} ENCONTRADO{plural.upper()}**
{'═' * 50}

"""

        for i, alumno in enumerate(alumnos, 1):
            nombre = alumno.get('nombre', '').upper()
            curp = alumno.get('curp', '')
            grado = alumno.get('grado', '')
            grupo = alumno.get('grupo', '')
            turno = alumno.get('turno', '')
            matricula = alumno.get('matricula', '')

            content += f"**{i}.** **{nombre}**\n"
            content += f"   📋 **CURP:** {curp}\n"
            content += f"   🎓 **Grado:** {grado}° {grupo} - {turno}\n"
            content += f"   🆔 **Matrícula:** {matricula}\n\n"

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

        content = self._format_single_student_details(alumno)
        formatted_content = self.response_formatter.format_response(content, "data")
        self._show_message(formatted_content, "formatted")

        return True

    def _format_single_student_details(self, alumno: Dict) -> str:
        """👤 FORMATO ULTRA LIMPIO Y LEGIBLE"""

        # 🎯 DATOS PRINCIPALES
        nombre = alumno.get('nombre', 'No disponible')
        grado = alumno.get('grado', 'N/A')
        grupo = alumno.get('grupo', 'N/A')
        turno = alumno.get('turno', 'No disponible')

        # 🎯 CONSTRUIR CONTENIDO SIN ESPACIOS AL INICIO
        content = f"🎓 {nombre}"
        content += f"\n\n📚 {grado}° grado, grupo {grupo}"
        content += f"\n🕐 Turno {turno.lower()}"
        content += f"\n\n─────────────────────────────────"
        content += f"\n📋 Datos personales:"
        content += f"\nCURP: {alumno.get('curp', 'No disponible')}"
        content += f"\nMatrícula: {alumno.get('matricula', 'No disponible')}"
        content += f"\nNacimiento: {alumno.get('fecha_nacimiento', 'No disponible')}"
        content += f"\nEscuela: {alumno.get('escuela', 'No disponible')}"
        content += f"\n\n─────────────────────────────────"

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
            content += "\n📊 Calificaciones:"

            # 🎯 FORMATO CON SEPARADORES VISUALES
            for cal in calificaciones:
                materia = cal.get('nombre', cal.get('materia', 'No especificada'))

                # Formatear calificaciones por periodo si existen
                if cal.get('i') is not None or cal.get('ii') is not None:
                    p1 = self._format_grade(cal.get('i', 0))
                    p2 = self._format_grade(cal.get('ii', 0))
                    p3 = self._format_grade(cal.get('iii', 0))
                    prom = self._format_grade(cal.get('promedio', 0))

                    content += f"\n• {materia}\n"
                    content += f"  Periodo 1: {p1}  |  Periodo 2: {p2}  |  Periodo 3: {p3}\n"
                    content += f"  Promedio: {prom}\n"
                else:
                    calificacion = cal.get('promedio', cal.get('calificacion', 'N/A'))
                    if isinstance(calificacion, (int, float)):
                        calificacion = self._format_grade(calificacion)
                    content += f"\n• {materia}: {calificacion}\n"

            # 🎯 RESUMEN FINAL CON SEPARACIÓN
            total_materias = len(calificaciones)
            promedio_general = sum(cal.get('promedio', 0) for cal in calificaciones if cal.get('promedio', 0) > 0) / total_materias if total_materias > 0 else 0

            content += f"\n─────────────────────────────────\n"
            content += f"📈 Promedio general: {self._format_grade(promedio_general)} ({total_materias} materias)"
        else:
            content += "\n📊 Calificaciones: Sin registros"

        # 🧹 LIMPIAR ESPACIOS EN BLANCO AL INICIO Y FINAL
        return content.strip()

    def _format_grade(self, grade) -> str:
        """📊 FORMATEA CALIFICACIONES CONSISTENTEMENTE"""
        if isinstance(grade, (int, float)) and grade > 0:
            return f"{grade:.1f}" if grade % 1 != 0 else str(int(grade))
        return '-'

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
