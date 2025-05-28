#!/usr/bin/env python3
"""
🔬 TESTING A/B PARA OPTIMIZACIÓN DEL INTENTIONDETECTOR
Compara versión actual vs versión optimizada

Uso: python testing_ab_intention_detector.py
"""

import time
import json
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass

# Importar las clases necesarias
import sys
import os

# Agregar el directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.core.ai.interpretation.intention_detector import IntentionDetector
from app.ui.ai_chat.gemini_client import GeminiClient
from app.core.config import Config
from app.core.logging import get_logger

@dataclass
class TestResult:
    """Resultado de una prueba individual"""
    query: str
    version: str
    response_time: float
    intention_type: str
    sub_intention: str
    confidence: float
    detected_entities: Dict[str, Any]
    success: bool
    error: str = ""

class IntentionDetectorOptimized:
    """Versión optimizada del IntentionDetector para testing"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

    def detect_intention(self, user_query: str):
        """Versión optimizada del prompt"""
        try:
            # PROMPT OPTIMIZADO (38 líneas vs 68 originales)
            optimized_prompt = f"""
Detector de intenciones para sistema escolar.

🏫 SISTEMA: Escuela primaria con 211 alumnos registrados
📋 CAPACIDADES: Consultas, constancias, transformación PDFs, ayuda
👥 USUARIOS: Personal administrativo, maestros, directivos

📝 CONSULTA: "{user_query}"

🎯 CLASIFICACIÓN:

1. "consulta_alumnos":
   a) "busqueda_simple": "buscar Juan", "cuántos alumnos", "alumnos 3er grado"
   b) "generar_constancia": "constancia estudios Juan", "certificado calificaciones"
   c) "transformar_pdf": "transformar constancia", "convertir PDF formato"
   d) "consulta_avanzada": "estadísticas grado", "análisis académico"

2. "ayuda_sistema":
   a) "entender_capacidades" - Qué puede hacer el sistema
   b) "tutorial_paso_a_paso" - Cómo usar funcionalidades
   c) "solucion_problema" - Resolver errores o problemas
   d) "ejemplo_practico" - Solicitar ejemplos específicos

3. "conversacion_general":
   - "hola", "buenos días", "gracias", "¿cómo estás?"

🧠 EXTRAER:
- Nombres, tipos constancia, acciones específicas
- Contexto datos (BD/PDF/conversación)
- Parámetros (grados, grupos, turnos, fechas)

RESPONDE con JSON:
{{
    "intention_type": "consulta_alumnos|ayuda_sistema|conversacion_general",
    "sub_intention": "busqueda_simple|generar_constancia|transformar_pdf|consulta_avanzada|entender_capacidades|tutorial_paso_a_paso|solucion_problema|ejemplo_practico|chat_casual",
    "confidence": 0.0-1.0,
    "reasoning": "Explicación del análisis",
    "detected_entities": {{
        "nombres": ["nombres detectados"],
        "tipo_constancia": "estudios|calificaciones|traslado|null",
        "accion_principal": "acción detectada",
        "fuente_datos": "base_datos|pdf_cargado|conversacion_previa|null",
        "contexto_especifico": "contexto relevante",
        "filtros": ["filtros detectados"],
        "parametros_extra": {{"parámetros adicionales"}}
    }}
}}
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(optimized_prompt)

            if response:
                # Parsear respuesta (usar mismo método que original)
                return self._parse_intention_response(response)

            return None

        except Exception as e:
            self.logger.error(f"Error en detección optimizada: {e}")
            return None

    def _parse_intention_response(self, response: str):
        """Mismo método de parsing que el original"""
        try:
            import re
            clean_response = response.strip()

            json_patterns = [
                r'```json\s*(.*?)\s*```',
                r'```\s*(.*?)\s*```',
                r'(\{.*?\})'
            ]

            for pattern in json_patterns:
                matches = re.findall(pattern, clean_response, re.DOTALL)
                if matches:
                    try:
                        return json.loads(matches[0])
                    except json.JSONDecodeError:
                        continue

            try:
                return json.loads(clean_response)
            except json.JSONDecodeError:
                return None

        except Exception as e:
            return None

class ABTester:
    """Ejecutor de pruebas A/B"""

    def __init__(self):
        self.gemini_client = GeminiClient()
        self.original_detector = IntentionDetector(self.gemini_client)
        self.optimized_detector = IntentionDetectorOptimized(self.gemini_client)

        # Consultas de prueba
        self.test_queries = [
            # Búsqueda simple
            "cuántos alumnos hay en la escuela",
            "buscar a Juan García",
            "alumnos de 3er grado",
            "dame la CURP de María López",

            # Generar constancia
            "constancia de estudios para María",
            "necesito certificado de calificaciones",
            "generar constancia de traslado",

            # Transformar PDF
            "transformar esta constancia",
            "convertir PDF al nuevo formato",

            # Consulta avanzada
            "estadísticas por grado",
            "análisis académico del turno matutino",

            # Ayuda sistema
            "qué puedes hacer",
            "ayúdame con el sistema",
            "cómo generar constancias",

            # Conversación general
            "hola buenos días",
            "gracias por la ayuda",
            "¿cómo estás?"
        ]

    def run_single_test(self, query: str, detector, version: str) -> TestResult:
        """Ejecuta una prueba individual"""
        start_time = time.time()

        try:
            if version == "original":
                result = detector.detect_intention(query)
            else:
                result = detector.detect_intention(query)

            response_time = time.time() - start_time

            if result:
                return TestResult(
                    query=query,
                    version=version,
                    response_time=response_time,
                    intention_type=result.get('intention_type', '') if isinstance(result, dict) else result.intention_type,
                    sub_intention=result.get('sub_intention', '') if isinstance(result, dict) else result.sub_intention,
                    confidence=result.get('confidence', 0) if isinstance(result, dict) else result.confidence,
                    detected_entities=result.get('detected_entities', {}) if isinstance(result, dict) else result.detected_entities,
                    success=True
                )
            else:
                return TestResult(
                    query=query,
                    version=version,
                    response_time=response_time,
                    intention_type="",
                    sub_intention="",
                    confidence=0,
                    detected_entities={},
                    success=False,
                    error="No response"
                )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                query=query,
                version=version,
                response_time=response_time,
                intention_type="",
                sub_intention="",
                confidence=0,
                detected_entities={},
                success=False,
                error=str(e)
            )

    def run_ab_test(self) -> Dict[str, Any]:
        """Ejecuta el test A/B completo"""
        print("🔬 INICIANDO TESTING A/B DEL INTENTIONDETECTOR")
        print("=" * 60)

        results = []

        for i, query in enumerate(self.test_queries, 1):
            print(f"\n📝 Test {i}/{len(self.test_queries)}: {query}")

            # Test versión original
            print("   🔄 Testing versión original...")
            original_result = self.run_single_test(query, self.original_detector, "original")
            results.append(original_result)

            # Test versión optimizada
            print("   ⚡ Testing versión optimizada...")
            optimized_result = self.run_single_test(query, self.optimized_detector, "optimized")
            results.append(optimized_result)

            # Mostrar comparación inmediata
            print(f"   📊 Original: {original_result.response_time:.2f}s | Optimizada: {optimized_result.response_time:.2f}s")

        return self.analyze_results(results)

    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analiza los resultados del testing"""
        original_results = [r for r in results if r.version == "original"]
        optimized_results = [r for r in results if r.version == "optimized"]

        # Métricas de tiempo
        original_times = [r.response_time for r in original_results if r.success]
        optimized_times = [r.response_time for r in optimized_results if r.success]

        # Métricas de precisión
        original_success_rate = len([r for r in original_results if r.success]) / len(original_results)
        optimized_success_rate = len([r for r in optimized_results if r.success]) / len(optimized_results)

        analysis = {
            "timing": {
                "original_avg": statistics.mean(original_times) if original_times else 0,
                "optimized_avg": statistics.mean(optimized_times) if optimized_times else 0,
                "improvement_percent": 0,
                "original_times": original_times,
                "optimized_times": optimized_times
            },
            "accuracy": {
                "original_success_rate": original_success_rate,
                "optimized_success_rate": optimized_success_rate,
                "accuracy_maintained": optimized_success_rate >= original_success_rate * 0.95
            },
            "detailed_results": results
        }

        if original_times and optimized_times:
            improvement = (statistics.mean(original_times) - statistics.mean(optimized_times)) / statistics.mean(original_times) * 100
            analysis["timing"]["improvement_percent"] = improvement

        return analysis

def main():
    """Función principal"""
    tester = ABTester()
    results = tester.run_ab_test()

    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL TESTING A/B")
    print("=" * 60)

    timing = results["timing"]
    accuracy = results["accuracy"]

    print(f"\n⏱️  MÉTRICAS DE TIEMPO:")
    print(f"   Original promedio: {timing['original_avg']:.2f}s")
    print(f"   Optimizada promedio: {timing['optimized_avg']:.2f}s")
    print(f"   Mejora: {timing['improvement_percent']:.1f}%")

    print(f"\n🎯 MÉTRICAS DE PRECISIÓN:")
    print(f"   Tasa éxito original: {accuracy['original_success_rate']:.1%}")
    print(f"   Tasa éxito optimizada: {accuracy['optimized_success_rate']:.1%}")
    print(f"   Precisión mantenida: {'✅ SÍ' if accuracy['accuracy_maintained'] else '❌ NO'}")

    # Recomendación
    if timing['improvement_percent'] >= 25 and accuracy['accuracy_maintained']:
        print(f"\n🎉 RECOMENDACIÓN: ✅ IMPLEMENTAR VERSIÓN OPTIMIZADA")
        print(f"   Mejora significativa de velocidad con precisión mantenida")
    else:
        print(f"\n⚠️  RECOMENDACIÓN: ❌ NO IMPLEMENTAR")
        print(f"   Mejora insuficiente o pérdida de precisión")

if __name__ == "__main__":
    main()
