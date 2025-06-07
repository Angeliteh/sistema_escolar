# 🎓 PLAN: IMPLEMENTACIÓN DE MATERIAS DINÁMICAS
## SISTEMA COMPLETAMENTE CONFIGURABLE POR ESCUELA

**Objetivo:** Hacer las materias 100% configurables por escuela  
**Tiempo estimado:** 2-3 horas  
**Impacto:** Sistema adaptable a cualquier nivel educativo

---

## 🎯 **PASO 1: ACTUALIZAR CONFIGURACIÓN ESCOLAR**

### **1.1 Agregar sección de materias a school_config.json**

```json
{
  "school_info": {
    "name": "PROF. MAXIMO GAMIZ FERNANDEZ",
    "cct": "10DPR0392H",
    "director": "JOSE ANGEL ALVARADO SOSA",
    "education_level": "PRIMARIA"
  },
  "academic_info": {
    "current_year": "2024-2025",
    "grades": [1, 2, 3, 4, 5, 6],
    "groups": ["A", "B", "C"],
    "shifts": ["MATUTINO", "VESPERTINO"],
    
    // 🆕 NUEVA SECCIÓN: MATERIAS DINÁMICAS
    "materias_por_grado": {
      "1": [
        "Matemáticas",
        "Español",
        "Conocimiento del Medio",
        "Educación Física",
        "Educación Artística"
      ],
      "2": [
        "Matemáticas",
        "Español", 
        "Conocimiento del Medio",
        "Educación Física",
        "Educación Artística"
      ],
      "3": [
        "Matemáticas",
        "Español",
        "Ciencias Naturales",
        "Historia",
        "Educación Física",
        "Educación Artística"
      ],
      "4": [
        "Matemáticas",
        "Español",
        "Ciencias Naturales", 
        "Historia",
        "Geografía",
        "Educación Física",
        "Educación Artística"
      ],
      "5": [
        "Matemáticas",
        "Español",
        "Ciencias Naturales",
        "Historia", 
        "Geografía",
        "Formación Cívica y Ética",
        "Educación Física",
        "Educación Artística"
      ],
      "6": [
        "Matemáticas",
        "Español",
        "Ciencias Naturales",
        "Historia",
        "Geografía", 
        "Formación Cívica y Ética",
        "Educación Física",
        "Educación Artística"
      ]
    },
    
    // 🆕 CONFIGURACIÓN DE EVALUACIÓN
    "evaluacion_config": {
      "periodos": ["Periodo 1", "Periodo 2", "Periodo 3"],
      "escala_calificaciones": {
        "minima": 5.0,
        "maxima": 10.0,
        "aprobatoria": 6.0,
        "decimales": 1
      },
      "mostrar_promedio_general": true,
      "calcular_promedio_automatico": true
    }
  }
}
```

### **1.2 Ejemplos para otros niveles educativos**

```json
// EJEMPLO: SECUNDARIA
{
  "school_info": {
    "education_level": "SECUNDARIA"
  },
  "academic_info": {
    "grades": [1, 2, 3],
    "materias_por_grado": {
      "1": [
        "Matemáticas",
        "Español",
        "Ciencias (Biología)",
        "Historia",
        "Geografía",
        "Inglés",
        "Educación Física",
        "Artes"
      ],
      "2": [
        "Matemáticas",
        "Español", 
        "Ciencias (Física)",
        "Historia",
        "Geografía",
        "Inglés",
        "Educación Física",
        "Artes",
        "Tecnología"
      ],
      "3": [
        "Matemáticas",
        "Español",
        "Ciencias (Química)",
        "Historia",
        "Geografía",
        "Inglés",
        "Educación Física",
        "Artes",
        "Orientación Vocacional"
      ]
    }
  }
}

// EJEMPLO: PREESCOLAR
{
  "school_info": {
    "education_level": "PREESCOLAR"
  },
  "academic_info": {
    "grades": [1, 2, 3],
    "materias_por_grado": {
      "1": [
        "Lenguaje y Comunicación",
        "Pensamiento Matemático",
        "Exploración del Mundo",
        "Desarrollo Personal y Social",
        "Expresión Artística",
        "Desarrollo Físico"
      ],
      "2": [
        "Lenguaje y Comunicación",
        "Pensamiento Matemático", 
        "Exploración del Mundo",
        "Desarrollo Personal y Social",
        "Expresión Artística",
        "Desarrollo Físico"
      ],
      "3": [
        "Lenguaje y Comunicación",
        "Pensamiento Matemático",
        "Exploración del Mundo", 
        "Desarrollo Personal y Social",
        "Expresión Artística",
        "Desarrollo Físico"
      ]
    }
  }
}
```

---

## 🔧 **PASO 2: CREAR MATERIA MANAGER**

### **2.1 Crear archivo: app/core/config/materia_manager.py**

```python
"""
🎓 GESTOR DE MATERIAS DINÁMICO
Maneja configuración de materias por escuela y grado
"""

from typing import List, Dict, Optional, Any
from app.core.logging import get_logger
from app.core.config.school_config_manager import get_school_config_manager

class MateriaManager:
    """
    🎓 GESTOR DE MATERIAS DINÁMICO
    
    Responsabilidades:
    - Obtener materias configuradas por grado
    - Validar estructura de calificaciones
    - Generar plantillas de calificaciones
    - Calcular promedios según configuración
    """
    
    def __init__(self, school_config_manager=None):
        self.logger = get_logger(__name__)
        self.school_config = school_config_manager or get_school_config_manager()
    
    def get_materias_for_grade(self, grado: int) -> List[str]:
        """
        🎯 OBTENER MATERIAS PARA UN GRADO ESPECÍFICO
        
        Args:
            grado: Número de grado (1-6 primaria, 1-3 secundaria, etc.)
            
        Returns:
            Lista de nombres de materias configuradas para ese grado
        """
        try:
            materias_config = self.school_config.get_config_value(
                "academic_info.materias_por_grado", {}
            )
            
            materias = materias_config.get(str(grado), [])
            
            if not materias:
                self.logger.warning(f"No hay materias configuradas para grado {grado}")
                # Fallback: materias básicas
                materias = self._get_default_materias_for_grade(grado)
            
            self.logger.info(f"📚 Materias para grado {grado}: {len(materias)} materias")
            return materias
            
        except Exception as e:
            self.logger.error(f"Error obteniendo materias para grado {grado}: {e}")
            return self._get_default_materias_for_grade(grado)
    
    def _get_default_materias_for_grade(self, grado: int) -> List[str]:
        """Materias por defecto si no hay configuración"""
        education_level = self.school_config.get_education_level().upper()
        
        if education_level == "PRIMARIA":
            if grado <= 2:
                return ["Matemáticas", "Español", "Conocimiento del Medio"]
            else:
                return ["Matemáticas", "Español", "Ciencias Naturales", "Historia"]
        elif education_level == "SECUNDARIA":
            return ["Matemáticas", "Español", "Ciencias", "Historia", "Geografía"]
        else:
            return ["Área 1", "Área 2", "Área 3"]
    
    def validate_calificaciones_structure(self, grado: int, calificaciones: List[Dict]) -> Dict[str, Any]:
        """
        ✅ VALIDAR ESTRUCTURA DE CALIFICACIONES
        
        Args:
            grado: Grado del alumno
            calificaciones: Lista de calificaciones a validar
            
        Returns:
            Dict con resultado de validación y detalles
        """
        try:
            materias_esperadas = set(self.get_materias_for_grade(grado))
            materias_recibidas = set(cal.get('nombre', cal.get('materia', '')) for cal in calificaciones)
            
            # Verificar materias faltantes y extras
            materias_faltantes = materias_esperadas - materias_recibidas
            materias_extras = materias_recibidas - materias_esperadas
            
            is_valid = len(materias_faltantes) == 0
            
            result = {
                "is_valid": is_valid,
                "materias_esperadas": list(materias_esperadas),
                "materias_recibidas": list(materias_recibidas),
                "materias_faltantes": list(materias_faltantes),
                "materias_extras": list(materias_extras),
                "total_esperadas": len(materias_esperadas),
                "total_recibidas": len(materias_recibidas)
            }
            
            if is_valid:
                self.logger.info(f"✅ Calificaciones válidas para grado {grado}")
            else:
                self.logger.warning(f"⚠️ Calificaciones incompletas para grado {grado}: faltan {materias_faltantes}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validando calificaciones para grado {grado}: {e}")
            return {
                "is_valid": False,
                "error": str(e),
                "materias_esperadas": [],
                "materias_recibidas": []
            }
    
    def generate_empty_calificaciones_template(self, grado: int) -> List[Dict]:
        """
        📋 GENERAR PLANTILLA VACÍA DE CALIFICACIONES
        
        Args:
            grado: Grado para el cual generar la plantilla
            
        Returns:
            Lista de diccionarios con estructura de calificaciones vacía
        """
        try:
            materias = self.get_materias_for_grade(grado)
            periodos = self.school_config.get_config_value(
                "academic_info.evaluacion_config.periodos", 
                ["Periodo 1", "Periodo 2", "Periodo 3"]
            )
            
            calificaciones = []
            for materia in materias:
                cal_materia = {
                    "nombre": materia,
                    "materia": materia  # Alias para compatibilidad
                }
                
                # Agregar campos por periodo
                for i, periodo in enumerate(periodos, 1):
                    cal_materia[f"periodo_{i}"] = None
                
                # Campo de promedio
                cal_materia["promedio"] = None
                
                calificaciones.append(cal_materia)
            
            self.logger.info(f"📋 Plantilla generada para grado {grado}: {len(calificaciones)} materias")
            return calificaciones
            
        except Exception as e:
            self.logger.error(f"Error generando plantilla para grado {grado}: {e}")
            return []
    
    def calculate_promedio_materia(self, calificacion_materia: Dict) -> Optional[float]:
        """
        🧮 CALCULAR PROMEDIO DE UNA MATERIA
        
        Args:
            calificacion_materia: Dict con calificaciones de una materia
            
        Returns:
            Promedio calculado o None si no se puede calcular
        """
        try:
            periodos = self.school_config.get_config_value(
                "academic_info.evaluacion_config.periodos", 
                ["Periodo 1", "Periodo 2", "Periodo 3"]
            )
            
            calificaciones_validas = []
            for i in range(1, len(periodos) + 1):
                cal = calificacion_materia.get(f"periodo_{i}")
                if cal is not None and isinstance(cal, (int, float)) and cal > 0:
                    calificaciones_validas.append(float(cal))
            
            if len(calificaciones_validas) > 0:
                promedio = sum(calificaciones_validas) / len(calificaciones_validas)
                
                # Aplicar redondeo según configuración
                decimales = self.school_config.get_config_value(
                    "academic_info.evaluacion_config.escala_calificaciones.decimales", 1
                )
                
                return round(promedio, decimales)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculando promedio de materia: {e}")
            return None
    
    def get_evaluation_config(self) -> Dict[str, Any]:
        """
        ⚙️ OBTENER CONFIGURACIÓN DE EVALUACIÓN
        
        Returns:
            Dict con configuración de evaluación (periodos, escala, etc.)
        """
        return self.school_config.get_config_value(
            "academic_info.evaluacion_config",
            {
                "periodos": ["Periodo 1", "Periodo 2", "Periodo 3"],
                "escala_calificaciones": {
                    "minima": 5.0,
                    "maxima": 10.0,
                    "aprobatoria": 6.0,
                    "decimales": 1
                },
                "mostrar_promedio_general": True,
                "calcular_promedio_automatico": True
            }
        )


# 🌟 INSTANCIA GLOBAL
_materia_manager = None

def get_materia_manager() -> MateriaManager:
    """
    Obtiene la instancia global del MateriaManager
    
    Returns:
        Instancia del MateriaManager
    """
    global _materia_manager
    
    if _materia_manager is None:
        _materia_manager = MateriaManager()
    
    return _materia_manager
```

---

## 🔧 **PASO 3: INTEGRAR CON SISTEMA EXISTENTE**

### **3.1 Actualizar SchoolConfigManager**

```python
# Agregar métodos para materias en app/core/config/school_config_manager.py

def get_materias_por_grado(self) -> Dict[str, List[str]]:
    """Obtiene configuración de materias por grado"""
    return self.get_config_value("academic_info.materias_por_grado", {})

def get_materias_for_grade(self, grado: int) -> List[str]:
    """Obtiene materias para un grado específico"""
    materias_config = self.get_materias_por_grado()
    return materias_config.get(str(grado), [])

def get_evaluation_config(self) -> Dict:
    """Obtiene configuración de evaluación"""
    return self.get_config_value("academic_info.evaluacion_config", {})

def get_periodos_evaluacion(self) -> List[str]:
    """Obtiene periodos de evaluación configurados"""
    return self.get_evaluation_config().get("periodos", ["Periodo 1", "Periodo 2", "Periodo 3"])
```

### **3.2 Actualizar validaciones en ConstanciaProcessor**

```python
# En app/core/ai/interpretation/student_query/constancia_processor.py

def _validate_calificaciones_with_config(self, grado: int, calificaciones: List[Dict]) -> bool:
    """Validar calificaciones usando configuración dinámica"""
    from app.core.config.materia_manager import get_materia_manager
    
    materia_manager = get_materia_manager()
    validation_result = materia_manager.validate_calificaciones_structure(grado, calificaciones)
    
    if not validation_result["is_valid"]:
        self.logger.warning(f"Calificaciones no válidas: {validation_result}")
        return False
    
    return True
```

---

## 🎯 **RESULTADO ESPERADO**

### **✅ SISTEMA COMPLETAMENTE CONFIGURABLE**

1. **🏫 Por Escuela**: Cada escuela define sus materias
2. **📚 Por Grado**: Materias específicas para cada grado  
3. **📊 Por Nivel**: Primaria, Secundaria, Preescolar
4. **⚙️ Evaluación**: Periodos y escalas configurables

### **🚀 MIGRACIÓN FÁCIL**

```bash
# Para nueva escuela secundaria:
# 1. Copiar school_config.json
# 2. Cambiar education_level a "SECUNDARIA"
# 3. Configurar materias_por_grado para grados 1-3
# 4. ¡Listo! Sistema adaptado automáticamente
```

**¿Empezamos implementando esto? Es la base para hacer el sistema 100% adaptable.** 🎓
