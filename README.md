# GMAO Biomédicale

Application de **Gestion de Maintenance Assistée par Ordinateur** pour équipements
biomédicaux (échographes) : suivi du parc, maintenances préventives/correctives,
pannes, stock de pièces de rechange, et **notifications d'équipe en temps réel**.

## ✅ Ce qui a été mis en place

- **Connexion obligatoire** (nom d'utilisateur + mot de passe) : aucune page n'est
  accessible sans être authentifié.
- **Notifications à toute l'équipe** : dès qu'un membre ajoute un échographe, une
  panne, une maintenance, une planification, une pièce de rechange ou un mouvement
  de stock, **tous les autres membres reçoivent une alerte** indiquant son nom et
  les détails de l'ajout (cloche dans la barre supérieure + page "Notifications").
- **Tableau de bord** : indicateurs clés (échographes, pannes en cours, alertes de
  stock, membres actifs), maintenances planifiées à venir, dernières pannes,
  activité récente de l'équipe.
- **Toutes vos données existantes sont conservées** (établissements, services,
  échographes, historique des maintenances/pannes, utilisateurs).
- Interface propre et cohérente (identité visuelle dédiée), responsive.
- `render.yaml` corrigé (il contenait une erreur d'indentation qui empêchait le
  déploiement) et complété (collecte des fichiers statiques, variables
  d'environnement, clé secrète générée automatiquement).

## 📁 Structure du projet

```
gmao/
├── manage.py
├── requirements.txt
├── render.yaml
├── db.sqlite3                # votre base existante, données conservées
├── backend/                  # configuration Django (settings, urls, wsgi)
├── equipments/                # application principale
│   ├── models.py              # tous les modèles (existants + Notification)
│   ├── views.py                # dashboard, CRUD, notifications
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── utils.py                # notifier_ajout() : diffusion des alertes
│   ├── context_processors.py  # rend les notifications disponibles partout
│   └── migrations/
│       ├── 0001_initial.py     # reflète le schéma déjà en place dans votre BDD
│       └── 0002_notification.py# ajoute uniquement la table Notification
├── templates/                 # toutes les pages (login, dashboard, listes...)
└── static/css/style.css       # identité visuelle
```

## 🚀 Lancer le projet en local

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt

# Votre base existante est déjà incluse (db.sqlite3).
# Cette commande ajoute uniquement la nouvelle table "Notification",
# sans toucher à vos données existantes :
python manage.py migrate

python manage.py runserver
```

Rendez-vous sur http://127.0.0.1:8000/ — vous serez redirigé vers la page de
connexion. Utilisez un compte existant de votre base, ou créez-en un nouveau :

```bash
python manage.py createsuperuser
```

## ☁️ Déployer sur Render

1. Poussez ce dossier sur un dépôt Git (GitHub/GitLab).
2. Sur Render, créez un nouveau **Blueprint** à partir de ce dépôt : `render.yaml`
   configure automatiquement le service.
3. ⚠️ **Important** : SQLite n'est pas persistant sur Render (le disque est
   réinitialisé à chaque déploiement). Pour la production, il est fortement
   recommandé de décommenter la section `databases` dans `render.yaml` afin
   d'utiliser une base **PostgreSQL** managée par Render, et de migrer vos
   données existantes vers celle-ci avec `python manage.py dumpdata` /
   `loaddata`.

## 🔔 Comment fonctionne la notification d'équipe

Chaque création (échographe, panne, maintenance, planification, pièce, mouvement
de stock) passe par `equipments/utils.py::notifier_ajout()`, appelée
automatiquement par les vues de création. Une notification est enregistrée pour
**tous les membres** ; chacun a son propre statut « lu / non lu » (visible via la
cloche et la page *Notifications*), sans dupliquer les alertes en base.

## 🧩 Prochaines améliorations possibles (à la demande)

- Génération/lecture de QR codes sur les fiches équipement (le modèle `qr_code`
  et `QRImport` sont déjà en place, prêts à être branchés).
- Export PDF/Excel des rapports de maintenance.
- Rôles et permissions différenciés (technicien / responsable / lecture seule).
- Notifications par e-mail en plus des alertes in-app.
