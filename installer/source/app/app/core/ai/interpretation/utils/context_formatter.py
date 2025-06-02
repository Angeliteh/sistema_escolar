"""
Formateador de contexto
Responsabilidad: Formatear contexto conversacional para LLMs
"""
from typing import Dict, Any, List, Optional
from app.core.logging import get_logger


class ContextFormatter:
    """Formatea contexto conversacional para uso en prompts de LLM"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def format_conversation_stack(self, conversation_stack: List[Dict]) -> str:
        """
        Formatea la pila conversacional para incluir en prompts
        
        Args:
            conversation_stack: Lista de niveles conversacionales
            
        Returns:
            String formateado para usar en prompts
        """
        try:
            if not conversation_stack:
                return "PILA CONVERSACIONAL VACÍA"
            
            formatted_context = "CONTEXTO CONVERSACIONAL:\n"
            
            for i, level in enumerate(conversation_stack, 1):
                formatted_context += self._format_conversation_level(level, i)
            
            return formatted_context
            
        except Exception as e:
            self.logger.error(f"Error formateando pila conversacional: {e}")
            return "ERROR FORMATEANDO CONTEXTO"
    
    def _format_conversation_level(self, level: Dict, level_number: int) -> str:
        """Formatea un nivel individual de la conversación"""
        formatted = f"\nNIVEL {level_number}:\n"
        formatted += f"- Consulta: \"{level.get('query', 'N/A')}\"\n"
        formatted += f"- Elementos: {level.get('row_count', 0)}\n"
        formatted += f"- Esperando: {level.get('awaiting', 'N/A')}\n"
        
        # Agregar muestra de datos si están disponibles
        if level.get('data') and len(level.get('data', [])) > 0:
            data_sample = self._format_data_sample(level['data'])
            formatted += f"- Datos: {data_sample}\n"
        
        return formatted
    
    def _format_data_sample(self, data: List[Dict], max_items: int = 3) -> str:
        """Formatea una muestra de los datos para el contexto"""
        if not data:
            return "Sin datos"
        
        sample_items = data[:max_items]
        formatted_items = []
        
        for item in sample_items:
            if isinstance(item, dict):
                # Extraer información clave del item
                key_info = self._extract_key_info(item)
                formatted_items.append(key_info)
            else:
                formatted_items.append(str(item))
        
        result = ", ".join(formatted_items)
        
        if len(data) > max_items:
            result += f" (y {len(data) - max_items} más)"
        
        return result
    
    def _extract_key_info(self, item: Dict) -> str:
        """Extrae información clave de un item de datos"""
        # Priorizar campos importantes
        priority_fields = ['nombre', 'nombre_alumno', 'curp', 'grado', 'grupo']
        
        key_info = []
        for field in priority_fields:
            if field in item and item[field]:
                key_info.append(f"{field}: {item[field]}")
                break  # Solo tomar el primer campo encontrado para mantenerlo conciso
        
        if not key_info:
            # Si no hay campos prioritarios, tomar el primer campo disponible
            for key, value in item.items():
                if value and len(str(value)) < 50:  # Evitar valores muy largos
                    key_info.append(f"{key}: {value}")
                    break
        
        return key_info[0] if key_info else "Sin información clave"
    
    def format_student_list_for_prompt(self, students: List[Dict]) -> str:
        """
        Formatea lista de alumnos específicamente para prompts
        
        Args:
            students: Lista de alumnos
            
        Returns:
            String formateado para prompts
        """
        if not students:
            return "No hay alumnos disponibles"
        
        formatted = f"ALUMNOS DISPONIBLES ({len(students)}):\n"
        
        for i, student in enumerate(students, 1):
            name = student.get('nombre') or student.get('nombre_alumno', 'N/A')
            formatted += f"{i}. {name}\n"
        
        return formatted.strip()
    
    def format_query_context(self, user_query: str, previous_queries: List[str] = None) -> str:
        """
        Formatea el contexto de consultas para prompts
        
        Args:
            user_query: Consulta actual del usuario
            previous_queries: Consultas anteriores (opcional)
            
        Returns:
            Contexto formateado
        """
        context = f"CONSULTA ACTUAL: \"{user_query}\"\n"
        
        if previous_queries:
            context += "\nCONSULTAS ANTERIORES:\n"
            for i, query in enumerate(previous_queries[-3:], 1):  # Solo las últimas 3
                context += f"{i}. \"{query}\"\n"
        
        return context
    
    def format_error_context(self, error_type: str, details: Dict[str, Any]) -> str:
        """
        Formatea contexto de error para logging y debugging
        
        Args:
            error_type: Tipo de error
            details: Detalles del error
            
        Returns:
            Contexto de error formateado
        """
        formatted = f"ERROR: {error_type}\n"
        
        for key, value in details.items():
            if isinstance(value, (list, dict)):
                formatted += f"- {key}: {type(value).__name__} con {len(value)} elementos\n"
            else:
                formatted += f"- {key}: {value}\n"
        
        return formatted
    
    def truncate_for_prompt(self, text: str, max_length: int = 1000) -> str:
        """
        Trunca texto para que quepa en prompts sin perder información importante
        
        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            
        Returns:
            Texto truncado
        """
        if len(text) <= max_length:
            return text
        
        # Truncar pero intentar mantener líneas completas
        truncated = text[:max_length]
        last_newline = truncated.rfind('\n')
        
        if last_newline > max_length * 0.8:  # Si hay un salto de línea cerca del final
            truncated = truncated[:last_newline]
        
        return truncated + "\n... (truncado)"
    
    def format_system_state(self, state_info: Dict[str, Any]) -> str:
        """
        Formatea información del estado del sistema para contexto
        
        Args:
            state_info: Información del estado del sistema
            
        Returns:
            Estado formateado
        """
        formatted = "ESTADO DEL SISTEMA:\n"
        
        for key, value in state_info.items():
            if key == 'conversation_stack':
                formatted += f"- Niveles conversacionales: {len(value) if value else 0}\n"
            elif key == 'last_action':
                formatted += f"- Última acción: {value}\n"
            elif key == 'pending_confirmations':
                formatted += f"- Confirmaciones pendientes: {len(value) if value else 0}\n"
            else:
                formatted += f"- {key}: {value}\n"
        
        return formatted
