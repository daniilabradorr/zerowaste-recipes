from __future__ import annotations
import logging
import re
import unicodedata
import difflib

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()
logger = logging.getLogger(__name__)


# 1️⃣ Huella de CO₂ (kg CO₂-eq por kg)
CO2_EMISSIONS: dict[str, float] = {
    # carnes y pescados
    "beef": 99.5, "lamb": 39.7, "pork": 12.3, "chicken": 9.9,
    "turkey": 10.9, "duck": 11.4, "salmon": 6.1, "tuna": 6.0,
    # lácteos y huevos
    "milk": 3.0, "cheese": 23.9, "yogurt": 2.2, "butter": 12.0, "eggs": 4.5,
    # proteínas vegetales
    "tofu": 3.7, "tempeh": 2.0, "lentils": 4.2, "chickpeas": 1.1,
    "beans": 0.7, "peas": 1.0, "peanuts": 2.5,
    # cereales y tubérculos
    "rice": 2.6, "wheat": 1.4, "oats": 1.6, "barley": 1.3,
    "corn": 1.1, "potatoes": 0.5, "sweet potato": 0.6,
    # verduras y hortalizas
    "tomato": 1.0, "lettuce": 0.45, "cucumber": 0.7, "carrot": 0.38,
    "broccoli": 1.8, "spinach": 1.2, "pepper": 1.5, "onion": 0.8,
    "garlic": 1.1, "eggplant": 1.3, "zucchini": 1.1,
    # frutas
    "apple": 0.9, "banana": 0.8, "orange": 0.7, "grapes": 1.1,
    "strawberry": 1.7, "blueberry": 1.3, "pear": 1.0,
    # frutos secos y semillas
    "almonds": 2.3, "walnuts": 1.5, "cashews": 2.2,
    "sunflower seeds": 1.1, "chia seeds": 1.8, "pumpkin seeds": 1.2,
    # aceites y grasas
    "olive oil": 6.0, "canola oil": 3.1, "coconut oil": 7.6,
    # bebidas y otros
    "coffee": 17.2, "tea": 8.0, "wine": 1.2, "beer": 0.45,
    "juice": 1.0, "soda": 0.6, "sugar": 3.0, "salt": 0.02,
    "flour": 1.1, "bread": 1.4, "chocolate": 19.7, "honey": 2.0,
    "vinegar": 1.5,
}

# 2️⃣ Mapeo ES → EN
SPANISH_TO_EN: dict[str, str] = {
    "carne de vaca": "beef", "cordero": "lamb", "cerdo": "pork",
    "pollo": "chicken", "pavo": "turkey", "pato": "duck",
    "salmón": "salmon", "atún": "tuna",
    "leche": "milk", "queso": "cheese", "yogur": "yogurt",
    "mantequilla": "butter", "huevos": "eggs",
    "tofu": "tofu", "tempeh": "tempeh", "lentejas": "lentils",
    "garbanzos": "chickpeas", "frijoles": "beans", "guisantes": "peas",
    "cacahuetes": "peanuts",
    "arroz": "rice", "trigo": "wheat", "avena": "oats",
    "cebada": "barley", "maíz": "corn", "patatas": "potatoes",
    "batata": "sweet potato",
    "tomate": "tomato", "lechuga": "lettuce", "pepino": "cucumber",
    "zanahoria": "carrot", "brócoli": "broccoli", "espinacas": "spinach",
    "pimiento": "pepper", "cebolla": "onion", "ajo": "garlic",
    "berenjena": "eggplant", "calabacín": "zucchini",
    "manzana": "apple", "plátano": "banana", "naranja": "orange",
    "uvas": "grapes", "fresa": "strawberry", "arándanos": "blueberry",
    "pera": "pear",
    "almendras": "almonds", "nueces": "walnuts", "anacardos": "cashews",
    "piparras": "sunflower seeds", "semillas de chía": "chia seeds",
    "semillas de calabaza": "pumpkin seeds",
    "aceite de oliva": "olive oil", "aceite de canola": "canola oil",
    "aceite de coco": "coconut oil",
    "café": "coffee", "té": "tea", "vino": "wine", "cerveza": "beer",
    "zumo": "juice", "refresco": "soda",
    "azúcar": "sugar", "sal": "salt", "harina": "flour", "pan": "bread",
    "chocolate": "chocolate", "miel": "honey", "vinagre": "vinegar",
}


class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    LANGUAGE_CHOICES = [
        ("es", _("Español")),
        ("en", _("English")),
    ]

    title        = models.CharField(max_length=200)
    instructions = models.TextField()
    language     = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default="es")
    is_ai        = models.BooleanField(default=False)
    created_by   = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

    def _normalize(self, raw: str) -> str:
        """
        1. Quito todo menos letras y espacios.
        2. Paso a minúsculas y quito tildes.
        3. Divido en tokens y, de atrás hacia adelante,
           devuelvo el primero que casé en CO2_EMISSIONS o SPANISH_TO_EN.
        4. Si nada, intento fuzzy match.
        """
        txt = re.sub(r"[^A-Za-zÀ-ÿ ]+", " ", raw)
        txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode().lower()
        tokens = txt.split()

        for token in reversed(tokens):
            if token in CO2_EMISSIONS:
                return token
            if token in SPANISH_TO_EN:
                return SPANISH_TO_EN[token]

        match = difflib.get_close_matches(" ".join(tokens), list(CO2_EMISSIONS), n=1, cutoff=0.8)
        return match[0] if match else ""

    def calc_footprint(self) -> float | None:
        total = 0.0
        missing: list[str] = []
        for ri in self.ingredients.all():
            key = self._normalize(ri.ingredient.name)
            if key:
                total += CO2_EMISSIONS[key]
            else:
                missing.append(ri.ingredient.name)

        if missing:
            logger.warning("Sin huella CO₂ para: %s", missing)
            return None
        return round(total, 2)

    def footprint_display(self) -> str:
        fp = self.calc_footprint()
        if fp is None:
            return _("No se puede calcular la huella de CO₂ para algunos ingredientes.")
        return _("{value} kg CO₂eq").format(value=fp)


class RecipeIngredient(models.Model):
    recipe     = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity   = models.CharField(max_length=80, blank=True)


class Leftover(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leftovers")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    added_at   = models.DateTimeField(auto_now_add=True)


# —————————————————————————————————————————
# Nuevo: registro de cada “compartición”
class ShareEvent(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="share_events")
    platform   = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} shared via {self.platform} @ {self.created_at}"


# —————————————————————————————————————————
# Insignias y asignaciones
class Badge(models.Model):
    """
    Yo creo una insignia con:
    - name:       nombre único
    - icon:       imagen SVG/PNG o emoji
    - description: texto que explica qué es la insignia y qué beneficio ofrece
    - threshold:  cuántas acciones (recetas, compartidos…) para desbloquearla
    - active:     si ya está disponible o es “próximamente”
    - discount:   porcentaje de descuento futuro (opcional)
    """
    name        = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Ej. Starter, Eco-Hero")
    )
    icon        = models.ImageField(
        upload_to="badges/",
        help_text=_("SVG o PNG para mostrar en la UI")
    )
    description = models.TextField(
        default="",
        blank=True,
        help_text=_("Descripción de la insignia y beneficio que otorga")
    )
    threshold   = models.PositiveIntegerField(
        default=0,
        help_text=_("Número de acciones necesarias para desbloquear")
    )
    active      = models.BooleanField(
        default=True,
        help_text=_("Si ya está disponible o aparece como Próximamente")
    )
    discount    = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Descuento (%) que ofrece esta insignia cuando esté activa")
    )


class BadgeAssignment(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name="badges")
    badge       = models.ForeignKey(Badge, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")
        ordering        = ["-assigned_at"]


# Señal para asignar automáticamente Starter/Eco-Hero (por recetas IA)
@receiver(post_save, sender=Recipe)
def assign_recipes_badges(sender, instance, created, **kwargs):
    if not created or not instance.is_ai or not instance.created_by:
        return
    user  = instance.created_by
    total = sender.objects.filter(created_by=user, is_ai=True).count()
    for b in Badge.objects.filter(active=True, threshold__gt=0, threshold__lte=total):
        BadgeAssignment.objects.get_or_create(user=user, badge=b)
