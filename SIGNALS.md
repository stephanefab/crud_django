# Documentation Django — Les signaux

> Mémo sur les **signaux** Django : réagir automatiquement à des événements (sauvegarde, suppression, connexion…) de façon découplée.
> Basé sur **Django 6.0** et le projet `company` (modèle `Customer`).
> Voir aussi : [MODELS.md](MODELS.md) (surcharge de `save()`), [AUTH.md](AUTH.md) (signaux de connexion).

---

## Sommaire

1. [C'est quoi un signal ?](#1-cest-quoi-un-signal-)
2. [Le vocabulaire : signal, sender, receiver](#2-le-vocabulaire--signal-sender-receiver)
3. [Les signaux intégrés](#3-les-signaux-intégrés)
4. [Connecter un receiver](#4-connecter-un-receiver)
5. [Où mettre le code : `signals.py` + `apps.py`](#5-où-mettre-le-code--signalspy--appspy)
6. [`post_save` : le plus utilisé (`created`)](#6-post_save--le-plus-utilisé-created)
7. [`pre_save`, `pre_delete`, `post_delete`](#7-pre_save-pre_delete-post_delete)
8. [Les signaux d'authentification](#8-les-signaux-dauthentification)
9. [Créer ses propres signaux](#9-créer-ses-propres-signaux)
10. [Signal ou pas ? Avantages / limites](#10-signal-ou-pas--avantages--limites)
11. [Checklist & pièges](#11-checklist--pièges)

---

## 1. C'est quoi un signal ?

Un **signal** permet à un morceau de code de **réagir à un événement** déclenché ailleurs, **sans couplage direct**. Django **émet** des signaux à des moments clés (avant/après une sauvegarde, une suppression, une connexion…), et tu **branches** des fonctions qui s'exécutent automatiquement quand l'événement survient.

```
Événement (ex: un Customer est sauvegardé)
        │  Django ÉMET le signal post_save
        ▼
Ton "receiver" s'exécute automatiquement (ex: écrire un log, créer un objet lié)
```

> 🧠 L'intérêt = le **découplage** : le code qui sauvegarde un `Customer` n'a pas besoin de connaître toutes les actions à déclencher derrière (log, email, cache…). Mais ce découplage a un coût en lisibilité — voir [§10](#10-signal-ou-pas--avantages--limites) avant d'en abuser.

---

## 2. Le vocabulaire : signal, sender, receiver

| Terme | Rôle | Exemple |
| ---------- | ------------------------------------- | ----------------------- |
| **signal** | l'événement | `post_save` |
| **sender** | qui l'émet (souvent un modèle) | `Customer` |
| **receiver** | la fonction qui réagit | `def log_customer(...)` |

Un receiver reçoit toujours des arguments **par mot-clé** (`**kwargs`), dont `sender` et `instance` :

```python
def mon_receiver(sender, instance, **kwargs):
    # sender   = la classe (Customer)
    # instance = l'objet concerné (le client sauvegardé)
    ...
```

> ⚠️ Mets **toujours** `**kwargs` dans la signature : Django passe des arguments supplémentaires (`created`, `using`, `signal`…) et omettre `**kwargs` ferait planter le receiver.

---

## 3. Les signaux intégrés

Les plus courants (modules `django.db.models.signals`, `django.contrib.auth.signals`, `django.core.signals`) :

| Signal | Émis… | Arguments utiles |
| ----------------- | ------------------------------------- | --------------------------- |
| `pre_save` | **avant** d'enregistrer un objet | `instance` |
| `post_save` | **après** l'enregistrement | `instance`, **`created`** |
| `pre_delete` | **avant** la suppression | `instance` |
| `post_delete` | **après** la suppression | `instance` |
| `m2m_changed` | quand une relation **ManyToMany** change | `action`, `pk_set` |
| `user_logged_in` | un utilisateur se connecte | `user`, `request` |
| `user_logged_out` | un utilisateur se déconnecte | `user`, `request` |
| `request_started` / `request_finished` | début/fin d'une requête HTTP | — |
| `pre_migrate` / `post_migrate` | autour des migrations | — |

---

## 4. Connecter un receiver

**Méthode recommandée — le décorateur `@receiver`** :

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer

@receiver(post_save, sender=Customer)        # ← s'exécute après chaque save() d'un Customer
def log_customer(sender, instance, created, **kwargs):
    if created:
        print(f"Nouveau client : {instance}")
```

**Méthode alternative — `.connect()`** (utile pour brancher dynamiquement) :

```python
def log_customer(sender, instance, created, **kwargs):
    ...

post_save.connect(log_customer, sender=Customer)
```

> 💡 Toujours préciser **`sender=Customer`** : sans lui, le receiver se déclencherait pour **tous** les modèles du projet (rarement voulu).

---

## 5. Où mettre le code : `signals.py` + `apps.py`

Un receiver ne s'exécute que s'il a été **importé** (= « enregistré »). Le bon emplacement, propre et standard :

**1. Écris les receivers dans `company/signals.py`** :

```python
# company/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer

@receiver(post_save, sender=Customer)
def log_customer(sender, instance, created, **kwargs):
    if created:
        print(f"Nouveau client : {instance}")
```

**2. Importe-les dans la méthode `ready()` de l'app** (`company/apps.py`) :

```python
# company/apps.py
from django.apps import AppConfig

class CompanyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "company"

    def ready(self):
        import company.signals      # ← enregistre les receivers au démarrage
```

> ⚠️ **Le piège n°1** : un signal qui « ne se déclenche pas » est presque toujours un `signals.py` **jamais importé**. L'import dans `ready()` est la solution officielle. (Évite d'importer les signaux dans `models.py` : risque d'imports circulaires.)

> ℹ️ Vérifie que `INSTALLED_APPS` référence bien la config (`"company"` suffit si `apps.py` est standard).

---

## 6. `post_save` : le plus utilisé (`created`)

`post_save` s'émet **après** chaque `save()`. Son argument **`created`** distingue création et modification :

```python
@receiver(post_save, sender=Customer)
def apres_sauvegarde(sender, instance, created, **kwargs):
    if created:
        print(f"CRÉÉ : {instance}")      # première sauvegarde (INSERT)
    else:
        print(f"MODIFIÉ : {instance}")   # mise à jour (UPDATE)
```

**Cas d'usage classique — créer un objet lié automatiquement.** Exemple : créer un `Profile` à chaque nouvel utilisateur (voir [AUTH.md §10](AUTH.md)) :

```python
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
```

> ⚠️ **Boucle infinie** : ne fais **pas** `instance.save()` sans condition dans un `post_save` → il ré-émet `post_save` → boucle. Si tu dois modifier l'instance, fais-le dans **`pre_save`** (avant l'écriture, sans re-sauvegarder).

---

## 7. `pre_save`, `pre_delete`, `post_delete`

**`pre_save`** — modifier/normaliser une valeur **avant** l'enregistrement (sans re-sauvegarder) :

```python
from django.db.models.signals import pre_save

@receiver(pre_save, sender=Customer)
def normaliser_email(sender, instance, **kwargs):
    instance.email = instance.email.strip().lower()   # appliqué juste avant l'INSERT/UPDATE
```

**`pre_delete` / `post_delete`** — agir autour d'une suppression (nettoyer un fichier, journaliser) :

```python
from django.db.models.signals import post_delete

@receiver(post_delete, sender=Customer)
def apres_suppression(sender, instance, **kwargs):
    print(f"Client supprimé : {instance}")
```

> ⚠️ `pre_save`/`post_save`/`*_delete` ne se déclenchent **pas** pour les opérations **en masse** : `Customer.objects.filter(...).update(...)`, `.bulk_create()`, `.bulk_update()`, `QuerySet.delete()` (sur le queryset) **court-circuitent** `save()`/`delete()` et donc les signaux. (Voir [§11](#11-checklist--pièges).)

---

## 8. Les signaux d'authentification

Pratiques pour journaliser ou réagir aux connexions (voir [AUTH.md](AUTH.md)) :

```python
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

@receiver(user_logged_in)
def a_la_connexion(sender, request, user, **kwargs):
    print(f"{user.username} s'est connecté")

@receiver(user_logged_out)
def a_la_deconnexion(sender, request, user, **kwargs):
    print(f"{user.username} s'est déconnecté")
```

(Ici pas de `sender=` : on écoute toutes les connexions.)

---

## 9. Créer ses propres signaux

Pour découpler une logique métier maison, tu peux **définir** et **émettre** un signal custom.

**1. Définir** (`company/signals.py`) :

```python
import django.dispatch

facture_payee = django.dispatch.Signal()      # ton signal personnalisé
```

**2. Émettre** (là où l'événement se produit, ex. une vue) :

```python
from .signals import facture_payee

def payer(request, facture_id):
    # ... logique de paiement ...
    facture_payee.send(sender=Facture, facture=facture, montant=montant)
```

**3. Recevoir** :

```python
@receiver(facture_payee)
def envoyer_recu(sender, facture, montant, **kwargs):
    print(f"Reçu envoyé pour {montant} €")
```

> 💡 En pratique, un **appel de fonction direct** (ou une couche « service ») est souvent plus clair qu'un signal custom. Réserve les signaux maison aux cas où plusieurs modules indépendants doivent réagir au même événement.

---

## 10. Signal ou pas ? Avantages / limites

| ✅ Avantages | ⚠️ Limites / inconvénients |
| ------------------------------------------ | ----------------------------------------- |
| Découplage (le sender ignore les receivers) | Logique **cachée** → difficile à suivre/déboguer |
| Réagir à des événements d'apps tierces | Ne se déclenchent pas sur les opérations **en masse** |
| Brancher plusieurs actions à un événement | Ordre d'exécution non garanti |
| Logique transverse (log, cache, audit) | Risque de **boucles** (`save()` dans `post_save`) |

> 👉 **Quand préférer une alternative :**
> - Logique propre à **un** modèle (normaliser un champ, calculer une valeur) → **surcharge `save()`** dans le modèle ([MODELS.md](MODELS.md)), plus visible.
> - Enchaînement métier dans une action → **appel de fonction** explicite dans la vue.
> - **Garde les signaux** pour le transverse (audit, réagir à un modèle que tu ne contrôles pas comme `User`), pas pour cacher de la logique métier centrale.

> 🧠 Règle simple : *« Si je peux le faire dans `save()` ou en appelant une fonction, je n'utilise pas de signal. »*

---

## 11. Checklist & pièges

Mettre en place un signal :

- [ ] Écrire le receiver dans `company/signals.py` (avec `**kwargs`)
- [ ] Préciser `sender=MonModele` (sauf si tu veux écouter tous)
- [ ] Importer `company.signals` dans `ready()` de `company/apps.py`
- [ ] Vérifier le `created` pour distinguer création/modification (`post_save`)
- [ ] Tester réellement (créer/modifier/supprimer un objet)

| Piège | Cause / solution |
| ------------------------------------------ | ----------------------------------------- |
| Le signal **ne se déclenche jamais** | `signals.py` non importé → l'importer dans `ready()` |
| `TypeError: ... unexpected keyword argument` | `**kwargs` manquant dans le receiver |
| **Boucle infinie** | `instance.save()` dans `post_save` → utiliser `pre_save` ou une condition |
| Signal ignoré sur un import en masse | `update()`/`bulk_create()`/`bulk_update()`/`QuerySet.delete()` ne passent pas par `save()`/`delete()` |
| Receiver branché pour tous les modèles | `sender=` oublié dans `@receiver` |
| Logique métier introuvable | trop de logique cachée en signaux → préférer `save()` / une fonction |
