# 🚀 GUÍA COMPLETA PARA GENERAR INSTALADOR PROFESIONAL

## 📋 RESUMEN DEL PROCESO

Tu sistema ya tiene **TODO CONFIGURADO** para generar un instalador profesional con Inno Setup. El proceso es muy sencillo:

## 🎯 PROCESO AUTOMÁTICO (RECOMENDADO)

### **Opción 1: Script Completo Automático**
```bash
python build_installer.py
```

**Lo que hace automáticamente:**
1. ✅ Verifica que Inno Setup esté instalado
2. ✅ Limpia builds anteriores
3. ✅ Genera ejecutable con PyInstaller
4. ✅ Prepara archivos del instalador
5. ✅ Compila instalador con Inno Setup
6. ✅ Verifica resultado final

**Resultado:** `installer/output/SistemaConstancias_Installer_v2.0.0.exe`

---

## 🔧 PROCESO MANUAL (PASO A PASO)

### **Paso 1: Instalar Inno Setup**
- Descargar desde: https://jrsoftware.org/isdl.php
- Instalar (es gratis y muy ligero)

### **Paso 2: Generar Ejecutable**
```bash
pyinstaller SistemaConstancias.spec
```
O si no tienes el .spec:
```bash
pyinstaller --onedir --windowed --name="SistemaConstancias" --icon="app/ui/resources/images/logos/logo_educacion.ico" simple_launcher.py
```

### **Paso 3: Preparar Instalador**
```bash
python prepare_installer.py
```

### **Paso 4: Compilar Instalador**
1. Abrir **Inno Setup Compiler**
2. Abrir archivo: `installer/SistemaConstancias.iss`
3. Presionar **F9** o **Build → Compile**

---

## 📁 ESTRUCTURA GENERADA

```
installer/
├── source/
│   ├── app/                    # Ejecutable completo
│   ├── dependencies/           # Visual C++ + wkhtmltopdf
│   ├── config/                # Archivos de configuración
│   └── resources/             # Recursos adicionales
├── scripts/
│   ├── license.txt            # Licencia del software
│   └── readme.txt             # Información para usuarios
├── output/
│   └── SistemaConstancias_Installer_v2.0.0.exe  # ¡INSTALADOR FINAL!
└── SistemaConstancias.iss     # Script de Inno Setup
```

---

## 🎯 CARACTERÍSTICAS DEL INSTALADOR

### ✅ **Instalación Automática de Dependencias:**
- **Visual C++ Redistributables** (para PyQt5)
- **wkhtmltopdf** (para generación de PDFs)

### ✅ **Configuración Profesional:**
- Instalación en `Program Files`
- Accesos directos en menú inicio y escritorio
- Desinstalador automático
- Detección y actualización de versiones anteriores

### ✅ **Múltiples Interfaces:**
- Acceso directo principal
- Acceso directo "Interfaz con IA"
- Acceso directo "Interfaz Tradicional"

### ✅ **Configuración de Usuario:**
- Archivos de configuración en `%APPDATA%`
- Preserva configuraciones en actualizaciones

---

## 🔍 VERIFICACIÓN DEL INSTALADOR

### **Probar en Máquina Limpia:**
1. Usar máquina virtual o PC sin el sistema instalado
2. Ejecutar el instalador
3. Verificar que se instalan todas las dependencias
4. Confirmar que la aplicación funciona correctamente

### **Verificar Funcionalidades:**
- ✅ Interfaz tradicional funciona
- ✅ Interfaz con IA funciona
- ✅ Generación de PDFs funciona
- ✅ Base de datos se crea correctamente
- ✅ Configuración se guarda correctamente

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### **Error: "No se encuentra dist/SistemaConstancias/"**
**Solución:** Ejecutar primero PyInstaller:
```bash
pyinstaller SistemaConstancias.spec
```

### **Error: "Inno Setup no encontrado"**
**Solución:** Instalar Inno Setup desde https://jrsoftware.org/isdl.php

### **Error: "Dependencias no se descargan"**
**Solución:** Descargar manualmente:
- Visual C++: https://aka.ms/vs/17/release/vc_redist.x64.exe
- wkhtmltopdf: https://wkhtmltopdf.org/downloads.html

### **Error: "Aplicación no inicia después de instalar"**
**Solución:** Verificar que todas las dependencias están en el .spec:
- Revisar `hiddenimports` en `SistemaConstancias.spec`
- Agregar módulos faltantes

---

## 📊 TAMAÑO ESPERADO DEL INSTALADOR

- **Ejecutable PyInstaller:** ~150-200 MB
- **Dependencias:** ~50 MB
- **Instalador final:** ~200-250 MB

---

## 🎉 RESULTADO FINAL

**Archivo generado:** `installer/output/SistemaConstancias_Installer_v2.0.0.exe`

**Características:**
- ✅ Instalador profesional con Inno Setup
- ✅ Incluye todas las dependencias
- ✅ Funciona en cualquier Windows 10/11
- ✅ Instalación y desinstalación automática
- ✅ Listo para distribución a usuarios finales

---

## 🚀 COMANDOS RÁPIDOS

```bash
# Proceso completo automático
python build_installer.py

# Solo preparar archivos
python prepare_installer.py

# Solo generar ejecutable
pyinstaller SistemaConstancias.spec
```

¡Tu sistema está **LISTO PARA PRODUCCIÓN**! 🎉
