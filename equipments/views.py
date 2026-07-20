from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    EchographeForm, EtablissementForm, FournisseurForm, MaintenanceForm,
    MouvementStockForm, PanneForm, PieceRechangeForm,
    PlanificationMaintenanceForm, ServiceForm,
)
from .models import (
    Echographe, Etablissement, Fournisseur, Maintenance, MouvementStock,
    Notification, Panne, PieceRechange, PlanificationMaintenance, Service,
)
from .utils import notifier_ajout


# ==========================================================================
#  TABLEAU DE BORD
# ==========================================================================

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'dashboard.html'
    context_object_name = 'notifications_feed'
    model = Notification
    paginate_by = 0

    def get_queryset(self):
        return Notification.objects.select_related('auteur')[:10]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        aujourdhui = timezone.now().date()
        horizon = aujourdhui + timedelta(days=30)

        ctx['total_echographes'] = Echographe.objects.count()
        ctx['total_services'] = Service.objects.count()
        ctx['total_etablissements'] = Etablissement.objects.count()
        ctx['total_membres'] = User.objects.filter(is_active=True).count()

        ctx['pannes_en_cours'] = Panne.objects.exclude(statut='resolue').count()
        ctx['pannes_urgentes'] = Panne.objects.filter(
            priorite='urgente'
        ).exclude(statut='resolue').count()

        ctx['maintenances_a_venir'] = PlanificationMaintenance.objects.filter(
            date_prevue__range=[aujourdhui, horizon]
        ).exclude(statut__in=['terminee', 'annulee']).order_by('date_prevue')[:6]

        ctx['pieces_en_alerte'] = [
            p for p in PieceRechange.objects.select_related('fournisseur')
            if p.en_alerte
        ]

        ctx['dernieres_pannes'] = Panne.objects.select_related('equipement')[:5]
        ctx['derniers_echographes'] = Echographe.objects.select_related('service')[:5]

        # Répartition des pannes par statut (pour le graphique)
        ctx['pannes_par_statut'] = {
            'declaree': Panne.objects.filter(statut='declaree').count(),
            'en_cours': Panne.objects.filter(statut='en_cours').count(),
            'resolue': Panne.objects.filter(statut='resolue').count(),
        }
        return ctx


# ==========================================================================
#  NOTIFICATIONS
# ==========================================================================

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'equipments/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.select_related('auteur')


def marquer_notification_lue(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.lu_par.add(request.user)
    if notification.lien:
        return redirect(notification.lien)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


def marquer_toutes_lues(request):
    for notification in Notification.objects.exclude(lu_par=request.user):
        notification.lu_par.add(request.user)
    messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# ==========================================================================
#  MIXIN : notifie tous les membres à la création d'un nouvel objet
# ==========================================================================

class NotifiantCreateView(LoginRequiredMixin, CreateView):
    notif_type = 'info'
    notif_titre = "Nouvel élément ajouté"

    def message_notification(self, objet):
        return f"{self.request.user.get_full_name() or self.request.user.username} a ajouté : {objet}"

    def form_valid(self, form):
        response = super().form_valid(form)
        notifier_ajout(
            auteur=self.request.user,
            type_notification=self.notif_type,
            titre=self.notif_titre,
            message=self.message_notification(self.object),
            lien=self.get_success_url(),
        )
        messages.success(self.request, "Ajout effectué avec succès. Les membres ont été notifiés.")
        return response


# ==========================================================================
#  ÉTABLISSEMENTS
# ==========================================================================

class EtablissementListView(LoginRequiredMixin, ListView):
    model = Etablissement
    template_name = 'equipments/etablissement_list.html'
    context_object_name = 'objets'


class EtablissementCreateView(NotifiantCreateView):
    model = Etablissement
    form_class = EtablissementForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('etablissement_list')
    notif_type = 'info'
    notif_titre = "Nouvel établissement"
    extra_context = {'titre_page': "Ajouter un établissement"}


class EtablissementUpdateView(LoginRequiredMixin, UpdateView):
    model = Etablissement
    form_class = EtablissementForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('etablissement_list')
    extra_context = {'titre_page': "Modifier l'établissement"}


class EtablissementDeleteView(LoginRequiredMixin, DeleteView):
    model = Etablissement
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('etablissement_list')


# ==========================================================================
#  SERVICES
# ==========================================================================

class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'equipments/service_list.html'
    context_object_name = 'objets'


class ServiceCreateView(NotifiantCreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('service_list')
    notif_type = 'info'
    notif_titre = "Nouveau service"
    extra_context = {'titre_page': "Ajouter un service"}


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('service_list')
    extra_context = {'titre_page': "Modifier le service"}


class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Service
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('service_list')


# ==========================================================================
#  FOURNISSEURS
# ==========================================================================

class FournisseurListView(LoginRequiredMixin, ListView):
    model = Fournisseur
    template_name = 'equipments/fournisseur_list.html'
    context_object_name = 'objets'


class FournisseurCreateView(NotifiantCreateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('fournisseur_list')
    notif_type = 'info'
    notif_titre = "Nouveau fournisseur"
    extra_context = {'titre_page': "Ajouter un fournisseur"}


class FournisseurUpdateView(LoginRequiredMixin, UpdateView):
    model = Fournisseur
    form_class = FournisseurForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('fournisseur_list')
    extra_context = {'titre_page': "Modifier le fournisseur"}


class FournisseurDeleteView(LoginRequiredMixin, DeleteView):
    model = Fournisseur
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('fournisseur_list')


# ==========================================================================
#  ÉCHOGRAPHES
# ==========================================================================

class EchographeListView(LoginRequiredMixin, ListView):
    model = Echographe
    template_name = 'equipments/echographe_list.html'
    context_object_name = 'objets'
    paginate_by = 12

    def get_queryset(self):
        qs = Echographe.objects.select_related('service', 'service__etablissement')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(numero_serie__icontains=q) | qs.filter(marque__icontains=q) | qs.filter(modele__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class EchographeDetailView(LoginRequiredMixin, DetailView):
    model = Echographe
    template_name = 'equipments/echographe_detail.html'
    context_object_name = 'objet'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['maintenances'] = self.object.maintenances.all()
        ctx['planifications'] = self.object.planifications.all()
        ctx['pannes'] = self.object.pannes.all()
        return ctx


class EchographeCreateView(NotifiantCreateView):
    model = Echographe
    form_class = EchographeForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('echographe_list')
    notif_type = 'echographe'
    notif_titre = "Nouvel échographe ajouté"
    extra_context = {'titre_page': "Ajouter un échographe"}

    def message_notification(self, objet):
        auteur = self.request.user.get_full_name() or self.request.user.username
        return (
            f"{auteur} a ajouté un nouvel échographe : {objet.marque} {objet.modele} "
            f"(N° série : {objet.numero_serie}) au service {objet.service}."
        )


class EchographeUpdateView(LoginRequiredMixin, UpdateView):
    model = Echographe
    form_class = EchographeForm
    template_name = 'equipments/generic_form.html'
    extra_context = {'titre_page': "Modifier l'échographe"}

    def get_success_url(self):
        return reverse_lazy('echographe_detail', args=[self.object.pk])


class EchographeDeleteView(LoginRequiredMixin, DeleteView):
    model = Echographe
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('echographe_list')


# ==========================================================================
#  MAINTENANCES
# ==========================================================================

class MaintenanceListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'equipments/maintenance_list.html'
    context_object_name = 'objets'
    paginate_by = 15

    def get_queryset(self):
        return Maintenance.objects.select_related('echographe')


class MaintenanceCreateView(NotifiantCreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('maintenance_list')
    notif_type = 'maintenance'
    notif_titre = "Nouvelle intervention de maintenance"
    extra_context = {'titre_page': "Ajouter une maintenance"}

    def message_notification(self, objet):
        auteur = self.request.user.get_full_name() or self.request.user.username
        return (
            f"{auteur} a enregistré une maintenance {objet.get_type_maintenance_display().lower()} "
            f"sur {objet.echographe} (technicien : {objet.technicien})."
        )


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('maintenance_list')
    extra_context = {'titre_page': "Modifier la maintenance"}


class MaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Maintenance
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('maintenance_list')


# ==========================================================================
#  PLANIFICATIONS DE MAINTENANCE
# ==========================================================================

class PlanificationListView(LoginRequiredMixin, ListView):
    model = PlanificationMaintenance
    template_name = 'equipments/planification_list.html'
    context_object_name = 'objets'

    def get_queryset(self):
        return PlanificationMaintenance.objects.select_related('echographe')


class PlanificationCreateView(NotifiantCreateView):
    model = PlanificationMaintenance
    form_class = PlanificationMaintenanceForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('planification_list')
    notif_type = 'planification'
    notif_titre = "Nouvelle planification de maintenance"
    extra_context = {'titre_page': "Planifier une maintenance"}

    def message_notification(self, objet):
        auteur = self.request.user.get_full_name() or self.request.user.username
        return (
            f"{auteur} a planifié une maintenance {objet.get_type_maintenance_display().lower()} "
            f"pour {objet.echographe} le {objet.date_prevue:%d/%m/%Y}."
        )


class PlanificationUpdateView(LoginRequiredMixin, UpdateView):
    model = PlanificationMaintenance
    form_class = PlanificationMaintenanceForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('planification_list')
    extra_context = {'titre_page': "Modifier la planification"}


class PlanificationDeleteView(LoginRequiredMixin, DeleteView):
    model = PlanificationMaintenance
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('planification_list')


# ==========================================================================
#  PANNES
# ==========================================================================

class PanneListView(LoginRequiredMixin, ListView):
    model = Panne
    template_name = 'equipments/panne_list.html'
    context_object_name = 'objets'
    paginate_by = 15

    def get_queryset(self):
        return Panne.objects.select_related('equipement', 'technicien')


class PanneCreateView(NotifiantCreateView):
    model = Panne
    form_class = PanneForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('panne_list')
    notif_type = 'panne'
    notif_titre = "Nouvelle panne déclarée"
    extra_context = {'titre_page': "Déclarer une panne"}

    def message_notification(self, objet):
        auteur = self.request.user.get_full_name() or self.request.user.username
        return (
            f"{auteur} a déclaré une panne (priorité {objet.get_priorite_display().lower()}) "
            f"sur {objet.equipement}."
        )


class PanneUpdateView(LoginRequiredMixin, UpdateView):
    model = Panne
    form_class = PanneForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('panne_list')
    extra_context = {'titre_page': "Modifier la panne"}


class PanneDeleteView(LoginRequiredMixin, DeleteView):
    model = Panne
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('panne_list')


# ==========================================================================
#  PIÈCES DE RECHANGE / STOCK
# ==========================================================================

class PieceRechangeListView(LoginRequiredMixin, ListView):
    model = PieceRechange
    template_name = 'equipments/piece_list.html'
    context_object_name = 'objets'

    def get_queryset(self):
        return PieceRechange.objects.select_related('fournisseur')


class PieceRechangeCreateView(NotifiantCreateView):
    model = PieceRechange
    form_class = PieceRechangeForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('piece_list')
    notif_type = 'piece'
    notif_titre = "Nouvelle pièce de rechange"
    extra_context = {'titre_page': "Ajouter une pièce de rechange"}

    def message_notification(self, objet):
        auteur = self.request.user.get_full_name() or self.request.user.username
        return f"{auteur} a ajouté la pièce de rechange « {objet.nom} » (réf. {objet.reference}) au stock."


class PieceRechangeUpdateView(LoginRequiredMixin, UpdateView):
    model = PieceRechange
    form_class = PieceRechangeForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('piece_list')
    extra_context = {'titre_page': "Modifier la pièce de rechange"}


class PieceRechangeDeleteView(LoginRequiredMixin, DeleteView):
    model = PieceRechange
    template_name = 'equipments/generic_confirm_delete.html'
    success_url = reverse_lazy('piece_list')


class MouvementStockCreateView(NotifiantCreateView):
    model = MouvementStock
    form_class = MouvementStockForm
    template_name = 'equipments/generic_form.html'
    success_url = reverse_lazy('piece_list')
    notif_type = 'stock'
    notif_titre = "Nouveau mouvement de stock"
    extra_context = {'titre_page': "Enregistrer un mouvement de stock"}

    def message_notification(self, objet):
        auteur = self.request.user.get_full_name() or self.request.user.username
        return (
            f"{auteur} a enregistré une {objet.get_type_mouvement_display().lower()} de "
            f"{objet.quantite} unité(s) pour la pièce « {objet.piece.nom} »."
        )
