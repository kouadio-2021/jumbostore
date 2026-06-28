from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class RechercheProduitCreate(BaseModel):
    designation: str
    quantite: int = 1


class OffreFournisseurOut(BaseModel):
    id: int
    nom_fournisseur: str
    type_fournisseur: str
    prix_unitaire: float
    prix_total: float
    devise: str
    delai_livraison_jours: Optional[int] = None
    garantie_mois: Optional[int] = None
    note_avantage: float
    lien_achat: Optional[str] = None
    source_site: Optional[str] = None

    class Config:
        from_attributes = True


class RechercheProduitOut(BaseModel):
    id: int
    designation: str
    quantite: int
    date_recherche: datetime
    offres: List[OffreFournisseurOut] = []

    class Config:
        from_attributes = True
