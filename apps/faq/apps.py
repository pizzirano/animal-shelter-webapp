from django.apps import AppConfig # pyright: ignore[reportMissingModuleSource]


class FaqConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.faq"
    verbose_name = "Gestione FAQ"
