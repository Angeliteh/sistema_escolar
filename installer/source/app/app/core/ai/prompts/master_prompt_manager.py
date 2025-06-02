"""
MasterPromptManager - Centralización de prompts del nivel MAESTRO
Maneja la detección de intenciones y routing principal del sistema
"""

from typing import Dict, List, Optional
from .base_prompt_manager import BasePromptManager


class MasterPromptManager(BasePromptManager):
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

    def __init__(self, database_analyzer=None):
        super().__init__()  # Inicializar BasePromptManager
        self.database_analyzer = database_analyzer
        self._school_context_cache = None
        self._database_context_cache = None

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
        PROMPT MAESTRO CONSOLIDADO para detección de intenciones + categorización específica

        🆕 CONSOLIDADO: Incluye funcionalidad del Student Prompt 1 eliminado

        REEMPLAZA:
        - IntentionDetector.detect_intention() (prompt hardcodeado)
        - StudentQueryPromptManager.get_specific_student_intention_prompt() (ELIMINADO)

        PROPÓSITO:
        - Detectar intención principal + sub-intención
        - 🆕 CATEGORIZACIÓN ESPECÍFICA para consultas de alumnos
        - Usar contexto conversacional para continuaciones
        - Extraer entidades relevantes
        - Dirigir al intérprete correcto

        VENTAJAS:
        - Elimina redundancia entre Master y Student Prompt 1
        - Contexto escolar consistente
        - Mantenimiento centralizado
        - Fácil optimización
        - Testing unificado
        """
        # Usar identidad unificada del BasePromptManager
        unified_header = self.get_unified_prompt_header("detector de intenciones maestro consolidado")

        # El conversation_context ya viene formateado como string, no como lista
        conversation_context_formatted = conversation_context if conversation_context else "\n💭 CONTEXTO CONVERSACIONAL: Esta es una nueva conversación.\n"

        return f"""
{unified_header}

{conversation_context_formatted}

CONSULTA DEL USUARIO: "{user_query}"

🚨 VERIFICACIÓN OBLIGATORIA ANTES DE RESPONDER:
¿La consulta "{user_query}" menciona un NOMBRE COMPLETO de persona?
- SI menciona NOMBRE COMPLETO → intention_type: "consulta_alumnos" (OBLIGATORIO)
- SI es vaga sin nombre → intention_type: "aclaracion_requerida"
- SI es pregunta explícita con "¿" → intention_type: "ayuda_sistema"

🎯 MI TAREA ESPECÍFICA:
Analizar la consulta del usuario y determinar qué módulo especializado debe manejarla.
Mantengo el contexto de nuestra conversación para detectar continuaciones y referencias.

TIPOS DE INTENCIÓN DISPONIBLES:

1. **consulta_alumnos**: Gestión de datos de estudiantes y constancias
   - Sub-intenciones OFICIALES (según INTENCIONES_ACCIONES_DEFINITIVAS.md):
     * **busqueda_simple**: Búsquedas con 1-2 criterios básicos y directos
     * **busqueda_compleja**: Búsquedas con múltiples criterios (3+) o campos especiales
     * **estadisticas**: Cálculos, conteos y análisis estadísticos
     * **generar_constancia**: Generación de documentos oficiales PDF
     * **transformacion_pdf**: Transformación de constancias entre formatos

   🎯 **CRITERIOS DE CLASIFICACIÓN CONSOLIDADOS**:

   **INTENCIONES PRINCIPALES:**
   - **consulta_alumnos**: Búsquedas, estadísticas, reportes, constancias de estudiantes
   - **ayuda_sistema**: Explicaciones de funcionalidad del sistema
   - **transformacion_pdf**: Conversión de formatos de documentos
   - **conversacion_general**: Charla casual, saludos

   **SUB-INTENCIONES (si es consulta_alumnos):**
   - **busqueda_simple**: 1-2 criterios básicos (nombre, grado, grupo, turno)
   - **busqueda_compleja**: 3+ criterios combinados O campos especiales (promedio)
   - **estadisticas**: Solicita números, conteos, promedios ("cuántos", "total")
   - **generar_constancia**: Solicita documentos ("constancia", "certificado")

   🆕 **CATEGORIZACIÓN ESPECÍFICA (si es consulta_alumnos):**
   - **categoria**: busqueda|estadistica|reporte|constancia|transformacion|continuacion
   - **sub_tipo**: simple|complejo|listado|conteo|generacion|conversion|referencia|confirmacion
   - **complejidad**: baja|media|alta
   - **flujo_optimo**: sql_directo|analisis_datos|listado_completo|generacion_docs|procesamiento_contexto

   📋 **EJEMPLOS POR SUB-INTENCIÓN**:
   - **busqueda_simple**: "buscar García", "alumnos de 2do A", "turno matutino"
   - **busqueda_compleja**: "alumnos de 2do A turno matutino", "García del vespertino con calificaciones"
   - **estadisticas**: "cuántos alumnos hay", "total por grado", "distribución de estudiantes"
   - **generar_constancia**: "constancia para Juan Pérez", "certificado de María García"
   - **transformacion_pdf**: "convertir PDF", "cambiar formato de constancia"

   🎯 **FORMATO ESPECÍFICO DE FILTROS**:
   - "cuántos hay en 3° A" → filtros: ["grado: 3", "grupo: A"]
   - "alumnos de 2do B" → filtros: ["grado: 2", "grupo: B"]
   - "estudiantes del turno matutino" → filtros: ["turno: MATUTINO"]
   - "niños de 1° grado turno vespertino" → filtros: ["grado: 1", "turno: VESPERTINO"]

2. **transformacion_pdf**: Procesar PDFs de constancias en el panel integrado
   - Sub-intenciones: cargar_pdf, transformar_formato, comparar_formatos
   - ✅ Ejemplos: "transformar este PDF", "convertir al formato estándar", "comparar con original"
   - ✅ Contexto: Usuario tiene PDF cargado en el panel y quiere procesarlo

3. **ayuda_sistema**: Información sobre capacidades y uso del sistema
   - Sub-intenciones: entender_capacidades, tutorial_uso, tipos_constancias, como_usar
   - ✅ Capacidades: "qué puedes hacer", "qué tipos de constancias generas"
   - ✅ Tutoriales: "cómo buscar alumnos", "cómo generar constancias"
   - ✅ Información: Preguntas sobre tipos, procesos, funcionalidades SIN ejecutar acciones

4. **conversacion_general**: Interacción social y temas fuera del dominio escolar
   - Sub-intenciones: chat_casual, saludo, despedida, agradecimiento
   - ✅ Ejemplos: "hola", "buenos días", "gracias", "adiós", "cómo estás"

REGLAS ESPECIALES PARA CONTINUACIONES:
- Si hay contexto conversacional previo, analiza si es continuación
- Continuaciones de alumnos → SIEMPRE "consulta_alumnos" con "busqueda_simple"
- Palabras como "sí", "generala", "para él" → continuaciones
- Filtros sobre datos previos → "busqueda_simple" (usar BUSCAR_UNIVERSAL)
- Usa "fuente_datos": "conversacion_previa" para continuaciones

REGLAS CRÍTICAS PARA EVITAR CONFUSIONES:

🎯 **PRINCIPIO FUNDAMENTAL CORREGIDO**:
- **PREGUNTA EXPLÍCITA** sobre capacidades → ayuda_sistema (¿qué puedes hacer?)
- **ACCIÓN COMPLETA** con criterios → consulta_alumnos (buscar García)
- **ACCIÓN INCOMPLETA** sin criterios → aclaracion_requerida (dame información)

🔍 **AYUDA_SISTEMA** (Preguntas explícitas sobre capacidades):
- ❓ "¿qué tipos de constancias puedes generar?" → Pregunta explícita sobre opciones
- ❓ "¿cómo buscar alumnos por grado?" → Pregunta explícita sobre proceso
- ❓ "¿qué puedes hacer?" → Pregunta explícita sobre capacidades
- ❓ "explícame las funciones" → Solicitud explícita de tutorial
- 🔑 **Indicadores**: Preguntas directas con "¿qué?", "¿cómo?", "explícame", "cuáles son"

🔍 **CONSULTA_ALUMNOS** (Acciones específicas con datos):
- ✅ "constancia de estudios para Juan Pérez" → Acción específica con destinatario
- ✅ "buscar García" → Acción específica con criterio
- ✅ "cuántos alumnos hay en 3er grado" → Acción específica con parámetro
- ✅ "mostrar todos los alumnos" → Acción específica completa
- 🔑 **Indicadores**: Acciones directas con criterios específicos

🔍 **ACLARACION_REQUERIDA** (Acciones incompletas):
- ❓ "dame información" → Acción incompleta (¿información de qué?)
- ❓ "buscar información" → Acción incompleta (¿información de qué?)
- ❓ "generar documento" → Acción incompleta (¿qué documento? ¿para quién?)
- ❓ "mostrar datos" → Acción incompleta (¿qué datos?)
- 🔑 **Indicadores**: Verbos de acción + objetos vagos sin especificar

🔍 **TRANSFORMACION_PDF** (Procesamiento de archivos):
- 📄 "transformar este PDF" → Usuario tiene archivo cargado
- 📄 "convertir al formato estándar" → Procesar PDF actual
- 📄 "comparar formatos" → Análisis de PDF cargado

⚠️ **CASOS LÍMITE COMUNES**:
- "generar constancia" (sin nombre) → **ayuda_sistema** (falta información específica)
- "buscar alumno" (sin nombre) → **ayuda_sistema** (pregunta general sobre proceso)
- "constancia para Juan" (con nombre) → **consulta_alumnos** (solicitud específica)
- "cómo generar constancia para Juan" → **consulta_alumnos** (acción específica con tutorial)

🚨 REGLA CRÍTICA OBLIGATORIA - LEER PRIMERO:

SI LA CONSULTA ES VAGA O INCOMPLETA → SIEMPRE usar intention_type: "aclaracion_requerida"
NO usar "ayuda_sistema" para consultas vagas. Solo para preguntas explícitas con "¿".

PRINCIPIO CLAVE: Evaluar si especifica QUÉ/QUIÉN/CUÁL, no palabras específicas.

🧠 DETECCIÓN INTELIGENTE DE AMBIGÜEDADES (ANÁLISIS SEMÁNTICO):

IDENTIDAD: Master del sistema escolar "PROF. MAXIMO GAMIZ FERNANDEZ"
CONTEXTO: 211 alumnos en grados 1° a 6°, capacidades de búsqueda, constancias, estadísticas

🎯 **ANÁLISIS SEMÁNTICO INTELIGENTE:**

1. **COMPLETITUD SEMÁNTICA**: ¿La consulta especifica claramente la acción y el objeto?

   **PATRONES COMPLETOS** (VERBO + OBJETO_ESPECÍFICO):
   - ✅ "buscar alumnos García" → Acción clara + criterio específico
   - ✅ "constancia para Juan Pérez" → Acción clara + destinatario específico
   - ✅ "cuántos alumnos en segundo grado" → Acción clara + parámetro específico
   - ✅ "estadísticas del turno matutino" → Acción clara + criterio específico

   **PATRONES INCOMPLETOS** (VERBO + OBJETO_SIN_ESPECIFICAR):
   - ❓ "dame información" → Falta especificar DE QUÉ/QUIÉN
   - ❓ "buscar estudiante" → Falta especificar CUÁL estudiante
   - ❓ "generar documento" → Falta especificar QUÉ documento y PARA QUIÉN
   - ❓ "mostrar datos" → Falta especificar QUÉ datos
   - ❓ "cuántos hay" → Falta especificar QUÉ contar y DÓNDE

2. **VERIFICACIÓN CONTEXTUAL**: Solo si la consulta es semánticamente incompleta
   - ¿El contexto conversacional proporciona el objeto/criterio faltante?
   - ¿La referencia es explícita y resoluble? ("del segundo", "para él")
   - ¿Tiene más sentido con contexto que sin él?

3. **DECISIÓN INTELIGENTE**:
   - **Semánticamente completa** → Procesar normalmente (confianza 0.7-0.95)
   - **Incompleta + contexto resuelve** → Usar contexto (confianza 0.6-0.8)
   - **Incompleta sin resolución** → intention_type: "aclaracion_requerida" (confianza 0.3-0.5)

🚨 **REGLA CRÍTICA REFINADA**:
- Si falta especificar DE QUÉ/QUIÉN/CUÁL → aclaracion_requerida
- Si especifica claramente el objeto/persona → consulta_alumnos
- Si es pregunta explícita sobre capacidades → ayuda_sistema

**EJEMPLOS CRÍTICOS DE APLICACIÓN:**
- "información" → aclaracion_requerida (falta especificar DE QUIÉN)
- "datos" → aclaracion_requerida (falta especificar DE QUIÉN)
- "información de Juan García" → consulta_alumnos (especifica DE QUIÉN)
- "datos de María López" → consulta_alumnos (especifica DE QUIÉN)
- "detalles de Pedro Sánchez" → consulta_alumnos (especifica DE QUIÉN)
- "¿qué información puedes dar?" → ayuda_sistema (pregunta sobre capacidades)

**REGLA ABSOLUTA**: Si menciona un NOMBRE COMPLETO de persona, es consulta_alumnos.

**PARA CONSULTAS QUE REQUIEREN ACLARACIÓN:**
- intention_type: "aclaracion_requerida"
- confidence: 0.3-0.5
- reasoning: "Falta especificar [QUÉ/QUIÉN/CUÁL] en la consulta"
- detected_entities.clarification_needed: Pregunta específica

**PRINCIPIO FUNDAMENTAL**: Evaluar si la consulta especifica claramente QUÉ/QUIÉN/CUÁL, no las palabras exactas usadas.

DETECCIÓN DE TIPO DE CONSTANCIA:
- "constancia de estudios" → tipo_constancia: "estudio"
- "constancia de calificaciones" → tipo_constancia: "calificaciones"
- "constancia de traslado" → tipo_constancia: "traslado"
- "certificado de estudios" → tipo_constancia: "estudios"
- "certificado de calificaciones" → tipo_constancia: "calificaciones"
- "constancia" (sin especificar) → tipo_constancia: "estudios" (por defecto)
- "genera una constancia" → tipo_constancia: "estudios" (por defecto)

DETECCIÓN DE FOTO:
- "constancia con foto" → incluir_foto: true
- "constancia de traslado con foto" → incluir_foto: true
- "generar constancia con fotografía" → incluir_foto: true
- "constancia sin foto" → incluir_foto: false
- Si no se menciona foto → incluir_foto: false

{self.get_unified_json_instructions({
    "intention_type": "consulta_alumnos|transformacion_pdf|ayuda_sistema|conversacion_general",
    "sub_intention": "busqueda_simple|busqueda_compleja|estadisticas|generar_constancia|transformacion_pdf|pregunta_capacidades|chat_casual",
    "confidence": "0.0-1.0",
    "reasoning": "Explicación detallada de la decisión manteniendo mi personalidad",
    "detected_entities": {
        "nombres": ["lista de nombres detectados"],
        "tipo_constancia": "estudios|calificaciones|traslado|null",
        "accion_principal": "buscar|generar|contar|listar|transformar|ayudar",
        "fuente_datos": "base_datos|conversacion_previa|pdf_cargado|sistema",
        "contexto_especifico": "información adicional relevante",
        "filtros": ["formato: campo: valor (ej: grado: 3, grupo: A, turno: MATUTINO)"],
        "incluir_foto": "true|false",
        "alumno_resuelto": "objeto con id, nombre y posicion O null si no aplica",
        "campo_solicitado": "campo específico solicitado (curp, nombre, etc.) O null si no aplica",
        "parametros_extra": "cualquier parámetro adicional relevante"
    },
    "student_categorization": {
        "categoria": "busqueda|estadistica|reporte|constancia|transformacion|continuacion",
        "sub_tipo": "simple|complejo|listado|conteo|generacion|conversion|referencia|confirmacion",
        "complejidad": "baja|media|alta",
        "requiere_contexto": "true|false",
        "flujo_optimo": "sql_directo|analisis_datos|listado_completo|generacion_docs|procesamiento_contexto"
    }
})}
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
            # 🛠️ VERIFICAR TIPO DE DATOS PARA EVITAR ERRORES
            if isinstance(level, dict):
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
            else:
                # Si level no es un dict, tratarlo como string
                context += f"📋 NIVEL {i}: {str(level)}\n"

        context += """
🧠 APLICACIÓN DEL ANÁLISIS SEMÁNTICO CON CONTEXTO:

Usar el mismo proceso de análisis semántico definido arriba, pero considerando el contexto disponible.

🎯 RESOLUCIÓN INTELIGENTE DE REFERENCIAS:

Cuando detectes una referencia explícita en la consulta:

**REFERENCIAS POSICIONALES**: "primero", "segundo", "tercero", "último", "número X"
**REFERENCIAS PRONOMINALES**: "él/ella", "ese/esa", "este/esta"

**PROCESO DE RESOLUCIÓN**:
1. Identifica la referencia en la consulta
2. Localiza los datos correspondientes en el contexto
3. Extrae la información específica del elemento referenciado
4. Incluye los datos completos en detected_entities.alumno_resuelto
5. Cambia requiere_contexto a "false" (ya resuelto por Master)

**RESULTADO**: El Student recibe la información completa sin necesidad de interpretar referencias.
"""

        return context
