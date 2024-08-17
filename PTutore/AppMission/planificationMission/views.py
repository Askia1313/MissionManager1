from django.shortcuts import render, redirect, get_object_or_404
from Authentification.models import Mission, Objectif, Tache, Predecesseur, Ressource , Evaluation, Notification  # Assurez-vous d'importer correctement le modèle Mission
from .forms import MissionForm,ObjectifForm, TacheForm, TachePredecesseurForm, RessourceForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

@csrf_protect
@login_required
def gestion_mission(request):
    missions = Mission.objects.all()
    form = MissionForm()

    if request.method == 'POST':
        if 'create' in request.POST:
            form = MissionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('planificationMission:missions')
        elif 'update' in request.POST:
            mission_id = request.POST.get('mission_id')
            mission = get_object_or_404(Mission, id=mission_id)
            form = MissionForm(request.POST, instance=mission)
            if form.is_valid():
                form.save()
                return redirect('planificationMission:missions')
        elif 'delete' in request.POST:
            mission_id = request.POST.get('mission_id')
            mission = get_object_or_404(Mission, id=mission_id)
            mission.delete()
            return redirect('planificationMission:missions')

    return render(request, 'gestionMission.html', {'missions': missions, 'form': form})



# Vue pour lister et gérer les tâches
from django.http import JsonResponse

@csrf_protect
@login_required
def tache_list(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    taches = Tache.objects.filter(mission=mission)
    tache_form = TacheForm()

    if request.method == 'POST':
        if 'save_tache' in request.POST:
            form = TacheForm(request.POST)
            if form.is_valid():
                tache = form.save(commit=False)
                tache.mission = mission
                tache.save()
                return redirect('planificationMission:tache_list', mission_id=mission_id)
        elif 'edit_tache' in request.POST:
            tache_id = request.POST.get('tache_id')
            tache = get_object_or_404(Tache, id=tache_id)
            form = TacheForm(request.POST, instance=tache)
            if form.is_valid():
                form.save()
                return redirect('planificationMission:tache_list', mission_id=mission_id)

    elif request.method == 'GET' and 'delete_tache_id' in request.GET:
        tache_id = request.GET.get('delete_tache_id')
        tache = get_object_or_404(Tache, id=tache_id)
        tache.delete()
        return JsonResponse({'success': True})

    return render(request, 'taches.html', {'mission': mission, 'taches': taches, 'tache_form': tache_form})

# Vue pour gérer les prédécesseurs d'une tâche

@csrf_protect
@login_required
def predecesseur_manage(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)
    mission = tache.mission

    # Obtenir les prédécesseurs de la tâche actuelle
    pred_ids = Predecesseur.objects.filter(tache=tache).values_list('predecesseur_id', flat=True)
    predecesseurs = Tache.objects.filter(id__in=pred_ids)

    # Obtenir les autres tâches de la mission
    autres_taches = Tache.objects.filter(mission=mission).exclude(id__in=pred_ids).exclude(id=tache_id)

    action = request.GET.get('action')
    pred_tache_id = request.GET.get('pred_tache_id')

    if action and pred_tache_id:
        pred_tache = get_object_or_404(Tache, id=pred_tache_id)

        if action == 'ajouter':
            try:
                Predecesseur.objects.create(tache=tache, predecesseur=pred_tache)
            except IntegrityError:
                # Handle duplicate entry gracefully
                print("This predecesseur is already added.")
        elif action == 'banir':
            try:
                predecesseur = get_object_or_404(Predecesseur, tache=tache, predecesseur=pred_tache)
                predecesseur.delete()
            except Predecesseur.DoesNotExist:
                # Handle case where the entry does not exist
                print("This predecesseur was not found.")

        return redirect('planificationMission:predecesseur_manage', tache_id=tache_id)

    return render(request, 'predecesseur.html', {
        'tache': tache,
        'predecesseurs': predecesseurs,
        'autres_taches': autres_taches
    })

# Vue pour gérer les ressources d'une tâche
@csrf_protect
@login_required
def ressource_manage(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)
    ressources = Ressource.objects.filter(tache=tache)

    if request.method == 'POST':
        description = request.POST.get('description')
        Ressource.objects.create(tache=tache, description=description)
        return redirect('ressource_manage', tache_id=tache.id)

    return render(request, 'ressource.html', {'tache': tache, 'ressources': ressources})


@csrf_protect
@login_required
def ressource_manage(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)
    mission = tache.mission
    ressources = Ressource.objects.filter(tache=tache)
    ressource_form = RessourceForm()

    if 'add_ressource' in request.GET:
        ressource_form = RessourceForm(request.GET)
        if ressource_form.is_valid():
            ressource = ressource_form.save(commit=False)
            ressource.tache = tache
            ressource.mission = mission
            ressource.save()
            return redirect('planificationMission:ressource_manage', tache_id=tache_id)

    if 'delete_ressource' in request.GET:
        ressource_id = request.GET.get('ressource_id')
        ressource = get_object_or_404(Ressource, id=ressource_id)
        ressource.delete()
        return redirect('planificationMission:ressource_manage', tache_id=tache_id)

    if 'edit_ressource' in request.GET:
        ressource_id = request.GET.get('ressource_id')
        ressource = get_object_or_404(Ressource, id=ressource_id)
        ressource_form = RessourceForm(request.GET, instance=ressource)
        if ressource_form.is_valid():
            ressource_form.save()
            return redirect('planificationMission:ressource_manage', tache_id=tache_id)

    return render(request, 'ressource.html', {
        'tache': tache,
        'ressources': ressources,
        'ressource_form': ressource_form,
    })


#vue pour les ressources de la mission
@csrf_protect
@login_required
def ressource_mission_view(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    taches = mission.taches.all()

    budget_total = 0
    tache_ressources = []

    for tache in taches:
        ressources = tache.ressources.all()
        total_tache = sum(ressource.prix for ressource in ressources)
        budget_total += total_tache
        tache_ressources.append({
            'tache': tache,
            'ressources': ressources,
            'total': total_tache
        })

    return render(request, 'ressourceMission.html', {
        'mission': mission,
        'tache_ressources': tache_ressources,
        'budget_total': budget_total
    })




###vue pour affectation des missions aux utilisateurs
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import ModelMultipleChoiceField, Form
from django import forms
from Authentification.models import Utilisateur, Tache, Mission



@csrf_protect
@login_required
class TacheAffectationForm(Form):
    taches = ModelMultipleChoiceField(queryset=Tache.objects.none(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        mission = kwargs.pop('mission', None)
        super(TacheAffectationForm, self).__init__(*args, **kwargs)
        if mission:
            self.fields['taches'].queryset = Tache.objects.filter(mission=mission, utilisateur__isnull=True)


@csrf_protect
@login_required
def affectation_view(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    utilisateurs = Utilisateur.objects.all()
    utilisateurs_taches = []

    for utilisateur in utilisateurs:
        taches_utilisateur = utilisateur.taches.filter(mission=mission)
        utilisateurs_taches.append({
            'utilisateur': utilisateur,
            'taches': taches_utilisateur
        })

    if request.method == 'POST':
        utilisateur_id = request.POST.get('utilisateur_id')
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        tache_ids = request.POST.getlist('taches')
        if 'affecter' in request.POST:
            Tache.objects.filter(id__in=tache_ids).update(utilisateur=utilisateur)
        elif 'omettre' in request.POST:
            tache_id = request.POST.get('tache_id')
            tache = get_object_or_404(Tache, id=tache_id)
            tache.utilisateur = None
            tache.save()
        return redirect('planificationMission:affectation', mission_id=mission_id)

    taches_disponibles = Tache.objects.filter(mission=mission, utilisateur__isnull=True)

    return render(request, 'affectation.html', {
        'mission': mission,
        'utilisateurs_taches': utilisateurs_taches,
        'taches_disponibles': taches_disponibles,
    })

@csrf_protect
@login_required
def utilisateur_missions(request):
    utilisateur = request.user
    missions = Mission.objects.filter(taches__utilisateur=utilisateur).distinct()
    return render(request, 'utilisateur.html', {'missions': missions})



#### vue pour les taches des utilisateurs
from django.utils import timezone

@csrf_protect
@login_required
def tache_utilisateur(request, mission_id):
    # Récupère l'utilisateur connecté
    utilisateur = request.user

    # Récupère la mission en fonction de l'ID fourni
    mission = get_object_or_404(Mission, id=mission_id)

    # Récupère les tâches assignées à l'utilisateur connecté pour la mission donnée
    taches = Tache.objects.filter(utilisateur=utilisateur, mission=mission)

    if request.method == 'POST':
        # Récupère l'ID de la tâche depuis le formulaire
        tache_id = request.POST.get('tache_id')
        tache = get_object_or_404(Tache, id=tache_id)

        # Récupère l'action du bouton cliqué (commencer ou terminer)
        action = request.POST.get('action')

        if action == 'start':
            # Vérification des prédécesseurs : toutes les tâches prédécesseurs doivent être terminées
            pred_taches = Predecesseur.objects.filter(tache=tache)
            if all(pred.predecesseur.etat == 3 for pred in pred_taches):
                # Si les prédécesseurs sont tous terminés, on passe la tâche à "En cours"
                tache.etat = 2
                tache.save()
            else:
                # Gérer le cas où tous les prédécesseurs ne sont pas terminés (ex: message d'erreur)
                pass

        elif action == 'finish':
            # Récupère le fichier PDF envoyé dans le formulaire
            pdf_file = request.FILES.get('pdf_file')
            if pdf_file:
                # Si un fichier est fourni, on l'associe à la tâche et on met la tâche à "Terminé"
                tache.pdf = pdf_file
                tache.etat = 3
                tache.dateFin = timezone.now().date()  # Met à jour la date de fin
                tache.save()

        # Redirige vers la même page après traitement du formulaire
        return redirect('planificationMission:tache_utilisateur', mission_id=mission.id)

    # Rend la page avec la liste des tâches assignées à l'utilisateur pour la mission spécifiée
    return render(request, 'tacheUtilisateurs.html', {'taches': taches})
def objectif(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)

    # Handle form submissions
    if request.method == 'POST':
        if 'add_objectif' in request.POST:
            form = ObjectifForm(request.POST)
            if form.is_valid():
                objectif = form.save(commit=False)
                objectif.mission = mission
                objectif.save()
                return redirect('planificationMission:objectif', mission_id=mission.id)
        elif 'update_objectif' in request.POST:
            objectif_id = request.POST.get('objectif_id')
            objectif = get_object_or_404(Objectif, id=objectif_id)
            form = ObjectifForm(request.POST, instance=objectif)
            if form.is_valid():
                form.save()
                return redirect('planificationMission:objectif', mission_id=mission.id)
        elif 'delete_objectif' in request.POST:
            objectif_id = request.POST.get('objectif_id')
            objectif = get_object_or_404(Objectif, id=objectif_id)
            objectif.delete()
            return redirect('planificationMission:objectif', mission_id=mission.id)

    objectifs = mission.objectifs.all()
    objectif_form = ObjectifForm()

    return render(request, 'objectif.html', {
        'mission': mission,
        'objectifs': objectifs,
        'objectif_form': objectif_form
    })

###vue pour evaluer

def evaluer_tache_view(request, mission_id):
    taches = Tache.objects.filter(mission_id=mission_id)
    mission = get_object_or_404(Mission, id=mission_id)
    taches_terminees = taches.filter(etat=3).count()
    total_taches = taches.count()
    progression = (taches_terminees / total_taches) * 100 if total_taches > 0 else 0

    if request.method == 'POST':
        if 'evaluation' in request.POST:
            # Sauvegarder l'évaluation
            tache_id = request.POST.get('tache_id')
            tache = get_object_or_404(Tache, id=tache_id)
            note = request.POST.get('note')
            commentaire = request.POST.get('commentaire')
            Evaluation.objects.create(tache=tache, note=note, commentaire=commentaire, dateEvaluation=timezone.now())
            return redirect('evaluer_tache_view', mission_id=mission_id)

        elif 'notification' in request.POST:
            # Sauvegarder la notification
            tache_id = request.POST.get('tache_id')
            tache = get_object_or_404(Tache, id=tache_id)
            message = request.POST.get('message')
            Notification.objects.create(
                utilisateur=tache.utilisateur,
                messages=message,
                admin=request.user,
                tache=tache  # Ajout de la tâche à la notification
            )
            return redirect('planificationMission:evaluer_tache_view', mission_id=mission_id)

    return render(request, 'evaluerTache.html', {
        'taches': taches,
        'mission': mission,
        'progression': progression,
    })


def notifications_non_lues(request):
    if request.user.is_authenticated:
        notifications_non_lues_count = Notification.objects.filter(
            utilisateur=request.user,
            est_lu=False
        ).count()
    else:
        notifications_non_lues_count = 0
    return {
        'notifications_non_lues_count': notifications_non_lues_count
    }


###notification

def notifications_view(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(utilisateur=request.user).select_related('tache__mission').order_by('-date_creation')
    else:
        notifications = []

    if request.method == "POST":
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id, utilisateur=request.user)
                notification.est_lu = True
                notification.save()
            except Notification.DoesNotExist:
                pass

    return render(request, 'notification.html', {
        'notifications': notifications,
    })


from datetime import timedelta


def diagramme_gantt(request, mission_id):
    mission = Mission.objects.get(id=mission_id)
    taches = mission.taches.all()

    taches_info = []
    for tache in taches:
        predecesseurs = tache.pred_taches.all()
        duree = (tache.dateEcheance - tache.dateCreation).days  # Calcul de la durée en jours
        taches_info.append({
            'tache': tache,
            'predecesseurs': predecesseurs,
            'duree': duree,
        })

    context = {
        'mission': mission,
        'taches_info': taches_info,
    }

    return render(request, 'diagrammeGantt.html', context)

###pdf
def afficher_pdf(request, tache_id):
    tache = get_object_or_404(Tache, id=tache_id)
    context = {
        'tache': tache,
    }
    return render(request, 'taches.html', context)


#####generer pdf
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import datetime


def generate_pdf_view(request, mission_id):
    mission = Mission.objects.get(id=mission_id)
    objectifs = mission.objectifs.all()
    taches = mission.taches.all()
    ressources = mission.ressources.all()
    rapports = mission.rapports.all()

    taches_info = []
    for tache in taches:
        predecesseurs = tache.pred_taches.all()
        duree = (tache.dateEcheance - tache.dateCreation).days  # Calcul de la durée en jours
        taches_info.append({
            'tache': tache,
            'predecesseurs': predecesseurs,
            'duree': duree,
        })

    context = {
        'taches_info': taches_info,
        'mission': mission,
        'objectifs': objectifs,
        'taches': taches,
        'ressources': ressources,
        'rapports': rapports,
        'date': datetime.date.today(),
    }

    html = render_to_string('mission_report_template.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_mission_{mission_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response