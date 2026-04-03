from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DynamicPage, Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "charges", "documents_required", "tutorial_link", "apply_link"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "charges": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "documents_required": forms.TextInput(attrs={"class": "form-control", "placeholder": "Aadhar, PAN, Photo"}),
            "tutorial_link": forms.URLInput(attrs={"class": "form-control"}),
            "apply_link": forms.URLInput(attrs={"class": "form-control"}),
        }


class DynamicPageForm(forms.ModelForm):
    class Meta:
        model = DynamicPage
        fields = ["name", "description"]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
