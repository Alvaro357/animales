# myapp/urls.py - URLs completas del sistema

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Páginas principales
    path('', views.Inicio, name='inicio'),
    path('mis-favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('buscador-avanzado/', views.buscador_avanzado, name='buscador_avanzado'),
    path('resultados-busqueda/', views.resultados_busqueda, name='resultados_busqueda'),
    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_asociacion, name='registro'),
    
    # Gestión de animales
    path('crear_animal/', views.crear_animal, name='crear_animal'),
    path('mis_animales/', views.mis_animales, name='mis_animales'),
    path('ver_animal/<int:animal_id>/', views.vista_animal, name='ver_animal'),
    
    # AJAX para gestión de animales
    path('animales/toggle-adopcion/<int:animal_id>/', views.toggle_adopcion_ajax, name='toggle_adopcion'),
    path('animales/editar/<int:animal_id>/', views.editar_animal, name='editar_animal'),
    path('animales/eliminar/<int:animal_id>/', views.eliminar_animal, name='eliminar_animal'),
    
    # APIs (opcional)
    path('api/favoritos/', views.obtener_animales_favoritos, name='obtener_animales_favoritos'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)