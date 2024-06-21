from django import forms
from .models import Driver

class Step1Form(forms.Form):
    drivers = forms.ModelMultipleChoiceField(queryset=Driver.objects.all(), widget=forms.CheckboxSelectMultiple)

class Step2Form(forms.Form):
    file = forms.FileField(label='Seleccionar archivo CSV', widget=forms.FileInput(attrs={'id': 'file', 'class': 'form-control mb-3'}))

class Step3Form(forms.Form):
    phone = forms.CharField(max_length=15)
