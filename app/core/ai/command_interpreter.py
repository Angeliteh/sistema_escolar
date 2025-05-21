"""
Intérprete de comandos para IA usando Gemini
"""
import os
import json
from typing import Dict, Any, List, Optional, Union
import google.generativeai as genai
from app.core.commands.base_command import Command
from app.core.commands.alumno_commands import (
    BuscarAlumnoCommand, RegistrarAlumnoCommand,
    ActualizarAlumnoCommand, EliminarAlumnoCommand
)
from app.core.commands.constancia_commands import (
    GenerarConstanciaCommand, TransformarConstanciaCommand,
    ListarConstanciasCommand
)
from app.core.service_provider import ServiceProvider

class GeminiProvider:
    """Proveedor de Gemini API"""

    def __init__(self, api_key=None):
        """
        Inicializa el proveedor de Gemini

        Args:
            api_key: API key para Gemini (opcional, si no se proporciona se busca en variables de entorno)
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere una API key para Gemini. Proporciona una o configura la variable de entorno GEMINI_API_KEY.")

        # Configurar la API de Gemini
        genai.configure(api_key=self.api_key)

        # Modelo a utilizar
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_response(self, prompt: str) -> str:
        """
        Genera una respuesta usando Gemini

        Args:
            prompt: Texto del prompt

        Returns:
            Respuesta generada
        """
        response = self.model.generate_content(prompt)
        return response.text

class CommandInterpreter:
    """Intérprete de comandos para IA usando Gemini"""

    def __init__(self, gemini_provider=None):
        """
        Inicializa el intérprete

        Args:
            gemini_provider: Proveedor de Gemini (opcional)
        """
        self.gemini_provider = gemini_provider or GeminiProvider()
        self.service_provider = ServiceProvider.get_instance()

    def interpret(self, text: str) -> Optional[Command]:
        """
        Interpreta un texto y devuelve un comando usando Gemini

        Args:
            text: Texto a interpretar

        Returns:
            Comando a ejecutar o None si no se pudo interpretar
        """
        # Crear el prompt para Gemini
        prompt = self._create_command_prompt(text)

        try:
            # Obtener la respuesta de Gemini
            response = self.gemini_provider.generate_response(prompt)

            # Intentar parsear la respuesta como JSON
            command_data = self._extract_json_from_response(response)

            if not command_data:
                print(f"No se pudo extraer JSON de la respuesta: {response}")
                return None

            # Crear el comando correspondiente
            return self._create_command_from_data(command_data)

        except Exception as e:
            print(f"Error al interpretar el comando: {str(e)}")
            return None

    def _create_command_prompt(self, text: str) -> str:
        """
        Crea un prompt para Gemini

        Args:
            text: Texto del usuario

        Returns:
            Prompt para Gemini
        """
        return f"""
        Eres un asistente especializado en interpretar comandos en lenguaje natural para un sistema de gestión de constancias escolares.

        El usuario te proporcionará un texto en español y tu tarea es interpretarlo y convertirlo en un comando estructurado.

        Los comandos disponibles son:

        1. BuscarAlumno: Busca alumnos por nombre o CURP
           - Parámetros: query (texto de búsqueda)

        2. RegistrarAlumno: Registra un nuevo alumno
           - Parámetros: datos (diccionario con nombre, curp, y opcionalmente matricula, grado, grupo, etc.)

        3. ActualizarAlumno: Actualiza los datos de un alumno existente
           - Parámetros: alumno_id (ID del alumno), datos (diccionario con los datos a actualizar)

        4. EliminarAlumno: Elimina un alumno
           - Parámetros: alumno_id (ID del alumno)

        5. GenerarConstancia: Genera una constancia para un alumno
           - Parámetros: alumno_id (ID del alumno), tipo_constancia (estudio, calificaciones o traslado), incluir_foto (booleano)

        6. ListarConstancias: Lista las constancias generadas para un alumno
           - Parámetros: alumno_id (ID del alumno)

        Responde ÚNICAMENTE con un objeto JSON que contenga:
        1. "command": El nombre del comando (uno de los listados arriba)
        2. "parameters": Un objeto con los parámetros necesarios para el comando
        3. "confidence": Un número del 0 al 1 que indique tu confianza en la interpretación

        Si no puedes interpretar el comando, responde con un JSON que tenga "command": "Unknown" y "confidence": 0.

        Texto del usuario: "{text}"
        """

    def _extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Extrae el JSON de la respuesta de Gemini

        Args:
            response: Respuesta de Gemini

        Returns:
            Diccionario con los datos del comando o None si no se pudo extraer
        """
        try:
            # Intentar encontrar JSON en la respuesta
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

            return None
        except Exception as e:
            print(f"Error al extraer JSON: {str(e)}")
            return None

    def _create_command_from_data(self, data: Dict[str, Any]) -> Optional[Command]:
        """
        Crea un comando a partir de los datos extraídos

        Args:
            data: Diccionario con los datos del comando

        Returns:
            Comando a ejecutar o None si no se pudo crear
        """
        command_type = data.get("command")
        parameters = data.get("parameters", {})
        confidence = data.get("confidence", 0)

        # Si la confianza es muy baja, no ejecutar el comando
        if confidence < 0.5:
            print(f"Confianza demasiado baja ({confidence}) para ejecutar el comando")
            return None

        # Crear el comando correspondiente
        if command_type == "BuscarAlumno":
            query = parameters.get("query")
            if query:
                return BuscarAlumnoCommand(query)

        elif command_type == "RegistrarAlumno":
            datos = parameters.get("datos")
            if datos and "nombre" in datos and "curp" in datos:
                return RegistrarAlumnoCommand(datos)

        elif command_type == "ActualizarAlumno":
            alumno_id = parameters.get("alumno_id")
            datos = parameters.get("datos")
            if alumno_id and datos:
                return ActualizarAlumnoCommand(alumno_id, datos)

        elif command_type == "EliminarAlumno":
            alumno_id = parameters.get("alumno_id")
            if alumno_id:
                return EliminarAlumnoCommand(alumno_id)

        elif command_type == "GenerarConstancia":
            alumno_id = parameters.get("alumno_id")
            tipo_constancia = parameters.get("tipo_constancia")
            incluir_foto = parameters.get("incluir_foto", False)

            if alumno_id and tipo_constancia:
                return GenerarConstanciaCommand(alumno_id, tipo_constancia, incluir_foto)

        elif command_type == "ListarConstancias":
            alumno_id = parameters.get("alumno_id")
            if alumno_id:
                return ListarConstanciasCommand(alumno_id)

        return None
