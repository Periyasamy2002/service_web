from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import DynamicPage, Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "charges", "documents_required", "tutorial_link", "apply_link", "page"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Enter service name"}),
            "charges": forms.NumberInput(attrs={"class": "form-control form-control-lg", "step": "0.01", "placeholder": "Enter amount"}),
            "documents_required": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Aadhar, PAN, Photo"}),
            "tutorial_link": forms.URLInput(attrs={"class": "form-control form-control-lg", "placeholder": "https://example.com"}),
            "apply_link": forms.URLInput(attrs={"class": "form-control form-control-lg", "placeholder": "https://example.com"}),
            "page": forms.Select(attrs={"class": "form-control form-control-lg"}),
        }


class DynamicPageForm(forms.ModelForm):
    class Meta:
        model = DynamicPage
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "Page name"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Page description"}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"class": "form-control form-control-lg"})
        self.fields['email'].widget.attrs.update({"class": "form-control form-control-lg"})
        self.fields['password1'].widget.attrs.update({"class": "form-control form-control-lg"})
        self.fields['password2'].widget.attrs.update({"class": "form-control form-control-lg"})
