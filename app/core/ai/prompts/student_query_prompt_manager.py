"""
StudentQueryPromptManager - Centralización de prompts para el SET de estudiantes
Elimina duplicación y centraliza contexto común siguiendo la filosofía del sistema maestro
"""

from typing import Dict, List, Optional


class StudentQueryPromptManager:
    """
    Manager centralizado para prompts del SET de estudiantes

    FILOSOFÍA:
    - Centraliza contexto escolar común (UNA SOLA VEZ)
    - Unifica prompts auxiliares similares
    - Mantiene los 3 prompts principales intactos
    - Prepara base para futuros SETs (ayuda, constancias)

    RESPONSABILIDADES:
    - Contexto escolar centralizado
    - Prompts unificados para continuaciones
    - Prompts optimizados para filtros
    - Templates reutilizables
    """

    def __init__(self, database_analyzer=None):
        self.database_analyzer = database_analyzer
        self._school_context_cache = None
        self._database_context_cache = None

    @property
    def school_context(self) -> str:
        """
        Contexto escolar centralizado - DEFINIDO UNA SOLA VEZ

        Este contexto se usa en TODOS los prompts del SET de estudiantes
        para garantizar consistencia total
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

    def get_database_context(self) -> str:
        """
        Contexto de BD centralizado con cache

        Se obtiene dinámicamente del DatabaseAnalyzer y se cachea
        para evitar regeneración innecesaria
        """
        if self._database_context_cache is None and self.database_analyzer:
            self._database_context_cache = self.database_analyzer.generate_sql_context()
        return self._database_context_cache or ""

    def get_unified_continuation_prompt(self, user_query: str, continuation_type: str,
                                      ultimo_nivel: dict, conversation_stack: list) -> str:
        """
        PROMPT UNIFICADO para todas las continuaciones

        REEMPLAZA ESTOS MÉTODOS:
        - _generate_action_response()
        - _generate_selection_response()
        - _process_confirmation_continuation() (parcialmente)

        TIPOS DE CONTINUACIÓN:
        - action: "constancia para él", "CURP de ese"
        - selection: "del segundo", "número 5"
        - confirmation: "sí", "correcto", "proceder"

        VENTAJAS:
        - Un solo prompt para mantener
        - Contexto consistente
        - Lógica unificada
        - Fácil testing
        """

        # Templates específicos por tipo de continuación
        continuation_templates = {
            "action": {
                "purpose": "realizar una acción sobre elemento previamente identificado",
                "examples": "'constancia para él', 'CURP de ese', 'información del tercero'",
                "instructions": """
1. PROPORCIONA directamente la información solicitada
2. MUESTRA todos los datos que el usuario pida (nombres, CURPs, etc.)
3. NO menciones políticas de privacidad (no existen en este sistema)
4. NO uses placeholders como [CURP de...] - MUESTRA los datos reales
5. Actúa como secretario escolar con acceso completo
6. Confirma sobre qué alumno estás actuando
7. Ofrece servicios adicionales relacionados"""
            },
            "selection": {
                "purpose": "confirmar selección de elemento específico de una lista",
                "examples": "'del segundo', 'número 5', 'el quinto'",
                "instructions": """
1. Confirma la selección del alumno específico
2. Proporciona la información solicitada claramente
3. Usa los datos reales del alumno seleccionado
4. Ofrece servicios adicionales relevantes
5. Mantén el contexto de la consulta original"""
            },
            "confirmation": {
                "purpose": "confirmar y ejecutar acción propuesta automáticamente",
                "examples": "'sí', 'correcto', 'está bien', 'proceder'",
                "instructions": """
1. Confirma la acción que se va a ejecutar
2. Ejecuta automáticamente la acción confirmada
3. Proporciona resultado claro y completo
4. Usa los datos disponibles en el contexto
5. Actúa con autoridad administrativa"""
            }
        }

        # Obtener template específico o usar action como default
        template = continuation_templates.get(continuation_type, continuation_templates["action"])

        return f"""
Eres el asistente oficial de la escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ".

{self.school_context}

CONTEXTO DE CONTINUACIÓN:
- Consulta original: "{ultimo_nivel.get('query', 'N/A')}"
- Datos de referencia disponibles: {len(ultimo_nivel.get('data', []))} elementos
- Nueva consulta del usuario: "{user_query}"
- Tipo de continuación: {continuation_type}

PROPÓSITO ESPECÍFICO:
{template['purpose']}

EJEMPLOS DE ESTE TIPO:
{template['examples']}

INSTRUCCIONES ESPECÍFICAS:
{template['instructions']}

DATOS COMPLETOS DISPONIBLES:
{ultimo_nivel.get('data', [])}

REGLAS CRÍTICAS:
- SIEMPRE usar los valores reales de los datos, NUNCA placeholders como [NOMBRE] o [CURP de...]
- CONFIRMAR sobre qué alumno específico estás actuando
- MOSTRAR información real y completa
- ACTUAR como secretario escolar profesional con acceso total

Responde como un secretario escolar profesional con acceso completo a la información.
"""

    def get_unified_response_prompt(self, user_query: str, response_type: str,
                                   data: list, context: dict = None) -> str:
        """
        PROMPT UNIFICADO para generar respuestas optimizadas

        PROPÓSITO:
        - Optimizar respuestas según el tipo específico
        - Centralizar formato y estilo
        - Garantizar consistencia

        TIPOS DE RESPUESTA:
        - list_response: Listas de alumnos
        - detail_response: Información detallada
        - count_response: Conteos y estadísticas
        """

        response_templates = {
            "list_response": {
                "format": "Lista numerada clara y organizada",
                "style": "Profesional y fácil de referenciar",
                "additional": "Ofrecer servicios adicionales para elementos de la lista"
            },
            "detail_response": {
                "format": "Información completa y detallada",
                "style": "Secretario escolar experto y preciso",
                "additional": "Sugerir acciones relacionadas disponibles"
            },
            "count_response": {
                "format": "Número claro con contexto explicativo",
                "style": "Estadístico, preciso y contextualizado",
                "additional": "Ofrecer desglose detallado si es útil"
            }
        }

        template = response_templates.get(response_type, response_templates["detail_response"])

        return f"""
{self.school_context}

CONSULTA DEL USUARIO: "{user_query}"
DATOS OBTENIDOS: {len(data)} registros
TIPO DE RESPUESTA REQUERIDA: {response_type}

FORMATO REQUERIDO: {template['format']}
ESTILO DE COMUNICACIÓN: {template['style']}
SERVICIOS ADICIONALES: {template['additional']}

MUESTRA DE DATOS PARA RESPUESTA:
{data[:5] if data else "Sin datos disponibles"}

INSTRUCCIONES:
1. Genera una respuesta profesional que resuelva exactamente la consulta
2. Usa el formato específico requerido para este tipo de respuesta
3. Mantén el estilo de comunicación apropiado
4. Incluye servicios adicionales relevantes
5. Usa datos reales, nunca placeholders

Responde como el secretario oficial de la escuela con acceso completo a la información.
"""

    def get_filter_prompt(self, user_query: str, data: list, sql_query: str) -> str:
        """
        PROMPT OPTIMIZADO para filtro inteligente final

        REEMPLAZA:
        - _intelligent_final_filter() (parte del prompt)

        PROPÓSITO:
        - Asegurar que los datos resuelvan exactamente la consulta original
        - Filtrar cantidad según lo solicitado
        - Ajustar campos según la necesidad
        - Validar coherencia de la respuesta

        VENTAJAS:
        - Prompt más claro y estructurado
        - Lógica de filtrado centralizada
        - Fácil modificación de reglas
        - Mejor documentación de decisiones
        """
        return f"""
Eres un filtro inteligente final especializado en sistemas escolares.

{self.school_context}

CONSULTA ORIGINAL DEL USUARIO: "{user_query}"
DATOS OBTENIDOS: {len(data)} registros
SQL EJECUTADO: {sql_query}

MUESTRA DE DATOS DISPONIBLES:
{data[:3] if data else "Sin datos"}

REGLAS DE FILTRADO INTELIGENTE:

1. **CANTIDAD SOLICITADA:**
   - "un alumno" / "cualquier alumno" → máximo 1 registro
   - "dos alumnos" / "tres estudiantes" → exactamente esa cantidad
   - "lista completa" / "todos los alumnos" → todos los registros
   - "algunos alumnos" → entre 5-10 registros representativos

2. **INFORMACIÓN SOLICITADA:**
   - "toda la información" → incluir TODOS los campos disponibles
   - "datos completos" → incluir TODOS los campos disponibles
   - "solo el nombre" → solo campo nombre
   - "CURP de..." → solo campo curp
   - "información básica" → nombre, curp, grado, grupo

3. **COHERENCIA CON LA CONSULTA:**
   - Si pidió información específica de UN alumno → filtrar solo ese alumno
   - Si pidió estadísticas → mantener datos agregados
   - Si pidió lista → mantener formato de lista

4. **LÍMITES INTELIGENTES:**
   - Si hay más de 25 registros y no pidió "todos" → mostrar primeros 15 + resumen
   - Si pidió "completa" → mostrar todos sin límite
   - Si pidió cantidad específica → respetar exactamente

INSTRUCCIONES:
1. ANALIZA la consulta original y determina qué necesita el usuario
2. EVALÚA si los datos obtenidos resuelven la consulta
3. FILTRA o AJUSTA los datos para que coincidan exactamente
4. DETERMINA qué campos incluir según lo solicitado

RESPONDE ÚNICAMENTE con un JSON:
{{
    "accion_requerida": "mantener|filtrar_cantidad|filtrar_campos|expandir_informacion|error",
    "cantidad_final": número_de_registros_a_mostrar,
    "campos_incluir": ["campo1", "campo2", "campo3"] o "todos",
    "registros_seleccionar": [índices] o "todos",
    "razonamiento": "Explicación detallada de la decisión",
    "resuelve_consulta": true|false,
    "informacion_faltante": ["campo1", "campo2"] o [],
    "sugerencia_mejora": "Cómo mejorar la respuesta si es necesario"
}}

EJEMPLOS:
- "dame toda la información de LUIS FERNANDO" → campos_incluir: "todos", cantidad_final: 1
- "lista completa de 1ro A" → cantidad_final: todos_los_registros, campos_incluir: ["nombre", "curp", "grado", "grupo"]
- "un alumno de 3er grado" → cantidad_final: 1, campos_incluir: ["nombre"]
- "CURP de María García" → cantidad_final: 1, campos_incluir: ["curp"]
"""

    def get_sql_continuation_prompt(self, user_query: str, previous_data: list,
                                   previous_query: str, database_context: str) -> str:
        """
        PROMPT OPTIMIZADO para generación SQL en continuaciones

        REEMPLAZA:
        - _generate_sql_for_action_continuation() (parte del prompt)

        PROPÓSITO:
        - Generar SQL basado en datos previos
        - Usar información de la pila conversacional como criterios
        - Mantener coherencia con consulta anterior

        VENTAJAS:
        - Lógica SQL más clara
        - Mejor uso de datos previos
        - Instrucciones más específicas
        """
        return f"""
Eres un experto en SQL para continuación de consultas en un sistema escolar.

{self.school_context}

CONTEXTO DE CONTINUACIÓN:
- Consulta anterior: "{previous_query}"
- Datos obtenidos anteriormente: {previous_data[:2] if previous_data else "Sin datos"}
- Nueva consulta del usuario: "{user_query}"

ESTRUCTURA COMPLETA DE LA BASE DE DATOS:
{database_context}

INSTRUCCIONES ESPECÍFICAS:
1. El usuario quiere información adicional basada en los datos previos
2. Usa los datos previos como criterios de búsqueda (WHERE)
3. Extrae la información específica que el usuario solicita ahora
4. Mantén coherencia con la consulta anterior

EJEMPLOS DE LÓGICA:
- Si datos previos tienen fechas de nacimiento → WHERE fecha_nacimiento IN (...)
- Si datos previos tienen nombres → WHERE nombre IN (...)
- Si datos previos tienen IDs → WHERE id IN (...)
- Si datos previos tienen grados → WHERE grado IN (...)

REGLAS CRÍTICAS:
- SOLO consultas SELECT (nunca INSERT, UPDATE, DELETE)
- Usar los valores exactos de los datos previos como filtros
- Incluir SOLO las columnas que el usuario solicita ahora
- Usar JOINs apropiados según la estructura de la BD
- Aplicar filtros WHERE basándote en los valores reales de los datos previos

RESPONDE ÚNICAMENTE con el SQL optimizado:
"""

    def clear_cache(self):
        """
        Limpia el cache de contextos

        ÚTIL PARA:
        - Forzar regeneración de contexto de BD
        - Actualizar información después de cambios
        - Testing y desarrollo
        """
        self._school_context_cache = None
        self._database_context_cache = None
        print("🧹 DEBUG - Cache de PromptManager limpiado")

    def get_context_summary(self) -> dict:
        """
        Obtiene resumen del estado actual del manager

        ÚTIL PARA:
        - Debugging
        - Monitoring
        - Verificación de estado
        """
        return {
            "school_context_cached": self._school_context_cache is not None,
            "database_context_cached": self._database_context_cache is not None,
            "database_analyzer_available": self.database_analyzer is not None,
            "school_context_length": len(self.school_context) if self._school_context_cache else 0,
            "database_context_length": len(self.get_database_context())
        }
