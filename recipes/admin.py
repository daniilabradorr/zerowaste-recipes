from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, Leftover

#Registro los modelos en admin
admin.site.register([Recipe, Ingredient, RecipeIngredient, Leftover])
