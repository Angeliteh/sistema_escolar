"""
🗺️ FIELD MAPPER - MAPEO DINÁMICO DE CAMPOS
Mapea campos de usuario a campos de base de datos de forma dinámica y configurable
"""

from typing import Dict, Any, Optional, List
from app.core.logging import get_logger

class FieldMapper:
    """Mapea campos de usuario a campos de base de datos dinámicamente"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Mapeo dinámico de campos - configurable por escuela
        self._field_mapping = {
            # Campos de alumnos
            'matricula': {'tabla': 'alumnos', 'campo': 'matricula'},
            'matrícula': {'tabla': 'alumnos', 'campo': 'matricula'},
            'nombre': {'tabla': 'alumnos', 'campo': 'nombre'},
            'nombres': {'tabla': 'alumnos', 'campo': 'nombre'},
            'curp': {'tabla': 'alumnos', 'campo': 'curp'},
            'fecha_nacimiento': {'tabla': 'alumnos', 'campo': 'fecha_nacimiento'},
            'nacimiento': {'tabla': 'alumnos', 'campo': 'fecha_nacimiento'},
            
            # Campos de datos escolares
            'grado': {'tabla': 'datos_escolares', 'campo': 'grado'},
            'grupo': {'tabla': 'datos_escolares', 'campo': 'grupo'},
            'turno': {'tabla': 'datos_escolares', 'campo': 'turno'},
            'escuela': {'tabla': 'datos_escolares', 'campo': 'escuela'},
            'ciclo_escolar': {'tabla': 'datos_escolares', 'campo': 'ciclo_escolar'},
            'calificaciones': {'tabla': 'datos_escolares', 'campo': 'calificaciones'},
            
            # Aliases comunes
            'id': {'tabla': 'alumnos', 'campo': 'id'},
            'alumno_id': {'tabla': 'datos_escolares', 'campo': 'alumno_id'}
        }
    
    def map_user_field_to_db(self, user_field: str) -> Optional[Dict[str, str]]:
        """
        Mapea un campo de usuario a su equivalente en base de datos
        
        Args:
            user_field: Campo como lo escribe el usuario (ej: "grado", "matrícula")
            
        Returns:
            Dict con 'tabla' y 'campo' o None si no se encuentra
        """
        try:
            user_field_lower = user_field.lower().strip()
            mapping = self._field_mapping.get(user_field_lower)
            
            if mapping:
                self.logger.debug(f"✅ Campo mapeado: {user_field} → {mapping['tabla']}.{mapping['campo']}")
                return mapping
            else:
                self.logger.debug(f"⚠️ Campo no mapeado: {user_field}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error mapeando campo {user_field}: {e}")
            return None
    
    def get_table_prefix(self, tabla: str) -> str:
        """Obtiene el prefijo de tabla para SQL dinámicamente"""
        # Generar prefijo dinámicamente basado en el nombre de la tabla
        if tabla.startswith('datos_'):
            return 'de'
        elif tabla.startswith('alumno'):
            return 'a'
        else:
            # Usar primera letra como prefijo por defecto
            return tabla[0].lower() if tabla else 'a'
    
    def add_field_mapping(self, user_field: str, tabla: str, campo_db: str):
        """Agrega un nuevo mapeo de campo dinámicamente"""
        self._field_mapping[user_field.lower()] = {
            'tabla': tabla,
            'campo': campo_db
        }
        self.logger.info(f"✅ Nuevo mapeo agregado: {user_field} → {tabla}.{campo_db}")
    
    def get_all_mappings(self) -> Dict[str, Dict[str, str]]:
        """Obtiene todos los mapeos disponibles"""
        return self._field_mapping.copy()
    
    def is_valid_field(self, user_field: str) -> bool:
        """Verifica si un campo de usuario es válido"""
        return user_field.lower().strip() in self._field_mapping

    def validate_and_map_criterion(self, criterion: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Valida y mapea un criterio completo

        Args:
            criterion: Dict con 'tabla', 'campo', 'operador', 'valor'

        Returns:
            Criterio validado y mapeado o None si no es válido
        """
        try:
            if not isinstance(criterion, dict):
                return None

            campo = criterion.get('campo', '')
            if not campo:
                return None

            # Mapear el campo
            mapped_field = self.map_user_field_to_db(campo)
            if not mapped_field:
                # Si no se puede mapear, usar el criterio original
                return criterion

            # Crear criterio mapeado
            mapped_criterion = criterion.copy()
            mapped_criterion['tabla'] = mapped_field['tabla']
            mapped_criterion['campo'] = mapped_field['campo']

            return mapped_criterion

        except Exception as e:
            self.logger.error(f"Error validando criterio: {e}")
            return None

    def suggest_fields(self, user_field: str, tabla: str = None) -> List[str]:
        """
        Sugiere campos similares al campo de usuario

        Args:
            user_field: Campo que no se pudo mapear
            tabla: Tabla específica (opcional)

        Returns:
            Lista de campos sugeridos
        """
        try:
            user_field_lower = user_field.lower()
            suggestions = []

            for field_name, mapping in self._field_mapping.items():
                # Si se especifica tabla, filtrar por tabla
                if tabla and mapping['tabla'] != tabla:
                    continue

                # Buscar coincidencias parciales
                if user_field_lower in field_name or field_name in user_field_lower:
                    suggestions.append(f"{field_name} ({mapping['tabla']}.{mapping['campo']})")

            return suggestions[:5]  # Máximo 5 sugerencias

        except Exception as e:
            self.logger.error(f"Error generando sugerencias: {e}")
            return []
