"""
🎯 CATÁLOGO CENTRALIZADO DEL SISTEMA

Todas las intenciones, sub-intenciones, acciones y capacidades
en un solo lugar para fácil modificación y mantenimiento.

Este archivo reemplaza la información dispersa en múltiples archivos
y permite inyección dinámica en prompts.
"""

from typing import Dict, List
from app.core.config.school_config_manager import get_school_config_manager


class SystemCatalog:
    """
    🎯 CATÁLOGO CENTRALIZADO DEL SISTEMA ESCOLAR
    
    Contiene todas las intenciones, sub-intenciones, especialistas y acciones
    disponibles en el sistema. Se usa para generar prompts dinámicamente.
    """
    
    @staticmethod
    def get_available_intentions() -> Dict:
        """
        📋 INTENCIONES COMPLETAS DEL SISTEMA

        Basado en la información actual funcionando extraída de:
        - master_interpreter.py (system_map)
        - master_knowledge.py (interpreters_map)
        - Prompts actuales del Master

        Returns:
            Dict con todas las intenciones, sub-intenciones y ejemplos
        """
        # 🎯 OBTENER CONFIGURACIÓN DINÁMICA
        school_config = get_school_config_manager()
        school_name = school_config.get_school_name()
        data_scope = school_config.get_data_scope_text()

        return {
            "consulta_alumnos": {
                "description": f"TODO sobre alumnos de la escuela {school_name} ({data_scope})",
                "specialist": "StudentQueryInterpreter",
                "database_access": True,
                "priority": 1,  # Máxima prioridad para consultas escolares
                "sub_intentions": {
                    "busqueda_simple": {
                        "description": "Buscar alumno específico por nombre, matrícula, CURP, grado, grupo, turno (1-2 criterios básicos)",
                        "examples": [
                            "buscar García",
                            "información de Juan Pérez",
                            "datos de matrícula 123",
                            "alumno con CURP RARR150330...",
                            "alumnos de 3er grado",
                            "estudiantes del turno vespertino"
                        ],
                        "capabilities": ["nombre", "matrícula", "CURP", "grado", "grupo", "turno"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "busqueda_compleja": {
                        "description": "Búsquedas con múltiples criterios combinados (3+ criterios o campos especiales)",
                        "examples": [
                            "García de 3er grado turno matutino",
                            "alumnos con promedio mayor a 8",
                            "estudiantes de grupo A con calificaciones altas"
                        ],
                        "capabilities": ["criterios combinados", "filtros múltiples", "promedios"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },


                    "estadisticas": {
                        "description": "Conteos, distribuciones, análisis numéricos y estadísticas",
                        "examples": [
                            "cuántos alumnos hay",
                            "distribución por grados",
                            "estadísticas del turno vespertino",
                            "total de estudiantes por grupo",
                            "análisis de calificaciones"
                        ],
                        "capabilities": ["conteos", "distribuciones", "promedios", "análisis numérico"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "generar_constancia": {
                        "description": "Generar constancias oficiales para alumnos específicos",
                        "examples": [
                            "constancia para Franco Alexander",
                            "certificado de estudios de María",
                            "generar constancia de Juan Pérez",
                            "generale una constancia de calificaciones",
                            "genera constancia para ese alumno",
                            "crea una constancia de estudios",
                            "documento oficial para el alumno",
                            "constancia de calificaciones a ese alumno"
                        ],
                        "capabilities": ["constancias de estudio", "certificados", "documentos oficiales"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "transformacion_pdf": {
                        "description": "Transformación de constancias entre formatos",
                        "examples": [
                            "convertir constancia a formato de estudios",
                            "cambiar formato PDF",
                            "transformar a constancia de calificaciones"
                        ],
                        "capabilities": ["conversión de formatos", "transformación de documentos"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    }
                }
            },
            
            "ayuda_sistema": {
                "description": "Ayuda sobre el sistema, capacidades, creador, funcionamiento y soporte técnico",
                "specialist": "HelpInterpreter",
                "database_access": False,
                "priority": 2,
                "sub_intentions": {
                    "explicacion_general": {
                        "description": "Capacidades generales del sistema y qué puede hacer",
                        "examples": [
                            "qué puedes hacer",
                            "ayuda",
                            "capacidades del sistema",
                            "qué tipos de consultas manejas"
                        ],
                        "capabilities": ["explicación de capacidades", "guía general"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "tutorial_funciones": {
                        "description": "Cómo usar funciones específicas del sistema",
                        "examples": [
                            "cómo buscar alumnos",
                            "cómo generar constancias",
                            "tutorial de uso",
                            "guía paso a paso"
                        ],
                        "capabilities": ["tutoriales", "guías de uso", "instrucciones"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "sobre_creador": {
                        "description": "Información sobre Angel, el creador del sistema",
                        "examples": [
                            "quién te creó",
                            "quién es Angel",
                            "tu creador",
                            "información del desarrollador"
                        ],
                        "capabilities": ["información del creador", "historia del desarrollo"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "auto_consciencia": {
                        "description": "Identidad y naturaleza del asistente de IA",
                        "examples": [
                            "qué eres",
                            "quién eres",
                            "cómo te defines",
                            "tu identidad"
                        ],
                        "capabilities": ["auto-explicación", "identidad del asistente"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "ventajas_sistema": {
                        "description": "Beneficios y ventajas de usar IA vs métodos tradicionales",
                        "examples": [
                            "por qué usar IA",
                            "ventajas del sistema",
                            "beneficios vs Excel",
                            "qué mejoras ofreces"
                        ],
                        "capabilities": ["comparaciones", "beneficios", "ventajas competitivas"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "casos_uso_avanzados": {
                        "description": "Funciones impresionantes y casos de uso avanzados",
                        "examples": [
                            "sorpréndeme",
                            "qué más puedes hacer",
                            "funciones avanzadas",
                            "casos impresionantes"
                        ],
                        "capabilities": ["casos avanzados", "funciones impresionantes"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    },
                    "limitaciones_honestas": {
                        "description": "Limitaciones y restricciones del sistema",
                        "examples": [
                            "cuáles son tus limitaciones",
                            "qué no puedes hacer",
                            "restricciones del sistema",
                            "limitaciones técnicas"
                        ],
                        "capabilities": ["transparencia", "limitaciones", "honestidad"]
                        # ❌ ELIMINADO: "actions" - Master NO debe conocer acciones específicas
                    }
                }
            },
            


            "conversacion_general": {
                "description": "Conversación casual y temas no relacionados al sistema escolar",
                "specialist": "GeneralInterpreter",
                "database_access": False,
                "priority": 4,
                "sub_intentions": {
                    "saludo": {
                        "description": "Saludos y presentaciones",
                        "examples": [
                            "hola",
                            "buenos días",
                            "¿cómo estás?",
                            "buenas tardes"
                        ],
                        "capabilities": ["saludos amigables", "presentación del sistema"]
                    },
                    "chat_casual": {
                        "description": "Conversación no relacionada al sistema",
                        "examples": [
                            "¿qué tal el clima?",
                            "cuéntame un chiste",
                            "háblame de ti",
                            "conversación general"
                        ],
                        "capabilities": ["conversación natural", "redirección educada al sistema"]
                    }
                }
            }
        }
    
    @staticmethod
    def get_specialist_capabilities() -> Dict:
        """
        🎯 CAPACIDADES ESPECÍFICAS DE CADA ESPECIALISTA
        
        Información detallada sobre qué puede hacer cada intérprete,
        sus acciones disponibles y limitaciones.
        """
        # 🎯 OBTENER CONFIGURACIÓN DINÁMICA
        school_config = get_school_config_manager()
        school_name = school_config.get_school_name()
        data_scope = school_config.get_data_scope_text()
        total_students = school_config.get_total_students()

        return {
            "StudentQueryInterpreter": {
                "description": f"Especialista en consultas escolares de {total_students} alumnos activos",
                "database_access": True,
                "data_scope": data_scope,
                "school_name": school_name,
                "available_actions": [
                    "BUSCAR_UNIVERSAL",
                    "CALCULAR_ESTADISTICA", 
                    "CONTAR_UNIVERSAL",
                    "PREPARAR_DATOS_CONSTANCIA",
                    "GENERAR_CONSTANCIA_COMPLETA",
                    "GENERAR_LISTADO_COMPLETO",
                    "FILTRAR_POR_CALIFICACIONES",
                    "TRANSFORMAR_PDF"
                ],
                "capabilities": [
                    "Búsquedas por cualquier campo",
                    "Estadísticas y conteos",
                    "Generación de constancias oficiales",
                    "Análisis de calificaciones",
                    "Filtrado de resultados",
                    "Transformación de PDFs"
                ],
                "limitations": [
                    "Solo datos de alumnos activos (no históricos)",
                    "Constancias limitadas a formatos predefinidos",
                    "No puede modificar datos, solo consultar"
                ]
            },
            
            "HelpInterpreter": {
                "description": "Especialista en ayuda del sistema y auto-explicación con personalidad",
                "database_access": False,
                "data_scope": "Conocimiento del sistema, capacidades, limitaciones, información sobre Angel",
                "available_actions": [
                    "EXPLICACION_GENERAL",
                    "TUTORIAL_FUNCIONES",
                    "SOBRE_CREADOR",
                    "AUTO_CONSCIENCIA",
                    "VENTAJAS_SISTEMA",
                    "CASOS_USO_AVANZADOS",
                    "LIMITACIONES_HONESTAS"
                ],
                "capabilities": [
                    "Explicación de capacidades del sistema",
                    "Tutoriales y guías de uso",
                    "Información sobre el creador (Angel)",
                    "Auto-consciencia y personalidad",
                    "Comparaciones con métodos tradicionales",
                    "Transparencia sobre limitaciones"
                ],
                "personality": [
                    "Conversacional y amigable",
                    "Persuasivo sobre ventajas de IA",
                    "Conoce a Angel como experto en IA",
                    "Honesto sobre limitaciones",
                    "Entusiasta del sistema"
                ]
            },

            "GeneralInterpreter": {
                "description": "Especialista en conversación general y temas no escolares",
                "database_access": False,
                "data_scope": "Conversación natural manteniendo identidad escolar sutil",
                "available_actions": [
                    "RESPUESTA_CASUAL",
                    "SALUDO_AMIGABLE",
                    "REDIRECCION_EDUCADA"
                ],
                "capabilities": [
                    "Conversación natural sobre cualquier tema",
                    "Saludos y despedidas amigables",
                    "Redirección educada hacia funciones del sistema",
                    "Mantiene identidad escolar sutilmente"
                ],
                "personality": [
                    "LLM versátil con identidad escolar sutil",
                    "Conversacional y naturalmente humano",
                    "Redirige educadamente a funciones escolares",
                    "Mantiene tono profesional pero casual"
                ]
            }
        }

    @staticmethod
    def generate_intentions_section() -> str:
        """
        📋 GENERAR SECCIÓN DE INTENCIONES PARA PROMPTS

        Genera dinámicamente la sección de intenciones que se inyecta
        en los prompts del Master para mantener consistencia.

        Returns:
            String formateado con todas las intenciones disponibles
        """
        intentions_catalog = SystemCatalog.get_available_intentions()
        sections = []

        for intention_key, intention_data in intentions_catalog.items():
            specialist = intention_data["specialist"]
            description = intention_data["description"]
            priority = intention_data.get("priority", 99)

            section = f"""
🎯 **{intention_key.upper()}** → {specialist} (Prioridad: {priority})
   ├── DESCRIPCIÓN: {description}
   ├── SUB-INTENCIONES DISPONIBLES:"""

            for sub_key, sub_data in intention_data["sub_intentions"].items():
                sub_desc = sub_data["description"]
                examples = ", ".join(sub_data["examples"][:3])  # Primeros 3 ejemplos
                capabilities = ", ".join(sub_data.get("capabilities", []))

                section += f"""
   │   ├── {sub_key}: {sub_desc}
   │   │   ├── Ejemplos: {examples}
   │   │   └── Capacidades: {capabilities}"""

            sections.append(section)

        return "\n".join(sections)

    @staticmethod
    def generate_mapping_examples() -> str:
        """
        🎯 GENERAR EJEMPLOS DE MAPEO PARA PROMPTS

        Genera dinámicamente los ejemplos de mapeo que ayudan al LLM
        a entender cómo mapear consultas a intenciones específicas.

        Returns:
            String con ejemplos de mapeo formateados
        """
        intentions_catalog = SystemCatalog.get_available_intentions()
        mappings = []

        for intention_key, intention_data in intentions_catalog.items():
            for sub_key, sub_data in intention_data["sub_intentions"].items():
                for example in sub_data["examples"][:2]:  # 2 ejemplos por sub-intención
                    mapping = f'- "{example}" → {intention_key}/{sub_key}'
                    mappings.append(mapping)

        return "\n".join(mappings)

    @staticmethod
    def get_intention_by_specialist(specialist_name: str) -> Dict:
        """
        🔍 OBTENER INTENCIONES POR ESPECIALISTA

        Filtra las intenciones que puede manejar un especialista específico.
        Útil para validación y delegación.

        Args:
            specialist_name: Nombre del especialista

        Returns:
            Dict con las intenciones que puede manejar el especialista
        """
        intentions_catalog = SystemCatalog.get_available_intentions()
        specialist_intentions = {}

        for intention_key, intention_data in intentions_catalog.items():
            if intention_data["specialist"] == specialist_name:
                specialist_intentions[intention_key] = intention_data

        return specialist_intentions

    @staticmethod
    def validate_intention_mapping(intention: str, sub_intention: str, specialist: str) -> bool:
        """
        ✅ VALIDAR MAPEO DE INTENCIÓN

        Verifica que una combinación de intención/sub-intención/especialista
        sea válida según el catálogo.

        Args:
            intention: Intención principal
            sub_intention: Sub-intención específica
            specialist: Especialista asignado

        Returns:
            True si el mapeo es válido, False en caso contrario
        """
        try:
            intentions_catalog = SystemCatalog.get_available_intentions()

            # Verificar que la intención existe
            if intention not in intentions_catalog:
                return False

            intention_data = intentions_catalog[intention]

            # Verificar que el especialista es correcto
            if intention_data["specialist"] != specialist:
                return False

            # Verificar que la sub-intención existe
            if sub_intention not in intention_data["sub_intentions"]:
                return False

            return True

        except Exception:
            return False

    @staticmethod
    def generate_examples_section() -> str:
        """
        🎯 GENERAR EJEMPLOS ESPECÍFICOS PARA DETECCIÓN PRECISA

        Genera ejemplos detallados que ayudan al LLM a detectar correctamente
        límites, filtros y entidades específicas.
        """
        return """
🎯 **EJEMPLOS ESPECÍFICOS PARA DETECCIÓN PRECISA:**

**LÍMITES NUMÉRICOS (CRÍTICO PARA FUNCIONALIDAD):**
- "Dame 3 alumnos de 3er grado" → limite_resultados: 3, filtros: ["grado: 3"]
- "Muestra 5 estudiantes" → limite_resultados: 5
- "Los primeros 2" → limite_resultados: 2
- "Solo 1 alumno" → limite_resultados: 1
- "Máximo 10" → limite_resultados: 10
- "El segundo de la lista" → limite_resultados: 1 (posición específica)

**FILTROS ESPECÍFICOS:**
- "alumnos de 2do A" → filtros: ["grado: 2", "grupo: A"]
- "estudiantes turno matutino" → filtros: ["turno: MATUTINO"]
- "niños de primer grado grupo B" → filtros: ["grado: 1", "grupo: B"]
- "3er grado vespertino" → filtros: ["grado: 3", "turno: VESPERTINO"]

**CONSTANCIAS (CRÍTICO - DETECCIÓN OBLIGATORIA):**
- "constancia para Juan Pérez" → generar_constancia, nombres: ["Juan Pérez"]
- "certificado de estudios" → generar_constancia, tipo_constancia: "estudios"
- "constancia con foto" → generar_constancia, incluir_foto: true
- "generale una constancia de calificaciones" → generar_constancia, tipo_constancia: "calificaciones"
- "genera constancia para ese alumno" → generar_constancia (con contexto)
- "crea una constancia de estudios" → generar_constancia, tipo_constancia: "estudios"
- "constancia de calificaciones a ese alumno" → generar_constancia, tipo_constancia: "calificaciones"
- "si porfavior generale a ese alumno una constancia de traslado" → generar_constancia, tipo_constancia: "traslado"
- "generale una constancia" → generar_constancia
- "genera una constancia" → generar_constancia
- "crea constancia" → generar_constancia
- "documento oficial" → generar_constancia
- "certificado" → generar_constancia

**RESOLUCIÓN DE CONTEXTO (CRÍTICO):**
- "a ese alumno" + contexto con 1 alumno → alumno_resuelto: {datos del contexto}
- "para él" + contexto con 1 alumno → alumno_resuelto: {datos del contexto}
- "para Franco" + contexto con Franco Alexander → alumno_resuelto: Franco Alexander
- "al estudiante" + contexto con 1 alumno → alumno_resuelto: {datos del contexto}

**ESTADÍSTICAS:**
- "cuántos alumnos hay" → estadisticas, sub_tipo: "conteo"
- "distribución por grados" → estadisticas, sub_tipo: "distribucion"
- "total de estudiantes" → estadisticas, sub_tipo: "conteo"

**PATRONES DE LÍMITES CRÍTICOS:**
- Números explícitos: 1, 2, 3, 4, 5, etc. → limite_resultados: [número]
- Ordinales: "primero" → limite_resultados: 1, "segundo" → limite_resultados: 1 (posición 2)
- Limitadores: "solo", "máximo", "hasta", "no más de" → limite_resultados: [número]

**MAPEO DE TÉRMINOS:**
- "primer grado", "1er grado", "primero" → grado: 1
- "segundo grado", "2do grado" → grado: 2
- "tercer grado", "3er grado" → grado: 3
- "matutino", "mañana" → turno: MATUTINO
- "vespertino", "tarde" → turno: VESPERTINO
"""

    @staticmethod
    def generate_context_rules() -> str:
        """
        🧠 GENERAR REGLAS PARA MANEJO INTELIGENTE DE CONTEXTO

        Reglas específicas para resolver referencias contextuales
        y manejar continuaciones de conversación.
        """
        return """
🧠 **REGLAS DE CONTEXTO CONVERSACIONAL:**

**RESOLUCIÓN DE REFERENCIAS:**
- "de esos" → filtrar lista del NIVEL 1 (más reciente)
- "el segundo" → elemento en posición 2 de lista anterior
- "para Juan" → buscar Juan en contexto o base de datos
- "también dame" → operación adicional sobre contexto

**PRIORIZACIÓN DE NIVELES:**
- NIVEL 1 = MÁS RECIENTE = MÁXIMA PRIORIDAD
- Usar niveles anteriores como contexto adicional
- Resolver referencias con información más reciente primero

**CASOS DE RESOLUCIÓN:**
- 1 elemento en contexto + referencia clara → RESOLVER directamente
- Múltiples elementos + referencia ambigua → PEDIR aclaración
- Sin contexto + referencia → BUSCAR en base de datos completa
"""

    @staticmethod
    def get_json_structure() -> dict:
        """
        📋 ESTRUCTURA JSON DINÁMICA COMPLETA

        Estructura completa para respuestas del Master con todos
        los campos necesarios para detección precisa.
        """
        return {
            "intention_type": "consulta_alumnos|ayuda_sistema|conversacion_general",
            "sub_intention": "busqueda_simple|estadisticas|generar_constancia|explicacion_general|tutorial_funciones|saludo|chat_casual",
            "confidence": 0.95,
            "reasoning": "Explicación detallada del proceso mental seguido paso a paso",
            "detected_entities": {
                # 🎯 ENTIDADES ESPECÍFICAS POR SUB-INTENCIÓN:

                # Para busqueda_simple:
                "nombres": ["Juan Pérez", "María García"],  # Solo si busca alumnos específicos
                "filtros": ["grado: 2", "grupo: A"],       # Solo si busca por criterios
                "limite_resultados": 3,                    # Solo si especifica límite

                # Para generar_constancia:
                "alumno_resuelto": None,                   # Solo para constancias con contexto
                "tipo_constancia": "estudios",             # Solo para constancias
                "incluir_foto": False,                     # Solo para constancias

                # Para estadisticas:
                "accion_principal": "contar",              # Solo para estadísticas

                # 🚫 ELIMINADOS (Student los deduce por sub-intención):
                # "campo_solicitado": None,               # ❌ Student lo deduce
                # "fuente_datos": "base_datos",           # ❌ Siempre es BD
                # "contexto_especifico": None             # ❌ Redundante
            },
            "student_categorization": {
                "categoria": "busqueda",
                "sub_tipo": "simple",
                "requiere_contexto": False,
                "flujo_optimo": "sql_directo"
            }
        }

    @staticmethod
    def get_json_instructions_with_examples() -> str:
        """
        📋 INSTRUCCIONES JSON CON EJEMPLOS ESPECÍFICOS

        Genera instrucciones JSON con ejemplos concretos para
        guiar al LLM en la detección correcta de entidades.
        """
        return """
📋 **FORMATO DE RESPUESTA OBLIGATORIO:**

Responde ÚNICAMENTE con un JSON válido siguiendo estos EJEMPLOS ESPECÍFICOS:

**EJEMPLO 1: "Dame 3 alumnos de segundo grado"**
```json
{{
  "intention_type": "consulta_alumnos",
  "sub_intention": "busqueda_simple",
  "confidence": 0.95,
  "reasoning": "Usuario solicita búsqueda por criterios: 3 alumnos de grado 2",
  "detected_entities": {{
    "filtros": ["grado: 2"],
    "limite_resultados": 3
  }},
  "student_categorization": {{
    "categoria": "busqueda",
    "sub_tipo": "simple",
    "requiere_contexto": false,
    "flujo_optimo": "sql_directo"
  }}
}}
```

**EJEMPLO 2: "Cuántos alumnos hay en total"**
```json
{{
  "intention_type": "consulta_alumnos",
  "sub_intention": "estadisticas",
  "confidence": 0.95,
  "reasoning": "Usuario solicita conteo total de alumnos",
  "detected_entities": {{
    "accion_principal": "contar"
  }},
  "student_categorization": {{
    "categoria": "estadistica",
    "sub_tipo": "conteo",
    "requiere_contexto": false,
    "flujo_optimo": "sql_directo"
  }}
}}
```

**EJEMPLO 3: "Información completa de Juan Pérez"**
```json
{{
  "intention_type": "consulta_alumnos",
  "sub_intention": "busqueda_simple",
  "confidence": 0.95,
  "reasoning": "Usuario solicita información de alumno específico",
  "detected_entities": {{
    "nombres": ["Juan Pérez"]
  }},
  "student_categorization": {{
    "categoria": "busqueda",
    "sub_tipo": "simple",
    "requiere_contexto": false,
    "flujo_optimo": "sql_directo"
  }}
}}
```

**EJEMPLO 4: "Genera constancia para ese alumno"**
```json
{{
  "intention_type": "consulta_alumnos",
  "sub_intention": "generar_constancia",
  "confidence": 0.95,
  "reasoning": "Usuario solicita constancia para alumno del contexto",
  "detected_entities": {{
    "alumno_resuelto": {{"id": 1, "nombre": "Franco Alexander"}},
    "tipo_constancia": "estudios"
  }},
  "student_categorization": {{
    "categoria": "constancia",
    "sub_tipo": "individual",
    "requiere_contexto": true,
    "flujo_optimo": "alumno_resuelto"
  }}
}}
```

⚠️ **REGLAS CRÍTICAS:**
- DETECTAR LÍMITES: "dame 3" → limite_resultados: 3
- DETECTAR FILTROS: "segundo grado" → filtros: ["grado: 2"]
- USAR COMILLAS DOBLES (") para strings
- NO agregar explicaciones fuera del JSON
"""

    @staticmethod
    def get_available_actions_for_intention(intention: str, sub_intention: str) -> List[str]:
        """
        🚨 MÉTODO OBSOLETO - MASTER NO DEBE CONOCER ACCIONES

        Este método ya no se usa porque Master no debe conocer acciones específicas.
        Las acciones son responsabilidad de cada especialista (Student/Help).

        Returns:
            Lista vacía - Master solo maneja intenciones y delegación
        """
        # ❌ ELIMINADO: Master no debe conocer acciones específicas
        # Cada especialista maneja sus propias acciones independientemente
        return []
