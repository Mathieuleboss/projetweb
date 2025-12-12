# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from datetime import date, time, timedelta
from restaurant.models import (
    Profile, Table, Reservation, Plat, Categorie, 
    Commande, LigneCommande, Avis, EmployeInfo
)

# ============================================
# TESTS DES MODÈLES
# ============================================

class ProfileModelTest(TestCase):
    """Tests du modèle Profile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test : Un profile est créé automatiquement avec l'utilisateur"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'client')
        self.assertEqual(self.user.profile.points, 0)
    
    def test_profile_str(self):
        """Test : La représentation string du profile"""
        expected = f"{self.user.username} (client)"
        self.assertEqual(str(self.user.profile), expected)


class EmployeInfoModelTest(TestCase):
    """Tests du modèle EmployeInfo"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='employe1',
            password='testpass123'
        )
        self.user.profile.role = 'employe'
        self.user.profile.save()
    
    def test_employe_info_creation(self):
        """Test : EmployeInfo créé automatiquement pour un employé"""
        self.assertTrue(hasattr(self.user.profile, 'employe_info'))
    
    def test_salaire_mensuel_calculation(self):
        """Test : Calcul du salaire mensuel"""
        employe = self.user.profile.employe_info
        employe.salaire_horaire = Decimal('15.00')
        employe.heures_hebdomadaires = Decimal('35.00')
        employe.save()
        
        # Salaire = 15 * 35 * 4.33 = 2273.25
        expected = Decimal('15.00') * Decimal('35.00') * Decimal('4.33')
        self.assertEqual(employe.salaire_mensuel, expected)
    
    def test_anciennete_calculation(self):
        """Test : Calcul de l'ancienneté"""
        employe = self.user.profile.employe_info
        employe.date_embauche = date.today() - timedelta(days=730)  # 2 ans
        employe.save()
        
        self.assertEqual(employe.anciennete_annees, 2)
        self.assertGreaterEqual(employe.anciennete_jours, 730)


class PlatModelTest(TestCase):
    """Tests du modèle Plat"""
    
    def setUp(self):
        self.categorie = Categorie.objects.create(
            nom='Entrées',
            type='entree'
        )
        self.plat = Plat.objects.create(
            nom='Salade César',
            description='Salade avec poulet grillé',
            prix=Decimal('9.50'),
            categorie=self.categorie,
            disponible=True
        )
    
    def test_plat_creation(self):
        """Test : Création d'un plat"""
        self.assertEqual(self.plat.nom, 'Salade César')
        self.assertEqual(self.plat.prix, Decimal('9.50'))
        self.assertTrue(self.plat.disponible)
    
    def test_plat_str(self):
        """Test : Représentation string du plat"""
        expected = "Salade César - 9.50€"
        self.assertEqual(str(self.plat), expected)


class CommandeModelTest(TestCase):
    """Tests du modèle Commande"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.categorie = Categorie.objects.create(nom='Plats', type='plat')
        self.plat = Plat.objects.create(
            nom='Pizza',
            description='Pizza Margherita',
            prix=Decimal('12.00'),
            categorie=self.categorie
        )
    
    def test_commande_creation(self):
        """Test : Création d'une commande"""
        commande = Commande.objects.create(
            user=self.user,
            montant_total=Decimal('25.00'),
            mode_paiement='carte',
            telephone='0612345678',
            statut='en_attente'
        )
        
        self.assertEqual(commande.statut, 'en_attente')
        self.assertEqual(commande.montant_total, Decimal('25.00'))
    
    def test_points_calculation(self):
        """Test : Calcul des points fidélité (1 point / 5€)"""
        commande = Commande.objects.create(
            user=self.user,
            montant_total=Decimal('27.00'),
            mode_paiement='carte',
            telephone='0612345678'
        )
        
        # 27 / 5 = 5 points
        self.assertEqual(commande.points_gagnes, 5)


class ReservationModelTest(TestCase):
    """Tests du modèle Reservation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.table = Table.objects.create(number=1, seats=4)
    
    def test_reservation_creation(self):
        """Test : Création d'une réservation"""
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            time=time(19, 0)
        )
        
        self.assertEqual(reservation.table, self.table)
        self.assertEqual(reservation.user, self.user)


class AvisModelTest(TestCase):
    """Tests du modèle Avis"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
    
    def test_avis_creation(self):
        """Test : Création d'un avis"""
        avis = Avis.objects.create(
            user=self.user,
            note=5,
            commentaire='Excellent restaurant !'
        )
        
        self.assertEqual(avis.note, 5)
        self.assertEqual(avis.commentaire, 'Excellent restaurant !')


# ============================================
# TESTS DES VUES
# ============================================

class ViewsTest(TestCase):
    """Tests des vues du site"""
    
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.user_employe = User.objects.create_user(
            username='employe1',
            password='testpass123'
        )
        self.user_employe.profile.role = 'employe'
        self.user_employe.profile.save()
    
    def test_accueil_page(self):
        """Test : Page d'accueil accessible"""
        response = self.client.get(reverse('accueil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Restaurant Gourmet')
    
    def test_menu_page(self):
        """Test : Page menu accessible"""
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_redirect(self):
        """Test : Connexion et redirection selon le rôle"""
        # Connexion client
        self.client.login(username='client1', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)  # Redirection
    
    def test_register_page(self):
        """Test : Page d'inscription accessible"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_creates_user(self):
        """Test : L'inscription crée bien un utilisateur"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'role': 'client'
        })
        
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_mon_compte_client_requires_login(self):
        """Test : Page client nécessite une connexion"""
        response = self.client.get(reverse('mon_compte'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_mon_compte_client_accessible_when_logged(self):
        """Test : Page client accessible quand connecté"""
        self.client.login(username='client1', password='testpass123')
        response = self.client.get(reverse('mon_compte'))
        self.assertEqual(response.status_code, 200)
    
    def test_employe_cannot_access_client_page(self):
        """Test : Un employé ne peut pas accéder aux pages client"""
        self.client.login(username='employe1', password='testpass123')
        response = self.client.get(reverse('mon_compte'))
        self.assertEqual(response.status_code, 302)  # Redirection
    
    def test_client_cannot_access_employe_page(self):
        """Test : Un client ne peut pas accéder aux pages employé"""
        self.client.login(username='client1', password='testpass123')
        response = self.client.get(reverse('mon_compte_employe'))
        self.assertEqual(response.status_code, 302)  # Redirection
    
    def test_avis_page(self):
        """Test : Page avis accessible"""
        response = self.client.get(reverse('avis'))
        self.assertEqual(response.status_code, 200)


# ============================================
# TESTS DES FORMULAIRES
# ============================================

class FormsTest(TestCase):
    """Tests des formulaires"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.table = Table.objects.create(number=1, seats=4)
    
    def test_avis_form_valid(self):
        """Test : Formulaire d'avis valide"""
        from restaurant.forms import AvisForm
        
        form = AvisForm(data={
            'note': 5,
            'commentaire': 'Très bon restaurant, je recommande !'
        })
        
        self.assertTrue(form.is_valid())
    
    def test_avis_form_invalid_short_comment(self):
        """Test : Commentaire trop court refusé"""
        from restaurant.forms import AvisForm
        
        form = AvisForm(data={
            'note': 5,
            'commentaire': 'Top'  # Trop court
        })
        
        self.assertFalse(form.is_valid())
    
    def test_reservation_form_valid(self):
        """Test : Formulaire de réservation valide"""
        from restaurant.forms import ReservationForm
        
        tomorrow = date.today() + timedelta(days=1)
        
        form = ReservationForm(data={
            'table': self.table.id,
            'date': tomorrow,
            'time': time(19, 0)
        })
        
        self.assertTrue(form.is_valid())
    
    def test_reservation_form_invalid_past_date(self):
        """Test : Date passée refusée"""
        from restaurant.forms import ReservationForm
        
        yesterday = date.today() - timedelta(days=1)
        
        form = ReservationForm(data={
            'table': self.table.id,
            'date': yesterday,
            'time': time(19, 0)
        })
        
        self.assertFalse(form.is_valid())


# ============================================
# TESTS D'INTÉGRATION
# ============================================

class IntegrationTest(TestCase):
    """Tests d'intégration (flux complet)"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.categorie = Categorie.objects.create(nom='Plats', type='plat')
        self.plat = Plat.objects.create(
            nom='Pizza',
            description='Pizza Margherita',
            prix=Decimal('12.00'),
            categorie=self.categorie
        )
    
    def test_complete_order_flow(self):
        """Test : Flux complet de commande"""
        # 1. Connexion
        self.client.login(username='client1', password='testpass123')
        
        # 2. Accès à la page de commande
        response = self.client.get(reverse('commander'))
        self.assertEqual(response.status_code, 200)
        
        # 3. Vérification du panier vide
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.points, 0)
        
        # 4. Simuler l'ajout au panier et validation
        # (Note: Le panier utilise sessionStorage côté client, 
        # donc on teste directement la création de commande)
        
        commande = Commande.objects.create(
            user=self.user,
            montant_total=Decimal('25.00'),
            mode_paiement='carte',
            telephone='0612345678'
        )
        
        # 5. Vérifier que la commande est créée
        self.assertTrue(Commande.objects.filter(user=self.user).exists())
        
        # 6. Vérifier les points fidélité
        self.assertEqual(commande.points_gagnes, 5)  # 25 / 5 = 5 points


# ============================================
# COMMENT EXÉCUTER LES TESTS
# ============================================

"""
Pour exécuter tous les tests :
    python manage.py test

Pour exécuter un test spécifique :
    python manage.py test restaurant.tests.ProfileModelTest

Pour voir plus de détails :
    python manage.py test --verbosity=2

Pour mesurer la couverture du code :
    pip install coverage
    coverage run --source='.' manage.py test
    coverage report
"""
