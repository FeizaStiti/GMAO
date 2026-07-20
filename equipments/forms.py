from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import (
    Echographe, Etablissement, Fournisseur, Maintenance, MouvementStock,
    Panne, PieceRechange, PlanificationMaintenance, Service,
)


class BootstrapFormMixin:
    """Ajoute automatiquement les classes Bootstrap à tous les champs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault('class', 'form-select')
            elif isinstance(widget, (forms.ClearableFileInput,)):
                widget.attrs.setdefault('class', 'form-control')
            else:
                widget.attrs.setdefault('class', 'form-control')


class StyledLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class EtablissementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Etablissement
        fields = ['nom', 'adresse', 'telephone']
        widgets = {'adresse': forms.Textarea(attrs={'rows': 3})}


class ServiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = ['nom', 'etablissement']


class FournisseurForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'email', 'adresse']
        widgets = {'adresse': forms.Textarea(attrs={'rows': 3})}


class EchographeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Echographe
        fields = [
            'marque', 'modele', 'numero_serie', 'photo', 'fiche_technique',
            'bon_livraison', 'date_installation', 'garantie', 'service',
            'prochaine_maintenance',
        ]
        widgets = {
            'date_installation': forms.DateInput(attrs={'type': 'date'}),
            'garantie': forms.DateInput(attrs={'type': 'date'}),
            'prochaine_maintenance': forms.DateInput(attrs={'type': 'date'}),
        }


class MaintenanceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'echographe', 'type_maintenance', 'date_intervention', 'technicien',
            'panne', 'reparation', 'temps_arret',
        ]
        widgets = {
            'date_intervention': forms.DateInput(attrs={'type': 'date'}),
            'panne': forms.Textarea(attrs={'rows': 3}),
            'reparation': forms.Textarea(attrs={'rows': 3}),
        }


class PlanificationMaintenanceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PlanificationMaintenance
        fields = ['echographe', 'type_maintenance', 'date_prevue', 'technicien', 'statut', 'commentaire']
        widgets = {
            'date_prevue': forms.DateInput(attrs={'type': 'date'}),
            'commentaire': forms.Textarea(attrs={'rows': 3}),
        }


class PanneForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Panne
        fields = ['equipement', 'description', 'priorite', 'statut', 'technicien']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class PieceRechangeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PieceRechange
        fields = ['nom', 'reference', 'description', 'quantite_stock', 'seuil_alerte', 'fournisseur']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class MouvementStockForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['piece', 'type_mouvement', 'quantite', 'utilisateur']
