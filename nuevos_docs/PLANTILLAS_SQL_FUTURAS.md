# 📋 PLANTILLAS SQL - IMPLEMENTACIÓN FUTURA

## 🎯 **ESTADO ACTUAL**

**Las plantillas SQL están implementadas pero NO se usan en el flujo principal.**

### **ARCHIVOS MOVIDOS:**
- `future_implementations/sql_templates/template_manager.py` - 15+ plantillas SQL
- `future_implementations/sql_templates/template_executor.py` - Ejecutor de plantillas

### **FLUJO ACTUAL (SIN PLANTILLAS):**
```
ActionExecutor → _build_dynamic_sql() → SQL generado dinámicamente ✅ FUNCIONA BIEN
```

## ❌ **POR QUÉ NO SE IMPLEMENTARON**

### **1. SQL DINÁMICO ES SUPERIOR:**
- **Flexibilidad total:** Maneja cualquier combinación de criterios
- **Operadores avanzados:** =, LIKE, >, <, BETWEEN, JSON_PROMEDIO, etc.
- **Sin explosión combinatoria:** Una función vs 200+ plantillas

### **2. PLANTILLAS SON RÍGIDAS:**
```sql
-- Plantilla rígida
SELECT * FROM alumnos WHERE grado = ? AND grupo = ?

-- ¿Qué pasa si quiero agregar turno? ¿Nueva plantilla?
-- ¿Y si quiero nombre + grado? ¿Otra plantilla?
-- ¿Y si quiero 4 criterios? ¿Otra más?
```

### **3. MANTENIMIENTO COMPLEJO:**
- Cada nueva combinación = nueva plantilla
- Cambios en BD = actualizar múltiples plantillas
- Debugging más difícil

## 🔮 **CUÁNDO PODRÍAN SER ÚTILES**

### **CASOS ESPECÍFICOS FUTUROS:**
1. **Consultas muy complejas** con lógica de negocio específica
2. **Optimizaciones de rendimiento** para consultas frecuentes
3. **Reportes especializados** con cálculos complejos
4. **Integración con sistemas externos** que requieren SQL específico

### **EJEMPLO DE USO FUTURO:**
```sql
-- Reporte complejo que justificaría una plantilla
SELECT 
    a.nombre,
    de.grado,
    COUNT(c.materia) as materias_cursadas,
    AVG(c.promedio) as promedio_general,
    CASE 
        WHEN AVG(c.promedio) >= 9.0 THEN 'Excelente'
        WHEN AVG(c.promedio) >= 8.0 THEN 'Muy Bueno'
        WHEN AVG(c.promedio) >= 7.0 THEN 'Bueno'
        ELSE 'Regular'
    END as clasificacion,
    (SELECT COUNT(*) FROM asistencias WHERE alumno_id = a.id) as dias_asistencia
FROM alumnos a
JOIN datos_escolares de ON a.id = de.alumno_id
LEFT JOIN calificaciones c ON a.id = c.alumno_id
LEFT JOIN asistencias ast ON a.id = ast.alumno_id
WHERE de.ciclo_escolar = '2024-2025'
GROUP BY a.id, a.nombre, de.grado
HAVING COUNT(c.materia) >= 5
ORDER BY promedio_general DESC, dias_asistencia DESC
```

## 📋 **PLANTILLAS IMPLEMENTADAS (REFERENCIA)**

### **BÚSQUEDAS BÁSICAS:**
- `buscar_alumno` - Por nombre con información completa
- `buscar_alumno_exacto` - Por nombre exacto
- `buscar_por_curp` - Por CURP específico
- `buscar_por_matricula` - Por matrícula específica

### **FILTROS COMBINADOS:**
- `filtrar_por_turno` - Solo por turno
- `filtrar_por_grupo` - Solo por grupo
- `filtrar_grado_grupo` - Grado + grupo combinados

### **CONTEOS Y ESTADÍSTICAS:**
- `contar_alumnos_total` - Conteo total
- `contar_por_grado` - Distribución por grado
- `contar_por_turno` - Distribución por turno

### **CALIFICACIONES:**
- `alumnos_con_calificaciones` - Que tienen calificaciones
- `alumnos_sin_calificaciones` - Que NO tienen calificaciones

## 🚀 **CÓMO IMPLEMENTAR EN EL FUTURO**

### **PASO 1: Integrar al ActionExecutor**
```python
# En ActionExecutor.__init__()
from future_implementations.sql_templates.template_manager import SQLTemplateManager
self.template_manager = SQLTemplateManager()

# En _execute_buscar_universal()
def _execute_buscar_universal(self, params):
    # Opción 1: SQL dinámico (actual)
    if self._should_use_dynamic_sql(params):
        return self._build_dynamic_sql(params)
    
    # Opción 2: Plantilla específica (futuro)
    template_name = self._select_template_for_params(params)
    return self._execute_template(template_name, params)
```

### **PASO 2: Criterios de selección**
```python
def _should_use_dynamic_sql(self, params):
    # Usar SQL dinámico para casos complejos/flexibles
    criterios_count = len(params.get("filtros_adicionales", [])) + 1
    return criterios_count > 3 or self._has_special_operators(params)

def _select_template_for_params(self, params):
    # Seleccionar plantilla para casos simples/optimizados
    if self._is_simple_name_search(params):
        return "buscar_alumno"
    elif self._is_grade_group_search(params):
        return "filtrar_grado_grupo"
    # etc...
```

### **PASO 3: Sistema híbrido**
```python
# Lo mejor de ambos mundos:
# - Plantillas para casos simples y optimizados
# - SQL dinámico para casos complejos y flexibles
```

## 📝 **DOCUMENTACIÓN DE PLANTILLAS**

### **ESTRUCTURA SQLTemplate:**
```python
@dataclass
class SQLTemplate:
    name: str
    description: str
    sql: str
    parameters: List[str]
    returns_multiple: bool = True
    requires_exact_match: bool = False
```

### **EJEMPLO DE PLANTILLA:**
```python
templates["buscar_alumno"] = SQLTemplate(
    name="buscar_alumno",
    description="Busca alumno por nombre con información completa",
    sql="""
        SELECT a.id, a.curp, a.nombre, a.matricula, a.fecha_nacimiento,
               de.grado, de.grupo, de.turno, de.calificaciones
        FROM alumnos a
        LEFT JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE a.nombre LIKE '%{nombre}%'
        ORDER BY a.nombre
    """,
    parameters=["nombre"],
    returns_multiple=True
)
```

## 🎯 **DECISIÓN ACTUAL**

**MANTENER SQL DINÁMICO como sistema principal.**
**CONSERVAR PLANTILLAS para implementación futura opcional.**

### **RAZONES:**
1. ✅ SQL dinámico funciona bien actualmente
2. ✅ Es más flexible y mantenible
3. ✅ Plantillas pueden agregarse después sin romper nada
4. ✅ Sistema híbrido es posible en el futuro

---

**ARCHIVO MOVIDO A DOCUMENTACIÓN FUTURA - NO IMPLEMENTAR HASTA QUE SEA NECESARIO**
