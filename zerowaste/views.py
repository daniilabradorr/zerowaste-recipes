from django.shortcuts import redirect
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, TemplateView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model

from django import forms

User = get_user_model()
# — Yo gestiono el registro, auto-login y muestro un mensaje de éxito o error —
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Correo electrónico"),
        required=True,
        widget=forms.EmailInput(attrs={"class": "w-full p-2 border rounded", "placeholder": _("email@example.com")})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")


class RegisterView(CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("recipes:home")  # o la URL de tu home

    def form_valid(self, form):
        # Cuando el formulario es válido, guardo al usuario y le hago login
        user = form.save()
        login(self.request, user)
        messages.success(self.request, _("Registro exitoso. ¡Bienvenido!"))
        return redirect(self.success_url)

    def form_invalid(self, form):
        # Si hay errores, los recorro y muestro con messages.error
        for field, errors in form.errors.items():
            label = form.fields[field].label or field
            for error in errors:
                messages.error(self.request, f"{label}: {error}")
        return super().form_invalid(form)

# — Yo gestiono el login y aviso si fue exitoso o falla —
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = AuthenticationForm

    def form_valid(self, form):
        messages.success(self.request, _("Has iniciado sesión correctamente"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Usuario o contraseña incorrectos"))
        return super().form_invalid(form)
    
class CookiePolicyView(TemplateView):
    """
    Muestro la página estática con nuestra política de cookies.
    """
    template_name = "cookie_policy.html"