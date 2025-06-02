"""
Analizador de capacidades del sistema
Especializado en explicar qué puede hacer el sistema
"""

from typing import Dict, Any, List, Optional
from app.core.logging import get_logger

class CapabilityAnalyzer:
    """
    Clase especializada en analizar y explicar las capacidades del sistema
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.system_capabilities = self._load_system_capabilities()
    
    def analyze_system_capabilities(self, user_query: str, detected_entities: Dict) -> Optional[Dict]:
        """
        Analiza qué capacidades del sistema son relevantes para la consulta del usuario
        
        Args:
            user_query: Consulta original del usuario
            detected_entities: Entidades detectadas por el MasterInterpreter
            
        Returns:
            Dict con las capacidades relevantes organizadas
        """
        try:
            self.logger.debug(f"Analizando capacidades para: {user_query}")
            
            # Determinar qué tipo de capacidades busca el usuario
            capability_type = self._determine_capability_type(user_query, detected_entities)
            
            # Obtener capacidades relevantes
            relevant_capabilities = self._get_relevant_capabilities(capability_type)
            
            # Organizar respuesta
            capabilities_response = {
                "tipo_consulta": capability_type,
                "capacidades_principales": relevant_capabilities.get("principales", []),
                "ejemplos_practicos": relevant_capabilities.get("ejemplos", []),
                "modulos_disponibles": relevant_capabilities.get("modulos", []),
                "como_empezar": relevant_capabilities.get("como_empezar", []),
                "informacion_sistema": self._get_system_info()
            }
            
            self.logger.debug(f"Capacidades analizadas: {capability_type}")
            return capabilities_response
            
        except Exception as e:
            self.logger.error(f"Error analizando capacidades: {e}")
            return None
    
    def _determine_capability_type(self, user_query: str, detected_entities: Dict) -> str:
        """Determina qué tipo de capacidades busca el usuario"""
        query_lower = user_query.lower()
        
        # Palabras clave para diferentes tipos de consultas
        if any(word in query_lower for word in ["qué puedes hacer", "qué puede hacer", "capacidades", "funciones"]):
            return "capacidades_generales"
        elif any(word in query_lower for word in ["cómo usar", "cómo funciona", "tutorial", "guía"]):
            return "tutorial_uso"
        elif any(word in query_lower for word in ["consultas", "buscar", "alumnos", "estudiantes"]):
            return "consultas_alumnos"
        elif any(word in query_lower for word in ["constancias", "documentos", "certificados"]):
            return "constancias"
        elif any(word in query_lower for word in ["ayuda", "help", "asistencia"]):
            return "ayuda_general"
        else:
            return "capacidades_generales"
    
    def _get_relevant_capabilities(self, capability_type: str) -> Dict:
        """Obtiene las capacidades relevantes según el tipo"""
        capabilities_map = {
            "capacidades_generales": {
                "principales": [
                    "🔍 Buscar información de alumnos usando lenguaje natural",
                    "📊 Generar estadísticas escolares automáticamente", 
                    "📄 Crear constancias oficiales individuales",
                    "🔄 Transformar documentos entre formatos",
                    "💬 Mantener conversaciones contextuales",
                    "🆘 Proporcionar ayuda y tutoriales"
                ],
                "ejemplos": [
                    "\"cuántos alumnos hay en total\" → Cuenta todos los estudiantes",
                    "\"buscar a Juan\" → Encuentra todos los alumnos llamados Juan",
                    "\"alumnos de 2do grado\" → Lista estudiantes de segundo grado",
                    "\"constancia de estudios para María\" → Genera documento oficial"
                ],
                "modulos": ["Consultas de Alumnos", "Generación de Constancias", "Sistema de Ayuda"],
                "como_empezar": [
                    "1. Escribe tu consulta en lenguaje natural",
                    "2. El sistema entiende automáticamente qué necesitas",
                    "3. Recibes respuestas precisas y contextualizadas",
                    "4. Puedes hacer preguntas de seguimiento"
                ]
            },
            "consultas_alumnos": {
                "principales": [
                    "🔢 Contar alumnos con criterios específicos",
                    "🔍 Buscar estudiantes por nombre, parcial o completo",
                    "📚 Filtrar por grado, grupo, turno",
                    "📋 Obtener información específica (CURP, matrícula, etc.)",
                    "📊 Generar estadísticas automáticas",
                    "🔄 Combinar múltiples criterios de búsqueda"
                ],
                "ejemplos": [
                    "\"cuántos alumnos hay\" → Total de estudiantes registrados",
                    "\"buscar García\" → Todos los alumnos con apellido García",
                    "\"estudiantes del turno matutino\" → Lista por turno",
                    "\"alumnos de 3er grado grupo A\" → Filtro combinado",
                    "\"dame la CURP de Juan López\" → Información específica"
                ],
                "modulos": ["Base de Datos de Alumnos", "Motor de Búsqueda Inteligente"],
                "como_empezar": [
                    "1. Describe qué información necesitas en español natural",
                    "2. Usa términos como 'buscar', 'cuántos', 'alumnos de'",
                    "3. Combina criterios: grado + grupo + turno",
                    "4. Pide información específica cuando la necesites"
                ]
            },
            "constancias": {
                "principales": [
                    "📄 Constancias de estudios oficiales",
                    "📋 Constancias de calificaciones",
                    "🔄 Constancias de traslado",
                    "🖼️ Opción de incluir fotografía",
                    "📱 Vista previa antes de generar",
                    "💾 Descarga en formato PDF"
                ],
                "ejemplos": [
                    "\"constancia de estudios para Juan\" → Documento oficial",
                    "\"constancia de calificaciones para María\" → Con notas",
                    "\"constancia de traslado para Pedro\" → Para cambio de escuela"
                ],
                "modulos": ["Generador de Documentos", "Plantillas Oficiales"],
                "como_empezar": [
                    "1. Busca primero al alumno específico",
                    "2. Especifica el tipo de constancia necesaria",
                    "3. Revisa la vista previa generada",
                    "4. Descarga el documento final"
                ]
            },
            "tutorial_uso": {
                "principales": [
                    "💬 Interfaz de chat conversacional",
                    "🗣️ Comunicación en español natural",
                    "🔄 Contexto conversacional mantenido",
                    "📱 Respuestas inmediatas",
                    "🎯 Sugerencias automáticas",
                    "🆘 Ayuda contextual disponible"
                ],
                "ejemplos": [
                    "Escribe: \"ayuda\" → Obtén asistencia general",
                    "Escribe: \"buscar alumnos\" → Tutorial de búsquedas",
                    "Escribe: \"cómo generar constancias\" → Guía paso a paso"
                ],
                "modulos": ["Chat Engine", "Sistema de Ayuda Contextual"],
                "como_empezar": [
                    "1. Simplemente escribe lo que necesitas",
                    "2. No uses comandos técnicos, habla natural",
                    "3. El sistema te guiará paso a paso",
                    "4. Pide ayuda específica cuando la necesites"
                ]
            },
            "ayuda_general": {
                "principales": [
                    "🆘 Explicaciones de funcionalidades",
                    "📚 Tutoriales paso a paso",
                    "💡 Ejemplos prácticos",
                    "🔧 Solución de problemas",
                    "🎯 Guías contextuales",
                    "📖 Documentación interactiva"
                ],
                "ejemplos": [
                    "\"ayuda con consultas\" → Tutorial de búsquedas",
                    "\"cómo usar el sistema\" → Guía completa",
                    "\"ejemplos de constancias\" → Casos prácticos"
                ],
                "modulos": ["Sistema de Ayuda Inteligente", "Base de Conocimiento"],
                "como_empezar": [
                    "1. Pregunta sobre cualquier funcionalidad",
                    "2. Solicita ejemplos específicos",
                    "3. Pide tutoriales paso a paso",
                    "4. Obtén ayuda contextual inmediata"
                ]
            }
        }
        
        return capabilities_map.get(capability_type, capabilities_map["capacidades_generales"])
    
    def _get_system_info(self) -> Dict:
        """Información básica del sistema"""
        return {
            "nombre": "Sistema de Gestión Escolar Inteligente",
            "escuela": "PROF. MAXIMO GAMIZ FERNANDEZ",
            "ciclo_escolar": "2024-2025",
            "tipo": "Sistema conversacional con IA",
            "idioma": "Español natural",
            "estado": "Completamente funcional"
        }
    
    def _load_system_capabilities(self) -> Dict:
        """Carga las capacidades completas del sistema"""
        return {
            "modulos_principales": [
                "Consultas de Alumnos",
                "Generación de Constancias", 
                "Sistema de Ayuda",
                "Transformación de Documentos"
            ],
            "tecnologias": [
                "Inteligencia Artificial",
                "Procesamiento de Lenguaje Natural",
                "Base de Datos Escolar",
                "Generación de PDFs"
            ],
            "capacidades_avanzadas": [
                "Comprensión contextual",
                "Auto-reflexión conversacional",
                "Detección de intenciones",
                "Continuaciones inteligentes"
            ]
        }
