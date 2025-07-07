from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget

from .models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Leftover,
    Badge,
    BadgeAssignment,
)

# Registra los modelos básicos
admin.site.register([Recipe, Ingredient, RecipeIngredient, Leftover])


# Creo un ModelForm que use CKEditorWidget para el campo `description`
class BadgeAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditorWidget(),  # aquí carga la barra de herramientas WYSIWYG
        label="Descripción",      # opcional: personaliza la etiqueta
        required=False,           # permite dejarlo en blanco
    )

    class Meta:
        model = Badge
        fields = "__all__"        # incluye todos los campos del modelo


# uso este formulario en el admin de Badge
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    form = BadgeAdminForm           # conecta nuestro form con el admin
    list_display  = ("name", "threshold", "active", "discount")
    list_editable = ("threshold", "active", "discount")


@admin.register(BadgeAssignment)
class BadgeAssignmentAdmin(admin.ModelAdmin):
    list_display     = ("user", "badge", "assigned_at")
    readonly_fields  = ("assigned_at",)
