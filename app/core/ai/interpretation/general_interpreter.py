"""
🗣️ GENERAL INTERPRETER - CONVERSACIÓN NATURAL Y TEMAS GENERALES

Especialista en conversación casual y temas no relacionados al sistema escolar.
Mantiene identidad escolar sutil mientras proporciona conversación natural.

Según PLAN_EMPLEADO_DIGITAL_COMPLETO.md:
- Función: LLM estándar con identidad escolar
- Responsabilidad: Cualquier tema no escolar
- Personalidad: Versátil pero manteniendo identidad de empleado escolar
"""

from typing import Optional
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger
from app.core.ai.general_action_catalog import GeneralActionCatalog


class GeneralInterpreter(BaseInterpreter):
    """
    🗣️ ESPECIALISTA EN CONVERSACIÓN GENERAL
    
    Maneja conversación casual y temas no relacionados al sistema escolar.
    Funciona como LLM estándar pero mantiene identidad escolar sutil.
    """
    
    def __init__(self, gemini_client=None):
        super().__init__("GeneralInterpreter", priority=4)
        self.logger = get_logger(__name__)
        self.gemini_client = gemini_client
        
        # Importar PromptManager específico
        from app.core.ai.prompts.general_prompt_manager import GeneralPromptManager
        self.prompt_manager = GeneralPromptManager()
    
    def can_handle(self, context: InterpretationContext) -> bool:
        """
        🎯 DETERMINA SI PUEDE MANEJAR LA CONSULTA
        
        Maneja conversación general y temas no escolares.
        """
        if not context.user_message:
            return False
        
        # Palabras clave que indican conversación general
        general_keywords = [
            "hola", "buenos días", "buenas tardes", "¿cómo estás?",
            "clima", "chiste", "háblame", "conversación", "charla",
            "¿qué tal?", "saludos", "despedida", "hasta luego"
        ]
        
        user_message_lower = context.user_message.lower()
        
        # Si contiene palabras de conversación general
        for keyword in general_keywords:
            if keyword in user_message_lower:
                return True
        
        # Si NO contiene palabras escolares específicas, podría ser general
        school_keywords = [
            "alumno", "estudiante", "constancia", "calificación", "grado",
            "grupo", "turno", "escuela", "buscar", "cuántos", "ayuda",
            "sistema", "capacidades"
        ]
        
        has_school_keywords = any(keyword in user_message_lower for keyword in school_keywords)
        
        # Si no tiene palabras escolares, probablemente es conversación general
        return not has_school_keywords
    
    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        🎯 PROCESA CONVERSACIÓN GENERAL
        
        Maneja saludos, conversación casual y temas no escolares.
        """
        try:
            self.logger.info(f"🗣️ [GENERAL] Procesando conversación general: {context.user_message}")
            
            # Obtener información del Master si está disponible
            intention_info = getattr(context, 'intention_info', {})
            sub_intention = intention_info.get('sub_intention', 'chat_casual')
            
            self.logger.info(f"📥 [GENERAL] Sub-intención del Master: {sub_intention}")
            
            # Mapear sub-intención a tipo de respuesta usando catálogo centralizado
            mapping = GeneralActionCatalog.get_sub_intention_mapping()
            
            if sub_intention in mapping:
                config = mapping[sub_intention]
                response_type = config["response_type"]
                self.logger.info(f"✅ [GENERAL] Mapeado: {sub_intention} → {response_type}")
                
                # Generar respuesta usando el catálogo centralizado
                return self._execute_centralized_general_response(sub_intention, context.user_message, config)
            
            # Fallback: conversación casual general
            return self._execute_general_conversation(context.user_message)
            
        except Exception as e:
            self.logger.error(f"❌ [GENERAL] Error en GeneralInterpreter: {e}")
            return self._create_error_result("Error procesando conversación general")
    
    def _execute_centralized_general_response(self, sub_intention: str, user_query: str, config: dict) -> InterpretationResult:
        """
        🎯 EJECUTAR RESPUESTA USANDO GENERALACTIONCATALOG CENTRALIZADO
        
        Usa el catálogo centralizado para generar respuestas coherentes.
        """
        try:
            self.logger.info(f"🎯 [GENERAL] Ejecutando respuesta centralizada: {config['response_type']}")
            
            # Obtener información del sistema desde el catálogo
            system_info = GeneralActionCatalog.get_system_information()
            templates = GeneralActionCatalog.get_response_templates()
            
            # Generar contenido usando el template correspondiente
            template_key = config["prompt_template"]
            template = templates.get(template_key, templates["conversacion_casual"])
            
            # Formatear template con información dinámica
            formatted_content = template.format(
                school_name=system_info.get("school_name", "la escuela"),
                user_query=user_query,
                sistema_capacidades="\n".join([f"- {cap}" for cap in system_info["capacidades_principales"]])
            )
            
            general_content = {
                "tipo": config["response_type"],
                "sub_intention": sub_intention,
                "titulo": f"Conversación: {config['description']}",
                "contenido_principal": formatted_content,
                "tono": config["tone"],
                "mantiene_identidad": config["mantiene_identidad"],
                "system_info": system_info
            }
            
            return self._create_success_result(
                config["response_type"], 
                general_content, 
                f"Respuesta centralizada para {sub_intention}"
            )
            
        except Exception as e:
            self.logger.error(f"❌ [GENERAL] Error en respuesta centralizada: {e}")
            return self._create_error_result("Error generando respuesta de conversación")
    
    def _execute_general_conversation(self, user_query: str) -> InterpretationResult:
        """
        🗣️ EJECUTAR CONVERSACIÓN GENERAL USANDO LLM
        
        Fallback para conversación general usando Gemini directamente.
        """
        try:
            if not self.gemini_client:
                return self._create_fallback_response(user_query)
            
            # Generar prompt para conversación general
            conversation_prompt = self.prompt_manager.get_general_conversation_prompt(user_query)
            
            # Llamar a Gemini para conversación natural
            response = self.gemini_client.generate_content(conversation_prompt)
            
            if response and hasattr(response, 'text'):
                return self._create_success_result(
                    "CONVERSACION_GENERAL",
                    {
                        "tipo": "conversacion_natural",
                        "contenido": response.text,
                        "user_query": user_query,
                        "metodo": "llm_directo"
                    },
                    "Conversación general procesada por LLM"
                )
            else:
                return self._create_fallback_response(user_query)
                
        except Exception as e:
            self.logger.error(f"❌ [GENERAL] Error en conversación LLM: {e}")
            return self._create_fallback_response(user_query)
    
    def _create_fallback_response(self, user_query: str) -> InterpretationResult:
        """
        🔄 RESPUESTA DE FALLBACK PARA CONVERSACIÓN GENERAL
        """
        fallback_responses = GeneralActionCatalog.get_fallback_responses()
        
        # Seleccionar respuesta apropiada
        if any(saludo in user_query.lower() for saludo in ["hola", "buenos", "buenas"]):
            response = fallback_responses["saludo"]
        else:
            response = fallback_responses["conversacion_general"]
        
        return self._create_success_result(
            "RESPUESTA_FALLBACK",
            {
                "tipo": "fallback",
                "contenido": response,
                "user_query": user_query
            },
            "Respuesta de fallback para conversación general"
        )
    
    def _create_success_result(self, action_type: str, content: dict, message: str) -> InterpretationResult:
        """Crear resultado exitoso"""
        return InterpretationResult(
            success=True,
            action_type=action_type,
            content=content,
            message=message,
            specialist_used="GeneralInterpreter"
        )
    
    def _create_error_result(self, error_message: str) -> InterpretationResult:
        """Crear resultado de error"""
        return InterpretationResult(
            success=False,
            action_type="ERROR",
            content={"error": error_message},
            message=error_message,
            specialist_used="GeneralInterpreter"
        )
