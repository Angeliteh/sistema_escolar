"""
🔄 CONTINUATION HANDLER - Manejo inteligente de continuaciones

RESPONSABILIDAD: Manejar consultas de continuación y contexto conversacional
TAMAÑO: ~400 líneas

FUNCIONES PRINCIPALES:
- Detectar tipo de continuación (filtro, selección, expansión)
- Procesar referencias contextuales
- Manejar selecciones posicionales
- Gestionar filtros sobre resultados previos
"""

from typing import Dict, Any, Optional, List
from app.core.logging import get_logger
from ..base_interpreter import InterpretationResult

class ContinuationHandler:
    """Manejador inteligente de continuaciones conversacionales"""
    
    def __init__(self, database_analyzer, sql_executor, gemini_client=None):
        self.logger = get_logger(__name__)
        self.database_analyzer = database_analyzer
        self.sql_executor = sql_executor
        self.gemini_client = gemini_client
    
    def handle_continuation(self, user_query: str, conversation_stack: List[Dict], 
                          continuation_info: Dict[str, Any]) -> Optional[InterpretationResult]:
        """
        🔄 MANEJO PRINCIPAL DE CONTINUACIONES
        
        Args:
            user_query: Consulta del usuario
            conversation_stack: Stack conversacional
            continuation_info: Información de continuación del análisis
            
        Returns:
            InterpretationResult o None si no se puede procesar
        """
        try:
            self.logger.info(f"🔄 [CONTINUATION] Procesando: '{user_query[:50]}...'")
            
            if not conversation_stack:
                self.logger.warning("❌ No hay contexto conversacional para continuación")
                return None
            
            tipo_continuacion = continuation_info.get('estrategia', 'expansion')
            
            if tipo_continuacion == 'seleccion':
                return self._handle_selection_continuation(user_query, conversation_stack, continuation_info)
            elif tipo_continuacion == 'filtro':
                return self._handle_filter_continuation(user_query, conversation_stack, continuation_info)
            elif tipo_continuacion == 'expansion':
                return self._handle_expansion_continuation(user_query, conversation_stack, continuation_info)
            else:
                return self._handle_generic_continuation(user_query, conversation_stack, continuation_info)
                
        except Exception as e:
            self.logger.error(f"Error manejando continuación: {e}")
            return None
    
    def _handle_selection_continuation(self, user_query: str, conversation_stack: List[Dict], 
                                     continuation_info: Dict[str, Any]) -> Optional[InterpretationResult]:
        """Maneja continuaciones de selección (primero, segundo, etc.)"""
        try:
            self.logger.info("🎯 [CONTINUATION] Procesando selección posicional")
            
            # Obtener datos del último nivel
            ultimo_nivel = conversation_stack[-1]
            datos_disponibles = ultimo_nivel.get('data', [])
            
            if not datos_disponibles:
                self.logger.warning("❌ No hay datos en el contexto para selección")
                return None
            
            # Extraer índice de selección
            indice = continuation_info.get('indice', 0)
            
            # Validar índice
            if indice == -1:  # último
                indice = len(datos_disponibles) - 1
            elif indice >= len(datos_disponibles):
                self.logger.warning(f"❌ Índice {indice} fuera de rango (disponibles: {len(datos_disponibles)})")
                return None
            
            # Obtener elemento seleccionado
            elemento_seleccionado = datos_disponibles[indice]
            
            # Crear resultado
            return InterpretationResult(
                action="seleccion_realizada",
                parameters={
                    "alumno_seleccionado": elemento_seleccionado,
                    "indice_seleccionado": indice,
                    "total_disponibles": len(datos_disponibles),
                    "query_original": user_query,
                    "data": [elemento_seleccionado],
                    "row_count": 1,
                    "message": f"Seleccionado: {elemento_seleccionado.get('nombre', 'N/A')}"
                },
                confidence=0.95
            )
            
        except Exception as e:
            self.logger.error(f"Error en selección: {e}")
            return None
    
    def _handle_filter_continuation(self, user_query: str, conversation_stack: List[Dict], 
                                  continuation_info: Dict[str, Any]) -> Optional[InterpretationResult]:
        """Maneja continuaciones de filtro (de esos que...)"""
        try:
            self.logger.info("🔍 [CONTINUATION] Procesando filtro sobre resultados previos")
            
            # Obtener datos del último nivel
            ultimo_nivel = conversation_stack[-1]
            datos_previos = ultimo_nivel.get('data', [])
            
            if not datos_previos:
                self.logger.warning("❌ No hay datos previos para filtrar")
                return None
            
            # Obtener criterios de filtro
            criterios = continuation_info.get('criterios', [])
            
            if not criterios:
                self.logger.warning("❌ No se detectaron criterios de filtro")
                return None
            
            # Aplicar filtros
            datos_filtrados = self._apply_filters_to_data(datos_previos, criterios)
            
            # Crear resultado
            return InterpretationResult(
                action="filtro_aplicado",
                parameters={
                    "data": datos_filtrados,
                    "row_count": len(datos_filtrados),
                    "total_previos": len(datos_previos),
                    "criterios_aplicados": criterios,
                    "query_original": user_query,
                    "message": f"Filtrados {len(datos_filtrados)} de {len(datos_previos)} resultados"
                },
                confidence=0.9
            )
            
        except Exception as e:
            self.logger.error(f"Error en filtro: {e}")
            return None
    
    def _handle_expansion_continuation(self, user_query: str, conversation_stack: List[Dict], 
                                     continuation_info: Dict[str, Any]) -> Optional[InterpretationResult]:
        """Maneja continuaciones de expansión (nueva búsqueda)"""
        try:
            self.logger.info("🔄 [CONTINUATION] Procesando expansión de búsqueda")
            
            # Para expansiones, retornamos None para que se procese como búsqueda normal
            # pero con contexto conversacional disponible
            return None
            
        except Exception as e:
            self.logger.error(f"Error en expansión: {e}")
            return None
    
    def _handle_generic_continuation(self, user_query: str, conversation_stack: List[Dict], 
                                   continuation_info: Dict[str, Any]) -> Optional[InterpretationResult]:
        """Maneja continuaciones genéricas"""
        try:
            self.logger.info("🔄 [CONTINUATION] Procesando continuación genérica")
            
            # Análisis básico del contexto
            ultimo_nivel = conversation_stack[-1]
            datos_disponibles = ultimo_nivel.get('data', [])
            
            if not datos_disponibles:
                return None
            
            # Crear respuesta contextual básica
            return InterpretationResult(
                action="continuacion_procesada",
                parameters={
                    "data": datos_disponibles,
                    "row_count": len(datos_disponibles),
                    "query_original": user_query,
                    "message": f"Contexto disponible: {len(datos_disponibles)} elementos"
                },
                confidence=0.7
            )
            
        except Exception as e:
            self.logger.error(f"Error en continuación genérica: {e}")
            return None
    
    def _apply_filters_to_data(self, data: List[Dict], criterios: List[Dict]) -> List[Dict]:
        """Aplica filtros a los datos en memoria"""
        try:
            datos_filtrados = data.copy()
            
            for criterio in criterios:
                campo = criterio.get('campo', '')
                operador = criterio.get('operador', '=')
                valor = criterio.get('valor', '').upper()
                
                if not campo or not valor:
                    continue
                
                # Aplicar filtro
                if operador == 'LIKE':
                    datos_filtrados = [
                        item for item in datos_filtrados
                        if valor in str(item.get(campo, '')).upper()
                    ]
                elif operador == '=':
                    datos_filtrados = [
                        item for item in datos_filtrados
                        if str(item.get(campo, '')).upper() == valor
                    ]
                elif operador == '>':
                    try:
                        valor_num = float(valor)
                        datos_filtrados = [
                            item for item in datos_filtrados
                            if float(item.get(campo, 0)) > valor_num
                        ]
                    except ValueError:
                        continue
                elif operador == '<':
                    try:
                        valor_num = float(valor)
                        datos_filtrados = [
                            item for item in datos_filtrados
                            if float(item.get(campo, 0)) < valor_num
                        ]
                    except ValueError:
                        continue
            
            return datos_filtrados
            
        except Exception as e:
            self.logger.error(f"Error aplicando filtros: {e}")
            return data
    
    def analyze_context_needs(self, user_query: str, conversation_stack: List[Dict]) -> Dict[str, Any]:
        """
        🧠 ANÁLISIS INTELIGENTE DE NECESIDADES DE CONTEXTO
        
        Determina si la consulta necesita información del contexto conversacional
        y qué tipo de procesamiento requiere.
        """
        try:
            if not conversation_stack:
                return {"needs_context": False, "reason": "no_context_available"}
            
            user_lower = user_query.lower()
            ultimo_nivel = conversation_stack[-1]
            datos_disponibles = ultimo_nivel.get('data', [])
            
            # Palabras que indican referencia contextual
            context_indicators = [
                'de esos', 'de esas', 'de ellos', 'de ellas',
                'primero', 'segundo', 'tercero', 'último',
                'el de', 'la de', 'ese', 'esa', 'esos', 'esas'
            ]
            
            has_context_reference = any(indicator in user_lower for indicator in context_indicators)
            
            if has_context_reference:
                # Determinar tipo de referencia
                if any(word in user_lower for word in ['primero', 'segundo', 'tercero', 'último']):
                    return {
                        "needs_context": True,
                        "type": "selection",
                        "reason": "positional_reference",
                        "available_items": len(datos_disponibles)
                    }
                elif any(word in user_lower for word in ['de esos', 'de esas', 'que']):
                    return {
                        "needs_context": True,
                        "type": "filter",
                        "reason": "filter_reference",
                        "available_items": len(datos_disponibles)
                    }
                else:
                    return {
                        "needs_context": True,
                        "type": "generic",
                        "reason": "generic_reference",
                        "available_items": len(datos_disponibles)
                    }
            
            # Verificar si es una consulta que podría beneficiarse del contexto
            # aunque no tenga referencias explícitas
            if datos_disponibles and len(datos_disponibles) > 0:
                # Si hay datos disponibles y la consulta es corta, podría ser continuación
                if len(user_query.split()) <= 3:
                    return {
                        "needs_context": True,
                        "type": "expansion",
                        "reason": "short_query_with_context",
                        "available_items": len(datos_disponibles)
                    }
            
            return {
                "needs_context": False,
                "reason": "no_context_indicators",
                "available_items": len(datos_disponibles)
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando necesidades de contexto: {e}")
            return {"needs_context": False, "reason": "analysis_error"}
    
    def extract_positional_reference(self, user_query: str) -> Optional[int]:
        """Extrae referencia posicional de la consulta"""
        user_lower = user_query.lower()
        
        if 'primero' in user_lower or 'primer' in user_lower:
            return 0
        elif 'segundo' in user_lower:
            return 1
        elif 'tercero' in user_lower or 'tercer' in user_lower:
            return 2
        elif 'cuarto' in user_lower:
            return 3
        elif 'quinto' in user_lower:
            return 4
        elif 'último' in user_lower or 'ultima' in user_lower:
            return -1
        
        return None
    
    def format_conversation_context(self, conversation_stack: List[Dict]) -> str:
        """Formatea el contexto conversacional para uso en prompts"""
        try:
            if not conversation_stack:
                return "No hay contexto conversacional previo."
            
            context_lines = []
            for i, nivel in enumerate(conversation_stack):
                query = nivel.get('query', 'N/A')
                row_count = nivel.get('row_count', 0)
                context_lines.append(f"Nivel {i+1}: '{query}' → {row_count} resultados")
            
            return "\n".join(context_lines)
            
        except Exception as e:
            self.logger.error(f"Error formateando contexto: {e}")
            return "Error formateando contexto conversacional."
