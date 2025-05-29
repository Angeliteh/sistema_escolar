"""
Cliente para la API de Gemini - CENTRALIZADO Y OPTIMIZADO
"""
import os
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import google.generativeai as genai
from dotenv import load_dotenv
from app.core.logging import get_logger
from app.core.config import Config

# Cargar variables de entorno
load_dotenv()

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
            # 🆕 USAR CONFIGURACIÓN CENTRALIZADA - obtener nombres de modelos dinámicamente
            model_names = list(self.models.keys())
            primary_model = model_names[0] if len(model_names) > 0 else None
            fallback_model = model_names[1] if len(model_names) > 1 else None

            # Intentar con modelo principal primero
            if primary_model and self.models.get(primary_model):
                try:
                    response = self.models[primary_model].generate_content(self.prompt)
                    self.response_ready.emit(response)
                    return
                except Exception:
                    # Si falla, intentar con el modelo de respaldo
                    pass

            # Intentar con modelo de respaldo
            if fallback_model and self.models.get(fallback_model):
                try:
                    response = self.models[fallback_model].generate_content(self.prompt)
                    self.response_ready.emit(response)
                    return
                except Exception as e:
                    self.error_occurred.emit(f"Error con {fallback_model}: {str(e)}")
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
        self.logger = get_logger(__name__)

        # 🆕 USAR CONFIGURACIÓN CENTRALIZADA CON MÚLTIPLES API KEYS
        self.config = Config.GEMINI
        self.api_keys = {}  # Almacenar API keys disponibles
        self.model_instances = {}  # Almacenar instancias de modelos por API key
        self.setup_gemini()

    def setup_gemini(self):
        """Configura múltiples API keys y modelos de Gemini"""
        # 🆕 CARGAR MÚLTIPLES API KEYS
        self._load_api_keys()

        if not self.api_keys:
            self.error_occurred.emit("No se encontraron API keys válidas de Gemini")
            return False

        # 🆕 INICIALIZAR MODELOS CON MÚLTIPLES API KEYS
        self._initialize_models()

        # Verificar que al menos una combinación modelo+API key esté disponible
        if not any(self.model_instances.values()):
            self.error_occurred.emit("No se pudo inicializar ningún modelo de Gemini")
            return False

        self.logger.info(f"✅ Gemini configurado con {len(self.api_keys)} API keys y {len(self.model_instances)} modelos")
        return True

    def _load_api_keys(self):
        """Carga todas las API keys disponibles desde variables de entorno"""
        for key_name, env_var in self.config['api_keys'].items():
            api_key = os.environ.get(env_var)
            if api_key and api_key != "tu-api-key-aquí":
                self.api_keys[key_name] = api_key
                self.logger.info(f"✅ API key '{key_name}' cargada desde {env_var}")
            else:
                self.logger.warning(f"❌ API key '{key_name}' no encontrada en {env_var}")

    def _initialize_models(self):
        """Inicializa modelos para cada API key disponible"""
        for key_name, api_key in self.api_keys.items():
            try:
                # Configurar Gemini con esta API key
                genai.configure(api_key=api_key)

                # Inicializar modelos para esta API key
                models_for_key = {}

                # Modelo principal
                try:
                    primary_model = self.config['primary_model']
                    # 🛠️ CONFIGURAR PARÁMETROS DE GENERACIÓN
                    generation_config = genai.types.GenerationConfig(
                        max_output_tokens=8192,  # Aumentar límite de tokens
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40
                    )
                    models_for_key[primary_model] = genai.GenerativeModel(
                        primary_model,
                        generation_config=generation_config
                    )
                    self.logger.debug(f"✅ {primary_model} inicializado con API key '{key_name}'")
                except Exception as e:
                    self.logger.warning(f"❌ No se pudo inicializar {primary_model} con '{key_name}': {e}")

                # Modelo de respaldo
                if self.config['enable_fallback']:
                    try:
                        fallback_model = self.config['fallback_model']
                        # 🛠️ MISMA CONFIGURACIÓN PARA MODELO DE RESPALDO
                        generation_config = genai.types.GenerationConfig(
                            max_output_tokens=8192,  # Aumentar límite de tokens
                            temperature=0.7,
                            top_p=0.8,
                            top_k=40
                        )
                        models_for_key[fallback_model] = genai.GenerativeModel(
                            fallback_model,
                            generation_config=generation_config
                        )
                        self.logger.debug(f"✅ {fallback_model} inicializado con API key '{key_name}'")
                    except Exception as e:
                        self.logger.warning(f"❌ No se pudo inicializar {fallback_model} con '{key_name}': {e}")

                # Guardar modelos para esta API key
                if models_for_key:
                    self.model_instances[key_name] = models_for_key

            except Exception as e:
                self.logger.error(f"❌ Error configurando API key '{key_name}': {e}")

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

    def send_prompt_sync(self, prompt):
        """Envía un prompt a Gemini con estrategia simple: 2.0 → 1.5"""
        try:
            # 🎯 ESTRATEGIA SIMPLE: Solo 2 modelos
            return self._send_with_single_api_fallback(prompt)

        except Exception as e:
            self.logger.error(f"Error en consulta síncrona: {str(e)}")
            return None

    # MÉTODO ELIMINADO: _send_with_multi_api_fallback() era demasiado complejo
    # Usar _send_with_single_api_fallback() para simplicidad

    def _send_with_single_api_fallback(self, prompt):
        """Envía prompt usando estrategia de fallback tradicional (una sola API key)"""
        primary_model = self.config['primary_model']
        fallback_model = self.config['fallback_model']
        primary_api_key = list(self.api_keys.keys())[0] if self.api_keys else None

        if not primary_api_key or primary_api_key not in self.model_instances:
            self.logger.error("No hay API keys disponibles")
            return None

        models = self.model_instances[primary_api_key]

        # Configurar API key
        genai.configure(api_key=self.api_keys[primary_api_key])

        # Intentar con modelo principal
        if primary_model in models:
            try:
                self.logger.debug(f"🎯 Intentando con modelo principal: {primary_model}")
                response = models[primary_model].generate_content(prompt)
                if response and response.text:
                    self.logger.debug(f"✅ Respuesta exitosa con {primary_model}")
                    return response.text
            except Exception as e:
                self.logger.warning(f"❌ Error con {primary_model}: {str(e)}")

        # Intentar con modelo de respaldo
        if self.config['enable_fallback'] and fallback_model in models:
            try:
                self.logger.info(f"🔄 ACTIVANDO FALLBACK: Intentando con {fallback_model}")
                response = models[fallback_model].generate_content(prompt)
                if response and response.text:
                    self.logger.info(f"✅ FALLBACK EXITOSO: Respuesta obtenida con {fallback_model}")
                    return response.text
            except Exception as e:
                self.logger.error(f"❌ FALLBACK FALLÓ: Error con {fallback_model}: {str(e)}")

        return None

    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parsea una respuesta JSON del modelo"""
        try:
            import json
            import re

            # Limpiar la respuesta
            clean_response = response.strip()

            # Buscar JSON en la respuesta
            json_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```',
                r'(\{.*?\})'
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, clean_response, re.DOTALL)
                if matches:
                    try:
                        parsed_json = json.loads(matches[0])
                        return parsed_json
                    except json.JSONDecodeError:
                        continue

            # Si no encuentra JSON, intentar parsear directamente
            try:
                parsed_json = json.loads(clean_response)
                return parsed_json
            except json.JSONDecodeError:
                self.logger.warning(f"No se pudo parsear JSON: {clean_response}")
                return None

        except Exception as e:
            self.logger.error(f"Error parseando JSON: {e}")
            return None
