"""
URLs for the Contacts app.
"""
from django.urls import path # pyright: ignore[reportMissingModuleSource]
from .views import ContactView, ContactSuccessView

app_name = 'contacts'

urlpatterns = [
    path('', ContactView.as_view(), name='contact'),
    path('success/', ContactSuccessView.as_view(), name='success'),
]
