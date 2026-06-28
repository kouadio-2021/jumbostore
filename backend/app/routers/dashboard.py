from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appel_offres import AppelOffres
from app.models.soumission import Soumission
from app.schemas.appel_offres import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Tableau de Bord"])


@router.get("/stats", response_model=DashboardStats)
def obtenir_statistiques(db: Session = Depends(get_db)):
    nombre_appels = db.query(AppelOffres).count()
    nombre_soumissions = db.query(Soumission).count()

    total_avec_analyse = db.query(AppelOffres).filter(AppelOffres.score_compatibilite.isnot(None)).count()
    conformes = db.query(AppelOffres).filter(AppelOffres.score_compatibilite >= 55).count()
    taux_conformite = round((conformes / total_avec_analyse * 100), 1) if total_avec_analyse else 0.0

    marches_gagnes = db.query(AppelOffres).filter(AppelOffres.statut == "gagne").count()

    ca_potentiel = db.query(func.sum(AppelOffres.montant_estimatif)).filter(
        AppelOffres.statut.in_(["en_preparation", "soumis", "en_analyse", "nouveau"])
    ).scalar() or 0.0

    par_categorie_raw = db.query(AppelOffres.categorie, func.count(AppelOffres.id)).group_by(AppelOffres.categorie).all()
    appels_par_categorie = {str(cat.value if hasattr(cat, "value") else cat): count for cat, count in par_categorie_raw}

    par_statut_raw = db.query(AppelOffres.statut, func.count(AppelOffres.id)).group_by(AppelOffres.statut).all()
    appels_par_statut = {str(s.value if hasattr(s, "value") else s): count for s, count in par_statut_raw}

    return DashboardStats(
        nombre_appels_detectes=nombre_appels,
        nombre_soumissions=nombre_soumissions,
        taux_conformite=taux_conformite,
        marches_gagnes=marches_gagnes,
        chiffre_affaires_potentiel=ca_potentiel,
        appels_par_categorie=appels_par_categorie,
        appels_par_statut=appels_par_statut,
    )
