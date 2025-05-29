"""
Procesador de constancias
Responsabilidad: Manejar la generación y procesamiento de constancias de alumnos
"""
from typing import Dict, Any, Optional
from app.core.logging import get_logger
from ..base_interpreter import InterpretationResult


class ConstanciaProcessor:
    """Procesa solicitudes de constancias de alumnos"""

    def __init__(self, gemini_client=None):
        self.logger = get_logger(__name__)
        self.gemini_client = gemini_client

    def process_constancia_request(self, alumno: Dict, tipo_constancia: str, user_query: str) -> InterpretationResult:
        """
        Procesa una solicitud de constancia para un alumno específico

        Args:
            alumno: Datos completos del alumno
            tipo_constancia: Tipo de constancia (estudios, calificaciones, traslado)
            user_query: Consulta original del usuario

        Returns:
            InterpretationResult con el resultado del procesamiento
        """
        try:
            # Validar datos del alumno
            validation_result = self._validate_student_data(alumno, tipo_constancia)
            if not validation_result['valid']:
                return self._create_error_result(validation_result['message'], validation_result['error_code'])

            # Generar constancia
            generation_result = self._generate_constancia(alumno, tipo_constancia, user_query)

            if generation_result['success']:
                # Generar respuesta con auto-reflexión
                response_with_reflection = self._generate_response_with_reflection(
                    alumno, tipo_constancia, generation_result['data']
                )

                return InterpretationResult(
                    action="constancia_preview",
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Vista previa generada"),
                        "data": generation_result['data'],
                        "files": [generation_result['data'].get("ruta_archivo")] if generation_result['data'].get("ruta_archivo") else [],
                        "alumno": alumno,
                        "tipo_constancia": tipo_constancia,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "constancia_processor"
                    },
                    confidence=0.95
                )
            else:
                return self._create_error_result(
                    f"❌ Error generando constancia: {generation_result['message']}",
                    "generation_failed"
                )

        except Exception as e:
            self.logger.error(f"Error procesando constancia: {e}")
            return self._create_error_result(
                f"❌ Error interno procesando constancia para {alumno.get('nombre', 'N/A')}",
                "internal_error"
            )

    def _validate_student_data(self, alumno: Dict, tipo_constancia: str) -> Dict[str, Any]:
        """Valida que el alumno tenga los datos necesarios para la constancia"""
        try:
            # Verificar que el alumno tenga ID
            alumno_id = alumno.get('id')
            if not alumno_id:
                return {
                    'valid': False,
                    'message': f"Error: No se puede generar constancia, falta ID del alumno {alumno.get('nombre', 'N/A')}",
                    'error_code': 'missing_student_id'
                }

            # 🆕 VERIFICAR CALIFICACIONES MEJORADO - Buscar en múltiples fuentes
            if tipo_constancia == "calificaciones":
                # Buscar calificaciones desde la base de datos directamente
                calificaciones = self._get_calificaciones_from_database(alumno.get('id'))

                self.logger.info(f"🔍 VERIFICANDO CALIFICACIONES (MEJORADO):")
                self.logger.info(f"   - Alumno: {alumno.get('nombre', 'N/A')} (ID: {alumno.get('id')})")
                self.logger.info(f"   - Calificaciones encontradas: {calificaciones is not None}")
                self.logger.info(f"   - Tipo: {type(calificaciones)}")
                self.logger.info(f"   - Cantidad: {len(calificaciones) if isinstance(calificaciones, list) else 'N/A'}")

                if not calificaciones or len(calificaciones) == 0:
                    self.logger.warning(f"❌ {alumno.get('nombre', 'N/A')} no tiene calificaciones registradas en la base de datos")
                    return {
                        'valid': False,
                        'message': f"❌ {alumno.get('nombre', 'N/A')} no tiene calificaciones registradas. No se puede generar constancia de calificaciones.",
                        'error_code': 'no_grades_available'
                    }
                else:
                    self.logger.info(f"✅ {alumno.get('nombre', 'N/A')} tiene {len(calificaciones)} materias con calificaciones")

            return {'valid': True}

        except Exception as e:
            self.logger.error(f"Error validando datos del alumno: {e}")
            return {
                'valid': False,
                'message': f"Error validando datos del alumno: {str(e)}",
                'error_code': 'validation_error'
            }

    def _generate_constancia(self, alumno: Dict, tipo_constancia: str, user_query: str = "") -> Dict[str, Any]:
        """Genera la constancia usando el servicio correspondiente"""
        try:
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            constancia_service = service_provider.constancia_service

            alumno_id = alumno.get('id')

            self.logger.info(f"🎯 GENERANDO CONSTANCIA:")
            self.logger.info(f"   - Tipo: {tipo_constancia}")
            self.logger.info(f"   - Alumno: {alumno.get('nombre')} (ID: {alumno_id})")
            self.logger.info(f"   - Preview mode: True")

            # 🆕 DETECTAR SI SE SOLICITA FOTO EN LA CONSULTA
            incluir_foto = self._detect_photo_request(user_query)

            # Generar vista previa
            self.logger.info("🔄 Llamando a constancia_service.generar_constancia_para_alumno()...")
            success, message, data = constancia_service.generar_constancia_para_alumno(
                alumno_id, tipo_constancia, incluir_foto=incluir_foto, preview_mode=True
            )

            self.logger.info(f"📊 RESULTADO DEL SERVICIO:")
            self.logger.info(f"   - Success: {success}")
            self.logger.info(f"   - Message: {message}")
            self.logger.info(f"   - Data: {data is not None} ({'keys: ' + str(list(data.keys())) if data else 'None'})")

            return {
                'success': success,
                'message': message,
                'data': data
            }

        except Exception as e:
            self.logger.error(f"Error generando constancia: {e}")
            return {
                'success': False,
                'message': f"Error interno: {str(e)}",
                'data': None
            }

    def _generate_response_with_reflection(self, alumno: Dict, tipo_constancia: str, data: Dict) -> Optional[Dict]:
        """Genera respuesta con auto-reflexión sobre la constancia generada"""
        try:
            if not self.gemini_client:
                self.logger.warning("No hay cliente Gemini disponible para auto-reflexión")
                return {
                    "respuesta_usuario": f"✅ Vista previa de constancia de {tipo_constancia} generada para {alumno.get('nombre')}",
                    "reflexion_conversacional": {}
                }

            # Crear prompt para auto-reflexión
            reflection_prompt = f"""
Eres un asistente educativo que acaba de generar una constancia.

INFORMACIÓN DE LA CONSTANCIA GENERADA:
- Alumno: {alumno.get('nombre', 'N/A')}
- Tipo: {tipo_constancia}
- Estado: Vista previa generada exitosamente
- Archivo: {data.get('ruta_archivo', 'N/A')}

INSTRUCCIONES:
1. Genera una respuesta amigable confirmando la generación
2. Incluye auto-reflexión sobre posibles acciones siguientes

RESPONDE con un JSON:
{{
    "respuesta_usuario": "Mensaje amigable para el usuario",
    "reflexion_conversacional": {{
        "espera_continuacion": true|false,
        "tipo_esperado": "confirmation|action|none",
        "datos_recordar": {{"constancia_generada": true, "alumno": "nombre", "tipo": "tipo"}},
        "razonamiento": "Por qué esperas o no continuación"
    }}
}}
"""

            response = self.gemini_client.send_prompt_sync(reflection_prompt)

            if response:
                # Parsear respuesta JSON
                import json
                import re

                # Buscar JSON en la respuesta
                json_patterns = [
                    r'```json\s*(.*?)\s*```',
                    r'```\s*(.*?)\s*```',
                    r'(\{.*?\})'
                ]

                for pattern in json_patterns:
                    matches = re.findall(pattern, response, re.DOTALL)
                    if matches:
                        try:
                            return json.loads(matches[0])
                        except json.JSONDecodeError:
                            continue

                # Intentar parsear directamente
                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    pass

            # Fallback si no se puede parsear
            return {
                "respuesta_usuario": f"✅ Vista previa de constancia de {tipo_constancia} generada para {alumno.get('nombre')}",
                "reflexion_conversacional": {
                    "espera_continuacion": True,
                    "tipo_esperado": "confirmation",
                    "datos_recordar": {
                        "constancia_generada": True,
                        "alumno": alumno.get('nombre'),
                        "tipo": tipo_constancia
                    },
                    "razonamiento": "Se generó una vista previa, el usuario podría querer confirmar o hacer cambios"
                }
            }

        except Exception as e:
            self.logger.error(f"Error generando auto-reflexión: {e}")
            return {
                "respuesta_usuario": f"✅ Vista previa de constancia de {tipo_constancia} generada para {alumno.get('nombre')}",
                "reflexion_conversacional": {}
            }

    def _get_calificaciones_from_database(self, alumno_id: int) -> list:
        """
        🆕 MÉTODO AUXILIAR: Obtiene calificaciones directamente desde la base de datos

        Args:
            alumno_id: ID del alumno

        Returns:
            Lista de calificaciones o lista vacía si no hay
        """
        try:
            if not alumno_id:
                self.logger.warning("No se puede obtener calificaciones: alumno_id es None")
                return []

            # Obtener calificaciones desde el servicio de alumnos
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            alumno_service = service_provider.alumno_service

            # Obtener alumno completo con calificaciones (MÉTODO CORRECTO)
            alumno_completo = alumno_service.get_alumno(alumno_id)

            if not alumno_completo:
                self.logger.info(f"No se encontró alumno con ID {alumno_id}")
                return []

            # Obtener calificaciones del alumno (es un diccionario)
            calificaciones = alumno_completo.get('calificaciones', None)

            self.logger.info(f"📊 CALIFICACIONES DESDE BD:")
            self.logger.info(f"   - Alumno ID: {alumno_id}")
            self.logger.info(f"   - Alumno encontrado: {alumno_completo is not None}")
            self.logger.info(f"   - Calificaciones tipo: {type(calificaciones)}")
            self.logger.info(f"   - Calificaciones cantidad: {len(calificaciones) if isinstance(calificaciones, list) else 'N/A'}")

            if isinstance(calificaciones, list) and len(calificaciones) > 0:
                return calificaciones
            else:
                return []

        except Exception as e:
            self.logger.error(f"Error obteniendo calificaciones desde BD para alumno {alumno_id}: {e}")
            return []

    def _detect_photo_request(self, user_query: str) -> bool:
        """Detecta si el usuario solicita incluir foto en la constancia"""
        if not user_query:
            return False

        user_lower = user_query.lower()
        photo_keywords = ["con foto", "incluir foto", "foto", "fotografía", "imagen"]

        return any(keyword in user_lower for keyword in photo_keywords)

    def _create_error_result(self, message: str, error_code: str) -> InterpretationResult:
        """Crea un resultado de error estandarizado"""
        return InterpretationResult(
            action="constancia_error",
            parameters={
                "message": message,
                "error": error_code
            },
            confidence=0.3
        )

    def detect_constancia_type(self, user_query: str) -> str:
        """Detecta el tipo de constancia solicitada en la consulta"""
        user_lower = user_query.lower()

        if "calificaciones" in user_lower:
            return "calificaciones"
        elif "traslado" in user_lower:
            return "traslado"
        elif "estudios" in user_lower or "estudio" in user_lower:
            return "estudio"
        else:
            return "estudio"  # Por defecto

    def is_constancia_request(self, user_query: str) -> bool:
        """Detecta si la consulta es una solicitud de constancia"""
        constancia_keywords = ["constancia", "certificado", "genera", "generar", "crear", "documento"]
        user_lower = user_query.lower()
        return any(keyword in user_lower for keyword in constancia_keywords)
