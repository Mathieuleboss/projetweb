from pathlib import Path

# ------------------------------
# Chemins de base
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# Sécurité
# ------------------------------
SECRET_KEY = 'django-insecure-5e3qh%)wm%3=c#)*+ascei$8a29%3e+y9*w$nr_7brz%*esdtl'
DEBUG = True
ALLOWED_HOSTS = []

# ------------------------------
# Applications installées
# ------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Ton app
    'restaurant',
]

# ------------------------------
# Middleware
# ------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'restaurant.middleware.NoCacheMiddleware',  # <-- ajoute cette ligne
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ------------------------------
# URL configuration
# ------------------------------
ROOT_URLCONF = 'projetweb.urls'

# ------------------------------
# Templates
# ------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "restaurant" / "templates"],  # chemin pour templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # <--- nécessaire pour request dans template
                'django.contrib.auth.context_processors.auth',  # <--- nécessaire pour user.is_authenticated
                'django.template.context_processors.csrf',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ------------------------------
# WSGI
# ------------------------------
WSGI_APPLICATION = 'projetweb.wsgi.application'

# ------------------------------
# Base de données
# ------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------
# Validation des mots de passe
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------
# Internationalisation
# ------------------------------
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# ------------------------------
# Fichiers statiques
# ------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "restaurant" / "static",
]

# ------------------------------
# Clé primaire par défaut
# ------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------
# Redirections Login/Logout
# ------------------------------
LOGIN_URL = 'login'  # Nom de l'URL de connexion

# URL de redirection après connexion réussie
LOGIN_REDIRECT_URL = 'accueil'

# URL de redirection après déconnexion
LOGOUT_REDIRECT_URL = 'accueil'

# ------------------------------
# Fichiers médias (images uploadées)
# ------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_ROOT = BASE_DIR / "staticfiles"
ALLOWED_HOSTS = ['*']
