from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class NotificationOut(BaseModel):
    id: int
    type_notification: str
    canal: str
    titre: str
    message: str
    lue: bool
    lien_ressource: Optional[str] = None
    date_creation: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    nom_complet: str
    email: EmailStr
    password: str
    role: str = "charge_appels_offres"


class UserOut(BaseModel):
    id: int
    nom_complet: str
    email: str
    role: str
    actif: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
