# 📋 PLANTILLAS SQL - CÓDIGO MOVIDO TEMPORALMENTE

## 🎯 **ESTADO ACTUAL**

**Este directorio contiene el código de plantillas SQL que NO se usa en el flujo principal.**

### **ARCHIVOS MOVIDOS:**
- `template_manager.py` - 15+ plantillas SQL implementadas
- `template_executor.py` - Ejecutor de plantillas
- `templates/` - Archivos .sql individuales

## ❌ **POR QUÉ SE MOVIERON**

### **RAZÓN PRINCIPAL:**
El sistema actual usa **generación SQL dinámica** que es:
- ✅ Más flexible
- ✅ Más mantenible  
- ✅ Funciona bien con consultas complejas
- ✅ No requiere plantillas predefinidas

### **PROBLEMA CON PLANTILLAS:**
- Explosión combinatoria (200+ plantillas para todas las combinaciones)
- Rigidez (cada nueva combinación = nueva plantilla)
- Mantenimiento complejo
- No aportan valor sobre SQL dinámico actual

## 🔮 **CUÁNDO VOLVER A IMPLEMENTAR**

### **CASOS FUTUROS QUE JUSTIFICARÍAN PLANTILLAS:**
1. **Consultas muy complejas** con lógica de negocio específica
2. **Optimizaciones de rendimiento** para consultas frecuentes
3. **Reportes especializados** con cálculos complejos
4. **Integración con sistemas externos** que requieren SQL específico

### **EJEMPLO DE CONSULTA COMPLEJA:**
```sql
-- Reporte que justificaría una plantilla
SELECT 
    a.nombre,
    de.grado,
    COUNT(c.materia) as materias_cursadas,
    AVG(c.promedio) as promedio_general,
    CASE 
        WHEN AVG(c.promedio) >= 9.0 THEN 'Excelente'
        WHEN AVG(c.promedio) >= 8.0 THEN 'Muy Bueno'
        ELSE 'Regular'
    END as clasificacion
FROM alumnos a
JOIN datos_escolares de ON a.id = de.alumno_id
LEFT JOIN calificaciones c ON a.id = c.alumno_id
WHERE de.ciclo_escolar = '2024-2025'
GROUP BY a.id, a.nombre, de.grado
HAVING COUNT(c.materia) >= 5
ORDER BY promedio_general DESC
```

## 🚀 **CÓMO REINTEGRAR EN EL FUTURO**

### **PASO 1: Importar en ActionExecutor**
```python
# En ActionExecutor.__init__()
from future_implementations.sql_templates.template_manager import SQLTemplateManager
self.template_manager = SQLTemplateManager()
```

### **PASO 2: Sistema híbrido**
```python
def _execute_buscar_universal(self, params):
    # Decidir entre SQL dinámico vs plantilla
    if self._should_use_template(params):
        return self._execute_with_template(params)
    else:
        return self._build_dynamic_sql(params)  # Actual
```

### **PASO 3: Criterios de selección**
```python
def _should_use_template(self, params):
    # Usar plantilla solo para casos específicos optimizados
    return (
        self._is_simple_standard_query(params) and
        self._has_performance_template(params)
    )
```

## 📝 **DOCUMENTACIÓN COMPLETA**

Ver: `nuevos_docs/PLANTILLAS_SQL_FUTURAS.md` para documentación detallada.

## 🎯 **DECISIÓN ACTUAL**

**MANTENER SQL DINÁMICO como sistema principal.**
**CONSERVAR PLANTILLAS para implementación futura opcional.**

---

**CÓDIGO MOVIDO TEMPORALMENTE - REINTEGRAR SOLO SI ES NECESARIO**
