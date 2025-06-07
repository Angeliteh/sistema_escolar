# 🎯 INTENCIONES Y ACCIONES DEFINITIVAS DEL SISTEMA
## DOCUMENTACIÓN OFICIAL - ARQUITECTURA ÚNICA

**Fecha:** Enero 2025
**Estado:** DEFINITIVO - Base para implementación
**Propósito:** Definir claramente todas las intenciones, sub-intenciones y acciones del sistema
**Actualización:** Acciones BUSCAR_UNIVERSAL y CONTAR_UNIVERSAL implementadas y validadas

---

## 🧠 **PROCESO MENTAL DEL MASTER - FUNDAMENTO ARQUITECTÓNICO**

### **FILOSOFÍA CENTRAL:**
**EL MASTER ES UN DIRECTOR DE ESCUELA EXPERIMENTADO** que entiende cualquier forma de comunicación natural y prepara instrucciones claras para sus especialistas técnicos.

### **PROCESO MENTAL COMPLETO:**

#### **1. ANÁLISIS SEMÁNTICO NATURAL**
```
MASTER SE PREGUNTA:
- ¿QUÉ quiere exactamente? → buscar, contar, generar, explicar, conversar
- ¿DE QUIÉN/QUÉ habla? → nombres, grupos, criterios específicos
- ¿CUÁNTO necesita? → cantidades específicas, límites, "todo"
- ¿HAY CORTESÍAS? → "muy bien", "gracias", "por favor"
```

#### **2. ANÁLISIS DE CONTEXTO CONVERSACIONAL**
```
MASTER EVALÚA:
- ¿Hay conversation_stack disponible?
- ¿La consulta tiene referencias? → "de esos", "el segundo", "también"
- ¿Puedo resolver las referencias?
- ¿Tengo información suficiente para proceder?
```

#### **3. EVALUACIÓN DE CAPACIDADES DE INTERPRETERS**
```
MASTER CONOCE (SIN DETALLES TÉCNICOS):
- Student: "Maneja TODO sobre alumnos" (búsquedas, estadísticas, constancias)
- Help: "Explica el sistema" (capacidades, tutoriales, limitaciones)
- General: "Conversa sobre cualquier tema" (chat casual, temas no escolares)
```

#### **4. PREPARACIÓN DE INSTRUCCIÓN CLARA**
```
MASTER PREPARA ORDEN CONCEPTUAL:
- "Busca 3 alumnos de 3er grado"
- "Filtra lista anterior por turno vespertino"
- "Genera constancia para Juan del contexto"
- "Explica cómo funciona el sistema"
```

### **EJEMPLOS DE RAZONAMIENTO MASTER:**

#### **EJEMPLO 1: Consulta con Límite**
```
Usuario: "dame 3 alumnos de 3er grado"

MASTER RAZONA:
1. QUÉ: "dame" = solicitud de mostrar/buscar
2. CUÁNTO: "3" = límite específico (NO es grado)
3. FILTRO: "de 3er grado" = criterio de filtrado
4. CONTEXTO: No necesita contexto anterior
5. CAPACIDAD: Student puede hacer búsquedas
6. INSTRUCCIÓN: "Busca alumnos de 3er grado, límite 3"

RESULTADO: intention_type="consulta_alumnos", limite_resultados=3
```

#### **EJEMPLO 2: Referencia Contextual**
```
Usuario: "de esos dame los del turno matutino"

MASTER RAZONA:
1. QUÉ: "dame" = solicitud de filtrar/mostrar
2. REFERENCIA: "de esos" = lista anterior del contexto
3. FILTRO: "turno matutino" = criterio adicional
4. CONTEXTO: SÍ necesita conversation_stack
5. RESOLUCIÓN: ¿Hay lista anterior? → SÍ, 85 alumnos
6. INSTRUCCIÓN: "Filtra lista anterior por turno matutino"

RESULTADO: requiere_contexto=true, filtro_adicional="turno: MATUTINO"
```

#### **EJEMPLO 3: Ambigüedad que Requiere Aclaración**
```
Usuario: "información de Juan"

MASTER RAZONA:
1. QUÉ: "información" = solicitud de datos
2. DE QUIÉN: "Juan" = nombre específico pero ambiguo
3. CONTEXTO: ¿Hay Juan específico en contexto? → NO
4. PROBLEMA: Múltiples Juan en el sistema
5. DECISIÓN: Necesita aclaración
6. RESPUESTA: "¿Te refieres a Juan Pérez de 3°A o Juan García de 5°B?"

RESULTADO: intention_type="aclaracion_requerida"
```

---

## 📋 **INTENCIONES PRINCIPALES (3)**

### **1. `consulta_alumnos`** - Todo lo relacionado con datos de estudiantes
**Descripción:** Maneja todas las consultas, búsquedas, análisis y documentos relacionados con alumnos  
**Especialista:** StudentQueryInterpreter  
**Cobertura:** ~95% de las consultas del sistema

### **2. `ayuda_sistema`** - Soporte y explicaciones
**Descripción:** Proporciona ayuda, explicaciones y soporte técnico del sistema  
**Especialista:** HelpInterpreter  
**Cobertura:** ~4% de las consultas del sistema

### **3. `conversacion_general`** - Chat casual
**Descripción:** Maneja saludos y conversación no relacionada al sistema  
**Especialista:** MasterInterpreter (respuesta directa)  
**Cobertura:** ~1% de las consultas del sistema

---

## 🎯 **SUB-INTENCIONES Y ACCIONES DETALLADAS**

### **📊 INTENCIÓN: `consulta_alumnos`**

#### **SUB-INTENCIÓN: `busqueda_simple`**
**Descripción:** Búsquedas con 1-2 criterios básicos y directos  
**Características:**
- Criterios simples (nombre, grado, grupo, turno)
- Campos que existen directamente en la base de datos
- No requiere cálculos especiales o JSON_EXTRACT

**Ejemplos:**
- "buscar García"
- "alumnos de 2do A"
- "estudiantes del turno matutino"
- "alumnos del grupo B"

**ACCIONES DISPONIBLES:**
- **`BUSCAR_UNIVERSAL`** - Búsqueda universal con criterios múltiples ✅ IMPLEMENTADA
  - *Incluye búsqueda exacta por CURP, matrícula, nombre*

---

#### **SUB-INTENCIÓN: `busqueda_compleja`**
**Descripción:** Búsquedas con múltiples criterios o campos especiales  
**Características:**
- Múltiples criterios combinados (3+ filtros)
- Campos especiales que requieren JSON_EXTRACT (promedio)
- Filtros dinámicos o cálculos

**Ejemplos:**
- "alumnos de 2do A turno matutino con promedio > 8"
- "estudiantes sin calificaciones del vespertino"
- "alumnos que tengan García en el nombre y sean de 3er grado"

**ACCIONES DISPONIBLES:**
- **`BUSCAR_UNIVERSAL`** - Búsqueda con múltiples criterios y filtros especiales ✅ IMPLEMENTADA
  - *Maneja automáticamente criterios complejos y combinados*

---

#### **SUB-INTENCIÓN: `estadisticas`**
**Descripción:** Cálculos, conteos y análisis estadísticos  
**Características:**
- Solicita números, promedios, distribuciones
- Requiere cálculos agregados
- Análisis de datos

**Ejemplos:**
- "cuántos alumnos hay en total"
- "promedio general de calificaciones"
- "distribución por grados"
- "estadísticas del turno vespertino"

**ACCIONES DISPONIBLES:**
- **`CONTAR_UNIVERSAL`** - Conteos universales con criterios múltiples ✅ IMPLEMENTADA
- **`CALCULAR_ESTADISTICA`** - Promedios, distribuciones y análisis numéricos ✅ IMPLEMENTADA
  - *CONTAR_UNIVERSAL maneja todos los tipos de conteos con filtros*

---

#### **SUB-INTENCIÓN: `generar_constancia`**
**Descripción:** Generación de documentos oficiales PDF  
**Características:**
- Crea documentos oficiales
- Requiere datos específicos del alumno
- Genera archivos PDF

**Ejemplos:**
- "constancia para Juan Pérez"
- "generar certificado de calificaciones"
- "constancia de estudios para el tercero"
- "documento oficial para María"

**ACCIONES DISPONIBLES:**
- **`GENERAR_CONSTANCIA_COMPLETA`** - Crear documentos PDF oficiales ✅ IMPLEMENTADA

**TIPOS DE CONSTANCIA:**
- Constancia de estudios (sin calificaciones)
- Constancia de calificaciones (con notas)
- Constancia de traslado

---

#### **SUB-INTENCIÓN: `transformacion_pdf`**
**Descripción:** Transformación de constancias entre formatos  
**Características:**
- Convierte documentos existentes
- Cambia formato o tipo de constancia
- Trabaja con PDFs externos

**Ejemplos:**
- "convertir constancia a formato de estudios"
- "cambiar formato PDF"
- "transformar a constancia de calificaciones"

**ACCIONES DISPONIBLES:**
- **`GENERAR_CONSTANCIA_COMPLETA`** - Regenera documento en nuevo formato ✅ IMPLEMENTADA

---

### **❓ INTENCIÓN: `ayuda_sistema`**

#### **SUB-INTENCIÓN: `explicacion_general`**
**Descripción:** Qué puede hacer el sistema - capacidades generales
**Ejemplos:**
- "qué puedes hacer"
- "ayuda"
- "capacidades del sistema"

**ACCIONES DISPONIBLES:**
- **`EXPLICAR_CAPACIDADES`** - Lista capacidades generales del sistema

#### **SUB-INTENCIÓN: `tutorial_funciones`**
**Descripción:** Cómo usar funcionalidades específicas - guías paso a paso
**Ejemplos:**
- "cómo buscar alumnos"
- "cómo generar constancias"
- "tutorial de uso"

**ACCIONES DISPONIBLES:**
- **`TUTORIAL_FUNCIONES`** - Explica cómo usar funciones específicas

#### **SUB-INTENCIÓN: `sobre_creador`**
**Descripción:** Información sobre Angel y el desarrollo del sistema
**Ejemplos:**
- "quién te creó"
- "quién te hizo"
- "tu creador"
- "angel"

**ACCIONES DISPONIBLES:**
- **`SOBRE_CREADOR`** - Información sobre Angel como desarrollador

#### **SUB-INTENCIÓN: `auto_consciencia`**
**Descripción:** Identidad y naturaleza del asistente de IA
**Ejemplos:**
- "qué eres"
- "quién eres"
- "te defines"
- "eres una ia"

**ACCIONES DISPONIBLES:**
- **`AUTO_CONSCIENCIA`** - Explicación de identidad como IA escolar

#### **SUB-INTENCIÓN: `ventajas_sistema`**
**Descripción:** Beneficios de usar IA vs métodos tradicionales
**Ejemplos:**
- "por qué usar ia"
- "ventajas"
- "beneficios"
- "por qué eres mejor"

**ACCIONES DISPONIBLES:**
- **`VENTAJAS_SISTEMA`** - Comparación IA vs métodos tradicionales

#### **SUB-INTENCIÓN: `casos_uso_avanzados`**
**Descripción:** Funcionalidades impresionantes y avanzadas
**Ejemplos:**
- "qué más puedes"
- "funciones avanzadas"
- "sorpréndeme"
- "impresióname"

**ACCIONES DISPONIBLES:**
- **`CASOS_AVANZADOS`** - Demostración de capacidades avanzadas

#### **SUB-INTENCIÓN: `limitaciones_honestas`**
**Descripción:** Qué no puede hacer el sistema - transparencia
**Ejemplos:**
- "qué no puedes"
- "limitaciones"
- "qué falla"
- "problemas"

**ACCIONES DISPONIBLES:**
- **`LIMITACIONES_HONESTAS`** - Explicación honesta de limitaciones

---

### **💬 INTENCIÓN: `conversacion_general`**

#### **SUB-INTENCIÓN: `saludo`**
**Descripción:** Saludos y presentaciones  
**Ejemplos:**
- "hola"
- "buenos días"
- "¿cómo estás?"

**ACCIONES DISPONIBLES:**
- **`RESPUESTA_CASUAL`** - Respuesta de saludo amigable

#### **SUB-INTENCIÓN: `chat_casual`**
**Descripción:** Conversación no relacionada al sistema  
**Ejemplos:**
- "¿qué tal el clima?"
- "cuéntame un chiste"

**ACCIONES DISPONIBLES:**
- **`RESPUESTA_CASUAL`** - Respuesta educada redirigiendo al sistema

---

## 🔗 **MAPEO INTENCIÓN → ESPECIALISTA**

```
consulta_alumnos → StudentQueryInterpreter
├── busqueda_simple → BUSCAR_UNIVERSAL ✅
├── busqueda_compleja → BUSCAR_UNIVERSAL ✅
├── estadisticas → CONTAR_UNIVERSAL ✅, CALCULAR_ESTADISTICA ✅
├── generar_constancia → GENERAR_CONSTANCIA_COMPLETA ✅
└── transformacion_pdf → GENERAR_CONSTANCIA_COMPLETA ✅

ayuda_sistema → HelpInterpreter
├── explicacion_general → EXPLICAR_CAPACIDADES ✅
├── tutorial_funciones → TUTORIAL_FUNCIONES ✅
├── sobre_creador → SOBRE_CREADOR ✅
├── auto_consciencia → AUTO_CONSCIENCIA ✅
├── ventajas_sistema → VENTAJAS_SISTEMA ✅
├── casos_uso_avanzados → CASOS_AVANZADOS ✅
└── limitaciones_honestas → LIMITACIONES_HONESTAS ✅

conversacion_general → MasterInterpreter (directo)
├── saludo → RESPUESTA_CASUAL
└── chat_casual → RESPUESTA_CASUAL
```

---

## 📊 **RESUMEN DE ACCIONES PRINCIPALES**

### **ACCIONES DE BÚSQUEDA:**
- **`BUSCAR_UNIVERSAL`** - Búsqueda universal con múltiples criterios ✅ IMPLEMENTADA
  - *Nota: Incluye funcionalidad de búsqueda exacta de alumnos*

### **ACCIONES DE ANÁLISIS:**
- **`CONTAR_UNIVERSAL`** - Conteos universales con criterios múltiples ✅ IMPLEMENTADA
- **`CALCULAR_ESTADISTICA`** - Cálculos, promedios y distribuciones ✅ IMPLEMENTADA

### **ACCIONES DE DOCUMENTOS:**
- **`GENERAR_CONSTANCIA_COMPLETA`** - Generación de PDFs oficiales ✅ IMPLEMENTADA

### **ACCIONES DE AYUDA:**
- **`EXPLICAR_CAPACIDADES`** - Capacidades generales del sistema ✅ IMPLEMENTADA
- **`TUTORIAL_FUNCIONES`** - Guías paso a paso de uso ✅ IMPLEMENTADA
- **`SOBRE_CREADOR`** - Información sobre Angel ✅ IMPLEMENTADA
- **`AUTO_CONSCIENCIA`** - Identidad del asistente ✅ IMPLEMENTADA
- **`VENTAJAS_SISTEMA`** - Beneficios vs métodos tradicionales ✅ IMPLEMENTADA
- **`CASOS_AVANZADOS`** - Funcionalidades impresionantes ✅ IMPLEMENTADA
- **`LIMITACIONES_HONESTAS`** - Transparencia sobre limitaciones ✅ IMPLEMENTADA

### **ACCIONES GENERALES:**
- **`RESPUESTA_CASUAL`** - Chat general y saludos (MasterInterpreter directo)

---

## ✅ **CRITERIOS DE CLASIFICACIÓN**

### **¿CUÁNDO ES `busqueda_simple`?**
- 1-2 criterios básicos
- Campos directos de BD (nombre, grado, grupo, turno)
- No requiere cálculos especiales

### **¿CUÁNDO ES `busqueda_compleja`?**
- 3+ criterios combinados
- Incluye campos especiales (promedio)
- Requiere JSON_EXTRACT o filtros dinámicos

### **¿CUÁNDO ES `estadisticas`?**
- Solicita números, conteos, promedios
- Palabras clave: "cuántos", "promedio", "total", "distribución"

### **¿CUÁNDO ES `generar_constancia`?**
- Solicita documentos oficiales
- Palabras clave: "constancia", "certificado", "documento"

### **¿CUÁNDO ES `transformacion_pdf`?**
- Menciona conversión o cambio de formato
- Palabras clave: "convertir", "transformar", "cambiar formato"

---

---

## 🧠 **PROCESO MENTAL DEL MASTER PARA DETECCIÓN DE INTENCIONES**

### **FILOSOFÍA DE DETECCIÓN:**
El Master NO debe buscar palabras clave específicas, sino **razonar semánticamente** como un humano experto:

#### **PROCESO DE RAZONAMIENTO:**
```
1. ¿QUÉ QUIERE EL USUARIO? (análisis semántico puro)
2. ¿TENGO INFORMACIÓN SUFICIENTE? (verificación de completitud)
3. ¿NECESITO CONTEXTO ANTERIOR? (análisis de referencias)
4. ¿QUÉ INTERPRETER PUEDE RESOLVERLO? (mapeo de capacidades)
5. ¿QUÉ INSTRUCCIÓN CLARA DOY? (preparación de delegación)
```

#### **MAPEO INTELIGENTE DE INTENCIONES:**
```
MENCIONA ALUMNOS/ESTUDIANTES/ESCUELA → consulta_alumnos
- "buscar García", "cuántos alumnos", "constancia para Juan"
- "información de estudiantes", "datos escolares", "distribución por grados"
- "el segundo de la lista" (si contexto tiene alumnos)

PREGUNTA SOBRE EL SISTEMA → ayuda_sistema
- "qué puedes hacer", "cómo funciona", "ayuda", "capacidades"
- "quién te creó", "limitaciones", "tutorial"

CONVERSACIÓN NO ESCOLAR → conversacion_general
- "hola", "gracias", "¿cómo estás?", "adiós"
- Temas externos a la escuela
```

#### **DETECCIÓN DE SUB-INTENCIONES:**
```
DENTRO DE consulta_alumnos:

busqueda_simple: 1-2 criterios básicos
- "buscar García", "alumnos de 3er grado", "estudiantes del turno matutino"

busqueda_compleja: 3+ criterios o campos especiales
- "García de 3er grado turno matutino con promedio > 8"

estadisticas: Solicita números, conteos, análisis
- "cuántos alumnos", "distribución por grados", "promedio general"

generar_constancia: Solicita documentos oficiales
- "constancia para Juan", "certificado de estudios", "documento oficial"

transformacion_pdf: Conversión entre formatos
- "convertir constancia", "cambiar formato PDF"
```

### **EJEMPLOS DE RAZONAMIENTO CORRECTO:**
```
"Dame 3 alumnos de 3er grado"
→ RAZONAMIENTO: Quiere buscar alumnos (consulta_alumnos), criterios simples (busqueda_simple), límite específico (3)
→ RESULTADO: consulta_alumnos/busqueda_simple

"muy bien gracias ahora de ellos solo los de la tarde"
→ RAZONAMIENTO: Cortesía + filtrar lista anterior (consulta_alumnos), usa contexto (busqueda_simple con contexto)
→ RESULTADO: consulta_alumnos/busqueda_simple

"cuántos hay en total"
→ RAZONAMIENTO: Solicita conteo (consulta_alumnos), análisis numérico (estadisticas)
→ RESULTADO: consulta_alumnos/estadisticas

"¿cómo funciona el sistema?"
→ RAZONAMIENTO: Pregunta sobre funcionamiento (ayuda_sistema), explicación general (explicacion_general)
→ RESULTADO: ayuda_sistema/explicacion_general
```

---

**ESTA DOCUMENTACIÓN DEFINE LA ARQUITECTURA ÚNICA Y DEFINITIVA DEL SISTEMA DE INTENCIONES Y ACCIONES.**
