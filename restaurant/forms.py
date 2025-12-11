from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.utils import timezone
from datetime import timedelta, datetime, time as datetime_time
from .models import Reservation, Table
from .models import Avis
from .models import Commande
import re

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label="Rôle")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "role"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        role = self.cleaned_data['role']
        
        if commit:
            user.save()
            # ✅ Le profil est créé automatiquement par le signal
            # On recharge l'utilisateur pour avoir le profil
            user.refresh_from_db()
            
            # Mettre à jour le rôle
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.save()
        
        return user

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'id': 'id_date', 'required': True}),
            'time': forms.TimeInput(attrs={'type': 'time', 'id': 'id_time', 'required': True}),
            'table': forms.HiddenInput(attrs={'id': 'id_table'}),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        today = timezone.now().date()
        max_date = today + timedelta(days=31)
        if date < today:
            raise forms.ValidationError("La date ne peut pas être passée.")
        if date > max_date:
            raise forms.ValidationError("Vous ne pouvez réserver que 31 jours à l'avance.")
        return date

    def clean_time(self):
        t = self.cleaned_data['time']
        opening = datetime_time(12, 0)  # 12h00
        closing = datetime_time(22, 0)  # 22h00
        if t < opening or t > closing:
            raise forms.ValidationError("L'heure doit être entre 12h et 22h.")
        return t

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')

        if table and date and time:
            if Reservation.objects.filter(table=table, date=date, time=time).exists():
                raise forms.ValidationError("Cette table est déjà réservée à cette date et heure.")
        
        return cleaned_data

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'commentaire': forms.Textarea(attrs={
                'placeholder': 'Partagez votre expérience...',
                'rows': 5,
                'class': 'form-control'
            }),
        }
        labels = {
            'note': 'Votre note',
            'commentaire': 'Votre avis',
        }

    def clean_commentaire(self):
        commentaire = self.cleaned_data.get("commentaire", "").strip().lower()

        # Minimum de longueur
        if len(commentaire) < 5:
            raise forms.ValidationError("Votre avis est trop court.")

        # Doit contenir une voyelle
        if not re.search(r"[aeiouyàâéèêëîïôöûü]", commentaire):
            raise forms.ValidationError("Votre avis doit contenir des mots compréhensibles.")

        # Pas plus de 3 consonnes d'affilée
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{4,}", commentaire):
            raise forms.ValidationError("Votre avis semble contenir des séquences non naturelles.")

        # Si aucun espace et plus de 6 lettres ⇒ mot suspect
        if " " not in commentaire and len(commentaire) > 6:
            raise forms.ValidationError("Votre avis doit être une phrase ou plusieurs mots.")

        # Éviter les répétitions absurdes
        if re.search(r"(.)\1{3,}", commentaire):
            raise forms.ValidationError("Votre avis ne doit pas contenir de répétitions anormales.")

        # Ratio consonnes/voyelles
        consonnes = re.findall(r"[bcdfghjklmnpqrstvwxyz]", commentaire)
        voyelles = re.findall(r"[aeiouyàâéèêëîïôöûü]", commentaire)

        if len(voyelles) == 0 or (len(consonnes) / max(1, len(voyelles))) > 4:
            raise forms.ValidationError("Votre avis ne semble pas être un texte compréhensible.")

        return commentaire

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['mode_paiement', 'telephone', 'adresse_livraison']
        widgets = {
            'mode_paiement': forms.RadioSelect(),
            'telephone': forms.TextInput(attrs={
                'placeholder': '06 12 34 56 78',
                'class': 'form-control'
            }),
            'adresse_livraison': forms.Textarea(attrs={
                'placeholder': 'Adresse complète pour la livraison (optionnel pour emporter)',
                'rows': 3,
                'class': 'form-control'
            }),
        }
        labels = {
            'mode_paiement': 'Mode de paiement',
            'telephone': 'Téléphone',
            'adresse_livraison': 'Adresse de livraison (optionnel)',
        }