"""
Module Facturation : proforma, factures, devis, bons de commande.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class TypeFacture(str, enum.Enum):
    PROFORMA = "Proforma"
    FACTURE = "Facture"
    DEVIS = "Devis"
    BON_COMMANDE = "Bon de commande"


class StatutFacture(str, enum.Enum):
    BROUILLON = "brouillon"
    ENVOYE = "envoye"
    PAYE = "paye"
    EN_RETARD = "en_retard"
    ANNULE = "annule"


class Facture(Base):
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True, nullable=False)
    type_document = Column(Enum(TypeFacture), default=TypeFacture.PROFORMA)
    client_nom = Column(String, nullable=False)
    client_adresse = Column(String, nullable=True)
    montant_ht = Column(Float, default=0.0)
    tva_taux = Column(Float, default=18.0)
    montant_ttc = Column(Float, default=0.0)
    statut = Column(Enum(StatutFacture), default=StatutFacture.BROUILLON)
    date_emission = Column(DateTime, default=datetime.utcnow)
    date_echeance = Column(DateTime, nullable=True)

    lignes = relationship("LigneFacture", back_populates="facture")


class LigneFacture(Base):
    __tablename__ = "lignes_facture"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id"), nullable=False)
    designation = Column(String, nullable=False)
    quantite = Column(Float, default=1.0)
    prix_unitaire = Column(Float, default=0.0)
    montant = Column(Float, default=0.0)

    facture = relationship("Facture", back_populates="lignes")
