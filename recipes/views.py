from __future__ import annotations  # Para mejorar los type hints sin afectar al código en ejecución

import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils.translation import get_language, gettext_lazy as _
from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Recipe, Ingredient, RecipeIngredient, Badge
from .utils import suggest_recipe

logger = logging.getLogger(__name__)  # para dejar trazas en el log de Render

def home(request) -> HttpResponse:
    """Mi landing page, accesible sin autenticación."""
    #Todas las insignias definidas
    all_badges = Badge.objects.all().order_by('threshold')
    # Insignias que ya ha ganado el usuario
    user_badges = request.user.badges.all() if request.user.is_authenticated else []
    return render(request, "home.html", {
        "all_badges": all_badges,
        "user_badges": user_badges,
    })



class IngredientFormView(LoginRequiredMixin, View):
    """
    Muestro el textarea para que el usuario escriba sus sobras.
    Solo accesible para usuarios autenticados.
    """
    login_url = "login"
    redirect_field_name = "next"
    template_name = "recipes/ingredient_form.html"

    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)


class SuggestView(LoginRequiredMixin, View):
    """
    Recibo la lista de ingredientes por POST, llamo a Groq para generar la receta,
    la guardo y devuelvo la tarjeta parcial para HTMX.
    """
    login_url = "login"
    redirect_field_name = "next"

    def post(self, request) -> HttpResponse:
        raw_ingredients = request.POST.get("ingredients", "").strip()
        if not raw_ingredients:
            return HttpResponse(
                "<p class='text-red-500'>⚠️ Debes introducir al menos un ingrediente.</p>",
                status=400,
            )

        lang = get_language()[:2] or "es"
        try:
            data = suggest_recipe(raw_ingredients, lang)
        except Exception as err:
            logger.error("Error al generar receta IA: %s", err)
            return HttpResponseServerError(
                "<p class='text-red-500'>😔 Lo siento, la IA no pudo generar la receta. Intenta de nuevo.</p>"
            )

        # Creo y guardo la receta generada
        recipe = Recipe.objects.create(
            title=data.get("title"),
            instructions="\n".join(data["steps"]),
            language=lang,
            is_ai=True,
            created_by=request.user,
        )
        # Vinculo ingredientes
        for name in data["ingredients"]:
            ing, _ = Ingredient.objects.get_or_create(name=name)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ing,
                quantity="",
            )

        return render(request, "recipes/_recipe_card.html", {"recipe": recipe})


class TranslateView(LoginRequiredMixin, View):
    """
    Traduzco una receta existente al otro idioma, creo una nueva Recipe
    y copio sus ingredientes, luego devuelvo la tarjeta traducida.
    """
    login_url = "login"
    redirect_field_name = "next"

    def post(self, request, pk) -> HttpResponse:
        recipe = get_object_or_404(Recipe, pk=pk)
        target = "en" if recipe.language == "es" else "es"

        prompt = (
            f"Traduce este título y pasos al "
            f'{"inglés" if target == "en" else "español"}\n\n'
            f'Título: "{recipe.title}"\n'
            f"Pasos:\n{recipe.instructions}"
        )
        try:
            data = suggest_recipe(prompt, target)
        except Exception as err:
            logger.error("Error translating recipe: %s", err)
            return render(
                request,
                "recipes/_recipe_card.html",
                {"recipe": recipe, "error": _("No se pudo traducir. Intenta de nuevo.")},
                status=500,
            )

        # Creo la receta traducida y copio los ingredientes
        translated = Recipe.objects.create(
            title=data.get("title", recipe.title),
            instructions="\n".join(data.get("steps", recipe.instructions.splitlines())),
            language=target,
            is_ai=True,
            created_by=request.user,
        )
        for ri in recipe.ingredients.all():
            RecipeIngredient.objects.create(
                recipe=translated,
                ingredient=ri.ingredient,
                quantity=ri.quantity,
            )

        return render(
            request,
            "recipes/_recipe_card.html",
            {"recipe": translated},
        )
    