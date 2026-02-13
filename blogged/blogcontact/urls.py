# sendemail/urls.py
from django.urls import path

from .views import ContactView
from .views import FailureView
from .views import SuccessView

urlpatterns = [
    # path('contact/', views.contact, name='contact'),
    path("contact/", ContactView.as_view(), name="contact"),
    path("contact/success/", SuccessView.as_view(), name="contact-success"),
    path("contact/failure/", FailureView.as_view(), name="contact-failure"),
]
