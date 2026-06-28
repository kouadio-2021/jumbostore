from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class LigneFactureCreate(BaseModel):
    designation: str
    quantite: float = 1.0
    prix_unitaire: float = 0.0


class FactureCreate(BaseModel):
    type_document: str
    client_nom: str
    client_adresse: Optional[str] = None
    tva_taux: float = 18.0
    date_echeance: Optional[datetime] = None
    lignes: List[LigneFactureCreate]


class LigneFactureOut(BaseModel):
    id: int
    designation: str
    quantite: float
    prix_unitaire: float
    montant: float

    class Config:
        from_attributes = True


class FactureOut(BaseModel):
    id: int
    numero: str
    type_document: str
    client_nom: str
    client_adresse: Optional[str] = None
    montant_ht: float
    tva_taux: float
    montant_ttc: float
    statut: str
    date_emission: datetime
    date_echeance: Optional[datetime] = None
    lignes: List[LigneFactureOut] = []

    class Config:
        from_attributes = True
