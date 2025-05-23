# Documentación de la Base de Datos del Sistema de Constancias

## Índice
1. [Estructura de la Base de Datos](#estructura-de-la-base-de-datos)
2. [Relaciones entre Tablas](#relaciones-entre-tablas)
3. [Procesos de Registro y Actualización](#procesos-de-registro-y-actualización)
4. [Generación de Constancias](#generación-de-constancias)
5. [Transformación de Constancias](#transformación-de-constancias)
6. [Manejo de Datos Incompletos](#manejo-de-datos-incompletos)
7. [Historial Académico](#historial-académico)
8. [Ejemplos Prácticos](#ejemplos-prácticos)

## Estructura de la Base de Datos

El sistema utiliza una base de datos SQLite con las siguientes tablas principales:

### Tabla `alumnos`

Almacena la información personal básica de los alumnos.

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | INTEGER | Identificador único (clave primaria) | Sí (auto) |
| nombre | TEXT | Nombre completo del alumno | Sí |
| curp | TEXT | CURP del alumno (único) | Sí |
| matricula | TEXT | Matrícula escolar | No |
| fecha_nacimiento | TEXT | Fecha de nacimiento | No |
| fecha_registro | TEXT | Fecha de registro en el sistema | Sí (auto) |
| foto_path | TEXT | Ruta a la foto del alumno | No |

### Tabla `datos_escolares`

Almacena la información académica de los alumnos, que puede cambiar cada ciclo escolar.

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | INTEGER | Identificador único (clave primaria) | Sí (auto) |
| alumno_id | INTEGER | ID del alumno (clave foránea) | Sí |
| ciclo_escolar | TEXT | Ciclo escolar (ej. "2024-2025") | No |
| grado | INTEGER | Grado escolar (1-6) | No |
| grupo | TEXT | Grupo (A-F) | No |
| turno | TEXT | Turno (MATUTINO/VESPERTINO) | No |
| escuela | TEXT | Nombre de la escuela | No |
| cct | TEXT | Clave del Centro de Trabajo | No |
| calificaciones | TEXT | Calificaciones en formato JSON | No |

### Tabla `constancias`

Registra las constancias generadas para los alumnos.

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | INTEGER | Identificador único (clave primaria) | Sí (auto) |
| alumno_id | INTEGER | ID del alumno (clave foránea) | Sí |
| tipo | TEXT | Tipo de constancia (estudio/calificaciones/traslado) | Sí |
| fecha_generacion | TEXT | Fecha de generación | Sí (auto) |
| ruta_archivo | TEXT | Ruta al archivo PDF | Sí |
| incluye_foto | INTEGER | Si incluye foto (0/1) | Sí |

## Relaciones entre Tablas

```
┌─────────────┐       ┌────────────────┐       ┌─────────────┐
│   alumnos   │       │ datos_escolares │       │ constancias │
│             │       │                │       │             │
│ id          │◄──┐   │ id             │       │ id          │
│ nombre      │   │   │ alumno_id      │◄──┐   │ alumno_id   │
│ curp        │   └───┤ ciclo_escolar  │   │   │ tipo        │
│ matricula   │       │ grado          │   └───┤ fecha_gen   │
│ fecha_nac   │       │ grupo          │       │ ruta_archivo│
│ fecha_reg   │       │ turno          │       │ incluye_foto│
│ foto_path   │       │ escuela        │       │             │
└─────────────┘       │ cct            │       └─────────────┘
                      │ calificaciones │
                      └────────────────┘
```

- Un alumno puede tener múltiples registros en `datos_escolares` (uno por ciclo escolar)
- Un alumno puede tener múltiples constancias generadas
- Cada registro en `datos_escolares` y `constancias` está vinculado a un único alumno

## Procesos de Registro y Actualización

### Registro de un Nuevo Alumno

Cuando se registra un nuevo alumno, el sistema:

1. Crea un registro en la tabla `alumnos` con los datos personales
2. Crea un registro en la tabla `datos_escolares` vinculado al alumno
3. Asigna el ciclo escolar actual configurado en el sistema

**Ejemplo de comando:**
```
Registra a Juan Pérez con CURP PERJ010101HDFXXX01 en 3° grado grupo A turno matutino
```

**Resultado en la base de datos:**
- Nuevo registro en `alumnos` con nombre, CURP, etc.
- Nuevo registro en `datos_escolares` con alumno_id, grado=3, grupo="A", turno="MATUTINO", etc.

### Actualización de Datos

Cuando se actualizan los datos de un alumno, el sistema:

1. Identifica al alumno por ID, nombre o CURP
2. Actualiza los campos correspondientes en la tabla `alumnos` y/o `datos_escolares`
3. Si se cambia información académica de un ciclo diferente, puede crear un nuevo registro en `datos_escolares`

**Ejemplo de comando:**
```
Actualiza los datos del alumno con ID 5, cambia su grupo a B y su turno a vespertino
```

**Resultado en la base de datos:**
- Se actualiza el registro en `datos_escolares` para el alumno con ID 5

## Generación de Constancias

### Proceso de Generación

Cuando se genera una constancia, el sistema:

1. Identifica al alumno por ID, nombre o CURP
2. Obtiene los datos personales de la tabla `alumnos`
3. Obtiene los datos académicos de la tabla `datos_escolares` (normalmente del ciclo más reciente)
4. Genera un documento PDF según el tipo de constancia solicitado
5. Registra la constancia generada en la tabla `constancias`

### Tipos de Constancias y Datos Requeridos

#### Constancia de Estudios
- **Datos mínimos**: Nombre, CURP
- **Datos recomendados**: Grado, grupo, turno, escuela
- **Propósito**: Certificar que el alumno está inscrito en la escuela

#### Constancia de Calificaciones
- **Datos mínimos**: Nombre, CURP, grado, grupo
- **Datos recomendados**: Calificaciones por materia, ciclo escolar
- **Propósito**: Mostrar el desempeño académico del alumno

#### Constancia de Traslado
- **Datos mínimos**: Nombre, CURP, grado, grupo, escuela
- **Datos recomendados**: Historial académico completo, calificaciones
- **Propósito**: Facilitar el cambio de escuela del alumno

## Transformación de Constancias

### Proceso de Transformación

Cuando se transforma una constancia existente, el sistema:

1. Extrae información del PDF original
2. Identifica al alumno en la base de datos o crea un nuevo registro si se especifica `guardar_alumno=true`
3. Genera un nuevo PDF con el formato solicitado
4. Registra la nueva constancia en la tabla `constancias`

### Opciones de Transformación

- **guardar_alumno**: Si es `true`, crea un nuevo registro de alumno si no existe
- **incluir_foto**: Si es `true`, incluye la foto del alumno en la constancia
- **tipo_destino**: Especifica el formato de la nueva constancia (estudio/calificaciones/traslado)

## Manejo de Datos Incompletos

### Registro con Datos Mínimos

El sistema permite registrar alumnos con datos mínimos:
- **Obligatorios**: Nombre y CURP
- **Opcionales**: Todos los demás campos

**Ejemplo:**
```
Registra a María Rodríguez con CURP RODM010101MDFXXX01
```

**Resultado:**
- Se crea el registro en `alumnos` con nombre y CURP
- Se puede crear un registro en `datos_escolares` con valores nulos o predeterminados

### Generación de Constancias con Datos Incompletos

El sistema puede generar constancias incluso con información incompleta:

- Los campos faltantes aparecerán vacíos o con la leyenda "No disponible"
- Se generará una advertencia si faltan datos importantes para el tipo de constancia
- La constancia se generará, pero estará incompleta

## Historial Académico

### Seguimiento por Ciclo Escolar

La tabla `datos_escolares` permite mantener un historial académico completo:

- Cada ciclo escolar tiene un registro separado
- Se puede rastrear el progreso del alumno a lo largo de los años
- Las constancias pueden generarse para un ciclo específico o el más reciente

### Consulta de Historial

Para consultar el historial académico de un alumno:
```
SELECT * FROM datos_escolares WHERE alumno_id = X ORDER BY ciclo_escolar DESC
```

## Ejemplos Prácticos

### Ejemplo 1: Registro Completo

```
Registra a Juan Pérez con CURP PERJ010101HDFXXX01 en 3° grado grupo A turno matutino
```

**Resultado en la base de datos:**
- `alumnos`: Nuevo registro con ID=1, nombre="Juan Pérez", curp="PERJ010101HDFXXX01"
- `datos_escolares`: Nuevo registro con alumno_id=1, grado=3, grupo="A", turno="MATUTINO"

### Ejemplo 2: Registro con Datos Mínimos

```
Registra a María Rodríguez con CURP RODM010101MDFXXX01
```

**Resultado en la base de datos:**
- `alumnos`: Nuevo registro con ID=2, nombre="María Rodríguez", curp="RODM010101MDFXXX01"
- `datos_escolares`: Nuevo registro con alumno_id=2, otros campos NULL o con valores predeterminados

### Ejemplo 3: Actualización de Datos

```
Actualiza los datos del alumno con ID 1, cambia su grado a 4 y su grupo a B
```

**Resultado en la base de datos:**
- `datos_escolares`: Se actualiza el registro para alumno_id=1 con grado=4, grupo="B"

### Ejemplo 4: Generación de Constancia

```
Genera una constancia de estudios para Juan Pérez
```

**Resultado:**
- Se genera un archivo PDF con los datos de Juan Pérez
- `constancias`: Nuevo registro con alumno_id=1, tipo="estudio", ruta_archivo="..."

### Ejemplo 5: Transformación de Constancia

```
Transforma la constancia en C:/constancias/ejemplo.pdf a formato de calificaciones con guardar_alumno=true
```

**Resultado:**
- Si el alumno no existe, se crea un nuevo registro en `alumnos` y `datos_escolares`
- Se genera un nuevo archivo PDF en formato de constancia de calificaciones
- `constancias`: Nuevo registro con el alumno_id correspondiente
