# restaurant/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, EmployeInfo

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un profil quand un utilisateur est créé
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Sauvegarde le profil quand l'utilisateur est sauvegardé
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()

@receiver(post_save, sender=Profile)
def create_employe_info(sender, instance, created, **kwargs):
    """
    Crée automatiquement EmployeInfo si le rôle est 'employe'
    """
    if instance.role == 'employe':
        if not hasattr(instance, 'employe_info'):
            EmployeInfo.objects.get_or_create(profile=instance)