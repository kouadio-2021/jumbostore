import json
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.soumission import Soumission, DocumentGenere
from app.models.appel_offres import AppelOffres
from app.models.entreprise import EntrepriseProfile, ReferenceTechnique
from app.schemas.soumission import SoumissionOut, SoumissionCreate, GenererDocumentsRequest
from app.services.document_service import generer_document
from app.services.ia_redaction_service import (
    analyser_cahier_des_charges,
    generer_contenu_dao_complet,
    GeminiNonConfigure,
)

router = APIRouter(prefix="/api/soumissions", tags=["Génération Automatique"])


@router.get("", response_model=list[SoumissionOut])
def lister_soumissions(db: Session = Depends(get_db)):
    return db.query(Soumission).order_by(Soumission.date_creation.desc()).all()


@router.get("/{soumission_id}", response_model=SoumissionOut)
def obtenir_soumission(soumission_id: int, db: Session = Depends(get_db)):
    soumission = db.query(Soumission).filter(Soumission.id == soumission_id).first()
    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")
    return soumission


@router.post("", response_model=SoumissionOut)
def creer_soumission(payload: SoumissionCreate, db: Session = Depends(get_db)):
    ao = db.query(AppelOffres).filter(AppelOffres.id == payload.appel_offres_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres non trouvé")

    soumission = Soumission(**payload.model_dump())
    db.add(soumission)
    ao.statut = "en_preparation"
    db.commit()
    db.refresh(soumission)
    return soumission


@router.post("/generer-documents", response_model=SoumissionOut)
def generer_documents_soumission(payload: GenererDocumentsRequest, db: Session = Depends(get_db)):
    soumission = db.query(Soumission).filter(Soumission.id == payload.soumission_id).first()
    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")

    ao = db.query(AppelOffres).filter(AppelOffres.id == soumission.appel_offres_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres lié non trouvé")

    for type_doc in payload.types_documents:
        generer_document(db, soumission, ao, type_doc)

    soumission.statut = "complete"
    db.commit()
    db.refresh(soumission)
    return soumission


@router.get("/documents/{document_id}/telecharger")
def telecharger_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(DocumentGenere).filter(DocumentGenere.id == document_id).first()
    if not document or not document.chemin_fichier:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return FileResponse(
        path=document.chemin_fichier,
        filename=document.nom_fichier,
        media_type="application/octet-stream",
    )


@router.patch("/{soumission_id}/valider", response_model=SoumissionOut)
def valider_soumission(soumission_id: int, valide_par: str, db: Session = Depends(get_db)):
    from datetime import datetime
    soumission = db.query(Soumission).filter(Soumission.id == soumission_id).first()
    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")
    soumission.statut = "validee"
    soumission.valide_par = valide_par
    soumission.date_validation = datetime.utcnow()
    db.commit()
    db.refresh(soumission)
    return soumission


@router.post("/{soumission_id}/analyser-cahier-charges")
async def analyser_cahier_charges_soumission(
    soumission_id: int,
    fichier: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Reçoit le cahier des charges (PDF) d'un appel d'offres, en extrait le texte,
    puis demande à l'IA d'identifier les pièces administratives, techniques et
    financières exigées. Stocke le texte extrait pour réutilisation ultérieure
    lors de la rédaction du DAO.
    """
    soumission = db.query(Soumission).filter(Soumission.id == soumission_id).first()
    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")

    if not fichier.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés pour le moment.")

    contenu_pdf = await fichier.read()
    try:
        lecteur = PdfReader(BytesIO(contenu_pdf))
        texte_extrait = "\n".join((page.extract_text() or "") for page in lecteur.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Impossible de lire le PDF : {exc}")

    if not texte_extrait.strip():
        raise HTTPException(
            status_code=400,
            detail="Aucun texte n'a pu être extrait de ce PDF (probablement un scan sans OCR).",
        )

    try:
        analyse = analyser_cahier_des_charges(texte_extrait)
    except GeminiNonConfigure as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur lors de l'analyse IA : {exc}")

    soumission.cahier_des_charges_texte = texte_extrait
    soumission.documents_requis_json = json.dumps(analyse, ensure_ascii=False)
    db.commit()

    return {"soumission_id": soumission_id, "analyse": analyse}


@router.post("/{soumission_id}/rediger-dao")
def rediger_dao_ia(soumission_id: int, db: Session = Depends(get_db)):
    """
    Génère le contenu rédigé (méthodologie, présentation, planning, moyens)
    pour le DAO, en s'appuyant sur le cahier des charges déjà analysé et le
    profil réel de l'entreprise. Le texte généré est stocké sur la soumission
    et utilisé ensuite par /generer-documents pour produire les PDF/DOCX/XLSX.
    """
    soumission = db.query(Soumission).filter(Soumission.id == soumission_id).first()
    if not soumission:
        raise HTTPException(status_code=404, detail="Soumission non trouvée")
    if not soumission.cahier_des_charges_texte:
        raise HTTPException(
            status_code=400,
            detail="Aucun cahier des charges n'a encore été analysé pour cette soumission. "
                   "Utilisez d'abord /analyser-cahier-charges.",
        )

    ao = db.query(AppelOffres).filter(AppelOffres.id == soumission.appel_offres_id).first()
    if not ao:
        raise HTTPException(status_code=404, detail="Appel d'offres lié non trouvé")

    profile = db.query(EntrepriseProfile).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil entreprise non configuré")

    references = db.query(ReferenceTechnique).filter(ReferenceTechnique.profile_id == profile.id).all()

    profil_dict = {
        "raison_sociale": profile.raison_sociale,
        "adresse": profile.adresse,
        "domaines_expertise": json.loads(profile.domaines_expertise or "[]"),
        "references_techniques": [
            {
                "intitule_projet": r.intitule_projet,
                "client": r.client,
                "montant": r.montant or 0,
                "annee": r.annee,
            }
            for r in references
        ],
    }

    try:
        contenu = generer_contenu_dao_complet(
            objet_marche=ao.objet,
            cahier_des_charges_texte=soumission.cahier_des_charges_texte,
            profil_entreprise=profil_dict,
        )
    except GeminiNonConfigure as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Erreur lors de la rédaction IA : {exc}")

    soumission.methodologie_resume = contenu.get("methodologie")
    soumission.planning_resume = contenu.get("planning_execution")
    db.commit()

    return {"soumission_id": soumission_id, "contenu_redige": contenu}
