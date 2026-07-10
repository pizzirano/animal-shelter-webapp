"""
Management command to clear the cache.
"""
from django.core.management.base import BaseCommand # pyright: ignore[reportMissingModuleSource]
from django.core.cache import cache # pyright: ignore[reportMissingModuleSource]


class Command(BaseCommand):
    help = 'Clear the whole cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefix',
            type=str,
            help='Only clear keys with this prefix',
        )

    def handle(self, *args, **options):
        prefix = options.get('prefix')

        if prefix:
            # Clear only one prefix (requires Redis!)
            if hasattr(cache, 'delete_pattern'):
                deleted = cache.delete_pattern(f"*{prefix}*")
                self.stdout.write(
                    self.style.SUCCESS(f'Cache cleared for prefix "{prefix}": {deleted} keys removed')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Cache backend does not support delete_pattern, using clear()')
                )
                cache.clear()
        else:
            # Clear the whole cache
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Cache fully cleared!'))
