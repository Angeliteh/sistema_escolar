"""
Procesador de tutoriales paso a paso
Especializado en generar guías detalladas
"""

from typing import Dict, Any, Optional, List
from app.core.logging import get_logger

class TutorialProcessor:
    """
    Clase especializada en generar tutoriales paso a paso
    """
    
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.tutorial_templates = self._load_tutorial_templates()
    
    def generate_tutorial(self, user_query: str, detected_entities: Dict) -> Optional[Dict]:
        """
        Genera tutorial paso a paso usando LLM
        
        Args:
            user_query: Consulta original del usuario
            detected_entities: Entidades detectadas
            
        Returns:
            Dict con el tutorial generado
        """
        try:
            self.logger.debug(f"Generando tutorial para: {user_query}")
            
            # Determinar tipo de tutorial
            tutorial_type = self._determine_tutorial_type(user_query, detected_entities)
            
            # Generar tutorial usando LLM
            tutorial_content = self._generate_tutorial_with_llm(user_query, tutorial_type, detected_entities)
            
            if tutorial_content:
                self.logger.debug(f"Tutorial generado: {tutorial_type}")
                return tutorial_content
            else:
                # Fallback a template predefinido
                self.logger.info("Usando template predefinido como fallback")
                return self._get_template_tutorial(tutorial_type)
                
        except Exception as e:
            self.logger.error(f"Error generando tutorial: {e}")
            return None
    
    def _determine_tutorial_type(self, user_query: str, detected_entities: Dict) -> str:
        """Determina qué tipo de tutorial necesita el usuario"""
        query_lower = user_query.lower()
        
        # Mapeo de palabras clave a tipos de tutorial
        tutorial_keywords = {
            "consultas": ["consultar", "buscar", "alumnos", "estudiantes", "información"],
            "constancias": ["constancia", "documento", "certificado", "generar", "crear"],
            "sistema": ["usar", "funciona", "sistema", "empezar", "comenzar"],
            "navegacion": ["interfaz", "chat", "navegar", "usar"],
            "ejemplos": ["ejemplo", "muestra", "demo", "práctica"]
        }
        
        # Buscar coincidencias
        for tutorial_type, keywords in tutorial_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return tutorial_type
        
        # Default
        return "sistema"
    
    def _generate_tutorial_with_llm(self, user_query: str, tutorial_type: str, detected_entities: Dict) -> Optional[Dict]:
        """Genera tutorial usando LLM"""
        try:
            # Crear prompt especializado
            tutorial_prompt = self._build_tutorial_prompt(user_query, tutorial_type, detected_entities)
            
            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(tutorial_prompt)
            
            if response:
                # Parsear respuesta
                tutorial_data = self._parse_tutorial_response(response)
                return tutorial_data
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error con LLM en tutorial: {e}")
            return None
    
    def _build_tutorial_prompt(self, user_query: str, tutorial_type: str, detected_entities: Dict) -> str:
        """Construye prompt para generar tutorial"""
        return f"""
Eres un especialista en crear TUTORIALES PASO A PASO para sistema escolar.

CONTEXTO DEL SISTEMA:
- Sistema: Gestión Escolar "PROF. MAXIMO GAMIZ FERNANDEZ"
- Interfaz: Chat conversacional en español
- Usuarios: Personal administrativo y educativo
- Funcionalidades: Consultas de alumnos, generación de constancias, ayuda

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
- "constancia de estudios para Juan Pérez" → Genera documento oficial
- "constancia de calificaciones para María" → Incluye notas del alumno
- "constancia de traslado para Pedro" → Para cambio de escuela
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
    
    def _parse_tutorial_response(self, response: str) -> Optional[Dict]:
        """Parsea la respuesta del tutorial del LLM"""
        try:
            import json
            import re
            
            # Limpiar la respuesta
            clean_response = response.strip()
            
            # Buscar JSON en la respuesta
            json_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```',
                r'(\{.*?\})'
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, clean_response, re.DOTALL)
                if matches:
                    try:
                        tutorial_data = json.loads(matches[0])
                        
                        # Validar estructura mínima
                        if "pasos" in tutorial_data and tutorial_data["pasos"]:
                            self.logger.debug("Tutorial parseado exitosamente")
                            return tutorial_data
                        else:
                            self.logger.warning("Tutorial no tiene estructura válida")
                            continue
                            
                    except json.JSONDecodeError:
                        continue
            
            self.logger.warning(f"No se pudo parsear tutorial: {clean_response[:100]}...")
            return None
                
        except Exception as e:
            self.logger.error(f"Error parseando tutorial: {e}")
            return None
    
    def _get_template_tutorial(self, tutorial_type: str) -> Dict:
        """Obtiene tutorial predefinido como fallback"""
        return self.tutorial_templates.get(tutorial_type, self.tutorial_templates["sistema"])
    
    def _load_tutorial_templates(self) -> Dict:
        """Carga templates predefinidos de tutoriales"""
        return {
            "consultas": {
                "tipo_tutorial": "consultas",
                "titulo": "Cómo hacer consultas de alumnos",
                "descripcion": "Aprende a buscar información de estudiantes usando lenguaje natural",
                "pasos": [
                    {
                        "numero": 1,
                        "titulo": "Escribe tu consulta",
                        "descripcion": "Describe qué información necesitas en español natural",
                        "ejemplo": "cuántos alumnos hay en total",
                        "consejos": ["Usa palabras simples", "No necesitas comandos técnicos"]
                    },
                    {
                        "numero": 2,
                        "titulo": "Revisa la respuesta",
                        "descripcion": "El sistema te dará la información solicitada",
                        "ejemplo": "Respuesta: 211 alumnos registrados",
                        "consejos": ["Lee toda la información", "Puedes hacer preguntas de seguimiento"]
                    }
                ],
                "ejemplos_completos": [
                    {
                        "titulo": "Buscar alumno específico",
                        "descripcion": "Encontrar información de un estudiante",
                        "pasos_ejemplo": ["Escribir: buscar García", "Ver lista de resultados", "Seleccionar alumno específico"]
                    }
                ],
                "problemas_comunes": [
                    {
                        "problema": "No encuentra al alumno",
                        "solucion": "Verifica la ortografía o usa solo el apellido"
                    }
                ],
                "consejos_adicionales": ["Puedes combinar criterios", "Usa referencias como 'del segundo'"],
                "siguientes_pasos": ["Probar consultas más específicas", "Generar constancias para alumnos encontrados"]
            },
            "constancias": {
                "tipo_tutorial": "constancias",
                "titulo": "Cómo generar constancias",
                "descripcion": "Aprende a crear documentos oficiales para estudiantes",
                "pasos": [
                    {
                        "numero": 1,
                        "titulo": "Busca al alumno",
                        "descripcion": "Primero encuentra al estudiante específico",
                        "ejemplo": "buscar Juan Pérez",
                        "consejos": ["Usa nombre completo si es posible", "Verifica que sea el alumno correcto"]
                    },
                    {
                        "numero": 2,
                        "titulo": "Solicita la constancia",
                        "descripcion": "Especifica el tipo de constancia necesaria",
                        "ejemplo": "constancia de estudios para Juan Pérez",
                        "consejos": ["Especifica el tipo: estudios, calificaciones, traslado", "Menciona si necesita foto"]
                    }
                ],
                "ejemplos_completos": [
                    {
                        "titulo": "Constancia completa",
                        "descripcion": "Proceso completo de generación",
                        "pasos_ejemplo": ["Buscar alumno", "Solicitar constancia", "Revisar vista previa", "Descargar PDF"]
                    }
                ],
                "problemas_comunes": [
                    {
                        "problema": "Alumno sin calificaciones",
                        "solucion": "Solo se pueden generar constancias de estudios"
                    }
                ],
                "consejos_adicionales": ["Revisa siempre la vista previa", "Guarda el PDF en lugar seguro"],
                "siguientes_pasos": ["Generar más constancias", "Explorar otros tipos de documentos"]
            },
            "sistema": {
                "tipo_tutorial": "sistema",
                "titulo": "Cómo usar el sistema",
                "descripcion": "Guía básica para empezar a usar el sistema escolar",
                "pasos": [
                    {
                        "numero": 1,
                        "titulo": "Entiende la interfaz",
                        "descripcion": "El sistema funciona como un chat conversacional",
                        "ejemplo": "Escribe preguntas en español normal",
                        "consejos": ["No uses comandos técnicos", "Habla como si fuera una persona"]
                    },
                    {
                        "numero": 2,
                        "titulo": "Haz tu primera consulta",
                        "descripcion": "Prueba con una consulta simple",
                        "ejemplo": "cuántos alumnos hay",
                        "consejos": ["Empieza con consultas simples", "Lee las respuestas completas"]
                    }
                ],
                "ejemplos_completos": [
                    {
                        "titulo": "Primera sesión",
                        "descripcion": "Qué hacer en tu primera vez",
                        "pasos_ejemplo": ["Hacer consulta simple", "Probar búsqueda", "Pedir ayuda específica"]
                    }
                ],
                "problemas_comunes": [
                    {
                        "problema": "No entiendo la respuesta",
                        "solucion": "Pide que te explique con más detalle"
                    }
                ],
                "consejos_adicionales": ["Experimenta con diferentes consultas", "Pide ayuda cuando la necesites"],
                "siguientes_pasos": ["Explorar consultas de alumnos", "Aprender a generar constancias"]
            }
        }
