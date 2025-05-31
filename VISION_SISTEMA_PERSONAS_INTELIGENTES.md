# 🧠 VISIÓN: SISTEMA DE PERSONAS INTELIGENTES
## ARQUITECTURA DE COMUNICACIÓN ENTRE PROMPTS ESPECIALIZADOS

**Fecha:** Diciembre 2024
**Estado:** ✅ IMPLEMENTADO Y VALIDADO - Protocolo oficial del sistema
**Propósito:** Documentar la visión completa del sistema como "equipo de personas inteligentes"
**Última validación:** Enero 2025 - Sistema funcionando al 100%

---

## 🎯 **FILOSOFÍA CENTRAL**

### **CONCEPTO CLAVE:**
**Los prompts funcionan como PERSONAS INTELIGENTES que razonan, se comunican y colaboran entre sí para resolver consultas complejas.**

### **PRINCIPIOS FUNDAMENTALES:**
1. **🧠 RAZONAMIENTO HUMANO:** Cada prompt piensa como una persona experta
2. **💬 COMUNICACIÓN BIDIRECCIONAL:** Los prompts "se hablan" entre sí
3. **🎯 ESPECIALIZACIÓN:** Cada prompt es experto en su dominio
4. **📋 PLANIFICACIÓN ESTRATÉGICA:** Se arman planes antes de ejecutar
5. **🔄 RETROALIMENTACIÓN:** Los prompts aprenden de interacciones previas

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### **ESTRUCTURA JERÁRQUICA:**
```
🧠 MASTER PROMPT (Líder/Coordinador)
├── 📊 STUDENT INTERPRETER (Especialista en Alumnos)
├── 📄 CONSTANCIA INTERPRETER (Especialista en Documentos)
├── ❓ HELP INTERPRETER (Especialista en Ayuda)
└── [Futuros especialistas...]
```

### **FLUJO DE COMUNICACIÓN:**
```
👤 Usuario → 🧠 Master → 📊 Student → 🔧 Acciones → 📊 Student → 🧠 Master → 👤 Usuario
```

---

## 🧠 **MASTER PROMPT - EL LÍDER INTELIGENTE**

### **PERSONALIDAD:**
- **Rol:** Director general que conoce TODO el sistema
- **Responsabilidad:** Detectar intenciones y dirigir al especialista correcto
- **Conocimiento:** Capacidades completas del sistema, no detalles técnicos

### **CONTEXTO ESTRATÉGICO QUE DEBE TENER:**
```
🎯 MAPA DEL SISTEMA (Qué especialista para qué):
- StudentQueryInterpreter:
  * Maneja: consulta_alumnos, generar_constancia
  * Sub-intenciones: busqueda_simple, busqueda_compleja, estadisticas
  * Capacidades: "Consultas de BD, documentos, análisis de 211 alumnos"

- HelpInterpreter:
  * Maneja: ayuda_sistema
  * Sub-intenciones: pregunta_capacidades, pregunta_tecnica
  * Capacidades: "Ayuda y soporte técnico del sistema"

💭 MEMORIA DE INTERACCIONES:
- last_specialist: "StudentQueryInterpreter"
- last_result_summary: "59 alumnos grupo A matutino - filtro promedio pendiente"
- conversation_flow: "búsqueda → especificación pendiente"
- specialist_feedback: "Esperando aplicar filtro dinámico de promedio"

🔄 CONTEXTO CONVERSACIONAL:
- conversation_stack: [datos de consultas previas]
- awaiting_continuation: true/false
- continuation_type: "selection", "action", "confirmation"

⚠️ LIMITACIONES GENERALES:
- Solo consulta datos, no los modifica
- Requiere datos existentes para constancias
- No puede acceder a sistemas externos
```

### **INTENCIONES Y SUB-INTENCIONES OFICIALES (VALIDADAS):**
```
📊 consulta_alumnos:
├── busqueda_simple      → 1-2 criterios básicos (nombre, grado, turno)
├── busqueda_compleja    → 3+ criterios O campos especiales (promedio)
├── estadisticas         → Conteos, promedios, distribuciones ("cuántos", "total")
├── generar_constancia   → Documentos oficiales PDF
└── transformacion_pdf   → Conversión entre formatos de constancias

❓ ayuda_sistema:
├── pregunta_capacidades → Qué puede hacer el sistema
└── pregunta_tecnica    → Ayuda con funcionalidades específicas

💬 conversacion_general:
├── saludo              → Saludos y presentaciones
└── chat_casual         → Conversación no relacionada al sistema
```

### **CRITERIOS DE CLASIFICACIÓN VALIDADOS:**
```
✅ busqueda_simple:
   - Ejemplos: "buscar García", "alumnos de 2do A", "turno matutino"
   - Criterios: 1-2 filtros básicos
   - Campos: directos en BD (nombre, grado, grupo, turno)

✅ busqueda_compleja:
   - Ejemplos: "alumnos de 2do A turno matutino", "García con promedio > 8"
   - Criterios: 3+ filtros O campos especiales
   - Campos: combinaciones múltiples O JSON (promedio)

✅ estadisticas:
   - Ejemplos: "cuántos alumnos hay", "total por grado", "distribución"
   - Palabras clave: "cuántos", "total", "promedio", "distribución"
   - Resultado: números, conteos, análisis

✅ generar_constancia:
   - Ejemplos: "constancia para Juan Pérez", "certificado de María"
   - Palabras clave: "constancia", "certificado", "documento"
   - Resultado: archivo PDF

✅ transformacion_pdf:
   - Ejemplos: "convertir PDF", "cambiar formato de constancia"
   - Palabras clave: "convertir", "transformar", "cambiar formato"
   - Resultado: PDF convertido
```

### **COMUNICACIÓN CON ESPECIALISTAS:**
```python
# Master → Student:
{
    "intention_type": "consulta_alumnos",
    "sub_intention": "busqueda_compleja",
    "detected_entities": {"nombres": ["García"], "criterios": ["grupo A"]},
    "master_message": "Detecté búsqueda compleja. Procede con análisis estratégico.",
    "conversation_context": [datos_previos],
    "system_capabilities": [capacidades_disponibles]
}

# Student → Master:
{
    "status": "completed",
    "strategy_used": "BUSCAR_ALUMNOS + FILTRAR_RESULTADOS",
    "results_summary": "5 alumnos García encontrados",
    "ambiguity_detected": true,
    "awaiting_continuation": "selection",
    "student_message": "Consulta ambigua resuelta. Mostré todos los García. Esperando especificación del usuario."
}
```

---

## 📊 **STUDENT INTERPRETER - EL ESPECIALISTA EN ALUMNOS**

### **PERSONALIDAD:**
- **Rol:** Especialista experto en datos de alumnos y consultas académicas
- **Responsabilidad:** Razonar estratégicamente y resolver consultas complejas
- **Conocimiento:** Base de datos completa, acciones disponibles, capacidades técnicas

### **CONTEXTO TÉCNICO COMPLETO QUE DEBE TENER:**
```
🗄️ ESTRUCTURA DE BASE DE DATOS:
- alumnos: id, curp, nombre, matricula, fecha_nacimiento
- datos_escolares: id, alumno_id, grado, grupo, turno, escuela, calificaciones(JSON)
- constancias: id, alumno_id, tipo, ruta_archivo, fecha_generacion

⚠️ CAMPOS ESPECIALES (CRÍTICOS):
- promedio: NO existe como campo directo
- calificaciones: JSON con promedio por materia
- Para promedio general: usar JSON_EXTRACT o filtros dinámicos

🔧 ACCIONES DISPONIBLES VALIDADAS:
- BUSCAR_UNIVERSAL (PRINCIPAL):
  * Propósito: "Búsqueda flexible con criterios múltiples"
  * Entrada: "criterio_principal + filtros_adicionales"
  * Salida: "lista de alumnos filtrada"
  * Uso: "Para búsquedas con 1-3 criterios combinados"
  * Validado: ✅ Funciona perfectamente con múltiples filtros

- BUSCAR_Y_FILTRAR (ALIAS):
  * Propósito: "Alias de BUSCAR_UNIVERSAL para consultas complejas"
  * Entrada: "lista de criterios"
  * Salida: "redirige a BUSCAR_UNIVERSAL"
  * Uso: "Cuando Student detecta múltiples criterios"
  * Validado: ✅ Conversión automática funcional

- OBTENER_ALUMNO_EXACTO:
  * Propósito: "Obtener UN alumno específico"
  * Entrada: "identificador único (CURP, matrícula, ID)"
  * Salida: "datos completos de un alumno"
  * Uso: "Cuando se busca una persona específica"
  * Validado: ⏳ Pendiente de validación

- CALCULAR_ESTADISTICA:
  * Propósito: "Cálculos y análisis de datos"
  * Entrada: "tipo de estadística, filtros opcionales"
  * Salida: "números, promedios, distribuciones"
  * Uso: "Para análisis numéricos y reportes"
  * Validado: ⏳ Pendiente de validación

- GENERAR_CONSTANCIA_COMPLETA:
  * Propósito: "Generación de documentos oficiales PDF"
  * Entrada: "datos del alumno, tipo de constancia"
  * Salida: "archivo PDF generado"
  * Uso: "Para documentos oficiales"
  * Validado: ⏳ Pendiente de validación

📋 PLANTILLAS SQL OPTIMIZADAS:
- buscar_por_nombre.sql: "Para búsquedas por nombre/apellido"
- filtrar_grado_grupo.sql: "Para filtros de grado y grupo"
- buscar_con_promedio.sql: "Para criterios de promedio (JSON_EXTRACT)"
- contar_con_filtros.sql: "Para conteos específicos"

🧠 GUÍAS DE RAZONAMIENTO ESTRATÉGICO:
- "García" → apellido común → varios resultados → mostrar todos + preguntar
- "CURP específico" → identificador único → un resultado → mostrar directo
- "promedio > 8" → requiere JSON_EXTRACT → usar plantilla especial
```

### **PROCESO DE RAZONAMIENTO ESTRATÉGICO:**
```
🧠 ANÁLISIS DE CONSULTA:
1. ¿Qué quiere realmente el usuario?
2. ¿Es ambigua la consulta?
3. ¿Qué tipo de resultado esperar?
4. ¿Hay referencias al contexto previo?

🎯 PLANIFICACIÓN ESTRATÉGICA:
1. ¿Qué acciones necesito?
2. ¿En qué orden ejecutarlas?
3. ¿Cómo combinar resultados?
4. ¿Qué plantillas usar?

💬 COMUNICACIÓN DE RESULTADO:
1. ¿Cómo explicar lo que encontré?
2. ¿Hay ambigüedad que aclarar?
3. ¿Espero continuación del usuario?
4. ¿Qué información dar al Master?
```

### **EJEMPLOS DE RAZONAMIENTO:**

#### **CASO 1: "buscar García"**
```
🧠 RAZONAMIENTO:
"La consulta dice 'buscar García'. García es un apellido común en la base de datos.
¿El usuario quiere UNA persona específica o TODOS los García?
La consulta es ambigua porque no especifica.

ESTRATEGIA:
1. Usar BUSCAR_ALUMNOS_POR_CRITERIO con criterio 'apellido García'
2. Mostrar TODOS los resultados encontrados
3. Explicar que hay varios y preguntar por especificación
4. Marcar awaiting_continuation = 'selection'

PLANTILLA: buscar_por_nombre.sql
PARÁMETROS: nombre LIKE '%García%'"

📊 RESULTADO ESPERADO: Lista de múltiples alumnos
💬 MENSAJE: "Encontré 5 alumnos García. ¿Te refieres a alguno en particular?"
```

#### **CASO 2: "buscar a todos los García"**
```
🧠 RAZONAMIENTO:
"La consulta dice 'buscar a TODOS los García'.
La palabra 'todos' indica claramente que quiere ver todos los resultados.
No hay ambigüedad. Es una solicitud directa de listado completo.

ESTRATEGIA:
1. Usar BUSCAR_ALUMNOS_POR_CRITERIO con criterio 'apellido García'
2. Mostrar lista completa sin preguntar
3. No marcar continuación a menos que usuario pregunte algo más

PLANTILLA: buscar_por_nombre.sql
PARÁMETROS: nombre LIKE '%García%'"

📊 RESULTADO ESPERADO: Lista completa
💬 MENSAJE: "Aquí están todos los alumnos García (5 encontrados):"
```

#### **CASO 3: "alumnos de 2do A turno matutino con promedio > 8"**
```
🧠 RAZONAMIENTO:
"Consulta compleja con múltiples criterios:
- grado = 2
- grupo = A
- turno = MATUTINO
- promedio > 8 (requiere JSON_EXTRACT)

ESTRATEGIA:
1. Usar BUSCAR_ALUMNOS_POR_CRITERIO para criterios básicos
2. Aplicar filtro de promedio con plantilla especial
3. Combinar resultados
4. El resultado será específico, no ambiguo

PLANTILLAS:
- Primaria: filtrar_grado_grupo.sql
- Secundaria: buscar_con_promedio.sql
PARÁMETROS: grado=2, grupo='A', turno='MATUTINO', promedio>8"

📊 RESULTADO ESPERADO: Lista filtrada específica
💬 MENSAJE: "Encontré 12 alumnos de 2°A del turno matutino con promedio mayor a 8"
```

---

## 🔗 **COMUNICACIÓN ENTRE PROMPTS**

### **PROTOCOLO DE COMUNICACIÓN:**
```
🧠 Master → 📊 Student:
- intention_info: Intención y sub-intención detectada
- master_message: Instrucciones específicas del líder
- conversation_context: Contexto de conversaciones previas
- system_capabilities: Qué puede hacer el sistema

📊 Student → 🧠 Master:
- strategy_used: Qué estrategia se usó
- results_summary: Resumen de resultados obtenidos
- ambiguity_detected: Si se detectó ambigüedad
- awaiting_continuation: Tipo de continuación esperada
- student_message: Mensaje para el Master sobre el estado
```

### **MEMORIA CONVERSACIONAL:**
```python
# Master recuerda:
previous_interactions = {
    "last_intention": "consulta_alumnos/busqueda_simple",
    "last_result": "5 alumnos García encontrados",
    "student_status": "awaiting_selection",
    "conversation_flow": "García → esperando especificación"
}

# Student recuerda:
conversation_stack = [
    {
        "query": "buscar García",
        "strategy": "BUSCAR_ALUMNOS_POR_CRITERIO",
        "results": [lista_garcia],
        "awaiting": "selection"
    }
]
```

---

## 🎯 **INTEGRACIÓN CON ACCIONES Y PLANTILLAS**

### **ACCIONES COMO HERRAMIENTAS ESPECIALIZADAS:**
```
BUSCAR_ALUMNOS_POR_CRITERIO:
- Propósito: Búsqueda flexible con criterios múltiples
- Entrada: criterios dinámicos
- Salida: lista de alumnos
- Plantillas: buscar_por_nombre, filtrar_grado_grupo, buscar_general
- Uso: Cuando se necesita búsqueda con 1-3 criterios

OBTENER_ALUMNO_EXACTO:
- Propósito: Obtener UN alumno específico
- Entrada: identificador único (CURP, matrícula, ID)
- Salida: datos completos de un alumno
- Plantillas: buscar_por_curp, buscar_por_matricula
- Uso: Cuando se busca una persona específica

CALCULAR_ESTADISTICA:
- Propósito: Cálculos y análisis de datos
- Entrada: tipo de estadística, filtros opcionales
- Salida: números, promedios, distribuciones
- Plantillas: promedio_general, conteo_por_grado, distribuciones
- Uso: Para análisis numéricos y reportes
```

### **PLANTILLAS SQL OPTIMIZADAS:**
```sql
-- buscar_por_nombre.sql
SELECT a.id, a.nombre, a.curp, de.grado, de.grupo, de.turno
FROM alumnos a
LEFT JOIN datos_escolares de ON a.id = de.alumno_id
WHERE a.nombre LIKE '%{nombre_criterio}%'
ORDER BY a.nombre;

-- buscar_con_promedio.sql
SELECT a.nombre, a.curp, de.grado, de.grupo,
       (SELECT AVG(CAST(json_extract(value, '$.promedio') AS REAL))
        FROM json_each(de.calificaciones)
        WHERE json_extract(value, '$.promedio') IS NOT NULL) as promedio_calculado
FROM alumnos a
JOIN datos_escolares de ON a.id = de.alumno_id
WHERE {criterios_basicos}
HAVING promedio_calculado > {promedio_minimo};
```

---

## 🚀 **FLUJO COMPLETO DE EJEMPLO**

### **CONSULTA: "buscar García del turno matutino"**

#### **1. MASTER PROMPT:**
```
🧠 ANÁLISIS:
- Intención: consulta_alumnos
- Sub-intención: busqueda_compleja (dos criterios)
- Entidades: apellido "García", turno "matutino"

📤 MENSAJE A STUDENT:
"Detecté búsqueda compleja con múltiples criterios. Procede con análisis estratégico."
```

#### **2. STUDENT INTERPRETER:**
```
🧠 RAZONAMIENTO:
"Consulta con dos criterios: apellido García + turno matutino.
García puede dar múltiples resultados, pero el filtro de turno los reducirá.
Estrategia: buscar García primero, filtrar por turno después."

🎯 PLAN:
1. BUSCAR_ALUMNOS_POR_CRITERIO con nombre='García' AND turno='MATUTINO'
2. Usar plantilla buscar_con_filtros.sql
3. Mostrar resultados específicos

🔧 EJECUCIÓN:
- Plantilla: buscar_con_filtros.sql
- Parámetros: nombre LIKE '%García%' AND turno = 'MATUTINO'
- Resultado: 2 alumnos encontrados

📤 MENSAJE A MASTER:
"Completado. Estrategia: búsqueda con filtros múltiples.
Encontré 2 alumnos García del turno matutino. Resultado específico, no requiere continuación."
```

#### **3. RESPUESTA AL USUARIO:**
```
💬 "Encontré 2 alumnos García del turno matutino:
1. Juan García López - 2°A - Matutino
2. Ana García Torres - 4°A - Matutino

¿Necesitas información específica de alguno de ellos?"
```

---

## ✅ **BENEFICIOS DE ESTA ARQUITECTURA**

### **🧠 INTELIGENCIA HUMANA:**
- Razonamiento natural sobre ambigüedades
- Planificación estratégica antes de actuar
- Comunicación clara y contextual

### **🔄 FLEXIBILIDAD:**
- Adaptación a consultas imprevistas
- Combinación creativa de acciones
- Aprendizaje de interacciones previas

### **🎯 PRECISIÓN:**
- Uso de plantillas SQL probadas
- Validación contra estructura real de BD
- Manejo inteligente de casos especiales

### **💬 EXPERIENCIA DE USUARIO:**
- Respuestas naturales y contextuales
- Manejo inteligente de ambigüedades
- Conversaciones fluidas y coherentes

---

## ✅ **FLUJO VALIDADO EN PRODUCCIÓN**

### **CONSULTA VALIDADA: "dame alumnos de 2do A turno matutino"**

#### **1. MASTER INTERPRETER (VALIDADO):**
```
🧠 ANÁLISIS PERFECTO:
- Intención: consulta_alumnos ✅
- Sub-intención: busqueda_compleja ✅ (3 criterios)
- Confianza: 0.95 ✅
- Entidades detectadas: grado:2, grupo:A, turno:matutino ✅

📤 COMUNICACIÓN MASTER→STUDENT:
- Información completa transferida ✅
- Contexto estratégico incluido ✅
- Sin decisiones técnicas (correcto) ✅
```

#### **2. STUDENT INTERPRETER (VALIDADO):**
```
🧠 RAZONAMIENTO INTELIGENTE:
- Categoría: reporte/listado ✅
- Flujo: listado_completo ✅
- Acción seleccionada: BUSCAR_Y_FILTRAR → BUSCAR_UNIVERSAL ✅

🎯 PARÁMETROS GENERADOS:
- criterio_principal: grado = '2' ✅
- filtros_adicionales: grupo = 'A', turno = 'MATUTINO' ✅
- Conversión automática funcionando ✅
```

#### **3. ACTION EXECUTOR (VALIDADO):**
```
🔧 EJECUCIÓN PERFECTA:
- 3 criterios procesados correctamente ✅
- 0 criterios de promedio (correcto) ✅
- SQL generado: WHERE de.grado = '2' AND de.grupo = 'A' AND de.turno = 'MATUTINO' ✅
- Resultados: 11 alumnos obtenidos ✅
```

#### **4. RESPUESTA CONVERSACIONAL (VALIDADA):**
```
💬 RESPUESTA CORREGIDA:
"Encontré **11 alumnos de segundo grado del grupo A del turno matutino**"

✅ INCLUYE TODOS LOS FILTROS:
- ✅ segundo grado (grado)
- ✅ grupo A (grupo)
- ✅ turno matutino (turno)

✅ AUTO-REFLEXIÓN ACTIVADA:
- Conversation_stack actualizado ✅
- Datos guardados para seguimiento ✅
- Continuación esperada: analysis ✅
```

### **DATOS REALES OBTENIDOS (VALIDADOS):**
```
11 estudiantes de 2do A turno matutino:
1. VALERIA RAMIREZ SANCHEZ
2. ROSA MENDOZA MORALES (con calificaciones)
3. BENJAMIN GONZALEZ SANCHEZ (con calificaciones)
4. ADRIANA RODRIGUEZ GONZALEZ (con calificaciones)
5. ALBERTO CRUZ TORRES
6. CAMILA ROMERO RODRIGUEZ
7. ANDRES HERNANDEZ PEREZ (con calificaciones)
8. ALBERTO SANCHEZ PEREZ (con calificaciones)
9. DIANA GONZALEZ TORRES (con calificaciones)
10. MANUEL RUIZ LOPEZ (con calificaciones)
11. LEONARDO PEREZ GUERRERO (con calificaciones)
```

### **PAUSAS DE DEBUG VALIDADAS:**
```
🛑 PAUSA DEBUG: Comunicación Master→Student ✅
🛑 PAUSA 1: Análisis de consulta completado ✅
🛑 PAUSA 2: Acción seleccionada ✅
🛑 PAUSA 3: Análisis de filtros ✅
🛑 PAUSA 4: SQL final generado ✅

Control por argumentos:
- python ai_chat.py --debug-pauses (activar)
- python ai_chat.py (desactivar por defecto)
```

---

## 🎯 **PRINCIPIOS DE DIVISIÓN DE CONTEXTOS INFALIBLES**

### **FILOSOFÍA: CONTEXTO POR RESPONSABILIDAD**
```
🎯 Master: "¿QUÉ especialista puede resolver esto?"
📊 Student: "¿CÓMO resuelvo esto con mis herramientas?"
```

### **PRINCIPIO 1: INFORMACIÓN JUST-IN-TIME**
- ✅ **CORRECTO:** Dar contexto cuando se necesita
- ❌ **INCORRECTO:** Dar todo el contexto a todos

### **PRINCIPIO 2: CONTEXTO ESTRATÉGICO vs TÉCNICO**
- **Master:** Contexto **ESTRATÉGICO** (qué puede hacer el sistema)
- **Student:** Contexto **TÉCNICO** (cómo hacer las cosas)

### **PRINCIPIO 3: COMUNICACIÓN BIDIRECCIONAL**
- **Master → Student:** Intención + contexto estratégico
- **Student → Master:** Resultado + retroalimentación + estado

### **DISEÑO DE CONTEXTOS INFALIBLES:**

#### **MASTER CONTEXT (LIGERO - ESTRATÉGICO):**
```python
master_context = {
    "system_map": {
        "StudentQueryInterpreter": {
            "handles": ["consulta_alumnos", "generar_constancia"],
            "sub_intentions": ["busqueda_simple", "busqueda_compleja"],
            "capabilities": "Consultas BD + documentos (211 alumnos)"
        },
        "HelpInterpreter": {
            "handles": ["ayuda_sistema"],
            "sub_intentions": ["pregunta_capacidades", "pregunta_tecnica"],
            "capabilities": "Ayuda y soporte técnico"
        }
    },
    "interaction_memory": {
        "last_specialist": "StudentQueryInterpreter",
        "last_result_summary": "59 alumnos encontrados",
        "conversation_flow": "búsqueda → filtro pendiente",
        "specialist_feedback": "Esperando aplicar filtro promedio"
    },
    "conversation_stack": [...],
    "awaiting_continuation": true
}
```

#### **STUDENT CONTEXT (COMPLETO - TÉCNICO):**
```python
student_context = {
    "database_structure": {
        "alumnos": ["id", "curp", "nombre", "matricula"],
        "datos_escolares": ["alumno_id", "grado", "grupo", "turno", "calificaciones"],
        "special_fields": {
            "promedio": "NO existe - usar JSON_EXTRACT",
            "calificaciones": "JSON con promedio por materia"
        }
    },
    "action_catalog": {
        "BUSCAR_ALUMNOS_POR_CRITERIO": {
            "purpose": "Búsqueda flexible con criterios múltiples",
            "input": "criterios dinámicos",
            "output": "lista de alumnos",
            "when_to_use": "1-3 criterios de búsqueda"
        }
    },
    "sql_templates": {
        "buscar_por_nombre.sql": "Para búsquedas por nombre/apellido",
        "buscar_con_promedio.sql": "Para criterios de promedio (JSON_EXTRACT)"
    },
    "strategic_guidelines": {
        "García": "apellido común → varios resultados → mostrar + preguntar",
        "CURP": "único → un resultado → mostrar directo",
        "promedio > X": "requiere JSON_EXTRACT → plantilla especial"
    },
    "conversation_stack": [...],
    "intention_info": {...}
}
```

### **VALIDACIÓN DE CONTEXTO:**
```python
def validate_master_context(context):
    required = ["system_map", "interaction_memory", "conversation_stack"]
    return all(field in context for field in required)

def validate_student_context(context):
    required = ["database_structure", "action_catalog", "sql_templates", "intention_info"]
    return all(field in context for field in required)
```

---

## 🔧 **IMPLEMENTACIÓN TÉCNICA RECOMENDADA**

### **CAMBIOS NECESARIOS EN EL SISTEMA ACTUAL:**

#### **1. MEJORAR MASTER PROMPT:**
```python
# Agregar contexto del sistema completo
system_capabilities_context = """
CAPACIDADES DEL SISTEMA:
- StudentQueryInterpreter: 8 acciones disponibles, 15+ plantillas SQL
- ConstanciaInterpreter: 3 tipos de constancias
- HelpInterpreter: Ayuda técnica y capacidades

LIMITACIONES:
- Solo consulta, no modifica datos
- Requiere datos existentes para constancias
- Base de datos: 211 alumnos activos
"""

# Agregar memoria de interacciones
previous_interaction_memory = {
    "last_specialist": "StudentQueryInterpreter",
    "last_result": "5 alumnos García - awaiting selection",
    "conversation_flow": "búsqueda → especificación pendiente"
}
```

#### **2. MEJORAR STUDENT INTERPRETER:**
```python
# Agregar prompt de razonamiento estratégico
strategic_reasoning_prompt = f"""
🧠 ANÁLISIS ESTRATÉGICO REQUERIDO:

CONSULTA: "{user_query}"
CONTEXTO COMPLETO:
{database_structure}
{available_actions}
{sql_templates}
{conversation_context}

MI PROCESO DE RAZONAMIENTO:
1. ¿Qué quiere realmente el usuario?
2. ¿Es ambigua la consulta? ¿Por qué?
3. ¿Qué tipo de resultado esperar? (uno/varios/conteo/cálculo)
4. ¿Qué estrategia usar? (simple/combinada/secuencial)
5. ¿Qué acciones y plantillas necesito?
6. ¿Cómo comunicar el resultado?

EJEMPLOS DE RAZONAMIENTO:
- "García" → apellido común → varios resultados → mostrar todos + preguntar
- "CURP específico" → identificador único → un resultado → mostrar directo
- "promedio > 8" → requiere JSON_EXTRACT → usar plantilla especial
"""
```

#### **3. PROTOCOLO DE COMUNICACIÓN:**
```python
class InterPromptCommunication:
    def master_to_student(self, intention_info, master_analysis):
        return {
            "intention_type": intention_info.intention_type,
            "sub_intention": intention_info.sub_intention,
            "detected_entities": intention_info.detected_entities,
            "master_message": master_analysis.reasoning,
            "system_context": self.get_full_system_context(),
            "conversation_memory": self.get_conversation_memory(),
            "expected_specialist_behavior": "strategic_reasoning"
        }

    def student_to_master(self, strategy_result, execution_result):
        return {
            "specialist": "StudentQueryInterpreter",
            "strategy_used": strategy_result.strategy_name,
            "reasoning_applied": strategy_result.reasoning,
            "actions_executed": strategy_result.actions_used,
            "results_summary": execution_result.summary,
            "ambiguity_detected": strategy_result.ambiguity_level,
            "awaiting_continuation": execution_result.continuation_type,
            "specialist_message": strategy_result.message_to_master,
            "user_response_ready": execution_result.response_text
        }
```

### **FASES DE IMPLEMENTACIÓN:**

#### **FASE 1: Contexto del Sistema (1-2 horas)**
1. Agregar system_capabilities_context al Master Prompt
2. Agregar database_structure_context completo al Student
3. Agregar sql_templates_context al Student
4. Probar que contextos se pasen correctamente

#### **FASE 2: Razonamiento Estratégico (2-3 horas)**
1. Crear prompt de strategic_reasoning para Student
2. Implementar análisis de ambigüedad
3. Implementar planificación de estrategias
4. Probar con casos como "buscar García"

#### **FASE 3: Comunicación Bidireccional (1-2 horas)**
1. Implementar InterPromptCommunication
2. Master recuerda interacciones previas
3. Student reporta estado detallado
4. Probar flujo completo de comunicación

#### **FASE 4: Integración y Pruebas (2-3 horas)**
1. Integrar todos los componentes
2. Probar casos complejos
3. Ajustar razonamiento según resultados
4. Documentar comportamiento final

---

## 🎯 **CASOS DE PRUEBA PARA VALIDAR LA VISIÓN**

### **CASO 1: Ambigüedad Simple**
```
👤 "buscar García"
🧠 Master: consulta_alumnos/busqueda_simple
📊 Student: "García = apellido común → varios resultados → mostrar + preguntar"
💬 Resultado: Lista + "¿Te refieres a alguno en particular?"
```

### **CASO 2: Consulta Específica**
```
👤 "buscar CURP EABF180526HDGSRRA6"
🧠 Master: consulta_alumnos/busqueda_simple
📊 Student: "CURP = único → un resultado → mostrar directo"
💬 Resultado: Datos del alumno específico
```

### **CASO 3: Consulta Compleja**
```
👤 "alumnos de 2do A turno matutino con promedio > 8"
🧠 Master: consulta_alumnos/busqueda_compleja
📊 Student: "Múltiples criterios + promedio JSON → estrategia combinada"
💬 Resultado: Lista filtrada específica
```

### **CASO 4: Continuación Contextual**
```
👤 "buscar García" → [lista de 5]
👤 "constancia para el tercero"
🧠 Master: consulta_alumnos/generar_constancia + contexto previo
📊 Student: "Referencia contextual → usar datos previos → generar documento"
💬 Resultado: Constancia para Pedro García Silva
```

### **CASO 5: Estadística**
```
👤 "promedio general de calificaciones"
🧠 Master: consulta_alumnos/calcular_estadistica
📊 Student: "Cálculo estadístico → usar plantilla JSON_EXTRACT → interpretar resultado"
💬 Resultado: "El promedio general es 8.3 (excelente nivel académico)"
```

---

## 📋 **CRITERIOS DE ÉXITO**

### **✅ RAZONAMIENTO HUMANO:**
- [ ] Student analiza ambigüedades como persona
- [ ] Student explica su razonamiento en logs
- [ ] Student anticipa tipo de resultado esperado
- [ ] Student maneja casos especiales inteligentemente

### **✅ COMUNICACIÓN EFECTIVA:**
- [ ] Master recuerda interacciones previas
- [ ] Student reporta estado detallado al Master
- [ ] Comunicación bidireccional funciona
- [ ] Contexto se mantiene entre consultas

### **✅ FLEXIBILIDAD Y PRECISIÓN:**
- [ ] Sistema maneja consultas imprevistas
- [ ] Acciones se combinan creativamente
- [ ] Plantillas SQL se usan correctamente
- [ ] Resultados son precisos y relevantes

### **✅ EXPERIENCIA DE USUARIO:**
- [ ] Respuestas naturales y contextuales
- [ ] Manejo inteligente de ambigüedades
- [ ] Conversaciones fluidas
- [ ] Usuario siente que habla con personas expertas

---

---

## 🎯 **FILOSOFÍA DE COMUNICACIÓN: "CONFIANZA CON CONTEXTO ESTRATÉGICO"**

### **ENFOQUE HÍBRIDO RECOMENDADO:**
**Master proporciona análisis estratégico PERO Student decide autónomamente**

#### **🏢 ANALOGÍA: DIRECCIÓN ESCOLAR REAL**
```
👨‍💼 Director (Master): "Juan necesita una constancia, parece urgente"
👩‍💼 Secretario (Student): "Entendido, revisaré qué tipo necesita y la generaré"
```

**CARACTERÍSTICAS:**
- **Director da contexto** pero **secretario decide cómo hacerlo**
- **Colaboración** sin **micromanagement**
- **Confianza** con **información útil**

### **MASTER COMO DIRECTOR DE ESCUELA:**

#### **🎯 CONTEXTO ESTRATÉGICO QUE NECESITA:**
```python
master_context = {
    "sistema_escolar": {
        "tipo": "Dirección de Escuela Primaria PROF. MAXIMO GAMIZ FERNANDEZ",
        "estudiantes_total": 211,
        "areas_disponibles": ["Consultas de Alumnos", "Ayuda Técnica"]
    },

    "especialistas_disponibles": {
        "StudentQueryInterpreter": {
            "rol": "Secretario Académico - Especialista en Datos de Alumnos",
            "capacidades": [
                "Búsquedas de alumnos por cualquier criterio",
                "Generación de constancias oficiales",
                "Estadísticas y reportes escolares",
                "Transformación de documentos"
            ],
            "cobertura": "TODO lo relacionado con estudiantes y documentos"
        },
        "HelpInterpreter": {
            "rol": "Especialista en Soporte Técnico",
            "capacidades": ["Explicar sistema", "Ayuda técnica"],
            "cobertura": "Ayuda y explicaciones del sistema"
        }
    },

    "tipos_consultas_escolares": {
        "busquedas": "buscar García, alumnos de 2do A, estudiantes matutinos",
        "estadisticas": "cuántos alumnos hay, promedio general, distribuciones",
        "documentos": "constancia para Juan, certificado de calificaciones",
        "transformaciones": "convertir constancia, cambiar formato",
        "ayuda": "qué puedes hacer, cómo buscar alumnos"
    }
}
```

#### **❌ LO QUE MASTER NO NECESITA SABER:**
- Estructura detallada de base de datos
- Plantillas SQL específicas
- Detalles técnicos de implementación
- Cómo calcular promedios en JSON

### **STUDENT COMO SECRETARIO ACADÉMICO CON RAZONAMIENTO INTELIGENTE:**

#### **🧠 PROCESO DE RAZONAMIENTO ESTRATÉGICO:**
```
PASO 1: ANÁLISIS DE CONSULTA
"¿Qué necesita realmente el usuario?"
- Examinar consulta original
- Identificar entidades y criterios
- Detectar campos especiales (promedio, edad calculada)

PASO 2: ANÁLISIS DE BASE DE DATOS
"¿Dónde encuentro esta información?"
- Revisar estructura real de BD
- Mapear criterios a campos existentes
- Identificar cálculos necesarios (JSON_EXTRACT, fechas)

PASO 3: SELECCIÓN DE ESTRATEGIA
"¿Qué acciones necesito y en qué orden?"
- Evaluar acciones disponibles
- Seleccionar la más apropiada
- Planificar parámetros específicos

PASO 4: EJECUCIÓN INTELIGENTE
"¿Cómo combinar resultados?"
- Ejecutar acción seleccionada
- Aplicar filtros adicionales si es necesario
- Validar resultados obtenidos

PASO 5: COMUNICACIÓN NATURAL
"¿Cómo explicar lo que encontré?"
- Generar respuesta conversacional
- Detectar si se espera continuación
- Proporcionar contexto útil al usuario
```

#### **🎯 CONTEXTO TÉCNICO COMPLETO QUE NECESITA:**
```python
student_context = {
    "base_datos_escolar": {
        "total_alumnos": 211,
        "estructura_real": {
            "alumnos": {
                "campos": ["id", "curp", "nombre", "matricula", "fecha_nacimiento"],
                "ejemplos": {"nombre": "JUAN GARCIA LOPEZ", "curp": "GALJ180526..."}
            },
            "datos_escolares": {
                "campos": ["alumno_id", "grado", "grupo", "turno", "calificaciones"],
                "ejemplos": {"grado": 2, "grupo": "A", "turno": "MATUTINO"}
            }
        },
        "campos_especiales_criticos": {
            "promedio": {
                "existe_directo": False,
                "ubicacion": "JSON en calificaciones",
                "calculo": "JSON_EXTRACT(calificaciones, '$.promedio')",
                "ejemplo": "[{'nombre': 'MATEMATICAS', 'promedio': 8.5}]"
            },
            "edad": {
                "existe_directo": False,
                "calculo": "strftime('%Y', 'now') - strftime('%Y', fecha_nacimiento)",
                "campo_base": "fecha_nacimiento"
            }
        },
        "limitaciones": [
            "Solo consulta, no modifica datos",
            "Promedio requiere cálculo JSON especial",
            "Constancias requieren datos existentes"
        ]
    },

    "acciones_inteligentes": {
        "BUSCAR_UNIVERSAL": {
            "proposito": "Búsqueda flexible con razonamiento automático",
            "capacidades": [
                "Criterios simples y complejos",
                "Cálculos automáticos (promedio, edad)",
                "Combinación inteligente de filtros"
            ],
            "razonamiento": "Analiza consulta → mapea a BD → construye estrategia → ejecuta"
        },
        "CALCULAR_ESTADISTICA": {
            "proposito": "Análisis numéricos con contexto",
            "capacidades": [
                "Promedios generales y por materia",
                "Distribuciones por grado/grupo/turno",
                "Conteos con filtros complejos"
            ],
            "razonamiento": "Identifica tipo de estadística → selecciona método → interpreta resultado"
        },
        "GENERAR_CONSTANCIA_COMPLETA": {
            "proposito": "Documentos oficiales con validación",
            "capacidades": [
                "Verificación de datos existentes",
                "Selección automática de tipo",
                "Generación con contexto completo"
            ],
            "razonamiento": "Identifica alumno → valida datos → selecciona formato → genera PDF"
        }
    },

    "plantillas_universales": {
        "busqueda_universal": {
            "proposito": "Plantilla flexible para cualquier búsqueda",
            "parametros_dinamicos": ["criterios", "orden", "limite"],
            "capacidad": "LLM construye WHERE clause inteligentemente"
        },
        "calculo_promedio": {
            "proposito": "Cálculos con JSON de calificaciones",
            "parametros_dinamicos": ["filtros_base", "tipo_promedio"],
            "capacidad": "JSON_EXTRACT automático con validaciones"
        },
        "estadisticas_agrupadas": {
            "proposito": "Análisis con GROUP BY dinámico",
            "parametros_dinamicos": ["agrupacion", "metricas"],
            "capacidad": "Estadísticas flexibles según consulta"
        }
    },

    "guias_razonamiento_avanzado": {
        "consultas_ambiguas": {
            "García": "apellido común → múltiples resultados → mostrar lista + preguntar especificación",
            "alumnos de 2do": "grado específico → usar filtro directo → mostrar todos del grado",
            "promedio > 8": "campo especial → usar JSON_EXTRACT → calcular dinámicamente"
        },
        "consultas_complejas": {
            "2do A matutino promedio > 8": "múltiples criterios → combinar filtros directos + cálculo JSON",
            "mayores de 10 años": "edad no existe → calcular desde fecha_nacimiento",
            "sin calificaciones": "verificar JSON vacío o NULL"
        },
        "continuaciones_contextuales": {
            "el tercero": "referencia a lista previa → usar conversation_stack",
            "sí": "confirmación → analizar contexto previo",
            "constancia para él": "pronombre → resolver desde contexto"
        }
    }
}
```

### **PROTOCOLO DE COMUNICACIÓN HÍBRIDO:**

#### **MASTER → STUDENT:**
```python
master_to_student = {
    "user_query": "constancia para Juan",
    "strategic_context": {
        "task_type": "document_generation",
        "urgency": "normal",
        "complexity": "standard"
    },
    "master_guidance": "Detecté solicitud de documento oficial",
    "confidence": 0.95
}
```

#### **STUDENT RAZONAMIENTO:**
```python
student_reasoning = """
Recibo análisis del Master: 'document_generation'
Mi análisis independiente: También veo que es constancia
DECISIÓN: Coincidimos, usaré GENERAR_CONSTANCIA_COMPLETA
AUTONOMÍA: Yo decido los detalles técnicos específicos
"""
```

### **VENTAJAS DEL ENFOQUE HÍBRIDO:**

#### **✅ PARA MASTER:**
- **Más inteligente:** Detecta sub-intenciones específicas
- **Mejor contexto:** Sabe exactamente qué tipo de tarea es
- **Sin sobrecarga:** No necesita detalles técnicos
- **Confianza:** Puede delegar con seguridad

#### **✅ PARA STUDENT:**
- **Mejor contexto:** Recibe orientación estratégica útil
- **Autonomía:** Decide cómo ejecutar técnicamente
- **Flexibilidad:** Puede ignorar sugerencias si no aplican
- **Especialización:** Mantiene su expertise técnico

#### **✅ PARA EL SISTEMA:**
- **Colaboración real:** Como personas trabajando juntas
- **Sin micromanagement:** Master no controla detalles
- **Eficiencia:** Menos re-análisis redundante
- **Escalabilidad:** Fácil agregar nuevos especialistas

---

---

## 🚀 **IMPLEMENTACIÓN TÉCNICA DEL RAZONAMIENTO INTELIGENTE**

### **ARQUITECTURA UNIFICADA DEFINITIVA:**

#### **FLUJO DE RAZONAMIENTO STUDENT:**
```python
class StudentQueryInterpreter:
    def interpret(self, context):
        # PASO 1: ANÁLISIS INTELIGENTE DE CONSULTA
        analysis = self._analyze_query_with_reasoning(context.user_message)

        # PASO 2: MAPEO A BASE DE DATOS
        db_mapping = self._map_to_database_structure(analysis)

        # PASO 3: SELECCIÓN DE ESTRATEGIA
        strategy = self._select_optimal_strategy(analysis, db_mapping)

        # PASO 4: EJECUCIÓN INTELIGENTE
        result = self._execute_with_intelligence(strategy)

        # PASO 5: COMUNICACIÓN NATURAL
        response = self._generate_natural_response(result, context)

        return response
```

#### **PROMPTS DE RAZONAMIENTO:**

##### **PROMPT 1: ANÁLISIS INTELIGENTE**
```python
analysis_prompt = f"""
🧠 ANÁLISIS ESTRATÉGICO DE CONSULTA:

CONSULTA: "{user_query}"

MI PROCESO DE RAZONAMIENTO:
1. ¿Qué información específica necesita el usuario?
2. ¿Hay ambigüedades que debo resolver?
3. ¿Qué tipo de resultado espera? (uno/varios/conteo/cálculo)
4. ¿Hay campos especiales involucrados? (promedio, edad calculada)

ESTRUCTURA DE BD DISPONIBLE:
{database_structure_with_examples}

CAMPOS ESPECIALES CRÍTICOS:
- promedio: NO existe directo, está en JSON calificaciones
- edad: NO existe, calcular desde fecha_nacimiento

TAREA: Analiza la consulta y identifica exactamente qué necesitas buscar.
"""
```

##### **PROMPT 2: SELECCIÓN DE ESTRATEGIA**
```python
strategy_prompt = f"""
🎯 SELECCIÓN DE ESTRATEGIA ÓPTIMA:

ANÁLISIS PREVIO: {analysis_result}

ACCIONES DISPONIBLES:
{actions_catalog_with_reasoning}

PLANTILLAS UNIVERSALES:
{universal_templates_catalog}

MI RAZONAMIENTO ESTRATÉGICO:
1. Basándome en mi análisis, ¿qué acción resuelve mejor esta consulta?
2. ¿Necesito plantillas especiales para campos como promedio?
3. ¿Puedo resolver todo en una acción o necesito combinar?
4. ¿Qué parámetros específicos necesito construir?

TAREA: Selecciona la estrategia óptima y construye parámetros específicos.
"""
```

### **PLANTILLAS UNIVERSALES IMPLEMENTADAS:**

#### **1. BÚSQUEDA UNIVERSAL:**
```sql
-- busqueda_universal.sql
SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento,
       de.grado, de.grupo, de.turno, de.ciclo_escolar, de.calificaciones,
       -- Cálculo dinámico de promedio cuando se necesite
       CASE
         WHEN de.calificaciones IS NOT NULL AND de.calificaciones != '[]' THEN
           (SELECT AVG(CAST(json_extract(value, '$.promedio') AS REAL))
            FROM json_each(de.calificaciones)
            WHERE json_extract(value, '$.promedio') IS NOT NULL
            AND json_extract(value, '$.promedio') != 0)
         ELSE NULL
       END as promedio_calculado,
       -- Cálculo dinámico de edad cuando se necesite
       (strftime('%Y', 'now') - strftime('%Y', a.fecha_nacimiento)) as edad_calculada
FROM alumnos a
LEFT JOIN datos_escolares de ON a.id = de.alumno_id
WHERE {criterios_dinamicos}
ORDER BY {orden_dinamico}
LIMIT {limite_dinamico}
```

#### **2. ESTADÍSTICAS UNIVERSALES:**
```sql
-- estadisticas_universales.sql
SELECT {campos_agrupacion},
       COUNT(*) as total,
       AVG(promedio_calculado) as promedio_grupo,
       MIN(promedio_calculado) as promedio_minimo,
       MAX(promedio_calculado) as promedio_maximo
FROM (
    SELECT a.*, de.*,
           CASE
             WHEN de.calificaciones IS NOT NULL AND de.calificaciones != '[]' THEN
               (SELECT AVG(CAST(json_extract(value, '$.promedio') AS REAL))
                FROM json_each(de.calificaciones)
                WHERE json_extract(value, '$.promedio') IS NOT NULL)
             ELSE NULL
           END as promedio_calculado
    FROM alumnos a
    LEFT JOIN datos_escolares de ON a.id = de.alumno_id
    WHERE {criterios_base}
) subquery
GROUP BY {campos_agrupacion}
ORDER BY {orden_estadisticas}
```

### **INTEGRACIÓN CON CÓDIGO EXISTENTE:**

#### **MODIFICACIONES NECESARIAS:**

##### **1. StudentQueryInterpreter - Agregar Razonamiento:**
```python
def _analyze_query_with_reasoning(self, user_query):
    """Análisis inteligente de la consulta del usuario"""
    prompt = self._build_analysis_prompt(user_query)
    response = self.gemini_client.generate_content(prompt)
    return self._parse_analysis_response(response)

def _map_to_database_structure(self, analysis):
    """Mapea análisis a estructura real de BD"""
    mapping = {}
    for criterion in analysis.criteria:
        if criterion.field == "promedio":
            mapping[criterion.field] = {
                "type": "calculated",
                "method": "json_extract",
                "source": "calificaciones"
            }
        elif criterion.field == "edad":
            mapping[criterion.field] = {
                "type": "calculated",
                "method": "date_diff",
                "source": "fecha_nacimiento"
            }
        else:
            mapping[criterion.field] = {
                "type": "direct",
                "table": self._get_table_for_field(criterion.field)
            }
    return mapping
```

##### **2. ActionExecutor - Plantillas Universales:**
```python
def _execute_buscar_universal(self, parametros):
    """Ejecución con plantillas universales"""
    # Usar plantilla universal en lugar de SQL dinámico
    template = self.sql_template_manager.get_universal_template("busqueda_universal")

    # Construir criterios dinámicos basados en mapeo inteligente
    criterios = self._build_dynamic_criteria(parametros)

    # Ejecutar con plantilla universal
    sql_query = template.format(
        criterios_dinamicos=criterios,
        orden_dinamico=parametros.get("orden", "a.nombre"),
        limite_dinamico=parametros.get("limite", "100")
    )

    return self.sql_executor.execute_query(sql_query)
```

### **CASOS DE PRUEBA PARA VALIDAR RAZONAMIENTO:**

#### **CASO 1: Consulta Compleja con Razonamiento**
```
👤 "alumnos de 2do A turno matutino con promedio mayor a 8"

🧠 ANÁLISIS ESPERADO:
- Criterios: grado=2, grupo=A, turno=MATUTINO, promedio>8
- Campo especial detectado: promedio (requiere JSON_EXTRACT)
- Estrategia: BUSCAR_UNIVERSAL con plantilla universal
- Resultado: Lista filtrada con cálculo automático de promedio

📊 RAZONAMIENTO STUDENT:
"Detecto múltiples criterios. Grado, grupo y turno son campos directos.
Promedio es especial - está en JSON calificaciones.
Usaré BUSCAR_UNIVERSAL con plantilla universal que calcula promedio automáticamente."
```

#### **CASO 2: Consulta Ambigua con Razonamiento**
```
👤 "García"

🧠 ANÁLISIS ESPERADO:
- Criterio: nombre LIKE '%García%'
- Ambigüedad detectada: apellido común
- Estrategia: BUSCAR_UNIVERSAL + mostrar lista + preguntar
- Resultado: Lista de todos los García + pregunta de especificación

📊 RAZONAMIENTO STUDENT:
"García es un apellido común. Probablemente habrá múltiples resultados.
Usaré BUSCAR_UNIVERSAL para encontrar todos y luego preguntaré al usuario
cuál específicamente necesita."
```

---

**ESTA VISIÓN ACTUALIZADA REPRESENTA UN SISTEMA DONDE LA IA RAZONA COMO UNA PERSONA EXPERTA, ANALIZANDO CONSULTAS, MAPEANDO A DATOS REALES, Y EJECUTANDO ESTRATEGIAS INTELIGENTES.**

**DOCUMENTO DE REFERENCIA COMPLETO - ACTUALIZADO CON RAZONAMIENTO INTELIGENTE - LISTO PARA IMPLEMENTACIÓN**
