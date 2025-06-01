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

🎯 **PRINCIPIO FUNDAMENTAL**:
- **PREGUNTA TEÓRICA** → ayuda_sistema (usuario quiere aprender)
- **ACCIÓN PRÁCTICA** → consulta_alumnos (usuario quiere hacer algo)

🔍 **AYUDA_SISTEMA** (Información y tutoriales):
- ❓ "qué tipos de constancias puedes generar?" → Quiere conocer opciones disponibles
- ❓ "cómo buscar alumnos por grado?" → Quiere aprender el proceso
- ❓ "qué puedes hacer?" → Quiere conocer capacidades
- ❓ "cuáles son los pasos para..." → Quiere tutorial
- 🔑 **Indicadores**: "qué", "cómo", "cuáles", "puedes", "tipos", "pasos", "proceso"

🔍 **CONSULTA_ALUMNOS** (Acciones con datos reales):
- ✅ "constancia de estudios para Juan Pérez" → Quiere generar constancia específica
- ✅ "buscar García" → Quiere encontrar alumnos específicos
- ✅ "cuántos alumnos hay en 3er grado" → Quiere estadística específica
- ✅ "mostrar todos los alumnos" → Quiere ver datos reales
- 🔑 **Indicadores**: Nombres propios, acciones directas, solicitudes específicas

🔍 **TRANSFORMACION_PDF** (Procesamiento de archivos):
- 📄 "transformar este PDF" → Usuario tiene archivo cargado
- 📄 "convertir al formato estándar" → Procesar PDF actual
- 📄 "comparar formatos" → Análisis de PDF cargado

⚠️ **CASOS LÍMITE COMUNES**:
- "generar constancia" (sin nombre) → **ayuda_sistema** (falta información específica)
- "buscar alumno" (sin nombre) → **ayuda_sistema** (pregunta general sobre proceso)
- "constancia para Juan" (con nombre) → **consulta_alumnos** (solicitud específica)
- "cómo generar constancia para Juan" → **consulta_alumnos** (acción específica con tutorial)

INSTRUCCIONES FINALES:
1. Analiza la consulta en el contexto conversacional completo
2. Aplica el PRINCIPIO FUNDAMENTAL: ¿Es pregunta teórica o acción práctica?
3. Usa las REGLAS CRÍTICAS para distinguir intenciones
4. Revisa los CASOS LÍMITE para situaciones ambiguas
5. Determina la intención principal y sub-intención más apropiada
6. Extrae entidades relevantes (nombres, tipos, acciones)
7. 🆕 DETECTA SI SE SOLICITA FOTO: Busca palabras como "con foto", "incluir foto", "foto", "fotografía"
8. Asigna confianza basada en claridad y especificidad de la consulta

DETECCIÓN DE TIPO DE CONSTANCIA:
- "constancia de estudios" → tipo_constancia: "estudios"
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
