from django import forms
from Authentification.models import Mission, Objectif, Tache,Predecesseur


class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['titre', 'dateDebut', 'datefin', 'description']
        widgets = {
            'dateDebut': forms.DateInput(attrs={'type': 'date'}),
            'datefin': forms.DateInput(attrs={'type': 'date'}),
        }

class ObjectifForm(forms.ModelForm):
    class Meta:
        model = Objectif
        fields = ['titre', 'description']






class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ['titre', 'description', 'dateCreation', 'dateEcheance']
        widgets = {
            'dateCreation': forms.DateInput(attrs={'type': 'date'}),
            'dateEcheance': forms.DateInput(attrs={'type': 'date'}),
        }
class PredecesseurForm(forms.ModelForm):
    class Meta:
        model = Predecesseur
        fields = ['tache', 'predecesseur']

class TachePredecesseurForm(forms.Form):
    tache_id = forms.IntegerField(widget=forms.HiddenInput())
    predecesseurs = forms.ModelMultipleChoiceField(
        queryset=Tache.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

from django import forms
from Authentification.models import Predecesseur, Ressource


class PredecesseurForm(forms.ModelForm):
    class Meta:
        model = Predecesseur
        fields = ['tache', 'predecesseur']


class RessourceForm(forms.ModelForm):
    class Meta:
        model = Ressource
        fields = ['titre', 'prix', 'description']

