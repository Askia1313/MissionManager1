
from django.urls import path
from .views import logout_user,login_user,register,verifier_email,home,A_propos


app_name = "Authentification"
urlpatterns = [
    path('login/',login_user,name='login'),
    path('logout/',logout_user,name='logout'),
    path('register/',register,name='register'),
    path('verifier_email/',verifier_email,name='verifier_email'),
    path('', home, name='home'),
    path('A_propos',A_propos,name='A_propos'),

]
