"""
🎓 CATÁLOGO CENTRALIZADO DE ACCIONES PARA STUDENT

Centraliza TODA la información que Student necesita para tomar decisiones:
- Qué acciones existen
- Cuándo usar cada una
- Ejemplos específicos de mapeo
- Criterios de decisión claros

ELIMINA la confusión del Student sobre qué acción elegir.
"""

from typing import Dict, List
from app.core.config.school_config_manager import get_school_config_manager


class StudentActionCatalog:
    """
    🎯 CATÁLOGO CENTRALIZADO PARA STUDENT
    
    Proporciona información clara y coherente sobre:
    - Acciones disponibles
    - Criterios de decisión
    - Ejemplos de mapeo
    - Parámetros requeridos
    """
    
    @staticmethod
    def get_sub_intention_mapping() -> Dict:
        """
        🎯 MAPEO DIRECTO SUB-INTENCIÓN → ACCIÓN

        Student recibe sub-intención del Master y mapea directamente a acción.
        INDEPENDIENTE del Master - Student decide autónomamente cómo ejecutar.
        """
        return {
            # 🔍 BÚSQUEDAS
            "busqueda_simple": {
                "primary_action": "BUSCAR_UNIVERSAL",
                "description": "Búsqueda de alumnos específicos",
                "parameters": {
                    "criterio_principal": {"tabla": "alumnos", "campo": "nombre", "operador": "LIKE", "valor": "texto"}
                }
            },

            "busqueda_compleja": {
                "primary_action": "BUSCAR_UNIVERSAL",
                "description": "Búsqueda con múltiples criterios",
                "parameters": {
                    "criterio_principal": "...",
                    "filtros_adicionales": [...]
                }
            },

            "informacion_completa": {
                "primary_action": "BUSCAR_UNIVERSAL",
                "description": "Información detallada de alumno específico",
                "parameters": {
                    "criterio_principal": "...",
                    "campos_solicitados": ["todos"]
                }
            },

            # 📊 ESTADÍSTICAS
            "estadisticas": {
                "primary_action": "CALCULAR_ESTADISTICA",
                "description": "Conteos, distribuciones y análisis numéricos",
                "parameters": {
                    "conteo_simple": {"tipo": "conteo"},
                    "distribucion": {"tipo": "distribucion", "agrupar_por": "campo"},
                    "promedio": {"tipo": "promedio", "campo": "calificaciones"}
                },
                "fallback_action": "CONTAR_UNIVERSAL",
                "fallback_criteria": "Solo para operadores complejos (BETWEEN, IN, NOT_IN)"
            },

            # 📄 CONSTANCIAS
            "generar_constancia": {
                "primary_action": "GENERAR_CONSTANCIA_COMPLETA",
                "description": "Generación de constancias oficiales",
                "parameters": {
                    "alumno_identificador": "nombre_o_id",
                    "tipo_constancia": "estudio|calificaciones|traslado"
                }
            },

            # 🔄 TRANSFORMACIONES
            "transformacion_pdf": {
                "primary_action": "TRANSFORMAR_PDF",
                "description": "Transformación de documentos PDF",
                "parameters": {
                    "tipo_constancia": "estudio|traslado"
                }
            }
        }

    @staticmethod
    def get_action_decision_matrix() -> Dict:
        """
        🎯 MATRIZ DE DECISIÓN POR PATRONES DE CONSULTA

        Para casos donde Student necesita interpretar consultas directas.
        """
        return {
            "conteos_y_estadisticas": {
                "primary_action": "CALCULAR_ESTADISTICA",
                "description": "PRIMERA OPCIÓN para cualquier conteo o estadística",
                "patterns": [
                    "cuántos alumnos hay",
                    "cuántos alumnos hay en total",
                    "total de estudiantes",
                    "cuántos hay en 3er grado",
                    "cuántos del turno matutino",
                    "distribución por grado",
                    "cuántos por turno",
                    "estadísticas generales",
                    "promedio de calificaciones"
                ],
                "parameters": {
                    "conteo_simple": {"tipo": "conteo"},
                    "conteo_filtrado": {"tipo": "conteo", "filtro": {"campo": "valor"}},
                    "distribucion": {"tipo": "distribucion", "agrupar_por": "campo"},
                    "promedio": {"tipo": "promedio", "campo": "calificaciones"}
                },
                "fallback_action": "CONTAR_UNIVERSAL",
                "fallback_criteria": "Solo si necesitas operadores BETWEEN, IN, NOT_IN o múltiples filtros complejos"
            },
            
            "busquedas": {
                "primary_action": "BUSCAR_UNIVERSAL", 
                "description": "ÚNICA OPCIÓN para búsquedas de alumnos",
                "patterns": [
                    "buscar García",
                    "información de Juan Pérez", 
                    "datos de matrícula 123",
                    "alumno con CURP",
                    "alumnos de 3er grado",
                    "estudiantes del turno vespertino",
                    "dame la CURP de María"
                ],
                "parameters": {
                    "busqueda_simple": {"criterio_principal": {"tabla": "alumnos", "campo": "nombre", "operador": "LIKE", "valor": "texto"}},
                    "busqueda_filtrada": {"criterio_principal": "...", "filtros_adicionales": []}
                }
            },
            
            "constancias": {
                "primary_action": "GENERAR_CONSTANCIA_COMPLETA",
                "description": "ÚNICA OPCIÓN para generar constancias",
                "patterns": [
                    "constancia de estudios para Juan",
                    "certificado de calificaciones",
                    "constancia de traslado",
                    "generar constancia"
                ],
                "parameters": {
                    "basico": {"alumno_identificador": "nombre", "tipo_constancia": "estudio"},
                    "con_foto": {"alumno_identificador": "nombre", "tipo_constancia": "estudio", "incluir_foto": True}
                }
            },
            
            "transformaciones": {
                "primary_action": "TRANSFORMAR_PDF",
                "description": "ÚNICA OPCIÓN para transformar PDFs",
                "patterns": [
                    "transformar PDF a constancia",
                    "convertir PDF a formato estándar"
                ],
                "parameters": {
                    "basico": {"tipo_constancia": "estudio"}
                }
            }
        }
    
    @staticmethod
    def get_clear_examples() -> str:
        """
        🎯 EJEMPLOS CLAROS Y COHERENTES
        
        Proporciona ejemplos específicos sin contradicciones.
        """
        return """
🎯 EJEMPLOS CLAROS DE MAPEO CONSULTA → ACCIÓN:

═══════════════════════════════════════════════════════════════════════════════
📊 CONTEOS Y ESTADÍSTICAS → CALCULAR_ESTADISTICA:
═══════════════════════════════════════════════════════════════════════════════

✅ "cuántos alumnos hay" → CALCULAR_ESTADISTICA (tipo: "conteo")
✅ "cuántos alumnos hay en total" → CALCULAR_ESTADISTICA (tipo: "conteo") 
✅ "total de estudiantes" → CALCULAR_ESTADISTICA (tipo: "conteo")
✅ "cuántos hay en 3er grado" → CALCULAR_ESTADISTICA (tipo: "conteo", filtro: {"grado": "3"})
✅ "cuántos del turno matutino" → CALCULAR_ESTADISTICA (tipo: "conteo", filtro: {"turno": "MATUTINO"})
✅ "distribución por grado" → CALCULAR_ESTADISTICA (tipo: "distribucion", agrupar_por: "grado")
✅ "cuántos por turno" → CALCULAR_ESTADISTICA (tipo: "distribucion", agrupar_por: "turno")
✅ "promedio de calificaciones" → CALCULAR_ESTADISTICA (tipo: "promedio", campo: "calificaciones")

═══════════════════════════════════════════════════════════════════════════════
🔍 BÚSQUEDAS → BUSCAR_UNIVERSAL:
═══════════════════════════════════════════════════════════════════════════════

✅ "buscar García" → BUSCAR_UNIVERSAL (criterio_principal: {"tabla": "alumnos", "campo": "nombre", "operador": "LIKE", "valor": "García"})
✅ "información de Juan Pérez" → BUSCAR_UNIVERSAL (criterio_principal: {"tabla": "alumnos", "campo": "nombre", "operador": "LIKE", "valor": "Juan Pérez"})
✅ "alumnos de 3er grado" → BUSCAR_UNIVERSAL (criterio_principal: {"tabla": "datos_escolares", "campo": "grado", "operador": "=", "valor": "3"})
✅ "dame la CURP de María" → BUSCAR_UNIVERSAL (criterio_principal: {"tabla": "alumnos", "campo": "nombre", "operador": "LIKE", "valor": "María"}, campos_solicitados: ["curp"])

═══════════════════════════════════════════════════════════════════════════════
📄 CONSTANCIAS → GENERAR_CONSTANCIA_COMPLETA:
═══════════════════════════════════════════════════════════════════════════════

✅ "constancia de estudios para Juan" → GENERAR_CONSTANCIA_COMPLETA (alumno_identificador: "Juan", tipo_constancia: "estudio")
✅ "certificado de calificaciones" → GENERAR_CONSTANCIA_COMPLETA (tipo_constancia: "calificaciones")

═══════════════════════════════════════════════════════════════════════════════
🔄 TRANSFORMACIONES → TRANSFORMAR_PDF:
═══════════════════════════════════════════════════════════════════════════════

✅ "transformar PDF a constancia" → TRANSFORMAR_PDF (tipo_constancia: "estudio")
"""
    
    @staticmethod
    def get_decision_rules() -> str:
        """
        🎯 REGLAS DE DECISIÓN SIMPLES
        
        Criterios claros para que Student sepa qué elegir.
        """
        return """
🚨 REGLAS DE DECISIÓN PARA STUDENT:

1. **¿Es un CONTEO o ESTADÍSTICA?** → CALCULAR_ESTADISTICA
   - Palabras clave: "cuántos", "total", "distribución", "promedio"
   
2. **¿Es una BÚSQUEDA de alumnos?** → BUSCAR_UNIVERSAL  
   - Palabras clave: "buscar", "información de", "datos de", "dame"
   
3. **¿Es una CONSTANCIA?** → GENERAR_CONSTANCIA_COMPLETA
   - Palabras clave: "constancia", "certificado", "generar"
   
4. **¿Es una TRANSFORMACIÓN?** → TRANSFORMAR_PDF
   - Palabras clave: "transformar", "convertir" + "PDF"

🎯 REGLA DE ORO: En caso de duda, usa la PRIMERA OPCIÓN de cada categoría.
"""
    
    @staticmethod
    def generate_student_prompt_section() -> str:
        """
        🎯 GENERA SECCIÓN COMPLETA PARA PROMPTS DE STUDENT
        
        Reemplaza toda la información dispersa con una sección coherente.
        """
        school_config = get_school_config_manager()
        school_name = school_config.get_school_name()
        total_students = school_config.get_total_students()
        
        decision_matrix = StudentActionCatalog.get_action_decision_matrix()
        examples = StudentActionCatalog.get_clear_examples()
        rules = StudentActionCatalog.get_decision_rules()
        
        return f"""
═══════════════════════════════════════════════════════════════════════════════
🎓 CATÁLOGO DE ACCIONES CENTRALIZADO PARA STUDENT
═══════════════════════════════════════════════════════════════════════════════

🏫 CONTEXTO: {school_name} - {total_students} alumnos activos

{rules}

{examples}

═══════════════════════════════════════════════════════════════════════════════
🎯 MATRIZ DE DECISIÓN DETALLADA:
═══════════════════════════════════════════════════════════════════════════════

{StudentActionCatalog._format_decision_matrix(decision_matrix)}

🚨 IMPORTANTE: NO uses acciones que no estén en esta lista.
🚨 IMPORTANTE: Sigue EXACTAMENTE los ejemplos mostrados.
🚨 IMPORTANTE: En caso de duda, usa la PRIMERA OPCIÓN de cada categoría.
"""
    
    @staticmethod
    def _format_decision_matrix(matrix: Dict) -> str:
        """Formatea la matriz de decisión para el prompt"""
        formatted = ""
        for category, info in matrix.items():
            formatted += f"""
📊 {category.upper().replace('_', ' ')}:
   ├── Acción principal: {info['primary_action']}
   ├── Descripción: {info['description']}
   └── Patrones: {', '.join(info['patterns'][:3])}...
"""
        return formatted
