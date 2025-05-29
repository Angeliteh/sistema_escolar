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

    def __init__(self):
        super().__init__()  # Inicializar BasePromptManager
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
        # Usar identidad unificada del BasePromptManager
        unified_header = self.get_unified_prompt_header("detector de intenciones maestro")

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
   - Sub-intenciones: busqueda_simple, generar_constancia, estadisticas, listado_completo
   - ✅ Búsquedas: "buscar Juan Pérez", "alumnos de 3er grado", "cuántos estudiantes hay"
   - ✅ Constancias: "constancia de estudios para María García", "generar constancia de calificaciones"
   - ✅ Estadísticas: "cuántos alumnos hay en total", "distribución por grados"
   - ❌ NO incluye: Preguntas teóricas sobre tipos o procesos

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
- Continuaciones de alumnos → SIEMPRE "consulta_alumnos"
- Palabras como "sí", "generala", "para él" → continuaciones
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

DETECCIÓN DE FOTO:
- "constancia con foto" → incluir_foto: true
- "constancia de traslado con foto" → incluir_foto: true
- "generar constancia con fotografía" → incluir_foto: true
- "constancia sin foto" → incluir_foto: false
- Si no se menciona foto → incluir_foto: false

{self.get_unified_json_instructions({
    "intention_type": "consulta_alumnos|transformacion_pdf|ayuda_sistema|conversacion_general",
    "sub_intention": "sub_categoria_especifica",
    "confidence": "0.0-1.0",
    "reasoning": "Explicación detallada de la decisión manteniendo mi personalidad",
    "detected_entities": {
        "nombres": ["lista de nombres detectados"],
        "tipo_constancia": "estudios|calificaciones|traslado|null",
        "accion_principal": "buscar|generar|contar|listar|transformar|ayudar",
        "fuente_datos": "base_datos|conversacion_previa|pdf_cargado|sistema",
        "contexto_especifico": "información adicional relevante",
        "filtros": ["criterios de filtrado"],
        "incluir_foto": "true|false",
        "parametros_extra": "cualquier parámetro adicional relevante"
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
