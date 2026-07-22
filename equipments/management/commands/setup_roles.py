from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

ROLES = ["Responsable", "Technicien", "Lecture seule"]


class Command(BaseCommand):
    help = "Crée les groupes de rôles (Responsable / Technicien / Lecture seule) s'ils n'existent pas."

    def handle(self, *args, **options):
        for nom in ROLES:
            groupe, cree = Group.objects.get_or_create(name=nom)
            if cree:
                self.stdout.write(self.style.SUCCESS(f"Groupe créé : {nom}"))
            else:
                self.stdout.write(f"Groupe déjà existant : {nom}")
        self.stdout.write(self.style.SUCCESS("Rôles initialisés avec succès."))
