"""
Module Génération Automatique : soumissions et documents produits
(offre technique, offre financière, documents administratifs).
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class StatutSoumission(str, enum.Enum):
    BROUILLON = "brouillon"
    EN_COURS = "en_cours"
    COMPLETE = "complete"
    VALIDEE = "validee"
    DEPOSEE = "deposee"


class Soumission(Base):
    __tablename__ = "soumissions"

    id = Column(Integer, primary_key=True, index=True)
    appel_offres_id = Column(Integer, ForeignKey("appels_offres.id"), nullable=True)
    entreprise_id = Column(Integer, ForeignKey("entreprise_profile.id"), nullable=False)

    # Si la soumission concerne un AO trouvé par vous-même (hors collecte automatique),
    # ces champs permettent de le décrire manuellement (appel_offres_id reste alors NULL).
    objet_externe = Column(String, nullable=True)
    source_externe = Column(String, nullable=True)

    statut = Column(Enum(StatutSoumission), default=StatutSoumission.BROUILLON)
    montant_propose = Column(Float, nullable=True)
    methodologie_resume = Column(Text, nullable=True)
    planning_resume = Column(Text, nullable=True)
    cahier_des_charges_texte = Column(Text, nullable=True)  # Texte brut extrait du PDF du DAO/cahier des charges
    documents_requis_json = Column(Text, nullable=True)  # Liste JSON des documents identifiés par l'IA comme requis
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_validation = Column(DateTime, nullable=True)
    valide_par = Column(String, nullable=True)

    appel_offres = relationship("AppelOffres", back_populates="soumission")
    entreprise = relationship("EntrepriseProfile")
    documents = relationship("DocumentGenere", back_populates="soumission")

    @property
    def objet(self) -> str:
        """Objet du marché, qu'il vienne d'un AO collecté ou saisi manuellement."""
        if self.appel_offres:
            return self.appel_offres.objet
        return self.objet_externe or "Objet non renseigné"


class DocumentGenere(Base):
    __tablename__ = "documents_generes"

    id = Column(Integer, primary_key=True, index=True)
    soumission_id = Column(Integer, ForeignKey("soumissions.id"), nullable=False)
    type_document = Column(String, nullable=False)
    # ex: "Offre Technique", "Offre Financière", "Lettre de soumission",
    # "Déclaration d'engagement", "Bordereau des prix", "DQE"
    format_fichier = Column(String, default="PDF")  # PDF, DOCX, XLSX
    nom_fichier = Column(String, nullable=False)
    chemin_fichier = Column(String, nullable=True)
    date_generation = Column(DateTime, default=datetime.utcnow)

    soumission = relationship("Soumission", back_populates="documents")
