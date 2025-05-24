"""
Procesador de mensajes y comandos para la interfaz de chat
"""
import json
import random
from datetime import datetime

from app.core.ai.command_executor import CommandExecutor

class MessageProcessor:
    """Procesador de mensajes y comandos para la interfaz de chat"""
    
    def __init__(self):
        """Inicializa el procesador de mensajes"""
        self.command_executor = CommandExecutor()
        
        # Frases de variación para respuestas más naturales
        self.greeting_phrases = [
            "¡Hola! ¿En qué puedo ayudarte hoy?",
            "¡Buen día! ¿Qué necesitas hacer?",
            "¡Saludos! Estoy listo para asistirte.",
            "¿En qué puedo ayudarte con las constancias hoy?",
            "Estoy aquí para ayudarte. ¿Qué necesitas?"
        ]
        
        self.success_phrases = [
            "¡Listo! He completado la tarea con éxito.",
            "¡Perfecto! La operación se ha realizado correctamente.",
            "¡Excelente! Todo ha salido bien.",
            "¡Tarea completada! Todo en orden.",
            "¡Genial! He terminado lo que me pediste."
        ]
    
    def create_prompt(self, user_text, current_pdf=None):
        """Crea un prompt para Gemini"""
        # Añadir información sobre el PDF cargado si existe
        pdf_info = ""
        if current_pdf:
            pdf_info = f"\nEl usuario ha cargado un PDF: {current_pdf}"
        
        return f"""
        Eres un asistente especializado en un sistema de gestión de constancias escolares para una escuela primaria.

        El sistema permite:
        - Buscar alumnos por nombre o CURP
        - Buscar alumnos por criterios como grado, grupo, turno, etc.
        - Registrar nuevos alumnos
        - Generar constancias (de estudio, calificaciones o traslado)
        - Transformar constancias existentes
        - Gestionar datos de alumnos{pdf_info}

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

        0. mostrar_ayuda
           - No requiere parámetros
           - Usa esta acción cuando el usuario pregunte qué puede hacer el sistema, pida ayuda, o solicite información sobre las funcionalidades disponibles
           - Ejemplos de consultas: "¿Qué puedes hacer?", "Ayuda", "Muéstrame las funciones", "¿Cómo te uso?"

        1. buscar_alumno
           - nombre: Nombre del alumno a buscar (puede ser nombre parcial)
           - curp: CURP del alumno (opcional)
           - busqueda_exacta: true para buscar coincidencias exactas, false para buscar coincidencias parciales (opcional, por defecto false)

        2. buscar_alumnos_por_criterio
           - criterio: Campo por el que se va a buscar ("grado", "grupo", "turno", "ciclo_escolar", "escuela")
           - valor: Valor a buscar

        3. registrar_alumno
           - nombre: Nombre completo del alumno
           - curp: CURP del alumno
           - matricula: Matrícula escolar (opcional)
           - grado: Grado escolar (1-6)
           - grupo: Grupo (A-F)
           - turno: MATUTINO o VESPERTINO

        4. generar_constancia
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
           - tipo: "estudio", "calificaciones" o "traslado"
           - incluir_foto: true o false

        5. transformar_constancia
           - ruta_archivo: Ruta al archivo PDF (usa el PDF cargado si está disponible)
           - tipo_destino: "estudio", "calificaciones" o "traslado"
           - incluir_foto: true o false
           - guardar_alumno: true o false (si se deben guardar los datos del alumno en la base de datos)

        6. guardar_alumno_pdf
           - ruta_archivo: Ruta al archivo PDF (usa el PDF cargado si está disponible)

        7. actualizar_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
           - datos: Objeto con los datos a actualizar (nombre, curp, grado, etc.)

        8. eliminar_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        9. listar_constancias
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        10. detalles_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        11. obtener_dato_especifico
           - nombre: Nombre del alumno para buscar (opcional si se proporciona alumno_id)
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - campo: Campo específico a consultar ("curp", "grado", "grupo", "turno", "matricula", "fecha_nacimiento", "escuela", "cct")
           - Usa esta acción cuando el usuario pregunte por un dato específico de un alumno
           - Ejemplos de consultas: "¿Cuál es la CURP de Juan?", "¿En qué grado está María?", "¿A qué grupo pertenece el alumno con ID 5?"

        Responde ÚNICAMENTE con el JSON, sin texto adicional.
        """
    
    def extract_json_from_response(self, response_text):
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
    
    def process_command(self, command_data, current_pdf=None):
        """Procesa un comando y devuelve el resultado"""
        if not command_data:
            return False, "No se pudo entender tu solicitud. ¿Podrías reformularla?", {}
        
        # Procesar el comando
        accion = command_data.get("accion", "desconocida")
        parametros = command_data.get("parametros", {})
        
        # Si es una transformación y hay un PDF cargado, usar esa ruta
        if accion == "transformar_constancia" and current_pdf:
            # Verificar si el usuario quiere guardar los datos
            if "guardar" in parametros and parametros["guardar"]:
                parametros["guardar_alumno"] = True
            elif "guardar_alumno" in parametros and parametros["guardar_alumno"]:
                # Asegurarse de que el valor sea booleano
                parametros["guardar_alumno"] = True
            
            # Si hay un PDF cargado, usar esa ruta
            if not parametros.get("ruta_archivo"):
                parametros["ruta_archivo"] = current_pdf
            
            command_data["parametros"] = parametros
        
        # Si es guardar alumno desde PDF y hay un PDF cargado, usar esa ruta
        if accion == "guardar_alumno_pdf" and current_pdf:
            if not parametros.get("ruta_archivo"):
                parametros["ruta_archivo"] = current_pdf
            
            command_data["parametros"] = parametros
        
        # Ejecutar el comando
        return self.command_executor.execute_command(command_data)
    
    def get_current_time(self):
        """Obtiene la hora actual en formato HH:MM"""
        now = datetime.now()
        return now.strftime("%H:%M")
    
    def get_random_greeting(self):
        """Devuelve un saludo aleatorio"""
        return random.choice(self.greeting_phrases)
    
    def get_random_success_phrase(self):
        """Devuelve una frase de éxito aleatoria"""
        return random.choice(self.success_phrases)
