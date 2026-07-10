from django.apps import AppConfig # pyright: ignore[reportMissingModuleSource]


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core Application"
