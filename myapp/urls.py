from django.urls import path
from . import views
from .views import registro_asociacion
from .views import crear_animal

urlpatterns = [
path('', views.Inicio, name='Inicio'),
path('registro/', views.registro_asociacion, name='registro_asociacion'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('crear_animal/', views.crear_animal, name='crear_animal'),
]
