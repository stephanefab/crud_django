# Documentation Django — Les modèles & l'ORM

> Mémo sur les modèles Django : définition, migrations, opérations (CRUD), requêtes et astuces.
> Basé sur **Django 6.0**.

---

## Sommaire

1. [C'est quoi l'ORM ?](#1-cest-quoi-lorm-)
2. [Définir un modèle](#2-définir-un-modèle)
3. [Les types de champs](#3-les-types-de-champs)
4. [Les migrations](#4-les-migrations)
5. [Le shell Django (pour tester)](#5-le-shell-django-pour-tester)
6. [CRUD : créer, lire, modifier, supprimer](#6-crud--créer-lire-modifier-supprimer)
7. [Les QuerySets : filtrer et trier](#7-les-querysets--filtrer-et-trier)
8. [Les lookups (`__gt`, `__contains`…)](#8-les-lookups-__gt-__contains)
9. [Les relations (ForeignKey, M2M…)](#9-les-relations-foreignkey-m2m)
10. [Options `Meta` et `__str__`](#10-options-meta-et-__str__)
11. [Astuces & pièges](#11-astuces--pièges)
12. [Modèles avancés (aller plus loin)](#12-modèles-avancés-aller-plus-loin)
13. [La pagination](#13-la-pagination)
14. [Recherche + pagination combinées](#14-recherche--pagination-combinées)
15. [Mémo express](#15-mémo-express)

---

## 1. C'est quoi l'ORM ?

**ORM** = *Object-Relational Mapping* (mapping objet-relationnel).

C'est un **traducteur** entre ton code Python et la base de données SQL. Au lieu d'écrire du SQL à la main, tu manipules des **objets Python**, et Django génère le SQL pour toi.

```
        TON CODE PYTHON                      CE QUE DJANGO ENVOIE EN BASE
  Company.objects.filter(actif=True)   →   SELECT * FROM company WHERE actif = 1;
  c = Company(nom="ACME"); c.save()     →   INSERT INTO company (nom) VALUES ('ACME');
  c.delete()                            →   DELETE FROM company WHERE id = 1;
```

**Pourquoi c'est utile :**

| Sans ORM (SQL brut) | Avec l'ORM Django |
| ------------------- | ----------------- |
| Écrire du SQL à la main | Manipuler des objets Python |
| Dépend de la base (MySQL, PostgreSQL…) | **Même code** quelle que soit la base |
| Risque d'injection SQL | Protégé automatiquement |
| Conversion manuelle des types | Types Python natifs (date, int…) |

> En résumé : **un modèle = une table**, **un objet = une ligne**, **un attribut = une colonne**. Tu penses en objets, l'ORM s'occupe du SQL.

---

## 2. Définir un modèle

Un modèle est une classe Python qui hérite de `models.Model`. Chaque attribut = une colonne.

`company/models.py` :

```python
from django.db import models

class Company(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    actif = models.BooleanField(default=True)
    creee_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom
```

Django ajoute **automatiquement** une colonne `id` (clé primaire auto-incrémentée) — tu n'as pas à la déclarer.

Cette classe correspond à une table SQL :

```
Table company_company
┌────┬──────────┬──────────────┬───────┬─────────────────────┐
│ id │ nom      │ email        │ actif │ creee_le            │
├────┼──────────┼──────────────┼───────┼─────────────────────┤
│ 1  │ ACME     │ a@acme.com   │ 1     │ 2026-06-02 14:30:00 │
└────┴──────────┴──────────────┴───────┴─────────────────────┘
```

---

## 3. Les types de champs

| Champ Django            | Pour stocker…                       | Options fréquentes              |
| ----------------------- | ----------------------------------- | ------------------------------- |
| `CharField`             | texte court (titre, nom)            | `max_length` (obligatoire)      |
| `TextField`             | texte long (description)            | —                               |
| `IntegerField`          | nombre entier                       | `default`                       |
| `FloatField` / `DecimalField` | nombre décimal                | `max_digits`, `decimal_places`  |
| `BooleanField`          | vrai / faux                         | `default=True`                  |
| `DateField`             | date                                | `auto_now_add`, `auto_now`      |
| `DateTimeField`         | date + heure                        | `auto_now_add`, `auto_now`      |
| `EmailField`            | email (avec validation)             | `blank=True`                    |
| `URLField`              | URL                                 | —                               |
| `SlugField`             | identifiant URL (`mon-titre`)       | `unique=True`                   |
| `ImageField` / `FileField` | image / fichier                  | `upload_to="dossier/"`          |
| `ForeignKey`            | lien vers un autre modèle (1-N)     | `on_delete`                     |

### Options communes à (presque) tous les champs

| Option            | Effet                                                        |
| ----------------- | ----------------------------------------------------------- |
| `null=True`       | autorise `NULL` **en base** (niveau SQL)                    |
| `blank=True`      | autorise le champ vide **dans les formulaires** (validation) |
| `default=…`       | valeur par défaut                                           |
| `unique=True`     | valeur unique dans toute la table                          |
| `choices=…`       | liste de valeurs autorisées (menu déroulant)               |
| `verbose_name=…`  | nom lisible affiché dans l'admin                           |

> ⚠️ **`null` vs `blank`** — confusion classique :
> - `null` = base de données (la colonne peut être vide)
> - `blank` = validation des formulaires (le champ n'est pas obligatoire)
>
> Pour un champ texte optionnel, on met **`blank=True`** seul (un texte vide `""` suffit, pas besoin de `null`). Pour une date/nombre optionnel, on met **`null=True, blank=True`**.

### Les `choices`

```python
class Company(models.Model):
    STATUT_CHOICES = [
        ("active", "Active"),
        ("pause", "En pause"),
        ("fermee", "Fermée"),
    ]
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="active")
```

En base on stocke `"active"`, mais l'admin et les formulaires affichent `"Active"`.

---

## 4. Les migrations

Une **migration** = un fichier qui décrit un changement de structure de la base. C'est le pont entre ton `models.py` et la vraie table SQL.

**Le cycle à retenir** (à refaire après CHAQUE modif de `models.py`) :

```bash
# 1. Générer le fichier de migration à partir des modèles
python manage.py makemigrations

# 2. Appliquer la migration (crée/modifie réellement les tables)
python manage.py migrate
```

```
models.py  ──makemigrations──►  fichier migration  ──migrate──►  table SQL
(ton code)                      (company/migrations/)            (db.sqlite3)
```

Commandes utiles :

```bash
python manage.py showmigrations      # liste l'état des migrations
python manage.py sqlmigrate company 0001   # voir le SQL généré (sans l'exécuter)
```

> ⚠️ Erreur fréquente : modifier `models.py` puis oublier `makemigrations` + `migrate`. La base ne change pas toute seule → tu obtiens des erreurs « no such column ».

---

## 5. Le shell Django (pour tester)

Pour jouer avec l'ORM **sans créer de vue**, ouvre un shell interactif :

```bash
python manage.py shell
```

Puis :

```python
>>> from company.models import Company
>>> Company.objects.create(nom="ACME")
>>> Company.objects.all()
<QuerySet [<Company: ACME>]>
```

> 💡 C'est l'endroit idéal pour apprendre l'ORM : tu testes une requête, tu vois le résultat immédiatement.

---

## 6. CRUD : créer, lire, modifier, supprimer

On passe toujours par le **manager** `.objects` (la « porte d'entrée » vers la table).

### CREATE — créer

```python
# Méthode 1 : instancier puis sauvegarder
c = Company(nom="ACME", email="a@acme.com")
c.save()

# Méthode 2 : create() fait les deux d'un coup
c = Company.objects.create(nom="ACME", email="a@acme.com")
```

### READ — lire

```python
Company.objects.all()                 # tous → QuerySet
Company.objects.get(id=1)             # UN seul objet (par clé unique)
Company.objects.get(nom="ACME")       # UN seul (erreur si 0 ou plusieurs)
Company.objects.filter(actif=True)    # plusieurs → QuerySet
Company.objects.first()               # le premier (ou None)
Company.objects.count()               # nombre de lignes
Company.objects.exists()              # True/False
```

> ⚠️ `get()` lève une exception s'il trouve **0** (`DoesNotExist`) ou **plusieurs** (`MultipleObjectsReturned`) résultats. Pour « 0 ou 1 sans planter », utilise `filter().first()`.

### UPDATE — modifier

```python
# Un objet : modifier un attribut puis save()
c = Company.objects.get(id=1)
c.nom = "ACME Corp"
c.save()

# Plusieurs d'un coup (plus efficace, un seul SQL)
Company.objects.filter(actif=False).update(actif=True)
```

### DELETE — supprimer

```python
c = Company.objects.get(id=1)
c.delete()                              # un objet

Company.objects.filter(actif=False).delete()   # plusieurs
```

---

## 7. Les QuerySets : filtrer et trier

Un **QuerySet** = une liste « paresseuse » de résultats. Tu peux l'enchaîner comme des filtres.

```python
Company.objects.filter(actif=True)              # garde ceux qui matchent
Company.objects.exclude(actif=True)             # garde ceux qui NE matchent PAS
Company.objects.filter(actif=True).exclude(nom="ACME")   # enchaînement

# Tri
Company.objects.order_by("nom")        # croissant (A→Z)
Company.objects.order_by("-creee_le")  # décroissant (le "-" inverse)

# Limiter (slicing comme une liste Python)
Company.objects.all()[:5]              # les 5 premiers

# Récupérer certaines colonnes seulement
Company.objects.values("nom", "email")        # liste de dicts
Company.objects.values_list("nom", flat=True) # liste de valeurs ["ACME", ...]
```

### Lazy (paresseux) : un point clé de performance

Un QuerySet **ne touche PAS la base** tant que tu ne lis pas vraiment les données. La requête SQL ne part qu'au moment où tu **itères**, fais un `len()`, un `list()`, etc.

```python
qs = Company.objects.filter(actif=True)   # ← AUCUN SQL ici
qs = qs.order_by("nom")                   # ← toujours rien
for c in qs:                              # ← MAINTENANT le SQL part
    print(c.nom)
```

> Avantage : tu peux construire ta requête en plusieurs morceaux sans frapper la base à chaque ligne.

### Combiner des conditions (ET / OU)

```python
# ET : plusieurs arguments = tous doivent matcher
Company.objects.filter(actif=True, nom="ACME")

# OU : avec des objets Q
from django.db.models import Q
Company.objects.filter(Q(nom="ACME") | Q(nom="Globex"))   # | = OU
Company.objects.filter(Q(actif=True) & ~Q(nom="ACME"))    # & = ET, ~ = NON
```

---

## 8. Les lookups (`__gt`, `__contains`…)

Pour des filtres plus fins que l'égalité, on ajoute `__lookup` au nom du champ (double underscore).

```python
Company.objects.filter(nom__contains="AC")       # contient "AC"
Company.objects.filter(nom__icontains="ac")      # idem, insensible à la casse
Company.objects.filter(nom__startswith="A")      # commence par
Company.objects.filter(nom__endswith="E")        # finit par
Company.objects.filter(id__gt=5)                 # > 5
Company.objects.filter(id__gte=5)                # >= 5
Company.objects.filter(id__lt=5)                 # < 5
Company.objects.filter(id__lte=5)                # <= 5
Company.objects.filter(id__in=[1, 2, 3])         # dans la liste
Company.objects.filter(email__isnull=True)       # est NULL
Company.objects.filter(creee_le__year=2026)      # année = 2026
Company.objects.filter(creee_le__date=date(2026, 6, 2))  # un jour précis
```

| Lookup        | Sens                          |
| ------------- | ----------------------------- |
| `__gt` / `__gte` | plus grand (que / ou égal)  |
| `__lt` / `__lte` | plus petit (que / ou égal)  |
| `__contains`  | contient (sensible casse)     |
| `__icontains` | contient (insensible casse)   |
| `__startswith` / `__endswith` | commence / finit par |
| `__in`        | dans une liste                |
| `__isnull`    | est NULL (True/False)         |
| `__year` / `__month` / `__day` | partie d'une date |
| `__range`     | entre deux valeurs            |

---

## 9. Les relations (ForeignKey, M2M…)

### ForeignKey — relation 1 à N (un-à-plusieurs)

« Une entreprise a plusieurs employés ; un employé appartient à une entreprise. »

```python
class Company(models.Model):
    nom = models.CharField(max_length=100)

class Employe(models.Model):
    nom = models.CharField(max_length=100)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,       # si l'entreprise est supprimée → employés supprimés
        related_name="employes",         # accès inverse : company.employes.all()
    )
```

Utilisation :

```python
emp = Employe.objects.get(id=1)
emp.company.nom                  # accès direct → l'entreprise de l'employé

comp = Company.objects.get(id=1)
comp.employes.all()              # accès inverse → tous les employés (via related_name)
```

**Valeurs de `on_delete` (obligatoire) :**

| Valeur               | Si l'objet lié est supprimé…                |
| -------------------- | ------------------------------------------- |
| `CASCADE`            | supprime aussi les objets enfants           |
| `PROTECT`            | empêche la suppression (erreur)             |
| `SET_NULL`           | met la relation à NULL (besoin `null=True`) |
| `SET_DEFAULT`        | met la valeur par défaut                    |

### ManyToManyField — relation N à N

« Un projet a plusieurs entreprises, une entreprise est sur plusieurs projets. »

```python
class Projet(models.Model):
    nom = models.CharField(max_length=100)
    companies = models.ManyToManyField(Company, related_name="projets")
```

```python
projet.companies.add(comp)       # lier
projet.companies.remove(comp)    # délier
projet.companies.all()           # lister
comp.projets.all()               # accès inverse
```

### OneToOneField — relation 1 à 1

Un profil par utilisateur, par exemple : `models.OneToOneField(User, on_delete=models.CASCADE)`.

### Éviter le piège N+1 : `select_related` / `prefetch_related`

Accéder à une relation dans une boucle = une requête SQL **par objet** (lent). Pré-charge les relations :

```python
# ❌ Lent : 1 requête pour les employés + 1 par employé pour son entreprise
for e in Employe.objects.all():
    print(e.company.nom)

# ✅ Rapide : tout en 1 requête (JOIN)
for e in Employe.objects.select_related("company"):
    print(e.company.nom)
```

- `select_related` → pour `ForeignKey` / `OneToOne` (fait un JOIN)
- `prefetch_related` → pour `ManyToMany` / relations inverses

---

## 10. Options `Meta` et `__str__`

### `__str__` — l'affichage lisible

Sans lui, un objet s'affiche `<Company: Company object (1)>`. Avec, tu choisis le texte (utilisé partout : admin, shell, templates) :

```python
def __str__(self):
    return self.nom
```

### `class Meta` — réglages du modèle

```python
class Company(models.Model):
    nom = models.CharField(max_length=100)
    creee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creee_le"]            # tri par défaut de tous les QuerySets
        verbose_name = "Entreprise"          # nom affiché dans l'admin
        verbose_name_plural = "Entreprises"
        unique_together = ["nom", "email"]   # combinaison unique
```

`ordering` est pratique : tous tes `.all()` / `.filter()` seront triés automatiquement.

---

## 11. Astuces & pièges

### get_object_or_404 — pour les vues

Dans une vue, au lieu de gérer l'exception `DoesNotExist`, utilise ce raccourci qui renvoie une **page 404** propre si l'objet n'existe pas :

```python
from django.shortcuts import get_object_or_404

def detail_view(request, id):
    company = get_object_or_404(Company, id=id)
    return render(request, "company/detail.html", {"company": company})
```

### get_or_create / update_or_create

```python
# Récupère l'objet, ou le crée s'il n'existe pas
obj, cree = Company.objects.get_or_create(nom="ACME")
# cree = True si nouvel objet, False s'il existait déjà
```

### Agrégations (compter, sommer, moyenne)

```python
from django.db.models import Count, Sum, Avg, Max, Min

Company.objects.count()                          # nombre total
Company.objects.aggregate(Avg("id"))             # {'id__avg': 3.5}
Company.objects.aggregate(total=Sum("id"))       # {'total': 21}

# annotate : ajouter un calcul par objet (ex: nb d'employés par entreprise)
Company.objects.annotate(nb=Count("employes"))
# chaque company a maintenant un attribut .nb
```

### Voir le SQL généré (debug)

```python
qs = Company.objects.filter(actif=True)
print(qs.query)         # affiche le SQL réel
```

### Les pièges les plus courants

| Piège | Solution |
| ----- | -------- |
| Modifier `models.py` sans migrer | `makemigrations` + `migrate` |
| `get()` qui plante (0 ou N résultats) | `filter().first()` |
| Confondre `null` (base) et `blank` (formulaire) | texte → `blank` seul ; date/nombre → les deux |
| Oublier `on_delete` sur un `ForeignKey` | obligatoire en Django moderne |
| Boucle qui fait N+1 requêtes | `select_related` / `prefetch_related` |
| Objet affiché `Company object (1)` | définir `__str__` |

---

## 12. Modèles avancés (aller plus loin)

Une fois les bases en place, voici les outils qui font la différence sur un vrai projet.

### 12.1 `choices` modernes : `TextChoices` / `IntegerChoices`

La forme « liste de tuples » (section 3) fonctionne, mais depuis Django 3 on préfère les classes d'énumération, plus lisibles et réutilisables :

```python
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING   = "pending",   "En attente"
        SHIPPED   = "shipped",   "Expédiée"
        DELIVERED = "delivered", "Livrée"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
```

Utilisation :

```python
order.status                       # "pending"  (valeur stockée)
order.get_status_display()         # "En attente"  (libellé lisible — méthode auto)
Order.Status.SHIPPED               # "shipped"   (référence sans "magic string")
Order.objects.filter(status=Order.Status.DELIVERED)
```

> 🧠 Django génère **automatiquement** une méthode `get_<champ>_display()` pour **tout** champ avec `choices`. Pour les valeurs numériques, utilise `IntegerChoices` à la place.

### 12.2 La clé primaire (`pk`) en profondeur

Django ajoute une clé primaire auto (`id`) si tu n'en déclares pas. `pk` en est l'**alias universel** (`obj.pk` == `obj.id` par défaut).

```python
# Clé primaire personnalisée
reference = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
code = models.CharField(max_length=10, primary_key=True)   # PK non numérique
```

Le **type** de l'`id` auto est fixé globalement dans `settings.py` :

```python
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"   # le défaut moderne (grands entiers)
```

> 💡 Dans le code générique, préfère **`pk`** à `id` (`get_object_or_404(Customer, pk=...)`) : ça marche même si la clé primaire n'est pas un champ nommé `id`.

### 12.3 Timestamps : `auto_now_add` vs `auto_now`

```python
created_at = models.DateTimeField(auto_now_add=True)   # figé à la CRÉATION
updated_at = models.DateTimeField(auto_now=True)       # MAJ à CHAQUE save()
```

| Option | Quand c'est écrit | Modifiable ? |
| ------------- | ------------------ | ------------ |
| `auto_now_add` | une fois, à la création | non |
| `auto_now` | à chaque `save()` | non |

> ⚠️ `auto_now` n'est **pas** déclenché par un `.update()` en masse (qui ne passe pas par `save()`). Idem pour `default=...` : il ne s'applique qu'à la création.

### 12.4 Validators et validation

On attache des **validateurs** à un champ pour contraindre sa valeur :

```python
from django.core.validators import MinValueValidator, RegexValidator

age = models.PositiveIntegerField(validators=[MinValueValidator(18)])
phone = models.CharField(
    max_length=15,
    validators=[RegexValidator(r"^\+?\d{9,15}$", "Numéro invalide")],
)
```

Et une validation **inter-champs** via `clean()` sur le modèle :

```python
from django.core.exceptions import ValidationError

def clean(self):
    if self.first_name == self.last_name:
        raise ValidationError("Le prénom et le nom ne peuvent pas être identiques.")
```

> ⚠️ Rappel crucial : `create()` et `save()` **ne valident pas**. Seuls `full_clean()`, les `ModelForm` et l'admin déclenchent `clean()` et les validators. (Voir [DJANGO.md section 10.10](DJANGO.md).)

### 12.5 Méthodes, propriétés et surcharge de `save()`

Un modèle est une classe : on y met de la **logique métier**.

```python
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name  = models.CharField(max_length=100)
    email      = models.EmailField()

    @property
    def full_name(self):                      # attribut calculé : customer.full_name
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):               # URL canonique de l'objet
        from django.urls import reverse
        return reverse("company.customerDetail", args=[self.pk])

    def save(self, *args, **kwargs):          # normaliser avant d'enregistrer
        self.email = self.email.lower().strip()
        super().save(*args, **kwargs)         # ← ne JAMAIS oublier l'appel parent
```

### 12.6 Managers et QuerySets personnalisés

Pour réutiliser une requête fréquente, on crée un **manager** ou un **QuerySet** personnalisé au lieu de répéter le même `filter()` partout.

```python
class CustomerQuerySet(models.QuerySet):
    def actifs(self):
        return self.filter(is_active=True)

class Customer(models.Model):
    is_active = models.BooleanField(default=True)
    objects = CustomerQuerySet.as_manager()

# usage — chaînable comme n'importe quel QuerySet :
Customer.objects.actifs()
Customer.objects.actifs().order_by("last_name")
```

> 💡 `as_manager()` transforme un QuerySet en manager : tes méthodes deviennent disponibles **et** restent chaînables.

### 12.7 `F()` : opérer sans charger en Python

`F()` référence la valeur d'un champ **directement en base** — plus rapide et sans *race condition* :

```python
from django.db.models import F

# ❌ risqué (lecture-modification-écriture en Python)
o = Order.objects.get(pk=1); o.amount += 10; o.save()

# ✅ atomique, fait par la base
Order.objects.filter(pk=1).update(amount=F("amount") + 10)
Order.objects.update(amount=F("amount") * 1.2)   # +20 % à tout le monde
```

### 12.8 Héritage de modèles : classe de base abstraite

Pour factoriser des champs communs (timestamps…) sans créer de table pour la base :

```python
class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True            # ← pas de table pour TimeStamped

class Customer(TimeStamped):        # hérite des deux champs
    first_name = models.CharField(max_length=100)
```

`Customer` aura `created_at` et `updated_at` sans qu'on les réécrive. (Il existe aussi l'héritage *multi-table* et les *proxy models*, plus rares.)

### 12.9 `ManyToMany` avec données sur la relation (`through`)

Une `ManyToManyField` simple ne stocke **que** le lien. Pour ajouter des infos sur la relation (quantité, date…), on déclare le modèle de liaison soi-même :

```python
class Order(models.Model):
    products = models.ManyToManyField("Product", through="OrderLine")

class OrderLine(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE)
    product  = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)   # ← donnée sur la relation
```

> Avec `through`, on crée les liens via le modèle intermédiaire (`OrderLine.objects.create(...)`), plus via `.add()`.

### 12.10 Opérations en masse et transactions

```python
# Insérer/mettre à jour des milliers de lignes en une requête
Customer.objects.bulk_create([Customer(first_name=f"C{i}") for i in range(1000)])
Customer.objects.bulk_update(liste, ["phone"])

# Tout-ou-rien : si une erreur survient, AUCUNE écriture n'est gardée
from django.db import transaction

with transaction.atomic():
    order = Order.objects.create(customer=c, amount=100)
    OrderLine.objects.create(order=order, product=p, quantity=2)
    # si ça plante ici → les deux créations sont annulées (rollback)
```

> ⚠️ `bulk_create`/`bulk_update` **ne déclenchent pas** `save()` ni les signaux : à utiliser pour la performance, pas quand tu dépends d'une logique dans `save()`.

---

## 13. La pagination

Dès qu'une liste devient longue (50, 1000 entreprises…), on la **découpe en pages**. Django fournit la classe `Paginator` pour ça.

### Principe

```
QuerySet complet (1000 objets)
        │  Paginator(qs, 10)  →  découpe en pages de 10
        ▼
Page 1 [1-10]   Page 2 [11-20]   Page 3 [21-30]  ...
```

### Dans la vue

```python
from django.core.paginator import Paginator

def liste_view(request):
    companies = Company.objects.all()           # le QuerySet complet

    paginator = Paginator(companies, 10)         # 10 par page
    numero_page = request.GET.get("page")        # ?page=2 dans l'URL
    page = paginator.get_page(numero_page)       # l'objet Page demandé

    return render(request, "company/liste.html", {"page": page})
```

> 💡 Utilise **`get_page()`** plutôt que `page()` : il gère tout seul les cas d'erreur (page inexistante, `?page=abc`…) en renvoyant une page valide, sans planter.

### Dans le template

L'objet `page` est **itérable** (il contient les objets de la page courante) et porte les infos de navigation :

```django
<ul>
{% for company in page %}
    <li>{{ company.nom }}</li>
{% endfor %}
</ul>

{# Navigation #}
{% if page.has_previous %}
    <a href="?page={{ page.previous_page_number }}">Précédent</a>
{% endif %}

<span>Page {{ page.number }} sur {{ page.paginator.num_pages }}</span>

{% if page.has_next %}
    <a href="?page={{ page.next_page_number }}">Suivant</a>
{% endif %}
```

### Les attributs/méthodes utiles de `page`

| Élément                        | Donne…                                  |
| ------------------------------ | --------------------------------------- |
| `page` (en boucle)             | les objets de la page courante          |
| `page.number`                  | numéro de la page actuelle              |
| `page.has_next`                | True s'il y a une page suivante         |
| `page.has_previous`            | True s'il y a une page précédente       |
| `page.next_page_number`        | numéro de la page suivante              |
| `page.previous_page_number`    | numéro de la page précédente            |
| `page.paginator.num_pages`     | nombre total de pages                   |
| `page.paginator.count`         | nombre total d'objets                   |
| `page.paginator.page_range`    | `range(1, n+1)` → pour lister les pages |

### Version Bootstrap (jolie barre de pagination)

Bootstrap fournit un composant `pagination` clé en main :

```django
<nav aria-label="Pagination">
    <ul class="pagination justify-content-center">

        {# Bouton Précédent #}
        <li class="page-item {% if not page.has_previous %}disabled{% endif %}">
            <a class="page-link"
               href="{% if page.has_previous %}?page={{ page.previous_page_number }}{% else %}#{% endif %}">
               Précédent
            </a>
        </li>

        {# Numéros de page #}
        {% for num in page.paginator.page_range %}
            <li class="page-item {% if num == page.number %}active{% endif %}">
                <a class="page-link" href="?page={{ num }}">{{ num }}</a>
            </li>
        {% endfor %}

        {# Bouton Suivant #}
        <li class="page-item {% if not page.has_next %}disabled{% endif %}">
            <a class="page-link"
               href="{% if page.has_next %}?page={{ page.next_page_number }}{% else %}#{% endif %}">
               Suivant
            </a>
        </li>

    </ul>
</nav>
```

Classes Bootstrap utilisées : `pagination` (la barre), `page-item` (chaque case), `page-link` (le lien), `active` (page courante), `disabled` (bouton grisé).

### Astuces pagination

- **Garde les filtres dans l'URL** : si tu as une recherche `?q=acme`, le lien de page doit devenir `?page=2&q={{ request.GET.q }}`, sinon le filtre est perdu en changeant de page.
- **Beaucoup de pages ?** Plutôt que d'afficher 200 numéros, affiche seulement quelques pages autour de la courante (`page.number|add:"-2"` … ) ou installe `django-bootstrap-pagination` / un *template tag* maison.
- **Trie toujours ton QuerySet** (`order_by` ou `Meta.ordering`) avant de paginer : sans ordre stable, un même objet peut apparaître sur deux pages.
- La pagination reste **lazy** : Django ne charge en base que les objets de la page demandée (avec `LIMIT`/`OFFSET`), pas les 1000.

---

## 14. Recherche + pagination combinées

Le piège : tu fais une recherche `?name=fabien`, tu cliques sur « page 2 »… et le lien `?page=2` **écrase** `name` → la recherche est perdue, la page 2 affiche tout. Voici comment faire proprement.

### Le problème en image

```
Recherche :  ?name=fabien          → 30 résultats, page 1 OK
Clic page 2 : ?page=2              → ⚠️ name a disparu ! → 1000 résultats
Ce qu'on veut : ?name=fabien&page=2 → page 2 DES résultats filtrés ✅
```

### Dans la vue — lire le paramètre et filtrer

```python
from django.core.paginator import Paginator

def liste_view(request):
    name = request.GET.get("name", "")        # "" si absent → pas de recherche

    companies = Company.objects.all().order_by("nom")   # trier AVANT de paginer
    if name:                                   # filtre seulement si on a tapé qqch
        companies = companies.filter(nom__icontains=name)

    paginator = Paginator(companies, 10)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "company/liste.html", {
        "page": page,
        "name": name,        # on renvoie la recherche au template
    })
```

Points clés :
- `request.GET.get("name", "")` → récupère `?name=...`, avec `""` par défaut (jamais de plantage).
- `if name:` → si la recherche est vide, on ne filtre pas (on montre tout).
- `nom__icontains` → recherche partielle insensible à la casse (« fab » trouve « Fabien »).
- On **renvoie `name`** au template pour deux raisons : pré-remplir le champ ET reconstruire les liens de page.

### Dans le template — le champ de recherche

```django
<form method="get">
    <input type="text" name="name" value="{{ name }}" placeholder="Rechercher…"
           class="form-control">
    <button type="submit" class="btn btn-primary">Chercher</button>
</form>
```

- **`method="get"`** (pas `post`) → la recherche apparaît dans l'URL (`?name=fabien`), donc partageable et compatible pagination.
- **`value="{{ name }}"`** → le champ reste rempli après la recherche (sinon il se vide à chaque fois).

### La clé : conserver `name` dans les liens de pagination

Il suffit d'ajouter `&name={{ name }}` à **chaque** lien de page :

```django
<ul class="pagination justify-content-center">
    <li class="page-item {% if not page.has_previous %}disabled{% endif %}">
        <a class="page-link"
           href="?page={{ page.previous_page_number }}&name={{ name }}">Précédent</a>
    </li>

    {% for num in page.paginator.page_range %}
        <li class="page-item {% if num == page.number %}active{% endif %}">
            <a class="page-link" href="?page={{ num }}&name={{ name }}">{{ num }}</a>
        </li>
    {% endfor %}

    <li class="page-item {% if not page.has_next %}disabled{% endif %}">
        <a class="page-link"
           href="?page={{ page.next_page_number }}&name={{ name }}">Suivant</a>
    </li>
</ul>
```

> 👉 La seule chose à retenir : partout où tu mets `?page=…`, ajoute `&name={{ name }}`.

### Astuce pro : conserver TOUS les paramètres automatiquement

Si tu as plusieurs filtres (`name`, `statut`, `tri`…), recopier `&name=…&statut=…` partout devient pénible et fragile. La solution propre est un *template tag* qui réécrit la querystring en gardant l'existant. Crée `company/templatetags/url_tools.py` :

```python
from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()      # copie tous les paramètres actuels
    for key, value in kwargs.items():
        query[key] = value                       # remplace/ajoute ceux qu'on passe
    return query.urlencode()                     # → "name=fabien&page=2"
```

(crée aussi un fichier vide `company/templatetags/__init__.py`)

Puis dans le template :

```django
{% load url_tools %}

<a class="page-link" href="?{% url_replace page=num %}">{{ num }}</a>
```

`url_replace page=num` garde `name`, `statut`, etc. tels quels et ne change que `page`. **Plus aucun filtre perdu, quel que soit le nombre de paramètres.**

> ⚠️ Pour que `context["request"]` existe, il faut le context processor `django.template.context_processors.request` — il est **déjà présent** par défaut dans `settings.py` (`TEMPLATES → OPTIONS → context_processors`).

### Récap des règles anti-casse

| Règle | Pourquoi |
| ----- | -------- |
| `method="get"` sur le formulaire | la recherche va dans l'URL → compatible pagination |
| `value="{{ name }}"` sur l'input | le champ reste rempli après recherche |
| `request.GET.get("name", "")` | pas de plantage si le paramètre est absent |
| `order_by` avant `Paginator` | pas de doublons entre pages |
| `&name={{ name }}` (ou `url_replace`) sur chaque lien de page | la recherche survit au changement de page |

---

## 15. Mémo express

```
L'ORM
  modèle = table · objet = ligne · attribut = colonne
  on parle Python, Django génère le SQL

CYCLE APRÈS CHAQUE MODIF DE models.py
  makemigrations  →  migrate

CRUD (via .objects)
  create  : Company.objects.create(nom="X")  /  obj.save()
  read    : .all() .get(id=1) .filter(...) .first() .count()
  update  : obj.nom="Y"; obj.save()  /  .filter(...).update(...)
  delete  : obj.delete()  /  .filter(...).delete()

REQUÊTES
  .filter() .exclude() .order_by("-champ") [:5]
  ET : filter(a=1, b=2)   OU : filter(Q(a=1) | Q(b=2))
  lazy : le SQL ne part qu'à l'itération

LOOKUPS
  __gt __lt __gte __lte · __contains __icontains
  __startswith __in __isnull __year __range

RELATIONS
  ForeignKey(Model, on_delete=CASCADE, related_name="x")  ← 1-N
  ManyToManyField(Model)                                  ← N-N
  perf : select_related (FK) / prefetch_related (M2M)

ASTUCES
  get_object_or_404 · get_or_create · annotate/aggregate
  __str__ pour l'affichage · Meta.ordering pour le tri
  test rapide : python manage.py shell

PAGINATION
  vue      : Paginator(qs, 10) ; page = paginator.get_page(request.GET.get("page"))
  template : boucle sur {{ page }} ; page.has_next / .next_page_number
             page.number / page.paginator.num_pages / .page_range
  bootstrap: <ul class="pagination"> page-item page-link active disabled
  garder les filtres : ?page=2&q={{ request.GET.q }}
  toujours order_by avant de paginer

RECHERCHE + PAGINATION (sans casser)
  vue      : name = request.GET.get("name","") ; if name: qs.filter(nom__icontains=name)
  form     : method="get" + <input name="name" value="{{ name }}">
  liens    : href="?page={{ num }}&name={{ name }}"   ← garder name partout
  pro      : {% url_replace page=num %} → conserve TOUS les paramètres
```

> 📚 Référence officielle : https://docs.djangoproject.com/en/6.0/topics/db/queries/
