# Documentation Bootstrap 5 — Guide pratique

> Mémo sur Bootstrap 5.3 : grille responsive, menu, colonnes, flex, images.
> Basé sur **Bootstrap 5.3.8** (déjà inclus via CDN dans `base.html`).

---

## Sommaire

1. [Container, Row, Col : la base](#1-container-row-col--la-base)
2. [Les breakpoints (tailles d'écran)](#2-les-breakpoints-tailles-décran)
3. [Colonnes responsives (3 / 2 / 1)](#3-colonnes-responsives-3--2--1)
4. [Pleine largeur, moitié, tiers…](#4-pleine-largeur-moitié-tiers)
5. [Menu responsive rapide](#5-menu-responsive-rapide)
6. [Flexbox : `d-flex` vs grille `row`](#6-flexbox--d-flex-vs-grille-row)
7. [Manipuler les images](#7-manipuler-les-images)
8. [Les formulaires](#8-les-formulaires)
9. [Les alertes (alerts)](#9-les-alertes-alerts)
10. [Bordures, ombres, arrondis & formes](#10-bordures-ombres-arrondis--formes)
11. [Les cards (cartes)](#11-les-cards-cartes)
12. [Couleurs, fonds & texte (typographie)](#12-couleurs-fonds--texte-typographie)
13. [Espacements & utilitaires courants](#13-espacements--utilitaires-courants)
14. [Mémo express](#14-mémo-express)

---

## 1. Container, Row, Col : la base

Bootstrap fonctionne avec **3 niveaux emboîtés**. C'est la confusion la plus fréquente, alors voici l'image mentale :

```
.container           ← LE CADRE : centre le contenu et limite sa largeur max
└── .row             ← UNE LIGNE horizontale : groupe des colonnes (système flex)
    └── .col         ← UNE COLONNE : le contenu réel, se partage la largeur
```

| Classe         | Rôle                                                       | Analogie          |
| -------------- | ---------------------------------------------------------- | ----------------- |
| `.container`   | Délimite et centre la zone de contenu, gère les marges     | Le cadre du tableau |
| `.row`         | Conteneur **horizontal** qui aligne des colonnes côte à côte | Une étagère       |
| `.col`         | La cellule où va ton contenu ; se divise la largeur de la row | Les objets sur l'étagère |

**Règle d'or :** une `col` doit **toujours** être dans une `.row`, et une `.row` **toujours** dans un `.container` (ou `.container-fluid`).

```html
<div class="container">
    <div class="row">
        <div class="col">Colonne A</div>
        <div class="col">Colonne B</div>
    </div>
</div>
```

### `.container` vs `.container-fluid`

| Classe              | Largeur                                              |
| ------------------- | --------------------------------------------------- |
| `.container`        | Largeur **fixe** par palier, centrée (marges sur les côtés) |
| `.container-fluid`  | **100 %** de la largeur, toujours (bord à bord)     |
| `.container-md`     | Fluide jusqu'au breakpoint `md`, puis fixe          |

### Le système des 12 colonnes

Une `.row` est **toujours divisée en 12 unités**. Tu répartis ces 12 entre tes colonnes.

```
| col-6           | col-6           |   → 6 + 6 = 12
| col-4     | col-4     | col-4     |   → 4 + 4 + 4 = 12
| col-8                 | col-4     |   → 8 + 4 = 12
```

```html
<div class="row">
    <div class="col-8">Large (8/12)</div>
    <div class="col-4">Étroit (4/12)</div>
</div>
```

> `col` (sans chiffre) = « partage l'espace équitablement ». `col-6` = « prends exactement 6/12 ».

### Imbrication : un `row` DANS un `col`

On **peut** (et on doit) mettre un `row` à l'intérieur d'un `col` pour re-découper une colonne. La vraie règle est l'**alternance** : `row → col → row → col…`.

- ✅ `row` dans `col` → autorisé, c'est l'imbrication
- ❌ `col` directement dans `col` → interdit, il faut un `row` entre les deux

Chaque `row` imbriqué **repart de 12**, mais sur la largeur de sa colonne parente (pas de la page) :

```html
<div class="row">
    <div class="col-8">
        <div class="row">                <!-- redécoupe les 8/12 en 12 -->
            <div class="col-6">moitié de la colonne</div>
            <div class="col-6">moitié de la colonne</div>
        </div>
    </div>
    <div class="col-4">sidebar</div>
</div>
```

---

## 2. Les breakpoints (tailles d'écran)

Le responsive repose sur des **préfixes** insérés dans la classe : `col-{breakpoint}-{taille}`.

| Préfixe | Cible                       | S'active à partir de |
| ------- | --------------------------- | -------------------- |
| (aucun) | tous les écrans (mobile first) | 0px                  |
| `sm`    | petits (paysage mobile)     | ≥ 576px              |
| `md`    | tablettes                   | ≥ 768px              |
| `lg`    | ordinateurs                 | ≥ 992px              |
| `xl`    | grands écrans               | ≥ 1200px             |
| `xxl`   | très grands écrans          | ≥ 1400px             |

**Logique « mobile first » :** une règle s'applique à partir de son breakpoint **et au-dessus**. `col-md-6` = « 6/12 à partir de `md` (tablette) et plus grand ». En dessous de `md`, la colonne reprend le comportement par défaut (pleine largeur).

---

## 3. Colonnes responsives (3 / 2 / 1)

C'est ton cas d'usage : **3 colonnes sur grand écran, 2 sur moyen, 1 sur petit**.

On empile les préfixes en partant du plus petit. Rappel : 12 / nb_colonnes = taille de chaque col.

- 1 colonne → `col-12` (12/12)
- 2 colonnes → `col-md-6` (6/12 chacune)
- 3 colonnes → `col-lg-4` (4/12 chacune)

```html
<div class="container">
    <div class="row">
        <div class="col-12 col-md-6 col-lg-4">Bloc 1</div>
        <div class="col-12 col-md-6 col-lg-4">Bloc 2</div>
        <div class="col-12 col-md-6 col-lg-4">Bloc 3</div>
        <div class="col-12 col-md-6 col-lg-4">Bloc 4</div>
    </div>
</div>
```

**Comment le lire :**

```
Petit écran (<768px) :   col-12  → 1 colonne (chaque bloc pleine largeur, empilé)
Moyen (≥768px) :         col-md-6 → 2 colonnes
Large (≥992px) :         col-lg-4 → 3 colonnes
```

```
mobile          tablette          desktop
┌──────┐       ┌────┬────┐       ┌───┬───┬───┐
│  1   │       │ 1  │ 2  │       │ 1 │ 2 │ 3 │
├──────┤       ├────┼────┤       ├───┴─┬─┴───┤
│  2   │       │ 3  │ 4  │       │  4  │     │
├──────┤       └────┴────┘       └─────┴─────┘
│  3   │
└──────┘
```

### Astuce : `row-cols` (encore plus rapide)

Au lieu de mettre la classe sur chaque colonne, mets le nombre de colonnes **sur la row** :

```html
<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3">
    <div class="col">Bloc 1</div>
    <div class="col">Bloc 2</div>
    <div class="col">Bloc 3</div>
    <div class="col">Bloc 4</div>
</div>
```

`row-cols-1` = 1 colonne par ligne, `row-cols-md-2` = 2 dès `md`, `row-cols-lg-3` = 3 dès `lg`. Les `col` se calculent tout seuls. **C'est la méthode la plus concise** pour des grilles régulières.

---

## 4. Pleine largeur, moitié, tiers…

| Je veux…                  | Classe        | Détail            |
| ------------------------- | ------------- | ----------------- |
| Toute la largeur          | `col-12`      | 12/12             |
| La moitié                 | `col-6`       | 6/12              |
| Un tiers                  | `col-4`       | 4/12              |
| Un quart                  | `col-3`       | 3/12              |
| Deux tiers                | `col-8`       | 8/12              |
| Largeur **automatique**   | `col-auto`    | s'adapte au contenu |
| Le reste de la place      | `col`         | prend l'espace libre |

```html
<div class="row">
    <div class="col-12">Bandeau pleine largeur</div>
</div>

<div class="row">
    <div class="col-6">Moitié gauche</div>
    <div class="col-6">Moitié droite</div>
</div>

<div class="row">
    <div class="col-auto">Menu (largeur du contenu)</div>
    <div class="col">Contenu (prend tout le reste)</div>
</div>
```

### Décalage et alignement

```html
<!-- Centrer une colonne de moitié : 3 de marge à gauche (offset) -->
<div class="row">
    <div class="col-6 offset-3">Centré</div>
</div>

<!-- Aligner les colonnes dans la row -->
<div class="row justify-content-center">...</div>   <!-- centré horizontalement -->
<div class="row justify-content-between">...</div>  <!-- espacé aux extrémités -->
<div class="row align-items-center">...</div>       <!-- centré verticalement -->
```

---

## 5. Menu responsive rapide

Le composant `navbar` est déjà responsive : il se transforme en bouton « hamburger » sur mobile. La clé est `navbar-expand-{breakpoint}`.

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <!-- Logo / marque -->
        <a class="navbar-brand" href="#">MonSite</a>

        <!-- Bouton hamburger (visible sous lg) -->
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#nav" aria-controls="nav"
                aria-expanded="false" aria-label="Menu">
            <span class="navbar-toggler-icon"></span>
        </button>

        <!-- Liens (repliés dans le hamburger sous lg) -->
        <div class="collapse navbar-collapse" id="nav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item"><a class="nav-link active" href="#">Accueil</a></li>
                <li class="nav-item"><a class="nav-link" href="#">Entreprises</a></li>
            </ul>
            <!-- Élément poussé à droite grâce au me-auto ci-dessus -->
            <span class="navbar-text">Connecté</span>
        </div>
    </div>
</nav>
```

**Les 3 ingrédients indispensables :**

1. `navbar-expand-lg` → menu déplié à partir de `lg`, hamburger en dessous. (Mets `md` pour replier plus tôt, ou enlève-le pour toujours afficher le hamburger.)
2. Le `button.navbar-toggler` avec `data-bs-target="#nav"` qui **pointe vers l'id** du bloc à replier.
3. Le `div.collapse.navbar-collapse` avec le **même id** (`id="nav"`).

> ⚠️ Le repli/dépli nécessite le **JS de Bootstrap** (`bootstrap.bundle.min.js`) — déjà inclus dans ton `base.html`.

**Astuces de placement :**
- `me-auto` sur le `<ul>` = « margin-end auto » → pousse tout ce qui suit vers la droite.
- `ms-auto` = pousse vers la droite à partir de cet élément.

---

## 6. Flexbox : `d-flex` vs grille `row`

Deux façons d'aligner des éléments côte à côte. À ne pas confondre.

| | **Grille** (`row` / `col`) | **Flex** (`d-flex`) |
| --- | --- | --- |
| Pour quoi | Mise en page **structurée** en 12 colonnes | Aligner **quelques éléments** (barre, boutons, icône+texte) |
| Largeurs | Calculées sur 12 unités | Selon le contenu / `flex-grow` |
| Exemple type | Galerie de cartes responsive | Header avec titre à gauche + bouton à droite |

### Passer de « row » (grille) à du flex pur

La grille `row` **est déjà du flex** sous le capot. Mais pour un alignement simple, `d-flex` est plus direct :

```html
<!-- Titre à gauche, bouton à droite -->
<div class="d-flex justify-content-between align-items-center">
    <h1>Mon titre</h1>
    <button class="btn btn-primary">Ajouter</button>
</div>
```

### Les utilitaires flex essentiels

```html
<div class="d-flex">...</div>              <!-- active flexbox (ligne par défaut) -->
<div class="d-flex flex-column">...</div>  <!-- empile verticalement -->
<div class="d-flex flex-row">...</div>     <!-- en ligne (défaut, pour forcer) -->
<div class="d-flex flex-wrap">...</div>    <!-- passe à la ligne si ça déborde -->
```

**Alignement horizontal** (`justify-content-*`) :

```html
<div class="d-flex justify-content-start">...</div>    <!-- début (défaut) -->
<div class="d-flex justify-content-center">...</div>   <!-- centré -->
<div class="d-flex justify-content-end">...</div>      <!-- fin -->
<div class="d-flex justify-content-between">...</div>  <!-- espacé aux bords -->
<div class="d-flex justify-content-around">...</div>   <!-- espace autour -->
```

**Alignement vertical** (`align-items-*`) :

```html
<div class="d-flex align-items-start">...</div>    <!-- haut -->
<div class="d-flex align-items-center">...</div>   <!-- centré verticalement -->
<div class="d-flex align-items-end">...</div>      <!-- bas -->
```

**Élément qui prend toute la place restante :** `flex-grow-1`

```html
<div class="d-flex">
    <div>Logo</div>
    <div class="flex-grow-1 text-center">Titre centré qui prend l'espace</div>
    <div>Menu</div>
</div>
```

### Flex responsive

Comme la grille, le flex accepte des breakpoints :

```html
<!-- Empilé sur mobile, en ligne sur md+ -->
<div class="d-flex flex-column flex-md-row">...</div>
```

> 💡 **Règle simple :** plusieurs blocs structurants qui se réorganisent selon l'écran → `row`/`col`. Juste aligner 2-3 éléments dans une barre → `d-flex`.

---

## 7. Manipuler les images

### Image responsive (s'adapte à son conteneur)

```html
<img src="..." class="img-fluid" alt="...">
```

`img-fluid` = `max-width: 100%; height: auto;` → l'image ne dépasse jamais et garde ses proportions. **À mettre quasi systématiquement.**

### Formes

```html
<img src="..." class="img-thumbnail" alt="...">   <!-- bordure + petit padding -->
<img src="..." class="rounded" alt="...">          <!-- coins arrondis -->
<img src="..." class="rounded-circle" alt="...">   <!-- cercle (idéal avatar carré) -->
```

### Taille

```html
<img src="..." class="w-100" alt="...">     <!-- 100% de la largeur du parent -->
<img src="..." class="w-50" alt="...">      <!-- 50% -->
<img src="..." style="width: 120px;" alt=""> <!-- taille fixe -->
```

### Centrer une image

```html
<!-- Image en bloc, centrée horizontalement -->
<img src="..." class="img-fluid d-block mx-auto" alt="...">
```

`d-block` + `mx-auto` (marges gauche/droite auto) = centrage horizontal.

### Comportement de recadrage : `object-fit`

Quand tu imposes une taille fixe, l'image peut se déformer. `object-fit-cover` recadre sans déformer :

```html
<img src="..." class="rounded object-fit-cover"
     style="width: 200px; height: 200px;" alt="...">
```

| Classe                | Effet                                          |
| --------------------- | ---------------------------------------------- |
| `object-fit-cover`    | Remplit la zone en recadrant (pas de déformation) |
| `object-fit-contain`  | Tient entièrement dans la zone (bandes possibles) |

### Image dans une card

```html
<div class="card" style="width: 18rem;">
    <img src="..." class="card-img-top" alt="...">
    <div class="card-body">
        <h5 class="card-title">Titre</h5>
        <p class="card-text">Description.</p>
    </div>
</div>
```

### Figure avec légende

```html
<figure class="figure">
    <img src="..." class="figure-img img-fluid rounded" alt="...">
    <figcaption class="figure-caption">Une légende.</figcaption>
</figure>
```

---

## 8. Les formulaires

Bootstrap stylise les champs avec la classe **`form-control`** (et `form-label`, `form-select`…). La structure de base est : un `<div class="mb-3">` par champ, contenant un `<label>` + le champ.

### Formulaire de base

```html
<form method="post">
    <div class="mb-3">
        <label for="nom" class="form-label">Nom</label>
        <input type="text" class="form-control" id="nom" name="nom" placeholder="ACME">
    </div>

    <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <input type="email" class="form-control" id="email" name="email">
        <div class="form-text">On ne partagera jamais ton email.</div>
    </div>

    <button type="submit" class="btn btn-primary">Envoyer</button>
</form>
```

| Classe         | Sur quel élément                  |
| -------------- | --------------------------------- |
| `form-control` | `<input>`, `<textarea>`           |
| `form-select`  | `<select>`                        |
| `form-label`   | `<label>`                         |
| `form-text`    | petit texte d'aide (gris)         |
| `form-check`   | conteneur d'une case / radio      |

### Les différents champs

```html
<!-- Zone de texte -->
<textarea class="form-control" rows="3"></textarea>

<!-- Liste déroulante -->
<select class="form-select">
    <option selected>Choisir…</option>
    <option value="1">Option 1</option>
</select>

<!-- Case à cocher -->
<div class="form-check">
    <input class="form-check-input" type="checkbox" id="ok">
    <label class="form-check-label" for="ok">J'accepte</label>
</div>

<!-- Boutons radio -->
<div class="form-check">
    <input class="form-check-input" type="radio" name="choix" id="r1">
    <label class="form-check-label" for="r1">Oui</label>
</div>

<!-- Interrupteur (switch) -->
<div class="form-check form-switch">
    <input class="form-check-input" type="checkbox" id="sw">
    <label class="form-check-label" for="sw">Activer</label>
</div>
```

### Formulaire en grille (champs côte à côte)

On combine `row` / `col` avec les champs. `g-3` ajoute un espace (gutter) entre eux.

```html
<form class="row g-3">
    <div class="col-md-6">
        <label class="form-label">Prénom</label>
        <input type="text" class="form-control">
    </div>
    <div class="col-md-6">
        <label class="form-label">Nom</label>
        <input type="text" class="form-control">
    </div>
    <div class="col-12">
        <label class="form-label">Adresse</label>
        <input type="text" class="form-control">
    </div>
</form>
```

### Validation (champ valide / invalide)

Ajoute `is-valid` ou `is-invalid` sur le champ, et un message associé :

```html
<div class="mb-3">
    <label class="form-label">Email</label>
    <input type="email" class="form-control is-invalid">
    <div class="invalid-feedback">Email obligatoire.</div>
</div>

<div class="mb-3">
    <label class="form-label">Nom</label>
    <input type="text" class="form-control is-valid">
    <div class="valid-feedback">Parfait !</div>
</div>
```

### Avec un formulaire Django

Django génère les `<input>`, mais **pas** les classes Bootstrap. Trois approches :

```django
<!-- 1. Rendu rapide (champs bruts, sans style Bootstrap automatique) -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Envoyer</button>
</form>
```

```django
<!-- 2. Rendu champ par champ pour ajouter form-control -->
<form method="post">
    {% csrf_token %}
    <div class="mb-3">
        {{ form.nom.label_tag }}
        {{ form.nom }}
        {% if form.nom.errors %}
            <div class="text-danger small">{{ form.nom.errors }}</div>
        {% endif %}
    </div>
    <button type="submit" class="btn btn-primary">Envoyer</button>
</form>
```

> Pour appliquer `form-control` automatiquement à tous les champs Django, le plus simple est le package **`django-crispy-forms`** (avec `crispy-bootstrap5`) — sinon on ajoute la classe dans le widget du champ :
> ```python
> nom = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
> ```

> ⚠️ N'oublie jamais `{% csrf_token %}` dans un formulaire `method="post"` Django, sinon erreur **403 CSRF**.

---

## 9. Les alertes (alerts)

Une alerte = un bandeau coloré pour un message. Structure : `alert` + une couleur `alert-{type}`.

```html
<div class="alert alert-success">Opération réussie !</div>
<div class="alert alert-danger">Une erreur est survenue.</div>
<div class="alert alert-warning">Attention, vérifie tes données.</div>
<div class="alert alert-info">Information utile.</div>
```

### Les 8 couleurs disponibles

| Classe            | Usage typique          | Couleur   |
| ----------------- | ---------------------- | --------- |
| `alert-primary`   | info principale        | bleu      |
| `alert-secondary` | info secondaire        | gris      |
| `alert-success`   | succès, validation     | vert      |
| `alert-danger`    | erreur, échec          | rouge     |
| `alert-warning`   | avertissement          | jaune     |
| `alert-info`      | information neutre     | cyan      |
| `alert-light`     | sur fond sombre        | clair     |
| `alert-dark`      | contraste fort         | sombre    |

> Ce sont les **mêmes 8 couleurs** que pour les boutons (`btn-success`…), badges (`badge`), textes (`text-danger`), fonds (`bg-warning`). Apprends-les une fois, réutilise-les partout.

### Alerte avec titre et contenu

```html
<div class="alert alert-warning">
    <h4 class="alert-heading">Attention !</h4>
    <p>Ton abonnement expire bientôt.</p>
    <hr>
    <p class="mb-0">Pense à le renouveler.</p>
    <a href="#" class="alert-link">Voir les détails</a>
</div>
```

`alert-link` colore le lien automatiquement dans le ton de l'alerte.

### Alerte fermable (bouton croix)

Ajoute `alert-dismissible fade show` + un bouton `btn-close`. (Nécessite le JS Bootstrap.)

```html
<div class="alert alert-success alert-dismissible fade show" role="alert">
    Enregistré avec succès.
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer"></button>
</div>
```

### Alertes avec les messages Django

Django a un système de **messages** (`django.contrib.messages`) qui se marie parfaitement avec les alertes. Les niveaux Django correspondent presque aux couleurs Bootstrap.

Dans la vue :

```python
from django.contrib import messages

def home_view(request):
    messages.success(request, "Entreprise créée !")
    messages.error(request, "Quelque chose a échoué.")
    return render(request, "company/index.html")
```

Dans le template (souvent dans `base.html`, au-dessus du `{% block content %}`) :

```django
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endfor %}
{% endif %}
```

> Astuce : `message.tags` renvoie `success`, `error`, `warning`… Or Bootstrap utilise `danger` (pas `error`). Pour mapper `error` → `danger`, ajoute ceci dans `settings.py` :
> ```python
> from django.contrib.messages import constants as messages
> MESSAGE_TAGS = {messages.ERROR: "danger"}
> ```

---

## 10. Bordures, ombres, arrondis & formes

### Bordures

Ajoute/retire des bordures avec `border` et ses variantes de côté.

```html
<div class="border">bordure sur les 4 côtés</div>
<div class="border-top">bordure en haut seulement</div>
<div class="border-bottom border-end">bas + droite</div>
<div class="border border-0">sans bordure (retire)</div>
```

Côtés : `border-top`, `border-bottom`, `border-start` (gauche), `border-end` (droite).

**Couleur et épaisseur :**

```html
<div class="border border-primary">bordure bleue</div>
<div class="border border-danger">bordure rouge</div>
<div class="border border-3">bordure épaisse (1 à 5)</div>
```

> Les couleurs sont les **8 couleurs Bootstrap** habituelles (`primary`, `success`, `danger`…).

### Arrondis (border-radius)

```html
<div class="rounded">coins arrondis (léger)</div>
<div class="rounded-0">coins carrés (retire l'arrondi)</div>
<div class="rounded-1">arrondi petit</div>
<div class="rounded-3">arrondi moyen</div>
<div class="rounded-pill">forme « pilule » (très arrondi)</div>
<div class="rounded-circle">cercle complet</div>
```

Arrondir un seul côté/coin :

```html
<div class="rounded-top">coins du haut arrondis</div>
<div class="rounded-end">coins de droite arrondis</div>
```

### Ombres (shadows)

```html
<div class="shadow-none">aucune ombre</div>
<div class="shadow-sm">ombre légère</div>
<div class="shadow">ombre normale</div>
<div class="shadow-lg">ombre prononcée</div>
```

> `shadow-sm` est parfait pour donner un léger relief aux cards sans surcharger.

### Faire des formes (carré, rond)

Bootstrap n'a pas de classe « carré » : une forme se fait en **fixant largeur = hauteur**, puis en jouant sur l'arrondi.

```html
<!-- Carré -->
<div class="bg-primary" style="width: 100px; height: 100px;"></div>

<!-- Carré à coins arrondis -->
<div class="bg-primary rounded-3" style="width: 100px; height: 100px;"></div>

<!-- Rond (cercle) : carré + rounded-circle -->
<div class="bg-primary rounded-circle" style="width: 100px; height: 100px;"></div>

<!-- Pastille / badge rond avec texte centré -->
<div class="bg-success rounded-circle d-flex align-items-center justify-content-center text-white"
     style="width: 60px; height: 60px;">
    99+
</div>
```

> 🔑 **Recette du rond** : un élément **carré** (même `width` et `height`) + `rounded-circle`. Si la largeur ≠ hauteur, tu obtiens un ovale.

**Avatar rond à partir d'une image** (rappel §7) :

```html
<img src="..." class="rounded-circle object-fit-cover"
     style="width: 80px; height: 80px;" alt="avatar">
```

### Tout combiner

```html
<div class="border border-2 rounded-3 shadow p-4">
    Encadré : bordure + arrondi + ombre + padding
</div>
```

---

## 11. Les cards (cartes)

Une **card** est un conteneur polyvalent (encadré + ombre possible) pour regrouper image, titre, texte et boutons. C'est LE composant pour afficher une liste d'éléments.

### Card de base

```html
<div class="card" style="width: 18rem;">
    <div class="card-body">
        <h5 class="card-title">Titre</h5>
        <h6 class="card-subtitle mb-2 text-muted">Sous-titre</h6>
        <p class="card-text">Une description du contenu de la carte.</p>
        <a href="#" class="btn btn-primary">Action</a>
    </div>
</div>
```

| Classe          | Rôle                              |
| --------------- | --------------------------------- |
| `card`          | le conteneur                      |
| `card-body`     | la zone de contenu (padding)      |
| `card-title`    | le titre                          |
| `card-subtitle` | le sous-titre                     |
| `card-text`     | le paragraphe                     |
| `card-header`   | en-tête (bandeau haut)            |
| `card-footer`   | pied (bandeau bas)                |
| `card-img-top`  | image en haut, coins arrondis OK  |

### Card avec en-tête et pied

```html
<div class="card">
    <div class="card-header">En-tête</div>
    <div class="card-body">
        <p class="card-text">Contenu.</p>
    </div>
    <div class="card-footer text-muted">Pied de carte</div>
</div>
```

### Card avec image (style « poster de film » 🎬)

L'image va en haut avec `card-img-top`. Pour un rendu poster, on impose un ratio et `object-fit-cover` pour que l'affiche ne se déforme pas.

```html
<div class="card shadow-sm" style="width: 14rem;">
    <img src="poster.jpg" class="card-img-top object-fit-cover"
         style="height: 320px;" alt="Affiche du film">
    <div class="card-body">
        <h5 class="card-title mb-1">Inception</h5>
        <p class="card-text text-muted small mb-2">2010 · Science-fiction</p>
        <span class="badge bg-warning text-dark">★ 8.8</span>
    </div>
</div>
```

Les ingrédients « poster » :
- **`object-fit-cover` + `height` fixe** → toutes les affiches ont la même hauteur, sans déformation (l'image est recadrée).
- **`shadow-sm`** → léger relief.
- **`badge`** → la note, comme sur les sites de films.

### Image de fond avec texte par-dessus (poster avec titre sur l'image)

```html
<div class="card text-white">
    <img src="poster.jpg" class="card-img object-fit-cover"
         style="height: 360px;" alt="...">
    <div class="card-img-overlay d-flex flex-column justify-content-end">
        <h5 class="card-title">Inception</h5>
        <p class="card-text small">2010 · Science-fiction</p>
    </div>
</div>
```

`card-img` (image qui remplit) + `card-img-overlay` (contenu superposé). Le `d-flex flex-column justify-content-end` pousse le texte en bas de l'affiche.

> 💡 Si le texte est peu lisible sur l'image, ajoute un fond semi-transparent au texte : `<h5 class="card-title bg-dark bg-opacity-50 p-1 rounded">…`.

### Grille de cards responsive (galerie de posters)

On combine la grille (§3) avec les cards. `g-4` espace les colonnes, `h-100` égalise la hauteur des cards.

```html
<div class="container py-4">
    <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4">

        <div class="col">
            <div class="card h-100 shadow-sm">
                <img src="poster1.jpg" class="card-img-top object-fit-cover"
                     style="height: 300px;" alt="...">
                <div class="card-body">
                    <h6 class="card-title mb-0">Film 1</h6>
                </div>
            </div>
        </div>

        <!-- répéter le bloc .col pour chaque film -->

    </div>
</div>
```

- `row-cols-1 ... row-cols-lg-4` → 1 colonne sur mobile, jusqu'à 4 sur grand écran (galerie responsive).
- **`h-100` sur la card** → toutes les cards d'une même ligne ont la **même hauteur**, même si les titres sont de longueurs différentes (sinon elles se décalent).
- `g-4` → l'espacement entre les posters.

> Avec un modèle Django, ce bloc `.col` se met dans une boucle `{% for film in page %}…{% endfor %}` — et hop, une galerie paginée.

---

## 12. Couleurs, fonds & texte (typographie)

### Les 8 couleurs de base

Tout Bootstrap tourne autour de **8 couleurs sémantiques**. On les retrouve partout, juste en changeant le préfixe (`text-`, `bg-`, `btn-`, `border-`, `alert-`…).

| Nom         | Couleur | Sens habituel        |
| ----------- | ------- | -------------------- |
| `primary`   | bleu    | action principale    |
| `secondary` | gris    | secondaire           |
| `success`   | vert    | succès               |
| `danger`    | rouge   | erreur / danger      |
| `warning`   | jaune   | avertissement        |
| `info`      | cyan    | information          |
| `light`     | clair   | sur fond sombre      |
| `dark`      | sombre  | contraste fort       |

### Couleur du texte (`text-*`)

```html
<p class="text-primary">texte bleu</p>
<p class="text-success">texte vert</p>
<p class="text-danger">texte rouge</p>
<p class="text-muted">texte gris discret</p>
<p class="text-white">texte blanc</p>
<p class="text-body">couleur de texte par défaut</p>
<p class="text-body-secondary">gris (remplace text-muted en BS 5.3)</p>
```

Opacité du texte :

```html
<p class="text-primary text-opacity-75">bleu à 75 %</p>
<p class="text-primary text-opacity-50">bleu à 50 %</p>
```

### Couleur de fond (`bg-*`)

```html
<div class="bg-primary text-white">fond bleu</div>
<div class="bg-success text-white">fond vert</div>
<div class="bg-warning">fond jaune</div>
<div class="bg-light">fond clair</div>
<div class="bg-dark text-light">fond sombre</div>
<div class="bg-body-tertiary">gris très clair (fond de page doux)</div>
<div class="bg-transparent">fond transparent</div>
```

> 💡 Sur un fond coloré, pense à régler la **couleur du texte** (`text-white` sur fond sombre) pour la lisibilité.

**Opacité du fond** (utile pour superposer du texte sur une image, cf. §11) :

```html
<div class="bg-dark bg-opacity-50 text-white">fond noir semi-transparent</div>
<div class="bg-primary bg-opacity-25">bleu très léger</div>
```

Valeurs d'opacité : `10`, `25`, `50`, `75`, `100`.

### Dégradé

```html
<div class="bg-primary bg-gradient">fond bleu avec léger dégradé</div>
```

### Taille du texte (`fs-*`)

`fs` = *font-size*, de `1` (le plus grand, comme un `<h1>`) à `6` (le plus petit).

```html
<p class="fs-1">Très grand (≈ h1)</p>
<p class="fs-3">Moyen (≈ h3)</p>
<p class="fs-6">Petit</p>
<p class="small">encore plus petit (texte secondaire)</p>
```

> Astuce : `fs-*` change **seulement la taille** sans la sémantique. Pratique pour faire un `<p>` gros sans utiliser un titre, ou un `<h1>` visuellement plus petit (`<h1 class="fs-4">`).

### Graisse et style (`fw-*`, `fst-*`)

```html
<p class="fw-bold">gras</p>
<p class="fw-semibold">semi-gras</p>
<p class="fw-normal">normal</p>
<p class="fw-light">fin</p>
<p class="fst-italic">italique</p>
<p class="text-decoration-underline">souligné</p>
<p class="text-decoration-line-through">barré</p>
<a href="#" class="text-decoration-none">lien sans soulignement</a>
```

### Alignement et transformation du texte

```html
<p class="text-start">aligné à gauche</p>
<p class="text-center">centré</p>
<p class="text-end">aligné à droite</p>

<p class="text-uppercase">EN MAJUSCULES</p>
<p class="text-lowercase">en minuscules</p>
<p class="text-capitalize">Première Lettre De Chaque Mot</p>
```

Alignement **responsive** (comme la grille) :

```html
<p class="text-center text-md-start">centré sur mobile, à gauche dès md</p>
```

### Gérer le texte qui déborde

```html
<p class="text-truncate" style="max-width: 200px;">
    Texte très long coupé avec des points de suspension…
</p>

<p class="text-nowrap">ne passe jamais à la ligne</p>
<p class="text-break">coupe-les-mots-très-longs-pour-eviter-le-debordement</p>
```

`text-truncate` (une ligne + `…`) est très utile pour les titres de cards qui doivent rester sur une ligne.

### Titres « display » (gros titres d'accueil)

Pour un titre de bannière plus imposant qu'un `<h1>` normal :

```html
<h1 class="display-1">Très gros</h1>
<h1 class="display-4">Gros titre d'accueil</h1>
<p class="lead">Paragraphe d'introduction, légèrement plus grand.</p>
```

### Tout combiner — exemple

```html
<div class="bg-dark text-white text-center rounded-3 shadow p-5">
    <h1 class="display-5 fw-bold">Bienvenue</h1>
    <p class="lead text-body-secondary">Une bannière en quelques classes.</p>
    <span class="badge bg-success fs-6">Nouveau</span>
</div>
```

---

## 13. Espacements & utilitaires courants

Bootstrap fournit des classes d'espacement : `{propriété}{côté}-{taille}`.

- Propriété : `m` (margin) ou `p` (padding)
- Côté : `t` haut, `b` bas, `s` gauche (start), `e` droite (end), `x` horizontal, `y` vertical, ou rien (tous)
- Taille : `0` à `5` (0, .25rem, .5rem, 1rem, 1.5rem, 3rem), ou `auto`

```html
<div class="mt-3">  marge en haut (1rem) </div>
<div class="p-4">   padding partout (1.5rem) </div>
<div class="mx-auto">  centré horizontalement </div>
<div class="px-2 py-4"> padding horizontal court, vertical large </div>
<div class="mb-0">  pas de marge en bas </div>
```

Autres utilitaires très utiles :

```html
<p class="text-center">centré</p>
<p class="text-end">à droite</p>
<p class="text-muted">gris discret</p>
<p class="fw-bold">gras</p>
<p class="fs-4">grande police</p>

<div class="bg-light">fond clair</div>
<div class="bg-dark text-light">fond sombre, texte clair</div>

<div class="border rounded shadow-sm">bordure + arrondi + ombre</div>

<div class="d-none d-md-block">caché sur mobile, visible dès md</div>
<div class="d-block d-md-none">visible sur mobile uniquement</div>
```

---

## 14. Mémo express

```
STRUCTURE
  container > row > col          ← toujours dans cet ordre
  12 colonnes par row

RESPONSIVE (mobile first)
  col-12 col-md-6 col-lg-4       ← 1 / 2 / 3 colonnes
  row-cols-1 row-cols-md-2 row-cols-lg-3   ← version courte
  préfixes : sm 576 / md 768 / lg 992 / xl 1200

LARGEUR
  col-12 plein · col-6 moitié · col-4 tiers · col-auto contenu · col reste

MENU
  navbar-expand-lg + toggler(data-bs-target="#x") + collapse(id="x")
  besoin du JS bootstrap.bundle

FLEX (aligner quelques éléments)
  d-flex
  justify-content-between / -center   ← horizontal
  align-items-center                  ← vertical
  flex-grow-1                         ← prend la place restante
  flex-column / flex-md-row           ← empilé puis en ligne

IMAGES
  img-fluid          ← responsive (presque toujours)
  rounded-circle     ← avatar
  object-fit-cover   ← recadre sans déformer
  d-block mx-auto    ← centrer

FORMULAIRES
  form-control       ← input / textarea
  form-select        ← select
  form-label         ← label
  form-check         ← case / radio (+ form-switch)
  mb-3 par champ · row g-3 pour côte à côte
  is-valid / is-invalid + valid-feedback / invalid-feedback
  Django : {% csrf_token %} obligatoire !

ALERTES
  alert alert-success / -danger / -warning / -info
  8 couleurs (= mêmes que boutons/badges)
  fermable : alert-dismissible fade show + btn-close
  Django messages : alert-{{ message.tags }}

BORDURES / OMBRES / FORMES
  border · border-primary · border-3 · border-0
  rounded · rounded-3 · rounded-pill · rounded-circle · rounded-0
  shadow-sm / shadow / shadow-lg
  rond = carré (width=height) + rounded-circle

CARDS
  card > card-body > card-title / card-text
  card-img-top (image en haut) · card-header / card-footer
  poster : card-img-top + object-fit-cover + height fixe
  texte sur image : card-img + card-img-overlay
  galerie : row row-cols-1..4 g-4 + card h-100

COULEURS (8 : primary secondary success danger warning info light dark)
  texte : text-danger · text-muted · text-white · text-opacity-50
  fond  : bg-primary · bg-dark · bg-body-tertiary · bg-opacity-50 · bg-gradient

TEXTE / TYPO
  taille  : fs-1..6 · small · lead · display-1..6
  graisse : fw-bold / -semibold / -light · fst-italic
  align   : text-center / -start / -end (+ responsive: text-md-start)
  casse   : text-uppercase / -lowercase / -capitalize
  overflow: text-truncate (… sur 1 ligne) · text-nowrap · text-break
  déco    : text-decoration-none / -underline / -line-through

ESPACEMENT
  m=margin p=padding · t/b/s/e/x/y · 0→5 · ex: mt-3 px-2 mb-0
```

> 📚 Référence officielle : https://getbootstrap.com/docs/5.3/
