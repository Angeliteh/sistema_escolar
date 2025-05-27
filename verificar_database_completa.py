#!/usr/bin/env python3
"""
Verificación Completa de la Base de Datos
Analiza la consistencia, variedad y calidad de los datos para pruebas de robustez
"""

import sqlite3
import json
from collections import Counter, defaultdict
from datetime import datetime
from app.core.config import Config
from app.core.logging import get_logger

class DatabaseVerifier:
    """Verificador completo de la base de datos"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.db_path = Config.DB_PATH
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Conecta a la base de datos"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Desconecta de la base de datos"""
        if self.conn:
            self.conn.close()
    
    def verificar_database_completa(self):
        """Ejecuta verificación completa de la base de datos"""
        
        print("🔍 VERIFICACIÓN COMPLETA DE LA BASE DE DATOS")
        print("=" * 60)
        
        self.connect()
        
        try:
            # 1. Estadísticas generales
            stats = self._get_general_stats()
            self._print_general_stats(stats)
            
            # 2. Distribución de datos
            distribution = self._get_data_distribution()
            self._print_data_distribution(distribution)
            
            # 3. Calidad de datos
            quality = self._check_data_quality()
            self._print_data_quality(quality)
            
            # 4. Variedad de nombres
            name_variety = self._check_name_variety()
            self._print_name_variety(name_variety)
            
            # 5. Consistencia de datos
            consistency = self._check_data_consistency()
            self._print_data_consistency(consistency)
            
            # 6. Evaluación final
            self._print_final_evaluation(stats, distribution, quality, name_variety, consistency)
            
        finally:
            self.disconnect()
    
    def _get_general_stats(self):
        """Obtiene estadísticas generales"""
        
        # Total de alumnos
        self.cursor.execute("SELECT COUNT(*) as total FROM alumnos")
        total_alumnos = self.cursor.fetchone()['total']
        
        # Alumnos con datos escolares
        self.cursor.execute("""
        SELECT COUNT(DISTINCT a.id) as con_datos 
        FROM alumnos a 
        JOIN datos_escolares de ON a.id = de.alumno_id
        """)
        con_datos_escolares = self.cursor.fetchone()['con_datos']
        
        # Alumnos con calificaciones
        self.cursor.execute("""
        SELECT COUNT(DISTINCT a.id) as con_calificaciones
        FROM alumnos a 
        JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE de.calificaciones IS NOT NULL AND de.calificaciones != '[]'
        """)
        con_calificaciones = self.cursor.fetchone()['con_calificaciones']
        
        # Alumnos con matrícula
        self.cursor.execute("SELECT COUNT(*) as con_matricula FROM alumnos WHERE matricula IS NOT NULL AND matricula != ''")
        con_matricula = self.cursor.fetchone()['con_matricula']
        
        return {
            'total_alumnos': total_alumnos,
            'con_datos_escolares': con_datos_escolares,
            'con_calificaciones': con_calificaciones,
            'con_matricula': con_matricula,
            'sin_datos_escolares': total_alumnos - con_datos_escolares,
            'sin_calificaciones': con_datos_escolares - con_calificaciones,
            'sin_matricula': total_alumnos - con_matricula
        }
    
    def _get_data_distribution(self):
        """Obtiene distribución de datos"""
        
        # Distribución por grados
        self.cursor.execute("""
        SELECT grado, COUNT(*) as cantidad 
        FROM datos_escolares 
        WHERE grado IS NOT NULL 
        GROUP BY grado 
        ORDER BY grado
        """)
        por_grados = dict(self.cursor.fetchall())
        
        # Distribución por grupos
        self.cursor.execute("""
        SELECT grupo, COUNT(*) as cantidad 
        FROM datos_escolares 
        WHERE grupo IS NOT NULL 
        GROUP BY grupo 
        ORDER BY grupo
        """)
        por_grupos = dict(self.cursor.fetchall())
        
        # Distribución por turnos
        self.cursor.execute("""
        SELECT turno, COUNT(*) as cantidad 
        FROM datos_escolares 
        WHERE turno IS NOT NULL 
        GROUP BY turno 
        ORDER BY turno
        """)
        por_turnos = dict(self.cursor.fetchall())
        
        # Distribución por ciclo escolar
        self.cursor.execute("""
        SELECT ciclo_escolar, COUNT(*) as cantidad 
        FROM datos_escolares 
        WHERE ciclo_escolar IS NOT NULL 
        GROUP BY ciclo_escolar
        """)
        por_ciclo = dict(self.cursor.fetchall())
        
        return {
            'por_grados': por_grados,
            'por_grupos': por_grupos,
            'por_turnos': por_turnos,
            'por_ciclo': por_ciclo
        }
    
    def _check_data_quality(self):
        """Verifica calidad de los datos"""
        
        # CURPs válidas (formato básico)
        self.cursor.execute("SELECT curp FROM alumnos WHERE curp IS NOT NULL")
        curps = [row['curp'] for row in self.cursor.fetchall()]
        curps_validas = sum(1 for curp in curps if len(curp) == 18)
        
        # Nombres completos (al menos 2 palabras)
        self.cursor.execute("SELECT nombre FROM alumnos WHERE nombre IS NOT NULL")
        nombres = [row['nombre'] for row in self.cursor.fetchall()]
        nombres_completos = sum(1 for nombre in nombres if len(nombre.split()) >= 2)
        
        # Fechas de nacimiento válidas
        self.cursor.execute("SELECT fecha_nacimiento FROM alumnos WHERE fecha_nacimiento IS NOT NULL")
        fechas = self.cursor.fetchall()
        fechas_validas = 0
        for fecha in fechas:
            try:
                datetime.strptime(fecha['fecha_nacimiento'], '%Y-%m-%d')
                fechas_validas += 1
            except:
                pass
        
        # Calificaciones válidas (JSON)
        self.cursor.execute("SELECT calificaciones FROM datos_escolares WHERE calificaciones IS NOT NULL AND calificaciones != '[]'")
        calificaciones = self.cursor.fetchall()
        calificaciones_validas = 0
        total_materias = 0
        for cal in calificaciones:
            try:
                cal_data = json.loads(cal['calificaciones'])
                if isinstance(cal_data, list) and len(cal_data) > 0:
                    calificaciones_validas += 1
                    total_materias += len(cal_data)
            except:
                pass
        
        return {
            'curps_validas': curps_validas,
            'total_curps': len(curps),
            'nombres_completos': nombres_completos,
            'total_nombres': len(nombres),
            'fechas_validas': fechas_validas,
            'total_fechas': len(fechas),
            'calificaciones_validas': calificaciones_validas,
            'total_calificaciones': len(calificaciones),
            'promedio_materias': total_materias / calificaciones_validas if calificaciones_validas > 0 else 0
        }
    
    def _check_name_variety(self):
        """Verifica variedad en los nombres"""
        
        # Obtener todos los nombres
        self.cursor.execute("SELECT nombre FROM alumnos WHERE nombre IS NOT NULL")
        nombres_completos = [row['nombre'] for row in self.cursor.fetchall()]
        
        # Separar nombres y apellidos
        primeros_nombres = []
        apellidos_paternos = []
        apellidos_maternos = []
        
        for nombre_completo in nombres_completos:
            partes = nombre_completo.split()
            if len(partes) >= 3:
                primeros_nombres.append(partes[0])
                apellidos_paternos.append(partes[1])
                apellidos_maternos.append(partes[2])
            elif len(partes) == 2:
                primeros_nombres.append(partes[0])
                apellidos_paternos.append(partes[1])
        
        # Contar frecuencias
        freq_nombres = Counter(primeros_nombres)
        freq_apellidos_p = Counter(apellidos_paternos)
        freq_apellidos_m = Counter(apellidos_maternos)
        
        return {
            'total_nombres_unicos': len(freq_nombres),
            'total_apellidos_p_unicos': len(freq_apellidos_p),
            'total_apellidos_m_unicos': len(freq_apellidos_m),
            'nombres_mas_comunes': freq_nombres.most_common(10),
            'apellidos_p_mas_comunes': freq_apellidos_p.most_common(10),
            'apellidos_m_mas_comunes': freq_apellidos_m.most_common(10),
            'nombres_con_coincidencias': sum(1 for count in freq_nombres.values() if count > 1),
            'apellidos_con_coincidencias': sum(1 for count in freq_apellidos_p.values() if count > 1)
        }
    
    def _check_data_consistency(self):
        """Verifica consistencia de los datos"""
        
        # Verificar duplicados por CURP
        self.cursor.execute("""
        SELECT curp, COUNT(*) as cantidad 
        FROM alumnos 
        WHERE curp IS NOT NULL 
        GROUP BY curp 
        HAVING COUNT(*) > 1
        """)
        duplicados_curp = self.cursor.fetchall()
        
        # Verificar alumnos sin datos escolares
        self.cursor.execute("""
        SELECT a.id, a.nombre 
        FROM alumnos a 
        LEFT JOIN datos_escolares de ON a.id = de.alumno_id 
        WHERE de.id IS NULL
        """)
        sin_datos_escolares = self.cursor.fetchall()
        
        # Verificar datos escolares huérfanos
        self.cursor.execute("""
        SELECT de.id 
        FROM datos_escolares de 
        LEFT JOIN alumnos a ON de.alumno_id = a.id 
        WHERE a.id IS NULL
        """)
        datos_huerfanos = self.cursor.fetchall()
        
        # Verificar rangos de edad coherentes
        self.cursor.execute("""
        SELECT a.nombre, a.fecha_nacimiento, de.grado
        FROM alumnos a
        JOIN datos_escolares de ON a.id = de.alumno_id
        WHERE a.fecha_nacimiento IS NOT NULL AND de.grado IS NOT NULL
        """)
        alumnos_edad = self.cursor.fetchall()
        
        edades_incoherentes = 0
        for alumno in alumnos_edad:
            try:
                fecha_nac = datetime.strptime(alumno['fecha_nacimiento'], '%Y-%m-%d')
                edad = (datetime.now() - fecha_nac).days // 365
                grado = alumno['grado']
                edad_esperada = 6 + grado - 1
                
                # Permitir variación de ±2 años
                if abs(edad - edad_esperada) > 2:
                    edades_incoherentes += 1
            except:
                pass
        
        return {
            'duplicados_curp': len(duplicados_curp),
            'sin_datos_escolares': len(sin_datos_escolares),
            'datos_huerfanos': len(datos_huerfanos),
            'edades_incoherentes': edades_incoherentes,
            'total_verificados': len(alumnos_edad)
        }
    
    def _print_general_stats(self, stats):
        """Imprime estadísticas generales"""
        
        print("\n📊 ESTADÍSTICAS GENERALES")
        print("-" * 30)
        print(f"👥 Total de alumnos: {stats['total_alumnos']}")
        print(f"🎓 Con datos escolares: {stats['con_datos_escolares']} ({stats['con_datos_escolares']/stats['total_alumnos']*100:.1f}%)")
        print(f"📊 Con calificaciones: {stats['con_calificaciones']} ({stats['con_calificaciones']/stats['total_alumnos']*100:.1f}%)")
        print(f"🆔 Con matrícula: {stats['con_matricula']} ({stats['con_matricula']/stats['total_alumnos']*100:.1f}%)")
        print(f"⚠️  Sin datos escolares: {stats['sin_datos_escolares']}")
        print(f"⚠️  Sin calificaciones: {stats['sin_calificaciones']}")
        print(f"⚠️  Sin matrícula: {stats['sin_matricula']}")
    
    def _print_data_distribution(self, dist):
        """Imprime distribución de datos"""
        
        print("\n📈 DISTRIBUCIÓN DE DATOS")
        print("-" * 30)
        
        print("🎓 Por grados:")
        for grado, cantidad in dist['por_grados'].items():
            print(f"   {grado}°: {cantidad} alumnos")
        
        print("📚 Por grupos:")
        for grupo, cantidad in dist['por_grupos'].items():
            print(f"   Grupo {grupo}: {cantidad} alumnos")
        
        print("⏰ Por turnos:")
        for turno, cantidad in dist['por_turnos'].items():
            print(f"   {turno}: {cantidad} alumnos")
        
        print("📅 Por ciclo escolar:")
        for ciclo, cantidad in dist['por_ciclo'].items():
            print(f"   {ciclo}: {cantidad} alumnos")
    
    def _print_data_quality(self, quality):
        """Imprime calidad de datos"""
        
        print("\n💎 CALIDAD DE DATOS")
        print("-" * 30)
        
        curp_pct = quality['curps_validas'] / quality['total_curps'] * 100 if quality['total_curps'] > 0 else 0
        print(f"🆔 CURPs válidas: {quality['curps_validas']}/{quality['total_curps']} ({curp_pct:.1f}%)")
        
        nombre_pct = quality['nombres_completos'] / quality['total_nombres'] * 100 if quality['total_nombres'] > 0 else 0
        print(f"👤 Nombres completos: {quality['nombres_completos']}/{quality['total_nombres']} ({nombre_pct:.1f}%)")
        
        fecha_pct = quality['fechas_validas'] / quality['total_fechas'] * 100 if quality['total_fechas'] > 0 else 0
        print(f"📅 Fechas válidas: {quality['fechas_validas']}/{quality['total_fechas']} ({fecha_pct:.1f}%)")
        
        cal_pct = quality['calificaciones_validas'] / quality['total_calificaciones'] * 100 if quality['total_calificaciones'] > 0 else 0
        print(f"📊 Calificaciones válidas: {quality['calificaciones_validas']}/{quality['total_calificaciones']} ({cal_pct:.1f}%)")
        print(f"📚 Promedio materias por alumno: {quality['promedio_materias']:.1f}")
    
    def _print_name_variety(self, variety):
        """Imprime variedad de nombres"""
        
        print("\n🎭 VARIEDAD DE NOMBRES")
        print("-" * 30)
        print(f"👤 Nombres únicos: {variety['total_nombres_unicos']}")
        print(f"👨 Apellidos paternos únicos: {variety['total_apellidos_p_unicos']}")
        print(f"👩 Apellidos maternos únicos: {variety['total_apellidos_m_unicos']}")
        print(f"🔄 Nombres con coincidencias: {variety['nombres_con_coincidencias']}")
        print(f"🔄 Apellidos con coincidencias: {variety['apellidos_con_coincidencias']}")
        
        print("\n🏆 Nombres más comunes:")
        for nombre, count in variety['nombres_mas_comunes'][:5]:
            print(f"   {nombre}: {count} veces")
        
        print("\n🏆 Apellidos más comunes:")
        for apellido, count in variety['apellidos_p_mas_comunes'][:5]:
            print(f"   {apellido}: {count} veces")
    
    def _print_data_consistency(self, consistency):
        """Imprime consistencia de datos"""
        
        print("\n🔍 CONSISTENCIA DE DATOS")
        print("-" * 30)
        print(f"❌ Duplicados por CURP: {consistency['duplicados_curp']}")
        print(f"⚠️  Sin datos escolares: {consistency['sin_datos_escolares']}")
        print(f"🔗 Datos huérfanos: {consistency['datos_huerfanos']}")
        print(f"📅 Edades incoherentes: {consistency['edades_incoherentes']}/{consistency['total_verificados']}")
    
    def _print_final_evaluation(self, stats, dist, quality, variety, consistency):
        """Imprime evaluación final"""
        
        print("\n" + "=" * 60)
        print("🏁 EVALUACIÓN FINAL PARA PRUEBAS DE ROBUSTEZ")
        print("=" * 60)
        
        # Calcular puntuaciones
        volume_score = min(100, stats['total_alumnos'] / 200 * 100)  # 200+ alumnos = 100%
        quality_score = (
            (quality['curps_validas'] / quality['total_curps'] * 25) +
            (quality['nombres_completos'] / quality['total_nombres'] * 25) +
            (quality['fechas_validas'] / quality['total_fechas'] * 25) +
            (quality['calificaciones_validas'] / quality['total_calificaciones'] * 25)
        ) if quality['total_curps'] > 0 else 0
        
        variety_score = min(100, (variety['total_nombres_unicos'] + variety['total_apellidos_p_unicos']) / 100 * 100)
        consistency_score = max(0, 100 - (consistency['duplicados_curp'] + consistency['edades_incoherentes']) * 5)
        
        overall_score = (volume_score + quality_score + variety_score + consistency_score) / 4
        
        print(f"📊 Puntuación de Volumen: {volume_score:.1f}/100")
        print(f"💎 Puntuación de Calidad: {quality_score:.1f}/100")
        print(f"🎭 Puntuación de Variedad: {variety_score:.1f}/100")
        print(f"🔍 Puntuación de Consistencia: {consistency_score:.1f}/100")
        print(f"\n🎯 PUNTUACIÓN GENERAL: {overall_score:.1f}/100")
        
        # Evaluación final
        if overall_score >= 90:
            print("\n🎉 ¡EXCELENTE! Base de datos ideal para pruebas de robustez")
            print("✅ Lista para pruebas con 200+ alumnos")
            print("✅ Datos variados y consistentes")
            print("✅ Calidad de datos alta")
        elif overall_score >= 75:
            print("\n✅ BUENA. Base de datos apropiada para pruebas")
            print("✅ Suficiente para validar robustez")
            print("⚠️  Algunas mejoras menores recomendadas")
        elif overall_score >= 60:
            print("\n⚠️  REGULAR. Base de datos funcional pero mejorable")
            print("⚠️  Puede usarse para pruebas básicas")
            print("❌ No ideal para pruebas exhaustivas")
        else:
            print("\n❌ CRÍTICA. Base de datos necesita mejoras")
            print("❌ No recomendada para pruebas de robustez")
            print("🔧 Requiere corrección de datos")
        
        # Recomendaciones específicas
        print(f"\n💡 RECOMENDACIONES:")
        if stats['total_alumnos'] < 200:
            print(f"   📈 Generar más alumnos (actual: {stats['total_alumnos']}, ideal: 200+)")
        if quality_score < 80:
            print("   🔧 Mejorar calidad de datos (CURPs, nombres, fechas)")
        if variety_score < 70:
            print("   🎭 Aumentar variedad de nombres y apellidos")
        if consistency_score < 90:
            print("   🔍 Corregir inconsistencias (duplicados, edades)")

def main():
    """Función principal"""
    try:
        verifier = DatabaseVerifier()
        verifier.verificar_database_completa()
        return 0
    except Exception as e:
        print(f"❌ Error en verificación: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
