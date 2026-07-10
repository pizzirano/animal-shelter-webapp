"""
Shelter domain configuration — the single place to customize this webapp.

Fork the project and edit the values in ``SHELTER_CONFIG`` below with your own
shelter's data (name, contacts, address, opening hours, tagline). These values
are read by ``config/settings/base.py`` and exposed to every template through
``apps.core.context_processor.site_config``.

Secrets and runtime settings (SECRET_KEY, database, SMTP, reCAPTCHA, Cloudinary)
do NOT belong here — keep those in your ``.env`` file (see ``.env.example``).

The values below are neutral demo placeholders; replace them before going live.
"""

SHELTER_CONFIG = {
    # Public name of the shelter, shown across the site (header, footer, titles).
    "name": "Demo Animal Shelter",

    # Short slogan displayed in the footer.
    "tagline": "From heart to leash: helping dogs find a family that loves them.",

    # Public contact details shown to visitors.
    "contact_phone": "+39 000 000 0000",
    "public_email": "info@example.org",

    # Address, split in two lines as rendered in the footer.
    "address_street_and_number": "123 Example Street",
    "address_city_and_postal_code": "00000 Example City (XX)",

    # Opening hours, one line each.
    "visiting_hours_weekdays": "Mon - Fri: 09:00 - 12:00, 14:00 - 17:00",
    "visiting_hours_saturday": "Saturday: 10:00 - 13:00, 14:00 - 18:00",
    "visiting_hours_sunday": "Sunday: closed",
}
