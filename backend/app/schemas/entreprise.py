from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class DocumentEntrepriseOut(BaseModel):
    id: int
    type_document: str
    nom_fichier: str
    statut: str
    date_expiration: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReferenceTechniqueOut(BaseModel):
    id: int
    intitule_projet: str
    client: str
    montant: Optional[float] = None
    annee: Optional[int] = None
    secteur: Optional[str] = None

    class Config:
        from_attributes = True


class EntrepriseProfileOut(BaseModel):
    id: int
    raison_sociale: str
    rccm: Optional[str] = None
    dfe: Optional[str] = None
    cnps: Optional[str] = None
    attestation_fiscale: Optional[str] = None
    capacite_financiere: float
    capacite_technique_score: float
    domaines_expertise: Optional[str] = None
    secteurs: Optional[str] = None
    adresse: Optional[str] = None
    documents: List[DocumentEntrepriseOut] = []
    references_techniques: List[ReferenceTechniqueOut] = []

    class Config:
        from_attributes = True


class EntrepriseProfileCreate(BaseModel):
    raison_sociale: str
    rccm: Optional[str] = None
    dfe: Optional[str] = None
    cnps: Optional[str] = None
    attestation_fiscale: Optional[str] = None
    adresse: Optional[str] = None
    domaines_expertise: Optional[List[str]] = None
    secteurs: Optional[List[str]] = None


class EntrepriseProfileUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    rccm: Optional[str] = None
    dfe: Optional[str] = None
    cnps: Optional[str] = None
    attestation_fiscale: Optional[str] = None
    adresse: Optional[str] = None
    domaines_expertise: Optional[List[str]] = None
    secteurs: Optional[List[str]] = None


class AnalyseDAOOut(BaseModel):
    id: int
    appel_offres_id: int
    conditions_administratives: Optional[str] = None
    criteres_techniques: Optional[str] = None
    criteres_financiers: Optional[str] = None
    delais: Optional[str] = None
    score_compatibilite: float
    conformite: str
    points_attention: Optional[str] = None
    documents_requis: Optional[str] = None
    date_analyse: datetime

    class Config:
        from_attributes = True


class AnalyseDAORequest(BaseModel):
    appel_offres_id: int
