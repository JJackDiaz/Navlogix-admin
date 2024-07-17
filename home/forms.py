from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Company,UserProfile

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Selecciona un archivo')

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'phone', 'email']

class UserProfileCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True)
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Group')  # Agregar campo para seleccionar grupo

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'company', 'group')  # Incluir 'group' en los campos

    def save(self, commit=True):
        user = super(UserProfileCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user_profile = UserProfile(user=user, company=self.cleaned_data['company'])
            user_profile.save()
            # Asignar al grupo seleccionado
            group = self.cleaned_data['group']
            user.groups.add(group)
        return user