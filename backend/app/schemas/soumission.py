from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class DocumentGenereOut(BaseModel):
    id: int
    type_document: str
    format_fichier: str
    nom_fichier: str
    date_generation: datetime

    class Config:
        from_attributes = True


class SoumissionCreate(BaseModel):
    entreprise_id: int
    appel_offres_id: Optional[int] = None
    # Si appel_offres_id n'est pas fourni : décrire manuellement l'AO trouvé par vous-même
    objet_externe: Optional[str] = None
    source_externe: Optional[str] = None
    montant_propose: Optional[float] = None
    methodologie_resume: Optional[str] = None
    planning_resume: Optional[str] = None


class SoumissionOut(BaseModel):
    id: int
    entreprise_id: int
    appel_offres_id: Optional[int] = None
    objet_externe: Optional[str] = None
    source_externe: Optional[str] = None
    statut: str
    montant_propose: Optional[float] = None
    methodologie_resume: Optional[str] = None
    planning_resume: Optional[str] = None
    date_creation: datetime
    date_validation: Optional[datetime] = None
    valide_par: Optional[str] = None
    documents: List[DocumentGenereOut] = []

    class Config:
        from_attributes = True


class GenererDocumentsRequest(BaseModel):
    soumission_id: int
    types_documents: List[str]  # ex: ["Offre Technique", "Offre Financière", "Lettre de soumission"]
