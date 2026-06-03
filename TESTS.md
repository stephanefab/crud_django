# Documentation Django — Les tests

> Mémo sur les tests automatisés dans Django : tester les modèles, les vues, les formulaires, l'authentification, et mesurer la couverture.
> Basé sur **Django 6.0** et le projet `company` (modèle `Customer`, `CustomerForm`, vues CRUD).
> Voir aussi : [DJANGO.md](DJANGO.md) (vues, URLs), [MODELS.md](MODELS.md) (modèles & ORM).

---

## Sommaire

1. [Pourquoi tester ? Les types de tests](#1-pourquoi-tester--les-types-de-tests)
2. [Le test runner de Django](#2-le-test-runner-de-django)
3. [Anatomie d'un test](#3-anatomie-dun-test)
4. [Tester un modèle](#4-tester-un-modèle)
5. [Tester une vue (le `Client`)](#5-tester-une-vue-le-client)
6. [Tester un formulaire](#6-tester-un-formulaire)
7. [La base de test & l'isolation](#7-la-base-de-test--lisolation)
8. [Données de test : `setUpTestData`, fixtures, factories](#8-données-de-test--setuptestdata-fixtures-factories)
9. [Tester l'authentification & les permissions](#9-tester-lauthentification--les-permissions)
10. [Organiser ses tests](#10-organiser-ses-tests)
11. [La couverture (`coverage`)](#11-la-couverture-coverage)
12. [Alternative : `pytest-django`](#12-alternative--pytest-django)
13. [Bonnes pratiques & pièges](#13-bonnes-pratiques--pièges)
14. [Checklist mémo](#14-checklist-mémo)

---

## 1. Pourquoi tester ? Les types de tests

Un **test automatisé** = du code qui vérifie que ton code fait ce qu'il doit. On le relance à chaque modification → on **détecte les régressions** instantanément, sans cliquer partout à la main.

| Type | Vérifie… | Exemple |
| ------------- | ------------------------------- | ------------------------------ |
| **Unitaire** | une brique isolée | une méthode du modèle `Customer` |
| **Intégration** | plusieurs briques ensemble | une vue (URL → vue → template → réponse) |
| **Fonctionnel / E2E** | le parcours utilisateur complet | remplir un formulaire dans un navigateur (Selenium/Playwright) |

> 🧠 En Django, on écrit surtout des tests **unitaires** (modèles, formulaires) et d'**intégration** (vues via le `Client`). C'est le meilleur rapport effort/bénéfice.

---

## 2. Le test runner de Django

Django embarque un système de tests basé sur le module standard **`unittest`** — **rien à installer**.

**Où écrire les tests :** dans `company/tests.py` (créé par `startapp`), ou dans un package `company/tests/` (voir section 10).

**Lancer les tests :**

```bash
python manage.py test                  # tous les tests du projet
python manage.py test company          # une app
python manage.py test company.tests.CustomerModelTest        # une classe
python manage.py test company.tests.CustomerModelTest.test_str  # un test précis
python manage.py test -v 2             # verbeux (détaille chaque test)
python manage.py test --failfast       # s'arrête au 1er échec
```

> 💡 Django crée **automatiquement une base de données de test** (vide, séparée de ta vraie base), la remplit pendant les tests, puis la **détruit** à la fin. Tes vraies données ne sont **jamais** touchées (voir section 7).

---

## 3. Anatomie d'un test

Un test = une **classe** héritant de `TestCase`, avec des **méthodes** dont le nom commence par `test_`.

```python
# company/tests.py
from django.test import TestCase
from .models import Customer


class CustomerModelTest(TestCase):

    def setUp(self):
        # exécuté AVANT chaque méthode test_ (prépare les données)
        self.customer = Customer.objects.create(
            first_name="Fabien", last_name="Martin",
            email="f@x.com", phone="0600000000", address="Paris",
        )

    def test_str(self):
        # 1. on appelle le code · 2. on AFFIRME le résultat attendu
        self.assertEqual(str(self.customer), "Fabien Martin")
```

**Les assertions les plus utiles** (`self.assert...`) :

| Assertion | Vérifie |
| ----------------------------------- | ------------------------------ |
| `assertEqual(a, b)` | `a == b` |
| `assertTrue(x)` / `assertFalse(x)` | booléen |
| `assertIsNone(x)` | `x is None` |
| `assertIn(a, b)` | `a in b` |
| `assertContains(response, "texte")` | le texte est dans la réponse HTTP |
| `assertRedirects(response, url)` | la réponse redirige vers `url` |
| `assertRaises(Erreur)` | une exception est levée |
| `assertQuerySetEqual(...)` | comparer un QuerySet |

> 🧠 Patron mental **AAA** : **Arrange** (préparer), **Act** (agir), **Assert** (vérifier).

---

## 4. Tester un modèle

On teste la logique métier du modèle : `__str__`, méthodes, propriétés, validation (voir [MODELS.md](MODELS.md)).

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Customer


class CustomerModelTest(TestCase):

    def test_str_retourne_nom_complet(self):
        c = Customer(first_name="Fabien", last_name="Martin")
        self.assertEqual(str(c), "Fabien Martin")

    def test_email_invalide_rejete(self):
        c = Customer(first_name="A", last_name="B", email="pas-un-email",
                     phone="06", address="x")
        with self.assertRaises(ValidationError):
            c.full_clean()          # full_clean() déclenche la validation (cf. MODELS.md)

    def test_creation_en_base(self):
        Customer.objects.create(first_name="A", last_name="B",
                                email="a@b.com", phone="06", address="x")
        self.assertEqual(Customer.objects.count(), 1)
```

---

## 5. Tester une vue (le `Client`)

Django fournit un **client HTTP de test** (`self.client`) qui simule un navigateur : il appelle tes URLs, suit les redirections, et te donne la réponse à inspecter — **sans lancer de serveur**.

```python
from django.test import TestCase
from django.urls import reverse
from .models import Customer


class CustomerViewsTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Fabien", last_name="Martin",
            email="f@x.com", phone="0600000000", address="Paris",
        )

    # --- READ : la liste ---
    def test_liste_affiche_les_clients(self):
        response = self.client.get(reverse("company.customers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Martin")          # le client apparaît
        self.assertTemplateUsed(response, "company/customers.html")

    # --- CREATE : POST valide → redirige + crée l'objet ---
    def test_creation_client(self):
        data = {"first_name": "Alice", "last_name": "Durand",
                "email": "a@d.com", "phone": "0611111111", "address": "Lyon"}
        response = self.client.post(reverse("company.customerCreate"), data)
        self.assertRedirects(response, reverse("company.customers"))
        self.assertTrue(Customer.objects.filter(last_name="Durand").exists())

    # --- CREATE : POST invalide → reste sur la page, ne crée rien ---
    def test_creation_invalide(self):
        response = self.client.post(reverse("company.customerCreate"), {})  # tout vide
        self.assertEqual(response.status_code, 200)       # pas de redirection
        self.assertEqual(Customer.objects.count(), 1)     # rien créé (juste celui du setUp)

    # --- DELETE : POST supprime ---
    def test_suppression(self):
        url = reverse("company.customerDelete", args=[self.customer.id])
        self.client.post(url)
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())
```

**Les méthodes du `Client` :**

```python
self.client.get(url)                  # requête GET
self.client.post(url, data_dict)      # requête POST (formulaire)
self.client.get(url, follow=True)     # suit les redirections
self.client.login(username=..., password=...)   # se connecter (section 9)
```

**Inspecter la réponse :**

```python
response.status_code        # 200, 302, 404...
response.content            # le HTML brut (bytes)
response.context["page"]    # les variables passées au template
response.redirect_chain     # avec follow=True
```

---

## 6. Tester un formulaire

On teste que le `ModelForm` valide/rejette correctement (voir [DJANGO.md §10.11](DJANGO.md)).

```python
from django.test import TestCase
from .forms import CustomerForm


class CustomerFormTest(TestCase):

    def test_form_valide(self):
        form = CustomerForm(data={
            "first_name": "Fabien", "last_name": "Martin",
            "email": "f@x.com", "phone": "0600000000", "address": "Paris",
        })
        self.assertTrue(form.is_valid())

    def test_champ_obligatoire_manquant(self):
        form = CustomerForm(data={"first_name": "", "last_name": "Martin",
                                  "email": "f@x.com", "phone": "06", "address": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)      # l'erreur porte sur ce champ

    def test_email_invalide(self):
        form = CustomerForm(data={"first_name": "A", "last_name": "B",
                                  "email": "pas-un-email", "phone": "06", "address": "x"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
```

> 🧠 Tester le formulaire **séparément** de la vue est plus rapide et plus précis : tu cibles la validation sans passer par le HTTP.

---

## 7. La base de test & l'isolation

Points essentiels du fonctionnement :

- Django crée une **base de test dédiée** (préfixée `test_`), **vide** au départ — jamais ta vraie base.
- Chaque méthode `test_` s'exécute dans une **transaction annulée à la fin** (`TestCase`) → les tests sont **isolés** : ce qu'un test crée n'existe pas pour le suivant.
- `setUp()` s'exécute **avant chaque** `test_` ; `tearDown()` **après**.

```python
class MonTest(TestCase):
    def setUp(self):        # avant CHAQUE test
        ...
    def tearDown(self):     # après CHAQUE test (souvent inutile, la BD est annulée)
        ...
```

> ⚠️ `TestCase` (transactionnel, rapide) vs `TransactionTestCase` (recrée vraiment les tables, plus lent — utile pour tester `transaction.atomic`, les contraintes BD). Par défaut, utilise **`TestCase`**.

> 💡 Accélérer la suite : `python manage.py test --parallel` (exécute en parallèle) et une BD SQLite en mémoire pour les tests.

---

## 8. Données de test : `setUpTestData`, fixtures, factories

**`setUpTestData`** (recommandé) — crée les données **une seule fois** pour toute la classe (plus rapide que `setUp` qui recrée à chaque test) :

```python
class CustomerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.c1 = Customer.objects.create(first_name="A", last_name="X",
                                         email="a@x.com", phone="06", address="x")
    # les objets sont rechargés proprement pour chaque test
```

**Fixtures** — des données en JSON chargées dans la base de test :

```bash
python manage.py dumpdata company.Customer --indent 2 > company/fixtures/customers.json
```

```python
class CustomerTest(TestCase):
    fixtures = ["customers.json"]      # chargé automatiquement avant les tests
```

**Factories** (`factory_boy`) — générer des objets variés sans tout écrire à la main :

```bash
pip install factory_boy
```

```python
import factory
from .models import Customer

class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer
    first_name = factory.Faker("first_name")
    last_name  = factory.Faker("last_name")
    email      = factory.Faker("email")
    phone      = "0600000000"
    address    = factory.Faker("address")

# dans un test :
CustomerFactory()                 # 1 client aléatoire
CustomerFactory.create_batch(10)  # 10 clients
```

> 👉 `setUpTestData` pour quelques objets fixes ; **factories** dès que tu as besoin de beaucoup d'objets ou de variété.

---

## 9. Tester l'authentification & les permissions

Pour tester des vues protégées (`@login_required`, permissions — voir [AUTH.md](AUTH.md)), on crée un utilisateur et on le connecte.

```python
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class AccesProtegeTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="alice", password="secret123")

    def test_anonyme_redirige_vers_login(self):
        response = self.client.get(reverse("company.customerCreate"))
        self.assertEqual(response.status_code, 302)        # redirigé vers login

    def test_connecte_a_acces(self):
        self.client.login(username="alice", password="secret123")
        response = self.client.get(reverse("company.customerCreate"))
        self.assertEqual(response.status_code, 200)
```

> 💡 `self.client.force_login(self.user)` connecte **sans** vérifier le mot de passe (plus rapide quand le login n'est pas l'objet du test). Pour donner une permission : `user.user_permissions.add(perm)` ou ajouter l'utilisateur à un groupe.

---

## 10. Organiser ses tests

Quand `tests.py` devient gros, remplace-le par un **package** `company/tests/` :

```
company/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_forms.py
    └── test_auth.py
```

> ⚠️ Chaque fichier doit s'appeler `test_*.py` (sinon le runner ne le trouve pas) et le dossier doit contenir `__init__.py`. **Supprime** l'ancien `tests.py` pour éviter le conflit.

**Conventions de nommage** : `test_<ce_qui_est_testé>_<comportement_attendu>` → `test_creation_client_invalide_ne_cree_rien`. Un nom explicite sert de documentation.

---

## 11. La couverture (`coverage`)

La **couverture de code** mesure quel pourcentage de ton code est exécuté par les tests.

```bash
pip install coverage

coverage run --source="." manage.py test     # lance les tests en mesurant
coverage report                              # résumé dans le terminal
coverage html                                # rapport HTML détaillé (htmlcov/index.html)
```

> 🧠 Une couverture élevée (80–90 %) est un bon **indicateur**, pas un but en soi : 100 % de couverture ne garantit pas l'absence de bugs (on peut exécuter une ligne sans vraiment tester son comportement). Vise à couvrir la **logique métier** et les **cas limites**.

Un fichier `.coveragerc` permet d'exclure le bruit :

```ini
[run]
omit = */migrations/*, */tests/*, manage.py, */venv/*, config/*
```

---

## 12. Alternative : `pytest-django`

Beaucoup de projets préfèrent **pytest** (syntaxe plus légère, `assert` natif, fixtures puissantes).

```bash
pip install pytest pytest-django
```

`pytest.ini` (à la racine) :

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
```

Un test pytest = une **fonction** (pas de classe), avec le simple mot-clé `assert` :

```python
import pytest
from company.models import Customer

@pytest.mark.django_db          # ← autorise l'accès à la base de test
def test_str():
    c = Customer(first_name="Fabien", last_name="Martin")
    assert str(c) == "Fabien Martin"

def test_liste(client):         # "client" = fixture fournie par pytest-django
    response = client.get("/company/customers/")
    assert response.status_code == 200
```

```bash
pytest                  # lance tout
pytest company/tests/test_models.py -v
```

| | `manage.py test` (Django) | `pytest-django` |
| ----------- | --------------------------- | ------------------------- |
| Installation | rien (intégré) | `pip install pytest-django` |
| Syntaxe | classes + `self.assert*` | fonctions + `assert` |
| Fixtures | `setUp` / `setUpTestData` | `@pytest.fixture` (réutilisables) |
| Accès BD | automatique (`TestCase`) | `@pytest.mark.django_db` |

> 👉 Le runner intégré suffit largement pour démarrer. `pytest` devient intéressant sur des projets plus gros (fixtures partagées, plugins, paramétrage).

---

## 13. Bonnes pratiques & pièges

- **Un test = une chose** : un comportement vérifié par test, avec un nom explicite.
- **Tester les cas limites** : champ vide, valeur invalide, objet inexistant (404), accès non autorisé.
- **Tester via `reverse(...)`** plutôt que des URLs en dur (résiste aux changements d'URL).
- **Rapide** : `setUpTestData` plutôt que `setUp`, `force_login` plutôt que `login` quand l'auth n'est pas l'objet du test.
- **Indépendant** : ne dépends pas de l'ordre des tests ni de données préexistantes.

| Piège | Conséquence |
| ------------------------------------------ | ----------------------------------------- |
| Fichier de test pas nommé `test_*.py` | le runner ne le trouve pas |
| `tests.py` **et** `tests/` en même temps | conflit d'import |
| Tester sur la vraie base | impossible : Django utilise une base de test isolée |
| URLs en dur (`/company/...`) | tests cassés si l'URL change → `reverse()` |
| `@pytest.mark.django_db` oublié (pytest) | erreur d'accès à la base |
| Couverture = objectif unique | faux sentiment de sécurité |

---

## 14. Checklist mémo

Pour tester une fonctionnalité :

- [ ] Écrire les tests dans `company/tests.py` (ou `company/tests/test_*.py`)
- [ ] Hériter de `TestCase`, méthodes en `test_*`
- [ ] **Modèle** : `__str__`, méthodes, `full_clean()`
- [ ] **Formulaire** : `is_valid()` + `form.errors` (valide / invalide)
- [ ] **Vue** : `self.client.get/post`, `status_code`, `assertContains`, `assertRedirects`
- [ ] **Auth** : `create_user` + `client.login` / `force_login`
- [ ] Lancer : `python manage.py test`
- [ ] (Optionnel) `coverage run ... && coverage report`

```
LANCER
  python manage.py test            # tout
  python manage.py test company    # une app
  python manage.py test -v 2       # verbeux

ASSERTIONS CLÉS
  assertEqual · assertTrue/False · assertContains
  assertRedirects · assertRaises · form.errors

CLIENT HTTP
  self.client.get(reverse("name"))
  self.client.post(url, data) · login / force_login
  response.status_code / .context / .content
```
