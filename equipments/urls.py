from django.urls import path

from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification_list'),
    path('notifications/<int:pk>/lue/', views.marquer_notification_lue, name='notification_lue'),
    path('notifications/tout-marquer/', views.marquer_toutes_lues, name='notifications_tout_marquer'),

    # Établissements
    path('etablissements/', views.EtablissementListView.as_view(), name='etablissement_list'),
    path('etablissements/ajouter/', views.EtablissementCreateView.as_view(), name='etablissement_create'),
    path('etablissements/<int:pk>/modifier/', views.EtablissementUpdateView.as_view(), name='etablissement_update'),
    path('etablissements/<int:pk>/supprimer/', views.EtablissementDeleteView.as_view(), name='etablissement_delete'),

    # Services
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/ajouter/', views.ServiceCreateView.as_view(), name='service_create'),
    path('services/<int:pk>/modifier/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('services/<int:pk>/supprimer/', views.ServiceDeleteView.as_view(), name='service_delete'),

    # Fournisseurs
    path('fournisseurs/', views.FournisseurListView.as_view(), name='fournisseur_list'),
    path('fournisseurs/ajouter/', views.FournisseurCreateView.as_view(), name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/', views.FournisseurUpdateView.as_view(), name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.FournisseurDeleteView.as_view(), name='fournisseur_delete'),

    # Échographes
    path('echographes/', views.EchographeListView.as_view(), name='echographe_list'),
    path('echographes/ajouter/', views.EchographeCreateView.as_view(), name='echographe_create'),
    path('echographes/<int:pk>/', views.EchographeDetailView.as_view(), name='echographe_detail'),
    path('echographes/<int:pk>/modifier/', views.EchographeUpdateView.as_view(), name='echographe_update'),
    path('echographes/<int:pk>/supprimer/', views.EchographeDeleteView.as_view(), name='echographe_delete'),

    # Maintenances
    path('maintenances/', views.MaintenanceListView.as_view(), name='maintenance_list'),
    path('maintenances/ajouter/', views.MaintenanceCreateView.as_view(), name='maintenance_create'),
    path('maintenances/<int:pk>/modifier/', views.MaintenanceUpdateView.as_view(), name='maintenance_update'),
    path('maintenances/<int:pk>/supprimer/', views.MaintenanceDeleteView.as_view(), name='maintenance_delete'),

    # Planifications
    path('planifications/', views.PlanificationListView.as_view(), name='planification_list'),
    path('planifications/ajouter/', views.PlanificationCreateView.as_view(), name='planification_create'),
    path('planifications/<int:pk>/modifier/', views.PlanificationUpdateView.as_view(), name='planification_update'),
    path('planifications/<int:pk>/supprimer/', views.PlanificationDeleteView.as_view(), name='planification_delete'),

    # Pannes
    path('pannes/', views.PanneListView.as_view(), name='panne_list'),
    path('pannes/ajouter/', views.PanneCreateView.as_view(), name='panne_create'),
    path('pannes/<int:pk>/modifier/', views.PanneUpdateView.as_view(), name='panne_update'),
    path('pannes/<int:pk>/supprimer/', views.PanneDeleteView.as_view(), name='panne_delete'),

    # Pièces de rechange / stock
    path('pieces/', views.PieceRechangeListView.as_view(), name='piece_list'),
    path('pieces/ajouter/', views.PieceRechangeCreateView.as_view(), name='piece_create'),
    path('pieces/<int:pk>/modifier/', views.PieceRechangeUpdateView.as_view(), name='piece_update'),
    path('pieces/<int:pk>/supprimer/', views.PieceRechangeDeleteView.as_view(), name='piece_delete'),
    path('mouvements/ajouter/', views.MouvementStockCreateView.as_view(), name='mouvement_create'),

    # Suggestions automatiques
    path('suggestions/', views.SuggestionListView.as_view(), name='suggestion_list'),
    path('suggestions/<int:pk>/traiter/', views.marquer_suggestion_vue, name='suggestion_traiter'),

    # QR code
    path('qr/scanner/', views.qr_scan_view, name='qr_scan'),

    # Exports PDF / Excel
    path('exports/maintenances.pdf', views.export_maintenances_pdf, name='export_maintenances_pdf'),
    path('exports/maintenances.xlsx', views.export_maintenances_excel, name='export_maintenances_excel'),
    path('exports/pannes.pdf', views.export_pannes_pdf, name='export_pannes_pdf'),
    path('exports/pannes.xlsx', views.export_pannes_excel, name='export_pannes_excel'),
]
