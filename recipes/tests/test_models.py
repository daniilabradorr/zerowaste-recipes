import pytest
from recipes.models import Ingredient

@pytest.mark.django_db
def test_ingredient_str():
    ing = Ingredient.objects.create(name="Zanahoria")
    assert str(ing) == "Zanahoria"
