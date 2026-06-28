"""
Module Comparateur de Prix : recherche fournisseurs et comparaison.
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class RechercheProduit(Base):
    __tablename__ = "recherches_produits"

    id = Column(Integer, primary_key=True, index=True)
    designation = Column(String, nullable=False)  # ex: "50 ordinateurs portables Dell"
    quantite = Column(Integer, default=1)
    date_recherche = Column(DateTime, default=datetime.utcnow)

    offres = relationship("OffreFournisseur", back_populates="recherche")


class OffreFournisseur(Base):
    __tablename__ = "offres_fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    recherche_id = Column(Integer, ForeignKey("recherches_produits.id"), nullable=False)
    nom_fournisseur = Column(String, nullable=False)
    type_fournisseur = Column(String, default="local")  # local, international, distributeur_agree
    prix_unitaire = Column(Float, nullable=False)
    prix_total = Column(Float, nullable=False)
    devise = Column(String, default="FCFA")
    delai_livraison_jours = Column(Integer, nullable=True)
    garantie_mois = Column(Integer, nullable=True)
    note_avantage = Column(Float, default=0.0)  # score global combinant prix/délai/garantie
    lien_achat = Column(String, nullable=True)  # URL directe vers la page produit pour achat
    source_site = Column(String, nullable=True)  # ex: "Jumia.ci"

    recherche = relationship("RechercheProduit", back_populates="offres")
