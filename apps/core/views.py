"""
Core utility views.
"""
from django.shortcuts import render # pyright: ignore[reportMissingModuleSource]


def rate_limit_view(request, exception=None):
    """
    Custom view shown when a user is rate limited.
    """
    return render(request, 'core/rate_limit.html', {
        'exception': exception
    }, status=429)
