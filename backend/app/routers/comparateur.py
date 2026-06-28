from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.comparateur import RechercheProduit
from app.schemas.comparateur import RechercheProduitOut, RechercheProduitCreate
from app.services.comparateur_service import comparer_fournisseurs, extraire_quantite

router = APIRouter(prefix="/api/comparateur", tags=["Comparateur de Prix"])


@router.post("/rechercher", response_model=RechercheProduitOut)
def rechercher_prix(payload: RechercheProduitCreate, db: Session = Depends(get_db)):
    quantite = extraire_quantite(payload.designation, payload.quantite)
    recherche = comparer_fournisseurs(db, payload.designation, quantite)
    return recherche


@router.get("/historique", response_model=list[RechercheProduitOut])
def historique_recherches(db: Session = Depends(get_db)):
    return db.query(RechercheProduit).order_by(RechercheProduit.date_recherche.desc()).limit(20).all()


@router.get("/{recherche_id}", response_model=RechercheProduitOut)
def obtenir_recherche(recherche_id: int, db: Session = Depends(get_db)):
    recherche = db.query(RechercheProduit).filter(RechercheProduit.id == recherche_id).first()
    if not recherche:
        raise HTTPException(status_code=404, detail="Recherche non trouvée")
    return recherche
