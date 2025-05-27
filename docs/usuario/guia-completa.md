# 👥 Guía Completa de Usuario - Sistema de Constancias Escolares

## 🎯 **Introducción**

El Sistema de Constancias Escolares es una herramienta completa que permite generar, transformar y gestionar constancias académicas utilizando inteligencia artificial y una interfaz moderna e intuitiva.

---

## 🚀 **Inicio Rápido**

### **1. Ejecutar el Sistema**
```bash
python ai_chat.py
```

### **2. Interfaz Principal**
Al abrir el sistema verás:
- **Panel de Chat** (izquierda): Para comandos de IA
- **Panel de PDF** (derecha): Para transformación de documentos
- **Barra Superior**: Botones de navegación

### **3. Primer Uso**
1. Configura tu API Key de Gemini en el archivo `.env`
2. Prueba con: `"Busca alumnos de sexto grado"`
3. Carga un PDF en el panel derecho para transformar

---

## 🤖 **Chat con Inteligencia Artificial**

### **Comandos de Búsqueda de Alumnos**
```bash
# Búsqueda por nombre
"Busca al alumno Juan Pérez"
"Encuentra a María García"
"Muestra información de Carlos López"

# Búsqueda por CURP
"Busca CURP ABCD123456HDFRRL01"
"Encuentra alumno con CURP EFGH789012"

# Búsqueda por criterios escolares
"Muestra alumnos de sexto grado"
"Busca alumnos del grupo A"
"Encuentra estudiantes del turno matutino"
"Alumnos de quinto grado grupo B"

# Búsquedas combinadas
"Busca alumnos de tercer grado grupo A del turno vespertino"
```

### **Comandos de Generación de Constancias**
```bash
# Constancias básicas
"Genera constancia de estudios para Juan Pérez"
"Crea constancia de calificaciones para María García"
"Genera constancia de traslado para Pedro López"

# Con opciones específicas
"Constancia de estudios con foto para Ana Martínez"
"Constancia de calificaciones sin foto para Carlos Ruiz"
"Constancia de traslado con foto para Laura Sánchez"

# Usando CURP
"Genera constancia de estudios para CURP ABCD123456HDFRRL01"
```

### **Comandos de Información General**
```bash
# Estadísticas
"¿Cuántos alumnos hay en total?"
"¿Cuántos alumnos hay por grado?"
"Muestra estadísticas del turno matutino"

# Ayuda
"¿Qué tipos de constancias puedo generar?"
"¿Cómo busco un alumno?"
"Ayuda con comandos disponibles"
```

---

## 📄 **Transformación de PDFs**

### **Paso 1: Cargar PDF**
1. Haz clic en **"🔄 Transformación de PDF"** en la barra superior
2. El panel derecho se expandirá mostrando el área de carga
3. **Arrastra y suelta** un PDF en el área designada
4. O haz clic en **"📁 Seleccionar Archivo"** para navegar

### **Paso 2: Extraer Datos**
1. El sistema extrae automáticamente los datos del PDF
2. Haz clic en **"📋 Ver Datos Extraídos"** para revisar la información
3. Verifica que los datos sean correctos

### **Paso 3: Transformar**
Escribe en el chat el tipo de transformación deseada:
```bash
# Transformaciones disponibles
"transforma este PDF a constancia de estudios"
"convierte a constancia de calificaciones"
"transforma a constancia de traslado"
"convierte a constancia de estudios con foto"
"transforma a constancia de calificaciones con foto"
```

### **Paso 4: Vista Previa**
1. Se genera automáticamente una vista previa del PDF transformado
2. Puedes alternar entre el **PDF original** y el **PDF transformado**
3. Revisa que el resultado sea el esperado

### **Paso 5: Guardar (Opcional)**
1. Haz clic en **"📋 Ver Datos"** en el panel
2. Marca la casilla **"💾 Guardar estos datos en la BD"**
3. Haz clic en **"💾 Guardar en BD"** para registrar al alumno
4. Recibirás confirmación del guardado exitoso

---

## 🔍 **Búsqueda Avanzada**

### **Tipos de Búsqueda Soportados**

#### **Por Nombre Parcial**
- `"Juan"` - Encuentra todos los Juan
- `"Pérez"` - Encuentra todos los Pérez
- `"Juan Pé"` - Búsqueda más específica

#### **Por CURP**
- `"ABCD123456"` - CURP parcial
- `"ABCD123456HDFRRL01"` - CURP completa

#### **Por Criterios Escolares**
- `"sexto grado"` - Todos los de 6°
- `"grupo A"` - Todos del grupo A
- `"turno matutino"` - Todos del turno matutino

#### **Búsquedas Combinadas**
- `"alumnos de quinto grado grupo B"`
- `"estudiantes del turno vespertino de tercer grado"`

### **Resultados de Búsqueda**
Los resultados muestran:
- **Nombre completo** del alumno
- **CURP** (si está disponible)
- **Grado y grupo** actual
- **Turno** escolar
- **Opciones** para generar constancias

---

## 📊 **Tipos de Constancias**

### **1. 📜 Constancia de Estudios**
- **Propósito**: Certifica que el alumno está inscrito
- **Contenido**: Datos básicos del alumno y escuela
- **Calificaciones**: No incluye notas
- **Foto**: Opcional (automática si está disponible)

### **2. 📊 Constancia de Calificaciones**
- **Propósito**: Muestra el rendimiento académico
- **Contenido**: Datos del alumno + calificaciones por materia
- **Calificaciones**: Incluye todas las materias y promedio
- **Foto**: Opcional (automática si está disponible)

### **3. 🔄 Constancia de Traslado**
- **Propósito**: Para transferencia a otra institución
- **Contenido**: Datos completos + calificaciones obligatorias
- **Calificaciones**: Siempre incluidas
- **Foto**: Opcional (automática si está disponible)

---

## 🎨 **Interfaz de Usuario**

### **Panel de Chat (Izquierda)**
- **Área de mensajes**: Conversación con la IA
- **Campo de entrada**: Escribe tus comandos aquí
- **Botón enviar**: O presiona Enter
- **Historial**: Se mantiene durante la sesión

### **Panel de PDF (Derecha)**
- **Área de carga**: Drag & drop para PDFs
- **Visor integrado**: Muestra PDFs cargados
- **Botones contextuales**: Cambian según la situación
  - `📋 Ver Datos Extraídos` - Para PDFs cargados
  - `📋 Ver Datos` - Para PDFs transformados
  - `📋 Ver Datos del Alumno` - Para constancias generadas

### **Barra Superior**
- **🔄 Transformación de PDF**: Activa/desactiva panel
- **🏠 Inicio**: Vuelve a la vista principal
- **⚙️ Configuración**: Ajustes del sistema

---

## 💡 **Consejos y Trucos**

### **Para Búsquedas Efectivas**
1. **Usa nombres parciales** si no recuerdas el nombre completo
2. **Combina criterios** para búsquedas más específicas
3. **Usa CURP** para búsquedas exactas
4. **Prueba variaciones** si no encuentras resultados

### **Para Transformación de PDFs**
1. **Verifica los datos extraídos** antes de transformar
2. **Usa vista previa** para confirmar el resultado
3. **Guarda en BD** solo si los datos son correctos
4. **Prueba diferentes tipos** de transformación

### **Para Generación de Constancias**
1. **Especifica el tipo** claramente en tu comando
2. **Menciona si quieres foto** o no
3. **Usa nombres exactos** o CURP para precisión
4. **Revisa la vista previa** antes de imprimir

---

## ❓ **Preguntas Frecuentes**

### **¿Qué hago si no encuentro un alumno?**
1. Verifica la ortografía del nombre
2. Prueba con nombre parcial
3. Usa la CURP si la tienes
4. Verifica que el alumno esté registrado en la BD

### **¿Cómo sé si un PDF se transformó correctamente?**
1. Revisa los datos extraídos con "📋 Ver Datos"
2. Compara el PDF original con el transformado
3. Verifica que toda la información sea correcta

### **¿Puedo generar constancias sin foto?**
Sí, especifica en tu comando:
- `"constancia de estudios sin foto"`
- `"constancia de calificaciones sin foto"`

### **¿Qué formatos de PDF acepta el sistema?**
El sistema acepta la mayoría de PDFs de constancias escolares estándar. Si tienes problemas, verifica que:
- El PDF no esté protegido con contraseña
- El texto sea seleccionable (no imagen escaneada)
- El formato sea similar a constancias mexicanas estándar

---

## 🆘 **Soporte**

### **Si Encuentras Problemas**
1. **Revisa los logs** en la carpeta `logs/`
2. **Verifica tu conexión** a internet (para IA)
3. **Confirma tu API Key** de Gemini
4. **Reinicia el sistema** si es necesario

### **Para Reportar Bugs**
1. Describe el problema detalladamente
2. Incluye los pasos para reproducir
3. Adjunta logs relevantes
4. Menciona tu sistema operativo

---

**🎓 ¡Disfruta usando el Sistema de Constancias Escolares! ✨**
