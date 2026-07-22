from django.conf import settings
from django.db import models
from django.urls import reverse


# ==========================================================================
#  STRUCTURE : Établissements / Services / Fournisseurs
# ==========================================================================

class Etablissement(models.Model):
    nom = models.CharField(max_length=200)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)

    class Meta:
        ordering = ['nom']
        verbose_name = "Établissement"
        verbose_name_plural = "Établissements"

    def __str__(self):
        return self.nom


class Service(models.Model):
    nom = models.CharField(max_length=100)
    etablissement = models.ForeignKey(
        Etablissement, on_delete=models.CASCADE, related_name='services'
    )

    class Meta:
        ordering = ['nom']
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return f"{self.nom} ({self.etablissement.nom})"


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    adresse = models.TextField()

    class Meta:
        ordering = ['nom']
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.nom


# ==========================================================================
#  ÉQUIPEMENT : Échographe
# ==========================================================================

class Echographe(models.Model):
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    photo = models.ImageField(upload_to='echographes/photos/', blank=True)
    fiche_technique = models.FileField(upload_to='echographes/fiches/', blank=True)
    bon_livraison = models.FileField(upload_to='echographes/bons/', blank=True)
    date_installation = models.DateField(null=True, blank=True)
    garantie = models.DateField(null=True, blank=True)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='echographes'
    )
    qr_code = models.ImageField(upload_to='echographes/qrcodes/', null=True, blank=True)
    prochaine_maintenance = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Échographe"
        verbose_name_plural = "Échographes"

    def __str__(self):
        return f"{self.marque} {self.modele} — {self.numero_serie}"

    def get_absolute_url(self):
        return reverse('echographe_detail', args=[self.pk])


# ==========================================================================
#  MAINTENANCE
# ==========================================================================

TYPE_MAINTENANCE_CHOICES = [
    ('preventive', 'Préventive'),
    ('corrective', 'Corrective'),
]


class Maintenance(models.Model):
    type_maintenance = models.CharField(max_length=20, choices=TYPE_MAINTENANCE_CHOICES)
    date_intervention = models.DateField()
    technicien = models.CharField(max_length=100)
    panne = models.TextField(blank=True)
    reparation = models.TextField(blank=True)
    temps_arret = models.FloatField(help_text="Temps d'arrêt en heures", default=0)
    echographe = models.ForeignKey(
        Echographe, on_delete=models.CASCADE, related_name='maintenances'
    )

    class Meta:
        ordering = ['-date_intervention']
        verbose_name = "Maintenance"
        verbose_name_plural = "Maintenances"

    def __str__(self):
        return f"Maintenance {self.get_type_maintenance_display()} — {self.echographe}"


STATUT_PLANIFICATION_CHOICES = [
    ('planifiee', 'Planifiée'),
    ('en_cours', 'En cours'),
    ('terminee', 'Terminée'),
    ('annulee', 'Annulée'),
]


class PlanificationMaintenance(models.Model):
    type_maintenance = models.CharField(max_length=20, choices=TYPE_MAINTENANCE_CHOICES)
    date_prevue = models.DateField()
    technicien = models.CharField(max_length=100)
    statut = models.CharField(
        max_length=30, choices=STATUT_PLANIFICATION_CHOICES, default='planifiee'
    )
    commentaire = models.TextField(blank=True)
    echographe = models.ForeignKey(
        Echographe, on_delete=models.CASCADE, related_name='planifications'
    )

    class Meta:
        ordering = ['date_prevue']
        verbose_name = "Planification de maintenance"
        verbose_name_plural = "Planifications de maintenance"

    def __str__(self):
        return f"Planification {self.get_type_maintenance_display()} — {self.echographe} — {self.date_prevue}"


# ==========================================================================
#  PANNES
# ==========================================================================

PRIORITE_CHOICES = [
    ('basse', 'Basse'),
    ('moyenne', 'Moyenne'),
    ('haute', 'Haute'),
    ('urgente', 'Urgente'),
]

STATUT_PANNE_CHOICES = [
    ('declaree', 'Déclarée'),
    ('en_cours', 'En cours de traitement'),
    ('resolue', 'Résolue'),
]


class Panne(models.Model):
    description = models.TextField()
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='moyenne')
    statut = models.CharField(max_length=20, choices=STATUT_PANNE_CHOICES, default='declaree')
    date_declaration = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    equipement = models.ForeignKey(
        Echographe, on_delete=models.CASCADE, related_name='pannes'
    )
    technicien = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pannes_assignees'
    )

    class Meta:
        ordering = ['-date_declaration']
        verbose_name = "Panne"
        verbose_name_plural = "Pannes"

    def __str__(self):
        return f"Panne — {self.equipement} — {self.get_statut_display()}"


# ==========================================================================
#  STOCK DE PIÈCES DE RECHANGE
# ==========================================================================

class PieceRechange(models.Model):
    nom = models.CharField(max_length=100)
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=1)
    date_creation = models.DateTimeField(auto_now_add=True)
    fournisseur = models.ForeignKey(
        Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='pieces'
    )

    class Meta:
        ordering = ['nom']
        verbose_name = "Pièce de rechange"
        verbose_name_plural = "Pièces de rechange"

    def __str__(self):
        return f"{self.nom} ({self.reference})"

    @property
    def en_alerte(self):
        return self.quantite_stock <= self.seuil_alerte


TYPE_MOUVEMENT_CHOICES = [
    ('entree', 'Entrée'),
    ('sortie', 'Sortie'),
]


class MouvementStock(models.Model):
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT_CHOICES)
    quantite = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    utilisateur = models.CharField(max_length=100)
    piece = models.ForeignKey(
        PieceRechange, on_delete=models.CASCADE, related_name='mouvements'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        return f"{self.get_type_mouvement_display()} — {self.piece} ({self.quantite})"


# ==========================================================================
#  IMPORT QR CODE
# ==========================================================================

class QRImport(models.Model):
    contenu_qr = models.TextField()
    date_scan = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_scan']
        verbose_name = "Import QR code"
        verbose_name_plural = "Imports QR code"

    def __str__(self):
        return f"Scan du {self.date_scan:%d/%m/%Y %H:%M}"


# ==========================================================================
#  SUGGESTIONS — recommandations automatiques du moteur de suggestions
# ==========================================================================

TYPE_SUGGESTION_CHOICES = [
    ('stock', 'Réapprovisionnement de stock'),
    ('maintenance', 'Planification de maintenance'),
    ('panne_recurrente', 'Panne récurrente'),
    ('technicien', "Affectation d'un technicien"),
]


class Suggestion(models.Model):
    """
    Recommandation générée automatiquement par le moteur de suggestions
    après un enregistrement (stock bas, maintenance à prévoir, panne
    récurrente, technicien fréquent sur un équipement, etc.).
    `cle_unicite` évite de dupliquer plusieurs fois la même suggestion.
    """
    type_suggestion = models.CharField(max_length=30, choices=TYPE_SUGGESTION_CHOICES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=200, blank=True)
    cle_unicite = models.CharField(max_length=200, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    traitee = models.BooleanField(default=False)
    traitee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='suggestions_traitees'
    )
    date_traitement = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Suggestion"
        verbose_name_plural = "Suggestions"

    def __str__(self):
        return self.titre


# ==========================================================================
#  NOTIFICATIONS — alerte tous les membres à chaque nouveauté
# ==========================================================================

TYPE_NOTIFICATION_CHOICES = [
    ('echographe', 'Nouvel équipement'),
    ('panne', 'Nouvelle panne'),
    ('maintenance', 'Nouvelle maintenance'),
    ('planification', 'Nouvelle planification'),
    ('piece', 'Nouvelle pièce de rechange'),
    ('stock', 'Mouvement de stock'),
    ('info', 'Information'),
]


class Notification(models.Model):
    """
    Une notification est diffusée à TOUS les membres dès qu'une nouveauté
    est ajoutée dans le système (nouvel échographe, nouvelle panne, etc.).
    Chaque utilisateur garde son propre statut de lecture via `lu_par`.
    """
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='notifications_envoyees'
    )
    type_notification = models.CharField(
        max_length=30, choices=TYPE_NOTIFICATION_CHOICES, default='info'
    )
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=200, blank=True, help_text="URL relative liée à l'objet concerné")
    date_creation = models.DateTimeField(auto_now_add=True)
    lu_par = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='notifications_lues', blank=True
    )

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return self.titre

    def est_lue_par(self, user):
        return self.lu_par.filter(pk=user.pk).exists()
