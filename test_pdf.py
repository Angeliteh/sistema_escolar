import pdfplumber
import re
import sys

def extract_text_from_pdf(pdf_path):
    """Extrae el texto completo de un PDF y lo muestra"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
            return text
    except Exception as e:
        return f"Error al extraer texto: {e}"

def check_for_calificaciones(text):
    """Verifica si el texto contiene patrones de calificaciones"""
    print("\n=== VERIFICANDO PATRONES DE CALIFICACIONES ===")
    
    # Patrón 1: Encabezado de tabla de calificaciones con MATERIAS
    pattern = r"MATERIAS\s+I\s+II\s+III\s+Promedio"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        print(f"Patrón encontrado: {pattern}")
        print(f"Contexto: {text[max(0, match.start()-20):min(len(text), match.end()+20)]}")
    else:
        print(f"Patrón NO encontrado: {pattern}")
    
    # Patrón 2: Encabezado de tabla de calificaciones con ASIGNATURA
    pattern = r"ASIGNATURA\s+P1\s+P2\s+P3\s+Promedio"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        print(f"Patrón encontrado: {pattern}")
        print(f"Contexto: {text[max(0, match.start()-20):min(len(text), match.end()+20)]}")
    else:
        print(f"Patrón NO encontrado: {pattern}")
    
    # Patrón 3: Buscar palabras clave específicas de materias seguidas de números
    materias_clave = [
        r"LENGUAJES\s+\d",
        r"SABERES Y PENSAMIENTOS\s+\d",
        r"ETICA, NATURALEZA\s+\d",
        r"DE LO HUMANO Y LO COMUNITARIO\s+\d",
        r"FORMACION CIVICA\s+\d"
    ]
    
    for pattern in materias_clave:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            print(f"Patrón encontrado: {pattern}")
            print(f"Contexto: {text[max(0, match.start()-20):min(len(text), match.end()+20)]}")
        else:
            print(f"Patrón NO encontrado: {pattern}")
    
    # Verificar si hay una sección que contiene múltiples números que podrían ser calificaciones
    pattern = r"(\d(\.\d)?)\s+(\d(\.\d)?)\s+(\d(\.\d)?)\s+(\d(\.\d)?)"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        print(f"Patrón encontrado: {pattern}")
        print(f"Contexto: {text[max(0, match.start()-20):min(len(text), match.end()+20)]}")
    else:
        print(f"Patrón NO encontrado: {pattern}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_pdf.py <archivo_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    print(f"Analizando PDF: {pdf_path}")
    
    text = extract_text_from_pdf(pdf_path)
    print("\n=== TEXTO EXTRAÍDO DEL PDF ===")
    print(text)
    
    check_for_calificaciones(text)
