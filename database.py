from pymongo import MongoClient
from config import Config

_client = None
_db = None

def init_db():
    """
    Inicializa la conexión a la base de datos de MongoDB una sola vez.
    """
    global _client, _db
    if _client is None: # Solo inicializar si no se ha inicializado ya
        _client = MongoClient(Config.MONGO_URI)
        _db = _client[Config.MONGO_DB_NAME]
    
def get_db():
    """
    Retorna la instancia de la base de datos de MongoDB.
    Inicializa la conexión si aún no se ha hecho.
    """
    global _client, _db
    if _db is None:
        _client = MongoClient(Config.MONGO_URI)
        _db = _client[Config.MONGO_DB_NAME]
    return _db
