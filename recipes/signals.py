from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Recipe, Badge, BadgeAssignment

User = get_user_model()

@receiver(post_save, sender=Recipe)
def assign_badge_on_recipe(sender, instance, created, **kwargs):
    if not created or not instance.created_by:
        return
    user = instance.created_by

    # cuento sus recetas IA
    count = Recipe.objects.filter(created_by=user, is_ai=True).count()

    # busco todas las badges cuyo umbral ≤ count
    earned = Badge.objects.filter(threshold__lte=count)
    for badge in earned:
        BadgeAssignment.objects.get_or_create(user=user, badge=badge)
