from src.kmsConfig import get_kms
from .config import  ENV, DKMS_RDS_SECRET, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from urllib.parse import quote_plus

kms_client = get_kms()

# Default local
database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


if ENV in ("production", "staging"):
    secret_json = kms_client.get_secret_data(DKMS_RDS_SECRET)
    secret = json.loads(secret_json)
    password = quote_plus(secret['AccountPassword'])
    database_url = f"mysql+pymysql://{secret['AccountName']}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


uatConnectionPool = {
# Docker only 1 G memory, so set the pool size to 5
    "pool_size": 5,
    "max_overflow": 10,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "pool_timeout": 30,
    "echo_pool": True
}

engine = create_engine(database_url,
       **uatConnectionPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()