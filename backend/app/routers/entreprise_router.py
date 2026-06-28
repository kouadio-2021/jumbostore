import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import DATA_DIR
from app.database import get_db
from app.models.entreprise import EntrepriseProfile, DocumentEntreprise
from app.models.appel_offres import AppelOffres
from app.models.analyse_dao import AnalyseDAO
from app.schemas.entreprise import (
    EntrepriseProfileOut,
    EntrepriseProfileCreate,
    EntrepriseProfileUpdate,
    AnalyseDAOOut,
    AnalyseDAORequest,
)
from app.services.analyse_service import analyser_dao

router = APIRouter(prefix="/api", tags=["Profil Entreprise & Analyse DAO"])

DOCUMENTS_ENTREPRISE_DIR = DATA_DIR / "documents_entreprise"
DOCUMENTS_ENTREPRISE_DIR.mkdir(exist_ok=True, parents=True)


@router.get("/entreprises", response_model=list[EntrepriseProfileOut])
def lister_entreprises(db: Session = Depends(get_db)):
    """Liste toutes les entreprises (profils) gérées par l'utilisateur."""
    return db.query(EntrepriseProfile).order_by(EntrepriseProfile.raison_sociale).all()


@router.get("/entreprises/{entreprise_id}", response_model=EntrepriseProfileOut)
def obtenir_entreprise(entreprise_id: int, db: Session = Depends(get_db)):
    profile = db.query(EntrepriseProfile).filter(EntrepriseProfile.id == entreprise_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    return profile


@router.post("/entreprises", response_model=EntrepriseProfileOut)
def creer_entreprise(payload: EntrepriseProfileCreate, db: Session = Depends(get_db)):
    """Crée un nouveau profil d'entreprise (vous pouvez en gérer plusieurs)."""
    profile = EntrepriseProfile(
        raison_sociale=payload.raison_sociale,
        rccm=payload.rccm,
        dfe=payload.dfe,
        cnps=payload.cnps,
        attestation_fiscale=payload.attestation_fiscale,
        adresse=payload.adresse,
        domaines_expertise=json.dumps(payload.domaines_expertise or [], ensure_ascii=False),
        secteurs=json.dumps(payload.secteurs or [], ensure_ascii=False),
        capacite_financiere=0.0,
        capacite_technique_score=0.0,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/entreprises/{entreprise_id}", response_model=EntrepriseProfileOut)
def modifier_entreprise(entreprise_id: int, payload: EntrepriseProfileUpdate, db: Session = Depends(get_db)):
    """Modifie les informations d'une entreprise existante (nom, RCCM, DFE, etc.)."""
    profile = db.query(EntrepriseProfile).filter(EntrepriseProfile.id == entreprise_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")

    donnees = payload.model_dump(exclude_unset=True)
    if "domaines_expertise" in donnees:
        donnees["domaines_expertise"] = json.dumps(donnees["domaines_expertise"] or [], ensure_ascii=False)
    if "secteurs" in donnees:
        donnees["secteurs"] = json.dumps(donnees["secteurs"] or [], ensure_ascii=False)

    for champ, valeur in donnees.items():
        setattr(profile, champ, valeur)
    profile.date_maj = datetime.utcnow()

    db.commit()
    db.refresh(profile)
    return profile


@router.delete("/entreprises/{entreprise_id}")
def supprimer_entreprise(entreprise_id: int, db: Session = Depends(get_db)):
    profile = db.query(EntrepriseProfile).filter(EntrepriseProfile.id == entreprise_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")
    db.delete(profile)
    db.commit()
    return {"detail": "Entreprise supprimée"}


@router.post("/entreprises/{entreprise_id}/documents")
async def uploader_document_entreprise(
    entreprise_id: int,
    type_document: str = Form(...),
    date_expiration: str | None = Form(None),
    fichier: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Uploade un vrai document (RCCM, DFE, CNPS, attestation fiscale, agrément...)
    pour une entreprise donnée. Le fichier est stocké réellement sur le disque.
    """
    profile = db.query(EntrepriseProfile).filter(EntrepriseProfile.id == entreprise_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Entreprise non trouvée")

    dossier_entreprise = DOCUMENTS_ENTREPRISE_DIR / str(entreprise_id)
    dossier_entreprise.mkdir(exist_ok=True, parents=True)

    chemin_fichier = dossier_entreprise / fichier.filename
    contenu = await fichier.read()
    chemin_fichier.write_bytes(contenu)

    date_exp = None
    if date_expiration:
        try:
            date_exp = datetime.strptime(date_expiration, "%Y-%m-%d")
        except ValueError:
            pass

    document = DocumentEntreprise(
        profile_id=entreprise_id,
        type_document=type_document,
        nom_fichier=fichier.filename,
        chemin_fichier=str(chemin_fichier),
        statut="valide",
        date_expiration=date_exp,
        date_ajout=datetime.utcnow(),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "type_document": document.type_document,
        "nom_fichier": document.nom_fichier,
        "statut": document.statut,
    }


@router.delete("/entreprises/documents/{document_id}")
def supprimer_document_entreprise(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentEntreprise).filter(DocumentEntreprise.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé")

    if document.chemin_fichier:
        chemin = Path(document.chemin_fichier)
        if chemin.exists():
            chemin.unlink()

    db.delete(document)
    db.commit()
    return {"detail": "Document supprimé"}


@router.post("/analyse-dao", response_model=AnalyseDAOOut)
def lancer_analyse_dao(payload: AnalyseDAORequest, db: Session = Depends(get_db)):
    ao = db.query(AppelOffres).filter(AppelOffres.id == payload.appel_offres_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres non trouvé")

    existante = db.query(AnalyseDAO).filter(AnalyseDAO.appel_offres_id == ao.id).first()
    if existante:
        return existante

    analyse = analyser_dao(db, ao)
    return analyse


@router.get("/analyse-dao/{ao_id}", response_model=AnalyseDAOOut)
def obtenir_analyse_dao(ao_id: int, db: Session = Depends(get_db)):
    analyse = db.query(AnalyseDAO).filter(AnalyseDAO.appel_offres_id == ao_id).first()
    if not analyse:
        raise HTTPException(status_code=404, detail="Aucune analyse trouvée pour cet appel d'offres")
    return analyse
