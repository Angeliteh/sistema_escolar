# 🎯 ESTRUCTURA DEL PROYECTO LIMPIO - ENFOQUE DESARROLLO

## 📁 ESTRUCTURA OPTIMIZADA PARA DESARROLLO
```
constancias_system/                 # Proyecto principal (limpio)
├── 📄 simple_launcher.py           # Launcher principal
├── 📄 ai_chat.py                   # 🎯 INTERFAZ IA (FOCO)
├── 📄 main_qt.py                   # Interfaz tradicional
├── 📄 school_config.json           # Configuración
├── 📄 version.json                 # Versión
├── 📄 requirements.txt             # Dependencias
├── 📄 ENFOQUE_DESARROLLO.md        # Esta documentación
│
├── 📁 app/                         # Código principal
│   ├── 📁 core/                    # Núcleo del sistema
│   │   ├── chat_engine.py          # 🎯 MOTOR DE CHAT IA
│   │   ├── database_manager.py     # Gestión de BD
│   │   ├── school_config.py        # Configuración
│   │   ├── pdf_generator.py        # Generación PDFs
│   │   └── executable_paths.py     # Rutas dinámicas
│   │
│   ├── 📁 data/                    # Modelos y repositorios
│   ├── 📁 services/                # Servicios de negocio
│   └── 📁 ui/                      # Interfaces
│       ├── 📁 ai_chat/             # 🎯 INTERFAZ CHAT IA
│       │   ├── chat_window.py      # Ventana principal
│       │   ├── chat_interface.py   # Lógica de chat
│       │   ├── message_widget.py   # Widgets de mensajes
│       │   └── styles/             # 🎨 ESTILOS (MEJORAS)
│       ├── menu_principal.py       # Interfaz tradicional
│       ├── alumno_ui.py           # Gestión alumnos
│       ├── buscar_ui.py           # Búsqueda
│       ├── transformar_ui.py      # Transformación PDFs
│       └── pdf_viewer.py          # Visor PDFs
│
├── 📁 resources/                   # Recursos del sistema
│   ├── 📁 data/alumnos.db         # Base de datos
│   ├── 📁 templates/              # Plantillas HTML
│   └── 📁 images/                 # Imágenes y logos
│
└── 📁 logs/                       # Logs del sistema

../constancias_builds/              # Builds y distribución (EXTERNO)
└── v2.0.0_YYYYMMDD_HHMM/
    ├── installer/                  # Instalador profesional
    ├── dist/                      # Ejecutable portable
    ├── GUIA_COMPLETA_EJECUTABLES.md
    ├── RESUMEN_EJECUTIVO.md
    └── BUILD_INFO.md
```

## 🎯 ENFOQUE ACTUAL: MEJORAS DEL CHAT IA

### 🎨 PRIORIDADES DE DESARROLLO
1. **Mejoras estéticas** del chat IA
2. **Optimizaciones** de rendimiento
3. **Experiencia de usuario** mejorada

### 📋 ARCHIVOS CLAVE PARA MODIFICAR
- `app/ui/ai_chat/chat_window.py` - Ventana principal
- `app/ui/ai_chat/message_widget.py` - Widgets de mensajes
- `app/core/chat_engine.py` - Motor de chat
- `app/ui/ai_chat/styles/` - Estilos (crear)

## ✅ PROYECTO OPTIMIZADO
- **Tamaño reducido** - Sin archivos de build
- **Indexado rápido** - Solo código fuente
- **Enfoque claro** - Desarrollo del chat IA
- **Builds externos** - Organizados por versión

---

**🎯 LISTO PARA DESARROLLO ENFOCADO EN CHAT IA** 🚀
