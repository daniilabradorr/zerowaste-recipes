from django.urls import path
from .views import IngredientFormView, SuggestView, home, TranslateView, BadgeListView, share_app, MissionView

app_name = "recipes"

urlpatterns = [
    path("", home, name="home"),                     # /
    path("ingredients/", IngredientFormView.as_view(), name="ingredients"),
    path("mission/", MissionView.as_view(), name="mission"),
    path("suggest/",     SuggestView.as_view(),      name="suggest"),  # HTMX
    path("translate/<int:pk>/", TranslateView.as_view(), name="translate"),
    path("my_badges/", BadgeListView.as_view(), name="my_badges"),
    path("share/", share_app, name="share_app"),
]
