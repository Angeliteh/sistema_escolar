# 🎓 Sistema de Constancias Escolares

Sistema integral para la gestión y generación de constancias escolares con inteligencia artificial integrada y transformación automática de PDFs.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-green.svg)](https://pypi.org/project/PyQt5/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI%20Powered-orange.svg)](https://ai.google.dev/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## ✨ **Características Principales**

### 🤖 **Inteligencia Artificial Avanzada**
- **Chat conversacional** con Google Gemini 2.0 Flash
- **Detección automática** de intenciones y comandos
- **Contexto conversacional** mantenido durante toda la sesión
- **Búsqueda inteligente** por nombre parcial, CURP o criterios específicos

### 📄 **Transformación de PDFs**
- **Drag & Drop** intuitivo para cargar PDFs
- **Extracción automática** de datos de constancias existentes
- **Transformación a cualquier formato**: estudios, calificaciones, traslado
- **Vista previa dual** (original y transformado)
- **Guardado directo** en base de datos desde la interfaz

### 🗄️ **Gestión Completa de Datos**
- **Base de datos SQLite** con estructura optimizada
- **Gestión de alumnos** con datos personales y escolares
- **Sistema de calificaciones** por periodos y materias
- **Fotos de alumnos** integradas automáticamente

### 📊 **Múltiples Formatos de Constancias**
- **Constancias de Estudios**: Datos básicos del alumno
- **Constancias de Calificaciones**: Incluye notas académicas
- **Constancias de Traslado**: Para cambio de escuela
- **Con/sin foto**: Opción automática según disponibilidad

### 🎨 **Interfaz Moderna**
- **Panel contraíble** para transformación de PDFs
- **Chat con burbujas** diferenciadas por usuario/asistente
- **Vista previa integrada** de PDFs y constancias
- **Botones contextuales** que cambian según la situación

## 🚀 **Instalación y Configuración**

### **Prerrequisitos**
- **Python 3.8+**
- **wkhtmltopdf** (para generación de PDFs de alta calidad)
- **API Key de Google Gemini**

### **Instalación Paso a Paso**

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd constancias_system
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Instalar wkhtmltopdf**:
   - **Windows**: Descargar desde [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
   - **Linux**: `sudo apt-get install wkhtmltopdf`
   - **Mac**: `brew install wkhtmltopdf`

5. **Configurar variables de entorno**:
   ```bash
   # Crear archivo .env en la raíz del proyecto
   GEMINI_API_KEY=tu_api_key_de_google_gemini
   ```

6. **Ejecutar el sistema**:
   ```bash
   python ai_chat.py
   ```

## 📖 **Guía de Uso**

### 🤖 **Comandos de IA Disponibles**

#### **Gestión de Alumnos**
```bash
# Buscar alumnos
"Busca al alumno Juan Pérez"
"Muestra alumnos de sexto grado grupo A"
"Busca CURP ABCD123456HDFRRL01"

# Registrar alumnos
"Registra un nuevo alumno con nombre Juan Pérez, CURP..."

# Ver detalles
"Muestra los detalles completos de María García"
```

#### **Generación de Constancias**
```bash
# Constancias básicas
"Genera constancia de estudios para Juan Pérez"
"Crea constancia de calificaciones para María García"
"Genera constancia de traslado con foto para Pedro López"

# Con opciones específicas
"Constancia de calificaciones con foto para Juan"
"Constancia de estudios sin foto para María"
```

#### **Transformación de PDFs**
```bash
# Después de cargar un PDF en el panel:
"transforma este PDF a constancia de estudios"
"convierte a constancia de calificaciones con foto"
"transforma a constancia de traslado"
```

### 📄 **Flujo de Transformación de PDFs**

1. **Cargar PDF**:
   - Haz clic en "🔄 Transformación de PDF" en la barra superior
   - Arrastra y suelta un PDF en el área designada

2. **Extraer Datos**:
   - El sistema extrae automáticamente los datos del PDF
   - Haz clic en "📋 Ver Datos Extraídos" para revisar

3. **Transformar**:
   - Escribe el comando de transformación en el chat
   - Ejemplo: "transforma este PDF a constancia de calificaciones con foto"

4. **Vista Previa**:
   - Se genera una vista previa del PDF transformado
   - Puedes alternar entre original y transformado

5. **Guardar** (opcional):
   - En "📋 Ver Datos", marca "💾 Guardar estos datos en la BD"
   - Haz clic en "💾 Guardar en BD" para registrar al alumno

### 🔍 **Búsqueda Avanzada**

El sistema soporta búsquedas flexibles:
- **Por nombre parcial**: "Juan", "Pérez", "Juan Pé"
- **Por CURP completa o parcial**: "ABCD123456"
- **Por criterios escolares**: "sexto grado", "grupo A", "turno matutino"
- **Combinaciones**: "alumnos de quinto grado grupo B"

## 🏗️ **Arquitectura del Sistema**

### **Patrón de Arquitectura**
- **Presentación**: PyQt5 con componentes modulares
- **Aplicación**: Servicios con lógica de negocio
- **Dominio**: Entidades y reglas de negocio
- **Infraestructura**: Repositorios y acceso a datos

### **Componentes Principales**

#### **Frontend (UI)**
- `ChatWindow`: Interfaz principal con chat de IA
- `PDFPanel`: Panel de transformación de PDFs
- `PDFViewer`: Visor de PDFs integrado

#### **Backend (Services)**
- `ConstanciaService`: Generación y transformación de constancias
- `AlumnoService`: Gestión de alumnos
- `CalificacionService`: Gestión de calificaciones

#### **Core (Lógica de Negocio)**
- `PDFExtractor`: Extracción de datos de PDFs
- `PDFGenerator`: Generación de PDFs con plantillas
- `GeminiClient`: Cliente para IA de Google Gemini

#### **Database (Persistencia)**
- `AlumnoRepository`: Acceso a datos de alumnos
- `CalificacionRepository`: Acceso a datos de calificaciones
- `DatosEscolaresRepository`: Acceso a datos escolares

## 📁 **Estructura Detallada del Proyecto**

```
constancias_system/
├── app/
│   ├── core/                 # Lógica de negocio central
│   │   ├── pdf_extractor.py  # Extracción de datos de PDFs
│   │   ├── pdf_generator.py  # Generación de PDFs
│   │   ├── gemini_client.py  # Cliente de IA Gemini
│   │   └── service_provider.py # Inyección de dependencias
│   ├── services/             # Servicios de aplicación
│   │   ├── constancia_service.py # Lógica de constancias
│   │   ├── alumno_service.py     # Lógica de alumnos
│   │   └── calificacion_service.py # Lógica de calificaciones
│   ├── ui/                   # Interfaz de usuario
│   │   ├── ai_chat/          # Componentes del chat
│   │   │   ├── chat_window.py    # Ventana principal
│   │   │   ├── pdf_panel.py      # Panel de PDFs
│   │   │   └── pdf_viewer.py     # Visor de PDFs
│   │   └── components/       # Componentes reutilizables
│   ├── database/             # Acceso a datos
│   │   ├── repositories/     # Repositorios
│   │   ├── models/          # Modelos de datos
│   │   └── connection.py    # Conexión a BD
│   └── ai/                  # Módulos de IA
│       ├── interpreters/    # Intérpretes de comandos
│       └── context/         # Gestión de contexto
├── docs/                    # Documentación completa
│   ├── desarrollo/          # Documentación técnica
│   ├── usuario/            # Guías de usuario
│   └── api/                # Documentación de API
├── resources/              # Recursos del sistema
│   ├── templates/          # Plantillas HTML
│   ├── logos/             # Logotipos
│   ├── photos/            # Fotos de alumnos
│   └── examples/          # PDFs de ejemplo
├── tests/                 # Pruebas automatizadas
│   ├── unit/             # Pruebas unitarias
│   ├── integration/      # Pruebas de integración
│   └── fixtures/         # Datos de prueba
├── logs/                 # Archivos de log
├── .env                  # Variables de entorno
├── requirements.txt      # Dependencias Python
└── ai_chat.py           # Punto de entrada principal
```

## 🔧 **Configuración Avanzada**

### **Variables de Entorno (.env)**
```bash
# API de Google Gemini
GEMINI_API_KEY=tu_api_key_aqui

# Configuración de Base de Datos (opcional)
DATABASE_PATH=./database/constancias.db

# Configuración de Logging (opcional)
LOG_LEVEL=INFO
LOG_FILE=./logs/system.log

# Configuración de wkhtmltopdf (opcional)
WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf
```

### **Personalización de Plantillas**
Las plantillas HTML están en `resources/templates/`:
- `constancia_estudio.html`: Plantilla para constancias de estudios
- `constancia_calificaciones.html`: Plantilla para constancias con calificaciones
- `constancia_traslado.html`: Plantilla para constancias de traslado

## 🧪 **Testing**

### **Ejecutar Pruebas**
```bash
# Todas las pruebas
python -m pytest tests/

# Pruebas específicas
python -m pytest tests/unit/
python -m pytest tests/integration/

# Con cobertura
python -m pytest --cov=app tests/
```

### **Pruebas Manuales**
El sistema incluye PDFs de ejemplo en `resources/examples/` para probar la funcionalidad de transformación.

## 📊 **Monitoreo y Logs**

El sistema genera logs detallados en `logs/`:
- **system.log**: Log general del sistema
- **gemini.log**: Logs específicos de la IA
- **database.log**: Logs de operaciones de BD

## 🤝 **Contribuir al Proyecto**

### **Proceso de Contribución**
1. **Fork** el repositorio
2. **Crea una rama** para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. **Commit** tus cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. **Push** a la rama: `git push origin feature/nueva-funcionalidad`
5. **Abre un Pull Request**

### **Estándares de Código**
- Seguir PEP 8 para Python
- Documentar funciones y clases
- Incluir pruebas para nuevas funcionalidades
- Mantener cobertura de pruebas > 80%

### **Reportar Bugs**
Usa el sistema de Issues de GitHub incluyendo:
- Descripción detallada del problema
- Pasos para reproducir
- Logs relevantes
- Información del sistema

## 📄 **Licencia**

Este proyecto está bajo la **Licencia MIT** - ver el archivo [LICENSE](LICENSE) para detalles completos.

## 🆘 **Soporte**

- **Documentación**: Ver carpeta `docs/`
- **Issues**: GitHub Issues
- **Wiki**: GitHub Wiki del proyecto

---

**¡Sistema de Constancias Escolares - Transformando la gestión educativa con IA! 🎓✨**
