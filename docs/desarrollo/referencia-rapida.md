# ⚡ REFERENCIA RÁPIDA DE DESARROLLO

## 🎯 COMANDOS ESENCIALES

### **📝 LOGGING**
```python
# Importar y configurar
from app.core.logging import get_logger
self.logger = get_logger(__name__)

# Usar niveles apropiados
self.logger.debug("Información detallada")    # Solo desarrollo
self.logger.info("Evento importante")         # Flujo normal
self.logger.warning("Situación anómala")      # Advertencia
self.logger.error("Error funcional")          # Error que afecta
self.logger.critical("Error crítico")         # Sistema en peligro
```

### **⚙️ CONFIGURACIONES**
```python
# Acceder a configuraciones
from app.core.config import Config

# Configuraciones existentes
Config.INTERPRETATION['confidence_thresholds']['high']  # 0.8
Config.RESPONSES['greeting_phrases']                    # Lista de saludos
Config.GEMINI['primary_model']                         # "gemini-2.0-flash-exp"
Config.LOGGING['level']                                # "INFO"

# Agregar nuevas configuraciones
Config.MI_MODULO = {'key': 'value'}
```

### **🤖 GEMINI CLIENT**
```python
# Usar cliente centralizado
response = self.gemini_client.send_prompt_sync(prompt)

# Parsear respuesta JSON
import json
import re
json_match = re.search(r'\{.*\}', response, re.DOTALL)
if json_match:
    data = json.loads(json_match.group())
```

---

## 🏗️ ESTRUCTURA DE ARCHIVOS

### **📁 NUEVOS INTÉRPRETES**
```
app/core/ai/interpretation/
├── mi_interpreter.py          # Nuevo intérprete
├── base_interpreter.py        # Clase base (no modificar)
└── master_interpreter.py     # Registrar aquí
```

### **📁 SERVICIOS DE NEGOCIO**
```
app/services/
├── mi_service.py             # Nuevo servicio
├── alumno_service.py         # Existente
└── constancia_service.py     # Existente
```

### **📁 TESTS**
```
tests/
├── test_mi_interpreter.py    # Tests del intérprete
└── test_mi_service.py        # Tests del servicio
```

---

## 🔧 PATRONES COMUNES

### **🎯 DETECCIÓN DE PALABRAS CLAVE**
```python
def can_handle(self, context: InterpretationContext) -> bool:
    keywords = ['palabra1', 'palabra2', 'frase completa']
    user_lower = context.user_message.lower()
    return any(keyword in user_lower for keyword in keywords)
```

### **🎯 PROMPT ESTRUCTURADO**
```python
def _build_prompt(self, user_message):
    return f"""
    CONTEXTO: Sistema de constancias escolares
    TAREA: [Descripción específica]
    
    ENTRADA: "{user_message}"
    
    RESPONDE ÚNICAMENTE CON JSON:
    {{
        "campo1": "valor",
        "campo2": true/false,
        "confianza": 0.9
    }}
    """
```

### **🎯 MANEJO DE ERRORES**
```python
try:
    # Código principal
    result = self._process_request()
    self.logger.info("Operación exitosa")
    return result
except Exception as e:
    self.logger.error(f"Error en operación: {e}")
    return None
```

### **🎯 RESULTADO DE INTERPRETACIÓN**
```python
return InterpretationResult(
    action="nombre_accion",
    parameters={
        "mensaje": "Respuesta para el usuario",
        "datos": resultado_procesado,
        "metadata": {"timestamp": datetime.now().isoformat()}
    },
    confidence=0.9
)
```

---

## 📊 CONFIGURACIONES DISPONIBLES

### **🎯 INTERPRETATION**
```python
Config.INTERPRETATION = {
    'confidence_thresholds': {
        'high': 0.8,
        'medium': 0.6,
        'low': 0.4,
        'fallback': 0.2
    },
    'max_retries': 3,
    'timeout_seconds': 30
}
```

### **🎯 RESPONSES**
```python
Config.RESPONSES = {
    'greeting_phrases': ["¡Hola!", "Buenos días", ...],
    'success_phrases': ["Perfecto", "Excelente", ...],
    'error_messages': {
        'system_error': "Error del sistema",
        'not_found': "No encontrado",
        'invalid_input': "Entrada inválida"
    }
}
```

### **🎯 GEMINI**
```python
Config.GEMINI = {
    'primary_model': 'gemini-2.0-flash-exp',
    'fallback_model': 'gemini-1.5-flash',
    'temperature': 0.1,
    'max_tokens': 1000
}
```

---

## 🧪 TESTING RÁPIDO

### **🎯 TEST BÁSICO**
```python
def test_basic_functionality(self):
    # Arrange
    context = Mock()
    context.user_message = "test input"
    
    # Act
    result = self.interpreter.interpret(context)
    
    # Assert
    self.assertIsNotNone(result)
    self.assertEqual(result.action, "expected_action")
```

### **🎯 MOCK GEMINI**
```python
def setUp(self):
    self.mock_gemini = Mock()
    self.mock_gemini.send_prompt_sync.return_value = '{"key": "value"}'
    self.interpreter = MiInterpreter(self.mock_gemini)
```

### **🎯 TEST LOGGING**
```python
@patch('app.core.ai.interpretation.mi_interpreter.get_logger')
def test_logging(self, mock_get_logger):
    mock_logger = Mock()
    mock_get_logger.return_value = mock_logger
    
    # Test code here
    
    mock_logger.info.assert_called_with("Expected message")
```

---

## 🚀 COMANDOS DE DESARROLLO

### **🔍 DEBUGGING**
```bash
# Ver logs en tiempo real
tail -f logs/system.log

# Buscar errores
grep "ERROR" logs/system.log

# Filtrar por módulo
grep "mi_interpreter" logs/system.log
```

### **🧪 TESTING**
```bash
# Ejecutar tests específicos
python -m pytest tests/test_mi_interpreter.py

# Con cobertura
python -m pytest --cov=app tests/

# Solo tests que fallan
python -m pytest --lf
```

### **📊 VERIFICACIÓN**
```bash
# Verificar sintaxis
python -m py_compile app/core/ai/interpretation/mi_interpreter.py

# Verificar imports
python -c "from app.core.ai.interpretation.mi_interpreter import MiInterpreter"
```

---

## ❌ ERRORES COMUNES

### **🚫 NO HACER**
```python
# ❌ Usar prints
print("Debug info")

# ❌ Hardcodear configuraciones
threshold = 0.8

# ❌ No manejar errores
result = risky_operation()

# ❌ No usar logging
# Código sin logs
```

### **✅ HACER**
```python
# ✅ Usar logging
self.logger.debug("Debug info")

# ✅ Usar configuraciones
threshold = Config.MI_MODULO['threshold']

# ✅ Manejar errores
try:
    result = risky_operation()
except Exception as e:
    self.logger.error(f"Error: {e}")

# ✅ Logging apropiado
self.logger.info("Operación completada")
```

---

## 🎯 CHECKLIST RÁPIDO

### **✅ NUEVO INTÉRPRETE**
- [ ] Hereda de `BaseInterpreter`
- [ ] Implementa `can_handle()` y `interpret()`
- [ ] Usa `get_logger(__name__)`
- [ ] Configuraciones en `Config`
- [ ] Registrado en `MasterInterpreter`
- [ ] Tests unitarios creados

### **✅ CÓDIGO LIMPIO**
- [ ] Sin `print()` statements
- [ ] Manejo de errores con try/catch
- [ ] Logging en niveles apropiados
- [ ] Configuraciones centralizadas
- [ ] Documentación en docstrings

### **✅ INTEGRACIÓN**
- [ ] Funciona con Gemini client
- [ ] Respeta arquitectura existente
- [ ] No rompe funcionalidad existente
- [ ] Tests pasan correctamente

---

## 🔗 ENLACES ÚTILES

- **Guía Completa**: `docs/desarrollo/guia-desarrollo-estandarizada.md`
- **Plantillas**: `docs/desarrollo/plantillas-codigo.md`
- **Configuraciones**: `app/core/config.py`
- **Logging**: `app/core/logging/`
- **Tests**: `tests/`

**¡Con esta referencia tienes todo lo esencial al alcance!** ⚡
