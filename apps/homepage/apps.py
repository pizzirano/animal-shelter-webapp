from django.apps import AppConfig # pyright: ignore[reportMissingModuleSource]


class HomepageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.homepage"
    verbose_name = "Gestione Homepage"
