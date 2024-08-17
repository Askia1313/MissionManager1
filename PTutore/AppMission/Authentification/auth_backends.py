from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        user = None
        if '@' in username:
            # Recherche par email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        elif username.isdigit():
            # Recherche par numéro de téléphone
            try:
                user = User.objects.get(telephone=username)
            except User.DoesNotExist:
                return None
        else:
            # Recherche par nom d'utilisateur
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user is not None and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None