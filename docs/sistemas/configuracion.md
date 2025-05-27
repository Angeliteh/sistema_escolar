# ⚙️ CONFIGURACIÓN CENTRALIZADA DEL SISTEMA

## 📋 RESUMEN
**Estado:** ✅ **IMPLEMENTADO Y EXPANDIDO**
**Configuraciones Centralizadas:** 6 categorías
**Valores Hardcodeados Eliminados:** 15+

---

## 🎯 OBJETIVO

Centralizar todas las configuraciones del sistema en un solo lugar para mejorar la mantenibilidad, flexibilidad y facilitar el despliegue en diferentes entornos.

---

## 🏗️ ESTRUCTURA DE CONFIGURACIÓN

### **Archivo Principal: app/core/config.py**

```python
from app.core.config import Config

# Acceso a cualquier configuración
window_size = Config.UI['main_window']
cleanup_days = Config.FILES['temp_cleanup_days']
ai_timeout = Config.AI['timeout_seconds']
```

---

## 📁 CATEGORÍAS DE CONFIGURACIÓN

### **1. 🖥️ CONFIGURACIÓN DE UI**
```python
Config.UI = {
    'main_window': {'min_width': 1200, 'min_height': 800},
    'search_window': {'min_width': 900, 'min_height': 700},
    'chat_window': {'min_width': 1000, 'min_height': 700},
    'menu_window': {'min_width': 1200, 'min_height': 800}
}
```

**Uso:**
```python
# En lugar de:
self.setMinimumSize(1200, 800)  # ❌ Hardcodeado

# Usar:
size = Config.UI['main_window']
self.setMinimumSize(size['min_width'], size['min_height'])  # ✅ Centralizado
```

### **2. 📁 CONFIGURACIÓN DE ARCHIVOS**
```python
Config.FILES = {
    'temp_cleanup_days': 3,
    'max_file_size_mb': 50,
    'allowed_extensions': ['.pdf', '.jpg', '.png'],
    'temp_file_patterns': ["*.html", "preview_*.pdf", "constancia_*.html"],
    'backup_interval_hours': 24
}
```

### **3. 🤖 CONFIGURACIÓN DE AI/LLM**
```python
Config.AI = {
    'max_context_length': 1000000,
    'fallback_confidence_threshold': 0.5,
    'retry_attempts': 3,
    'timeout_seconds': 30,
    'max_tokens': 4096
}
```

### **4. 🗄️ CONFIGURACIÓN DE BASE DE DATOS**
```python
Config.DATABASE = {
    'connection_timeout': 30,
    'max_connections': 10,
    'query_limit_default': 100,
    'backup_on_startup': True
}
```

### **5. 📄 CONFIGURACIÓN DE PDF**
```python
Config.PDF = {
    'wkhtmltopdf_paths': [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"/usr/local/bin/wkhtmltopdf",
        r"/usr/bin/wkhtmltopdf"
    ],
    'default_options': {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8'
    }
}
```

### **6. 📝 CONFIGURACIÓN DE LOGGING**
```python
Config.LOGGING = {
    'level': 'INFO',
    'max_file_size_mb': 10,
    'backup_count': 5,
    'console_enabled': True,
    'debug_mode': False
}
```

---

## 🔄 MIGRACIÓN REALIZADA

### **Valores Hardcodeados Eliminados:**

#### **1. Tamaños de Ventana:**
```python
# ANTES (disperso en múltiples archivos):
self.setMinimumSize(1200, 800)  # menu_principal.py
self.setMinimumSize(900, 700)   # buscar_ui.py

# DESPUÉS (centralizado):
size = Config.UI['main_window']
self.setMinimumSize(size['min_width'], size['min_height'])
```

#### **2. Configuración de Limpieza:**
```python
# ANTES:
clean_temp_files(max_age_days=3)  # main_qt.py
file_patterns = ["*.html", "preview_*.pdf"]  # utils.py

# DESPUÉS:
clean_temp_files(max_age_days=Config.FILES['temp_cleanup_days'])
patterns = Config.FILES['temp_file_patterns']
```

#### **3. Rutas de wkhtmltopdf:**
```python
# ANTES (hardcodeado en pdf_generator.py):
paths = [
    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe"
]

# DESPUÉS (centralizado):
paths = Config.PDF['wkhtmltopdf_paths']
```

---

## 🛠️ CONFIGURACIÓN PERSONALIZADA

### **Archivo config.json (Opcional):**
```json
{
    "SCHOOL_NAME": "Mi Escuela Personalizada",
    "UI": {
        "main_window": {"min_width": 1400, "min_height": 900}
    },
    "FILES": {
        "temp_cleanup_days": 7
    },
    "LOGGING": {
        "level": "DEBUG"
    }
}
```

### **Carga Automática:**
- El sistema carga automáticamente `config.json` si existe
- Sobrescribe valores por defecto con valores personalizados
- Mantiene valores por defecto para configuraciones no especificadas

---

## 📊 BENEFICIOS OBTENIDOS

### **Antes (Valores Dispersos):**
- ❌ **Configuraciones hardcodeadas** en múltiples archivos
- ❌ **Difícil mantenimiento** - cambios en muchos lugares
- ❌ **Sin flexibilidad** para diferentes entornos
- ❌ **Valores mágicos** sin documentación

### **Después (Centralizado):**
- ✅ **Una sola fuente de verdad** para configuraciones
- ✅ **Mantenimiento fácil** - cambios en un solo lugar
- ✅ **Flexibilidad total** para diferentes entornos
- ✅ **Configuraciones documentadas** y organizadas
- ✅ **Personalización fácil** con config.json

---

## 🚀 EJEMPLOS DE USO

### **1. Configurar Ventana:**
```python
from app.core.config import Config

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # Usar configuración centralizada
        size = Config.UI['main_window']
        self.setMinimumSize(size['min_width'], size['min_height'])
```

### **2. Configurar Limpieza de Archivos:**
```python
from app.core.config import Config

def limpiar_archivos_temporales():
    days = Config.FILES['temp_cleanup_days']
    patterns = Config.FILES['temp_file_patterns']
    
    for pattern in patterns:
        clean_files_by_pattern(pattern, max_age_days=days)
```

### **3. Configurar AI:**
```python
from app.core.config import Config

class AIClient:
    def __init__(self):
        self.timeout = Config.AI['timeout_seconds']
        self.max_retries = Config.AI['retry_attempts']
        self.max_tokens = Config.AI['max_tokens']
```

---

## 🔧 CONFIGURACIONES AVANZADAS

### **1. Configuración por Entorno:**
```python
# config_desarrollo.json
{
    "LOGGING": {"level": "DEBUG", "debug_mode": true},
    "AI": {"timeout_seconds": 60}
}

# config_produccion.json
{
    "LOGGING": {"level": "INFO", "console_enabled": false},
    "AI": {"timeout_seconds": 30}
}
```

### **2. Validación de Configuración:**
```python
def validate_config():
    """Valida que la configuración sea correcta"""
    assert Config.UI['main_window']['min_width'] > 0
    assert Config.FILES['temp_cleanup_days'] > 0
    assert Config.AI['timeout_seconds'] > 0
```

---

## ✅ VALIDACIÓN

### **Configuraciones Centralizadas:**
- ✅ **UI**: Tamaños de ventana centralizados
- ✅ **FILES**: Limpieza y patrones centralizados
- ✅ **AI**: Timeouts y límites centralizados
- ✅ **DATABASE**: Configuraciones de conexión
- ✅ **PDF**: Rutas y opciones centralizadas
- ✅ **LOGGING**: Sistema completo centralizado

### **Verificación:**
```python
# Verificar que las configuraciones están disponibles
from app.core.config import Config

print(f"UI Config: {Config.UI}")
print(f"Files Config: {Config.FILES}")
print(f"AI Config: {Config.AI}")
```

---

## 🎉 CONCLUSIÓN

**La configuración centralizada está completamente implementada y funcional.**

### **Logros:**
- ✅ **6 categorías** de configuración centralizadas
- ✅ **15+ valores hardcodeados** eliminados
- ✅ **Sistema flexible** para diferentes entornos
- ✅ **Configuración personalizada** con JSON
- ✅ **Mantenibilidad mejorada** significativamente

### **Impacto:**
- 🚀 **Despliegue más fácil** en diferentes entornos
- 🔧 **Mantenimiento simplificado** de configuraciones
- 📊 **Flexibilidad total** para personalización
- 🛡️ **Configuraciones documentadas** y organizadas

**¡El sistema está listo para producción con configuración de nivel empresarial!** 🎯
