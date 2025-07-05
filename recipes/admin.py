from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient, Leftover, Badge, BadgeAssignment

#Registro los modelos en admin
admin.site.register([Recipe, Ingredient, RecipeIngredient, Leftover])

# Ahora registro los modelos de insignias y asignaciones
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display   = ("name","threshold","active","discount")
    list_editable  = ("threshold","active","discount")
    readonly_fields = ()

@admin.register(BadgeAssignment)
class BadgeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user","badge","assigned_at")
    readonly_fields = ("assigned_at",)