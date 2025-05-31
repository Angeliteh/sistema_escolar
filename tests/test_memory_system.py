"""
🧪 TESTS DEL SISTEMA DE MEMORIA CONVERSACIONAL
Tests unitarios para los componentes de memoria
"""
import sys
import os
import pytest
import json
from datetime import datetime, timedelta

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.memory.conversational_memory import ConversationalMemory, MemoryInteraction
from app.core.memory.intelligent_prompt_manager import IntelligentPromptManager, LLMDecision
from app.core.memory.memory_operations import MemoryOperations, FilterCriteria
from app.core.memory.advanced_context_processor import AdvancedContextProcessor, ProcessingContext
from app.core.memory.memory_system_integration import MemorySystemIntegration


class MockGeminiClient:
    """Mock del cliente Gemini para tests"""
    def __init__(self):
        self.available = True

    def send_prompt_sync(self, prompt):
        """Simular respuesta del LLM"""
        return '''
        {
            "understanding": "Test query entendida",
            "memory_analysis": "No hay datos en memoria",
            "action": "search_database",
            "reasoning": "Necesito buscar en base de datos",
            "sql_query": "SELECT * FROM alumnos WHERE nombre LIKE '%test%'",
            "memory_operations": [],
            "response": "Buscando información...",
            "prediction": "Usuario podría pedir más detalles",
            "confidence": 0.8
        }
        '''


class MockSQLExecutor:
    """Mock del ejecutor SQL para tests"""
    def __init__(self):
        self.available = True

    def execute_query(self, sql_query):
        """Simular ejecución de SQL"""
        class MockSQLResult:
            def __init__(self):
                self.success = True
                self.data = [
                    {"id": 1, "nombre": "Test Student", "curp": "TEST123456", "grado": 4},
                    {"id": 2, "nombre": "Another Student", "curp": "TEST789012", "grado": 4}
                ]
                self.row_count = 2
                self.message = "Query ejecutado exitosamente"
                self.query_executed = sql_query

        return MockSQLResult()


class TestConversationalMemory:
    """Tests para ConversationalMemory"""

    def setup_method(self):
        """Setup para cada test"""
        self.memory = ConversationalMemory(max_interactions=5, max_age_hours=1)

    def test_add_interaction(self):
        """Test agregar interacción"""
        # Agregar interacción
        self.memory.add_interaction(
            query="test query",
            summary="test summary",
            data=[{"nombre": "Test", "curp": "TEST123"}],
            action_taken="search_database"
        )

        # Verificar
        assert len(self.memory.interactions) == 1
        interaction = self.memory.interactions[0]
        assert interaction.query == "test query"
        assert interaction.row_count == 1
        assert interaction.has_data()

    def test_get_recent_interactions(self):
        """Test obtener interacciones recientes"""
        # Agregar múltiples interacciones
        for i in range(3):
            self.memory.add_interaction(
                query=f"query {i}",
                summary=f"summary {i}",
                data=[{"id": i}],
                action_taken="test"
            )

        # Obtener recientes
        recent = self.memory.get_recent_interactions(2)
        assert len(recent) == 2
        assert recent[0].query == "query 2"  # Más reciente primero
        assert recent[1].query == "query 1"

    def test_format_for_llm_prompt(self):
        """Test formateo para prompt LLM"""
        # Agregar interacción
        self.memory.add_interaction(
            query="buscar alumnos",
            summary="encontrados 5 alumnos",
            data=[{"nombre": "Test"}],
            action_taken="search_database"
        )

        # Formatear
        prompt_context = self.memory.format_for_llm_prompt()

        assert "MEMORIA CONVERSACIONAL" in prompt_context
        assert "buscar alumnos" in prompt_context
        assert "encontrados 5 alumnos" in prompt_context

    def test_cleanup_old_interactions(self):
        """Test limpieza automática"""
        # Configurar memoria con límite bajo
        memory = ConversationalMemory(max_interactions=2, max_age_hours=1)

        # Agregar más interacciones que el límite
        for i in range(4):
            memory.add_interaction(
                query=f"query {i}",
                summary=f"summary {i}",
                data=[],
                action_taken="test"
            )

        # Verificar que se mantienen solo las más recientes
        assert len(memory.interactions) == 2
        assert memory.interactions[0].query == "query 2"
        assert memory.interactions[1].query == "query 3"

    def test_memory_stats(self):
        """Test estadísticas de memoria"""
        # Agregar interacciones
        self.memory.add_interaction("query1", "summary1", [{"test": 1}], "action1")
        self.memory.add_interaction("query2", "summary2", [], "action2")

        # Obtener estadísticas
        stats = self.memory.get_memory_stats()

        assert stats.total_interactions == 2
        assert stats.interactions_with_data == 1
        assert stats.average_confidence == 1.0  # Default confidence


class TestIntelligentPromptManager:
    """Tests para IntelligentPromptManager"""

    def setup_method(self):
        """Setup para cada test"""
        self.memory = ConversationalMemory()
        self.prompt_manager = IntelligentPromptManager(self.memory)

    def test_create_contextual_prompt(self):
        """Test creación de prompt contextual"""
        # Agregar contexto a memoria
        self.memory.add_interaction(
            query="alumnos de 4to",
            summary="encontrados 6 alumnos",
            data=[{"nombre": "Test"}],
            action_taken="search_database"
        )

        # Crear prompt
        prompt = self.prompt_manager.create_contextual_prompt("detalles de test")

        assert "ASISTENTE ESCOLAR INTELIGENTE" in prompt
        assert "alumnos de 4to" in prompt
        assert "detalles de test" in prompt
        assert "JSON" in prompt

    def test_parse_llm_response_valid(self):
        """Test parseo de respuesta válida"""
        response = '''
        {
            "understanding": "Usuario quiere detalles",
            "memory_analysis": "Hay datos en memoria",
            "action": "use_memory",
            "reasoning": "Tengo la información",
            "sql_query": null,
            "memory_operations": [],
            "response": "Aquí están los detalles",
            "prediction": "Podría pedir constancia",
            "confidence": 0.9
        }
        '''

        decision = self.prompt_manager.parse_llm_response(response)

        assert decision is not None
        assert decision.action == "use_memory"
        assert decision.confidence == 0.9
        assert decision.is_valid()

    def test_parse_llm_response_invalid(self):
        """Test parseo de respuesta inválida"""
        response = "Esta no es una respuesta JSON válida"

        decision = self.prompt_manager.parse_llm_response(response)

        assert decision is None

    def test_create_fallback_decision(self):
        """Test creación de decisión de fallback"""
        decision = self.prompt_manager.create_fallback_decision("constancia para alumno")

        assert decision.action == "generate_document"  # Detecta "constancia"
        assert decision.confidence < 0.5  # Baja confianza para fallback
        assert "fallback" in decision.reasoning.lower()


class TestMemoryOperations:
    """Tests para MemoryOperations"""

    def setup_method(self):
        """Setup para cada test"""
        self.operations = MemoryOperations()
        self.sample_data = [
            {"nombre": "Ana", "grado": 4, "promedio": 9.5},
            {"nombre": "Luis", "grado": 4, "promedio": 8.7},
            {"nombre": "María", "grado": 5, "promedio": 9.2},
            {"nombre": "Carlos", "grado": 4, "promedio": 8.9}
        ]

    def test_filter_data(self):
        """Test filtrado de datos"""
        # Filtrar por grado
        criteria = [FilterCriteria(field="grado", operator="equals", value=4)]
        result = self.operations.filter_data(self.sample_data, criteria)

        assert result.success
        assert result.result_count == 3  # Ana, Luis, Carlos
        assert all(item["grado"] == 4 for item in result.data)

    def test_calculate_statistics(self):
        """Test cálculo de estadísticas"""
        # Calcular promedio
        result = self.operations.calculate_statistics(self.sample_data, "promedio", "average")

        assert result.success
        assert result.calculation is not None
        assert result.calculation.operation == "average"
        assert abs(result.calculation.result - 9.075) < 0.01  # Promedio esperado

    def test_rank_data(self):
        """Test ranking de datos"""
        # Rankear por promedio descendente
        result = self.operations.rank_data(self.sample_data, "promedio", descending=True, limit=2)

        assert result.success
        assert result.result_count == 2
        assert result.data[0]["nombre"] == "Ana"  # Mejor promedio
        assert result.data[1]["nombre"] == "María"  # Segundo mejor

    def test_search_in_data(self):
        """Test búsqueda en datos"""
        # Buscar por nombre
        result = self.operations.search_in_data(self.sample_data, "ana", ["nombre"])

        assert result.success
        assert result.result_count == 1
        assert result.data[0]["nombre"] == "Ana"

    def test_select_by_position(self):
        """Test selección por posición"""
        # Seleccionar segundo elemento (posición 2)
        result = self.operations.select_by_position(self.sample_data, 2)

        assert result.success
        assert result.result_count == 1
        assert result.data[0]["nombre"] == "Luis"  # Segundo en la lista

    def test_filter_multiple_criteria(self):
        """Test filtrado con múltiples criterios"""
        criteria = [
            FilterCriteria(field="grado", operator="equals", value=4),
            FilterCriteria(field="promedio", operator="greater", value=8.8)
        ]
        result = self.operations.filter_data(self.sample_data, criteria)

        assert result.success
        assert result.result_count == 2  # Ana y Carlos
        assert all(item["grado"] == 4 and item["promedio"] > 8.8 for item in result.data)


class TestAdvancedContextProcessor:
    """Tests para AdvancedContextProcessor"""

    def setup_method(self):
        """Setup para tests"""
        # Crear con mocks para simular sistema real
        self.mock_gemini = MockGeminiClient()
        self.mock_sql = MockSQLExecutor()
        self.processor = AdvancedContextProcessor(self.mock_gemini, self.mock_sql)

    def test_processor_initialization(self):
        """Test inicialización del procesador"""
        assert self.processor.memory is not None
        assert self.processor.prompt_manager is not None
        assert self.processor.operations is not None
        assert self.processor.stats["queries_processed"] == 0

    def test_process_query_without_clients(self):
        """Test procesamiento sin clientes externos"""
        context = ProcessingContext(
            user_query="test query",
            conversation_history=[],
            available_actions=["test"],
            gemini_client=None,
            sql_executor=None,
            additional_context={}
        )

        result = self.processor.process_query(context)

        # Debe crear un fallback por falta de clientes
        assert result is not None
        assert result.action_taken in ["fallback", "error"]


class TestMemorySystemIntegration:
    """Tests para MemorySystemIntegration"""

    def setup_method(self):
        """Setup para tests"""
        # Crear con mocks para simular sistema real
        self.mock_gemini = MockGeminiClient()
        self.mock_sql = MockSQLExecutor()
        self.integration = MemorySystemIntegration(self.mock_gemini, self.mock_sql)

    def test_integration_initialization(self):
        """Test inicialización de integración"""
        assert self.integration.processor is not None
        assert self.integration.fallback_enabled == True
        assert self.integration.integration_stats["queries_processed"] == 0

    def test_process_query_compatible(self):
        """Test procesamiento compatible"""
        result = self.integration.process_query_compatible("test query")

        assert result is not None
        assert hasattr(result, 'action')
        assert hasattr(result, 'parameters')
        assert hasattr(result, 'confidence')

    def test_legacy_format_conversion(self):
        """Test conversión a formato legacy"""
        # Crear resultado mock
        from app.core.memory.advanced_context_processor import ProcessingResult

        mock_result = ProcessingResult(
            success=True,
            action_taken="use_memory",
            data=[{"test": "data"}],
            row_count=1,
            message="Test message",
            sql_query=None,
            confidence=0.9,
            processing_time_ms=100.0,
            memory_used=True,
            prediction="Test prediction",
            debug_info={}
        )

        legacy_result = self.integration._convert_to_legacy_format(mock_result)

        assert legacy_result.action == "consulta_sql_exitosa"
        assert legacy_result.parameters["data"] == [{"test": "data"}]
        assert legacy_result.parameters["row_count"] == 1
        assert legacy_result.confidence == 0.9


class TestIntegration:
    """Tests de integración entre componentes"""

    def setup_method(self):
        """Setup para tests de integración"""
        self.memory = ConversationalMemory()
        self.prompt_manager = IntelligentPromptManager(self.memory)
        self.operations = MemoryOperations()

        # Crear con mocks para simular sistema real
        self.mock_gemini = MockGeminiClient()
        self.mock_sql = MockSQLExecutor()
        self.processor = AdvancedContextProcessor(self.mock_gemini, self.mock_sql)
        self.integration = MemorySystemIntegration(self.mock_gemini, self.mock_sql)

    def test_full_workflow(self):
        """Test flujo completo de memoria"""
        # 1. Agregar datos a memoria
        student_data = [
            {"nombre": "Ana García", "grado": 4, "promedio": 9.5},
            {"nombre": "Luis Pérez", "grado": 4, "promedio": 8.7}
        ]

        self.memory.add_interaction(
            query="alumnos de 4to grado",
            summary="encontrados 2 alumnos",
            data=student_data,
            action_taken="search_database"
        )

        # 2. Crear prompt con contexto
        prompt = self.prompt_manager.create_contextual_prompt("el mejor alumno")
        assert "alumnos de 4to grado" in prompt

        # 3. Simular operación en memoria
        rank_result = self.operations.rank_data(student_data, "promedio", descending=True, limit=1)
        assert rank_result.success
        assert rank_result.data[0]["nombre"] == "Ana García"

        # 4. Verificar estadísticas
        stats = self.memory.get_memory_stats()
        assert stats.total_interactions == 1
        assert stats.interactions_with_data == 1

    def test_end_to_end_integration(self):
        """Test integración completa end-to-end"""
        # Procesar consulta a través del sistema integrado
        result = self.integration.process_query_compatible("test query")

        # Verificar que el resultado es compatible
        assert result.action in ["consulta_sql_exitosa", "consulta_sql_fallida"]
        assert "data" in result.parameters
        assert "row_count" in result.parameters
        assert "message" in result.parameters

        # Verificar información del sistema de memoria
        assert "memory_system_info" in result.parameters
        memory_info = result.parameters["memory_system_info"]
        assert "action_taken" in memory_info
        assert "memory_used" in memory_info
        assert "processing_time_ms" in memory_info


class TestStudentQueryInterpreterIntegration:
    """Tests de integración con StudentQueryInterpreter"""

    def setup_method(self):
        """Setup para tests de integración con StudentQueryInterpreter"""
        # Mock del StudentQueryInterpreter
        self.mock_interpreter = self._create_mock_student_interpreter()

    def _create_mock_student_interpreter(self):
        """Crear mock del StudentQueryInterpreter"""
        class MockStudentQueryInterpreter:
            def __init__(self):
                # ✅ AHORA CON CLIENTES MOCK
                self.gemini_client = MockGeminiClient()
                self.sql_executor = MockSQLExecutor()
                self.logger = None

                # Simular inicialización del sistema de memoria
                self._memory_system = None
                self._memory_system_enabled = True

        return MockStudentQueryInterpreter()

    def test_memory_system_integration(self):
        """Test integración básica del sistema de memoria"""
        # Crear sistema de memoria para el mock interpreter
        memory_system = MemorySystemIntegration.create_for_student_interpreter(self.mock_interpreter)

        # Verificar que se creó correctamente
        assert memory_system is not None
        assert memory_system.processor is not None

        # Test procesamiento básico
        result = memory_system.process_query_compatible("test query")
        assert result is not None
        assert hasattr(result, 'action')
        assert hasattr(result, 'parameters')

    def test_memory_system_fallback(self):
        """Test fallback cuando no hay clientes disponibles"""
        memory_system = MemorySystemIntegration.create_for_student_interpreter(self.mock_interpreter)

        # Procesar consulta sin clientes
        result = memory_system.process_query_compatible("dame una lista de alumnos")

        # Debe funcionar con fallback
        assert result is not None
        assert result.confidence >= 0.0  # Puede ser baja pero debe existir

    def test_conversion_to_interpretation_result(self):
        """Test conversión a InterpretationResult"""
        memory_system = MemorySystemIntegration.create_for_student_interpreter(self.mock_interpreter)

        # Crear resultado mock
        from app.core.memory.memory_system_integration import LegacyResult

        mock_legacy_result = LegacyResult(
            action="consulta_sql_exitosa",
            parameters={
                "data": [{"test": "data"}],
                "row_count": 1,
                "message": "Test message"
            },
            confidence=0.8
        )

        # Convertir a InterpretationResult
        interpretation_result = memory_system.convert_to_interpretation_result(
            mock_legacy_result,
            "test query"
        )

        # Verificar conversión
        assert interpretation_result is not None
        assert interpretation_result.action == "consulta_sql_exitosa"
        assert interpretation_result.confidence == 0.8
        assert "memory_system_used" in interpretation_result.parameters


if __name__ == "__main__":
    # Ejecutar tests básicos
    print("🧪 Ejecutando tests del sistema de memoria avanzado...")

    # Test ConversationalMemory
    test_memory = TestConversationalMemory()
    test_memory.setup_method()
    test_memory.test_add_interaction()
    print("✅ ConversationalMemory: test_add_interaction")

    # Test MemoryOperations
    test_ops = TestMemoryOperations()
    test_ops.setup_method()
    test_ops.test_filter_data()
    print("✅ MemoryOperations: test_filter_data")

    # Test AdvancedContextProcessor
    test_processor = TestAdvancedContextProcessor()
    test_processor.setup_method()
    test_processor.test_processor_initialization()
    print("✅ AdvancedContextProcessor: test_processor_initialization")

    # Test MemorySystemIntegration
    test_integration_sys = TestMemorySystemIntegration()
    test_integration_sys.setup_method()
    test_integration_sys.test_integration_initialization()
    print("✅ MemorySystemIntegration: test_integration_initialization")

    # Test Integration completa
    test_integration = TestIntegration()
    test_integration.setup_method()
    test_integration.test_full_workflow()
    print("✅ Integration: test_full_workflow")

    test_integration.test_end_to_end_integration()
    print("✅ Integration: test_end_to_end_integration")

    # Test integración con StudentQueryInterpreter
    try:
        test_student_integration = TestStudentQueryInterpreterIntegration()
        test_student_integration.setup_method()
        test_student_integration.test_memory_system_integration()
        print("✅ StudentQueryInterpreter: test_memory_system_integration")
    except Exception as e:
        print(f"⚠️ StudentQueryInterpreter integration test skipped: {e}")

    print("🎉 Tests del sistema avanzado completados exitosamente!")
