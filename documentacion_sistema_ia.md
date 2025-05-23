# Documentación del Sistema de IA para Constancias Escolares

## Índice
1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Componentes Principales](#componentes-principales)
3. [Flujo de Trabajo](#flujo-de-trabajo)
4. [Comandos Disponibles](#comandos-disponibles)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Configuración y Requisitos](#configuración-y-requisitos)
7. [Solución de Problemas](#solución-de-problemas)
8. [Extensión del Sistema](#extensión-del-sistema)

## Arquitectura del Sistema

El sistema utiliza una arquitectura en capas que separa claramente las responsabilidades:

```
┌─────────────────────────────────────┐
│            Interfaz de Usuario      │
│  ┌─────────────┐    ┌─────────────┐ │
│  │  UI Gráfica │    │ Terminal IA │ │
│  └──────┬──────┘    └──────┬──────┘ │
└─────────┼─────────────────┼─────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────┐
│         Capa de Comandos            │
│  ┌─────────────┐    ┌─────────────┐ │
│  │  Comandos   │    │ Intérprete  │ │
│  └──────┬──────┘    └──────┬──────┘ │
└─────────┼─────────────────┼─────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────┐
│         Capa de Servicios           │
│  ┌─────────────┐    ┌─────────────┐ │
│  │AlumnoService│    │ConstanciaSrv│ │
│  └──────┬──────┘    └──────┬──────┘ │
└─────────┼─────────────────┼─────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────┐
│         Capa de Datos               │
│  ┌─────────────┐    ┌─────────────┐ │
│  │  Database   │    │PDF Processor│ │
│  └─────────────┘    └─────────────┘ │
└─────────────────────────────────────┘
```

### Características clave:
- **Separación de responsabilidades**: Cada capa tiene una función específica
- **Reutilización de código**: La lógica de negocio es compartida entre interfaces
- **Extensibilidad**: Fácil de añadir nuevas interfaces o funcionalidades

## Componentes Principales

### 1. ServiceProvider
Centraliza el acceso a los servicios del sistema.

**Ubicación**: `app/core/service_provider.py`

```python
class ServiceProvider:
    """Proveedor centralizado de servicios"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Obtiene la instancia única del proveedor de servicios"""
        if cls._instance is None:
            cls._instance = ServiceProvider()
        return cls._instance
    
    def __init__(self):
        """Inicializa el proveedor de servicios"""
        # Inicializar servicios
        self.alumno_service = AlumnoService()
        self.constancia_service = ConstanciaService()
```

### 2. Comandos
Encapsulan operaciones específicas del sistema.

**Ubicación**: `app/core/commands/`

Ejemplos:
- `BuscarAlumnoCommand`: Busca alumnos por nombre o CURP
- `GenerarConstanciaCommand`: Genera una constancia para un alumno

### 3. Intérprete de Comandos
Traduce el lenguaje natural a comandos ejecutables.

**Ubicación**: `app/core/ai/command_interpreter.py`

### 4. Ejecutor de Comandos
Ejecuta los comandos interpretados.

**Ubicación**: `app/core/ai/command_executor.py`

### 5. Terminal de IA
Interfaz de línea de comandos para interactuar con el sistema mediante lenguaje natural.

**Ubicación**: `ai_terminal_executor.py`

## Flujo de Trabajo

1. **Entrada del usuario**: El usuario escribe un comando en lenguaje natural
2. **Interpretación**: El texto se envía a Gemini para ser interpretado
3. **Conversión a comando**: La respuesta de Gemini se convierte en un comando ejecutable
4. **Ejecución**: El comando se ejecuta utilizando los servicios del sistema
5. **Resultado**: Se muestra el resultado al usuario

### Ejemplo de flujo:

```
Usuario: "Genera una constancia de estudios para Franco"
↓
Gemini: {"accion": "generar_constancia", "parametros": {"nombre": "Franco", "tipo": "estudio"}}
↓
CommandExecutor: Crea y ejecuta GenerarConstanciaCommand
↓
AlumnoService: Busca al alumno "Franco"
↓
ConstanciaService: Genera la constancia
↓
Usuario: Ve el resultado y puede abrir el archivo generado
```

## Comandos Disponibles

### 1. Gestión de Alumnos

#### buscar_alumno
Busca alumnos por nombre o CURP.

**Parámetros**:
- `nombre`: Nombre del alumno (puede ser parcial)
- `curp`: CURP del alumno (opcional)
- `busqueda_exacta`: Si es `true`, busca coincidencias exactas (por defecto `false`)

**Ejemplos**:
```
Busca al alumno Juan Pérez
Busca alumnos con apellido García
```

#### registrar_alumno
Registra un nuevo alumno.

**Parámetros**:
- `nombre`: Nombre completo del alumno
- `curp`: CURP del alumno
- `matricula`: Matrícula escolar (opcional)
- `grado`: Grado escolar (1-6)
- `grupo`: Grupo (A-F)
- `turno`: MATUTINO o VESPERTINO

**Ejemplos**:
```
Registra un nuevo alumno llamado Carlos López con CURP LOPC010101HDFXXX01
Registra a María con CURP RODM010101MDFXXX01 en 3° grado grupo B turno matutino
```

#### actualizar_alumno
Actualiza los datos de un alumno existente.

**Parámetros**:
- `alumno_id`: ID del alumno
- `datos`: Objeto con los datos a actualizar

**Ejemplos**:
```
Actualiza los datos del alumno con ID 7, cambia su nombre a Luis Martínez
Modifica el grado del alumno con ID 3 a 4° grado grupo C
```

#### eliminar_alumno
Elimina un alumno de la base de datos.

**Parámetros**:
- `alumno_id`: ID del alumno

**Ejemplos**:
```
Elimina al alumno con ID 15
Borra el registro del alumno con CURP SANP010101HDFXXX01
```

### 2. Generación de Constancias

#### generar_constancia
Genera una constancia para un alumno.

**Parámetros**:
- `alumno_id`: ID del alumno (opcional si se proporciona nombre)
- `nombre`: Nombre del alumno (opcional si se proporciona alumno_id)
- `tipo`: "estudio", "calificaciones" o "traslado"
- `incluir_foto`: Si se debe incluir la foto del alumno (por defecto `false`)

**Ejemplos**:
```
Genera una constancia de estudios para el alumno con ID 5
Crea una constancia de calificaciones para Juan Pérez
Genera una constancia de traslado para Franco con foto
```

#### transformar_constancia
Transforma una constancia existente.

**Parámetros**:
- `ruta_archivo`: Ruta al archivo PDF
- `tipo_destino`: "estudio", "calificaciones" o "traslado"
- `incluir_foto`: Si se debe incluir la foto (por defecto `false`)

**Ejemplos**:
```
Transforma la constancia en C:/constancias/ejemplo.pdf a formato de estudios
Convierte el archivo PDF en D:/documentos/constancia.pdf a constancia de calificaciones con foto
```

#### listar_constancias
Lista las constancias generadas para un alumno.

**Parámetros**:
- `alumno_id`: ID del alumno (opcional si se proporciona nombre)
- `nombre`: Nombre del alumno (opcional si se proporciona alumno_id)

**Ejemplos**:
```
Muestra las constancias del alumno con ID 5
Lista las constancias generadas para Franco
```

## Ejemplos de Uso

### Flujo de trabajo típico

1. **Buscar un alumno**:
   ```
   > Busca alumnos con nombre Fra
   ```

2. **Generar una constancia**:
   ```
   > Genera una constancia de traslado para Franco
   ```

3. **Ver las constancias generadas**:
   ```
   > Muestra las constancias de Franco
   ```

### Manejo de ambigüedad

Si hay múltiples alumnos con nombres similares:

```
> Genera una constancia para Juan

Se encontraron múltiples alumnos con ese nombre. Por favor, especifica el ID:
1. Juan Pérez (ID: 3)
2. Juan García (ID: 7)
3. Juan Rodríguez (ID: 12)
```

Puedes entonces especificar el ID:

```
> Genera una constancia de estudios para el alumno con ID 7
```

## Configuración y Requisitos

### Requisitos previos
- Python 3.6 o superior
- Bibliotecas Python (ver `ai_requirements.txt`)
- API key de Gemini

### Configuración
1. Crear un archivo `.env` en la raíz del proyecto:
   ```
   GEMINI_API_KEY=tu-api-key-aquí
   ```

2. Instalar dependencias:
   ```
   pip install -r ai_requirements.txt
   ```

### Ejecución
Para iniciar la interfaz de IA:
```
python ai_terminal_executor.py
```

## Solución de Problemas

### Problemas comunes

1. **Error de API key**:
   - Verifica que la API key en el archivo `.env` sea correcta
   - Asegúrate de que la API key tenga permisos para los modelos Gemini 2.0 Flash y 1.5 Flash

2. **Alumno no encontrado**:
   - Verifica que el alumno exista en la base de datos
   - Intenta buscar por nombre parcial o por ID

3. **Error al generar constancia**:
   - Verifica que el tipo de constancia sea válido ("estudio", "calificaciones" o "traslado")
   - Asegúrate de que el alumno tenga todos los datos necesarios

4. **Error al transformar constancia**:
   - Verifica que la ruta del archivo sea correcta
   - Asegúrate de que el archivo exista y sea un PDF válido

### Mecanismo de respaldo

El sistema utiliza un mecanismo de respaldo entre modelos de Gemini:
1. Primero intenta con Gemini 2.0 Flash
2. Si falla, utiliza Gemini 1.5 Flash

Si ves mensajes como "Error con Gemini 2.0 Flash... Intentando con modelo de respaldo...", es normal y parte del funcionamiento del sistema.

## Extensión del Sistema

### Añadir nuevos comandos

1. Crear una nueva clase de comando en `app/core/commands/`
2. Implementar el método `execute()`
3. Añadir el comando al ejecutor en `app/core/ai/command_executor.py`
4. Actualizar el prompt en `ai_terminal_executor.py`

### Mejorar la interpretación

Para mejorar la interpretación de comandos, puedes:
1. Añadir más ejemplos al prompt
2. Refinar las instrucciones para Gemini
3. Implementar un sistema de feedback para mejorar la interpretación

### Integración con la interfaz gráfica

Es posible integrar la interfaz de IA con la interfaz gráfica:
1. Añadir un panel de chat en la interfaz gráfica
2. Conectar el panel con el intérprete y ejecutor de comandos
3. Mostrar los resultados en la interfaz gráfica
