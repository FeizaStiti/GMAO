import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Crée un superutilisateur à partir des variables d'environnement "
        "ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL, uniquement s'il n'existe "
        "pas déjà. Ne fait rien si ADMIN_USERNAME ou ADMIN_PASSWORD n'est pas défini. "
        "Pensé pour les plateformes sans accès Shell (ex : Render plan Free)."
    )

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL', '')

        if not username or not password:
            self.stdout.write("ADMIN_USERNAME / ADMIN_PASSWORD non définis : aucun compte créé.")
            return

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"L'utilisateur « {username} » existe déjà, aucune action effectuée."
            ))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superutilisateur « {username} » créé avec succès."))