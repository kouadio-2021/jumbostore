"""
Module Notifications + Journal d'actions (traçabilité / sécurité).
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class CanalNotification(str, enum.Enum):
    WHATSAPP = "WhatsApp"
    EMAIL = "Email"
    SMS = "SMS"
    TELEGRAM = "Telegram"
    SYSTEME = "Système"


class TypeNotification(str, enum.Enum):
    NOUVEL_AO = "Nouvel appel d'offres"
    DATE_LIMITE_PROCHE = "Date limite proche"
    PIECE_MANQUANTE = "Pièce manquante"
    SOUMISSION_VALIDEE = "Soumission validée"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type_notification = Column(Enum(TypeNotification), nullable=False)
    canal = Column(Enum(CanalNotification), default=CanalNotification.SYSTEME)
    titre = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    lue = Column(Boolean, default=False)
    lien_ressource = Column(String, nullable=True)  # ex: /appels-offres/12
    date_creation = Column(DateTime, default=datetime.utcnow)


class JournalAction(Base):
    __tablename__ = "journal_actions"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    date_action = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("User", back_populates="actions")
