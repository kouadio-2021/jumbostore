"""
Modèle Utilisateur avec gestion des rôles :
Administrateur Général, Directeur, Chargé d'Appels d'Offres, Comptabilité.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class RoleEnum(str, enum.Enum):
    ADMIN = "administrateur_general"
    DIRECTEUR = "directeur"
    CHARGE_AO = "charge_appels_offres"
    COMPTABILITE = "comptabilite"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom_complet = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.CHARGE_AO)
    actif = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.utcnow)

    actions = relationship("JournalAction", back_populates="utilisateur")
