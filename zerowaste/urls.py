
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView 
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


    # — Service Worker (scope global) —
    path(
        "sw.js",
        TemplateView.as_view(
            template_name="sw.js",
            content_type="application/javascript"
        ),
        name="service_worker"
    ),

    # Si algún día pongo también el manifest en la raíz, descomentar:
    # path(
    #     "manifest.json",
    #     TemplateView.as_view(
    #         template_name="manifest.json",
    #         content_type="application/manifest+json"
    #     ),
    #     name="manifest"
    # ),

    # — Resto de la app —
    path("", include("recipes.urls")),
    path('cookies/', CookiePolicyView.as_view(),
         name='cookie_policy'),
]