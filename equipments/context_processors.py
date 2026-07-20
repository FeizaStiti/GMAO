from .models import Notification


def notifications_context(request):
    """
    Rend disponible dans tous les templates :
    - le nombre de notifications non lues
    - les 8 dernières notifications (pour le menu cloche dans la navbar)
    """
    if not request.user.is_authenticated:
        return {}

    notifications_recentes = Notification.objects.exclude(
        lu_par=request.user
    ).order_by('-date_creation')[:8]

    total_non_lues = Notification.objects.exclude(lu_par=request.user).count()

    return {
        'notifications_recentes': notifications_recentes,
        'notifications_non_lues_count': total_non_lues,
    }
