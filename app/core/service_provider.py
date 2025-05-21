"""
Proveedor centralizado de servicios para la aplicación
"""
import sqlite3
from app.services.alumno_service import AlumnoService
from app.services.constancia_service import ConstanciaService
from app.core.config import Config

class ServiceProvider:
    """Clase que proporciona acceso centralizado a los servicios de la aplicación"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Obtiene la instancia única del proveedor de servicios (patrón Singleton)"""
        if cls._instance is None:
            cls._instance = ServiceProvider()
        return cls._instance
    
    def __init__(self):
        """Inicializa los servicios"""
        # Crear una única conexión a la base de datos que será compartida por todos los servicios
        self.db_connection = sqlite3.connect(Config.DB_PATH)
        self.db_connection.row_factory = sqlite3.Row
        
        # Inicializar servicios como None para crearlos bajo demanda
        self._alumno_service = None
        self._constancia_service = None
    
    @property
    def alumno_service(self):
        """Obtiene el servicio de alumnos"""
        if self._alumno_service is None:
            self._alumno_service = AlumnoService(db_connection=self.db_connection)
        return self._alumno_service
    
    @property
    def constancia_service(self):
        """Obtiene el servicio de constancias"""
        if self._constancia_service is None:
            self._constancia_service = ConstanciaService(db_connection=self.db_connection)
        return self._constancia_service
    
    def close(self):
        """Cierra todas las conexiones de servicios"""
        if self.db_connection:
            self.db_connection.close()
