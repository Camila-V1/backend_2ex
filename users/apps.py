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
            import json
            
            # Verificar si ya está inicializado
            if firebase_admin._apps:
                logger.info("✅ Firebase ya está inicializado")
                settings.FIREBASE_INITIALIZED = True
                return
            
            cred = None
            project_id = None
            
            # OPCIÓN 1: Leer desde variable de entorno FIREBASE_CREDENTIALS (PRODUCCIÓN)
            firebase_creds_json = os.getenv('FIREBASE_CREDENTIALS')
            
            if firebase_creds_json:
                try:
                    logger.info("🔍 Intentando cargar Firebase desde variable de entorno FIREBASE_CREDENTIALS...")
                    cred_dict = json.loads(firebase_creds_json)
                    project_id = cred_dict.get('project_id')
                    
                    # Validar que no sea placeholder
                    if project_id == 'TU-PROJECT-ID-AQUI':
                        logger.warning("⚠️ FIREBASE_CREDENTIALS contiene valores placeholder")
                        settings.FIREBASE_INITIALIZED = False
                        return
                    
                    cred = credentials.Certificate(cred_dict)
                    logger.info(f"✅ Credenciales cargadas desde FIREBASE_CREDENTIALS env var para proyecto: {project_id}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Error al parsear FIREBASE_CREDENTIALS JSON: {e}")
                    settings.FIREBASE_INITIALIZED = False
                    return
                except Exception as e:
                    logger.error(f"❌ Error al procesar FIREBASE_CREDENTIALS: {e}")
                    settings.FIREBASE_INITIALIZED = False
                    return
            
            # OPCIÓN 2: Leer desde archivo local (DESARROLLO)
            else:
                logger.info("🔍 Variable FIREBASE_CREDENTIALS no encontrada, intentando archivo local...")
                cred_path = settings.FIREBASE_CREDENTIALS_PATH
                
                if not os.path.exists(cred_path):
                    logger.warning(f"⚠️ Archivo de credenciales Firebase no encontrado en: {cred_path}")
                    logger.warning("Las notificaciones push NO funcionarán hasta que configures:")
                    logger.warning("1. Variable de entorno FIREBASE_CREDENTIALS (producción)")
                    logger.warning("2. O archivo firebase_credentials.json (desarrollo)")
                    settings.FIREBASE_INITIALIZED = False
                    return
                
                # Leer y validar archivo
                with open(cred_path, 'r') as f:
                    data = json.load(f)
                    project_id = data.get('project_id')
                    
                    if project_id == 'TU-PROJECT-ID-AQUI':
                        logger.warning("⚠️ firebase_credentials.json contiene valores placeholder")
                        logger.warning("Reemplaza el archivo con tus credenciales reales de Firebase")
                        settings.FIREBASE_INITIALIZED = False
                        return
                
                cred = credentials.Certificate(cred_path)
                logger.info(f"✅ Credenciales cargadas desde archivo local para proyecto: {project_id}")
            
            # Inicializar Firebase con las credenciales obtenidas
            if cred:
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase Admin SDK inicializado correctamente")
                logger.info(f"📱 Notificaciones push ACTIVAS para proyecto: {project_id}")
                settings.FIREBASE_INITIALIZED = True
            else:
                logger.error("❌ No se pudieron obtener credenciales de Firebase")
                settings.FIREBASE_INITIALIZED = False
            
        except ImportError:
            logger.warning("⚠️ firebase-admin no está instalado")
            logger.warning("Instala con: pip install firebase-admin")
            settings.FIREBASE_INITIALIZED = False
        except Exception as e:
            logger.error(f"❌ Error al inicializar Firebase: {e}")
            settings.FIREBASE_INITIALIZED = False
