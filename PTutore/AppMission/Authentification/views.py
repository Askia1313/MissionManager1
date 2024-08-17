
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import random
from .models import Utilisateur
from .forms import UserRegistrationForm, CustomAuthenticationForm
from .auth_backends import CustomBackend
from django.views.decorators.csrf import csrf_exempt



def logout_user(request):
    logout(request)
    return redirect('Authentification:home')

def A_propos(request):
    return render(request, 'A_propos.html')
def home(request):
        return render(request, 'home.html')

@csrf_exempt

def login_user(request):
    message = ''
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = CustomBackend().authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_active:
                    message = 'Votre compte est inactif. Veuillez vérifier votre email pour activer votre compte.'
                    return render(request, 'activation.html', {'message': message})
                else:
                    user.backend = 'Authentification.auth_backends.CustomBackend'
                    auth_login(request, user)
                    if user.is_admin:
                        return redirect('planificationMission:missions')
                    else:
                        return redirect('planificationMission:utilisateur_missions')
            else:
                message = 'Identifiant ou mot de passe incorrect, veuillez réessayer.'
        else:
            message = 'Identifiant ou mot de passe incorrect, veuillez réessayer.'
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form, 'message': message})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.num_mail = random.randint(100000, 999999)
            user.save()

            subject = "Activation de votre compte "
            body = render_to_string('activate_email.html', {'user': user})

            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            send_mail.content_subtype = "html"

            return render(request, 'activation.html', {'user': user})
        else:
            messages.error(request, 'Le formulaire n\'est pas valide. Veuillez corriger les erreurs.')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def verifier_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')

        try:
            user = Utilisateur.objects.get(email=email)
            if int(code) == int(user.num_mail):
                user.is_active = True
                user.save()
                user.backend = 'Authentification.auth_backends.CustomBackend'  # Specify the backend
                auth_login(request, user)
                #if user.is_admin:
                return redirect('planificationMission:missions')
                #else:
                    #return redirect('planificationMission:missionsUser')
            else:
                info2 = "Code invalide, veuillez réessayer"
                return render(request, "activation.html", {'info2': info2})
        except Utilisateur.DoesNotExist:
            info2 = "Vous avez entré un mauvais email, veuillez réessayer"
            return render(request, "activation.html", {'info2': info2})
    else:
        return render(request, "activation.html")

