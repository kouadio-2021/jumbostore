import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

def _parser_prix(texte_prix):
    if not texte_prix:
        return None
    nettoye = re.sub(r"[^\d.]", "", texte_prix.replace(",", ""))
    try:
        return float(nettoye)
    except ValueError:
        return None

r = requests.get('https://www.jumia.ci/slp/ciment', headers=HEADERS, timeout=15)
soup = BeautifulSoup(r.text, 'lxml')
liens_produits = soup.select("a[href$='.html']")

offres = []
vus = set()

for lien_tag in liens_produits:
    lien = lien_tag.get("href", "")
    if not lien or lien in vus:
        continue

    texte_complet = lien_tag.get_text(separator=" ", strip=True)
    if "FCFA" not in texte_complet:
        continue

    montants = re.findall(r"([\d,]+\.\d{2})\s*FCFA", texte_complet)
    if not montants:
        continue

    prix_candidats = [_parser_prix(m) for m in montants]
    prix_candidats = [p for p in prix_candidats if p is not None]
    if not prix_candidats:
        print("ECHEC prix_candidats vide pour:", montants)
        continue
    prix = min(prix_candidats)

    nom_produit = texte_complet.split(montants[0])[0].strip(" -")
    if not nom_produit:
        print("ECHEC nom_produit vide, montants[0]=", repr(montants[0]))
        continue
    nom_produit = nom_produit[:150]

    vus.add(lien)
    offres.append({"nom_produit": nom_produit, "prix_unitaire": prix, "lien_achat": lien})

print("TOTAL OFFRES:", len(offres))
for o in offres[:3]:
    print(o)