"""
HelpPromptManager - Centralización de prompts para HelpInterpreter
Reemplaza prompts hardcodeados en clases especializadas de ayuda
"""

from typing import Dict, Any
from app.core.logging import get_logger

class HelpPromptManager:
    """
    Gestor centralizado de prompts para el sistema de ayuda

    REEMPLAZA:
    - HelpContentGenerator._build_content_prompt() (80 líneas)
    - HelpResponseGenerator._build_response_prompt() (52 líneas)
    - TutorialProcessor._build_tutorial_prompt() (55 líneas)

    VENTAJAS:
    - Prompts centralizados y mantenibles
    - Contexto del sistema unificado
    - Fácil optimización y actualización
    - Consistencia entre todos los prompts de ayuda
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.system_context = self._build_system_context()

    def get_help_content_prompt(self, user_query: str, help_type: str, detected_entities: Dict) -> str:
        """
        PROMPT CENTRALIZADO: Genera contenido específico de ayuda

        REEMPLAZA: HelpContentGenerator._build_content_prompt()

        Args:
            user_query: Consulta original del usuario
            help_type: Tipo de ayuda (solucion_problema, ejemplo_practico, general)
            detected_entities: Entidades detectadas por el master

        Returns:
            Prompt optimizado para generar contenido de ayuda
        """
        base_prompt = f"""
Eres un especialista en generar CONTENIDO DE AYUDA para sistema escolar.

CONTEXTO COMPLETO DEL SISTEMA:
{self.system_context}

CONSULTA DEL USUARIO: "{user_query}"
TIPO DE AYUDA: {help_type}
ENTIDADES DETECTADAS: {detected_entities}

INSTRUCCIONES ESPECÍFICAS PARA {help_type.upper()}:
"""

        if help_type == "solucion_problema":
            return base_prompt + """
1. IDENTIFICA el problema específico del usuario
2. PROPORCIONA soluciones EXACTAS basadas en el comportamiento real del sistema
3. INCLUYE pasos específicos que realmente funcionan
4. MENCIONA características específicas como vista previa automática

🎯 INSTRUCCIONES ESPECIALES PARA CONSTANCIAS:
Si la consulta es sobre "cómo obtener constancia", DEBES explicar el proceso REAL:

PROCESO REAL PASO A PASO:
1. BUSCAR ALUMNO: "buscar [nombre del alumno]"
2. SOLICITAR CONSTANCIA: "constancia de [tipo] para [referencia al alumno]"
3. VISTA PREVIA: El sistema genera automáticamente vista previa
4. REVISIÓN: Se abre PDF automáticamente para revisar
5. CONFIRMACIÓN: Usuario puede confirmar o cancelar

TIPOS DE CONSTANCIA REALES:
- "estudios": Para CUALQUIER alumno registrado
- "calificaciones": SOLO para alumnos CON calificaciones
- "traslado": SOLO para alumnos CON calificaciones

REFERENCIAS CONTEXTUALES QUE FUNCIONAN:
- "para ese alumno" (si ya se buscó antes)
- "para el primero/segundo/tercero" (posición en lista)
- "para [nombre completo]" (nombre específico)

FORMATO DE RESPUESTA:
{
    "tipo_contenido": "solucion_problema",
    "problema_identificado": "Descripción del problema específico",
    "soluciones": [
        {
            "titulo": "Proceso paso a paso REAL",
            "pasos": ["pasos exactos que funcionan en el sistema"],
            "consejos": ["características específicas como vista previa automática"]
        }
    ],
    "alternativas": ["métodos alternativos reales"],
    "prevencion": ["reglas importantes del sistema"],
    "ejemplos_practicos": ["ejemplos exactos que funcionan"]
}
"""

        elif help_type == "ejemplo_practico":
            return base_prompt + """
1. GENERA ejemplos reales y específicos del sistema
2. INCLUYE casos de uso comunes y útiles
3. PROPORCIONA pasos detallados para cada ejemplo
4. MUESTRA resultados esperados

FORMATO DE RESPUESTA:
{
    "tipo_contenido": "ejemplo_practico",
    "ejemplos": [
        {
            "titulo": "Ejemplo 1",
            "descripcion": "Qué hace este ejemplo",
            "pasos": ["paso1", "paso2", "paso3"],
            "comando_ejemplo": "texto exacto a escribir",
            "resultado_esperado": "qué verá el usuario"
        }
    ],
    "casos_uso_comunes": ["caso1", "caso2"],
    "consejos_practicos": ["consejo1", "consejo2"]
}
"""

        else:  # Contenido general
            return base_prompt + """
1. ANALIZA qué información específica necesita el usuario
2. ESTRUCTURA el contenido de manera clara y útil
3. INCLUYE ejemplos prácticos cuando sea apropiado
4. PROPORCIONA pasos específicos si es necesario

FORMATO DE RESPUESTA:
{
    "tipo_contenido": "ayuda_general",
    "contenido_principal": "Explicación principal",
    "puntos_clave": ["punto1", "punto2", "punto3"],
    "ejemplos": ["ejemplo1", "ejemplo2"],
    "pasos_recomendados": ["paso1", "paso2"],
    "informacion_adicional": "Información extra útil"
}

RESPONDE ÚNICAMENTE CON EL JSON, sin explicaciones adicionales.
"""

    def get_help_response_prompt(self, user_query: str, help_content: Dict) -> str:
        """
        PROMPT CENTRALIZADO: Genera respuesta con auto-reflexión

        REEMPLAZA: HelpResponseGenerator._build_response_prompt()

        Args:
            user_query: Consulta original del usuario
            help_content: Contenido de ayuda generado

        Returns:
            Prompt para generar respuesta natural con auto-reflexión
        """
        return f"""
Eres un comunicador experto de AYUDA para sistema escolar con CAPACIDAD DE AUTO-REFLEXIÓN.

CONSULTA ORIGINAL: "{user_query}"
CONTENIDO GENERADO: {help_content}

INSTRUCCIONES PRINCIPALES:
1. Valida que el contenido responde la consulta del usuario
2. Genera respuesta profesional y útil para personal escolar
3. 🆕 AUTO-REFLEXIONA sobre tu respuesta

🧠 AUTO-REFLEXIÓN DE AYUDA:
Después de generar tu respuesta, reflexiona como un especialista en soporte:

ANÁLISIS REFLEXIVO:
- ¿La respuesta podría generar preguntas de seguimiento?
- ¿Mencioné funcionalidades que el usuario podría querer explorar?
- ¿Ofrecí ejemplos que podrían requerir más detalles?
- ¿Debería recordar el contexto de ayuda para futuras consultas?

DECISIÓN CONVERSACIONAL:
Si tu respuesta espera continuación, especifica:
- Tipo esperado: "tutorial_detallado|ejemplo_practico|exploracion_funcionalidad|none"
- Datos a recordar: información relevante para seguimiento
- Razonamiento: por qué esperas esta continuación

FORMATO DE RESPUESTA:
{{
  "respuesta_usuario": "Tu respuesta de ayuda completa aquí - profesional, clara y útil",
  "reflexion_conversacional": {{
    "espera_continuacion": true|false,
    "tipo_esperado": "tutorial_detallado|ejemplo_practico|exploracion_funcionalidad|none",
    "datos_recordar": {{
      "funcionalidad_explicada": "constancias|busquedas|estadisticas|ayuda_general",
      "nivel_detalle_proporcionado": "basico|intermedio|avanzado",
      "ejemplos_mencionados": ["ejemplo1", "ejemplo2"],
      "temas_relacionados": ["tema1", "tema2"]
    }},
    "razonamiento": "Explicación de por qué esperas o no esperas continuación"
  }}
}}

CRITERIOS PARA ESPERAR CONTINUACIÓN:
- Si explicas funcionalidades que tienen sub-opciones
- Si mencionas ejemplos que podrían necesitar más detalle
- Si introduces conceptos que podrían generar preguntas
- Si ofreces múltiples opciones al usuario

TONO: Profesional pero amigable, como un colega educativo experto

RESPONDE ÚNICAMENTE CON EL JSON, sin explicaciones adicionales.
"""

    def get_tutorial_prompt(self, user_query: str, tutorial_type: str, detected_entities: Dict) -> str:
        """
        PROMPT CENTRALIZADO: Genera tutoriales paso a paso

        REEMPLAZA: TutorialProcessor._build_tutorial_prompt()

        Args:
            user_query: Consulta original del usuario
            tutorial_type: Tipo de tutorial (consultas, constancias, sistema, etc.)
            detected_entities: Entidades detectadas

        Returns:
            Prompt para generar tutorial detallado
        """
        return f"""
Eres un especialista en crear TUTORIALES PASO A PASO para sistema escolar.

CONTEXTO DEL SISTEMA:
{self.system_context}

CONSULTA DEL USUARIO: "{user_query}"
TIPO DE TUTORIAL: {tutorial_type}
ENTIDADES DETECTADAS: {detected_entities}

INSTRUCCIONES PARA TUTORIAL DE {tutorial_type.upper()}:
1. CREA pasos específicos y claros
2. INCLUYE ejemplos reales que funcionen
3. PROPORCIONA consejos prácticos
4. ANTICIPA problemas comunes
5. OFRECE alternativas cuando sea apropiado

FORMATO DE RESPUESTA:
{{
    "tipo_tutorial": "{tutorial_type}",
    "titulo": "Título descriptivo del tutorial",
    "descripcion": "Qué aprenderá el usuario",
    "pasos": [
        {{
            "numero": 1,
            "titulo": "Título del paso",
            "descripcion": "Qué hacer en este paso",
            "ejemplo": "Ejemplo específico",
            "consejos": ["consejo1", "consejo2"]
        }}
    ],
    "ejemplos_completos": [
        {{
            "titulo": "Ejemplo práctico completo",
            "descripcion": "Caso de uso real",
            "pasos_ejemplo": ["acción1", "acción2", "resultado"]
        }}
    ],
    "problemas_comunes": [
        {{
            "problema": "Descripción del problema",
            "solucion": "Cómo resolverlo"
        }}
    ],
    "consejos_adicionales": ["consejo1", "consejo2"],
    "siguientes_pasos": ["qué hacer después", "cómo profundizar"]
}}

EJEMPLOS ESPECÍFICOS PARA {tutorial_type.upper()}:
{self._get_tutorial_examples(tutorial_type)}

RESPONDE ÚNICAMENTE CON EL JSON, sin explicaciones adicionales.
"""

    def _build_system_context(self) -> str:
        """Construye el contexto completo del sistema para todos los prompts"""
        return """
SISTEMA: Gestión Escolar Inteligente
ESCUELA: "PROF. MAXIMO GAMIZ FERNANDEZ"
CICLO: 2024-2025

🎯 COMPORTAMIENTO REAL DEL SISTEMA:

1. CONSULTAS DE ALUMNOS:
   ✅ FUNCIONAMIENTO REAL:
   - Escribe en lenguaje natural: "cuántos alumnos hay", "buscar García"
   - El sistema detecta automáticamente la intención
   - Genera SQL automáticamente y ejecuta la consulta
   - Responde con datos reales de la base de datos (211 alumnos)
   - Mantiene contexto conversacional para preguntas de seguimiento

   ✅ BÚSQUEDAS AVANZADAS DISPONIBLES:
   - Por nombre: "buscar García", "buscar Juan López"
   - Por grado: "alumnos de 2do grado", "estudiantes de sexto"
   - Por grupo: "alumnos del grupo A", "estudiantes de 3B"
   - Por turno: "alumnos del turno matutino"
   - Combinadas: "alumnos de 2do grado grupo A turno matutino"

   ✅ ESTADÍSTICAS AUTOMÁTICAS:
   - "cuántos alumnos hay" → "211 alumnos registrados"
   - "alumnos por grado" → Distribución completa
   - "alumnos con calificaciones" → Solo los que tienen notas
   - "alumnos sin calificaciones" → Los que no tienen notas

   ✅ INFORMACIÓN DETALLADA:
   - Datos personales: nombre, CURP, matrícula, fecha nacimiento
   - Datos escolares: grado, grupo, turno, ciclo escolar
   - Calificaciones: por materia y periodo (si están disponibles)

2. GENERACIÓN DE CONSTANCIAS:
   ✅ PROCESO REAL PASO A PASO:

   PASO 1: Identificar al alumno
   - Primero busca al alumno: "buscar Juan Pérez"
   - O usa referencia contextual: "para ese alumno" (si ya se buscó antes)

   PASO 2: Solicitar constancia específica
   - Especifica el tipo: "constancia de estudios para Juan Pérez"
   - Tipos disponibles: estudios, calificaciones, traslado

   PASO 3: Vista previa automática
   - El sistema SIEMPRE genera una vista previa primero
   - Se abre automáticamente el PDF de vista previa
   - El usuario puede revisar antes de confirmar

   PASO 4: Confirmación (opcional)
   - El usuario puede confirmar o cancelar
   - Si confirma, se genera la versión final

   ✅ REGLAS IMPORTANTES:
   - Constancias de calificaciones/traslado: SOLO para alumnos CON calificaciones
   - Constancias de estudios: Para CUALQUIER alumno registrado
   - SIEMPRE se genera vista previa primero
   - El PDF se abre automáticamente para revisión

3. TRANSFORMACIÓN DE PDFs:
   ✅ FUNCIONALIDAD COMPLETA (NO DISPONIBLE EN CHAT):
   - Cargar PDF externo del usuario
   - Extracción automática de datos del PDF
   - Selección de tipo de constancia a generar
   - Vista previa del resultado transformado
   - Opción de guardar alumno en base de datos

   ✅ CASOS DE USO REALES:
   - Convertir constancias de otros formatos al formato oficial
   - Estandarizar documentos existentes
   - Agregar alumnos desde PDFs externos a la base de datos
   - Actualizar formato de constancias antiguas

   ⚠️ NOTA: Esta funcionalidad requiere la interfaz tradicional (main_qt.py)

4. SISTEMA CONVERSACIONAL:
   ✅ CARACTERÍSTICAS REALES:
   - Mantiene contexto de conversaciones anteriores
   - Entiende referencias como "ese alumno", "del segundo", "para él"
   - Auto-reflexiona para sugerir acciones de seguimiento
   - Detecta automáticamente si necesitas constancias después de buscar alumnos

   ✅ FLUJO TÍPICO REAL:
   1. Usuario: "buscar García"
   2. Sistema: Muestra lista de García
   3. Sistema auto-reflexiona: "¿Necesitas constancia para alguno?"
   4. Usuario: "constancia de estudios para el primero"
   5. Sistema: Genera vista previa automáticamente

5. INTERFACES DISPONIBLES:
   ✅ CHAT CONVERSACIONAL (ACTUAL):
   - Consultas de alumnos en lenguaje natural
   - Generación de constancias con contexto
   - Ayuda del sistema
   - Mantenimiento de contexto conversacional

   ✅ INTERFAZ TRADICIONAL (main_qt.py):
   - Transformación de PDFs externos
   - Gestión completa de alumnos (agregar, modificar, eliminar)
   - Búsqueda avanzada con filtros visuales
   - Administración de base de datos

   ⚠️ LIMITACIONES DEL CHAT:
   - NO puede modificar datos de alumnos existentes
   - NO puede eliminar alumnos
   - NO puede transformar PDFs externos
   - NO puede acceder a administración de BD

6. AYUDA CONTEXTUAL:
   ✅ RESPUESTAS BASADAS EN COMPORTAMIENTO REAL:
   - Explica exactamente cómo funciona el sistema
   - Da ejemplos que realmente funcionan
   - Menciona características específicas como vista previa automática
   - Incluye reglas de negocio reales (ej: calificaciones requeridas)
   - Distingue entre funcionalidades del chat vs interfaz tradicional

DATOS REALES DISPONIBLES:
- 211 alumnos registrados actualmente
- Grados: 1°, 2°, 3°, 4°, 5°, 6°
- Grupos: A, B, C
- Turnos: Matutino, Vespertino
- Información completa: nombres, CURPs, matrículas, fechas, calificaciones
- Base de datos SQLite en tiempo real
"""

    def _get_tutorial_examples(self, tutorial_type: str) -> str:
        """Obtiene ejemplos específicos según el tipo de tutorial"""
        examples_map = {
            "consultas": """
- "cuántos alumnos hay" → Cuenta total de estudiantes
- "buscar García" → Encuentra alumnos con apellido García
- "alumnos de 2do grado" → Lista estudiantes de segundo grado
- "dame la CURP de Juan López" → Obtiene información específica
""",
            "constancias": """
PROCESO REAL PASO A PASO:

1. BUSCAR ALUMNO PRIMERO:
   - "buscar Juan Pérez" → Sistema encuentra al alumno
   - "buscar García" → Sistema muestra lista de García

2. SOLICITAR CONSTANCIA CON REFERENCIA:
   - "constancia de estudios para Juan Pérez" → Genera vista previa automática
   - "constancia de estudios para ese alumno" → Usa contexto conversacional
   - "constancia para el primero" → Usa posición en lista anterior

3. TIPOS DISPONIBLES:
   - "constancia de estudios" → Para CUALQUIER alumno (siempre disponible)
   - "constancia de calificaciones" → SOLO alumnos CON calificaciones
   - "constancia de traslado" → SOLO alumnos CON calificaciones

4. VISTA PREVIA AUTOMÁTICA:
   - El sistema SIEMPRE genera vista previa primero
   - Se abre PDF automáticamente para revisión
   - Usuario puede confirmar o cancelar después

EJEMPLOS REALES QUE FUNCIONAN:
- Usuario: "buscar CAMILA VARGAS" → Sistema: "Encontré a CAMILA VARGAS GUTIERREZ"
- Usuario: "constancia de estudios para ella" → Sistema: Genera vista previa automática
""",
            "sistema": """
- Escribir consultas en lenguaje natural
- Interpretar respuestas del sistema
- Usar funcionalidades de seguimiento
- Obtener ayuda contextual
""",
            "navegacion": """
- Usar el chat conversacional
- Interpretar respuestas del sistema
- Hacer preguntas de seguimiento
- Acceder a diferentes funcionalidades
""",
            "ejemplos": """
- Casos de uso reales del día a día escolar
- Consultas típicas del personal administrativo
- Procesos comunes de generación de documentos
"""
        }

        return examples_map.get(tutorial_type, "Ejemplos generales del sistema")
