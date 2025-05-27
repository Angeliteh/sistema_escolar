"""
Normalizador de estructuras de datos
Responsabilidad: Convertir diferentes formatos de datos a estructura estándar
"""
from typing import Dict, Any, Optional, List
from app.core.logging import get_logger


class DataNormalizer:
    """Normaliza diferentes estructuras de datos de alumnos a formato estándar"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def normalize_student_data(self, item: Dict) -> Optional[Dict]:
        """
        Normaliza diferentes estructuras de datos de alumnos a un formato estándar
        
        Args:
            item: Diccionario con datos del alumno en cualquier formato
            
        Returns:
            Diccionario normalizado con estructura estándar o None si no se puede normalizar
        """
        try:
            # Estructura estándar que queremos: {'nombre': 'NOMBRE COMPLETO', 'id': 123, ...}
            
            # 🔧 CASO 1: Estructura simple {'nombre': 'NOMBRE'}
            if 'nombre' in item:
                self.logger.debug(f"   - Estructura ya normalizada: {item.get('nombre')}")
                return item
            
            # 🔧 CASO 2: Estructura con prefijo {'nombre_alumno': 'NOMBRE', 'curp_alumno': 'CURP', ...}
            if 'nombre_alumno' in item:
                normalized = self._normalize_prefixed_structure(item)
                if normalized:
                    self.logger.debug(f"   - Normalizado: {item.get('nombre_alumno')} → estructura estándar")
                    return normalized
            
            # 🔧 CASO 3: Estructura con otros campos identificables
            normalized = self._normalize_alternative_fields(item)
            if normalized:
                return normalized
            
            # 🔧 CASO 4: No se puede normalizar
            self.logger.warning(f"   - No se pudo normalizar estructura: {list(item.keys())}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error normalizando estructura de datos: {e}")
            return None
    
    def _normalize_prefixed_structure(self, item: Dict) -> Optional[Dict]:
        """Normaliza estructura con prefijos como 'nombre_alumno', 'curp_alumno', etc."""
        try:
            normalized = {
                'nombre': item.get('nombre_alumno'),
                'curp': item.get('curp_alumno'),
                'grado': item.get('grado_alumno'),
                'grupo': item.get('grupo_alumno'),
                'turno': item.get('turno_alumno'),
                'id': item.get('id_alumno') or item.get('id')
            }
            
            # Agregar otros campos que puedan existir
            excluded_keys = [
                'nombre_alumno', 'curp_alumno', 'grado_alumno', 
                'grupo_alumno', 'turno_alumno', 'id_alumno'
            ]
            
            for key, value in item.items():
                if key not in excluded_keys:
                    normalized[key] = value
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Error normalizando estructura con prefijos: {e}")
            return None
    
    def _normalize_alternative_fields(self, item: Dict) -> Optional[Dict]:
        """Normaliza estructuras con campos alternativos para nombres"""
        possible_name_fields = ['student_name', 'full_name', 'name', 'alumno_nombre']
        
        for field in possible_name_fields:
            if field in item:
                normalized = {'nombre': item[field]}
                
                # Copiar otros campos
                for key, value in item.items():
                    if key != field:
                        normalized[key] = value
                
                self.logger.debug(f"   - Normalizado: {item[field]} → estructura estándar (campo: {field})")
                return normalized
        
        return None
    
    def normalize_student_list(self, data_list: List[Dict]) -> List[Dict]:
        """
        Normaliza una lista completa de datos de alumnos
        
        Args:
            data_list: Lista de diccionarios con datos de alumnos
            
        Returns:
            Lista de diccionarios normalizados
        """
        normalized_list = []
        
        for item in data_list:
            normalized_item = self.normalize_student_data(item)
            if normalized_item:
                normalized_list.append(normalized_item)
        
        self.logger.debug(f"Normalizados {len(normalized_list)} de {len(data_list)} elementos")
        return normalized_list
    
    def validate_required_fields(self, student_data: Dict, required_fields: List[str]) -> bool:
        """
        Valida que los datos del alumno contengan los campos requeridos
        
        Args:
            student_data: Datos del alumno
            required_fields: Lista de campos requeridos
            
        Returns:
            True si todos los campos están presentes, False en caso contrario
        """
        missing_fields = []
        
        for field in required_fields:
            if not student_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            self.logger.warning(f"Campos faltantes en datos del alumno: {missing_fields}")
            return False
        
        return True
    
    def clean_student_data(self, student_data: Dict) -> Dict:
        """
        Limpia y estandariza los datos del alumno
        
        Args:
            student_data: Datos del alumno a limpiar
            
        Returns:
            Datos del alumno limpiados
        """
        cleaned_data = {}
        
        for key, value in student_data.items():
            # Limpiar valores None o vacíos
            if value is None or value == '':
                cleaned_data[key] = None
            # Limpiar strings
            elif isinstance(value, str):
                cleaned_data[key] = value.strip().upper() if key in ['nombre', 'curp'] else value.strip()
            # Mantener otros tipos de datos
            else:
                cleaned_data[key] = value
        
        return cleaned_data
    
    def extract_student_names(self, data_list: List[Dict]) -> List[str]:
        """
        Extrae solo los nombres de una lista de datos de alumnos
        
        Args:
            data_list: Lista de datos de alumnos
            
        Returns:
            Lista de nombres de alumnos
        """
        names = []
        
        for item in data_list:
            normalized_item = self.normalize_student_data(item)
            if normalized_item and normalized_item.get('nombre'):
                names.append(normalized_item['nombre'])
        
        return names
    
    def merge_student_data(self, base_data: Dict, additional_data: Dict) -> Dict:
        """
        Combina datos de alumno de diferentes fuentes
        
        Args:
            base_data: Datos base del alumno
            additional_data: Datos adicionales a combinar
            
        Returns:
            Datos combinados del alumno
        """
        # Normalizar ambos conjuntos de datos
        normalized_base = self.normalize_student_data(base_data) or {}
        normalized_additional = self.normalize_student_data(additional_data) or {}
        
        # Combinar datos (los adicionales tienen prioridad si no son None)
        merged_data = normalized_base.copy()
        
        for key, value in normalized_additional.items():
            if value is not None and value != '':
                merged_data[key] = value
        
        return merged_data
