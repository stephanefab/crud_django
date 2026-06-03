# crud1 — Projet d'apprentissage Django

Projet **Django 6.0** pour apprendre le framework de bout en bout : structure projet/app, ORM, **CRUD complet** (formulaires, validation, `ModelForm`), authentification, recherche, pagination, et front avec **Bootstrap 5.3**. Gère une liste de clients (`Customer`).

---

## 📚 Guides

Une bibliothèque de mémos rédigés au fil de l'apprentissage, à la racine du projet. [DJANGO.md](DJANGO.md) est le point d'entrée (il renvoie vers les autres).

**Cœur du framework**

| Guide | Contenu |
| ----- | ------- |
| [DJANGO.md](DJANGO.md) | Structure projet/app, vues, objet `request`, URLs, templates, CRUD, settings, upload, statics, serveur |
| [MODELS.md](MODELS.md) | L'ORM, CRUD, requêtes, relations, migrations, pagination, recherche, modèles avancés |
| [CBV.md](CBV.md) | Vues génériques (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, mixins) |
| [SIGNALS.md](SIGNALS.md) | Signaux (`post_save`, `pre_save`, `*_delete`, auth, custom) |

**Données & sécurité**

| Guide | Contenu |
| ----- | ------- |
| [DATABASE-ENV.md](DATABASE-ENV.md) | Bases de données (SQLite, PostgreSQL, MySQL, Oracle, multi-BD), migrations, base existante, variables d'environnement |
| [AUTH.md](AUTH.md) | Authentification & autorisation : login/logout, inscription, permissions, groupes |
| [DJANGO-ADMIN.md](DJANGO-ADMIN.md) | Le site d'administration (enregistrer, personnaliser, inlines, actions) |

**Qualité & exploitation**

| Guide | Contenu |
| ----- | ------- |
| [TESTS.md](TESTS.md) | Tests automatisés (modèles, vues, formulaires, auth, couverture, pytest) |
| [LOGGING.md](LOGGING.md) | Logs (config, fichier + rotation, formatage) et audit |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Mise en production et hébergeurs gratuits |

**Outils & front**

| Guide | Contenu |
| ----- | ------- |
| [COMMANDS.md](COMMANDS.md) | `manage.py` et les commandes personnalisées (seed) |
| [BOOTSTRAP.md](BOOTSTRAP.md) | Grille, menu, flex, images, formulaires, alertes, cards, couleurs |

> 📄 Tous les guides sont convertissables en PDF avec [md_to_pdf.py](md_to_pdf.py) : `python md_to_pdf.py` (tous) ou `python md_to_pdf.py ./DJANGO.md` (un seul).

---

## 🚀 Démarrage

```powershell
# 1. Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# 2. Appliquer les migrations
python manage.py migrate

# 3. (optionnel) Remplir la base avec des clients fictifs
python manage.py seed_customers 100

# 4. Lancer le serveur
python manage.py runserver
```

Puis ouvrir **http://127.0.0.1:8000/company/customers/**

---

## 🗂️ Structure

```
crud1/
├── config/                 # LE PROJET (settings, urls racine)
├── company/                # L'APP
│   ├── models.py           # modèle Customer
│   ├── forms.py            # CustomerForm (ModelForm)
│   ├── views.py            # CRUD : liste (+recherche/pagination), détail, create, update, delete
│   ├── urls.py             # routes de l'app
│   ├── admin.py            # enregistrement dans l'admin
│   ├── templates/company/  # customers.html, customer_detail.html, customer_add.html, customer_update.html
│   └── management/commands/ # seed_customers.py
├── templates/              # base.html (partagé, Bootstrap)
├── manage.py
├── md_to_pdf.py            # export des guides .md en PDF
└── *.md                    # les guides
```

---

## 🔗 Routes

| URL | Vue | Page |
| --- | --- | ---- |
| `/company/` | `home_view` | accueil |
| `/company/customers/` | `customers_list_view` | liste (recherche + pagination) |
| `/company/customers/new` | `customers_create` | créer un client |
| `/company/customers/<id>` | `customer_detail_view` | fiche d'un client |
| `/company/customers/update/<id>` | `customer_update` | modifier un client |
| `/company/customers/delete/<id>` | `customer_delete` | supprimer un client |
| `/admin/` | — | administration Django |

---

## 🛠️ Commandes utiles

```powershell
python manage.py seed_customers [n]   # créer n clients fictifs (défaut 100)
python manage.py shell                # shell Python avec Django
python manage.py createsuperuser      # créer un compte admin
python manage.py makemigrations       # après une modif de models.py
python manage.py migrate              # appliquer les migrations
python manage.py test                 # lancer les tests
```

---

## ⚙️ Stack

- **Django 6.0** (Python)
- **SQLite** (base de données par défaut — voir [DATABASE-ENV.md](DATABASE-ENV.md) pour PostgreSQL)
- **Bootstrap 5.3.8** (CDN, dans `templates/base.html`)
