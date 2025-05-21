"""
Script de terminal para interactuar con el sistema de constancias mediante IA
con capacidad de ejecución de comandos
"""
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from app.core.ai.command_executor import CommandExecutor
from app.core.utils import open_file_with_default_app

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def setup_gemini():
    """Configura la API de Gemini"""
    # Intentar obtener la API key de las variables de entorno (cargadas desde .env)
    api_key = os.environ.get("GEMINI_API_KEY")

    # Si no está en las variables de entorno, pedirla al usuario
    if not api_key or api_key == "tu-api-key-aquí":
        print("No se encontró una API key válida de Gemini.")
        print("Puedes configurarla en el archivo .env o ingresarla ahora.")
        api_key = input("Por favor, ingresa tu API key de Gemini: ").strip()

        if not api_key:
            print("Error: Se requiere una API key para continuar.")
            print("Consejo: Edita el archivo .env en la raíz del proyecto para guardar tu API key.")
            exit(1)

        # Opcional: guardar la API key para esta sesión
        os.environ["GEMINI_API_KEY"] = api_key
        print("API key configurada para esta sesión.")
        print("Consejo: Para guardarla permanentemente, edita el archivo .env")
    else:
        print("API key de Gemini cargada correctamente.")

    # Configurar Gemini
    genai.configure(api_key=api_key)

    # Crear modelos con mecanismo de respaldo
    # Intentaremos con Gemini 2.0 Flash primero, luego con 1.5 Flash como respaldo
    models = {
        "gemini-2.0-flash": None,  # Primera opción (principal)
        "gemini-1.5-flash": None   # Segunda opción (respaldo)
    }

    # Intentar inicializar Gemini 2.0 Flash
    try:
        models["gemini-2.0-flash"] = genai.GenerativeModel('gemini-2.0-flash')
        print("Modelo Gemini 2.0 Flash inicializado correctamente.")
    except Exception as e:
        print(f"No se pudo inicializar Gemini 2.0 Flash: {str(e)}")

    # Intentar inicializar Gemini 1.5 Flash
    try:
        models["gemini-1.5-flash"] = genai.GenerativeModel('gemini-1.5-flash')
        print("Modelo Gemini 1.5 Flash (respaldo) inicializado correctamente.")
    except Exception as e:
        print(f"No se pudo inicializar Gemini 1.5 Flash: {str(e)}")

    # Verificar que al menos un modelo esté disponible
    if not any(models.values()):
        print("Error: No se pudo inicializar ningún modelo de Gemini.")
        print("Verifica tu API key y la disponibilidad de los modelos.")
        exit(1)

    return models

def create_prompt(user_text):
    """Crea un prompt para Gemini"""
    return f"""
    Eres un asistente especializado en un sistema de gestión de constancias escolares para una escuela primaria.

    El sistema permite:
    - Buscar alumnos por nombre o CURP
    - Registrar nuevos alumnos
    - Generar constancias (de estudio, calificaciones o traslado)
    - Transformar constancias existentes
    - Gestionar datos de alumnos

    El usuario te ha pedido: "{user_text}"

    Analiza lo que quiere hacer y responde ÚNICAMENTE con un JSON que siga este formato:

    {{
        "accion": "nombre_de_la_accion",
        "parametros": {{
            "param1": "valor1",
            "param2": "valor2"
        }}
    }}

    Acciones disponibles y sus parámetros:

    1. buscar_alumno
       - nombre: Nombre del alumno a buscar (puede ser nombre parcial)
       - curp: CURP del alumno (opcional)
       - busqueda_exacta: true para buscar coincidencias exactas, false para buscar coincidencias parciales (opcional, por defecto false)

    2. registrar_alumno
       - nombre: Nombre completo del alumno
       - curp: CURP del alumno
       - matricula: Matrícula escolar (opcional)
       - grado: Grado escolar (1-6)
       - grupo: Grupo (A-F)
       - turno: MATUTINO o VESPERTINO

    3. generar_constancia
       - alumno_id: ID del alumno (opcional si se proporciona nombre)
       - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
       - tipo: "estudio", "calificaciones" o "traslado"
       - incluir_foto: true o false

    4. transformar_constancia
       - ruta_archivo: Ruta al archivo PDF
       - tipo_destino: "estudio", "calificaciones" o "traslado"
       - incluir_foto: true o false

    5. actualizar_alumno
       - alumno_id: ID del alumno
       - datos: Objeto con los datos a actualizar (nombre, curp, grado, etc.)

    6. eliminar_alumno
       - alumno_id: ID del alumno

    7. listar_constancias
       - alumno_id: ID del alumno (opcional si se proporciona nombre)
       - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

    Ejemplos:

    - "Busca al alumno Juan Pérez" → {{"accion": "buscar_alumno", "parametros": {{"nombre": "Juan Pérez"}}}}
    - "Genera una constancia de estudios para el alumno con ID 5" → {{"accion": "generar_constancia", "parametros": {{"alumno_id": 5, "tipo": "estudio", "incluir_foto": false}}}}
    - "Genera una constancia de calificaciones para Juan Pérez" → {{"accion": "generar_constancia", "parametros": {{"nombre": "Juan Pérez", "tipo": "calificaciones", "incluir_foto": false}}}}
    - "Registra a María López con CURP LOPM010101MDFXXX01 en 3° grado grupo B turno matutino" → {{"accion": "registrar_alumno", "parametros": {{"nombre": "María López", "curp": "LOPM010101MDFXXX01", "grado": 3, "grupo": "B", "turno": "MATUTINO"}}}}

    Si no puedes determinar la acción o faltan parámetros esenciales, responde con:
    {{"accion": "desconocida", "parametros": {{"mensaje": "Explicación del problema"}}}}

    Responde ÚNICAMENTE con el JSON, sin texto adicional.
    """

def extract_json_from_response(response_text):
    """Extrae el JSON de la respuesta de Gemini"""
    try:
        # Buscar el primer { y el último }
        start = response_text.find('{')
        end = response_text.rfind('}') + 1

        if start >= 0 and end > start:
            json_str = response_text[start:end]
            return json.loads(json_str)

        return None
    except Exception as e:
        print(f"Error al extraer JSON: {str(e)}")
        print(f"Respuesta original: {response_text}")
        return None

def generate_with_fallback(models, prompt):
    """
    Intenta generar contenido con el modelo principal, y si falla, usa el modelo de respaldo

    Args:
        models: Diccionario de modelos disponibles
        prompt: Prompt para Gemini

    Returns:
        Respuesta generada o None si todos los modelos fallan
    """
    # Intentar con Gemini 2.0 Flash primero
    if models["gemini-2.0-flash"]:
        try:
            print("Usando modelo Gemini 2.0 Flash...")
            response = models["gemini-2.0-flash"].generate_content(prompt)
            return response
        except Exception as e:
            print(f"Error con Gemini 2.0 Flash: {str(e)}")
            print("Intentando con modelo de respaldo...")

    # Intentar con Gemini 1.5 Flash como respaldo
    if models["gemini-1.5-flash"]:
        try:
            print("Usando modelo Gemini 1.5 Flash...")
            response = models["gemini-1.5-flash"].generate_content(prompt)
            return response
        except Exception as e:
            print(f"Error con Gemini 1.5 Flash: {str(e)}")

    # Si llegamos aquí, todos los modelos fallaron
    return None

def mostrar_alumnos(alumnos):
    """Muestra una lista de alumnos en formato tabular"""
    if not alumnos:
        print("No se encontraron alumnos.")
        return

    # Encabezados
    print("\n{:<5} {:<30} {:<20} {:<15} {:<10}".format(
        "ID", "Nombre", "CURP", "Grado/Grupo", "Matrícula"
    ))
    print("-" * 85)

    # Datos
    for alumno in alumnos:
        grado_grupo = f"{alumno.get('grado', '')}° {alumno.get('grupo', '')}"
        print("{:<5} {:<30} {:<20} {:<15} {:<10}".format(
            alumno.get('id', ''),
            alumno.get('nombre', '')[:30],
            alumno.get('curp', '')[:20],
            grado_grupo[:15],
            alumno.get('matricula', '')[:10]
        ))

def mostrar_constancias(constancias):
    """Muestra una lista de constancias en formato tabular"""
    if not constancias:
        print("No se encontraron constancias.")
        return

    # Encabezados
    print("\n{:<5} {:<15} {:<20} {:<40}".format(
        "ID", "Tipo", "Fecha", "Archivo"
    ))
    print("-" * 85)

    # Datos
    for constancia in constancias:
        print("{:<5} {:<15} {:<20} {:<40}".format(
            constancia.get('id', ''),
            constancia.get('tipo', '')[:15],
            constancia.get('fecha_generacion', '')[:20],
            constancia.get('ruta_archivo', '')[:40] if constancia.get('ruta_archivo') else ''
        ))

def main():
    """Función principal"""
    print("=" * 80)
    print("  ASISTENTE DE CONSTANCIAS ESCOLARES CON IA (CON EJECUCIÓN DE COMANDOS)")
    print("=" * 80)
    print("Escribe tus comandos en lenguaje natural.")
    print("Ejemplos:")
    print("  - Busca al alumno Juan Pérez")
    print("  - Genera una constancia de estudios para el alumno con ID 5")
    print("  - Registra a María López con CURP LOPM010101MDFXXX01")
    print("\nEscribe 'salir' para terminar.")
    print("-" * 80)

    # Configurar Gemini
    models = setup_gemini()

    # Inicializar el ejecutor de comandos
    # Nota: El ServiceProvider se inicializa automáticamente dentro del CommandExecutor
    command_executor = CommandExecutor()
    print("Ejecutor de comandos inicializado correctamente.")

    # Bucle principal
    while True:
        try:
            # Obtener entrada del usuario
            user_input = input("\n> ").strip()

            # Verificar si el usuario quiere salir
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("¡Hasta luego!")
                break

            if not user_input:
                continue

            # Crear el prompt y enviar a Gemini
            prompt = create_prompt(user_input)
            print("\nConsultando a Gemini...")

            # Usar la función de respaldo para generar contenido
            response = generate_with_fallback(models, prompt)

            if response:
                print("\nRespuesta de Gemini:")
                print(response.text)

                # Extraer JSON de la respuesta
                command_data = extract_json_from_response(response.text)

                if command_data:
                    print("\nComando interpretado:")
                    print(f"Acción: {command_data.get('accion', 'desconocida')}")
                    print("Parámetros:")
                    for key, value in command_data.get('parametros', {}).items():
                        print(f"  - {key}: {value}")

                    # Ejecutar el comando
                    print("\nEjecutando comando...")
                    success, message, data = command_executor.execute_command(command_data)

                    # Mostrar resultado
                    if success:
                        print(f"\n✅ {message}")

                        # Mostrar datos según el tipo de comando
                        if "alumnos" in data:
                            mostrar_alumnos(data["alumnos"])

                        if "alumno" in data and isinstance(data["alumno"], dict):
                            print("\nDetalles del alumno:")
                            for key, value in data["alumno"].items():
                                print(f"  - {key}: {value}")

                        if "constancias" in data:
                            mostrar_constancias(data["constancias"])

                        if "ruta_archivo" in data:
                            print(f"\nArchivo generado: {data['ruta_archivo']}")
                            abrir = input("¿Deseas abrir el archivo? (s/n): ").strip().lower()
                            if abrir == 's':
                                open_file_with_default_app(data['ruta_archivo'])
                    else:
                        print(f"\n❌ {message}")
                else:
                    print("\nNo se pudo interpretar la respuesta como un comando válido.")
            else:
                print("\nNo se pudo generar una respuesta con ninguno de los modelos disponibles.")
                print("Verifica tu API key y la disponibilidad de los modelos.")

        except KeyboardInterrupt:
            print("\n\nOperación cancelada por el usuario.")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
