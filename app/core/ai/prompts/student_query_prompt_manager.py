"""
StudentQueryPromptManager - Centralización de prompts para el SET de estudiantes
Elimina duplicación y centraliza contexto común siguiendo la filosofía del sistema maestro
"""

from typing import Dict, List, Optional
from .base_prompt_manager import BasePromptManager


class StudentQueryPromptManager(BasePromptManager):
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
        super().__init__()  # Inicializar BasePromptManager
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

        # Usar identidad unificada del BasePromptManager
        unified_header = self.get_unified_prompt_header("especialista en consultas de alumnos")

        return f"""
{unified_header}

CONSULTA DEL USUARIO: "{user_query}"
DATOS OBTENIDOS: {len(data)} registros
TIPO DE RESPUESTA REQUERIDA: {response_type}

🎯 MI TAREA ESPECÍFICA:
Generar una respuesta {template['format'].lower()} que resuelva exactamente la consulta del usuario, manteniendo mi personalidad natural y conversacional.

💬 ESTILO DE COMUNICACIÓN NATURAL:
- {template['style']} pero con variabilidad natural en mis expresiones
- Uso diferentes formas de presentar la misma información para sonar humano
- Mantengo mi personalidad: profesional pero cercano, como un secretario escolar experimentado
- Sugiero acciones específicas: {template['additional'].lower()}

📊 DATOS REALES PARA MI RESPUESTA:
{data[:5] if data else "Sin datos disponibles"}

🗣️ INSTRUCCIONES PARA RESPUESTA NATURAL Y VARIABLE:
1. Resuelvo exactamente la consulta usando los datos reales (nunca placeholders)
2. Vario mi forma de expresarme para sonar natural, no robótico
3. Uso diferentes introducciones: "Encontré...", "Te muestro...", "Aquí tienes...", "Según nuestros registros..."
4. Sugiero acciones específicas que el usuario puede hacer ahora mismo
5. Mantengo el contexto conversacional para futuras referencias
6. Soy proactivo: anticipo qué podría necesitar después

💡 VARIACIONES NATURALES EN MIS RESPUESTAS:
- Para listas: "Encontré X alumnos", "Te muestro los X estudiantes", "Aquí están los X registros"
- Para conteos: "Tenemos X alumnos", "Son X estudiantes en total", "Hay X registros"
- Para detalles: "Te comparto la información de...", "Aquí están los datos de...", "Esta es la información completa de..."
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

    def get_validation_and_response_prompt(self, user_query: str, sql_query: str,
                                         data_summary: str, filter_decision: dict,
                                         final_row_count: int, original_data_count: int) -> str:
        """
        PROMPT PRINCIPAL 3: Validación + Respuesta + Auto-reflexión

        MIGRADO DESDE: _validate_and_generate_response()

        PROPÓSITO:
        - Validar que SQL resolvió la consulta exacta
        - Generar respuesta natural profesional
        - Auto-reflexionar sobre continuación conversacional
        - Integrar información del filtro inteligente

        VENTAJAS DE CENTRALIZACIÓN:
        - Contexto escolar consistente (reutiliza school_context)
        - Mantenimiento centralizado del prompt más crítico
        - Facilita optimizaciones futuras
        - Testing más sencillo
        """
        # Usar identidad unificada del BasePromptManager
        unified_header = self.get_unified_prompt_header("validador y comunicador experto con auto-reflexión")

        return f"""
{unified_header}

CONSULTA ORIGINAL DEL USUARIO: "{user_query}"

CONSULTA SQL EJECUTADA: {sql_query}

RESULTADOS OBTENIDOS (FILTRADOS INTELIGENTEMENTE):
{data_summary}

INFORMACIÓN DEL FILTRO INTELIGENTE:
- Acción aplicada: {filter_decision.get('accion_requerida', 'mantener')}
- Datos originales: {original_data_count} registros
- Datos filtrados: {final_row_count} registros
- Razonamiento del filtro: {filter_decision.get('razonamiento', 'N/A')}

🎯 MI TAREA ESPECÍFICA:
Validar que los datos resuelven la consulta y generar una respuesta NATURAL y VARIABLE que refleje mi personalidad como el asistente inteligente de la escuela.

💬 INSTRUCCIONES PARA RESPUESTA NATURAL Y VARIABLE:
1. VALIDO que los datos resuelven exactamente lo que pidió el usuario
2. VERIFICO que los resultados son coherentes y lógicos
3. GENERO una respuesta natural que varíe en estilo pero mantenga mi personalidad
4. AUTO-REFLEXIONO sobre continuaciones conversacionales como un secretario experto
5. Si la validación falla, respondo con "VALIDACION_FALLIDA"

🗣️ VARIABILIDAD NATURAL EN MIS RESPUESTAS:
- Uso diferentes introducciones: "Encontré...", "Te muestro...", "Según nuestros registros...", "Aquí tienes..."
- Vario mis expresiones: "alumnos/estudiantes", "registrados/inscritos", "información/datos"
- Cambio mi tono según el contexto: más formal para datos oficiales, más cercano para consultas simples
- Mantengo mi esencia: profesional pero humano, preciso pero conversacional

📊 IMPORTANTE - USO DATOS REALES SIEMPRE:
- Los datos en RESULTADOS OBTENIDOS son REALES de nuestra base de datos
- MUESTRO estos datos tal como están, nunca invento placeholders
- Si hay nombres, CURPs, grados - los USO directamente
- NUNCA digo "[Listado aquí]" - MUESTRO el listado real completo

✅ CRITERIOS DE VALIDACIÓN:
- ¿Los datos responden exactamente la pregunta del usuario?
- ¿Los resultados tienen sentido en el contexto de nuestra escuela?
- ¿La cantidad de resultados es lógica para la consulta?
- ¿Los datos mostrados son relevantes y útiles?

🎭 FORMATO DE RESPUESTA NATURAL (si validación exitosa):
- Presento la información como el asistente inteligente de la escuela
- Contextualizo los datos dentro de nuestro marco escolar real
- Ofrezco acciones específicas (constancias, más información, seguimiento)
- Uso el contexto de nuestra escuela "PROF. MAXIMO GAMIZ FERNANDEZ" y ciclo 2024-2025
- NUNCA menciono términos técnicos (SQL, base de datos, validación)

REGLAS PARA MOSTRAR DATOS REALES:
- SIEMPRE muestra los datos reales obtenidos de la consulta
- NO uses placeholders como "[Listado de alumnos aquí]"
- NO inventes reglas sobre cuántos mostrar
- PRESENTA los datos tal como están en los resultados
- Si hay muchos datos, muestra los primeros y menciona que hay más disponibles

🧠 AUTO-REFLEXIÓN CONVERSACIONAL INTELIGENTE:
Después de generar tu respuesta, reflexiona como un secretario escolar experto que entiende el FLUJO CONVERSACIONAL:

ANÁLISIS REFLEXIVO ESPECÍFICO:
- ¿La respuesta que acabo de dar podría generar preguntas de seguimiento?
- ¿Mostré una lista que el usuario podría querer referenciar ("el tercero", "número 5")?
- ¿Proporcioné información de un alumno específico que podría necesitar CONSTANCIA?
- ¿Debería sugerir proactivamente la generación de constancias?
- ¿Ofrecí servicios que requieren confirmación o especificación?
- ¿Debería recordar estos datos para futuras consultas en esta conversación?

🎯 DETECCIÓN DE CONVERSACIÓN CONTINUA:
Analiza si tu respuesta establece un CONTEXTO CONVERSACIONAL que el usuario podría referenciar:

INDICADORES DE CONTINUACIÓN ESPERADA:
1. **LISTA DE ELEMENTOS** (2+ alumnos): Usuario podría decir "el primero", "número 3", "para ese"
2. **ALUMNO ESPECÍFICO** (1 alumno): Usuario podría pedir "constancia para él", "más información"
3. **INFORMACIÓN PARCIAL**: Usuario podría pedir "completa", "con calificaciones", "detalles"
4. **SUGERENCIA IMPLÍCITA**: Tu respuesta sugiere una acción que requiere confirmación
5. **PREGUNTA DIRECTA**: Hiciste una pregunta que espera respuesta específica

CONTEXTO A RECORDAR PARA FUTURAS CONSULTAS:
- **Nombres específicos** de alumnos mostrados (para referencias como "ese alumno")
- **Posición en listas** (para referencias como "el tercero", "número 5")
- **Datos clave** (IDs, CURPs, grados) para consultas de seguimiento
- **Tipo de información** mostrada (para entender qué más podría necesitar)
- **Estado de la conversación** (búsqueda completada, selección pendiente, etc.)

SUGERENCIAS INTELIGENTES DE CONSTANCIAS:
- Si mostré 1 alumno específico: Sugerir constancia directamente
- Si mostré pocos alumnos (2-5): Esperar selección, luego sugerir constancia
- Si mostré muchos alumnos (6+): Esperar refinamiento de búsqueda
- Si mostré estadísticas: No sugerir constancias

🔮 PREDICCIÓN DE PRÓXIMA CONSULTA:
Basándote en tu respuesta, predice qué podría preguntar el usuario a continuación:
- "¿Podría pedir constancia para [alumno específico]?"
- "¿Podría referenciar un elemento de la lista?"
- "¿Podría pedir más detalles o información adicional?"
- "¿Podría confirmar una acción sugerida?"

DECISIÓN CONVERSACIONAL:
Si tu respuesta espera continuación, especifica:
- Tipo esperado: "selection" (selección de lista), "action" (acción sobre alumno), "confirmation" (confirmación), "specification" (especificación), "constancia_suggestion" (sugerir constancia)
- Datos a recordar: información relevante para futuras referencias
- Razonamiento: por qué esperas esta continuación y cómo el contexto ayudará al próximo prompt

FORMATO DE RESPUESTA COMPLETA:
{{
  "respuesta_usuario": "Tu respuesta profesional completa aquí",
  "reflexion_conversacional": {{
    "espera_continuacion": true|false,
    "tipo_esperado": "selection|action|confirmation|specification|none",
    "datos_recordar": {{
      "query": "consulta original",
      "data": [datos relevantes filtrados],
      "row_count": número_elementos_filtrados,
      "context": "contexto adicional",
      "filter_applied": "información del filtro inteligente"
    }},
    "razonamiento": "Explicación de por qué esperas o no esperas continuación"
  }}
}}

EJEMPLOS DE AUTO-REFLEXIÓN CONVERSACIONAL:

Ejemplo 1 - Lista de alumnos (CONTEXTO CONVERSACIONAL FUERTE):
"Mostré una lista de 21 alumnos García. Es muy probable que el usuario quiera información específica de alguno, como 'CURP del quinto' o 'constancia para el tercero'. DEBO recordar esta lista completa con posiciones para que el próximo prompt pueda entender referencias como 'el primero', 'número 5', 'para ese'. El contexto conversacional es CRÍTICO aquí."

Ejemplo 2 - Información específica (CONTEXTO DE CONSTANCIA):
"Proporcioné datos completos de Juan Pérez. Esto típicamente lleva a solicitudes de constancias o más información. DEBO recordar que estamos hablando específicamente de Juan Pérez para que si el usuario dice 'constancia para él' o 'para ese alumno', el próximo prompt sepa exactamente a quién se refiere. El contexto conversacional facilitará la generación directa de constancia."

Ejemplo 3 - Consulta estadística (SIN CONTEXTO CONVERSACIONAL):
"Di un número total de alumnos. Esta es información general que no requiere seguimiento específico. No hay contexto conversacional que recordar porque no hay elementos específicos que el usuario pueda referenciar."

Ejemplo 4 - Búsqueda con sugerencia (CONTEXTO + ACCIÓN ESPERADA):
"Encontré a CAMILA VARGAS GUTIERREZ y mostré sus datos completos. Sugerí generar constancia. Es muy probable que el usuario confirme con 'sí' o especifique tipo con 'constancia de estudios'. DEBO recordar todos los datos de Camila para que el próximo prompt pueda generar la constancia directamente sin nueva búsqueda."

Ejemplo 5 - Lista corta con acción implícita (CONTEXTO + SELECCIÓN):
"Mostré 3 alumnos de 2do grado. El usuario podría seleccionar uno específico ('el segundo', 'para María') o pedir acción general ('constancias para todos'). DEBO recordar la lista completa y sus posiciones para facilitar referencias contextuales."
"""

    def get_student_query_intention_prompt(self, user_query: str, conversation_context: str = "") -> str:
        """
        PROMPT 1 CENTRALIZADO: Detecta si la consulta es sobre alumnos/estudiantes
        🆕 MEJORADO: Ahora incluye contexto conversacional para mejor detección

        REEMPLAZA:
        - StudentQueryInterpreter._detect_student_query_intention() (prompt hardcodeado)

        PROPÓSITO:
        - Detectar si la consulta se refiere a estudiantes/escuela
        - Clasificar tipo de consulta (conteo, búsqueda, etc.)
        - Usar contexto escolar Y conversacional para interpretación inteligente
        - Detectar referencias contextuales ("ese alumno", "el tercero", etc.)

        VENTAJAS:
        - Contexto escolar centralizado
        - Contexto conversacional integrado
        - Lógica de detección unificada
        - Detección de continuaciones conversacionales
        """
        context_section = f"""
CONTEXTO CONVERSACIONAL DISPONIBLE:
{conversation_context}

🧠 ANÁLISIS CONVERSACIONAL:
Si hay contexto conversacional disponible, analiza si la consulta actual hace referencia a información anterior:
- Referencias directas: "ese alumno", "el tercero", "para él", "número 5"
- Referencias implícitas: "sí", "ok", "generar", "constancia"
- Continuaciones: "también", "además", "y qué tal", "más información"
- Especificaciones: "de estudios", "con foto", "completa"

""" if conversation_context.strip() else ""

        return f"""
Eres el ASISTENTE OFICIAL de la escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ" con CAPACIDAD DE ANÁLISIS CONVERSACIONAL.

{self.school_context}

{context_section}

CONSULTA DEL USUARIO: "{user_query}"

INSTRUCCIONES CONTEXTUALES MEJORADAS:
Como asistente de una escuela primaria, determina si la consulta se refiere a:
- Información de alumnos/estudiantes (DIRECTO)
- Información de "la escuela" (= información de alumnos, INDIRECTO)
- Estadísticas escolares (= estadísticas de estudiantes)
- Datos académicos o administrativos
- Búsquedas, conteos, listados de estudiantes
- Generación de documentos para alumnos
- 🆕 CONTINUACIONES de conversaciones anteriores sobre alumnos

🎯 DETECCIÓN DE CONTINUACIÓN CONVERSACIONAL:
Si hay contexto conversacional, evalúa si la consulta actual:
1. Hace referencia a alumnos mencionados anteriormente
2. Solicita acciones sobre datos ya mostrados
3. Es una confirmación de acción sugerida
4. Especifica detalles de una solicitud anterior

RESPONDE ÚNICAMENTE con un JSON:
{{
    "es_consulta_alumnos": true|false,
    "razonamiento": "Explicación contextual de por qué es/no es sobre alumnos, incluyendo análisis conversacional",
    "tipo_detectado": "conteo|busqueda|listado|detalles|constancia|estadisticas|continuacion|otro",
    "requiere_contexto": true|false,
    "tipo_continuacion": "referencia_directa|confirmacion|especificacion|nueva_consulta"
}}

EJEMPLOS CONTEXTUALES MEJORADOS:
- "cuántos alumnos hay" → es_consulta_alumnos: true, tipo: "conteo", requiere_contexto: false
- "constancia para ese alumno" → es_consulta_alumnos: true, tipo: "constancia", requiere_contexto: true, tipo_continuacion: "referencia_directa"
- "sí, genérala" → es_consulta_alumnos: true, tipo: "continuacion", requiere_contexto: true, tipo_continuacion: "confirmacion"
- "de estudios" → es_consulta_alumnos: true, tipo: "continuacion", requiere_contexto: true, tipo_continuacion: "especificacion"
- "el tercero de la lista" → es_consulta_alumnos: true, tipo: "continuacion", requiere_contexto: true, tipo_continuacion: "referencia_directa"
- "ayuda del sistema" → es_consulta_alumnos: false, tipo: "otro", requiere_contexto: false
"""

    def get_sql_generation_prompt(self, user_query: str) -> str:
        """
        PROMPT 2 CENTRALIZADO: Genera estrategia + SQL en un solo paso

        REEMPLAZA:
        - StudentQueryInterpreter._generate_sql_with_strategy() (prompt hardcodeado)

        PROPÓSITO:
        - Analizar consulta y generar SQL optimizado
        - Interpretar matices del lenguaje natural
        - Usar estructura completa de la base de datos

        VENTAJAS:
        - Contexto de BD centralizado
        - Reglas SQL unificadas
        - Ejemplos centralizados
        """
        database_context = self.get_database_context()

        return f"""
Eres un experto en SQL para un sistema escolar. Tu trabajo es analizar consultas de usuarios y generar SQL optimizado en un solo paso.

{self.school_context}

ESTRUCTURA COMPLETA DE LA BASE DE DATOS:
{database_context}

CONSULTA DEL USUARIO: "{user_query}"

INSTRUCCIONES INTELIGENTES:
1. ANALIZA la consulta comparándola con la estructura completa de la DB
2. IDENTIFICA qué tablas, columnas y relaciones necesitas
3. DETERMINA el tipo de consulta (COUNT, SELECT, filtros específicos)
4. 🧠 INTERPRETA matices del lenguaje natural:
   - "cualquier alumno" = 1 solo alumno → LIMIT 1
   - "un alumno" = 1 solo alumno → LIMIT 1
   - "el nombre de" = solo columna nombre
   - "la CURP de" = solo columna curp
   - "todos los alumnos" = sin LIMIT
   - "lista de alumnos" = múltiples resultados
5. GENERA directamente el SQL optimizado

REGLAS IMPORTANTES:
- SOLO consultas SELECT (nunca INSERT, UPDATE, DELETE)
- Usar nombres exactos de columnas de la estructura
- Para COUNT: SELECT COUNT(*) as total
- Para SELECT: incluir SOLO las columnas que el usuario pidió
- Usar JOINs apropiados: LEFT JOIN para datos opcionales, INNER JOIN para requeridos
- Aplicar filtros WHERE basándote en los valores reales de la estructura
- NO añadir LIMIT a consultas COUNT
- SÍ añadir LIMIT 1 cuando el usuario pida "un/cualquier" elemento específico

EJEMPLOS INTELIGENTES BASADOS EN LA ESTRUCTURA REAL:
- "cuántos alumnos hay en total" → SELECT COUNT(*) as total FROM alumnos
- "alumnos de 3er grado" → SELECT a.nombre, a.curp, de.grado, de.grupo, de.turno FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.grado = 3
- "dame el nombre de cualquier alumno de 3er grado" → SELECT a.nombre FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.grado = 3 LIMIT 1
- "dame un alumno de primer grado" → SELECT a.nombre FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.grado = 1 LIMIT 1
- "la CURP de María García" → SELECT curp FROM alumnos WHERE nombre LIKE '%MARIA%' AND nombre LIKE '%GARCIA%'
- "estudiantes nacidos en 2018" → SELECT nombre, curp, fecha_nacimiento FROM alumnos WHERE STRFTIME('%Y', fecha_nacimiento) = '2018'
- "alumnos que tengan calificaciones" → SELECT a.nombre, a.curp, de.grado, de.grupo FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.calificaciones IS NOT NULL AND de.calificaciones != '[]' AND de.calificaciones != ''
- "2 alumnos al azar que tengan calificaciones" → SELECT a.nombre, a.curp, de.grado, de.grupo FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.calificaciones IS NOT NULL AND de.calificaciones != '[]' AND de.calificaciones != '' ORDER BY RANDOM() LIMIT 2
- "alumnos sin calificaciones" → SELECT a.nombre, a.curp, de.grado, de.grupo FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.calificaciones IS NULL OR de.calificaciones = '[]' OR de.calificaciones = ''

🧮 EJEMPLOS ANALÍTICOS AVANZADOS (calificaciones como lista de materias):
- "promedio general de 5to grado" → SELECT AVG(CAST(JSON_EXTRACT(materia.value, '$.promedio') AS REAL)) as promedio_general FROM datos_escolares de, JSON_EACH(de.calificaciones) as materia WHERE de.grado = 5 AND de.calificaciones IS NOT NULL AND de.calificaciones != '[]'
- "cuántos alumnos de 5to grado tienen calificaciones" → SELECT COUNT(DISTINCT de.alumno_id) as cantidad FROM datos_escolares de WHERE de.grado = 5 AND de.calificaciones IS NOT NULL AND de.calificaciones != '[]' AND de.calificaciones != ''
- "alumnos de 5to grado con sus promedios" → SELECT a.nombre, de.grado, de.grupo, AVG(CAST(JSON_EXTRACT(materia.value, '$.promedio') AS REAL)) as promedio_alumno FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id, JSON_EACH(de.calificaciones) as materia WHERE de.grado = 5 AND de.calificaciones IS NOT NULL GROUP BY a.id, a.nombre ORDER BY promedio_alumno DESC
- "qué grupo tiene mejor rendimiento en 3er grado" → SELECT de.grupo, AVG(CAST(JSON_EXTRACT(materia.value, '$.promedio') AS REAL)) as promedio_grupo FROM datos_escolares de, JSON_EACH(de.calificaciones) as materia WHERE de.grado = 3 AND de.calificaciones IS NOT NULL GROUP BY de.grupo ORDER BY promedio_grupo DESC
- "distribución de alumnos por grado con calificaciones" → SELECT de.grado, COUNT(DISTINCT de.alumno_id) as alumnos_con_calificaciones FROM datos_escolares de WHERE de.calificaciones IS NOT NULL AND de.calificaciones != '[]' GROUP BY de.grado ORDER BY de.grado
- "estadísticas de calificaciones por materia en 4to grado" → SELECT JSON_EXTRACT(materia.value, '$.nombre') as materia_nombre, AVG(CAST(JSON_EXTRACT(materia.value, '$.promedio') AS REAL)) as promedio_materia, COUNT(*) as total_alumnos FROM datos_escolares de, JSON_EACH(de.calificaciones) as materia WHERE de.grado = 4 AND de.calificaciones IS NOT NULL GROUP BY materia_nombre ORDER BY promedio_materia DESC

RESPONDE ÚNICAMENTE con la consulta SQL, sin explicaciones adicionales.
"""
