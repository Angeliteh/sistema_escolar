# Sistema de Constancias Escolares

Este sistema permite transformar diferentes tipos de constancias escolares (estudios, calificaciones, traslado) a partir de PDFs existentes, extrayendo los datos relevantes y generando nuevos documentos con formatos estandarizados.

## Estructura del Sistema

El sistema está organizado en una arquitectura en capas:

```
constancias_system/
├── app/                      # Código principal de la aplicación
│   ├── core/                 # Utilidades y configuración
│   │   ├── config.py         # Configuración centralizada
│   │   ├── pdf_extractor.py  # Extracción de datos de PDFs
│   │   ├── pdf_generator.py  # Generación de PDFs
│   │   └── utils.py          # Funciones auxiliares
│   │
│   ├── data/                 # Capa de acceso a datos
│   │   ├── models/           # Modelos de datos
│   │   │   ├── alumno.py     # Modelo de Alumno
│   │   │   ├── constancia.py # Modelo de Constancia
│   │   │   └── datos_escolares.py # Modelo de Datos Escolares
│   │   │
│   │   └── repositories/     # Repositorios específicos
│   │       ├── alumno_repository.py
│   │       ├── constancia_repository.py
│   │       └── datos_escolares_repository.py
│   │
│   ├── services/             # Servicios de aplicación
│   │   ├── alumno_service.py # Servicio para gestión de alumnos
│   │   └── constancia_service.py # Servicio para gestión de constancias
│   │
│   └── ui/                   # Interfaces de usuario
│       ├── alumno_ui.py      # UI para gestión de alumnos
│       ├── buscar_ui.py      # UI para búsqueda de alumnos
│       ├── menu_principal.py # Menú principal
│       ├── pdf_viewer.py     # Visor de PDF integrado
│       └── transformar_ui.py # UI para transformar constancias
│
├── resources/                # Recursos del sistema
│   ├── data/                 # Datos
│   │   └── alumnos.db        # Base de datos SQLite
│   │
│   ├── images/               # Imágenes
│   │   ├── logos/            # Logos para constancias
│   │   └── photos/           # Fotos de alumnos
│   │
│   ├── templates/            # Plantillas para constancias
│   └── output/               # Constancias generadas
│
├── main_qt.py                # Punto de entrada principal
├── transformar.py            # Acceso directo a transformación
├── buscar.py                 # Acceso directo a búsqueda
└── alumno_manager.py         # Acceso directo a gestión de alumnos
```

## Características

- Extracción de datos de constancias en PDF existentes
- Transformación entre diferentes tipos de constancias
- Almacenamiento de datos de alumnos en base de datos
- Interfaz gráfica intuitiva con botones grandes
- Visor de PDF integrado para previsualizar constancias
- Arquitectura en capas con repositorios y servicios

## Tipos de Constancias

El sistema puede generar tres tipos de constancias:

1. **Constancia de Estudios** (`estudio`): Certifica que el alumno está inscrito en la escuela. No incluye calificaciones.
2. **Constancia de Calificaciones** (`calificaciones`): Muestra las calificaciones del alumno.
3. **Constancia de Traslado** (`traslado`): Certifica que el alumno puede ser trasladado a otra institución. Incluye calificaciones.

## Requisitos

- Python 3.7 o superior
- PyQt5 para la interfaz gráfica
- PyMuPDF (fitz) para el visor de PDF
- Otras dependencias listadas en `requirements.txt`

## Instalación

1. Clonar o descargar este repositorio
2. Instalar las dependencias:

```
pip install -r requirements.txt
```

3. Instalar wkhtmltopdf (opcional, pero recomendado para generar PDFs):
   - Descargar desde: https://wkhtmltopdf.org/downloads.html
   - Instalar siguiendo las instrucciones para su sistema operativo
   - Asegurarse de que el ejecutable esté en el PATH del sistema

Si no se instala wkhtmltopdf, el sistema generará archivos HTML en lugar de PDFs, que pueden ser convertidos a PDF manualmente usando un navegador web.

## Directorios de Recursos

- `resources/templates/`: Contiene las plantillas HTML para generar las constancias
- `resources/images/logos/`: Imágenes de logos para las constancias
- `resources/images/photos/`: Fotos de los alumnos (opcional)
- `resources/output/`: Directorio donde se guardan las constancias generadas
- `resources/data/`: Contiene la base de datos y otros archivos de datos

## Uso

### Menú Principal

Para iniciar el menú principal con todas las opciones:

```
python main_qt.py
```

Desde aquí podrás acceder a todas las funcionalidades del sistema a través de botones grandes e intuitivos.

### Transformar Constancias

Para transformar una constancia existente a formato estandarizado:

```
python transformar.py
```

Esta interfaz incluye:
- Selección de archivo PDF
- Vista previa de datos extraídos
- Vista previa de la constancia a generar
- Opciones de configuración

### Buscar y Generar Constancias

Para buscar alumnos registrados y generar constancias:

```
python buscar.py
```

Esta interfaz incluye:
- Búsqueda por nombre o CURP
- Lista de alumnos encontrados
- Botón para generar constancias

### Administrar Base de Datos

Para gestionar alumnos (agregar, modificar, eliminar):

```
python alumno_manager.py
```

Esta interfaz incluye:
- Búsqueda por nombre o CURP
- Lista de alumnos registrados
- Funciones para agregar, modificar y eliminar alumnos
- Generación de constancias

## Arquitectura del Sistema

El sistema sigue una arquitectura en capas que separa claramente las responsabilidades:

### 1. Capa de Modelos

Clases que representan las entidades del sistema:
- `Alumno`: Datos personales del estudiante
- `DatosEscolares`: Información académica (grado, grupo, calificaciones)
- `Constancia`: Registro de constancias generadas

### 2. Capa de Repositorios

Clases que manejan el acceso a datos para cada entidad:
- `AlumnoRepository`: Operaciones CRUD para alumnos
- `DatosEscolaresRepository`: Operaciones CRUD para datos escolares
- `ConstanciaRepository`: Operaciones CRUD para constancias

### 3. Capa de Servicios

Clases que implementan la lógica de negocio:
- `AlumnoService`: Gestión de alumnos y sus datos
- `ConstanciaService`: Generación y gestión de constancias

### 4. Capa de Presentación

Interfaces gráficas para interactuar con el usuario:
- `MenuPrincipal`: Menú con botones grandes para acceder a las funcionalidades
- `TransformarWindow`: Interfaz para transformar PDFs en constancias
- `BuscarWindow`: Interfaz para buscar alumnos y generar constancias
- `AlumnoManagerWindow`: Interfaz para gestionar alumnos

## Flujo de Funcionamiento

### 1. Flujo de Transformación de Constancias

1. El usuario selecciona un PDF existente
2. El sistema extrae los datos del PDF
3. El usuario selecciona el tipo de constancia y opciones
4. Se muestra una vista previa en el visor de PDF integrado
5. El usuario confirma la transformación
6. El sistema genera la nueva constancia
7. Se guarda la constancia y los datos del alumno en la base de datos

### 2. Flujo de Búsqueda y Generación

1. El usuario busca un alumno por nombre o CURP
2. El sistema muestra los resultados en una tabla
3. El usuario selecciona un alumno y elige "Generar Constancia"
4. El usuario selecciona el tipo de constancia
5. El sistema genera la constancia
6. Se muestra la constancia generada al usuario

### 3. Flujo de Administración de Alumnos

1. El usuario puede ver la lista de alumnos
2. El usuario puede buscar alumnos específicos
3. El usuario puede agregar nuevos alumnos
4. El usuario puede editar datos de alumnos existentes
5. El usuario puede eliminar alumnos
6. El usuario puede generar constancias para alumnos seleccionados

## Base de Datos

El sistema utiliza SQLite para almacenar los datos de los alumnos. El archivo de base de datos se encuentra en `resources/data/alumnos.db`.

La base de datos contiene las siguientes tablas:
- `alumnos`: Datos básicos de los alumnos (CURP, nombre, matrícula, etc.)
- `datos_escolares`: Información escolar (grado, grupo, turno, calificaciones, etc.)
- `constancias`: Registro de las constancias generadas

## Personalización

### Configuración

En el archivo `app/core/config.py`, puedes modificar los valores por defecto para ciertos campos:

```python
class Config:
    # Configuración de la escuela
    SCHOOL_NAME = "PROF. MAXIMO GAMIZ FERNANDEZ"
    SCHOOL_CCT = "10DPR0392H"
    SCHOOL_DIRECTOR = "JOSE ANGEL ALVARADO SOSA"
    CURRENT_SCHOOL_YEAR = "2024-2025"

    # Valores por defecto para alumnos
    DEFAULT_GRADE = 1
    DEFAULT_GROUP = "A"
    DEFAULT_SHIFT = "MATUTINO"

    # Versión del sistema
    VERSION = "1.0.0"
```

### Plantillas HTML

Las plantillas se encuentran en el directorio `resources/templates/`. Puedes modificarlas para personalizar el diseño de las constancias.

### Logos

Puedes reemplazar el archivo `resources/images/logos/logo_educacion.png` con el logo de tu institución.

## Licencia

Este proyecto es software libre y puede ser utilizado, modificado y distribuido libremente.
