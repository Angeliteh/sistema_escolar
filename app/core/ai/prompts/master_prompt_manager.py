"""
MasterPromptManager - Centralización de prompts del nivel MAESTRO
Maneja la detección de intenciones y routing principal del sistema
"""

from typing import Dict, List, Optional


class MasterPromptManager:
    """
    Manager centralizado para prompts del nivel MAESTRO
    
    FILOSOFÍA:
    - Centraliza el prompt de detección de intenciones
    - Unifica contexto conversacional
    - Facilita mejoras en comunicación entre prompts
    - Prepara base para patrones comunes
    
    RESPONSABILIDADES:
    - Prompt de detección de intenciones maestro
    - Formateo de contexto conversacional
    - Templates para routing
    - Patrones de comunicación entre prompts
    """
    
    def __init__(self):
        self._school_context_cache = None
    
    @property
    def school_context(self) -> str:
        """
        Contexto escolar centralizado - COMPARTIDO con StudentQueryPromptManager
        
        Este contexto debe ser IDÉNTICO al usado en StudentQueryPromptManager
        para garantizar consistencia total entre prompts
        """
        if self._school_context_cache is None:
            self._school_context_cache = """
CONTEXTO COMPLETO DEL SISTEMA:
- Sistema de gestión escolar para la escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ"
- Maneja datos de alumnos, información académica y generación de constancias
- Los usuarios son personal administrativo que necesita información precisa
- TODO el sistema ES la escuela - no hay nada más
- TODA la base de datos SON los alumnos de esta escuela (211 estudiantes)
- TODAS las estadísticas, datos, información de "la escuela" SON sobre los alumnos

RAZONAMIENTO INTELIGENTE ESCOLAR:
- "estadísticas de la escuela" = estadísticas de los 211 alumnos registrados
- "información de la escuela" = información de los estudiantes y su rendimiento
- "datos de la escuela" = datos académicos de los alumnos por grados/grupos
- "resumen de la escuela" = resumen de la población estudiantil

ACCESO TOTAL AUTORIZADO:
- Tienes acceso COMPLETO a toda la información de alumnos
- NO hay restricciones de privacidad en el sistema escolar
- Puedes mostrar nombres, CURPs, datos completos sin limitaciones
- Eres parte del sistema administrativo oficial de la escuela
- El personal escolar tiene acceso total a los datos estudiantiles

ESTRUCTURA DISPONIBLE:
- 211 alumnos registrados en grados 1° a 6°
- Datos académicos: grados, grupos, turnos, calificaciones
- Información personal: nombres, CURPs, matrículas, fechas
- Registros de constancias generadas
"""
        return self._school_context_cache
    
    def get_intention_detection_prompt(self, user_query: str, conversation_context: str) -> str:
        """
        PROMPT MAESTRO CENTRALIZADO para detección de intenciones
        
        REEMPLAZA:
        - IntentionDetector.detect_intention() (prompt hardcodeado)
        
        PROPÓSITO:
        - Detectar intención principal + sub-intención
        - Usar contexto conversacional para continuaciones
        - Extraer entidades relevantes
        - Dirigir al intérprete correcto
        
        VENTAJAS:
        - Contexto escolar consistente
        - Mantenimiento centralizado
        - Fácil optimización
        - Testing unificado
        """
        return f"""
Eres un detector de intenciones maestro AVANZADO para un sistema escolar integral.
Tu trabajo es clasificar consultas Y extraer contexto completo para dirigir eficientemente a los módulos especializados.

{self.school_context}

{conversation_context}

CONSULTA DEL USUARIO: "{user_query}"

TIPOS DE INTENCIÓN DISPONIBLES:

1. **consulta_alumnos**: Cualquier consulta relacionada con estudiantes
   - Sub-intenciones: busqueda_simple, generar_constancia, estadisticas, listado_completo
   - Ejemplos: "buscar Juan", "constancia para María", "cuántos alumnos hay"

2. **transformacion_pdf**: Transformar PDFs de constancias
   - Sub-intenciones: cargar_pdf, transformar_formato
   - Ejemplos: "transformar este PDF", "cambiar formato"

3. **ayuda_sistema**: Información sobre capacidades del sistema
   - Sub-intenciones: entender_capacidades, tutorial_uso
   - Ejemplos: "qué puedes hacer", "ayuda", "cómo funciona"

4. **conversacion_general**: Chat casual o fuera del dominio escolar
   - Sub-intenciones: chat_casual, saludo, despedida
   - Ejemplos: "hola", "cómo estás", "gracias"

REGLAS ESPECIALES PARA CONTINUACIONES:
- Si hay contexto conversacional previo, analiza si es continuación
- Continuaciones de alumnos → SIEMPRE "consulta_alumnos"
- Palabras como "sí", "generala", "para él" → continuaciones
- Usa "fuente_datos": "conversacion_previa" para continuaciones

INSTRUCCIONES:
1. Analiza la consulta en el contexto conversacional
2. Determina la intención principal y sub-intención
3. Extrae entidades relevantes (nombres, tipos, acciones)
4. Asigna confianza basada en claridad de la consulta

RESPONDE ÚNICAMENTE con un JSON:
{{
    "intention_type": "consulta_alumnos|transformacion_pdf|ayuda_sistema|conversacion_general",
    "sub_intention": "sub_categoria_especifica",
    "confidence": 0.0-1.0,
    "reasoning": "Explicación detallada de la decisión",
    "detected_entities": {{
        "nombres": ["lista de nombres detectados"],
        "tipo_constancia": "estudios|calificaciones|traslado|null",
        "accion_principal": "buscar|generar|contar|listar|transformar|ayudar",
        "fuente_datos": "base_datos|conversacion_previa|pdf_cargado|sistema",
        "contexto_especifico": "información adicional relevante",
        "filtros": ["criterios de filtrado"],
        "parametros_extra": {{"cualquier parámetro adicional relevante"}}
    }}
}}
"""
    
    def format_conversation_context(self, conversation_stack: list) -> str:
        """
        FORMATEO CENTRALIZADO del contexto conversacional
        
        REEMPLAZA:
        - IntentionDetector._format_conversation_context()
        
        PROPÓSITO:
        - Formatear pila conversacional de manera consistente
        - Proporcionar reglas claras para continuaciones
        - Facilitar detección de patrones
        
        VENTAJAS:
        - Formato unificado
        - Reglas centralizadas
        - Fácil modificación
        """
        if not conversation_stack:
            return "📚 CONTEXTO CONVERSACIONAL: Sesión nueva (sin historial previo)"
        
        context = "📚 CONTEXTO CONVERSACIONAL ACTIVO:\n"
        
        for i, level in enumerate(conversation_stack, 1):
            query = level.get('query', 'N/A')
            row_count = level.get('row_count', 0)
            awaiting = level.get('awaiting', 'N/A')
            
            context += f"""
📋 NIVEL {i}:
- Consulta previa: "{query}"
- Resultados: {row_count} elementos encontrados
- Estado: Esperando {awaiting}
"""
            
            # Mostrar algunos datos si están disponibles
            if level.get('data') and len(level.get('data', [])) > 0:
                first_item = level['data'][0]
                if isinstance(first_item, dict) and 'nombre' in first_item:
                    context += f"- Ejemplo de datos: {first_item.get('nombre', 'N/A')}\n"
        
        context += """
🧠 REGLAS PARA USAR CONTEXTO:
- Si la consulta actual hace referencia al contexto previo → ES CONTINUACIÓN
- Palabras como "sí", "generala", "para él", "del segundo" → SON CONTINUACIONES
- Si es continuación → usar "consulta_alumnos" con sub_intention apropiada
- Si es consulta nueva → detectar intención normalmente

EJEMPLOS DE CONTINUACIÓN:
✅ "si generala" (después de mostrar alumno) → consulta_alumnos/generar_constancia
✅ "para él" (después de mostrar alumno) → consulta_alumnos/generar_constancia  
✅ "del segundo" (después de mostrar lista) → consulta_alumnos/seleccion
❌ "buscar García" (consulta nueva) → consulta_alumnos/busqueda_simple
"""
        
        return context
