# 🎯 MIGRACIÓN FUTURA: TABLA CALIFICACIONES SEPARADA

## 📋 **PROBLEMA ACTUAL:**
- Calificaciones almacenadas en JSON dentro de `datos_escolares.calificaciones`
- Consultas complejas requieren JSON_EXTRACT
- Difícil filtrar por materia específica
- Rendimiento lento en consultas de calificaciones

## 🚀 **SOLUCIÓN PROPUESTA:**

### **📊 NUEVA ESTRUCTURA DE TABLA:**
```sql
CREATE TABLE calificaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alumno_id INTEGER NOT NULL,
    materia TEXT NOT NULL,
    bimestre_i REAL DEFAULT 0,
    bimestre_ii REAL DEFAULT 0,
    bimestre_iii REAL DEFAULT 0,
    promedio REAL GENERATED ALWAYS AS (
        CASE 
            WHEN bimestre_i > 0 AND bimestre_ii > 0 AND bimestre_iii > 0 
            THEN (bimestre_i + bimestre_ii + bimestre_iii) / 3.0
            WHEN bimestre_i > 0 AND bimestre_ii > 0 
            THEN (bimestre_i + bimestre_ii) / 2.0
            WHEN bimestre_i > 0 
            THEN bimestre_i
            ELSE 0
        END
    ) STORED,
    ciclo_escolar TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE
);

-- Índices para optimización
CREATE INDEX idx_calificaciones_alumno ON calificaciones(alumno_id);
CREATE INDEX idx_calificaciones_materia ON calificaciones(materia);
CREATE INDEX idx_calificaciones_promedio ON calificaciones(promedio);
```

### **📊 DATOS DE EJEMPLO:**
```sql
INSERT INTO calificaciones (alumno_id, materia, bimestre_i, bimestre_ii, bimestre_iii, ciclo_escolar) VALUES
(1, 'MATEMATICAS', 8.0, 9.0, 8.5, '2024-2025'),
(1, 'ESPAÑOL', 9.0, 9.0, 9.0, '2024-2025'),
(1, 'CIENCIAS', 7.5, 8.0, 8.5, '2024-2025'),
(1, 'HISTORIA', 8.5, 8.0, 9.0, '2024-2025');
```

## 🎯 **VENTAJAS DE LA MIGRACIÓN:**

### **✅ CONSULTAS SIMPLES Y RÁPIDAS:**
```sql
-- Promedio general por alumno
SELECT a.nombre, AVG(c.promedio) as promedio_general
FROM alumnos a
JOIN calificaciones c ON a.id = c.alumno_id
GROUP BY a.id, a.nombre;

-- Alumnos con promedio > 8 en matemáticas
SELECT a.nombre, c.promedio
FROM alumnos a
JOIN calificaciones c ON a.id = c.alumno_id
WHERE c.materia = 'MATEMATICAS' AND c.promedio > 8.0;

-- Mejores estudiantes por materia
SELECT c.materia, a.nombre, c.promedio
FROM calificaciones c
JOIN alumnos a ON c.alumno_id = a.id
WHERE c.promedio = (
    SELECT MAX(promedio) 
    FROM calificaciones c2 
    WHERE c2.materia = c.materia
);

-- Estudiantes que necesitan apoyo (promedio < 6)
SELECT a.nombre, c.materia, c.promedio
FROM alumnos a
JOIN calificaciones c ON a.id = c.alumno_id
WHERE c.promedio < 6.0
ORDER BY c.promedio ASC;
```

### **✅ CONSULTAS COMPLEJAS POSIBLES:**
```sql
-- Alumnos de 2do A con promedio general > 8
SELECT a.nombre, de.grado, de.grupo, AVG(c.promedio) as promedio_general
FROM alumnos a
JOIN datos_escolares de ON a.id = de.alumno_id
JOIN calificaciones c ON a.id = c.alumno_id
WHERE de.grado = 2 AND de.grupo = 'A'
GROUP BY a.id
HAVING AVG(c.promedio) > 8.0;

-- Distribución de calificaciones por materia y grado
SELECT de.grado, c.materia, 
       COUNT(*) as total_estudiantes,
       AVG(c.promedio) as promedio_materia,
       MIN(c.promedio) as promedio_minimo,
       MAX(c.promedio) as promedio_maximo
FROM calificaciones c
JOIN alumnos a ON c.alumno_id = a.id
JOIN datos_escolares de ON a.id = de.alumno_id
GROUP BY de.grado, c.materia
ORDER BY de.grado, c.materia;

-- Estudiantes que mejoraron del bimestre I al III
SELECT a.nombre, c.materia, 
       c.bimestre_i as inicial,
       c.bimestre_iii as final,
       (c.bimestre_iii - c.bimestre_i) as mejora
FROM alumnos a
JOIN calificaciones c ON a.id = c.alumno_id
WHERE c.bimestre_iii > c.bimestre_i
ORDER BY mejora DESC;
```

## 🔧 **SCRIPT DE MIGRACIÓN:**

### **📊 MIGRAR DATOS EXISTENTES:**
```sql
-- 1. Crear nueva tabla
-- (Ver estructura arriba)

-- 2. Migrar datos desde JSON
INSERT INTO calificaciones (alumno_id, materia, bimestre_i, bimestre_ii, bimestre_iii, ciclo_escolar)
SELECT 
    de.alumno_id,
    json_extract(cal.value, '$.nombre') as materia,
    COALESCE(json_extract(cal.value, '$.i'), 0) as bimestre_i,
    COALESCE(json_extract(cal.value, '$.ii'), 0) as bimestre_ii,
    COALESCE(json_extract(cal.value, '$.iii'), 0) as bimestre_iii,
    de.ciclo_escolar
FROM datos_escolares de,
     json_each(de.calificaciones) cal
WHERE de.calificaciones IS NOT NULL 
  AND de.calificaciones != '[]'
  AND json_extract(cal.value, '$.nombre') IS NOT NULL;

-- 3. Verificar migración
SELECT COUNT(*) as total_registros_migrados FROM calificaciones;

-- 4. Opcional: Limpiar campo JSON después de verificar
-- ALTER TABLE datos_escolares DROP COLUMN calificaciones;
```

## 🎯 **IMPACTO EN EL SISTEMA:**

### **📋 CAMBIOS NECESARIOS:**

#### **1. ActionExecutor:**
```python
# ANTES (JSON):
elif operador_principal.upper() == "JSON_PROMEDIO":
    # Complejo JSON_EXTRACT...

# DESPUÉS (Tabla):
elif campo_principal == "promedio":
    sql += f" AND c.promedio {operador_principal} {valor_principal}"
```

#### **2. Plantillas SQL:**
```sql
-- Nueva plantilla: buscar_con_promedio.sql
SELECT a.*, de.*, AVG(c.promedio) as promedio_general
FROM alumnos a
LEFT JOIN datos_escolares de ON a.id = de.alumno_id
LEFT JOIN calificaciones c ON a.id = c.alumno_id
WHERE {criterios_base}
GROUP BY a.id
HAVING AVG(c.promedio) {operador_promedio} {valor_promedio}
```

#### **3. Student Interpreter:**
```python
# Promedio se convierte en campo normal
if "promedio" in query:
    criterio = {
        "tabla": "calificaciones",
        "campo": "promedio", 
        "operador": ">",
        "valor": "8"
    }
```

## ⏰ **CRONOGRAMA SUGERIDO:**

### **FASE 1: VALIDACIÓN ACTUAL (AHORA)**
- [ ] Probar consultas sin calificaciones
- [ ] Confirmar funcionamiento básico del sistema
- [ ] Validar arquitectura Master→Student

### **FASE 2: PREPARACIÓN (FUTURO)**
- [ ] Crear script de migración
- [ ] Probar migración en copia de BD
- [ ] Actualizar plantillas SQL

### **FASE 3: MIGRACIÓN (CUANDO SEA NECESARIO)**
- [ ] Ejecutar migración de datos
- [ ] Actualizar código del sistema
- [ ] Probar consultas complejas de calificaciones

## 📝 **NOTAS:**
- Esta migración es OPCIONAL y solo necesaria si se requieren consultas complejas de calificaciones
- El sistema actual funciona perfectamente para consultas básicas
- La migración mejorará significativamente el rendimiento y flexibilidad de consultas de calificaciones
