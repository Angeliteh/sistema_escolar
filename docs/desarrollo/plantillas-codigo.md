# 🧩 PLANTILLAS DE CÓDIGO ESTANDARIZADAS

## 🎯 PROPÓSITO
Plantillas listas para usar que siguen todos los estándares del sistema: logging centralizado, configuraciones en Config, integración con Gemini, y arquitectura limpia.

---

## 🤖 PLANTILLA: NUEVO INTÉRPRETE

### **📁 Archivo: `app/core/ai/interpretation/mi_interpreter.py`**
```python
"""
Intérprete para [DESCRIPCIÓN DE FUNCIONALIDAD]
"""
from typing import Optional
from app.core.ai.interpretation.base_interpreter import BaseInterpreter, InterpretationContext, InterpretationResult
from app.core.logging import get_logger
from app.core.config import Config

class MiInterpreter(BaseInterpreter):
    """Intérprete especializado en [FUNCIONALIDAD]"""
    
    def __init__(self, gemini_client, **dependencies):
        super().__init__("MiInterpreter", priority=5)  # Ajustar prioridad según necesidad
        
        # 🎯 DEPENDENCIAS
        self.gemini_client = gemini_client
        # Agregar otras dependencias aquí
        
        # 🎯 LOGGING CENTRALIZADO
        self.logger = get_logger(__name__)
        
        # 🎯 CONFIGURACIONES CENTRALIZADAS
        self.config = Config.MI_MODULO  # Definir en Config
        
        self.logger.info(f"{self.name} inicializado correctamente")
        
    def can_handle(self, context: InterpretationContext) -> bool:
        """
        Determina si este intérprete puede manejar la consulta
        
        Args:
            context: Contexto de interpretación
            
        Returns:
            True si puede manejar la consulta
        """
        try:
            # 🎯 PALABRAS CLAVE desde configuración
            keywords = self.config.get('keywords', [])
            user_lower = context.user_message.lower()
            
            can_handle = any(keyword in user_lower for keyword in keywords)
            
            if can_handle:
                self.logger.debug(f"Puede manejar consulta: {context.user_message}")
            
            return can_handle
            
        except Exception as e:
            self.logger.error(f"Error en can_handle: {e}")
            return False
            
    def interpret(self, context: InterpretationContext) -> Optional[InterpretationResult]:
        """
        Interpreta la consulta del usuario
        
        Args:
            context: Contexto de interpretación
            
        Returns:
            Resultado de interpretación o None si falla
        """
        try:
            self.logger.info(f"Interpretando: {context.user_message}")
            
            # 🎯 PASO 1: Analizar consulta con Gemini
            analysis = self._analyze_with_gemini(context.user_message)
            
            if not analysis:
                self.logger.warning("No se pudo analizar la consulta")
                return None
                
            # 🎯 PASO 2: Procesar según análisis
            if analysis.get('es_valida', False):
                return self._process_valid_request(analysis, context)
            else:
                self.logger.debug("Consulta no válida para este intérprete")
                return None
                
        except Exception as e:
            self.logger.error(f"Error en interpret: {e}")
            return None
            
    def _analyze_with_gemini(self, user_message: str) -> Optional[dict]:
        """Analiza la consulta usando Gemini"""
        try:
            prompt = self._build_analysis_prompt(user_message)
            
            self.logger.debug("Enviando prompt a Gemini para análisis")
            response = self.gemini_client.send_prompt_sync(prompt)
            
            if response:
                parsed = self._parse_json_response(response)
                self.logger.debug(f"Análisis completado: {parsed}")
                return parsed
            else:
                self.logger.warning("Respuesta vacía de Gemini")
                return None
                
        except Exception as e:
            self.logger.error(f"Error en análisis con Gemini: {e}")
            return None
            
    def _build_analysis_prompt(self, user_message: str) -> str:
        """Construye el prompt para análisis"""
        return f"""
        CONTEXTO: Sistema de constancias escolares
        MÓDULO: {self.name}
        CONFIGURACIÓN: {self.config}
        
        ANALIZA ESTA CONSULTA: "{user_message}"
        
        RESPONDE ÚNICAMENTE CON JSON:
        {{
            "es_valida": true/false,
            "categoria": "categoria_detectada",
            "parametros_extraidos": {{"param": "valor"}},
            "confianza": 0.9,
            "razonamiento": "Por qué es/no es válida"
        }}
        """
        
    def _process_valid_request(self, analysis: dict, context: InterpretationContext) -> InterpretationResult:
        """Procesa una solicitud válida"""
        try:
            # 🎯 LÓGICA ESPECÍFICA DEL INTÉRPRETE AQUÍ
            
            # Ejemplo de procesamiento
            categoria = analysis.get('categoria')
            parametros = analysis.get('parametros_extraidos', {})
            
            self.logger.info(f"Procesando categoría: {categoria}")
            
            # Generar resultado
            return InterpretationResult(
                action=f"accion_{categoria}",
                parameters={
                    "mensaje": "Procesamiento completado",
                    "categoria": categoria,
                    **parametros
                },
                confidence=analysis.get('confianza', 0.5)
            )
            
        except Exception as e:
            self.logger.error(f"Error procesando solicitud: {e}")
            return None
            
    def _parse_json_response(self, response: str) -> Optional[dict]:
        """Parsea respuesta JSON de Gemini"""
        try:
            import json
            import re
            
            # Extraer JSON de la respuesta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                self.logger.warning("No se encontró JSON válido en la respuesta")
                return None
                
        except Exception as e:
            self.logger.error(f"Error parseando JSON: {e}")
            return None
```

---

## ⚙️ PLANTILLA: CONFIGURACIÓN EN CONFIG

### **📁 Agregar en: `app/core/config.py`**
```python
class Config:
    # ... configuraciones existentes ...
    
    # 🆕 CONFIGURACIÓN PARA NUEVO MÓDULO
    MI_MODULO = {
        # Palabras clave para detección
        'keywords': ['palabra1', 'palabra2', 'frase clave'],
        
        # Umbrales de confianza
        'confidence_threshold': 0.7,
        'min_confidence': 0.5,
        
        # Configuraciones de comportamiento
        'max_retries': 3,
        'timeout_seconds': 30,
        'enable_cache': True,
        
        # Respuestas predefinidas
        'messages': {
            'success': "Operación completada exitosamente",
            'error': "Error procesando solicitud",
            'not_found': "No se encontraron resultados",
            'invalid_input': "Entrada no válida"
        },
        
        # Configuraciones específicas del módulo
        'opciones_disponibles': ['opcion1', 'opcion2', 'opcion3'],
        'formato_salida': 'json',
        'validar_entrada': True
    }
```

---

## 🔧 PLANTILLA: SERVICIO DE NEGOCIO

### **📁 Archivo: `app/services/mi_service.py`**
```python
"""
Servicio de negocio para [FUNCIONALIDAD]
"""
from typing import List, Dict, Any, Optional, Tuple
from app.core.logging import get_logger
from app.core.config import Config

class MiService:
    """Servicio para manejar [FUNCIONALIDAD]"""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.logger = get_logger(__name__)
        self.config = Config.MI_MODULO
        
        self.logger.info("MiService inicializado")
        
    def procesar_solicitud(self, parametros: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Procesa una solicitud de negocio
        
        Args:
            parametros: Parámetros de la solicitud
            
        Returns:
            Tupla (éxito, mensaje, datos)
        """
        try:
            self.logger.info(f"Procesando solicitud: {parametros}")
            
            # 🎯 VALIDAR entrada
            if not self._validar_parametros(parametros):
                return False, self.config['messages']['invalid_input'], {}
                
            # 🎯 PROCESAR lógica de negocio
            resultado = self._ejecutar_logica_negocio(parametros)
            
            if resultado:
                self.logger.info("Solicitud procesada exitosamente")
                return True, self.config['messages']['success'], resultado
            else:
                self.logger.warning("No se obtuvieron resultados")
                return False, self.config['messages']['not_found'], {}
                
        except Exception as e:
            self.logger.error(f"Error procesando solicitud: {e}")
            return False, self.config['messages']['error'], {}
            
    def _validar_parametros(self, parametros: Dict[str, Any]) -> bool:
        """Valida los parámetros de entrada"""
        try:
            # 🎯 VALIDACIONES específicas aquí
            required_fields = ['campo_requerido']
            
            for field in required_fields:
                if field not in parametros:
                    self.logger.warning(f"Campo requerido faltante: {field}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando parámetros: {e}")
            return False
            
    def _ejecutar_logica_negocio(self, parametros: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Ejecuta la lógica de negocio principal"""
        try:
            # 🎯 LÓGICA ESPECÍFICA DEL SERVICIO AQUÍ
            
            # Ejemplo de consulta a base de datos
            if self.db_connection:
                cursor = self.db_connection.cursor()
                # Ejecutar consultas aquí
                
            # Procesar datos
            resultado = {
                'procesado': True,
                'timestamp': self._get_timestamp(),
                'datos': parametros
            }
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"Error en lógica de negocio: {e}")
            return None
            
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()
```

---

## 🧪 PLANTILLA: TEST UNITARIO

### **📁 Archivo: `tests/test_mi_interpreter.py`**
```python
"""
Tests para MiInterpreter
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from app.core.ai.interpretation.mi_interpreter import MiInterpreter
from app.core.ai.interpretation.base_interpreter import InterpretationContext

class TestMiInterpreter(unittest.TestCase):
    """Tests para MiInterpreter"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.mock_gemini = Mock()
        self.interpreter = MiInterpreter(self.mock_gemini)
        
    def test_can_handle_valid_keywords(self):
        """Test: Detecta correctamente palabras clave válidas"""
        context = Mock()
        context.user_message = "palabra1 en la consulta"
        
        result = self.interpreter.can_handle(context)
        
        self.assertTrue(result)
        
    def test_can_handle_invalid_keywords(self):
        """Test: Rechaza consultas sin palabras clave"""
        context = Mock()
        context.user_message = "consulta sin palabras relevantes"
        
        result = self.interpreter.can_handle(context)
        
        self.assertFalse(result)
        
    def test_interpret_success(self):
        """Test: Interpretación exitosa"""
        # 🎯 MOCK respuesta de Gemini
        self.mock_gemini.send_prompt_sync.return_value = '''
        {
            "es_valida": true,
            "categoria": "test_categoria",
            "parametros_extraidos": {"param": "valor"},
            "confianza": 0.9
        }
        '''
        
        context = Mock()
        context.user_message = "palabra1 test"
        
        result = self.interpreter.interpret(context)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.action, "accion_test_categoria")
        self.assertEqual(result.confidence, 0.9)
        
    def test_interpret_gemini_error(self):
        """Test: Manejo de error en Gemini"""
        self.mock_gemini.send_prompt_sync.side_effect = Exception("Error de conexión")
        
        context = Mock()
        context.user_message = "palabra1 test"
        
        result = self.interpreter.interpret(context)
        
        self.assertIsNone(result)
        
    @patch('app.core.ai.interpretation.mi_interpreter.get_logger')
    def test_logging_integration(self, mock_get_logger):
        """Test: Integración con sistema de logging"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        interpreter = MiInterpreter(self.mock_gemini)
        
        # Verificar que se llamó al logger
        mock_get_logger.assert_called_once()
        mock_logger.info.assert_called_with("MiInterpreter inicializado correctamente")

if __name__ == '__main__':
    unittest.main()
```

---

## 🎯 PLANTILLA: INTEGRACIÓN CON MASTER INTERPRETER

### **📁 Modificar: `app/core/ai/interpretation/master_interpreter.py`**
```python
# Agregar import
from app.core.ai.interpretation.mi_interpreter import MiInterpreter

class MasterInterpreter:
    def __init__(self, gemini_client):
        # ... código existente ...
        
        # 🆕 AGREGAR nuevo intérprete
        self.mi_interpreter = MiInterpreter(gemini_client)
        
    def interpret(self, context: InterpretationContext, conversation_stack=None) -> Optional[InterpretationResult]:
        # ... código existente de detección de intención ...
        
        # 🆕 AGREGAR nueva condición
        elif intention.intention_type == "mi_intencion":
            self.logger.debug("Dirigiendo a mi intérprete")
            return self.mi_interpreter.interpret(context)
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### **✅ ANTES DE EMPEZAR**
- [ ] Definir configuraciones en `Config.MI_MODULO`
- [ ] Planificar palabras clave y detección
- [ ] Identificar dependencias necesarias
- [ ] Diseñar estructura de respuesta

### **✅ DURANTE DESARROLLO**
- [ ] Copiar plantilla de intérprete
- [ ] Personalizar `can_handle()` y `interpret()`
- [ ] Implementar análisis con Gemini
- [ ] Agregar logging apropiado
- [ ] Crear tests unitarios

### **✅ INTEGRACIÓN**
- [ ] Registrar en MasterInterpreter
- [ ] Agregar detección de intención
- [ ] Probar flujo completo
- [ ] Verificar logging en archivos

**¡Con estas plantillas puedes crear nuevos módulos rápidamente siguiendo todos los estándares!** 🚀
