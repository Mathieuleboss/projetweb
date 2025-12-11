from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.page_accueil, name='accueil'),
    path('menu/', views.page_menu, name='menu'),

    # Authentification personnalisée
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Espace client
    path('client/', views.page_client, name='client'),
    path('mon_compte/', views.mon_compte, name='mon_compte'),
    path('update-profile/', views.update_profile, name='update_profile'),
    
    # Réservations (clients uniquement)
    path('reservations/', views.reservations, name='reservations'),
    path('mes_reservations/', views.mes_reservations, name='mes_reservations'),
    path('annuler-reservation/<int:reservation_id>/', views.annuler_reservation, name='annuler_reservation'),

    # Commandes (clients uniquement)
    path('commander/', views.commander, name='commander'),
    path('commander/valider/', views.valider_commande, name='valider_commande'),
    path('panier/', views.panier, name='panier'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),

    # Avis (accessible à tous les connectés)
    path('avis/', views.avis, name='avis'),

    # Espace employé
    path('employe/', views.page_employe, name='employe'),
    path('mon_compte_employe/', views.mon_compte_employe, name='mon_compte_employe'),
    path('update-employe-info/', views.update_employe_info, name='update_employe_info'),
    path('changer_statut_commande/<int:commande_id>/', views.changer_statut_commande, name='changer_statut_commande'),
]