# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An open-source Django platform for an animal shelter to showcase adoptable dogs. It is designed as a **reusable template**: a fork rebrands the site by editing only two files — `config/shelter_config.py` (public data: name, contacts, hours) and `.env` (secrets/runtime). No application code should need editing to rebrand. Keep that contract in mind: shelter-specific data belongs in `shelter_config.py`, never hard-coded in apps or templates.

UI source strings are **Italian** (`msgid`), wrapped in Django i18n tags. The site serves one language per deployment via `LANGUAGE_CODE` in `config/settings/base.py` (default `it-it`); an English example catalog ships in `locale/en/`.

## Commands

```bash
# Environment is selected by DJANGO_ENVIRONMENT (development | test | production), default development
pip install -r requirements/development.txt

python manage.py migrate
python manage.py runserver          # http://localhost:8000  (admin at /admin/)

# Tests — MUST set the env; pytest.ini points DJANGO_SETTINGS_MODULE at config.settings.test
DJANGO_ENVIRONMENT=test pytest
DJANGO_ENVIRONMENT=test pytest apps/contacts/tests.py -v            # single app
DJANGO_ENVIRONMENT=test pytest apps/dogs/tests.py::TestDogModel     # single class/test
DJANGO_ENVIRONMENT=test pytest --cov=apps --cov-report=term        # coverage
docker compose --profile test run --rm test                        # tests on real PostgreSQL

# i18n
django-admin makemessages -l en
django-admin compilemessages

# Docker (full stack: web + db + redis + nginx + certbot)
docker compose up -d
docker compose up -d web            # recreate to reload .env (NOT `restart`)
```

On Windows/PowerShell, set the env var separately: `$env:DJANGO_ENVIRONMENT='test'; pytest`.

## Settings selection (important, non-obvious)

There are two independent entry points into settings, and they select the environment differently:

- **`manage.py` / `wsgi` / `asgi`** point at the `config.settings` *package*. Its `__init__.py` reads `DJANGO_ENVIRONMENT` and re-exports `development`, `test`, or `production`.
- **pytest** bypasses that: `pytest.ini` sets `DJANGO_SETTINGS_MODULE = config.settings.test` directly, and `conftest.py` forces `os.environ['DJANGO_ENVIRONMENT'] = 'test'` at import time (before `decouple` reads `.env`).

Settings modules: `base.py` (shared) → `development.py` (SQLite, LocMem cache, debug toolbar, hardcoded `DEBUG=True`/`ALLOWED_HOSTS=['*']`), `test.py` (separate `db_test.sqlite3`, in-memory email, official reCAPTCHA test keys, strips debug toolbar), `test_pg.py` (real PostgreSQL — note: named `test_*` but excluded from collection via `testpaths = apps`), `production.py` (PostgreSQL, Redis, Cloudinary, SSL).

Environment variables are read via `python-decouple` (`env_config`). `base.py` provides working defaults for everything so a fresh clone boots without a `.env`.

## Architecture

Five local apps under `apps/`, all following Django's app conventions (`models`/`views`/`urls`/`admin`/`serializers`/`api_views`/`tests`):

- **`core`** — cross-cutting infra, no user-facing pages. Abstract base models (`TimeStampedModel`, `PublishableModel` in `models.py`), custom middleware (`ResponseTimeMiddleware` adds `X-Response-Time` + logs slow requests; `RequestLoggingMiddleware`), the `site_config` context processor, and cache helpers (`cache.py`).
- **`dogs`** — the domain core. `Dog`/`Breed`/`DogImage` models, custom `DogQuerySet`/`DogManager` (`managers.py`), image upload validators (`validators.py`), filters, and cache-invalidation signals (`signals.py`).
- **`contacts`** — the contact form and its multi-layer anti-spam (see below).
- **`homepage`** — featured dogs + shelter statistics.
- **`faq`** — FAQ by category with a frontend accordion.

### Shelter config → templates flow

`config/shelter_config.py` defines `SHELTER_CONFIG` → `base.py` unpacks it into module-level settings (`SHELTER_NAME`, `CONTACT_PHONE`, etc.) → `apps.core.context_processor.site_config` exposes those to every template (e.g. `{{ SHELTER_NAME }}`). To add a shelter field, add it in all three places.

### Caching (manual, key-based)

There is **no** cache middleware or `@cache_page`. Views call `cache.get`/`cache.set` explicitly with well-known string keys, and `apps/dogs/signals.py` deletes those exact keys on `Dog`/`Breed` `post_save`/`post_delete`. When you add or rename a cached key in a view, update the invalidation signal to match. Known keys: `homepage_featured_dogs`, `homepage_stats`, `similar_dogs_{id}`, `dog_breeds_list`, `contact_count_{ip}`.

Dev/test use `LocMemCache`; prod uses Redis. `invalidate_cache_by_prefix` in `core/cache.py` relies on Redis's `delete_pattern` and **falls back to a full `cache.clear()`** on LocMem — prefer deleting explicit keys.

Querysets are optimized via the manager: use `Dog.objects.published()`, `.available()`, `.with_breed()`, `.with_related()` to avoid N+1 (see `DogListView`/`DogDetailView`).

### Contact-form anti-spam (layered, in `apps/contacts/`)

Layers, in order: (1) `@ratelimit(key='ip', rate='3/h', block=False)` on `ContactView.post` — because `block=False`, the view manually checks `request.limited` and renders an error instead of raising; (2) reCAPTCHA v2 field; (3) hidden **honeypot** `website` field (`clean_website` rejects if filled); (4) content validation in `ContactForm.clean_message`/`clean_email` (min length, link/`http` rejection, spam-word list, disposable-email-domain blocklist). The spam-word and disposable-domain lists are inline in `forms.py` (marked with TODOs to extract). The view also records `ip_address`/`user_agent`/`spam_score` and emails `STAFF_EMAIL`.

### API

DRF ViewSets (`api_views.py` per app) registered on a `DefaultRouter` in `config/urls.py`. Public read access (`AllowAny`, no auth), throttled (`anon: 100/hour`). OpenAPI via drf-spectacular: schema `/api/schema/`, Swagger `/api/docs/`, ReDoc `/api/redoc/`. Admin and all API URL prefixes are configurable via env (`ADMIN_URL`, `API_URL`, …).

### Security stack

`django-axes` (login brute-force lockout, 5 failures) with `AxesStandaloneBackend` first in `AUTHENTICATION_BACKENDS`; cached-db sessions with hardened cookies (`shelter_sessionid`, HttpOnly, SameSite=Lax, 60 min); security headers + HSTS in production. Client IP is read from `X-Forwarded-For` (first hop) — relevant since prod runs behind nginx.

## Tests

Shared factories and fixtures live in the root `conftest.py` (`DogFactory`, `BreedFactory`, `ContactMessageFactory`, plus image fixtures `fake_image_jpg`/`fake_image_large`/`fake_file_pdf`, and `admin_user`). Tests are collected only from `apps/` (`testpaths = apps`), matching `tests.py` and `test_*.py`. Rate limiting is enabled by default in the test settings; tests that don't exercise it use `override_settings`.
