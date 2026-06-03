# Documentation Django — Authentification & autorisation

> Mémo sur le système d'auth intégré de Django : se connecter / se déconnecter, protéger des pages, inscription, permissions et groupes.
> Basé sur **Django 6.0** et le projet `company`.
> Voir aussi : [DJANGO.md](DJANGO.md) (vues, URLs, templates), [DJANGO-ADMIN.md](DJANGO-ADMIN.md) (l'admin), [MODELS.md](MODELS.md) (modèles).

---

## Sommaire

1. [Authentification vs autorisation](#1-authentification-vs-autorisation)
2. [Le système d'auth de Django](#2-le-système-dauth-de-django)
3. [Le modèle `User`](#3-le-modèle-user)
4. [Login / Logout (vues intégrées)](#4-login--logout-vues-intégrées)
5. [Les réglages `settings.py`](#5-les-réglages-settingspy)
6. [Inscription (signup)](#6-inscription-signup)
7. [Protéger les vues](#7-protéger-les-vues)
8. [Protéger les templates](#8-protéger-les-templates)
9. [Autorisation : permissions & groupes](#9-autorisation--permissions--groupes)
10. [Custom User model](#10-custom-user-model)
11. [Changer / réinitialiser un mot de passe](#11-changer--réinitialiser-un-mot-de-passe)
12. [Checklist & pièges](#12-checklist--pièges)

---

## 1. Authentification vs autorisation

Deux notions qu'on confond souvent :

| | **Authentification** (authn) | **Autorisation** (authz) |
| --------- | ----------------------------------- | ------------------------------------- |
| Question | **Qui es-tu ?** | **As-tu le droit de faire ça ?** |
| Exemple | se connecter avec login/mot de passe | accéder à `/admin/`, supprimer un client |
| Dans Django | `login()`, `logout()`, `User` | permissions, groupes, `@login_required` |

> 🧠 D'abord on **authentifie** (savoir qui c'est), ensuite on **autorise** (savoir ce qu'il peut faire).

---

## 2. Le système d'auth de Django

Django fournit un système d'auth **complet et déjà installé** (`django.contrib.auth`). Il apporte :

- un modèle **`User`** (table `auth_user`),
- des **vues prêtes** pour login, logout, changement et reset de mot de passe,
- un système de **permissions** et de **groupes**,
- l'objet **`request.user`** disponible dans **toutes** les vues et templates.

> ✅ Vérifie qu'on a bien dans `config/settings.py` (présents par défaut) :
> - `INSTALLED_APPS` : `'django.contrib.auth'`, `'django.contrib.contenttypes'`
> - `MIDDLEWARE` : `'django.contrib.sessions...'` et `'django.contrib.auth.middleware.AuthenticationMiddleware'`
>
> C'est ce middleware qui **attache `request.user`** à chaque requête (voir [DJANGO.md section 6](DJANGO.md)).

---

## 3. Le modèle `User`

Le modèle intégré contient déjà les champs essentiels :

| Champ | Rôle |
| ------------------ | ----------------------------------------- |
| `username` | identifiant de connexion (unique) |
| `password` | mot de passe **haché** (jamais en clair) |
| `email` | adresse email |
| `first_name` / `last_name` | nom |
| `is_active` | compte activé ? |
| `is_staff` | peut accéder à l'admin ? |
| `is_superuser` | a tous les droits ? |
| `last_login` / `date_joined` | dates |

**Créer des utilisateurs :**

```bash
# en ligne de commande (superuser = accès admin total)
python manage.py createsuperuser
```

```python
# dans le code (shell ou vue) — TOUJOURS via create_user (qui hache le mot de passe)
from django.contrib.auth.models import User

User.objects.create_user(username="alice", email="a@x.com", password="secret123")
User.objects.create_superuser(username="admin", password="secret123")
```

> ⚠️ **Ne jamais** faire `User(password="secret")` : le mot de passe serait stocké **en clair**. Utilise `create_user()` / `create_superuser()` (ou `user.set_password("...")`) qui le **hachent**.

---

## 4. Login / Logout (vues intégrées)

Inutile d'écrire la logique de connexion : Django fournit `LoginView` et `LogoutView`.

### 4.1 Brancher les URLs

Le plus simple : inclure les routes d'auth de Django dans `config/urls.py`.

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),   # login, logout, password...
    path('company/', include('company.urls')),
]
```

`include('django.contrib.auth.urls')` fournit notamment :

```
/accounts/login/     name="login"
/accounts/logout/    name="logout"
/accounts/password_change/ ...
/accounts/password_reset/  ...
```

### 4.2 Le template de login

`LoginView` cherche par défaut le template **`registration/login.html`**. Crée-le dans `templates/registration/login.html` :

```html
{% extends "base.html" %}
{% block title %}Connexion{% endblock %}

{% block content %}
<h1>Connexion</h1>

{% if form.errors %}
    <div class="alert alert-danger">Identifiants invalides.</div>
{% endif %}

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Se connecter</button>
</form>
{% endblock %}
```

> ⚠️ Pour que `registration/login.html` soit trouvé, il faut un dossier `templates/` global déclaré dans `DIRS` (voir [DJANGO.md section 9](DJANGO.md)).

### 4.3 Le bouton logout

Depuis Django 5, **`logout` n'accepte que le POST** (sécurité). On utilise donc un petit formulaire, pas un lien :

```html
{% if user.is_authenticated %}
    <span>Bonjour {{ user.username }}</span>
    <form method="post" action="{% url 'logout' %}" class="d-inline">
        {% csrf_token %}
        <button type="submit" class="btn btn-sm btn-outline-light">Déconnexion</button>
    </form>
{% else %}
    <a href="{% url 'login' %}" class="btn btn-sm btn-light">Connexion</a>
{% endif %}
```

> ❗ Piège fréquent : `<a href="{% url 'logout' %}">` (lien GET) renvoie une **405 Method Not Allowed** sur Django 5+. Utilise un `<form method="post">`.

---

## 5. Les réglages `settings.py`

Trois réglages contrôlent les redirections d'auth :

```python
LOGIN_URL = "login"                 # où rediriger un visiteur NON connecté (@login_required)
LOGIN_REDIRECT_URL = "company.index"  # où aller APRÈS une connexion réussie
LOGOUT_REDIRECT_URL = "login"       # où aller APRÈS une déconnexion
```

> Sans `LOGIN_REDIRECT_URL`, Django redirige vers `/accounts/profile/` par défaut (souvent une 404). Pense à le définir.

Le paramètre `?next=` gère le retour : si un visiteur non connecté tente `/company/customers/new`, il est envoyé vers `login/?next=/company/customers/new`, puis **ramené** à cette page après connexion.

---

## 6. Inscription (signup)

Django ne fournit **pas** de vue d'inscription toute faite (contrairement au login), mais propose le formulaire `UserCreationForm`.

`company/views.py` :

```python
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()       # crée le User (mot de passe haché)
            login(request, user)     # connecte directement après l'inscription
            return redirect("company.index")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
```

`company/urls.py` :

```python
path("signup/", views.signup, name="signup"),
```

`templates/registration/signup.html` :

```html
{% extends "base.html" %}
{% block content %}
<h1>Créer un compte</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">S'inscrire</button>
</form>
{% endblock %}
```

> 🧠 `UserCreationForm` est un **`ModelForm`** sur `User` (voir [DJANGO.md section 10.11](DJANGO.md)) : il valide le username, exige le mot de passe deux fois et le hache. Pour ajouter l'email, on le sous-classe.

---

## 7. Protéger les vues

### 7.1 `@login_required` (vues fonction)

Le décorateur bloque l'accès aux visiteurs non connectés (et les redirige vers `LOGIN_URL`) :

```python
from django.contrib.auth.decorators import login_required

@login_required
def customers_create(request):
    ...
```

### 7.2 `request.user` dans la vue

L'utilisateur courant est toujours disponible :

```python
def ma_vue(request):
    if request.user.is_authenticated:
        print(request.user.username)
    # un visiteur non connecté est un AnonymousUser (is_authenticated == False)
```

### 7.3 Exiger une permission précise

```python
from django.contrib.auth.decorators import permission_required

@permission_required("company.delete_customer", raise_exception=True)
def customers_delete(request, id):
    ...
```

### 7.4 Vues en classe (CBV)

```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView

class CustomerList(LoginRequiredMixin, ListView):
    model = Customer
    # login_url = "login"   # optionnel, sinon LOGIN_URL
```

> 🧠 Règle : **décorateur** (`@login_required`) pour les vues fonction, **mixin** (`LoginRequiredMixin`) pour les vues classe. Le mixin doit être **en premier** dans l'héritage.

---

## 8. Protéger les templates

L'objet `user` est disponible dans **tous** les templates (grâce au context processor `auth`). On adapte l'affichage :

```html
{% if user.is_authenticated %}
    <p>Connecté en tant que {{ user.username }}</p>

    {% if perms.company.add_customer %}
        <a href="{% url 'company.customerCreate' %}">+ Nouveau client</a>
    {% endif %}

    {% if user.is_staff %}
        <a href="/admin/">Admin</a>
    {% endif %}
{% else %}
    <a href="{% url 'login' %}">Se connecter</a>
{% endif %}
```

- `user.is_authenticated` → connecté ou non.
- `perms.app.codename` → l'utilisateur a-t-il cette permission ? (ex : `perms.company.add_customer`)
- `user.is_staff` / `user.is_superuser` → drapeaux spéciaux.

> ⚠️ Masquer un bouton dans le template **n'empêche pas** l'accès direct à l'URL. La sécurité **réelle** se fait dans la **vue** (section 7) ; le template ne fait que l'affichage.

---

## 9. Autorisation : permissions & groupes

### 9.1 Les permissions automatiques

Pour **chaque** modèle, Django crée **4 permissions** (codename = `action_modele`) :

| Permission | Codename (modèle `Customer`) |
| ---------- | ----------------------------- |
| Ajouter | `company.add_customer` |
| Modifier | `company.change_customer` |
| Supprimer | `company.delete_customer` |
| Voir | `company.view_customer` |

Vérifier en code :

```python
request.user.has_perm("company.delete_customer")   # True / False
```

### 9.2 Les groupes (le bon réflexe)

Un **groupe** = un paquet de permissions qu'on assigne à plusieurs utilisateurs. Plutôt que de cocher 10 permissions par personne, on crée un groupe « Gestionnaire » une fois, et on y ajoute les gens.

```
Groupe "Gestionnaire" → [add_customer, change_customer, view_customer]
   ├── alice
   └── bob          ← héritent automatiquement des 3 permissions
```

Cela se gère **dans l'admin** (Groups + onglet Permissions sur chaque User), ou en code :

```python
from django.contrib.auth.models import Group

g = Group.objects.get(name="Gestionnaire")
user.groups.add(g)            # l'utilisateur hérite des permissions du groupe
```

### 9.3 Permissions personnalisées

On peut déclarer ses propres permissions dans le modèle :

```python
class Customer(models.Model):
    ...
    class Meta:
        permissions = [
            ("export_customer", "Peut exporter les clients en CSV"),
        ]
```

(puis `makemigrations` + `migrate`, et `user.has_perm("company.export_customer")`).

> 🧠 `is_superuser=True` court-circuite tout : `has_perm()` renvoie **toujours** `True` pour un superuser.

---

## 10. Custom User model

> ⚠️ **Le conseil n°1 de la doc Django** : si tu penses un jour avoir besoin d'un User personnalisé (login par email, champs supplémentaires…), crée-le **dès le début** du projet. Le changer après coup est très pénible (migrations).

Deux approches courantes :

**A — Étendre via un profil (`OneToOne`)** — sans toucher au User, pour ajouter des champs :

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
```

**B — Custom User model (`AbstractUser`)** — pour vraiment remplacer le User :

```python
# company/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
```

```python
# settings.py — INDISPENSABLE, et dès le départ
AUTH_USER_MODEL = "company.User"
```

> 🧠 Dans le code, ne référence jamais `User` en dur : utilise `settings.AUTH_USER_MODEL` (dans les `ForeignKey`) et `get_user_model()` (dans le code), pour rester compatible avec un User personnalisé.
> ```python
> from django.contrib.auth import get_user_model
> User = get_user_model()
> ```

---

## 11. Changer / réinitialiser un mot de passe

`include('django.contrib.auth.urls')` (section 4.1) fournit déjà les vues :

| URL | name | Usage |
| ----------------------- | --------------------- | --------------------------------- |
| `/accounts/password_change/` | `password_change` | l'utilisateur **connecté** change son mot de passe |
| `/accounts/password_reset/` | `password_reset` | mot de passe **oublié** → envoi d'un email |

Les templates attendus vont dans `templates/registration/` (ex : `password_change_form.html`, `password_reset_form.html`, `password_reset_email.html`…).

> 📧 Le **reset par email** nécessite de configurer l'envoi d'emails (`EMAIL_BACKEND`…). En développement, on affiche les emails dans la console :
> ```python
> EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
> ```

Changer un mot de passe en ligne de commande :

```bash
python manage.py changepassword <username>
```

---

## 12. Checklist & pièges

Mettre en place l'auth dans le projet :

- [ ] `migrate` (tables d'auth) + `createsuperuser`
- [ ] `path('accounts/', include('django.contrib.auth.urls'))` dans `config/urls.py`
- [ ] `templates/registration/login.html`
- [ ] `LOGIN_REDIRECT_URL` et `LOGOUT_REDIRECT_URL` dans `settings.py`
- [ ] Bouton logout en **POST** (form + `{% csrf_token %}`)
- [ ] Protéger les vues sensibles avec `@login_required` / permissions
- [ ] (Si besoin) groupes + permissions dans l'admin

| Piège | Solution |
| ------------------------------------------- | ----------------------------------------- |
| `logout` renvoie **405** | utiliser un `<form method="post">`, pas un lien |
| `login.html` introuvable | le mettre dans `templates/registration/` + `DIRS` configuré |
| Redirige vers `/accounts/profile/` après login | définir `LOGIN_REDIRECT_URL` |
| Mot de passe stocké en clair | utiliser `create_user()` / `set_password()`, jamais `User(password=...)` |
| Bouton caché mais URL accessible | sécuriser dans la **vue**, pas seulement le template |
| Custom User ajouté trop tard | le créer **dès le début** du projet |
| `request.user` toujours `AnonymousUser` | `AuthenticationMiddleware` manquant dans `MIDDLEWARE` |
