"""
🎯 MAPEADOR Y VALIDADOR CENTRALIZADO DE CAMPOS

Este módulo centraliza toda la lógica de validación y mapeo de campos
para asegurar que SIEMPRE se usen campos válidos de la base de datos.

Responsabilidades:
- Validar campos contra estructura real de BD
- Mapear campos del usuario a campos reales
- Convertir operadores según el tipo de campo
- Proporcionar sugerencias inteligentes
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from app.core.database.database_analyzer import DatabaseAnalyzer


class FieldMapper:
    """
    🎯 MAPEADOR CENTRALIZADO DE CAMPOS
    
    Valida y mapea campos del usuario a campos reales de la base de datos
    antes de cualquier consulta SQL.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.database_analyzer = DatabaseAnalyzer(db_path)
        
        # Cache de estructura para evitar consultas repetidas
        self._structure_cache = None
        
        # 🚫 HARDCODEO ELIMINADO - USAR SOLO LLM INTELIGENTE
        # Todos los mapeos ahora se manejan por LLM con contexto estructural
        self._field_mappings = {}
    
    def validate_and_map_criterion(self, criterion: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 VALIDA Y MAPEA UN CRITERIO COMPLETO
        
        Args:
            criterion: Criterio con formato {"tabla": "...", "campo": "...", "operador": "...", "valor": "..."}
            
        Returns:
            Criterio validado y mapeado, o None si no se puede mapear
        """
        try:
            tabla = criterion.get("tabla", "alumnos")
            campo = criterion.get("campo", "")
            operador = criterion.get("operador", "=")
            valor = criterion.get("valor", "")
            
            self.logger.info(f"🔍 Validando criterio: {tabla}.{campo} {operador} '{valor}'")
            
            # 1. Obtener estructura de la base de datos
            structure = self._get_database_structure()
            
            # 2. Validar que la tabla existe
            if tabla not in structure.get("tables", {}):
                self.logger.warning(f"❌ Tabla '{tabla}' no existe")
                # Intentar mapear a tabla correcta
                tabla = self._map_table(tabla)
                if not tabla:
                    return None
            
            # 3. Validar y mapear el campo
            mapped_field_info = self._validate_and_map_field(tabla, campo, valor, operador)
            if not mapped_field_info:
                self.logger.warning(f"❌ No se pudo mapear campo '{campo}' en tabla '{tabla}'")
                return None
            
            # 4. Construir criterio mapeado
            mapped_criterion = {
                "tabla": mapped_field_info["tabla"],
                "campo": mapped_field_info["campo"],
                "operador": mapped_field_info["operador"],
                "valor": mapped_field_info["valor"]
            }
            
            self.logger.info(f"✅ Criterio mapeado: {mapped_criterion}")
            return mapped_criterion
            
        except Exception as e:
            self.logger.error(f"Error validando criterio: {e}")
            return None
    
    def _validate_and_map_field(self, tabla: str, campo: str, valor: str, operador: str = "=") -> Optional[Dict[str, Any]]:
        """
        🔧 VALIDA Y MAPEA UN CAMPO ESPECÍFICO

        Args:
            tabla: Nombre de la tabla
            campo: Nombre del campo
            valor: Valor a buscar
            operador: Operador SQL (=, LIKE, >, etc.)

        Returns:
            Dict con información del campo mapeado o None si no se puede mapear
        """
        try:
            structure = self._get_database_structure()
            table_columns = structure.get("tables", {}).get(tabla, {}).get("columns", {})
            
            # 1. Si el campo existe directamente, usarlo PRESERVANDO EL OPERADOR ORIGINAL
            if campo in table_columns:
                self.logger.info(f"✅ Campo '{campo}' existe directamente en '{tabla}'")

                # 🔧 NORMALIZACIÓN DE DATOS SEGÚN EL CAMPO
                valor_normalizado = self._normalize_field_value(campo, valor)

                # 🔧 PRESERVAR OPERADOR ORIGINAL - NO CAMBIAR A "="
                # Si es LIKE y el valor no tiene %, agregarlo
                if operador == "LIKE" and not ("%" in valor_normalizado):
                    if campo == "nombre":  # Para nombres, buscar que contenga
                        valor_normalizado = f"%{valor_normalizado}%"
                    else:
                        valor_normalizado = f"%{valor_normalizado}%"  # Por defecto, buscar que contenga

                return {
                    "tabla": tabla,
                    "campo": campo,
                    "operador": operador,  # ✅ PRESERVAR OPERADOR ORIGINAL
                    "valor": valor_normalizado  # ✅ VALOR NORMALIZADO
                }
            
            # 2. Intentar mapeo inteligente
            if campo.lower() in self._field_mappings:
                mapping_info = self._field_mappings[campo.lower()]
                target_field = mapping_info["target_field"]
                strategy = mapping_info["strategy"]
                
                # Verificar que el campo objetivo existe
                if target_field in table_columns:
                    # Normalizar valor antes del mapeo
                    valor_normalizado = self._normalize_field_value(target_field, valor)
                    mapped_info = self._apply_mapping_strategy(tabla, target_field, valor_normalizado, strategy)
                    if mapped_info:
                        self.logger.info(f"✅ Campo '{campo}' mapeado a '{target_field}' con estrategia '{strategy}'")
                        return mapped_info
            
            # 3. Buscar campos similares
            similar_field = self._find_similar_field(campo, table_columns.keys())
            if similar_field:
                self.logger.info(f"✅ Campo '{campo}' mapeado a campo similar '{similar_field}'")
                return {
                    "tabla": tabla,
                    "campo": similar_field,
                    "operador": "LIKE" if isinstance(valor, str) else "=",
                    "valor": f"%{valor}%" if isinstance(valor, str) and similar_field == "nombre" else valor
                }
            
            # 4. Intentar mapeo a tabla relacionada
            if tabla == "alumnos":
                # Intentar en datos_escolares
                datos_escolares_columns = structure.get("tables", {}).get("datos_escolares", {}).get("columns", {})
                if campo in datos_escolares_columns:
                    self.logger.info(f"✅ Campo '{campo}' encontrado en tabla relacionada 'datos_escolares'")
                    return {
                        "tabla": "datos_escolares",
                        "campo": campo,
                        "operador": "=",
                        "valor": valor
                    }
            
            self.logger.warning(f"❌ No se pudo mapear campo '{campo}'")
            return None
            
        except Exception as e:
            self.logger.error(f"Error mapeando campo: {e}")
            return None
    
    def _apply_mapping_strategy(self, tabla: str, target_field: str, valor: str, strategy: str) -> Optional[Dict[str, Any]]:
        """
        🎯 APLICA ESTRATEGIA DE MAPEO ESPECÍFICA
        """
        try:
            if strategy == "contains":
                return {
                    "tabla": tabla,
                    "campo": target_field,
                    "operador": "LIKE",
                    "valor": f"%{valor}%"
                }
            elif strategy == "starts_with":
                return {
                    "tabla": tabla,
                    "campo": target_field,
                    "operador": "LIKE",
                    "valor": f"{valor}%"
                }
            elif strategy == "exact":
                return {
                    "tabla": tabla,
                    "campo": target_field,
                    "operador": "=",
                    "valor": valor
                }
            elif strategy == "calculated":
                # Para campos calculados como edad
                if target_field == "fecha_nacimiento":
                    # Convertir edad a rango de fechas
                    return self._convert_age_to_date_range(tabla, valor)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error aplicando estrategia de mapeo: {e}")
            return None
    
    def _convert_age_to_date_range(self, tabla: str, edad_str: str) -> Optional[Dict[str, Any]]:
        """
        🗓️ CONVIERTE EDAD A RANGO DE FECHAS
        """
        try:
            from datetime import datetime, timedelta
            
            edad = int(edad_str)
            hoy = datetime.now()
            
            # Calcular rango de fechas para la edad
            fecha_max = hoy - timedelta(days=edad * 365)
            fecha_min = hoy - timedelta(days=(edad + 1) * 365)
            
            # Por simplicidad, usar solo año
            año_nacimiento = fecha_max.year
            
            return {
                "tabla": tabla,
                "campo": "fecha_nacimiento",
                "operador": "LIKE",
                "valor": f"%{año_nacimiento}%"
            }
            
        except (ValueError, Exception) as e:
            self.logger.error(f"Error convirtiendo edad a fecha: {e}")
            return None
    
    def _find_similar_field(self, campo: str, available_fields: List[str]) -> Optional[str]:
        """
        🔍 ENCUENTRA CAMPO SIMILAR USANDO LÓGICA DIFUSA
        """
        try:
            campo_lower = campo.lower()
            
            # Buscar coincidencias parciales
            for field in available_fields:
                field_lower = field.lower()
                
                # Coincidencia exacta
                if campo_lower == field_lower:
                    return field
                
                # Coincidencia parcial
                if campo_lower in field_lower or field_lower in campo_lower:
                    return field
                
                # Coincidencias específicas
                if campo_lower in ["apellido", "apellidos"] and "nombre" in field_lower:
                    return field
                if campo_lower in ["cedula", "documento"] and "curp" in field_lower:
                    return field
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error buscando campo similar: {e}")
            return None
    
    def _map_table(self, tabla: str) -> Optional[str]:
        """
        🗂️ MAPEA NOMBRE DE TABLA A TABLA REAL
        """
        table_mappings = {
            "estudiantes": "alumnos",
            "alumnado": "alumnos",
            "estudiante": "alumnos",
            "alumno": "alumnos",
            "datos": "datos_escolares",
            "escolares": "datos_escolares",
            "academicos": "datos_escolares",
            "notas": "calificaciones",
            "grades": "calificaciones"
        }
        
        return table_mappings.get(tabla.lower())
    
    def _normalize_field_value(self, campo: str, valor: str) -> str:
        """
        🔧 NORMALIZA VALORES SEGÚN EL CAMPO PARA COINCIDIR CON LA BASE DE DATOS

        Args:
            campo: Nombre del campo
            valor: Valor a normalizar

        Returns:
            Valor normalizado según las reglas del campo
        """
        if not isinstance(valor, str):
            return str(valor)

        # Campos que deben estar en MAYÚSCULAS (como están en la DB)
        uppercase_fields = {
            'nombre', 'curp', 'grupo', 'turno', 'escuela', 'cct'
        }

        # Campos que deben mantener formato específico
        if campo.lower() in uppercase_fields:
            # Normalizar a mayúsculas y limpiar espacios extra
            normalized = valor.strip().upper()
            self.logger.info(f"🔧 Normalizado '{campo}': '{valor}' → '{normalized}'")
            return normalized

        # Para otros campos, solo limpiar espacios
        return valor.strip()

    def _get_database_structure(self) -> Dict[str, Any]:
        """
        📊 OBTIENE ESTRUCTURA DE LA BASE DE DATOS (CON CACHE)
        """
        if self._structure_cache is None:
            self._structure_cache = self.database_analyzer.get_database_structure()
        return self._structure_cache
    
    def get_available_fields(self, tabla: str = "alumnos") -> List[str]:
        """
        📋 OBTIENE LISTA DE CAMPOS DISPONIBLES PARA UNA TABLA
        """
        structure = self._get_database_structure()
        return list(structure.get("tables", {}).get(tabla, {}).get("columns", {}).keys())
    
    def suggest_fields(self, partial_field: str, tabla: str = "alumnos") -> List[str]:
        """
        💡 SUGIERE CAMPOS BASADO EN ENTRADA PARCIAL
        """
        available_fields = self.get_available_fields(tabla)
        suggestions = []
        
        partial_lower = partial_field.lower()
        
        for field in available_fields:
            if partial_lower in field.lower():
                suggestions.append(field)
        
        return suggestions[:5]  # Máximo 5 sugerencias
