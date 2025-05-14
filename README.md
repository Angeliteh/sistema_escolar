# Sistema de Transformación de Constancias Escolares

Este sistema permite transformar diferentes tipos de constancias escolares (estudios, calificaciones, traslado) a partir de PDFs existentes, extrayendo los datos relevantes y generando nuevos documentos con formatos estandarizados.

## Características

- Extracción de datos de constancias en PDF existentes
- Transformación entre diferentes tipos de constancias
- Almacenamiento opcional de datos de alumnos en base de datos
- Interfaz gráfica para facilitar el uso
- Modo consola para automatización

## Tipos de Constancias

El sistema puede generar tres tipos de constancias:

1. **Constancia de Estudios** (`estudio`): Certifica que el alumno está inscrito en la escuela. No incluye calificaciones.
2. **Constancia de Calificaciones** (`calificaciones`): Muestra las calificaciones del alumno.
3. **Constancia de Traslado** (`traslado`): Certifica que el alumno puede ser trasladado a otra institución. Incluye calificaciones.

### Verificación de Calificaciones

El sistema verifica automáticamente si la constancia original contiene calificaciones:

- Si se solicita una constancia de traslado a partir de una constancia sin calificaciones, el sistema mostrará una advertencia y preguntará si desea continuar.
- Si decide continuar, se generará la constancia con calificaciones de ejemplo.
- Si decide no continuar, la operación se cancelará.

## Requisitos

- Python 3.7 o superior
- Dependencias listadas en `requirements.txt`

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

## Estructura de directorios

- `plantillas/`: Contiene las plantillas HTML para generar las constancias
- `logos/`: Imágenes de logos para las constancias
- `fotos/`: Fotos de los alumnos (opcional)
- `salidas/`: Directorio donde se guardan las constancias generadas

## Uso

### Modo GUI

Para iniciar la interfaz gráfica:

```
python main_qt.py
```

### Modo Consola

Para usar el modo consola:

```
python main.py <archivo_pdf> <tipo_constancia> [--con-foto=si|no|auto]
```

Donde:
- `<archivo_pdf>`: Ruta al archivo PDF de origen
- `<tipo_constancia>`: Tipo de constancia a generar (traslado, estudio, calificaciones)
- `[--con-foto=si|no|auto]`: Opción para controlar la inclusión de fotos (opcional)

Opciones para el manejo de fotos:
- `--con-foto=si`: Incluir foto en la constancia (si está disponible). Si no hay foto disponible, se mostrará un espacio reservado para la foto con el texto "Espacio para foto".
- `--con-foto=no`: No incluir foto en la constancia, independientemente de si está disponible. El diseño se ajustará automáticamente como si la foto nunca hubiera existido.
- `--con-foto=auto`: Detectar automáticamente (comportamiento por defecto). Incluye la foto si está disponible, de lo contrario no muestra ningún espacio para foto.

Ejemplos:
```
python main.py constacia_prueba_calificaciones.pdf traslado
python main.py constacia_prueba_calificaciones.pdf traslado --con-foto=si
python main.py constacia_prueba_calificaciones.pdf traslado --con-foto=no
```

## Módulos principales

- `pdf_extractor.py`: Extrae datos de PDFs existentes
- `pdf_generator.py`: Genera nuevas constancias en PDF
- `db_manager.py`: Gestiona la base de datos de alumnos
- `qt_gui.py`: Interfaz gráfica de usuario con PyQt5
- `main.py`: Punto de entrada para el modo consola
- `main_qt.py`: Punto de entrada para la interfaz gráfica

## Flujo de Funcionamiento del Sistema

### 1. Extracción de Datos

El proceso comienza con la extracción de datos de un PDF existente:

1. Se carga el PDF con `pdfplumber`.
2. Se extrae todo el texto del PDF.
3. Se determina automáticamente el tipo de constancia (traslado, estudio, calificaciones).
4. Se extraen los datos básicos del alumno (nombre, CURP, matrícula, etc.).
5. Si es una constancia de calificaciones, se extraen también las calificaciones.

### 2. Generación de Constancias

Una vez extraídos los datos, se utilizan para generar una nueva constancia:

1. Se selecciona la plantilla HTML adecuada según el tipo de constancia deseado.
2. Se renderiza la plantilla con los datos extraídos usando Jinja2.
3. Se guarda el HTML resultante.
4. Si wkhtmltopdf está instalado, se convierte el HTML a PDF.

### 3. Almacenamiento en Base de Datos (Opcional)

Si se desea, los datos del alumno y la constancia generada se pueden guardar en la base de datos:

1. Se verifica si el alumno ya existe en la base de datos.
2. Si existe, se actualizan sus datos; si no, se crea un nuevo registro.
3. Se guardan los datos escolares actuales.
4. Se registra la constancia generada.

## Personalización

### Plantillas HTML

Las plantillas se encuentran en:
- `plantillas/constancia_traslado.html`
- `plantillas/constancia_estudio.html` (generada automáticamente)
- `plantillas/constancia_calificaciones.html` (generada automáticamente)

Para modificar el diseño de las constancias, puedes editar estas plantillas HTML. Los elementos más importantes que puedes personalizar son:

#### 1. Diseño de la sección de datos del alumno

```html
<div class="info-container" style="padding-left: 40px; padding-right: 20px;">
    <table style="width:90%; border:none; margin: 0 auto;">
        <tr>
            <td style="width:130px; vertical-align:middle; border:none; padding-right:25px;">
                <img src="fotos/{{ curp }}.jpg" alt="Foto del alumno" class="foto" style="display:block; margin:0 auto;">
            </td>
            <td style="vertical-align:top; border:none; text-align:left;">
                <div class="datos-lista" style="text-align:left;">
                    <p style="text-align:left;"><strong>Nombre:</strong> {{ nombre }}</p>
                    <!-- Otros datos... -->
                </div>
            </td>
        </tr>
    </table>
</div>
```

#### 2. Estilos CSS

```css
.foto {
    width: 110px;  /* Aproximadamente 3 cm */
    height: 145px; /* Aproximadamente 3.5 cm */
    border: 1px solid #333;
    object-fit: cover;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}
```

#### 3. Tabla de calificaciones

```html
<div class="calificaciones" style="padding-left: 40px; padding-right: 20px;">
    <h3>Calificaciones de las asignaturas cursadas:</h3>
    <table style="width:90%; margin: 0 auto;">
        <!-- Encabezados y filas de la tabla -->
    </table>
</div>
```

### Ajustes Manuales del Diseño

Si deseas hacer ajustes manuales al diseño, estos son los lugares clave para modificar:

1. **Posición y tamaño de la foto**:
   - En `plantillas/constancia_traslado.html`, líneas 148-150
   - Ajusta `width:130px` para cambiar el ancho de la columna
   - Ajusta `padding-right:25px` para cambiar el espacio entre la foto y los datos

2. **Posición de los datos**:
   - Ajusta `padding-left: 40px; padding-right: 20px` en la línea 146 para mover todo el contenedor
   - Ajusta `width:90%; margin: 0 auto` en la línea 147 para cambiar el ancho y centrado

3. **Estilo de la foto**:
   - En `plantillas/constancia_traslado.html`, líneas 61-67
   - Ajusta `width: 110px` y `height: 145px` para cambiar el tamaño de la foto

4. **Espaciado y tamaño de los datos**:
   - En `plantillas/constancia_traslado.html`, líneas 72-78
   - Ajusta `margin: 8px 0` y `padding: 4px 0` para cambiar el espaciado
   - Ajusta `font-size: 13pt` para cambiar el tamaño del texto

### Datos por Defecto

En el archivo `pdf_extractor.py`, puedes modificar los valores por defecto para ciertos campos:

```python
datos = {
    "escuela": "PROF. MAXIMO GAMIZ FERNANDEZ",  # Valor por defecto
    "cct": "10DPR0392H",  # Valor por defecto
    "ciclo": "2024-2025",  # Valor por defecto
    "director": "JOSE ANGEL ALVARADO SOSA",  # Valor por defecto
    "fecha_actual": datetime.now().strftime("%d días del mes de %B de %Y").capitalize(),
}
```

### Logos

Puede reemplazar el archivo `logos/logo_educacion.png` con el logo de su institución. El sistema está configurado para usar este archivo en todas las plantillas.

### Fotos de alumnos

El sistema puede manejar constancias con o sin fotos de alumnos:

1. **Detección automática**: El sistema intentará detectar automáticamente la foto del alumno basándose en patrones observados en PDFs anteriores. Si está seguro de la detección, le preguntará para confirmar.

2. **Extracción interactiva**: Si la detección automática falla o si usted rechaza la selección automática, el sistema extraerá todas las imágenes y le permitirá seleccionar manualmente cuál es la foto del alumno.

3. **Fotos manuales**: También puede añadir fotos manualmente guardándolas en el directorio `fotos/` con el nombre `CURP.jpg` (donde CURP es la CURP del alumno).

4. **Control explícito de inclusión de fotos**: Puede controlar explícitamente si desea incluir fotos en las constancias usando la opción `--con-foto`:
   - `--con-foto=si`: Incluir foto en la constancia (si está disponible). Si no hay foto disponible, se mostrará un espacio reservado para la foto con el texto "Espacio para foto".
   - `--con-foto=no`: No incluir foto en la constancia. El diseño se ajustará automáticamente como si la foto nunca hubiera existido.
   - `--con-foto=auto`: Detectar automáticamente (comportamiento por defecto). Incluye la foto si está disponible, de lo contrario no muestra ningún espacio para foto.

Las fotos extraídas se guardan en el directorio `fotos/` con el nombre `CURP.jpg` para su reutilización en futuras constancias del mismo alumno.

## Base de datos

El sistema utiliza SQLite para almacenar los datos de los alumnos. El archivo de base de datos se crea automáticamente como `alumnos.db` en el directorio raíz.

La base de datos contiene las siguientes tablas:
- `alumnos`: Datos básicos de los alumnos (CURP, nombre, matrícula, etc.)
- `datos_escolares`: Información escolar (grado, grupo, turno, calificaciones, etc.)
- `constancias`: Registro de las constancias generadas

## Licencia

Este proyecto es software libre y puede ser utilizado, modificado y distribuido libremente.
