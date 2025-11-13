import os
import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """Se ejecuta cuando la aplicación está lista"""
        # Inicializar Firebase Admin SDK
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializa Firebase Admin SDK si las credenciales existen"""
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            # Verificar si ya está inicializado
            if firebase_admin._apps:
                logger.info("✅ Firebase ya está inicializado")
                settings.FIREBASE_INITIALIZED = True
                return
            
            # Verificar si existe el archivo de credenciales
            cred_path = settings.FIREBASE_CREDENTIALS_PATH
            
            if not os.path.exists(cred_path):
                logger.warning(f"⚠️ Archivo de credenciales Firebase no encontrado en: {cred_path}")
                logger.warning("Las notificaciones push NO funcionarán hasta que configures firebase_credentials.json")
                settings.FIREBASE_INITIALIZED = False
                return
            
            # Verificar que no sea el archivo placeholder
            with open(cred_path, 'r') as f:
                import json
                data = json.load(f)
                if data.get('project_id') == 'TU-PROJECT-ID-AQUI':
                    logger.warning("⚠️ firebase_credentials.json contiene valores placeholder")
                    logger.warning("Reemplaza el archivo con tus credenciales reales de Firebase")
                    settings.FIREBASE_INITIALIZED = False
                    return
            
            # Inicializar Firebase con el archivo de credenciales
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            logger.info("✅ Firebase Admin SDK inicializado correctamente")
            logger.info(f"📱 Notificaciones push ACTIVAS para proyecto: {data.get('project_id')}")
            settings.FIREBASE_INITIALIZED = True
            
        except ImportError:
            logger.warning("⚠️ firebase-admin no está instalado")
            logger.warning("Instala con: pip install firebase-admin")
            settings.FIREBASE_INITIALIZED = False
        except Exception as e:
            logger.error(f"❌ Error al inicializar Firebase: {e}")
            settings.FIREBASE_INITIALIZED = False
