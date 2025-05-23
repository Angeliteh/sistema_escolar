# Interfaz de Chat con IA para el Sistema de Constancias

## Descripción General

La Interfaz de Chat con IA es una nueva funcionalidad que combina la potencia del procesamiento de lenguaje natural con una interfaz gráfica intuitiva para el sistema de constancias escolares. Esta interfaz permite a los usuarios interactuar con el sistema mediante comandos en lenguaje natural, cargar PDFs y visualizar las constancias generadas, todo en una única ventana.

## Características Principales

- **Interfaz de chat intuitiva**: Similar a ChatGPT, permite escribir comandos en lenguaje natural
- **Carga de PDFs integrada**: Botón para cargar PDFs directamente en la interfaz
- **Vista previa de constancias**: Visualización de las constancias generadas en tiempo real
- **Procesamiento de lenguaje natural**: Utiliza Google Gemini para interpretar comandos
- **Sistema de respaldo**: Cambio automático entre modelos Gemini 2.0 Flash y 1.5 Flash
- **Validación mejorada**: Verifica la disponibilidad de calificaciones para constancias que las requieren

## Capturas de Pantalla

![Interfaz de Chat con IA](resources/images/screenshots/ai_chat_interface.png)

## Arquitectura

La interfaz de chat se integra con el sistema existente a través de la siguiente arquitectura:

```
┌─────────────────────────────────────────────┐
│            Interfaz de Chat con IA          │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │  Panel de   │    │ Panel de Carga y    │ │
│  │    Chat     │    │ Vista Previa de PDF │ │
│  └──────┬──────┘    └──────────┬──────────┘ │
└─────────┼─────────────────────┼─────────────┘
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────┐
│              Capa de Integración            │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │ Intérprete  │    │ Visor de PDF y      │ │
│  │ de Comandos │    │ Gestor de Archivos  │ │
│  └──────┬──────┘    └──────────┬──────────┘ │
└─────────┼─────────────────────┼─────────────┘
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────────┐
│              Sistema Existente              │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │ Ejecutor de │    │ Servicios de        │ │
│  │  Comandos   │    │ Alumnos/Constancias │ │
│  └─────────────┘    └─────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Panel de Chat
- Área de texto para mostrar la conversación
- Campo de entrada para escribir comandos
- Botón de envío para ejecutar comandos

### 2. Panel de Carga y Vista Previa
- Botón para cargar PDFs
- Etiqueta que muestra el PDF actualmente cargado
- Visor de PDF integrado para mostrar constancias

### 3. Intérprete de Comandos
- Utiliza Google Gemini para interpretar comandos en lenguaje natural
- Convierte los comandos en acciones ejecutables por el sistema
- Sistema de respaldo entre modelos Gemini 2.0 Flash y 1.5 Flash

### 4. Ejecutor de Comandos
- Ejecuta las acciones interpretadas
- Devuelve resultados para mostrar en la interfaz
- Validación mejorada para constancias que requieren calificaciones

## Flujo de Trabajo

1. **Interacción con el Chat**:
   - El usuario escribe un comando en lenguaje natural
   - El sistema muestra el comando en el área de chat
   - Se muestra una barra de progreso mientras se procesa

2. **Interpretación del Comando**:
   - El comando se envía a Google Gemini
   - Gemini interpreta el comando y devuelve un JSON estructurado
   - El sistema extrae la acción y los parámetros del JSON

3. **Ejecución del Comando**:
   - El ejecutor de comandos procesa la acción y los parámetros
   - Se realizan validaciones adicionales (ej. verificar calificaciones)
   - Se ejecuta la acción correspondiente

4. **Visualización de Resultados**:
   - El resultado se muestra en el área de chat
   - Si se generó una constancia, se muestra en el visor de PDF
   - Se ofrece la opción de abrir el archivo generado

5. **Carga de PDFs**:
   - El usuario puede cargar un PDF usando el botón correspondiente
   - El PDF se muestra en el visor
   - El sistema informa que el PDF está listo para transformación

## Comandos Soportados

La interfaz de chat soporta todos los comandos disponibles en el sistema:

1. **Búsqueda de Alumnos**:
   - "Busca al alumno Juan Pérez"
   - "Busca alumnos con apellido García"
   - "Busca al alumno con CURP LOPC020202HDFXXX02"

2. **Registro de Alumnos**:
   - "Registra a Ana García con CURP GARA010101MDFXXX01 en 1° grado grupo A turno matutino"
   - "Registra a Carlos López con CURP LOPC020202HDFXXX02"

3. **Generación de Constancias**:
   - "Genera una constancia de estudios para Ana García"
   - "Genera una constancia de calificaciones para Carlos López"
   - "Genera una constancia de traslado para Ana García con foto"

4. **Transformación de Constancias**:
   - "Transforma este PDF a formato de estudios"
   - "Transforma este PDF a formato de calificaciones con foto"
   - "Transforma este PDF a formato de traslado"

5. **Actualización de Datos**:
   - "Actualiza los datos del alumno Ana García, cambia su grado a 2 y su grupo a B"
   - "Actualiza al alumno Carlos López, asigna grado 2, grupo B, turno vespertino"

6. **Eliminación de Alumnos**:
   - "Elimina al alumno Carlos López"

7. **Listado de Constancias**:
   - "Muestra las constancias de Ana García"

## Validaciones Mejoradas

Se han implementado validaciones adicionales para garantizar la coherencia del sistema:

1. **Validación de Calificaciones**:
   - Para constancias de calificaciones y traslado, se verifica que el alumno tenga calificaciones registradas
   - Si no hay calificaciones, se muestra un mensaje claro y se impide la generación

2. **Validación de PDFs para Transformación**:
   - Se verifica que el archivo exista
   - Para constancias de calificaciones y traslado, se verifica que el PDF contenga calificaciones
   - Se muestran mensajes claros sobre los tipos de constancias disponibles según los datos

## Cómo Usar la Interfaz

1. **Iniciar la Aplicación**:
   ```
   python ai_chat.py
   ```

2. **Interactuar con el Chat**:
   - Escribe comandos en el campo de texto inferior
   - Presiona Enter o haz clic en "Enviar" para ejecutar el comando
   - Los resultados se mostrarán en el área de chat

3. **Cargar un PDF**:
   - Haz clic en el botón "Cargar PDF"
   - Selecciona un archivo PDF en el diálogo de archivos
   - El PDF se mostrará en el visor y estará listo para transformación

4. **Transformar un PDF Cargado**:
   - Con un PDF cargado, escribe un comando como "Transforma este PDF a formato de estudios"
   - El sistema utilizará automáticamente el PDF cargado
   - La constancia generada se mostrará en el visor

5. **Ver Constancias Generadas**:
   - Las constancias generadas se muestran automáticamente en el visor
   - Puedes responder "sí" cuando se te pregunte si deseas abrir el archivo

## Requisitos Técnicos

- Python 3.7 o superior
- PyQt5 para la interfaz gráfica
- Google Generative AI (google-generativeai) para la interpretación de comandos
- API Key de Google Gemini configurada en el archivo .env

## Configuración

1. **Archivo .env**:
   ```
   GEMINI_API_KEY=tu-api-key-aquí
   ```

2. **Modelos de Gemini**:
   - Gemini 2.0 Flash (principal)
   - Gemini 1.5 Flash (respaldo)

## Mejoras Futuras

1. **Historial de Conversaciones**:
   - Guardar el historial entre sesiones
   - Permitir continuar conversaciones anteriores

2. **Sugerencias de Comandos**:
   - Mostrar sugerencias mientras el usuario escribe
   - Botones rápidos para comandos comunes

3. **Mejoras en la Interfaz**:
   - Temas claros/oscuros
   - Tamaño ajustable de los paneles
   - Más opciones de personalización

4. **Integración con Otras Funcionalidades**:
   - Edición de datos directamente desde la interfaz de chat
   - Visualización de estadísticas y reportes

## Conclusión

La Interfaz de Chat con IA representa un avance significativo en la usabilidad del sistema de constancias escolares, combinando la potencia del procesamiento de lenguaje natural con una interfaz gráfica intuitiva. Esta integración permite a los usuarios realizar todas las operaciones del sistema mediante comandos en lenguaje natural, mientras mantiene las ventajas visuales de una interfaz gráfica para la carga y visualización de PDFs.
