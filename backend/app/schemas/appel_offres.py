from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AppelOffresBase(BaseModel):
    reference: str
    objet: str
    source: str
    type_avis: str
    categorie: str
    date_publication: datetime
    date_limite: datetime
    montant_estimatif: Optional[float] = None
    devise: str = "FCFA"
    url_source: Optional[str] = None
    document_url: Optional[str] = None


class AppelOffresCreate(AppelOffresBase):
    pass


class AppelOffresOut(AppelOffresBase):
    id: int
    statut: str
    score_compatibilite: Optional[float] = None
    date_collecte: datetime

    class Config:
        from_attributes = True


class AppelOffresStatutUpdate(BaseModel):
    statut: str


class DashboardStats(BaseModel):
    nombre_appels_detectes: int
    nombre_soumissions: int
    taux_conformite: float
    marches_gagnes: int
    chiffre_affaires_potentiel: float
    appels_par_categorie: dict
    appels_par_statut: dict
