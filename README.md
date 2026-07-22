# GMAO Biomédicale

Application de **Gestion de Maintenance Assistée par Ordinateur** pour équipements
biomédicaux (échographes) : suivi du parc, maintenances préventives/correctives,
pannes, stock de pièces de rechange, **notifications d'équipe en temps réel
(in-app + e-mail)**, **rôles et permissions**, **QR codes**, **exports PDF/Excel**
et un **moteur de suggestions automatiques**.

## ✅ Ce qui a été mis en place

- **Connexion obligatoire** (nom d'utilisateur + mot de passe) : aucune page n'est
  accessible sans être authentifié.
- **Notifications à toute l'équipe (in-app + e-mail)** : dès qu'un membre ajoute un
  échographe, une panne, une maintenance, une planification, une pièce de rechange
  ou un mouvement de stock, **tous les autres membres reçoivent une alerte**
  (cloche + page *Notifications*) et un **e-mail** (si une adresse est configurée).
- **Rôles & permissions** — 3 groupes Django :
  - **Responsable** : accès complet (ajout, modification, suppression).
  - **Technicien** : peut ajouter et modifier, mais pas supprimer.
  - **Lecture seule** : consultation uniquement, aucune action de modification.
  Les boutons d'ajout/modification/suppression sont automatiquement masqués selon
  le rôle de l'utilisateur connecté. Les groupes sont créés automatiquement à la
  migration (`0004_create_roles`) ou via `python manage.py setup_roles`.
- **QR codes** : génération automatique à la création d'un échographe, affichée
  sur sa fiche détail. Une page **Scanner QR** (`/qr/scanner/`) permet de retrouver
  l'équipement à partir du contenu scanné (URL ou n° de série).
- **Moteur de suggestions automatiques** (page *Suggestions* + section sur le
  tableau de bord) :
  - pièce sous son seuil d'alerte → suggestion de commande (avec fournisseur) ;
  - échographe sans date de maintenance ou dont la date approche/est dépassée →
    suggestion de planification ;
  - ≥ 2 pannes sur le même équipement en moins de 90 jours → alerte de panne
    récurrente ;
  - technicien déjà intervenu ≥ 2 fois sur un équipement → suggestion
    d'affectation lors d'une nouvelle panne.
  Chaque suggestion peut être marquée comme traitée ; les doublons sont évités.
- **Exports PDF / Excel** (reportlab / openpyxl) des listes de maintenances et de
  pannes, accessibles via des boutons sur les pages correspondantes.
- **Tableau de bord** : indicateurs clés, maintenances planifiées à venir,
  dernières pannes, suggestions actives, activité récente de l'équipe.
- **Toutes vos données existantes sont conservées** (établissements, services,
  échographes, historique des maintenances/pannes, utilisateurs).
- Interface propre et cohérente (identité visuelle dédiée), responsive.

## 📁 Structure du projet

```
gmao/
├── manage.py
├── requirements.txt
├── render.yaml
├── db.sqlite3                  # votre base existante, données conservées
├── backend/                    # configuration Django (settings, urls, wsgi)
├── equipments/                 # application principale
│   ├── models.py                # tous les modèles (+ Suggestion)
│   ├── views.py                 # dashboard, CRUD, rôles, suggestions, QR, exports
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── utils.py                  # notifications (in-app + email), QR, moteur de suggestions
│   ├── context_processors.py    # notifications, suggestions, permissions dispo partout
│   ├── management/commands/
│   │   └── setup_roles.py        # (re)crée les 3 groupes de rôles
│   └── migrations/
│       ├── 0001_initial.py
│       ├── 0002_notification.py
│       ├── 0003_suggestion.py    # ajoute le modèle Suggestion
│       └── 0004_create_roles.py  # crée automatiquement les groupes de rôles
├── templates/                   # toutes les pages (login, dashboard, listes...)
│   └── equipments/
│       ├── suggestion_list.html
│       └── qr_scan.html
└── static/css/style.css         # identité visuelle
```

## 🚀 Lancer le projet en local

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt

# Votre base existante est déjà incluse (db.sqlite3).
# Cette commande ajoute les nouvelles tables (Suggestion) et crée les
# groupes de rôles, sans toucher à vos données existantes :
python manage.py migrate

python manage.py runserver
```

Rendez-vous sur http://127.0.0.1:8000/ — vous serez redirigé vers la page de
connexion. Utilisez un compte existant de votre base, ou créez-en un nouveau :

```bash
python manage.py createsuperuser
```

### Attribuer un rôle à un utilisateur

Dans l'admin Django (`/admin/`), ouvrez l'utilisateur concerné et ajoutez-le au
groupe **Responsable**, **Technicien** ou **Lecture seule**. Un utilisateur sans
groupe, ou un compte staff/superutilisateur, conserve un accès complet par défaut.

### Configurer l'envoi d'e-mails

Par défaut, les e-mails sont simplement affichés dans la console (aucune
configuration requise). Pour un envoi réel via SMTP, définissez ces variables
d'environnement :

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-compte@exemple.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=GMAO Biomédicale <no-reply@exemple.com>
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
4. Pensez à définir les variables d'environnement e-mail (voir ci-dessus) dans
   les paramètres du service Render si vous souhaitez des notifications par
   e-mail réelles.

## 🔔 Comment fonctionne la notification d'équipe

Chaque création (échographe, panne, maintenance, planification, pièce, mouvement
de stock) passe par `equipments/utils.py::notifier_ajout()`, appelée
automatiquement par les vues de création. Une notification est enregistrée pour
**tous les membres** (chacun a son propre statut « lu / non lu ») et un e-mail est
envoyé en tâche de fond aux membres actifs disposant d'une adresse e-mail.

## 💡 Comment fonctionne le moteur de suggestions

Après chaque enregistrement pertinent (pièce, échographe, panne), les fonctions de
`equipments/utils.py` évaluent les conditions (stock bas, maintenance à prévoir,
récurrence de pannes, technicien fréquent) et créent une `Suggestion` si les
critères sont remplis — en évitant les doublons grâce à une clé d'unicité. Les
suggestions actives apparaissent sur le tableau de bord et sur la page dédiée, où
elles peuvent être marquées comme traitées.

## 🧩 Prochaines améliorations possibles (à la demande)

- Historique des suggestions traitées avec filtres.
- Tâche planifiée (Celery/cron) pour revérifier les échéances de maintenance
  même sans nouvel enregistrement.
- Notifications push mobiles.
- Export PDF/Excel pour le parc d'échographes et le stock de pièces.
