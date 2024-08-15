# parking/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search_parking/', views.search_parking, name='search_parking'),
    path('reserve/<int:objectid>/', views.reserve_parking, name='reserve_parking'),
    path('calculate_price/', views.calculate_price_view, name='calculate_price'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
