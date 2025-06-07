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



    def _get_intentions_config_text(self) -> str:
        """
        Genera el texto de configuración de intenciones usando SystemCatalog (fuente única de verdad)
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            return SystemCatalog.generate_intentions_section()
        except Exception as e:
            # Fallback en caso de error
            return """
🎯 **INTENCIONES Y SUB-INTENCIONES VÁLIDAS:**

**CONSULTA_ALUMNOS** - Todo lo relacionado con datos de estudiantes
Especialista: StudentQueryInterpreter
Sub-intenciones:
   - **busqueda_simple**: 1-2 criterios básicos (nombre, grado, grupo, turno)
   - **busqueda_compleja**: 3+ criterios combinados O campos especiales
   - **estadisticas**: Números, conteos, promedios, distribuciones
   - **generar_constancia**: Documentos oficiales PDF
   - **transformacion_pdf**: Conversión entre formatos de constancia

**AYUDA_SISTEMA** - Soporte y explicaciones del sistema
Especialista: HelpInterpreter
Sub-intenciones:
   - **explicacion_general**: Capacidades generales del sistema
   - **tutorial_funciones**: Guías paso a paso de uso
   - **sobre_creador**: Información sobre Angel
   - **auto_consciencia**: Identidad del asistente IA
   - **ventajas_sistema**: Beneficios vs métodos tradicionales
   - **casos_uso_avanzados**: Funcionalidades impresionantes
   - **limitaciones_honestas**: Transparencia sobre limitaciones

**CONVERSACION_GENERAL** - Chat casual y saludos
Especialista: MasterInterpreter
Sub-intenciones:
   - **saludo**: Saludos y presentaciones
   - **chat_casual**: Conversación no relacionada al sistema

🚨 **CRÍTICO**: SOLO usar estas intenciones y sub-intenciones. NO crear nuevas.
🚨 **MAPEO ESPECIAL**: 'información completa', 'datos de', 'dame todo sobre' → busqueda_simple
"""

    def _get_examples_section(self) -> str:
        """
        Genera ejemplos específicos usando SystemCatalog
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            examples = SystemCatalog.generate_examples_section()

            # 🔍 DEBUG: Verificar que los ejemplos de constancia estén incluidos
            if "generale una constancia" in examples:
                print("✅ [DEBUG] Ejemplos de constancia cargados correctamente en MasterPromptManager")
            else:
                print("❌ [DEBUG] Ejemplos de constancia NO encontrados en SystemCatalog")

            return examples
        except Exception as e:
            print(f"❌ [DEBUG] Error cargando SystemCatalog: {e}")
            # Fallback básico
            return """
🎯 **EJEMPLOS BÁSICOS:**
- "Dame 3 alumnos" → limite_resultados: 3
- "alumnos de 2do A" → filtros: ["grado: 2", "grupo: A"]
- "constancia para Juan" → generar_constancia, nombres: ["Juan"]
"""

    def _get_context_rules(self) -> str:
        """
        Genera reglas de contexto usando SystemCatalog
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            return SystemCatalog.generate_context_rules()
        except Exception as e:
            # Fallback básico
            return """
🧠 **REGLAS DE CONTEXTO:**
- "de esos" → filtrar lista anterior
- "el segundo" → elemento en posición 2
- NIVEL 1 = MÁS RECIENTE = MÁXIMA PRIORIDAD
"""

    def _get_student_capabilities(self) -> str:
        """
        Genera capacidades del Student usando SystemCatalog
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            return SystemCatalog.generate_student_capabilities_section()
        except Exception as e:
            # Fallback básico
            return """
- BUSCAR_UNIVERSAL: Encontrar alumnos por cualquier criterio
- CALCULAR_ESTADISTICA: Análisis, conteos, distribuciones, promedios
- CONTAR_UNIVERSAL: Conteos específicos y rápidos
- GENERAR_CONSTANCIA: Crear documentos oficiales PDF
- BUSCAR_Y_FILTRAR: Filtrar resultados previos
"""

    def _get_intentions_routing(self) -> str:
        """
        Genera intenciones y routing usando SystemCatalog
        """
        try:
            from app.core.ai.system_catalog import SystemCatalog
            return SystemCatalog.generate_intentions_section()
        except Exception as e:
            # Fallback básico
            return """
**CONSULTA_ALUMNOS** → StudentQueryInterpreter
- busqueda_simple: 1-2 criterios básicos (nombre, grado, grupo)
- busqueda_compleja: 3+ criterios combinados
- estadisticas: Conteos, análisis, distribuciones
- generar_constancia: Documentos oficiales PDF

**AYUDA_SISTEMA** → HelpInterpreter
- explicacion_general: Capacidades del sistema
- tutorial_funciones: Guías de uso
- sobre_creador: Información sobre Angel

**CONVERSACION_GENERAL** → GeneralInterpreter
- saludo: Saludos y cortesías
- chat_casual: Conversación no escolar
"""

    @property
    def school_context(self) -> str:
        """
        Contexto escolar centralizado - COMPARTIDO con StudentQueryPromptManager

        Este contexto debe ser IDÉNTICO al usado en StudentQueryPromptManager
        para garantizar consistencia total entre prompts
        """
        if self._school_context_cache is None:
            # 🎯 CONTEXTO DINÁMICO: Se adapta automáticamente a cualquier escuela
            school_name = self.school_config.get_school_name()
            education_level = self.school_config.get_education_level().lower()
            total_students = self.school_config.get_total_students()

            self._school_context_cache = f"""
CONTEXTO COMPLETO DEL SISTEMA:
- Sistema de gestión escolar para la escuela {education_level} "{school_name}"
- Maneja datos de alumnos, información académica y generación de constancias
- Los usuarios son personal administrativo que necesita información precisa
- TODO el sistema ES la escuela - no hay nada más
- TODA la base de datos SON los alumnos de esta escuela ({total_students} estudiantes)
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

{self._get_examples_section()}

🎯 **MI TAREA ESPECÍFICA:**
{self.get_unified_prompt_header("MASTER INTELIGENTE del sistema escolar")}

🧠 **RAZONAMIENTO SEMÁNTICO HUMANO:**
Como un director de escuela experimentado, entiendo el CONTEXTO y las NECESIDADES.

🎯 **CAPACIDADES DEL STUDENT QUE DIRIJO:**
{self._get_student_capabilities()}

🧠 **PROCESO MENTAL COMPLETO EN 6 PASOS OBLIGATORIOS:**

**PASO 1: ANÁLISIS SEMÁNTICO PURO**
- ¿QUÉ acción quiere? (buscar, contar, generar, ayudar, conversar)
- ¿DE QUIÉN/QUÉ? (nombres, criterios, filtros específicos)
- ¿CUÁNTO? (límites numéricos explícitos)

**PASO 2: EXTRACCIÓN DE ENTIDADES ESPECÍFICAS**
- **LÍMITES**: Detectar números explícitos ("3", "5", "primeros 2") → limite_resultados
- **FILTROS**: Detectar criterios ("segundo grado", "grupo A") → filtros array
- **NOMBRES**: Detectar nombres propios ("Juan Pérez") → nombres array
- **TIPOS**: Detectar tipos de constancia ("estudios") → tipo_constancia

**PASO 3: VERIFICACIÓN DE INFORMACIÓN SUFICIENTE**
- ¿Tengo criterios claros y específicos?
- ¿Necesito aclaración del usuario?
- ¿Puedo proceder con la información disponible?

**PASO 4: ANÁLISIS DE CONTEXTO CONVERSACIONAL (CRÍTICO)**
- ¿Se refiere a algo de la conversación anterior?
- ¿Puedo resolver referencias como "de esos", "el segundo", "a ese alumno"?
- ¿Necesito información del contexto previo?

**RESOLUCIÓN INTELIGENTE DE CONTEXTO:**
- "a ese alumno" + contexto con 1 alumno → alumno_resuelto: [datos completos del alumno]
- "para él" + contexto con 1 alumno → alumno_resuelto: [datos completos del alumno]
- "al estudiante" + contexto con 1 alumno → alumno_resuelto: [datos completos del alumno]
- "generale una constancia a ese alumno" + Franco Alexander en contexto → generar_constancia + alumno_resuelto: Franco Alexander

**PASO 5: VERIFICACIÓN DE CAPACIDADES**
- ¿Student puede manejar consultas de alumnos?
- ¿Help puede explicar el sistema?
- ¿General puede conversar casualmente?

**PASO 6: PREPARACIÓN DE INSTRUCCIÓN COMPLETA**
- Mapear a intention_type y sub_intention específicos
- Incluir TODAS las entidades detectadas
- Preparar categorización completa para Student

🎯 **INTENCIONES Y ROUTING:**
{self._get_intentions_routing()}

🎯 **FORMATO ESTÁNDAR PARA STUDENT:**

SIEMPRE incluir información COMPLETA y ESPECÍFICA:

**EJEMPLO 1 - BÚSQUEDA SIMPLE:**
```json
{{
  "intention_type": "consulta_alumnos",
  "sub_intention": "busqueda_simple",
  "confidence": 0.95,
  "reasoning": "Usuario solicita 3 alumnos de segundo grado - criterios claros",
  "detected_entities": {{
    "filtros": ["grado: 2"],
    "limite_resultados": 3,
    "accion_principal": "buscar",
    "nombres": [],
    "tipo_constancia": null,
    "incluir_foto": false,
    "alumno_resuelto": null
  }},
  "student_categorization": {{
    "categoria": "busqueda",
    "sub_tipo": "simple",
    "requiere_contexto": false,
    "flujo_optimo": "sql_directo"
  }}
}}
```

**EJEMPLO 2 - CONSTANCIA CON CONTEXTO RESUELTO:**
```json
{{
  "intention_type": "consulta_alumnos",
  "sub_intention": "generar_constancia",
  "confidence": 0.95,
  "reasoning": "Usuario solicita constancia para alumno específico del contexto - Franco Alexander ya identificado",
  "detected_entities": {{
    "filtros": [],
    "limite_resultados": null,
    "accion_principal": "generar_constancia",
    "nombres": [],
    "tipo_constancia": "traslado",
    "incluir_foto": false,
    "alumno_resuelto": {{"id": 1, "nombre": "Franco Alexander", "posicion": "contexto nivel 1"}}
  }},
  "student_categorization": {{
    "categoria": "constancia",
    "sub_tipo": "individual",
    "requiere_contexto": true,
    "flujo_optimo": "alumno_resuelto"
  }}
}}
```

⚠️ **REGLAS CRÍTICAS OBLIGATORIAS:**
- NUNCA enviar campos vacíos o null sin razón
- SIEMPRE detectar límites numéricos explícitos
- SIEMPRE detectar filtros de grado/grupo/turno
- SIEMPRE incluir reasoning detallado

🚨 **DETECCIÓN DE CONSTANCIAS - OBLIGATORIO:**
- Si la consulta contiene "constancia", "certificado", "documento", "generale", "genera", "crea" → sub_intention: "generar_constancia"
- Si hay contexto con 1 alumno + solicitud de constancia → alumno_resuelto: [datos del alumno del contexto]
- NUNCA usar "busqueda_simple" para solicitudes de constancias
- SIEMPRE resolver "a ese alumno", "para él", "al estudiante" usando el contexto

🎯 **EJEMPLOS CRÍTICOS DE DETECCIÓN:**
- "generale una constancia" → generar_constancia
- "genera constancia" → generar_constancia
- "crea una constancia" → generar_constancia
- "constancia para ese alumno" → generar_constancia + alumno_resuelto
- "documento oficial" → generar_constancia

{self.get_unified_json_instructions_dynamic()}
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

**CON CONTEXTO:**
Si hay información previa, la uso inteligentemente para entender referencias como:
- "de esos" = filtrar la lista anterior
- "el segundo" = segundo elemento de la lista
- "para Juan" = Juan mencionado en el contexto
- "ahora dame 3" = límite de 3 de la lista actual
"""

        return context

    # ✅ MÉTODO ELIMINADO: get_forced_routing_prompt() - Reemplazado por análisis unificado con SystemCatalog

    def _format_conversation_context(self, conversation_stack: list) -> str:
        """Formatea el contexto conversacional para prompts"""
        if not conversation_stack:
            return "No hay contexto conversacional previo."

        context = "Conversación reciente:\n"
        for i, entry in enumerate(conversation_stack[-3:], 1):  # Últimas 3 interacciones
            query = entry.get('query', '')[:100] + "..." if len(entry.get('query', '')) > 100 else entry.get('query', '')
            specialist = entry.get('specialist_used', 'unknown')
            context += f"{i}. Usuario: {query} (Atendido por: {specialist})\n"

        return context
