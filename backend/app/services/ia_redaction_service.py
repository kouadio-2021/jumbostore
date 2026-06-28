"""
Service IA — Analyse de cahier des charges et rédaction automatique de DAO.

Utilise l'API Gemini (Google AI Studio) pour :
  1. Lire un cahier des charges / DAO (texte extrait d'un PDF) et identifier
     précisément la liste des pièces administratives, techniques et
     financières exigées par le maître d'ouvrage.
  2. Une fois ces pièces fournies (ou tirées du profil entreprise existant),
     rédiger un contenu réel et personnalisé pour chaque section du dossier
     de soumission (présentation, méthodologie, planning, etc.) — remplaçant
     les textes génériques fixes utilisés jusqu'ici.

Nécessite la variable d'environnement GEMINI_API_KEY (voir .env).
"""
import json
import logging
import os
from typing import Optional

import requests

logger = logging.getLogger("ia_redaction")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


class GeminiNonConfigure(Exception):
    """Levée quand GEMINI_API_KEY n'est pas définie dans l'environnement."""


def _appeler_gemini(prompt: str, attendre_json: bool = False) -> str:
    """
    Envoie un prompt à l'API Gemini et retourne le texte de la réponse.
    Si attendre_json=True, demande explicitement une sortie JSON pure.
    """
    if not GEMINI_API_KEY:
        raise GeminiNonConfigure(
            "GEMINI_API_KEY n'est pas configurée. Ajoutez-la dans le fichier .env du backend."
        )

    generation_config = {"temperature": 0.3, "maxOutputTokens": 4096}
    if attendre_json:
        generation_config["responseMimeType"] = "application/json"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }

    reponse = requests.post(
        f"{GEMINI_URL}?key={GEMINI_API_KEY}",
        json=payload,
        timeout=60,
    )
    reponse.raise_for_status()
    data = reponse.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Réponse Gemini inattendue : {data}") from exc


def analyser_cahier_des_charges(texte_cahier_des_charges: str) -> dict:
    """
    Lit le texte d'un cahier des charges / DAO et retourne la liste structurée
    des pièces exigées, regroupées par catégorie.

    Retour : {
        "objet_resume": str,
        "documents_administratifs": [str, ...],
        "documents_techniques": [str, ...],
        "documents_financiers": [str, ...],
        "points_attention": [str, ...]
    }
    """
    prompt = f"""Tu es un expert en analyse de dossiers d'appel d'offres (marchés publics) en Côte d'Ivoire.

Voici le texte d'un cahier des charges / dossier d'appel d'offres (DAO). Analyse-le et extrais
UNIQUEMENT les informations explicitement présentes dans le texte. Ne suppose rien et n'invente
aucune pièce qui ne serait pas mentionnée ou clairement sous-entendue par le contexte réglementaire
ivoirien standard (RCCM, DFE, attestation CNPS, attestation fiscale sont des pièces usuelles
si le texte parle de "pièces administratives" sans toutes les lister).

Réponds STRICTEMENT en JSON avec cette structure exacte, sans aucun texte avant ou après :
{{
  "objet_resume": "résumé en une phrase de l'objet du marché",
  "documents_administratifs": ["pièce 1", "pièce 2", ...],
  "documents_techniques": ["pièce 1", "pièce 2", ...],
  "documents_financiers": ["pièce 1", "pièce 2", ...],
  "points_attention": ["élément important à ne pas manquer", ...]
}}

Texte du cahier des charges :
---
{texte_cahier_des_charges[:15000]}
---
"""
    texte_reponse = _appeler_gemini(prompt, attendre_json=True)
    try:
        return json.loads(texte_reponse)
    except json.JSONDecodeError as exc:
        logger.error(f"Réponse Gemini non-JSON : {texte_reponse}")
        raise RuntimeError(
            "L'IA a renvoyé une réponse mal formée. Veuillez réessayer."
        ) from exc


def rediger_section_dao(
    section: str,
    objet_marche: str,
    cahier_des_charges_extrait: str,
    profil_entreprise: dict,
) -> str:
    """
    Rédige le contenu réel d'une section du DAO (ex: "méthodologie",
    "présentation_entreprise", "planning") en s'appuyant sur le cahier
    des charges réel et le profil de Jumbo Store SARL.

    profil_entreprise attend des clés comme : raison_sociale, adresse,
    domaines_expertise (liste), references_techniques (liste de dict
    avec intitule_projet/client/montant/annee).
    """
    references_texte = "\n".join(
        f"- {r.get('intitule_projet')} pour {r.get('client')} "
        f"({r.get('annee')}, {r.get('montant'):,.0f} FCFA)"
        for r in profil_entreprise.get("references_techniques", [])
    ) or "Aucune référence technique fournie."

    prompt = f"""Tu es un rédacteur professionnel spécialisé dans les dossiers d'appel d'offres (DAO)
pour le secteur du BTP et des fournitures générales en Côte d'Ivoire.

Rédige la section "{section}" d'un dossier de soumission, en français professionnel et précis,
pour l'entreprise suivante :

Entreprise : {profil_entreprise.get('raison_sociale')}
Adresse : {profil_entreprise.get('adresse')}
Domaines d'expertise : {", ".join(profil_entreprise.get('domaines_expertise', []))}
Références techniques réelles :
{references_texte}

Objet du marché visé : {objet_marche}

Extrait pertinent du cahier des charges :
---
{cahier_des_charges_extrait[:8000]}
---

Consignes :
- Utilise UNIQUEMENT les références techniques listées ci-dessus, n'en invente aucune.
- Adapte le ton et le contenu à l'objet réel du marché.
- Reste factuel, professionnel, sans formules creuses génériques.
- Réponds uniquement avec le texte de la section, sans titre ni préambule.
"""
    return _appeler_gemini(prompt, attendre_json=False).strip()


def generer_contenu_dao_complet(
    objet_marche: str,
    cahier_des_charges_texte: str,
    profil_entreprise: dict,
) -> dict:
    """
    Génère le contenu rédigé de toutes les sections principales d'un DAO.
    Retourne un dict {section: texte}.
    """
    sections = ["presentation_entreprise", "methodologie", "planning_execution", "moyens_humains_et_materiels"]
    resultat = {}
    for section in sections:
        resultat[section] = rediger_section_dao(
            section=section,
            objet_marche=objet_marche,
            cahier_des_charges_extrait=cahier_des_charges_texte,
            profil_entreprise=profil_entreprise,
        )
    return resultat
