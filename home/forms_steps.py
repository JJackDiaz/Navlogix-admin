from django import forms
from django.contrib.auth.models import User

class Step1Form(forms.Form):
    drivers = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)

class Step2Form(forms.Form):
    file = forms.FileField(label='Seleccionar archivo CSV', widget=forms.FileInput(attrs={'id': 'file', 'class': 'form-control mb-3'}))


