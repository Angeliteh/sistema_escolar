#!/usr/bin/env python3
"""
Script para probar las plantillas SQL individualmente
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.sql_templates.template_executor import TemplateExecutor

def test_all_templates():
    """Prueba todas las plantillas con datos de ejemplo"""
    
    print("=" * 60)
    print("🧪 TESTING DE PLANTILLAS SQL")
    print("=" * 60)
    print()
    
    executor = TemplateExecutor()
    
    # Obtener plantillas disponibles
    templates_info = executor.get_available_templates()
    print(f"📋 Plantillas disponibles: {len(templates_info)}")
    for name, description in templates_info.items():
        print(f"  ✅ {name}: {description}")
    print()
    
    # Tests específicos
    test_cases = [
        {
            "name": "Búsqueda básica por nombre",
            "query": "busca a ELENA JIMENEZ HERNANDEZ",
            "expected_template": "buscar_alumno_basico"
        },
        {
            "name": "Información completa de alumno", 
            "query": "información de ELENA JIMENEZ HERNANDEZ",
            "expected_template": "buscar_alumno_completo"
        },
        {
            "name": "Datos de alumno",
            "query": "datos de LUIS FERNANDO MARTINEZ TORRES", 
            "expected_template": "buscar_alumno_completo"
        },
        {
            "name": "Filtrar por grado",
            "query": "alumnos de 4to grado",
            "expected_template": "filtrar_por_grado"
        },
        {
            "name": "Filtrar por turno",
            "query": "alumnos del turno matutino",
            "expected_template": "filtrar_por_turno"
        },
        {
            "name": "Contar total",
            "query": "cuántos alumnos hay en total",
            "expected_template": "contar_alumnos_total"
        }
    ]
    
    print("🧪 EJECUTANDO CASOS DE PRUEBA:")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 TEST {i}: {test_case['name']}")
        print(f"🔍 Query: '{test_case['query']}'")
        print(f"🎯 Plantilla esperada: {test_case['expected_template']}")
        
        try:
            result = executor.execute_query(test_case['query'])
            
            if result.success:
                print(f"✅ ÉXITO")
                print(f"   📊 Plantilla usada: {result.template_used}")
                print(f"   📈 Resultados: {result.row_count}")
                print(f"   📋 Parámetros: {result.parameters_used}")
                
                # Verificar si usó la plantilla esperada
                if result.template_used == test_case['expected_template']:
                    print(f"   🎯 ✅ Plantilla correcta")
                else:
                    print(f"   🎯 ⚠️ Plantilla diferente (esperada: {test_case['expected_template']})")
                
                # Mostrar muestra de datos si hay resultados
                if result.data and result.row_count > 0:
                    if isinstance(result.data, list) and len(result.data) > 0:
                        sample = result.data[0]
                        if isinstance(sample, dict):
                            print(f"   📄 Muestra: {sample.get('nombre', 'N/A')}")
                        else:
                            print(f"   📄 Muestra: {sample}")
                    else:
                        print(f"   📄 Datos: {result.data}")
                        
            else:
                print(f"❌ FALLO: {result.message}")
                print(f"   📊 Plantilla intentada: {result.template_used}")
                
        except Exception as e:
            print(f"💥 ERROR: {e}")
        
        print("-" * 40)
    
    print("\n🎉 TESTING COMPLETADO")

def test_specific_template():
    """Prueba una plantilla específica con parámetros manuales"""
    
    print("\n" + "=" * 60)
    print("🔧 TESTING DE PLANTILLA ESPECÍFICA")
    print("=" * 60)
    
    executor = TemplateExecutor()
    
    # Test manual de plantilla específica
    print("\n📋 Probando 'buscar_alumno_completo' con ELENA JIMENEZ HERNANDEZ")
    
    result = executor.test_template(
        "buscar_alumno_completo",
        {"nombre": "ELENA JIMENEZ HERNANDEZ"}
    )
    
    if result.success:
        print("✅ ÉXITO")
        print(f"📊 Resultados: {result.row_count}")
        print(f"🔍 SQL ejecutado: {result.sql_executed}")
        
        if result.data:
            print("📄 DATOS OBTENIDOS:")
            if isinstance(result.data, list):
                for i, record in enumerate(result.data):
                    print(f"  📋 Registro {i+1}:")
                    if isinstance(record, dict):
                        for key, value in record.items():
                            if key == 'calificaciones' and value:
                                print(f"    {key}: {len(value)} materias")
                            else:
                                print(f"    {key}: {value}")
                    print()
    else:
        print(f"❌ FALLO: {result.message}")

if __name__ == "__main__":
    try:
        test_all_templates()
        test_specific_template()
    except Exception as e:
        print(f"💥 ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
