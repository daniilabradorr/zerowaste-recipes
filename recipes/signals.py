# recipes/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Recipe, ShareEvent, Badge, BadgeAssignment

@receiver(post_save, sender=Recipe)
def assign_recipe_badges(sender, instance, created, **kwargs):
    """
    Al crear una receta IA, asigna todas las badges de tipo "recipes"
    cuyo threshold ya haya superado el usuario.
    """
    if not created or not instance.is_ai or not instance.created_by:
        return

    user = instance.created_by
    total = Recipe.objects.filter(created_by=user, is_ai=True).count()

    # Solo badges de recetas (metric="recipes")
    recipe_badges = Badge.objects.filter(
        metric="recipes",
        active=True,
        threshold__lte=total
    )

    for badge in recipe_badges:
        BadgeAssignment.objects.get_or_create(user=user, badge=badge)


@receiver(post_save, sender=ShareEvent)
def assign_share_badges(sender, instance, created, **kwargs):
    """
    Al registrar un ShareEvent, asigna todas las badges de tipo "shares"
    cuyo threshold ya haya superado el usuario.
    """
    if not created or not instance.user:
        return

    user = instance.user
    total = ShareEvent.objects.filter(user=user).count()

    # Solo badges de compartidos (metric="shares")
    share_badges = Badge.objects.filter(
        metric="shares",
        active=True,
        threshold__lte=total
    )

    for badge in share_badges:
        BadgeAssignment.objects.get_or_create(user=user, badge=badge)
