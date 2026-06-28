from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appel_offres import AppelOffres
from app.schemas.appel_offres import AppelOffresOut, AppelOffresCreate, AppelOffresStatutUpdate
from app.services.scraping_service import collecter_toutes_sources

router = APIRouter(prefix="/api/appels-offres", tags=["Veille Marchés"])


@router.post("/collecter")
def lancer_collecte(db: Session = Depends(get_db)):
    """
    Déclenche une collecte réelle des appels d'offres depuis les sources
    configurées (ARCOP pour l'instant). Retourne un résumé par source.
    """
    resultats = collecter_toutes_sources(db)
    return {"resultats": resultats}


@router.get("", response_model=list[AppelOffresOut])
def lister_appels_offres(
    categorie: Optional[str] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(AppelOffres)
    if categorie:
        query = query.filter(AppelOffres.categorie == categorie)
    if statut:
        query = query.filter(AppelOffres.statut == statut)
    return query.order_by(AppelOffres.date_limite.asc()).all()


@router.get("/{ao_id}", response_model=AppelOffresOut)
def obtenir_appel_offres(ao_id: int, db: Session = Depends(get_db)):
    ao = db.query(AppelOffres).filter(AppelOffres.id == ao_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres non trouvé")
    return ao


@router.post("", response_model=AppelOffresOut)
def creer_appel_offres(payload: AppelOffresCreate, db: Session = Depends(get_db)):
    import re
    ref_existe = db.query(AppelOffres).filter(AppelOffres.reference == payload.reference).first()
    if ref_existe:
        raise HTTPException(status_code=400, detail="Cette référence existe déjà")

    ao = AppelOffres(**payload.model_dump())
    db.add(ao)
    db.commit()
    db.refresh(ao)
    return ao


@router.patch("/{ao_id}/statut", response_model=AppelOffresOut)
def changer_statut(ao_id: int, payload: AppelOffresStatutUpdate, db: Session = Depends(get_db)):
    ao = db.query(AppelOffres).filter(AppelOffres.id == ao_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres non trouvé")
    ao.statut = payload.statut
    db.commit()
    db.refresh(ao)
    return ao


@router.delete("/{ao_id}")
def archiver_appel_offres(ao_id: int, db: Session = Depends(get_db)):
    ao = db.query(AppelOffres).filter(AppelOffres.id == ao_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres non trouvé")
    ao.statut = "archive"
    db.commit()
    return {"message": "Appel d'offres archivé"}
