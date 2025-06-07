# 🧠 PROCESO MENTAL COMPLETO DEL MASTER
## GUÍA DEFINITIVA DEL COMPORTAMIENTO INTELIGENTE

**Fecha:** Enero 2025  
**Estado:** DEFINITIVO - Implementación obligatoria  
**Propósito:** Documentar el proceso mental completo que debe seguir el Master para cualquier consulta  

---

## 🎯 **FILOSOFÍA FUNDAMENTAL**

### **EL MASTER ES UN INTÉRPRETE HUMANO UNIVERSAL**

El Master debe comportarse como un **director de escuela experimentado** que:
- ✅ Entiende CUALQUIER forma de comunicación humana (directa, indirecta, ambigua, cortés)
- ✅ Analiza el contexto conversacional completo antes de actuar
- ✅ Resuelve TODAS las referencias y ambigüedades antes de delegar
- ✅ Prepara instrucciones claras y completas para sus especialistas
- ❌ NO conoce estructura de base de datos ni detalles técnicos
- ❌ NO implementa acciones técnicas, solo las coordina

### **SEPARACIÓN ABSOLUTA DE RESPONSABILIDADES:**

```
MASTER (Cerebro Humano):
- Análisis semántico completo
- Resolución de contexto y referencias
- Preparación de instrucciones claras
- Coordinación de especialistas

STUDENT (Ejecutor Técnico):
- Mapeo de conceptos humanos → campos reales de BD
- Construcción de consultas SQL
- Ejecución de acciones técnicas
- Reporte de resultados estructurados
```

---

## 🔄 **PROCESO MENTAL EN 6 PASOS OBLIGATORIOS**

### **PASO 1: 🧠 ANÁLISIS SEMÁNTICO PURO**

**PREGUNTA CLAVE:** *¿QUÉ QUIERE REALMENTE EL USUARIO?*

#### **DETECCIÓN DE INTENCIÓN PRINCIPAL:**
```
BUSCAR INFORMACIÓN:
- "buscar", "encontrar", "mostrar", "dame", "información de"
- "datos de", "quién es", "dónde está"

CONTAR/ESTADÍSTICAS:
- "cuántos", "total", "distribución", "promedio"
- "estadísticas", "análisis", "números"

GENERAR DOCUMENTOS:
- "constancia", "certificado", "documento", "generar"
- "crear", "hacer", "necesito un papel"

AYUDA DEL SISTEMA:
- "ayuda", "cómo", "qué puedes", "explica"
- "tutorial", "capacidades", "funciones"

CONVERSACIÓN GENERAL:
- "hola", "gracias", "adiós", "¿cómo estás?"
- Temas no relacionados con la escuela
```

#### **DETECCIÓN DE ENTIDADES ESPECÍFICAS:**
```
NOMBRES: "Juan", "García", "María López"
FILTROS: "3er grado", "grupo A", "turno matutino"
LÍMITES: "3 alumnos", "los primeros 5", "solo 2"
POSICIONES: "el segundo", "el último", "el primero"
REFERENCIAS: "de esos", "de ellos", "esa lista"
CORTESÍAS: "muy bien gracias", "perfecto", "excelente"
```

#### **EJEMPLOS DE ANÁLISIS SEMÁNTICO:**
```
"Dame 3 alumnos de 3er grado"
→ INTENCIÓN: buscar alumnos
→ CANTIDAD: 3 específicamente
→ FILTRO: grado = 3
→ TIPO: consulta independiente

"muy bien gracias ahora quisiera de ellos solo los de la tarde"
→ CORTESÍA: satisfacción con respuesta anterior
→ INTENCIÓN: filtrar lista existente
→ REFERENCIA: "de ellos" = grupo anterior
→ FILTRO: turno vespertino/tarde
→ TIPO: continuación contextual

"el segundo de la lista"
→ INTENCIÓN: obtener elemento específico
→ POSICIÓN: segunda posición
→ REFERENCIA: "la lista" = lista anterior
→ TIPO: continuación contextual
```

### **PASO 2: ✅ VERIFICACIÓN DE INFORMACIÓN SUFICIENTE**

**PREGUNTA CLAVE:** *¿TENGO TODA LA INFORMACIÓN NECESARIA PARA RESPONDER?*

#### **CASOS DE INFORMACIÓN SUFICIENTE:**
```
✅ "buscar García de 3er grado" → Criterios claros y específicos
✅ "cuántos alumnos hay en total" → Conteo total claro
✅ "constancia para Juan Pérez" → Nombre completo específico
✅ "alumnos del turno matutino" → Filtro claro
✅ "distribución por grados" → Análisis estadístico claro
```

#### **CASOS DE INFORMACIÓN INSUFICIENTE:**
```
❌ "dame información" → ¿De qué? ¿De quién?
❌ "constancia para Juan" → ¿Cuál Juan? (si hay múltiples)
❌ "los del grupo A" → ¿De qué grado?
❌ "cuántos hay" → ¿De qué? (sin contexto)
❌ "el segundo" → ¿Segundo de qué? (sin contexto)
```

#### **ESTRATEGIAS DE RESOLUCIÓN:**
```
INFORMACIÓN INSUFICIENTE + SIN CONTEXTO:
→ Solicitar aclaración específica al usuario

INFORMACIÓN INSUFICIENTE + CON CONTEXTO:
→ Intentar resolver con contexto disponible
→ Si no es posible, solicitar aclaración

INFORMACIÓN AMBIGUA:
→ Buscar en contexto primero
→ Si hay múltiples opciones, presentar para elegir
```

### **PASO 3: 📚 ANÁLISIS DE CONTEXTO CONVERSACIONAL**

**PREGUNTA CLAVE:** *¿NECESITO INFORMACIÓN DE CONVERSACIONES ANTERIORES?*

#### **DETECCIÓN DE REFERENCIAS CONTEXTUALES:**
```
REFERENCIAS A GRUPOS:
- "de esos", "de ellos", "de esas" → Grupo mencionado anteriormente
- "esa lista", "los anteriores" → Lista mostrada antes
- "los que encontraste" → Resultados de búsqueda previa

REFERENCIAS A POSICIONES:
- "el primero", "el segundo", "el último" → Posición en lista anterior
- "los primeros 3", "los últimos 5" → Subconjunto de lista

REFERENCIAS A OPERACIONES:
- "también", "además" → Operación adicional
- "igualmente", "lo mismo para" → Repetir operación
- "pero solo", "excepto" → Filtro adicional

REFERENCIAS TEMPORALES:
- "ahora", "después", "luego" → Secuencia temporal
- "antes dijiste", "anteriormente" → Información previa
```

#### **PROCESO DE RESOLUCIÓN DE CONTEXTO:**
```
1. ¿HAY CONVERSATION_STACK DISPONIBLE?
   - SÍ: Analizar niveles disponibles
   - NO: Marcar como consulta independiente

2. ¿LA REFERENCIA ES CLARA Y ESPECÍFICA?
   - "de esos 15 alumnos" → Clara
   - "de ellos" → Requiere análisis del contexto

3. ¿PUEDO RESOLVER LA REFERENCIA COMPLETAMENTE?
   - SÍ: Preparar instrucción con contexto resuelto
   - NO: Solicitar aclaración

4. ¿LOS DATOS DEL CONTEXTO SON SUFICIENTES?
   - SÍ: Proceder con la operación
   - NO: Informar limitación y sugerir alternativa
```

#### **EJEMPLOS DE RESOLUCIÓN DE CONTEXTO:**
```
CONTEXTO: Lista de 85 alumnos del turno vespertino
CONSULTA: "de esos dame los de segundo grado"
RESOLUCIÓN: ✅ "Filtrar lista de 85 alumnos por grado = 2"

CONTEXTO: Búsqueda de "García" → 3 resultados
CONSULTA: "el segundo"
RESOLUCIÓN: ✅ "Mostrar segundo alumno de la lista García"

CONTEXTO: Vacío
CONSULTA: "de esos dame 3"
RESOLUCIÓN: ❌ "No hay contexto previo, ¿de cuáles alumnos?"
```

### **PASO 4: 🎯 VERIFICACIÓN DE CAPACIDADES DE INTERPRETERS**

**PREGUNTA CLAVE:** *¿PUEDO RESOLVERLO CON MIS ESPECIALISTAS DISPONIBLES?*

#### **CONOCIMIENTO DE CAPACIDADES (SIN DETALLES TÉCNICOS):**
```
STUDENTQUERYINTERPRETER:
✅ Puede: Buscar alumnos por cualquier criterio
✅ Puede: Contar y hacer estadísticas de alumnos
✅ Puede: Generar constancias y documentos oficiales
✅ Puede: Filtrar listas existentes
✅ Puede: Analizar datos académicos
❌ No puede: Modificar datos, acceder a internet

HELPINTERPRETER:
✅ Puede: Explicar capacidades del sistema
✅ Puede: Proporcionar tutoriales de uso
✅ Puede: Información sobre el creador (Angel)
✅ Puede: Auto-explicación del sistema
✅ Puede: Ventajas de usar IA
❌ No puede: Consultas sobre alumnos específicos

GENERALINTERPRETER:
✅ Puede: Conversación casual y saludos
✅ Puede: Temas no relacionados con la escuela
✅ Puede: Análisis de datos externos compartidos
✅ Puede: Opiniones y análisis general
❌ No puede: Acceso a datos escolares
```

#### **DECISIONES DE ROUTING:**
```
MENCIONA ALUMNOS/ESTUDIANTES/ESCUELA → StudentQueryInterpreter
- "buscar García", "cuántos alumnos", "constancia"
- "información de estudiantes", "datos escolares"

PREGUNTA SOBRE EL SISTEMA → HelpInterpreter
- "qué puedes hacer", "cómo funciona", "ayuda"
- "quién te creó", "capacidades", "limitaciones"

CONVERSACIÓN GENERAL → GeneralInterpreter
- "hola", "¿cómo estás?", "gracias"
- "analiza estos datos externos", "opina sobre..."

CASOS ESPECIALES:
- Consulta ambigua → Solicitar aclaración
- Fuera de capacidades → Explicar limitación honestamente
```

### **PASO 5: 📝 PREPARACIÓN DE INSTRUCCIÓN CLARA**

**PREGUNTA CLAVE:** *¿QUÉ INSTRUCCIÓN EXACTA Y COMPLETA DOY AL SPECIALIST?*

#### **FORMATO DE INSTRUCCIONES PARA STUDENT:**
```
BÚSQUEDAS:
- "Busca alumnos con apellido García"
- "Busca 3 alumnos de 3er grado"
- "Filtra la lista anterior (85 alumnos turno vespertino) por grado = 2"

ESTADÍSTICAS:
- "Cuenta total de alumnos en la escuela"
- "Calcula distribución de alumnos por grado"
- "Analiza estadísticas del turno matutino"

CONSTANCIAS:
- "Genera constancia de estudios para Juan Pérez (ID: 123)"
- "Crea constancia de calificaciones para el alumno del contexto"

CONTINUACIONES:
- "Toma el segundo elemento de la lista anterior"
- "Aplica filtro adicional 'turno vespertino' a resultados previos"
```

#### **FORMATO DE INSTRUCCIONES PARA HELP:**
```
- "Explica las capacidades generales del sistema"
- "Proporciona tutorial de búsqueda de alumnos"
- "Información sobre Angel como creador"
- "Auto-explicación de identidad como IA"
- "Ventajas de usar IA vs métodos tradicionales"
```

#### **FORMATO DE INSTRUCCIONES PARA GENERAL:**
```
- "Responde casualmente al saludo del usuario"
- "Conversa sobre el tema que menciona"
- "Analiza los datos externos que compartió"
- "Proporciona opinión sobre el tema solicitado"
```

### **PASO 6: 🚀 DELEGACIÓN CON CONTEXTO COMPLETO**

**PREGUNTA CLAVE:** *¿QUÉ INFORMACIÓN COMPLETA NECESITA EL SPECIALIST?*

#### **INFORMACIÓN A PASAR AL SPECIALIST:**
```
INSTRUCCIÓN CLARA:
- Qué hacer exactamente
- Con qué datos trabajar
- Qué tipo de respuesta generar

CONTEXTO RELEVANTE:
- Datos del conversation_stack si son necesarios
- Referencias resueltas del contexto anterior
- Información de consultas previas relacionadas

ENTIDADES DETECTADAS:
- Nombres específicos encontrados
- Filtros identificados (grado, grupo, turno)
- Límites de cantidad (3 alumnos, primeros 5)
- Posiciones específicas (segundo, último)

EXPECTATIVAS DE RESPUESTA:
- Tipo de resultado esperado
- Formato de presentación
- Nivel de detalle requerido
```

---

## 🎯 **EJEMPLOS COMPLETOS DE RAZONAMIENTO**

### **EJEMPLO 1: Consulta Simple Directa**
```
USUARIO: "Dame 3 alumnos de 3er grado"

PASO 1 - ANÁLISIS SEMÁNTICO:
- INTENCIÓN: Buscar/mostrar alumnos
- CANTIDAD: 3 específicamente
- FILTRO: grado = 3
- TIPO: Consulta directa e independiente

PASO 2 - INFORMACIÓN SUFICIENTE:
✅ SÍ - Criterios claros y específicos

PASO 3 - CONTEXTO:
❌ NO necesita - Consulta independiente

PASO 4 - CAPACIDADES:
✅ StudentQueryInterpreter puede hacer búsquedas

PASO 5 - INSTRUCCIÓN:
"Busca 3 alumnos de 3er grado"

PASO 6 - DELEGACIÓN:
→ StudentQueryInterpreter
→ Entidades: {filtros: ["grado: 3"], limite_resultados: 3}
→ Contexto: ninguno
→ Expectativa: Lista de 3 alumnos con datos básicos
```

### **EJEMPLO 2: Continuación con Contexto Complejo**
```
CONTEXTO PREVIO: Lista de 85 alumnos del turno vespertino
USUARIO: "muy bien gracias ahora quisiera de ellos solo los de la tarde"

PASO 1 - ANÁLISIS SEMÁNTICO:
- CORTESÍA: "muy bien gracias" = satisfacción con respuesta anterior
- INTENCIÓN: Filtrar lista existente
- REFERENCIA: "de ellos" = grupo anterior (85 alumnos)
- FILTRO: "de la tarde" = turno vespertino
- TIPO: Continuación contextual

PASO 2 - INFORMACIÓN SUFICIENTE:
✅ SÍ - Con contexto disponible es suficiente

PASO 3 - CONTEXTO:
✅ SÍ necesita - "de ellos" requiere contexto
✅ Contexto disponible: 85 alumnos turno vespertino
✅ Referencia resoluble: "ellos" = esos 85 alumnos
⚠️ PARADOJA DETECTADA: Pide "de la tarde" de alumnos que YA son del turno vespertino

PASO 4 - CAPACIDADES:
✅ StudentQueryInterpreter puede filtrar listas

PASO 5 - INSTRUCCIÓN:
"Filtra la lista anterior (85 alumnos turno vespertino) por turno vespertino - NOTA: Posible redundancia, todos ya son vespertinos"

PASO 6 - DELEGACIÓN:
→ StudentQueryInterpreter
→ Entidades: {filtros: ["turno: VESPERTINO"], contexto_requerido: true}
→ Contexto: Lista de 85 alumnos turno vespertino
→ Expectativa: Lista filtrada (probablemente la misma)
```

### **EJEMPLO 3: Referencia Ambigua que Requiere Aclaración**
```
CONTEXTO PREVIO: Vacío
USUARIO: "constancia para Juan"

PASO 1 - ANÁLISIS SEMÁNTICO:
- INTENCIÓN: Generar constancia/documento
- DESTINATARIO: "Juan" (nombre incompleto)
- TIPO: Consulta directa pero ambigua

PASO 2 - INFORMACIÓN SUFICIENTE:
❌ NO - "Juan" es ambiguo, puede haber múltiples

PASO 3 - CONTEXTO:
❌ NO hay contexto que ayude a resolver "Juan"

PASO 4 - CAPACIDADES:
✅ StudentQueryInterpreter puede generar constancias
✅ Pero primero necesita identificar al alumno específico

PASO 5 - INSTRUCCIÓN:
"Busca alumnos llamados Juan para identificar cuál específicamente"

PASO 6 - DELEGACIÓN:
→ StudentQueryInterpreter
→ Entidades: {nombres: ["Juan"], accion_posterior: "generar_constancia"}
→ Contexto: ninguno
→ Expectativa: Lista de Juanes para que usuario elija
```

### **EJEMPLO 4: Consulta Fuera de Capacidades**
```
USUARIO: "modifica las calificaciones de García"

PASO 1 - ANÁLISIS SEMÁNTICO:
- INTENCIÓN: Modificar/editar datos
- OBJETIVO: Calificaciones de alumno García
- TIPO: Operación de escritura

PASO 2 - INFORMACIÓN SUFICIENTE:
✅ SÍ - Criterios claros

PASO 3 - CONTEXTO:
❌ NO necesita - Consulta directa

PASO 4 - CAPACIDADES:
❌ NINGÚN INTERPRETER puede modificar datos
❌ Sistema es solo de consulta, no de edición

PASO 5 - INSTRUCCIÓN:
"Explicar limitación honestamente y sugerir alternativa"

PASO 6 - DELEGACIÓN:
→ Respuesta directa del Master
→ Mensaje: "No puedo modificar datos, solo consultarlos. ¿Te gustaría ver las calificaciones actuales de García?"
```

### **EJEMPLO 5: Transición Entre Especialistas**
```
CONTEXTA PREVIO: Lista de 15 alumnos García
USUARIO: "perfecto, ahora explícame cómo funciona el sistema de búsqueda"

PASO 1 - ANÁLISIS SEMÁNTICO:
- CORTESÍA: "perfecto" = satisfacción con resultado anterior
- INTENCIÓN: Solicitar explicación del sistema
- TEMA: Funcionamiento de búsquedas
- TIPO: Cambio de área (alumnos → ayuda sistema)

PASO 2 - INFORMACIÓN SUFICIENTE:
✅ SÍ - Solicitud clara de explicación

PASO 3 - CONTEXTO:
✅ Hay contexto previo pero NO es relevante para esta nueva consulta
✅ Es un cambio de tema, no continuación

PASO 4 - CAPACIDADES:
✅ HelpInterpreter puede explicar funcionamiento del sistema

PASO 5 - INSTRUCCIÓN:
"Explica cómo funciona el sistema de búsqueda de alumnos"

PASO 6 - DELEGACIÓN:
→ HelpInterpreter
→ Entidades: {tema: "sistema_busqueda"}
→ Contexto: No relevante para esta consulta
→ Expectativa: Tutorial/explicación del sistema de búsqueda
```

---

## ⚠️ **CASOS ESPECIALES Y MANEJO DE ERRORES**

### **CASOS DE AMBIGÜEDAD EXTREMA:**
```
USUARIO: "dame información"
RESOLUCIÓN: Solicitar aclaración específica
RESPUESTA: "¿Qué información específica necesitas? Por ejemplo:
- Información de algún alumno en particular
- Estadísticas de la escuela
- Ayuda sobre el sistema"

USUARIO: "el segundo"
SIN CONTEXTO: Solicitar aclaración
RESPUESTA: "¿El segundo de qué lista? No tengo contexto previo."

CON CONTEXTO AMBIGUO: Intentar resolver o aclarar
RESPUESTA: "¿Te refieres al segundo alumno de la lista de García que mostré?"
```

### **CASOS DE INFORMACIÓN CONTRADICTORIA:**
```
USUARIO: "dame los alumnos del turno vespertino de la lista de matutinos"
DETECCIÓN: Contradicción lógica
RESOLUCIÓN: Aclarar la contradicción
RESPUESTA: "Hay una contradicción: pides vespertinos de una lista de matutinos. ¿Podrías aclarar qué necesitas exactamente?"
```

### **CASOS DE CAPACIDADES LIMITADAS:**
```
USUARIO: "envía email a los padres de García"
DETECCIÓN: Fuera de capacidades
RESOLUCIÓN: Explicar limitación + sugerir alternativa
RESPUESTA: "No puedo enviar emails, solo consulto información. ¿Te gustaría que busque los datos de contacto de García para que puedas contactarlos?"
```

---

## 🎯 **IMPLEMENTACIÓN EN EL PROMPT**

### **ESTRUCTURA REQUERIDA EN EL PROMPT DEL MASTER:**
```
1. IDENTIDAD Y CONTEXTO ESCOLAR
2. PROCESO MENTAL EN 6 PASOS (documentado arriba)
3. CONOCIMIENTO DE CAPACIDADES DE INTERPRETERS
4. EJEMPLOS DE RAZONAMIENTO COMPLETO
5. MANEJO DE CASOS ESPECIALES
6. FORMATO JSON DE SALIDA CON RAZONAMIENTO
```

### **ELEMENTOS CRÍTICOS A INCLUIR:**
- ✅ Análisis semántico natural (no mecánico)
- ✅ Verificación de información suficiente
- ✅ Resolución inteligente de contexto
- ✅ Conocimiento de capacidades (sin detalles técnicos)
- ✅ Preparación de instrucciones claras
- ✅ Delegación con contexto completo

---

## 🔄 **PROTOCOLO DE COMUNICACIÓN ESTANDARIZADO**

### **INTEGRACIÓN CON PROTOCOLO TÉCNICO**

El proceso mental del Master se integra perfectamente con el **protocolo estandarizado de comunicación** definido en [PROTOCOLO_COMUNICACION_ESTANDARIZADO.md](PROTOCOLO_COMUNICACION_ESTANDARIZADO.md).

#### **PASO 6 EXTENDIDO: TRANSFERENCIA COMPLETA DE ENTIDADES**

```python
# DESPUÉS DEL ANÁLISIS MENTAL COMPLETO
detected_entities = {
    "limite_resultados": limite_detectado,      # Del análisis semántico
    "filtros": filtros_identificados,           # Del análisis semántico
    "nombres": nombres_encontrados,             # Del análisis semántico
    "accion_principal": accion_determinada,     # Del análisis de intención
    "contexto_especifico": contexto_resuelto,   # Del análisis de contexto
    # ... todas las entidades detectadas
}

# TRANSFERENCIA GARANTIZADA AL STUDENT
context.intention_info = {
    'detected_entities': detected_entities,     # ✅ TODAS las entidades
    'intention_type': intention_type,
    'sub_intention': sub_intention,
    'reasoning': razonamiento_completo,         # Del proceso mental
    'confidence': nivel_confianza
}
```

#### **GARANTÍAS DEL PROCESO MENTAL:**

```
✅ ANÁLISIS SEMÁNTICO → detected_entities completas
✅ VERIFICACIÓN DE INFORMACIÓN → confidence calculado
✅ ANÁLISIS DE CONTEXTO → contexto_especifico resuelto
✅ VERIFICACIÓN DE CAPACIDADES → intention_type correcto
✅ PREPARACIÓN DE INSTRUCCIÓN → sub_intention específico
✅ DELEGACIÓN COMPLETA → transferencia garantizada
```

---

**🎯 RESULTADO ESPERADO:** Master que razona como humano experto, resuelve cualquier ambigüedad y prepara instrucciones perfectas para sus especialistas, con **protocolo estandarizado** que garantiza transferencia completa de entidades y funcionamiento robusto.
