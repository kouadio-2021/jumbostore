"""
Service Comparateur de Prix — Recherche réelle de fournisseurs.

Source actuelle : Jumia Côte d'Ivoire (jumia.ci), via ses pages de recherche
"/slp/{terme}" qui exposent prix réels et liens d'achat directs.

Architecture extensible : chaque source a sa propre fonction de recherche
(`rechercher_jumia`, et plus tard `rechercher_produitbat`, etc.), toutes
combinées par `comparer_fournisseurs`.
"""
import re
import logging
import unicodedata
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.comparateur import RechercheProduit, OffreFournisseur

logger = logging.getLogger("comparateur")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

JUMIA_SEARCH_URL = "https://www.jumia.ci/slp/{query}"


def extraire_quantite(designation: str, quantite_defaut: int) -> int:
    match = re.match(r"^\s*(\d+)\s", designation)
    if match:
        return int(match.group(1))
    return quantite_defaut


def _slugifier(texte: str) -> str:
    """Convertit un texte de recherche en slug compatible avec l'URL /slp/ de Jumia
    (ex: 'ciment portland' -> 'ciment-portland')."""
    texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode("ascii")
    texte = re.sub(r"[^a-zA-Z0-9\s]", "", texte).strip().lower()
    texte = re.sub(r"\s+", "-", texte)
    return texte


def _parser_prix(texte_prix: str) -> float | None:
    """Convertit '12,900.00 FCFA' ou '12 900 FCFA' en float 12900.0."""
    if not texte_prix:
        return None
    nettoye = re.sub(r"[^\d.]", "", texte_prix.replace(",", ""))
    try:
        return float(nettoye)
    except ValueError:
        return None


def rechercher_jumia(designation: str, quantite_demandee: int, max_resultats: int = 10) -> list[dict]:
    """
    Recherche réellement un produit sur Jumia.ci (page /slp/{terme}) et
    retourne une liste d'offres réelles : [{nom_produit, prix_unitaire, lien_achat}, ...]
    """
    slug = _slugifier(designation)
    url = JUMIA_SEARCH_URL.format(query=slug)

    try:
        reponse = requests.get(url, headers=HEADERS, timeout=20)
        reponse.raise_for_status()
    except requests.RequestException as exc:
        logger.error(f"Impossible de joindre Jumia : {exc}")
        return []

    soup = BeautifulSoup(reponse.text, "lxml")
    offres = []
    vus = set()

    # Sur les pages /slp/, chaque produit est un lien <a> se terminant par .html,
    # dont le texte contient le titre suivi du prix (ex: "...Titre...12,900.00 FCFA").
    liens_produits = soup.select("a[href$='.html']")

    for lien_tag in liens_produits:
        lien = lien_tag.get("href", "")
        if not lien or lien in vus:
            continue

        texte_complet = lien_tag.get_text(separator=" ", strip=True)
        if "FCFA" not in texte_complet:
            continue

        # Le prix est le DERNIER montant en FCFA qui apparaît dans le texte du lien
        # (le premier prix après une remise barrée serait l'ancien prix, donc on
        # cherche tous les montants et on garde le plus petit, qui est le prix actuel).
        montants = re.findall(r"([\d,]+\.\d{2})\s*FCFA", texte_complet)
        if not montants:
            continue

        prix_candidats = [_parser_prix(m) for m in montants]
        prix_candidats = [p for p in prix_candidats if p is not None]
        if not prix_candidats:
            continue
        prix = min(prix_candidats)  # le prix promo/actuel est toujours <= prix barré

        # Le nom du produit est le texte avant le premier prix trouvé
        nom_produit = texte_complet.split(montants[0])[0].strip(" -")
        if not nom_produit:
            continue
        nom_produit = nom_produit[:150]

        vus.add(lien)
        lien_complet = lien if lien.startswith("http") else f"https://www.jumia.ci{lien}"

        offres.append({
            "nom_produit": nom_produit,
            "prix_unitaire": prix,
            "lien_achat": lien_complet,
        })

        if len(offres) >= max_resultats:
            break

    return offres


def comparer_fournisseurs(db: Session, designation: str, quantite: int) -> RechercheProduit:
    """
    Lance une recherche réelle multi-sources pour un produit donné, et
    enregistre les offres trouvées triées par prix croissant.
    """
    recherche = RechercheProduit(designation=designation, quantite=quantite)
    db.add(recherche)
    db.commit()
    db.refresh(recherche)

    offres_brutes = []
    offres_brutes.extend(
        {**offre, "source_site": "Jumia.ci", "type_fournisseur": "local"}
        for offre in rechercher_jumia(designation, quantite)
    )
    # Futures sources, une fois validées techniquement :
    # offres_brutes.extend(rechercher_produitbat(designation, quantite))

    if not offres_brutes:
        db.commit()
        return recherche

    prix_min = min(o["prix_unitaire"] for o in offres_brutes)
    prix_max = max(o["prix_unitaire"] for o in offres_brutes)
    ecart_prix = (prix_max - prix_min) or 1  # éviter division par zéro si un seul résultat

    for offre_data in offres_brutes:
        prix_unit = offre_data["prix_unitaire"]
        prix_total = prix_unit * quantite
        # Score d'avantage basé uniquement sur le prix (seule donnée réelle disponible) :
        # 100 = moins cher trouvé, 0 = plus cher trouvé.
        note_avantage = round((1 - (prix_unit - prix_min) / ecart_prix) * 100, 1)

        offre = OffreFournisseur(
            recherche_id=recherche.id,
            nom_fournisseur=offre_data["nom_produit"],
            type_fournisseur=offre_data["type_fournisseur"],
            prix_unitaire=round(prix_unit, 0),
            prix_total=round(prix_total, 0),
            devise="FCFA",
            note_avantage=note_avantage,
            lien_achat=offre_data["lien_achat"],
            source_site=offre_data["source_site"],
        )
        db.add(offre)

    db.commit()
    db.refresh(recherche)
    return recherche
