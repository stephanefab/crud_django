import random

from django.core.management.base import BaseCommand

from company.models import Customer

PRENOMS = [
    "Fabien", "Marie", "Lucas", "Emma", "Hugo", "Chloé", "Nathan", "Léa",
    "Louis", "Manon", "Jules", "Camille", "Adam", "Sarah", "Gabriel", "Inès",
    "Raphaël", "Jade", "Arthur", "Louise", "Paul", "Alice", "Antoine", "Zoé",
    "Maxime", "Lina", "Théo", "Anna", "Noah", "Eva",
]

NOMS = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier", "Morel",
    "Girard", "André", "Lefevre", "Mercier", "Dupont", "Lambert", "Bonnet",
    "Francois", "Martinez",
]

VILLES = ["Paris", "Lyon", "Marseille", "Toulouse", "Nantes", "Bordeaux", "Lille"]
RUES = ["rue de la Paix", "avenue des Champs", "boulevard Voltaire", "rue Victor Hugo"]


class Command(BaseCommand):
    help = "Crée des clients fictifs pour tester (par défaut 100)."

    def add_arguments(self, parser):
        parser.add_argument("nombre", type=int, nargs="?", default=100,
                            help="Nombre de clients à créer (défaut: 100)")

    def handle(self, *args, **options):
        nombre = options["nombre"]
        clients = []

        for i in range(nombre):
            prenom = random.choice(PRENOMS)
            nom = random.choice(NOMS)
            # i garantit l'unicité de l'email même si prénom/nom se répètent
            email = f"{prenom.lower()}.{nom.lower()}{i}@example.com"
            phone = "06" + "".join(str(random.randint(0, 9)) for _ in range(8))
            address = f"{random.randint(1, 200)} {random.choice(RUES)}, {random.choice(VILLES)}"

            clients.append(Customer(
                first_name=prenom,
                last_name=nom,
                email=email,
                phone=phone,
                address=address,
            ))

        # bulk_create : une seule requête SQL pour tout insérer (rapide)
        Customer.objects.bulk_create(clients)

        self.stdout.write(self.style.SUCCESS(
            f"{nombre} clients créés. Total en base : {Customer.objects.count()}"
        ))
