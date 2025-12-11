from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import Table, Reservation, Avis, Plat, Categorie, Commande, LigneCommande
from .forms import RegisterForm, ReservationForm, CommandeForm, AvisForm
from decimal import Decimal
import json
from .decorators import client_required, employe_required, role_required
from .models import EmployeInfo

# ============================================
# PAGES PUBLIQUES
# ============================================

def page_accueil(request):
    return render(request, "restaurant/accueil.html")

def page_menu(request):
    return render(request, "restaurant/menu.html")

# ============================================
# AUTHENTIFICATION
# ============================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('/admin/')
            elif hasattr(user, 'profile') and user.profile.role == 'employe':
                return redirect('mon_compte_employe')
            else:
                return redirect('mon_compte') 
        else:
            messages.error(request, "Nom ou mot de passe incorrect.")
    return render(request, "restaurant/login.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get("role")
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.save()
            login(request, user)
            messages.success(request, "Compte créé avec succès !")
            return redirect('accueil')
    else:
        form = RegisterForm()
    return render(request, 'restaurant/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('accueil')

# ============================================
# PAGES CLIENT / EMPLOYÉ (protégées)
# ============================================

@login_required(login_url='login')
def page_client(request):
    return render(request, "restaurant/client.html")

@login_required(login_url='login')
def page_employe(request):
    return render(request, "restaurant/employe.html")

@login_required
def client(request):
    user = request.user
    
    # Récupérer toutes les données du client
    commandes = Commande.objects.filter(user=user).order_by('-date_creation')
    reservations = Reservation.objects.filter(user=user).order_by('-date')
    avis_list = Avis.objects.filter(user=user).order_by('-date_creation')
    
    # Calcul des points (optionnel si tu veux la somme à la volée)
    points_total = sum(c.points_gagnes for c in commandes)
    
    context = {
        'commandes': commandes,
        'reservations': reservations,
        'avis_list': avis_list,
        'points_total': points_total,
    }
    
    return render(request, 'restaurant/client.html', context)

# ============================================
# RÉSERVATIONS
# ============================================

@login_required(login_url='login')
def reservations(request):
    tables = Table.objects.all()
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            messages.success(request, f"Réservation confirmée pour la table {reservation.table.number} le {reservation.date} à {reservation.time}.")
            return redirect('reservations')
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez vérifier les informations.")
    else:
        form = ReservationForm()
    return render(request, 'restaurant/reservations.html', {'tables': tables, 'form': form})

@login_required(login_url='login')
def mes_reservations(request):
    user_reservations = Reservation.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'restaurant/mes_reservations.html', {'reservations': user_reservations})

@login_required
def annuler_reservation(request, reservation_id):
    """
    Vue pour annuler une réservation
    """
    if request.method == 'POST':
        try:
            # ✅ Correction: utiliser 'user' au lieu de 'client'
            reservation = Reservation.objects.get(id=reservation_id, user=request.user)
            
            # ✅ Suppression directe de la réservation
            reservation.delete()
            messages.success(request, 'Votre réservation a été annulée avec succès.')
                
        except Reservation.DoesNotExist:
            messages.error(request, 'Réservation introuvable.')
    
    # ✅ Redirection vers 'mon_compte'
    return redirect('mon_compte')

# ============================================
# COMMANDES
# ============================================

@login_required(login_url='login')
def commander(request):
    entrees = Plat.objects.filter(categorie__type='entree', disponible=True)
    plats = Plat.objects.filter(categorie__type='plat', disponible=True)
    desserts = Plat.objects.filter(categorie__type='dessert', disponible=True)

    if request.method == 'POST':
        montant_total = Decimal('0.00')
        lignes_commande = []

        for plat in list(entrees) + list(plats) + list(desserts):
            qty = int(request.POST.get(f'quantite_{plat.id}', 0))
            if qty > 0:
                sous_total = plat.prix * qty
                montant_total += sous_total
                lignes_commande.append((plat, qty, plat.prix))

        if montant_total > 0:
            points_gagnes = int(montant_total // 5)
            commande = Commande.objects.create(
                user=request.user,
                montant_total=montant_total,
                mode_paiement=request.POST.get('mode_paiement', 'carte'),
                adresse_livraison=request.POST.get('adresse', ''),
                telephone=request.POST.get('telephone', ''),
                points_gagnes=points_gagnes
            )

            for plat, qty, prix in lignes_commande:
                LigneCommande.objects.create(
                    commande=commande,
                    plat=plat,
                    quantite=qty,
                    prix_unitaire=prix
                )

            profile = request.user.profile
            profile.points += points_gagnes
            profile.save()

            return render(request, 'restaurant/commander.html', {
                'entrees': entrees,
                'plats': plats,
                'desserts': desserts,
                'commande': commande,
                'points_gagnes': points_gagnes,
                'points_total': profile.points,
            })

    return render(request, 'restaurant/commander.html', {
        'entrees': entrees,
        'plats': plats,
        'desserts': desserts,
    })

@login_required(login_url='login')
def panier(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        panier_data = request.POST.get('panier_data')

        if form.is_valid() and panier_data:
            try:
                panier = json.loads(panier_data)
                montant_total = Decimal('0.00')
                lignes = []

                for item in panier:
                    plat = Plat.objects.get(id=item['id'])
                    quantite = int(item['quantite'])
                    sous_total = plat.prix * quantite
                    montant_total += sous_total
                    lignes.append({
                        'plat': plat,
                        'quantite': quantite,
                        'prix_unitaire': plat.prix
                    })

                commande = form.save(commit=False)
                commande.user = request.user
                commande.montant_total = montant_total
                commande.save()

                for ligne in lignes:
                    LigneCommande.objects.create(
                        commande=commande,
                        plat=ligne['plat'],
                        quantite=ligne['quantite'],
                        prix_unitaire=ligne['prix_unitaire']
                    )

                messages.success(request, f"Commande #{commande.id} validée ! Montant total : {montant_total}€")
                return redirect('mes_commandes')
            except Exception as e:
                messages.error(request, f"Erreur lors de la commande : {str(e)}")
    else:
        form = CommandeForm()

    return render(request, 'restaurant/panier.html', {'form': form})

@login_required(login_url='login')
def mes_commandes(request):
    commandes = Commande.objects.filter(user=request.user).prefetch_related('lignes__plat')
    return render(request, 'restaurant/mes_commandes.html', {'commandes': commandes})

@login_required(login_url='login')
def valider_commande(request):
    if request.method != 'POST':
        return redirect('commander')

    panier_json = request.POST.get('panier_json', '[]')
    try:
        panier = json.loads(panier_json)
    except json.JSONDecodeError:
        panier = []

    if not panier:
        messages.error(request, "Votre panier est vide.")
        return redirect('commander')

    # Calcul du total
    total = Decimal('0.00')
    for item in panier:
        plat = Plat.objects.get(id=item['id'])
        total += plat.prix * int(item['quantite'])

    # Création de la commande
    commande = Commande.objects.create(
        user=request.user,
        montant_total=total,
        mode_paiement='carte',
        telephone='',
        adresse_livraison='',
    )

    # Création des lignes de commande
    for item in panier:
        plat = Plat.objects.get(id=item['id'])
        LigneCommande.objects.create(
            commande=commande,
            plat=plat,
            quantite=int(item['quantite']),
            prix_unitaire=plat.prix
        )

    # Calcul des points fidélité
    profile = request.user.profile
    points_gagnes = int(total // 5)
    profile.points += points_gagnes
    profile.save()

    # On peut renvoyer un contexte pour afficher les points gagnés
    context = {
        'commande': commande,
        'points_gagnes': points_gagnes,
        'points_total': profile.points
    }

    messages.success(request, f"Commande validée ! Vous avez gagné {points_gagnes} points.")

    # Rediriger ou afficher la confirmation
    return render(request, 'restaurant/commander.html', context)

# ============================================
# AVIS
# ============================================

def avis(request):
    avis_list = Avis.objects.all().select_related('user').order_by('-date_creation')

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AvisForm(request.POST)
            if form.is_valid():
                avis_obj = form.save(commit=False)
                avis_obj.user = request.user
                avis_obj.save()
                messages.success(request, "Votre avis a été publié avec succès !")
                return redirect('avis')
            else:
                messages.error(request, "Votre avis contient des erreurs. Veuillez corriger.")
        else:
            form = AvisForm()
    else:
        form = None

    return render(request, 'restaurant/avis.html', {
        'avis_list': avis_list,
        'form': form
    })

# ============================================
# PAIEMENT
# ============================================

@login_required(login_url='login')
def paiement(request):
    if request.method == 'POST':
        panier_json = request.POST.get('panier_json', '[]')
        try:
            panier = json.loads(panier_json)
        except json.JSONDecodeError:
            panier = []

        if not panier:
            return redirect('commander')

        total = Decimal('0.00')
        for item in panier:
            total += Decimal(str(item.get('prix', 0))) * item.get('quantite', 0)

        points_gagnes = int(total)
        profile = request.user.profile
        profile.points += points_gagnes
        profile.save()

        commande = Commande.objects.create(
            user=request.user,
            montant_total=total,
            mode_paiement='carte',
            telephone='',
            adresse_livraison=''
        )

        for item in panier:
            plat = Plat.objects.get(id=item['id'])
            LigneCommande.objects.create(
                commande=commande,
                plat=plat,
                quantite=item['quantite'],
                prix_unitaire=Decimal(str(item['prix']))
            )

        return render(request, 'restaurant/paiement.html', {
            'commande': commande,
            'points_gagnes': points_gagnes,
            'points_total': profile.points
        })
    else:
        return redirect('commander')

# ============================================
# COMPTE UTILISATEUR
# ============================================

@login_required
def mon_compte(request):
    user = request.user
    
    # Récupérer toutes les commandes de l'utilisateur
    commandes = Commande.objects.filter(user=user).order_by('-date_creation')
    
    # Récupérer toutes les réservations de l'utilisateur
    reservations = Reservation.objects.filter(user=user).order_by('-date')
    
    # Récupérer tous les avis de l'utilisateur
    avis_list = Avis.objects.filter(user=user).order_by('-date_creation')
    
    context = {
        'commandes': commandes,
        'reservations': reservations,
        'avis_list': avis_list,
    }
    
    return render(request, 'restaurant/mon_compte.html', context)

@login_required
def update_profile(request):
    """
    Vue pour mettre à jour les informations du profil client
    """
    if request.method == 'POST':
        user = request.user
        
        # Mettre à jour les informations de base
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Mettre à jour le profil (si vous avez un modèle Profile)
        if hasattr(user, 'profile'):
            user.profile.phone = request.POST.get('phone', '')
            user.profile.save()
        
        messages.success(request, 'Vos informations ont été mises à jour avec succès !')
        return redirect('mon_compte')
    
    return redirect('mon_compte')



# ============================================
# COMPTE EMPLOYÉ
# ============================================

@employe_required
def mon_compte_employe(request):
    """
    Page de compte pour les employés
    """
    user = request.user
    employe_info = user.profile.employe_info
    
    # Préparer les horaires pour l'affichage
    jours_semaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    horaires_list = []
    
    for jour in jours_semaine:
        if jour in employe_info.horaires:
            horaires_list.append({
                'jour': jour,
                'debut': employe_info.horaires[jour].get('debut', 'Repos'),
                'fin': employe_info.horaires[jour].get('fin', '')
            })
        else:
            horaires_list.append({
                'jour': jour,
                'debut': 'Repos',
                'fin': ''
            })
    
    # ✅ RÉCUPÉRER LES COMMANDES À SERVIR
    commandes_a_servir = Commande.objects.filter(
        statut__in=['en_attente', 'en_preparation']
    ).select_related('user').prefetch_related('lignes__plat').order_by('-date_creation')
    
    context = {
        'employe_info': employe_info,
        'horaires_list': horaires_list,
        'salaire_mensuel': employe_info.salaire_mensuel,
        'anciennete_annees': employe_info.anciennete_annees,
        'anciennete_jours': employe_info.anciennete_jours,
        'commandes_a_servir': commandes_a_servir,  # ✅ Nouvelle ligne
    }
    
    return render(request, 'restaurant/mon_compte_employe.html', context)
@employe_required
def update_employe_info(request):
    """
    Vue pour mettre à jour les informations personnelles de l'employé
    """
    if request.method == 'POST':
        user = request.user
        employe_info = user.profile.employe_info
        
        # Mettre à jour les informations de base
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Mettre à jour le profil
        user.profile.phone = request.POST.get('phone', '')
        user.profile.save()
        
        # Mettre à jour les informations d'urgence
        employe_info.telephone_urgence = request.POST.get('telephone_urgence', '')
        employe_info.contact_urgence = request.POST.get('contact_urgence', '')
        employe_info.save()
        
        messages.success(request, 'Vos informations ont été mises à jour avec succès !')
        return redirect('mon_compte_employe')
    
    return redirect('mon_compte_employe')


# ============================================
# MODIFICATION DES VUES EXISTANTES
# ============================================

# Remplacez vos anciennes vues par celles-ci avec les décorateurs

@client_required
def mon_compte(request):
    """
    Page de compte pour les CLIENTS uniquement
    """
    user = request.user
    
    # Récupérer toutes les commandes de l'utilisateur
    commandes = Commande.objects.filter(user=user).order_by('-date_creation')
    
    # Récupérer toutes les réservations de l'utilisateur
    reservations = Reservation.objects.filter(user=user).order_by('-date')
    
    # Récupérer tous les avis de l'utilisateur
    avis_list = Avis.objects.filter(user=user).order_by('-date_creation')
    
    context = {
        'commandes': commandes,
        'reservations': reservations,
        'avis_list': avis_list,
    }
    
    return render(request, 'restaurant/mon_compte.html', context)


@client_required
def update_profile(request):
    """
    Vue pour mettre à jour les informations du profil CLIENT
    """
    if request.method == 'POST':
        user = request.user
        
        # Mettre à jour les informations de base
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Mettre à jour le profil
        if hasattr(user, 'profile'):
            user.profile.phone = request.POST.get('phone', '')
            user.profile.save()
        
        messages.success(request, 'Vos informations ont été mises à jour avec succès !')
        return redirect('mon_compte')
    
    return redirect('mon_compte')



@employe_required
def changer_statut_commande(request, commande_id):
    """
    Permet à un employé de changer le statut d'une commande
    """
    if request.method == 'POST':
        try:
            commande = Commande.objects.get(id=commande_id)
            nouveau_statut = request.POST.get('statut')
            
            if nouveau_statut in dict(Commande.STATUTS):
                commande.statut = nouveau_statut
                commande.save()
                messages.success(request, f'Commande #{commande.id} passée en "{commande.get_statut_display()}"')
            else:
                messages.error(request, 'Statut invalide')
                
        except Commande.DoesNotExist:
            messages.error(request, 'Commande introuvable')
    
    return redirect('mon_compte_employe')