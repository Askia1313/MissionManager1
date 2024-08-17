from django.contrib.auth.forms import AuthenticationForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ('email', 'telephone', 'nom', 'prenom','fonction')

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.username:
            user.username = user.email or user.telephone
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email or Phone', max_length=254)

    def confirm_login_allowed(self, user):
        # Ne rien faire ici pour éviter les vérifications d'état actif/inactif
        pass