"""
Module Analyse des DAO : extraction intelligente et score de compatibilité.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class ConformiteEnum(str, enum.Enum):
    CONFORME = "Conforme"
    CONFORME_RESERVES = "Conforme avec réserves"
    NON_CONFORME = "Non conforme"


class AnalyseDAO(Base):
    __tablename__ = "analyses_dao"

    id = Column(Integer, primary_key=True, index=True)
    appel_offres_id = Column(Integer, ForeignKey("appels_offres.id"), nullable=False)

    conditions_administratives = Column(Text, nullable=True)  # JSON texte
    criteres_techniques = Column(Text, nullable=True)
    criteres_financiers = Column(Text, nullable=True)
    delais = Column(Text, nullable=True)

    score_compatibilite = Column(Float, default=0.0)  # 0-100
    conformite = Column(Enum(ConformiteEnum), default=ConformiteEnum.CONFORME_RESERVES)
    points_attention = Column(Text, nullable=True)  # JSON liste des réserves/risques
    documents_requis = Column(Text, nullable=True)  # JSON liste

    date_analyse = Column(DateTime, default=datetime.utcnow)

    appel_offres = relationship("AppelOffres", back_populates="analyse")
