"""
🧠 GESTOR UNIFICADO DE CONTEXTO CONVERSACIONAL
Centraliza TODA la lógica de contexto, continuaciones y decisiones inteligentes
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from app.core.logging import get_logger


@dataclass
class ContextLevel:
    """Representa un nivel en la pila conversacional"""
    query: str
    data: List[Dict]
    row_count: int
    awaiting_type: str  # "selection", "action", "confirmation", "specification"
    timestamp: str
    sql_query: str
    message: str
    context_info: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "data": self.data,
            "row_count": self.row_count,
            "awaiting": self.awaiting_type,
            "timestamp": self.timestamp,
            "sql_query": self.sql_query,
            "message": self.message,
            "context": self.context_info
        }


@dataclass
class ContextAnalysis:
    """Resultado del análisis de contexto"""
    has_context: bool
    available_fields: List[str]
    data_count: int
    data_type: str  # "list", "single", "empty"
    sample_data: Dict[str, Any]
    context_quality: str  # "complete", "partial", "minimal", "none"


@dataclass
class RequirementAnalysis:
    """Análisis de requerimientos de la consulta"""
    required_fields: List[str]
    detail_level: str  # "basic", "complete", "constancia"
    needs_database_search: bool
    query_type: str
    specific_requests: List[str]


@dataclass
class IntelligentDecision:
    """Decisión inteligente sobre cómo proceder"""
    action: str  # "use_context", "expand_search", "new_query"
    reason: str
    confidence: float
    recommended_fields: List[str]
    fallback_action: str


class UnifiedContextManager:
    """
    🧠 GESTOR UNIFICADO DE CONTEXTO CONVERSACIONAL
    
    RESPONSABILIDADES:
    1. Mantener pila conversacional unificada
    2. Detectar continuaciones inteligentemente
    3. Analizar contexto disponible
    4. Analizar requerimientos de consultas
    5. Tomar decisiones inteligentes
    6. Resolver referencias contextuales
    """
    
    def __init__(self, gemini_client=None):
        self.logger = get_logger(__name__)
        self.gemini_client = gemini_client
        
        # 🎯 PILA CONVERSACIONAL UNIFICADA
        self.conversation_stack: List[ContextLevel] = []
        self.conversation_history: List[Dict] = []
        
        # 🧠 ESTADO DE CONTINUACIÓN
        self.awaiting_continuation = False
        self.last_decision: Optional[IntelligentDecision] = None
        
        # 📊 MÉTRICAS DE CONTEXTO
        self.context_usage_stats = {
            "context_used": 0,
            "searches_expanded": 0,
            "decisions_made": 0
        }
    
    def add_context_level(self, query: str, result_data: Dict[str, Any], 
                         awaiting_type: str, context_info: str = "") -> None:
        """🔄 AGREGAR NIVEL A LA PILA CONVERSACIONAL"""
        try:
            level = ContextLevel(
                query=query,
                data=result_data.get("data", []),
                row_count=result_data.get("row_count", 0),
                awaiting_type=awaiting_type,
                timestamp=datetime.now().strftime("%H:%M:%S"),
                sql_query=result_data.get("sql_query", ""),
                message=result_data.get("message", ""),
                context_info=context_info
            )
            
            self.conversation_stack.append(level)
            self.awaiting_continuation = True
            
            self.logger.info(f"📚 CONTEXTO AGREGADO: Nivel {len(self.conversation_stack)}")
            self.logger.info(f"   ├── Tipo esperado: {awaiting_type}")
            self.logger.info(f"   ├── Datos: {level.row_count} elementos")
            self.logger.info(f"   └── Query: '{query[:50]}...'")
            
        except Exception as e:
            self.logger.error(f"Error agregando contexto: {e}")
    
    def analyze_context(self) -> ContextAnalysis:
        """🔍 ANALIZAR CONTEXTO DISPONIBLE"""
        try:
            if not self.conversation_stack:
                return ContextAnalysis(
                    has_context=False,
                    available_fields=[],
                    data_count=0,
                    data_type="empty",
                    sample_data={},
                    context_quality="none"
                )
            
            # Obtener el último nivel con datos
            latest_level = None
            for level in reversed(self.conversation_stack):
                if level.data and len(level.data) > 0:
                    latest_level = level
                    break
            
            if not latest_level:
                return ContextAnalysis(
                    has_context=True,
                    available_fields=[],
                    data_count=0,
                    data_type="empty",
                    sample_data={},
                    context_quality="minimal"
                )
            
            # Analizar datos disponibles
            data = latest_level.data
            first_item = data[0] if isinstance(data, list) and len(data) > 0 else {}
            available_fields = list(first_item.keys()) if isinstance(first_item, dict) else []
            
            # Determinar calidad del contexto
            context_quality = self._assess_context_quality(available_fields, len(data))
            
            # Determinar tipo de datos
            data_type = "list" if len(data) > 1 else "single" if len(data) == 1 else "empty"
            
            return ContextAnalysis(
                has_context=True,
                available_fields=available_fields,
                data_count=len(data),
                data_type=data_type,
                sample_data=first_item,
                context_quality=context_quality
            )
            
        except Exception as e:
            self.logger.error(f"Error analizando contexto: {e}")
            return ContextAnalysis(
                has_context=False,
                available_fields=[],
                data_count=0,
                data_type="empty",
                sample_data={},
                context_quality="none"
            )
    
    def analyze_requirements(self, user_query: str, query_type: str = "unknown") -> RequirementAnalysis:
        """🎯 ANALIZAR REQUERIMIENTOS DE LA CONSULTA"""
        try:
            user_lower = user_query.lower()
            
            # Campos básicos siempre necesarios
            basic_fields = ['nombre', 'curp']
            required_fields = basic_fields.copy()
            
            # Detectar nivel de detalle requerido
            detail_level = "basic"
            specific_requests = []
            
            # Detectar solicitudes de detalles completos
            detail_keywords = ['detalles', 'información completa', 'todo', 'completo', 'datos completos']
            if any(keyword in user_lower for keyword in detail_keywords):
                required_fields.extend(['grado', 'grupo', 'turno', 'matricula', 'fecha_nacimiento'])
                detail_level = "complete"
                specific_requests.append("detalles_completos")
            
            # Detectar solicitudes de constancias
            constancia_keywords = ['constancia', 'certificado', 'genera', 'generar', 'crear', 'documento']
            if any(keyword in user_lower for keyword in constancia_keywords):
                required_fields.extend(['grado', 'grupo', 'turno', 'matricula', 'id'])
                detail_level = "constancia"
                specific_requests.append("constancia")
                
                # Si es constancia de calificaciones
                if 'calificaciones' in user_lower:
                    required_fields.append('calificaciones')
                    specific_requests.append("calificaciones")
            
            # Detectar solicitudes específicas de campos
            field_requests = {
                'curp': ['curp'],
                'matricula': ['matricula', 'matrícula'],
                'grado': ['grado'],
                'grupo': ['grupo'],
                'turno': ['turno'],
                'calificaciones': ['calificaciones', 'notas', 'calificación']
            }
            
            for field, keywords in field_requests.items():
                if any(keyword in user_lower for keyword in keywords):
                    if field not in required_fields:
                        required_fields.append(field)
                    specific_requests.append(f"campo_{field}")
            
            # Determinar si necesita búsqueda en BD
            needs_database_search = detail_level in ["complete", "constancia"] or len(specific_requests) > 1
            
            return RequirementAnalysis(
                required_fields=required_fields,
                detail_level=detail_level,
                needs_database_search=needs_database_search,
                query_type=query_type,
                specific_requests=specific_requests
            )
            
        except Exception as e:
            self.logger.error(f"Error analizando requerimientos: {e}")
            return RequirementAnalysis(
                required_fields=['nombre', 'curp'],
                detail_level="basic",
                needs_database_search=False,
                query_type="unknown",
                specific_requests=[]
            )
    
    def make_intelligent_decision(self, user_query: str, context_analysis: ContextAnalysis, 
                                requirement_analysis: RequirementAnalysis) -> IntelligentDecision:
        """🧠 TOMAR DECISIÓN INTELIGENTE SOBRE CÓMO PROCEDER"""
        try:
            # Si no hay contexto, siempre nueva búsqueda
            if not context_analysis.has_context:
                return IntelligentDecision(
                    action="new_query",
                    reason="No hay contexto disponible",
                    confidence=1.0,
                    recommended_fields=requirement_analysis.required_fields,
                    fallback_action="expand_search"
                )
            
            available_fields = set(context_analysis.available_fields)
            required_fields = set(requirement_analysis.required_fields)
            missing_fields = required_fields - available_fields
            
            # DECISIÓN BASADA EN NIVEL DE DETALLE
            detail_level = requirement_analysis.detail_level
            
            if detail_level == "basic":
                # Para consultas básicas, si tengo nombre y CURP es suficiente
                if "nombre" in available_fields and ("curp" in available_fields or len(missing_fields) <= 1):
                    return IntelligentDecision(
                        action="use_context",
                        reason=f"Información suficiente para consulta básica. Campos: {list(available_fields)}",
                        confidence=0.9,
                        recommended_fields=list(available_fields),
                        fallback_action="expand_search"
                    )
            
            elif detail_level == "complete":
                # Para detalles completos, evaluar campos faltantes
                important_fields = {"grado", "grupo", "turno", "matricula"}
                missing_important = important_fields - available_fields
                
                if len(missing_important) > 2:
                    return IntelligentDecision(
                        action="expand_search",
                        reason=f"Faltan campos importantes: {list(missing_important)}",
                        confidence=0.95,
                        recommended_fields=requirement_analysis.required_fields,
                        fallback_action="use_context"
                    )
                else:
                    return IntelligentDecision(
                        action="use_context",
                        reason=f"Suficientes campos disponibles. Solo faltan: {list(missing_fields)}",
                        confidence=0.8,
                        recommended_fields=list(available_fields),
                        fallback_action="expand_search"
                    )
            
            elif detail_level == "constancia":
                # Para constancias, siempre expandir para datos verificados
                return IntelligentDecision(
                    action="expand_search",
                    reason="Constancias requieren datos completos y verificados",
                    confidence=1.0,
                    recommended_fields=requirement_analysis.required_fields,
                    fallback_action="use_context"
                )
            
            # DECISIÓN POR DEFECTO
            if len(missing_fields) <= 2:
                return IntelligentDecision(
                    action="use_context",
                    reason=f"Solo faltan {len(missing_fields)} campos: {list(missing_fields)}",
                    confidence=0.7,
                    recommended_fields=list(available_fields),
                    fallback_action="expand_search"
                )
            else:
                return IntelligentDecision(
                    action="expand_search",
                    reason=f"Faltan demasiados campos: {list(missing_fields)}",
                    confidence=0.8,
                    recommended_fields=requirement_analysis.required_fields,
                    fallback_action="use_context"
                )
                
        except Exception as e:
            self.logger.error(f"Error en decisión inteligente: {e}")
            return IntelligentDecision(
                action="use_context",
                reason="Error en análisis, usando contexto por defecto",
                confidence=0.5,
                recommended_fields=[],
                fallback_action="expand_search"
            )
    
    def _assess_context_quality(self, available_fields: List[str], data_count: int) -> str:
        """📊 EVALUAR CALIDAD DEL CONTEXTO"""
        if not available_fields:
            return "none"
        
        # Campos importantes para alumnos
        important_fields = {'nombre', 'curp', 'grado', 'grupo', 'turno', 'matricula'}
        available_important = set(available_fields) & important_fields
        
        if len(available_important) >= 5:
            return "complete"
        elif len(available_important) >= 3:
            return "partial"
        elif len(available_important) >= 1:
            return "minimal"
        else:
            return "none"
    
    def clear_context(self) -> None:
        """🧹 LIMPIAR CONTEXTO"""
        stack_size = len(self.conversation_stack)
        self.conversation_stack = []
        self.awaiting_continuation = False
        self.last_decision = None
        
        self.logger.info(f"🧹 CONTEXTO LIMPIADO (tenía {stack_size} niveles)")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """📊 OBTENER RESUMEN DEL CONTEXTO"""
        return {
            "levels": len(self.conversation_stack),
            "awaiting_continuation": self.awaiting_continuation,
            "last_decision": self.last_decision.action if self.last_decision else None,
            "stats": self.context_usage_stats,
            "context_quality": self.analyze_context().context_quality
        }
