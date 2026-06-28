import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.facture import Facture, LigneFacture, TypeFacture
from app.schemas.facture import FactureOut, FactureCreate

router = APIRouter(prefix="/api/factures", tags=["Facturation"])


def _generer_numero(type_document: str) -> str:
    prefixes = {
        "Proforma": "PRO",
        "Facture": "FAC",
        "Devis": "DEV",
        "Bon de commande": "BC",
    }
    prefixe = prefixes.get(type_document, "DOC")
    return f"{prefixe}-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"


@router.get("", response_model=list[FactureOut])
def lister_factures(db: Session = Depends(get_db)):
    return db.query(Facture).order_by(Facture.date_emission.desc()).all()


@router.get("/{facture_id}", response_model=FactureOut)
def obtenir_facture(facture_id: int, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return facture


@router.post("", response_model=FactureOut)
def creer_facture(payload: FactureCreate, db: Session = Depends(get_db)):
    montant_ht = sum(l.quantite * l.prix_unitaire for l in payload.lignes)
    montant_ttc = montant_ht * (1 + payload.tva_taux / 100)

    facture = Facture(
        numero=_generer_numero(payload.type_document),
        type_document=payload.type_document,
        client_nom=payload.client_nom,
        client_adresse=payload.client_adresse,
        montant_ht=montant_ht,
        tva_taux=payload.tva_taux,
        montant_ttc=montant_ttc,
        date_echeance=payload.date_echeance,
    )
    db.add(facture)
    db.commit()
    db.refresh(facture)

    for ligne in payload.lignes:
        lf = LigneFacture(
            facture_id=facture.id,
            designation=ligne.designation,
            quantite=ligne.quantite,
            prix_unitaire=ligne.prix_unitaire,
            montant=ligne.quantite * ligne.prix_unitaire,
        )
        db.add(lf)
    db.commit()
    db.refresh(facture)
    return facture


@router.patch("/{facture_id}/statut", response_model=FactureOut)
def changer_statut_facture(facture_id: int, statut: str, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    facture.statut = statut
    db.commit()
    db.refresh(facture)
    return facture
