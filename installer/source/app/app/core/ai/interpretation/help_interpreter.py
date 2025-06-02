"""
🎯 HELP INTERPRETER SIMPLIFICADO
Interpretador básico de ayuda sin contexto propio para evitar interferencias.
"""

from typing import Optional
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger

class HelpInterpreter(BaseInterpreter):
    """Interpretador simplificado de ayuda del sistema - SIN CONTEXTO PROPIO"""

    def __init__(self, gemini_client):
        super().__init__("HelpInterpreter")
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.logger.debug("✅ HelpInterpreter SIMPLIFICADO inicializado")

    def _get_supported_actions(self):
        """Acciones soportadas por el intérprete de ayuda"""
        return ["ayuda_sistema", "ayuda_error"]

    def can_handle(self, context: InterpretationContext) -> bool:
        """El MasterInterpreter ya decidió que somos el intérprete correcto"""
        return True

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        🎯 HELP INTERPRETER CON FLUJO COMO STUDENT

        Sigue el patrón del StudentInterpreter:
        1. Recibe intención + sub-intención del Master
        2. Ejecuta acción específica basada en sub-intención
        3. Retorna datos estructurados para respuesta humanizada del Master
        """
        try:
            self.logger.info(f"🔄 [HELP] Iniciando procesamiento: '{context.user_message[:50]}...'")

            # 🎯 OBTENER INFORMACIÓN DEL MASTER (COMO STUDENT)
            intention_info = getattr(context, 'intention_info', {})
            sub_intention = intention_info.get('sub_intention', 'entender_capacidades')
            detected_entities = intention_info.get('detected_entities', {})

            self.logger.info(f"📥 [HELP] Sub-intención del Master: {sub_intention}")
            self.logger.info(f"📥 [HELP] Entidades detectadas: {len(detected_entities)}")

            # 🎯 EJECUTAR ACCIÓN ESPECÍFICA BASADA EN SUB-INTENCIÓN
            if sub_intention in ["entender_capacidades", "pregunta_capacidades"]:
                return self._execute_capacidades_action(context.user_message, detected_entities)

            elif sub_intention in ["tutorial_uso", "pregunta_tecnica", "como_usar"]:
                return self._execute_tutorial_action(context.user_message, detected_entities)

            else:
                # Fallback: Si no reconoce la sub-intención, mostrar capacidades
                self.logger.info(f"⚠️ [HELP] Sub-intención no reconocida: {sub_intention} → mostrando capacidades")
                return self._execute_capacidades_action(context.user_message, detected_entities)

        except Exception as e:
            self.logger.error(f"Error en HelpInterpreter: {e}")
            return self._create_error_result("Error interno procesando ayuda")

    def _execute_capacidades_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """Ejecuta acción para explicar capacidades REALES del sistema basadas en pruebas validadas"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: CAPACIDADES")

            help_content = {
                "tipo": "capacidades_sistema",
                "titulo": "¿Qué puedo hacer? - Sistema Escolar PROF. MAXIMO GAMIZ FERNANDEZ",
                "contenido": {
                    "busquedas_por_apellido": {
                        "descripcion": "Buscar alumnos por apellidos (✅ Probado A1.1-A1.5)",
                        "ejemplos_reales": [
                            "busca alumnos con apellido MARTINEZ TORRES",
                            "estudiantes apellido DIAZ RODRIGUEZ",
                            "dame los RAMOS GUTIERREZ",
                            "buscar HERNANDEZ MENDOZA"
                        ],
                        "nota": "✅ Funciona con apellidos compuestos reales"
                    },
                    "busquedas_por_nombre_completo": {
                        "descripcion": "Buscar por nombre y apellidos completos (✅ Probado A2.1-A2.5)",
                        "ejemplos_reales": [
                            "buscar SOPHIA ROMERO GARCIA",
                            "información de ANDRES FLORES SANCHEZ",
                            "dame datos de ADRIANA TORRES RODRIGUEZ",
                            "estudiante PATRICIA TORRES TORRES"
                        ],
                        "nota": "✅ Búsqueda exacta con nombres completos"
                    },
                    "busquedas_por_criterios_academicos": {
                        "descripcion": "Filtrar por grado, grupo y turno (✅ Probado A3.1-A3.5)",
                        "ejemplos_reales": [
                            "alumnos de 2 grado",
                            "estudiantes del turno VESPERTINO",
                            "alumnos de 3° A",
                            "estudiantes de 5 grado turno MATUTINO",
                            "alumnos del grupo B turno VESPERTINO"
                        ],
                        "nota": "✅ Con interfaz colapsable para listas grandes"
                    },
                    "constancias_pdf_completas": {
                        "descripcion": "Generar documentos oficiales en PDF (✅ Probado B1.1-B2.4)",
                        "tipos_validados": ["estudios", "calificaciones", "traslado"],
                        "ejemplos_reales": [
                            "constancia para NICOLAS GOMEZ DIAZ",
                            "constancia de estudios para ANDRES RUIZ SANCHEZ",
                            "constancia con foto para NATALIA MORALES SILVA",
                            "constancia para SOPHIA ROMERO GARCIA sin foto",
                            "constancia de traslado para ADRIANA TORRES RODRIGUEZ"
                        ],
                        "nota": "✅ Genera PDFs reales instantáneamente"
                    },
                    "estadisticas_y_conteos": {
                        "descripcion": "Obtener números y distribuciones (✅ Probado A5.1-A5.5)",
                        "ejemplos_reales": [
                            "cuántos alumnos hay en total",
                            "distribución por grado",
                            "estadísticas por turno",
                            "cuántos alumnos hay en 6 grado",
                            "estudiantes sin calificaciones",
                            "alumnos que tienen notas"
                        ],
                        "nota": "✅ Con interfaz colapsable automática"
                    },
                    "continuaciones_contextuales": {
                        "descripcion": "Filtrar y refinar búsquedas anteriores (✅ Probado B3.1-B3.3)",
                        "ejemplos_reales": [
                            "1. 'alumnos de segundo grado' → 2. 'de esos los del turno vespertino'",
                            "1. 'buscar MARTINEZ' → 2. 'constancia para el primero'",
                            "1. 'estudiantes de 3° A' → 2. 'constancia para el tercer alumno de la lista'"
                        ],
                        "nota": "✅ Referencias como 'el segundo', 'de esos', 'el primero'"
                    },
                    "filtros_de_calificaciones": {
                        "descripcion": "Buscar por estado de calificaciones (✅ Probado A4.4-A4.5)",
                        "ejemplos_reales": [
                            "estudiantes sin calificaciones",
                            "alumnos que tienen notas",
                            "estudiantes con calificaciones registradas"
                        ],
                        "nota": "✅ Verificación básica implementada"
                    }
                },
                "datos_sistema": {
                    "total_alumnos": 211,
                    "grados": "1° a 6° grado",
                    "turnos": ["MATUTINO", "VESPERTINO"],
                    "grupos": ["A", "B"],
                    "estado_pruebas": "✅ 25+ casos críticos validados en BATERIA_PRUEBAS_MASTER_STUDENT.md"
                }
            }

            return self._create_success_result("AYUDA_CAPACIDADES", help_content, "Capacidades reales del sistema explicadas")

        except Exception as e:
            self.logger.error(f"Error en acción capacidades: {e}")
            return self._create_error_result("Error explicando capacidades")

    def _execute_tutorial_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """Ejecuta acción para generar tutoriales basados en casos REALES probados"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: TUTORIAL")

            help_content = {
                "tipo": "tutorial_uso",
                "titulo": "Tutorial Paso a Paso - Casos Reales Probados",
                "pasos": [
                    {
                        "paso": 1,
                        "titulo": "🔍 Búsquedas Básicas (✅ Probado)",
                        "descripcion": "Buscar alumnos por nombre, apellido o criterios académicos",
                        "ejemplos_reales": [
                            "buscar MARTINEZ TORRES",
                            "estudiante PATRICIA TORRES TORRES",
                            "alumnos de 3° A",
                            "estudiantes del turno vespertino"
                        ],
                        "resultado": "Lista de alumnos con interfaz colapsable si son muchos"
                    },
                    {
                        "paso": 2,
                        "titulo": "📄 Generar Constancias (✅ Probado)",
                        "descripcion": "Crear documentos PDF oficiales directamente",
                        "ejemplos_reales": [
                            "constancia para NICOLAS GOMEZ DIAZ",
                            "constancia de estudios para ANDRES RUIZ SANCHEZ",
                            "constancia con foto para NATALIA MORALES SILVA"
                        ],
                        "resultado": "PDF generado automáticamente en panel derecho"
                    },
                    {
                        "paso": 3,
                        "titulo": "🔄 Continuaciones Inteligentes (✅ Probado)",
                        "descripcion": "Filtrar y refinar resultados anteriores",
                        "ejemplos_reales": [
                            "1. 'alumnos de segundo grado' → 2. 'de esos los del turno vespertino'",
                            "1. 'buscar MARTINEZ' → 2. 'constancia para el primero'"
                        ],
                        "resultado": "Sistema recuerda búsquedas anteriores automáticamente"
                    },
                    {
                        "paso": 4,
                        "titulo": "📊 Estadísticas y Conteos (✅ Probado)",
                        "descripcion": "Obtener números y distribuciones del sistema",
                        "ejemplos_reales": [
                            "cuántos alumnos hay en total",
                            "distribución por grado",
                            "estadísticas por turno"
                        ],
                        "resultado": "Datos organizados con interfaz colapsable"
                    }
                ],
                "consejos": [
                    "💡 Usa nombres COMPLETOS para mejores resultados",
                    "💡 El sistema recuerda tu búsqueda anterior automáticamente",
                    "💡 Puedes referenciar 'el primero', 'el segundo', etc.",
                    "💡 Las constancias se generan como PDF real instantáneamente"
                ]
            }

            return self._create_success_result("AYUDA_TUTORIAL", help_content, "Tutorial con casos reales generado")

        except Exception as e:
            self.logger.error(f"Error en acción tutorial: {e}")
            return self._create_error_result("Error generando tutorial")

    # 🗑️ MÉTODOS ELIMINADOS PARA SIMPLIFICAR A SOLO 2 ACCIONES:
    # - _execute_tipos_constancias_action() → Incluido en CAPACIDADES
    # - _execute_como_usar_action() → Fusionado con TUTORIAL
    # - _execute_ayuda_general_action() → Fallback a CAPACIDADES

    def _create_success_result(self, action_name: str, help_content: dict, summary: str) -> InterpretationResult:
        """Crea resultado exitoso con datos estructurados para el Master"""
        help_data = {
            "technical_response": f"Ayuda generada: {action_name}",
            "data": help_content,
            "row_count": 1,
            "help_type": help_content.get("tipo", "general"),
            "query_category": "ayuda_sistema",
            "execution_summary": summary,
            "requires_master_response": True,  # ✅ Master debe generar respuesta humanizada
            "student_action": action_name,
            "origen": "help_interpreter"
        }

        return InterpretationResult(
            action=action_name,
            parameters=help_data,
            confidence=0.9
        )

    def _create_error_result(self, error_message: str) -> InterpretationResult:
        """Crea resultado de error"""
        return InterpretationResult(
            action="ayuda_error",
            parameters={
                "message": f"❌ {error_message}",
                "error": "help_processing_error"
            },
            confidence=0.3
        )

    def _generate_basic_help_response(self, user_query: str) -> Optional[str]:
        """
        🎯 GENERA RESPUESTA BÁSICA DE AYUDA SIN CONTEXTO
        
        Responde consultas comunes sobre el sistema de manera simple y directa.
        """
        try:
            # 🎯 PROMPT SIMPLIFICADO PARA AYUDA BÁSICA
            help_prompt = f"""
Eres el asistente de ayuda de la escuela "PROF. MAXIMO GAMIZ FERNANDEZ" 🏫

CONSULTA DEL USUARIO: "{user_query}"

🎯 INFORMACIÓN DEL SISTEMA:
- Base de datos: 211 alumnos de 1° a 6° grado
- Turnos: MATUTINO y VESPERTINO
- Grupos: A, B (principalmente)
- Funcionalidades principales:
  * Búsqueda de alumnos por nombre, grado, grupo, turno
  * Generación de constancias (estudios, calificaciones, traslado)
  * Estadísticas y conteos
  * Transformación de PDFs

🎯 CAPACIDADES PRINCIPALES:

**1. BÚSQUEDA DE ALUMNOS:**
- "buscar [nombre]" - Busca por nombre
- "alumnos de [grado]° [grupo]" - Por grado y grupo
- "estudiantes del turno [matutino/vespertino]" - Por turno
- "cuántos alumnos hay en [criterio]" - Conteos

**2. CONSTANCIAS:**
- "constancia de estudios para [nombre]" - Constancia básica
- "constancia de calificaciones para [nombre]" - Con notas
- "constancia de traslado para [nombre]" - Para cambio de escuela

**3. ESTADÍSTICAS:**
- "cuántos alumnos hay" - Total general
- "distribución por grados" - Estadísticas por grado
- "alumnos por turno" - Estadísticas por turno

**4. EJEMPLOS PRÁCTICOS:**
- "buscar García" → Encuentra alumnos con apellido García
- "alumnos de 3° A" → Lista estudiantes de tercer grado grupo A
- "constancia de estudios para Juan Pérez" → Genera constancia
- "cuántos hay en turno matutino" → Cuenta alumnos del turno

🎭 TU TAREA:
Responde de manera amigable y práctica, explicando:
1. Qué puede hacer el sistema relacionado con su pregunta
2. Ejemplos específicos de cómo usar las funciones
3. Sugerencias útiles para aprovechar mejor el sistema

RESPONDE de manera conversacional, amigable y práctica. Máximo 4-5 líneas.
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(help_prompt)
            
            if response and response.strip():
                return response.strip()
            else:
                # Fallback básico
                return self._get_fallback_help_response(user_query)

        except Exception as e:
            self.logger.error(f"Error generando respuesta básica de ayuda: {e}")
            return self._get_fallback_help_response(user_query)

    def _get_fallback_help_response(self, user_query: str) -> str:
        """Respuesta de fallback cuando el LLM no está disponible"""
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ["qué puedes", "qué haces", "capacidades", "funciones"]):
            return """¡Hola! 👋 Soy tu asistente escolar. Puedo ayudarte con:

📚 **Búsquedas**: "buscar [nombre]", "alumnos de 3° A"
📄 **Constancias**: "constancia de estudios para [nombre]"
📊 **Estadísticas**: "cuántos alumnos hay", "distribución por grados"

¡Pregúntame lo que necesites sobre los 211 estudiantes de nuestra escuela!"""

        elif any(word in query_lower for word in ["constancia", "certificado", "documento"]):
            return """Para generar constancias:

1. **Busca al alumno**: "buscar [nombre del alumno]"
2. **Solicita la constancia**: "constancia de [tipo] para [nombre]"

**Tipos disponibles**: estudios, calificaciones, traslado
**Ejemplo**: "constancia de estudios para Juan Pérez"

¡El sistema genera automáticamente una vista previa para revisión!"""

        elif any(word in query_lower for word in ["buscar", "encontrar", "alumno"]):
            return """Para buscar alumnos puedes usar:

🔍 **Por nombre**: "buscar García", "buscar María"
🎓 **Por grado**: "alumnos de 3° A", "estudiantes de 2do grado"
🕐 **Por turno**: "alumnos del turno matutino"
📊 **Conteos**: "cuántos hay en 4° grado"

¡Prueba con cualquier combinación de criterios!"""

        else:
            return """¡Hola! 👋 Soy tu asistente para la escuela "PROF. MAXIMO GAMIZ FERNANDEZ".

Puedo ayudarte con búsquedas de alumnos, generar constancias y estadísticas.

**Ejemplos útiles**:
- "buscar López" - Busca alumnos
- "constancia de estudios para Juan Pérez" - Genera documentos
- "cuántos alumnos hay en 3° grado" - Estadísticas

¿En qué te puedo ayudar específicamente?"""
