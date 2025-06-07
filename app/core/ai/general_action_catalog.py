"""
🗣️ CATÁLOGO CENTRALIZADO DE ACCIONES PARA GENERALINTERPRETER

Centraliza TODA la información que GeneralInterpreter necesita para responder:
- Qué tipos de conversación puede manejar
- Cómo mapear sub-intenciones a respuestas
- Prompts específicos para cada tipo de conversación
- Información del sistema para mantener identidad escolar sutil

INDEPENDIENTE del Master y otros especialistas - GeneralInterpreter decide autónomamente.
"""

from typing import Dict, List
from app.core.config.school_config_manager import get_school_config_manager


class GeneralActionCatalog:
    """
    🎯 CATÁLOGO CENTRALIZADO PARA GENERALINTERPRETER
    
    Proporciona información clara sobre:
    - Sub-intenciones de conversación disponibles
    - Tipos de respuesta para cada una
    - Prompts específicos
    - Información del sistema para mantener identidad
    """
    
    @staticmethod
    def get_sub_intention_mapping() -> Dict:
        """
        🎯 MAPEO DIRECTO SUB-INTENCIÓN → TIPO DE RESPUESTA
        
        GeneralInterpreter recibe sub-intención del Master y mapea a tipo de conversación.
        INDEPENDIENTE del Master - GeneralInterpreter decide autónomamente cómo responder.
        """
        return {
            "saludo": {
                "response_type": "SALUDO_AMIGABLE",
                "description": "Saludos y presentaciones amigables",
                "prompt_template": "saludo_con_identidad",
                "mantiene_identidad": True,
                "tone": "amigable_y_acogedor"
            },
            
            "chat_casual": {
                "response_type": "CONVERSACION_CASUAL", 
                "description": "Conversación natural sobre temas generales",
                "prompt_template": "conversacion_casual",
                "mantiene_identidad": True,
                "tone": "conversacional_natural"
            },
            
            "despedida": {
                "response_type": "DESPEDIDA_AMIGABLE",
                "description": "Despedidas cordiales con invitación a regresar",
                "prompt_template": "despedida_con_invitacion",
                "mantiene_identidad": True,
                "tone": "cordial_y_acogedor"
            },
            
            "redireccion_educada": {
                "response_type": "REDIRECCION_SISTEMA",
                "description": "Redirección educada hacia funciones del sistema",
                "prompt_template": "redireccion_funciones",
                "mantiene_identidad": True,
                "tone": "educado_y_util"
            }
        }
    
    @staticmethod
    def get_system_information() -> Dict:
        """
        🎯 INFORMACIÓN DEL SISTEMA PARA GENERALINTERPRETER
        
        Información que GeneralInterpreter necesita para mantener identidad escolar sutil.
        """
        school_config = get_school_config_manager()
        school_name = school_config.get_school_name()
        total_students = school_config.get_total_students()
        
        return {
            "school_name": school_name,
            "total_students": total_students,
            
            "capacidades_principales": [
                f"Gestión de {total_students} estudiantes",
                "Búsquedas inteligentes de alumnos",
                "Generación de constancias oficiales",
                "Estadísticas académicas instantáneas",
                "Conversación natural y contextual"
            ],
            
            "identidad_escolar": {
                "rol": "Asistente de IA Escolar",
                "escuela": school_name,
                "personalidad": "Profesional pero accesible",
                "enfoque": "Ayuda integral en gestión escolar"
            },
            
            "temas_redireccion": [
                "Si necesitas información de alumnos, puedo ayudarte",
                "¿Te gustaría generar alguna constancia?",
                "Puedo hacer búsquedas específicas de estudiantes",
                "¿Necesitas estadísticas de la escuela?"
            ]
        }
    
    @staticmethod
    def get_response_templates() -> Dict:
        """
        🎯 PLANTILLAS DE RESPUESTA PARA GENERALINTERPRETER
        
        Plantillas específicas para cada tipo de conversación.
        """
        return {
            "saludo_con_identidad": """
¡Hola! 👋 Soy el Asistente de IA de {school_name}.

🏫 **¿En qué puedo ayudarte hoy?**
- Información de alumnos
- Generar constancias oficiales  
- Estadísticas académicas
- O simplemente conversar 😊

¿Hay algo específico que necesites?
""",
            
            "conversacion_casual": """
{user_query}

Como asistente de {school_name}, me encanta conversar contigo. 😊

💡 **Por cierto**, si en algún momento necesitas:
{sistema_capacidades}

¡Estaré aquí para ayudarte! ¿Hay algo más en lo que pueda asistirte?
""",
            
            "despedida_con_invitacion": """
¡Ha sido un placer conversar contigo! 👋

🏫 Recuerda que siempre estaré aquí en {school_name} para ayudarte con:
- Información de estudiantes
- Constancias y documentos oficiales
- Estadísticas académicas
- ¡O simplemente para charlar!

¡Que tengas un excelente día! 🌟
""",
            
            "redireccion_funciones": """
Entiendo tu consulta sobre "{user_query}". 

🤖 Como asistente de {school_name}, mi especialidad está en:

{sistema_capacidades}

💡 **¿Te gustaría que te ayude con alguna de estas funciones?** 
Por ejemplo:
- "buscar alumno García"
- "cuántos estudiantes hay en 3er grado"
- "generar constancia para Juan Pérez"

¡Estoy aquí para hacer tu trabajo más fácil! 😊
""",
            
            "conversacion_natural_llm": """
Eres el Asistente de IA Escolar de {school_name}.

🎯 **CONTEXTO**: El usuario quiere conversar sobre: "{user_query}"

🗣️ **INSTRUCCIONES**:
- Mantén una conversación natural y amigable
- Conserva sutilmente tu identidad como asistente escolar
- Si es apropiado, menciona tus capacidades escolares
- Sé conversacional pero profesional
- Usa emojis moderadamente

RESPONDE de manera natural manteniendo tu identidad escolar sutil.
"""
        }
    
    @staticmethod
    def get_fallback_responses() -> Dict:
        """
        🔄 RESPUESTAS DE FALLBACK PARA CUANDO NO HAY LLM DISPONIBLE
        """
        school_config = get_school_config_manager()
        school_name = school_config.get_school_name()
        
        return {
            "saludo": f"""
¡Hola! 👋 Soy el Asistente de IA de {school_name}.

🏫 Estoy aquí para ayudarte con:
- Información de alumnos
- Generar constancias oficiales
- Estadísticas académicas
- ¡Y mucho más!

¿En qué puedo asistirte hoy? 😊
""",
            
            "conversacion_general": f"""
¡Gracias por conversar conmigo! 😊

Como asistente de {school_name}, me encanta interactuar contigo. 

💡 **¿Sabías que puedo ayudarte con?**
- Búsquedas de estudiantes
- Generación de documentos oficiales
- Análisis estadísticos
- ¡Y responder tus preguntas!

¿Hay algo específico en lo que pueda ayudarte? 🎯
""",
            
            "despedida": f"""
¡Hasta luego! 👋

Recuerda que siempre estaré aquí en {school_name} para ayudarte.

¡Que tengas un excelente día! 🌟
"""
        }
    
    @staticmethod
    def get_conversation_patterns() -> Dict:
        """
        🎯 PATRONES DE CONVERSACIÓN PARA DETECCIÓN
        
        Ayuda a GeneralInterpreter a identificar tipos de conversación.
        """
        return {
            "saludos": [
                "hola", "buenos días", "buenas tardes", "buenas noches",
                "¿cómo estás?", "¿qué tal?", "saludos", "hey"
            ],
            
            "despedidas": [
                "adiós", "hasta luego", "nos vemos", "chao", "bye",
                "hasta pronto", "me voy", "despedida"
            ],
            
            "conversacion_casual": [
                "clima", "tiempo", "chiste", "háblame", "cuéntame",
                "¿qué opinas?", "conversación", "charla", "plática"
            ],
            
            "temas_personales": [
                "¿quién eres?", "¿cómo te llamas?", "háblame de ti",
                "¿qué haces?", "tu trabajo", "tu función"
            ]
        }
    
    @staticmethod
    def generate_general_prompt_section(sub_intention: str, user_query: str) -> str:
        """
        🎯 GENERA SECCIÓN COMPLETA PARA PROMPTS DE GENERALINTERPRETER
        
        Reemplaza información dispersa con sección coherente específica para la sub-intención.
        """
        mapping = GeneralActionCatalog.get_sub_intention_mapping()
        system_info = GeneralActionCatalog.get_system_information()
        templates = GeneralActionCatalog.get_response_templates()
        
        if sub_intention not in mapping:
            sub_intention = "chat_casual"  # Fallback
        
        config = mapping[sub_intention]
        template_key = config["prompt_template"]
        
        return f"""
═══════════════════════════════════════════════════════════════════════════════
🗣️ GENERALINTERPRETER - CONVERSACIÓN NATURAL
═══════════════════════════════════════════════════════════════════════════════

🎯 SUB-INTENCIÓN: {sub_intention}
📝 CONSULTA: "{user_query}"
🎭 TIPO DE RESPUESTA: {config['response_type']}
🗣️ TONO: {config['tone']}

🏫 IDENTIDAD ESCOLAR:
- Escuela: {system_info['school_name']}
- Rol: {system_info['identidad_escolar']['rol']}
- Estudiantes: {system_info['total_students']} alumnos activos

📋 PLANTILLA A USAR:
{templates.get(template_key, templates['conversacion_casual'])}

🚨 INSTRUCCIONES ESPECÍFICAS:
1. Usa el tono {config['tone']}
2. {'Mantén identidad escolar sutil' if config['mantiene_identidad'] else 'Conversación completamente natural'}
3. Enfócate en {config['description']}
4. Sé natural y conversacional
5. Redirige sutilmente a funciones escolares cuando sea apropiado

RESPONDE DE FORMA NATURAL Y CONVERSACIONAL:
"""
