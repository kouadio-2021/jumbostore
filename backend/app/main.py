"""
JUMBOSTORE — Point d'entrée principal de l'API FastAPI.
Plateforme intelligente de veille marchés et gestion des appels d'offres
pour Jumbo Store SARL (BTP & fournitures diverses, Côte d'Ivoire).
"""
from dotenv import load_dotenv
load_dotenv()  # Charge les variables du fichier .env (GEMINI_API_KEY, etc.) avant tout le reste

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, CORS_ORIGINS
from app.database import Base, engine
from app import models  # noqa: F401 - assure l'enregistrement de tous les modèles
from app.routers import auth, appels_offres, entreprise, soumissions, comparateur, factures, notifications, dashboard
from app.seed_data import seed

app = FastAPI(
    title=APP_NAME,
    description="API de la plateforme intelligente JUMBOSTORE — veille marchés, analyse DAO, génération automatique de documents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def on_startup():
    seed()


app.include_router(auth.router)
app.include_router(appels_offres.router)
app.include_router(entreprise.router)
app.include_router(soumissions.router)
app.include_router(comparateur.router)
app.include_router(factures.router)
app.include_router(notifications.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "JUMBOSTORE API — opérationnelle", "docs": "/docs"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
