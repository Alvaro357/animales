from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from functools import wraps
from .forms import RegistroAsociacionForm, LoginForm, CreacionAnimalesForm
from .models import RegistroAsociacion, CreacionAnimales
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST, require_GET
from django.middleware.csrf import get_token
from django.utils import timezone
import json
from .telegram_utils import (
    enviar_notificacion_nueva_asociacion,
    enviar_notificacion_aprobacion,
    enviar_notificacion_rechazo,
    enviar_notificacion_rechazo_web,
    enviar_notificacion_suspension,
    enviar_notificacion_reactivacion,
    enviar_notificacion_eliminacion
)

def session_login_required(view_func):
    """Decorador actualizado que verifica sesión Y estado de la asociación"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('esta_logueado'):
            return redirect('login')
        
        # Verificar estado de la asociación
        asociacion_id = request.COOKIES.get('asociacion_id')
        if asociacion_id:
            try:
                asociacion = RegistroAsociacion.objects.get(id=asociacion_id)
                if not asociacion.puede_acceder():
                    # Limpiar sesión y redirigir con mensaje
                    request.session.flush()
                    response = redirect('login')
                    response.delete_cookie('asociacion_id')
                    return response
            except RegistroAsociacion.DoesNotExist:
                request.session.flush()
                response = redirect('login')
                response.delete_cookie('asociacion_id')
                return response
        
        return view_func(request, *args, **kwargs)
    return wrapper

# ==================== VISTAS ADMINISTRATIVAS ====================

@csrf_protect
def aprobar_asociacion(request, token):
    """Vista para aprobar una asociación usando el token del correo - Ahora con confirmación POST"""
    try:
        asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)

        if request.method == 'GET':
            # Mostrar página de confirmación
            if asociacion.estado == 'activa':
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #10b981;">✅ Asociación ya aprobada</h2>
                            <p>La asociación "<strong>{}</strong>" ya fue aprobada anteriormente.</p>
                            <p style="color: #666;">Fecha de aprobación: {}</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                        </body>
                    </html>
                """.format(
                    asociacion.nombre,
                    asociacion.fecha_aprobacion.strftime("%d/%m/%Y %H:%M") if asociacion.fecha_aprobacion else "No disponible"
                ))

            # Mostrar formulario de confirmación
            csrf_token = get_token(request)
            return HttpResponse(f"""
                <html>
                    <head>
                        <title>Confirmar Aprobación</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                            .form-container {{ background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                            .btn {{ padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                            .btn-success {{ background: #10b981; color: white; }}
                            .btn-secondary {{ background: #6b7280; color: white; margin-left: 10px; }}
                        </style>
                    </head>
                    <body>
                        <div class="form-container">
                            <h2 style="color: #10b981;">✅ Confirmar Aprobación</h2>
                            <p><strong>Asociación:</strong> {asociacion.nombre}</p>
                            <p><strong>Email:</strong> {asociacion.email}</p>
                            <p><strong>Estado actual:</strong> {asociacion.get_estado_display()}</p>

                            <form method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                <button type="submit" class="btn btn-success">✅ Confirmar Aprobación</button>
                                <a href="/admin/panel/" class="btn btn-secondary">↩️ Cancelar</a>
                            </form>
                        </div>
                    </body>
                </html>
            """)

        elif request.method == 'POST':
            # Procesar la aprobación
            if asociacion.estado != 'activa':
                asociacion.aprobar(admin_name="Administrador Web", notas="Aprobada vía enlace directo")

                # Enviar notificaciones (solo una vez cada función)
                enviar_notificacion_aprobacion(asociacion)
                enviar_email_aprobacion(asociacion)

            return HttpResponse("""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #10b981;">✅ Asociación aprobada exitosamente</h2>
                        <p>La asociación "<strong>{}</strong>" ha sido aprobada.</p>
                        <p style="color: #666;">Fecha de aprobación: {}</p>
                        <div style="background: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10b981;">
                            <strong>✓</strong> Se ha enviado un email de confirmación a la asociación<br>
                            <strong>✓</strong> Ya pueden iniciar sesión y gestionar sus animales
                        </div>
                        <hr style="margin: 30px 0;">
                        <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                    </body>
                </html>
            """.format(
                asociacion.nombre,
                asociacion.fecha_aprobacion.strftime("%d/%m/%Y %H:%M")
            ))

    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #ef4444;">❌ Error</h2>
                    <p>Token inválido o asociación no encontrada.</p>
                    <p style="color: #666;">El enlace puede haber expirado o ser incorrecto.</p>
                </body>
            </html>
        """, status=404)

@require_GET
def rechazar_asociacion(request, token):
    """Vista para rechazar una asociación"""
    try:
        asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)
        
        if asociacion.estado == 'rechazada':
            return HttpResponse("""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #ef4444;">❌ Asociación ya rechazada</h2>
                        <p>La asociación "<strong>{}</strong>" ya fue rechazada anteriormente.</p>
                        <hr style="margin: 30px 0;">
                        <p><a href="/admin/aprobar/{}/" style="color: #10b981;">✅ Aprobar asociación</a></p>
                        <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                    </body>
                </html>
            """.format(asociacion.nombre, token))
        
        # Mostrar formulario de rechazo
        return HttpResponse("""
            <html>
                <head>
                    <title>Rechazar Asociación</title>
                    <style>
                        body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                        .form-container { background: #f8f9fa; padding: 30px; border-radius: 10px; }
                        .form-group { margin-bottom: 20px; }
                        label { display: block; font-weight: bold; margin-bottom: 5px; }
                        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; min-height: 120px; }
                        .btn { padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
                        .btn-danger { background: #ef4444; color: white; }
                        .btn-secondary { background: #6b7280; color: white; margin-left: 10px; }
                    </style>
                </head>
                <body>
                    <div class="form-container">
                        <h2 style="color: #ef4444;">❌ Rechazar Asociación</h2>
                        <p><strong>Asociación:</strong> {}</p>
                        <p><strong>Email:</strong> {}</p>
                        <p><strong>Fecha de registro:</strong> {}</p>
                        
                        <form method="post" action="/admin/rechazar_confirmar/{}/">
                            <div class="form-group">
                                <label for="motivo">Motivo del rechazo (será enviado a la asociación):</label>
                                <textarea name="motivo" id="motivo" placeholder="Explica el motivo del rechazo..." required></textarea>
                            </div>
                            
                            <button type="submit" class="btn btn-danger">❌ Confirmar Rechazo</button>
                            <a href="/admin/panel/" class="btn btn-secondary">↩️ Cancelar</a>
                        </form>
                    </div>
                </body>
            </html>
        """.format(
            asociacion.nombre,
            asociacion.email,
            asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M"),
            token
        ))
        
    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("❌ Token inválido o asociación no encontrada.", status=404)



@require_POST
def rechazar_asociacion_confirmar(request, token):
    """Confirma el rechazo de una asociación - LA ELIMINA INMEDIATAMENTE"""
    try:
        asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)
        motivo = request.POST.get('motivo', '')

        # Guardar datos antes de eliminar
        nombre_asociacion = asociacion.nombre
        email_asociacion = asociacion.email

        # Enviar email de rechazo ANTES de eliminar
        enviar_email_rechazo(asociacion, motivo)

        # ELIMINAR la asociación inmediatamente del sistema
        asociacion.delete()

        # Enviar notificación de Telegram
        enviar_notificacion_rechazo_web(nombre_asociacion, email_asociacion, motivo)

        return HttpResponse("""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #ef4444;">❌ Asociación rechazada y eliminada</h2>
                    <p>La asociación "<strong>{}</strong>" ha sido rechazada y eliminada del sistema.</p>
                    <div style="background: #fee2e2; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ef4444;">
                        <strong>✓</strong> Se ha enviado un email explicando el motivo del rechazo<br>
                        <strong>✓</strong> La asociación ha sido eliminada permanentemente del sistema
                    </div>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                        <strong>⚠️</strong> La asociación no podrá registrarse nuevamente con los mismos datos
                    </div>
                    <hr style="margin: 30px 0;">
                    <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                </body>
            </html>
        """.format(nombre_asociacion))

    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("❌ Error procesando el rechazo.", status=404)


# Removed duplicate panel_administracion function - using the template-based one at the end


@require_GET
def info_asociacion_admin(request, token):
    """Vista detallada de una asociación para administración"""
    try:
        # Buscar por ambos tokens
        asociacion = None
        try:
            asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)
        except RegistroAsociacion.DoesNotExist:
            try:
                asociacion = RegistroAsociacion.objects.get(token_gestion=token)
            except RegistroAsociacion.DoesNotExist:
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #ef4444;">❌ Error</h2>
                            <p>Token inválido o asociación no encontrada.</p>
                            <p style="color: #666;">El enlace puede haber expirado o ser incorrecto.</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                        </body>
                    </html>
                """, status=404)

        animales = asociacion.animales.all()

        # Generar botones según estado
        if asociacion.estado == 'pendiente':
            botones = f"""
                <a href="/admin/aprobar/{asociacion.token_aprobacion}/" class="btn btn-success">✅ Aprobar</a>
                <a href="/admin/rechazar/{asociacion.token_aprobacion}/" class="btn btn-danger">❌ Rechazar</a>
                <a href="/admin/panel/" class="btn btn-secondary">↩️ Volver al Panel</a>
            """
        elif asociacion.estado == 'activa':
            botones = f"""
                <a href="/gestion/suspender/{asociacion.token_gestion}/" class="btn btn-warning">⏸️ Suspender</a>
                <a href="/admin/panel/" class="btn btn-secondary">↩️ Volver al Panel</a>
            """
        elif asociacion.estado == 'suspendida':
            botones = f"""
                <a href="/gestion/reactivar/{asociacion.token_gestion}/" class="btn btn-success">🔄 Reactivar</a>
                <a href="/gestion/eliminar/{asociacion.token_gestion}/" class="btn btn-danger">🗑️ Eliminar</a>
                <a href="/admin/panel/" class="btn btn-secondary">↩️ Volver al Panel</a>
            """
        else:
            botones = f'<a href="/admin/panel/" class="btn btn-secondary">↩️ Volver al Panel</a>'
        
        return HttpResponse("""
            <html>
                <head>
                    <title>Información de Asociación</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; padding: 20px; }}
                        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
                        .estado {{ padding: 8px 16px; border-radius: 20px; color: white; display: inline-block; }}
                        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
                        .info-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                        .actions {{ text-align: center; margin: 30px 0; }}
                        .btn {{ display: inline-block; padding: 12px 24px; margin: 5px; text-decoration: none; border-radius: 6px; font-weight: bold; }}
                        .btn-success {{ background: #28a745; color: white; }}
                        .btn-danger {{ background: #dc3545; color: white; }}
                        .btn-warning {{ background: #f59e0b; color: white; }}
                        .btn-secondary {{ background: #6c757d; color: white; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>{}</h1>
                        <span class="estado" style="background: {}">
                            {} 
                        </span>
                        <p style="margin: 10px 0; color: #666;">
                            Registrada {}<br>
                            ID: #{} | Email: {}
                        </p>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-box">
                            <h3>📋 Información Básica</h3>
                            <p><strong>Nombre:</strong> {}</p>
                            <p><strong>Email:</strong> {}</p>
                            <p><strong>Teléfono:</strong> {}</p>
                            <p><strong>Dirección:</strong> {}</p>
                            <p><strong>Población:</strong> {}</p>
                            <p><strong>Provincia:</strong> {}</p>
                            <p><strong>Código Postal:</strong> {}</p>
                        </div>
                        
                        <div class="info-box">
                            <h3>📊 Estado y Estadísticas</h3>
                            <p><strong>Estado actual:</strong> {}</p>
                            <p><strong>Fecha registro:</strong> {}</p>
                            <p><strong>Total animales:</strong> {}</p>
                            <p><strong>Animales disponibles:</strong> {}</p>
                            <p><strong>Token aprobación:</strong> <code style="font-size: 10px;">{}</code></p>
                        </div>
                    </div>
                    
                    <div class="actions">
                        {}
                    </div>
                </body>
            </html>
        """.format(
            asociacion.nombre,
            asociacion.get_estado_color(),
            asociacion.get_estado_display().upper(),
            asociacion.get_tiempo_desde_registro(),
            asociacion.id,
            asociacion.email,
            asociacion.nombre,
            asociacion.email,
            asociacion.telefono,
            asociacion.direccion,
            asociacion.poblacion,
            asociacion.provincia,
            asociacion.codigo_postal,
            asociacion.get_estado_display(),
            asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M"),
            animales.count(),
            animales.filter(adoptado=False).count(),
            str(asociacion.token_aprobacion)[:16] + "...",
            botones
        ))
        
    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("❌ Token inválido o asociación no encontrada.", status=404)


# ==================== FUNCIONES DE EMAIL ====================

def enviar_email_aprobacion(asociacion):
    """Envía email de aprobación a la asociación"""
    subject = "🎉 ¡Tu asociación ha sido aprobada en Adopta!"
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1>🎉 ¡Aprobación Exitosa!</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
                <p>Estimados <strong>{asociacion.nombre}</strong>,</p>
                
                <p>¡Excelentes noticias! Su asociación ha sido <strong>aprobada</strong> y ya puede acceder al sistema de Adopta.</p>
                
                <div style="background: #d1fae5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
                    <h3 style="margin: 0; color: #065f46;">✅ Su cuenta está activa</h3>
                    <p style="margin: 10px 0 0 0; color: #047857;">
                        Ya puede iniciar sesión y comenzar a registrar sus animales para adopción.
                    </p>
                </div>
                
                <h3>📝 Sus datos de acceso:</h3>
                <ul>
                    <li><strong>Usuario:</strong> {asociacion.nombre}</li>
                    <li><strong>Contraseña:</strong> La que eligió durante el registro</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://tu-dominio.com" style="background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                        🏠 Acceder a Adopta
                    </a>
                </div>
                
                <p>Gracias por unirse a nuestra plataforma y ayudar a los animales a encontrar un hogar.</p>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Si tiene alguna pregunta, puede responder a este correo.<br>
                    Equipo de Adopta
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Su asociación {asociacion.nombre} ha sido aprobada. Ya puede acceder al sistema.",
            from_email=None,
            to=[asociacion.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Email de aprobación enviado a: {asociacion.email}")
    except Exception as e:
        print(f"❌ Error enviando email de aprobación: {e}")


def enviar_email_rechazo(asociacion, motivo):
    """Envía email de rechazo a la asociación"""
    subject = "❌ Solicitud de registro rechazada - Adopta"

    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #ef4444; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1>❌ Registro No Completado</h1>
            </div>

            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
                <p>Estimados <strong>{asociacion.nombre}</strong>,</p>

                <p>Lamentablemente, <strong>su asociación no ha sido registrada</strong> en nuestra plataforma por el siguiente motivo:</p>
                
                <div style="background: #fee2e2; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ef4444;">
                    <h3 style="margin: 0; color: #7f1d1d;">📋 Motivo del rechazo:</h3>
                    <p style="margin: 10px 0 0 0; color: #991b1b;">
                        {motivo}
                    </p>
                </div>
                
                <p><strong>Su asociación NO ha sido registrada en el sistema y deberá realizar una nueva solicitud si desea intentarlo nuevamente.</strong></p>

                <p>Si considera que ha habido un error o desea enviar información adicional, puede responder a este correo.</p>

                <p>Le invitamos a corregir los aspectos mencionados y volver a enviar su solicitud de registro.</p>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Equipo de Adopta
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Su solicitud para {asociacion.nombre} no fue aprobada. Motivo: {motivo}",
            from_email=None,
            to=[asociacion.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Email de rechazo enviado a: {asociacion.email}")
    except Exception as e:
        print(f"❌ Error enviando email de rechazo: {e}")

@csrf_protect
def suspender_asociacion(request, token):
    """Vista para suspender una asociación usando el token - Ahora con confirmación POST"""
    try:
        # Buscar por ambos tokens para compatibilidad
        asociacion = None
        try:
            asociacion = RegistroAsociacion.objects.get(token_gestion=token)
        except RegistroAsociacion.DoesNotExist:
            asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)

        if request.method == 'GET':
            # Mostrar página de confirmación
            if asociacion.estado == 'suspendida':
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #f59e0b;">⚠️ Asociación ya suspendida</h2>
                            <p>La asociación "<strong>{}</strong>" ya estaba suspendida.</p>
                            <p style="color: #666;">Fecha de suspensión anterior: {}</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/gestion/reactivar/{}/" style="color: #10b981;">🔄 Reactivar asociación</a></p>
                            <p><a href="/gestion/eliminar/{}/" style="color: #ef4444;">🗑️ Eliminar definitivamente</a></p>
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                        </body>
                    </html>
                """.format(
                    asociacion.nombre,
                    asociacion.fecha_modificacion_estado.strftime("%d/%m/%Y %H:%M") if asociacion.fecha_modificacion_estado else "No disponible",
                    asociacion.token_gestion,
                    asociacion.token_gestion
                ))

            if asociacion.estado == 'eliminada':
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #ef4444;">❌ Asociación eliminada</h2>
                            <p>La asociación "<strong>{}</strong>" ya fue eliminada.</p>
                            <p style="color: #666;">No se pueden realizar más acciones.</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                        </body>
                    </html>
                """.format(asociacion.nombre))

            # Mostrar formulario de confirmación
            csrf_token = get_token(request)
            return HttpResponse(f"""
                <html>
                    <head>
                        <title>Confirmar Suspensión</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                            .form-container {{ background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                            .btn {{ padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                            .btn-warning {{ background: #f59e0b; color: white; }}
                            .btn-secondary {{ background: #6b7280; color: white; margin-left: 10px; }}
                        </style>
                    </head>
                    <body>
                        <div class="form-container">
                            <h2 style="color: #f59e0b;">⚠️ Confirmar Suspensión</h2>
                            <p><strong>Asociación:</strong> {asociacion.nombre}</p>
                            <p><strong>Email:</strong> {asociacion.email}</p>
                            <p><strong>Estado actual:</strong> {asociacion.get_estado_display()}</p>
                            <p><strong>Animales registrados:</strong> {asociacion.animales.count()}</p>

                            <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                                <strong>⚠️ Importante:</strong> La asociación no podrá iniciar sesión ni gestionar sus animales, pero sus animales seguirán siendo visibles en la web.
                            </div>

                            <form method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                <button type="submit" class="btn btn-warning">⚠️ Confirmar Suspensión</button>
                                <a href="/admin/panel/" class="btn btn-secondary">↩️ Cancelar</a>
                            </form>
                        </div>
                    </body>
                </html>
            """)

        elif request.method == 'POST':
            # Procesar la suspensión
            if asociacion.estado != 'suspendida':
                asociacion.estado = 'suspendida'
                asociacion.fecha_modificacion_estado = timezone.now()
                asociacion.save()

                # Enviar notificaciones
                enviar_notificacion_suspension(asociacion)

            # Contar animales afectados
            animales_count = asociacion.animales.count()

            return HttpResponse("""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #f59e0b;">✅ Asociación suspendida exitosamente</h2>
                        <p>La asociación "<strong>{}</strong>" ha sido suspendida.</p>
                        <p style="color: #666;">Fecha de suspensión: {}</p>
                        <p style="color: #666;">Animales afectados: {}</p>
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                            <strong>✓</strong> La asociación no podrá iniciar sesión<br>
                            <strong>✓</strong> Sus animales seguirán siendo visibles en la web
                        </div>
                        <hr style="margin: 30px 0;">
                        <p><a href="/gestion/reactivar/{}/" style="color: #10b981;">🔄 Reactivar asociación</a></p>
                        <p><a href="/gestion/eliminar/{}/" style="color: #ef4444;">🗑️ Eliminar definitivamente</a></p>
                        <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                    </body>
                </html>
            """.format(
                asociacion.nombre,
                timezone.now().strftime("%d/%m/%Y %H:%M"),
                animales_count,
                asociacion.token_gestion,
                asociacion.token_gestion
            ))

    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #ef4444;">❌ Error</h2>
                    <p>Token inválido o asociación no encontrada.</p>
                    <p style="color: #666;">El enlace puede haber expirado o ser incorrecto.</p>
                    <hr style="margin: 30px 0;">
                    <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                </body>
            </html>
        """, status=404)


@csrf_protect
def eliminar_asociacion(request, token):
    """Vista para eliminar definitivamente una asociación - Ahora con confirmación POST"""
    try:
        # Buscar por ambos tokens para compatibilidad
        asociacion = None
        try:
            asociacion = RegistroAsociacion.objects.get(token_gestion=token)
        except RegistroAsociacion.DoesNotExist:
            asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)

        if request.method == 'GET':
            # Mostrar página de confirmación
            if asociacion.estado == 'eliminada':
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #ef4444;">❌ Asociación ya eliminada</h2>
                            <p>La asociación "<strong>{}</strong>" ya fue eliminada anteriormente.</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                        </body>
                    </html>
                """.format(asociacion.nombre))

            # Contar datos antes de eliminar
            animales_count = asociacion.animales.count()

            # Mostrar formulario de confirmación
            csrf_token = get_token(request)
            return HttpResponse(f"""
                <html>
                    <head>
                        <title>Confirmar Eliminación</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                            .form-container {{ background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                            .btn {{ padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                            .btn-danger {{ background: #ef4444; color: white; }}
                            .btn-secondary {{ background: #6b7280; color: white; margin-left: 10px; }}
                        </style>
                    </head>
                    <body>
                        <div class="form-container">
                            <h2 style="color: #ef4444;">🗑️ Confirmar Eliminación Definitiva</h2>
                            <p><strong>Asociación:</strong> {asociacion.nombre}</p>
                            <p><strong>Email:</strong> {asociacion.email}</p>
                            <p><strong>Estado actual:</strong> {asociacion.get_estado_display()}</p>
                            <p><strong>Animales registrados:</strong> {animales_count}</p>

                            <div style="background: #fee2e2; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ef4444;">
                                <strong>⚠️ ATENCIÓN:</strong> Esta acción es <strong>PERMANENTE</strong> y no se puede deshacer.<br>
                                - La asociación no podrá iniciar sesión<br>
                                - Sus animales no aparecerán en las búsquedas<br>
                                - Toda la información quedará marcada como eliminada
                            </div>

                            <form method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                <button type="submit" class="btn btn-danger" onclick="return confirm('¿ESTÁS ABSOLUTAMENTE SEGURO? Esta acción NO se puede deshacer.');">🗑️ ELIMINAR DEFINITIVAMENTE</button>
                                <a href="/admin/panel/" class="btn btn-secondary">↩️ Cancelar</a>
                            </form>
                        </div>
                    </body>
                </html>
            """)

        elif request.method == 'POST':
            # Procesar la eliminación
            nombre_asociacion = asociacion.nombre
            animales_count = asociacion.animales.count()

            if asociacion.estado != 'eliminada':
                # Marcar como eliminada (soft delete)
                asociacion.estado = 'eliminada'
                asociacion.fecha_modificacion_estado = timezone.now()
                asociacion.save()

                # Enviar notificaciones
                enviar_notificacion_eliminacion(asociacion)

            return HttpResponse("""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #ef4444;">✅ Asociación eliminada definitivamente</h2>
                        <p>La asociación "<strong>{}</strong>" ha sido eliminada.</p>
                        <p style="color: #666;">Fecha de eliminación: {}</p>
                        <p style="color: #666;">Animales que tenía: {}</p>
                        <div style="background: #fee2e2; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ef4444;">
                            <strong>✓</strong> La asociación no puede iniciar sesión<br>
                            <strong>✓</strong> Sus animales no aparecen en las búsquedas<br>
                            <strong>✓</strong> Esta acción es permanente
                        </div>
                        <hr style="margin: 30px 0;">
                        <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                    </body>
                </html>
            """.format(
                nombre_asociacion,
                timezone.now().strftime("%d/%m/%Y %H:%M"),
                animales_count
            ))

    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #ef4444;">❌ Error</h2>
                    <p>Token inválido o asociación no encontrada.</p>
                    <p style="color: #666;">El enlace puede haber expirado o ser incorrecto.</p>
                    <hr style="margin: 30px 0;">
                    <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                </body>
            </html>
        """, status=404)


@csrf_protect
def reactivar_asociacion(request, token):
    """Vista para reactivar una asociación suspendida - Ahora con confirmación POST"""
    try:
        # Buscar por ambos tokens para compatibilidad
        asociacion = None
        try:
            asociacion = RegistroAsociacion.objects.get(token_gestion=token)
        except RegistroAsociacion.DoesNotExist:
            asociacion = RegistroAsociacion.objects.get(token_aprobacion=token)

        if request.method == 'GET':
            # Mostrar página de confirmación
            if asociacion.estado == 'eliminada':
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #ef4444;">❌ No se puede reactivar</h2>
                            <p>La asociación "<strong>{}</strong>" fue eliminada y no puede reactivarse.</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                        </body>
                    </html>
                """.format(asociacion.nombre))

            if asociacion.estado == 'activa':
                return HttpResponse("""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h2 style="color: #10b981;">✅ Asociación ya activa</h2>
                            <p>La asociación "<strong>{}</strong>" ya está activa.</p>
                            <hr style="margin: 30px 0;">
                            <p><a href="/gestion/suspender/{}/" style="color: #f59e0b;">⏸️ Suspender asociación</a></p>
                            <p><a href="/gestion/eliminar/{}/" style="color: #ef4444;">🗑️ Eliminar definitivamente</a></p>
                            <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                        </body>
                    </html>
                """.format(asociacion.nombre, asociacion.token_gestion, asociacion.token_gestion))

            # Mostrar formulario de confirmación
            animales_count = asociacion.animales.count()
            csrf_token = get_token(request)
            return HttpResponse(f"""
                <html>
                    <head>
                        <title>Confirmar Reactivación</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                            .form-container {{ background: #f8f9fa; padding: 30px; border-radius: 10px; }}
                            .btn {{ padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
                            .btn-success {{ background: #10b981; color: white; }}
                            .btn-secondary {{ background: #6b7280; color: white; margin-left: 10px; }}
                        </style>
                    </head>
                    <body>
                        <div class="form-container">
                            <h2 style="color: #10b981;">🔄 Confirmar Reactivación</h2>
                            <p><strong>Asociación:</strong> {asociacion.nombre}</p>
                            <p><strong>Email:</strong> {asociacion.email}</p>
                            <p><strong>Estado actual:</strong> {asociacion.get_estado_display()}</p>
                            <p><strong>Animales registrados:</strong> {animales_count}</p>

                            <div style="background: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10b981;">
                                <strong>✓ Resultado:</strong> La asociación podrá iniciar sesión y gestionar sus animales normalmente.
                            </div>

                            <form method="post">
                                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                                <button type="submit" class="btn btn-success">🔄 Confirmar Reactivación</button>
                                <a href="/admin/panel/" class="btn btn-secondary">↩️ Cancelar</a>
                            </form>
                        </div>
                    </body>
                </html>
            """)

        elif request.method == 'POST':
            # Procesar la reactivación
            if asociacion.estado != 'activa':
                asociacion.estado = 'activa'
                asociacion.fecha_modificacion_estado = timezone.now()
                asociacion.save()

                # Enviar notificaciones
                enviar_notificacion_reactivacion(asociacion)

            animales_count = asociacion.animales.count()

            return HttpResponse("""
                <html>
                    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                        <h2 style="color: #10b981;">✅ Asociación reactivada exitosamente</h2>
                        <p>La asociación "<strong>{}</strong>" ha sido reactivada.</p>
                        <p style="color: #666;">Fecha de reactivación: {}</p>
                        <p style="color: #666;">Animales disponibles: {}</p>
                        <div style="background: #d1fae5; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10b981;">
                            <strong>✓</strong> La asociación ya puede iniciar sesión<br>
                            <strong>✓</strong> Puede gestionar sus animales normalmente
                        </div>
                        <hr style="margin: 30px 0;">
                        <p><a href="/gestion/suspender/{}/" style="color: #f59e0b;">⏸️ Suspender asociación</a></p>
                        <p><a href="/gestion/eliminar/{}/" style="color: #ef4444;">🗑️ Eliminar definitivamente</a></p>
                        <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Panel de Administración</a></p>
                    </body>
                </html>
            """.format(
                asociacion.nombre,
                timezone.now().strftime("%d/%m/%Y %H:%M"),
                animales_count,
                asociacion.token_gestion,
                asociacion.token_gestion
            ))

    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h2 style="color: #ef4444;">❌ Error</h2>
                    <p>Token inválido o asociación no encontrada.</p>
                    <p style="color: #666;">El enlace puede haber expirado o ser incorrecto.</p>
                    <hr style="margin: 30px 0;">
                    <p><a href="/admin/panel/" style="color: #3b82f6;">🏠 Ir al Panel de Administración</a></p>
                </body>
            </html>
        """, status=404)


@require_GET
def info_asociacion(request, token):
    """Vista para mostrar información detallada de la asociación"""
    try:
        asociacion = RegistroAsociacion.objects.get(token_gestion=token)
        animales = asociacion.animales.all()
        animales_activos = animales.filter(adoptado=False)
        animales_adoptados = animales.filter(adoptado=True)
        
        estado_color = {
            'activa': '#10b981',
            'suspendida': '#f59e0b', 
            'eliminada': '#ef4444'
        }
        
        # Generar botones de acción según el estado actual
        def generar_botones_accion():
            if asociacion.estado == 'activa':
                return f"""
                    <a href="/gestion/suspender/{token}/" class="action-btn btn-suspend">⏸️ Suspender</a>
                    <a href="/gestion/eliminar/{token}/" class="action-btn btn-delete">🗑️ Eliminar</a>
                """
            elif asociacion.estado == 'suspendida':
                return f"""
                     <a href="/gestion/reactivar/{token}/" class="action-btn btn-activate">🔄 Reactivar</a>
                    <a href="/gestion/eliminar/{token}/" class="action-btn btn-delete">🗑️ Eliminar</a>
                """
            else:  # eliminada
                return "<p style='color: #666;'>No hay acciones disponibles para asociaciones eliminadas.</p>"
        
        # Generar tabla de animales
        def generar_tabla_animales():
            if not animales_activos.exists():
                return ""
            
            filas = ""
            for animal in animales_activos:
                filas += f"""
                    <tr>
                        <td>{animal.nombre}</td>
                        <td>{animal.tipo_de_animal}</td>
                        <td>{animal.raza}</td>
                        <td>{animal.poblacion}, {animal.provincia}</td>
                        <td>{animal.fecha_creacion.strftime("%d/%m/%Y")}</td>
                    </tr>
                """
            
            return f"""
                <div style="margin: 30px 0;">
                    <h3>🐕 Animales Disponibles</h3>
                    <table class="animals-table">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Tipo</th>
                                <th>Raza</th>
                                <th>Ubicación</th>
                                <th>Fecha</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas}
                        </tbody>
                    </table>
                </div>
            """
        
        return HttpResponse("""
            <html>
                <head>
                    <title>Gestión de Asociación</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        .header {{ text-align: center; margin-bottom: 30px; }}
                        .estado {{ padding: 8px 16px; border-radius: 20px; color: white; display: inline-block; }}
                        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }}
                        .info-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #dee2e6; }}
                        .actions {{ text-align: center; margin: 30px 0; }}
                        .action-btn {{ display: inline-block; padding: 12px 24px; margin: 5px; text-decoration: none; 
                                     border-radius: 6px; font-weight: bold; }}
                        .btn-suspend {{ background: #f59e0b; color: white; }}
                        .btn-activate {{ background: #10b981; color: white; }}
                        .btn-delete {{ background: #ef4444; color: white; }}
                        .animals-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                        .animals-table th, .animals-table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                        .animals-table th {{ background: #f1f3f4; }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Gestión de Asociación</h1>
                        <h2>{}</h2>
                        <span class="estado" style="background: {}">
                            {} 
                        </span>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-box">
                            <h3>📧 Información de Contacto</h3>
                            <p><strong>Email:</strong> {}</p>
                            <p><strong>Teléfono:</strong> {}</p>
                            <p><strong>Dirección:</strong> {}</p>
                            <p><strong>Población:</strong> {} ({})</p>
                            <p><strong>Código Postal:</strong> {}</p>
                        </div>
                        
                        <div class="info-box">
                            <h3>📊 Estadísticas</h3>
                            <p><strong>Fecha de registro:</strong> {}</p>
                            <p><strong>Total de animales:</strong> {}</p>
                            <p><strong>Animales disponibles:</strong> {}</p>
                            <p><strong>Animales adoptados:</strong> {}</p>
                        </div>
                    </div>
                    
                    <div class="actions">
                        {}
                    </div>
                    
                    {}
                    
                </body>
            </html>
        """.format(
            asociacion.nombre,
            estado_color.get(asociacion.estado, '#666'),
            asociacion.get_estado_display().upper(),
            asociacion.email,
            asociacion.telefono, 
            asociacion.direccion,
            asociacion.poblacion,
            asociacion.provincia,
            asociacion.codigo_postal,
            asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M"),
            animales.count(),
            animales_activos.count(),
            animales_adoptados.count(),
            generar_botones_accion(),
            generar_tabla_animales()
        ))
        
    except RegistroAsociacion.DoesNotExist:
        return HttpResponse("❌ Token inválido o asociación no encontrada.", status=404)


# ==================== VISTAS PRINCIPALES ====================

def registro_exitoso_view(request):
    """Vista para mostrar página de registro exitoso"""
    # Esta vista se puede acceder directamente o después de un registro
    return render(request, 'registro_exitoso.html')


def registro_asociacion(request):
    """Vista para registrar una nueva asociación con estado pendiente"""
    # Detectar si es una petición AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = RegistroAsociacionForm(request.POST, request.FILES)

        try:
            if form.is_valid():
                # Continuar con el registro normal - la validación de duplicados ya está en el form
                asociacion = form.save(commit=False)
                password = form.cleaned_data['password']
                asociacion.password = make_password(password)
                asociacion.save()

                # Enviar notificaciones
                try:
                    enviar_email_registro_pendiente(asociacion)
                except Exception as e:
                    print(f"Warning: Error enviando email: {e}")

                try:
                    enviar_notificacion_nueva_asociacion(asociacion, request)
                except Exception as e:
                    print(f"Warning: Error enviando notificación Telegram: {e}")

                # Si es AJAX, devolver respuesta JSON de éxito
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Registro exitoso. Tu asociación está pendiente de aprobación.',
                        'redirect': '/registro_exitoso/'
                    }, status=200)

                # Si no es AJAX, mostrar página de registro exitoso
                return render(request, 'registro_exitoso.html', {
                    'asociacion': asociacion
                })
            else:
                # Formulario no válido - hay errores de validación
                error_messages = []

                # Recopilar todos los errores
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        error_messages.append(str(error))

                error_text = ". ".join(error_messages) if error_messages else 'Error en el formulario. Por favor, verifica los datos.'

                # Si es AJAX, devolver respuesta JSON con errores
                if is_ajax:
                    # Verificar si es error de nombre duplicado
                    if 'nombre' in form.errors:
                        return JsonResponse({
                            'success': False,
                            'error': 'duplicate_name',
                            'message': error_text
                        }, status=400)

                    return JsonResponse({
                        'success': False,
                        'error': 'form_errors',
                        'message': error_text,
                        'form_errors': form.errors
                    }, status=400)

                # Si no es AJAX, mostrar template con errores
                return render(request, 'registro_asociacion.html', {
                    'form': form
                })

        except Exception as e:
            print(f"Error inesperado en registro: {e}")

            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'error': 'server_error',
                    'message': 'Error del servidor. Por favor, intenta nuevamente.'
                }, status=500)

            messages.error(request, 'Error interno del servidor. Por favor, intenta nuevamente.')
            return redirect('inicio')

    else:
        # GET request - mostrar formulario vacío
        form = RegistroAsociacionForm()
        return render(request, 'registro_asociacion.html', {
            'form': form
        })


@require_POST
@csrf_protect
def validar_nombre_asociacion(request):
    """Vista AJAX para validar nombres de asociación en tiempo real"""
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()

        if not nombre:
            return JsonResponse({
                'disponible': True,
                'mensaje': ''
            })

        # Verificar si existe una asociación con ese nombre exacto (case insensitive)
        existe = RegistroAsociacion.objects.filter(nombre__iexact=nombre).exists()

        if existe:
            return JsonResponse({
                'disponible': False,
                'mensaje': 'Ya existe una asociación registrada con este nombre. Por favor, elige otro nombre.'
            })
        else:
            return JsonResponse({
                'disponible': True,
                'mensaje': 'Nombre disponible'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'disponible': True,
            'mensaje': ''
        })
    except Exception as e:
        return JsonResponse({
            'disponible': True,
            'mensaje': ''
        })


def enviar_email_registro_pendiente(asociacion):
    """Envía email inmediato confirmando el registro pendiente"""
    subject = "📋 Registro recibido - En proceso de revisión"
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #f59e0b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1>📋 Registro Recibido</h1>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
                <p>Estimados <strong>{asociacion.nombre}</strong>,</p>
                
                <p>Hemos recibido su solicitud para registrarse en Adopta. Gracias por su interés en ayudar a los animales.</p>
                
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <h3 style="margin: 0; color: #92400e;">⏳ Estado: En Revisión</h3>
                    <p style="margin: 10px 0 0 0; color: #a16207;">
                        Su solicitud está siendo revisada por nuestro equipo. Le notificaremos el resultado por email.
                    </p>
                </div>
                
                <h3>📝 Datos registrados:</h3>
                <ul>
                    <li><strong>Nombre:</strong> {asociacion.nombre}</li>
                    <li><strong>Email:</strong> {asociacion.email}</li>
                    <li><strong>Ubicación:</strong> {asociacion.poblacion}, {asociacion.provincia}</li>
                    <li><strong>Fecha:</strong> {asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M")}</li>
                </ul>
                
                <div style="background: #e0e7ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #3730a3; font-size: 14px;">
                        <strong>💡 Mientras espera:</strong> No intente iniciar sesión todavía. 
                        Le enviaremos un correo cuando su cuenta esté lista.
                    </p>
                </div>
                
                <p>Si tiene alguna pregunta, puede responder a este correo.</p>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Equipo de Adopta
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Su registro para {asociacion.nombre} está en revisión.",
            from_email=None,
            to=[asociacion.email]
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Email de confirmación enviado a: {asociacion.email}")
    except Exception as e:
        print(f"❌ Error enviando email de confirmación: {e}")

def enviar_email_admin_nueva_asociacion(asociacion, request):
    """Envía email al admin con la nueva asociación para revisar"""
    domain = request.get_host()
    protocol = 'https' if request.is_secure() else 'http'
    base_url = f"{protocol}://{domain}"
    
    url_aprobar = f"{base_url}/admin/aprobar/{asociacion.token_aprobacion}/"
    url_rechazar = f"{base_url}/admin/rechazar/{asociacion.token_aprobacion}/"
    url_info = f"{base_url}/admin/info/{asociacion.token_aprobacion}/"
    url_panel = f"{base_url}/admin/panel/"

    subject = f"🆕 Nueva asociación pendiente: {asociacion.nombre}"
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="background: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1>🆕 Nueva Asociación Registrada</h1>
                <p style="margin: 5px 0; opacity: 0.9;">Requiere revisión y aprobación</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px;">
                <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin: 0 0 25px 0; border-left: 4px solid #f59e0b;">
                    <h2 style="margin: 0 0 10px 0; color: #92400e;">⏳ Acción Requerida</h2>
                    <p style="margin: 0; color: #a16207;">Una nueva asociación se ha registrado y necesita tu aprobación.</p>
                </div>
                
                <h3 style="color: #1f2937;">📋 Información de la Asociación</h3>
                <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <p><strong>Nombre:</strong> {asociacion.nombre}</p>
                            <p><strong>Email:</strong> {asociacion.email}</p>
                            <p><strong>Teléfono:</strong> {asociacion.telefono}</p>
                            <p><strong>Dirección:</strong> {asociacion.direccion}</p>
                        </div>
                        <div>
                            <p><strong>Población:</strong> {asociacion.poblacion}</p>
                            <p><strong>Provincia:</strong> {asociacion.provincia}</p>
                            <p><strong>Código Postal:</strong> {asociacion.codigo_postal}</p>
                            <p><strong>Fecha registro:</strong> {asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M")}</p>
                        </div>
                    </div>
                </div>
                
                <h3 style="color: #1f2937; margin-top: 30px;">⚡ Acciones Rápidas</h3>
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{url_aprobar}" style="background: #10b981; color: white; padding: 15px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; display: inline-block;">
                        ✅ Aprobar Inmediatamente
                    </a>
                    <a href="{url_rechazar}" style="background: #ef4444; color: white; padding: 15px 25px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; display: inline-block;">
                        ❌ Rechazar con Motivo
                    </a>
                </div>
                
                <div style="text-align: center; margin: 15px 0;">
                    <a href="{url_info}" style="background: #3b82f6; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; display: inline-block;">
                        👁️ Ver Información Completa
                    </a>
                    <a href="{url_panel}" style="background: #6b7280; color: white; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 5px; display: inline-block;">
                        🏠 Panel de Administración
                    </a>
                </div>
                
                <div style="background: #e0e7ff; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #3730a3;">🔐 Información de Tokens</h4>
                    <p style="margin: 0; color: #4338ca; font-size: 14px;">
                        <strong>Token de aprobación:</strong> <code>{asociacion.token_aprobacion}</code><br>
                        <small>Este token permite acciones de aprobación/rechazo</small>
                    </p>
                </div>
                
                <div style="background: #fee2e2; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #7f1d1d; font-size: 14px;">
                        <strong>⚠️ Importante:</strong> La asociación está esperando tu aprobación y no puede acceder hasta que tomes una decisión.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Nueva asociación registrada: {asociacion.nombre}. Token: {asociacion.token_aprobacion}",
            from_email=None,
            to=['alvaro_m_a@icloud.com']
        )
        email.attach_alternative(mensaje_html, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Email de revisión enviado para: {asociacion.nombre}")
    except Exception as e:
        print(f"❌ Error enviando email de revisión: {e}")

def login_view(request):
    """Vista de login actualizada para manejar estados pendientes y rechazados"""
    error_message = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                asociacion = RegistroAsociacion.objects.get(nombre=username)

                # Verificar contraseña
                if check_password(password, asociacion.password):
                    
                    # VERIFICAR ESTADO DE LA ASOCIACIÓN
                    if asociacion.estado == 'pendiente':
                        error_message = {
                            'tipo': 'pendiente',
                            'mensaje': 'Tu asociación está pendiente de aprobación.',
                            'detalle': 'Recibirás un email cuando sea aprobada. Mientras tanto, revisa tu correo.'
                        }
                    elif asociacion.estado == 'rechazada':
                        motivo = asociacion.motivo_rechazo or "No se especificó un motivo."
                        error_message = {
                            'tipo': 'rechazada',
                            'mensaje': 'Tu asociación fue rechazada.',
                            'detalle': f'Motivo: {motivo}'
                        }
                        response = redirect('inicio')
                    elif asociacion.estado == 'suspendida':
                        error_message = {
                            'tipo': 'suspendida',
                            'mensaje': 'Tu asociación ha sido suspendida temporalmente.',
                            'detalle': 'Contacta con el administrador si crees que es un error.'
                        }
                        response = redirect('inicio')
                    elif asociacion.estado == 'eliminada':
                        error_message = {
                            'tipo': 'eliminada', 
                            'mensaje': 'Esta asociación ha sido eliminada.',
                            'detalle': 'No es posible acceder con esta cuenta.'
                        }
                    elif asociacion.estado == 'activa':
                        # SECURITY: Regenerar sesión para prevenir session fixation
                        request.session.cycle_key()

                        # Login exitoso
                        response = redirect('inicio')
                        max_age = 86400  # 24 horas
                        response.set_cookie('asociacion_id', asociacion.id, max_age=max_age)

                        request.session['esta_logueado'] = True
                        request.session['asociacion_nombre'] = asociacion.nombre
                        request.session['asociacion_estado'] = asociacion.estado

                        return response
                    else:
                        error_message = {
                            'tipo': 'desconocido',
                            'mensaje': 'Estado de asociación desconocido.',
                            'detalle': 'Contacta con el administrador.'
                        }
                else:
                    form.add_error(None, 'Contraseña incorrecta.')
                    
            except RegistroAsociacion.DoesNotExist:
                form.add_error(None, 'No existe una asociación con ese nombre.')
    else:
        form = LoginForm()

    return render(request, 'index.html', {
        'form': form,
        'error_message': error_message
    })


def logout_view(request):
    """Vista para cerrar sesión"""
    response = redirect('inicio')
    response.delete_cookie('asociacion_id')
    request.session.flush()
    return response


def Inicio(request):
    """Vista de inicio actualizada que filtra asociaciones eliminadas"""
    # Solo mostrar animales de asociaciones activas y suspendidas
    animales = CreacionAnimales.objects.filter(
        asociacion__estado__in=['activa', 'suspendida']
    ).select_related('asociacion')
    
    asociacion_id = request.COOKIES.get('asociacion_id')
    mis_animales = None
    
    if asociacion_id:
        try:
            asociacion = RegistroAsociacion.objects.get(id=asociacion_id)
            
            # Verificar si la asociación puede acceder
            if asociacion.puede_acceder():
                mis_animales = CreacionAnimales.objects.filter(asociacion=asociacion)
                
                return render(request, 'index.html', {
                    'asociacion': asociacion,
                    'logueado': True,
                    'animales': animales,
                    'mis_animales': mis_animales
                })
            else:
                # Asociación suspendida o eliminada, limpiar sesión
                response = render(request, 'index.html', {
                    'logueado': False, 
                    'animales': animales,
                    'mis_animales': None
                })
                response.delete_cookie('asociacion_id')
                return response
                
        except RegistroAsociacion.DoesNotExist:
            pass
            
    return render(request, 'index.html', {
        'logueado': False, 
        'animales': animales,
        'mis_animales': None
    })


# Alias para compatibilidad
def inicio(request):
    """Alias de Inicio para compatibilidad con URLs"""
    return Inicio(request)


@session_login_required
def crear_animal(request):
    """Vista para crear un nuevo animal"""
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    
    if request.method == 'POST':
        form = CreacionAnimalesForm(request.POST, request.FILES, asociacion=asociacion)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.asociacion = asociacion
            
            # PROCESAR COLOR MANUALMENTE
            color_predefinido = request.POST.get('color_predefinido', '')
            color_personalizado = request.POST.get('color_personalizado', '')
            color_final = request.POST.get('color', '')
            
            # Lógica para determinar el color final
            if color_predefinido and color_predefinido != 'Otro':
                animal.color = color_predefinido
            elif color_predefinido == 'Otro' and color_personalizado:
                animal.color = color_personalizado
            elif color_final:
                animal.color = color_final
            else:
                animal.color = "No especificado"
            
            animal.save()
            
            # OPCIONAL: Notificar nuevos animales por Telegram
            # from .telegram_utils import enviar_notificacion_nuevo_animal
            # enviar_notificacion_nuevo_animal(animal)
            
            return redirect('mis_animales')
        else:
            print("Errores del formulario:", form.errors)
    else:
        form = CreacionAnimalesForm(asociacion=asociacion)
    
    return render(request, 'creacion_de_animales.html', {
        'form': form,
        'asociacion': asociacion
    })


def vista_animal(request, animal_id):
    """Vista de animal actualizada que verifica estado de la asociación"""
    try:
        animal = get_object_or_404(
            CreacionAnimales.objects.select_related('asociacion'), 
            id=animal_id,
            asociacion__estado__in=['activa', 'suspendida']  # Solo mostrar si no está eliminada
        )
        return render(request, 'vista_animal.html', {'animal': animal})
    except:
        # Redirigir al inicio si el animal no existe o su asociación está eliminada
        return redirect('inicio')


# Alias para compatibilidad
def ver_animal(request, animal_id):
    """Alias de vista_animal para compatibilidad con URLs"""
    return vista_animal(request, animal_id)


@session_login_required
def mis_animales(request):
    """Vista para mostrar los animales de la asociación logueada"""
    if not request.session.get('esta_logueado'):
        return redirect('login')
    
    asociacion_id = request.COOKIES.get('asociacion_id')
    mis_animales = CreacionAnimales.objects.filter(asociacion_id=asociacion_id)
    
    return render(request, 'mis_animales.html', {
        'mis_animales': mis_animales,
        'asociacion_nombre': request.session.get('asociacion_nombre')
    })


@session_login_required
def editar_animal(request, animal_id):
    """Vista para editar un animal con verificación de propiedad"""
    asociacion_id = request.COOKIES.get('asociacion_id')
    if not asociacion_id:
        return HttpResponseForbidden("Sesión no válida")

    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    animal = get_object_or_404(CreacionAnimales, id=animal_id)

    # SECURITY: Verificar que el animal pertenece a la asociación logueada
    if animal.asociacion.id != int(asociacion_id):
        return HttpResponseForbidden("No tienes permisos para editar este animal")
    
    if request.method == 'POST':
        # PROCESAR COLOR IGUAL QUE EN CREAR_ANIMAL
        color_predefinido = request.POST.get('color_predefinido', '')
        color_personalizado = request.POST.get('color_personalizado', '')
        color_final = request.POST.get('color', '')
        
        # Lógica para determinar el color final
        if color_predefinido and color_predefinido != 'Otro':
            nuevo_color = color_predefinido
        elif color_predefinido == 'Otro' and color_personalizado:
            nuevo_color = color_personalizado
        elif color_final:
            nuevo_color = color_final
        else:
            nuevo_color = "No especificado"
        
        # Actualizar todos los campos
        animal.nombre = request.POST.get('nombre')
        animal.tipo_de_animal = request.POST.get('tipo_de_animal')
        animal.raza = request.POST.get('raza')
        animal.color = nuevo_color
        animal.email = request.POST.get('email')
        animal.telefono = request.POST.get('telefono')
        animal.poblacion = request.POST.get('poblacion')
        animal.provincia = request.POST.get('provincia')
        animal.codigo_postal = request.POST.get('codigo_postal')
        animal.descripcion = request.POST.get('descripcion')
        
        # Manejar archivos
        if 'imagen' in request.FILES:
            animal.imagen = request.FILES['imagen']
        if 'video' in request.FILES:
            animal.video = request.FILES['video']
        
        animal.save()
        return redirect('mis_animales')
    
    return render(request, 'editar_animal.html', {
        'animal': animal,
        'asociacion': asociacion
    })


@session_login_required
def eliminar_animal(request, animal_id):
    """Vista para eliminar un animal con verificación de propiedad"""
    asociacion_id = request.COOKIES.get('asociacion_id')
    if not asociacion_id:
        return HttpResponseForbidden("Sesión no válida")

    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    animal = get_object_or_404(CreacionAnimales, id=animal_id)

    # SECURITY: Verificar que el animal pertenece a la asociación logueada
    if animal.asociacion.id != int(asociacion_id):
        return HttpResponseForbidden("No tienes permisos para eliminar este animal")
    
    if request.method == 'POST':
        animal.delete()
        return redirect('mis_animales')
    
    return render(request, 'confirmar_eliminar.html', {
        'animal': animal,
        'asociacion': asociacion
    })


@session_login_required
def toggle_adopcion_ajax(request, animal_id):
    """Toggle de adopción AJAX"""
    if request.method == 'POST':
        try:
            # Obtener la asociación logueada
            asociacion_id = request.COOKIES.get('asociacion_id')
            if not asociacion_id:
                return JsonResponse({'error': 'Sesión no válida'}, status=401)
                
            asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
            
            # Buscar el animal que pertenece a esta asociación
            animal = CreacionAnimales.objects.get(id=animal_id, asociacion=asociacion)
            animal.adoptado = not animal.adoptado
            animal.save()
            
            return JsonResponse({'adoptado': animal.adoptado})
        except CreacionAnimales.DoesNotExist:
            return JsonResponse({'error': 'Animal no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def mis_favoritos(request):
    """Vista de favoritos actualizada que filtra asociaciones eliminadas"""
    # Solo animales de asociaciones activas y suspendidas
    animales = CreacionAnimales.objects.filter(
        asociacion__estado__in=['activa', 'suspendida']
    ).select_related('asociacion').order_by('-id')
    
    context = {
        'animales': animales,
        'page_title': 'Mis Favoritos - Adopta'
    }
    
    return render(request, 'mis_favoritos.html', context)


def obtener_animales_favoritos(request):
    """Vista AJAX para obtener solo los animales que están en favoritos"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids_favoritos = data.get('favoritos', [])
            
            # Filtrar animales por los IDs favoritos
            animales_favoritos = CreacionAnimales.objects.filter(id__in=ids_favoritos)
            
            # Convertir a lista de diccionarios
            animales_data = []
            for animal in animales_favoritos:
                animal_dict = {
                    'id': animal.id,
                    'nombre': animal.nombre,
                    'tipo': animal.tipo_de_animal,
                    'raza': animal.raza,
                    'email': animal.email,
                    'telefono': animal.telefono,
                    'poblacion': animal.poblacion,
                    'provincia': animal.provincia,
                    'descripcion': animal.descripcion,
                    'imagen': animal.imagen.url if animal.imagen else None,
                }
                animales_data.append(animal_dict)
            
            return JsonResponse({
                'success': True,
                'animales': animales_data,
                'total': len(animales_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})



def buscador_avanzado(request):
    """
    Buscador avanzado con filtros dependientes
    """
    try:
        # Solo incluir animales de asociaciones activas y suspendidas, no adoptados
        animales_disponibles = CreacionAnimales.objects.filter(
            asociacion__estado__in=['activa', 'suspendida'],
            adoptado=False
        ).select_related('asociacion')
        
        # Convertir animales a lista de diccionarios para JavaScript
        animales_list = []
        for animal in animales_disponibles:
            # Determinar categoría del animal
            tipo_lower = animal.tipo_de_animal.lower()
            if 'perro' in tipo_lower:
                categoria = 'perro'
            elif 'gato' in tipo_lower:
                categoria = 'gato'
            else:
                categoria = 'otros'
                
            animales_list.append({
                'id': animal.id,
                'nombre': animal.nombre,
                'tipo_de_animal': animal.tipo_de_animal,
                'raza': animal.raza or 'Sin especificar',
                'color': animal.color or 'Sin especificar',
                'provincia': animal.provincia or 'Sin especificar',
                'poblacion': animal.poblacion or 'Sin especificar',
                'categoria': categoria,
                'descripcion': animal.descripcion[:100] + '...' if len(animal.descripcion or '') > 100 else animal.descripcion,
                'imagen_url': animal.imagen.url if animal.imagen else None,
                'asociacion_nombre': animal.asociacion.nombre
            })
        
        # Preparar datos para JavaScript
        datos_filtros = {
            'animales': animales_list,
            'total_animales': len(animales_list)
        }
        
        # Convertir a JSON para el template
        datos_filtros_json = json.dumps(datos_filtros, ensure_ascii=False)
        
        context = {
            'datos_filtros': datos_filtros_json,
            'total_animales': len(animales_list),
            'page_title': 'Buscador Avanzado - Adopta'
        }
        
        return render(request, 'buscador_avanzado.html', context)
        
    except Exception as e:
        # Context de fallback en caso de error
        context = {
            'datos_filtros': '{"animales": [], "total_animales": 0}',
            'total_animales': 0,
            'page_title': 'Buscador Avanzado - Adopta'
        }
        return render(request, 'buscador_avanzado.html', context)


def resultados_busqueda(request):
    """Resultados de búsqueda actualizados que filtran asociaciones eliminadas"""
    raza = request.GET.get('raza', '')
    ubicacion = request.GET.get('ubicacion', '')
    color = request.GET.get('color', '')
    tipo = request.GET.get('tipo', '')
    
    # Solo animales de asociaciones activas y suspendidas
    animales = CreacionAnimales.objects.filter(
        asociacion__estado__in=['activa', 'suspendida']
    ).select_related('asociacion')
    
    # Aplicar filtros
    if raza:
        animales = animales.filter(raza__icontains=raza)
    if ubicacion:
        animales = animales.filter(provincia__icontains=ubicacion)
    if color:
        animales = animales.filter(color__icontains=color)
    if tipo:
        animales = animales.filter(tipo_de_animal__icontains=tipo)
    
    total_resultados = animales.count()
    
    # Crear mensaje de búsqueda
    filtros_aplicados = []
    if raza:
        filtros_aplicados.append(f"raza: {raza}")
    if ubicacion:
        filtros_aplicados.append(f"ubicación: {ubicacion}")
    if color:
        filtros_aplicados.append(f"color: {color}")
    if tipo:
        filtros_aplicados.append(f"tipo: {tipo}")
    
    mensaje_busqueda = f"Resultados para: {', '.join(filtros_aplicados)}" if filtros_aplicados else "Todos los animales disponibles"
    
    context = {
        'animales': animales,
        'total_resultados': total_resultados,
        'mensaje_busqueda': mensaje_busqueda,
        'filtros': {
            'raza': raza,
            'ubicacion': ubicacion,
            'color': color,
            'tipo': tipo,
        }
    }
    
    return render(request, 'resultados_busqueda.html', context)


def acerca(request):
    """Vista para la página Acerca de"""
    return render(request, 'acerca.html')


@require_GET
def panel_administracion(request):
    """Panel de administración moderno para gestionar asociaciones"""
    
    # Obtener asociaciones por estado
    pendientes = RegistroAsociacion.objects.filter(estado='pendiente').order_by('-fecha_registro')
    activas = RegistroAsociacion.objects.filter(estado='activa').order_by('-fecha_aprobacion')
    suspendidas = RegistroAsociacion.objects.filter(estado='suspendida').order_by('-fecha_modificacion_estado')
    rechazadas = RegistroAsociacion.objects.filter(estado='rechazada').order_by('-fecha_rechazo')
    
    # Preparar datos para el template
    context = {
        'pendientes': pendientes,
        'activas': activas,
        'suspendidas': suspendidas,
        'rechazadas': rechazadas,
        'stats': {
            'pendientes_count': pendientes.count(),
            'activas_count': activas.count(),
            'suspendidas_count': suspendidas.count(),
            'rechazadas_count': rechazadas.count(),
            'total_count': pendientes.count() + activas.count() + suspendidas.count() + rechazadas.count(),
        }
    }
    
    return render(request, 'admin_panel.html', context)