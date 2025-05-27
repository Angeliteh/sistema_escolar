#!/usr/bin/env python3
"""
Script para verificar alumnos existentes y crear 10 más similares
Analiza los datos actuales y genera alumnos coherentes
"""

import sqlite3
import json
import random
from datetime import datetime, timedelta
from app.core.config import Config
from app.core.service_provider import ServiceProvider

class AlumnoAnalyzer:
    """Analizador y generador de alumnos basado en datos existentes"""

    def __init__(self):
        self.db_path = Config.DB_PATH
        self.service_provider = ServiceProvider.get_instance()
        self.alumno_service = self.service_provider.alumno_service

        # Nombres mexicanos comunes para generar variaciones
        self.nombres_masculinos = [
            "JUAN", "LUIS", "CARLOS", "MIGUEL", "JOSÉ", "FRANCISCO",
            "ALEJANDRO", "DANIEL", "RICARDO", "FERNANDO", "EDUARDO",
            "ROBERTO", "ANTONIO", "JAVIER", "DIEGO", "PABLO", "PEDRO",
            "MANUEL", "RAFAEL", "SERGIO", "MARIO", "ALBERTO", "ANDRÉS"
        ]

        self.nombres_femeninos = [
            "MARÍA", "ANA", "LAURA", "CARMEN", "GABRIELA", "PATRICIA",
            "CLAUDIA", "DIANA", "MÓNICA", "VERÓNICA", "ADRIANA", "SILVIA",
            "ELENA", "SOFÍA", "ROSA", "BEATRIZ", "TERESA", "LUCÍA",
            "CRISTINA", "ALEJANDRA", "VALERIA", "NATALIA", "ISABELLA"
        ]

        self.apellidos_paternos = [
            "GARCÍA", "MARTÍNEZ", "RODRÍGUEZ", "GONZÁLEZ", "LÓPEZ",
            "HERNÁNDEZ", "PÉREZ", "SÁNCHEZ", "RAMÍREZ", "FLORES",
            "GÓMEZ", "DÍAZ", "CRUZ", "MORALES", "JIMÉNEZ", "RUIZ",
            "GUTIÉRREZ", "VARGAS", "CASTILLO", "ORTIZ", "MENDOZA",
            "TORRES", "RAMOS", "AGUILAR", "MORENO", "VÁZQUEZ"
        ]

        self.apellidos_maternos = [
            "LÓPEZ", "HERNÁNDEZ", "PÉREZ", "SÁNCHEZ", "RAMÍREZ",
            "FLORES", "GÓMEZ", "DÍAZ", "MORALES", "JIMÉNEZ", "RUIZ",
            "GUTIÉRREZ", "VARGAS", "CASTILLO", "ORTIZ", "MENDOZA",
            "TORRES", "RAMOS", "AGUILAR", "MORENO", "VÁZQUEZ", "SILVA",
            "CASTRO", "ROMERO", "HERRERA", "MEDINA", "GUERRERO"
        ]

    def conectar_db(self):
        """Conecta directamente a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def verificar_alumnos_existentes(self):
        """Verifica qué alumnos están registrados actualmente"""
        print("🔍 Verificando alumnos existentes en la base de datos...")
        print("=" * 60)

        try:
            conn = self.conectar_db()
            cursor = conn.cursor()

            # Consultar alumnos con sus datos escolares
            cursor.execute("""
            SELECT a.id, a.nombre, a.curp, a.matricula, a.fecha_nacimiento,
                   de.ciclo_escolar, de.grado, de.grupo, de.turno, de.escuela,
                   de.calificaciones
            FROM alumnos a
            LEFT JOIN datos_escolares de ON a.id = de.alumno_id
            ORDER BY a.nombre
            """)

            alumnos = cursor.fetchall()

            if not alumnos:
                print("❌ No hay alumnos registrados en la base de datos.")
                return []

            print(f"✅ Encontrados {len(alumnos)} alumnos registrados:")
            print()

            alumnos_data = []
            for i, alumno in enumerate(alumnos, 1):
                # Procesar calificaciones
                calificaciones = []
                if alumno['calificaciones']:
                    try:
                        calificaciones = json.loads(alumno['calificaciones'])
                    except:
                        calificaciones = []

                alumno_dict = {
                    'id': alumno['id'],
                    'nombre': alumno['nombre'],
                    'curp': alumno['curp'],
                    'matricula': alumno['matricula'],
                    'fecha_nacimiento': alumno['fecha_nacimiento'],
                    'ciclo_escolar': alumno['ciclo_escolar'],
                    'grado': alumno['grado'],
                    'grupo': alumno['grupo'],
                    'turno': alumno['turno'],
                    'escuela': alumno['escuela'],
                    'calificaciones': calificaciones
                }

                alumnos_data.append(alumno_dict)

                # Mostrar información del alumno
                print(f"{i}. {alumno['nombre']}")
                print(f"   📋 CURP: {alumno['curp']}")
                print(f"   🎓 Grado: {alumno['grado']}° {alumno['grupo']} - {alumno['turno']}")
                print(f"   🏫 Escuela: {alumno['escuela'] or 'No especificada'}")
                print(f"   📊 Calificaciones: {len(calificaciones)} materias")
                print(f"   🆔 ID: {alumno['id']}")
                print()

            conn.close()
            return alumnos_data

        except Exception as e:
            print(f"❌ Error al verificar alumnos: {str(e)}")
            return []

    def analizar_patrones(self, alumnos_existentes):
        """Analiza patrones en los alumnos existentes"""
        if not alumnos_existentes:
            return {
                'ciclo_escolar': '2023-2024',
                'escuela': 'ESCUELA PRIMARIA BENITO JUÁREZ',
                'grados_comunes': [1, 2, 3],
                'grupos_comunes': ['A', 'B'],
                'turnos_comunes': ['MATUTINO', 'VESPERTINO'],
                'tiene_calificaciones': True
            }

        # Extraer patrones
        ciclos = [a['ciclo_escolar'] for a in alumnos_existentes if a['ciclo_escolar']]
        escuelas = [a['escuela'] for a in alumnos_existentes if a['escuela']]
        grados = [a['grado'] for a in alumnos_existentes if a['grado']]
        grupos = [a['grupo'] for a in alumnos_existentes if a['grupo']]
        turnos = [a['turno'] for a in alumnos_existentes if a['turno']]

        # Determinar valores más comunes
        ciclo_comun = max(set(ciclos), key=ciclos.count) if ciclos else '2023-2024'
        escuela_comun = max(set(escuelas), key=escuelas.count) if escuelas else 'ESCUELA PRIMARIA BENITO JUÁREZ'

        return {
            'ciclo_escolar': ciclo_comun,
            'escuela': escuela_comun,
            'grados_comunes': list(set(grados)) if grados else [1, 2, 3, 4, 5, 6],
            'grupos_comunes': list(set(grupos)) if grupos else ['A', 'B', 'C'],
            'turnos_comunes': list(set(turnos)) if turnos else ['MATUTINO', 'VESPERTINO'],
            'tiene_calificaciones': any(len(a['calificaciones']) > 0 for a in alumnos_existentes)
        }

    def generar_curp_realista(self, nombre_completo, fecha_nacimiento, sexo):
        """Genera una CURP realista con formato válido"""
        # Limpiar y separar el nombre
        partes = nombre_completo.replace("Ñ", "X").replace("ñ", "x").split()

        # Extraer apellidos y nombre
        if len(partes) >= 3:
            nombre = partes[0]
            apellido1 = partes[1]
            apellido2 = partes[2]
        elif len(partes) == 2:
            nombre = partes[0]
            apellido1 = partes[1]
            apellido2 = "XXXX"
        else:
            nombre = partes[0] if partes else "XXXX"
            apellido1 = "XXXX"
            apellido2 = "XXXX"

        # Función para obtener primera vocal interna
        def primera_vocal_interna(palabra):
            vocales = "AEIOU"
            for i, char in enumerate(palabra[1:], 1):
                if char in vocales:
                    return char
            return "X"

        # Función para obtener primera consonante interna
        def primera_consonante_interna(palabra):
            consonantes = "BCDFGHJKLMNPQRSTVWXYZ"
            for i, char in enumerate(palabra[1:], 1):
                if char in consonantes:
                    return char
            return "X"

        # Construir CURP paso a paso
        curp = ""

        # 1. Primera letra del primer apellido
        curp += apellido1[0] if apellido1 else "X"

        # 2. Primera vocal interna del primer apellido
        curp += primera_vocal_interna(apellido1) if len(apellido1) > 1 else "X"

        # 3. Primera letra del segundo apellido
        curp += apellido2[0] if apellido2 else "X"

        # 4. Primera letra del nombre
        curp += nombre[0] if nombre else "X"

        # 5. Fecha de nacimiento (AAMMDD)
        curp += fecha_nacimiento.strftime("%y%m%d")

        # 6. Sexo
        curp += sexo

        # 7. Entidad federativa (DF para CDMX)
        curp += "DF"

        # 8. Primera consonante interna del primer apellido
        curp += primera_consonante_interna(apellido1) if len(apellido1) > 1 else "X"

        # 9. Primera consonante interna del segundo apellido
        curp += primera_consonante_interna(apellido2) if len(apellido2) > 1 else "X"

        # 10. Primera consonante interna del nombre
        curp += primera_consonante_interna(nombre) if len(nombre) > 1 else "X"

        # 11. Dígito verificador (2 dígitos)
        curp += f"{random.randint(0, 9)}{random.randint(0, 9)}"

        return curp.upper()[:18]

    def generar_calificaciones(self, grado):
        """Genera calificaciones realistas según el grado en el formato correcto"""
        materias_por_grado = {
            1: ["ESPANOL", "MATEMATICAS", "CONOCIMIENTO DEL MEDIO", "EDUCACION FISICA"],
            2: ["ESPANOL", "MATEMATICAS", "CONOCIMIENTO DEL MEDIO", "EDUCACION FISICA", "EDUCACION ARTISTICA"],
            3: ["ESPANOL", "MATEMATICAS", "CIENCIAS NATURALES", "HISTORIA", "GEOGRAFIA", "EDUCACION FISICA"],
            4: ["ESPANOL", "MATEMATICAS", "CIENCIAS NATURALES", "HISTORIA", "GEOGRAFIA", "FORMACION CIVICA Y ETICA", "EDUCACION FISICA"],
            5: ["ESPANOL", "MATEMATICAS", "CIENCIAS NATURALES", "HISTORIA", "GEOGRAFIA", "FORMACION CIVICA Y ETICA", "EDUCACION FISICA", "INGLES"],
            6: ["ESPANOL", "MATEMATICAS", "CIENCIAS NATURALES", "HISTORIA", "GEOGRAFIA", "FORMACION CIVICA Y ETICA", "EDUCACION FISICA", "INGLES", "EDUCACION ARTISTICA"]
        }

        materias = materias_por_grado.get(grado, materias_por_grado[3])
        calificaciones = []

        for materia in materias:
            # Generar calificaciones por periodo (6-10, con tendencia a 8-9)
            p1 = random.choices([6, 7, 8, 9, 10], weights=[5, 15, 35, 35, 10])[0]
            p2 = random.choices([6, 7, 8, 9, 10], weights=[5, 15, 35, 35, 10])[0]
            p3 = random.choices([6, 7, 8, 9, 10], weights=[5, 15, 35, 35, 10])[0]

            # Calcular promedio
            promedio = round((p1 + p2 + p3) / 3, 1)

            # Formato correcto que espera la interfaz
            calificaciones.append({
                "nombre": materia,
                "i": p1,
                "ii": p2,
                "iii": p3,
                "promedio": promedio
            })

        return calificaciones

    def crear_alumnos_similares(self, patrones, cantidad=10):
        """Crea alumnos similares a los existentes"""
        print(f"🎯 Generando {cantidad} alumnos similares...")
        print("=" * 40)

        alumnos_nuevos = []

        for i in range(cantidad):
            # Determinar sexo y nombre
            sexo = random.choice(["H", "M"])
            if sexo == "H":
                nombre = random.choice(self.nombres_masculinos)
            else:
                nombre = random.choice(self.nombres_femeninos)

            # Generar apellidos por separado
            apellido_paterno = random.choice(self.apellidos_paternos)
            apellido_materno = random.choice(self.apellidos_maternos)
            nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"

            # Datos escolares basados en patrones
            grado = random.choice(patrones['grados_comunes'])
            grupo = random.choice(patrones['grupos_comunes'])
            turno = random.choice(patrones['turnos_comunes'])

            # Fecha de nacimiento coherente con el grado
            edad_base = 6 + grado - 1
            fecha_base = datetime.now() - timedelta(days=365 * edad_base)
            fecha_nacimiento = fecha_base + timedelta(days=random.randint(-120, 120))

            # CURP
            curp = self.generar_curp_realista(nombre_completo, fecha_nacimiento, sexo)

            # Matrícula
            matricula = f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}"

            # Calificaciones (70% tienen calificaciones)
            calificaciones = []
            if random.random() < 0.7:
                calificaciones = self.generar_calificaciones(grado)

            alumno = {
                "nombre": nombre_completo,
                "curp": curp,
                "matricula": matricula,
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "ciclo_escolar": patrones['ciclo_escolar'],
                "escuela": patrones['escuela'],
                "calificaciones": calificaciones
            }

            alumnos_nuevos.append(alumno)

            # Mostrar información
            cal_info = f"({len(calificaciones)} materias)" if calificaciones else "(sin calificaciones)"
            print(f"{i+1:2d}. {nombre_completo}")
            print(f"    🎓 {grado}° {grupo} {turno} {cal_info}")

        return alumnos_nuevos

    def crear_alumnos_realistas(self, patrones, cantidad=50):
        """Crea alumnos realistas con variaciones para probar coincidencias y casos similares"""
        print(f"👥 Generando {cantidad} alumnos realistas con MUCHA VARIEDAD...")
        print("📋 Incluye variaciones estratégicas:")
        print("   • Nombres: 20% similares para testing, 80% muy variados")
        print("   • Apellidos: 30% comunes, 40% menos comunes, 30% únicos")
        print("   • Grados: Distribución equilibrada 1° a 6°")
        print("   • Grupos: A (50%), B (33%), C (17%)")
        print("   • Turnos: Matutino (60%), Vespertino (40%)")
        print("   • Calificaciones: 60% completas, 20% parciales, 20% nuevos")
        print("   • Matrículas: 80% tienen, 3 formatos diferentes")
        print()

        alumnos_nuevos = []

        # Crear algunos nombres intencionalmente similares para testing
        nombres_similares = [
            # Grupo Juan/Juana
            ("JUAN", "H"), ("JUANA", "M"), ("JUAN CARLOS", "H"), ("JUAN PABLO", "H"),
            # Grupo María/Mario
            ("MARÍA", "M"), ("MARIO", "H"), ("MARÍA JOSÉ", "M"), ("MARÍA ELENA", "M"),
            # Grupo Ana/Antonio
            ("ANA", "M"), ("ANTONIO", "H"), ("ANA SOFÍA", "M"), ("ANA LAURA", "M"),
            # Grupo Luis/Luisa
            ("LUIS", "H"), ("LUISA", "M"), ("LUIS MIGUEL", "H"), ("LUIS FERNANDO", "H")
        ]

        for i in range(cantidad):
            # Determinar sexo primero
            sexo = random.choice(["H", "M"])

            # 20% de probabilidad de usar nombres similares para testing (menos repetitivo)
            if i < len(nombres_similares) and random.random() < 0.20:
                nombre_base, sexo_similar = nombres_similares[i % len(nombres_similares)]
                nombre = nombre_base
                sexo = sexo_similar  # Usar el sexo correcto para el nombre
            else:
                # Nombres variados con más opciones
                if sexo == "H":
                    # Agregar más nombres masculinos variados
                    nombres_extra_m = ["DIEGO", "SEBASTIÁN", "MATEO", "SANTIAGO", "NICOLÁS", "SAMUEL", "BENJAMÍN", "LEONARDO", "GABRIEL", "ADRIÁN"]
                    todos_nombres_m = self.nombres_masculinos + nombres_extra_m
                    nombre = random.choice(todos_nombres_m)
                else:
                    # Agregar más nombres femeninos variados
                    nombres_extra_f = ["VALENTINA", "CAMILA", "ISABELLA", "SOPHIA", "REGINA", "FERNANDA", "XIMENA", "NATALIA", "PAULINA", "ANDREA"]
                    todos_nombres_f = self.nombres_femeninos + nombres_extra_f
                    nombre = random.choice(todos_nombres_f)

            # Apellidos con MÁS VARIEDAD
            apellidos_comunes = ["GARCÍA", "LÓPEZ", "MARTÍNEZ", "GONZÁLEZ", "PÉREZ", "RODRÍGUEZ", "SÁNCHEZ", "RAMÍREZ", "TORRES", "FLORES"]
            apellidos_menos_comunes = ["MORALES", "JIMÉNEZ", "RUIZ", "HERNÁNDEZ", "DÍAZ", "MORENO", "MUÑOZ", "ÁLVAREZ", "ROMERO", "GUTIÉRREZ"]

            # 30% apellidos muy comunes, 40% comunes, 30% menos comunes
            rand_apellido = random.random()
            if rand_apellido < 0.30:
                apellido_paterno = random.choice(apellidos_comunes)
                apellido_materno = random.choice(apellidos_comunes)
            elif rand_apellido < 0.70:
                apellido_paterno = random.choice(apellidos_menos_comunes)
                apellido_materno = random.choice(apellidos_comunes)
            else:
                apellido_paterno = random.choice(self.apellidos_paternos)
                apellido_materno = random.choice(self.apellidos_maternos)

            nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"

            # Datos escolares con MUCHA VARIEDAD
            # Distribución más realista de grados (no solo grados bajos)
            grados_variados = [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]  # Más variedad
            grado = random.choice(grados_variados)

            # Grupos variados (A, B, C con diferentes probabilidades)
            grupos_variados = ["A", "A", "A", "B", "B", "C"]  # Más A, menos C
            grupo = random.choice(grupos_variados)

            # Turnos variados (60% matutino, 40% vespertino)
            turnos_variados = ["MATUTINO", "MATUTINO", "MATUTINO", "VESPERTINO", "VESPERTINO"]
            turno = random.choice(turnos_variados)

            # Fecha de nacimiento con MÁS VARIEDAD
            edad_base = 6 + grado - 1
            fecha_base = datetime.now() - timedelta(days=365 * edad_base)
            # Variación de hasta 6 meses (más realista)
            fecha_nacimiento = fecha_base + timedelta(days=random.randint(-180, 180))

            # CURP
            curp = self.generar_curp_realista(nombre_completo, fecha_nacimiento, sexo)

            # Matrícula con VARIEDAD (80% la tienen, formatos variados)
            matricula = ""
            if random.random() < 0.80:  # 80% tienen matrícula
                # Diferentes formatos de matrícula para variedad
                formato = random.choice([1, 2, 3])
                if formato == 1:
                    matricula = f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}"
                elif formato == 2:
                    matricula = f"ALU{random.randint(10000, 99999)}"
                else:
                    matricula = f"{grado}{grupo}{random.randint(1000, 9999)}"

            # Calificaciones con VARIEDAD (60% completas, 20% parciales, 20% sin calificaciones)
            calificaciones = []
            tipo_alumno = "nuevo"
            rand_cal = random.random()

            if rand_cal < 0.60:  # 60% calificaciones completas
                calificaciones = self.generar_calificaciones(grado)
                tipo_alumno = "completo"
            elif rand_cal < 0.80:  # 20% calificaciones parciales
                calificaciones_completas = self.generar_calificaciones(grado)
                # Solo algunas materias
                num_materias = random.randint(2, len(calificaciones_completas))
                calificaciones = random.sample(calificaciones_completas, num_materias)
                tipo_alumno = "parcial"
            # 20% sin calificaciones (nuevo)

            # Crear alumno
            alumno = {
                "nombre": nombre_completo,
                "curp": curp,
                "matricula": matricula,
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "ciclo_escolar": patrones['ciclo_escolar'],
                "escuela": patrones['escuela'],
                "calificaciones": calificaciones
            }

            alumnos_nuevos.append(alumno)

            # Mostrar progreso cada 25 alumnos
            if (i + 1) % 25 == 0 or i == cantidad - 1:
                cal_info = f"({len(calificaciones)} materias)" if calificaciones else "(sin calificaciones)"
                print(f"{i+1:3d}. {nombre_completo}")
                print(f"     🎓 {grado}° {grupo} {turno} {cal_info} [{tipo_alumno}]")

        return alumnos_nuevos

    def crear_alumnos_diversos_testing(self, patrones, cantidad=25):
        """Crea alumnos con datos diversos para testing riguroso del sistema de IA"""
        print(f"🧪 Generando {cantidad} alumnos con datos diversos para testing...")
        print("=" * 50)

        alumnos_generados = []

        # Definir escenarios de testing con pesos
        escenarios = [
            {"tipo": "completo", "peso": 30, "desc": "Datos completos con calificaciones"},
            {"tipo": "sin_calificaciones", "peso": 25, "desc": "Sin calificaciones"},
            {"tipo": "sin_matricula", "peso": 15, "desc": "Sin matrícula"},
            {"tipo": "datos_minimos", "peso": 10, "desc": "Solo CURP y nombre"},
            {"tipo": "fecha_incompleta", "peso": 8, "desc": "Fecha de nacimiento incompleta"},
            {"tipo": "datos_inconsistentes", "peso": 7, "desc": "Datos inconsistentes (edad vs grado)"},
            {"tipo": "calificaciones_parciales", "peso": 5, "desc": "Calificaciones incompletas"}
        ]

        print("📊 Distribución de escenarios:")
        for escenario in escenarios:
            cantidad_estimada = int(cantidad * escenario["peso"] / 100)
            print(f"   • {escenario['desc']}: ~{cantidad_estimada} alumnos")
        print()

        for i in range(cantidad):
            # Seleccionar escenario basado en pesos
            escenario = random.choices(
                escenarios,
                weights=[e["peso"] for e in escenarios]
            )[0]

            # Seleccionar sexo y nombre
            sexo = random.choice(["H", "M"])
            if sexo == "H":
                nombre = random.choice(self.nombres_masculinos)
            else:
                nombre = random.choice(self.nombres_femeninos)

            # Generar apellidos por separado
            apellido_paterno = random.choice(self.apellidos_paternos)
            apellido_materno = random.choice(self.apellidos_maternos)
            nombre_completo = f"{nombre} {apellido_paterno} {apellido_materno}"

            # Datos escolares basados en patrones
            grado = random.choice(patrones['grados_comunes'])
            grupo = random.choice(patrones['grupos_comunes'])
            turno = random.choice(patrones['turnos_comunes'])

            # Fecha de nacimiento coherente con el grado
            edad_base = 6 + grado - 1
            fecha_base = datetime.now() - timedelta(days=365 * edad_base)
            fecha_nacimiento = fecha_base + timedelta(days=random.randint(-120, 120))

            # CURP (siempre presente - es obligatorio)
            curp = self.generar_curp_realista(nombre_completo, fecha_nacimiento, sexo)

            # Aplicar escenario específico
            alumno = self._aplicar_escenario_testing(
                escenario, nombre_completo, curp, fecha_nacimiento,
                grado, grupo, turno, patrones
            )

            alumnos_generados.append(alumno)
            print(f"{i+1:2d}. {nombre_completo}")
            print(f"    🎯 {grado}° {grupo} {turno} - [{escenario['desc']}]")

        return alumnos_generados

    def _aplicar_escenario_testing(self, escenario, nombre_completo, curp, fecha_nacimiento,
                                   grado, grupo, turno, patrones):
        """Aplica un escenario específico de testing"""

        alumno_base = {
            "nombre": nombre_completo,
            "curp": curp,
            "ciclo_escolar": patrones['ciclo_escolar'],
            "escuela": patrones['escuela']
        }

        if escenario["tipo"] == "completo":
            # Alumno con todos los datos
            alumno_base.update({
                "matricula": f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}",
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "calificaciones": self.generar_calificaciones(grado)
            })

        elif escenario["tipo"] == "sin_calificaciones":
            # Alumno sin calificaciones
            alumno_base.update({
                "matricula": f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}",
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "calificaciones": []
            })

        elif escenario["tipo"] == "sin_matricula":
            # Alumno sin matrícula
            alumno_base.update({
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "calificaciones": self.generar_calificaciones(grado) if random.random() < 0.6 else []
            })

        elif escenario["tipo"] == "datos_minimos":
            # Solo CURP y nombre (datos mínimos obligatorios)
            # Ocasionalmente agregar algunos datos escolares
            if random.random() < 0.3:
                alumno_base.update({
                    "grado": grado,
                    "grupo": grupo,
                    "turno": turno
                })

        elif escenario["tipo"] == "fecha_incompleta":
            # Fecha de nacimiento en formato diferente o incompleta
            formatos_fecha = [
                fecha_nacimiento.strftime("%d/%m/%Y"),
                fecha_nacimiento.strftime("%d DE %B DEL %Y").upper(),
                str(fecha_nacimiento.year),  # Solo año
                "",  # Fecha vacía
                "2018-06-20"  # Fecha fija para testing
            ]
            alumno_base.update({
                "matricula": f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}",
                "fecha_nacimiento": random.choice(formatos_fecha),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "calificaciones": []
            })

        elif escenario["tipo"] == "datos_inconsistentes":
            # Datos que no coinciden (edad vs grado)
            edad_incorrecta = random.choice([4, 5, 12, 13])  # Muy joven o muy mayor
            fecha_incorrecta = datetime.now() - timedelta(days=365 * edad_incorrecta)

            alumno_base.update({
                "matricula": f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}",
                "fecha_nacimiento": fecha_incorrecta.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "calificaciones": []
            })

        elif escenario["tipo"] == "calificaciones_parciales":
            # Calificaciones incompletas (solo algunas materias)
            calificaciones_completas = self.generar_calificaciones(grado)
            # Tomar solo 2-4 materias al azar
            num_materias = random.randint(2, min(4, len(calificaciones_completas)))
            calificaciones_parciales = random.sample(calificaciones_completas, num_materias)

            alumno_base.update({
                "matricula": f"{patrones['ciclo_escolar'][:4]}{grado:02d}{grupo}{random.randint(100, 999)}",
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": grado,
                "grupo": grupo,
                "turno": turno,
                "calificaciones": calificaciones_parciales
            })

        return alumno_base

    def registrar_alumnos(self, alumnos):
        """Registra los alumnos en la base de datos"""
        print(f"\n📝 Registrando {len(alumnos)} alumnos en la base de datos...")

        registrados = 0
        errores = 0

        for alumno in alumnos:
            try:
                success, message, _ = self.alumno_service.registrar_alumno(alumno)

                if success:
                    registrados += 1
                    print(f"✅ {alumno['nombre']}")
                else:
                    errores += 1
                    print(f"❌ {alumno['nombre']}: {message}")

            except Exception as e:
                errores += 1
                print(f"❌ {alumno['nombre']}: {str(e)}")

        print(f"\n📊 Resultado del registro:")
        print(f"   ✅ Registrados exitosamente: {registrados}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📝 Total procesados: {len(alumnos)}")

        return registrados, errores

    def crear_datos_prueba_sql(self):
        """Crea datos específicos para probar consultas SQL"""
        print("🧪 Creando datos específicos para pruebas SQL...")

        # Datos específicos para pruebas
        alumnos_prueba = [
            {
                "nombre": "JUAN PÉREZ GARCÍA",
                "sexo": "H",
                "grado": 1,
                "grupo": "A",
                "turno": "MATUTINO"
            },
            {
                "nombre": "JUAN LÓPEZ MARTÍNEZ",
                "sexo": "H",
                "grado": 2,
                "grupo": "B",
                "turno": "MATUTINO"
            },
            {
                "nombre": "JUAN GONZÁLEZ HERNÁNDEZ",
                "sexo": "H",
                "grado": 3,
                "grupo": "C",
                "turno": "VESPERTINO"
            },
            {
                "nombre": "MARÍA RODRÍGUEZ FLORES",
                "sexo": "M",
                "grado": 1,
                "grupo": "A",
                "turno": "MATUTINO"
            },
            {
                "nombre": "MARÍA SÁNCHEZ GÓMEZ",
                "sexo": "M",
                "grado": 2,
                "grupo": "B",
                "turno": "VESPERTINO"
            },
            {
                "nombre": "ANA DÍAZ RUIZ",
                "sexo": "M",
                "grado": 3,
                "grupo": "A",
                "turno": "MATUTINO"
            }
        ]

        alumnos_generados = []

        for datos in alumnos_prueba:
            # Fecha de nacimiento coherente
            edad_base = 6 + datos['grado'] - 1
            fecha_base = datetime.now() - timedelta(days=365 * edad_base)
            fecha_nacimiento = fecha_base + timedelta(days=random.randint(-60, 60))

            # CURP
            curp = self.generar_curp_realista(datos['nombre'], fecha_nacimiento, datos['sexo'])

            # Matrícula
            matricula = f"2024{datos['grado']:02d}{datos['grupo']}{random.randint(100, 999)}"

            # Calificaciones
            calificaciones = self.generar_calificaciones(datos['grado'])

            alumno = {
                "nombre": datos['nombre'],
                "curp": curp,
                "matricula": matricula,
                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                "grado": datos['grado'],
                "grupo": datos['grupo'],
                "turno": datos['turno'],
                "ciclo_escolar": "2024-2025",
                "escuela": "PROF. MAXIMO GAMIZ FERNANDEZ",
                "calificaciones": calificaciones
            }

            alumnos_generados.append(alumno)
            print(f"   ✅ {datos['nombre']} - {datos['grado']}° {datos['grupo']} {datos['turno']}")

        return alumnos_generados

def main():
    """Función principal"""
    print("🎯 Verificador y Generador de Alumnos")
    print("=" * 50)

    analyzer = AlumnoAnalyzer()

    # Verificar alumnos existentes
    alumnos_existentes = analyzer.verificar_alumnos_existentes()

    if alumnos_existentes:
        print(f"📊 Resumen actual: {len(alumnos_existentes)} alumnos registrados")
    else:
        print("📊 Base de datos vacía - se usarán valores por defecto")

    # Analizar patrones
    patrones = analyzer.analizar_patrones(alumnos_existentes)
    print(f"\n🔍 Patrones detectados:")
    print(f"   📅 Ciclo escolar: {patrones['ciclo_escolar']}")
    print(f"   🏫 Escuela: {patrones['escuela']}")
    print(f"   🎓 Grados: {patrones['grados_comunes']}")
    print(f"   📚 Grupos: {patrones['grupos_comunes']}")
    print(f"   ⏰ Turnos: {patrones['turnos_comunes']}")

    # Solicitar cantidad de alumnos
    print(f"\n" + "=" * 50)
    try:
        cantidad = int(input("¿Cuántos alumnos quieres generar? (recomendado: 50-300): ") or "50")
        cantidad = max(1, min(cantidad, 500))  # Entre 1 y 500
    except ValueError:
        cantidad = 50

    # Generar alumnos realistas
    print(f"\n👥 Generando {cantidad} alumnos realistas...")
    print("📋 Incluye: datos completos, casos comunes, variaciones estratégicas")
    alumnos_nuevos = analyzer.crear_alumnos_realistas(patrones, cantidad)

    # Preguntar si registrar
    cantidad_texto = len(alumnos_nuevos)
    respuesta = input(f"\n¿Registrar estos {cantidad_texto} alumnos en la base de datos? (s/n): ")

    if respuesta.lower() in ['s', 'sí', 'si', 'y', 'yes']:
        registrados, _ = analyzer.registrar_alumnos(alumnos_nuevos)

        if registrados > 0:
            total_final = len(alumnos_existentes) + registrados
            print(f"\n🎉 ¡Proceso completado!")
            print(f"   📊 Total de alumnos en la base de datos: {total_final}")
            print(f"\n🧪 Ahora puedes probar en el Asistente de IA:")
            print(f"   📊 CONSULTAS BÁSICAS:")
            print(f"   • 'alumnos de 3er grado'")
            print(f"   • 'estudiantes del grupo A'")
            print(f"   • 'alumnos del turno matutino'")
            print(f"   📝 CONSULTAS CONVERSACIONALES:")
            print(f"   • 'me ayudas a encontrar alumnos de primer grado'")
            print(f"   • 'quiero ver estudiantes del turno de la mañana'")
            print(f"   • 'muéstrame todos los de segundo año'")
            print(f"   🔍 BÚSQUEDAS POR NOMBRE:")
            print(f"   • 'buscar a Juan' (múltiples coincidencias)")
            print(f"   • 'detalles de [nombre completo]'")
            print(f"   🎯 CONSULTAS AVANZADAS:")
            print(f"   • 'cuántos alumnos hay en total'")
            print(f"   • 'alumnos de 3er grado del turno matutino'")
    else:
        print(f"\n📝 Alumnos generados pero no registrados.")

if __name__ == "__main__":
    main()
