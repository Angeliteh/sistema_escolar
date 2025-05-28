#!/usr/bin/env python3
"""
🔬 TESTING A/B PARA OPTIMIZACIÓN DEL PROMPT 3 (CRÍTICO)
Compara versión actual vs versión optimizada del _validate_and_generate_response

Uso: python testing_ab_prompt3_optimization.py
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

from app.ui.ai_chat.gemini_client import GeminiClient
from app.core.logging import get_logger

@dataclass
class TestResult:
    """Resultado de una prueba individual"""
    query: str
    version: str
    response_time: float
    success: bool
    response_quality: str
    has_auto_reflection: bool
    error: str = ""

class Prompt3Optimizer:
    """Versión optimizada del PROMPT 3 para testing"""

    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.logger = get_logger(__name__)

    def validate_and_generate_response_optimized(self, user_query: str, sql_query: str, data: List[Dict], row_count: int) -> Dict:
        """Versión ULTRA-optimizada del prompt 3 (104 → 22 líneas)"""
        try:
            # PROMPT ULTRA-OPTIMIZADO (22 líneas vs 104 originales)
            optimized_prompt = f"""
Validador escolar "PROF. MAXIMO GAMIZ FERNANDEZ".

CONSULTA: "{user_query}"
DATOS: {data if row_count <= 8 else data[:3]}

VALIDAR: ¿Los datos responden la consulta exacta?

RESPONDER como secretario profesional:
- Usa datos reales, NO placeholders
- Ofrece constancias si aplica
- NO menciones SQL/técnico

AUTO-REFLEXIÓN: ¿Esperas continuación?

JSON:
{{
  "respuesta_usuario": "Respuesta aquí",
  "reflexion_conversacional": {{
    "espera_continuacion": true|false,
    "tipo_esperado": "selection|action|confirmation|none",
    "datos_recordar": {{"query": "{user_query}", "data": [datos], "row_count": {row_count}}},
    "razonamiento": "Por qué esperas continuación"
  }}
}}

Si falla: "VALIDACION_FALLIDA"
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(optimized_prompt)

            if response:
                # Verificar si la validación falló
                if "VALIDACION_FALLIDA" in response.upper():
                    return None

                # Parsear respuesta JSON
                return self._parse_json_response(response)

            return None

        except Exception as e:
            self.logger.error(f"Error en prompt optimizado: {e}")
            return None

    def validate_and_generate_response_original(self, user_query: str, sql_query: str, data: List[Dict], row_count: int) -> Dict:
        """Versión original del prompt 3 (104 líneas)"""
        try:
            # PROMPT ORIGINAL COMPLETO (104 líneas)
            original_prompt = f"""
Eres un validador y comunicador experto para un sistema escolar con CAPACIDAD DE AUTO-REFLEXIÓN.

CONTEXTO COMPLETO DEL SISTEMA:
- Sistema de gestión escolar para la escuela primaria "PROF. MAXIMO GAMIZ FERNANDEZ"
- Maneja datos de alumnos, información académica y generación de constancias del ciclo escolar 2024-2025
- Los usuarios son personal administrativo, maestros y directivos que necesitan información para tomar decisiones educativas

CONSULTA ORIGINAL DEL USUARIO: "{user_query}"

CONSULTA SQL EJECUTADA: {sql_query}

RESULTADOS OBTENIDOS (FILTRADOS INTELIGENTEMENTE):
TIPO DE CONSULTA: SELECT (listado)
NÚMERO DE REGISTROS: {row_count}
DATOS OBTENIDOS: {data if row_count <= 15 else data[:10]}
{"... y " + str(row_count - 10) + " registros adicionales" if row_count > 10 else ""}

INFORMACIÓN DEL FILTRO INTELIGENTE:
- Acción aplicada: mantener
- Datos originales: {len(data)} registros
- Datos filtrados: {row_count} registros
- Razonamiento del filtro: Datos procesados correctamente

INSTRUCCIONES PRINCIPALES:
1. VALIDA que el SQL resolvió exactamente lo que pidió el usuario
2. VERIFICA que los resultados son coherentes y lógicos
3. Si la validación es exitosa, GENERA una respuesta natural integrada
4. 🆕 AUTO-REFLEXIONA sobre tu respuesta como un secretario experto
5. Si la validación falla, responde con "VALIDACION_FALLIDA"

IMPORTANTE - USA LOS DATOS REALES:
- Los datos en RESULTADOS OBTENIDOS son REALES de la base de datos
- MUESTRA estos datos tal como están, no inventes placeholders
- Si hay nombres, CURPs, grados - ÚSALOS directamente
- NO digas "[Listado aquí]" - MUESTRA el listado real

CRITERIOS DE VALIDACIÓN:
- ¿El SQL responde exactamente la pregunta del usuario?
- ¿Los resultados tienen sentido en el contexto escolar?
- ¿La cantidad de resultados es lógica?
- ¿Los datos mostrados son relevantes para la consulta?

FORMATO DE RESPUESTA NATURAL (si validación exitosa):
- Presenta la información como un colega educativo profesional
- Contextualiza los datos dentro del marco escolar real
- Ofrece acciones específicas (constancias, reportes, seguimiento)
- Usa el contexto de la escuela y ciclo escolar
- NO menciones términos técnicos (SQL, base de datos, validación)

REGLAS PARA MOSTRAR DATOS REALES:
- SIEMPRE muestra los datos reales obtenidos de la consulta
- NO uses placeholders como "[Listado de alumnos aquí]"
- NO inventes reglas sobre cuántos mostrar
- PRESENTA los datos tal como están en los resultados
- Si hay muchos datos, muestra los primeros y menciona que hay más disponibles

🧠 AUTO-REFLEXIÓN CONVERSACIONAL MEJORADA:
Después de generar tu respuesta, reflexiona como un secretario escolar experto:

ANÁLISIS REFLEXIVO ESPECÍFICO:
- ¿La respuesta que acabo de dar podría generar preguntas de seguimiento?
- ¿Mostré una lista que el usuario podría querer referenciar ("el tercero", "número 5")?
- ¿Proporcioné información de un alumno específico que podría necesitar CONSTANCIA?
- ¿Debería sugerir proactivamente la generación de constancias?
- ¿Ofrecí servicios que requieren confirmación o especificación?
- ¿Debería recordar estos datos para futuras consultas en esta conversación?

SUGERENCIAS INTELIGENTES DE CONSTANCIAS:
- Si mostré 1 alumno específico: Sugerir constancia directamente
- Si mostré pocos alumnos (2-5): Esperar selección, luego sugerir constancia
- Si mostré muchos alumnos (6+): Esperar refinamiento de búsqueda
- Si mostré estadísticas: No sugerir constancias

DECISIÓN CONVERSACIONAL:
Si tu respuesta espera continuación, especifica:
- Tipo esperado: "selection" (selección de lista), "action" (acción sobre alumno), "confirmation" (confirmación), "specification" (especificación), "constancia_suggestion" (sugerir constancia)
- Datos a recordar: información relevante para futuras referencias
- Razonamiento: por qué esperas esta continuación y si incluye sugerencia de constancia

FORMATO DE RESPUESTA COMPLETA:
{{
  "respuesta_usuario": "Tu respuesta profesional completa aquí",
  "reflexion_conversacional": {{
    "espera_continuacion": true|false,
    "tipo_esperado": "selection|action|confirmation|specification|none",
    "datos_recordar": {{
      "query": "consulta original",
      "data": [datos relevantes filtrados],
      "row_count": número_elementos_filtrados,
      "context": "contexto adicional",
      "filter_applied": "información del filtro inteligente"
    }},
    "razonamiento": "Explicación de por qué esperas o no esperas continuación"
  }}
}}

EJEMPLOS DE AUTO-REFLEXIÓN:

Ejemplo 1 - Lista de alumnos:
"Mostré una lista de 21 alumnos García. Es muy probable que el usuario quiera información específica de alguno, como 'CURP del quinto' o 'constancia para el tercero'. Debería recordar esta lista."

Ejemplo 2 - Información específica:
"Proporcioné datos completos de Juan Pérez. Esto típicamente lleva a solicitudes de constancias o más información. Debería recordar que estamos hablando de Juan."

Ejemplo 3 - Consulta estadística:
"Di un número total de alumnos. Esta es información general que no requiere seguimiento específico. No necesito recordar nada especial."
"""

            # Enviar al LLM
            response = self.gemini_client.send_prompt_sync(original_prompt)

            if response:
                # Verificar si la validación falló
                if "VALIDACION_FALLIDA" in response.upper():
                    return None

                # Parsear respuesta JSON
                return self._parse_json_response(response)

            return None

        except Exception as e:
            self.logger.error(f"Error en prompt original: {e}")
            return None

    def _parse_json_response(self, response: str) -> Dict:
        """Parsea respuesta JSON del LLM"""
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

class ABTesterPrompt3:
    """Ejecutor de pruebas A/B para Prompt 3"""

    def __init__(self):
        self.gemini_client = GeminiClient()
        self.optimizer = Prompt3Optimizer(self.gemini_client)

        # Casos de prueba realistas
        self.test_cases = [
            {
                "user_query": "cuántos alumnos hay en la escuela",
                "sql_query": "SELECT COUNT(*) as total FROM alumnos",
                "data": [{"total": 211}],
                "row_count": 1
            },
            {
                "user_query": "alumnos de 3er grado",
                "sql_query": "SELECT nombre, curp FROM alumnos a JOIN datos_escolares de ON a.id = de.alumno_id WHERE de.grado = 3",
                "data": [
                    {"nombre": "JUAN PÉREZ GARCÍA", "curp": "PEGJ120515HDFRZN01"},
                    {"nombre": "MARÍA LÓPEZ SANTOS", "curp": "LOSM130620MDFPNR02"},
                    {"nombre": "CARLOS RUIZ MENDOZA", "curp": "RUMC140710HDFZRL03"}
                ],
                "row_count": 3
            },
            {
                "user_query": "buscar a María García",
                "sql_query": "SELECT * FROM alumnos WHERE nombre LIKE '%MARIA%' AND nombre LIKE '%GARCIA%'",
                "data": [
                    {"id": 15, "nombre": "MARÍA GARCÍA LÓPEZ", "curp": "GALM130515MDFRZR01", "matricula": "2024001"}
                ],
                "row_count": 1
            },
            {
                "user_query": "estadísticas por grado",
                "sql_query": "SELECT grado, COUNT(*) as total FROM datos_escolares GROUP BY grado",
                "data": [
                    {"grado": 1, "total": 35},
                    {"grado": 2, "total": 38},
                    {"grado": 3, "total": 42},
                    {"grado": 4, "total": 39},
                    {"grado": 5, "total": 33},
                    {"grado": 6, "total": 24}
                ],
                "row_count": 6
            }
        ]

    def run_single_test(self, test_case: Dict, version: str) -> TestResult:
        """Ejecuta una prueba individual"""
        start_time = time.time()

        try:
            if version == "original":
                result = self.optimizer.validate_and_generate_response_original(
                    test_case["user_query"],
                    test_case["sql_query"],
                    test_case["data"],
                    test_case["row_count"]
                )
            else:
                result = self.optimizer.validate_and_generate_response_optimized(
                    test_case["user_query"],
                    test_case["sql_query"],
                    test_case["data"],
                    test_case["row_count"]
                )

            response_time = time.time() - start_time

            if result:
                has_reflection = "reflexion_conversacional" in result
                quality = "good" if result.get("respuesta_usuario") else "poor"

                return TestResult(
                    query=test_case["user_query"],
                    version=version,
                    response_time=response_time,
                    success=True,
                    response_quality=quality,
                    has_auto_reflection=has_reflection
                )
            else:
                return TestResult(
                    query=test_case["user_query"],
                    version=version,
                    response_time=response_time,
                    success=False,
                    response_quality="failed",
                    has_auto_reflection=False,
                    error="No response"
                )

        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                query=test_case["user_query"],
                version=version,
                response_time=response_time,
                success=False,
                response_quality="error",
                has_auto_reflection=False,
                error=str(e)
            )

    def run_ab_test(self) -> Dict[str, Any]:
        """Ejecuta el test A/B completo"""
        print("🔬 INICIANDO TESTING A/B DEL PROMPT 3 (CRÍTICO)")
        print("=" * 60)

        results = []

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n📝 Test {i}/{len(self.test_cases)}: {test_case['user_query']}")

            # Test versión original
            print("   🔄 Testing versión original...")
            original_result = self.run_single_test(test_case, "original")
            results.append(original_result)

            # Test versión optimizada
            print("   ⚡ Testing versión optimizada...")
            optimized_result = self.run_single_test(test_case, "optimized")
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

        # Métricas de calidad
        original_success_rate = len([r for r in original_results if r.success]) / len(original_results)
        optimized_success_rate = len([r for r in optimized_results if r.success]) / len(optimized_results)

        # Métricas de auto-reflexión
        original_reflection_rate = len([r for r in original_results if r.has_auto_reflection]) / len(original_results)
        optimized_reflection_rate = len([r for r in optimized_results if r.has_auto_reflection]) / len(optimized_results)

        analysis = {
            "timing": {
                "original_avg": statistics.mean(original_times) if original_times else 0,
                "optimized_avg": statistics.mean(optimized_times) if optimized_times else 0,
                "improvement_percent": 0,
                "original_times": original_times,
                "optimized_times": optimized_times
            },
            "quality": {
                "original_success_rate": original_success_rate,
                "optimized_success_rate": optimized_success_rate,
                "quality_maintained": optimized_success_rate >= original_success_rate * 0.95
            },
            "reflection": {
                "original_reflection_rate": original_reflection_rate,
                "optimized_reflection_rate": optimized_reflection_rate,
                "reflection_maintained": optimized_reflection_rate >= original_reflection_rate * 0.95
            },
            "detailed_results": results
        }

        if original_times and optimized_times:
            improvement = (statistics.mean(original_times) - statistics.mean(optimized_times)) / statistics.mean(original_times) * 100
            analysis["timing"]["improvement_percent"] = improvement

        return analysis

def main():
    """Función principal"""
    tester = ABTesterPrompt3()
    results = tester.run_ab_test()

    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL TESTING A/B - PROMPT 3")
    print("=" * 60)

    timing = results["timing"]
    quality = results["quality"]
    reflection = results["reflection"]

    print(f"\n⏱️  MÉTRICAS DE TIEMPO:")
    print(f"   Original promedio: {timing['original_avg']:.2f}s")
    print(f"   Optimizada promedio: {timing['optimized_avg']:.2f}s")
    print(f"   Mejora: {timing['improvement_percent']:.1f}%")

    print(f"\n🎯 MÉTRICAS DE CALIDAD:")
    print(f"   Tasa éxito original: {quality['original_success_rate']:.1%}")
    print(f"   Tasa éxito optimizada: {quality['optimized_success_rate']:.1%}")
    print(f"   Calidad mantenida: {'✅ SÍ' if quality['quality_maintained'] else '❌ NO'}")

    print(f"\n🧠 MÉTRICAS DE AUTO-REFLEXIÓN:")
    print(f"   Auto-reflexión original: {reflection['original_reflection_rate']:.1%}")
    print(f"   Auto-reflexión optimizada: {reflection['optimized_reflection_rate']:.1%}")
    print(f"   Auto-reflexión mantenida: {'✅ SÍ' if reflection['reflection_maintained'] else '❌ NO'}")

    # Recomendación (criterio ajustado para ser más realista)
    if (timing['improvement_percent'] >= 15 and
        quality['quality_maintained'] and
        reflection['reflection_maintained']):
        print(f"\n🎉 RECOMENDACIÓN: ✅ IMPLEMENTAR VERSIÓN OPTIMIZADA")
        print(f"   Mejora de velocidad ({timing['improvement_percent']:.1f}%) manteniendo calidad y funcionalidad")
    else:
        print(f"\n⚠️  RECOMENDACIÓN: ❌ NO IMPLEMENTAR")
        print(f"   Mejora insuficiente ({timing['improvement_percent']:.1f}% < 15%) o pérdida de calidad/funcionalidad")

if __name__ == "__main__":
    main()
