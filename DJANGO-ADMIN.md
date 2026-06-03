# Documentation Django — L'admin

> Mémo sur le site d'administration Django : y accéder, enregistrer des modèles, personnaliser l'affichage, les filtres, les inlines et les actions.
> Basé sur **Django 6.0** et le projet `company` / modèle `Customer`.
> Voir aussi : [DJANGO.md](DJANGO.md) (vues, URLs, templates), [MODELS.md](MODELS.md) (modèles), [AUTH.md](AUTH.md) (login, permissions, groupes).

---

## Sommaire

1. [C'est quoi l'admin Django ?](#1-cest-quoi-ladmin-django-)
2. [Y accéder : `createsuperuser`](#2-y-accéder--createsuperuser)
3. [Enregistrer un modèle](#3-enregistrer-un-modèle)
4. [Personnaliser l'affichage (`ModelAdmin`)](#4-personnaliser-laffichage-modeladmin)
5. [Recherche, filtres et tri](#5-recherche-filtres-et-tri)
6. [Organiser le formulaire d'édition](#6-organiser-le-formulaire-dédition)
7. [Relations : les `inlines`](#7-relations--les-inlines)
8. [Actions personnalisées](#8-actions-personnalisées)
9. [Personnaliser le site admin](#9-personnaliser-le-site-admin)
10. [Permissions dans l'admin](#10-permissions-dans-ladmin)
11. [Checklist & pièges](#11-checklist--pièges)

---

## 1. C'est quoi l'admin Django ?

L'**admin** est une interface web **générée automatiquement** pour gérer les données de ton site (créer/lire/modifier/supprimer) — un CRUD complet, prêt à l'emploi, **sans écrire de vue ni de template**.

| | L'admin | Tes vues (DJANGO.md) |
| ------------ | -------------------------------------- | ----------------------------- |
| Public | **toi / le staff** (back-office) | les visiteurs du site |
| Qui le crée | Django, automatiquement | toi |
| URL | `/admin/` | `/company/...` |
| Usage | gérer les données rapidement | l'expérience utilisateur finale |

> 🧠 L'admin est **déjà installé** : `'django.contrib.admin'` est dans `INSTALLED_APPS` et `path('admin/', admin.site.urls)` dans `config/urls.py` (généré par `startproject`). Il repose entièrement sur le système d'**authentification** (voir [AUTH.md](AUTH.md)).

---

## 2. Y accéder : `createsuperuser`

Pour te connecter à `/admin/`, il faut un **superutilisateur** (un compte avec tous les droits).

```bash
python manage.py createsuperuser
# Username, Email, Password (x2)
```

Puis lance le serveur et va sur :

```
http://127.0.0.1:8000/admin/
```

> ⚠️ Avant tout, les tables d'auth doivent exister : `python manage.py migrate` (créé les tables `auth_user`, etc.).

Par défaut, l'admin affiche déjà **Users** et **Groups** (le système d'auth). Tes propres modèles n'apparaissent **que** si tu les **enregistres** (étape 3).

---

## 3. Enregistrer un modèle

Pour qu'un modèle apparaisse dans l'admin, on l'enregistre dans `company/admin.py`.

**Version minimale :**

```python
from django.contrib import admin
from .models import Customer

admin.site.register(Customer)
```

`Customer` apparaît maintenant dans l'admin. Tu peux ajouter/éditer/supprimer des clients.

> 💡 Sans `__str__` sur le modèle, chaque ligne s'affiche `Customer object (1)`. Définis `__str__` (voir [MODELS.md](MODELS.md)) pour un libellé lisible — c'est lui que l'admin affiche partout.

---

## 4. Personnaliser l'affichage (`ModelAdmin`)

Pour contrôler **comment** le modèle s'affiche, on crée une classe `ModelAdmin`. La syntaxe moderne utilise le **décorateur** `@admin.register` :

```python
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display  = ("first_name", "last_name", "email", "phone")  # colonnes du tableau
    list_display_links = ("first_name", "last_name")               # colonnes cliquables
    search_fields = ("first_name", "last_name", "email")           # barre de recherche
    list_filter   = ("last_name",)                                 # filtres latéraux
    ordering      = ("last_name", "first_name")                    # tri par défaut
    list_per_page = 25                                             # pagination
```

> Équivalent sans décorateur : `admin.site.register(Customer, CustomerAdmin)`.

**Les options les plus utiles de `ModelAdmin` :**

| Option | Effet |
| ------------------- | ------------------------------------------------------- |
| `list_display` | les **colonnes** affichées dans la liste |
| `list_display_links` | quelles colonnes sont des **liens** vers l'édition |
| `list_editable` | éditer un champ **directement** dans la liste |
| `search_fields` | active une **barre de recherche** sur ces champs |
| `list_filter` | **filtres** dans la barre latérale |
| `ordering` | tri par défaut (`"-id"` = décroissant) |
| `list_per_page` | nombre de lignes par page |
| `readonly_fields` | champs **non modifiables** dans le formulaire |
| `date_hierarchy` | navigation par date (sur un champ date) |

> ⚠️ `list_editable` ne peut **pas** contenir un champ qui est aussi dans `list_display_links` (Django lève une erreur). Un champ éditable en ligne ne peut pas être en même temps le lien d'édition.

**Afficher une valeur calculée** comme colonne (méthode du `ModelAdmin`) :

```python
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email")

    @admin.display(description="Nom complet")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
```

---

## 5. Recherche, filtres et tri

Avec les options de la section 4, l'admin te donne **gratuitement** :

- **Recherche** (`search_fields`) : une barre en haut qui filtre sur les champs listés (insensible à la casse, recherche partielle). Préfixes possibles : `^` (commence par), `=` (égal exact), `@` (recherche plein texte).
  ```python
  search_fields = ("first_name", "=email")   # email exact, prénom partiel
  ```
- **Filtres** (`list_filter`) : des liens dans la barre latérale pour filtrer (par valeur exacte, par booléen, par date…).
  ```python
  list_filter = ("last_name", "email")
  ```
- **Tri** : clique sur un en-tête de colonne pour trier ; `ordering` définit le tri par défaut.

> 💡 Sur une `ForeignKey`, `list_filter = ("company",)` génère un filtre par entreprise liée. Pour beaucoup de valeurs, utilise `autocomplete_fields` (champ de recherche au lieu d'un menu géant).

---

## 6. Organiser le formulaire d'édition

Par défaut, le formulaire d'édition affiche tous les champs dans l'ordre du modèle. Tu peux le réorganiser :

```python
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    # ordre simple des champs
    fields = ("first_name", "last_name", "email", "phone", "address")

    # OU regroupés en sections (fieldsets)
    fieldsets = (
        ("Identité", {
            "fields": ("first_name", "last_name"),
        }),
        ("Contact", {
            "fields": ("email", "phone", "address"),
            "classes": ("collapse",),   # section repliable
        }),
    )

    readonly_fields = ("email",)        # affiché mais non modifiable
```

> ⚠️ `fields` et `fieldsets` sont **exclusifs** : on utilise l'un **ou** l'autre, pas les deux.

---

## 7. Relations : les `inlines`

Un **inline** permet d'éditer des objets liés **directement** dans le formulaire du parent. Exemple : éditer les commandes (`Order`) d'un client sur sa fiche.

```python
from django.contrib import admin
from .models import Customer, Order


class OrderInline(admin.TabularInline):   # TabularInline = tableau compact
    model = Order
    extra = 1                             # 1 ligne vide pour ajouter

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    inlines = [OrderInline]               # les commandes apparaissent sur la fiche client
```

- `TabularInline` → affichage en **tableau** (lignes compactes).
- `StackedInline` → affichage **empilé** (un bloc par objet, plus aéré).

> 🧠 L'inline se met sur le **parent** (`Customer`) et pointe vers le modèle **enfant** (`Order`) qui porte la `ForeignKey`. (Relations expliquées dans [MODELS.md](MODELS.md).)

---

## 8. Actions personnalisées

Une **action** s'applique à plusieurs objets sélectionnés via la liste déroulante en haut de la liste. Django en fournit une (« Supprimer les éléments sélectionnés ») ; tu peux en ajouter.

```python
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email")
    actions = ["mettre_en_majuscules"]

    @admin.action(description="Mettre le nom en MAJUSCULES")
    def mettre_en_majuscules(self, request, queryset):
        for customer in queryset:
            customer.last_name = customer.last_name.upper()
            customer.save()
        self.message_user(request, f"{queryset.count()} client(s) mis à jour.")
```

- `queryset` = les objets **cochés** dans la liste.
- `self.message_user(...)` affiche un message flash dans l'admin.

---

## 9. Personnaliser le site admin

Changer les titres affichés (dans `config/urls.py` ou un `admin.py`) :

```python
from django.contrib import admin

admin.site.site_header = "Administration Crud1"   # bandeau du haut
admin.site.site_title  = "Crud1 Admin"            # titre de l'onglet
admin.site.index_title = "Tableau de bord"        # titre de la page d'accueil
```

> Pour aller plus loin (thème, surcharge de templates), on peut surcharger les templates de l'admin ou utiliser une lib comme **django-jazzmin** / **django-grappelli**.

---

## 10. Permissions dans l'admin

L'admin respecte le système de **permissions** de Django (détaillé dans [AUTH.md](AUTH.md)). Pour chaque modèle, Django crée 4 permissions : `add`, `change`, `delete`, `view`.

- Un utilisateur doit avoir `is_staff = True` pour **accéder** à l'admin.
- Il ne voit/édite que les modèles pour lesquels il a la permission.
- Un **superuser** (`is_superuser = True`) a **toutes** les permissions.

```
is_staff = True   → peut entrer dans /admin/
is_superuser=True → voit et fait TOUT
permissions/groupes → contrôle fin du reste (voir AUTH.md)
```

> 💡 Pour donner un accès limité à un collaborateur : crée son compte, coche `is_staff`, et assigne-lui un **groupe** avec les bonnes permissions (plutôt que de cocher 40 permissions à la main).

---

## 11. Checklist & pièges

Pour exposer un modèle dans l'admin :

- [ ] `python manage.py migrate` (tables d'auth) puis `createsuperuser`
- [ ] Définir `__str__` sur le modèle ([MODELS.md](MODELS.md))
- [ ] `@admin.register(MonModele)` + classe `ModelAdmin` dans `app/admin.py`
- [ ] `list_display`, `search_fields`, `list_filter` pour une liste exploitable
- [ ] Tester sur `/admin/`

| Piège | Symptôme / solution |
| ------------------------------------------ | ----------------------------------------- |
| Modèle absent de l'admin | pas enregistré dans `admin.py` |
| Lignes affichées `Customer object (1)` | `__str__` manquant sur le modèle |
| `Cannot use list_editable ...` | un champ est à la fois éditable et lien (`list_display_links`) |
| Accès `/admin/` refusé | l'utilisateur n'a pas `is_staff=True` |
| `no such table: auth_user` | `migrate` oublié |
| Modèle modifié mais champ absent | `makemigrations` + `migrate` oubliés |
