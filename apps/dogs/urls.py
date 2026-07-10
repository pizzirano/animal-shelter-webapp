"""
URLs for the Dogs app.
"""
from django.urls import path # pyright: ignore[reportMissingModuleSource]
from .views import DogListView, DogDetailView

app_name = 'dogs'

urlpatterns = [
    path('', DogListView.as_view(), name='list'),
    path('<slug:slug>/', DogDetailView.as_view(), name='detail'),
]
