"""
Script para probar automáticamente la interpretación de comandos con Gemini
"""
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from app.core.service_provider import ServiceProvider

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def setup_gemini():
    """Configura la API de Gemini"""
    # Obtener la API key de las variables de entorno
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key or api_key == "tu-api-key-aquí":
        print("Error: No se encontró una API key válida de Gemini.")
        print("Configura la API key en el archivo .env")
        exit(1)
    
    # Configurar Gemini
    genai.configure(api_key=api_key)
    
    # Crear modelos con mecanismo de respaldo
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
       - nombre: Nombre del alumno a buscar
       - curp: CURP del alumno (opcional)
    
    2. registrar_alumno
       - nombre: Nombre completo del alumno
       - curp: CURP del alumno
       - matricula: Matrícula escolar (opcional)
       - grado: Grado escolar (1-6)
       - grupo: Grupo (A-F)
       - turno: MATUTINO o VESPERTINO
    
    3. generar_constancia
       - alumno_id: ID del alumno
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
    
    Ejemplos:
    
    - "Busca al alumno Juan Pérez" → {{"accion": "buscar_alumno", "parametros": {{"nombre": "Juan Pérez"}}}}
    - "Genera una constancia de estudios para el alumno con ID 5" → {{"accion": "generar_constancia", "parametros": {{"alumno_id": 5, "tipo": "estudio", "incluir_foto": false}}}}
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

def test_command(models, command_text):
    """
    Prueba un comando y muestra los resultados
    
    Args:
        models: Diccionario de modelos disponibles
        command_text: Texto del comando a probar
    
    Returns:
        True si el comando se interpretó correctamente, False en caso contrario
    """
    print("\n" + "=" * 80)
    print(f"PROBANDO: '{command_text}'")
    print("=" * 80)
    
    # Crear el prompt y enviar a Gemini
    prompt = create_prompt(command_text)
    print("Consultando a Gemini...")
    
    # Usar la función de respaldo para generar contenido
    response = generate_with_fallback(models, prompt)
    
    if not response:
        print("ERROR: No se pudo generar una respuesta.")
        return False
    
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
        
        # Verificar si la acción es desconocida
        if command_data.get('accion') == "desconocida":
            print("\nRESULTADO: ❌ El comando no se pudo interpretar correctamente.")
            return False
        
        print("\nRESULTADO: ✅ El comando se interpretó correctamente.")
        return True
    else:
        print("\nERROR: No se pudo interpretar la respuesta como un comando válido.")
        return False

def main():
    """Función principal"""
    print("=" * 80)
    print("  PRUEBA AUTOMÁTICA DE COMANDOS PARA EL ASISTENTE DE CONSTANCIAS")
    print("=" * 80)
    
    # Configurar Gemini
    models = setup_gemini()
    
    # Inicializar el proveedor de servicios
    service_provider = ServiceProvider.get_instance()
    print("Proveedor de servicios inicializado correctamente.")
    
    # Lista de comandos a probar
    commands = [
        # Comandos de búsqueda
        "Busca al alumno Juan Pérez",
        "Encuentra alumnos con apellido García",
        "Busca al alumno con CURP LOPM010101MDFXXX01",
        
        # Comandos de registro
        "Registra un nuevo alumno llamado Carlos López con CURP LOPC010101HDFXXX01",
        "Registra a María Rodríguez con CURP RODM010101MDFXXX01 en 3° grado grupo B turno matutino",
        "Agrega al alumno Pedro Sánchez con CURP SANP010101HDFXXX01, matrícula 12345, en 5° grado grupo A",
        
        # Comandos de generación de constancias
        "Genera una constancia de estudios para el alumno con ID 5",
        "Crea una constancia de calificaciones para Juan Pérez",
        "Genera una constancia de traslado para el alumno con ID 10 con foto",
        
        # Comandos de transformación
        "Transforma la constancia en C:/constancias/ejemplo.pdf a formato de estudios",
        "Convierte el archivo PDF en D:/documentos/constancia.pdf a constancia de calificaciones con foto",
        
        # Comandos de actualización
        "Actualiza los datos del alumno con ID 7, cambia su nombre a Luis Martínez",
        "Modifica el grado del alumno con ID 3 a 4° grado grupo C",
        
        # Comandos de eliminación
        "Elimina al alumno con ID 15",
        "Borra el registro del alumno con CURP SANP010101HDFXXX01",
        
        # Comandos ambiguos o complejos
        "Necesito una constancia para Juan",
        "Quiero registrar un alumno nuevo",
        "Muestra todos los alumnos de 3er grado"
    ]
    
    # Resultados
    results = {
        "total": len(commands),
        "success": 0,
        "failure": 0
    }
    
    # Probar cada comando
    for i, command in enumerate(commands, 1):
        print(f"\nPrueba {i}/{len(commands)}")
        success = test_command(models, command)
        
        if success:
            results["success"] += 1
        else:
            results["failure"] += 1
        
        # Pequeña pausa para no sobrecargar la API
        if i < len(commands):
            print("\nEsperando 2 segundos antes de la siguiente prueba...")
            time.sleep(2)
    
    # Mostrar resultados finales
    print("\n" + "=" * 80)
    print("  RESULTADOS FINALES")
    print("=" * 80)
    print(f"Total de comandos probados: {results['total']}")
    print(f"Comandos interpretados correctamente: {results['success']} ({results['success']/results['total']*100:.1f}%)")
    print(f"Comandos con problemas: {results['failure']} ({results['failure']/results['total']*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main()
