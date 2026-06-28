# JUMBOSTORE — Prototype

Plateforme intelligente de veille marchés et gestion des appels d'offres pour **Jumbo Store SARL** (BTP & fournitures diverses, Côte d'Ivoire).

Ce prototype couvre les 10 modules fonctionnels du cahier des charges :
1. Veille Marchés (appels d'offres)
2. Profil Entreprise
3. Analyse des DAO (score de compatibilité IA)
4. Génération Automatique de documents (PDF/DOCX/XLSX)
5. Comparateur de Prix fournisseurs
6. Facturation (proforma, factures, devis, bons de commande)
7. Notifications multi-canal
8. Tableau de Bord
9. Gestion des utilisateurs et rôles
10. Journal d'actions (traçabilité)

## ⚠️ Important — Ce qui est réel vs simulé

Pour produire un prototype démontrable rapidement, certains modules utilisent une **logique simulée mais réaliste** plutôt qu'une intégration externe complète :

| Module | État dans ce prototype |
|---|---|
| Base de données, API, CRUD | ✅ Réel (SQLite, FastAPI) |
| Génération de documents PDF/DOCX/XLSX | ✅ Réel (ReportLab, python-docx, openpyxl) |
| Analyse DAO (score de compatibilité) | ⚙️ Logique déterministe réaliste — **pas encore d'OCR/NLP réel** sur de vrais fichiers PDF/scannés |
| Comparateur de prix fournisseurs | ⚙️ Données simulées (pas de scraping réel de sites fournisseurs) |
| Collecte automatique d'appels d'offres | ⚙️ Données de démonstration insérées au démarrage — **pas de scraping réel des portails (ANRMP, etc.)** |
| Notifications WhatsApp/SMS/Telegram | ⚙️ Stockées en base, **pas d'envoi réel** (nécessiterait Twilio, API WhatsApp Business, etc.) |
| Authentification JWT | ✅ Réel mais basique (pas de double authentification encore) |

L'architecture est conçue pour qu'on puisse brancher les vraies intégrations (OCR Tesseract, scraping Playwright, API Twilio/WhatsApp Business, etc.) sans tout réécrire.

## ⚠️ Non testé en exécution réelle

Ce code a été écrit dans un environnement sans accès réseau, donc sans pouvoir installer les dépendances ni lancer le serveur. La syntaxe a été vérifiée (compilation Python + validation esbuild sur tout le JS/JSX), et la cohérence des routes/schémas entre frontend et backend a été contrôlée manuellement. **Testez impérativement en local avant tout déploiement** (voir ci-dessous) afin de détecter d'éventuelles erreurs d'exécution.

---

## 1. Lancer en local (test avant déploiement)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

L'API est accessible sur `http://localhost:8000`, avec documentation interactive sur `http://localhost:8000/docs`.

Au premier démarrage, des données de démonstration sont créées automatiquement (entreprise Jumbo Store SARL, 10 appels d'offres réalistes, utilisateurs, notifications).

**Comptes de test** (mot de passe : `jumbostore2026`) :
- `gildas@jumbostore.ci` — Administrateur Général
- `pdg@jumbostore.ci` — Directeur
- `commercial@jumbostore.ci` — Chargé d'Appels d'Offres
- `compta@jumbostore.ci` — Comptabilité

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est accessible sur `http://localhost:5173`. Le fichier `.env` pointe déjà vers `http://localhost:8000`.

---

## 2. Déploiement en ligne (lien partageable)

### Option recommandée : Railway (rapide, gratuit pour démarrer)

**Backend :**
1. Créez un compte sur [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo" (poussez d'abord ce dossier `backend/` sur GitHub)
3. Railway détecte le `Dockerfile` automatiquement et déploie
4. Une fois déployé, notez l'URL publique (ex: `https://jumbostore-backend.up.railway.app`)

**Frontend :**
1. Modifiez `frontend/.env` avec l'URL du backend déployé :
   ```
   VITE_API_URL=https://jumbostore-backend.up.railway.app
   ```
2. Sur Railway, créez un second service depuis le même repo (dossier `frontend/`)
3. Railway build avec `npm run build` et sert le contenu de `dist/`
   - Si besoin, ajoutez un fichier `frontend/railway.json` ou configurez la commande de démarrage : `npm run build && npx serve dist -p $PORT`

Vous obtenez alors un lien public du type `https://jumbostore.up.railway.app` à partager avec le PDG ou les partenaires.

### Option alternative : Render.com

Même principe : un "Web Service" pour le backend (Docker), un "Static Site" pour le frontend (build command `npm run build`, publish directory `dist`).

### Option alternative : VPS (plus de contrôle)

Si vous disposez déjà d'un VPS (OVH, Contabo, etc.) :
1. Installez Docker
2. `docker build -t jumbostore-backend ./backend && docker run -d -p 8000:8000 jumbostore-backend`
3. Pour le frontend : `npm run build` puis servez le dossier `dist/` avec Nginx, en le configurant pour rediriger `/api` vers le backend
4. Pointez un nom de domaine ou sous-domaine vers l'IP du VPS

---

## 3. Limitations à connaître pour la démo

- La base de données SQLite est fichier-unique : pratique pour une démo, mais à migrer vers PostgreSQL pour un usage en production multi-utilisateurs simultanés (changement d'une seule ligne dans `app/config.py`)
- Les documents générés (PDF/DOCX/XLSX) sont stockés sur le disque du serveur backend — sur certains hébergeurs gratuits, ce stockage est éphémère (perdu au redéploiement). Pour la production, prévoir un stockage S3 ou équivalent
- Pas encore de double authentification (mentionnée dans le cahier des charges comme exigence de sécurité)

## Structure du projet

```
jumbostore/
├── backend/            # API FastAPI
│   ├── app/
│   │   ├── models/     # Modèles SQLAlchemy (1 fichier par module métier)
│   │   ├── schemas/    # Schémas Pydantic (validation API)
│   │   ├── routers/    # Endpoints API (1 fichier par module)
│   │   ├── services/   # Logique métier (analyse DAO, génération documents, comparateur)
│   │   ├── seed_data.py
│   │   └── main.py
│   └── requirements.txt
└── frontend/           # Application React
    └── src/
        ├── components/ # Layout, ScoreGauge, StatusBadge, UI génériques
        ├── pages/       # 1 page par module
        └── services/api.js
```
