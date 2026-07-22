"""
Utilitaires :
- diffusion des notifications à tous les membres (in-app + e-mail)
- génération des QR codes équipement
- moteur de suggestions automatiques
"""
import io
import threading
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Notification, Suggestion


# ==========================================================================
#  NOTIFICATIONS (in-app + e-mail)
# ==========================================================================

def _envoyer_emails(sujet, message, destinataires):
    """Envoie les e-mails dans un thread séparé pour ne pas bloquer la requête."""
    if not destinataires:
        return
    try:
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            destinataires,
            fail_silently=True,
        )
    except Exception:
        # On ne bloque jamais l'application pour un problème d'envoi d'e-mail.
        pass


def notifier_ajout(auteur, type_notification, titre, message, lien=''):
    """
    Crée une notification visible par TOUS les membres et envoie un e-mail
    aux membres actifs disposant d'une adresse e-mail. L'auteur de l'action
    est automatiquement marqué comme l'ayant déjà lue.
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

    User = get_user_model()
    destinataires = list(
        User.objects.filter(is_active=True)
        .exclude(email='')
        .exclude(pk=getattr(auteur, 'pk', None))
        .values_list('email', flat=True)
    )
    if destinataires:
        corps = f"{message}\n\nConsultez l'application GMAO Biomédicale pour plus de détails."
        threading.Thread(
            target=_envoyer_emails,
            args=(f"[GMAO Bio] {titre}", corps, destinataires),
            daemon=True,
        ).start()

    return notification


# ==========================================================================
#  QR CODE — génération pour un échographe
# ==========================================================================

def generer_qr_code(echographe, request=None):
    """
    Génère un QR code pointant vers la fiche détail de l'échographe
    (URL absolue si une requête est disponible, sinon le n° de série)
    et l'enregistre dans le champ `qr_code`.
    """
    import qrcode

    if request is not None:
        contenu = request.build_absolute_uri(echographe.get_absolute_url())
    else:
        contenu = echographe.numero_serie

    img = qrcode.make(contenu)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    nom_fichier = f"qr_{echographe.numero_serie}.png"
    echographe.qr_code.save(nom_fichier, ContentFile(buffer.getvalue()), save=True)
    return echographe.qr_code


# ==========================================================================
#  MOTEUR DE SUGGESTIONS
# ==========================================================================

def _creer_suggestion(type_suggestion, titre, message, lien, cle_unicite):
    """Crée une suggestion si elle n'existe pas déjà et n'a pas été traitée."""
    if Suggestion.objects.filter(cle_unicite=cle_unicite).exists():
        return None
    return Suggestion.objects.create(
        type_suggestion=type_suggestion,
        titre=titre,
        message=message,
        lien=lien,
        cle_unicite=cle_unicite,
    )


def suggerer_stock_bas(piece):
    """Pièce sous son seuil d'alerte → suggestion de commande auprès du fournisseur."""
    if not piece.en_alerte:
        return None
    fournisseur = f" auprès de {piece.fournisseur}" if piece.fournisseur else ""
    return _creer_suggestion(
        type_suggestion='stock',
        titre=f"Stock bas : {piece.nom}",
        message=(
            f"La pièce « {piece.nom} » (réf. {piece.reference}) est sous le seuil d'alerte "
            f"({piece.quantite_stock}/{piece.seuil_alerte}). Pensez à commander{fournisseur}."
        ),
        lien='/pieces/',
        cle_unicite=f"stock-{piece.pk}-{piece.quantite_stock}",
    )


def suggerer_maintenance_echographe(echographe):
    """Échographe sans maintenance prévue, ou maintenance proche/dépassée → suggestion de planification."""
    aujourdhui = timezone.now().date()
    horizon = aujourdhui + timedelta(days=30)

    if echographe.prochaine_maintenance is None:
        return _creer_suggestion(
            type_suggestion='maintenance',
            titre=f"Aucune maintenance planifiée : {echographe}",
            message=(
                f"L'échographe {echographe} n'a pas de date de prochaine maintenance renseignée. "
                f"Pensez à planifier une intervention préventive."
            ),
            lien=echographe.get_absolute_url(),
            cle_unicite=f"maint-absente-{echographe.pk}",
        )

    if echographe.prochaine_maintenance <= horizon:
        etat = "dépassée" if echographe.prochaine_maintenance < aujourdhui else "proche"
        return _creer_suggestion(
            type_suggestion='maintenance',
            titre=f"Maintenance {etat} : {echographe}",
            message=(
                f"La date de prochaine maintenance de {echographe} "
                f"({echographe.prochaine_maintenance:%d/%m/%Y}) est {etat}. "
                f"Pensez à planifier ou confirmer l'intervention."
            ),
            lien=echographe.get_absolute_url(),
            cle_unicite=f"maint-{etat}-{echographe.pk}-{echographe.prochaine_maintenance}",
        )
    return None


def suggerer_panne_recurrente(panne):
    """≥ 2 pannes sur le même équipement en moins de 90 jours → alerte de récurrence."""
    from .models import Panne

    horizon = timezone.now() - timedelta(days=90)
    nb_pannes = Panne.objects.filter(
        equipement=panne.equipement,
        date_declaration__gte=horizon,
    ).count()

    if nb_pannes >= 2:
        return _creer_suggestion(
            type_suggestion='panne_recurrente',
            titre=f"Pannes récurrentes : {panne.equipement}",
            message=(
                f"{nb_pannes} pannes ont été déclarées sur {panne.equipement} au cours des "
                f"90 derniers jours. Une intervention approfondie ou un remplacement de pièce "
                f"pourrait être nécessaire."
            ),
            lien=panne.equipement.get_absolute_url(),
            cle_unicite=f"panne-recurrente-{panne.equipement_id}-{nb_pannes}",
        )
    return None


def suggerer_technicien_frequent(panne):
    """Technicien le plus fréquent sur cet équipement → suggestion d'affectation."""
    from django.db.models import Count

    from .models import Maintenance

    top = (
        Maintenance.objects.filter(echographe=panne.equipement)
        .exclude(technicien='')
        .values('technicien')
        .annotate(total=Count('technicien'))
        .order_by('-total')
        .first()
    )
    if top and top['total'] >= 2 and panne.technicien is None:
        return _creer_suggestion(
            type_suggestion='technicien',
            titre=f"Technicien suggéré : {panne.equipement}",
            message=(
                f"{top['technicien']} est déjà intervenu {top['total']} fois sur {panne.equipement}. "
                f"Vous pourriez lui affecter cette nouvelle panne pour assurer la continuité du suivi."
            ),
            lien=panne.equipement.get_absolute_url(),
            cle_unicite=f"technicien-{panne.pk}",
        )
    return None


def marquer_suggestion_traitee(suggestion, utilisateur):
    suggestion.traitee = True
    suggestion.traitee_par = utilisateur
    suggestion.date_traitement = timezone.now()
    suggestion.save()
