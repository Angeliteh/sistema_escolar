"""
Generador de respuestas
Responsabilidad: Generar respuestas apropiadas para diferentes tipos de consultas
"""
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger


class ResponseGenerator:
    """Genera respuestas contextuales para consultas de alumnos"""
    
    def __init__(self, gemini_client=None, prompt_manager=None):
        self.logger = get_logger(__name__)
        self.gemini_client = gemini_client
        self.prompt_manager = prompt_manager
    
    def generate_continuation_response(self, user_query: str, continuation_type: str, 
                                     ultimo_nivel: Dict, conversation_stack: list) -> str:
        """
        Genera respuesta unificada para continuaciones usando PromptManager
        
        Args:
            user_query: Consulta del usuario
            continuation_type: Tipo de continuación (action, selection, confirmation)
            ultimo_nivel: Último nivel de la pila conversacional
            conversation_stack: Pila conversacional completa
            
        Returns:
            Respuesta generada para el usuario
        """
        try:
            if not self.prompt_manager or not self.gemini_client:
                return self._generate_fallback_response(user_query, continuation_type)
            
            # Usar PromptManager para respuesta unificada
            continuation_prompt = self.prompt_manager.get_unified_continuation_prompt(
                user_query, continuation_type, ultimo_nivel, conversation_stack
            )
            
            response = self.gemini_client.send_prompt_sync(continuation_prompt)
            if response:
                return response.strip()
            else:
                return self._generate_fallback_response(user_query, continuation_type)
                
        except Exception as e:
            self.logger.error(f"Error generando respuesta de continuación: {e}")
            return self._generate_fallback_response(user_query, continuation_type)
    
    def generate_sql_response_with_reflection(self, user_query: str, sql_query: str, 
                                            data: List[Dict], row_count: int) -> Optional[Dict]:
        """
        Genera respuesta para consultas SQL con auto-reflexión
        
        Args:
            user_query: Consulta original del usuario
            sql_query: Consulta SQL ejecutada
            data: Datos obtenidos
            row_count: Número de filas
            
        Returns:
            Dict con respuesta y reflexión conversacional
        """
        try:
            if not self.prompt_manager or not self.gemini_client:
                return self._generate_fallback_sql_response(user_query, data, row_count)
            
            # Usar PromptManager para generar respuesta con reflexión
            response_prompt = self.prompt_manager.get_response_with_reflection_prompt(
                user_query, sql_query, data, row_count
            )
            
            response = self.gemini_client.send_prompt_sync(response_prompt)
            
            if response:
                parsed_response = self._parse_json_response(response)
                if parsed_response:
                    return parsed_response
            
            return self._generate_fallback_sql_response(user_query, data, row_count)
            
        except Exception as e:
            self.logger.error(f"Error generando respuesta SQL con reflexión: {e}")
            return self._generate_fallback_sql_response(user_query, data, row_count)
    
    def generate_error_response(self, error_type: str, details: Dict[str, Any]) -> str:
        """
        Genera respuestas de error amigables
        
        Args:
            error_type: Tipo de error
            details: Detalles del error
            
        Returns:
            Mensaje de error amigable para el usuario
        """
        error_messages = {
            'no_students_found': "No encontré alumnos que coincidan con tu búsqueda. ¿Podrías intentar con otros criterios?",
            'missing_student_id': f"No puedo generar la constancia porque faltan datos del alumno {details.get('student_name', '')}.",
            'no_grades_available': f"El alumno {details.get('student_name', '')} no tiene calificaciones registradas para generar una constancia de calificaciones.",
            'sql_error': "Hubo un problema procesando tu consulta. ¿Podrías reformularla?",
            'internal_error': "Ocurrió un error interno. Por favor, intenta nuevamente.",
            'invalid_continuation': "No entiendo a qué te refieres. ¿Podrías ser más específico?",
            'out_of_range': f"Solo hay {details.get('available_count', 0)} elementos disponibles. ¿Podrías elegir un número válido?"
        }
        
        return error_messages.get(error_type, "Ocurrió un error procesando tu solicitud.")
    
    def generate_confirmation_response(self, action_type: str, target: str) -> str:
        """
        Genera respuestas de confirmación
        
        Args:
            action_type: Tipo de acción a confirmar
            target: Objetivo de la acción
            
        Returns:
            Mensaje de confirmación
        """
        confirmation_templates = {
            'constancia_generation': f"¿Quieres que genere una constancia para {target}?",
            'data_display': f"¿Te muestro más información sobre {target}?",
            'list_continuation': f"¿Necesitas hacer algo más con {target}?",
            'search_refinement': f"¿Quieres refinar la búsqueda de {target}?"
        }
        
        return confirmation_templates.get(action_type, f"¿Continúo con {target}?")
    
    def _generate_fallback_response(self, user_query: str, continuation_type: str) -> str:
        """Genera respuesta de fallback cuando no hay LLM disponible"""
        fallback_responses = {
            'action': f"✅ Procesando acción para: {user_query}",
            'selection': f"✅ Elemento seleccionado: {user_query}",
            'confirmation': f"✅ Confirmación procesada: {user_query}",
            'specification': f"✅ Especificación procesada: {user_query}"
        }
        
        return fallback_responses.get(continuation_type, f"✅ Procesando solicitud: {user_query}")
    
    def _generate_fallback_sql_response(self, user_query: str, data: List[Dict], row_count: int) -> Dict:
        """Genera respuesta de fallback para consultas SQL"""
        if row_count == 0:
            message = "No se encontraron resultados para tu consulta."
        elif row_count == 1:
            message = "Encontré 1 resultado para tu consulta."
        else:
            message = f"Encontré {row_count} resultados para tu consulta."
        
        return {
            "respuesta_usuario": message,
            "reflexion_conversacional": {
                "espera_continuacion": row_count > 0,
                "tipo_esperado": "selection" if row_count > 1 else "action" if row_count == 1 else "none",
                "datos_recordar": {
                    "query": user_query,
                    "data": data,
                    "row_count": row_count
                },
                "razonamiento": "Respuesta generada sin LLM disponible"
            }
        }
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parsea respuesta JSON del LLM"""
        try:
            import json
            import re
            
            # Limpiar la respuesta
            clean_response = response.strip()
            
            # Buscar JSON en la respuesta
            json_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```',
                r'(\{.*?\})'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, clean_response, re.DOTALL)
                if matches:
                    try:
                        return json.loads(matches[0])
                    except json.JSONDecodeError:
                        continue
            
            # Intentar parsear directamente
            try:
                return json.loads(clean_response)
            except json.JSONDecodeError:
                return None
                
        except Exception as e:
            self.logger.error(f"Error parseando JSON: {e}")
            return None
    
    def format_student_list(self, students: List[Dict], query_context: str = "") -> str:
        """
        Formatea una lista de alumnos para mostrar al usuario
        
        Args:
            students: Lista de alumnos
            query_context: Contexto de la consulta
            
        Returns:
            Lista formateada como string
        """
        if not students:
            return "No se encontraron alumnos."
        
        if len(students) == 1:
            student = students[0]
            return f"📋 Alumno encontrado: {student.get('nombre', 'N/A')}"
        
        formatted_list = f"📋 {len(students)} alumnos encontrados:\n"
        for i, student in enumerate(students, 1):
            formatted_list += f"{i}. {student.get('nombre', 'N/A')}\n"
        
        return formatted_list.strip()
    
    def format_student_details(self, student: Dict) -> str:
        """
        Formatea los detalles de un alumno específico
        
        Args:
            student: Datos del alumno
            
        Returns:
            Detalles formateados como string
        """
        details = f"👤 **{student.get('nombre', 'N/A')}**\n"
        
        if student.get('curp'):
            details += f"🆔 CURP: {student['curp']}\n"
        
        if student.get('grado') and student.get('grupo'):
            details += f"📚 Grado: {student['grado']}° {student.get('grupo', '')}\n"
        
        if student.get('turno'):
            details += f"🕐 Turno: {student['turno']}\n"
        
        return details.strip()
