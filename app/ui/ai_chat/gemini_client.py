"""
Cliente para la API de Gemini
"""
import os
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import google.generativeai as genai

class GeminiThread(QThread):
    """Hilo para ejecutar consultas a Gemini sin bloquear la interfaz"""
    response_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def __init__(self, models, prompt):
        super().__init__()
        self.models = models
        self.prompt = prompt

    def run(self):
        try:
            # Intentar con Gemini 2.0 Flash primero
            if self.models["gemini-2.0-flash"]:
                try:
                    response = self.models["gemini-2.0-flash"].generate_content(self.prompt)
                    self.response_ready.emit(response)
                    return
                except Exception:
                    # Si falla, intentar con el modelo de respaldo
                    pass

            # Intentar con Gemini 1.5 Flash como respaldo
            if self.models["gemini-1.5-flash"]:
                try:
                    response = self.models["gemini-1.5-flash"].generate_content(self.prompt)
                    self.response_ready.emit(response)
                    return
                except Exception as e:
                    self.error_occurred.emit(f"Error con Gemini 1.5 Flash: {str(e)}")
            else:
                self.error_occurred.emit("No hay modelos disponibles")

        except Exception as e:
            self.error_occurred.emit(f"Error en el hilo: {str(e)}")

class GeminiClient(QObject):
    """Cliente para la API de Gemini"""
    
    response_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.models = {
            "gemini-2.0-flash": None,  # Primera opción (principal)
            "gemini-1.5-flash": None   # Segunda opción (respaldo)
        }
        self.setup_gemini()
    
    def setup_gemini(self):
        """Configura la API de Gemini"""
        # Obtener la API key de las variables de entorno
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key or api_key == "tu-api-key-aquí":
            self.error_occurred.emit("No se encontró una API key válida de Gemini")
            return False
        
        # Configurar Gemini
        genai.configure(api_key=api_key)
        
        # Inicializar Gemini 2.0 Flash
        try:
            self.models["gemini-2.0-flash"] = genai.GenerativeModel('gemini-2.0-flash')
            print("Modelo Gemini 2.0 Flash inicializado correctamente.")
        except Exception as e:
            print(f"No se pudo inicializar Gemini 2.0 Flash: {str(e)}")
        
        # Inicializar Gemini 1.5 Flash
        try:
            self.models["gemini-1.5-flash"] = genai.GenerativeModel('gemini-1.5-flash')
            print("Modelo Gemini 1.5 Flash (respaldo) inicializado correctamente.")
        except Exception as e:
            print(f"No se pudo inicializar Gemini 1.5 Flash: {str(e)}")
        
        # Verificar que al menos un modelo esté disponible
        if not any(self.models.values()):
            self.error_occurred.emit("No se pudo inicializar ningún modelo de Gemini")
            return False
        
        return True
    
    def send_prompt(self, prompt):
        """Envía un prompt a Gemini"""
        # Crear y ejecutar el hilo para Gemini
        self.gemini_thread = GeminiThread(self.models, prompt)
        self.gemini_thread.response_ready.connect(self._handle_response)
        self.gemini_thread.error_occurred.connect(self._handle_error)
        self.gemini_thread.start()
    
    def _handle_response(self, response):
        """Maneja la respuesta de Gemini"""
        self.response_ready.emit(response)
    
    def _handle_error(self, error_message):
        """Maneja errores en la comunicación con Gemini"""
        self.error_occurred.emit(error_message)
