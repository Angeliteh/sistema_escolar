"""
🔍 QUERY ANALYZER - Análisis inteligente de consultas

RESPONSABILIDAD: Analizar y categorizar consultas del usuario
TAMAÑO: ~300 líneas

FUNCIONES PRINCIPALES:
- Detectar tipo de consulta (búsqueda, estadística, constancia)
- Extraer entidades y criterios
- Determinar estrategia de ejecución
- Mapear campos a base de datos
"""

import re
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger

class QueryAnalyzer:
    """Analizador inteligente de consultas de usuario"""
    
    def __init__(self, database_analyzer, gemini_client=None):
        self.logger = get_logger(__name__)
        self.database_analyzer = database_analyzer
        self.gemini_client = gemini_client
    
    def analyze_query(self, user_query: str, master_intention: Dict[str, Any], conversation_context: str = "") -> Dict[str, Any]:
        """
        🎯 ANÁLISIS PRINCIPAL DE CONSULTA
        
        Args:
            user_query: Consulta del usuario
            master_intention: Información del Master
            conversation_context: Contexto conversacional
            
        Returns:
            Dict con análisis completo de la consulta
        """
        try:
            self.logger.info(f"🔍 [ANALYZER] Analizando consulta: '{user_query[:50]}...'")
            
            # Extraer información básica
            categoria = master_intention.get('categoria', 'busqueda')
            detected_entities = master_intention.get('detected_entities', {})
            
            # Análisis específico por categoría
            if categoria == 'busqueda':
                return self._analyze_search_query(user_query, detected_entities, conversation_context)
            elif categoria == 'estadistica':
                return self._analyze_statistics_query(user_query, detected_entities, conversation_context)
            elif categoria == 'constancia':
                return self._analyze_constancia_query(user_query, detected_entities, conversation_context)
            elif categoria == 'transformacion':
                return self._analyze_transformation_query(user_query, detected_entities, conversation_context)
            elif categoria == 'continuacion':
                return self._analyze_continuation_query(user_query, detected_entities, conversation_context)
            else:
                return self._analyze_generic_query(user_query, detected_entities, conversation_context)
                
        except Exception as e:
            self.logger.error(f"Error analizando consulta: {e}")
            return self._create_fallback_analysis(user_query, master_intention)
    
    def _analyze_search_query(self, user_query: str, entities: Dict, context: str) -> Dict[str, Any]:
        """Analiza consultas de búsqueda"""
        try:
            # Detectar criterios de búsqueda
            criterios = self._extract_search_criteria(user_query, entities)
            
            # Determinar estrategia
            estrategia = "simple" if len(criterios) <= 1 else "compleja"
            
            # Mapear acción principal
            accion_principal = "BUSCAR_UNIVERSAL"
            
            return {
                "categoria": "busqueda",
                "estrategia": estrategia,
                "accion_principal": accion_principal,
                "criterios": criterios,
                "parametros": {
                    "criterio_principal": criterios[0] if criterios else None,
                    "filtros_adicionales": criterios[1:] if len(criterios) > 1 else []
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando búsqueda: {e}")
            return self._create_fallback_search()
    
    def _analyze_statistics_query(self, user_query: str, entities: Dict, context: str) -> Dict[str, Any]:
        """Analiza consultas de estadísticas"""
        try:
            # Detectar tipo de estadística
            tipo_estadistica = self._detect_statistics_type(user_query)

            return {
                "categoria": "estadistica",
                "estrategia": "simple",
                "accion_principal": "CALCULAR_ESTADISTICA",
                "tipo_estadistica": tipo_estadistica,
                "parametros": {
                    "tipo": tipo_estadistica,
                    "incluir_detalles": "detalle" in user_query.lower()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando estadística: {e}")
            return self._create_fallback_statistics()
    
    def _analyze_constancia_query(self, user_query: str, entities: Dict, context: str) -> Dict[str, Any]:
        """Analiza consultas de constancias"""
        try:
            # Detectar tipo de constancia
            tipo_constancia = self._detect_constancia_type(user_query)

            return {
                "categoria": "constancia",
                "estrategia": "simple",
                "accion_principal": "GENERAR_CONSTANCIA_COMPLETA",
                "tipo_constancia": tipo_constancia,
                "parametros": {
                    "tipo_constancia": tipo_constancia,
                    "incluir_foto": self._detect_photo_request(user_query)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando constancia: {e}")
            return self._create_fallback_constancia()

    def _analyze_transformation_query(self, user_query: str, entities: Dict, context: str) -> Dict[str, Any]:
        """Analiza consultas de transformación de PDF"""
        try:
            # Detectar tipo de constancia destino
            tipo_constancia = self._detect_constancia_type(user_query)

            return {
                "categoria": "transformacion",
                "estrategia": "simple",
                "accion_principal": "TRANSFORMAR_PDF",
                "tipo_constancia": tipo_constancia,
                "parametros": {
                    "tipo_constancia": tipo_constancia,
                    "incluir_foto": self._detect_photo_request(user_query),
                    "guardar_alumno": "guardar" in user_query.lower()
                }
            }

        except Exception as e:
            self.logger.error(f"Error analizando transformación: {e}")
            return self._create_fallback_transformation()

    def _analyze_continuation_query(self, user_query: str, entities: Dict, context: str) -> Dict[str, Any]:
        """Analiza consultas de continuación"""
        try:
            # Detectar tipo de continuación
            if self._is_filter_continuation(user_query):
                return {
                    "categoria": "continuacion",
                    "estrategia": "filtro",
                    "accion_principal": "BUSCAR_Y_FILTRAR",
                    "parametros": {
                        "usar_contexto": True,
                        "criterios": self._extract_filter_criteria(user_query)
                    }
                }
            elif self._is_selection_continuation(user_query):
                return {
                    "categoria": "continuacion",
                    "estrategia": "seleccion",
                    "accion_principal": "CONTINUACION_PROCESADA",
                    "parametros": {
                        "tipo_seleccion": "posicional",
                        "indice": self._extract_position_index(user_query)
                    }
                }
            else:
                return {
                    "categoria": "continuacion",
                    "estrategia": "expansion",
                    "accion_principal": "BUSCAR_UNIVERSAL",
                    "parametros": {
                        "expandir_busqueda": True
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error analizando continuación: {e}")
            return self._create_fallback_continuation()
    
    def _analyze_generic_query(self, user_query: str, entities: Dict, context: str) -> Dict[str, Any]:
        """Análisis genérico para consultas no categorizadas"""
        # Verificar si es transformación de PDF
        if "transform" in user_query.lower() or "pdf" in user_query.lower():
            tipo_constancia = self._detect_constancia_type(user_query)
            return {
                "categoria": "transformacion",
                "estrategia": "simple",
                "accion_principal": "TRANSFORMAR_PDF",
                "tipo_constancia": tipo_constancia,
                "parametros": {
                    "tipo_constancia": tipo_constancia,
                    "incluir_foto": self._detect_photo_request(user_query),
                    "guardar_alumno": "guardar" in user_query.lower()
                }
            }

        return {
            "categoria": "busqueda",
            "estrategia": "simple",
            "accion_principal": "BUSCAR_UNIVERSAL",
            "parametros": {
                "criterio_principal": {
                    "tabla": "alumnos",
                    "campo": "nombre",
                    "operador": "LIKE",
                    "valor": user_query
                }
            }
        }
    
    def _extract_search_criteria(self, user_query: str, entities: Dict) -> List[Dict]:
        """Extrae criterios de búsqueda de la consulta"""
        criterios = []
        user_lower = user_query.lower()
        
        # Detectar nombre/apellido
        if any(word in user_lower for word in ['nombre', 'apellido', 'llama', 'apelliden']):
            # Extraer el nombre/apellido
            nombre_match = re.search(r'(?:nombre|apellido|llama|apelliden)\s+(\w+)', user_lower)
            if nombre_match:
                criterios.append({
                    "tabla": "alumnos",
                    "campo": "nombre",
                    "operador": "LIKE",
                    "valor": nombre_match.group(1)
                })
        
        # Detectar turno dinámicamente
        if 'turno' in user_lower:
            # Buscar cualquier palabra después de "turno" (no solo matutino/vespertino)
            turno_match = re.search(r'turno\s+(\w+)', user_lower)
            if turno_match:
                criterios.append({
                    "tabla": "datos_escolares",
                    "campo": "turno",
                    "operador": "=",
                    "valor": turno_match.group(1).upper()
                })
        
        # Detectar grado
        grado_match = re.search(r'(\d+)(?:°|º)?\s*grado', user_lower)
        if grado_match:
            criterios.append({
                "tabla": "datos_escolares",
                "campo": "grado",
                "operador": "=",
                "valor": grado_match.group(1)
            })
        
        # Detectar grupo
        grupo_match = re.search(r'grupo\s+([a-z])', user_lower)
        if grupo_match:
            criterios.append({
                "tabla": "datos_escolares",
                "campo": "grupo",
                "operador": "=",
                "valor": grupo_match.group(1).upper()
            })
        
        return criterios
    
    def _detect_statistics_type(self, user_query: str) -> str:
        """Detecta el tipo de estadística solicitada"""
        user_lower = user_query.lower()

        if 'promedio' in user_lower:
            return 'promedio'
        elif 'conteo' in user_lower or 'cuantos' in user_lower:
            return 'conteo'
        elif 'distribucion' in user_lower:
            return 'distribucion'
        else:
            return 'general'

    def _detect_grouping_field(self, user_query: str) -> str:
        """Detecta el campo de agrupación para distribuciones"""
        user_lower = user_query.lower()

        if 'grado' in user_lower:
            return 'grado'
        elif 'grupo' in user_lower:
            return 'grupo'
        elif 'turno' in user_lower:
            return 'turno'
        elif 'ciclo' in user_lower:
            return 'ciclo_escolar'
        else:
            return 'grado'  # Default

    def _extract_count_criteria(self, user_query: str) -> List[Dict]:
        """Extrae criterios para consultas de conteo"""
        return self._extract_search_criteria(user_query, {})
    
    def _detect_constancia_type(self, user_query: str) -> str:
        """Detecta el tipo de constancia solicitada"""
        user_lower = user_query.lower()
        
        if 'calificaciones' in user_lower:
            return 'calificaciones'
        elif 'traslado' in user_lower:
            return 'traslado'
        else:
            return 'estudio'
    
    def _detect_photo_request(self, user_query: str) -> bool:
        """Detecta si se solicita incluir foto"""
        return 'foto' in user_query.lower() or 'fotografía' in user_query.lower()
    
    def _is_filter_continuation(self, user_query: str) -> bool:
        """Detecta si es una continuación de filtro"""
        filter_words = ['de esos', 'de esas', 'de ellos', 'de ellas', 'que', 'con']
        return any(word in user_query.lower() for word in filter_words)
    
    def _is_selection_continuation(self, user_query: str) -> bool:
        """Detecta si es una continuación de selección"""
        selection_words = ['primero', 'segundo', 'tercero', 'último', 'el de', 'la de']
        return any(word in user_query.lower() for word in selection_words)
    
    def _extract_filter_criteria(self, user_query: str) -> List[Dict]:
        """Extrae criterios de filtro de una continuación"""
        return self._extract_search_criteria(user_query, {})
    
    def _extract_position_index(self, user_query: str) -> int:
        """Extrae índice posicional de una selección"""
        user_lower = user_query.lower()
        
        if 'primero' in user_lower:
            return 0
        elif 'segundo' in user_lower:
            return 1
        elif 'tercero' in user_lower:
            return 2
        elif 'último' in user_lower:
            return -1
        else:
            return 0
    
    def _create_fallback_analysis(self, user_query: str, master_intention: Dict) -> Dict[str, Any]:
        """Crea análisis de fallback en caso de error"""
        return {
            "categoria": "busqueda",
            "estrategia": "simple",
            "accion_principal": "BUSCAR_UNIVERSAL",
            "parametros": {
                "criterio_principal": {
                    "tabla": "alumnos",
                    "campo": "nombre",
                    "operador": "LIKE",
                    "valor": user_query
                }
            }
        }
    
    def _create_fallback_search(self) -> Dict[str, Any]:
        """Fallback para búsquedas"""
        return {
            "categoria": "busqueda",
            "estrategia": "simple",
            "accion_principal": "BUSCAR_UNIVERSAL",
            "parametros": {}
        }
    
    def _create_fallback_statistics(self) -> Dict[str, Any]:
        """Fallback para estadísticas"""
        return {
            "categoria": "estadistica",
            "estrategia": "simple",
            "accion_principal": "CALCULAR_ESTADISTICA",
            "parametros": {"tipo": "general"}
        }
    
    def _create_fallback_constancia(self) -> Dict[str, Any]:
        """Fallback para constancias"""
        return {
            "categoria": "constancia",
            "estrategia": "simple",
            "accion_principal": "GENERAR_CONSTANCIA_COMPLETA",
            "parametros": {"tipo_constancia": "estudio"}
        }

    def _create_fallback_transformation(self) -> Dict[str, Any]:
        """Fallback para transformaciones"""
        return {
            "categoria": "transformacion",
            "estrategia": "simple",
            "accion_principal": "TRANSFORMAR_PDF",
            "parametros": {
                "tipo_constancia": "estudio",
                "incluir_foto": False,
                "guardar_alumno": False
            }
        }
    
    def _create_fallback_continuation(self) -> Dict[str, Any]:
        """Fallback para continuaciones"""
        return {
            "categoria": "continuacion",
            "estrategia": "expansion",
            "accion_principal": "BUSCAR_UNIVERSAL",
            "parametros": {}
        }
