"""
Service de Veille Marchés — Collecte réelle des appels d'offres.

Source actuelle : ARCOP (ex-ANRMP), page "Avis d'appel d'offres".
URL : https://arcop.ci/documentation/avis/avis-dappel-doffres/

Architecture pensée pour être étendue : chaque source a sa propre fonction
de collecte (`collecter_arcop`, et plus tard `collecter_sigomap`,
`collecter_fao`, etc.), toutes orchestrées par `collecter_toutes_sources`.
"""
import re
import logging
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.appel_offres import AppelOffres, CategorieAO, TypeAvis, StatutAO

logger = logging.getLogger("scraping")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

ARCOP_URL = "https://www.anrmp.ci/docutheque/annonces/avis-dappel-doffres"

# Mots-clés -> catégorie. Le premier mot-clé trouvé dans le titre l'emporte.
MOTS_CLES_CATEGORIE = [
    (["btp", "construction", "travaux", "bâtiment", "batiment", "génie civil",
      "réhabilitation", "rehabilitation", "rénovation", "renovation", "route",
      "pont", "voirie", "aile du siège", "immeuble"], CategorieAO.BTP),
    (["informatique", "logiciel", "licences", "ordinateur", "serveur",
      "réseau", "messagerie", "intranet", "ged", "bande passante",
      "antivirus", "matériels informatiques", "materiels informatiques"], CategorieAO.INFORMATIQUE),
    (["électrique", "electrique", "groupe électrogène", "groupe electrogene",
      "climatisation", "câblage", "cablage"], CategorieAO.ELECTRICITE),
    (["eau", "hydraulique", "forage", "assainissement", "adduction"], CategorieAO.HYDRAULIQUE),
    (["sécurité", "securite", "gardiennage", "surveillance"], CategorieAO.SECURITE),
    (["véhicule", "vehicule", "transport", "logistique", "camion"], CategorieAO.TRANSPORT),
]

MOTS_CLES_TYPE = [
    (["manifestation d'intérêt", "manifestation d intérêt", "manifestation d’intérêt"],
     TypeAvis.MANIFESTATION_INTERET),
    (["consultation restreinte"], TypeAvis.CONSULTATION_RESTREINTE),
    (["demande de cotation", "cotation"], TypeAvis.DEMANDE_COTATION),
]


def _deduire_categorie(titre: str) -> CategorieAO:
    titre_lower = titre.lower()
    for mots, categorie in MOTS_CLES_CATEGORIE:
        if any(mot in titre_lower for mot in mots):
            return categorie
    return CategorieAO.FOURNITURES


def _deduire_type_avis(titre: str) -> TypeAvis:
    titre_lower = titre.lower()
    for mots, type_avis in MOTS_CLES_TYPE:
        if any(mot in titre_lower for mot in mots):
            return type_avis
    return TypeAvis.APPEL_OFFRES


def _extraire_reference(titre: str, fallback: str) -> str:
    """Essaie d'extraire une référence du type 'F114-2026', 'T 950-2022', 'OP 51-2023'."""
    match = re.search(r"\b([A-Z]{1,3}\s?\d{1,4}-\d{4})\b", titre)
    if match:
        return match.group(1).replace(" ", "")
    return f"ARCOP-{fallback}"


def _parser_date(date_str: str) -> Optional[datetime]:
    """Parse une date au format JJ/MM/AAAA."""
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y")
    except (ValueError, AttributeError):
        return None


def collecter_arcop(db: Session) -> dict:
    """
    Visite réellement la page ARCOP des avis d'appel d'offres, extrait
    chaque ligne du tableau, et insère les nouveaux appels d'offres en base.

    Retourne un résumé : {"trouves": int, "nouveaux": int, "erreurs": list}
    """
    resultat = {"source": "ARCOP", "trouves": 0, "nouveaux": 0, "erreurs": []}

    try:
        reponse = requests.get(ARCOP_URL, headers=HEADERS, timeout=20)
        reponse.raise_for_status()
    except requests.RequestException as exc:
        msg = f"Impossible de joindre ARCOP : {exc}"
        logger.error(msg)
        resultat["erreurs"].append(msg)
        return resultat

    soup = BeautifulSoup(reponse.text, "lxml")

    # Le tableau des avis est le premier <table> de la page (zone "Avis d'appel d'offres")
    table = soup.find("table")
    if table is None:
        resultat["erreurs"].append("Tableau des avis introuvable (structure du site a peut-être changé)")
        return resultat

    lignes = table.find_all("tr")
    references_vues_dans_ce_batch = set()

    for ligne in lignes:
        cellules = ligne.find_all("td")
        if len(cellules) < 4:
            continue  # ligne d'en-tête ou ligne incomplète

        lien_titre = cellules[0].find("a")
        if lien_titre is None:
            continue

        titre = lien_titre.get_text(strip=True)
        if not titre:
            continue

        date_publication_str = cellules[2].get_text(strip=True)
        date_publication = _parser_date(date_publication_str)
        if date_publication is None:
            continue

        lien_telecharger = cellules[3].find("a")
        document_url = lien_telecharger["href"] if lien_telecharger and lien_telecharger.has_attr("href") else None
        url_source = lien_titre.get("href", ARCOP_URL)

        resultat["trouves"] += 1

        # Identifiant unique basé sur le document (stable même si le titre est dupliqué)
        fallback_id = document_url.rstrip("/").split("/")[-2] if document_url else titre[:30]
        reference = _extraire_reference(titre, fallback_id)

        deja_existant = db.query(AppelOffres).filter(
            AppelOffres.reference == reference
        ).first()
        if deja_existant:
            continue

        if reference in references_vues_dans_ce_batch:
            # Même référence générée deux fois dans ce passage (titre dupliqué
            # sur la page, ou collision de génération) : on ignore le doublon.
            continue
        references_vues_dans_ce_batch.add(reference)

        # Si la référence générée existe déjà pour un AUTRE document (cas "ARCOP-xxx"
        # dupliqué), on vérifie aussi sur l'URL du document pour éviter les vrais doublons.
        if document_url:
            deja_par_url = db.query(AppelOffres).filter(
                AppelOffres.document_url == document_url
            ).first()
            if deja_par_url:
                continue

        ao = AppelOffres(
            reference=reference,
            objet=titre,
            source="ARCOP",
            type_avis=_deduire_type_avis(titre),
            categorie=_deduire_categorie(titre),
            date_publication=date_publication,
            date_limite=date_publication,  # ARCOP n'indique pas toujours de date limite distincte
            statut=StatutAO.NOUVEAU,
            url_source=url_source,
            document_url=document_url,
            date_collecte=datetime.utcnow(),
        )
        db.add(ao)
        resultat["nouveaux"] += 1

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        msg = f"Erreur lors de l'enregistrement en base : {exc}"
        logger.error(msg)
        resultat["erreurs"].append(msg)

    return resultat


def collecter_toutes_sources(db: Session) -> list[dict]:
    """
    Point d'entrée unique pour lancer la collecte sur toutes les sources actives.
    Pour ajouter une nouvelle source : écrire `collecter_xxx(db)` puis l'ajouter
    à la liste ci-dessous.
    """
    resultats = []
    resultats.append(collecter_arcop(db))
    # Futures sources, une fois prêtes :
    # resultats.append(collecter_sigomap(db))
    # resultats.append(collecter_fao(db))
    return resultats
