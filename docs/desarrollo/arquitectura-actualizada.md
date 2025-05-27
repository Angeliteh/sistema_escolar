# 🏗️ Arquitectura del Sistema - Estado Actual

## 📋 **Resumen Ejecutivo**

El Sistema de Constancias Escolares implementa una **arquitectura limpia y modular** basada en patrones de diseño empresariales, con separación clara de responsabilidades y alta mantenibilidad.

---

## 🎯 **Principios Arquitectónicos**

### **1. Separación de Responsabilidades**
- **UI Layer**: Solo manejo de interfaz de usuario
- **Service Layer**: Lógica de negocio centralizada
- **Repository Layer**: Acceso a datos abstraído
- **Core Layer**: Funcionalidades centrales del sistema

### **2. Inversión de Dependencias**
- Las capas superiores no dependen de las inferiores
- Uso de interfaces y abstracciones
- Inyección de dependencias centralizada

### **3. Principio Abierto/Cerrado**
- Extensible para nuevas funcionalidades
- Cerrado para modificaciones en código existente
- Uso de patrones Strategy y Factory

---

## 🏛️ **Arquitectura en Capas**

```
┌─────────────────────────────────────────────────────────┐
│                    UI LAYER (PyQt5)                    │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │   ChatWindow    │  │    PDFPanel     │             │
│  │                 │  │                 │             │
│  │ - Chat con IA   │  │ - Transformación│             │
│  │ - Comandos      │  │ - Vista previa  │             │
│  │ - Resultados    │  │ - Carga de PDFs │             │
│  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                  SERVICE LAYER                          │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │ ConstanciaService│  │  AlumnoService  │             │
│  │                 │  │                 │             │
│  │ - Generación    │  │ - Búsqueda      │             │
│  │ - Transformación│  │ - Gestión CRUD  │             │
│  │ - Validación    │  │ - Validaciones  │             │
│  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   CORE LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │  PDFExtractor   │  │  PDFGenerator   │             │
│  │                 │  │                 │             │
│  │ - Extracción    │  │ - Generación    │             │
│  │ - Parsing       │  │ - Plantillas    │             │
│  │ - Validación    │  │ - Formateo      │             │
│  └─────────────────┘  └─────────────────┘             │
│                                                         │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │  GeminiClient   │  │ ServiceProvider │             │
│  │                 │  │                 │             │
│  │ - IA Gemini     │  │ - DI Container  │             │
│  │ - Interpretación│  │ - Configuración │             │
│  │ - Contexto      │  │ - Logging       │             │
│  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                REPOSITORY LAYER                         │
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │ AlumnoRepository│  │CalificacionRepo │             │
│  │                 │  │                 │             │
│  │ - CRUD Alumnos  │  │ - CRUD Notas    │             │
│  │ - Búsquedas     │  │ - Cálculos      │             │
│  │ - Validaciones  │  │ - Estadísticas  │             │
│  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                  DATABASE LAYER                         │
│                    SQLite Database                      │
│                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   alumnos   │ │calificaciones│ │datos_escolares│     │
│  │             │ │             │ │             │      │
│  │ - id        │ │ - id        │ │ - id        │      │
│  │ - nombre    │ │ - alumno_id │ │ - alumno_id │      │
│  │ - curp      │ │ - materia   │ │ - grado     │      │
│  │ - ...       │ │ - periodo   │ │ - grupo     │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 **Patrones de Diseño Implementados**

### **1. Repository Pattern**
```python
class AlumnoRepository:
    """Abstrae el acceso a datos de alumnos"""
    
    def buscar_por_nombre(self, nombre: str) -> List[Alumno]:
        """Búsqueda flexible por nombre"""
        
    def buscar_por_curp(self, curp: str) -> Optional[Alumno]:
        """Búsqueda exacta por CURP"""
        
    def obtener_por_criterios(self, **criterios) -> List[Alumno]:
        """Búsqueda avanzada por múltiples criterios"""
```

**Beneficios:**
- Abstrae la lógica de acceso a datos
- Facilita testing con mocks
- Permite cambiar BD sin afectar lógica de negocio

### **2. Service Layer Pattern**
```python
class ConstanciaService:
    """Centraliza la lógica de negocio de constancias"""
    
    def generar_constancia(self, tipo: str, alumno_id: int, **opciones):
        """Orquesta la generación completa"""
        
    def transformar_pdf(self, archivo_pdf: str, tipo_destino: str):
        """Maneja la transformación de PDFs"""
```

**Beneficios:**
- Centraliza lógica de negocio
- Coordina múltiples repositorios
- Mantiene transacciones y consistencia

### **3. Strategy Pattern**
```python
class InterpretadorComandos:
    """Estrategia base para interpretación"""
    
class StudentQueryInterpreter(InterpretadorComandos):
    """Estrategia para consultas de alumnos"""
    
class PDFTransformInterpreter(InterpretadorComandos):
    """Estrategia para transformación de PDFs"""
```

**Beneficios:**
- Algoritmos intercambiables
- Fácil extensión de funcionalidades
- Separación de responsabilidades

### **4. Dependency Injection**
```python
class ServiceProvider:
    """Container de inyección de dependencias"""
    
    @staticmethod
    def get_alumno_service() -> AlumnoService:
        return AlumnoService(
            alumno_repo=ServiceProvider.get_alumno_repository(),
            logger=ServiceProvider.get_logger()
        )
```

**Beneficios:**
- Bajo acoplamiento
- Fácil testing
- Configuración centralizada

---

## 🤖 **Arquitectura del Sistema de IA**

### **Flujo de Procesamiento de Comandos**
```
Usuario escribe comando
         │
         ▼
┌─────────────────────┐
│  Master Interpreter │ ← Detecta intención principal
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Intention Detection │ ← Clasifica tipo de comando
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│Specialized Interpreter│ ← Procesa comando específico
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│  Command Executor   │ ← Ejecuta acción
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Response Format   │ ← Formatea respuesta
└─────────────────────┘
```

### **Interpretadores Especializados**

#### **StudentQueryInterpreter**
- **Propósito**: Consultas y búsquedas de alumnos
- **Comandos**: "Busca alumno...", "Muestra estudiantes..."
- **Capacidades**: Búsqueda flexible, criterios múltiples

#### **ConstanciaInterpreter**
- **Propósito**: Generación de constancias
- **Comandos**: "Genera constancia...", "Crea certificado..."
- **Capacidades**: Detección de tipo, opciones de foto

#### **PDFTransformInterpreter**
- **Propósito**: Transformación de documentos
- **Comandos**: "Transforma PDF...", "Convierte a..."
- **Capacidades**: Detección de formato, opciones avanzadas

#### **HelpInterpreter**
- **Propósito**: Sistema de ayuda
- **Comandos**: "Ayuda...", "¿Cómo...?", "¿Qué puedo...?"
- **Capacidades**: Contexto sensible, ejemplos dinámicos

---

## 📊 **Gestión de Estado y Contexto**

### **Context Manager**
```python
class ContextManager:
    """Gestiona el contexto conversacional"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_context = {}
        self.user_preferences = {}
    
    def add_interaction(self, user_input: str, ai_response: str):
        """Registra interacción para contexto"""
    
    def get_relevant_context(self, current_input: str) -> dict:
        """Obtiene contexto relevante para la consulta actual"""
```

### **Estados de la Aplicación**
- **PDF_LOADED**: PDF cargado, esperando comando de transformación
- **CONSTANCIA_GENERATED**: Constancia generada, opciones de guardado
- **SEARCH_RESULTS**: Resultados de búsqueda, opciones de acción
- **IDLE**: Estado normal, esperando comando

---

## 🔄 **Flujos de Trabajo Principales**

### **1. Flujo de Transformación de PDF**
```
1. Usuario carga PDF → PDFPanel.load_pdf()
2. Extracción automática → PDFExtractor.extract_data()
3. Usuario solicita transformación → Chat command
4. Interpretación → PDFTransformInterpreter.process()
5. Generación → PDFGenerator.generate()
6. Vista previa → PDFPanel.show_preview()
7. Guardado opcional → AlumnoService.save()
```

### **2. Flujo de Búsqueda de Alumnos**
```
1. Usuario escribe búsqueda → Chat input
2. Interpretación → StudentQueryInterpreter.process()
3. Búsqueda → AlumnoRepository.search()
4. Formateo → ResponseFormatter.format_results()
5. Mostrar resultados → ChatWindow.display_results()
```

### **3. Flujo de Generación de Constancias**
```
1. Usuario solicita constancia → Chat command
2. Interpretación → ConstanciaInterpreter.process()
3. Validación → AlumnoService.validate()
4. Generación → ConstanciaService.generate()
5. Vista previa → PDFPanel.show_constancia()
6. Opciones de guardado → User choice
```

---

## 🛡️ **Manejo de Errores y Logging**

### **Estrategia de Manejo de Errores**
```python
class SystemException(Exception):
    """Excepción base del sistema"""
    
class ValidationError(SystemException):
    """Error de validación de datos"""
    
class AIServiceError(SystemException):
    """Error en servicios de IA"""
    
class DatabaseError(SystemException):
    """Error de base de datos"""
```

### **Sistema de Logging Profesional**
- **Rotación automática**: Archivos de máximo 10MB
- **Múltiples niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Formato consistente**: `[TIMESTAMP] [LEVEL] [MODULE] - MESSAGE`
- **Configuración centralizada**: Via `Config.LOGGING`

---

## 📈 **Escalabilidad y Rendimiento**

### **Optimizaciones Implementadas**
- **Lazy Loading**: Carga de datos bajo demanda
- **Connection Pooling**: Reutilización de conexiones BD
- **Caching**: Cache de resultados frecuentes
- **Async Operations**: Operaciones no bloqueantes donde es posible

### **Preparación para Escalabilidad**
- **Modular Architecture**: Fácil distribución en microservicios
- **Database Abstraction**: Migración a BD más robustas
- **API Ready**: Interfaces preparadas para exposición REST
- **Configuration Management**: Configuración externa

---

## 🔧 **Herramientas de Desarrollo**

### **Testing Framework**
- **pytest**: Framework principal de testing
- **unittest.mock**: Mocking para testing aislado
- **coverage**: Medición de cobertura de código
- **fixtures**: Datos de prueba reutilizables

### **Quality Assurance**
- **flake8**: Linting de código Python
- **black**: Formateo automático de código
- **mypy**: Verificación de tipos estáticos
- **pre-commit**: Hooks de calidad pre-commit

### **Documentation**
- **Sphinx**: Generación de documentación
- **docstrings**: Documentación inline
- **type hints**: Tipado para mejor documentación
- **README**: Documentación de usuario

---

**🏗️ Arquitectura robusta, escalable y mantenible - Lista para producción! 🚀**
