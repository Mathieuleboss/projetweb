from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal

# ======================== PROFILE (EXTENSION USER) ========================
class Profile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('employe', 'Employé'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"

# ======================== TABLES ========================
class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    seats = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"Table {self.number} - {self.seats} places"


# ======================== RESERVATIONS ========================
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        unique_together = ('table', 'date', 'time')  # empêche le double booking

    def __str__(self):
        return f"{self.user.username} -> Table {self.table.number} le {self.date} à {self.time}"


# ======================== PLATS / MENU ========================
class Dish(models.Model):
    CATEGORY_CHOICES = [
        ('entree', 'Entrée'),
        ('plat', 'Plat'),
        ('dessert', 'Dessert'),
        ('boisson', 'Boisson'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.price}€)"


# ======================== COMMANDES ========================
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('preparing', 'En préparation'),
        ('ready', 'Prête'),
        ('done', 'Terminée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Commande #{self.id} par {self.user.username} [{self.status}]"


# ======================== DÉTAIL DES COMMANDES ========================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.dish.name}"

class Avis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avis')
    commentaire = models.TextField(verbose_name="Commentaire")
    note = models.IntegerField(
        choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)],
        verbose_name="Note"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Avis de {self.user.username} - {self.note}/5"
    

class Categorie(models.Model):
    TYPES = [
        ('entree', 'Entrée'),
        ('plat', 'Plat'),
        ('dessert', 'Dessert'),
    ]
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPES)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"


class Plat(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom du plat")
    description = models.TextField(verbose_name="Description")
    prix = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Prix (€)")
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='plats')
    
    image = models.ImageField(upload_to='plats/', blank=True, null=True)  # ✅ Remettre l'image

    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    
    class Meta:
        verbose_name = "Plat"
        verbose_name_plural = "Plats"
    
    def __str__(self):
        return f"{self.nom} - {self.prix}€"


class Commande(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('en_preparation', 'En préparation'),
        ('prete', 'Prête'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    MODES_PAIEMENT = [
        ('carte', 'Carte bancaire'),
        ('especes', 'Espèces'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commandes')
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    mode_paiement = models.CharField(max_length=20, choices=MODES_PAIEMENT)
    montant_total = models.DecimalField(max_digits=8, decimal_places=2)
    adresse_livraison = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20)
    points_gagnes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Commande #{self.id} - {self.user.username} - {self.montant_total}€"
    
    def save(self, *args, **kwargs):
        # Calcul des points : 1 point tous les 5 €
        self.points_gagnes = int(self.montant_total // 5)
        super().save(*args, **kwargs)

        # Ajouter les points au profil de l'utilisateur
        profile = self.user.profile
        profile.points += self.points_gagnes
        profile.save()
    
    


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    plat = models.ForeignKey(Plat, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
    
    def __str__(self):
        return f"{self.quantite}x {self.plat.nom}"
    
    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
    


class EmployeInfo(models.Model):
    """
    Informations supplémentaires pour les employés du restaurant
    """
    POSTES = [
        ('serveur', 'Serveur/Serveuse'),
        ('cuisinier', 'Cuisinier'),
        ('chef', 'Chef de cuisine'),
        ('plongeur', 'Plongeur'),
        ('manager', 'Manager'),
        ('caissier', 'Caissier'),
    ]
    
    CONTRATS = [
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('interim', 'Intérim'),
        ('stage', 'Stage'),
    ]
    
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='employe_info')
    poste = models.CharField(max_length=50, choices=POSTES, default='serveur')
    type_contrat = models.CharField(max_length=20, choices=CONTRATS, default='cdi')
    date_embauche = models.DateField(default=timezone.now)
    salaire_horaire = models.DecimalField(max_digits=6, decimal_places=2, default=12.00)
    heures_hebdomadaires = models.DecimalField(max_digits=5, decimal_places=2, default=35.00)
    
    # Horaires de travail (format JSON pour flexibilité)
    # Exemple: {"lundi": {"debut": "09:00", "fin": "17:00"}, ...}
    horaires = models.JSONField(default=dict, blank=True)
    
    # Informations administratives
    numero_securite_sociale = models.CharField(max_length=15, blank=True, null=True)
    telephone_urgence = models.CharField(max_length=20, blank=True, null=True)
    contact_urgence = models.CharField(max_length=100, blank=True, null=True)
    
    # Statut
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Informations employé"
        verbose_name_plural = "Informations employés"
    
    def __str__(self):
        return f"{self.profile.user.username} - {self.get_poste_display()}"
    
    @property
    def salaire_mensuel(self):
        """Calcule le salaire mensuel brut"""
        return (self.salaire_horaire * self.heures_hebdomadaires * Decimal('4.33'))
    
    @property
    def anciennete_jours(self):
        """Calcule l'ancienneté en jours"""
        return (timezone.now().date() - self.date_embauche).days
    
    @property
    def anciennete_annees(self):
        """Calcule l'ancienneté en années"""
        return self.anciennete_jours // 365


# Signal pour créer automatiquement EmployeInfo quand le profil est employé
@receiver(post_save, sender=Profile)
def create_employe_info(sender, instance, created, **kwargs):
    """Crée automatiquement les infos employé si le rôle est 'employe'"""
    if instance.role == 'employe' and not hasattr(instance, 'employe_info'):
        EmployeInfo.objects.get_or_create(profile=instance)