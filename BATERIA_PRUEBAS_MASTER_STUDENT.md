# 🧪 BATERÍA EXHAUSTIVA MASTER→STUDENT

## 📋 RESUMEN EJECUTIVO

**Objetivo**: Afianzar completamente la interacción Master→Student antes de integrar contexto multi-especialista
**Total de casos**: 120+ pruebas (individuales + continuaciones)
**Cobertura**: Todas las funcionalidades + edge cases + continuaciones complejas
**Estado**: ✅ Listo para ejecución sistemática
**🎯 DATOS REALES**: Actualizado con datos aleatorios extraídos de la base de datos real (211 alumnos)

## 🎯 INSTRUCCIONES DE USO

### **CONFIGURACIÓN REQUERIDA:**
```bash
# Habilitar pausas estratégicas para debugging
python ai_chat.py --debug-pauses

# O sin pausas para testing rápido
python ai_chat.py
```

### **METODOLOGÍA DE TESTING:**
1. **Ejecutar consultas individuales** primero
2. **Luego ejecutar secuencias de continuación** 
3. **Documentar comportamiento** de las 5 pausas estratégicas
4. **Verificar contexto conversacional** en continuaciones
5. **Confirmar robustez** antes de evolución multi-especialista

---

## 📋 SECCIÓN A: CONSULTAS INDIVIDUALES BÁSICAS

### **A1. BÚSQUEDAS POR APELLIDO (Datos Reales)**
```
A1.1: "busca alumnos con apellido MARTINEZ TORRES"
A1.2: "estudiantes apellido DIAZ RODRIGUEZ"
A1.3: "dame los RAMOS GUTIERREZ"
A1.4: "buscar HERNANDEZ MENDOZA"
A1.5: "alumnos que se apelliden MORALES PEREZ"
```

### **A2. BÚSQUEDAS POR NOMBRE COMPLETO (Datos Reales)**
```
A2.1: "buscar SOPHIA ROMERO GARCIA"
A2.2: "información de ANDRES FLORES SANCHEZ"
A2.3: "dame datos de ADRIANA TORRES RODRIGUEZ"
A2.4: "busca FRANCISCO RAMIREZ VARGAS"
A2.5: "estudiante PATRICIA TORRES TORRES"
```

### **A3. BÚSQUEDAS POR CRITERIOS ACADÉMICOS (Datos Reales)**
```
A3.1: "alumnos de 2 grado"
A3.2: "estudiantes del turno VESPERTINO"
A3.3: "alumnos de 3° A"
A3.4: "estudiantes de 5 grado turno MATUTINO"
A3.5: "alumnos del grupo B turno VESPERTINO"
```

### **A4. BÚSQUEDAS CON FILTROS DE CALIFICACIONES**
```
A4.4: "estudiantes sin calificaciones"
A4.5: "alumnos que tienen notas"
```

### **A5. CONSULTAS DE ESTADÍSTICAS**
```
A5.1: "cuántos alumnos hay en total"
A5.2: "distribución por grado"
A5.3: "estadísticas por turno"
A5.4: "promedio general de la escuela"
A5.5: "cuántos alumnos hay en 6 grado"
```

---

## 📋 SECCIÓN B: CONSTANCIAS Y DOCUMENTOS

### **B1. CONSTANCIAS POR NOMBRE (Datos Reales)**
```
B1.1: "constancia para NICOLAS GOMEZ DIAZ"
B1.2: "generar constancia de SILVIA MORENO MARTINEZ"
B1.3: "constancia de estudios para ANDRES RUIZ SANCHEZ"
B1.4: "constancia con foto para NATALIA MORALES SILVA"
B1.5: "constancia para MANUEL RUIZ LOPEZ"
```

### **B2. CONSTANCIAS CON OPCIONES (Datos Reales)**
```
B2.1: "constancia para SOPHIA ROMERO GARCIA sin foto"
B2.2: "certificado de ANDRES FLORES SANCHEZ con foto"
B2.3: "constancia de traslado para ADRIANA TORRES RODRIGUEZ"
B2.4: "constancia de calificaciones de FRANCISCO RAMIREZ VARGAS"
```

---

## 📋 SECCIÓN C: CONSULTAS COMPLEJAS INDIVIDUALES

### **C1. MÚLTIPLES CRITERIOS (Datos Reales)**
```
C1.1: "alumnos de 4 grado del turno VESPERTINO sin calificaciones"
C1.2: "estudiantes del grupo A que tengan calificaciones"
C1.3: "alumnos del turno MATUTINO con notas"
C1.4: "estudiantes de 1° B del turno VESPERTINO"
```

---

## 📋 SECCIÓN D: CASOS LÍMITE Y ERRORES

### **D1. NOMBRES NO EXISTENTES**
```
D1.1: "buscar ALUMNO INEXISTENTE FALSO"
D1.2: "constancia para NOMBRE QUE NO EXISTE"
D1.3: "información de ESTUDIANTE FICTICIO"
D1.4: "buscar APELLIDO INVENTADO"
D1.5: "datos de PERSONA INEXISTENTE"
```

### **D2. CRITERIOS IMPOSIBLES**
```
D2.1: "alumnos de grado 15" (no existe)
D2.2: "estudiantes del turno nocturno" (no existe)
D2.3: "alumnos con promedio mayor a 20" (imposible)
D2.4: "estudiantes de grupo Z" (no existe)
D2.5: "alumnos con edad mayor a 50" (imposible)
```

### **D3. CONSULTAS AMBIGUAS**
```
D3.1: "dame información del segundo" (no tiene una logica clara se debe preguntar al usuario deberia verificar el contexto si no encuentra nada que concuerde pregunta directaemten mas info)
```

---

## 🔄 SECCIÓN E: SECUENCIAS DE CONTINUACIÓN

### **E1. CONTINUACIÓN BÁSICA: FILTRADO (Datos Reales)**
```
SECUENCIA E1:
1. "busca alumnos con apellido MARTINEZ TORRES"
   → Esperar resultado (ej: 2 alumnos)
2. "de esos los del turno VESPERTINO"
   → Debe filtrar los 2 alumnos por turno
3. "cuántos son"
   → Debe contar los filtrados
```

### **E2. CONTINUACIÓN: MÚLTIPLES FILTROS (Datos Reales)**
```
SECUENCIA E2:
1. "alumnos de 1 grado"
   → Esperar resultado (ej: 41 alumnos según datos)
2. "de esos los del turno MATUTINO"
   → Debe filtrar por turno (29 alumnos)
3. "de esos los del grupo A"
   → Debe filtrar aún más (16 alumnos)
4. "con calificaciones"
   → Filtro final por calificaciones
```

### **E3. CONTINUACIÓN: CAMBIO DE CRITERIO (Datos Reales)**
```
SECUENCIA E3:
1. "estudiantes del turno VESPERTINO"
   → Esperar resultado
2. "mejor dicho, los de 6 grado"
   → Debe cambiar criterio completamente
3. "de esos los que tengan calificaciones"
   → Filtrar los nuevos resultados
```

### **E4. CONTINUACIÓN: CONSTANCIAS DESDE BÚSQUEDA (Datos Reales)**
```
SECUENCIA E4:
1. "busca alumnos con apellido DIAZ RODRIGUEZ"
   → Esperar lista de alumnos (2 alumnos)
2. "constancia para el primero"
   → Debe generar constancia para el primer alumno de la lista
3. "ahora para el segundo"
   → Debe generar para el segundo
```

### **E5. CONTINUACIÓN: ESTADÍSTICAS DESDE BÚSQUEDA (Datos Reales)**
```
SECUENCIA E5:
1. "alumnos de 5 grado del turno MATUTINO"
   → Esperar resultado (21 alumnos según datos)
2. "cuántos son por grupo"
   → Estadísticas de los resultados anteriores
3. "promedio de calificaciones de estos"
   → Análisis de los mismos datos
```

---

## 🔄 SECCIÓN F: CONTINUACIONES COMPLEJAS

### **F1. CONTINUACIÓN: MÚLTIPLES NIVELES**
```
SECUENCIA F1:
1. "todos los alumnos de la escuela"
   → Base amplia
2. "de esos los de [GRADO] grado"
   → Primer filtro
3. "de esos los del turno [TURNO]"
   → Segundo filtro
4. "de esos los del grupo [GRUPO]"
   → Tercer filtro
5. "de esos los que tengan promedio mayor a [NUM]"
   → Filtro final
6. "constancia para todos estos"
   → Acción sobre resultado final
```

### **F2. CONTINUACIÓN: ANÁLISIS PROGRESIVO**
```
SECUENCIA F2:
1. "alumnos con apellido [APELLIDO]"
   → Base de búsqueda
2. "cuántos son"
   → Conteo inicial
3. "distribución por grado"
   → Análisis 1
4. "distribución por turno"
   → Análisis 2
5. "promedio de calificaciones"
   → Análisis 3
6. "los que tienen mejor rendimiento"
   → Filtro basado en análisis
```

### **F3. CONTINUACIÓN: CAMBIOS DE CONTEXTO**
```
SECUENCIA F3:
1. "estudiantes de [GRADO] grado"
   → Contexto inicial
2. "mejor busca los de [APELLIDO]"
   → Cambio total de contexto
3. "de esos los del turno [TURNO]"
   → Continuación del nuevo contexto
4. "volviendo a los de [GRADO] grado"
   → Referencia al contexto anterior
5. "de esos los mejores"
   → Filtro del contexto recuperado
```

---

## 🔄 SECCIÓN G: EDGE CASES DE CONTINUACIÓN

### **G1. CONTINUACIÓN CON DATOS GRANDES**
```
SECUENCIA G1:
1. "todos los alumnos de la escuela"
   → Resultado grande (100+ alumnos)
2. "de esos los del turno [TURNO]"
   → Debe manejar regeneración de datos grandes
3. "cuántos son exactamente"
   → Verificar conteo correcto
```

### **G2. CONTINUACIÓN SIN RESULTADOS**
```
SECUENCIA G2:
1. "alumnos de [GRADO] grado"
   → Base con resultados
2. "de esos los que tengan promedio mayor a 15"
   → Filtro imposible (sin resultados)
3. "mejor los que tengan promedio mayor a [NUM_REAL]"
   → Corrección del filtro
```

### **G3. CONTINUACIÓN AMBIGUA**
```
SECUENCIA G3:
1. "busca alumnos con apellido [APELLIDO]"
   → Lista de alumnos
2. "del segundo"
   → Ambiguo: ¿segundo alumno o segundo grado?
3. "me refiero al segundo grado"
   → Clarificación
```

---

## 🎯 SECCIÓN H: VERIFICACIÓN DE PAUSAS ESTRATÉGICAS

### **H1. PAUSAS EN CONSULTAS INDIVIDUALES**
```
VERIFICAR EN CADA CONSULTA INDIVIDUAL:
✅ PAUSA #1: Master analiza intención correctamente
✅ PAUSA #2: Student recibe información completa
✅ PAUSA #4: Mapeo de campos inteligente
✅ PAUSA #5: SQL generado correctamente
❌ PAUSA #3: NO debe aparecer (sin continuación)
```

### **H2. PAUSAS EN CONTINUACIONES**
```
VERIFICAR EN CADA SECUENCIA DE CONTINUACIÓN:
✅ PAUSA #1: Master detecta continuación (fuente_datos: conversacion_previa)
✅ PAUSA #2: Student recibe contexto conversacional (NO VACÍO)
✅ PAUSA #3: Master detecta continuación inteligente (DEBE APARECER)
✅ PAUSA #4: Student mapea con contexto disponible
✅ PAUSA #5: SQL combina criterios del contexto + nuevos filtros
```

### **H3. INFORMACIÓN CRÍTICA A VERIFICAR**
```
EN PAUSA #1 (Master):
- ✅ fuente_datos: "base_datos" vs "conversacion_previa"
- ✅ contexto_especifico: Menciona búsqueda anterior en continuaciones
- ✅ Confianza alta (>0.9) para consultas claras

EN PAUSA #2 (Student):
- ✅ Contexto conversacional: "VACÍO" vs "X niveles"
- ✅ Información completa transferida

EN PAUSA #3 (Solo continuaciones):
- ✅ Tipo detectado: analysis, accion, etc.
- ✅ Razonamiento específico para la consulta

EN PAUSA #5 (ActionExecutor):
- ✅ SQL individual vs SQL con criterios combinados
- ✅ Mapeo correcto de tablas (alumnos vs datos_escolares)
```

---

## 📊 METODOLOGÍA DE TESTING

### **FASE 1: CONSULTAS INDIVIDUALES (A1-D3)**
```
OBJETIVO: Verificar que Master→Student funciona perfectamente sin contexto
TIEMPO: 45-60 minutos
CRITERIO: 95% de consultas básicas funcionan, errores elegantes para casos límite

PROCESO:
1. Ejecutar consultas A1-A5 (búsquedas básicas)
2. Ejecutar consultas B1-B2 (constancias)
3. Ejecutar consultas C1-C2 (complejas)
4. Ejecutar consultas D1-D3 (edge cases)
5. Documentar comportamiento de pausas #1, #2, #4, #5
```

### **FASE 2: CONTINUACIONES BÁSICAS (E1-E5)**
```
OBJETIVO: Verificar contexto conversacional y continuaciones simples
TIEMPO: 30-45 minutos
CRITERIO: Contexto se mantiene, filtros se combinan correctamente

PROCESO:
1. Ejecutar secuencias E1-E5 completas
2. Verificar que aparezca PAUSA #3 en continuaciones
3. Confirmar SQL combinado en PAUSA #5
4. Documentar comportamiento del contexto conversacional
```

### **FASE 3: CONTINUACIONES COMPLEJAS (F1-F3)**
```
OBJETIVO: Probar límites del contexto conversacional
TIEMPO: 45-60 minutos
CRITERIO: Múltiples niveles de contexto funcionan, cambios de contexto manejados

PROCESO:
1. Ejecutar secuencias F1-F3 paso a paso
2. Verificar contexto en cada nivel
3. Confirmar que cambios de contexto funcionan
4. Documentar comportamiento en casos complejos
```

### **FASE 4: EDGE CASES Y VERIFICACIÓN (G1-H3)**
```
OBJETIVO: Confirmar robustez total del sistema
TIEMPO: 30-45 minutos
CRITERIO: Sistema maneja casos límite elegantemente

PROCESO:
1. Ejecutar edge cases G1-G3
2. Verificar comportamiento de las 5 pausas estratégicas
3. Confirmar información crítica en cada pausa
4. Documentar cualquier comportamiento inesperado
```

---

## 📋 PLANTILLA DE DOCUMENTACIÓN

### **FORMATO PARA CONSULTAS INDIVIDUALES:**
```
CONSULTA: [ID] - "[texto]"
PAUSA #1: ✅ Master detectó [intención] con confianza [X]
PAUSA #2: ✅ Student recibió [X] entidades, contexto VACÍO
PAUSA #4: ✅ Mapeo [campo_usuario] → [campo_db]
PAUSA #5: ✅ SQL: [sql_generado]
RESULTADO: ✅/❌ [descripción]
TIEMPO: [X] segundos
OBSERVACIONES: [notas]
```

### **FORMATO PARA SECUENCIAS DE CONTINUACIÓN:**
```
SECUENCIA: [ID] - [descripción]
PASO 1: "[consulta_inicial]"
  - PAUSA #1: fuente_datos = "base_datos"
  - RESULTADO: [X] elementos encontrados
PASO 2: "[continuación]"
  - PAUSA #1: fuente_datos = "conversacion_previa" ✅
  - PAUSA #2: contexto = "1 niveles" ✅
  - PAUSA #3: tipo = "[analysis/accion]" ✅
  - PAUSA #5: SQL combinado ✅
  - RESULTADO: [Y] elementos filtrados
OBSERVACIONES: [comportamiento del contexto]
```

---

## ✅ CRITERIOS DE APROBACIÓN MASTER→STUDENT

### **SISTEMA APROBADO SI:**
- ✅ **95%+ consultas individuales** funcionan correctamente
- ✅ **90%+ continuaciones básicas** mantienen contexto
- ✅ **80%+ continuaciones complejas** manejan múltiples niveles
- ✅ **Pausas estratégicas** muestran información correcta
- ✅ **Errores elegantes** para casos imposibles
- ✅ **Performance** <5 segundos por consulta

### **LISTO PARA CONTEXTO MULTI-ESPECIALISTA SI:**
- ✅ Sistema Master→Student aprobado
- ✅ Contexto conversacional robusto
- ✅ Pausas estratégicas funcionando perfectamente
- ✅ Sin hardcodeo detectado
- ✅ Comportamiento predecible y documentado

---

**Total de casos**: 120+ pruebas
**Tiempo estimado**: 3-4 horas de testing exhaustivo
**Estado**: ✅ Listo para ejecución sistemática
**Próximo paso**: Ejecutar Fase 1 (consultas individuales)
