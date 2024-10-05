from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.home_page_view, name='home'),
    path('get_planets/', views.get_planets, name='get_planets'),
]