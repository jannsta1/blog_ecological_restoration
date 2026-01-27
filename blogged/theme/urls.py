from django.urls import path
from .views import change_theme

urlpatterns = [
    path("switch-theme/", change_theme, name="change-theme"),
]
