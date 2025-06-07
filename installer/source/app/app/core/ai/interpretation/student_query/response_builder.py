"""
📝 RESPONSE BUILDER - Construcción inteligente de respuestas

RESPONSABILIDAD: Construir respuestas finales y auto-reflexión
TAMAÑO: ~300 líneas

FUNCIONES PRINCIPALES:
- Generar respuestas técnicas para el Master
- Crear auto-reflexión conversacional
- Formatear datos para presentación
- Determinar expectativas de continuación
"""

from typing import Dict, Any, Optional, List
from app.core.logging import get_logger

class ResponseBuilder:
    """Constructor inteligente de respuestas y auto-reflexión"""
    
    def __init__(self, prompt_manager, gemini_client=None):
        self.logger = get_logger(__name__)
        self.prompt_manager = prompt_manager
        self.gemini_client = gemini_client
    
    def build_response(self, user_query: str, execution_result: Dict[str, Any], 
                      conversation_stack: List[Dict] = None) -> Dict[str, Any]:
        """
        📝 CONSTRUCCIÓN PRINCIPAL DE RESPUESTA
        
        Args:
            user_query: Consulta original del usuario
            execution_result: Resultado de la ejecución
            conversation_stack: Contexto conversacional
            
        Returns:
            Dict con respuesta técnica y auto-reflexión
        """
        try:
            self.logger.info(f"📝 [RESPONSE] Construyendo respuesta para: '{user_query[:50]}...'")
            
            # Extraer datos básicos
            data = execution_result.get('data', [])
            row_count = execution_result.get('row_count', 0)
            sql_executed = execution_result.get('sql_executed', '')
            action_used = execution_result.get('action_used', '')
            
            # Generar respuesta técnica
            technical_response = self._generate_technical_response(
                user_query, data, row_count, action_used
            )
            
            # Generar auto-reflexión
            reflexion = self._generate_auto_reflection(
                user_query, data, row_count, conversation_stack
            )
            
            return {
                "respuesta_usuario": technical_response,
                "reflexion_conversacional": reflexion,
                "data_summary": self._create_data_summary(data, row_count),
                "execution_info": {
                    "sql_executed": sql_executed,
                    "action_used": action_used,
                    "row_count": row_count
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error construyendo respuesta: {e}")
            return self._create_fallback_response(user_query, execution_result)
    
    def _generate_technical_response(self, user_query: str, data: List[Dict], 
                                   row_count: int, action_used: str) -> str:
        """Genera respuesta técnica para el Master"""
        try:
            if row_count == 0:
                return f"No se encontraron resultados para: '{user_query}'"
            elif row_count == 1:
                alumno = data[0] if data else {}
                nombre = alumno.get('nombre', 'N/A')
                return f"Encontrado: {nombre}"
            else:
                return f"Encontrados {row_count} resultados para: '{user_query}'"
                
        except Exception as e:
            self.logger.error(f"Error generando respuesta técnica: {e}")
            return f"Procesada consulta: '{user_query}'"
    
    def _generate_auto_reflection(self, user_query: str, data: List[Dict], 
                                row_count: int, conversation_stack: List[Dict] = None) -> Dict[str, Any]:
        """Genera auto-reflexión conversacional"""
        try:
            # Determinar si se espera continuación
            espera_continuacion = self._should_expect_continuation(user_query, data, row_count)
            
            # Determinar tipo de continuación esperada
            tipo_esperado = self._determine_expected_continuation_type(user_query, data, row_count)
            
            # Generar nota estratégica para el Master
            nota_estrategica = self._generate_strategic_note(
                user_query, data, row_count, espera_continuacion, tipo_esperado
            )
            
            return {
                "espera_continuacion": espera_continuacion,
                "tipo_esperado": tipo_esperado,
                "nota_para_master": nota_estrategica,
                "datos_recordar": {
                    "query": user_query,
                    "data": data[:10] if len(data) > 10 else data,  # Limitar datos
                    "row_count": row_count,
                    "context": f"Lista de {row_count} elementos disponible",
                    "filter_applied": "N/A"
                },
                "razonamiento": nota_estrategica  # Compatibilidad
            }
            
        except Exception as e:
            self.logger.error(f"Error generando auto-reflexión: {e}")
            return self._create_fallback_reflection()
    
    def _should_expect_continuation(self, user_query: str, data: List[Dict], row_count: int) -> bool:
        """Determina si se debe esperar una continuación"""
        try:
            # Si hay múltiples resultados, es probable que haya continuación
            if row_count > 1:
                return True
            
            # Si es una búsqueda general, es probable que haya continuación
            general_search_indicators = ['dame', 'muestra', 'lista', 'busca', 'encuentra']
            if any(indicator in user_query.lower() for indicator in general_search_indicators):
                return True
            
            # Si hay un solo resultado, podría haber solicitud de acción
            if row_count == 1:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error determinando expectativa de continuación: {e}")
            return False
    
    def _determine_expected_continuation_type(self, user_query: str, data: List[Dict], row_count: int) -> str:
        """Determina el tipo de continuación esperada"""
        try:
            if row_count > 1:
                # Múltiples resultados: probable filtro o selección
                return "filter_or_selection"
            elif row_count == 1:
                # Un resultado: probable acción específica
                return "action"
            else:
                # Sin resultados: probable nueva búsqueda
                return "new_search"
                
        except Exception as e:
            self.logger.error(f"Error determinando tipo de continuación: {e}")
            return "unknown"
    
    def _generate_strategic_note(self, user_query: str, data: List[Dict], row_count: int, 
                               espera_continuacion: bool, tipo_esperado: str) -> str:
        """Genera nota estratégica para el Master"""
        try:
            if row_count == 0:
                return "Sin resultados. Usuario podría reformular búsqueda o probar criterios diferentes."
            elif row_count == 1:
                alumno = data[0] if data else {}
                nombre = alumno.get('nombre', 'N/A')
                return f"Un resultado encontrado ({nombre}). Usuario podría solicitar constancia, detalles o nueva búsqueda."
            elif row_count <= 10:
                return f"{row_count} resultados encontrados. Usuario podría filtrar, seleccionar uno específico o solicitar acciones."
            else:
                return f"{row_count} resultados encontrados. Lista extensa - usuario probablemente necesitará filtrar o refinar búsqueda."
                
        except Exception as e:
            self.logger.error(f"Error generando nota estratégica: {e}")
            return "Consulta procesada. Esperando instrucciones del usuario."
    
    def _create_data_summary(self, data: List[Dict], row_count: int) -> Dict[str, Any]:
        """Crea resumen de los datos para el Master"""
        try:
            if not data:
                return {"type": "empty", "count": 0, "summary": "Sin datos"}
            
            # Analizar estructura de datos
            sample = data[0]
            fields = list(sample.keys())
            
            # Crear resumen
            summary = {
                "type": "student_list",
                "count": row_count,
                "fields": fields,
                "sample": {
                    "nombre": sample.get('nombre', 'N/A'),
                    "curp": sample.get('curp', 'N/A')[:8] + "..." if sample.get('curp') else 'N/A'
                }
            }
            
            # Agregar información adicional si está disponible
            if 'grado' in sample:
                summary["has_school_data"] = True
            if 'promedio' in sample:
                summary["has_grades"] = True
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creando resumen de datos: {e}")
            return {"type": "unknown", "count": row_count, "summary": "Error analizando datos"}
    
    def _create_fallback_response(self, user_query: str, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Crea respuesta de fallback en caso de error"""
        return {
            "respuesta_usuario": f"Consulta procesada: '{user_query}'",
            "reflexion_conversacional": self._create_fallback_reflection(),
            "data_summary": {"type": "fallback", "count": 0, "summary": "Error procesando"},
            "execution_info": {
                "sql_executed": execution_result.get('sql_executed', ''),
                "action_used": execution_result.get('action_used', 'UNKNOWN'),
                "row_count": execution_result.get('row_count', 0)
            }
        }
    
    def _create_fallback_reflection(self) -> Dict[str, Any]:
        """Crea auto-reflexión de fallback"""
        return {
            "espera_continuacion": False,
            "tipo_esperado": "unknown",
            "nota_para_master": "Error en procesamiento. Esperando nueva consulta.",
            "datos_recordar": {
                "query": "",
                "data": [],
                "row_count": 0,
                "context": "Error en procesamiento",
                "filter_applied": "N/A"
            },
            "razonamiento": "Error en auto-reflexión"
        }
    
    def format_for_display(self, data: List[Dict], display_type: str = "auto") -> Dict[str, Any]:
        """
        🎨 FORMATEO PARA VISUALIZACIÓN
        
        Formatea los datos para diferentes tipos de visualización
        """
        try:
            if not data:
                return {"type": "empty", "content": "Sin datos para mostrar"}
            
            row_count = len(data)
            
            # Determinar tipo de display automáticamente si no se especifica
            if display_type == "auto":
                if row_count == 1:
                    display_type = "detail"
                elif row_count <= 5:
                    display_type = "compact"
                elif row_count <= 20:
                    display_type = "summary"
                else:
                    display_type = "count_only"
            
            # Formatear según el tipo
            if display_type == "detail":
                return self._format_detail_view(data[0])
            elif display_type == "compact":
                return self._format_compact_view(data)
            elif display_type == "summary":
                return self._format_summary_view(data)
            else:
                return self._format_count_only(data)
                
        except Exception as e:
            self.logger.error(f"Error formateando para display: {e}")
            return {"type": "error", "content": "Error formateando datos"}
    
    def _format_detail_view(self, alumno: Dict) -> Dict[str, Any]:
        """Formatea vista detallada de un alumno"""
        return {
            "type": "detail",
            "content": {
                "nombre": alumno.get('nombre', 'N/A'),
                "curp": alumno.get('curp', 'N/A'),
                "matricula": alumno.get('matricula', 'N/A'),
                "grado": alumno.get('grado', 'N/A'),
                "grupo": alumno.get('grupo', 'N/A'),
                "turno": alumno.get('turno', 'N/A')
            }
        }
    
    def _format_compact_view(self, data: List[Dict]) -> Dict[str, Any]:
        """Formatea vista compacta para pocos elementos"""
        items = []
        for alumno in data:
            items.append({
                "nombre": alumno.get('nombre', 'N/A'),
                "curp": alumno.get('curp', 'N/A')[:8] + "..." if alumno.get('curp') else 'N/A',
                "info": f"{alumno.get('grado', '')}° {alumno.get('grupo', '')} {alumno.get('turno', '')}"
            })
        
        return {
            "type": "compact",
            "content": items,
            "count": len(data)
        }
    
    def _format_summary_view(self, data: List[Dict]) -> Dict[str, Any]:
        """Formatea vista resumen para elementos medianos"""
        # Mostrar solo nombres y conteo por grado/grupo
        nombres = [alumno.get('nombre', 'N/A') for alumno in data[:10]]
        
        return {
            "type": "summary",
            "content": {
                "sample_names": nombres,
                "total_count": len(data),
                "showing": min(10, len(data))
            }
        }
    
    def _format_count_only(self, data: List[Dict]) -> Dict[str, Any]:
        """Formatea solo conteo para listas grandes"""
        return {
            "type": "count_only",
            "content": {
                "total_count": len(data),
                "message": f"Se encontraron {len(data)} resultados"
            }
        }
