
from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, CustomLoginView, CookiePolicyView

urlpatterns = [
    # — Admin de Django —
    path("admin/", admin.site.urls),

    # — Rutas de autenticación nativa de Django (login, logout, password reset…) —
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", include("django.contrib.auth.urls")),  # logout via POST

    # — Registro de nuevos usuarios —
    path("accounts/register/", RegisterView.as_view(), name="register"),

    # — Cambio de idioma (i18n) —
    path("i18n/", include("django.conf.urls.i18n")),

    # — Resto de la app —
    path("", include("recipes.urls")),
    path('cookies/', CookiePolicyView.as_view(),
         name='cookie_policy'),
]