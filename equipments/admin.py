from django.contrib import admin

from .models import (
    Echographe, Etablissement, Fournisseur, Maintenance, MouvementStock,
    Notification, Panne, PieceRechange, PlanificationMaintenance, QRImport,
    Service, Suggestion,
)


@admin.register(Etablissement)
class EtablissementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone')
    search_fields = ('nom', 'adresse')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'etablissement')
    list_filter = ('etablissement',)
    search_fields = ('nom',)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email')
    search_fields = ('nom', 'email')


@admin.register(Echographe)
class EchographeAdmin(admin.ModelAdmin):
    list_display = ('numero_serie', 'marque', 'modele', 'service', 'date_installation', 'prochaine_maintenance')
    list_filter = ('marque', 'service__etablissement', 'service')
    search_fields = ('numero_serie', 'marque', 'modele')


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('echographe', 'type_maintenance', 'date_intervention', 'technicien', 'temps_arret')
    list_filter = ('type_maintenance',)
    search_fields = ('technicien', 'echographe__numero_serie')


@admin.register(PlanificationMaintenance)
class PlanificationMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('echographe', 'type_maintenance', 'date_prevue', 'statut', 'technicien')
    list_filter = ('statut', 'type_maintenance')


@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ('equipement', 'priorite', 'statut', 'date_declaration', 'technicien')
    list_filter = ('statut', 'priorite')


@admin.register(PieceRechange)
class PieceRechangeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'reference', 'quantite_stock', 'seuil_alerte', 'fournisseur')
    search_fields = ('nom', 'reference')


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('piece', 'type_mouvement', 'quantite', 'utilisateur', 'date')
    list_filter = ('type_mouvement',)


@admin.register(QRImport)
class QRImportAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_scan')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_notification', 'auteur', 'date_creation')
    list_filter = ('type_notification',)
    search_fields = ('titre', 'message')


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_suggestion', 'traitee', 'date_creation', 'traitee_par')
    list_filter = ('type_suggestion', 'traitee')
    search_fields = ('titre', 'message')
