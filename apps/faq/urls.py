"""
URLs for the FAQ app.
"""
from django.urls import path # pyright: ignore[reportMissingModuleSource]
from .views import FAQListView

app_name = 'faq'

urlpatterns = [
    path('', FAQListView.as_view(), name='list'),
]
