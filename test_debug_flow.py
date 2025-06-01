#!/usr/bin/env python3
"""
🛑 TEST DEBUG FLOW - Prueba el flujo completo con pausas estratégicas

Este script prueba el flujo Master → Student → ActionExecutor con pausas
en los puntos críticos para debugging.

Uso:
    python test_debug_flow.py --debug-pauses

Flujo de prueba:
    1. 🎯 ENTRADA: "busca alumnos con apellido Martinez"
    2. 🧠 MASTER: Detecta intención y entidades
    3. 🔄 MASTER → STUDENT: Envía información consolidada
    4. 🎓 STUDENT: Procesa y genera acción
    5. 🔧 ACTION EXECUTOR: Ejecuta SQL
    6. 📊 RESULTADO: Muestra datos encontrados
"""

import os
import sys
import subprocess

def main():
    """Ejecuta prueba con debug pauses"""
    
    print("🛑 TEST DEBUG FLOW - Flujo Master → Student → ActionExecutor")
    print("=" * 60)
    
    # Configurar variables de entorno
    os.environ['DEBUG_PAUSES'] = 'true'
    
    # Consulta de prueba
    test_query = "busca alumnos con apellido Martinez"
    
    print(f"📝 Consulta de prueba: '{test_query}'")
    print(f"🛑 DEBUG_PAUSES activado: {os.environ.get('DEBUG_PAUSES')}")
    print()
    print("🎯 PUNTOS DE PAUSA ESPERADOS:")
    print("   1. 🧠 MASTER detecta intención")
    print("   2. 🔄 MASTER → STUDENT comunicación")
    print("   3. 🎓 STUDENT recibe del Master")
    print("   4. 🔧 ACTION EXECUTOR recibe solicitud")
    print("   5. 📊 RESULTADO SQL ejecutado")
    print("   6. 🗣️ MASTER genera respuesta final")
    print()
    print("Presiona ENTER para iniciar...")
    input()
    
    try:
        # Cambiar al directorio del sistema
        os.chdir("C:\\Users\\Angel\\Desktop\\constancias_system")
        
        # Ejecutar ai_chat.py con la consulta
        cmd = f'echo "{test_query}" | python ai_chat.py'
        
        print(f"🚀 Ejecutando: {cmd}")
        print("=" * 60)
        
        # Ejecutar comando
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,  # Mostrar output en tiempo real
            text=True
        )
        
        print("=" * 60)
        print(f"✅ Comando completado con código: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
