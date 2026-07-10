from django.apps import AppConfig # pyright: ignore[reportMissingModuleSource]


class ContactsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contacts"
    verbose_name = "Gestione Contatti"
