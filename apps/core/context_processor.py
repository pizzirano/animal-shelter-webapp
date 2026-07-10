"""Expose shelter domain settings to all templates.

Values are defined in config/shelter_config.py and loaded in
config/settings/base.py. To add a new one, define it there and add it to the
dict returned below; it then becomes available in any template, e.g.
``{{ SHELTER_NAME }}``.
"""
from django.conf import settings


def site_config(request):
    return {
        'SHELTER_NAME': settings.SHELTER_NAME,
        'SHELTER_TAGLINE': settings.SHELTER_TAGLINE,
        'CONTACT_PHONE': settings.CONTACT_PHONE,
        'ADDRESS_STREET_AND_NUMBER': settings.ADDRESS_STREET_AND_NUMBER,
        'ADDRESS_CITY_AND_POSTAL_CODE': settings.ADDRESS_CITY_AND_POSTAL_CODE,
        'PUBLIC_EMAIL': settings.PUBLIC_EMAIL,
        'VISITING_HOURS_WEEKDAYS': settings.VISITING_HOURS_WEEKDAYS,
        'VISITING_HOURS_WEEKEND_SAT': settings.VISITING_HOURS_WEEKEND_SAT,
        'VISITING_HOURS_WEEKEND_SUN': settings.VISITING_HOURS_WEEKEND_SUN,
    }
