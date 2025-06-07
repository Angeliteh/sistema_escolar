"""
🧠 MASTER KNOWLEDGE - CEREBRO DEL SISTEMA
Conocimiento profundo de capacidades, limitaciones y mejores prácticas
"""

from typing import Dict, List, Optional, Any
import logging

class MasterKnowledge:
    """
    🧠 CEREBRO DEL MASTER - Conocimiento profundo del sistema escolar
    
    PROPÓSITO:
    - Entender capacidades y limitaciones de cada interpreter
    - Validar factibilidad antes de delegar
    - Sugerir alternativas cuando algo no es posible
    - Interpretar reportes de manera inteligente
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 🎯 MAPA COMPLETO DE INTERPRETERS Y CAPACIDADES
        self.interpreters_map = {
            "StudentQueryInterpreter": {
                "domain": "Gestión completa de alumnos y documentos escolares",
                "database_info": {
                    "total_students": 211,
                    "grades": "1° a 6° grado",
                    "structure": "alumnos + datos_escolares (con calificaciones JSON)"
                },
                "intentions": {
                    "consulta_alumnos": {
                        "description": "TODO sobre estudiantes - búsquedas, estadísticas, constancias",
                        "sub_intentions": {
                            "busqueda_simple": {
                                "description": "Buscar alumnos con 1-2 criterios básicos",
                                "capabilities": ["CURP", "matrícula", "nombre", "grado", "grupo", "turno"],
                                "examples": ["buscar García", "alumnos de 3er grado", "CURP RARR150330..."]
                            },
                            "busqueda_compleja": {
                                "description": "Búsquedas con múltiples criterios o campos especiales",
                                "capabilities": ["criterios combinados", "filtros múltiples"],
                                "examples": ["García de 3er grado turno matutino"]
                            },
                            "busqueda_filtrada": {
                                "description": "Filtros sobre resultados existentes en contexto",
                                "capabilities": ["filtrar por grupo", "filtrar por turno", "filtrar por criterios"],
                                "examples": ["de esos dame los del grupo B", "de la lista anterior los del turno matutino"]
                            },
                            "estadisticas": {
                                "description": "Análisis numérico y distribuciones",
                                "capabilities": {
                                    "available": [
                                        "conteos simples (cuántos alumnos)",
                                        "conteos agrupados (por grado, turno, grupo)",
                                        "distribuciones porcentuales",
                                        "promedio de edad (calculado desde fecha_nacimiento)"
                                    ],
                                    "limited": [
                                        "promedio de calificaciones (JSON complejo, análisis básico)"
                                    ],
                                    "not_available": [
                                        "rankings de estudiantes",
                                        "comparaciones entre grupos",
                                        "análisis por materia específica"
                                    ]
                                },
                                "examples": ["cuántos alumnos hay", "distribución por grados"]
                            },
                            "generar_constancia": {
                                "description": "Generación de documentos PDF oficiales",
                                "capabilities": {
                                    "types": ["estudios", "calificaciones", "traslado"],
                                    "options": ["con foto", "sin foto"],
                                    "formats": ["PDF oficial con membrete escolar"]
                                },
                                "examples": ["constancia para Juan Pérez", "certificado con foto"]
                            }
                        }
                    },
                    "transformacion_pdf": {
                        "description": "Conversión de PDFs cargados a diferentes formatos",
                        "capabilities": ["PDF → constancia estudios", "PDF → constancia traslado"],
                        "examples": ["transformar PDF cargado", "convertir a constancia de traslado"],
                        "sub_intentions": {
                            "transformacion_pdf": {
                                "description": "Transformar PDF cargado a constancia específica",
                                "examples": ["transformar a constancia de traslado", "convertir PDF a constancia de estudios"]
                            }
                        }
                    }
                },
                "technical_limitations": {
                    "calificaciones_json": {
                        "issue": "Calificaciones almacenadas en JSON, no tabla separada",
                        "impact": "Análisis por materia específica es complejo",
                        "workaround": "Solo análisis general de presencia/ausencia"
                    },
                    "advanced_analytics": {
                        "issue": "Rankings y comparaciones en desarrollo",
                        "alternatives": ["distribuciones", "conteos agrupados", "promedios generales"]
                    }
                }
            },
            
            "HelpInterpreter": {
                "domain": "Ayuda y explicaciones del sistema",
                "intentions": {
                    "ayuda_sistema": {
                        "description": "Explicaciones sobre capacidades y uso",
                        "sub_intentions": {
                            "pregunta_capacidades": {
                                "description": "¿Qué puede hacer el sistema?",
                                "examples": ["qué puedes hacer", "qué tipos de constancias generas"]
                            },
                            "pregunta_tecnica": {
                                "description": "¿Cómo funciona algo específico?",
                                "examples": ["cómo buscar alumnos", "cómo generar constancias"]
                            }
                        }
                    }
                }
            },
            
            "GeneralInterpreter": {
                "domain": "Conversación general y temas no escolares",
                "status": "planned",
                "intentions": {
                    "conversacion_general": {
                        "description": "Chat casual, saludos, temas generales",
                        "examples": ["hola", "cómo estás", "cuéntame un chiste"]
                    }
                }
            }
        }
    
    def can_handle_request(self, intention_type: str, sub_intention: str = None, 
                          query_details: dict = None) -> Dict[str, Any]:
        """
        🎯 EVALÚA SI EL SISTEMA PUEDE MANEJAR UNA SOLICITUD
        
        Returns:
        {
            "can_handle": bool,
            "confidence": float,
            "limitations": list,
            "alternatives": list,
            "explanation": str,
            "best_interpreter": str
        }
        """
        try:
            # Buscar el interpreter que maneja esta intención
            for interpreter_name, interpreter_info in self.interpreters_map.items():
                intentions = interpreter_info.get("intentions", {})
                
                if intention_type in intentions:
                    intention_info = intentions[intention_type]
                    
                    # Evaluar sub-intención si se proporciona
                    if sub_intention:
                        sub_intentions = intention_info.get("sub_intentions", {})
                        if sub_intention in sub_intentions:
                            sub_info = sub_intentions[sub_intention]
                            return self._evaluate_capability(
                                interpreter_name, intention_type, sub_intention, 
                                sub_info, query_details
                            )
                    else:
                        # Evaluar intención general
                        return self._evaluate_general_capability(
                            interpreter_name, intention_type, intention_info, query_details
                        )
            
            # No se encontró handler - generar explicación natural
            user_query = query_details.get("original_query", "") if query_details else ""
            natural_explanation = self._generate_natural_limitation_explanation(intention_type, user_query)

            return {
                "can_handle": False,
                "confidence": 0.0,
                "limitations": ["Funcionalidad no disponible"],
                "alternatives": self._suggest_natural_alternatives(),
                "explanation": natural_explanation,
                "best_interpreter": None
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluando capacidad: {e}")
            return {
                "can_handle": False,
                "confidence": 0.0,
                "limitations": [f"Error interno: {str(e)}"],
                "alternatives": [],
                "explanation": "Error evaluando la solicitud",
                "best_interpreter": None
            }
    
    def _evaluate_capability(self, interpreter_name: str, intention: str, 
                           sub_intention: str, sub_info: dict, query_details: dict) -> Dict[str, Any]:
        """🔍 EVALÚA CAPACIDAD ESPECÍFICA DE UNA SUB-INTENCIÓN"""
        
        # Casos especiales para estadísticas
        if sub_intention in ["estadisticas", "conteo_simple", "estadistica_distribucion"]:
            return self._evaluate_statistics_capability(query_details)
        
        # Casos especiales para búsquedas
        if sub_intention in ["busqueda_simple", "busqueda_compleja"]:
            return self._evaluate_search_capability(sub_intention, query_details)
        
        # Casos especiales para constancias
        if sub_intention == "generar_constancia":
            return self._evaluate_constancia_capability(query_details)

        # Casos especiales para transformaciones de PDF
        if sub_intention == "transformacion_pdf" or intention == "transformacion_pdf":
            return self._evaluate_transformation_capability(query_details)

        # Capacidad general disponible
        return {
            "can_handle": True,
            "confidence": 0.9,
            "limitations": [],
            "alternatives": [],
            "explanation": f"Capacidad '{sub_intention}' disponible en {interpreter_name}",
            "best_interpreter": interpreter_name
        }
    
    def _evaluate_statistics_capability(self, query_details: dict) -> Dict[str, Any]:
        """📊 EVALÚA CAPACIDADES ESTADÍSTICAS ESPECÍFICAS"""
        
        query_text = query_details.get("original_query", "").lower() if query_details else ""
        
        # Detectar solicitudes no disponibles
        if any(word in query_text for word in ["ranking", "mejor", "peor", "comparar"]):
            return {
                "can_handle": False,
                "confidence": 0.3,
                "limitations": ["Rankings y comparaciones están en desarrollo"],
                "alternatives": [
                    "Puedo mostrar distribuciones por grado",
                    "Puedo calcular conteos agrupados",
                    "Puedo generar estadísticas generales"
                ],
                "explanation": "Los rankings no están disponibles en este momento, pero puedo ofrecer análisis alternativos",
                "best_interpreter": "StudentQueryInterpreter"
            }
        
        # Detectar análisis por materia específica
        materias = ["matemáticas", "español", "ciencias", "historia", "geografía"]
        if any(materia in query_text for materia in materias):
            return {
                "can_handle": False,
                "confidence": 0.4,
                "limitations": ["Análisis por materia específica es limitado (calificaciones en JSON)"],
                "alternatives": [
                    "Puedo calcular promedio general de calificaciones",
                    "Puedo mostrar quién tiene/no tiene calificaciones",
                    "Puedo generar distribuciones por grado"
                ],
                "explanation": "El análisis por materia específica tiene limitaciones técnicas",
                "best_interpreter": "StudentQueryInterpreter"
            }
        
        # Estadísticas disponibles
        return {
            "can_handle": True,
            "confidence": 0.95,
            "limitations": ["Promedios de calificaciones son básicos (JSON)"],
            "alternatives": [],
            "explanation": "Estadísticas básicas y distribuciones están completamente disponibles",
            "best_interpreter": "StudentQueryInterpreter"
        }

    def _evaluate_search_capability(self, sub_intention: str, query_details: dict) -> Dict[str, Any]:
        """🔍 EVALÚA CAPACIDADES DE BÚSQUEDA"""

        # Todas las búsquedas están disponibles
        return {
            "can_handle": True,
            "confidence": 0.98,
            "limitations": [],
            "alternatives": [],
            "explanation": f"Búsquedas {sub_intention} completamente disponibles",
            "best_interpreter": "StudentQueryInterpreter"
        }

    def _evaluate_constancia_capability(self, query_details: dict) -> Dict[str, Any]:
        """📄 EVALÚA CAPACIDADES DE CONSTANCIAS"""

        # Todas las constancias están disponibles
        return {
            "can_handle": True,
            "confidence": 0.98,
            "limitations": [],
            "alternatives": [],
            "explanation": "Generación de constancias completamente disponible",
            "best_interpreter": "StudentQueryInterpreter"
        }

    def _evaluate_transformation_capability(self, query_details: dict) -> Dict[str, Any]:
        """🔄 EVALÚA CAPACIDADES DE TRANSFORMACIÓN DE PDF"""

        # Transformaciones de PDF están disponibles
        return {
            "can_handle": True,
            "confidence": 0.95,
            "limitations": ["Requiere PDF cargado previamente"],
            "alternatives": [],
            "explanation": "Transformación de PDF a constancias completamente disponible",
            "best_interpreter": "StudentQueryInterpreter"
        }

    def _evaluate_general_capability(self, interpreter_name: str, intention: str,
                                   intention_info: dict, query_details: dict) -> Dict[str, Any]:
        """🎯 EVALÚA CAPACIDAD GENERAL DE UNA INTENCIÓN"""

        return {
            "can_handle": True,
            "confidence": 0.9,
            "limitations": [],
            "alternatives": [],
            "explanation": f"Intención '{intention}' disponible en {interpreter_name}",
            "best_interpreter": interpreter_name
        }

    def _suggest_general_alternatives(self) -> List[str]:
        """💡 SUGIERE ALTERNATIVAS GENERALES"""

        return [
            "Puedo buscar información de alumnos",
            "Puedo generar estadísticas y conteos",
            "Puedo crear constancias oficiales",
            "Puedo explicar las capacidades del sistema"
        ]

    def _suggest_natural_alternatives(self) -> List[str]:
        """💡 SUGIERE ALTERNATIVAS DE MANERA NATURAL"""

        return [
            "Buscar información de estudiantes",
            "Generar estadísticas y conteos",
            "Crear constancias oficiales",
            "Obtener ayuda sobre el sistema"
        ]

    def _generate_natural_limitation_explanation(self, intention_type: str, user_query: str) -> str:
        """🎭 GENERA EXPLICACIONES NATURALES PARA LIMITACIONES"""

        # Mapeo de intenciones técnicas a explicaciones naturales
        natural_explanations = {
            "consulta_alumnos": self._explain_student_query_limitation(user_query),
            "generar_constancia": "La generación de constancias requiere información específica del estudiante",
            "estadistica": self._explain_statistics_limitation(user_query),
            "transformacion": "La transformación de documentos no está disponible en este momento",
            "ayuda_sistema": "Esa función de ayuda específica no está disponible",
            "aclaracion_requerida": self._explain_clarification_limitation(user_query)
        }

        return natural_explanations.get(intention_type, "Esa funcionalidad no está disponible en este momento")

    def _explain_student_query_limitation(self, user_query: str) -> str:
        """🎓 EXPLICA LIMITACIONES DE CONSULTAS DE ESTUDIANTES"""

        query_lower = user_query.lower()

        if any(word in query_lower for word in ["ranking", "mejor", "peor", "comparar"]):
            return "Los rankings de estudiantes no están disponibles en este momento"
        elif any(word in query_lower for word in ["matemáticas", "español", "ciencias", "historia"]):
            return "El análisis por materia específica tiene limitaciones técnicas"
        else:
            return "Esa consulta específica no está disponible"

    def _explain_statistics_limitation(self, user_query: str) -> str:
        """📊 EXPLICA LIMITACIONES DE ESTADÍSTICAS"""

        query_lower = user_query.lower()

        if any(word in query_lower for word in ["ranking", "mejor", "peor"]):
            return "Los rankings y comparaciones están en desarrollo"
        elif any(word in query_lower for word in ["promedio", "materia"]):
            return "Los promedios por materia específica tienen limitaciones técnicas"
        else:
            # 🔧 ARREGLO: No rechazar conteos básicos que SÍ están disponibles
            return "Estadísticas básicas y conteos están disponibles"

    def _explain_clarification_limitation(self, user_query: str) -> str:
        """❓ EXPLICA LIMITACIONES DE ACLARACIONES"""

        return "No pude entender completamente tu solicitud"

    def interpret_student_report(self, student_data: dict, original_query: str) -> Dict[str, Any]:
        """
        🔍 INTERPRETA REPORTES DEL STUDENT DE MANERA INTELIGENTE

        Analiza qué pasó internamente y sugiere mejoras o alternativas
        """
        try:
            action_used = student_data.get("action", "")
            row_count = student_data.get("row_count", 0)
            success = student_data.get("success", True)

            # Análisis por tipo de acción
            if "BUSCAR" in action_used:
                return self._interpret_search_report(student_data, original_query)
            elif "CALCULAR_ESTADISTICA" in action_used:
                return self._interpret_statistics_report(student_data, original_query)
            elif "GENERAR_CONSTANCIA" in action_used:
                return self._interpret_constancia_report(student_data, original_query)
            elif "TRANSFORMAR" in action_used:
                return self._interpret_transformation_report(student_data, original_query)
            else:
                return self._interpret_general_report(student_data, original_query)

        except Exception as e:
            self.logger.error(f"Error interpretando reporte: {e}")
            return {
                "interpretation": "Error analizando el reporte del sistema",
                "suggestions": ["Intenta reformular la consulta"],
                "user_explanation": "Hubo un problema interno analizando los resultados"
            }

    def _interpret_search_report(self, student_data: dict, original_query: str) -> Dict[str, Any]:
        """🔍 INTERPRETA REPORTES DE BÚSQUEDA"""

        row_count = student_data.get("row_count", 0)

        if row_count == 0:
            # Analizar por qué no encontró nada
            if "curp" in original_query.lower():
                return {
                    "interpretation": "CURP no encontrada en la base de datos",
                    "suggestions": [
                        "Verificar que la CURP esté bien escrita (18 caracteres)",
                        "Buscar por nombre en su lugar",
                        "Verificar que el alumno esté registrado"
                    ],
                    "user_explanation": "No encontré esa CURP. Podría estar mal escrita o el alumno no está registrado."
                }
            elif "matricula" in original_query.lower():
                return {
                    "interpretation": "Matrícula no encontrada",
                    "suggestions": [
                        "Verificar el formato de la matrícula",
                        "Buscar por nombre del alumno",
                        "Revisar si la matrícula está actualizada"
                    ],
                    "user_explanation": "No encontré esa matrícula. ¿Quieres buscar por nombre?"
                }
            else:
                return {
                    "interpretation": "Criterio de búsqueda no encontrado",
                    "suggestions": [
                        "Intentar con criterios más amplios",
                        "Verificar ortografía",
                        "Usar búsqueda parcial (solo apellido)"
                    ],
                    "user_explanation": "No encontré coincidencias. Intenta con criterios más amplios."
                }

        elif row_count == 1:
            return {
                "interpretation": "Búsqueda exitosa - alumno específico encontrado",
                "suggestions": [
                    "Puedes generar una constancia para este alumno",
                    "Puedes pedir información más detallada"
                ],
                "user_explanation": "¡Perfecto! Encontré exactamente al alumno que buscas."
            }

        elif row_count <= 10:
            return {
                "interpretation": "Búsqueda exitosa - lista pequeña manejable",
                "suggestions": [
                    "Puedes filtrar por criterios adicionales",
                    "Puedes seleccionar un alumno específico",
                    "Puedes generar constancias para varios"
                ],
                "user_explanation": f"Encontré {row_count} alumnos. ¿Quieres filtrar más o seleccionar uno específico?"
            }

        else:
            return {
                "interpretation": "Búsqueda exitosa - lista grande",
                "suggestions": [
                    "Agregar filtros para reducir resultados",
                    "Buscar por criterios más específicos",
                    "Filtrar por grado, grupo o turno"
                ],
                "user_explanation": f"Encontré {row_count} alumnos. Te recomiendo filtrar por grado, grupo o turno."
            }

    def _interpret_statistics_report(self, student_data: dict, original_query: str) -> Dict[str, Any]:
        """📊 INTERPRETA REPORTES DE ESTADÍSTICAS"""

        row_count = student_data.get("row_count", 0)

        if row_count == 0:
            return {
                "interpretation": "No se pudieron calcular estadísticas",
                "suggestions": [
                    "Verificar que hay datos en la base",
                    "Intentar con criterios más amplios",
                    "Revisar filtros aplicados"
                ],
                "user_explanation": "No pude calcular estadísticas con esos criterios."
            }

        elif "distribución" in original_query.lower() or "distribucion" in original_query.lower():
            return {
                "interpretation": "Distribución calculada exitosamente",
                "suggestions": [
                    "Puedes filtrar por criterios específicos",
                    "Puedes generar constancias para grupos específicos",
                    "Puedes pedir análisis más detallado"
                ],
                "user_explanation": f"¡Perfecto! Calculé la distribución con {row_count} grupos."
            }

        else:
            return {
                "interpretation": "Estadísticas calculadas exitosamente",
                "suggestions": [
                    "Puedes pedir análisis más específicos",
                    "Puedes filtrar por subgrupos",
                    "Puedes generar reportes detallados"
                ],
                "user_explanation": f"Estadísticas calculadas exitosamente ({row_count} resultados)."
            }

    def _interpret_constancia_report(self, student_data: dict, original_query: str) -> Dict[str, Any]:
        """📄 INTERPRETA REPORTES DE CONSTANCIAS"""

        success = student_data.get("success", True)

        if success:
            return {
                "interpretation": "Constancia generada exitosamente",
                "suggestions": [
                    "Puedes descargar el PDF",
                    "Puedes generar más constancias",
                    "Puedes modificar el formato si necesitas"
                ],
                "user_explanation": "¡Constancia generada exitosamente! Ya puedes descargarla."
            }
        else:
            return {
                "interpretation": "Error generando constancia",
                "suggestions": [
                    "Verificar que el alumno existe",
                    "Revisar que los datos estén completos",
                    "Intentar con otro tipo de constancia"
                ],
                "user_explanation": "Hubo un problema generando la constancia. Verifica los datos del alumno."
            }

    def _interpret_transformation_report(self, student_data: dict, original_query: str) -> Dict[str, Any]:
        """🔄 INTERPRETA REPORTES DE TRANSFORMACIONES"""

        success = student_data.get("success", True)

        if success:
            return {
                "interpretation": "Transformación de PDF exitosa",
                "suggestions": [
                    "Puedes comparar con el original",
                    "Puedes descargar el nuevo formato",
                    "Puedes hacer más transformaciones"
                ],
                "user_explanation": "¡PDF transformado exitosamente! Revisa el resultado."
            }
        else:
            return {
                "interpretation": "Error en transformación de PDF",
                "suggestions": [
                    "Verificar que el PDF esté cargado",
                    "Revisar el formato del archivo",
                    "Intentar cargar el PDF nuevamente"
                ],
                "user_explanation": "Hubo un problema transformando el PDF. Verifica que esté bien cargado."
            }

    def _interpret_general_report(self, student_data: dict, original_query: str) -> Dict[str, Any]:
        """🎯 INTERPRETA REPORTES GENERALES"""

        return {
            "interpretation": "Operación completada",
            "suggestions": [
                "Puedes hacer más consultas",
                "Puedes pedir información adicional",
                "Puedes generar documentos relacionados"
            ],
            "user_explanation": "Operación completada exitosamente."
        }

    def get_system_capabilities_summary(self) -> str:
        """📋 RESUMEN DE CAPACIDADES DEL SISTEMA"""

        return """
🏫 SISTEMA ESCOLAR "PROF. MAXIMO GAMIZ FERNANDEZ"

📊 BASE DE DATOS: 211 alumnos (1° a 6° grado)

🎯 CAPACIDADES PRINCIPALES:

🔍 BÚSQUEDAS:
• Por CURP, matrícula, nombre (completo o parcial)
• Por grado, grupo, turno
• Criterios combinados

📊 ESTADÍSTICAS:
• Conteos simples y agrupados
• Distribuciones porcentuales
• Promedio de edad
• Análisis básico de calificaciones

📄 CONSTANCIAS:
• Estudios, calificaciones, traslado
• Con o sin foto
• Formato PDF oficial

🔄 TRANSFORMACIONES:
• PDF → diferentes formatos de constancia
• Comparación con originales

⚠️ LIMITACIONES:
• Rankings en desarrollo
• Análisis por materia específica limitado
• Calificaciones en formato JSON (análisis básico)
"""
