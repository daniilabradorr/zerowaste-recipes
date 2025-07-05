from __future__ import annotations
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView
from django.utils.translation import get_language, gettext_lazy as _
from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


from urllib.parse import quote

from .models import Recipe, Ingredient, RecipeIngredient, Badge, BadgeAssignment, ShareEvent
from .utils   import suggest_recipe

logger = logging.getLogger(__name__)

def home(request) -> HttpResponse:
    """
    Landing page: muestro todas las insignias y las que el usuario ya tiene.
    """
    all_badges  = Badge.objects.all().order_by("threshold")
    user_badges = request.user.badges.all() if request.user.is_authenticated else []
    return render(request, "home.html", {
        "all_badges":  all_badges,
        "user_badges": user_badges,
    })

class IngredientFormView(LoginRequiredMixin, View):
    login_url           = "login"
    redirect_field_name = "next"
    template_name       = "recipes/ingredient_form.html"
    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)

class SuggestView(LoginRequiredMixin, View):
    """
    POST = recibo la lista de ingredientes, llamo a la IA para generar la receta,
    guardo la receta + sus ingredientes, y devuelvo el fragmento HTML para HTMX,
    incluyendo 'nuevas_badges' si el usuario acaba de ganar alguna.
    """
    login_url           = "login"
    redirect_field_name = "next"

    def post(self, request) -> HttpResponse:
        # 1️⃣ Leo y valido el input
        raw = request.POST.get("ingredients", "").strip()
        if not raw:
            return HttpResponse(
                "<p class='text-red-500'>⚠️ Debes introducir al menos un ingrediente.</p>",
                status=400
            )

        # 2️⃣ Determino idioma y llamo al helper de IA
        lang = get_language()[:2] or "es"
        try:
            data = suggest_recipe(raw, lang)
        except Exception as err:
            logger.error("Error IA: %s", err)
            return HttpResponseServerError(
                "<p class='text-red-500'>😔 La IA falló. Intenta de nuevo.</p>"
            )

        # 3️⃣ Creo y guardo la receta
        recipe = Recipe.objects.create(
            title=data.get("title"),
            instructions="\n".join(data["steps"]),
            language=lang,
            is_ai=True,
            created_by=request.user,
        )

        # 4️⃣ Vinculo cada ingrediente
        for name in data["ingredients"]:
            ing, _ = Ingredient.objects.get_or_create(name=name)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ing,
                quantity="",
            )

        # 5️⃣ Detecto si acabo de ganar alguna insignia
        nuevas = BadgeAssignment.objects.filter(
            user=request.user,
            assigned_at__gte=recipe.created_at
        )

        # 6️⃣ Devuelvo la tarjeta + posibles nuevas_badges
        return render(
            request,
            "recipes/_recipe_card.html",
            {
                "recipe": recipe,
                "nuevas_badges": list(nuevas),  # envía lista (vacía o con items)
            }
        )

class TranslateView(LoginRequiredMixin, View):
    login_url           = "login"
    redirect_field_name = "next"
    def post(self, request, pk) -> HttpResponse:
        recipe = get_object_or_404(Recipe, pk=pk)
        target = "en" if recipe.language=="es" else "es"
        prompt = (
            f"Traduce este título y pasos al "
            f'{"inglés" if target=="en" else "español"}\n\n'
            f'Título: "{recipe.title}"\nPasos:\n{recipe.instructions}'
        )
        try:
            data = suggest_recipe(prompt, target)
        except Exception as err:
            logger.error("Error traducción: %s", err)
            return render(request, "recipes/_recipe_card.html",
                          {"recipe": recipe, "error": _("No se pudo traducir.")},
                          status=500)
        translated = Recipe.objects.create(
            title=data.get("title", recipe.title),
            instructions="\n".join(data.get("steps", recipe.instructions.splitlines())),
            language=target, is_ai=True, created_by=request.user
        )
        for ri in recipe.ingredients.all():
            RecipeIngredient.objects.create(recipe=translated, ingredient=ri.ingredient, quantity=ri.quantity)
        return render(request, "recipes/_recipe_card.html", {"recipe": translated})

class BadgeListView(LoginRequiredMixin, TemplateView):
    template_name       = "recipes/badges.html"
    login_url           = "login"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        ctx          = super().get_context_data(**kwargs)
        user         = self.request.user
        all_badges   = Badge.objects.order_by("threshold")

        recipes_count = Recipe.objects.filter(created_by=user, is_ai=True).count()
        shares_count  = ShareEvent.objects.filter(user=user).count()

        owned_badges     = []
        available_badges = []
        coming_soon      = []

        for badge in all_badges:
            # Si ya la tiene asignada
            if BadgeAssignment.objects.filter(user=user, badge=badge).exists():
                badge.progress = badge.threshold  # completada
                owned_badges.append(badge)
                continue

            # Determinar métrica y unidad
            name = badge.name.strip().lower()
            if name == "partner":
                progress = shares_count
                unit = _("compartidos")
            else:
                progress = recipes_count
                unit = _("recetas IA")

            badge.unit_label = unit
            badge.progress   = progress

            if progress >= badge.threshold:
                available_badges.append(badge)
            else:
                coming_soon.append(badge)

        ctx.update({
            "owned_badges":     owned_badges,
            "available_badges": available_badges,
            "coming_soon":      coming_soon,
        })
        return ctx
    
    
@login_required
def share_app(request):
    """
    Registra un ShareEvent, asigna badge 'Partner' cuando llegan a threshold,
    y redirige al share URL (WhatsApp).
    """
    if not request.user.is_authenticated:
        return redirect("login")

    via = request.GET.get("via", "")
    ShareEvent.objects.create(user=request.user, platform=via)

    # ¿Partner?
    total_shares = ShareEvent.objects.filter(user=request.user).count()
    try:
        partner = Badge.objects.get(name__iexact="partner", active=True)
    except Badge.DoesNotExist:
        partner = None

    if partner and total_shares >= partner.threshold:
        BadgeAssignment.objects.get_or_create(user=request.user, badge=partner)

    # redirijo a WhatsApp con mensaje
    msg = quote(f"¡Mira ZeroWaste Recipes! {request.build_absolute_uri('/')}")
    return redirect(f"https://api.whatsapp.com/send?text={msg}")


class MissionView(TemplateView):
    """
    Muestro la página 'Nuestra Misión' con texto adaptado a ES/EN
    """
    template_name = "recipes/mission.html"