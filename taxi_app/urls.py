from django.urls import path
from .views import home, order, cars, about, order_confirmation

urlpatterns = [
    path('', home, name='home'),
    path('order/', order, name='order'),
    path('cars/', cars, name='cars'),
    path('about/', about, name='about'),
    path('order/confirmation/', order_confirmation, name='order_confirmation'),
]