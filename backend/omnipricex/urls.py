from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/data/', views.get_data, name='get_data'),
    path('', views.index, name='index'),
]