# restaurant/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def client_required(function):
    """
    Décorateur pour restreindre l'accès aux clients uniquement
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        
        if hasattr(request.user, 'profile') and request.user.profile.role == 'client':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Cette page est réservée aux clients.")
            return redirect('employe' if request.user.profile.role == 'employe' else 'accueil')
    
    return wrap


def employe_required(function):
    """
    Décorateur pour restreindre l'accès aux employés uniquement
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        
        if hasattr(request.user, 'profile') and request.user.profile.role == 'employe':
            return function(request, *args, **kwargs)
        else:
            messages.error(request, "Cette page est réservée aux employés.")
            return redirect('client' if request.user.profile.role == 'client' else 'accueil')
    
    return wrap


def role_required(allowed_roles):
    """
    Décorateur flexible pour autoriser plusieurs rôles
    Usage: @role_required(['client', 'employe'])
    """
    def decorator(function):
        @wraps(function)
        def wrap(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Vous devez être connecté pour accéder à cette page.")
                return redirect('login')
            
            user_role = request.user.profile.role if hasattr(request.user, 'profile') else None
            
            if user_role in allowed_roles:
                return function(request, *args, **kwargs)
            else:
                messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
                return redirect('accueil')
        
        return wrap
    return decorator