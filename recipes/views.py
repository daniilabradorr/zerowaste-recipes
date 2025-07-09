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

from django.contrib import messages  # Para el mensaje

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
        # ◾️ Lanzo un mensaje por cada nueva insignia
        for assignment in nuevas:
            badge = assignment.badge
            messages.success(
                request,
                _(f"¡Enhorabuena! Has ganado la insignia «{badge.name}» – {badge.description}")
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
        target = "en" if recipe.language == "es" else "es"
        prompt = (
            f"Traduce este título y pasos al "
            f'{"inglés" if target == "en" else "español"}\n\n'
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
    template_name = "recipes/badges.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        # Contar recetas IA y eventos de compartición del usuario
        recetas_generadas = Recipe.objects.filter(created_by=usuario, is_ai=True).count()
        veces_compartido  = ShareEvent.objects.filter(user=usuario).count()

        # Recoger IDs de insignias ya asignadas
        asignadas_ids = BadgeAssignment.objects.filter(user=usuario) \
                                               .values_list("badge_id", flat=True)

        # Preparar lista de "Tus Insignias" con progreso
        insignias_ganadas = []
        for insignia in Badge.objects.filter(id__in=asignadas_ids):
            progreso = recetas_generadas if insignia.metric == "recipes" else veces_compartido
            insignia.progress   = progreso
            insignia.unit_label = dict(Badge.METRIC_CHOICES)[insignia.metric]
            insignias_ganadas.append(insignia)

        # Preparar insignias activas disponibles (aún no conseguidas)
        disponibles = []
        for insignia in Badge.objects.filter(active=True).exclude(id__in=asignadas_ids).order_by("threshold"):
            progreso = recetas_generadas if insignia.metric == "recipes" else veces_compartido
            insignia.progress   = progreso
            insignia.unit_label = dict(Badge.METRIC_CHOICES)[insignia.metric]
            disponibles.append(insignia)

        # Preparar insignias “Próximamente” (inactivas)
        proximamente = []
        for insignia in Badge.objects.filter(active=False).order_by("threshold"):
            insignia.progress   = 0
            insignia.unit_label = dict(Badge.METRIC_CHOICES)[insignia.metric]
            proximamente.append(insignia)

        context.update({
            "owned_badges":     insignias_ganadas,
            "available_badges": disponibles,
            "coming_soon":      proximamente,
        })
        return context
    
@login_required
def share_app(request):
    """
    Registra un ShareEvent, asigna badge 'Partner' cuando llego a 5 compartidos,
    y redirige al share URL (WhatsApp).
    """
    if not request.user.is_authenticated:
        return redirect("login")

    via = request.GET.get("via", "")
    ShareEvent.objects.create(user=request.user, platform=via)

    # Cuento cuántas veces he compartido
    total_shares = ShareEvent.objects.filter(user=request.user).count()
    try:
        partner = Badge.objects.get(name__iexact="partner", active=True)
    except Badge.DoesNotExist:
        partner = None

    # Solo asigno y muestro mensaje cuando alcanzo el umbral de 5 compartidos
    if partner and total_shares >= partner.threshold:
        assigned, created = BadgeAssignment.objects.get_or_create(
            user=request.user,
            badge=partner
        )
        if created:
            messages.success(
                request,
                _(f"¡Enhorabuena! Has ganado la insignia «{partner.name}» – {partner.description}")
            )

    # redirijo a WhatsApp con mensaje
    msg = quote(f"¡Mira ZeroWaste Recipes! {request.build_absolute_uri('/')}" )
    return redirect(f"https://api.whatsapp.com/send?text={msg}")

class MissionView(TemplateView):
    """
    Muestro la página 'Nuestra Misión' con texto adaptado a ES/EN
    """
    template_name = "recipes/mission.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Objetivos genéricos
        ctx['objectives'] = [
            {'icon': '🌱', 'text_es': 'Evitar desperdicio doméstico', 'text_en': 'Avoid household waste'},
            {'icon': '⚡️', 'text_es': 'Medir recorte de CO₂',     'text_en': 'Measure CO₂ reduction'},
            {'icon': '🏆', 'text_es': 'Gamificar sostenibilidad', 'text_en': 'Gamify sustainability'},
            {'icon': '🤝', 'text_es': 'Construir comunidad',       'text_en': 'Build community'},
        ]

        # Pasos de "How It Works"
        ctx['how_it_works'] = [
            {
                'step': 1,
                'title_es': 'Añade tus sobras',
                'desc_es': 'Escanea o escribe los ingredientes que te quedan.',
                'title_en': 'Add your leftovers',
                'desc_en': 'Scan or type the ingredients you have left.'
            },
            {
                'step': 2,
                'title_es': 'IA crea tu receta',
                'desc_es': 'Nuestro modelo Llama-3 genera platos deliciosos y sostenibles.',
                'title_en': 'AI creates your recipe',
                'desc_en': 'Our Llama-3 model crafts tasty, sustainable dishes.'
            },
            {
                'step': 3,
                'title_es': 'Cocina y comparte',
                'desc_es': 'Muestra tu ahorro de CO₂ y gana insignias.',
                'title_en': 'Cook & share',
                'desc_en': 'Show your CO₂ savings and earn badges.'
            },
        ]

        # Beneficios
        ctx['benefits'] = [
            {
                'icon': 'no-waste.svg',
                'title_es': 'Reduce desperdicio',
                'desc_es': 'Da una segunda vida a cada alimento.',
                'title_en': 'Reduce waste',
                'desc_en': 'Give every scrap a second life.'
            },
            {
                'icon': 'co2.svg',
                'title_es': 'Recorta CO₂',
                'desc_es': 'Mide el impacto positivo de cada plato.',
                'title_en': 'Cut CO₂',
                'desc_en': 'Track the positive impact of each dish.'
            },
            {
                'icon': 'creativity.svg',
                'title_es': 'Creatividad al instante',
                'desc_es': 'Ideas sabrosas basadas en lo que ya tienes.',
                'title_en': 'Instant creativity',
                'desc_en': 'Delicious ideas using what you already have.'
            },
            {
                'icon': 'community.svg',
                'title_es': 'Comunidad',
                'desc_es': 'Comparte logros y reta a tus amigos.',
                'title_en': 'Community',
                'desc_en': 'Share achievements and challenge friends.'
            },
        ]

        # Testimonios
        ctx['testimonials'] = [
            {
                'img': 'user1.webp',
                'name': 'Laura',
                'quote_es': '“Ahora ahorro 30 € al mes y mi cubo de basura está casi vacío.”',
                'quote_en': '“I now save €30/month and my trash is almost empty.”'
            },
            {
                'img': 'user2.webp',
                'name': 'Carlos',
                'quote_es': '“Las insignias me pican: ¡no he fallado ni un reto semanal!”',
                'quote_en': '“The badges keep me going—I’ve never missed a weekly challenge!”'
            },
            {
                'img': 'user3.webp',
                'name': 'Aya',
                'quote_es': '“La IA clava mi dieta vegana con lo que hay en mi nevera.”',
                'quote_en': '“The AI nails my vegan diet with what’s in my fridge.”'
            },
        ]

        # FAQs
        ctx['faqs'] = [
            {
                'question_es': '¿Es gratis la app?',
                'answer_es': 'Sí, la funcionalidad básica…',
                'question_en': 'Is the app free?',
                'answer_en': 'Yes, the core recipe & CO₂ calculator is completely free.'
            },
            {
                'question_es': '¿Cómo calcula ZeroWaste Recipes el CO₂ evitado?',
                'answer_es': 'Usamos factores de emisión…',
                'question_en': 'How do you calculate CO₂ saved?',
                'answer_en': 'We use FAO emission factors & peer-reviewed studies.'
            },
            {
                'question_es': '¿Necesito conexión a internet?',
                'answer_es': 'La app es PWA: genera recetas sin conexión…',
                'question_en': 'Do I need internet?',
                'answer_en': 'The PWA works offline & syncs when reconnected.'
            },
            {
                'question_es': '¿La IA hace bien las recetas?',
                'answer_es': '¡Claro! Puedes indicar los alimentos…',
                'question_en': 'Are the AI recipes reliable?',
                'answer_en': 'Absolutely! Tell it your ingredients & it returns full recipes.'
            },
        ]

        return ctx
