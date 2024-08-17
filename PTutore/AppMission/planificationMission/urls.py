from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'planificationMission'

urlpatterns = [
                  path('missions/', views.gestion_mission, name='missions'),

                  path('missions/<int:mission_id>/taches/', views.tache_list, name='tache_list'),
                  path('taches/<int:tache_id>/predecesseurs/', views.predecesseur_manage, name='predecesseur_manage'),
                  path('taches/<int:tache_id>/ressources/', views.ressource_manage, name='ressource_manage'),
                  path('missions/<int:mission_id>/ressourcesMission/', views.ressource_mission_view,
                       name='ressourcesMission_list'),
                  path('missions/<int:mission_id>/affectation/', views.affectation_view, name='affectation'),
                  path('missions/<int:mission_id>/', views.tache_utilisateur, name='tache_utilisateur'),
                  path('missionsUser/', views.utilisateur_missions, name='utilisateur_missions'),
                  path('missions/<int:mission_id>/objectif', views.objectif, name='objectif'),
                  path('notifications/', views.notifications_view, name='notifications'),
                  path('missions/<int:mission_id>/evaluer/', views.evaluer_tache_view, name='evaluer_tache_view'),
                  path('gantt/<int:mission_id>/', views.diagramme_gantt, name='diagramme_gantt'),
                  path('tache/<int:tache_id>/pdf/', views.afficher_pdf, name='afficher_pdf'),
                  path('mission/<int:mission_id>/rapport/', views.generate_pdf_view, name='generate_pdf'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)