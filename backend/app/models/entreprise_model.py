"""
Module Profil Entreprise : documents légaux, analyse IA de capacité.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class EntrepriseProfile(Base):
    __tablename__ = "entreprise_profile"

    id = Column(Integer, primary_key=True, index=True)
    raison_sociale = Column(String, nullable=False)
    rccm = Column(String, nullable=True)
    dfe = Column(String, nullable=True)
    cnps = Column(String, nullable=True)
    attestation_fiscale = Column(String, nullable=True)
    capacite_financiere = Column(Float, default=0.0)  # en FCFA, estimation IA
    capacite_technique_score = Column(Float, default=0.0)  # 0-100
    domaines_expertise = Column(Text, nullable=True)  # JSON liste sous forme texte
    secteurs = Column(Text, nullable=True)
    adresse = Column(String, nullable=True)
    date_maj = Column(DateTime, default=datetime.utcnow)

    documents = relationship("DocumentEntreprise", back_populates="profile")
    references_techniques = relationship("ReferenceTechnique", back_populates="profile")


class DocumentEntreprise(Base):
    __tablename__ = "documents_entreprise"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("entreprise_profile.id"), nullable=False)
    type_document = Column(String, nullable=False)  # RCCM, DFE, CNPS, Attestation fiscale, Agrément, etc.
    nom_fichier = Column(String, nullable=False)
    chemin_fichier = Column(String, nullable=True)  # Chemin réel du fichier uploadé sur le disque
    statut = Column(String, default="valide")  # valide, expire, manquant
    date_expiration = Column(DateTime, nullable=True)
    date_ajout = Column(DateTime, default=datetime.utcnow)

    profile = relationship("EntrepriseProfile", back_populates="documents")


class ReferenceTechnique(Base):
    __tablename__ = "references_techniques"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("entreprise_profile.id"), nullable=False)
    intitule_projet = Column(String, nullable=False)
    client = Column(String, nullable=False)
    montant = Column(Float, nullable=True)
    annee = Column(Integer, nullable=True)
    secteur = Column(String, nullable=True)

    profile = relationship("EntrepriseProfile", back_populates="references_techniques")
