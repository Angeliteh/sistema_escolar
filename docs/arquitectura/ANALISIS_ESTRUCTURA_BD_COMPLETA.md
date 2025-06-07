# 🗄️ ANÁLISIS: ESTRUCTURA DE BASE DE DATOS COMPLETA
## ESTADO ACTUAL Y EXPANSIÓN PARA SISTEMA ESCOLAR INTEGRAL

**Fecha:** Enero 2025  
**Objetivo:** Diseñar estructura BD para sistema escolar completo  
**Estado:** Análisis de estructura actual y propuesta de expansión

---

## 📊 **ESTRUCTURA ACTUAL DE LA BASE DE DATOS**

### **✅ TABLAS EXISTENTES (FUNCIONANDO)**

#### **1. 🎓 TABLA: `alumnos`**
```sql
-- ESTRUCTURA INFERIDA DEL CÓDIGO
CREATE TABLE alumnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curp TEXT UNIQUE,
    nombre TEXT NOT NULL,
    matricula TEXT,
    fecha_nacimiento DATE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **2. 📚 TABLA: `datos_escolares`**
```sql
-- ESTRUCTURA INFERIDA DEL CÓDIGO
CREATE TABLE datos_escolares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL,
    ciclo_escolar TEXT,
    grado INTEGER,
    grupo TEXT,
    turno TEXT,
    escuela TEXT,
    cct TEXT,
    calificaciones TEXT,  -- JSON: [{"nombre": "Matemáticas", "periodo_1": 8.5, ...}]
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
);
```

#### **3. 📄 TABLA: `constancias` (INFERIDA)**
```sql
-- TABLA MENCIONADA EN DatabaseAnalyzer
CREATE TABLE constancias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL,
    tipo_constancia TEXT,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    archivo_path TEXT,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id)
);
```

### **🔍 RELACIONES ACTUALES**
```
alumnos (1) ←→ datos_escolares (N)  -- Un alumno puede tener múltiples registros por ciclo
alumnos (1) ←→ constancias (N)      -- Un alumno puede tener múltiples constancias
```

---

## 🚀 **PROPUESTA: SISTEMA ESCOLAR COMPLETO**

### **OPCIÓN A: EXPANSIÓN GRADUAL (RECOMENDADO)**

#### **🎯 MANTENER ESTRUCTURA ACTUAL + AGREGAR TABLAS NUEVAS**

```sql
-- ===== TABLAS EXISTENTES (SIN CAMBIOS) =====
-- alumnos, datos_escolares, constancias

-- ===== NUEVAS TABLAS PARA SISTEMA COMPLETO =====

-- 1. 👨‍🏫 MAESTROS/PROFESORES
CREATE TABLE maestros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    curp TEXT UNIQUE,
    rfc TEXT,
    especialidad TEXT,
    telefono TEXT,
    email TEXT,
    activo BOOLEAN DEFAULT 1,
    fecha_ingreso DATE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. 📚 MATERIAS (CATÁLOGO)
CREATE TABLE materias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    clave TEXT UNIQUE,
    descripcion TEXT,
    grado INTEGER,
    activa BOOLEAN DEFAULT 1,
    orden_display INTEGER DEFAULT 0
);

-- 3. 🏫 GRUPOS (DETALLE)
CREATE TABLE grupos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grado INTEGER NOT NULL,
    grupo TEXT NOT NULL,
    ciclo_escolar TEXT NOT NULL,
    turno TEXT DEFAULT 'MATUTINO',
    maestro_titular_id INTEGER,
    aula TEXT,
    capacidad_maxima INTEGER DEFAULT 30,
    activo BOOLEAN DEFAULT 1,
    FOREIGN KEY (maestro_titular_id) REFERENCES maestros(id),
    UNIQUE(grado, grupo, ciclo_escolar, turno)
);

-- 4. 📊 CALIFICACIONES (NORMALIZADA)
CREATE TABLE calificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    ciclo_escolar TEXT NOT NULL,
    periodo_1 REAL,
    periodo_2 REAL,
    periodo_3 REAL,
    promedio REAL,
    observaciones TEXT,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    UNIQUE(alumno_id, materia_id, ciclo_escolar)
);

-- 5. 👨‍🏫📚 ASIGNACIONES MAESTRO-MATERIA-GRUPO
CREATE TABLE asignaciones_maestros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maestro_id INTEGER NOT NULL,
    materia_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    ciclo_escolar TEXT NOT NULL,
    activa BOOLEAN DEFAULT 1,
    fecha_asignacion DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (maestro_id) REFERENCES maestros(id),
    FOREIGN KEY (materia_id) REFERENCES materias(id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    UNIQUE(materia_id, grupo_id, ciclo_escolar)
);

-- 6. 🎓📚 INSCRIPCIONES ALUMNO-GRUPO
CREATE TABLE inscripciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    ciclo_escolar TEXT NOT NULL,
    fecha_inscripcion DATE DEFAULT CURRENT_DATE,
    fecha_baja DATE,
    motivo_baja TEXT,
    activa BOOLEAN DEFAULT 1,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(id),
    UNIQUE(alumno_id, ciclo_escolar)
);
```

### **🔗 RELACIONES COMPLETAS**

```
📊 DIAGRAMA DE RELACIONES:

alumnos (1) ←→ inscripciones (N) ←→ grupos (1)
    ↓                                    ↓
datos_escolares (N)              maestros (1) ← asignaciones_maestros (N) → materias (1)
    ↓                                    ↓                                      ↓
constancias (N)                  grupos (1) ←→ calificaciones (N) ←→ materias (1)
                                         ↓
                                 calificaciones (N) → alumnos (1)
```

---

## 🎯 **CONSULTAS SQL AVANZADAS POSIBLES**

### **1. 📊 CONSULTAS ACADÉMICAS**

```sql
-- Calificaciones completas de un alumno
SELECT a.nombre as alumno, m.nombre as materia, 
       c.periodo_1, c.periodo_2, c.periodo_3, c.promedio,
       g.grado, g.grupo, g.turno
FROM alumnos a
JOIN inscripciones i ON a.id = i.alumno_id
JOIN grupos g ON i.grupo_id = g.id
JOIN calificaciones c ON a.id = c.alumno_id AND g.id = c.grupo_id
JOIN materias m ON c.materia_id = m.id
WHERE a.nombre LIKE '%García%' AND i.activa = 1
ORDER BY m.orden_display;

-- Promedio general por grupo
SELECT g.grado, g.grupo, g.turno,
       AVG(c.promedio) as promedio_grupo,
       COUNT(DISTINCT c.alumno_id) as total_alumnos
FROM grupos g
JOIN calificaciones c ON g.id = c.grupo_id
WHERE g.ciclo_escolar = '2024-2025' AND g.activo = 1
GROUP BY g.id
ORDER BY g.grado, g.grupo;

-- Ranking de alumnos por materia
SELECT a.nombre, c.promedio,
       RANK() OVER (PARTITION BY c.materia_id ORDER BY c.promedio DESC) as ranking
FROM alumnos a
JOIN calificaciones c ON a.id = c.alumno_id
JOIN materias m ON c.materia_id = m.id
WHERE m.nombre = 'Matemáticas' AND c.ciclo_escolar = '2024-2025'
ORDER BY c.promedio DESC;
```

### **2. 👨‍🏫 CONSULTAS ADMINISTRATIVAS**

```sql
-- Carga académica de un maestro
SELECT ma.nombre as maestro, mt.nombre as materia,
       g.grado, g.grupo, g.turno,
       COUNT(i.alumno_id) as total_alumnos
FROM maestros ma
JOIN asignaciones_maestros am ON ma.id = am.maestro_id
JOIN materias mt ON am.materia_id = mt.id
JOIN grupos g ON am.grupo_id = g.id
LEFT JOIN inscripciones i ON g.id = i.grupo_id AND i.activa = 1
WHERE ma.nombre LIKE '%López%' AND am.activa = 1
GROUP BY ma.id, mt.id, g.id
ORDER BY g.grado, g.grupo;

-- Grupos sin maestro titular
SELECT g.grado, g.grupo, g.turno, g.ciclo_escolar
FROM grupos g
WHERE g.maestro_titular_id IS NULL AND g.activo = 1;

-- Materias sin maestro asignado
SELECT m.nombre as materia, g.grado, g.grupo
FROM materias m
CROSS JOIN grupos g
LEFT JOIN asignaciones_maestros am ON m.id = am.materia_id 
    AND g.id = am.grupo_id AND am.activa = 1
WHERE am.id IS NULL AND g.activo = 1 AND m.activa = 1
ORDER BY g.grado, g.grupo, m.nombre;
```

### **3. 📈 CONSULTAS ESTADÍSTICAS**

```sql
-- Estadísticas por grado
SELECT g.grado,
       COUNT(DISTINCT i.alumno_id) as total_alumnos,
       COUNT(DISTINCT g.id) as total_grupos,
       AVG(c.promedio) as promedio_general,
       MIN(c.promedio) as calificacion_minima,
       MAX(c.promedio) as calificacion_maxima
FROM grupos g
LEFT JOIN inscripciones i ON g.id = i.grupo_id AND i.activa = 1
LEFT JOIN calificaciones c ON i.alumno_id = c.alumno_id
WHERE g.ciclo_escolar = '2024-2025' AND g.activo = 1
GROUP BY g.grado
ORDER BY g.grado;

-- Materias con mayor índice de reprobación
SELECT m.nombre as materia,
       COUNT(CASE WHEN c.promedio < 6.0 THEN 1 END) as reprobados,
       COUNT(c.id) as total_evaluados,
       ROUND(COUNT(CASE WHEN c.promedio < 6.0 THEN 1 END) * 100.0 / COUNT(c.id), 2) as porcentaje_reprobacion
FROM materias m
JOIN calificaciones c ON m.id = c.materia_id
WHERE c.ciclo_escolar = '2024-2025'
GROUP BY m.id, m.nombre
HAVING COUNT(c.id) > 0
ORDER BY porcentaje_reprobacion DESC;
```

---

## 🔧 **ESTRATEGIA DE IMPLEMENTACIÓN**

### **FASE 1: MIGRACIÓN GRADUAL (SIN ROMPER NADA)**

1. **✅ Mantener estructura actual** funcionando
2. **🆕 Agregar nuevas tablas** sin afectar código existente
3. **🔄 Migrar gradualmente** las calificaciones de JSON a tabla normalizada
4. **🎯 Actualizar consultas** para usar nuevas relaciones

### **FASE 2: COMPATIBILIDAD DUAL**

```python
# Ejemplo: Obtener calificaciones con compatibilidad
def get_calificaciones_alumno(alumno_id: int, use_normalized: bool = False):
    if use_normalized:
        # Usar nueva tabla calificaciones
        return get_calificaciones_from_table(alumno_id)
    else:
        # Usar JSON en datos_escolares (actual)
        return get_calificaciones_from_json(alumno_id)
```

### **FASE 3: MIGRACIÓN COMPLETA**

1. **📊 Migrar datos** de JSON a tablas normalizadas
2. **🔄 Actualizar código** para usar nuevas relaciones
3. **🗑️ Deprecar** campo JSON de calificaciones
4. **✅ Sistema completo** funcionando

---

## 🎯 **VENTAJAS DE LA ESTRUCTURA PROPUESTA**

### **✅ ESCALABILIDAD:**
- ✅ Soporte para múltiples maestros por materia
- ✅ Asignaciones flexibles maestro-grupo-materia
- ✅ Historial completo de inscripciones
- ✅ Calificaciones normalizadas y consultables

### **✅ FLEXIBILIDAD:**
- ✅ Grupos con maestros titulares
- ✅ Materias configurables por grado
- ✅ Turnos y horarios flexibles
- ✅ Capacidad de aulas configurable

### **✅ REPORTES AVANZADOS:**
- ✅ Carga académica de maestros
- ✅ Estadísticas por grupo/grado/materia
- ✅ Rankings y promedios
- ✅ Análisis de rendimiento académico

**¿Te parece bien esta estructura? ¿Empezamos implementando las nuevas tablas manteniendo compatibilidad con el sistema actual?** 🎓
