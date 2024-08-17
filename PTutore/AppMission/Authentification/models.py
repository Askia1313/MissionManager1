from django.db import models
from django.contrib.auth.models import AbstractUser

# Utilisateur personnalisé héritant d'AbstractUser
class Utilisateur(AbstractUser):
    nom=models.CharField(max_length=20)
    prenom=models.CharField(max_length=20)
    fonction=models.CharField(max_length=150)
    telephone=models.IntegerField()
    email=models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)  # Champ pour indiquer si l'utilisateur est un administrateur
    num_mail=models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['telephone', 'nom', 'prenom']

    def __str__(self):
        return self.username

# Mission model
class Mission(models.Model):
    titre = models.CharField(max_length=255)
    dateDebut = models.DateField()
    datefin = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.titre

# Objectif spécifique model
class Objectif(models.Model):
    titre = models.CharField(max_length=255)
    mission = models.ForeignKey(Mission, related_name='objectifs', on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return self.description

# Tache model
class Tache(models.Model):
    ETAT_CHOICES = [
        (1, 'En attente'),
        (2, 'En cours'),
        (3, 'Terminé'),
    ]
    titre = models.CharField(max_length=255)
    description = models.TextField()
    dateCreation = models.DateField()
    dateEcheance = models.DateField()
    dateFin = models.DateField(null=True, blank=True)  # Champ dateFin optionnel
    mission = models.ForeignKey(Mission, related_name='taches', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, related_name='taches', on_delete=models.SET_NULL, null=True)
    pdf = models.FileField(upload_to='pdfs/', null=True, blank=True)  # Champ PDF
    etat = models.IntegerField(choices=ETAT_CHOICES, default=1)  # Champ état avec valeurs 1, 2, 3

class Predecesseur(models.Model):
    tache = models.ForeignKey(Tache, related_name='pred_taches', on_delete=models.CASCADE)
    predecesseur = models.ForeignKey(Tache, related_name='succ_taches', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tache', 'predecesseur')


    def __str__(self):
        return self.description

# Ressource model

class Ressource(models.Model):
    mission = models.ForeignKey(Mission, related_name='ressources', on_delete=models.CASCADE)
    tache = models.ForeignKey(Tache, related_name='ressources', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    titre = models.CharField(max_length=255)  # Nouveau champ titre de type texte
    prix = models.DecimalField(max_digits=10, decimal_places=2)  # Nouveau champ prix de type réel

    def __str__(self):
        return self.titre  # Modifier pour afficher le titre


# Rapport de progression model
class RapportProgress(models.Model):
    dateRapport = models.DateField()
    mission = models.ForeignKey(Mission, related_name='rapports', on_delete=models.CASCADE)
    taches = models.ManyToManyField(Tache, related_name='rapports')
    contenu = models.TextField()
    retour = models.TextField()

    def __str__(self):
        return f"Rapport de {self.mission.titre}"

# Evaluation model
class Evaluation(models.Model):
    dateEvaluation = models.DateField()
    tache = models.ForeignKey(Tache, related_name='evaluations', on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()

    def __str__(self):
        return f"Evaluation de {self.tache.description}"

# Notification model
class Notification(models.Model):
    admin = models.ForeignKey(Utilisateur, related_name='notifications_creees', on_delete=models.CASCADE, limit_choices_to={'is_admin': True})
    est_lu=models.BooleanField(default=False)
    date_creation = models.DateField(auto_now_add=True)
    utilisateur = models.ForeignKey(Utilisateur, related_name='notifications_recues', on_delete=models.CASCADE)
    messages = models.TextField()
    tache = models.ForeignKey(Tache, on_delete=models.CASCADE)
    def __str__(self):
        return f"Notification pour {self.utilisateur.username} par {self.admin.username}"