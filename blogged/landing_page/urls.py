from django.urls import path
from landing_page.views import landing_page

urlpatterns = [
    # path('contact/', views.contact, name='contact'),
    path("", landing_page, name="landing_page"),
]
