from django.contrib import admin

# Register your models here.
from .models import Categorie, Plat, Commande, LigneCommande

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type']
    list_filter = ['type']

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'prix', 'disponible']
    list_filter = ['categorie', 'disponible']
    search_fields = ['nom', 'description']

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'date_creation', 'statut', 'montant_total', 'mode_paiement']
    list_filter = ['statut', 'mode_paiement', 'date_creation']
    search_fields = ['user__username', 'telephone']
    inlines = [LigneCommandeInline]



from .models import EmployeInfo

@admin.register(EmployeInfo)
class EmployeInfoAdmin(admin.ModelAdmin):
    list_display = ['profile', 'poste', 'type_contrat', 'date_embauche', 'salaire_horaire', 'actif']
    list_filter = ['poste', 'type_contrat', 'actif']
    search_fields = ['profile__user__username', 'profile__user__email']