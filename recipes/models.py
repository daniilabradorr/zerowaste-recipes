from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

#Inicio una clase para cada ingrediente 
class Ingredient(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

#Inicio una clase para cada receta
class Recipe(models.Model):
    #Opciones de idioma
    LANGUAGE_CHOICES = [
        ('es', 'Español'),
        ('en', 'English')
    ]

    title = models.CharField(max_length=200)
    instructions = models.TextField()
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES,default='es')
    is_ai = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
#clase para los ingredientes de las recetas
#Esta clase relaciona los ingredientes con las recetas
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete= models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=80, blank=True)

#Clase para las sobras de ingredientes
class Leftover(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='leftovers')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)