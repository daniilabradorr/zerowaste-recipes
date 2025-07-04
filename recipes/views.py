from __future__ import annotations #Para  mejorar los type hints sin afectar al codigo en ejecucion

from django.shortcuts import render
from django.views import View
from django.utils.translation import get_language
from .models import Recipe, Ingredient, RecipeIngredient
from .utils import suggest_recipe
from django.http import HttpResponse, HttpResponseServerError



import logging
logger = logging.getLogger(__name__)     # para dejar trazas en el log de Render

#viSTA DE PRUEBA UNICAMENTE 
def home(request) -> HttpResponse:
    return render(request, "home.html")


#Vista para el formulario de ingredientes
class IngredientFormView(View):
    """ Get = muestro el textarea donde el usuario escribe sus sobras.(no necesito POST aqui porque HTMX mandará el formulario a SuggestView) """

    template_name = "recipes/ingredient_form.html"
    def get(self, request) -> HttpResponse:
        return render(request, self.template_name)
    
#Vista para sugerir receta a la IA
class SuggestView(View):
    """ POST = recibo la lista de ingredientes, llamo a Groq, guardo la receta y devuelvo un fragmento HTML para que HTMX lo inserte en la pagina """

    def post(self,request)-> HttpResponse:
        #Leo los datos que vienen del textarea
        raw_ingredients = request.POST.get("ingredients", "").strip()  #Obtengo el texto del textarea y elimino espacios al principio y al final

        if not raw_ingredients:
            return HttpResponse("<p class='text-red-500'>⚠️ Debes introducir al menos un ingrediente.</p>",
                status=400,)

        lang = get_language()[:2] or "es"  #Obteengo el idioma que por defecto configure es (español)

        #Llamo al helper de IA que he creado y obtengpo el dict que devuelve con la receta
        try:
            data = suggest_recipe(raw_ingredients,lang)

            #Guardo la receta en la base de datos
            recipe = Recipe.objects.create(
                title=data.get("title"),
                instructions="\n".join(data["steps"]), #paso la list a texto
                language=lang,
                is_ai=True,
                created_by = request.user if request.user.is_authenticated else None, #Por si acaso le pongo un pequeño control de usuario autenticado
            )

            #Guardo y vinculo cada ingrediente de la receta
            for name in data["ingredients"]:
                ing, _ = Ingredient.objects.get_or_create(name = name)
                RecipeIngredient.objects.create(
                    recipe = recipe,
                    ingredient=ing,
                    quantity="", #Sin cantidades por ahora
                )
            
            # Devuelvo y renderizo la tarjeta parcial para HTMX
            return render(request, "recipes/_recipe_card.html", {"recipe": recipe})
        except RuntimeError as err:
             #Mi helper lanza RuntimeError en timeouts / json malformado / HTTP error
            logger.error("Error al generar receta IA: %s", err)
            friendly = ("<p class='text-red-500'>😔 Lo siento, la IA no pudo generar la receta. "
                "Inténtalo de nuevo en unos segundos.</p>"
            )
            return HttpResponseServerError(friendly)
        
        except Exception as exc: #Excepcion inesperada
            logger.exception("Fallo inesperado en SuggestView: %s", exc)
            return HttpResponseServerError(
                "<p class='text-red-500'>😔 Ocurrió un error inesperado.</p>"
            )