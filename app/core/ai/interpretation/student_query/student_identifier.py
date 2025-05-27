"""
Identificador de estudiantes en contexto conversacional
Responsabilidad: Identificar qué alumno específico se menciona en una consulta
"""
import re
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger


class StudentIdentifier:
    """Identifica alumnos específicos usando contexto conversacional y referencias"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def identify_student_from_context(self, user_query: str, conversation_stack: list) -> Optional[Dict[str, Any]]:
        """
        Identifica al alumno correcto usando el contexto conversacional y referencias en la consulta
        
        Args:
            user_query: Consulta del usuario
            conversation_stack: Pila conversacional con datos previos
            
        Returns:
            Dict con datos del alumno identificado o None si no se encuentra
        """
        try:
            self.logger.info(f"🔍 IDENTIFICANDO ALUMNO DESDE CONTEXTO:")
            self.logger.info(f"   - Query: '{user_query}'")
            self.logger.info(f"   - Pila disponible: {len(conversation_stack)} niveles")
            
            # Obtener alumnos disponibles de la pila
            alumnos_disponibles = self._extract_students_from_stack(conversation_stack)
            
            if not alumnos_disponibles:
                self.logger.warning("❌ No hay alumnos disponibles en la pila conversacional")
                return None
            
            # Aplicar estrategias de identificación en orden de prioridad
            strategies = [
                self._identify_by_name,
                self._identify_by_position,
                self._identify_by_number,
                self._identify_by_fallback
            ]
            
            for strategy in strategies:
                result = strategy(user_query, alumnos_disponibles)
                if result:
                    return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error identificando alumno desde contexto: {e}")
            return None
    
    def _extract_students_from_stack(self, conversation_stack: list) -> List[Dict[str, Any]]:
        """Extrae y normaliza alumnos de la pila conversacional"""
        from .data_normalizer import DataNormalizer
        normalizer = DataNormalizer()
        
        for i, level in enumerate(reversed(conversation_stack), 1):
            if level.get('data') and len(level.get('data', [])) > 0:
                raw_data = level['data']
                self.logger.info(f"   - Nivel {i}: {len(raw_data)} elementos encontrados")
                
                # Normalizar estructura de datos
                normalized_data = []
                for item in raw_data:
                    normalized_item = normalizer.normalize_student_data(item)
                    if normalized_item:
                        normalized_data.append(normalized_item)
                
                if normalized_data:
                    self.logger.info(f"   - Datos normalizados: {len(normalized_data)} alumnos válidos")
                    return normalized_data
        
        return []
    
    def _identify_by_name(self, user_query: str, alumnos_disponibles: List[Dict]) -> Optional[Dict]:
        """Estrategia 1: Buscar por nombre exacto o parcial"""
        user_lower = user_query.lower()
        
        # Extraer posibles nombres de la consulta
        palabras = user_query.split()
        posibles_nombres = []
        
        # Buscar palabras que podrían ser nombres (después de palabras clave)
        skip_words = {
            "para", "de", "del", "la", "el", "una", "constancia", "calificaciones", 
            "estudios", "traslado", "si", "dame", "por", "favor", "genera", "solo"
        }
        
        for palabra in palabras:
            palabra_clean = palabra.lower().strip(".,!?")
            if palabra_clean not in skip_words and len(palabra_clean) >= 3:
                posibles_nombres.append(palabra_clean)
        
        self.logger.info(f"   - Posibles nombres extraídos: {posibles_nombres}")
        
        # Buscar coincidencias en los alumnos disponibles
        for posible_nombre in posibles_nombres:
            for i, alumno in enumerate(alumnos_disponibles):
                nombre_alumno = alumno.get('nombre', '').lower()
                
                # Verificar si el posible nombre está en el nombre del alumno
                if posible_nombre in nombre_alumno:
                    self.logger.info(f"✅ COINCIDENCIA POR NOMBRE:")
                    self.logger.info(f"   - Posible nombre: '{posible_nombre}'")
                    self.logger.info(f"   - Alumno: {alumno.get('nombre', 'N/A')}")
                    self.logger.info(f"   - Posición en lista: {i + 1}")
                    return alumno
        
        return None
    
    def _identify_by_position(self, user_query: str, alumnos_disponibles: List[Dict]) -> Optional[Dict]:
        """Estrategia 2: Buscar por referencias posicionales"""
        user_lower = user_query.lower()
        
        referencias_posicionales = {
            "primero": 0, "primer": 0, "primera": 0, "1": 0, "uno": 0,
            "segundo": 1, "segunda": 1, "2": 1, "dos": 1,
            "tercero": 2, "tercer": 2, "tercera": 2, "3": 2, "tres": 2,
            "cuarto": 3, "cuarta": 3, "4": 3, "cuatro": 3,
            "quinto": 4, "quinta": 4, "5": 4, "cinco": 4,
            "último": -1, "ultima": -1, "final": -1
        }
        
        for referencia, indice in referencias_posicionales.items():
            if referencia in user_lower:
                try:
                    if indice == -1:
                        alumno_seleccionado = alumnos_disponibles[-1]
                    else:
                        alumno_seleccionado = alumnos_disponibles[indice]
                    
                    self.logger.info(f"✅ REFERENCIA POSICIONAL:")
                    self.logger.info(f"   - Referencia: '{referencia}' → posición {indice + 1 if indice >= 0 else 'último'}")
                    self.logger.info(f"   - Alumno: {alumno_seleccionado.get('nombre', 'N/A')}")
                    return alumno_seleccionado
                except IndexError:
                    self.logger.warning(f"❌ Referencia '{referencia}' fuera de rango (solo hay {len(alumnos_disponibles)} alumnos)")
                    continue
        
        return None
    
    def _identify_by_number(self, user_query: str, alumnos_disponibles: List[Dict]) -> Optional[Dict]:
        """Estrategia 3: Buscar por números explícitos"""
        numeros = re.findall(r'\b(\d+)\b', user_query)
        for numero_str in numeros:
            try:
                numero = int(numero_str)
                if 1 <= numero <= len(alumnos_disponibles):
                    alumno_seleccionado = alumnos_disponibles[numero - 1]  # Convertir a índice base 0
                    self.logger.info(f"✅ NÚMERO ENCONTRADO:")
                    self.logger.info(f"   - Número: {numero}")
                    self.logger.info(f"   - Alumno: {alumno_seleccionado.get('nombre', 'N/A')}")
                    return alumno_seleccionado
            except (ValueError, IndexError):
                continue
        
        return None
    
    def _identify_by_fallback(self, user_query: str, alumnos_disponibles: List[Dict]) -> Optional[Dict]:
        """Estrategia 4: Fallback al primer alumno disponible"""
        if alumnos_disponibles:
            self.logger.warning("❌ No se encontró referencia específica, usando primer alumno como fallback")
            return alumnos_disponibles[0]
        
        return None
    
    def get_complete_student_data(self, alumno_parcial: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene los datos completos del alumno desde la base de datos"""
        try:
            # Si ya tiene ID, verificar que tenga todos los datos necesarios
            if alumno_parcial.get('id'):
                self.logger.info(f"✅ Alumno ya tiene ID: {alumno_parcial.get('id')}")
                return alumno_parcial
            
            # Si no tiene ID, buscar por nombre
            nombre_alumno = alumno_parcial.get('nombre', '')
            if not nombre_alumno:
                self.logger.warning("❌ No se puede buscar alumno sin nombre")
                return None
            
            self.logger.info(f"🔍 Buscando datos completos para: {nombre_alumno}")
            
            from app.core.service_provider import ServiceProvider
            service_provider = ServiceProvider.get_instance()
            alumno_service = service_provider.alumno_service
            
            # Buscar alumno por nombre exacto
            alumnos_encontrados = alumno_service.buscar_alumnos(nombre_alumno)
            
            if not alumnos_encontrados:
                self.logger.warning(f"❌ No se encontró alumno con nombre: {nombre_alumno}")
                return None
            
            # Si hay múltiples coincidencias, buscar coincidencia exacta
            for alumno in alumnos_encontrados:
                alumno_dict = alumno.to_dict() if hasattr(alumno, 'to_dict') else alumno
                if alumno_dict.get('nombre', '').upper() == nombre_alumno.upper():
                    self.logger.info(f"✅ Datos completos obtenidos para: {alumno_dict.get('nombre')} (ID: {alumno_dict.get('id')})")
                    return alumno_dict
            
            # Si no hay coincidencia exacta, tomar el primero
            primer_alumno = alumnos_encontrados[0]
            alumno_dict = primer_alumno.to_dict() if hasattr(primer_alumno, 'to_dict') else primer_alumno
            
            self.logger.info(f"✅ Usando primer resultado: {alumno_dict.get('nombre')} (ID: {alumno_dict.get('id')})")
            return alumno_dict
            
        except Exception as e:
            self.logger.error(f"Error obteniendo datos completos del alumno: {e}")
            return None
