# Sistema de Constancias Escolares v2.0

## 🚀 Inicio Rápido

### Para Desarrollo:
```bash
python dev_launcher.py
```

### Para Producción:
```bash
python hybrid_launcher.py
```

### Para Generar Sistemas Personalizados:
```bash
python system_builder_ui.py
```

## 📁 Estructura del Proyecto

```
constancias_system/
├── 📱 APLICACIONES PRINCIPALES
│   ├── hybrid_launcher.py          # Launcher principal (producción)
│   ├── dev_launcher.py             # Launcher desarrollo
│   ├── ai_chat.py                  # Interfaz con IA
│   ├── main_qt.py                  # Interfaz tradicional
│   ├── database_admin.py           # Administración BD
│   └── system_builder_ui.py        # Generador de sistemas
│
├── 📁 app/                         # Código fuente principal
│   ├── core/                       # Núcleo del sistema
│   ├── data/                       # Modelos y repositorios
│   ├── services/                   # Lógica de negocio
│   └── ui/                         # Interfaces de usuario
│
├── 📁 resources/                   # Recursos del sistema
│   ├── data/                       # Base de datos
│   ├── templates/                  # Plantillas de constancias
│   └── images/                     # Imágenes y logos
│
├── 📁 docs/                        # Documentación
│   ├── architecture/               # Documentación técnica
│   ├── development/                # Guías de desarrollo
│   └── commercial/                 # Información comercial
│
├── 📁 testing/                     # Pruebas del sistema
│   ├── unit/                       # Pruebas unitarias
│   └── integration/                # Pruebas de integración
│
├── 📁 scripts/                     # Scripts de utilidad
│   ├── development/                # Scripts de desarrollo
│   └── maintenance/                # Scripts de mantenimiento
│
├── 📁 logs/                        # Logs del sistema
│
├── school_config.json              # Configuración de escuela
├── version.json                    # Información de versión
└── requirements.txt                # Dependencias Python
```

## ⚙️ Configuración

El sistema se configura automáticamente la primera vez que se ejecuta.

## 🏭 Generación de Sistemas Comerciales

Para generar sistemas personalizados para otras escuelas:

1. **Abrir System Builder:**
   ```bash
   python system_builder_ui.py
   ```

2. **Llenar datos de la escuela**

3. **Generar sistema personalizado**

4. **Entregar archivo ZIP al cliente**

## 💼 Valor Comercial

- **Sistema Portable:** $199-299 USD
- **Sistema Ejecutable:** $399-499 USD  
- **Sistema con Instalador:** $599-799 USD

## 🧪 Pruebas

```bash
# Pruebas unitarias
python testing/unit/test_system_detector.py

# Pruebas de integración
python testing/integration/test_launcher_fixes.py
```

## 📚 Documentación

La documentación completa está en `docs/`:
- **Arquitectura:** `docs/architecture/`
- **Desarrollo:** `docs/development/`
- **Comercial:** `docs/commercial/`

---

**Sistema de Constancias Escolares v2.0**  
*Desarrollado con arquitectura híbrida y IA integrada*
