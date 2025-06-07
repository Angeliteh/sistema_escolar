# 🚀 GUÍA COMPLETA: IMPLEMENTACIÓN MASTER-STUDENT

## 📋 **ÍNDICE**
1. [Arquitectura del Sistema](#arquitectura)
2. [Implementar Nueva Intención](#nueva-intencion)
3. [Implementar Nueva Sub-intención](#nueva-sub-intencion)
4. [Implementar Nuevo Intérprete](#nuevo-interprete)
5. [Centralización de Prompts](#centralizacion-prompts)
6. [Casos de Uso Prácticos](#casos-uso)

---

## 🏗️ **ARQUITECTURA DEL SISTEMA** {#arquitectura}

### **FLUJO PRINCIPAL:**
```
Usuario → Master → Specialist → ActionExecutor → Master (Vocero)
```

### **COMPONENTES CLAVE:**
- **MasterInterpreter**: Intérprete humano universal - Análisis semántico completo
- **StudentQueryInterpreter**: Ejecutor técnico especializado en datos de alumnos
- **HelpInterpreter**: Especialista en ayuda del sistema
- **ActionExecutor**: Ejecuta acciones técnicas
- **PromptManagers**: Centralizan todos los prompts

### **PROCESO MENTAL DEL MASTER (OBLIGATORIO):**
```
PASO 1: Análisis semántico puro (¿qué quiere realmente?)
PASO 2: Verificación de información suficiente
PASO 3: Análisis de contexto conversacional
PASO 4: Verificación de capacidades de interpreters
PASO 5: Preparación de instrucción clara
PASO 6: Delegación con contexto completo
```

**📖 DOCUMENTACIÓN COMPLETA:** Ver `PROCESO_MENTAL_MASTER_COMPLETO.md`

---

## 🎯 **IMPLEMENTAR NUEVA INTENCIÓN** {#nueva-intencion}

### **PASO 1: Definir la Intención**
```python
# Ejemplo: "gestion_profesores"
NUEVA_INTENCION = {
    "nombre": "gestion_profesores",
    "descripcion": "TODO sobre profesores - búsquedas, horarios, asignaciones",
    "especialista": "TeacherQueryInterpreter",  # Nuevo intérprete
    "sub_intenciones": [
        "busqueda_profesor",
        "horarios_profesor", 
        "asignaciones_materia"
    ]
}
```

### **PASO 2: Actualizar MasterKnowledge**
**Archivo**: `app/core/ai/interpretation/master_knowledge.py`

```python
# Agregar en self.interpreters_map (línea ~32)
"TeacherQueryInterpreter": {
    "domain": "Gestión de profesores y horarios",
    "intentions": {
        "gestion_profesores": {
            "description": "TODO sobre profesores",
            "sub_intentions": {
                "busqueda_profesor": {
                    "description": "Buscar profesores por nombre, materia, etc.",
                    "examples": ["buscar profesor García", "maestros de matemáticas"]
                },
                "horarios_profesor": {
                    "description": "Consultar horarios y disponibilidad",
                    "examples": ["horario del profesor López", "disponibilidad martes"]
                }
            }
        }
    }
}
```

### **PASO 3: Actualizar MasterInterpreter**
**Archivo**: `app/core/ai/interpretation/master_interpreter.py`

```python
# Agregar en self.system_map
"TeacherQueryInterpreter": {
    "handles": ["gestion_profesores"],
    "sub_intentions": ["busqueda_profesor", "horarios_profesor", "asignaciones_materia"],
    "capabilities": "Consultas de profesores, horarios, asignaciones",
    "description": "Especialista en gestión de profesores"
}
```

### **PASO 4: Actualizar MasterPromptManager**
**Archivo**: `app/core/ai/prompts/master_prompt_manager.py`

```python
# Agregar en el prompt principal (línea ~172)
4. **gestion_profesores**: TODO sobre profesores (búsquedas, horarios, asignaciones)
   - Sub-intenciones:
     * **busqueda_profesor**: Buscar profesores por criterios
     * **horarios_profesor**: Consultar horarios y disponibilidad
     * **asignaciones_materia**: Materias asignadas a profesores

# Agregar en sub_intention (línea ~378)
"sub_intention": "busqueda_simple|...|busqueda_profesor|horarios_profesor|asignaciones_materia",
```

---

## 🎯 **IMPLEMENTAR NUEVA SUB-INTENCIÓN** {#nueva-sub-intencion}

### **EJEMPLO: Agregar "calificaciones_alumno" a consulta_alumnos**

### **PASO 1: Actualizar MasterKnowledge**
```python
# En self.interpreters_map["StudentQueryInterpreter"]["intentions"]["consulta_alumnos"]["sub_intentions"]
"calificaciones_alumno": {
    "description": "Consultar calificaciones específicas de un alumno",
    "capabilities": ["calificaciones", "notas", "boletas"],
    "examples": ["calificaciones de Juan", "notas de María García", "boleta de Pedro"]
}
```

### **PASO 2: Actualizar MasterPromptManager**
```python
# Agregar en sub-intenciones de consulta_alumnos
* **calificaciones_alumno**: Consultar calificaciones específicas

# Agregar en sub_intention
"sub_intention": "busqueda_simple|...|calificaciones_alumno",
```

### **PASO 3: Actualizar StudentQueryInterpreter**
**Archivo**: `app/core/ai/interpretation/student_query_interpreter.py`

```python
# En el método de procesamiento, agregar lógica para la nueva sub-intención
if sub_intention == "calificaciones_alumno":
    # Lógica específica para calificaciones
    action_request = self._create_calificaciones_request(user_query, entities)
```

### **PASO 4: Actualizar StudentPromptManager**
**Archivo**: `app/core/ai/prompts/student_query_prompt_manager.py`

```python
# Agregar ejemplos de mapeo
- "calificaciones de Juan" → BUSCAR_UNIVERSAL (criterio: nombre=Juan, campos: calificaciones)
- "notas del alumno" → BUSCAR_UNIVERSAL (incluir: calificaciones)
```

---

## 🎯 **IMPLEMENTAR NUEVO INTÉRPRETE** {#nuevo-interprete}

### **EJEMPLO: TeacherQueryInterpreter**

### **PASO 1: Crear el Intérprete**
**Archivo**: `app/core/ai/interpretation/teacher_query_interpreter.py`

```python
from app.core.ai.interpretation.base_interpreter import BaseInterpreter
from app.core.logging import get_logger

class TeacherQueryInterpreter(BaseInterpreter):
    """Especialista en gestión de profesores"""
    
    def __init__(self, db_path: str, gemini_client=None):
        super().__init__("TeacherQueryInterpreter", priority=8)
        self.logger = get_logger(__name__)
        self.db_path = db_path
        self.gemini_client = gemini_client
        
        # Importar ActionExecutor para profesores
        from app.core.actions.teacher_action_executor import TeacherActionExecutor
        self.action_executor = TeacherActionExecutor(db_path)
    
    def can_handle(self, context) -> bool:
        """Determina si puede manejar la consulta"""
        return context.user_message and "profesor" in context.user_message.lower()
    
    def interpret(self, context) -> InterpretationResult:
        """Procesa consultas de profesores"""
        try:
            # Lógica similar a StudentQueryInterpreter
            # pero adaptada para profesores
            pass
        except Exception as e:
            self.logger.error(f"Error en TeacherQueryInterpreter: {e}")
            return None
```

### **PASO 2: Crear PromptManager Específico**
**Archivo**: `app/core/ai/prompts/teacher_prompt_manager.py`

```python
from app.core.ai.prompts.base_prompt_manager import BasePromptManager

class TeacherPromptManager(BasePromptManager):
    """Manager de prompts para gestión de profesores"""
    
    def get_teacher_search_prompt(self, user_query: str) -> str:
        """Prompt para búsqueda de profesores"""
        unified_header = self.get_unified_prompt_header("especialista en profesores")
        
        return f"""
{unified_header}

CONTEXTO: Sistema de gestión de profesores
CONSULTA: {user_query}

ACCIONES DISPONIBLES:
- BUSCAR_PROFESOR: Buscar por nombre, materia, departamento
- CONSULTAR_HORARIO: Ver horarios y disponibilidad
- LISTAR_MATERIAS: Materias asignadas

RESPONDE con la acción más apropiada.
"""
```

### **PASO 3: Crear ActionExecutor Específico**
**Archivo**: `app/core/actions/teacher_action_executor.py`

```python
class TeacherActionExecutor:
    """Ejecutor de acciones para profesores"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def execute(self, action_request: dict):
        """Ejecuta acciones específicas de profesores"""
        action = action_request.get('action')
        
        if action == "BUSCAR_PROFESOR":
            return self._buscar_profesor(action_request)
        elif action == "CONSULTAR_HORARIO":
            return self._consultar_horario(action_request)
        # ... más acciones
    
    def _buscar_profesor(self, request):
        """Implementa búsqueda de profesores"""
        # Lógica SQL específica para profesores
        pass
```

### **PASO 4: Registrar en el Sistema**
**Archivo**: `app/core/ai/interpretation/master_interpreter.py`

```python
# En __init__
from app.core.ai.interpretation.teacher_query_interpreter import TeacherQueryInterpreter

# Agregar a specialists
self.specialists["TeacherQueryInterpreter"] = TeacherQueryInterpreter(
    db_path=self.db_path, 
    gemini_client=self.gemini_client
)
```

---

## 🎯 **CENTRALIZACIÓN DE PROMPTS** {#centralizacion-prompts}

### **ESTRUCTURA ACTUAL:**
```
app/core/ai/prompts/
├── base_prompt_manager.py      # Identidad unificada
├── master_prompt_manager.py    # Prompts del Master
├── student_query_prompt_manager.py  # Prompts del Student
├── help_prompt_manager.py      # Prompts del Help
└── __init__.py                 # Imports centralizados
```

### **MODIFICAR RESPUESTAS FÁCILMENTE:**

#### **1. Cambiar Personalidad Global**
**Archivo**: `app/core/ai/prompts/base_prompt_manager.py`

```python
def get_unified_prompt_header(self, role_context: str = "") -> str:
    """PERSONALIDAD GLOBAL - Modificar aquí afecta TODO el sistema"""
    return f"""
Eres el Asistente de IA Escolar de {self.get_school_name()}.

PERSONALIDAD ACTUALIZADA:
- Más formal y profesional
- Respuestas más concisas
- Enfoque en eficiencia

{role_context}
"""
```

#### **2. Cambiar Respuestas del HelpInterpreter**
**Archivo**: `app/core/ai/interpretation/help_interpreter.py`

```python
# Buscar las respuestas hardcodeadas y centralizarlas
RESPUESTAS_HELP = {
    "SOBRE_CREADOR": """
¡Hola! 👋 Me creó Angel, un desarrollador experto...
[MODIFICAR AQUÍ LA RESPUESTA]
""",
    "AUTO_CONSCIENCIA": """
Soy tu Asistente de IA Escolar...
[MODIFICAR AQUÍ LA RESPUESTA]
""",
    "LIMITACIONES_HONESTAS": """
Te soy honesto, estas son mis limitaciones...
[MODIFICAR AQUÍ LA RESPUESTA]
"""
}
```

#### **3. Centralizar Mapeos de Acciones**
**Archivo**: `app/core/ai/prompts/student_query_prompt_manager.py`

```python
# Todas las reglas de mapeo están centralizadas aquí
MAPEO_ACCIONES = {
    "estadisticas": {
        "cuantos_alumnos": "CALCULAR_ESTADISTICA",
        "distribucion": "CALCULAR_ESTADISTICA", 
        "total_estudiantes": "CALCULAR_ESTADISTICA"
    },
    "busquedas": {
        "buscar_alumno": "BUSCAR_UNIVERSAL",
        "encontrar_estudiante": "BUSCAR_UNIVERSAL"
    }
}
```

---

## 🎯 **CASOS DE USO PRÁCTICOS** {#casos-uso}

### **CASO 1: Implementar GeneralInterpreter**

```python
# 1. Crear el intérprete
class GeneralInterpreter(BaseInterpreter):
    """Maneja conversación general y consultas no específicas"""
    
    def can_handle(self, context) -> bool:
        # Lógica para detectar conversación general
        return not any(keyword in context.user_message.lower() 
                      for keyword in ["alumno", "constancia", "ayuda"])

# 2. Agregar al Master
"GeneralInterpreter": {
    "handles": ["conversacion_general"],
    "sub_intentions": ["saludo", "despedida", "charla_casual"],
    "capabilities": "Conversación natural y consultas generales"
}

# 3. Crear prompts específicos
class GeneralPromptManager(BasePromptManager):
    def get_conversation_prompt(self, user_query: str) -> str:
        return f"""
{self.get_unified_prompt_header("asistente conversacional")}

Mantén una conversación natural sobre: {user_query}
"""
```

### **CASO 2: Modificar Respuesta de Limitaciones**

```python
# En help_interpreter.py, cambiar:
if action == "LIMITACIONES":
    return {
        "action": "LIMITACIONES_HONESTAS",
        "response": """
🤖 Mis limitaciones actualizadas:

1. 📊 **Datos**: Solo accedo a la información de esta escuela
2. 🔄 **Tiempo real**: No me actualizo automáticamente
3. 🌐 **Internet**: No puedo buscar información externa
4. 📝 **Edición**: No puedo modificar datos directamente

¡Pero soy muy bueno en lo que hago! 💪
""",
        "success": True
    }
```

---

## ✅ **CHECKLIST DE IMPLEMENTACIÓN**

### **Nueva Intención:**
- [ ] Actualizar MasterKnowledge
- [ ] Actualizar MasterInterpreter.system_map
- [ ] Actualizar MasterPromptManager
- [ ] Crear/Actualizar Intérprete específico
- [ ] Probar con consultas reales

### **Nueva Sub-intención:**
- [ ] Actualizar MasterKnowledge.sub_intentions
- [ ] Actualizar MasterPromptManager.sub_intention
- [ ] Actualizar lógica del Intérprete
- [ ] Actualizar PromptManager específico
- [ ] Probar mapeo correcto

### **Nuevo Intérprete:**
- [ ] Crear clase heredando BaseInterpreter
- [ ] Implementar can_handle() e interpret()
- [ ] Crear PromptManager específico
- [ ] Crear ActionExecutor específico
- [ ] Registrar en MasterInterpreter
- [ ] Actualizar MasterKnowledge
- [ ] Probar integración completa

---

## 🔄 **PROTOCOLO ESTANDARIZADO DE COMUNICACIÓN**

### **IMPLEMENTACIÓN CON PROTOCOLO GARANTIZADO**

Todas las nuevas funcionalidades DEBEN seguir el **protocolo estandarizado** definido en [PROTOCOLO_COMUNICACION_ESTANDARIZADO.md](PROTOCOLO_COMUNICACION_ESTANDARIZADO.md).

#### **CHECKLIST DE PROTOCOLO PARA NUEVAS FUNCIONALIDADES:**

```python
# ✅ MASTER: Detectar entidades completas
detected_entities = {
    "limite_resultados": limite_detectado,
    "filtros": filtros_identificados,
    "nombres": nombres_encontrados,
    "accion_principal": accion_determinada,
    # ... TODAS las entidades necesarias
}

# ✅ MASTER: Transferir entidades completas
context.intention_info = {
    'detected_entities': detected_entities,  # ✅ COMPLETAS
    'intention_type': intention_type,
    'sub_intention': sub_intention,
    'reasoning': razonamiento_completo
}

# ✅ STUDENT: Recibir entidades completas
self.master_intention = context.intention_info
limite = self._get_master_limit()           # ✅ ACCESO GARANTIZADO
filtros = self._get_master_filters()        # ✅ ACCESO GARANTIZADO

# ✅ STUDENT: Reportar resultados completos
return InterpretationResult(
    action=accion_ejecutada,
    parameters={
        "data": resultados,
        "row_count": len(resultados),
        "sql_executed": sql_query,
        "master_intention": self.master_intention,  # ✅ PRESERVAR CONTEXTO
        # ... datos técnicos completos
    }
)
```

#### **VALIDACIÓN AUTOMÁTICA:**

```python
# AGREGAR EN CADA NUEVO INTÉRPRETE
def validate_protocol_compliance(self, context, result):
    """Valida cumplimiento del protocolo estandarizado"""

    # Validar recepción de entidades
    if not hasattr(context, 'intention_info'):
        self.logger.error("❌ PROTOCOLO: Falta intention_info")
        return False

    # Validar detected_entities
    entities = context.intention_info.get('detected_entities', {})
    if not entities:
        self.logger.warning("⚠️ PROTOCOLO: detected_entities vacías")

    # Validar reporte completo
    required_params = ['data', 'row_count', 'master_intention']
    for param in required_params:
        if param not in result.parameters:
            self.logger.error(f"❌ PROTOCOLO: Falta {param} en reporte")
            return False

    return True
```

#### **LOGGING OBLIGATORIO:**

```python
# EN CADA NUEVO INTÉRPRETE
self.logger.info(f"🎯 [NUEVO_INTERPRETE] Entidades recibidas: {list(entities.keys())}")
self.logger.info(f"🎯 [NUEVO_INTERPRETE] Límite aplicado: {limite}")
self.logger.info(f"🎯 [NUEVO_INTERPRETE] Filtros aplicados: {filtros}")
self.logger.info(f"📤 [NUEVO_INTERPRETE] Reportando: {action} → {row_count} resultados")
```

### **GARANTÍAS DE FUNCIONAMIENTO:**

- ✅ **Transferencia completa** de entidades Master → Student
- ✅ **Acceso garantizado** a límites y filtros en Student
- ✅ **Reporte completo** Student → Master
- ✅ **Preservación de contexto** en toda la cadena
- ✅ **Validación automática** del protocolo
- ✅ **Logging detallado** en puntos críticos
- ✅ **Fallbacks robustos** para cada componente

---

**🎯 RESULTADO**: Sistema Master-Student completamente extensible, mantenible y con **protocolo estandarizado** que garantiza funcionamiento robusto al 100%.
