from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'

    def ready(self):
        # Importo el módulo de signals para conectar los handlers
        import recipes.signals
        # Esto asegura que los signals se registren al iniciar la app
        # y no al importar el módulo directamente, evitando problemas de importación circular.
