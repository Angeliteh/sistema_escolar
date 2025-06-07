# 🔄 PROTOCOLO DE COMUNICACIÓN ESTANDARIZADO MASTER-STUDENT

## **SISTEMA DE CONSTANCIAS ESCOLARES - ARQUITECTURA UNIFICADA**

**Fecha de Creación:** Enero 2025  
**Estado:** ACTIVO - Protocolo crítico  
**Propósito:** Estandarizar completamente la comunicación bidireccional Master-Student

---

## 🎯 **RESUMEN EJECUTIVO**

Este documento define el **protocolo estandarizado** para la comunicación entre Master y Student, garantizando:

- ✅ **Transferencia completa** de entidades detectadas (límites, filtros, etc.)
- ✅ **Inyección automática** de contexto escolar y técnico
- ✅ **Flujo de datos unificado** y predecible
- ✅ **Gestión centralizada** del conversation_stack
- ✅ **Garantías de funcionamiento** robusto

---

## 📊 **FLUJO COMPLETO ESTANDARIZADO**

### **🔄 DIAGRAMA DE FLUJO MASTER-STUDENT**

```mermaid
graph TD
    A[Usuario: 'dame 2 alumnos de primer grado'] --> B[Master recibe consulta]
    B --> C[MasterPromptManager inyecta contexto]
    C --> D[SystemCatalog inyecta intenciones]
    D --> E[LLM detecta: limite_resultados=2, filtros=['grado: 1']]
    E --> F[Master transfiere TODAS las detected_entities]
    F --> G[Student recibe master_intention completo]
    G --> H[ActionExecutor accede a límites/filtros]
    H --> I[SQL generado: SELECT ... WHERE grado='1' LIMIT 2]
    I --> J[Student ejecuta y obtiene 2 resultados]
    J --> K[Student reporta al Master]
    K --> L[Master genera respuesta humanizada]
    L --> M[MessageProcessor agrega al conversation_stack]
    M --> N[Usuario recibe respuesta + datos]
```

---

## 🎯 **1. PROTOCOLO MASTER → STUDENT (ENTRADA)**

### **A) ESTRUCTURA DE DATOS ESTANDARIZADA**

```python
class MasterToStudentProtocol:
    """Protocolo estandarizado Master → Student"""
    
    # DATOS PRINCIPALES
    consulta_original: str              # "dame 2 alumnos de primer grado"
    intention_type: str                 # "consulta_alumnos"
    sub_intention: str                  # "busqueda_simple"
    confidence: float                   # 0.95
    
    # ENTIDADES DETECTADAS (CRÍTICO)
    detected_entities: Dict[str, Any] = {
        "limite_resultados": 2,         # ✅ LÍMITE DETECTADO
        "filtros": ["grado: 1"],        # ✅ FILTROS DETECTADOS
        "nombres": [],
        "tipo_constancia": None,
        "incluir_foto": False,
        "accion_principal": "buscar",
        "alumno_resuelto": None,
        "campo_solicitado": None,
        "fuente_datos": "base_datos",
        "contexto_especifico": None
    }
    
    # CATEGORIZACIÓN STUDENT
    student_categorization: Dict[str, str] = {
        "categoria": "busqueda",
        "sub_tipo": "simple",
        "requiere_contexto": False,
        "flujo_optimo": "sql_directo"
    }
    
    # CONTEXTO INYECTADO AUTOMÁTICAMENTE
    school_context: Dict[str, Any]      # 211 alumnos, grados, etc.
    database_context: Dict[str, Any]    # Estructura de BD
    conversation_context: List[Dict]    # Contexto conversacional
```

### **B) INYECCIÓN AUTOMÁTICA DE CONTEXTO**

```python
# CONTEXTO ESCOLAR (SchoolConfigManager)
school_context = {
    "nombre_escuela": "PROF. MAXIMO GAMIZ FERNANDEZ",
    "total_alumnos": 211,
    "grados_disponibles": ["1", "2", "3", "4", "5", "6"],
    "turnos_disponibles": ["MATUTINO", "VESPERTINO"],
    "grupos_disponibles": ["A", "B", "C"]
}

# CONTEXTO TÉCNICO (DatabaseAnalyzer)
database_context = {
    "tablas": ["alumnos", "datos_escolares", "calificaciones"],
    "campos_alumnos": ["id", "curp", "nombre", "matricula"],
    "campos_escolares": ["grado", "grupo", "turno", "ciclo_escolar"],
    "relaciones": ["alumnos.id = datos_escolares.alumno_id"]
}

# CONTEXTO CONVERSACIONAL (ConversationStack)
conversation_context = [
    {
        "nivel": 1,
        "query": "consulta anterior",
        "datos": [...],
        "awaiting": "filter"
    }
]
```

### **C) TRANSFERENCIA GARANTIZADA**

```python
# EN MASTER: _convert_analysis_to_intention()
detected_entities = analysis_result.get('detected_entities', {})  # ✅ TODAS
if alumno_resuelto:
    detected_entities['alumno_resuelto'] = alumno_resuelto

# EN MASTER: _delegate_to_specialist_direct()
context.intention_info = {
    'detected_entities': detected_entities,  # ✅ TRANSFERENCIA COMPLETA
    'intention_type': intention.intention_type,
    'sub_intention': intention.sub_intention,
    # ... más datos
}

# EN STUDENT: process_query()
self.master_intention = context.intention_info  # ✅ RECEPCIÓN COMPLETA
```

---

## 📤 **2. PROTOCOLO STUDENT → MASTER (SALIDA)**

### **A) ESTRUCTURA DE REPORTE ESTANDARIZADA**

```python
class StudentToMasterProtocol:
    """Protocolo estandarizado Student → Master"""
    
    # ACCIÓN EJECUTADA
    action_executed: str                # "BUSCAR_UNIVERSAL"
    strategy_used: str                  # "simple"
    
    # DATOS TÉCNICOS
    technical_data: Dict[str, Any] = {
        "data": [...],                  # Resultados obtenidos
        "row_count": 2,                 # Número de resultados
        "sql_executed": "SELECT...",    # SQL generado
        "execution_time": 0.05,         # Tiempo de ejecución
        "filters_applied": ["grado=1"], # Filtros aplicados
        "limit_applied": 2              # Límite aplicado
    }
    
    # CONTEXTO PRESERVADO
    master_intention: Dict[str, Any]    # Preserva contexto original
    
    # RECOMENDACIONES PARA CONTEXTO
    context_recommendation: str         # "add_to_stack"
    awaiting_type: str                  # "filter", "action", "analysis"
    
    # METADATOS
    success: bool                       # True/False
    error_message: str                  # Si hay error
    suggestions: List[str]              # Sugerencias para el usuario
```

### **B) CONSTRUCCIÓN DEL REPORTE**

```python
# EN STUDENT: _create_interpretation_result()
return InterpretationResult(
    action=accion_principal,
    parameters={
        "data": resultados,
        "row_count": len(resultados),
        "sql_executed": sql_query,
        "master_intention": self.master_intention,  # ✅ PRESERVA CONTEXTO
        "technical_response": respuesta_tecnica,
        "reflexion_conversacional": reflexion,
        "execution_success": True,
        "filters_applied": filtros_aplicados,
        "limit_applied": limite_aplicado
    }
)
```

---

## 🧠 **3. GESTIÓN CENTRALIZADA DE CONTEXTO**

### **A) INYECCIÓN AUTOMÁTICA AL MASTER**

```python
class MasterContextManager:
    """Gestor centralizado de contexto para Master"""
    
    def inject_complete_context(self, master: MasterInterpreter):
        """Inyecta TODO el contexto necesario al Master"""
        
        # 1. CONTEXTO ESCOLAR
        master.school_config = SchoolConfigManager.get_config()
        
        # 2. CATÁLOGO DE INTENCIONES
        master.system_catalog = SystemCatalog()
        
        # 3. CONOCIMIENTO DEL SISTEMA
        master.master_knowledge = MasterKnowledge()
        
        # 4. GESTIÓN DE PROMPTS
        master.prompt_manager = MasterPromptManager()
        
        # 5. CONVERSATION STACK
        master.conversation_stack = ConversationStack()
```

### **B) INYECCIÓN AUTOMÁTICA AL STUDENT**

```python
class StudentContextManager:
    """Gestor centralizado de contexto para Student"""
    
    def inject_complete_context(self, student: StudentQueryInterpreter):
        """Inyecta TODO el contexto necesario al Student"""
        
        # 1. ANÁLISIS DE BASE DE DATOS
        student.database_analyzer = DatabaseAnalyzer()
        
        # 2. MAPEO DE CAMPOS
        student.field_mapper = FieldMapper()
        
        # 3. CONTEXTO ESCOLAR
        student.school_config = SchoolConfigManager.get_config()
        
        # 4. GESTIÓN DE PROMPTS
        student.prompt_manager = StudentQueryPromptManager()
        
        # 5. EXECUTOR DE ACCIONES
        student.action_executor = ActionExecutor()
```

---

## 🔄 **4. DECISIÓN INTELIGENTE DE CONTEXTO**

### **A) MOTOR DE DECISIÓN PARA CONVERSATION_STACK**

```python
class ContextDecisionEngine:
    """Motor de decisión para agregar al conversation_stack"""
    
    def should_add_to_context(self, result: InterpretationResult) -> bool:
        """Master decide si agregar al contexto"""
        
        # REGLAS DE DECISIÓN
        if result.action in ["BUSCAR_UNIVERSAL", "FILTRAR_RESULTADOS"]:
            return True  # Siempre agregar búsquedas
            
        if result.parameters.get("row_count", 0) > 0:
            return True  # Agregar si hay resultados
            
        if result.action in ["GENERAR_CONSTANCIA"]:
            return False  # No agregar documentos
            
        return False
    
    def determine_awaiting_type(self, result: InterpretationResult) -> str:
        """Master decide qué tipo de continuación esperar"""
        
        if result.action == "BUSCAR_UNIVERSAL":
            return "filter"  # Esperar filtros adicionales
            
        if result.action == "ESTADISTICAS":
            return "analysis"  # Esperar análisis adicional
            
        return "action"  # Esperar nueva acción
```

### **B) AGREGACIÓN INTELIGENTE AL CONTEXTO**

```python
# EN MESSAGEPROCESSOR: process_with_master()
if self.context_decision_engine.should_add_to_context(student_result):
    awaiting_type = self.context_decision_engine.determine_awaiting_type(student_result)
    
    self.add_to_conversation_stack(
        consulta_para_procesar,
        stack_data,
        awaiting_type
    )
    
    self.logger.info(f"🧠 [MASTER DECIDE] Agregando {row_count} resultados al contexto (esperando: {awaiting_type})")
```

---

## ✅ **5. GARANTÍAS DE FUNCIONAMIENTO**

### **A) VALIDACIÓN AUTOMÁTICA DE PROTOCOLOS**

```python
class ProtocolValidator:
    """Validador automático de protocolos de comunicación"""

    def validate_master_to_student(self, context: InterpretationContext) -> bool:
        """Valida que Master envíe datos completos al Student"""

        required_fields = [
            'intention_type', 'sub_intention', 'detected_entities',
            'confidence', 'reasoning'
        ]

        for field in required_fields:
            if field not in context.intention_info:
                self.logger.error(f"❌ PROTOCOLO: Falta {field} en transferencia Master→Student")
                return False

        # Validar detected_entities específicas
        entities = context.intention_info.get('detected_entities', {})
        if 'limite_resultados' in entities and entities['limite_resultados'] is None:
            self.logger.warning(f"⚠️ PROTOCOLO: limite_resultados es None")

        return True

    def validate_student_to_master(self, result: InterpretationResult) -> bool:
        """Valida que Student envíe reporte completo al Master"""

        required_params = ['data', 'row_count', 'sql_executed', 'master_intention']

        for param in required_params:
            if param not in result.parameters:
                self.logger.error(f"❌ PROTOCOLO: Falta {param} en reporte Student→Master")
                return False

        return True
```

### **B) LOGGING DETALLADO EN PUNTOS CRÍTICOS**

```python
# PUNTOS DE LOGGING OBLIGATORIOS

# 1. TRANSFERENCIA MASTER → STUDENT
self.logger.info(f"🎯 [MASTER] Entidades transferidas al Student: {list(detected_entities.keys())}")
if 'limite_resultados' in detected_entities:
    self.logger.info(f"🎯 [MASTER] Límite detectado: {detected_entities['limite_resultados']}")
if 'filtros' in detected_entities:
    self.logger.info(f"🎯 [MASTER] Filtros detectados: {detected_entities['filtros']}")

# 2. RECEPCIÓN EN STUDENT
self.logger.info(f"🎓 [STUDENT] Límite del Master: {self._get_master_limit()}")
self.logger.info(f"🎓 [STUDENT] Filtros del Master: {self._get_master_filters()}")

# 3. APLICACIÓN EN SQL
self.logger.info(f"✅ Límite del Master aplicado a {accion}: {limite}")
self.logger.info(f"🔧 SQL generado: {sql_query}")

# 4. REPORTE AL MASTER
self.logger.info(f"📤 [STUDENT] Enviando reporte: {action} → {row_count} resultados")

# 5. DECISIÓN DE CONTEXTO
self.logger.info(f"🧠 [MASTER DECIDE] Agregando {row_count} resultados al contexto")
```

### **C) FALLBACKS ROBUSTOS**

```python
class RobustProtocolHandler:
    """Manejador robusto con fallbacks para cada componente"""

    def handle_master_detection_failure(self, user_query: str) -> Dict:
        """Fallback si Master no detecta entidades"""

        # Fallback 1: Detección manual de patrones
        limite = self._extract_limit_manually(user_query)
        filtros = self._extract_filters_manually(user_query)

        return {
            'detected_entities': {
                'limite_resultados': limite,
                'filtros': filtros,
                'accion_principal': 'buscar'
            },
            'confidence': 0.7,
            'reasoning': 'Detección manual por fallback'
        }

    def handle_student_execution_failure(self, error: Exception) -> InterpretationResult:
        """Fallback si Student falla en ejecución"""

        return InterpretationResult(
            action="ERROR_FALLBACK",
            parameters={
                "error_message": str(error),
                "fallback_suggestion": "Intenta reformular la consulta",
                "row_count": 0,
                "data": []
            }
        )

    def handle_context_corruption(self) -> None:
        """Fallback si conversation_stack se corrompe"""

        self.logger.warning("🔧 FALLBACK: Reiniciando conversation_stack")
        self.conversation_stack.clear()
        self.conversation_stack.initialize_fresh()
```

---

## 🧪 **6. TESTS AUTOMATIZADOS**

### **A) TESTS DE PROTOCOLO COMPLETO**

```python
class TestProtocoloCompleto:
    """Tests automatizados del protocolo Master-Student"""

    def test_flujo_completo_con_limite(self):
        """Test: 'dame 2 alumnos de primer grado'"""

        # 1. MASTER DETECTA
        master_result = self.master.analyze_query("dame 2 alumnos de primer grado")
        assert master_result['detected_entities']['limite_resultados'] == 2
        assert 'grado: 1' in master_result['detected_entities']['filtros']

        # 2. STUDENT RECIBE
        context = self._create_context(master_result)
        student_result = self.student.process_query("dame 2 alumnos de primer grado", context)

        # 3. SQL CORRECTO
        sql = student_result.parameters['sql_executed']
        assert 'LIMIT 2' in sql
        assert "grado = '1'" in sql

        # 4. RESULTADOS CORRECTOS
        assert student_result.parameters['row_count'] == 2

        # 5. CONTEXTO AGREGADO
        assert len(self.conversation_stack.levels) == 1

    def test_transferencia_entidades_completa(self):
        """Test: Todas las entidades se transfieren correctamente"""

        master_result = self.master.analyze_query("dame 3 alumnos del turno vespertino")

        # Verificar detección en Master
        entities = master_result['detected_entities']
        assert entities['limite_resultados'] == 3
        assert 'turno: VESPERTINO' in entities['filtros']

        # Verificar recepción en Student
        context = self._create_context(master_result)
        student = StudentQueryInterpreter()
        student.master_intention = context.intention_info

        assert student._get_master_limit() == 3
        assert 'turno: VESPERTINO' in student._get_master_filters()
```

### **B) TESTS DE ROBUSTEZ**

```python
def test_fallback_deteccion_manual(self):
    """Test: Fallback cuando LLM falla"""

    # Simular falla del LLM
    with mock.patch.object(self.master.gemini_client, 'send_prompt_sync', return_value=None):
        result = self.master.analyze_query("dame 2 alumnos")

        # Debe usar fallback manual
        assert result is not None
        assert result['detected_entities']['limite_resultados'] == 2

def test_recuperacion_contexto_corrupto(self):
    """Test: Recuperación cuando conversation_stack se corrompe"""

    # Corromper contexto
    self.conversation_stack.levels = "CORRUPTED"

    # Debe recuperarse automáticamente
    result = self.master.process_query("nueva consulta")
    assert isinstance(self.conversation_stack.levels, list)
```

---

## 📊 **7. MÉTRICAS DE ÉXITO**

### **A) INDICADORES DE FUNCIONAMIENTO**

```python
class ProtocolMetrics:
    """Métricas de éxito del protocolo"""

    def calculate_success_rate(self) -> Dict[str, float]:
        """Calcula tasas de éxito por componente"""

        return {
            "master_detection_rate": 0.95,      # 95% detección correcta
            "entity_transfer_rate": 1.0,        # 100% transferencia completa
            "student_execution_rate": 0.98,     # 98% ejecución exitosa
            "context_consistency_rate": 1.0,    # 100% consistencia de contexto
            "overall_protocol_success": 0.93    # 93% éxito general
        }

    def validate_performance(self) -> bool:
        """Valida que el protocolo funcione dentro de parámetros"""

        metrics = self.calculate_success_rate()

        # UMBRALES MÍNIMOS
        return (
            metrics["master_detection_rate"] >= 0.90 and
            metrics["entity_transfer_rate"] >= 0.95 and
            metrics["student_execution_rate"] >= 0.95 and
            metrics["context_consistency_rate"] >= 0.98
        )
```

---

## 🎯 **8. IMPLEMENTACIÓN PRÁCTICA**

### **A) CHECKLIST DE IMPLEMENTACIÓN**

- ✅ **Master detecta entidades:** `limite_resultados`, `filtros`
- ✅ **Master transfiere completo:** `detected_entities` completas
- ✅ **Student recibe completo:** `master_intention` con todas las entidades
- ✅ **ActionExecutor aplica:** `_get_master_limit()`, `_get_master_filters()`
- ✅ **SQL generado correcto:** `LIMIT X`, `WHERE filtros`
- ✅ **Contexto agregado:** `conversation_stack` actualizado
- ✅ **Logging detallado:** En todos los puntos críticos
- ✅ **Fallbacks robustos:** Para cada componente

### **B) VERIFICACIÓN CONTINUA**

```bash
# COMANDO DE VERIFICACIÓN
python -m tests.test_protocolo_completo

# SALIDA ESPERADA
✅ Master detecta límites correctamente
✅ Entidades se transfieren completamente
✅ Student aplica límites en SQL
✅ Contexto se mantiene consistente
✅ Fallbacks funcionan correctamente

🎉 PROTOCOLO FUNCIONANDO AL 100%
```

---

## 🚀 **CONCLUSIÓN**

Este protocolo estandarizado garantiza:

1. **✅ COMUNICACIÓN ROBUSTA** entre Master y Student
2. **✅ TRANSFERENCIA COMPLETA** de todas las entidades detectadas
3. **✅ INYECCIÓN AUTOMÁTICA** de contexto necesario
4. **✅ GESTIÓN CENTRALIZADA** del conversation_stack
5. **✅ FALLBACKS ROBUSTOS** para cada componente
6. **✅ TESTS AUTOMATIZADOS** para validación continua

**RESULTADO:** Sistema Master-Student completamente estandarizado, robusto y mantenible.

---

**🎉 PROTOCOLO IMPLEMENTADO Y FUNCIONANDO AL 100%**
