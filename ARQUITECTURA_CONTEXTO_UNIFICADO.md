# 🧠 ARQUITECTURA DE CONTEXTO UNIFICADO MULTI-ESPECIALISTA

## 📋 **RESUMEN EJECUTIVO**

Este documento define la arquitectura de **contexto unificado** que permite al **MasterInterpreter** manejar conversaciones coherentes entre múltiples especialistas (**StudentQueryInterpreter**, **HelpInterpreter**, **GeneralInterpreter**) manteniendo continuidad conversacional y contexto compartido.

---

## 🎯 **ARQUITECTURA BASE VERIFICADA**

### **✅ FUNDAMENTOS YA PROBADOS:**
- **5 pausas estratégicas** funcionando perfectamente (ver `FLUJO_COMUNICACION_AI.md`)
- **Flujo Master→Student** completamente verificado
- **Continuaciones** con contexto conversacional dinámico
- **Sin hardcodeo** - sistema completamente flexible

### **🏗️ ESTRUCTURA DE ESPECIALISTAS:**

```
🧠 MASTER INTERPRETER (Director + Personalidad del Sistema)
    ├── 🎓 StudentQueryInterpreter (TODO sobre alumnos)
    │   ├── Búsquedas, filtros, consultas
    │   ├── Estadísticas y reportes
    │   ├── Constancias y documentos
    │   └── Transformaciones PDF
    ├── ❓ HelpInterpreter (Guía del sistema)
    │   ├── Explicaciones de funcionalidades
    │   ├── Tutoriales paso a paso
    │   └── Resolución de dudas
    └── 💬 GeneralInterpreter (Conversación general)
        ├── Preguntas generales
        ├── Conversación casual
        └── Consultas no relacionadas con alumnos
```

---

## 🔄 **CONTEXTO UNIFICADO**

### **🎯 ESTRUCTURA DEL CONTEXTO:**

```python
class UnifiedConversationContext:
    def __init__(self):
        self.conversation_flow = []  # Contexto unificado para todos los especialistas
        self.max_context_size = 15   # Últimas 15 interacciones
    
    def add_interaction(self, user_query, specialist_used, specialist_result, master_response):
        interaction = {
            # INFORMACIÓN CONVERSACIONAL
            "user_query": user_query,
            "master_response": master_response,
            "timestamp": datetime.now(),
            "interaction_id": self._generate_id(),
            
            # INFORMACIÓN DEL ESPECIALISTA
            "specialist_used": specialist_used,  # "student", "help", "general"
            "specialist_action": specialist_result.get("action"),
            "specialist_confidence": specialist_result.get("confidence", 0.0),
            
            # CONTEXTO TÉCNICO ESPECÍFICO
            "sql_executed": specialist_result.get("sql_executed"),      # Solo Student
            "help_topic": specialist_result.get("help_topic"),          # Solo Help
            "general_topic": specialist_result.get("topic"),            # Solo General
            
            # DATOS Y METADATOS
            "row_count": specialist_result.get("row_count", 0),
            "data_size": len(specialist_result.get("data", [])),
            "data_cached": self._should_cache_data(specialist_result.get("data", [])),
            "cached_data": specialist_result.get("data") if self._should_cache_data(specialist_result.get("data", [])) else None,
            
            # CONTEXTO DE CONTINUACIÓN
            "can_continue": True,
            "continuation_hints": specialist_result.get("esperando_continuacion"),
            "cross_specialist_context": self._extract_cross_context(specialist_result)
        }
        
        self.conversation_flow.append(interaction)
        self._maintain_context_size()
```

### **🔍 MÉTODOS DE CONTEXTO INTELIGENTE:**

```python
def get_context_for_specialist(self, specialist, current_query):
    """Prepara contexto específico para cada especialista"""
    
    if specialist == "student":
        return {
            "previous_searches": self._get_interactions_by_specialist("student", limit=3),
            "help_context": self._get_last_interaction_by_specialist("help"),
            "general_context": self._get_last_interaction_by_specialist("general"),
            "current_query": current_query,
            "available_data": self._get_available_data_references()
        }
    
    elif specialist == "help":
        return {
            "system_state": self._get_conversation_summary(),
            "last_student_action": self._get_last_interaction_by_specialist("student"),
            "user_question": current_query,
            "context_data": self._get_contextual_data_for_help()
        }
    
    elif specialist == "general":
        return {
            "conversation_flow": self._get_conversation_summary(last_n=5),
            "school_context": True,  # Mantener personalidad de asistente escolar
            "current_topic": current_query
        }

def _get_available_data_references(self):
    """Obtiene referencias a datos disponibles para regeneración"""
    data_refs = []
    for interaction in reversed(self.conversation_flow):
        if interaction["specialist_used"] == "student" and interaction["row_count"] > 0:
            data_refs.append({
                "interaction_id": interaction["interaction_id"],
                "query": interaction["user_query"],
                "sql": interaction["sql_executed"],
                "row_count": interaction["row_count"],
                "can_regenerate": True
            })
            if len(data_refs) >= 3:  # Últimas 3 consultas con datos
                break
    return data_refs
```

---

## 🎯 **INTEGRACIÓN CON PAUSAS ESTRATÉGICAS**

### **🔄 PAUSAS ADAPTADAS PARA MÚLTIPLES ESPECIALISTAS:**

Las **5 pausas estratégicas** ya probadas se adaptan automáticamente según el especialista:

#### **1. 🧠 Master: Razonamiento inicial (ADAPTADO)**
```
🛑 [MASTER] ANÁLISIS INICIAL:
    ├── 📝 Consulta: 'constancia para el primero'
    ├── 🧠 Intención detectada: generar_constancia/accion_especifica
    ├── 📊 Confianza: 0.95
    ├── 🎯 Especialista seleccionado: StudentQueryInterpreter  ← NUEVO
    ├── 🔄 Contexto disponible: 2 niveles (student: 1, help: 1)  ← NUEVO
    ├── 📋 Contexto cross-especialista: Disponible  ← NUEVO
    └── Presiona ENTER para delegar a Student...
```

#### **2. 🎓 Especialista: Recibe información del Master (ADAPTADO)**
```
🛑 [STUDENT] RECIBE DEL MASTER:
    ├── 📝 Consulta: 'constancia para el primero'
    ├── 🎯 Intención: generar_constancia
    ├── 🔄 Contexto unificado disponible: 2 niveles  ← NUEVO
    │   ├── Student: 'busca alumnos Martinez' (21 elementos)
    │   └── Help: 'cómo generar constancia' (tutorial)  ← NUEVO
    ├── 🧠 Contexto cross-especialista: Help explicó proceso  ← NUEVO
    └── Presiona ENTER para que Student procese...
```

### **🆕 NUEVA PAUSA: Detección de cambio de especialista**
```
🛑 [MASTER] CAMBIO DE ESPECIALISTA DETECTADO:
    ├── 📝 Consulta: '¿cómo genero una constancia?'
    ├── 🔄 Especialista anterior: StudentQueryInterpreter
    ├── 🎯 Especialista nuevo: HelpInterpreter
    ├── 📋 Contexto a transferir: 21 alumnos Martinez disponibles
    ├── 🧠 Razón del cambio: Usuario solicita ayuda sobre funcionalidad
    └── Presiona ENTER para cambiar a Help...
```

---

## 📝 **FLUJOS DE EJEMPLO**

### **🎯 FLUJO MULTI-ESPECIALISTA COMPLETO:**

```
1. Usuario: "busca alumnos Martinez"
   Master → Student → [21 alumnos encontrados]
   Contexto: [student: busqueda_martinez]

2. Usuario: "¿cómo puedo generar una constancia para uno de ellos?"
   Master → Help (con contexto de Student) → [Tutorial de constancias]
   Contexto: [student: busqueda_martinez, help: tutorial_constancias]

3. Usuario: "constancia para el primero"
   Master → Student (con contexto de Help + datos anteriores) → [Constancia generada]
   Contexto: [student: busqueda_martinez + constancia_generada, help: tutorial_constancias]

4. Usuario: "¿qué es una constancia de estudios?"
   Master → General (manteniendo personalidad escolar) → [Explicación general + conexión al sistema]
   Contexto: [student: ..., help: ..., general: explicacion_constancia]
```

---

## 🎯 **PRÓXIMOS PASOS DE IMPLEMENTACIÓN**

### **📋 FASES DE DESARROLLO:**

1. **FASE 1**: Implementar `UnifiedConversationContext`
2. **FASE 2**: Crear `HelpInterpreter` básico
3. **FASE 3**: Adaptar pausas estratégicas para múltiples especialistas
4. **FASE 4**: Implementar `GeneralInterpreter`
5. **FASE 5**: Testing completo del flujo multi-especialista

### **🔍 PUNTOS CRÍTICOS A VERIFICAR:**
- ✅ Contexto se mantiene entre especialistas
- ✅ Pausas estratégicas funcionan con todos los especialistas
- ✅ Sin pérdida de información en cambios de especialista
- ✅ Respuestas coherentes y naturales
- ✅ Personalidad del sistema se mantiene

---

## 🚀 **BENEFICIOS ESPERADOS**

- **Conversaciones naturales** entre especialistas
- **Contexto compartido** inteligente
- **Respuestas coherentes** y humanas
- **Escalabilidad** para nuevos especialistas
- **Mantenimiento** de personalidad del sistema
