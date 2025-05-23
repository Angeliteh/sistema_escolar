"""
Script para pruebas interactivas del sistema de IA para constancias escolares.
Este script permite seleccionar qué escenarios probar y ejecutarlos de forma individual o en grupo.
"""
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from app.core.ai.command_executor import CommandExecutor
from app.core.utils import open_file_with_default_app

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class PruebasInteractivas:
    """Clase para realizar pruebas interactivas del sistema de IA"""

    def __init__(self):
        """Inicializa el entorno de pruebas"""
        self.setup_gemini()
        self.command_executor = CommandExecutor()
        self.resultados = {
            "total": 0,
            "exitosos": 0,
            "fallidos": 0,
            "detalles": []
        }

        # Definir escenarios de prueba agrupados
        self.grupos_escenarios = {
            "1": {
                "nombre": "Escenarios Básicos",
                "descripcion": "Pruebas básicas de registro, búsqueda y generación",
                "escenarios": {
                    "1.1": {
                        "nombre": "Registro de alumno con datos completos",
                        "comando": "Registra a Ana García con CURP GARA010101MDFXXX01 en 1° grado grupo A turno matutino"
                    },
                    "1.2": {
                        "nombre": "Registro de alumno con datos mínimos",
                        "comando": "Registra a Carlos López con CURP LOPC020202HDFXXX02"
                    },
                    "1.3": {
                        "nombre": "Búsqueda de alumno por nombre completo",
                        "comando": "Busca al alumno Ana García"
                    },
                    "1.4": {
                        "nombre": "Generación de constancia de estudios",
                        "comando": "Genera una constancia de estudios para Ana García"
                    },
                    "1.5": {
                        "nombre": "Listado de constancias",
                        "comando": "Muestra las constancias de Ana García"
                    }
                }
            },
            "2": {
                "nombre": "Validación de Datos",
                "descripcion": "Pruebas de validación de datos y manejo de errores",
                "escenarios": {
                    "2.1": {
                        "nombre": "Validación de calificaciones",
                        "comando": "Genera una constancia de calificaciones para Carlos López"
                    },
                    "2.2": {
                        "nombre": "Validación de CURP inválida",
                        "comando": "Registra a Juan Pérez con CURP INVALIDA123"
                    },
                    "2.3": {
                        "nombre": "Datos incompletos",
                        "comando": "Registra a María sin CURP"
                    },
                    "2.4": {
                        "nombre": "Validación de constancia de traslado",
                        "comando": "Genera una constancia de traslado para Carlos López"
                    }
                }
            },
            "3": {
                "nombre": "Búsqueda Avanzada",
                "descripcion": "Pruebas de búsqueda con diferentes criterios",
                "escenarios": {
                    "3.1": {
                        "nombre": "Búsqueda por apellido (parcial)",
                        "comando": "Busca alumnos con apellido García"
                    },
                    "3.2": {
                        "nombre": "Búsqueda por CURP",
                        "comando": "Busca al alumno con CURP GARA010101MDFXXX01"
                    },
                    "3.3": {
                        "nombre": "Búsqueda con nombre parcial corto",
                        "comando": "Busca alumnos con nombre A"
                    },
                    "3.4": {
                        "nombre": "Búsqueda sin resultados",
                        "comando": "Busca al alumno Inexistente Totalmente"
                    }
                }
            },
            "4": {
                "nombre": "Actualización de Datos",
                "descripcion": "Pruebas de actualización de datos de alumnos",
                "escenarios": {
                    "4.1": {
                        "nombre": "Actualización de datos académicos",
                        "comando": "Actualiza los datos del alumno Carlos López, asigna grado 2, grupo B, turno vespertino"
                    },
                    "4.2": {
                        "nombre": "Actualización de datos por nombre",
                        "comando": "Actualiza los datos del alumno Ana García, cambia su grado a 2 y su grupo a B"
                    },
                    "4.3": {
                        "nombre": "Actualización de múltiples campos",
                        "comando": "Actualiza al alumno Ana García, cambia su grado a 3, grupo a C, turno a vespertino y matricula a AG2025"
                    }
                }
            },
            "5": {
                "nombre": "Eliminación de Datos",
                "descripcion": "Pruebas de eliminación de alumnos",
                "escenarios": {
                    "5.1": {
                        "nombre": "Eliminación de alumno por nombre",
                        "comando": "Elimina al alumno Carlos López"
                    },
                    "5.2": {
                        "nombre": "Eliminación de alumno inexistente",
                        "comando": "Elimina al alumno Inexistente Totalmente"
                    }
                }
            },
            "6": {
                "nombre": "Generación de Constancias",
                "descripcion": "Pruebas de generación de diferentes tipos de constancias",
                "escenarios": {
                    "6.1": {
                        "nombre": "Constancia de estudios con foto",
                        "comando": "Genera una constancia de estudios para Ana García con foto"
                    },
                    "6.2": {
                        "nombre": "Constancia de calificaciones",
                        "comando": "Genera una constancia de calificaciones para Ana García"
                    },
                    "6.3": {
                        "nombre": "Constancia de traslado",
                        "comando": "Genera una constancia de traslado para Ana García"
                    }
                }
            },
            "7": {
                "nombre": "Manejo de Errores",
                "descripcion": "Pruebas de manejo de errores y comandos ambiguos",
                "escenarios": {
                    "7.1": {
                        "nombre": "Comando ambiguo",
                        "comando": "Actualiza alumno"
                    },
                    "7.2": {
                        "nombre": "Comando con error tipográfico",
                        "comando": "Busca al alunmo Ana García"
                    },
                    "7.3": {
                        "nombre": "Comando complejo",
                        "comando": "Busca a Ana García y genera una constancia de estudios"
                    }
                }
            },
            "8": {
                "nombre": "Flujo Completo",
                "descripcion": "Pruebas de flujo completo de operaciones",
                "escenarios": {
                    "8.1": {
                        "nombre": "Registro de nuevo alumno",
                        "comando": "Registra a Pedro Sánchez con CURP SANP030303HDFXXX03 en 3° grado grupo C turno vespertino"
                    },
                    "8.2": {
                        "nombre": "Búsqueda del alumno registrado",
                        "comando": "Busca al alumno Pedro Sánchez"
                    },
                    "8.3": {
                        "nombre": "Actualización del alumno",
                        "comando": "Actualiza los datos del alumno Pedro Sánchez, cambia su grado a 4 y su grupo a D"
                    },
                    "8.4": {
                        "nombre": "Generación de constancia",
                        "comando": "Genera una constancia de estudios para Pedro Sánchez"
                    },
                    "8.5": {
                        "nombre": "Eliminación del alumno",
                        "comando": "Elimina al alumno Pedro Sánchez"
                    }
                }
            }
        }

        # Crear lista plana de escenarios para compatibilidad
        self.escenarios = {}

    def setup_gemini(self):
        """Configura la API de Gemini"""
        # Obtener la API key de las variables de entorno
        api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key or api_key == "tu-api-key-aquí":
            print("Error: No se encontró una API key válida de Gemini.")
            print("Configura la API key en el archivo .env antes de ejecutar las pruebas.")
            exit(1)

        # Configurar Gemini
        genai.configure(api_key=api_key)

        # Crear modelos con mecanismo de respaldo
        self.models = {
            "gemini-2.0-flash": None,  # Primera opción (principal)
            "gemini-1.5-flash": None   # Segunda opción (respaldo)
        }

        # Inicializar Gemini 2.0 Flash
        try:
            self.models["gemini-2.0-flash"] = genai.GenerativeModel('gemini-2.0-flash')
            print("Modelo Gemini 2.0 Flash inicializado correctamente.")
        except Exception as e:
            print(f"No se pudo inicializar Gemini 2.0 Flash: {str(e)}")

        # Inicializar Gemini 1.5 Flash
        try:
            self.models["gemini-1.5-flash"] = genai.GenerativeModel('gemini-1.5-flash')
            print("Modelo Gemini 1.5 Flash (respaldo) inicializado correctamente.")
        except Exception as e:
            print(f"No se pudo inicializar Gemini 1.5 Flash: {str(e)}")

        # Verificar que al menos un modelo esté disponible
        if not any(self.models.values()):
            print("Error: No se pudo inicializar ningún modelo de Gemini.")
            print("Verifica tu API key y la disponibilidad de los modelos.")
            exit(1)

    def create_prompt(self, user_text):
        """Crea un prompt para Gemini"""
        return f"""
        Eres un asistente especializado en un sistema de gestión de constancias escolares para una escuela primaria.

        El sistema permite:
        - Buscar alumnos por nombre o CURP
        - Registrar nuevos alumnos
        - Generar constancias (de estudio, calificaciones o traslado)
        - Transformar constancias existentes
        - Gestionar datos de alumnos

        El usuario te ha pedido: "{user_text}"

        Analiza lo que quiere hacer y responde ÚNICAMENTE con un JSON que siga este formato:

        {{
            "accion": "nombre_de_la_accion",
            "parametros": {{
                "param1": "valor1",
                "param2": "valor2"
            }}
        }}

        Acciones disponibles y sus parámetros:

        1. buscar_alumno
           - nombre: Nombre del alumno a buscar (puede ser nombre parcial)
           - curp: CURP del alumno (opcional)
           - busqueda_exacta: true para buscar coincidencias exactas, false para buscar coincidencias parciales (opcional, por defecto false)

        2. registrar_alumno
           - nombre: Nombre completo del alumno
           - curp: CURP del alumno
           - matricula: Matrícula escolar (opcional)
           - grado: Grado escolar (1-6)
           - grupo: Grupo (A-F)
           - turno: MATUTINO o VESPERTINO

        3. generar_constancia
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
           - tipo: "estudio", "calificaciones" o "traslado"
           - incluir_foto: true o false

        4. transformar_constancia
           - ruta_archivo: Ruta al archivo PDF
           - tipo_destino: "estudio", "calificaciones" o "traslado"
           - incluir_foto: true o false

        5. actualizar_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)
           - datos: Objeto con los datos a actualizar (nombre, curp, grado, etc.)

        6. eliminar_alumno
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        7. listar_constancias
           - alumno_id: ID del alumno (opcional si se proporciona nombre)
           - nombre: Nombre del alumno (opcional si se proporciona alumno_id)

        Ejemplos:

        - "Busca al alumno Juan Pérez" → {{"accion": "buscar_alumno", "parametros": {{"nombre": "Juan Pérez"}}}}
        - "Genera una constancia de estudios para el alumno con ID 5" → {{"accion": "generar_constancia", "parametros": {{"alumno_id": 5, "tipo": "estudio", "incluir_foto": false}}}}
        - "Genera una constancia de calificaciones para Juan Pérez" → {{"accion": "generar_constancia", "parametros": {{"nombre": "Juan Pérez", "tipo": "calificaciones", "incluir_foto": false}}}}
        - "Registra a María López con CURP LOPM010101MDFXXX01 en 3° grado grupo B turno matutino" → {{"accion": "registrar_alumno", "parametros": {{"nombre": "María López", "curp": "LOPM010101MDFXXX01", "grado": 3, "grupo": "B", "turno": "MATUTINO"}}}}
        - "Actualiza los datos del alumno Juan Pérez, cambia su grado a 4 y su grupo a B" → {{"accion": "actualizar_alumno", "parametros": {{"nombre": "Juan Pérez", "datos": {{"grado": 4, "grupo": "B"}}}}}}
        - "Elimina al alumno Carlos López" → {{"accion": "eliminar_alumno", "parametros": {{"nombre": "Carlos López"}}}}

        Responde ÚNICAMENTE con el JSON, sin texto adicional.
        """

    def extract_json_from_response(self, response_text):
        """Extrae el JSON de la respuesta de Gemini"""
        try:
            # Buscar el primer { y el último }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1

            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)

            return None
        except Exception as e:
            print(f"Error al extraer JSON: {str(e)}")
            print(f"Respuesta original: {response_text}")
            return None

    def generate_with_fallback(self, prompt):
        """Intenta generar contenido con el modelo principal, y si falla, usa el modelo de respaldo"""
        # Intentar con Gemini 2.0 Flash primero
        if self.models["gemini-2.0-flash"]:
            try:
                print("Usando modelo Gemini 2.0 Flash...")
                response = self.models["gemini-2.0-flash"].generate_content(prompt)
                return response
            except Exception as e:
                print(f"Error con Gemini 2.0 Flash: {str(e)}")
                print("Intentando con modelo de respaldo...")

        # Intentar con Gemini 1.5 Flash como respaldo
        if self.models["gemini-1.5-flash"]:
            try:
                print("Usando modelo Gemini 1.5 Flash...")
                response = self.models["gemini-1.5-flash"].generate_content(prompt)
                return response
            except Exception as e:
                print(f"Error con Gemini 1.5 Flash: {str(e)}")

        # Si llegamos aquí, todos los modelos fallaron
        return None

    def ejecutar_prueba(self, comando, descripcion):
        """Ejecuta una prueba con un comando específico"""
        print("\n" + "=" * 80)
        print(f"PRUEBA: {descripcion}")
        print(f"COMANDO: {comando}")
        print("-" * 80)

        self.resultados["total"] += 1

        try:
            # Crear el prompt y enviar a Gemini
            prompt = self.create_prompt(comando)
            print("Consultando a Gemini...")

            # Usar la función de respaldo para generar contenido
            response = self.generate_with_fallback(prompt)

            if not response:
                print("ERROR: No se pudo generar una respuesta con ninguno de los modelos disponibles.")
                self.resultados["fallidos"] += 1
                self.resultados["detalles"].append({
                    "comando": comando,
                    "descripcion": descripcion,
                    "resultado": "ERROR: No se pudo generar respuesta",
                    "exito": False
                })
                return False

            # Extraer JSON de la respuesta
            print("\nRespuesta de Gemini:")
            print(response.text)

            command_data = self.extract_json_from_response(response.text)

            if not command_data:
                print("ERROR: No se pudo interpretar la respuesta como un comando válido.")
                self.resultados["fallidos"] += 1
                self.resultados["detalles"].append({
                    "comando": comando,
                    "descripcion": descripcion,
                    "resultado": "ERROR: No se pudo interpretar la respuesta",
                    "exito": False
                })
                return False

            # Mostrar comando interpretado
            print("\nComando interpretado:")
            print(f"Acción: {command_data.get('accion', 'desconocida')}")
            print("Parámetros:")
            for key, value in command_data.get('parametros', {}).items():
                print(f"  - {key}: {value}")

            # Ejecutar el comando
            print("\nEjecutando comando...")
            success, message, data = self.command_executor.execute_command(command_data)

            # Mostrar resultado
            if success:
                print(f"\n✅ {message}")

                # Mostrar datos según el tipo de comando
                if "alumnos" in data:
                    print(f"Alumnos encontrados: {len(data['alumnos'])}")

                if "alumno" in data and isinstance(data["alumno"], dict):
                    print("Detalles del alumno disponibles")

                if "constancias" in data:
                    print(f"Constancias encontradas: {len(data['constancias'])}")

                if "ruta_archivo" in data:
                    print(f"Archivo generado: {data['ruta_archivo']}")
                    abrir = input("¿Deseas abrir el archivo? (s/n): ").strip().lower()
                    if abrir == 's':
                        open_file_with_default_app(data['ruta_archivo'])

                self.resultados["exitosos"] += 1
                self.resultados["detalles"].append({
                    "comando": comando,
                    "descripcion": descripcion,
                    "resultado": message,
                    "datos": data,
                    "exito": True
                })
                return True
            else:
                print(f"\n❌ {message}")
                self.resultados["fallidos"] += 1
                self.resultados["detalles"].append({
                    "comando": comando,
                    "descripcion": descripcion,
                    "resultado": message,
                    "exito": False
                })
                return False

        except Exception as e:
            print(f"\nERROR: {str(e)}")
            self.resultados["fallidos"] += 1
            self.resultados["detalles"].append({
                "comando": comando,
                "descripcion": descripcion,
                "resultado": f"ERROR: {str(e)}",
                "exito": False
            })
            return False

    def mostrar_resultados(self):
        """Muestra un resumen de los resultados de las pruebas"""
        print("\n" + "=" * 80)
        print("RESUMEN DE RESULTADOS")
        print("-" * 80)
        print(f"Total de pruebas: {self.resultados['total']}")
        print(f"Pruebas exitosas: {self.resultados['exitosos']}")
        print(f"Pruebas fallidas: {self.resultados['fallidos']}")

        if self.resultados["total"] > 0:
            porcentaje = (self.resultados["exitosos"] / self.resultados["total"]) * 100
            print(f"Porcentaje de éxito: {porcentaje:.2f}%")

        # Organizar detalles por grupos
        detalles_por_grupo = {}

        for detalle in self.resultados["detalles"]:
            # Buscar a qué grupo pertenece este escenario
            grupo_encontrado = "Sin grupo"
            escenario_id_completo = None

            # Buscar en la lista plana de escenarios
            for escenario_id, escenario in self.escenarios.items():
                if escenario["nombre"] == detalle["descripcion"]:
                    grupo_encontrado = escenario["grupo"]
                    escenario_id_completo = escenario["id_completo"]
                    break

            # Si no se encontró en la lista plana, buscar en los grupos
            if grupo_encontrado == "Sin grupo":
                for grupo_id, grupo in self.grupos_escenarios.items():
                    for esc_id, escenario in grupo["escenarios"].items():
                        if escenario["nombre"] == detalle["descripcion"]:
                            grupo_encontrado = grupo["nombre"]
                            escenario_id_completo = esc_id
                            break
                    if grupo_encontrado != "Sin grupo":
                        break

            # Añadir el ID completo al detalle
            detalle["id_completo"] = escenario_id_completo

            # Añadir al diccionario de grupos
            if grupo_encontrado not in detalles_por_grupo:
                detalles_por_grupo[grupo_encontrado] = []

            detalles_por_grupo[grupo_encontrado].append(detalle)

        # Mostrar resultados agrupados
        print("\nDETALLES DE PRUEBAS POR GRUPO:")

        for grupo_nombre, detalles in detalles_por_grupo.items():
            print(f"\n--- Grupo: {grupo_nombre} ---")

            # Contar éxitos y fallos en este grupo
            exitos_grupo = sum(1 for d in detalles if d["exito"])
            total_grupo = len(detalles)

            if total_grupo > 0:
                porcentaje_grupo = (exitos_grupo / total_grupo) * 100
                print(f"Pruebas: {total_grupo}, Exitosas: {exitos_grupo}, Fallidas: {total_grupo - exitos_grupo}")
                print(f"Porcentaje de éxito: {porcentaje_grupo:.2f}%")

            # Mostrar detalles de cada prueba en el grupo
            for detalle in detalles:
                estado = "✅ ÉXITO" if detalle["exito"] else "❌ FALLO"
                id_str = f" ({detalle['id_completo']})" if detalle.get('id_completo') else ""
                print(f"\n  {estado} - {detalle['descripcion']}{id_str}")
                print(f"  Comando: {detalle['comando']}")
                print(f"  Resultado: {detalle['resultado']}")

        # Mostrar también la lista completa para referencia
        print("\nLISTA COMPLETA DE PRUEBAS:")
        for i, detalle in enumerate(self.resultados["detalles"], 1):
            estado = "✅ ÉXITO" if detalle["exito"] else "❌ FALLO"
            id_str = f" ({detalle.get('id_completo', '')})" if detalle.get('id_completo') else ""
            print(f"{i}. {estado} - {detalle['descripcion']}{id_str}")

    def ejecutar_comando_personalizado(self):
        """Permite al usuario ingresar un comando personalizado"""
        print("\n" + "=" * 80)
        print("COMANDO PERSONALIZADO")
        print("-" * 80)

        comando = input("Ingresa el comando en lenguaje natural: ").strip()
        if not comando:
            print("Comando vacío. Operación cancelada.")
            return

        descripcion = "Comando personalizado"
        self.ejecutar_prueba(comando, descripcion)

    def inicializar_escenarios_planos(self):
        """Inicializa la lista plana de escenarios para compatibilidad"""
        # Crear una lista plana de todos los escenarios para compatibilidad
        contador = 1
        for grupo_id, grupo in self.grupos_escenarios.items():
            for escenario_id, escenario in grupo["escenarios"].items():
                self.escenarios[str(contador)] = {
                    "id_completo": escenario_id,
                    "nombre": escenario["nombre"],
                    "comando": escenario["comando"],
                    "grupo": grupo["nombre"]
                }
                contador += 1

    def menu_principal(self):
        """Muestra el menú principal"""
        # Inicializar escenarios planos
        self.inicializar_escenarios_planos()

        while True:
            print("\n" + "=" * 80)
            print("SISTEMA DE PRUEBAS INTERACTIVAS DE IA")
            print("=" * 80)
            print("1. Ejecutar todos los escenarios")
            print("2. Seleccionar grupos de escenarios")
            print("3. Seleccionar escenarios específicos")
            print("4. Ejecutar comando personalizado")
            print("5. Mostrar resultados")
            print("6. Salir")
            print("-" * 80)

            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                self.ejecutar_todos_escenarios()
            elif opcion == "2":
                self.seleccionar_grupos()
            elif opcion == "3":
                self.seleccionar_escenarios()
            elif opcion == "4":
                self.ejecutar_comando_personalizado()
            elif opcion == "5":
                self.mostrar_resultados()
            elif opcion == "6":
                print("\n¡Hasta luego!")
                break
            else:
                print("\nOpción no válida. Intenta de nuevo.")

    def ejecutar_todos_escenarios(self):
        """Ejecuta todos los escenarios de prueba"""
        print("\n" + "=" * 80)
        print("EJECUTANDO TODOS LOS ESCENARIOS")
        print("=" * 80)

        for grupo_id, grupo in self.grupos_escenarios.items():
            print(f"\n--- Grupo {grupo_id}: {grupo['nombre']} ---")
            print(f"Descripción: {grupo['descripcion']}")

            for escenario_id, escenario in grupo["escenarios"].items():
                self.ejecutar_prueba(escenario["comando"], escenario["nombre"])

    def seleccionar_grupos(self):
        """Permite al usuario seleccionar grupos completos de escenarios"""
        print("\n" + "=" * 80)
        print("SELECCIÓN DE GRUPOS DE ESCENARIOS")
        print("=" * 80)

        # Mostrar grupos disponibles
        for grupo_id, grupo in self.grupos_escenarios.items():
            print(f"{grupo_id}. {grupo['nombre']} - {grupo['descripcion']}")

        print("\nIngresa los números de los grupos que deseas ejecutar, separados por comas")
        print("Ejemplo: 1,3,5")
        seleccion = input("Selección: ").strip()

        if not seleccion:
            print("Selección vacía. Operación cancelada.")
            return

        # Procesar selección
        try:
            ids_seleccionados = [id.strip() for id in seleccion.split(",")]

            for grupo_id in ids_seleccionados:
                if grupo_id in self.grupos_escenarios:
                    grupo = self.grupos_escenarios[grupo_id]
                    print(f"\n--- Grupo {grupo_id}: {grupo['nombre']} ---")
                    print(f"Descripción: {grupo['descripcion']}")

                    for escenario_id, escenario in grupo["escenarios"].items():
                        self.ejecutar_prueba(escenario["comando"], escenario["nombre"])
                else:
                    print(f"Grupo {grupo_id} no encontrado. Omitiendo.")

        except Exception as e:
            print(f"Error al procesar la selección: {str(e)}")

    def seleccionar_escenarios(self):
        """Permite al usuario seleccionar escenarios específicos"""
        print("\n" + "=" * 80)
        print("SELECCIÓN DE ESCENARIOS ESPECÍFICOS")
        print("=" * 80)

        # Mostrar escenarios disponibles agrupados
        for grupo_id, grupo in self.grupos_escenarios.items():
            print(f"\nGrupo {grupo_id}: {grupo['nombre']}")
            print(f"Descripción: {grupo['descripcion']}")

            for escenario_id, escenario in grupo["escenarios"].items():
                print(f"  {escenario_id}. {escenario['nombre']}")

        print("\nIngresa los IDs completos de los escenarios que deseas ejecutar, separados por comas")
        print("Ejemplo: 1.1,2.3,5.2")
        seleccion = input("Selección: ").strip()

        if not seleccion:
            print("Selección vacía. Operación cancelada.")
            return

        # Procesar selección
        try:
            ids_seleccionados = [id.strip() for id in seleccion.split(",")]

            for escenario_id in ids_seleccionados:
                # Obtener el grupo y el escenario
                partes = escenario_id.split(".")
                if len(partes) != 2:
                    print(f"Formato de ID incorrecto: {escenario_id}. Debe ser 'grupo.escenario'. Omitiendo.")
                    continue

                grupo_id, sub_id = partes

                if grupo_id in self.grupos_escenarios and sub_id in self.grupos_escenarios[grupo_id]["escenarios"]:
                    escenario = self.grupos_escenarios[grupo_id]["escenarios"][sub_id]
                    self.ejecutar_prueba(escenario["comando"], escenario["nombre"])
                else:
                    print(f"Escenario {escenario_id} no encontrado. Omitiendo.")

        except Exception as e:
            print(f"Error al procesar la selección: {str(e)}")

if __name__ == "__main__":
    pruebas = PruebasInteractivas()
    pruebas.menu_principal()
