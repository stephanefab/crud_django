# Documentation Django — Les logs (journalisation)

> Mémo sur la journalisation dans Django : configurer, écrire dans un fichier, formater, utiliser dans le code, et tenir un journal d'**audit**.
> Basé sur **Django 6.0** et le projet `config` / `company`.
> Voir aussi : [DJANGO.md](DJANGO.md) (settings.py §2.2), [SIGNALS.md](SIGNALS.md) (audit via signaux), [DEPLOYMENT.md](DEPLOYMENT.md) (logs en prod).

---

## Sommaire

1. [Pourquoi logger (et pas `print`) ?](#1-pourquoi-logger-et-pas-print-)
2. [Les 4 briques : logger, handler, formatter, niveau](#2-les-4-briques--logger-handler-formatter-niveau)
3. [Les niveaux de log](#3-les-niveaux-de-log)
4. [Configurer `LOGGING` dans `settings.py`](#4-configurer-logging-dans-settingspy)
5. [Écrire dans un fichier (+ rotation)](#5-écrire-dans-un-fichier--rotation)
6. [Formater les messages](#6-formater-les-messages)
7. [Utiliser un logger dans le code](#7-utiliser-un-logger-dans-le-code)
8. [Les loggers intégrés de Django](#8-les-loggers-intégrés-de-django)
9. [Tenir un journal d'audit](#9-tenir-un-journal-daudit)
10. [En production](#10-en-production)
11. [Checklist & pièges](#11-checklist--pièges)

---

## 1. Pourquoi logger (et pas `print`) ?

Un **log** = un message horodaté décrivant ce que fait l'application. C'est **l'unique fenêtre** sur ce qui se passe en production (où il n'y a pas de console interactive).

| `print()` | `logging` |
| ----------------------------- | ----------------------------------------- |
| disparaît en prod | écrit dans un fichier / service |
| pas de niveau, pas de date | niveau, horodatage, module, contexte |
| tout ou rien | filtrable par niveau et par module |
| à retirer avant de livrer | reste, et se règle par environnement |

> 🧠 Règle simple : `print` pour bricoler vite, **`logging` pour tout le reste**. En prod, c'est ce qui te permet de comprendre un bug que tu ne peux pas reproduire.

---

## 2. Les 4 briques : logger, handler, formatter, niveau

Le système de log de Python (utilisé par Django) repose sur 4 composants :

| Brique | Rôle | Analogie |
| ------------ | ------------------------------------------ | ------------------------ |
| **Logger** | l'objet sur lequel tu écris (`logger.info(...)`) | l'auteur du message |
| **Handler** | **où** le message va (fichier, console…) | la destination |
| **Formatter** | **à quoi** ressemble la ligne | la mise en forme |
| **Niveau** | le seuil de gravité retenu | le filtre |

```
logger.error("Boom")  ──►  Logger  ──►  Handler(s)  ──►  Formatter  ──►  fichier / console
                            (filtre par niveau)         (met en forme la ligne)
```

Un logger peut avoir **plusieurs** handlers (ex : afficher dans la console **et** écrire dans un fichier).

---

## 3. Les niveaux de log

Du moins au plus grave. Le niveau configuré agit comme un **seuil** : on ne garde que les messages **≥** au niveau choisi.

| Niveau | Quand l'utiliser | Valeur |
| ----------- | ------------------------------------------- | ------ |
| `DEBUG` | détails de mise au point (dev) | 10 |
| `INFO` | événements normaux (« client créé ») | 20 |
| `WARNING` | quelque chose d'anormal mais non bloquant | 30 |
| `ERROR` | une opération a échoué | 40 |
| `CRITICAL` | l'application est gravement compromise | 50 |

> Exemple : un handler réglé sur `WARNING` ignore `DEBUG` et `INFO`, et garde `WARNING`/`ERROR`/`CRITICAL`. En dev on descend à `DEBUG`, en prod on reste souvent à `INFO` ou `WARNING`.

---

## 4. Configurer `LOGGING` dans `settings.py`

Django configure les logs via un **dictionnaire `LOGGING`** (format `dictConfig` de Python). Structure complète, commentée :

```python
# config/settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,        # garde les loggers Django par défaut

    # 1) à quoi ressemblent les lignes
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },

    # 2) où vont les messages
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",   # le dossier doit exister
            "formatter": "verbose",
            "level": "INFO",
        },
    },

    # 3) qui écrit, vers quels handlers, à partir de quel niveau
    "loggers": {
        "django": {                              # logs internes de Django
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "company": {                             # TON app (logger "company")
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```

> ⚠️ Le **dossier** `logs/` doit exister, sinon `FileHandler` plante au démarrage. Crée-le (et ajoute `logs/` au `.gitignore`), ou crée-le en Python avant : `(BASE_DIR / "logs").mkdir(exist_ok=True)`.

---

## 5. Écrire dans un fichier (+ rotation)

Le handler `FileHandler` (ci-dessus) écrit dans un fichier unique qui **grossit indéfiniment**. En pratique, on préfère un fichier **qui tourne** (rotation) pour éviter qu'il devienne énorme.

**Rotation par taille** — `RotatingFileHandler` :

```python
"handlers": {
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": BASE_DIR / "logs" / "django.log",
        "maxBytes": 5 * 1024 * 1024,    # 5 Mo par fichier
        "backupCount": 5,               # garde django.log.1 … django.log.5
        "formatter": "verbose",
    },
},
```

**Rotation par date** — `TimedRotatingFileHandler` (un fichier par jour) :

```python
"file": {
    "class": "logging.handlers.TimedRotatingFileHandler",
    "filename": BASE_DIR / "logs" / "django.log",
    "when": "midnight",                 # rotation chaque nuit
    "backupCount": 14,                  # garde 14 jours
    "formatter": "verbose",
},
```

> 💡 En production, beaucoup d'hébergeurs collectent plutôt la **sortie console** (stdout) : un simple `StreamHandler` suffit alors, c'est la plateforme qui gère les fichiers/rotation (voir [§10](#10-en-production)).

---

## 6. Formater les messages

Le `format` d'un formatter assemble des **attributs** entre `{...}` (avec `"style": "{"`). Les plus utiles :

| Champ | Donne |
| --------------- | --------------------------------- |
| `{asctime}` | date et heure |
| `{levelname}` | niveau (`INFO`, `ERROR`…) |
| `{name}` | nom du logger (ex : `company.views`) |
| `{message}` | le message |
| `{module}` | le module Python |
| `{funcName}` | la fonction |
| `{lineno}` | le numéro de ligne |
| `{process}` / `{thread}` | process / thread |

Exemple :

```python
"format": "{asctime} [{levelname}] {name} ({funcName}:{lineno}) — {message}",
"style": "{",
"datefmt": "%Y-%m-%d %H:%M:%S",
```

→ donne une ligne comme :

```
2026-06-03 14:30:12 [INFO] company.views (customers_create:45) — Client créé id=12
```

> 💡 Pour des logs exploités par des outils (ELK, Datadog…), on utilise souvent un **format JSON** via la lib `python-json-logger`.

---

## 7. Utiliser un logger dans le code

Dans n'importe quel module, on récupère un logger nommé d'après le module (`__name__`), puis on écrit :

```python
# company/views.py
import logging

logger = logging.getLogger(__name__)     # ex: "company.views"

def customers_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            logger.info("Client créé id=%s par %s", customer.id, request.user)
            return redirect("company.customers")
        else:
            logger.warning("Formulaire invalide : %s", form.errors)
    return render(request, "company/customer_add.html", {"form": form})
```

> 🧠 `logger = logging.getLogger(__name__)` : le nom (`company.views`) **hérite** de la config du logger parent `company` (§4). C'est la convention standard — un logger par module, configuré au niveau de l'app.

**Les méthodes** : `logger.debug()`, `.info()`, `.warning()`, `.error()`, `.critical()`.

**Logger une exception** (avec la stack trace complète) :

```python
try:
    risky()
except Exception:
    logger.exception("Échec du traitement")   # = error() + traceback automatique
    # ou : logger.error("Échec", exc_info=True)
```

> ⚠️ Utilise les **`%s`** (paramètres « lazy »), pas la f-string : `logger.info("id=%s", id)` plutôt que `logger.info(f"id={id}")`. Le formatage n'a lieu que si le message est réellement émis (perf).
>
> 🔐 Ne **jamais** logger de secrets (mots de passe, tokens, n° de carte, contenu de `request.POST` sensible).

---

## 8. Les loggers intégrés de Django

Django émet déjà des logs sur des loggers nommés — il suffit de les configurer (§4) :

| Logger | Contient |
| ----------------------- | ----------------------------------------- |
| `django` | logger parent de tout Django |
| `django.request` | erreurs des requêtes (4xx/5xx) |
| `django.server` | requêtes du serveur de dev (`runserver`) |
| `django.db.backends` | **les requêtes SQL** (niveau `DEBUG`) |
| `django.security.*` | événements de sécurité (ex : `DisallowedHost`) |

**Voir les requêtes SQL en dev** (pratique pour optimiser, cf. N+1 dans [MODELS.md](MODELS.md)) :

```python
"loggers": {
    "django.db.backends": {
        "handlers": ["console"],
        "level": "DEBUG",      # affiche chaque requête SQL
        "propagate": False,
    },
},
```

> ⚠️ N'active `django.db.backends` en `DEBUG` **qu'en développement** : en prod, ça inonde les logs et ralentit.

---

## 9. Tenir un journal d'audit

Un **audit** = tracer *qui a fait quoi et quand* (créations, modifications, suppressions, connexions) — utile pour la sécurité et la conformité. On dédie un **logger + fichier séparés**.

**1. Un handler et un logger d'audit** (`settings.py`) :

```python
LOGGING = {
    # ... (version, formatters) ...
    "handlers": {
        # ...
        "audit_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": BASE_DIR / "logs" / "audit.log",
            "when": "midnight",
            "backupCount": 90,                 # 90 jours d'historique
            "formatter": "verbose",
        },
    },
    "loggers": {
        # ...
        "audit": {
            "handlers": ["audit_file"],
            "level": "INFO",
            "propagate": False,                # n'écrit QUE dans audit.log
        },
    },
}
```

**2. Écrire les événements d'audit** dans les vues :

```python
import logging
audit = logging.getLogger("audit")

def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == "POST":
        audit.info("DELETE customer id=%s (%s) par user=%s",
                   id, customer, request.user)
        customer.delete()
    return redirect("company.customers")
```

**3. (Alternative) audit automatique via les signaux** — pour tracer **toutes** les sauvegardes/suppressions sans répéter le code (voir [SIGNALS.md](SIGNALS.md)) :

```python
# company/signals.py
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Customer

audit = logging.getLogger("audit")

@receiver(post_save, sender=Customer)
def audit_save(sender, instance, created, **kwargs):
    action = "CREATE" if created else "UPDATE"
    audit.info("%s customer id=%s (%s)", action, instance.id, instance)

@receiver(post_delete, sender=Customer)
def audit_delete(sender, instance, **kwargs):
    audit.info("DELETE customer id=%s (%s)", instance.id, instance)
```

> ⚠️ Le signal ne connaît pas `request.user` (pas d'accès à la requête). Pour tracer **l'utilisateur**, loggue dans la **vue** (où tu as `request`), ou utilise un middleware qui stocke l'utilisateur courant. Les signaux ne se déclenchent pas non plus sur les opérations en masse (cf. [SIGNALS.md](SIGNALS.md)).

> 💡 Pour un audit clé en main (qui/quoi/avant/après en base), des libs existent : **django-auditlog**, **django-simple-history**.

---

## 10. En production

- **Niveau** : `INFO` ou `WARNING` (pas `DEBUG`, trop bavard). Règle-le par variable d'environnement (voir [DATABASE-ENV.md](DATABASE-ENV.md)) :
  ```python
  LOG_LEVEL = env("LOG_LEVEL", default="INFO")
  ```
- **Console plutôt que fichier** : sur la plupart des hébergeurs (Render, Railway…), écris sur **stdout** (`StreamHandler`) — la plateforme collecte et archive les logs. Un fichier local serait effacé au redéploiement (système éphémère, cf. [DEPLOYMENT.md](DEPLOYMENT.md)).
- **Alerte sur erreurs** : connecte un service comme **Sentry** (`sentry-sdk`) pour être notifié des `ERROR`/exceptions avec la stack trace, plutôt que de fouiller les fichiers.
- **`ADMINS` + `mail_admins`** : Django peut **envoyer un email** aux admins sur les erreurs 500 (handler `django.utils.log.AdminEmailHandler`).
- 🔐 Jamais de secrets/données personnelles dans les logs (RGPD).

---

## 11. Checklist & pièges

Mettre en place les logs :

- [ ] Définir `LOGGING` dans `settings.py` (formatters / handlers / loggers)
- [ ] Créer le dossier `logs/` (+ l'ajouter au `.gitignore`)
- [ ] Un logger par module : `logger = logging.getLogger(__name__)`
- [ ] Utiliser le bon niveau (`info`, `warning`, `error`, `exception`)
- [ ] (Audit) logger `audit` + fichier dédié, écrit dans les vues (pour avoir `request.user`)
- [ ] En prod : niveau `INFO`, sortie console, éventuellement Sentry

| Piège | Cause / solution |
| ------------------------------------------- | ----------------------------------------- |
| `FileNotFoundError` au démarrage | dossier `logs/` inexistant |
| Rien ne s'écrit | mauvais nom de logger, ou niveau trop haut |
| Doublons de lignes | `propagate=True` + logger parent qui réécrit → mettre `propagate=False` |
| Logs SQL qui inondent | `django.db.backends` en `DEBUG` laissé en prod |
| Secrets dans les logs | ne jamais logger `request.POST`/mots de passe |
| Fichier de log géant | utiliser `RotatingFileHandler` / `TimedRotatingFileHandler` |
| Logs perdus après redéploiement | fichier sur disque éphémère → logger sur **stdout** en prod |
| f-string dans le log | préférer `logger.info("x=%s", x)` (lazy) |
