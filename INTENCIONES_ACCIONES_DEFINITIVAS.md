# 🎯 INTENCIONES Y ACCIONES DEFINITIVAS DEL SISTEMA
## DOCUMENTACIÓN OFICIAL - ARQUITECTURA ÚNICA

**Fecha:** Diciembre 2024  
**Estado:** DEFINITIVO - Base para implementación  
**Propósito:** Definir claramente todas las intenciones, sub-intenciones y acciones del sistema

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
- **`BUSCAR_ALUMNOS_POR_CRITERIO`** - Búsqueda con criterios básicos
- **`OBTENER_ALUMNO_EXACTO`** - Cuando se busca una persona específica (CURP, matrícula)

**PLANTILLAS SQL:**
- `buscar_por_nombre.sql`
- `filtrar_grado_grupo.sql`
- `filtrar_por_turno.sql`
- `buscar_por_curp.sql`

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
- **`BUSCAR_UNIVERSAL`** - Búsqueda con múltiples criterios y filtros especiales
- **`FILTRAR_RESULTADOS_EXISTENTES`** - Para aplicar filtros adicionales a resultados previos

**PLANTILLAS SQL:**
- `buscar_con_promedio_json.sql`
- `buscar_combinado.sql`
- `alumnos_sin_calificaciones.sql`

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
- **`CALCULAR_ESTADISTICA`** - Promedios y análisis numéricos
- **`CONTAR_ALUMNOS_CON_FILTRO`** - Conteos específicos con filtros

**PLANTILLAS SQL:**
- `contar_alumnos_total.sql`
- `promedio_general.sql`
- `distribucion_por_grado.sql`
- `conteo_con_filtros.sql`

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
- **`GENERAR_CONSTANCIA_COMPLETA`** - Crear documentos PDF oficiales

**PLANTILLAS SQL:**
- `buscar_alumno_exacto.sql`
- `datos_completos_constancia.sql`
- `verificar_calificaciones.sql`

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
- **`GENERAR_CONSTANCIA_COMPLETA`** - Regenera documento en nuevo formato

**PLANTILLAS SQL:**
- `buscar_alumno_exacto.sql` (para obtener datos actualizados)

---

### **❓ INTENCIÓN: `ayuda_sistema`**

#### **SUB-INTENCIÓN: `pregunta_capacidades`**
**Descripción:** Qué puede hacer el sistema  
**Ejemplos:**
- "qué puedes hacer"
- "ayuda"
- "capacidades del sistema"

**ACCIONES DISPONIBLES:**
- **`EXPLICAR_CAPACIDADES`** - Lista capacidades generales del sistema

#### **SUB-INTENCIÓN: `pregunta_tecnica`**
**Descripción:** Cómo usar funcionalidades específicas  
**Ejemplos:**
- "cómo buscar alumnos"
- "cómo generar constancias"
- "ayuda con consultas"

**ACCIONES DISPONIBLES:**
- **`EXPLICAR_FUNCIONALIDAD`** - Explica cómo usar funciones específicas

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
├── busqueda_simple → BUSCAR_ALUMNOS_POR_CRITERIO, OBTENER_ALUMNO_EXACTO
├── busqueda_compleja → BUSCAR_UNIVERSAL, FILTRAR_RESULTADOS_EXISTENTES  
├── estadisticas → CALCULAR_ESTADISTICA, CONTAR_ALUMNOS_CON_FILTRO
├── generar_constancia → GENERAR_CONSTANCIA_COMPLETA
└── transformacion_pdf → GENERAR_CONSTANCIA_COMPLETA

ayuda_sistema → HelpInterpreter
├── pregunta_capacidades → EXPLICAR_CAPACIDADES
└── pregunta_tecnica → EXPLICAR_FUNCIONALIDAD

conversacion_general → MasterInterpreter (directo)
├── saludo → RESPUESTA_CASUAL
└── chat_casual → RESPUESTA_CASUAL
```

---

## 📊 **RESUMEN DE ACCIONES PRINCIPALES**

### **ACCIONES DE BÚSQUEDA:**
- **`BUSCAR_ALUMNOS_POR_CRITERIO`** - Búsqueda básica con criterios simples
- **`OBTENER_ALUMNO_EXACTO`** - Búsqueda de alumno específico
- **`BUSCAR_UNIVERSAL`** - Búsqueda compleja con múltiples criterios
- **`FILTRAR_RESULTADOS_EXISTENTES`** - Filtros adicionales

### **ACCIONES DE ANÁLISIS:**
- **`CALCULAR_ESTADISTICA`** - Cálculos y promedios
- **`CONTAR_ALUMNOS_CON_FILTRO`** - Conteos específicos

### **ACCIONES DE DOCUMENTOS:**
- **`GENERAR_CONSTANCIA_COMPLETA`** - Generación de PDFs oficiales

### **ACCIONES DE AYUDA:**
- **`EXPLICAR_CAPACIDADES`** - Capacidades del sistema
- **`EXPLICAR_FUNCIONALIDAD`** - Ayuda específica

### **ACCIONES GENERALES:**
- **`RESPUESTA_CASUAL`** - Chat general y saludos

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

**ESTA DOCUMENTACIÓN DEFINE LA ARQUITECTURA ÚNICA Y DEFINITIVA DEL SISTEMA DE INTENCIONES Y ACCIONES.**
