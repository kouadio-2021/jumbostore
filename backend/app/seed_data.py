"""
Génère les données de base nécessaires au démarrage de JUMBOSTORE :
uniquement les comptes utilisateurs de connexion.

Les profils d'entreprise sont créés et gérés librement via l'interface
(plusieurs entreprises possibles, voir app/routers/entreprise.py).
Les appels d'offres ne sont PLUS générés ici — ils proviennent uniquement
de la collecte réelle (voir app/services/scraping_service.py), déclenchée
via POST /api/appels-offres/collecter.

À exécuter une seule fois au premier démarrage (ou via /api/admin/reset-demo).
"""
from app.database import SessionLocal, engine, Base
from app.models.user import User, RoleEnum
from app.services.security import get_password_hash


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Données déjà initialisées, seed ignoré.")
        db.close()
        return

    # --- Utilisateurs ---
    utilisateurs = [
        User(nom_complet="Karimu Waidi Abiola", email="pdg@jumbostore.ci", hashed_password=get_password_hash("jumbostore2026"), role=RoleEnum.DIRECTEUR),
        User(nom_complet="Digbo Hippolyte", email="dga@jumbostore.ci", hashed_password=get_password_hash("jumbostore2026"), role=RoleEnum.DIRECTEUR),
        User(nom_complet="Kouadio Koffi Ephrem Gildas", email="gildas@jumbostore.ci", hashed_password=get_password_hash("jumbostore2026"), role=RoleEnum.ADMIN),
        User(nom_complet="Sanusi Ibrahim", email="commercial@jumbostore.ci", hashed_password=get_password_hash("jumbostore2026"), role=RoleEnum.CHARGE_AO),
        User(nom_complet="Aïcha Touré", email="compta@jumbostore.ci", hashed_password=get_password_hash("jumbostore2026"), role=RoleEnum.COMPTABILITE),
    ]
    db.add_all(utilisateurs)
    db.commit()

    db.close()
    print("Données de base créées avec succès (utilisateurs uniquement).")


if __name__ == "__main__":
    seed()
