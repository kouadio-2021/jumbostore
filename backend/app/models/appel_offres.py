"""
Module Veille Marchés : appels d'offres collectés automatiquement.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class CategorieAO(str, enum.Enum):
    BTP = "BTP"
    INFORMATIQUE = "Informatique"
    FOURNITURES = "Fournitures"
    ELECTRICITE = "Électricité"
    HYDRAULIQUE = "Hydraulique"
    SECURITE = "Sécurité"
    TRANSPORT = "Transport"


class TypeAvis(str, enum.Enum):
    APPEL_OFFRES = "Appel d'offres"
    MANIFESTATION_INTERET = "Manifestation d'intérêt"
    DEMANDE_COTATION = "Demande de cotation"
    CONSULTATION_RESTREINTE = "Consultation restreinte"


class StatutAO(str, enum.Enum):
    NOUVEAU = "nouveau"
    EN_ANALYSE = "en_analyse"
    EN_PREPARATION = "en_preparation"
    SOUMIS = "soumis"
    GAGNE = "gagne"
    PERDU = "perdu"
    ARCHIVE = "archive"


class AppelOffres(Base):
    __tablename__ = "appels_offres"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, index=True, nullable=False)
    objet = Column(Text, nullable=False)
    source = Column(String, nullable=False)  # ex: ANRMP, Mairie de Cocody, FAO, etc.
    type_avis = Column(Enum(TypeAvis), default=TypeAvis.APPEL_OFFRES)
    categorie = Column(Enum(CategorieAO), default=CategorieAO.BTP)
    date_publication = Column(DateTime, nullable=False)
    date_limite = Column(DateTime, nullable=False)
    montant_estimatif = Column(Float, nullable=True)
    devise = Column(String, default="FCFA")
    statut = Column(Enum(StatutAO), default=StatutAO.NOUVEAU)
    url_source = Column(String, nullable=True)
    document_url = Column(String, nullable=True)
    score_compatibilite = Column(Float, nullable=True)  # rempli après analyse DAO
    date_collecte = Column(DateTime, default=datetime.utcnow)

    analyse = relationship("AnalyseDAO", back_populates="appel_offres", uselist=False)
    soumission = relationship("Soumission", back_populates="appel_offres", uselist=False)
