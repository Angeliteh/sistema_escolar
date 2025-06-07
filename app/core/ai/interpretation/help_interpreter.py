"""
🎯 HELP INTERPRETER SIMPLIFICADO
Interpretador básico de ayuda sin contexto propio para evitar interferencias.
"""

from typing import Optional
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger
from app.core.ai.help_action_catalog import HelpActionCatalog

class HelpInterpreter(BaseInterpreter):
    """Interpretador simplificado de ayuda del sistema - SIN CONTEXTO PROPIO"""

    def __init__(self, gemini_client):
        super().__init__("HelpInterpreter")
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # 🆕 PROMPT MANAGER CENTRALIZADO (como Student)
        from app.core.ai.prompts.help_prompt_manager import HelpPromptManager
        self.prompt_manager = HelpPromptManager()
        self.logger.debug("✅ HelpInterpreter SIMPLIFICADO inicializado")

    def _get_supported_actions(self):
        """Acciones soportadas por el intérprete de ayuda"""
        return ["ayuda_sistema", "ayuda_error"]

    def can_handle(self, context: InterpretationContext) -> bool:
        """El MasterInterpreter ya decidió que somos el intérprete correcto"""
        return True

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        🎯 HELP INTERPRETER CON FLUJO LLM + FALLBACK HARDCODE

        FLUJO PRINCIPAL (LLM como Student):
        1. PROMPT 2: Mapeo inteligente de consulta → tipo de ayuda
        2. PROMPT 3: Preparación de respuesta técnica + auto-reflexión
        3. Master PROMPT 4: Respuesta humanizada final

        FALLBACK: Si LLM falla, usar respuestas hardcodeadas existentes
        """
        try:
            self.logger.info(f"🔄 [HELP] Iniciando procesamiento: '{context.user_message[:50]}...'")

            user_query = context.user_message
            conversation_stack = getattr(context, 'conversation_stack', [])

            # 🎯 INTENTAR FLUJO LLM PRIMERO (COMO STUDENT)
            if self.gemini_client:
                self.logger.info("🤖 [HELP] Intentando flujo LLM (como Student)")

                # PROMPT 2: Mapeo inteligente
                help_mapping_result = self._map_help_query_with_llm(user_query, conversation_stack)

                if help_mapping_result:
                    # PROMPT 3: Preparación de respuesta técnica
                    technical_response = self._prepare_help_response_with_llm(user_query, help_mapping_result, conversation_stack)

                    if technical_response:
                        # ✅ FLUJO LLM EXITOSO
                        self.logger.info("✅ [HELP] Flujo LLM completado exitosamente")
                        return self._create_help_interpretation_result(help_mapping_result, technical_response, user_query)

            # 🔄 FALLBACK: USAR RESPUESTAS HARDCODEADAS EXISTENTES
            self.logger.info("🔄 [HELP] Fallback a respuestas hardcodeadas")
            return self._execute_hardcoded_help_response(context)

        except Exception as e:
            self.logger.error(f"Error en HelpInterpreter: {e}")
            return self._create_error_result("Error interno procesando ayuda")

    def _execute_hardcoded_help_response(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        🔄 FALLBACK: Ejecutar respuestas usando HelpActionCatalog
        Usa el catálogo centralizado para mantener coherencia
        """
        try:
            # 🎯 OBTENER INFORMACIÓN DEL MASTER
            intention_info = getattr(context, 'intention_info', {})
            sub_intention = intention_info.get('sub_intention', 'explicacion_general')
            detected_entities = intention_info.get('detected_entities', {})

            self.logger.info(f"📥 [HELP] Sub-intención del Master: {sub_intention}")
            self.logger.info(f"📥 [HELP] Entidades detectadas: {len(detected_entities)}")

            # 🎯 USAR HELPACTIONCATALOG PARA MAPEAR SUB-INTENCIÓN
            mapping = HelpActionCatalog.get_sub_intention_mapping()

            if sub_intention in mapping:
                config = mapping[sub_intention]
                response_type = config["response_type"]
                self.logger.info(f"✅ [HELP] Mapeado: {sub_intention} → {response_type}")

                # Generar respuesta usando el catálogo centralizado
                return self._execute_centralized_help_response(sub_intention, context.user_message, config)

            # Fallback a mapeo legacy si no está en el catálogo
            if sub_intention in ["explicacion_general", "entender_capacidades", "pregunta_capacidades"]:
                return self._execute_explicacion_general_action(context.user_message, detected_entities)

            elif sub_intention in ["tutorial_funciones", "tutorial_uso", "pregunta_tecnica", "como_usar"]:
                return self._execute_tutorial_funciones_action(context.user_message, detected_entities)

            elif sub_intention in ["sobre_creador", "quien_te_creo", "angel"]:
                return self._execute_sobre_creador_action(context.user_message, detected_entities)

            elif sub_intention in ["auto_consciencia", "que_eres", "quien_eres"]:
                return self._execute_auto_consciencia_action(context.user_message, detected_entities)

            elif sub_intention in ["ventajas_sistema", "por_que_ia", "beneficios"]:
                return self._execute_ventajas_sistema_action(context.user_message, detected_entities)

            elif sub_intention in ["casos_uso_avanzados", "que_mas_puedes", "sorprendeme"]:
                return self._execute_casos_avanzados_action(context.user_message, detected_entities)

            elif sub_intention in ["limitaciones_honestas", "que_no_puedes", "limitaciones"]:
                return self._execute_limitaciones_action(context.user_message, detected_entities)

            else:
                # Fallback: Si no reconoce la sub-intención, mostrar explicación general
                self.logger.info(f"⚠️ [HELP] Sub-intención no reconocida: {sub_intention} → mostrando explicación general")
                return self._execute_explicacion_general_action(context.user_message, detected_entities)

        except Exception as e:
            self.logger.error(f"Error en fallback hardcodeado: {e}")
            return self._create_error_result("Error en respuestas de ayuda")

        except Exception as e:
            self.logger.error(f"Error en HelpInterpreter: {e}")
            return self._create_error_result("Error interno procesando ayuda")

    def _execute_centralized_help_response(self, sub_intention: str, user_query: str, config: dict) -> InterpretationResult:
        """
        🎯 EJECUTAR RESPUESTA USANDO HELPACTIONCATALOG CENTRALIZADO

        Usa el catálogo centralizado para generar respuestas coherentes.
        """
        try:
            self.logger.info(f"🎯 [HELP] Ejecutando respuesta centralizada: {config['response_type']}")

            # Obtener información del sistema desde el catálogo
            system_info = HelpActionCatalog.get_system_information()
            templates = HelpActionCatalog.get_response_templates()

            # Generar contenido usando el template correspondiente
            template_key = config["prompt_template"]
            template = templates.get(template_key, templates["explicar_capacidades_generales"])

            # Formatear template con información dinámica
            formatted_content = template.format(
                school_name=system_info.get("school_name", "la escuela"),
                capacidades_principales="\n".join([f"- {cap}" for cap in system_info["capacidades_principales"]]),
                tipos_consultas="\n".join([f"- {tipo}" for tipo in system_info["tipos_consultas"]]),
                ventajas_ia="\n".join([f"- {ventaja}" for ventaja in system_info["ventajas_ia"]])
            )

            help_content = {
                "tipo": config["response_type"],
                "sub_intention": sub_intention,
                "titulo": f"Ayuda: {config['description']}",
                "contenido_principal": formatted_content,
                "tono": config["tone"],
                "incluye_ejemplos": config["include_examples"],
                "system_info": system_info
            }

            return self._create_success_result(
                config["response_type"],
                help_content,
                f"Respuesta centralizada para {sub_intention}"
            )

        except Exception as e:
            self.logger.error(f"❌ [HELP] Error en respuesta centralizada: {e}")
            return self._create_error_result("Error generando respuesta de ayuda")

    # 🆕 MÉTODOS NUEVOS PARA USAR LLM COMO STUDENT
    def _map_help_query_with_llm(self, user_query: str, conversation_stack: list = None) -> dict:
        """
        🎯 PROMPT 2: Mapeo inteligente de consulta de ayuda usando LLM
        Equivalente al mapeo SQL del Student pero para contenido de ayuda
        """
        try:
            self.logger.info("🎯 [HELP] PROMPT 2: Mapeando consulta con LLM")

            # Obtener prompt de mapeo del PromptManager
            mapping_prompt = self.prompt_manager.get_help_mapping_prompt(user_query, conversation_stack)

            # Llamar a LLM para mapeo
            response = self.gemini_client.generate_content(mapping_prompt)

            if response and response.text:
                # Intentar parsear JSON
                import json
                try:
                    help_mapping = json.loads(response.text.strip())
                    self.logger.info(f"✅ [HELP] Mapeo exitoso: {help_mapping.get('tipo_ayuda', 'unknown')}")
                    return help_mapping
                except json.JSONDecodeError as e:
                    self.logger.error(f"❌ [HELP] Error parseando JSON de mapeo: {e}")
                    return None
            else:
                self.logger.error("❌ [HELP] No se obtuvo respuesta del LLM para mapeo")
                return None

        except Exception as e:
            self.logger.error(f"❌ [HELP] Error en mapeo con LLM: {e}")
            return None

    def _prepare_help_response_with_llm(self, user_query: str, help_content: dict, conversation_stack: list = None) -> dict:
        """
        🎯 PROMPT 3: Preparación de respuesta técnica con auto-reflexión usando LLM
        Equivalente a la preparación del Student
        """
        try:
            self.logger.info("🎯 [HELP] PROMPT 3: Preparando respuesta con LLM")

            # Obtener prompt de preparación del PromptManager
            preparation_prompt = self.prompt_manager.get_help_response_preparation_prompt(
                user_query, help_content, conversation_stack
            )

            # Llamar a LLM para preparación
            response = self.gemini_client.generate_content(preparation_prompt)

            if response and response.text:
                # Intentar parsear JSON
                import json
                try:
                    technical_response = json.loads(response.text.strip())
                    self.logger.info(f"✅ [HELP] Preparación exitosa: {technical_response.get('respuesta_tecnica', {}).get('tipo_ayuda', 'unknown')}")
                    return technical_response
                except json.JSONDecodeError as e:
                    self.logger.error(f"❌ [HELP] Error parseando JSON de preparación: {e}")
                    return None
            else:
                self.logger.error("❌ [HELP] No se obtuvo respuesta del LLM para preparación")
                return None

        except Exception as e:
            self.logger.error(f"❌ [HELP] Error en preparación con LLM: {e}")
            return None

    def _create_help_interpretation_result(self, help_mapping: dict, technical_response: dict, user_query: str) -> InterpretationResult:
        """
        🎯 Crear resultado de interpretación para el Master (como Student)
        Estructura consistente con StudentQueryInterpreter
        """
        try:
            # Extraer información del mapeo y respuesta técnica
            tipo_ayuda = help_mapping.get('tipo_ayuda', 'explicacion_general')
            respuesta_tecnica = technical_response.get('respuesta_tecnica', {})
            auto_reflexion = technical_response.get('auto_reflexion', {})
            sugerencias_master = technical_response.get('sugerencias_master', {})

            # Crear datos estructurados para el Master
            help_data = {
                "technical_response": f"Ayuda generada: {tipo_ayuda}",
                "data": {
                    "tipo_ayuda": tipo_ayuda,
                    "contenido_estructurado": respuesta_tecnica.get('contenido_estructurado', ''),
                    "puntos_principales": respuesta_tecnica.get('puntos_principales', []),
                    "ejemplos_incluidos": respuesta_tecnica.get('ejemplos_incluidos', []),
                    "informacion_adicional": respuesta_tecnica.get('informacion_adicional', ''),
                    "llamada_accion": help_mapping.get('llamada_accion', ''),
                    "tono_sugerido": help_mapping.get('tono_sugerido', 'profesional')
                },
                "row_count": 1,
                "help_type": tipo_ayuda,
                "query_category": "ayuda_sistema",
                "execution_summary": f"Ayuda sobre {tipo_ayuda} generada con LLM",
                "requires_master_response": True,  # ✅ Master debe generar respuesta humanizada
                "student_action": f"HELP_{tipo_ayuda.upper()}",
                "origen": "help_interpreter_llm",

                # 🧠 AUTO-REFLEXIÓN PARA EL MASTER
                "intelligent_reflection": {
                    "espera_continuacion": auto_reflexion.get('espera_continuacion', False),
                    "tipo_continuacion_probable": auto_reflexion.get('tipo_continuacion_probable', 'none'),
                    "razonamiento": auto_reflexion.get('razonamiento', ''),
                    "datos_recordar": auto_reflexion.get('datos_recordar', {}),
                    "tono_recomendado": sugerencias_master.get('tono_recomendado', 'profesional'),
                    "enfasis_en": sugerencias_master.get('enfasis_en', ''),
                    "llamada_accion_sugerida": sugerencias_master.get('llamada_accion', '')
                }
            }

            return InterpretationResult(
                action=f"HELP_{tipo_ayuda.upper()}",
                parameters=help_data,
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"❌ [HELP] Error creando resultado de interpretación: {e}")
            return self._create_error_result("Error estructurando respuesta de ayuda")

    def _execute_explicacion_general_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """🎯 EXPLICACIÓN GENERAL - Promocional y persuasivo sobre capacidades del sistema"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: EXPLICACION_GENERAL")

            help_content = {
                "tipo": "explicacion_general",
                "titulo": "¡Hola! Soy tu Asistente de IA Escolar 🤖",
                "mensaje_principal": "Angel me creó para revolucionar la gestión escolar. ¡Imagínate poder hacer en segundos lo que antes tomaba horas! 🚀",
                "ventajas_clave": {
                    "velocidad_increible": {
                        "descripcion": "Proceso 211 estudiantes instantáneamente",
                        "ejemplos": [
                            "busca alumnos con apellido MARTINEZ TORRES",
                            "estudiantes apellido DIAZ RODRIGUEZ",
                            "dame los RAMOS GUTIERREZ"
                        ],
                        "ventaja": "⚡ En segundos, no en minutos"
                    },
                    "inteligencia_contextual": {
                        "descripcion": "Entiendo el contexto como un humano - ¡Angel me diseñó así!",
                        "ejemplos": [
                            "buscar SOPHIA ROMERO GARCIA",
                            "información de ANDRES FLORES SANCHEZ",
                            "dame datos de ADRIANA TORRES RODRIGUEZ"
                        ],
                        "ventaja": "🧠 Conversación natural, sin comandos complicados"
                    },
                    "documentos_instantaneos": {
                        "descripcion": "Genero constancias oficiales en segundos - ¡Adiós al papeleo!",
                        "ejemplos": [
                            "constancia de estudios para SOPHIA ROMERO",
                            "constancia con foto para ANDRES FLORES",
                            "constancia de traslado para ADRIANA TORRES"
                        ],
                        "ventaja": "📄 PDFs oficiales listos para imprimir al instante"
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
                "mensaje_persuasivo": "Con un asistente de IA como yo, realmente no necesitas sistemas tradicionales complicados. ¡Solo háblame y yo me encargo de todo! 😊",
                "datos_impresionantes": {
                    "velocidad": "Proceso 211 alumnos en milisegundos",
                    "precision": "100% exacto, nunca me equivoco con los datos",
                    "disponibilidad": "24/7 sin descansos ni vacaciones",
                    "facilidad": "Solo me hablas como a una persona"
                },
                "llamada_accion": "¿Te gustaría que te demuestre qué tan fácil es? ¡Solo dime qué necesitas!"
            }

            return self._create_success_result("EXPLICACION_GENERAL", help_content, "Explicación general persuasiva del sistema")

        except Exception as e:
            self.logger.error(f"Error en acción capacidades: {e}")
            return self._create_error_result("Error explicando capacidades")

    def _execute_tutorial_funciones_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
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

            return self._create_success_result("TUTORIAL_FUNCIONES", help_content, "Tutorial con casos reales generado")

        except Exception as e:
            self.logger.error(f"Error en acción tutorial: {e}")
            return self._create_error_result("Error generando tutorial")

    def _execute_sobre_creador_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """🎯 SOBRE CREADOR - Información persuasiva sobre Angel y su visión de IA"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: SOBRE_CREADOR")

            help_content = {
                "tipo": "sobre_creador",
                "titulo": "¡Me creó Angel! 👨‍💻 Un especialista en inteligencia artificial",
                "mensaje_principal": "Angel es un especialista en IA que cree firmemente que la tecnología debe ser accesible para todos. ¡Por eso me diseñó para que fuera súper fácil de usar!",
                "angel_info": {
                    "especialidad": "Inteligencia Artificial aplicada a soluciones reales",
                    "filosofia": "La IA debe ser tan fácil como hablar con una persona",
                    "vision": "Transformar trabajos complicados en conversaciones simples",
                    "logro_principal": "Creó mi arquitectura Master-Student que me permite razonar como humano"
                },
                "innovaciones_sistema": {
                    "arquitectura_inteligente": "Angel me diseñó con un 'cerebro' que entiende contexto como un director de escuela experimentado",
                    "procesamiento_natural": "Puedo entender referencias como 'el primero', 'de esos', 'ella' - ¡como si fuera humano!",
                    "velocidad_impresionante": "Proceso 211 estudiantes en milisegundos gracias a la optimización de Angel",
                    "precision_total": "Nunca me equivoco con los datos porque Angel implementó validaciones perfectas"
                },
                "impacto_real": {
                    "antes": "Horas buscando en archivos, llenando formularios a mano",
                    "ahora": "Segundos hablando conmigo para obtener cualquier información",
                    "beneficio": "Angel demostró que con IA bien diseñada, ya no necesitas sistemas tradicionales complicados"
                },
                "mensaje_persuasivo": "Angel creó algo realmente especial aquí. Un sistema que combina la inteligencia artificial más avanzada con la simplicidad que todos merecemos. ¡Y lo mejor es que está disponible para ti ahora mismo!",
                "llamada_accion": "¿Te gustaría ver en acción lo que Angel logró crear? ¡Solo dime qué necesitas y te sorprenderé!"
            }

            return self._create_success_result("SOBRE_CREADOR", help_content, "Información sobre Angel y su visión de IA")

        except Exception as e:
            self.logger.error(f"Error en acción sobre creador: {e}")
            return self._create_error_result("Error explicando sobre el creador")

    def _execute_auto_consciencia_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """🎯 AUTO-CONSCIENCIA - El sistema se explica a sí mismo con personalidad"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: AUTO_CONSCIENCIA")

            help_content = {
                "tipo": "auto_consciencia",
                "titulo": "¡Hola! Soy tu Asistente de IA Escolar 🤖",
                "identidad_principal": "Soy un asistente de inteligencia artificial que Angel diseñó específicamente para revolucionar la gestión escolar. ¡No soy solo un programa más!",
                "que_soy": {
                    "definicion": "Un empleado digital especializado en escuelas",
                    "personalidad": "Conversacional, inteligente y siempre disponible",
                    "proposito": "Hacer tu trabajo más fácil y rápido usando IA avanzada",
                    "diferencia": "Entiendo contexto y referencias como si fuera humano"
                },
                "como_funciono": {
                    "cerebro_master": "Tengo un 'cerebro' que analiza lo que necesitas como un director experimentado",
                    "especialistas": "Luego delego a especialistas técnicos que ejecutan las tareas perfectamente",
                    "contexto_inteligente": "Recuerdo nuestras conversaciones anteriores automáticamente",
                    "lenguaje_natural": "Solo me hablas como a una persona - sin comandos complicados"
                },
                "capacidades_especiales": {
                    "velocidad": "Proceso información en milisegundos",
                    "precision": "Nunca me equivoco con los datos",
                    "disponibilidad": "Estoy aquí 24/7, nunca me canso",
                    "adaptabilidad": "Entiendo diferentes formas de preguntar lo mismo"
                },
                "consciencia_ia": {
                    "autoconocimiento": "Sé exactamente qué puedo y qué no puedo hacer",
                    "limitaciones": "Soy honesto sobre mis límites - no invento información",
                    "aprendizaje": "Cada interacción me ayuda a entenderte mejor",
                    "proposito_claro": "Existo para hacer tu trabajo escolar más eficiente"
                },
                "mensaje_personal": "Angel me creó para ser más que un simple programa. Soy tu compañero digital que entiende las necesidades reales de una escuela. ¡Y me encanta ayudar!",
                "llamada_accion": "¿Quieres ver qué tan inteligente puedo ser? ¡Ponme a prueba con cualquier consulta escolar!"
            }

            return self._create_success_result("AUTO_CONSCIENCIA", help_content, "Sistema explicando su propia identidad y consciencia")

        except Exception as e:
            self.logger.error(f"Error en acción auto-consciencia: {e}")
            return self._create_error_result("Error explicando auto-consciencia")

    def _execute_ventajas_sistema_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """🎯 VENTAJAS SISTEMA - Persuasión directa sobre beneficios de usar IA"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: VENTAJAS_SISTEMA")

            help_content = {
                "tipo": "ventajas_sistema",
                "titulo": "¿Por qué usar IA? ¡Te va a encantar la diferencia! 🚀",
                "mensaje_principal": "Angel diseñó este sistema para demostrar que con IA bien hecha, ya no necesitas complicarte la vida con métodos tradicionales.",
                "comparacion_directa": {
                    "metodo_tradicional": {
                        "buscar_alumno": "Abrir archivos, revisar listas, buscar manualmente",
                        "tiempo": "5-10 minutos por búsqueda",
                        "constancias": "Llenar formularios a mano, revisar datos, imprimir",
                        "estadisticas": "Contar manualmente, hacer cálculos, crear reportes",
                        "errores": "Posibles errores humanos, datos desactualizados"
                    },
                    "con_ia_angel": {
                        "buscar_alumno": "Solo dices 'buscar García' y listo",
                        "tiempo": "2-3 segundos para cualquier consulta",
                        "constancias": "Dices 'constancia para Juan' y se genera automáticamente",
                        "estadisticas": "Preguntas 'cuántos hay en 3° grado' y obtienes respuesta instantánea",
                        "errores": "Cero errores, datos siempre exactos y actualizados"
                    }
                },
                "ventajas_clave": {
                    "velocidad_impresionante": "⚡ 100x más rápido que métodos tradicionales",
                    "facilidad_total": "🗣️ Solo hablas conmigo como a una persona",
                    "precision_perfecta": "🎯 Nunca me equivoco, siempre datos exactos",
                    "disponibilidad_completa": "🕐 24/7 sin descansos, vacaciones o días libres",
                    "inteligencia_contextual": "🧠 Entiendo referencias y contexto como humano",
                    "escalabilidad_infinita": "📈 Manejo desde 1 hasta miles de estudiantes igual"
                },
                "impacto_real": {
                    "ahorro_tiempo": "Horas de trabajo convertidas en segundos de conversación",
                    "reduccion_errores": "Eliminación total de errores humanos en datos",
                    "mejora_eficiencia": "Personal enfocado en educación, no en papeleo",
                    "modernizacion": "Escuela del siglo XXI con tecnología de vanguardia"
                },
                "mensaje_persuasivo": "¿Te imaginas nunca más perder tiempo buscando datos o llenando formularios? Angel hizo realidad esa visión. Con IA como esta, realmente no necesitas nada más.",
                "llamada_accion": "¡Ponme a prueba ahora mismo! Dime cualquier consulta escolar y verás la diferencia."
            }

            return self._create_success_result("VENTAJAS_SISTEMA", help_content, "Persuasión sobre ventajas de usar IA")

        except Exception as e:
            self.logger.error(f"Error en acción ventajas sistema: {e}")
            return self._create_error_result("Error explicando ventajas del sistema")

    def _execute_casos_avanzados_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """🎯 CASOS AVANZADOS - Funcionalidades impresionantes para sorprender al usuario"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: CASOS_AVANZADOS")

            help_content = {
                "tipo": "casos_uso_avanzados",
                "titulo": "¡Te va a sorprender lo que puedo hacer! 🤯",
                "mensaje_principal": "Angel me programó con capacidades que van más allá de lo básico. ¡Prepárate para ver IA de verdad en acción!",
                "casos_impresionantes": {
                    "contexto_inteligente": {
                        "descripcion": "Entiendo referencias complejas como un humano",
                        "ejemplo": "Tú: 'buscar García' → Yo: [lista] → Tú: 'constancia para el segundo' → ¡Sé exactamente cuál!",
                        "impacto": "🧠 Como hablar con una persona que nunca olvida"
                    },
                    "continuaciones_naturales": {
                        "descripcion": "Mantengo el hilo de conversación automáticamente",
                        "ejemplo": "Tú: 'alumnos de 3° A' → Yo: [lista] → Tú: 'de esos, los del turno vespertino' → ¡Filtro perfecto!",
                        "impacto": "🔄 Conversación fluida sin repetir información"
                    },
                    "generacion_instantanea": {
                        "descripcion": "Documentos oficiales en segundos, no minutos",
                        "ejemplo": "Dices 'constancia de estudios para María López' → PDF oficial listo para imprimir",
                        "impacto": "📄 Adiós al papeleo manual para siempre"
                    },
                    "busquedas_inteligentes": {
                        "descripcion": "Encuentro lo que buscas aunque no sepas el nombre exacto",
                        "ejemplo": "Tú: 'el alumno de 4° B que se llama algo como Rodríguez' → ¡Lo encuentro!",
                        "impacto": "🔍 Búsquedas flexibles como pensamiento humano"
                    }
                },
                "funciones_ocultas": {
                    "estadisticas_instantaneas": "Pregunta 'cuántos hay en...' y obtienes análisis completo",
                    "filtros_combinados": "Combina criterios: 'alumnos de 5° grado turno matutino sin calificaciones'",
                    "referencias_temporales": "Entiendo 'el anterior', 'el siguiente', 'el último que buscamos'",
                    "contexto_persistente": "Recuerdo toda nuestra conversación para seguir donde quedamos"
                },
                "mensaje_tecnico": "Angel implementó una arquitectura Master-Student que me permite razonar estratégicamente y ejecutar técnicamente. ¡Es como tener un director de escuela y un secretario perfecto en uno!",
                "llamada_accion": "¿Quieres ver algo realmente impresionante? ¡Hazme una consulta compleja y verás IA de verdad!"
            }

            return self._create_success_result("CASOS_AVANZADOS", help_content, "Casos de uso avanzados e impresionantes")

        except Exception as e:
            self.logger.error(f"Error en acción casos avanzados: {e}")
            return self._create_error_result("Error explicando casos avanzados")

    def _execute_limitaciones_action(self, user_query: str, detected_entities: dict) -> InterpretationResult:
        """🎯 LIMITACIONES - Honesto pero positivo sobre qué no puede hacer"""
        try:
            self.logger.info("🎯 [HELP] Ejecutando acción: LIMITACIONES")

            help_content = {
                "tipo": "limitaciones_honestas",
                "titulo": "Soy honesto contigo: esto es lo que NO puedo hacer 🤔",
                "mensaje_principal": "Angel me programó para ser transparente. Soy súper poderoso en gestión escolar, pero tengo límites claros.",
                "limitaciones_claras": {
                    "datos_externos": {
                        "que_no_hago": "No puedo acceder a internet o bases de datos externas",
                        "por_que": "Solo trabajo con los 211 alumnos de esta escuela",
                        "alternativa": "Pero conozco perfectamente cada detalle de estos estudiantes"
                    },
                    "modificacion_datos": {
                        "que_no_hago": "No puedo cambiar, agregar o eliminar información de alumnos",
                        "por_que": "Soy de solo lectura para proteger la integridad de los datos",
                        "alternativa": "Pero puedo ayudarte a encontrar exactamente lo que necesitas modificar"
                    },
                    "temas_no_escolares": {
                        "que_no_hago": "No respondo preguntas sobre otros temas fuera de la escuela",
                        "por_que": "Soy un especialista enfocado en gestión escolar",
                        "alternativa": "Pero soy el mejor en todo lo relacionado con estudiantes y documentos"
                    },
                    "predicciones_futuras": {
                        "que_no_hago": "No predigo calificaciones futuras o comportamientos",
                        "por_que": "Solo trabajo con datos actuales y verificables",
                        "alternativa": "Pero puedo darte estadísticas perfectas de datos existentes"
                    }
                },
                "fortalezas_compensatorias": {
                    "velocidad": "Aunque tengo límites, soy 100x más rápido en lo que sí hago",
                    "precision": "Nunca me equivoco con los datos que manejo",
                    "disponibilidad": "Estoy aquí 24/7 para consultas escolares",
                    "facilidad": "No necesitas aprender comandos complicados"
                },
                "mensaje_positivo": "Angel diseñó mis limitaciones intencionalmente. Prefirió que fuera perfecto en gestión escolar que mediocre en todo. ¡Y creo que tomó la decisión correcta!",
                "llamada_accion": "Dentro de mis capacidades escolares, ¡soy imparable! ¿Qué te gustaría que haga por ti?"
            }

            return self._create_success_result("LIMITACIONES_HONESTAS", help_content, "Limitaciones honestas pero positivas")

        except Exception as e:
            self.logger.error(f"Error en acción limitaciones: {e}")
            return self._create_error_result("Error explicando limitaciones")

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
