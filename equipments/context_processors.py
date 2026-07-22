from .models import Notification, Suggestion


def notifications_context(request):
    """
    Rend disponible dans tous les templates :
    - le nombre de notifications non lues
    - les 8 dernières notifications (pour le menu cloche dans la navbar)
    - le nombre de suggestions actives (moteur de suggestions)
    - les permissions de l'utilisateur (rôle) : peut modifier / peut supprimer
    """
    if not request.user.is_authenticated:
        return {}

    from .views import user_peut_modifier, user_peut_supprimer

    notifications_recentes = Notification.objects.exclude(
        lu_par=request.user
    ).order_by('-date_creation')[:8]

    total_non_lues = Notification.objects.exclude(lu_par=request.user).count()
    suggestions_non_traitees = Suggestion.objects.filter(traitee=False).count()

    return {
        'notifications_recentes': notifications_recentes,
        'notifications_non_lues_count': total_non_lues,
        'suggestions_non_traitees_count': suggestions_non_traitees,
        'user_peut_modifier': user_peut_modifier(request.user),
        'user_peut_supprimer': user_peut_supprimer(request.user),
    }
