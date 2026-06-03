# Documentation Django — Guide de démarrage

> Mémo personnel sur un projet Django de bout en bout : structure projet/app, vues, objet `request`, URLs, templates, CRUD complet (formulaires HTML, validation, ModelForm, messages flash), upload de fichiers, statics/médias et serveur (wsgi/asgi).
> Docs liées : [MODELS.md](MODELS.md) (modèles & ORM) · [DJANGO-ADMIN.md](DJANGO-ADMIN.md) (l'admin) · [AUTH.md](AUTH.md) (authentification, login/logout, permissions) · [DATABASE-ENV.md](DATABASE-ENV.md) (bases de données & variables d'environnement) · [TESTS.md](TESTS.md) (tests automatisés) · [CBV.md](CBV.md) (vues génériques / Class-Based Views) · [SIGNALS.md](SIGNALS.md) (signaux) · [DEPLOYMENT.md](DEPLOYMENT.md) (déploiement & hébergeurs) · [LOGGING.md](LOGGING.md) (logs & audit).
> Basé sur **Django 6.0**.

---

## Sommaire

1. [Vocabulaire : projet vs app](#1-vocabulaire--projet-vs-app)
2. [Initialiser un projet](#2-initialiser-un-projet)
    - 2.1 Créer le projet · 2.2 Le fichier `settings.py`
3. [Créer une app](#3-créer-une-app)
4. [Enregistrer l&#39;app](#4-enregistrer-lapp-étape-oubliée-1-fois-sur-2)
5. [Créer une vue](#5-créer-une-vue)
6. [L&#39;objet `request`](#6-lobjet-request)
    - 6.1 C'est quoi `request` ? · 6.2 Attributs essentiels · 6.3 GET vs POST · 6.4 Lire les données · 6.5 Mémo
7. [Configurer les URLs](#7-configurer-les-urls)
    - 7.1 Anatomie de `path()` · 7.2 Projet → app · 7.3 `include()` · 7.4 Paramètres · 7.5 Query string · 7.6 `re_path` · 7.7 Namespaces
8. [Comment accéder à une page](#8-comment-accéder-à-une-page)
9. [Les templates](#9-les-templates)
    - 9.1 Deux emplacements · 9.2 Sous-dossier au nom de l'app · 9.3 Tout centraliser · 9.4 Héritage · 9.5 Variables & logique · 9.6 Filtres
10. [CRUD avec les formulaires HTML de base](#10-crud-avec-les-formulaires-html-de-base)
    - 10.1 Notions clés · 10.2 URLs · 10.3 CREATE · 10.4 READ · 10.5 UPDATE · 10.6 DELETE · 10.7 Cycle · 10.8 Pièges · 10.9 Messages flash · 10.10 Validation · 10.11 ModelForm · 10.12 Garder les données · 10.13 Repeupler les champs
11. [Upload de fichiers et d'images](#11-upload-de-fichiers-et-dimages)
    - 11.1 MEDIA_ROOT/URL · 11.2 FileField/ImageField · 11.3 multipart · 11.4 request.FILES · 11.5 Afficher & limiter · 11.6 Compresser · 11.7 Stockage externe · 11.8 Récap
12. [Fichiers statiques vs médias](#12-fichiers-statiques-static-vs-médias-media)
    - 12.1 Config statics · 12.2 Utilisation · 12.3 collectstatic · 12.4 Récap
13. [Serveur : `wsgi.py` et `asgi.py`](#13-serveur--wsgipy-et-asgipy)
    - 13.1 Interface serveur · 13.2 Synchrone vs async · 13.3 Lequel choisir · 13.4 Contenu des fichiers · 13.5 Démarrer · 13.6 Mémo
14. [Récapitulatif du flux complet](#14-récapitulatif-du-flux-complet)
15. [Checklist mémo](#15-checklist-mémo)

---

## 1. Vocabulaire : projet vs app

C'est **la** distinction fondamentale de Django.

|           | **Projet** (`config/`)                   | **App** (`company/`, `shop/`...)               |
| --------- | ------------------------------------------------ | -------------------------------------------------------- |
| Rôle     | Le site complet, la configuration globale        | Un module fonctionnel réutilisable                      |
| Quantité | **1 seul** par site                        | **Plusieurs** par projet                           |
| Contient  | `settings.py`, `urls.py` racine, `wsgi.py` | `models.py`, `views.py`, `urls.py`, `templates/` |
| Analogie  | La maison entière + le tableau électrique      | Une pièce (cuisine, salon...)                           |

> 💡 Une **app** est censée faire **une chose** (gérer les entreprises, gérer un blog...). Un **projet** assemble plusieurs apps pour former le site.

Structure de ton projet actuel :

```
crud1/                  ← dossier racine du projet
├── config/             ← LE PROJET (config globale)
│   ├── settings.py     ← réglages
│   ├── urls.py         ← URLs racine (point d'entrée)
│   ├── wsgi.py / asgi.py
│   └── __init__.py
├── company/            ← UNE APP
│   ├── models.py       ← base de données
│   ├── views.py        ← logique des pages
│   ├── urls.py         ← URLs de l'app
│   ├── admin.py
│   └── __init__.py
├── templates/          ← templates partagés (à créer)
├── db.sqlite3          ← base de données
└── manage.py           ← outil en ligne de commande
```

---

## 2. Initialiser un projet

### 2.1 Créer le projet

```bash
# 1. Créer et activer un environnement virtuel
python -m venv venv
venv\Scripts\activate          # Windows (PowerShell : venv\Scripts\Activate.ps1)
# source venv/bin/activate     # macOS / Linux

# 2. Installer Django
pip install django

# 3. Créer le projet
# Le point "." final = créer dans le dossier courant, sans dossier en double
django-admin startproject config .
```

> Le nom `config` est une convention pour le dossier de configuration. On pourrait l'appeler `mysite`, mais `config` rend clair que ce dossier n'est PAS une app.

Ensuite, lancer le serveur de développement :

```bash
python manage.py runserver
# → http://127.0.0.1:8000/
```

### 2.2 Le fichier `settings.py`

`config/settings.py` est le **cerveau** du projet : un simple fichier **Python** qui contient **toute** la configuration. Django le lit au démarrage. Tu n'as pas besoin de tout comprendre d'un coup, mais voici les réglages que tu vas croiser le plus souvent.

```python
from pathlib import Path

# Racine du projet — sert à construire des chemins (templates/, media/, db…)
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Clé de chiffrement (sessions, tokens CSRF…). À garder SECRÈTE.
SECRET_KEY = "django-insecure-..."

# Mode debug : pages d'erreur détaillées. True en dev, OBLIGATOIREMENT False en prod.
DEBUG = True

# Domaines autorisés à servir le site (obligatoire dès que DEBUG = False)
ALLOWED_HOSTS = []

# Les apps activées (les tiennes + celles de Django) — voir section 4
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    # ...
    "company",
]

# Couches qui traitent CHAQUE requête (sécurité, sessions, auth…) — voir section 6
MIDDLEWARE = [ ... ]

ROOT_URLCONF = "config.urls"      # le fichier d'URLs racine (point d'entrée)

TEMPLATES = [ ... ]               # config des templates — voir section 9

WSGI_APPLICATION = "config.wsgi.application"   # point d'entrée serveur — voir section 13

# Base de données (SQLite par défaut — un simple fichier db.sqlite3)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Langue & fuseau (mettre "fr-fr" pour des dates/messages en français)
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"            # préfixe des fichiers statiques — voir section 12

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"   # type des clés primaires auto
```

**Les réglages à connaître :**

| Réglage | Rôle | Piège fréquent |
| ----------------- | ------------------------------------------- | ------------------------------------------ |
| `BASE_DIR` | racine du projet (chemins) | — |
| `SECRET_KEY` | clé de chiffrement | **ne jamais** la committer/exposer |
| `DEBUG` | erreurs détaillées | laisser `True` en prod = **faille de sécurité** |
| `ALLOWED_HOSTS` | domaines autorisés | vide + `DEBUG=False` → erreur 400 |
| `INSTALLED_APPS` | apps activées | app oubliée → modèle/template introuvable (section 4) |
| `DATABASES` | la base ([DATABASE-ENV.md](DATABASE-ENV.md)) | passer à PostgreSQL en prod |
| `LANGUAGE_CODE` | langue | `"fr-fr"` pour le français |
| `STATIC_URL` | fichiers statiques | voir section 12 |

> 🔐 **En production**, trois règles d'or :
> 1. `DEBUG = False`
> 2. `SECRET_KEY` lue depuis une **variable d'environnement** (jamais en dur dans le code)
> 3. `ALLOWED_HOSTS` renseigné avec ton vrai domaine
>
> Astuce courante : sortir les valeurs sensibles dans un fichier `.env` (avec `python-decouple` ou `django-environ`) et ajouter `.env` au `.gitignore`.

> 💡 `settings.py` étant du Python, tu peux y mettre de la logique (ex : `DEBUG = os.environ.get("DEBUG") == "1"`). Sur les gros projets, on le découpe même en plusieurs fichiers (`settings/base.py`, `settings/prod.py`).

---

## 3. Créer une app

```bash
python manage.py startapp company
```

Cela génère le dossier `company/` avec les fichiers de base (`models.py`, `views.py`, etc.).

> ⚠️ Créer l'app **ne suffit pas** : il faut encore l'enregistrer (étape 4).

---

## 4. Enregistrer l'app (étape oubliée 1 fois sur 2)

Dans `config/settings.py`, ajoute l'app dans `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'company',          # ← ton app ici
]
```

**Sans cette ligne :**

- Les `models` ne sont pas migrés en base.
- Les `templates/` de l'app ne sont pas trouvés (`APP_DIRS`).
- L'admin n'affiche pas tes modèles.

---

## 5. Créer une vue

Une **vue** = une fonction (ou classe) qui reçoit une requête et renvoie une réponse.

`company/views.py` :

```python
from django.shortcuts import render

def home_view(request):
    # 1er argument OBLIGATOIRE : request
    return render(request, "company/index.html")
```

> ❗ Erreur classique : `render("index.html")` sans `request`. Le **premier argument est toujours `request`**.

Trois façons courantes de répondre :

```python
from django.http import HttpResponse
from django.shortcuts import render, redirect

def exemple_texte(request):
    return HttpResponse("Bonjour")          # texte brut

def exemple_template(request):
    return render(request, "company/index.html", {"nom": "ACME"})  # template + données

def exemple_redirection(request):
    return redirect("company.index")        # redirige vers une URL nommée
```

Le 3ᵉ argument de `render` est le **contexte** : un dictionnaire de données passées au template.

### Sous le capot : `render()` est un raccourci

Certains tutos montrent la version « longue » avec `loader`. C'est **exactement la même chose** que `render()`, décomposée en étapes :

```python
from django.http import HttpResponse
from django.template import loader

def home_view(request):
    template = loader.get_template("company/index.html")   # 1. charger le template
    contexte = {"nom": "ACME"}
    return HttpResponse(template.render(contexte, request)) # 2. rendre → 3. réponse HTTP
```

…est équivalent à :

```python
from django.shortcuts import render

def home_view(request):
    return render(request, "company/index.html", {"nom": "ACME"})
```

| Étape | Version longue (`loader`)            | Rôle                          |
| ----- | ------------------------------------ | ----------------------------- |
| 1     | `loader.get_template("x.html")`      | Trouve et charge le template  |
| 2     | `template.render(contexte, request)` | Transforme template + données en HTML |
| 3     | `HttpResponse(html)`                 | Emballe le HTML dans une réponse HTTP |

`render()` enchaîne ces 3 étapes pour toi.

> ⚠️ Le `request` passé à `template.render(contexte, request)` est important : sans lui, `{% csrf_token %}`, `{{ user }}` et les *context processors* ne fonctionnent pas. C'est **pour ça que `render()` exige `request` en 1ᵉʳ argument** : il le transmet automatiquement.

**Quand utiliser la version longue ?** Quasi jamais en pratique — seulement si tu veux récupérer le HTML en **chaîne** sans l'envoyer tout de suite (générer un email, un PDF…). Pour une vue normale : **`render()`**.

---

## 6. L'objet `request`

Depuis la section 5, **toutes** tes vues commencent par `def ma_vue(request):` et tu écris `render(request, ...)`, `request.POST`, `request.method`… mais qu'est-ce que `request` exactement ? C'est **l'objet central** d'une vue.

### 6.1 C'est quoi `request` ?

À **chaque** fois qu'un navigateur appelle une URL, Django crée automatiquement un objet **`HttpRequest`** qui contient **tout** ce qu'on sait de la requête : la méthode HTTP, les données envoyées, l'utilisateur connecté, les cookies… Django le **passe en 1ᵉʳ argument** à ta vue. C'est pour ça que `request` est obligatoire (cf. l'erreur classique de la section 5).

```
Navigateur ──GET /company/customers/?page=2──►  Django crée un HttpRequest
                                                        │
                                                        ▼
                                          def customers_list_view(request):
                                                   request.method  → "GET"
                                                   request.GET     → {"page": "2"}
```

> 🧠 Tu ne crées **jamais** `request` toi-même : Django te le fournit. Tu te contentes de **lire** dedans.

### 6.2 Les attributs essentiels

| Attribut | Contient | Exemple |
| ------------------ | ------------------------------------------ | ------------------------------------ |
| `request.method` | la méthode HTTP | `"GET"`, `"POST"` |
| `request.GET` | les paramètres de l'URL (après `?`) | `?page=2` → `request.GET["page"]` |
| `request.POST` | les données d'un formulaire envoyé en POST | `request.POST["first_name"]` |
| `request.FILES` | les fichiers uploadés | `request.FILES["photo"]` (cf. section 11) |
| `request.user` | l'utilisateur connecté (ou `AnonymousUser`) | `request.user.is_authenticated` |
| `request.path` | le chemin demandé | `"/company/customers/"` |
| `request.session` | données conservées entre les requêtes | `request.session["panier"]` |
| `request.COOKIES` | les cookies du navigateur | `request.COOKIES.get("theme")` |
| `request.headers` | les en-têtes HTTP | `request.headers["User-Agent"]` |

### 6.3 GET vs POST : la distinction fondamentale

Deux **méthodes HTTP** que tu vas utiliser sans arrêt — elles n'ont pas le même rôle :

| | **GET** | **POST** |
| ----------------- | ------------------------------- | ----------------------------------------- |
| Sert à | **lire / afficher** | **modifier** (créer, éditer, supprimer) |
| Données | dans l'**URL** (`?q=acme&page=2`) | dans le **corps** (invisibles dans l'URL) |
| Où on les lit | `request.GET` | `request.POST` |
| Rejouable (F5) | sans risque | re-soumet le formulaire (d'où le PRG) |
| Exemple dans ce guide | recherche, pagination | création/édition de client |

C'est ce qui explique le motif qu'on retrouve dans toutes les vues qui traitent un formulaire :

```python
def ma_vue(request):
    if request.method == "POST":      # l'utilisateur a soumis le formulaire
        ... traiter request.POST ...
        return redirect(...)
    # sinon (GET) : afficher la page
    return render(request, "...")
```

### 6.4 Lire les données : `.get()` vs `[...]`

`request.GET` et `request.POST` se manipulent comme des **dictionnaires**, avec une nuance de sécurité :

```python
request.POST["first_name"]          # ❌ lève MultiValueDictKeyError si absent
request.POST.get("first_name")      # ✅ renvoie None si absent
request.POST.get("first_name", "")  # ✅ renvoie "" par défaut
```

> 💡 **Toujours préférer `.get()`** : un champ peut manquer (formulaire incomplet, checkbox décochée…), et `[...]` ferait planter la vue avec une erreur 500.

Cas particulier des **valeurs multiples** (checkboxes, `<select multiple>`) : `.get()` ne renvoie que la dernière. Pour récupérer **toute** la liste :

```python
request.POST.getlist("hobbies")     # → ["sport", "code"]
```

### 6.5 Mémo

```
request = tout ce que Django sait de la requête entrante (objet HttpRequest)
  request.method  → "GET" / "POST"   → quoi faire
  request.GET     → ?clé=valeur       → lecture (recherche, pagination)
  request.POST    → formulaire POST   → écriture (create/update/delete)
  request.FILES   → fichiers uploadés
  request.user    → utilisateur connecté
  lire : .get("clé")  (sûr)   plutôt que  ["clé"]  (plante si absent)
  multi : .getlist("clé")
```

---

## 7. Configurer les URLs

Le rôle de `urls.py` : faire correspondre une **URL** (ce que tape l'utilisateur) à une **vue** (la fonction qui répond). C'est le **routeur** de Django. À chaque requête, Django parcourt `urlpatterns` **de haut en bas** et s'arrête à la **première** route qui correspond.

### 7.1 Anatomie de `path()`

```python
path("customers/<int:id>", views.customer_detail, name="company.customerDetail")
#     └──────┬──────────┘   └───────┬──────────┘   └──────────┬───────────────┘
#         route (str)            vue à appeler          nom (pour {% url %} / reverse)
```

| Argument | Rôle | Obligatoire |
| ---------- | ---------------------------------------------- | ----------- |
| **route** | le motif d'URL à reconnaître (chaîne) | ✅ |
| **view** | la vue exécutée si ça correspond | ✅ |
| **name** | identifiant pour générer l'URL sans l'écrire en dur | recommandé |
| **kwargs** | dict de valeurs fixes passées à la vue | optionnel |

> ❗ Deux pièges classiques :
> - La variable **doit** s'appeler exactement `urlpatterns` (pas `urlspattern`).
> - Le chemin **ne commence jamais par `/`**. On met `""`, pas `"/"`.

### 7.2 Les deux niveaux : projet → app

Django utilise **deux niveaux** d'URLs : le projet **délègue** à chaque app via `include()`.

**Niveau 1 — URLs du projet (`config/urls.py`)** :

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('company/', include("company.urls")),   # délègue tout "company/..." à l'app
]
```

**Niveau 2 — URLs de l'app (`company/urls.py`)** :

```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="company.index"),
    path("customers/", views.customers_list_view, name="company.customers"),
]
```

**Comment les deux se combinent** — le préfixe du projet + le chemin de l'app = l'URL finale :

```
config/urls.py        company/urls.py        URL finale
  "company/"     +        ""           =     /company/
  "company/"     +   "customers/"      =     /company/customers/
```

### 7.3 `include()` : déléguer à une app

`include("company.urls")` dit : « tout ce qui commence par `company/`, c'est l'app `company` qui gère ». Avantages :

- **Découplage** : chaque app gère ses propres routes, le projet ne connaît que le préfixe.
- **Réutilisabilité** : on peut brancher la même app sous un autre préfixe.
- **Lisibilité** : `config/urls.py` reste court.

> 💡 Django **retire le préfixe** avant de passer la main : sous `path('company/', include(...))`, l'app voit `customers/` et non `company/customers/`. C'est pour ça que les routes de l'app ne répètent pas `company/`.

Variante sans fichier séparé (petits projets) — `include` accepte une liste inline :

```python
from django.urls import include, path

urlpatterns = [
    path('company/', include([
        path('', views.home_view, name='company.index'),
        path('customers/', views.customers_list_view, name='company.customers'),
    ])),
]
```

### 7.4 URLs avec paramètres (convertisseurs de chemin)

Pour capturer une partie variable de l'URL (un id, un slug…), on utilise la syntaxe **`<convertisseur:nom>`**. La valeur capturée est passée à la vue **en argument du même nom**.

```python
# urls.py
path("customers/<int:id>", views.customer_detail, name="company.customerDetail")
```

```python
# views.py — le paramètre "id" arrive en argument
def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)
    return render(request, "company/customer_detail.html", {"customer": customer})
```

```
/customers/5   →   id = 5  (un int)
```

**Les convertisseurs intégrés :**

| Convertisseur | Capture | Exemple d'URL |
| ----------- | ------------------------------------------------ | ------------------ |
| `str` | tout texte **sauf** le `/` (c'est le défaut) | `<str:name>` |
| `int` | un entier positif (0, 1, 2…) | `<int:id>` |
| `slug` | lettres/chiffres/tirets : `mon-article-2` | `<slug:slug>` |
| `uuid` | un UUID : `075194d3-...-95e6` | `<uuid:ref>` |
| `path` | comme `str` **mais accepte le `/`** | `<path:chemin>` |

> 🧠 `<int:id>` ne matche **que** des nombres : `/customers/abc` renverra **404** (pas une erreur 500). C'est une première validation gratuite.

**Plusieurs paramètres** dans une même route :

```python
path("blog/<int:year>/<slug:slug>", views.article, name="blog.article")
# /blog/2026/mon-premier-post  →  article(request, year=2026, slug="mon-premier-post")
```

### 7.5 Paramètres fixes et query string

**Valeurs fixes** via le 4ᵉ argument `kwargs` (utile pour réutiliser une vue avec un réglage différent) :

```python
path("archives/", views.list_items, {"status": "archived"}, name="items.archived")
# la vue reçoit : list_items(request, status="archived")
```

**Query string** (`?page=2&sort=nom`) : celle-ci ne se déclare **pas** dans `path()`. On la lit dans la vue via `request.GET` :

```python
# URL : /customers/?page=2
def customers_list_view(request):
    page = request.GET.get("page", 1)   # "2"  (ou 1 par défaut)
    ...
```

> Règle simple : ce qui fait partie du **chemin** → `path()` ; ce qui est après le **`?`** → `request.GET`.

### 7.6 `re_path` : pour les motifs complexes (rare)

Quand les convertisseurs ne suffisent pas, `re_path` accepte une **expression régulière**. Les groupes nommés `(?P<nom>...)` deviennent les arguments de la vue.

```python
from django.urls import re_path

re_path(r"^customers/(?P<id>[0-9]{1,6})$", views.customer_detail)
# capture un id de 1 à 6 chiffres
```

> 👉 En pratique, `path()` + convertisseurs couvre 95 % des cas. On ne sort `re_path` que pour des contraintes que les convertisseurs ne savent pas exprimer.

### 7.7 Nommer les URLs et les namespaces

Le `name=` permet de **ne jamais écrire l'URL en dur** (voir section 8). Pour éviter les collisions de noms entre apps, on peut ajouter un **namespace** par app avec `app_name` :

```python
# company/urls.py
app_name = "company"
urlpatterns = [
    path("", views.home_view, name="index"),
    path("customers/", views.customers_list_view, name="customers"),
]
```

On référence alors avec `namespace:name` :

```python
redirect("company:index")            # au lieu de "company.index"
{% url 'company:customers' %}
```

> 💡 Dans **ce projet**, on n'utilise pas `app_name` : on préfixe simplement les noms à la main (`name="company.index"`). Les deux approches marchent ; `app_name` est juste plus robuste quand le projet grossit. **Ne mélange pas les deux** (`company.index` ≠ `company:index`).

---

## 8. Comment accéder à une page

Une fois le serveur lancé (`python manage.py runserver`) :

```
http://127.0.0.1:8000/company/
```

### Ne jamais écrire les URLs « en dur »

Utilise les **noms d'URL** (`name="..."`) plutôt que les chemins littéraux. Ainsi, si tu changes l'URL, tout reste fonctionnel.

**Dans un template :**

```html
<a href="{% url 'company.index' %}">Accueil</a>
```

**Dans une vue (Python) :**

```python
from django.urls import reverse
from django.shortcuts import redirect

return redirect("company.index")
# ou
url = reverse("company.index")
```

### Rediriger vers une URL qui attend des paramètres

Pour une route comme `path("customers/update/<int:id>", ...)`, il faut **passer la valeur** du paramètre. La syntaxe **diffère selon l'outil** — c'est une source de bugs classique.

**`redirect()` et `{% url %}` → valeurs « à plat »** (jamais de dict) :

```python
redirect("company.customerUpdate", customer.id)        # positionnel
redirect("company.customerUpdate", id=customer.id)     # nommé (le nom = <int:id>)
```

```html
<a href="{% url 'company.customerUpdate' customer.id %}">Modifier</a>
<a href="{% url 'company.customerUpdate' id=customer.id %}">Modifier</a>
```

**`reverse()` → `args=` (liste) ou `kwargs=` (dict)** :

```python
reverse("company.customerUpdate", args=[customer.id])
reverse("company.customerUpdate", kwargs={"id": customer.id})
```

**Plusieurs paramètres** (`path("blog/<int:year>/<slug:slug>", ...)`) :

```python
redirect("blog.article", 2026, "mon-post")               # positionnel, dans l'ordre
redirect("blog.article", year=2026, slug="mon-post")     # nommé, ordre libre
reverse("blog.article", kwargs={"year": 2026, "slug": "mon-post"})
```

> 🧠 **Le piège** : c'est **`reverse()`** qui prend un **dict** (`kwargs={...}`), **pas `redirect()`**. Écrire `redirect("...", {"id": 5})` est **faux** — `redirect()` veut les valeurs directement (`redirect("...", id=5)`).

| Outil | Sans paramètre | Avec paramètre(s) |
| ------------- | ------------------------ | --------------------------------------- |
| `redirect()` | `redirect("name")` | `redirect("name", val)` / `redirect("name", id=val)` |
| `{% url %}` | `{% url 'name' %}` | `{% url 'name' val %}` / `{% url 'name' id=val %}` |
| `reverse()` | `reverse("name")` | `reverse("name", args=[val])` / `reverse("name", kwargs={"id": val})` |

> ⚠️ Après un **POST réussi**, on redirige généralement vers la **liste** ou le **détail** (`redirect("company.customerDetail", obj.id)`), pas vers le formulaire d'édition (sinon on boucle dessus).

---

## 9. Les templates

### 9.1 Deux endroits possibles

| Emplacement                    | Réglage           | Usage                                             |
| ------------------------------ | ------------------ | ------------------------------------------------- |
| `templates/` (racine projet) | `DIRS`           | Templates**partagés** (ex : `base.html`) |
| `app/templates/`             | `APP_DIRS: True` | Templates**propres à une app**             |

Configuration dans `config/settings.py` :

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # templates globaux
        'APP_DIRS': True,                   # + templates de chaque app
        ...
    },
]
```

### 9.2 Pourquoi `app/templates/app/...` (le sous-dossier répété)

Quand `APP_DIRS: True`, Django fusionne **tous** les `templates/` de **toutes** les apps dans **un seul espace de noms global**. Le nom de l'app est « oublié ».

Du coup, sans précaution :

```
company/templates/index.html   ⎫
shop/templates/index.html      ⎬  → COLLISION : Django prend le 1er trouvé
```

`render(request, "index.html")` peut afficher le template d'une autre app sans erreur — bug silencieux.

La solution = un sous-dossier au nom de l'app pour rendre le chemin unique :

```
company/templates/company/index.html   →  "company/index.html"
shop/templates/shop/index.html          →  "shop/index.html"
```

> C'est une **convention** (recommandée par la doc officielle), pas une obligation technique. Mais dès qu'on a plusieurs apps, c'est indispensable.
>
> Le `base.html` global (dans `DIRS`) n'a **pas** besoin de ce sous-dossier : il est unique par nature.

### 9.3 Tout centraliser dans le dossier `templates/` racine

Au lieu d'éparpiller les templates dans chaque `app/templates/`, on peut **tout regrouper** dans le seul dossier `templates/` du projet, avec un **sous-dossier par app**. C'est une approche tout à fait valable (et appréciée pour garder une vue d'ensemble).

```
crud1/
├── templates/
│   ├── base.html
│   ├── company/
│   │   └── index.html
│   └── shop/
│       └── produit.html
├── company/          ← plus de dossier templates/ ici
├── shop/
```

Configuration (la même que d'habitude, `DIRS` suffit) :

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # ← tout passe par ici
        'APP_DIRS': True,                   # peut rester True sans problème
        ...
    },
]
```

> Tu peux laisser `APP_DIRS: True` (aucun conflit) ou le passer à `False` pour forcer tout le monde à utiliser le dossier central.

Dans les vues, **rien ne change** : on garde le préfixe au nom de l'app pour éviter les collisions (même raison qu'en 9.2 — tout est fusionné dans un espace de noms unique).

```python
return render(request, "company/index.html")   # → templates/company/index.html
return render(request, "shop/produit.html")     # → templates/shop/produit.html
```

| Approche                              | Avantage                                            |
| ------------------------------------- | --------------------------------------------------- |
| `templates/` central + sous-dossiers | Tout au même endroit, vue d'ensemble facile         |
| `app/templates/app/` (par app)       | App **autonome / portable** (réutilisable ailleurs) |

> 👉 Dans les deux cas, **garde le sous-dossier au nom de l'app**. C'est ce qui rend le chemin unique, pas l'emplacement physique du dossier.

### 9.4 L'héritage de templates

Un seul `base.html` partagé, dont héritent toutes les pages.

`templates/base.html` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <title>{% block title %}Mon site{% endblock %}</title>
</head>
<body>
    <nav>
        <a href="{% url 'company.index' %}">Accueil</a>
    </nav>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>© 2026</footer>
</body>
</html>
```

`company/templates/company/index.html` :

```html
{% extends "base.html" %}

{% block title %}Accueil — Company{% endblock %}

{% block content %}
    <h1>Liste des clients</h1>
    <p>Contenu spécifique à cette page.</p>
{% endblock %}
```

- `{% extends "base.html" %}` → hérite du squelette.
- `{% block X %}...{% endblock %}` → remplit les zones laissées vides dans le parent.
- Tout ce qui est hors d'un `block` (nav, footer) est partagé automatiquement.

**Pour ajouter une 2ᵉ, 3ᵉ app :** chaque app fait simplement `{% extends "base.html" %}`. Le `base.html` et la config ne bougent plus.

```
templates/base.html  ←── partagé par tout le projet
    ▲          ▲          ▲
    │          │          │   {% extends "base.html" %}
 company/    shop/      blog/
```

### 9.5 Variables et logique dans un template

```html
<!-- Afficher une variable du contexte -->
<h1>{{ titre }}</h1>

<!-- Boucle -->
<ul>
{% for customer in customers %}
    <li>{{ customer.first_name }} {{ customer.last_name }}</li>
{% endfor %}
</ul>

<!-- Condition -->
{% if user.is_authenticated %}
    <p>Bonjour {{ user.username }}</p>
{% else %}
    <a href="{% url 'login' %}">Se connecter</a>
{% endif %}
```

- `{{ ... }}` → afficher une **valeur**.
- `{% ... %}` → **logique** (boucle, condition, extends, block, url...).

### 9.6 Filtres : manipuler chaînes, dates, nombres, listes

Un **filtre** transforme une valeur avec la syntaxe `{{ valeur|filtre }}`. On peut les enchaîner, et certains prennent un argument avec `:`.

```django
{{ nom|upper }}                    {# applique upper #}
{{ nom|upper|truncatechars:10 }}   {# enchaînement #}
{{ prix|add:5 }}                   {# filtre avec argument #}
```

#### Chaînes de caractères

```django
{{ "bonjour"|upper }}            → BONJOUR
{{ "BONJOUR"|lower }}            → bonjour
{{ "bonjour le monde"|title }}  → Bonjour Le Monde
{{ "bonjour"|capfirst }}        → Bonjour
{{ "a b c"|cut:" " }}           → abc            {# supprime les espaces #}

{# Longueur & découpe #}
{{ "Bonjour"|length }}                       → 7
{{ "Bonjour le monde"|truncatechars:10 }}    → Bonjour l…
{{ "Bonjour le monde"|truncatewords:2 }}     → Bonjour le …
{{ "a,b,c"|slice:":2" }}                     → a,        {# slicing Python #}

{# Valeur par défaut #}
{{ texte|default:"(vide)" }}        {# si texte est falsy #}
{{ texte|default_if_none:"N/A" }}   {# seulement si None #}

{# HTML / sécurité #}
{{ html|safe }}            {# ne pas échapper le HTML #}
{{ html|escape }}          {# forcer l'échappement #}
{{ html|striptags }}       {# enlever les balises HTML #}
{{ texte|linebreaks }}     {# \n → <br> et <p> #}
{{ "https://x.com"|urlize }}   {# liens cliquables #}
```

#### Dates et heures

La date du contexte (objet `datetime`) se formate avec `date` et `time` :

```django
{{ ma_date|date:"d/m/Y" }}         → 02/06/2026
{{ ma_date|date:"l d F Y" }}       → mardi 02 juin 2026
{{ ma_date|date:"d/m/Y H:i" }}     → 02/06/2026 14:30
{{ ma_date|time:"H:i" }}           → 14:30

{# Formats nommés (respectent la locale) #}
{{ ma_date|date:"SHORT_DATE_FORMAT" }}   → 02/06/2026
{{ ma_date|date:"DATETIME_FORMAT" }}

{# Distance par rapport à maintenant #}
{{ ma_date|timesince }}     → "il y a 3 jours"
{{ ma_date|timeuntil }}     → "dans 2 heures"
```

Codes de format les plus utiles :

| Code        | Sens                      | Exemple   |
| ----------- | ------------------------- | --------- |
| `d` / `j` | jour (02 / 2)             | `02`    |
| `m` / `n` | mois (06 / 6)             | `06`    |
| `Y` / `y` | année (2026 / 26)         | `2026`  |
| `H` / `i` | heures / minutes          | `14` `30` |
| `l` / `D` | jour semaine (long/court) | `mardi` |
| `F` / `M` | mois (long/court)         | `juin`  |

> Pour avoir « mardi » et « juin » en français : `LANGUAGE_CODE = 'fr-fr'` + `USE_I18N = True` dans `settings.py`.

#### Nombres

```django
{{ 1234.5678|floatformat }}      → 1234.6     {# 1 décimale par défaut #}
{{ 1234.5678|floatformat:2 }}    → 1234.57
{{ 3|add:5 }}                    → 8
{{ valeur|divisibleby:2 }}       → True/False
{{ 0.85|floatformat:0 }}         → 1
```

**Filtres `humanize`** — ajoute `'django.contrib.humanize'` dans `INSTALLED_APPS`, puis :

```django
{% load humanize %}

{{ 1234567|intcomma }}      → 1 234 567
{{ 1000000|intword }}       → 1.0 million
{{ 5|apnumber }}            → cinq
{{ ma_date|naturaltime }}   → "il y a 4 minutes"
{{ ma_date|naturalday }}    → "aujourd'hui", "hier"...
```

#### Listes et dictionnaires

```django
{{ liste|length }}          → nombre d'éléments
{{ liste|first }}           → premier élément
{{ liste|last }}            → dernier élément
{{ liste|join:", " }}       → "a, b, c"
{{ liste|slice:":3" }}      → 3 premiers
{{ liste|random }}          → un élément au hasard
{{ liste|dictsort:"nom" }}  → trie une liste de dicts par clé "nom"
{{ dico|length }}           → nombre de clés
```

#### Exemple complet

Vue :

```python
from datetime import datetime

def home_view(request):
    contexte = {
        "entreprise": "acme corp",
        "employes": ["Alice", "Bob", "Chloé"],
        "ca": 1234567.5,
        "creee_le": datetime(2020, 3, 15, 9, 30),
    }
    return render(request, "company/index.html", contexte)
```

Template :

```django
{% load humanize %}

<h1>{{ entreprise|title }}</h1>              {# Acme Corp #}

<p>{{ employes|length }} employé(s) : {{ employes|join:", " }}</p>
{# 3 employé(s) : Alice, Bob, Chloé #}

<p>CA : {{ ca|floatformat:2|intcomma }} €</p>   {# 1 234 567,50 € #}

<p>Créée le {{ creee_le|date:"d/m/Y" }}, soit {{ creee_le|timesince }}.</p>
{# Créée le 15/03/2020, soit il y a 6 ans, 2 mois. #}
```

---

## 10. CRUD avec les formulaires HTML de base

**CRUD** = **C**reate, **R**ead, **U**pdate, **D**elete : les 4 opérations de base sur des données. Ici on les fait avec de **simples formulaires HTML** (`<form>`), **sans** `Django Forms` ni `ModelForm` — pour bien comprendre le mécanisme brut. On s'appuie sur le modèle `Customer` du projet :

```python
# company/models.py
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField(max_length=100)
    phone      = models.CharField(max_length=15)
    address    = models.TextField(max_length=300)
```

> ⚠️ Avant tout : `python manage.py makemigrations` puis `python manage.py migrate` pour créer la table en base.

### 10.1 Les 2 notions clés des formulaires HTML

1. **`method="post"`** : pour **modifier** des données (créer/éditer/supprimer), on utilise toujours `POST`. `GET` sert seulement à **lire/afficher**.
2. **`{% csrf_token %}`** : Django **bloque** tout POST sans ce jeton (sécurité anti-CSRF). À mettre **dans chaque `<form method="post">`**, sinon erreur **403**.

Côté vue, on récupère les valeurs envoyées via `request.POST.get("nom_du_champ")` — le `name` de chaque `<input>` est la clé.

```
<input name="first_name">   →   request.POST.get("first_name")
```

### 10.2 Mise en place des URLs

`company/urls.py` — une route par opération :

```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="company.index"),

    # READ : liste
    path("customers/", views.customers_list_view, name="company.customers"),
    # CREATE : formulaire + enregistrement
    path("customers/new", views.customers_create, name="company.customerCreate"),
    # UPDATE : formulaire pré-rempli + mise à jour
    path("customers/<int:id>/edit", views.customers_update, name="company.customerUpdate"),
    # DELETE : suppression
    path("customers/<int:id>/delete", views.customers_delete, name="company.customerDelete"),
]
```

> `<int:id>` capture un nombre dans l'URL (ex : `/customers/3/edit`) et le passe à la vue en argument `id`.

### 10.3 CREATE — créer un client

**La vue gère 2 cas dans une seule fonction :**

- `GET` → on **affiche** le formulaire vide.
- `POST` → on **enregistre** puis on **redirige** vers la liste.

`company/views.py` :

```python
from django.shortcuts import render, redirect
from .models import Customer

def customers_create(request):
    if request.method == "POST":
        Customer.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
        )
        return redirect("company.customers")   # ↩ Post/Redirect/Get

    # méthode GET : afficher le formulaire vide
    return render(request, "company/customer_add.html")
```

> 🧠 **Pattern Post/Redirect/Get (PRG)** : après un POST réussi, on **redirige** (au lieu de `render`). Ça évite que l'utilisateur ré-enregistre en rafraîchissant la page (F5).

`company/templates/company/customer_add.html` :

```html
{% extends "base.html" %}
{% block title %}Nouveau client{% endblock %}

{% block content %}
<h1>Ajouter un client</h1>

<form method="post">
    {% csrf_token %}

    <label>Prénom <input type="text" name="first_name" required></label>
    <label>Nom <input type="text" name="last_name" required></label>
    <label>Email <input type="email" name="email" required></label>
    <label>Téléphone <input type="text" name="phone"></label>
    <label>Adresse <textarea name="address"></textarea></label>

    <button type="submit">Enregistrer</button>
</form>
{% endblock %}
```

### 10.4 READ — lister les clients

```python
def customers_list_view(request):
    return render(request, "company/customers.html",
                  {"customers": Customer.objects.all()})
```

`company/templates/company/customers.html` :

```html
{% extends "base.html" %}
{% block title %}Clients{% endblock %}

{% block content %}
<h1>Clients</h1>
<a href="{% url 'company.customerCreate' %}">+ Nouveau client</a>

<table>
    <tr><th>Nom</th><th>Email</th><th>Téléphone</th><th>Actions</th></tr>

    {% for c in customers %}
    <tr>
        <td>{{ c.first_name }} {{ c.last_name }}</td>
        <td>{{ c.email }}</td>
        <td>{{ c.phone }}</td>
        <td>
            <a href="{% url 'company.customerUpdate' c.id %}">Éditer</a>
            <!-- DELETE doit passer par un form POST (voir 10.6) -->
            <form method="post" action="{% url 'company.customerDelete' c.id %}"
                  style="display:inline"
                  onsubmit="return confirm('Supprimer ce client ?')">
                {% csrf_token %}
                <button type="submit">Supprimer</button>
            </form>
        </td>
    </tr>
    {% empty %}
    <tr><td colspan="4">Aucun client pour l'instant.</td></tr>
    {% endfor %}
</table>
{% endblock %}
```

> `{% empty %}` s'affiche quand la liste est vide — pratique pour éviter un tableau désert.

### 10.5 UPDATE — modifier un client

Même logique que CREATE (GET affiche / POST enregistre), mais on **récupère d'abord** le client existant pour **pré-remplir** le formulaire.

```python
from django.shortcuts import get_object_or_404

def customers_update(request, id):
    customer = get_object_or_404(Customer, id=id)   # 404 si introuvable

    if request.method == "POST":
        customer.first_name = request.POST.get("first_name")
        customer.last_name  = request.POST.get("last_name")
        customer.email      = request.POST.get("email")
        customer.phone      = request.POST.get("phone")
        customer.address    = request.POST.get("address")
        customer.save()                              # UPDATE en base
        return redirect("company.customers")

    # GET : afficher le formulaire pré-rempli
    return render(request, "company/customer_edit.html", {"customer": customer})
```

> `get_object_or_404(Customer, id=id)` = `Customer.objects.get(id=id)` mais renvoie une **page 404** propre si l'id n'existe pas, au lieu d'une erreur 500.

`company/templates/company/customer_edit.html` — on remplit `value="..."` avec les données :

```html
{% extends "base.html" %}
{% block title %}Modifier {{ customer.first_name }}{% endblock %}

{% block content %}
<h1>Modifier le client</h1>

<form method="post">
    {% csrf_token %}

    <label>Prénom <input type="text" name="first_name" value="{{ customer.first_name }}" required></label>
    <label>Nom <input type="text" name="last_name" value="{{ customer.last_name }}" required></label>
    <label>Email <input type="email" name="email" value="{{ customer.email }}" required></label>
    <label>Téléphone <input type="text" name="phone" value="{{ customer.phone }}"></label>
    <label>Adresse <textarea name="address">{{ customer.address }}</textarea></label>

    <button type="submit">Mettre à jour</button>
</form>
{% endblock %}
```

> ⚠️ Pour un `<textarea>`, la valeur va **entre les balises** (`<textarea>{{ ... }}</textarea>`), pas dans un attribut `value`.

### 10.6 DELETE — supprimer un client

```python
def customers_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == "POST":
        customer.delete()
    return redirect("company.customers")
```

> ❗ **Ne jamais supprimer via un simple lien `<a href>`** (méthode GET). Un robot, un préchargement de navigateur ou un `<img>` malveillant pourrait déclencher la suppression. On supprime **toujours via un `<form method="post">`** (voir le bouton dans le tableau en 10.4).

### 10.7 Le cycle complet d'un formulaire

```
GET  /customers/new      → affiche le formulaire vide
       │  (l'utilisateur remplit et clique « Enregistrer »)
       ▼
POST /customers/new      → la vue lit request.POST, crée l'objet
       │
       ▼
redirect("company.customers")  → 302 vers /customers/
       │
       ▼
GET  /customers/         → la liste s'affiche, client ajouté ✅
```

### 10.8 Pièges fréquents (formulaires HTML)

| Erreur | Symptôme |
| ------------------------------------------- | ------------------------------------------ |
| `{% csrf_token %}` oublié | **403 Forbidden** au submit |
| `method="post"` oublié (reste en GET) | Données dans l'URL, vue ne les enregistre pas |
| `name="..."` absent sur un `<input>` | `request.POST.get(...)` renvoie `None` |
| `render` au lieu de `redirect` après POST | Doublons si l'utilisateur fait F5 |
| DELETE via lien `<a>` | Suppression accidentelle (GET non protégé) |
| Migration oubliée | `no such table: company_customer` |

> 🚀 **Et après ?** Tout ce code de `request.POST.get(...)` + validation manuelle est exactement ce que **`Django Forms` / `ModelForm`** automatisent (validation, ré-affichage des erreurs, sécurité). Les formulaires HTML bruts sont parfaits pour **comprendre**, mais en vrai projet on bascule vite sur `ModelForm`.

### 10.9 Messages flash (succès / erreur)

Un **message flash** est une notification **à usage unique** : affichée une fois après une action (création, suppression…), puis supprimée automatiquement. C'est le complément naturel du **Post/Redirect/Get** : comme on redirige après un POST, on a besoin d'un moyen de « transporter » le message jusqu'à la page suivante. Django gère ça avec le framework intégré **`django.contrib.messages`**.

#### 10.9.1 Vérifier la configuration (déjà en place par défaut)

Un projet généré par `startproject` a déjà les 3 éléments nécessaires dans `config/settings.py` :

```python
INSTALLED_APPS = [
    ...
    'django.contrib.messages',                       # 1. l'app
]

MIDDLEWARE = [
    ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',   # 2. le middleware
]

TEMPLATES = [{
    ...
    'OPTIONS': {
        'context_processors': [
            ...
            'django.contrib.messages.context_processors.messages',  # 3. rend `messages` dispo dans les templates
        ],
    },
}]
```

#### 10.9.2 Côté vue : émettre un message

On importe `messages` et on appelle le niveau voulu, **juste avant le `redirect`** :

```python
from django.contrib import messages

def customers_create(request):
    if request.method == "POST":
        Customer.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
        )
        messages.success(request, "Client créé avec succès ✅")
        return redirect("company.customers")

    return render(request, "company/customer_add.html")
```

Les 5 niveaux disponibles :

```python
messages.debug(request, "...")
messages.info(request, "Information.")
messages.success(request, "Opération réussie.")
messages.warning(request, "Attention…")
messages.error(request, "Une erreur est survenue.")
```

Exemple sur DELETE :

```python
def customers_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == "POST":
        customer.delete()
        messages.success(request, "Client supprimé.")
    return redirect("company.customers")
```

#### 10.9.3 Côté template : afficher les messages

À placer **une seule fois dans `base.html`** → toutes les pages en profitent automatiquement.

`templates/base.html` :

```html
<main>
    {% if messages %}
    <ul class="messages">
        {% for message in messages %}
        <li class="{{ message.tags }}">{{ message }}</li>
        {% endfor %}
    </ul>
    {% endif %}

    {% block content %}{% endblock %}
</main>
```

- `{{ message }}` → le texte du message.
- `{{ message.tags }}` → la classe CSS du niveau (`success`, `error`, `warning`…), pour le style.

> 🧠 **Usage unique** : une fois lus par le template, les messages sont **supprimés**. Au rafraîchissement (F5) suivant, ils ne réapparaissent pas.

#### 10.9.4 Style (optionnel)

```html
<style>
    .messages { list-style: none; padding: 0; }
    .messages li { padding: 10px; margin: 5px 0; border-radius: 4px; }
    .messages li.success { background: #d4edda; color: #155724; }
    .messages li.error   { background: #f8d7da; color: #721c24; }
    .messages li.warning { background: #fff3cd; color: #856404; }
    .messages li.info    { background: #d1ecf1; color: #0c5460; }
</style>
```

> ⚠️ Le niveau `error` a pour tag CSS `error`. Pour le mapper sur la classe Bootstrap `danger`, ajoute dans `settings.py` :
> ```python
> from django.contrib.messages import constants as messages
> MESSAGE_TAGS = {messages.ERROR: 'danger'}
> ```

#### 10.9.5 Le flux complet

```
POST /customers/new → vue crée le client + messages.success(...)
        │
        ▼
redirect("company.customers")   (302)
        │
        ▼
GET /customers/ → base.html lit {% for message in messages %} → affiche ✅
        │  (les messages sont consommés/supprimés)
        ▼
F5 → plus aucun message (usage unique)
```

> ❗ Piège classique : si rien ne s'affiche, c'est presque toujours le **context_processor `messages` manquant** (10.9.1) ou le **bloc d'affichage absent de `base.html`** (10.9.3).

### 10.10 Validation des données

> ⚠️ **Le piège qui surprend tout le monde.** On remplit un formulaire en laissant `address` vide, et… c'est enregistré en base. Alors qu'on n'a pas mis `null=True` ! Pourquoi ?

#### 10.10.1 `null` ≠ « champ obligatoire »

`null` concerne **uniquement la base de données** : la colonne accepte-t-elle la valeur SQL `NULL` ? Or un champ texte vide dans un formulaire n'envoie **pas** `NULL`, il envoie une **chaîne vide `""`**. Et `""` est une valeur parfaitement valide pour une colonne `NOT NULL` → aucune contrainte violée.

| Attribut | Concerne | Question posée |
| -------- | -------------------- | ------------------------------------ |
| `null` | la **base de données** | la colonne accepte-t-elle `NULL` ? |
| `blank` | la **validation** (formulaires) | le champ peut-il être laissé **vide** ? |

> 🧠 **Convention Django** : pour les champs texte (`CharField`, `TextField`, `EmailField`), on **évite `null=True`** et on utilise `blank`. Sinon « vide » aurait deux représentations (`NULL` **et** `""`) → bugs. Doc officielle : *« Avoid using null on string-based fields. »*

Donc pour rendre `address` obligatoire, ce n'est pas `null` qu'il faut régler : `blank=False` est **déjà** le défaut. Le vrai problème est ailleurs ↓

#### 10.10.2 `.objects.create()` et `.save()` ne valident RIEN

C'est **ça**, le responsable. La validation des modèles (`blank`, `max_length`, format `EmailField`…) n'est déclenchée **que** par la méthode **`full_clean()`**. Et `full_clean()` est appelé **automatiquement** par :

- les **`ModelForm`**
- l'**admin Django**

…mais **JAMAIS** par `Customer.objects.create(...)` ni par `instance.save()`. Ces méthodes écrivent directement en base sans vérifier autre chose que les contraintes SQL (`NOT NULL`, `UNIQUE`, longueur max selon le SGBD). Voilà pourquoi ton `""` est passé.

#### 10.10.3 Les solutions (de la plus faible à la plus robuste)

**Niveau 0 — `required` HTML** (confort, pas sécurité) :

```html
<input type="text" name="address" required>
```

Bloque le submit dans le navigateur, mais **contournable** (curl, JS désactivé…). Nécessaire mais **jamais suffisant**.

**Niveau 1 — Validation manuelle dans la vue :**

```python
from django.contrib import messages

def customers_create(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        address    = request.POST.get("address", "").strip()
        # ...

        if not first_name or not address:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, "company/customer_add.html")

        Customer.objects.create(first_name=first_name, address=address, ...)
        return redirect("company.customers")

    return render(request, "company/customer_add.html")
```

> `.strip()` est important : sinon `"   "` (que des espaces) passerait.

**Niveau 2 — Forcer la validation du modèle avec `full_clean()` :**

```python
from django.core.exceptions import ValidationError

def customers_create(request):
    if request.method == "POST":
        customer = Customer(
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
            email=request.POST.get("email", ""),
            phone=request.POST.get("phone", ""),
            address=request.POST.get("address", ""),
        )
        try:
            customer.full_clean()   # ← déclenche blank, max_length, EmailField...
            customer.save()
            return redirect("company.customers")
        except ValidationError as e:
            messages.error(request, "; ".join(
                f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()))
            return render(request, "company/customer_add.html")

    return render(request, "company/customer_add.html")
```

Ici `address=""` **est refusé** (`blank=False`), et `email="abc"` aussi (format invalide).

**Niveau 3 — `ModelForm` (LA vraie solution Django) ✅**

`company/forms.py` :

```python
from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone", "address"]
```

`views.py` :

```python
from .forms import CustomerForm

def customers_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():          # ← lance toute la validation du modèle
            form.save()
            messages.success(request, "Client créé ✅")
            return redirect("company.customers")
    else:
        form = CustomerForm()
    return render(request, "company/customer_add.html", {"form": form})
```

`is_valid()` appelle la validation et **ré-affiche le formulaire avec les erreurs** si quelque chose cloche. C'est ce qu'on utilise en vrai projet.

| Méthode d'enregistrement | Validation déclenchée ? |
| ------------------------------------ | ----------------------- |
| `Model.objects.create(...)` | ❌ non |
| `instance.save()` | ❌ non |
| `instance.full_clean()` puis `save()` | ✅ oui (manuel) |
| `ModelForm.is_valid()` puis `save()` | ✅ oui (auto) |
| Admin Django | ✅ oui (auto) |

#### 10.10.4 Styliser le formulaire et les messages d'erreur

`{{ form.as_p }}` rend vite un formulaire mais génère un HTML **figé** (chaque champ dans un `<p>`) difficile à styliser finement. Voici les options, de la plus simple à la plus contrôlée.

**Option A — Garder `as_p` / `as_div` et styliser via CSS**

Depuis Django 5, `{{ form.as_div }}` est le rendu recommandé (plus souple que `as_p`). Django ajoute déjà des classes utiles sur les champs en erreur :

```html
<form method="post" novalidate>
    {% csrf_token %}
    {{ form.as_div }}
    <button type="submit">Enregistrer</button>
</form>
```

```css
/* Les erreurs sont dans une <ul class="errorlist"> */
.errorlist { list-style: none; padding: 0; margin: 4px 0; color: #721c24; }
/* Django marque les champs requis et invalides */
input:focus, textarea:focus { outline: 2px solid #0d6efd; }
```

> `novalidate` sur le `<form>` désactive la validation HTML5 du navigateur pour **voir** les messages de Django (utile en apprentissage).

**Option B — Boucler sur les champs (contrôle moyen)**

On parcourt `form` et on place soi-même les balises et classes CSS :

```html
<form method="post" novalidate>
    {% csrf_token %}

    {% for field in form %}
    <div class="form-group">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}                              {# le widget <input>/<textarea> #}

        {% if field.help_text %}
            <small class="help">{{ field.help_text }}</small>
        {% endif %}

        {% for error in field.errors %}
            <p class="field-error">{{ error }}</p>   {# message d'erreur du champ #}
        {% endfor %}
    </div>
    {% endfor %}

    {# erreurs non liées à un champ précis (ex: clean() global) #}
    {% for error in form.non_field_errors %}
        <p class="field-error">{{ error }}</p>
    {% endfor %}

    <button type="submit">Enregistrer</button>
</form>
```

```css
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: bold; }
.field-error { color: #721c24; font-size: .85rem; margin: 4px 0 0; }
/* cibler un champ en erreur : Django ne met pas de classe par défaut → voir Option C */
```

Variables utiles par champ : `{{ field }}` (le widget), `{{ field.label }}`, `{{ field.errors }}`, `{{ field.help_text }}`, `{{ field.id_for_label }}`, `{{ field.value }}`.

**Option C — Ajouter des classes CSS aux `<input>` eux-mêmes**

`{{ field }}` ne porte aucune classe par défaut (impossible de cibler `.form-control` Bootstrap). On les ajoute dans le `forms.py` via les **widgets** :

```python
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone", "address"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
            "email":      forms.EmailInput(attrs={"class": "form-control"}),
            "address":    forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {"first_name": "Prénom", "address": "Adresse"}
        error_messages = {
            "first_name": {"required": "Le prénom est obligatoire."},
        }
```

> Pour appliquer une classe à **tous** les champs d'un coup, on le fait dans `__init__` :
> ```python
> def __init__(self, *args, **kwargs):
>     super().__init__(*args, **kwargs)
>     for field in self.fields.values():
>         field.widget.attrs["class"] = "form-control"
> ```

**Mettre en valeur un champ en erreur** (Option B + C) : on teste `field.errors` pour ajouter une classe sur le conteneur :

```html
<div class="form-group {% if field.errors %}has-error{% endif %}">
```

```css
.has-error input, .has-error textarea { border: 1px solid #dc3545; }
```

> 💡 Pour ne pas réécrire ce bloc dans chaque template, on le met une fois dans un partiel (`templates/partials/_field.html`) inclus avec `{% include %}`, ou on utilise une lib comme **django-crispy-forms** / **django-widget-tweaks** qui ajoutent des classes en une ligne dans le template.

#### 10.10.5 En résumé

- Ton modèle est correct : `null=False`/`blank=False` sont **déjà** les défauts.
- Le vrai coupable : **`create()`/`save()` ne valident rien**. Seuls `full_clean()`, les `ModelForm` et l'admin valident.
- Pour un vrai projet → **`ModelForm`** + stylisation via **widgets** (`attrs={"class": ...}`) et boucle `{% for field in form %}` pour placer les erreurs.

### 10.11 Exemple complet : CREATE avec `ModelForm`

Mise en pratique de tout ce qui précède sur le modèle `Customer`. On compare d'abord avec la **version manuelle** pour bien voir ce que `ModelForm` supprime.

#### 10.11.1 Le problème de la validation manuelle

Une vue « à la main » doit gérer elle-même chaque cas — et tombe vite dans deux pièges :

```python
# ❌ Version manuelle bancale
if not data.first_name:
    flash.error(request, "first_name ne peut pas être vide")
# ... 5 if ...
data.save()                       # ⚠️ s'exécute MÊME en cas d'erreur !
```

- **Piège 1** : `flash.error("...")` sans `request` → ne marche pas (signature : `messages.error(request, message)`).
- **Piège 2** : `save()` s'exécute toujours, car rien n'arrête le flux.

Si on tient à la version manuelle, il faut un **drapeau** pour ne sauvegarder que si tout est bon :

```python
errors = []
if not first_name: errors.append("Le prénom ne peut pas être vide")
if not address:    errors.append("L'adresse ne peut pas être vide")
# ...
if errors:                                  # ← "la vérification" = liste non vide ?
    for e in errors:
        flash.error(request, e)
    return render(request, "company/customer_add.html")   # on NE sauvegarde PAS
Customer.objects.create(first_name=first_name, address=address, ...)
```

> 🧠 On **ne relit jamais** les messages flash pour savoir s'il y a eu une erreur : les itérer les marque comme « lus » et ils ne s'afficheraient plus. On suit l'état avec une **liste** ou un **booléen**.
>
> ⚠️ Autre piège : si un champ n'est pas envoyé, `request.POST.get('x')` vaut `None`, et `None.strip()` **plante**. D'où le `(request.POST.get('x') or "")`.

Tout ce code est exactement ce que `ModelForm` automatise ↓

#### 10.11.2 `company/forms.py`

```python
from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone", "address"]

        error_messages = {
            "first_name": {"required": "Le prénom ne peut pas être vide"},
            "last_name":  {"required": "Le nom ne peut pas être vide"},
            "email":      {"required": "L'email ne peut pas être vide"},
            "phone":      {"required": "Le téléphone ne peut pas être vide"},
            "address":    {"required": "L'adresse ne peut pas être vide"},
        }

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom"}),
            "email":      forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}),
            "phone":      forms.TextInput(attrs={"class": "form-control", "placeholder": "Téléphone"}),
            "address":    forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Adresse"}),
        }

    # normalisation : remplace les .strip().title() / .lower() de la vue manuelle
    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip().title()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip().title()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def clean_address(self):
        return self.cleaned_data["address"].strip().lower()
```

> Les méthodes `clean_<champ>` sont appelées automatiquement par `is_valid()`. La vérification « vide » ayant déjà eu lieu, plus besoin de gérer le `None`.

#### 10.11.3 `company/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib import messages as flash
from .forms import CustomerForm


def customers_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():                 # ← fait TOUTES les vérifications d'un coup
            form.save()                     # ← crée le Customer (données déjà nettoyées)
            flash.success(request, "Nouveau client créé ✅")
            return redirect("company.customers")
        # sinon : on retombe en bas, `form` contient les erreurs + les valeurs saisies
    else:
        form = CustomerForm()               # GET : formulaire vide

    return render(request, "company/customer_add.html", {"form": form})
```

> 🧠 En cas d'échec, on **ne redirige pas** : on re-rend le **même `form`**, qui garde les **valeurs déjà saisies** (l'utilisateur ne perd rien) et porte les **erreurs** par champ.

#### 10.11.4 `company/templates/company/customer_add.html`

```html
{% extends "base.html" %}
{% block title %}Nouveau client{% endblock %}

{% block content %}
<h1>Ajouter un client</h1>

<form method="post" novalidate>
    {% csrf_token %}

    {% for field in form %}
    <div class="form-group {% if field.errors %}has-error{% endif %}">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}                              {# widget avec sa classe form-control #}

        {% for error in field.errors %}
            <p class="field-error">{{ error }}</p>
        {% endfor %}
    </div>
    {% endfor %}

    <button type="submit">Enregistrer</button>
</form>
{% endblock %}
```

```css
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: bold; }
.form-control { width: 100%; padding: 8px; }
.field-error { color: #721c24; font-size: .85rem; margin: 4px 0 0; }
.has-error .form-control { border: 1px solid #dc3545; }
```

#### 10.11.5 Réutiliser le même form pour l'UPDATE

Le **même `CustomerForm`** sert à l'édition : on lui passe l'`instance` à modifier.

```python
from django.shortcuts import get_object_or_404

def customers_update(request, id):
    customer = get_object_or_404(Customer, id=id)
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        form.save()
        flash.success(request, "Client mis à jour ✅")
        return redirect("company.customers")
    return render(request, "company/customer_edit.html", {"form": form})
```

> `request.POST or None` : en GET, `request.POST` est vide → le form est non-lié (vide mais pré-rempli par `instance`) ; en POST, il est lié aux données envoyées. Astuce pour gérer GET et POST en une ligne.

#### 10.11.6 Ce que `ModelForm` t'apporte

| Version manuelle | Avec `ModelForm` |
| ------------------------------------------ | --------------------------------- |
| 5 `if not ... : flash.error(...)` | `form.is_valid()` |
| Gérer le `None` / `.strip()` à la main | `clean_<champ>` |
| Drapeau `errors` + `return` avant `save()` | géré automatiquement |
| Valeurs perdues si erreur | ré-affichées automatiquement |
| `email` non validé | format email vérifié |
| Erreurs en bloc (messages flash) | erreur **sous chaque champ** |

### 10.12 Garder les données saisies en cas d'erreur

Quand la validation échoue, on veut **réafficher le formulaire avec ce que l'utilisateur avait déjà tapé** (sinon il doit tout retaper). La règle d'or, dans les deux approches :

> 🧠 **En cas d'erreur → on `render` (on reste sur la page avec les données), on ne `redirect` PAS.** La redirection (qui repart sur une requête GET = formulaire vide) est réservée au **succès** (pattern Post/Redirect/Get).

#### 10.12.1 Avec `ModelForm` : automatique ✅

Rien de spécial à faire. Il suffit de **re-rendre le `form` lié aux données POST** au lieu de rediriger :

```python
def customers_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)   # ← form LIÉ aux données envoyées
        if form.is_valid():
            form.save()
            return redirect("company.customers")
        # ❌ PAS de redirect ici → on retombe sur le render du bas
    else:
        form = CustomerForm()
    return render(request, "company/customer_add.html", {"form": form})
```

`{{ field }}` réaffiche `field.value()` (la valeur saisie) → tout est conservé tout seul.

> ⚠️ **Le piège qui efface tout** : faire `return redirect(...)` après une erreur. Redirection = nouvelle requête GET = formulaire vide.

#### 10.12.2 Avec un formulaire HTML manuel

Il faut renvoyer soi-même les données au template et remplir les attributs `value`.

**Côté vue** — repasser `request.POST` :

```python
if errors:
    for e in errors:
        flash.error(request, e)
    return render(request, "company/customer_add.html", {"data": request.POST})
```

**Côté template** — remplir `value` (et le contenu pour un `textarea`) :

```html
<input type="text"  name="first_name" value="{{ data.first_name }}">
<input type="email" name="email"      value="{{ data.email }}">

<!-- textarea : la valeur va ENTRE les balises, pas dans value -->
<textarea name="address">{{ data.address }}</textarea>
```

> 💡 `{{ data.first_name }}` ne plante pas si `data` n'existe pas (GET initial) : Django affiche une chaîne vide. Le même template marche donc pour l'affichage initial **et** le ré-affichage après erreur.

#### 10.12.3 Récap

| Approche | Garder les données en cas d'erreur |
| ---------------- | --------------------------------------------------------- |
| `ModelForm` | **Automatique** — re-rendre le `form` lié (ne pas rediriger) |
| Formulaire manuel | Passer `{"data": request.POST}` au template + `value="{{ data.champ }}"` |

### 10.13 Repeupler chaque type de champ (formulaire manuel)

`value="..."` marche pour les `<input>` texte, mais **chaque type de champ se repeuple différemment**. On suppose que la vue a renvoyé `{"data": request.POST}`.

> ℹ️ Rappel : `ModelForm` gère **tout** ce qui suit automatiquement. Ces techniques ne concernent que l'approche **manuelle**.

#### 10.13.1 Texte / email / nombre → `value`

```html
<input type="text"   name="first_name" value="{{ data.first_name }}">
<input type="email"  name="email"      value="{{ data.email }}">
<input type="number" name="age"        value="{{ data.age }}">
```

#### 10.13.2 Textarea → entre les balises

```html
<textarea name="address">{{ data.address }}</textarea>
```

> ⚠️ Aucun espace ni saut de ligne entre `>` et `{{` : tout ce qui est entre les balises devient le contenu affiché.

#### 10.13.3 Select → `selected` sur la bonne option

```html
<select name="country">
    <option value="">-- Choisir --</option>
    <option value="fr" {% if data.country == "fr" %}selected{% endif %}>France</option>
    <option value="be" {% if data.country == "be" %}selected{% endif %}>Belgique</option>
    <option value="ca" {% if data.country == "ca" %}selected{% endif %}>Canada</option>
</select>
```

#### 10.13.4 Radio → `checked` sur le bon bouton

```html
<label><input type="radio" name="gender" value="M" {% if data.gender == "M" %}checked{% endif %}> Homme</label>
<label><input type="radio" name="gender" value="F" {% if data.gender == "F" %}checked{% endif %}> Femme</label>
```

#### 10.13.5 Checkbox unique (oui/non)

Une checkbox **non cochée n'est pas envoyée** dans `request.POST` → il suffit de tester sa présence :

```html
<label>
    <input type="checkbox" name="newsletter" value="yes"
           {% if data.newsletter %}checked{% endif %}>
    S'abonner à la newsletter
</label>
```

#### 10.13.6 Checkbox multiples (liste de valeurs)

Plusieurs cases partagent le même `name` → côté Python il faut **`request.POST.getlist('hobbies')`** (`.get()` ne renverrait que la dernière). Comme `getlist` **n'est pas appelable dans un template**, on prépare la liste **dans la vue** :

```python
# vue
if errors:
    return render(request, "company/form.html", {
        "data": request.POST,
        "hobbies_selected": request.POST.getlist("hobbies"),   # ← liste préparée
    })
```

```html
<!-- template : test d'appartenance avec le filtre "in" -->
<label><input type="checkbox" name="hobbies" value="sport"
       {% if "sport" in hobbies_selected %}checked{% endif %}> Sport</label>
<label><input type="checkbox" name="hobbies" value="music"
       {% if "music" in hobbies_selected %}checked{% endif %}> Musique</label>
<label><input type="checkbox" name="hobbies" value="code"
       {% if "code" in hobbies_selected %}checked{% endif %}> Code</label>
```

#### 10.13.7 Date / time / datetime-local → `value` (format strict)

```html
<input type="date"           name="birthdate" value="{{ data.birthdate }}">
<input type="time"           name="start"     value="{{ data.start }}">
<input type="datetime-local" name="meeting"   value="{{ data.meeting }}">
```

> ⚠️ `<input type="date">` n'accepte que le format **`YYYY-MM-DD`** dans `value`. La valeur **repostée** est déjà au bon format. Mais si tu pré-remplis depuis un objet Python `date`, formate-le : `{{ obj.birthdate|date:"Y-m-d" }}` (et `H:i` pour l'heure).

#### 10.13.8 Tableau récap

| Type de champ | Comment repeupler |
| ---------------------- | ------------------------------------------------------------ |
| text / email / number | `value="{{ data.champ }}"` |
| textarea | `<textarea>{{ data.champ }}</textarea>` (entre les balises) |
| select | `{% if data.champ == "val" %}selected{% endif %}` sur chaque option |
| radio | `{% if data.champ == "val" %}checked{% endif %}` |
| checkbox unique | `{% if data.champ %}checked{% endif %}` |
| checkbox multiples | vue : `getlist(...)` → template : `{% if "val" in liste %}checked{% endif %}` |
| date / time | `value="{{ data.champ }}"` (format `Y-m-d` / `H:i`) |

> 🧠 Tout ce travail (comparer chaque valeur, gérer `getlist`, les formats de date…) est **exactement** ce que `ModelForm` fait tout seul. Dès qu'un formulaire dépasse 2-3 `<input>` texte, le `ModelForm` devient vraiment rentable.

---

## 11. Upload de fichiers et d'images

Gérer un fichier (photo de profil, document…) demande **3 choses spécifiques** qu'un champ texte n'a pas : un champ `FileField`/`ImageField`, un formulaire en `multipart`, et un endroit où stocker les fichiers.

### 11.1 Configuration : `MEDIA_ROOT` et `MEDIA_URL`

Les fichiers uploadés (les **médias**) sont distincts des fichiers `static` (CSS/JS du site). Dans `config/settings.py` :

```python
import os

MEDIA_URL = "/media/"                       # préfixe URL pour servir les fichiers
MEDIA_ROOT = BASE_DIR / "media"             # dossier physique où ils sont stockés
```

En **développement**, pour que Django serve ces fichiers, on ajoute dans `config/urls.py` :

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... tes routes ...
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

> ⚠️ Ce `static(...)` ne fonctionne **qu'en `DEBUG=True`**. En production, c'est le serveur web (Nginx) ou un service externe (11.6) qui sert les médias.

### 11.2 Le modèle : `FileField` / `ImageField`

```python
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    photo    = models.ImageField(upload_to="customers/%Y/%m/", blank=True, null=True)
    document = models.FileField(upload_to="docs/", blank=True, null=True)
```

- `upload_to` : sous-dossier dans `MEDIA_ROOT`. `%Y/%m/` crée automatiquement `customers/2026/06/` (range par date → évite des milliers de fichiers dans un seul dossier).
- `ImageField` valide que le fichier est **bien une image** (nécessite la lib **Pillow** : `pip install Pillow`).

> Après ajout du champ : `makemigrations` + `migrate`.

### 11.3 Le formulaire HTML : `enctype="multipart/form-data"`

**Sans cet attribut, le fichier n'est PAS envoyé** (Django ne reçoit que le nom). C'est l'erreur n°1.

```html
<form method="post" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="photo" accept="image/*">
    <button type="submit">Envoyer</button>
</form>
```

> `accept="image/*"` filtre le sélecteur côté navigateur (confort, pas sécurité).

### 11.4 La vue : `request.FILES`

Les fichiers n'arrivent **pas** dans `request.POST` mais dans **`request.FILES`** :

```python
def customers_create(request):
    if request.method == "POST":
        customer = Customer(first_name=request.POST.get("first_name"))
        if "photo" in request.FILES:
            customer.photo = request.FILES["photo"]   # ← le fichier
        customer.save()                                # Django écrit le fichier sur disque
        return redirect("company.customers")
    return render(request, "company/customer_add.html")
```

Avec un **`ModelForm`** (recommandé), il faut passer `request.FILES` en 2ᵉ argument :

```python
form = CustomerForm(request.POST, request.FILES)   # ⚠️ ne pas oublier request.FILES
if form.is_valid():
    form.save()
```

### 11.5 Afficher et limiter (taille / extension)

**Afficher** le fichier dans un template via `.url` :

```html
{% if customer.photo %}
    <img src="{{ customer.photo.url }}" alt="photo" width="120">
{% endif %}
<a href="{{ customer.document.url }}">Télécharger</a>
```

**Limiter la taille et l'extension** côté serveur (le `accept` HTML est contournable). Un validateur sur le modèle :

```python
from django.core.exceptions import ValidationError

def validate_size(file):
    limit_mo = 2
    if file.size > limit_mo * 1024 * 1024:
        raise ValidationError(f"Fichier trop lourd (max {limit_mo} Mo).")

class Customer(models.Model):
    photo = models.ImageField(upload_to="customers/", validators=[validate_size])
```

Pour restreindre les extensions, Django fournit `FileExtensionValidator` :

```python
from django.core.validators import FileExtensionValidator

document = models.FileField(
    upload_to="docs/",
    validators=[FileExtensionValidator(["pdf", "docx"])],
)
```

> ⚠️ Rappel : les validators ne se déclenchent qu'avec `full_clean()` / `ModelForm` (voir 10.10.2). Avec `.save()` direct, valide la taille toi-même dans la vue.

### 11.6 Réduire / compresser les images à l'upload

Stocker une photo de 5 Mo prise au téléphone est inutile : on la **redimensionne/compresse** avant sauvegarde. Avec **Pillow**, en surchargeant `save()` du modèle :

```python
from PIL import Image
from django.db import models

class Customer(models.Model):
    photo = models.ImageField(upload_to="customers/", blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)            # 1. on sauve d'abord (le fichier existe sur disque)
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 800 or img.width > 800:
                img.thumbnail((800, 800))        # 2. réduit en gardant les proportions
                img.save(self.photo.path, quality=70, optimize=True)   # 3. recompresse
```

- `thumbnail((800, 800))` : réduit pour tenir dans 800×800 **sans déformer**.
- `quality=70` : qualité JPEG (70 = bon compromis poids/qualité).
- `optimize=True` : passe d'optimisation supplémentaire.

> 💡 Pour automatiser sans coder, la lib **`django-imagekit`** ou **`django-resized`** (`pip install django-resized`) fait ça en déclaratif :
> ```python
> from django_resized import ResizedImageField
> photo = ResizedImageField(size=[800, 800], quality=70, upload_to="customers/")
> ```

### 11.7 Stockage externe (services gratuits) et `django-storages`

En production, on évite de stocker les médias sur le serveur applicatif (perdus à chaque redéploiement, pas scalable). On délègue à un **stockage objet**. La lib standard est **`django-storages`**, qui branche un backend distant **sans changer ton code** (`FileField` reste identique).

| Service | Offre gratuite | Backend `django-storages` |
| ----------------- | -------------------------------------- | ------------------------------ |
| **Cloudinary** | ~25 crédits/mois (images + transfo auto) | `cloudinary_storage` (lib dédiée) |
| **Supabase Storage** | 1 Go (compatible S3) | backend S3 |
| **Backblaze B2** | 10 Go gratuits (compatible S3) | backend S3 |
| **Cloudflare R2** | 10 Go/mois, **sans frais de sortie** | backend S3 |
| **AWS S3** | 5 Go pendant 12 mois | `storages.backends.s3` |

**Exemple avec un service compatible S3** (B2, R2, Supabase…) :

```bash
pip install django-storages boto3
```

```python
# settings.py
INSTALLED_APPS += ["storages"]

STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},      # médias → S3
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

AWS_ACCESS_KEY_ID     = os.environ["S3_KEY"]        # ← via variables d'environnement
AWS_SECRET_ACCESS_KEY = os.environ["S3_SECRET"]
AWS_STORAGE_BUCKET_NAME = "mon-bucket"
AWS_S3_ENDPOINT_URL   = "https://s3.eu-central-003.backblazeb2.com"   # propre au service
```

Ton code modèle/template **ne change pas** : `customer.photo.url` renvoie désormais l'URL du service distant.

**Cloudinary** (très simple pour les images, avec redimensionnement à la volée) utilise sa propre lib :

```bash
pip install cloudinary django-cloudinary-storage
```

```python
# settings.py
INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]
CLOUDINARY_STORAGE = {"CLOUDINARY_URL": os.environ["CLOUDINARY_URL"]}
STORAGES = {"default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}}
```

> 🔐 **Ne mets JAMAIS tes clés d'API en dur** dans `settings.py` (surtout si le code est sur GitHub). Utilise des **variables d'environnement** (ou un fichier `.env` avec `python-decouple` / `django-environ`), et ajoute `.env` au `.gitignore`.

### 11.8 Récap

| Étape | À faire |
| ----------------------- | ----------------------------------------------- |
| Config | `MEDIA_URL` + `MEDIA_ROOT` + `static(...)` en DEBUG |
| Modèle | `ImageField`/`FileField` + `upload_to` (+ Pillow) |
| Formulaire | `enctype="multipart/form-data"` (sinon rien n'arrive) |
| Vue | lire `request.FILES` (ou `ModelForm(request.POST, request.FILES)`) |
| Affichage | `{{ obj.photo.url }}` |
| Sécurité | valider **taille** et **extension** côté serveur |
| Compression | Pillow `thumbnail()` + `quality` (ou `django-resized`) |
| Production | `django-storages` + service externe (R2, B2, Cloudinary…) |

---

## 12. Fichiers statiques (`static`) vs médias (`media`)

C'est **la** confusion la plus fréquente dès qu'on parle de fichiers. Les deux servent des fichiers… mais pour des raisons opposées.

| | **Static** | **Media** |
| -------------- | ------------------------------------------ | ------------------------------------------ |
| Contenu | CSS, JS, logos, polices, icônes | Fichiers **uploadés par les utilisateurs** |
| Qui les crée | **toi**, le développeur | les utilisateurs (photos, docs…) |
| Versionnés Git | ✅ oui (font partie du code) | ❌ non (`.gitignore`) |
| Réglages | `STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT` | `MEDIA_URL`, `MEDIA_ROOT` |
| Balise template | `{% static '...' %}` | `{{ obj.fichier.url }}` |
| En production | `collectstatic` → servis par Nginx/CDN | servis par Nginx ou un service externe (11.7) |

> 🧠 Règle simple : **ça vient de ton dépôt → static ; ça vient d'un upload → media.**

### 12.1 Configuration des statics

```python
# config/settings.py
STATIC_URL = "static/"                       # préfixe URL
STATICFILES_DIRS = [BASE_DIR / "static"]     # où TU mets tes fichiers (en dev)
STATIC_ROOT = BASE_DIR / "staticfiles"       # où collectstatic les rassemble (prod)
```

> `STATICFILES_DIRS` = tes dossiers source. `STATIC_ROOT` = la **destination** de `collectstatic` (à ne jamais éditer à la main). Les deux doivent être **différents**.

Django cherche aussi automatiquement un dossier `static/` **dans chaque app** (comme pour les templates).

### 12.2 Structure et utilisation

```
crud1/
├── static/
│   ├── css/style.css
│   └── img/logo.png
```

Dans un template, on charge la balise puis on référence le chemin **relatif** :

```html
{% load static %}

<link rel="stylesheet" href="{% static 'css/style.css' %}">
<img src="{% static 'img/logo.png' %}" alt="logo">
```

> ❗ Ne **jamais** écrire le chemin en dur (`/static/css/style.css`). `{% static %}` gère le bon préfixe, le cache-busting et les CDN automatiquement.

### 12.3 En production : `collectstatic`

En dev (`DEBUG=True`), Django sert les statics tout seul. En production, on lance **une fois** :

```bash
python manage.py collectstatic
```

Cette commande **copie** tous les statics (les tiens + ceux de l'admin + ceux des libs) dans `STATIC_ROOT`, pour qu'un seul serveur (Nginx) ou un CDN les serve efficacement.

> 💡 Pour servir les statics en production **sans** Nginx, la lib **WhiteNoise** (`pip install whitenoise`) est l'option la plus simple : un middleware à ajouter et c'est réglé.

### 12.4 Récap mental

```
static/  →  TOI → {% static %}      → collectstatic → Nginx/CDN/WhiteNoise
media/   →  USER (upload) → .url     → Nginx ou service externe (R2, B2, Cloudinary)
```

---

## 13. Serveur : `wsgi.py` et `asgi.py`

Ces deux fichiers, générés automatiquement dans `config/`, sont le **point d'entrée** entre le serveur web et ton application Django. Tu les ouvres **rarement** : ils servent surtout en **production**.

### 13.1 C'est quoi une « interface » serveur ?

`runserver` (le serveur de dev) est pratique mais **pas fait pour la production** (lent, mono-thread, pas sécurisé). En prod, on utilise un vrai serveur d'application (Gunicorn, uWSGI, Uvicorn, Daphne...).

Le problème : comment ce serveur parle-t-il à Django ? Il faut un **contrat commun**. C'est le rôle de WSGI et ASGI : des **normes** Python qui définissent comment un serveur web transmet une requête à une application et récupère la réponse.

```
Navigateur → Serveur web (Nginx) → Serveur d'app (Gunicorn/Uvicorn) → [WSGI/ASGI] → Django
```

`wsgi.py` et `asgi.py` exposent simplement un objet `application` que le serveur d'app va appeler.

### 13.2 La différence fondamentale : synchrone vs asynchrone

| | **WSGI** (`wsgi.py`) | **ASGI** (`asgi.py`) |
| ----------------- | ------------------------------------------ | ------------------------------------------------------ |
| Sigle | **W**eb **S**erver **G**ateway **I**nterface | **A**synchronous **S**erver **G**ateway **I**nterface |
| Modèle | **Synchrone** (1 requête = 1 worker bloqué jusqu'à la réponse) | **Asynchrone** (un worker gère plusieurs requêtes en parallèle) |
| Apparu en | 2003 (la norme historique) | ~2018 (la norme moderne, **surensemble** de WSGI) |
| Gère | HTTP classique uniquement | HTTP **+ WebSockets, HTTP/2, long-polling, SSE** |
| Serveurs typiques | Gunicorn, uWSGI, mod_wsgi | Uvicorn, Daphne, Hypercorn (ou Gunicorn + worker Uvicorn) |
| `async def views` | Django les exécute, mais dans un pool de threads (pas de vrai gain) | Vrai support natif de l'asynchrone |

> 🧠 ASGI est **rétrocompatible** : il sait tout faire ce que fait WSGI, **plus** le temps réel. WSGI ne sait pas gérer les WebSockets.

### 13.3 Lequel choisir ?

**Utilise WSGI (le défaut) si :**

- Ton site est un CRUD classique : pages, formulaires, API REST.
- Pas de temps réel. → **C'est 90 % des projets.** Reste sur WSGI, c'est plus simple et éprouvé.

**Passe à ASGI si :**

- Tu as besoin de **WebSockets** (chat, notifications live, tableau de bord temps réel) — souvent via **Django Channels**.
- Tu fais beaucoup d'**appels réseau lents** (API externes) que tu veux paralléliser avec des `async def` views.
- Tu veux du **streaming** (SSE, longues réponses).

> 💡 Dans le doute : **WSGI**. Tu pourras toujours migrer vers ASGI plus tard (Django génère déjà les deux fichiers).

### 13.4 Contenu des fichiers

`config/wsgi.py` (généré automatiquement) :

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
```

`config/asgi.py` (généré automatiquement) :

```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
```

> La variable s'appelle **`application`** dans les deux cas : c'est le nom que les serveurs vont chercher par convention.

### 13.5 Comment démarrer le projet avec l'un ou l'autre

#### En développement (les deux confondus)

```bash
python manage.py runserver
```

`runserver` utilise **WSGI** par défaut. Inutile de te soucier de wsgi/asgi à ce stade.

#### En production — version WSGI (Gunicorn)

```bash
pip install gunicorn

# Syntaxe : gunicorn <module_python>:<objet_application>
gunicorn config.wsgi:application
# avec options courantes :
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

`config.wsgi` = le fichier `config/wsgi.py` ; `application` = l'objet dedans.

#### En production — version ASGI (Uvicorn)

```bash
pip install uvicorn

uvicorn config.asgi:application --host 0.0.0.0 --port 8000
```

Variante recommandée en prod : **Gunicorn qui pilote des workers Uvicorn** (robustesse de Gunicorn + asynchrone d'Uvicorn) :

```bash
pip install gunicorn uvicorn
gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

> Sur Windows, Gunicorn ne fonctionne pas : utilise **Uvicorn** ou **Waitress** (WSGI) directement.

### 13.6 Mémo

| Question | Réponse rapide |
| ----------------------------------- | ------------------------------------- |
| Quel fichier en prod par défaut ? | `wsgi.py` |
| Besoin de WebSockets / temps réel ? | `asgi.py` |
| Commande de dev ? | `python manage.py runserver` (WSGI) |
| Lancer en WSGI ? | `gunicorn config.wsgi:application` |
| Lancer en ASGI ? | `uvicorn config.asgi:application` |

---

## 14. Récapitulatif du flux complet

Du clic de l'utilisateur jusqu'à la page affichée :

```
1. Navigateur  →  http://127.0.0.1:8000/company/
                          │
2. config/urls.py  →  trouve "company/", délègue à company.urls
                          │
3. company/urls.py →  "" correspond à home_view
                          │
4. company/views.py → home_view(request) s'exécute
                          │            renvoie render(request, "company/index.html", contexte)
                          │
5. Template index.html → {% extends "base.html" %}, remplit les blocks
                          │
6. HTML final  →  renvoyé au navigateur ✅
```

---

## 15. Checklist mémo

Pour ajouter une **nouvelle app** au projet :

- [ ] `python manage.py startapp monapp`
- [ ] Ajouter `'monapp'` dans `INSTALLED_APPS` (settings.py)
- [ ] Créer une vue dans `monapp/views.py` (1er arg = `request` !)
- [ ] Créer `monapp/urls.py` avec une variable `urlpatterns`
- [ ] Brancher l'app dans `config/urls.py` via `include("monapp.urls")`
- [ ] Créer le template `monapp/templates/monapp/page.html`
- [ ] Le faire hériter : `{% extends "base.html" %}`
- [ ] Tester : `python manage.py runserver` → ouvrir l'URL

### Pièges les plus fréquents

| Erreur                                              | Symptôme                             |
| --------------------------------------------------- | ------------------------------------- |
| `urlspattern` au lieu de `urlpatterns`          | `ImproperlyConfigured`              |
| Chemin `"/"` au lieu de `""`                    | URL introuvable (404)                 |
| `render("x.html")` sans `request`               | `TypeError`                         |
| App absente de `INSTALLED_APPS`                   | Template / modèle introuvable        |
| Pas de sous-dossier `app/templates/app/`          | Mauvais template affiché (collision) |
| `DIRS` vide alors qu'on a un `base.html` global | `TemplateDoesNotExist: base.html`   |

---

## Pour aller plus loin

Ce guide couvre la base d'un projet Django. Pour les autres briques, voir les mémos dédiés :

- 📊 [MODELS.md](MODELS.md) — les **modèles** et l'**ORM** en profondeur (champs, relations, migrations, requêtes, pagination).
- 🛠️ [DJANGO-ADMIN.md](DJANGO-ADMIN.md) — le site d'**administration** (enregistrer des modèles, personnaliser, inlines, actions).
- 🔐 [AUTH.md](AUTH.md) — l'**authentification & autorisation** (login/logout, inscription, protéger les vues, permissions & groupes).
- 🗄️ [DATABASE-ENV.md](DATABASE-ENV.md) — les **bases de données** (SQLite, PostgreSQL, MySQL, Oracle, multi-BD) et les **variables d'environnement** (`.env`, secrets, config).
- 🧪 [TESTS.md](TESTS.md) — les **tests automatisés** (modèles, vues via le `Client`, formulaires, auth, couverture, pytest).
- 🧱 [CBV.md](CBV.md) — les **vues génériques** (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, mixins) : le CRUD en deux fois moins de code.
- 📡 [SIGNALS.md](SIGNALS.md) — les **signaux** (`post_save`, `pre_save`, `*_delete`, signaux d'auth, signaux custom) : réagir aux événements de façon découplée.
- 🚀 [DEPLOYMENT.md](DEPLOYMENT.md) — le **déploiement** (prod, statics, PostgreSQL, secrets, Gunicorn/WhiteNoise) et les **hébergeurs gratuits**.
- 📋 [LOGGING.md](LOGGING.md) — les **logs** (config `LOGGING`, écriture en fichier + rotation, formatage, usage) et l'**audit**.
