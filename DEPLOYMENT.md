# Documentation Django — Déploiement

> Mémo pour mettre un projet Django **en production** : préparer le projet, gérer statics/BD/secrets, et déployer sur un **hébergeur gratuit**.
> Basé sur **Django 6.0** et le projet `config` / `company`.
> Voir aussi : [DATABASE-ENV.md](DATABASE-ENV.md) (BD & variables d'env), [DJANGO.md](DJANGO.md) (statics §12, wsgi/asgi §13).

> ⚠️ Les **offres gratuites des hébergeurs changent souvent** (quotas, durée, carte requise). Vérifie toujours les conditions actuelles sur leur site avant de choisir.

---

## Sommaire

1. [Dev vs prod : ce qui change](#1-dev-vs-prod--ce-qui-change)
2. [La checklist de mise en production](#2-la-checklist-de-mise-en-production)
3. [Préparer `settings.py` pour la prod](#3-préparer-settingspy-pour-la-prod)
4. [Les fichiers nécessaires](#4-les-fichiers-nécessaires)
5. [Les fichiers statiques en prod (WhiteNoise)](#5-les-fichiers-statiques-en-prod-whitenoise)
6. [La base de données en prod](#6-la-base-de-données-en-prod)
7. [`manage.py check --deploy`](#7-managepy-check---deploy)
8. [Les hébergeurs gratuits (comparatif)](#8-les-hébergeurs-gratuits-comparatif)
9. [Déploiement pas-à-pas (Git-based, type Render)](#9-déploiement-pas-à-pas-git-based-type-render)
10. [Déploiement sur PythonAnywhere](#10-déploiement-sur-pythonanywhere)
11. [Erreurs de déploiement fréquentes](#11-erreurs-de-déploiement-fréquentes)
12. [Checklist mémo](#12-checklist-mémo)

---

## 1. Dev vs prod : ce qui change

Le serveur de dev (`runserver`) n'est **pas** fait pour la production. Passer en prod implique plusieurs changements :

| | Développement | Production |
| ------------- | ----------------------- | --------------------------------- |
| Serveur | `runserver` | Gunicorn/Uvicorn + (Nginx) — voir [DJANGO.md §13](DJANGO.md) |
| `DEBUG` | `True` | **`False`** |
| Base de données | SQLite | **PostgreSQL** (recommandé) |
| Statics | servis par Django | `collectstatic` + WhiteNoise/CDN |
| Secrets | en dur / `.env` local | **variables d'environnement** de l'hébergeur |
| `ALLOWED_HOSTS` | vide | ton **domaine** réel |
| HTTPS | non | oui (certificat) |

---

## 2. La checklist de mise en production

Les **non-négociables** avant de déployer :

1. `DEBUG = False`
2. `SECRET_KEY` lue depuis une **variable d'environnement** (jamais dans le code/Git)
3. `ALLOWED_HOSTS` renseigné (ton domaine)
4. Base de données **PostgreSQL** (pas SQLite, qui se perd à chaque redéploiement)
5. `collectstatic` + un moyen de servir les statics (WhiteNoise)
6. `requirements.txt` à jour + un serveur WSGI (Gunicorn)
7. Réglages de **sécurité HTTPS** activés

> 🧠 Le fil conducteur : **rien de sensible dans le code**, tout dans l'**environnement** (voir [DATABASE-ENV.md](DATABASE-ENV.md)).

---

## 3. Préparer `settings.py` pour la prod

Avec `django-environ` (voir [DATABASE-ENV.md §14](DATABASE-ENV.md)) :

```python
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")     # en local ; en prod, les vars viennent de l'hébergeur

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])     # ex: monsite.onrender.com

# Base de données (DATABASE_URL fournie par l'hébergeur)
DATABASES = {"default": env.db()}            # SQLite en local, Postgres en prod

# Statics
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"       # destination de collectstatic

# Origines de confiance pour le CSRF (domaine HTTPS)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Sécurité HTTPS — uniquement quand DEBUG=False
if not DEBUG:
    SECURE_SSL_REDIRECT = True               # force https
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")   # derrière un proxy
    SECURE_HSTS_SECONDS = 31536000
```

> ⚠️ `ALLOWED_HOSTS` vide + `DEBUG=False` → **erreur 400 (Bad Request)** sur chaque page. C'est l'oubli n°1.

---

## 4. Les fichiers nécessaires

À la racine du projet :

**`requirements.txt`** — les dépendances (l'hébergeur les installe) :

```bash
pip freeze > requirements.txt
```

```
Django>=6.0
gunicorn
psycopg[binary]
django-environ
whitenoise
```

**`Procfile`** (Render, Railway, Heroku…) — la commande de démarrage :

```
web: gunicorn config.wsgi:application
```

> `config.wsgi` = ton fichier `config/wsgi.py` (voir [DJANGO.md §13](DJANGO.md)).

**`.python-version`** ou `runtime.txt` (selon l'hébergeur) — la version de Python :

```
3.13
```

**`build.sh`** (script de build, ex. Render) — installe, collecte les statics, migre :

```bash
#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

**`.gitignore`** — ne **jamais** committer secrets/venv/base locale :

```gitignore
.env
*.sqlite3
__pycache__/
staticfiles/
venv/
```

---

## 5. Les fichiers statiques en prod (WhiteNoise)

En prod, Django ne sert **pas** les statics tout seul (voir [DJANGO.md §12](DJANGO.md)). La solution la plus simple **sans Nginx** : **WhiteNoise**, qui les sert directement depuis l'app.

```bash
pip install whitenoise
```

```python
# settings.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",     # ← juste après SecurityMiddleware
    # ... le reste ...
]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",  # compresse + cache
    },
}
```

Puis, au build : `python manage.py collectstatic --no-input`.

> 💡 Pour les **médias** uploadés par les utilisateurs (≠ statics), WhiteNoise ne suffit pas : utilise un stockage externe (S3, Cloudflare R2…) via `django-storages` — voir [DJANGO.md §11.7](DJANGO.md).

---

## 6. La base de données en prod

**N'utilise pas SQLite en prod** : le fichier est souvent **effacé à chaque redéploiement** (système de fichiers éphémère) → tu perds tes données. Utilise **PostgreSQL**, que la plupart des hébergeurs fournissent.

L'hébergeur te donne une **`DATABASE_URL`** (ex : `postgres://user:pass@host:5432/db`) à mettre en variable d'environnement ; `env.db()` la lit automatiquement (voir [DATABASE-ENV.md §14](DATABASE-ENV.md)).

Après déploiement, applique les migrations (souvent dans `build.sh`) :

```bash
python manage.py migrate
python manage.py createsuperuser   # une fois, via la console de l'hébergeur
```

---

## 7. `manage.py check --deploy`

Django a un **audit de sécurité** intégré pour la prod :

```bash
python manage.py check --deploy
```

Il signale les réglages risqués (`DEBUG=True`, cookies non sécurisés, `SECRET_KEY` faible, HSTS manquant…). À lancer **avant** de déployer et à corriger.

---

## 8. Les hébergeurs gratuits (comparatif)

> ⚠️ Offres **indicatives** (elles évoluent) — vérifie les conditions à jour.

| Hébergeur | Offre gratuite | Déploiement | Pour qui |
| ------------------ | -------------------------------------- | ------------------ | ------------------------------ |
| **PythonAnywhere** | 1 app web, sans carte, BD MySQL/SQLite | manuel (console + git) | **débutants** (le plus simple) |
| **Render** | web service gratuit (s'endort après inactivité), Postgres gratuit limité dans le temps | **Git** (auto à chaque push) | projets modernes, CI/CD |
| **Railway** | crédit d'essai puis paiement à l'usage | Git / CLI | prototypes (pas gratuit à long terme) |
| **Fly.io** | petite allocation gratuite (carte requise) | CLI (`flyctl`) | conteneurs, global |
| **Koyeb** | 1 service gratuit | Git / Docker | alternative à Render |
| **Vercel / Netlify** | gratuit mais **serverless** | Git | mal adapté à Django (plutôt front/JS) |
| **Heroku** | ❌ **plus de gratuit** depuis nov. 2022 | Git | (historique) |

> 👉 **Recommandation débutant** : **PythonAnywhere** (aucune carte, interface guidée, idéal pour un premier déploiement) ou **Render** (déploiement automatique par `git push`, plus « pro »). Garde en tête que les offres gratuites **mettent l'app en veille** après inactivité (premier accès lent) et que la **BD gratuite peut expirer**.

---

## 9. Déploiement pas-à-pas (Git-based, type Render)

Le modèle « tu pousses sur Git, l'hébergeur build et déploie ».

**1. Prépare le projet** (sections 3–5) : `requirements.txt`, `build.sh`, WhiteNoise, settings via env.

**2. Pousse le code sur GitHub** (sans `.env` !) :

```bash
git init
git add .
git commit -m "Prêt pour le déploiement"
git remote add origin https://github.com/toi/crud1.git
git push -u origin main
```

**3. Sur l'hébergeur**, crée un **Web Service** lié à ton dépôt GitHub, et configure :

- **Build command** : `./build.sh`
- **Start command** : `gunicorn config.wsgi:application`
- **Variables d'environnement** (dans l'interface, pas de `.env`) :
  ```
  SECRET_KEY=...(une nouvelle clé)
  DEBUG=False
  ALLOWED_HOSTS=monsite.onrender.com
  CSRF_TRUSTED_ORIGINS=https://monsite.onrender.com
  DATABASE_URL=...(fournie par la BD Postgres créée sur l'hébergeur)
  ```

**4. Crée une base PostgreSQL** sur l'hébergeur → copie son `DATABASE_URL` dans les variables.

**5. Déploie** : à chaque `git push`, l'hébergeur relance `build.sh` (install + collectstatic + migrate) puis Gunicorn.

**6. Crée le superuser** via la console web de l'hébergeur :

```bash
python manage.py createsuperuser
```

---

## 10. Déploiement sur PythonAnywhere

Sans Git ni carte bancaire — idéal pour un premier essai.

1. Crée un compte gratuit sur pythonanywhere.com.
2. Onglet **Consoles** → **Bash** : récupère ton code (`git clone ...`) et crée un venv :
   ```bash
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Onglet **Web** → **Add a new web app** → **Manual config** (Django) → choisis ta version de Python.
4. Configure le **virtualenv path**, le **WSGI file** (pointe vers `config/wsgi.py`, règle `DJANGO_SETTINGS_MODULE`).
5. Dans le fichier WSGI / les réglages : `ALLOWED_HOSTS = ["tonpseudo.pythonanywhere.com"]`, `DEBUG = False`.
6. Mappe les **statics** (URL `/static/` → dossier `staticfiles/`) et lance `collectstatic` + `migrate` dans la console.
7. **Reload** l'app depuis l'onglet Web.

> 💡 PythonAnywhere ne « dort » pas comme Render, mais l'offre gratuite limite le trafic, le CPU et n'autorise pas de domaine personnalisé.

---

## 11. Erreurs de déploiement fréquentes

| Erreur | Cause / solution |
| ------------------------------------------- | ----------------------------------------- |
| **400 Bad Request** sur tout le site | `ALLOWED_HOSTS` ne contient pas le domaine |
| **500** alors que tout marchait en local | `DEBUG=False` cache l'erreur → regarde les **logs** de l'hébergeur |
| Page sans CSS / statics manquants | `collectstatic` non lancé, ou WhiteNoise mal configuré |
| `CSRF verification failed` sur les formulaires | ajouter le domaine à `CSRF_TRUSTED_ORIGINS` |
| Données perdues après redéploiement | SQLite sur disque éphémère → passer à **PostgreSQL** |
| `SECRET_KEY` / `DATABASE_URL` introuvable | variable d'environnement non définie sur l'hébergeur |
| `ModuleNotFoundError` au démarrage | dépendance absente de `requirements.txt` |
| App très lente au premier accès | l'offre gratuite met l'app **en veille** (normal) |
| `DisallowedHost` dans les logs | idem `ALLOWED_HOSTS` |

---

## 12. Checklist mémo

Avant de déployer :

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS` en **variables d'environnement**
- [ ] `CSRF_TRUSTED_ORIGINS` = ton domaine (https)
- [ ] PostgreSQL (pas SQLite)
- [ ] `requirements.txt` à jour (Django, gunicorn, psycopg, whitenoise, django-environ)
- [ ] WhiteNoise configuré + `collectstatic` au build
- [ ] `Procfile` / start command : `gunicorn config.wsgi:application`
- [ ] `.env` et `*.sqlite3` dans `.gitignore`
- [ ] `python manage.py check --deploy` sans alerte bloquante
- [ ] `migrate` + `createsuperuser` après déploiement

```
NON-NÉGOCIABLES PROD
  DEBUG=False · SECRET_KEY en env · ALLOWED_HOSTS · PostgreSQL · collectstatic

DÉMARRAGE
  web: gunicorn config.wsgi:application

HÉBERGEURS GRATUITS (débutant)
  PythonAnywhere (sans carte, simple) · Render (git push, moderne)
  → l'app gratuite "s'endort", la BD gratuite peut expirer
```
