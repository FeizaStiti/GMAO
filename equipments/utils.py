"""
Utilitaires pour la diffusion des notifications à tous les membres
de l'équipe dès qu'une nouveauté est ajoutée dans le système.
"""
from .models import Notification


def notifier_ajout(auteur, type_notification, titre, message, lien=''):
    """
    Crée une notification visible par TOUS les membres.
    L'auteur de l'action est automatiquement marqué comme l'ayant déjà lue.
    """
    notification = Notification.objects.create(
        auteur=auteur,
        type_notification=type_notification,
        titre=titre,
        message=message,
        lien=lien,
    )
    if auteur is not None:
        notification.lu_par.add(auteur)
    return notification
