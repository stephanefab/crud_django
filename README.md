# crud1 — Projet d'apprentissage Django

Petit projet **Django 6.0** pour apprendre : structure projet/app, ORM, templates, et front avec **Bootstrap 5.3**. Gère une liste de clients (`Customer`).

---

## 📚 Guides

Quatre mémos rédigés au fil de l'apprentissage, à la racine du projet :

| Guide | Contenu |
| ----- | ------- |
| [DJANGO.md](DJANGO.md) | Structure projet/app, vues, URLs, templates, héritage, filtres |
| [MODELS.md](MODELS.md) | L'ORM, CRUD, requêtes, relations, pagination, recherche |
| [COMMANDS.md](COMMANDS.md) | `manage.py` et les commandes personnalisées (seed) |
| [BOOTSTRAP.md](BOOTSTRAP.md) | Grille, menu, flex, images, formulaires, alertes, cards, couleurs |

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

Puis ouvrir **http://127.0.0.1:8000/company/**

---

## 🗂️ Structure

```
crud1/
├── config/                 # LE PROJET (settings, urls racine)
├── company/                # L'APP
│   ├── models.py           # modèle Customer
│   ├── views.py            # home_view, customers_list_view
│   ├── urls.py             # routes de l'app
│   ├── templates/company/  # index.html, customers.html
│   └── management/commands/ # seed_customers.py
├── templates/              # base.html (partagé)
├── manage.py
└── *.md                    # les 4 guides
```

---

## 🔗 Routes

| URL | Vue | Page |
| --- | --- | ---- |
| `/company/` | `home_view` | accueil |
| `/company/customers` | `customers_list_view` | liste des clients |
| `/admin/` | — | administration Django |

---

## 🛠️ Commandes utiles

```powershell
python manage.py seed_customers [n]   # créer n clients fictifs (défaut 100)
python manage.py shell                # shell Python avec Django
python manage.py createsuperuser      # créer un compte admin
python manage.py makemigrations       # après une modif de models.py
python manage.py migrate              # appliquer les migrations
```

---

## ⚙️ Stack

- **Django 6.0** (Python)
- **SQLite** (base de données par défaut)
- **Bootstrap 5.3.8** (CDN, dans `templates/base.html`)
