from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label=_("Correo electrónico"),
        widget=forms.EmailInput(attrs={"class": "w-full p-2 border rounded"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": _("Usuario"),
            "password1": _("Contraseña"),
            "password2": _("Confirmar contraseña"),
        }
