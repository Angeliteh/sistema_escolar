"""
🧪 SCRIPT DE PRUEBA PARA ACCIONES

Este script prueba directamente las acciones sin pasar por el LLM
para verificar que funcionen correctamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Prueba las importaciones básicas"""
    try:
        from app.core.ai.actions import ActionCatalog, ActionExecutor
        print("✅ Importaciones exitosas")
        return True
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_action_catalog():
    """Prueba el catálogo de acciones"""
    print("🎯 PROBANDO CATÁLOGO DE ACCIONES")
    print("=" * 50)

    catalog = ActionCatalog()

    # Obtener todas las acciones
    all_actions = catalog.get_all_actions()
    print(f"📊 Total de acciones disponibles: {len(all_actions)}")

    for name, action in all_actions.items():
        print(f"✅ {name}: {action.description}")

    print("\n🔍 ACCIONES PARA BÚSQUEDA:")
    search_actions = catalog.get_actions_for_category("busqueda")
    for name, action in search_actions.items():
        print(f"   - {name}")

    print("\n📊 ACCIONES PARA ESTADÍSTICA:")
    stats_actions = catalog.get_actions_for_category("estadistica")
    for name, action in stats_actions.items():
        print(f"   - {name}")

def test_action_executor():
    """Prueba el ejecutor de acciones"""
    print("\n🎯 PROBANDO EJECUTOR DE ACCIONES")
    print("=" * 50)

    # Crear SQL executor
    sql_executor = SQLExecutor("resources/data/alumnos.db")

    # Crear action executor
    action_executor = ActionExecutor(sql_executor)

    # PRUEBA 1: Buscar coincidencias de "garcia"
    print("\n🔍 PRUEBA 1: BUSCAR_COINCIDENCIAS_NOMBRE")
    action_request_1 = {
        "estrategia": "simple",
        "accion_principal": "BUSCAR_COINCIDENCIAS_NOMBRE",
        "parametros": {
            "nombre_parcial": "garcia",
            "limite_resultados": 5
        },
        "razonamiento": "Prueba de búsqueda de coincidencias"
    }

    result_1 = action_executor.execute_action_request(action_request_1)
    print(f"   ✅ Success: {result_1.get('success')}")
    print(f"   📊 Resultados: {result_1.get('row_count')}")
    print(f"   💬 Mensaje: {result_1.get('message')}")
    if result_1.get('data'):
        print(f"   👤 Primer resultado: {result_1['data'][0].get('nombre', 'N/A')}")

    # PRUEBA 2: Buscar alumno exacto
    print("\n🎯 PRUEBA 2: BUSCAR_ALUMNO_EXACTO")
    action_request_2 = {
        "estrategia": "simple",
        "accion_principal": "BUSCAR_ALUMNO_EXACTO",
        "parametros": {
            "nombre_completo": "LUIS FERNANDO MARTINEZ TORRES",
            "strict_match": False
        },
        "razonamiento": "Prueba de búsqueda exacta"
    }

    result_2 = action_executor.execute_action_request(action_request_2)
    print(f"   ✅ Success: {result_2.get('success')}")
    print(f"   📊 Resultados: {result_2.get('row_count')}")
    print(f"   💬 Mensaje: {result_2.get('message')}")
    if result_2.get('data'):
        print(f"   👤 Resultado: {result_2['data'][0].get('nombre', 'N/A')}")

    # PRUEBA 3: Listar por criterio
    print("\n📋 PRUEBA 3: LISTAR_POR_CRITERIO")
    action_request_3 = {
        "estrategia": "simple",
        "accion_principal": "LISTAR_POR_CRITERIO",
        "parametros": {
            "criterio_campo": "grado",
            "criterio_valor": "2",
            "incluir_datos_completos": True
        },
        "razonamiento": "Prueba de listado por grado"
    }

    result_3 = action_executor.execute_action_request(action_request_3)
    print(f"   ✅ Success: {result_3.get('success')}")
    print(f"   📊 Resultados: {result_3.get('row_count')}")
    print(f"   💬 Mensaje: {result_3.get('message')}")
    if result_3.get('data'):
        print(f"   👤 Primer alumno: {result_3['data'][0].get('nombre', 'N/A')}")

    # PRUEBA 4: Contar alumnos
    print("\n🔢 PRUEBA 4: CONTAR_ALUMNOS")
    action_request_4 = {
        "estrategia": "simple",
        "accion_principal": "CONTAR_ALUMNOS",
        "parametros": {
            "criterio_campo": "grado",
            "criterio_valor": "2"
        },
        "razonamiento": "Prueba de conteo por grado"
    }

    result_4 = action_executor.execute_action_request(action_request_4)
    print(f"   ✅ Success: {result_4.get('success')}")
    print(f"   📊 Resultados: {result_4.get('row_count')}")
    print(f"   💬 Mensaje: {result_4.get('message')}")
    if result_4.get('data'):
        print(f"   🔢 Total: {result_4['data'][0].get('total', 'N/A')}")

    # PRUEBA 5: Conteo agrupado
    print("\n📊 PRUEBA 5: CONTAR_ALUMNOS (AGRUPADO)")
    action_request_5 = {
        "estrategia": "simple",
        "accion_principal": "CONTAR_ALUMNOS",
        "parametros": {
            "agrupar_por": "grado"
        },
        "razonamiento": "Prueba de conteo agrupado por grado"
    }

    result_5 = action_executor.execute_action_request(action_request_5)
    print(f"   ✅ Success: {result_5.get('success')}")
    print(f"   📊 Resultados: {result_5.get('row_count')}")
    print(f"   💬 Mensaje: {result_5.get('message')}")
    if result_5.get('data'):
        print("   📊 Distribución por grado:")
        for row in result_5['data'][:5]:  # Mostrar primeros 5
            print(f"      Grado {row.get('grado', 'N/A')}: {row.get('total', 'N/A')} alumnos")

def test_action_validation():
    """Prueba la validación de acciones"""
    print("\n🔍 PROBANDO VALIDACIÓN DE ACCIONES")
    print("=" * 50)

    catalog = ActionCatalog()

    # Solicitud válida
    valid_request = {
        "accion_principal": "BUSCAR_COINCIDENCIAS_NOMBRE",
        "parametros": {
            "nombre_parcial": "garcia",
            "limite_resultados": 10
        }
    }

    is_valid, message = catalog.validate_action_request(valid_request)
    print(f"✅ Solicitud válida: {is_valid} - {message}")

    # Solicitud inválida (falta parámetro)
    invalid_request = {
        "accion_principal": "BUSCAR_COINCIDENCIAS_NOMBRE",
        "parametros": {
            "limite_resultados": 10
            # Falta "nombre_parcial"
        }
    }

    is_valid, message = catalog.validate_action_request(invalid_request)
    print(f"❌ Solicitud inválida: {is_valid} - {message}")

    # Acción inexistente
    nonexistent_request = {
        "accion_principal": "ACCION_INEXISTENTE",
        "parametros": {}
    }

    is_valid, message = catalog.validate_action_request(nonexistent_request)
    print(f"❌ Acción inexistente: {is_valid} - {message}")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE SISTEMA DE ACCIONES")
    print("=" * 60)

    try:
        # Primero probar importaciones
        if not test_basic_imports():
            print("❌ Fallo en importaciones básicas")
            exit(1)

        # Importar aquí después de verificar
        from app.core.ai.actions import ActionCatalog, ActionExecutor
        from app.core.ai.interpretation.sql_executor import SQLExecutor

        # Probar catálogo
        print("\n🎯 PROBANDO CATÁLOGO...")
        catalog = ActionCatalog()
        all_actions = catalog.get_all_actions()
        print(f"📊 Total de acciones: {len(all_actions)}")

        for name, action in list(all_actions.items())[:3]:  # Solo primeras 3
            print(f"✅ {name}: {action.description}")

        # Probar validación
        print("\n🔍 PROBANDO VALIDACIÓN...")
        valid_request = {
            "accion_principal": "BUSCAR_COINCIDENCIAS_NOMBRE",
            "parametros": {
                "nombre_parcial": "garcia",
                "limite_resultados": 10
            }
        }

        is_valid, message = catalog.validate_action_request(valid_request)
        print(f"✅ Validación: {is_valid} - {message}")

        # Probar ejecución real de acción
        print("\n🎯 PROBANDO EJECUCIÓN DE ACCIÓN...")
        try:
            sql_executor = SQLExecutor("resources/data/alumnos.db")
            action_executor = ActionExecutor(sql_executor)

            # Ejecutar acción de búsqueda
            result = action_executor.execute_action_request(valid_request)
            print(f"✅ Ejecución: {result.get('success')}")
            print(f"📊 Resultados: {result.get('row_count', 0)}")
            print(f"💬 Mensaje: {result.get('message', 'N/A')}")

            if result.get('data') and len(result['data']) > 0:
                print(f"👤 Primer resultado: {result['data'][0].get('nombre', 'N/A')}")

        except Exception as e:
            print(f"⚠️ Error en ejecución (esperado si no hay BD): {e}")

        # 🆕 PROBAR ACCIÓN DE CONSTANCIA
        print("\n📄 PROBANDO ACCIÓN DE CONSTANCIA...")
        try:
            constancia_request = {
                "estrategia": "simple",
                "accion_principal": "PREPARAR_DATOS_CONSTANCIA",
                "parametros": {
                    "alumno_identificador": "ALEJANDRA SANCHEZ GARCIA",
                    "tipo_constancia": "estudio",
                    "incluir_calificaciones": False
                },
                "razonamiento": "Prueba de preparación de constancia"
            }

            result = action_executor.execute_action_request(constancia_request)
            print(f"✅ Constancia preparada: {result.get('success')}")
            print(f"📊 Resultados: {result.get('row_count', 0)}")
            print(f"💬 Mensaje: {result.get('message', 'N/A')}")

            if result.get('data') and len(result['data']) > 0:
                datos = result['data'][0]
                print(f"👤 Alumno: {datos.get('alumno', {}).get('nombre', 'N/A')}")
                print(f"📄 Tipo: {datos.get('tipo_constancia', 'N/A')}")
                print(f"✅ Puede generar: {datos.get('puede_generar', False)}")

        except Exception as e:
            print(f"⚠️ Error en constancia: {e}")

        # 🆕 PROBAR ACCIÓN DE ESTADÍSTICA
        print("\n📊 PROBANDO ACCIÓN DE ESTADÍSTICA...")
        try:
            estadistica_request = {
                "estrategia": "simple",
                "accion_principal": "CALCULAR_ESTADISTICA",
                "parametros": {
                    "tipo": "conteo",
                    "agrupar_por": "grado",
                    "filtro": {},
                    "incluir_detalles": "false"
                },
                "razonamiento": "Prueba de conteo por grado"
            }

            result = action_executor.execute_action_request(estadistica_request)
            print(f"✅ Estadística calculada: {result.get('success')}")
            print(f"📊 Resultados: {result.get('row_count', 0)}")
            print(f"💬 Mensaje: {result.get('message', 'N/A')}")

            if result.get('data') and len(result['data']) > 0:
                datos = result['data'][0]
                print(f"📈 Estadísticas: {datos}")
                print(f"🎯 Total elementos: {result.get('total_elementos', 'N/A')}")

        except Exception as e:
            print(f"⚠️ Error en estadística: {e}")

        print("\n🎉 PRUEBAS BÁSICAS COMPLETADAS")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
