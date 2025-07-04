from django.urls import path
from .views import IngredientFormView, SuggestView, home, TranslateView

app_name = "recipes"

urlpatterns = [
    path("", home, name="home"),                     # /
    path("ingredients/", IngredientFormView.as_view(), name="ingredients"),
    path("suggest/",     SuggestView.as_view(),      name="suggest"),  # HTMX
    path("translate/<int:pk>/", TranslateView.as_view(), name="translate"),
]
