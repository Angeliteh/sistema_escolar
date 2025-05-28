"""
Interpretador especializado en consultas de ayuda del sistema
Implementa la filosofía de dominios funcionales con auto-reflexión integrada.

DOMINIO: Sistema de Ayuda
- Explicación de funcionalidades
- Tutoriales paso a paso
- Solución de problemas
- Ejemplos prácticos
- Guías contextuales
"""

from typing import Optional, Dict
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger

# ✅ CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR)
from .help_query.help_content_generator import HelpContentGenerator
from .help_query.help_response_generator import HelpResponseGenerator
from .help_query.tutorial_processor import TutorialProcessor
from .help_query.capability_analyzer import CapabilityAnalyzer
from .utils.json_parser import JSONParser

class HelpInterpreter(BaseInterpreter):
    """Interpretador especializado en consultas de ayuda del sistema"""

    def __init__(self, gemini_client):
        super().__init__("HelpInterpreter")
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # ✅ INICIALIZAR CLASES ESPECIALIZADAS (ARQUITECTURA MODULAR)
        self.help_content_generator = HelpContentGenerator(gemini_client)
        self.help_response_generator = HelpResponseGenerator(gemini_client)
        self.tutorial_processor = TutorialProcessor(gemini_client)
        self.capability_analyzer = CapabilityAnalyzer()
        self.json_parser = JSONParser()

        self.logger.debug("✅ HelpInterpreter inicializado con clases especializadas")

    def _get_supported_actions(self):
        """Acciones soportadas por el intérprete de ayuda"""
        return [
            "ayuda_funcionalidades",
            "ayuda_tutorial",
            "ayuda_ejemplo",
            "ayuda_solucion",
            "ayuda_error"
        ]

    def can_handle(self, context: InterpretationContext) -> bool:
        """El MasterInterpreter ya decidió que somos el intérprete correcto"""
        return True

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        Interpreta consultas de ayuda usando el flujo optimizado de 4 prompts
        ARQUITECTURA: PROMPT 0 → PROMPT 1 → PROMPT 2 → PROMPT 3
        """
        try:
            # 🔄 [HELP] INICIANDO PROCESAMIENTO
            self.logger.info(f"🔄 [HELP] Iniciando procesamiento: '{context.user_message[:50]}...'")

            # Obtener información de intención del Master
            intention_info = getattr(context, 'intention_info', {})
            sub_intention = intention_info.get('sub_intention', '')
            detected_entities = intention_info.get('detected_entities', {})

            self.logger.info(f"   ├── Sub-intención: {sub_intention}")
            self.logger.info(f"   └── Entidades: {len(detected_entities)} detectadas")

            # 🚀 FLUJO DIRECTO USANDO ENTIDADES PRE-DETECTADAS
            if sub_intention == "entender_capacidades":
                self.logger.info("🎯 SUB-INTENCIÓN: ENTENDER CAPACIDADES")
                return self._process_capabilities_help(context.user_message, detected_entities)

            elif sub_intention == "tutorial_paso_a_paso":
                self.logger.info("🎯 SUB-INTENCIÓN: TUTORIAL PASO A PASO")
                return self._process_tutorial_help(context.user_message, detected_entities)

            elif sub_intention == "solucion_problema":
                self.logger.info("🎯 SUB-INTENCIÓN: SOLUCIÓN DE PROBLEMA")
                return self._process_problem_solution(context.user_message, detected_entities)

            elif sub_intention == "ejemplo_practico":
                self.logger.info("🎯 SUB-INTENCIÓN: EJEMPLO PRÁCTICO")
                return self._process_practical_example(context.user_message, detected_entities)

            # 🎯 PROMPT 1: DETECCIÓN DE CONTINUACIÓN (PATRÓN ESTÁNDAR)
            if hasattr(context, 'conversation_stack') and context.conversation_stack:
                self.logger.info("📚 VERIFICANDO PILA CONVERSACIONAL DE AYUDA")
                continuation_info = self._detect_help_continuation(context.user_message, context.conversation_stack)

                if continuation_info and continuation_info.get('es_continuacion', False):
                    self.logger.info(f"✅ CONTINUACIÓN DE AYUDA DETECTADA: {continuation_info.get('tipo_continuacion', 'unknown')}")
                    return self._process_help_continuation(context.user_message, continuation_info, context.conversation_stack)
                else:
                    self.logger.info("❌ NO ES CONTINUACIÓN DE AYUDA")
            else:
                self.logger.info("❌ NO HAY PILA CONVERSACIONAL DE AYUDA disponible")

            # 🎯 PROMPT 2: GENERACIÓN DE CONTENIDO DE AYUDA
            help_content = self._generate_help_content(context.user_message, context)

            if not help_content:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ No pude generar contenido de ayuda para tu consulta. ¿Podrías ser más específico?",
                        "error": "content_generation_failed"
                    },
                    confidence=0.3
                )

            # 🎯 PROMPT 3: RESPUESTA + AUTO-REFLEXIÓN (PATRÓN ESTÁNDAR)
            response_with_reflection = self._validate_and_generate_help_response(
                context.user_message, help_content
            )

            if response_with_reflection:
                # Determinar tipo de acción basado en el contenido
                action_type = self._determine_help_action_type(help_content)

                self.logger.info(f"📊 [HELP] Ayuda generada exitosamente: {action_type}")
                return InterpretationResult(
                    action=action_type,
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Ayuda generada"),
                        "help_content": help_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "help_interpreter"
                    },
                    confidence=0.9
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ Error generando respuesta de ayuda. Intenta reformular tu pregunta.",
                        "error": "response_generation_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error en HelpInterpreter: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error interno procesando tu consulta de ayuda. Intenta nuevamente.",
                    "error": "internal_error",
                    "exception": str(e)
                },
                confidence=0.1
            )

    def _process_capabilities_help(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa consultas sobre capacidades del sistema usando entidades pre-detectadas"""
        try:
            self.logger.info("🎯 PROCESANDO CAPACIDADES DEL SISTEMA")

            # Usar CapabilityAnalyzer para generar contenido
            capabilities_content = self.capability_analyzer.analyze_system_capabilities(user_query, detected_entities)

            if capabilities_content:
                # Generar respuesta con auto-reflexión
                response_with_reflection = self._validate_and_generate_help_response(user_query, capabilities_content)

                return InterpretationResult(
                    action="ayuda_funcionalidades",
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Funcionalidades del sistema"),
                        "capabilities": capabilities_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "capabilities_direct"
                    },
                    confidence=0.95
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ No pude analizar las capacidades solicitadas",
                        "error": "capabilities_analysis_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando capacidades: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error analizando capacidades del sistema",
                    "error": "capabilities_error"
                },
                confidence=0.1
            )

    def _process_tutorial_help(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa solicitudes de tutoriales paso a paso"""
        try:
            self.logger.info("🎯 PROCESANDO TUTORIAL PASO A PASO")

            # Usar TutorialProcessor para generar tutorial
            tutorial_content = self.tutorial_processor.generate_tutorial(user_query, detected_entities)

            if tutorial_content:
                response_with_reflection = self._validate_and_generate_help_response(user_query, tutorial_content)

                return InterpretationResult(
                    action="ayuda_tutorial",
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Tutorial generado"),
                        "tutorial": tutorial_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": "tutorial_direct"
                    },
                    confidence=0.95
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": "❌ No pude generar el tutorial solicitado",
                        "error": "tutorial_generation_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando tutorial: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error generando tutorial",
                    "error": "tutorial_error"
                },
                confidence=0.1
            )

    def _process_problem_solution(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa consultas de solución de problemas"""
        # Implementación similar a los métodos anteriores
        # Por ahora, usar el flujo general
        return self._process_general_help(user_query, detected_entities, "solucion_problema")

    def _process_practical_example(self, user_query: str, detected_entities: Dict) -> InterpretationResult:
        """Procesa solicitudes de ejemplos prácticos"""
        # Implementación similar a los métodos anteriores
        # Por ahora, usar el flujo general
        return self._process_general_help(user_query, detected_entities, "ejemplo_practico")

    def _process_general_help(self, user_query: str, detected_entities: Dict, help_type: str) -> InterpretationResult:
        """Procesa consultas generales de ayuda"""
        try:
            self.logger.info(f"🎯 PROCESANDO AYUDA GENERAL: {help_type}")

            # Generar contenido usando HelpContentGenerator
            help_content = self.help_content_generator.generate_content(user_query, help_type, detected_entities)

            if help_content:
                response_with_reflection = self._validate_and_generate_help_response(user_query, help_content)

                action_map = {
                    "solucion_problema": "ayuda_solucion",
                    "ejemplo_practico": "ayuda_ejemplo"
                }

                return InterpretationResult(
                    action=action_map.get(help_type, "ayuda_funcionalidades"),
                    parameters={
                        "message": response_with_reflection.get("respuesta_usuario", "Ayuda generada"),
                        "help_content": help_content,
                        "auto_reflexion": response_with_reflection.get("reflexion_conversacional", {}),
                        "origen": f"{help_type}_direct"
                    },
                    confidence=0.9
                )
            else:
                return InterpretationResult(
                    action="ayuda_error",
                    parameters={
                        "message": f"❌ No pude generar ayuda para {help_type}",
                        "error": f"{help_type}_failed"
                    },
                    confidence=0.3
                )

        except Exception as e:
            self.logger.error(f"Error procesando ayuda general: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error procesando consulta de ayuda",
                    "error": "general_help_error"
                },
                confidence=0.1
            )

    def _detect_help_continuation(self, user_query: str, conversation_stack: list) -> Optional[Dict]:
        """Detecta si la consulta es continuación de ayuda previa usando contexto inteligente"""
        try:
            if not conversation_stack:
                return {"es_continuacion": False, "tipo_continuacion": "none"}

            # Obtener último nivel de la pila
            ultimo_nivel = conversation_stack[-1]

            # Crear prompt para detectar continuación de ayuda
            continuation_prompt = f"""
Eres un experto en análisis conversacional para sistema de ayuda escolar.

CONTEXTO DE LA CONVERSACIÓN ANTERIOR:
- Consulta previa: "{ultimo_nivel.get('query', '')}"
- Datos mostrados: {ultimo_nivel.get('row_count', 0)} elementos
- Contexto: {ultimo_nivel.get('context', '')}

CONSULTA ACTUAL: "{user_query}"

ANALIZA si la consulta actual es una CONTINUACIÓN que requiere usar el contexto anterior:

TIPOS DE CONTINUACIÓN DE AYUDA:
1. "explicacion_constancia" - Pregunta cómo obtener constancia para alumno específico del contexto
2. "tutorial_especifico" - Pide tutorial usando datos del contexto
3. "aclaracion_proceso" - Necesita aclaración sobre proceso mencionado
4. "ejemplo_contextual" - Pide ejemplo usando datos específicos del contexto

INDICADORES DE CONTINUACIÓN:
- Referencias: "ese alumno", "para él/ella", "del anterior", "que mostraste"
- Preguntas sobre procesos: "cómo obtener", "cómo generar", "qué hacer"
- Solicitudes específicas: "para [nombre]", "con esos datos"

RESPONDE ÚNICAMENTE con JSON:
{{
    "es_continuacion": true|false,
    "tipo_continuacion": "explicacion_constancia|tutorial_especifico|aclaracion_proceso|ejemplo_contextual|none",
    "confianza": 0.0-1.0,
    "razonamiento": "Por qué es/no es continuación",
    "datos_contextuales_necesarios": ["nombre_alumno", "datos_mostrados", "proceso_anterior"]
}}
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(continuation_prompt)

            if response:
                # Parsear respuesta JSON
                continuation_data = self.gemini_client.parse_json_response(response)
                if continuation_data:
                    return continuation_data

            # Fallback si LLM falla
            return {"es_continuacion": False, "tipo_continuacion": "none"}

        except Exception as e:
            self.logger.error(f"Error detectando continuación de ayuda: {e}")
            return {"es_continuacion": False, "tipo_continuacion": "none"}

    def _process_help_continuation(self, user_query: str, continuation_info: Dict, conversation_stack: list) -> InterpretationResult:
        """Procesa continuaciones de ayuda usando contexto inteligente"""
        try:
            tipo_continuacion = continuation_info.get('tipo_continuacion', 'none')
            self.logger.info(f"🎯 PROCESANDO CONTINUACIÓN DE AYUDA: {tipo_continuacion}")

            # Extraer datos del contexto
            ultimo_nivel = conversation_stack[-1] if conversation_stack else {}
            datos_contextuales = self._extract_contextual_data(ultimo_nivel)

            # Procesar según el tipo de continuación
            if tipo_continuacion == "explicacion_constancia":
                return self._process_constancia_explanation(user_query, datos_contextuales)
            elif tipo_continuacion == "tutorial_especifico":
                return self._process_contextual_tutorial(user_query, datos_contextuales)
            elif tipo_continuacion == "aclaracion_proceso":
                return self._process_process_clarification(user_query, datos_contextuales)
            elif tipo_continuacion == "ejemplo_contextual":
                return self._process_contextual_example(user_query, datos_contextuales)
            else:
                # Continuación genérica
                return self._process_generic_continuation(user_query, datos_contextuales)

        except Exception as e:
            self.logger.error(f"Error procesando continuación de ayuda: {e}")
            return InterpretationResult(
                action="ayuda_error",
                parameters={
                    "message": "❌ Error procesando tu consulta de seguimiento. Intenta reformular.",
                    "error": "continuation_error"
                },
                confidence=0.3
            )

    def _extract_contextual_data(self, ultimo_nivel: Dict) -> Dict:
        """Extrae datos útiles del contexto conversacional"""
        datos = {
            "query_anterior": ultimo_nivel.get('query', ''),
            "datos_mostrados": ultimo_nivel.get('data', []),
            "row_count": ultimo_nivel.get('row_count', 0),
            "context": ultimo_nivel.get('context', ''),
            "nombres_alumnos": [],
            "primer_alumno": None
        }

        # Extraer nombres de alumnos si hay datos
        if datos["datos_mostrados"]:
            for item in datos["datos_mostrados"]:
                if isinstance(item, dict) and 'nombre' in item:
                    datos["nombres_alumnos"].append(item['nombre'])

            # Primer alumno para referencias como "el primero"
            if datos["nombres_alumnos"]:
                datos["primer_alumno"] = datos["nombres_alumnos"][0]

        return datos

    def _process_constancia_explanation(self, user_query: str, datos_contextuales: Dict) -> InterpretationResult:
        """Procesa explicaciones sobre cómo obtener constancias usando contexto específico"""
        try:
            # Crear prompt contextual para explicar constancias
            primer_alumno = datos_contextuales.get("primer_alumno", "")
            query_anterior = datos_contextuales.get("query_anterior", "")

            contextual_prompt = f"""
Eres un experto en explicar el proceso de generación de constancias escolares.

CONTEXTO DE LA CONVERSACIÓN:
- Consulta anterior: "{query_anterior}"
- Alumno específico encontrado: "{primer_alumno}"
- Usuario pregunta: "{user_query}"

EXPLICA ESPECÍFICAMENTE cómo obtener una constancia para este alumno usando el sistema de chat:

PROCESO REAL PASO A PASO:
1. El alumno ya fue encontrado: "{primer_alumno}"
2. Para generar constancia, escribe: "constancia de [tipo] para {primer_alumno}"
3. Tipos disponibles: estudios, calificaciones, traslado
4. El sistema genera vista previa automáticamente
5. Se abre PDF para revisión

EJEMPLO ESPECÍFICO CON ESTE ALUMNO:
- "constancia de estudios para {primer_alumno}"
- "constancia de calificaciones para {primer_alumno}" (si tiene calificaciones)

RESPONDE con explicación clara y específica usando el nombre del alumno.
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(contextual_prompt)

            if response:
                return InterpretationResult(
                    action="ayuda_constancia_contextual",
                    parameters={
                        "message": response,
                        "alumno_contexto": primer_alumno,
                        "query_anterior": query_anterior,
                        "origen": "constancia_explanation_contextual"
                    },
                    confidence=0.95
                )
            else:
                return self._create_fallback_constancia_help(primer_alumno)

        except Exception as e:
            self.logger.error(f"Error en explicación contextual de constancia: {e}")
            return self._create_fallback_constancia_help(datos_contextuales.get("primer_alumno", ""))

    def _create_fallback_constancia_help(self, alumno_nombre: str) -> InterpretationResult:
        """Crea respuesta de fallback para ayuda de constancias"""
        if alumno_nombre:
            message = f"""
Para generar una constancia para {alumno_nombre}:

1. **Constancia de estudios**: Escribe "constancia de estudios para {alumno_nombre}"
2. **Constancia de calificaciones**: Escribe "constancia de calificaciones para {alumno_nombre}" (solo si tiene calificaciones)
3. **Constancia de traslado**: Escribe "constancia de traslado para {alumno_nombre}" (solo si tiene calificaciones)

El sistema generará automáticamente una vista previa que se abrirá para tu revisión.
"""
        else:
            message = """
Para generar constancias:

1. Primero busca al alumno: "buscar [nombre del alumno]"
2. Luego solicita la constancia: "constancia de [tipo] para ese alumno"
3. El sistema genera vista previa automáticamente

Tipos disponibles: estudios, calificaciones, traslado
"""

        return InterpretationResult(
            action="ayuda_constancia_fallback",
            parameters={
                "message": message,
                "origen": "fallback_constancia"
            },
            confidence=0.8
        )

    def _process_contextual_tutorial(self, user_query: str, datos_contextuales: Dict) -> InterpretationResult:
        """Procesa tutoriales usando datos específicos del contexto"""
        # Implementación básica por ahora
        return self._process_generic_continuation(user_query, datos_contextuales)

    def _process_process_clarification(self, user_query: str, datos_contextuales: Dict) -> InterpretationResult:
        """Procesa aclaraciones sobre procesos usando contexto"""
        # Implementación básica por ahora
        return self._process_generic_continuation(user_query, datos_contextuales)

    def _process_contextual_example(self, user_query: str, datos_contextuales: Dict) -> InterpretationResult:
        """Procesa ejemplos usando datos específicos del contexto"""
        # Implementación básica por ahora
        return self._process_generic_continuation(user_query, datos_contextuales)

    def _process_generic_continuation(self, user_query: str, datos_contextuales: Dict) -> InterpretationResult:
        """Procesa continuaciones genéricas con contexto"""
        primer_alumno = datos_contextuales.get("primer_alumno", "")
        query_anterior = datos_contextuales.get("query_anterior", "")

        message = f"""
Basándome en tu consulta anterior "{query_anterior}" y tu pregunta "{user_query}":

{f"Para el alumno {primer_alumno} que encontramos:" if primer_alumno else ""}

Puedo ayudarte con:
- Explicaciones sobre el proceso de constancias
- Tutoriales paso a paso
- Ejemplos específicos usando los datos mostrados
- Aclaraciones sobre cualquier funcionalidad

¿Qué específicamente te gustaría saber?
"""

        return InterpretationResult(
            action="ayuda_continuacion_generica",
            parameters={
                "message": message,
                "contexto_usado": True,
                "origen": "generic_continuation"
            },
            confidence=0.8
        )

    def _generate_help_content(self, user_query: str, context) -> Optional[Dict]:
        """Genera contenido de ayuda usando HelpContentGenerator"""
        try:
            # Determinar tipo de ayuda
            help_type = self._determine_help_type_from_query(user_query)

            # Usar HelpContentGenerator
            return self.help_content_generator.generate_content(user_query, help_type, {})

        except Exception as e:
            self.logger.error(f"Error generando contenido de ayuda: {e}")
            return None

    def _determine_help_type_from_query(self, user_query: str) -> str:
        """Determina el tipo de ayuda basado en la consulta"""
        query_lower = user_query.lower()

        if any(word in query_lower for word in ["problema", "error", "no funciona", "falla"]):
            return "solucion_problema"
        elif any(word in query_lower for word in ["ejemplo", "muestra", "demo"]):
            return "ejemplo_practico"
        elif any(word in query_lower for word in ["tutorial", "cómo", "paso a paso"]):
            return "tutorial_paso_a_paso"
        else:
            return "ayuda_general"

    def _validate_and_generate_help_response(self, user_query: str, help_content: Dict) -> Optional[Dict]:
        """Valida contenido y genera respuesta con auto-reflexión usando HelpResponseGenerator"""
        try:
            return self.help_response_generator.generate_response_with_reflection(user_query, help_content)
        except Exception as e:
            self.logger.error(f"Error generando respuesta de ayuda: {e}")
            return None

    def _determine_help_action_type(self, help_content: Dict) -> str:
        """Determina el tipo de acción basado en el contenido"""
        content_type = help_content.get("tipo_contenido", "ayuda_general")

        action_map = {
            "solucion_problema": "ayuda_solucion",
            "ejemplo_practico": "ayuda_ejemplo",
            "tutorial_paso_a_paso": "ayuda_tutorial",
            "ayuda_general": "ayuda_funcionalidades"
        }

        return action_map.get(content_type, "ayuda_funcionalidades")