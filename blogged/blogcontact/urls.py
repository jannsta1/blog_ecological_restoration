# sendemail/urls.py
from django.urls import path

from .views import SuccessView, ContactView

urlpatterns = [
        # path('contact/', views.contact, name='contact'),
    path("contact/", ContactView.as_view(), name="contact"),
    path("success/", SuccessView.as_view(), name="success"),
]