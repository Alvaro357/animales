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
    path('ver_animal/<int:animal_id>/', views.vista_animal, name='vista_animal'),
    path('editar_animal/<int:animal_id>/', views.editar_animal, name='editar_animal_direct'),  # Nueva línea
    path('animales/editar/<int:animal_id>/', views.editar_animal, name='editar_animal'),
    path('animales/eliminar/<int:animal_id>/', views.eliminar_animal, name='eliminar_animal'),
    path('animales/toggle-adopcion/<int:animal_id>/', views.toggle_adopcion, name='toggle_adopcion'),
    path('toggle_adopcion/<int:animal_id>/', views.toggle_adopcion_ajax, name='toggle_adopcion_ajax'),
    path('animales/', views.lista_animales_asociacion, name='lista_animales_asociacion'),
    path('mis_animales/', views.mis_animales, name='mis_animales'),
]