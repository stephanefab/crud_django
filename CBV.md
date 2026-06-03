# Documentation Django — Les vues génériques (CBV)

> Mémo sur les **Class-Based Views** et les vues génériques de Django : `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`…
> Basé sur **Django 6.0** et le projet `company` (modèle `Customer`, `CustomerForm`).
> Voir aussi : [DJANGO.md](DJANGO.md) (le même CRUD en vues fonction, §10), [MODELS.md](MODELS.md), [AUTH.md](AUTH.md).

---

## Sommaire

1. [FBV vs CBV : c'est quoi ?](#1-fbv-vs-cbv--cest-quoi-)
2. [Brancher une CBV dans les URLs](#2-brancher-une-cbv-dans-les-urls)
3. [`TemplateView`](#3-templateview)
4. [`ListView`](#4-listview)
5. [`DetailView`](#5-detailview)
6. [`CreateView`](#6-createview)
7. [`UpdateView`](#7-updateview)
8. [`DeleteView`](#8-deleteview)
9. [Conventions de templates & de contexte](#9-conventions-de-templates--de-contexte)
10. [Personnaliser : les méthodes à surcharger](#10-personnaliser--les-méthodes-à-surcharger)
11. [Pagination, recherche & filtrage](#11-pagination-recherche--filtrage)
12. [Les mixins (auth, permissions)](#12-les-mixins-auth-permissions)
13. [FBV ou CBV ? Avantages / inconvénients](#13-fbv-ou-cbv--avantages--inconvénients)
14. [Checklist & pièges](#14-checklist--pièges)

---

## 1. FBV vs CBV : c'est quoi ?

Jusqu'ici (dans [DJANGO.md](DJANGO.md)), tes vues étaient des **fonctions** (FBV — *Function-Based Views*). Django propose aussi des vues sous forme de **classes** (CBV — *Class-Based Views*), et surtout des **vues génériques** : des classes toutes faites qui implémentent les opérations courantes (lister, afficher, créer, modifier, supprimer).

```python
# FBV — tu écris toute la logique
def customers_list_view(request):
    return render(request, "company/customers.html",
                  {"customers": Customer.objects.all()})

# CBV générique — Django fait le travail
from django.views.generic import ListView
class CustomerListView(ListView):
    model = Customer
```

> 🧠 L'idée : pour un CRUD classique, **90 % du code est répétitif**. Les vues génériques l'éliminent — tu déclares surtout *quel modèle* et *quel template*. Pour de la logique très spécifique, la FBV reste plus lisible.

Les vues génériques principales :

| Vue générique | Rôle | Équivalent CRUD |
| --------------- | ------------------------------ | --------------- |
| `TemplateView` | afficher un template | — |
| `ListView` | lister des objets | **R**ead (liste) |
| `DetailView` | afficher un objet | **R**ead (détail) |
| `CreateView` | formulaire de création | **C**reate |
| `UpdateView` | formulaire de modification | **U**pdate |
| `DeleteView` | confirmation + suppression | **D**elete |
| `FormView` | un formulaire non lié à un modèle | — |

---

## 2. Brancher une CBV dans les URLs

Une CBV ne se passe pas directement à `path()` : on appelle **`.as_view()`** (qui transforme la classe en fonction-vue).

```python
# company/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("customers/", views.CustomerListView.as_view(), name="company.customers"),
    path("customers/<int:pk>/", views.CustomerDetailView.as_view(), name="company.customerDetail"),
    path("customers/new/", views.CustomerCreateView.as_view(), name="company.customerCreate"),
    path("customers/<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="company.customerUpdate"),
    path("customers/<int:pk>/delete/", views.CustomerDeleteView.as_view(), name="company.customerDelete"),
]
```

> ⚠️ Les vues génériques de détail/édition/suppression attendent le paramètre **`<int:pk>`** (clé primaire) par défaut — pas `<int:id>`. (On peut changer via `pk_url_kwarg`.)

---

## 3. `TemplateView`

La plus simple : afficher un template, éventuellement avec du contexte.

```python
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "company/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["nb_clients"] = Customer.objects.count()    # données supplémentaires
        return ctx
```

```python
path("", views.HomeView.as_view(), name="company.index"),
```

---

## 4. `ListView`

Liste des objets d'un modèle.

```python
from django.views.generic import ListView
from .models import Customer

class CustomerListView(ListView):
    model = Customer
    template_name = "company/customers.html"     # défaut : company/customer_list.html
    context_object_name = "customers"            # défaut : object_list / customer_list
    ordering = ["-id"]
    paginate_by = 10                             # pagination automatique (voir §11)
```

Dans le template, l'objet est disponible sous `customers` (ou `object_list` par défaut) :

```html
{% for customer in customers %}
    <p>{{ customer.first_name }} {{ customer.last_name }}</p>
{% endfor %}
```

> 💡 Sans `template_name`, `ListView` cherche **`company/customer_list.html`** (`<app>/<modele>_list.html`). Voir §9.

---

## 5. `DetailView`

Affiche **un** objet, retrouvé par sa `pk` (ou son `slug`).

```python
from django.views.generic import DetailView

class CustomerDetailView(DetailView):
    model = Customer
    template_name = "company/customer_detail.html"   # défaut : déjà ce nom
    context_object_name = "customer"                 # défaut : object / customer
```

```html
<h1>{{ customer.first_name }} {{ customer.last_name }}</h1>
<p>{{ customer.email }}</p>
```

- URL : `path("customers/<int:pk>/", CustomerDetailView.as_view(), ...)`.
- 404 automatique si la `pk` n'existe pas (comme `get_object_or_404`).

---

## 6. `CreateView`

Génère le formulaire, le valide, sauvegarde — tout le cycle de [DJANGO.md §10.11](DJANGO.md) en une classe.

```python
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Customer
from .forms import CustomerForm

class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm                          # ton ModelForm existant
    template_name = "company/customer_add.html"        # défaut : company/customer_form.html
    success_url = reverse_lazy("company.customers")     # où aller après succès
```

> 🧠 `reverse_lazy` (et non `reverse`) : l'URL est résolue **au moment de la redirection**, pas au chargement du fichier (les URLs ne sont pas encore prêtes à l'import). Indispensable pour `success_url`.

**Alternative à `form_class`** : déclarer `fields` directement (Django génère le form) :

```python
class CustomerCreateView(CreateView):
    model = Customer
    fields = ["first_name", "last_name", "email", "phone", "address"]
    success_url = reverse_lazy("company.customers")
```

Le template reçoit la variable **`form`** (voir le rendu en [DJANGO.md §10.11.4](DJANGO.md)) :

```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Enregistrer</button>
</form>
```

---

## 7. `UpdateView`

Identique à `CreateView`, mais pré-remplit le formulaire avec l'objet existant (retrouvé par `pk`).

```python
from django.views.generic.edit import UpdateView

class CustomerUpdateView(UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "company/customer_update.html"   # défaut : company/customer_form.html
    success_url = reverse_lazy("company.customers")
```

- URL : `path("customers/<int:pk>/edit/", CustomerUpdateView.as_view(), ...)`.
- En GET → formulaire pré-rempli ; en POST valide → `save()` (UPDATE) + redirection.

> 💡 `CreateView` et `UpdateView` partagent le **même template par défaut** (`customer_form.html`). Tu peux donc n'en écrire qu'un seul pour les deux.

**Rediriger vers le détail** plutôt qu'une URL fixe : surcharge `get_success_url` (l'objet a un `pk`) :

```python
def get_success_url(self):
    return reverse("company.customerDetail", args=[self.object.pk])
```

Ou, plus propre, définis `get_absolute_url()` sur le modèle (voir [MODELS.md](MODELS.md)) → `CreateView`/`UpdateView` l'utilisent automatiquement.

---

## 8. `DeleteView`

Affiche une page de **confirmation** (GET), puis supprime (POST).

```python
from django.views.generic.edit import DeleteView

class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = "company/customer_confirm_delete.html"   # défaut : ce nom
    success_url = reverse_lazy("company.customers")
```

`company/templates/company/customer_confirm_delete.html` :

```html
{% extends "base.html" %}
{% block content %}
<h1>Supprimer {{ customer.first_name }} {{ customer.last_name }} ?</h1>
<form method="post">
    {% csrf_token %}
    <button type="submit" class="btn btn-danger">Confirmer</button>
    <a href="{% url 'company.customers' %}" class="btn btn-secondary">Annuler</a>
</form>
{% endblock %}
```

> ✅ `DeleteView` impose le **POST** pour supprimer (le GET ne fait qu'afficher la confirmation) — exactement la bonne pratique de [DJANGO.md §10.6](DJANGO.md), gérée automatiquement.

---

## 9. Conventions de templates & de contexte

Les vues génériques cherchent des **noms par défaut**. Les connaître évite d'écrire `template_name` et `context_object_name`.

| Vue | Template par défaut | Variable(s) de contexte |
| ------------- | ------------------------------------- | ------------------------------ |
| `ListView` | `company/customer_list.html` | `object_list`, `customer_list` |
| `DetailView` | `company/customer_detail.html` | `object`, `customer` |
| `CreateView` | `company/customer_form.html` | `form` |
| `UpdateView` | `company/customer_form.html` | `form` |
| `DeleteView` | `company/customer_confirm_delete.html` | `object`, `customer` |

Règle : `<app>/<modele_en_minuscule>_<suffixe>.html`, et la variable porte le nom du modèle en minuscule (en plus de `object`/`object_list`).

> 💡 `context_object_name` te permet de renommer la variable (`"customers"` au lieu de `object_list`) pour un template plus lisible — pratique si tu réutilises des templates de vues fonction.

---

## 10. Personnaliser : les méthodes à surcharger

Les vues génériques exposent des « points d'accroche » à surcharger selon les besoins :

| Méthode / attribut | Pour… |
| ----------------------- | ------------------------------------------ |
| `get_queryset()` | filtrer/trier les objets affichés (ListView) |
| `get_context_data()` | ajouter des variables au template |
| `get_object()` | personnaliser la récupération de l'objet |
| `form_valid(form)` | agir juste avant/après la sauvegarde |
| `get_success_url()` | calculer dynamiquement la redirection |
| `get_form_kwargs()` | passer des arguments au formulaire |

Exemples fréquents :

```python
class CustomerListView(ListView):
    model = Customer

    def get_queryset(self):                      # n'afficher que les actifs, triés
        return Customer.objects.filter(is_active=True).order_by("last_name")

    def get_context_data(self, **kwargs):        # ajouter une donnée
        ctx = super().get_context_data(**kwargs)
        ctx["total"] = self.get_queryset().count()
        return ctx


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy("company.customers")

    def form_valid(self, form):                  # logique avant sauvegarde
        form.instance.created_by = self.request.user
        messages.success(self.request, "Client créé ✅")
        return super().form_valid(form)
```

> 🧠 Toujours appeler `super().<methode>(...)` quand tu surcharges, pour garder le comportement de base.

---

## 11. Pagination, recherche & filtrage

**Pagination** : il suffit de `paginate_by`. `ListView` fournit alors `page_obj` et `paginator` au template (voir [MODELS.md §13](MODELS.md) pour le rendu).

```python
class CustomerListView(ListView):
    model = Customer
    paginate_by = 10
```

```html
{% for customer in object_list %}{{ customer }}{% endfor %}

{% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}">Suivant</a>
{% endif %}
```

**Recherche** : on filtre dans `get_queryset()` en lisant `self.request.GET` :

```python
class CustomerListView(ListView):
    model = Customer
    paginate_by = 10

    def get_queryset(self):
        qs = Customer.objects.order_by("-id")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(last_name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")     # pour pré-remplir le champ
        return ctx
```

> 💡 Pense à conserver `q` dans les liens de pagination (`?page=2&q={{ q }}`) — même logique que [MODELS.md §14](MODELS.md).

---

## 12. Les mixins (auth, permissions)

Pour protéger une CBV, on ajoute un **mixin** (voir [AUTH.md §7.4](AUTH.md)). Il doit être placé **avant** la vue générique dans l'héritage.

```python
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy("company.customers")
    # login_url = "login"           # optionnel (sinon settings.LOGIN_URL)


class CustomerDeleteView(PermissionRequiredMixin, DeleteView):
    model = Customer
    permission_required = "company.delete_customer"
    success_url = reverse_lazy("company.customers")
```

| Mixin | Effet |
| ------------------------- | ----------------------------------------- |
| `LoginRequiredMixin` | exige un utilisateur connecté |
| `PermissionRequiredMixin` | exige une permission (`permission_required`) |
| `UserPassesTestMixin` | condition custom via `test_func()` |

> ⚠️ **Ordre de l'héritage** : `class Vue(LoginRequiredMixin, CreateView)` — le mixin **d'abord**, la vue générique **ensuite**, sinon la protection ne s'applique pas.

---

## 13. FBV ou CBV ? Avantages / inconvénients

| | **FBV** (fonctions) | **CBV génériques** (classes) |
| -------------- | ----------------------------------- | ----------------------------------- |
| Lisibilité | explicite, tout est visible | concis mais « magie » cachée |
| Code répétitif | beaucoup pour un CRUD | quasi nul |
| Courbe d'apprentissage | facile | il faut connaître les méthodes/attributs |
| Personnalisation fine | très simple (c'est du Python direct) | via surcharge de méthodes |
| Idéal pour | logique spécifique, vues atypiques | **CRUD standard**, listes, formulaires |

> 👉 **Conseil** : apprends d'abord les FBV ([DJANGO.md](DJANGO.md)) pour **comprendre** ce qui se passe, puis bascule sur les CBV génériques pour **gagner du temps** sur le CRUD répétitif. Les deux coexistent très bien dans un même projet.

**Le même CRUD, deux fois moins de code** — comparé à [DJANGO.md §10](DJANGO.md), les 5 vues CRUD tiennent en ~25 lignes :

```python
class CustomerListView(ListView):     model = Customer; paginate_by = 10
class CustomerDetailView(DetailView): model = Customer
class CustomerCreateView(CreateView): model = Customer; form_class = CustomerForm; success_url = reverse_lazy("company.customers")
class CustomerUpdateView(UpdateView): model = Customer; form_class = CustomerForm; success_url = reverse_lazy("company.customers")
class CustomerDeleteView(DeleteView): model = Customer; success_url = reverse_lazy("company.customers")
```

---

## 14. Checklist & pièges

Pour passer une vue au générique :

- [ ] Choisir la bonne classe (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`)
- [ ] Définir `model` (+ `form_class` ou `fields` pour Create/Update)
- [ ] `success_url = reverse_lazy(...)` pour Create/Update/Delete
- [ ] Brancher l'URL avec **`.as_view()`** et **`<int:pk>`**
- [ ] Créer le template (nom par défaut ou `template_name`)
- [ ] Protéger si besoin avec un **mixin** (avant la vue dans l'héritage)

| Piège | Solution |
| ------------------------------------------- | ----------------------------------------- |
| `path(..., CustomerListView, ...)` | il faut **`.as_view()`** |
| URL avec `<int:id>` | les CBV attendent **`<int:pk>`** (ou `pk_url_kwarg`) |
| `reverse()` dans `success_url` | utiliser **`reverse_lazy()`** |
| `TemplateDoesNotExist: customer_list.html` | créer le template ou définir `template_name` |
| Mixin après la vue dans l'héritage | mettre le mixin **en premier** |
| Variable absente du template | c'est `object_list`/`object` par défaut → `context_object_name` |
| Surcharge sans `super()` | comportement de base perdu |
