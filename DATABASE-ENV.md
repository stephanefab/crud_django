# Documentation Django — Bases de données & variables d'environnement

> Mémo sur les bases de données dans Django (SQLite, PostgreSQL, MySQL, Oracle, multi-BD) et la gestion des **variables d'environnement** (secrets, config par machine).
> Basé sur **Django 6.0** et le projet `config` / `company`.
> Voir aussi : [DJANGO.md](DJANGO.md) (settings.py § 2.2), [MODELS.md](MODELS.md) (modèles & ORM).

---

## Sommaire

1. [Vue d'ensemble : le réglage `DATABASES`](#1-vue-densemble--le-réglage-databases)
2. [SQLite (par défaut)](#2-sqlite-par-défaut)
3. [PostgreSQL (recommandé en prod)](#3-postgresql-recommandé-en-prod)
4. [MySQL / MariaDB](#4-mysql--mariadb)
5. [Oracle](#5-oracle)
6. [Tableau comparatif](#6-tableau-comparatif)
7. [Le workflow commun (drivers, migrate)](#7-le-workflow-commun-drivers-migrate)
8. [Bases de données multiples](#8-bases-de-données-multiples)
9. [Les migrations](#9-les-migrations)
    - 9.1 À quoi ça sert · 9.2 Le cycle · 9.3 Commandes · 9.4 Anatomie d'un fichier · 9.5 Avantages / inconvénients · 9.6 Limites & pièges
10. [Connecter une base existante (legacy)](#10-connecter-une-base-existante-legacy)
    - 10.1 Se connecter · 10.2 `inspectdb` · 10.3 `managed=False` · 10.4 Tables système · 10.5 Nouveaux modèles · 10.6 Modifier une table · 10.7 Décision & précautions
11. [Variables d'environnement : pourquoi](#11-variables-denvironnement--pourquoi)
12. [Approche 1 — `os.environ` natif](#12-approche-1--osenviron-natif)
13. [Approche 2 — `python-decouple`](#13-approche-2--python-decouple)
14. [Approche 3 — `django-environ`](#14-approche-3--django-environ)
15. [Comparaison des trois approches](#15-comparaison-des-trois-approches)
16. [Sécurité : `.env`, `.gitignore`, `.env.example`](#16-sécurité--env-gitignore-envexample)
17. [Checklist & pièges](#17-checklist--pièges)

---

## 1. Vue d'ensemble : le réglage `DATABASES`

Django parle à la base via le réglage **`DATABASES`** dans `config/settings.py`. Chaque base est décrite par un **`ENGINE`** (le pilote) et des paramètres de connexion.

```python
DATABASES = {
    "default": {                                       # la BD "default" est obligatoire
        "ENGINE": "django.db.backends.sqlite3",        # quel SGBD
        "NAME": BASE_DIR / "db.sqlite3",               # nom / fichier de la base
        # "USER", "PASSWORD", "HOST", "PORT" pour les BD serveur
    }
}
```

> 🧠 **Le superpouvoir de l'ORM** : ton code modèle et tes requêtes (`Customer.objects.filter(...)`, voir [MODELS.md](MODELS.md)) sont **identiques** quelle que soit la base. Changer de SGBD = changer `DATABASES`, **pas** ton code. C'est tout l'intérêt de l'ORM.

| Clé | Rôle |
| ----------- | ----------------------------------------------- |
| `ENGINE` | le backend Django (sqlite3, postgresql, mysql, oracle) |
| `NAME` | nom de la base (ou chemin du fichier pour SQLite) |
| `USER` | utilisateur de la base |
| `PASSWORD` | mot de passe |
| `HOST` | adresse du serveur (`localhost`, IP, hostname) |
| `PORT` | port (5432 Postgres, 3306 MySQL…) |
| `OPTIONS` | options spécifiques au pilote |
| `CONN_MAX_AGE` | durée de réutilisation des connexions (perf) |

---

## 2. SQLite (par défaut)

C'est la base par défaut : un **simple fichier** (`db.sqlite3`), zéro installation, parfaite pour **apprendre et développer**.

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

- ✅ Aucune config, aucun serveur à lancer, intégrée à Python.
- ❌ Mono-fichier, gère mal les écritures concurrentes, pas adaptée à une vraie prod multi-utilisateurs.

> 💡 **Règle d'or** : SQLite pour le **dev**, un vrai serveur (PostgreSQL) pour la **prod**. Ne déploie pas un site public sur SQLite.

---

## 3. PostgreSQL (recommandé en prod)

Le choix **n°1** pour Django en production : robuste, performant, riche (types JSON, full-text search, etc.). Django a un support de première classe pour Postgres.

**1. Installer le pilote :**

```bash
pip install psycopg[binary]      # psycopg 3 (moderne). Ancien : psycopg2-binary
```

**2. Configurer :**

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "crud1_db",
        "USER": "crud1_user",
        "PASSWORD": "motdepasse",      # ← à mettre en variable d'env (§ 11+)
        "HOST": "localhost",
        "PORT": "5432",
        "CONN_MAX_AGE": 60,            # réutilise les connexions 60s (perf)
    }
}
```

**3. Créer la base côté Postgres** (une fois) puis :

```bash
python manage.py migrate
```

> 🧠 Django ne **crée pas** la base elle-même : tu crées une base + un utilisateur côté PostgreSQL (`createdb`, `CREATE USER`), Django crée seulement les **tables** via `migrate`.

---

## 4. MySQL / MariaDB

Très répandu en hébergement mutualisé. MariaDB est un fork compatible.

```bash
pip install mysqlclient
```

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "crud1_db",
        "USER": "crud1_user",
        "PASSWORD": "motdepasse",      # ← variable d'env
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",      # supporte les emojis / unicode complet
        },
    }
}
```

> ⚠️ Utilise **`utf8mb4`** (pas `utf8`, qui est tronqué sous MySQL). Sans ça, les emojis et certains caractères font planter l'insertion.

---

## 5. Oracle

Plus rare, surtout en entreprise.

```bash
pip install oracledb
```

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.oracle",
        "NAME": "monserveur:1521/orcl",   # host:port/service
        "USER": "crud1_user",
        "PASSWORD": "motdepasse",         # ← variable d'env
    }
}
```

> Oracle a des particularités (longueur des noms, types) ; à réserver aux contextes qui l'imposent.

---

## 6. Tableau comparatif

| SGBD | Backend `ENGINE` | Pilote (`pip`) | Quand l'utiliser |
| ------------ | ----------------------------------- | ------------------------ | ------------------------------ |
| **SQLite** | `django.db.backends.sqlite3` | (intégré) | dev, prototypes, tests |
| **PostgreSQL** | `django.db.backends.postgresql` | `psycopg[binary]` | **prod (recommandé)** |
| **MySQL/MariaDB** | `django.db.backends.mysql` | `mysqlclient` | hébergement mutualisé, existant |
| **Oracle** | `django.db.backends.oracle` | `oracledb` | entreprise / contrainte impos. |

> 🧠 Quel que soit le choix, **ton code Django ne change pas**. Passe de SQLite à PostgreSQL en éditant seulement `DATABASES`, puis `migrate`.

---

## 7. Le workflow commun (drivers, migrate)

Peu importe la base, le cycle est le même :

```bash
# 1. installer le pilote de la BD (sauf SQLite, intégré)
pip install psycopg[binary]        # ou mysqlclient, oracledb...

# 2. (BD serveur) créer la base + l'utilisateur côté SGBD

# 3. configurer DATABASES dans settings.py

# 4. créer les tables
python manage.py migrate

# 5. (optionnel) vérifier la connexion
python manage.py dbshell           # ouvre le client SQL de la base
```

> 💡 **Changer de base sans perdre les données** : `dumpdata` (exporter) puis `loaddata` (réimporter) :
> ```bash
> python manage.py dumpdata > data.json     # depuis l'ancienne BD
> # ... bascule DATABASES vers la nouvelle, puis migrate ...
> python manage.py loaddata data.json       # vers la nouvelle BD
> ```

---

## 8. Bases de données multiples

Django peut gérer **plusieurs bases** en même temps. On ajoute des entrées dans `DATABASES` (la clé `default` reste obligatoire) :

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "crud1_main",
        # ...
    },
    "analytics": {                                   # 2e base
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "crud1_stats",
        # ...
    },
}
```

### 8.1 Choisir la base explicitement : `using()`

```python
Customer.objects.using("analytics").all()      # lire depuis "analytics"
customer.save(using="analytics")               # écrire dans "analytics"
```

### 8.2 Router automatique

Pour router **automatiquement** certains modèles vers une base, on écrit un **database router** :

```python
# company/routers.py
class AnalyticsRouter:
    route_app_labels = {"analytics"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "analytics"
        return None        # None = laisse Django choisir (default)

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "analytics"
        return None

    def allow_migrate(self, db, app_label, **hints):
        if app_label in self.route_app_labels:
            return db == "analytics"
        return db == "default"
```

```python
# settings.py
DATABASE_ROUTERS = ["company.routers.AnalyticsRouter"]
```

Migrer une base précise :

```bash
python manage.py migrate --database=analytics
```

> 🧠 Cas d'usage typiques : séparer une base de **lecture seule** (réplica), isoler les **statistiques**, ou connecter une **base héritée** (legacy) en plus de la principale.

---

## 9. Les migrations

Une **migration** = un fichier Python qui décrit un **changement de schéma** de la base (créer une table, ajouter/modifier/supprimer une colonne…). C'est le **journal versionné** de l'évolution de ta base — le pont entre ton `models.py` (le code) et les **tables réelles** (la base). (Vue pratique aussi dans [MODELS.md §7](MODELS.md).)

### 9.1 À quoi ça sert

- **Synchroniser** `models.py` et le schéma réel de la base.
- **Versionner** les changements de structure (commités dans Git, comme le code).
- **Rejouer** l'historique sur n'importe quelle machine (collègue, serveur de prod) → **même schéma partout**.
- Faire évoluer la base **sans écrire de SQL** à la main, en équipe, de façon traçable.

```
models.py  ──makemigrations──►  fichier migration  ──migrate──►  tables SQL
(ton code)                      (app/migrations/, commité)        (la base)
```

### 9.2 Le cycle (après CHAQUE modif de `models.py`)

```bash
python manage.py makemigrations    # 1. détecte les diffs → écrit un fichier de migration
python manage.py migrate           # 2. applique → exécute le SQL réel sur la base
```

> 🧠 **Le point clé** : `makemigrations` ne **touche pas** la base (il écrit juste un fichier). C'est `migrate` qui exécute le SQL. L'oubli de l'un des deux est l'erreur n°1 (« no such column », changement sans effet).

### 9.3 Les commandes essentielles

| Commande | Rôle |
| ----------------------------------------- | ----------------------------------------- |
| `makemigrations` | générer les migrations pour tous les changements |
| `makemigrations company` | seulement pour une app |
| `makemigrations --name ajout_phone company` | nommer la migration |
| `migrate` | appliquer toutes les migrations en attente |
| `migrate company 0003` | migrer jusqu'à une version précise |
| `migrate company zero` | **annuler** toutes les migrations de l'app |
| `showmigrations` | lister l'état (`[X]` = appliquée) |
| `sqlmigrate company 0001` | **voir le SQL** d'une migration sans l'exécuter |
| `migrate --fake` | marquer comme appliquée **sans** exécuter |
| `migrate --fake-initial` | idem pour la création initiale (tables déjà là) |
| `makemigrations --merge` | résoudre un conflit de migrations (équipe) |
| `makemigrations --empty company` | migration vide (pour une **data migration**) |
| `squashmigrations company 0001 0020` | fusionner plusieurs migrations en une |

### 9.4 Anatomie d'un fichier de migration

```python
# company/migrations/0002_customer_phone.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("company", "0001_initial"),     # ← l'ordre : dépend de la migration précédente
    ]
    operations = [
        migrations.AddField(             # ← l'opération de schéma
            model_name="customer",
            name="phone",
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
```

- `dependencies` → garantit l'**ordre** d'application (graphe de migrations).
- `operations` → la liste des changements (`CreateModel`, `AddField`, `AlterField`, `RemoveField`, `RunPython`, `RunSQL`…).

> ⚠️ Les fichiers de `migrations/` se **committent dans Git** : ils font partie de l'historique du schéma, au même titre que le code.

### 9.5 Avantages / inconvénients

| ✅ Avantages | ⚠️ Inconvénients / pièges |
| ------------------------------------------ | ----------------------------------------- |
| Pas de SQL à écrire | Magie « boîte noire » au début |
| Versionné, rejouable partout | Fichiers qui s'accumulent (→ `squashmigrations`) |
| Travail en équipe traçable | Conflits possibles à plusieurs (→ `--merge`) |
| Réversible (rollback) | Un rollback peut **perdre des données** |
| Multi-SGBD (même migration) | Renommage parfois mal détecté |

### 9.6 Limites & pièges à connaître

- **Renommer un champ/modèle** : Django demande *« renamed ? »*. Si tu réponds mal (ou en non-interactif), il génère un **`RemoveField` + `AddField`** → **perte des données** de la colonne. Vérifie avec `sqlmigrate`.
- **Transformer des données** (pas juste le schéma) : ce n'est pas automatique. On écrit une **data migration** avec `RunPython` :
  ```python
  def remplir(apps, schema_editor):
      Customer = apps.get_model("company", "Customer")
      for c in Customer.objects.all():
          c.phone = c.phone or "N/A"
          c.save()
  operations = [migrations.RunPython(remplir, migrations.RunPython.noop)]
  ```
- **Opérations non gérées** par l'ORM (vues SQL, triggers…) → `migrations.RunSQL("...")`.
- **Grosse table en prod** : un `ALTER` peut **verrouiller** la table le temps de l'opération. À planifier (fenêtre de maintenance, outils comme `pg_repack`).
- **`managed = False`** (section 10) : Django ne génère **aucune** migration pour ces tables.
- **Ne jamais éditer une migration déjà appliquée** en prod : crée une nouvelle migration à la place.

---

## 10. Connecter une base existante (legacy)

Scénario fréquent : une base **existe déjà** (avec ou sans données) et tu veux y brancher Django **sans la casser**.

> 🛑 **Avant tout : sauvegarde** (`pg_dump`…) et travaille sur une **copie**. On ne teste jamais ça sur la prod directement.

### 10.1 Se connecter

Pointe `DATABASES` vers la base existante (sections 1–5). Rien de spécial : c'est la connexion normale.

### 10.2 Générer les modèles : `inspectdb`

Django peut **lire** la structure existante et générer les modèles :

```bash
python manage.py inspectdb > company/models.py     # toutes les tables
python manage.py inspectdb clients > extrait.py     # une seule table
```

Résultat type :

```python
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    # ...
    class Meta:
        managed = False        # ← Django NE gère PAS cette table (voir 10.3)
        db_table = 'clients'   # ← le vrai nom de la table existante
```

> ⚠️ `inspectdb` est un **point de départ**, pas magique : relis le fichier (clés primaires, `ForeignKey` + `on_delete`, `related_name`, types ambigus).

### 10.3 La clé de la non-casse : `managed = False`

```python
class Meta:
    managed = False
```

Dit à Django **« cette table existe déjà, n'y touche pas »** : il ne la **crée pas**, ne la **modifie pas** (`ALTER`), ne la **supprime pas** — mais **lit/écrit** dedans normalement via l'ORM. Aucune migration n'est générée pour elle. (Données présentes ou non : ça ne change rien.)

### 10.4 Les tables système de Django

Django a besoin de **ses propres** tables (`auth_user`, `django_migrations`, `django_session`, admin…). Leurs noms n'entrent pas en conflit avec les tiennes :

```bash
python manage.py migrate    # crée UNIQUEMENT les tables système (tes managed=False sont ignorées)
```

> 💡 Si une table existante porte par malchance un nom réservé, isole la base legacy dans une **2ᵉ entrée `DATABASES` + un router** (section 8).

### 10.5 Ajouter de NOUVEAUX modèles sans rien casser

Tes nouveaux modèles sont gérés par Django (`managed=True`, le défaut) :

```python
class Note(models.Model):                  # nouveau → géré par Django
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    texte = models.TextField()
```

```bash
python manage.py makemigrations
python manage.py migrate        # crée SEULEMENT la nouvelle table, ne touche pas aux legacy
```

### 10.6 Modifier (`ALTER`) une table existante

| Stratégie | Comment | Pour qui |
| ------------------------------ | ------------------------------------------------- | ----------------- |
| **A. Manuel (le plus sûr)** | `ALTER TABLE` en SQL, puis refléter le champ dans le modèle (`managed=False`) | legacy sensible |
| **B. Confier à Django** | passer `managed=True`, `makemigrations`, puis `migrate --fake-initial` | reprise durable |
| **C. Migration déjà faite** | `migrate company 0001 --fake` | cas ponctuel |

**Le piège de l'option B** : passer `managed=False → True` puis `makemigrations` génère une migration qui veut **CRÉER** la table (qui existe déjà) → erreur. La parade :

```bash
python manage.py makemigrations              # génère le "CreateModel"
python manage.py migrate --fake-initial      # le marque comme DÉJÀ appliqué (pas de CREATE)
# → ensuite, tes ALTER suivants se géreront normalement
```

### 10.7 Décision & précautions

| Situation | Quoi faire |
| ------------------------------------------ | ------------------------------------------- |
| Lire/écrire une table existante sans la modifier | `managed=False` + `db_table` |
| Ajouter une nouvelle table | modèle `managed=True` + `makemigrations`/`migrate` |
| Modifier une table legacy ponctuellement | `ALTER` SQL + refléter dans le modèle |
| Confier durablement une table à Django | `managed=True` + `migrate --fake-initial` |

**Règle d'or :**
1. Sauvegarde + copie de travail.
2. Relis les modèles `inspectdb`.
3. Commence **tout en `managed=False`**, valide la lecture, puis prends le contrôle table par table.
4. `sqlmigrate` pour voir le SQL **avant** d'appliquer ; `dbshell` pour inspecter la base.

---

## 11. Variables d'environnement : pourquoi

Mettre le `SECRET_KEY`, les mots de passe de BD, les clés d'API **en dur** dans `settings.py` pose 3 problèmes :

1. **Sécurité** : si le code part sur GitHub, les secrets fuitent.
2. **Portabilité** : la config diffère entre ta machine, celle d'un collègue et le serveur (BD, DEBUG…).
3. **Bonnes pratiques** : le principe [12-factor](https://12factor.net/config) recommande de stocker la config dans l'**environnement**, pas dans le code.

La solution : externaliser ces valeurs dans des **variables d'environnement**, généralement regroupées dans un fichier **`.env`** (jamais commité).

```
.env  (à la racine, ignoré par Git)
────────────────────────────────────
SECRET_KEY=django-insecure-xxxxx
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/crud1_db
```

Trois façons de lire ce `.env` dans Django ↓

---

## 12. Approche 1 — `os.environ` natif

Sans aucune dépendance, avec le module standard `os`. Django propose `os.environ` ; pour lire un fichier `.env`, on peut le charger à la main (ou via `python-dotenv`).

```python
# settings.py
import os

SECRET_KEY = os.environ["SECRET_KEY"]            # KeyError si absent (strict)
DEBUG = os.environ.get("DEBUG", "False") == "True"   # défaut + conversion manuelle
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
```

Pour charger un `.env` automatiquement (sinon il faut exporter les variables à la main) :

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")    # à mettre TOUT EN HAUT de settings.py
```

- ✅ Zéro/peu de dépendance, transparent.
- ❌ Tout est une **chaîne** : conversions manuelles (`bool`, `int`, listes), verbeux.

> ⚠️ `os.environ.get("DEBUG")` renvoie la **chaîne** `"True"`, pas le booléen `True`. `bool("False")` vaut `True` en Python ! D'où la comparaison `== "True"`.

---

## 13. Approche 2 — `python-decouple`

Légère et populaire : elle lit `.env` (ou `settings.ini`) et **convertit les types** proprement.

```bash
pip install python-decouple
```

```python
# settings.py
from decouple import config, Csv

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)        # vrai booléen
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())   # → liste

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}
```

- ✅ Simple, `default=`, `cast=bool/int/Csv()`, pas besoin de charger le `.env` à la main.
- ⚠️ Pas de parsing d'URL de BD intégré (mais on peut combiner avec `dj-database-url`).

---

## 14. Approche 3 — `django-environ`

La plus orientée Django : elle gère le `.env`, les types, **et** parse une **`DATABASE_URL`** en une ligne (très pratique, format standard du cloud : Heroku, Railway, Render…).

```bash
pip install django-environ
```

```python
# settings.py
import environ

env = environ.Env(
    DEBUG=(bool, False),                 # type + valeur par défaut
)
environ.Env.read_env(BASE_DIR / ".env") # charge le .env

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")                     # vrai booléen
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ⭐ toute la config BD en UNE ligne, depuis DATABASE_URL
DATABASES = {
    "default": env.db(),                 # lit DATABASE_URL et le parse
}
```

`.env` correspondant :

```
SECRET_KEY=django-insecure-xxxxx
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://crud1_user:motdepasse@localhost:5432/crud1_db
```

- ✅ Le plus concis, `DATABASE_URL` (idéal pour le déploiement cloud), types natifs.
- ⚠️ Une dépendance de plus, format `DATABASE_URL` à connaître.

> 🧠 `DATABASE_URL` change juste de préfixe selon la BD :
> `postgres://…` · `mysql://…` · `sqlite:///db.sqlite3` · `oracle://…`

---

## 15. Comparaison des trois approches

| Critère | `os.environ` | `python-decouple` | `django-environ` |
| ------------------ | ------------------ | ------------------- | ------------------- |
| Dépendance | aucune* | légère | légère |
| Lecture `.env` | via `python-dotenv` | intégrée | intégrée |
| Types (bool/int/list) | manuel | `cast=` | natif |
| Parse `DATABASE_URL` | non | + `dj-database-url` | **oui** (`env.db()`) |
| Idéal pour | comprendre / minimal | projets simples | **Django + cloud** |

\* `os.environ` est natif ; charger un `.env` demande `python-dotenv`.

> 👉 **Recommandation** : `django-environ` pour un vrai projet (surtout déployé), `python-decouple` si tu veux plus léger, `os.environ` pour **comprendre** le mécanisme. Les trois sont valables — l'important est de **sortir les secrets du code**.

---

## 16. Sécurité : `.env`, `.gitignore`, `.env.example`

Quelle que soit l'approche, **trois fichiers** entrent en jeu :

```
.env            → les VRAIES valeurs (secrets). JAMAIS commité.
.gitignore      → contient ".env" pour l'exclure de Git.
.env.example    → un modèle SANS secrets, commité, qui documente les clés attendues.
```

`.gitignore` :

```gitignore
.env
*.sqlite3
__pycache__/
```

`.env.example` (commité, sert de gabarit aux autres développeurs) :

```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/NOM_BASE
```

> 🔐 Règles d'or :
> 1. **`.env` dans `.gitignore`** avant le premier commit.
> 2. Le `SECRET_KEY` de prod doit être **différent** de celui du dev, et **régénéré** s'il a fuité.
> 3. En prod, beaucoup d'hébergeurs (Railway, Render, Heroku…) fournissent les variables d'env **directement dans leur interface** — pas besoin de fichier `.env` sur le serveur.

---

## 17. Checklist & pièges

Passer de SQLite (dev) à PostgreSQL + variables d'env :

- [ ] `pip install psycopg[binary] django-environ`
- [ ] Créer la base + l'utilisateur côté PostgreSQL
- [ ] Créer `.env` (avec `DATABASE_URL`, `SECRET_KEY`, `DEBUG`)
- [ ] Ajouter `.env` au `.gitignore` + créer `.env.example`
- [ ] Lire la config via `env(...)` dans `settings.py`
- [ ] `python manage.py migrate`
- [ ] `python manage.py createsuperuser`

| Piège | Symptôme / solution |
| ------------------------------------------- | ----------------------------------------- |
| `.env` commité par erreur | secrets exposés → régénérer `SECRET_KEY`, purger l'historique |
| `DEBUG` reste `True` en prod | `bool("False")` == `True` : utiliser un cast propre |
| `django.db.utils.OperationalError` | base/serveur non démarré, mauvais HOST/PORT/identifiants |
| Pilote manquant | `Error loading psycopg2/mysqlclient` → `pip install` le driver |
| MySQL + emojis cassés | utiliser `OPTIONS={"charset": "utf8mb4"}` |
| Django ne « crée » pas la base | créer la base côté SGBD ; Django ne fait que les **tables** (`migrate`) |
| `SECRET_KEY` introuvable | `.env` non chargé (`read_env`/`load_dotenv` manquant ou mal placé) |
