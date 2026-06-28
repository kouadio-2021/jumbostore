"""
Service d'analyse des DAO (Dossiers d'Appel d'Offres).

Pour ce prototype, l'extraction réelle de texte depuis des PDF/Word/scans
(OCR + NLP) est simulée par une logique déterministe et réaliste basée sur
les caractéristiques de l'appel d'offres (catégorie, montant, source), afin
de produire des résultats cohérents et démontrables. L'architecture est
prévue pour être branchée sur un vrai pipeline OCR/NLP (ex: Tesseract +
modèle de langage) sans changer l'interface du service.
"""
import json
import random
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.appel_offres import AppelOffres
from app.models.analyse_dao import AnalyseDAO, ConformiteEnum
from app.models.entreprise import EntrepriseProfile


DOCUMENTS_TYPES_PAR_CATEGORIE = {
    "BTP": ["RCCM", "DFE", "Attestation CNPS", "Agrément technique BTP", "Références de chantiers similaires", "Attestation fiscale"],
    "Informatique": ["RCCM", "DFE", "Attestation CNPS", "Certification revendeur agréé", "Références de fourniture équipements", "Attestation fiscale"],
    "Fournitures": ["RCCM", "DFE", "Attestation CNPS", "Attestation fiscale", "Catalogue produits"],
    "Électricité": ["RCCM", "DFE", "Agrément installation électrique", "Attestation CNPS", "Attestation fiscale"],
    "Hydraulique": ["RCCM", "DFE", "Agrément travaux hydrauliques", "Attestation CNPS", "Attestation fiscale"],
    "Sécurité": ["RCCM", "DFE", "Agrément prestations de sécurité", "Attestation CNPS", "Attestation fiscale"],
    "Transport": ["RCCM", "DFE", "Attestation CNPS", "Carte grise véhicules", "Attestation fiscale"],
}


def analyser_dao(db: Session, appel_offres: AppelOffres) -> AnalyseDAO:
    """
    Simule l'analyse intelligente d'un DAO et produit un score de
    compatibilité avec le profil de l'entreprise.
    """
    profile = db.query(EntrepriseProfile).first()

    # Seed déterministe basé sur la référence pour des résultats stables et reproductibles
    seed = sum(ord(c) for c in appel_offres.reference)
    rng = random.Random(seed)

    categorie = appel_offres.categorie.value if hasattr(appel_offres.categorie, "value") else str(appel_offres.categorie)
    documents_requis = DOCUMENTS_TYPES_PAR_CATEGORIE.get(categorie, DOCUMENTS_TYPES_PAR_CATEGORIE["Fournitures"])

    # Score de base influencé par la capacité financière déclarée et le montant du marché
    score_base = 72.0
    if profile and appel_offres.montant_estimatif:
        ratio = profile.capacite_financiere / max(appel_offres.montant_estimatif, 1)
        if ratio > 3:
            score_base += 15
        elif ratio > 1:
            score_base += 8
        elif ratio < 0.3:
            score_base -= 20

    variation = rng.uniform(-8, 10)
    score = max(5.0, min(98.0, score_base + variation))

    if score >= 80:
        conformite = ConformiteEnum.CONFORME
        points_attention = [
            "Vérifier la date de validité de l'attestation fiscale avant dépôt.",
            "Confirmer la disponibilité du personnel clé mentionné dans les références.",
        ]
    elif score >= 55:
        conformite = ConformiteEnum.CONFORME_RESERVES
        points_attention = [
            "Le nombre de références techniques sur les 3 dernières années est en limite du seuil exigé.",
            "Capacité financière à confirmer par une attestation bancaire récente.",
            "Délai d'exécution proposé à valider avec les équipes terrain.",
        ]
    else:
        conformite = ConformiteEnum.NON_CONFORME
        points_attention = [
            "Capacité financière insuffisante par rapport au montant estimatif du marché.",
            "Références techniques du secteur jugées insuffisantes pour ce type de DAO.",
            "Risque de rejet administratif si les pièces ne sont pas mises à jour en urgence.",
        ]

    conditions_administratives = {
        "caution_provisoire_exigee": True,
        "taux_caution_provisoire": "1.5% du montant de l'offre",
        "agrement_requis": categorie in ["BTP", "Électricité", "Hydraulique", "Sécurité"],
        "registre_commerce_anciennete_min_annees": 2,
    }

    criteres_techniques = {
        "experience_min_annees": 3 if appel_offres.montant_estimatif and appel_offres.montant_estimatif > 50_000_000 else 1,
        "references_similaires_exigees": 2,
        "personnel_cle_requis": ["Chef de projet", "Ingénieur technique"] if categorie == "BTP" else ["Responsable technique"],
    }

    criteres_financiers = {
        "chiffre_affaires_min_3_dernieres_annees": (appel_offres.montant_estimatif or 0) * 1.5,
        "garantie_financiere_exigee": True,
    }

    delais = {
        "delai_remise_offre_jours": (appel_offres.date_limite - appel_offres.date_publication).days,
        "delai_execution_marche_mois": rng.choice([3, 6, 9, 12, 18]),
        "validite_offre_jours": 90,
    }

    analyse = AnalyseDAO(
        appel_offres_id=appel_offres.id,
        conditions_administratives=json.dumps(conditions_administratives, ensure_ascii=False),
        criteres_techniques=json.dumps(criteres_techniques, ensure_ascii=False),
        criteres_financiers=json.dumps(criteres_financiers, ensure_ascii=False),
        delais=json.dumps(delais, ensure_ascii=False),
        score_compatibilite=round(score, 1),
        conformite=conformite,
        points_attention=json.dumps(points_attention, ensure_ascii=False),
        documents_requis=json.dumps(documents_requis, ensure_ascii=False),
        date_analyse=datetime.utcnow(),
    )
    db.add(analyse)

    appel_offres.score_compatibilite = analyse.score_compatibilite
    db.add(appel_offres)

    db.commit()
    db.refresh(analyse)
    return analyse
