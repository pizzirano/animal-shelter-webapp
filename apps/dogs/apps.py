from django.apps import AppConfig # pyright: ignore[reportMissingModuleSource]


class DogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dogs"
    verbose_name = "Gestione Cani"

    def ready(self):
        """Import signals when the app is ready."""
        import apps.dogs.signals  # noqa