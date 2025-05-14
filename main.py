from pdf_extractor import PDFExtractor
from pdf_generator import PDFGenerator
from db_manager import DBManager
import os
import sys

def main():
    """Ejecuta el programa en modo consola"""
    # Verificar argumentos
    if len(sys.argv) < 3:
        print("Uso: python main.py <archivo_pdf> <tipo_constancia> [--con-foto=si|no|auto]")
        print("Tipos disponibles: traslado, estudio, calificaciones")
        print("Opciones:")
        print("  --con-foto=si    Incluir foto en la constancia (si está disponible)")
        print("  --con-foto=no    No incluir foto en la constancia")
        print("  --con-foto=auto  Detectar automáticamente (por defecto)")
        return

    # Obtener argumentos
    pdf_path = sys.argv[1]
    tipo_constancia = sys.argv[2]

    # Procesar opción de foto
    incluir_foto = None  # Auto por defecto
    for arg in sys.argv[3:]:
        if arg.startswith("--con-foto="):
            opcion_foto = arg.split("=")[1].lower()
            if opcion_foto == "si":
                incluir_foto = True
            elif opcion_foto == "no":
                incluir_foto = False
            elif opcion_foto == "auto":
                incluir_foto = None
            else:
                print(f"Error: Valor no válido para --con-foto. Opciones: si, no, auto")
                return

    # Verificar que el archivo existe
    if not os.path.exists(pdf_path):
        print(f"Error: El archivo {pdf_path} no existe")
        return

    # Verificar tipo de constancia
    tipos_validos = ["traslado", "estudio", "calificaciones"]
    if tipo_constancia not in tipos_validos:
        print(f"Error: Tipo de constancia no válido. Opciones: {', '.join(tipos_validos)}")
        return

    # Extraer datos
    print(f"Extrayendo datos de {pdf_path}...")
    extractor = PDFExtractor(pdf_path)

    # Pasar el tipo de constancia solicitado para que se respete en la extracción
    datos = extractor.extraer_todos_datos(incluir_foto, tipo_constancia)

    # Mostrar datos extraídos
    print("\nDatos extraídos:")
    print(f"Nombre: {datos.get('nombre', '')}")
    print(f"CURP: {datos.get('curp', '')}")
    print(f"Matrícula: {datos.get('matricula', '')}")
    print(f"Grado: {datos.get('grado', '')} Grupo: {datos.get('grupo', '')} Turno: {datos.get('turno', '')}")

    # Mostrar si se incluirán calificaciones
    if datos.get("mostrar_calificaciones", False):
        print("Calificaciones: Se incluirán en la constancia")
    else:
        print("Calificaciones: No se incluirán en la constancia")

    # Mostrar estado de la foto
    if datos.get("has_photo", False):
        print("Foto: Incluida")
    else:
        if incluir_foto is False:
            print("Foto: No incluida (por elección del usuario)")
        else:
            print("Foto: No disponible")

    # Generar constancia
    print(f"\nGenerando constancia de {tipo_constancia}...")
    generator = PDFGenerator()
    generator.crear_todas_plantillas()
    output_path = generator.generar_constancia(tipo_constancia, datos)

    if output_path:
        print(f"Constancia generada con éxito: {output_path}")

        # Preguntar si guardar en base de datos
        respuesta = input("\n¿Desea guardar los datos del alumno en la base de datos? (s/n): ")
        if respuesta.lower() == "s":
            db = DBManager()
            alumno_id = db.guardar_alumno(datos)
            if alumno_id:
                db.registrar_constancia(alumno_id, tipo_constancia, output_path)
                print("Datos guardados en la base de datos")
            else:
                print("Error al guardar datos en la base de datos")
            db.close()
    else:
        print("Error al generar constancia")

# Crear directorios necesarios
os.makedirs("plantillas", exist_ok=True)
os.makedirs("logos", exist_ok=True)
os.makedirs("fotos", exist_ok=True)
os.makedirs("salidas", exist_ok=True)

if __name__ == "__main__":
    # Este script ahora solo ejecuta el modo consola
    main()
