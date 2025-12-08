# myapp/urls.py - URLs completas del sistema

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .telegram_utils import telegram_webhook 

urlpatterns = [
    # SEO - robots.txt y sitemap.xml
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # URLs existentes
    path('', views.Inicio, name='inicio'),
    path('registro/', views.registro_asociacion, name='registro_asociacion'),
    path('registro_exitoso/', views.registro_exitoso_view, name='registro_exitoso'),
    path('validar-nombre-asociacion/', views.validar_nombre_asociacion, name='validar_nombre_asociacion'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Restablecimiento de contraseña
    path('recuperar-password/', views.solicitar_reset_password, name='solicitar_reset_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('crear_animal/', views.crear_animal, name='crear_animal'),
    path('mis_animales/', views.mis_animales, name='mis_animales'),
    path('ver_animal/<int:animal_id>/', views.ver_animal, name='ver_animal'),
    path('vista_animal/<int:animal_id>/', views.vista_animal, name='vista_animal'),
    path('editar_animal/<int:animal_id>/', views.editar_animal, name='editar_animal'),
    path('eliminar_animal/<int:animal_id>/', views.eliminar_animal, name='eliminar_animal'),
    path('toggle_adopcion/<int:animal_id>/', views.toggle_adopcion_ajax, name='toggle_adopcion'),
    path('mis-favoritos/', views.mis_favoritos, name='mis_favoritos'),
    path('obtener-animales-favoritos/', views.obtener_animales_favoritos, name='obtener_animales_favoritos'),
    path('buscador-avanzado/', views.buscador_avanzado, name='buscador_avanzado'),
    path('resultados-busqueda/', views.resultados_busqueda, name='resultados_busqueda'),
    path('acerca/', views.acerca, name='acerca'),
    
    # URLs existentes de gestión (mantener compatibilidad)
    path('gestion/suspender/<str:token>/', views.suspender_asociacion, name='suspender_asociacion'),
    path('gestion/eliminar/<str:token>/', views.eliminar_asociacion, name='eliminar_asociacion'),
    path('gestion/reactivar/<str:token>/', views.reactivar_asociacion, name='reactivar_asociacion'),
    path('gestion/info/<str:token>/', views.info_asociacion, name='info_asociacion'),
    
    # ==================== NUEVAS URLs PARA SISTEMA DE APROBACIÓN ====================

    # Autenticación de admin
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),

    # Panel de administración principal
    path('admin/panel/', views.panel_administracion, name='panel_administracion'),
    
    # Acciones de aprobación/rechazo
    path('admin/aprobar/<str:token>/', views.aprobar_asociacion, name='aprobar_asociacion'),
    path('admin/rechazar/<str:token>/', views.rechazar_asociacion, name='rechazar_asociacion'),
    path('admin/rechazar_confirmar/<str:token>/', views.rechazar_asociacion_confirmar, name='rechazar_asociacion_confirmar'),
    
    # Información detallada para admin
    path('admin/info/<str:token>/', views.info_asociacion_admin, name='info_asociacion_admin'),
    
    # URLs alternativas para compatibilidad total con emails antiguos
    path('admin/gestion/aprobar/<str:token>/', views.aprobar_asociacion, name='aprobar_asociacion_alt'),
    path('admin/gestion/rechazar/<str:token>/', views.rechazar_asociacion, name='rechazar_asociacion_alt'),
    path('admin/gestion/info/<str:token>/', views.info_asociacion_admin, name='info_asociacion_admin_alt'),

    path('telegram/webhook/', telegram_webhook, name='telegram_webhook'),
]


# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)