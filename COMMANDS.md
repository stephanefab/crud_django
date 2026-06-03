# Documentation Django — `manage.py` & les commandes

> Mémo sur `manage.py`, les commandes intégrées et la création de **commandes personnalisées** (management commands).
> Basé sur **Django 6.0**.

---

## Sommaire

1. [`manage.py`, c'est quoi ?](#1-managepy-cest-quoi-)
2. [Les commandes intégrées les plus utiles](#2-les-commandes-intégrées-les-plus-utiles)
3. [Créer sa propre commande](#3-créer-sa-propre-commande)
4. [La structure d'une commande](#4-la-structure-dune-commande)
5. [Ajouter des arguments & options](#5-ajouter-des-arguments--options)
6. [Afficher du texte proprement](#6-afficher-du-texte-proprement)
7. [Exemple commenté : `seed_customers`](#7-exemple-commenté--seed_customers)
8. [Astuces & pièges](#8-astuces--pièges)
9. [Mémo express](#9-mémo-express)

---

## 1. `manage.py`, c'est quoi ?

`manage.py` est le **point d'entrée en ligne de commande** de ton projet. C'est l'équivalent de `php artisan` en Laravel ou de `rails` en Ruby on Rails.

Il fait deux choses :
1. Configure l'environnement Django (trouve `settings.py`).
2. Lance la commande que tu lui passes.

```bash
python manage.py <commande> [arguments] [options]
```

Pour voir **toutes** les commandes disponibles :

```bash
python manage.py help
```

Pour l'aide d'une commande précise :

```bash
python manage.py help migrate
python manage.py seed_customers --help
```

> 💡 Les commandes sont regroupées par app : `[django]`, `[auth]`, `[company]` (tes commandes perso)…

---

## 2. Les commandes intégrées les plus utiles

| Commande                          | Rôle                                              |
| --------------------------------- | ------------------------------------------------- |
| `runserver`                       | Lance le serveur de développement                 |
| `makemigrations`                  | Génère les fichiers de migration depuis les modèles |
| `migrate`                         | Applique les migrations (crée/modifie les tables) |
| `showmigrations`                  | Affiche l'état des migrations                      |
| `createsuperuser`                 | Crée un compte admin                              |
| `shell`                           | Ouvre un shell Python avec Django chargé          |
| `startapp <nom>`                  | Crée une nouvelle app                             |
| `startproject <nom>`              | Crée un nouveau projet                            |
| `collectstatic`                   | Rassemble les fichiers statiques (déploiement)    |
| `dumpdata` / `loaddata`           | Exporter / importer des données (fixtures)        |
| `check`                           | Vérifie le projet sans lancer le serveur          |
| `test`                            | Lance les tests                                   |

```bash
python manage.py runserver           # → http://127.0.0.1:8000/
python manage.py runserver 8080      # sur un autre port
python manage.py createsuperuser     # crée l'admin
```

---

## 3. Créer sa propre commande

C'est l'équivalent d'un **Seeder Laravel** ou d'une tâche personnalisée. Utile pour : remplir la base (seed), nettoyer des données, envoyer des emails groupés, importer un fichier…

### La structure de dossiers OBLIGATOIRE

Django cherche les commandes dans un chemin **précis** : `app/management/commands/`.

```
company/
├── management/
│   ├── __init__.py            ← fichier VIDE, obligatoire
│   └── commands/
│       ├── __init__.py        ← fichier VIDE, obligatoire
│       └── seed_customers.py  ← TA commande (= le nom à taper)
├── models.py
├── views.py
```

> ⚠️ Les deux `__init__.py` (vides) sont **obligatoires** : sans eux, Django ne trouve pas la commande. Le **nom du fichier** `.py` devient le nom de la commande (`seed_customers.py` → `manage.py seed_customers`).

---

## 4. La structure d'une commande

Une commande = une classe `Command` héritant de `BaseCommand`, avec une méthode `handle()` (le code exécuté).

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Description affichée par --help"

    def handle(self, *args, **options):
        # le code de la commande va ici
        self.stdout.write("Ma commande s'exécute !")
```

| Élément              | Rôle                                                  |
| -------------------- | ----------------------------------------------------- |
| `class Command`      | nom **obligatoire** (Django le cherche tel quel)      |
| `BaseCommand`        | la classe de base à hériter                           |
| `help`               | texte affiché par `manage.py <cmd> --help`            |
| `handle()`           | la méthode appelée quand on lance la commande         |
| `self.stdout.write()` | afficher du texte (préférer à `print()`)             |

Lancement :

```bash
python manage.py ma_commande
```

---

## 5. Ajouter des arguments & options

On surcharge `add_arguments(self, parser)`. Django utilise `argparse` (la lib standard Python).

### Argument positionnel (obligatoire ou avec défaut)

```python
def add_arguments(self, parser):
    parser.add_argument("nombre", type=int, nargs="?", default=100,
                        help="Nombre d'éléments")

def handle(self, *args, **options):
    nombre = options["nombre"]
    self.stdout.write(f"Nombre = {nombre}")
```

```bash
python manage.py seed_customers          # → 100 (défaut)
python manage.py seed_customers 50       # → 50
```

- `type=int` → convertit en entier
- `nargs="?"` → rend l'argument **optionnel**
- `default=100` → valeur si absent

### Option / flag (avec `--`)

```python
def add_arguments(self, parser):
    parser.add_argument("--clear", action="store_true",
                        help="Vide la table avant d'insérer")

def handle(self, *args, **options):
    if options["clear"]:
        Customer.objects.all().delete()
```

```bash
python manage.py seed_customers --clear
```

- `action="store_true"` → `--clear` devient `True` s'il est présent, `False` sinon (un interrupteur).

### Option avec valeur

```python
parser.add_argument("--locale", type=str, default="fr_FR",
                    help="Langue des fausses données")
```

```bash
python manage.py seed_customers --locale en_US
```

---

## 6. Afficher du texte proprement

Dans une commande, on utilise `self.stdout.write()` (pas `print()`), et `self.style` pour la **couleur** :

```python
self.stdout.write("texte normal")
self.stdout.write(self.style.SUCCESS("✓ Succès (vert)"))
self.stdout.write(self.style.WARNING("⚠ Attention (jaune)"))
self.stdout.write(self.style.ERROR("✗ Erreur (rouge)"))
self.stdout.write(self.style.NOTICE("Info (rouge clair)"))
```

> Pourquoi pas `print()` ? `self.stdout.write()` respecte les options Django (`--verbosity`, redirection de sortie, tests…) et permet la coloration.

---

## 7. Exemple commenté : `seed_customers`

La commande créée dans ce projet ([company/management/commands/seed_customers.py](company/management/commands/seed_customers.py)) :

```python
import random
from django.core.management.base import BaseCommand
from company.models import Customer

PRENOMS = ["Fabien", "Marie", "Lucas", ...]
NOMS = ["Martin", "Bernard", ...]

class Command(BaseCommand):
    help = "Crée des clients fictifs pour tester (par défaut 100)."

    def add_arguments(self, parser):
        parser.add_argument("nombre", type=int, nargs="?", default=100)

    def handle(self, *args, **options):
        nombre = options["nombre"]
        clients = []

        for i in range(nombre):
            clients.append(Customer(
                first_name=random.choice(PRENOMS),
                last_name=random.choice(NOMS),
                email=f"...{i}@example.com",   # i = unicité de l'email
                phone="06......",
                address="...",
            ))

        Customer.objects.bulk_create(clients)   # 1 seul INSERT pour tout

        self.stdout.write(self.style.SUCCESS(
            f"{nombre} clients créés. Total : {Customer.objects.count()}"
        ))
```

Utilisation :

```bash
python manage.py seed_customers       # 100
python manage.py seed_customers 50    # 50
```

> 🔑 **`bulk_create(liste)`** insère tous les objets en **une seule requête SQL**, bien plus rapide que 100 `.save()` séparés. C'est LA bonne pratique pour du seed en masse.

---

## 8. Astuces & pièges

| Piège | Solution |
| ----- | -------- |
| Commande introuvable (`Unknown command`) | vérifier les 2 `__init__.py` + le chemin `app/management/commands/` |
| App pas dans `INSTALLED_APPS` | Django ne scanne que les apps installées |
| Utiliser `print()` | préférer `self.stdout.write()` |
| Boucle de 1000 `.save()` (lent) | `bulk_create()` |
| Oublier que le **nom du fichier** = nom de la commande | `seed_customers.py` → `seed_customers` |

### Appeler une commande depuis le code Python

```python
from django.core.management import call_command

call_command("seed_customers", 50)
call_command("migrate")
```

Pratique pour enchaîner des commandes (ex : une commande `setup` qui migre puis seed).

---

## 9. Mémo express

```
manage.py
  python manage.py <commande> [args] [options]
  help / <cmd> --help

INTÉGRÉES UTILES
  runserver · makemigrations · migrate · shell
  createsuperuser · startapp · check · dumpdata/loaddata

COMMANDE PERSO (= seeder Laravel)
  emplacement : app/management/commands/nom.py
  + 2 fichiers __init__.py VIDES obligatoires
  nom du fichier = nom de la commande

STRUCTURE
  class Command(BaseCommand):
      help = "..."
      def add_arguments(self, parser): parser.add_argument(...)
      def handle(self, *args, **options): ...

ARGUMENTS
  positionnel : parser.add_argument("n", type=int, nargs="?", default=100)
  flag        : parser.add_argument("--clear", action="store_true")
  valeur      : parser.add_argument("--locale", default="fr_FR")
  lecture     : options["n"] / options["clear"]

AFFICHAGE
  self.stdout.write(self.style.SUCCESS("..."))   ← pas print()

PERFORMANCE
  bulk_create(liste)  ← 1 INSERT pour insérer en masse

APPEL DEPUIS LE CODE
  from django.core.management import call_command
  call_command("seed_customers", 50)
```

> 📚 Référence officielle : https://docs.djangoproject.com/en/6.0/howto/custom-management-commands/
