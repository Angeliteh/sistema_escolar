# 📚 GUÍA COMPLETA DE DESARROLLO ESTANDARIZADA

## 🎯 PROPÓSITO
Esta guía establece los **estándares y patrones** para continuar desarrollando el sistema de constancias con arquitectura limpia, código mantenible y funcionalidad escalable.

---

## 🏗️ ARQUITECTURA ESTANDARIZADA

### **📁 ESTRUCTURA DE MÓDULOS**
```
app/
├── core/                    # Núcleo del sistema
│   ├── config.py           # ✅ CONFIGURACIONES CENTRALIZADAS
│   ├── logging/            # ✅ SISTEMA DE LOGGING
│   └── ai/                 # ✅ INTELIGENCIA ARTIFICIAL
├── services/               # Servicios de negocio
├── ui/                     # Interfaz de usuario
└── utils/                  # Utilidades generales
```

### **🔧 PRINCIPIOS FUNDAMENTALES**
1. **Configuraciones centralizadas** en `Config`
2. **Logging estructurado** en lugar de prints
3. **Cliente Gemini único** reutilizable
4. **Separación de responsabilidades** clara
5. **Código sin duplicaciones**

---

## 📝 SISTEMA DE LOGGING ESTANDARIZADO

### **🚀 IMPLEMENTACIÓN BÁSICA**
```python
# ✅ PATRÓN ESTÁNDAR - Usar en TODOS los módulos
from app.core.logging import get_logger

class MiClase:
    def __init__(self):
        # 🎯 SIEMPRE agregar logger al constructor
        self.logger = get_logger(__name__)

    def mi_metodo(self):
        # 🎯 NIVELES DE LOGGING apropiados
        self.logger.debug("Información detallada para desarrollo")
        self.logger.info("Evento importante del flujo")
        self.logger.warning("Situación anómala pero no crítica")
        self.logger.error("Error que afecta funcionalidad")

        try:
            # código aquí
            self.logger.info("Operación completada exitosamente")
        except Exception as e:
            self.logger.error(f"Error en mi_metodo: {e}")
            raise
```

### **🎯 CUÁNDO USAR CADA NIVEL**
- **DEBUG**: Información detallada para debugging (SQL queries, datos internos)
- **INFO**: Eventos importantes del flujo (inicialización, operaciones exitosas)
- **WARNING**: Situaciones anómalas que no detienen ejecución
- **ERROR**: Errores que afectan funcionalidad
- **CRITICAL**: Errores que pueden detener el sistema

### **❌ QUÉ NO HACER**
```python
# ❌ NUNCA usar prints para debugging
print(f"Debug: {variable}")

# ❌ NUNCA hardcodear mensajes importantes
print("Error crítico en el sistema")

# ✅ SIEMPRE usar logging
self.logger.debug(f"Variable value: {variable}")
self.logger.error("Error crítico en el sistema")
```

---

## ⚙️ CONFIGURACIONES CENTRALIZADAS

### **🎯 USAR Config PARA TODO**
```python
from app.core.config import Config

# ✅ ACCEDER a configuraciones centralizadas
confidence_threshold = Config.INTERPRETATION['confidence_thresholds']['high']
greeting_phrases = Config.RESPONSES['greeting_phrases']
gemini_model = Config.GEMINI['primary_model']

# ❌ NUNCA hardcodear valores
confidence_threshold = 0.8  # MAL
greeting = "¡Hola! ¿En qué puedo ayudarte?"  # MAL
```

### **🔧 AGREGAR NUEVAS CONFIGURACIONES**
```python
# En app/core/config.py
class Config:
    # 🆕 NUEVA SECCIÓN para tu módulo
    MI_MODULO = {
        'timeout_seconds': 30,
        'max_retries': 3,
        'default_language': 'es',
        'enable_cache': True
    }
```

---

## 🤖 INTEGRACIÓN CON GEMINI LLM

### **🎯 PATRÓN ESTÁNDAR PARA USAR GEMINI**
```python
class MiInterpreter:
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

    def procesar_consulta(self, user_query):
        # 🎯 CONSTRUIR prompt estructurado
        prompt = self._build_prompt(user_query)

        # 🎯 ENVIAR a Gemini (usa configuración centralizada)
        response = self.gemini_client.send_prompt_sync(prompt)

        if response:
            # 🎯 PARSEAR respuesta JSON
            parsed_data = self._parse_json_response(response)
            self.logger.debug(f"Respuesta parseada: {parsed_data}")
            return parsed_data
        else:
            self.logger.warning("No se recibió respuesta de Gemini")
            return None

    def _build_prompt(self, user_query):
        return f"""
        CONTEXTO: Sistema de constancias escolares
        TAREA: Analizar consulta del usuario

        CONSULTA: "{user_query}"

        RESPONDE ÚNICAMENTE CON JSON:
        {{
            "accion": "nombre_accion",
            "parametros": {{"param": "valor"}},
            "confianza": 0.9
        }}
        """
```

### **🔧 MANEJO DE ERRORES CON GEMINI**
```python
def usar_gemini_con_fallback(self, prompt):
    try:
        response = self.gemini_client.send_prompt_sync(prompt)
        if response:
            return self._parse_json_response(response)
        else:
            self.logger.warning("Respuesta vacía de Gemini")
            return self._get_fallback_response()
    except Exception as e:
        self.logger.error(f"Error con Gemini: {e}")
        return self._get_fallback_response()
```

---

## 🎭 CREACIÓN DE NUEVOS INTÉRPRETES

### **🏗️ PLANTILLA ESTÁNDAR**
```python
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger
from app.core.config import Config

class MiNuevoInterpreter(BaseInterpreter):
    def __init__(self, gemini_client):
        super().__init__("MiInterpreter", priority=5)
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # 🎯 CONFIGURACIONES desde Config
        self.config = Config.MI_MODULO

    def can_handle(self, context: InterpretationContext) -> bool:
        """Determina si puede manejar esta consulta"""
        # 🎯 LÓGICA de detección aquí
        return "mi_palabra_clave" in context.user_message.lower()

    def interpret(self, context: InterpretationContext) -> InterpretationResult:
        """Interpreta la consulta del usuario"""
        try:
            self.logger.debug(f"Interpretando: {context.user_message}")

            # 🎯 PROCESAR con Gemini
            result = self._process_with_gemini(context.user_message)

            if result:
                return InterpretationResult(
                    action=result.get('accion'),
                    parameters=result.get('parametros', {}),
                    confidence=result.get('confianza', 0.5)
                )
            else:
                return self._get_fallback_result()

        except Exception as e:
            self.logger.error(f"Error en {self.name}: {e}")
            return None
```

---

## 🔄 PATRONES DE CONTINUACIÓN CONVERSACIONAL

### **🎯 IMPLEMENTAR AUTO-REFLEXIÓN**
```python
def _validate_and_generate_response(self, user_query, data):
    """Genera respuesta con auto-reflexión para continuaciones"""

    # 🎯 PROMPT para respuesta + auto-reflexión
    prompt = f"""
    CONTEXTO: Sistema de constancias escolares
    CONSULTA: "{user_query}"
    DATOS: {self._format_data_for_prompt(data)}

    GENERA RESPUESTA Y ANALIZA CONTINUACIÓN:
    {{
        "respuesta_usuario": "Respuesta clara y profesional",
        "reflexion_conversacional": {{
            "espera_continuacion": true/false,
            "tipo_esperado": "selection/action/confirmation/specification",
            "razonamiento": "Por qué esperas esa continuación"
        }}
    }}
    """

    response = self.gemini_client.send_prompt_sync(prompt)
    return self._parse_json_response(response)
```

### **🔧 MANEJAR PILA CONVERSACIONAL**
```python
def _add_to_conversation_stack(self, user_query, response_data, awaiting_type):
    """Agrega nivel a la pila conversacional"""
    level = {
        'user_query': user_query,
        'data': response_data.get('data', []),
        'row_count': len(response_data.get('data', [])),
        'awaiting_type': awaiting_type,
        'timestamp': datetime.now().isoformat()
    }

    self.conversation_stack.append(level)
    self.logger.debug(f"Agregado a pila conversacional: Nivel {len(self.conversation_stack)}")
```

---

## 📋 CHECKLIST PARA NUEVAS FUNCIONALIDADES

### **✅ ANTES DE EMPEZAR**
- [ ] Definir configuraciones en `Config`
- [ ] Planificar estructura de logging
- [ ] Identificar integración con Gemini
- [ ] Diseñar manejo de errores

### **✅ DURANTE DESARROLLO**
- [ ] Usar `get_logger(__name__)` en constructor
- [ ] Acceder configuraciones desde `Config`
- [ ] Implementar manejo de errores con logging
- [ ] Usar `gemini_client.send_prompt_sync()` para LLM
- [ ] Parsear respuestas JSON estructuradas

### **✅ ANTES DE COMMIT**
- [ ] Verificar que no hay `print()` statements
- [ ] Confirmar que configuraciones están en `Config`
- [ ] Probar manejo de errores
- [ ] Verificar logging apropiado
- [ ] Documentar nuevas configuraciones

---

## 🚀 PRÓXIMOS DESARROLLOS

### **🎯 CONSTANCIAS INTERPRETER**
```python
# Estructura sugerida
class ConstanciaInterpreter(BaseInterpreter):
    def __init__(self, gemini_client, pdf_generator):
        super().__init__("ConstanciaInterpreter", priority=8)
        self.gemini_client = gemini_client
        self.pdf_generator = pdf_generator
        self.logger = get_logger(__name__)

        # Configuraciones específicas
        self.config = Config.CONSTANCIAS  # Agregar a Config
```

### **🎯 HELPER INTERPRETER**
```python
# Estructura sugerida
class HelpInterpreter(BaseInterpreter):
    def __init__(self, gemini_client):
        super().__init__("HelpInterpreter", priority=3)
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

        # Configuraciones de ayuda
        self.config = Config.HELP_SYSTEM  # Agregar a Config
```

---

## 🎯 CONCLUSIÓN

**Esta guía garantiza:**
- ✅ **Consistencia** en todo el desarrollo
- ✅ **Mantenibilidad** a largo plazo
- ✅ **Escalabilidad** sin refactoring
- ✅ **Debugging** eficiente
- ✅ **Código profesional** enterprise-ready

**¡Sigue estos patrones y el sistema crecerá de forma ordenada y mantenible!** 🚀

---

## 📖 EJEMPLOS PRÁCTICOS DETALLADOS

### **🎯 EJEMPLO 1: CREAR CONSTANCIA INTERPRETER**

#### **PASO 1: Agregar configuraciones**
```python
# En app/core/config.py
CONSTANCIAS = {
    'tipos_disponibles': ['estudios', 'calificaciones', 'traslado'],
    'formatos_pdf': ['oficial', 'gobierno'],
    'timeout_generacion': 60,
    'max_intentos': 3,
    'validar_datos': True,
    'incluir_foto': False
}
```

#### **PASO 2: Implementar intérprete**
```python
# En app/core/ai/interpretation/constancia_interpreter.py
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger
from app.core.config import Config

class ConstanciaInterpreter(BaseInterpreter):
    def __init__(self, gemini_client, pdf_generator):
        super().__init__("ConstanciaInterpreter", priority=8)
        self.gemini_client = gemini_client
        self.pdf_generator = pdf_generator
        self.logger = get_logger(__name__)

        # 🎯 CONFIGURACIONES centralizadas
        self.config = Config.CONSTANCIAS

    def can_handle(self, context: InterpretationContext) -> bool:
        """Detecta solicitudes de constancias"""
        keywords = ['constancia', 'certificado', 'documento', 'generar', 'crear']
        user_lower = context.user_message.lower()
        return any(keyword in user_lower for keyword in keywords)

    def interpret(self, context: InterpretationContext) -> InterpretationResult:
        """Procesa solicitud de constancia"""
        try:
            self.logger.info(f"Procesando solicitud de constancia: {context.user_message}")

            # 🎯 ANALIZAR con Gemini
            analysis = self._analyze_constancia_request(context.user_message)

            if analysis and analysis.get('es_solicitud_constancia'):
                return self._process_constancia_request(analysis, context)
            else:
                self.logger.debug("No es una solicitud de constancia válida")
                return None

        except Exception as e:
            self.logger.error(f"Error en ConstanciaInterpreter: {e}")
            return None

    def _analyze_constancia_request(self, user_message):
        """Analiza la solicitud con Gemini"""
        prompt = f"""
        CONTEXTO: Sistema de constancias escolares
        TIPOS DISPONIBLES: {self.config['tipos_disponibles']}

        ANALIZA ESTA SOLICITUD: "{user_message}"

        RESPONDE CON JSON:
        {{
            "es_solicitud_constancia": true/false,
            "tipo_constancia": "estudios/calificaciones/traslado",
            "alumno_mencionado": "nombre si se menciona",
            "formato_solicitado": "oficial/gobierno",
            "confianza": 0.9
        }}
        """

        response = self.gemini_client.send_prompt_sync(prompt)
        return self._parse_json_response(response)
```

### **🎯 EJEMPLO 2: CREAR HELP INTERPRETER**

#### **PASO 1: Configuraciones**
```python
# En app/core/config.py
HELP_SYSTEM = {
    'categorias_ayuda': ['consultas', 'constancias', 'navegacion', 'errores'],
    'respuestas_predefinidas': {
        'consultas': "Puedo ayudarte a buscar alumnos por nombre, grado, grupo...",
        'constancias': "Puedo generar constancias de estudios, calificaciones...",
        'navegacion': "Usa comandos como /help, /stats, /history...",
        'errores': "Si hay un error, revisa los logs o contacta soporte..."
    },
    'ejemplos_consultas': [
        "buscar alumno Juan",
        "generar constancia de estudios",
        "cuántos alumnos hay en 3er grado"
    ]
}
```

#### **PASO 2: Implementación**
```python
class HelpInterpreter(BaseInterpreter):
    def __init__(self, gemini_client):
        super().__init__("HelpInterpreter", priority=3)
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)
        self.config = Config.HELP_SYSTEM

    def can_handle(self, context: InterpretationContext) -> bool:
        help_keywords = ['ayuda', 'help', 'cómo', 'qué puedo', 'comandos']
        user_lower = context.user_message.lower()
        return any(keyword in user_lower for keyword in help_keywords)

    def interpret(self, context: InterpretationContext) -> InterpretationResult:
        try:
            self.logger.info(f"Procesando solicitud de ayuda: {context.user_message}")

            # 🎯 CATEGORIZAR solicitud de ayuda
            category = self._categorize_help_request(context.user_message)

            # 🎯 GENERAR respuesta apropiada
            help_response = self._generate_help_response(category, context.user_message)

            return InterpretationResult(
                action="mostrar_ayuda",
                parameters={
                    "categoria": category,
                    "mensaje": help_response,
                    "ejemplos": self.config['ejemplos_consultas']
                },
                confidence=0.9
            )

        except Exception as e:
            self.logger.error(f"Error en HelpInterpreter: {e}")
            return None
```

---

## 🔧 INTEGRACIÓN CON MASTER INTERPRETER

### **🎯 REGISTRAR NUEVOS INTÉRPRETES**
```python
# En app/core/ai/interpretation/master_interpreter.py
class MasterInterpreter:
    def __init__(self, db_path: str, gemini_client):
        # ... código existente ...

        # 🆕 AGREGAR nuevos intérpretes
        self.constancia_interpreter = ConstanciaInterpreter(gemini_client, pdf_generator)
        self.help_interpreter = HelpInterpreter(gemini_client)

    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        # ... detección de intención existente ...

        if intention.intention_type == 'generar_constancia':
            self.logger.debug("Dirigiendo a intérprete de constancias")
            return self.constancia_interpreter.interpret(context)

        elif intention.intention_type == 'ayuda_sistema':
            self.logger.debug("Dirigiendo a intérprete de ayuda")
            return self.help_interpreter.interpret(context)
```

---

## 📊 TESTING Y VALIDACIÓN

### **🎯 TESTING ESTÁNDAR**
```python
# tests/test_mi_interpreter.py
import unittest
from unittest.mock import Mock, patch
from app.core.ai.interpretation.mi_interpreter import MiInterpreter

class TestMiInterpreter(unittest.TestCase):
    def setUp(self):
        self.mock_gemini = Mock()
        self.interpreter = MiInterpreter(self.mock_gemini)

    def test_can_handle_valid_request(self):
        context = Mock()
        context.user_message = "mi palabra clave aquí"

        result = self.interpreter.can_handle(context)
        self.assertTrue(result)

    def test_interpret_success(self):
        # 🎯 MOCK respuesta de Gemini
        self.mock_gemini.send_prompt_sync.return_value = '''
        {
            "accion": "mi_accion",
            "parametros": {"param": "valor"},
            "confianza": 0.9
        }
        '''

        context = Mock()
        context.user_message = "test query"

        result = self.interpreter.interpret(context)

        self.assertIsNotNone(result)
        self.assertEqual(result.action, "mi_accion")
        self.assertEqual(result.confidence, 0.9)
```

### **🎯 LOGGING EN TESTS**
```python
def test_with_logging(self):
    with self.assertLogs('app.core.ai.interpretation.mi_interpreter', level='DEBUG') as log:
        # código de test aquí
        pass

    # Verificar que se loggeó correctamente
    self.assertIn('DEBUG:app.core.ai.interpretation.mi_interpreter:Mensaje esperado', log.output)
```

---

## 🚀 DEPLOYMENT Y MONITOREO

### **🎯 CONFIGURACIÓN POR ENTORNO**
```python
# config/development.py
class DevelopmentConfig(Config):
    LOGGING = {
        'level': 'DEBUG',
        'console_enabled': True,
        'debug_mode': True
    }

# config/production.py
class ProductionConfig(Config):
    LOGGING = {
        'level': 'INFO',
        'console_enabled': False,
        'debug_mode': False
    }
```

### **🎯 MONITOREO DE LOGS**
```bash
# Monitorear logs en tiempo real
tail -f logs/system.log

# Buscar errores específicos
grep "ERROR" logs/system.log | tail -20

# Analizar rendimiento de Gemini
grep "Gemini" logs/system.log | grep "tiempo"
```

---

## 📋 CHECKLIST FINAL DE CALIDAD

### **✅ CÓDIGO LIMPIO**
- [ ] Sin prints de debugging
- [ ] Configuraciones en Config
- [ ] Logging apropiado en todos los métodos
- [ ] Manejo de errores con try/catch
- [ ] Documentación en docstrings

### **✅ ARQUITECTURA**
- [ ] Hereda de BaseInterpreter
- [ ] Usa gemini_client centralizado
- [ ] Implementa can_handle() y interpret()
- [ ] Registrado en MasterInterpreter
- [ ] Configuraciones centralizadas

### **✅ TESTING**
- [ ] Tests unitarios implementados
- [ ] Mocks para dependencias externas
- [ ] Cobertura de casos edge
- [ ] Validación de logging
- [ ] Tests de integración

**¡Con esta guía tienes todo lo necesario para desarrollar funcionalidades robustas y mantenibles!** 🎯
