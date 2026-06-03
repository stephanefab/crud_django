from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone", "address"]

        # messages d'erreur en français (sinon "This field is required.")
        error_messages = {
            "first_name": {"required": "Le prénom ne peut pas être vide"},
            "last_name":  {"required": "Le nom ne peut pas être vide"},
            "email":      {"required": "L'email ne peut pas être vide"},
            "phone":      {"required": "Le téléphone ne peut pas être vide"},
            "address":    {"required": "L'adresse ne peut pas être vide"},
        }

        # tes classes Bootstrap + placeholders directement sur les champs
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Fabien"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Martin"}),
            "email":      forms.EmailInput(attrs={"class": "form-control", "placeholder": "fabien.martin@example.com"}),
            "phone":      forms.TextInput(attrs={"class": "form-control", "placeholder": "0612345678"}),
            "address":    forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "12 rue de la Paix"}),
        }

    # remplace tes .strip().title() / .lower() de la vue
    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip().title()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip().title()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_phone(self):
        return self.cleaned_data["phone"].strip()

    def clean_address(self):
        return self.cleaned_data["address"].strip().lower()
