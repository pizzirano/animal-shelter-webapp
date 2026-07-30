"""
Shelter domain configuration — the single place to customize this webapp.

Fork the project and edit the values in ``SHELTER_CONFIG`` below with your own
shelter's data (name, contacts, address, opening hours, tagline). These values
are read by ``config/settings/base.py`` and exposed to every template through
``apps.core.context_processor.site_config``.

Secrets and runtime settings (SECRET_KEY, database, SMTP, reCAPTCHA, Cloudinary)
do NOT belong here — keep those in your ``.env`` file (see ``.env.example``).

ATENÇÃO: os campos marcados com "PLACEHOLDER" abaixo NÃO são dados reais da
ONG — são valores de espera até que telefone, e-mail, endereço e horários
sejam confirmados. Não publicar em produção antes de substituí-los.
"""

SHELTER_CONFIG = {
    # Public name of the shelter, shown across the site (header, footer, titles).
    "name": "ONG Arca de Noé — Rio Claro/SP",

    # Short slogan displayed in the footer.
    "tagline": "Resgate, cuidado e uma nova chance para cada animal.",

    # Public contact details shown to visitors.
    "contact_phone": "(19) 0000-0000",  # PLACEHOLDER — telefone real não confirmado
    "public_email": "contato@PLACEHOLDER.org.br",  # PLACEHOLDER — e-mail real não confirmado

    # Address, split in two lines as rendered in the footer.
    "address_street_and_number": "Rua PLACEHOLDER, 000",  # PLACEHOLDER — endereço não confirmado
    "address_city_and_postal_code": "Rio Claro/SP — CEP 00000-000",  # PLACEHOLDER — CEP não confirmado

    # Opening hours, one line each.
    "visiting_hours_weekdays": "Seg–Sex: horário a confirmar",  # PLACEHOLDER
    "visiting_hours_saturday": "Sábado: horário a confirmar",  # PLACEHOLDER
    "visiting_hours_sunday": "Domingo: fechado",  # a confirmar
}
