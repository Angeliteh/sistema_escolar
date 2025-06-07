"""
🆘 CATÁLOGO CENTRALIZADO DE ACCIONES PARA HELPINTERPRETER

Centraliza TODA la información que HelpInterpreter necesita para responder:
- Qué tipos de ayuda puede proporcionar
- Cómo mapear sub-intenciones a respuestas
- Prompts específicos para cada tipo de ayuda
- Información del sistema para explicar

INDEPENDIENTE del Master y Student - HelpInterpreter decide autónomamente.
"""

from typing import Dict, List
from app.core.config.school_config_manager import get_school_config_manager


class HelpActionCatalog:
    """
    🎯 CATÁLOGO CENTRALIZADO PARA HELPINTERPRETER
    
    Proporciona información clara sobre:
    - Sub-intenciones de ayuda disponibles
    - Tipos de respuesta para cada una
    - Prompts específicos
    - Información del sistema
    """
    
    @staticmethod
    def get_sub_intention_mapping() -> Dict:
        """
        🎯 MAPEO DIRECTO SUB-INTENCIÓN → TIPO DE RESPUESTA
        
        HelpInterpreter recibe sub-intención del Master y mapea a tipo de ayuda.
        INDEPENDIENTE del Master - HelpInterpreter decide autónomamente cómo responder.
        """
        return {
            "explicacion_general": {
                "response_type": "CAPACIDADES_SISTEMA",
                "description": "Explicar qué puede hacer el sistema",
                "prompt_template": "explicar_capacidades_generales",
                "include_examples": True,
                "tone": "amigable_y_profesional"
            },
            
            "tutorial_funciones": {
                "response_type": "TUTORIAL_ESPECIFICO", 
                "description": "Explicar cómo usar funciones específicas",
                "prompt_template": "tutorial_paso_a_paso",
                "include_examples": True,
                "tone": "instructivo_detallado"
            },
            
            "pregunta_tecnica": {
                "response_type": "RESPUESTA_TECNICA",
                "description": "Responder preguntas técnicas sobre el sistema",
                "prompt_template": "respuesta_tecnica_experta", 
                "include_examples": False,
                "tone": "profesional_y_preciso"
            },
            
            "informacion_creador": {
                "response_type": "INFO_ANGEL",
                "description": "Información sobre Angel como creador y experto en IA",
                "prompt_template": "presentar_angel_experto",
                "include_examples": False,
                "tone": "persuasivo_y_entusiasta"
            },
            
            "pregunta_capacidades": {
                "response_type": "CAPACIDADES_DETALLADAS",
                "description": "Detalles específicos sobre capacidades del sistema",
                "prompt_template": "capacidades_detalladas",
                "include_examples": True,
                "tone": "informativo_y_completo"
            }
        }
    
    @staticmethod
    def get_system_information() -> Dict:
        """
        🎯 INFORMACIÓN DEL SISTEMA PARA HELPINTERPRETER
        
        Información que HelpInterpreter necesita para explicar el sistema.
        """
        school_config = get_school_config_manager()
        school_name = school_config.get_school_name()
        total_students = school_config.get_total_students()
        
        return {
            "capacidades_principales": [
                f"Gestión completa de {total_students} estudiantes de {school_name}",
                "Búsquedas inteligentes por cualquier criterio",
                "Generación automática de constancias oficiales",
                "Estadísticas y análisis académicos",
                "Transformación de documentos PDF",
                "Respuestas contextuales y conversacionales"
            ],
            
            "tipos_consultas": [
                "Búsquedas: 'buscar García', 'alumnos de 3er grado'",
                "Estadísticas: 'cuántos alumnos hay', 'distribución por turno'", 
                "Constancias: 'constancia de estudios para Juan'",
                "Transformaciones: 'convertir PDF a constancia'",
                "Ayuda: 'qué puedes hacer', 'cómo buscar alumnos'"
            ],
            
            "ventajas_ia": [
                "Comprende lenguaje natural sin comandos específicos",
                "Mantiene contexto de conversaciones",
                "Aprende de patrones de uso",
                "Respuestas instantáneas 24/7",
                "Precisión en búsquedas complejas",
                "Generación automática de documentos"
            ],
            
            "creador_info": {
                "nombre": "Angel",
                "expertise": "Experto en Inteligencia Artificial y sistemas educativos",
                "vision": "Democratizar el acceso a tecnología IA en educación",
                "logros": "Sistema Master-Student innovador para gestión escolar"
            }
        }
    
    @staticmethod
    def get_response_templates() -> Dict:
        """
        🎯 PLANTILLAS DE RESPUESTA PARA HELPINTERPRETER
        
        Plantillas específicas para cada tipo de respuesta.
        """
        return {
            "explicar_capacidades_generales": """
🤖 ¡Hola! Soy el asistente inteligente de {school_name}.

🎯 **MIS CAPACIDADES PRINCIPALES:**
{capacidades_principales}

💬 **TIPOS DE CONSULTAS QUE MANEJO:**
{tipos_consultas}

🚀 **VENTAJAS DE USAR IA:**
{ventajas_ia}

💡 **EJEMPLOS RÁPIDOS:**
- "buscar García" → Te muestro todos los García registrados
- "cuántos alumnos hay en 3er grado" → Estadística instantánea
- "constancia de estudios para Juan Pérez" → Documento oficial generado

¿En qué puedo ayudarte específicamente?
""",
            
            "tutorial_paso_a_paso": """
📚 **TUTORIAL: {funcion_especifica}**

🔍 **PASO A PASO:**
{pasos_detallados}

💡 **EJEMPLOS PRÁCTICOS:**
{ejemplos_especificos}

⚠️ **CONSEJOS ÚTILES:**
{consejos_adicionales}

¿Te gustaría que te ayude con algún ejemplo específico?
""",
            
            "respuesta_tecnica_experta": """
🔧 **RESPUESTA TÉCNICA:**

{respuesta_detallada}

📊 **DETALLES TÉCNICOS:**
{detalles_tecnicos}

🎯 **APLICACIÓN PRÁCTICA:**
{aplicacion_practica}

¿Necesitas más detalles sobre algún aspecto específico?
""",
            
            "presentar_angel_experto": """
👨‍💻 **SOBRE ANGEL - CREADOR DEL SISTEMA:**

🎯 **EXPERTISE:**
Angel es un experto en Inteligencia Artificial especializado en sistemas educativos. Ha desarrollado este innovador sistema Master-Student que revoluciona la gestión escolar.

🚀 **VISIÓN:**
Su objetivo es democratizar el acceso a tecnología IA avanzada en el sector educativo, haciendo que las escuelas tengan herramientas de nivel empresarial.

💡 **INNOVACIÓN:**
Este sistema utiliza arquitectura Master-Student, donde diferentes especialistas de IA colaboran para proporcionar respuestas precisas y contextuales.

🏆 **LOGROS:**
- Sistema completamente dinámico y reutilizable
- Arquitectura escalable para cualquier institución
- Integración perfecta de IA conversacional con gestión de datos

¿Te interesa conocer más sobre las innovaciones técnicas del sistema?
""",
            
            "capacidades_detalladas": """
🎯 **CAPACIDADES DETALLADAS DEL SISTEMA:**

📊 **GESTIÓN DE DATOS:**
{capacidades_datos}

🔍 **BÚSQUEDAS INTELIGENTES:**
{capacidades_busqueda}

📄 **GENERACIÓN DE DOCUMENTOS:**
{capacidades_documentos}

📈 **ANÁLISIS Y ESTADÍSTICAS:**
{capacidades_estadisticas}

🤖 **INTELIGENCIA ARTIFICIAL:**
{capacidades_ia}

¿Qué aspecto te interesa explorar más a fondo?
"""
        }
    
    @staticmethod
    def generate_help_prompt_section(sub_intention: str, user_query: str) -> str:
        """
        🎯 GENERA SECCIÓN COMPLETA PARA PROMPTS DE HELPINTERPRETER
        
        Reemplaza información dispersa con sección coherente específica para la sub-intención.
        """
        mapping = HelpActionCatalog.get_sub_intention_mapping()
        system_info = HelpActionCatalog.get_system_information()
        templates = HelpActionCatalog.get_response_templates()
        
        if sub_intention not in mapping:
            sub_intention = "explicacion_general"  # Fallback
        
        config = mapping[sub_intention]
        template_key = config["prompt_template"]
        
        return f"""
═══════════════════════════════════════════════════════════════════════════════
🆘 HELPINTERPRETER - RESPUESTA ESPECIALIZADA
═══════════════════════════════════════════════════════════════════════════════

🎯 SUB-INTENCIÓN: {sub_intention}
📝 CONSULTA: "{user_query}"
🎭 TIPO DE RESPUESTA: {config['response_type']}
🗣️ TONO: {config['tone']}

📊 INFORMACIÓN DEL SISTEMA:
{HelpActionCatalog._format_system_info(system_info)}

📋 PLANTILLA A USAR:
{templates.get(template_key, templates['explicar_capacidades_generales'])}

🚨 INSTRUCCIONES ESPECÍFICAS:
1. Usa el tono {config['tone']}
2. {'Incluye ejemplos prácticos' if config['include_examples'] else 'Mantén respuesta concisa'}
3. Enfócate en {config['description']}
4. Sé persuasivo sobre las ventajas de IA
5. Menciona a Angel como experto cuando sea relevante

RESPONDE DE FORMA NATURAL Y CONVERSACIONAL:
"""
    
    @staticmethod
    def _format_system_info(system_info: Dict) -> str:
        """Formatea la información del sistema para el prompt"""
        formatted = ""
        for key, value in system_info.items():
            if isinstance(value, list):
                formatted += f"\n{key.upper()}:\n"
                for item in value:
                    formatted += f"  - {item}\n"
            elif isinstance(value, dict):
                formatted += f"\n{key.upper()}:\n"
                for subkey, subvalue in value.items():
                    formatted += f"  {subkey}: {subvalue}\n"
        return formatted
