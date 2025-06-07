# 🎯 GUÍA: CENTRALIZACIÓN Y GESTIÓN DE PROMPTS

## 📋 **ÍNDICE**
1. [Arquitectura de Prompts](#arquitectura-prompts)
2. [Modificar Respuestas Fácilmente](#modificar-respuestas)
3. [Agregar Nuevos Prompts](#nuevos-prompts)
4. [Personalidad Global](#personalidad-global)
5. [Casos Prácticos](#casos-practicos)

---

## 🏗️ **ARQUITECTURA DE PROMPTS** {#arquitectura-prompts}

### **ESTRUCTURA CENTRALIZADA:**
```
app/core/ai/prompts/
├── base_prompt_manager.py           # 🧠 PERSONALIDAD GLOBAL
├── master_prompt_manager.py         # 🎯 PROMPTS DEL MASTER
├── student_query_prompt_manager.py  # 🎓 PROMPTS DEL STUDENT
├── help_prompt_manager.py           # 🆘 PROMPTS DEL HELP
└── __init__.py                      # 📦 IMPORTS CENTRALIZADOS
```

### **JERARQUÍA DE HERENCIA:**
```python
BasePromptManager (Personalidad Global)
    ├── MasterPromptManager (Análisis y delegación)
    ├── StudentQueryPromptManager (Consultas técnicas)
    ├── HelpPromptManager (Ayuda y soporte)
    └── [Futuros] GeneralPromptManager, TeacherPromptManager...
```

### **FLUJO DE PROMPTS:**
```
Usuario → Master (MasterPromptManager) → Specialist (SpecificPromptManager) → Respuesta
```

---

## 🔧 **MODIFICAR RESPUESTAS FÁCILMENTE** {#modificar-respuestas}

### **1. CAMBIAR PERSONALIDAD GLOBAL**
**Archivo**: `app/core/ai/prompts/base_prompt_manager.py`

```python
def get_unified_prompt_header(self, role_context: str = "") -> str:
    """🎯 MODIFICAR AQUÍ AFECTA TODO EL SISTEMA"""
    return f"""
Eres el Asistente de IA Escolar de {self.get_school_name()}.

🎭 PERSONALIDAD (MODIFICAR AQUÍ):
- Tono: Amigable pero profesional
- Estilo: Claro y directo
- Emojis: Usar moderadamente
- Enfoque: Orientado a resultados

🏫 CONTEXTO ESCOLAR:
- Escuela: {self.get_school_name()}
- Alumnos: 211 estudiantes activos
- Función: Asistente integral de gestión escolar

{role_context}
"""

def get_communication_patterns(self) -> Dict[str, str]:
    """🗣️ PATRONES DE COMUNICACIÓN GLOBALES"""
    return {
        "saludo": "¡Hola! 👋",
        "despedida": "¡Hasta luego! 👋",
        "confirmacion": "¡Perfecto! ✅",
        "error": "Lo siento, hubo un problema ❌",
        "exito": "¡Excelente! 🎉",
        "procesando": "Un momento, procesando... ⏳"
    }
```

### **2. CAMBIAR RESPUESTAS DEL HELPINTERPRETER**
**Archivo**: `app/core/ai/interpretation/help_interpreter.py`

```python
# 🎯 CENTRALIZAR TODAS LAS RESPUESTAS AQUÍ
RESPUESTAS_HELP = {
    "SOBRE_CREADOR": """
¡Hola! 👋 ¡Qué buena pregunta! Te cuento, ¡me creó Angel! 👨‍💻 

🚀 **Angel es un desarrollador experto** que diseñó este sistema completo para revolucionar la gestión escolar. 

💡 **Su visión**: Crear un asistente de IA que realmente entienda las necesidades de las escuelas y haga todo más fácil y eficiente.

🎯 **Mi propósito**: Ser tu compañero inteligente para gestionar información de alumnos, generar constancias y hacer análisis que antes tomaban horas.

¿Te gustaría saber más sobre mis capacidades o sobre cómo Angel me programó? 🤖✨
""",

    "AUTO_CONSCIENCIA": """
¡Hola! 👋 ¡Soy tu Asistente de IA Escolar 🤖 de la escuela {school_name}!

🧠 **¿Qué soy exactamente?**
- Soy una IA especializada en gestión escolar
- Tengo acceso a toda la información de los 211 alumnos
- Puedo generar constancias, hacer búsquedas y análisis estadísticos

💪 **Mi especialidad:**
- Entiendo lenguaje natural (hablas normal, yo entiendo)
- Proceso información instantáneamente
- Genero documentos oficiales en segundos
- Mantengo conversaciones contextuales

🎯 **Mi misión**: Hacer tu trabajo más fácil y eficiente. ¡Soy como tener un asistente súper inteligente 24/7!

¿Qué te gustaría que haga por ti? 😊
""",

    "LIMITACIONES_HONESTAS": """
¡Hola! 👋 Soy honesto contigo, estas son mis limitaciones actuales:

⚠️ **LO QUE NO PUEDO HACER:**
1. 📊 **Datos externos**: Solo accedo a información de esta escuela
2. 🔄 **Tiempo real**: No me actualizo automáticamente con cambios externos
3. 🌐 **Internet**: No puedo buscar información en línea
4. 📝 **Edición directa**: No modifico la base de datos (solo consulto)
5. 🖼️ **Imágenes**: No proceso fotos ni documentos escaneados

✅ **PERO SOY MUY BUENO EN:**
- 🔍 Búsquedas instantáneas de alumnos
- 📊 Análisis estadísticos complejos
- 📄 Generación de constancias oficiales
- 🧠 Entender consultas en lenguaje natural
- 💬 Mantener conversaciones contextuales

🎯 **Mi filosofía**: Prefiero ser honesto sobre mis límites y excelente en lo que sí hago. ¡Así sabes exactamente qué esperar de mí!

¿En qué puedo ayudarte dentro de mis capacidades? 💪
"""
}

# 🔧 USAR LAS RESPUESTAS CENTRALIZADAS
def _execute_help_action(self, action: str, user_query: str, entities: dict) -> dict:
    """Ejecuta acciones de ayuda con respuestas centralizadas"""
    
    if action == "SOBRE_CREADOR":
        return {
            "action": "SOBRE_CREADOR",
            "response": RESPUESTAS_HELP["SOBRE_CREADOR"],
            "success": True
        }
    
    elif action == "AUTO_CONSCIENCIA":
        school_name = self._get_school_name()
        response = RESPUESTAS_HELP["AUTO_CONSCIENCIA"].format(school_name=school_name)
        return {
            "action": "AUTO_CONSCIENCIA", 
            "response": response,
            "success": True
        }
    
    elif action == "LIMITACIONES":
        return {
            "action": "LIMITACIONES_HONESTAS",
            "response": RESPUESTAS_HELP["LIMITACIONES_HONESTAS"],
            "success": True
        }
```

### **3. CAMBIAR MAPEOS DE ACCIONES DEL STUDENT**
**Archivo**: `app/core/ai/prompts/student_query_prompt_manager.py`

```python
# 🎯 CENTRALIZAR TODOS LOS MAPEOS AQUÍ (línea ~919)
MAPEOS_ACCIONES = {
    "estadisticas": {
        "patterns": [
            "cuántos alumnos hay en la escuela",
            "total de estudiantes", 
            "distribución por grados",
            "estadísticas generales"
        ],
        "action": "CALCULAR_ESTADISTICA",
        "tipo": "conteo"
    },
    
    "busquedas": {
        "patterns": [
            "buscar alumno",
            "encontrar estudiante",
            "información de",
            "datos de"
        ],
        "action": "BUSCAR_UNIVERSAL",
        "tipo": "busqueda"
    },
    
    "constancias": {
        "patterns": [
            "generar constancia",
            "crear certificado",
            "constancia de estudios",
            "constancia de traslado"
        ],
        "action": "GENERAR_CONSTANCIA_COMPLETA",
        "tipo": "generacion"
    }
}

# 🔧 MODIFICAR FÁCILMENTE LOS EJEMPLOS
EJEMPLOS_MAPEO = """
SIMPLE - ESTADÍSTICAS Y CONTEOS (APLICANDO MAPEO INTELIGENTE):
- "cuántos alumnos hay por grado" → CALCULAR_ESTADISTICA (tipo: conteo, agrupar_por: grado)
- "distribución por turno" → CALCULAR_ESTADISTICA (tipo: distribucion, agrupar_por: turno)
- "total de estudiantes" → CALCULAR_ESTADISTICA (tipo: conteo)
- "cuántos alumnos hay en la escuela" → CALCULAR_ESTADISTICA (tipo: conteo)

SIMPLE - BÚSQUEDAS (APLICANDO MAPEO INTELIGENTE):
- "buscar García" → BUSCAR_UNIVERSAL (criterio_principal: nombre LIKE '%García%')
- "alumnos de 3er grado" → BUSCAR_UNIVERSAL (criterio_principal: grado = '3')
- "estudiantes del turno matutino" → BUSCAR_UNIVERSAL (criterio_principal: turno = 'MATUTINO')

SIMPLE - CONSTANCIAS (APLICANDO MAPEO INTELIGENTE):
- "constancia para Juan" → GENERAR_CONSTANCIA_COMPLETA (buscar alumno: Juan)
- "certificado de estudios" → GENERAR_CONSTANCIA_COMPLETA (tipo: estudio)
"""
```

---

## 🆕 **AGREGAR NUEVOS PROMPTS** {#nuevos-prompts}

### **CREAR NUEVO PROMPTMANAGER**
**Archivo**: `app/core/ai/prompts/general_prompt_manager.py`

```python
from app.core.ai.prompts.base_prompt_manager import BasePromptManager

class GeneralPromptManager(BasePromptManager):
    """Manager para conversación general y consultas no específicas"""
    
    def get_conversation_prompt(self, user_query: str, context: str = "") -> str:
        """Prompt para conversación general"""
        unified_header = self.get_unified_prompt_header("asistente conversacional")
        
        return f"""
{unified_header}

🎯 **CONTEXTO**: Conversación general con el usuario
📝 **CONSULTA**: {user_query}

🗣️ **INSTRUCCIONES**:
- Mantén una conversación natural y amigable
- Si la consulta es sobre la escuela, proporciona información general
- Si no sabes algo específico, sugiere consultas más específicas
- Usa el tono establecido en la personalidad global

{context}

RESPONDE de manera conversacional y útil.
"""
    
    def get_clarification_prompt(self, user_query: str, ambiguous_terms: list) -> str:
        """Prompt para aclarar consultas ambiguas"""
        unified_header = self.get_unified_prompt_header("asistente de aclaración")
        
        return f"""
{unified_header}

🤔 **SITUACIÓN**: El usuario hizo una consulta ambigua
📝 **CONSULTA ORIGINAL**: {user_query}
⚠️ **TÉRMINOS AMBIGUOS**: {', '.join(ambiguous_terms)}

🎯 **TU TAREA**: 
- Pedir aclaración de manera amigable
- Sugerir opciones específicas
- Mantener el contexto de la conversación

EJEMPLO:
"Entiendo que buscas información sobre [término], pero podrías ser más específico? 
Por ejemplo:
- ¿Te refieres a [opción 1]?
- ¿O buscas [opción 2]?"

RESPONDE pidiendo aclaración de manera útil.
"""
```

### **REGISTRAR EN EL SISTEMA**
**Archivo**: `app/core/ai/prompts/__init__.py`

```python
from .general_prompt_manager import GeneralPromptManager

__all__ = [
    'StudentQueryPromptManager',
    'MasterPromptManager',
    'HelpPromptManager',
    'GeneralPromptManager'  # 🆕 NUEVO
]
```

---

## 🎭 **PERSONALIDAD GLOBAL** {#personalidad-global}

### **CONFIGURACIÓN CENTRALIZADA**
**Archivo**: `app/core/ai/prompts/base_prompt_manager.py`

```python
class BasePromptManager:
    """🧠 CEREBRO DE LA PERSONALIDAD GLOBAL"""
    
    def get_personality_config(self) -> Dict[str, Any]:
        """🎭 CONFIGURACIÓN COMPLETA DE PERSONALIDAD"""
        return {
            "tono": {
                "principal": "amigable_profesional",
                "nivel_formalidad": "medio",
                "uso_emojis": "moderado",
                "estilo_respuesta": "claro_directo"
            },
            
            "comunicacion": {
                "saludo": "¡Hola! 👋",
                "despedida": "¡Hasta luego! 👋", 
                "confirmacion": "¡Perfecto! ✅",
                "procesando": "Un momento... ⏳",
                "exito": "¡Excelente! 🎉",
                "error": "Lo siento ❌",
                "ayuda": "¿En qué puedo ayudarte? 🤔"
            },
            
            "comportamiento": {
                "proactivo": True,
                "sugiere_alternativas": True,
                "explica_procesos": False,  # No mostrar detalles técnicos
                "mantiene_contexto": True,
                "personaliza_respuestas": True
            }
        }
    
    def apply_personality_to_prompt(self, base_prompt: str, context: str = "") -> str:
        """🎨 APLICAR PERSONALIDAD A CUALQUIER PROMPT"""
        personality = self.get_personality_config()
        
        # Agregar elementos de personalidad
        if personality["comportamiento"]["proactivo"]:
            base_prompt += "\n\n🎯 Sé proactivo y sugiere acciones útiles."
        
        if personality["comportamiento"]["sugiere_alternativas"]:
            base_prompt += "\n💡 Si no puedes hacer algo, sugiere alternativas."
            
        return base_prompt
```

---

## 🎯 **CASOS PRÁCTICOS** {#casos-practicos}

### **CASO 1: Cambiar Tono a Más Formal**

```python
# En base_prompt_manager.py
def get_unified_prompt_header(self, role_context: str = "") -> str:
    return f"""
Usted está interactuando con el Sistema de Gestión Escolar de {self.get_school_name()}.

PROTOCOLO DE COMUNICACIÓN:
- Trato formal y respetuoso
- Respuestas precisas y concisas  
- Terminología técnica apropiada
- Sin uso de emojis

{role_context}
"""
```

### **CASO 2: Agregar Nuevas Respuestas de Ayuda**

```python
# En help_interpreter.py, agregar a RESPUESTAS_HELP:
"TUTORIAL_BUSQUEDA": """
📚 **TUTORIAL: Cómo buscar alumnos**

🔍 **MÉTODOS DE BÚSQUEDA:**
1. **Por nombre**: "buscar García" o "información de María"
2. **Por grado**: "alumnos de 3er grado" 
3. **Por grupo**: "estudiantes de 3° A"
4. **Por CURP**: "RARR150330HDGSRRA6"

💡 **CONSEJOS:**
- Puedes combinar criterios: "García de 3° A"
- No necesitas escribir completo: "Gar" encuentra "García"
- Funciona con apellidos o nombres

¿Quieres que busque algún alumno específico? 🎯
""",

"VENTAJAS_IA": """
🚀 **¿Por qué usar IA en lugar de Excel?**

⚡ **VELOCIDAD:**
- Excel: Buscar manualmente entre 211 registros
- IA: Respuesta instantánea con lenguaje natural

🧠 **INTELIGENCIA:**
- Excel: Búsquedas exactas solamente
- IA: Entiende "García de tercero" = "apellido García AND grado 3"

📊 **ANÁLISIS:**
- Excel: Crear fórmulas complejas
- IA: "distribución por grados" → análisis automático

📄 **DOCUMENTOS:**
- Excel: Copiar/pegar a Word, formatear manualmente
- IA: Constancia oficial lista en segundos

💬 **COMUNICACIÓN:**
- Excel: Interfaz técnica
- IA: Conversación natural como con un asistente humano

¡Es como tener un experto en Excel que nunca se cansa! 🤖✨
"""
```

### **CASO 3: Personalizar Mapeos por Escuela**

```python
# En student_query_prompt_manager.py
def get_school_specific_mappings(self) -> Dict[str, str]:
    """🏫 MAPEOS ESPECÍFICOS POR ESCUELA"""
    school_name = self.get_school_name()
    
    if "MAXIMO GAMIZ" in school_name:
        return {
            "nivel_educativo": "primaria",
            "grados_disponibles": ["1", "2", "3", "4", "5", "6"],
            "turnos": ["MATUTINO", "VESPERTINO"],
            "terminologia": {
                "estudiante": "alumno",
                "calificacion": "nota",
                "grupo": "sección"
            }
        }
    
    # Configuración por defecto
    return {
        "nivel_educativo": "general",
        "terminologia": {
            "estudiante": "estudiante",
            "calificacion": "calificación"
        }
    }
```

---

## ✅ **CHECKLIST DE MODIFICACIONES**

### **Cambiar Personalidad:**
- [ ] Modificar `base_prompt_manager.py`
- [ ] Actualizar `get_unified_prompt_header()`
- [ ] Probar en diferentes intérpretes
- [ ] Verificar consistencia global

### **Agregar Respuestas:**
- [ ] Identificar el intérprete correcto
- [ ] Agregar a diccionario centralizado
- [ ] Actualizar lógica de ejecución
- [ ] Probar nueva respuesta

### **Nuevo PromptManager:**
- [ ] Crear clase heredando BasePromptManager
- [ ] Implementar métodos específicos
- [ ] Registrar en `__init__.py`
- [ ] Integrar con intérprete correspondiente

---

**🎯 RESULTADO**: Sistema de prompts completamente centralizado y fácil de modificar.
