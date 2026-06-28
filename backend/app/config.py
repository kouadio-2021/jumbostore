"""
Configuration centrale de JUMBOSTORE.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "app" / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR}/jumbostore.db"

SECRET_KEY = os.environ.get("JUMBOSTORE_SECRET_KEY", "jumbostore-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12h

APP_NAME = "JUMBOSTORE"
COMPANY_NAME = "Jumbo Store SARL"

# CORS - autoriser le frontend en dev et en production (à restreindre en prod réelle)
CORS_ORIGINS = ["*"]
