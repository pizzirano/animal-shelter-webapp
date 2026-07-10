"""
URLs for the homepage.
"""
from django.urls import path # pyright: ignore[reportMissingModuleSource]
from .views import HomeView

app_name = 'homepage'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]
