import requests
import json
import os
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth.hashers import make_password

# Configurar logging
logger = logging.getLogger(__name__)

# Configuración segura del bot de Telegram
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '6344843081')

# Verificar que las credenciales estén configuradas
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    raise ImproperlyConfigured(
        "Las credenciales de Telegram no están configuradas. "
        "Asegúrate de definir TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en las variables de entorno."
    )

# ==================== SISTEMA DE ESTADOS CONVERSACIONALES ====================
# Almacenamiento temporal de estados (en producción usar Redis o base de datos)
ESTADOS_CONVERSACION = {}

def guardar_estado_conversacion(chat_id, estado, datos=None):
    """Guarda el estado de la conversación para un chat específico"""
    ESTADOS_CONVERSACION[chat_id] = {
        'estado': estado,
        'datos': datos or {},
        'timestamp': timezone.now()
    }
    logger.info(f"Estado guardado para chat {chat_id}: {estado}")

def obtener_estado_conversacion(chat_id):
    """Obtiene el estado actual de la conversación"""
    return ESTADOS_CONVERSACION.get(chat_id, None)

def limpiar_estado_conversacion(chat_id):
    """Limpia el estado de la conversación"""
    if chat_id in ESTADOS_CONVERSACION:
        del ESTADOS_CONVERSACION[chat_id]
        logger.info(f"Estado limpiado para chat {chat_id}")

# ==================== FUNCIONES BÁSICAS ====================

def enviar_mensaje_telegram(mensaje, botones=None):
    """Función base para enviar mensajes a Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    # Asegurar que el mensaje esté en UTF-8
    if isinstance(mensaje, str):
        mensaje = mensaje.encode('utf-8', errors='replace').decode('utf-8')

    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown'
    }

    if botones:
        data['reply_markup'] = json.dumps({
            'inline_keyboard': botones
        }, ensure_ascii=False)

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        logger.info("Mensaje de Telegram enviado exitosamente")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión enviando mensaje de Telegram: {e}")
        return False
    except Exception as e:
        logger.error(f"Error general en enviar_mensaje_telegram: {e}")
        return False

def editar_mensaje_telegram(chat_id, message_id, nuevo_texto, botones=None, parse_mode=None):
    """Edita un mensaje existente en Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"

    # Asegurar que el texto esté en UTF-8
    if isinstance(nuevo_texto, str):
        nuevo_texto = nuevo_texto.encode('utf-8', errors='replace').decode('utf-8')

    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': nuevo_texto
    }

    if parse_mode:
        data['parse_mode'] = parse_mode

    if botones:
        data['reply_markup'] = json.dumps({
            'inline_keyboard': botones
        }, ensure_ascii=False)

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        logger.info(f"Mensaje {message_id} editado exitosamente")
        return True
    except requests.exceptions.HTTPError as e:
        # Log más detallado del error de Telegram
        try:
            error_detail = response.json()
            logger.error(f"Error HTTP editando mensaje: Status {response.status_code}")
            logger.error(f"Detalle del error: {error_detail}")
            logger.error(f"Datos enviados: chat_id={chat_id}, message_id={message_id}, texto_length={len(nuevo_texto)}")
        except:
            logger.error(f"Error HTTP editando mensaje: {e}")
            logger.error(f"Response text: {response.text}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión editando mensaje: {e}")
        return False
    except Exception as e:
        logger.error(f"Error general editando mensaje: {e}")
        return False

def responder_callback(callback_query_id, texto=""):
    """Responde al callback query para quitar el spinner"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"

    # Preparar payload como JSON (formato preferido por Telegram)
    payload = {
        'callback_query_id': str(callback_query_id)
    }

    # Si hay texto, agregarlo (opcional)
    if texto:
        payload['text'] = str(texto)[:200]  # Telegram límite de 200 caracteres

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Callback {callback_query_id} respondido exitosamente")
        return True
    except requests.exceptions.HTTPError as e:
        # Log más detallado del error de Telegram
        try:
            error_detail = response.json()
            logger.error(f"Error HTTP respondiendo callback: Status {response.status_code}")
            logger.error(f"Detalle del error: {error_detail}")
            logger.error(f"Datos enviados: callback_query_id={callback_query_id}, texto='{texto}'")
        except:
            logger.error(f"Error HTTP respondiendo callback: {e}")
            logger.error(f"Response text: {response.text}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión respondiendo callback: {e}")
        return False
    except Exception as e:
        logger.error(f"Error general respondiendo callback: {e}")
        return False

# ==================== FUNCIONES DE NOTIFICACIÓN ====================

def enviar_notificacion_nueva_asociacion(asociacion, request):
    """Envía notificación de nueva asociación con URLs directas"""

    # Obtener la URL base del servidor
    try:
        import requests as req
        response = req.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            tunnels = response.json().get('tunnels', [])
            if tunnels:
                base_url = tunnels[0]['public_url']
                logger.info(f"Usando URL de ngrok: {base_url}")
            else:
                raise Exception("No hay túneles activos")
    except:
        # Si no hay ngrok, usar configuración por defecto
        from django.conf import settings
        if hasattr(settings, 'RENDER_EXTERNAL_HOSTNAME') and settings.RENDER_EXTERNAL_HOSTNAME:
            base_url = f"https://{settings.RENDER_EXTERNAL_HOSTNAME}"
        else:
            base_url = "http://127.0.0.1:8000"

    # Construir URLs para las acciones
    url_aprobar = f"{base_url}/admin/aprobar/{asociacion.token_aprobacion}/"
    url_rechazar = f"{base_url}/admin/rechazar/{asociacion.token_aprobacion}/"
    url_panel = f"{base_url}/admin/panel/"

    mensaje = f"""NUEVA ASOCIACIÓN REGISTRADA

Información:
• Nombre: {asociacion.nombre}
• Email: {asociacion.email}
• Teléfono: {asociacion.telefono}
• Ubicación: {asociacion.poblacion}, {asociacion.provincia}
• Fecha: {asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M")}

Estado: Pendiente de aprobación
ID: {asociacion.id}

🔗 Acciones disponibles:
✅ Aprobar: {url_aprobar}
❌ Rechazar: {url_rechazar}
👁️ Panel Admin: {url_panel}
    """

    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_aprobacion(asociacion):
    """Envía notificación de asociación aprobada"""
    mensaje = f"""
✅ <b>ASOCIACIÓN APROBADA</b>

📋 <b>Asociación:</b> {asociacion.nombre}
📧 <b>Email:</b> {asociacion.email}
📍 <b>Ubicación:</b> {asociacion.poblacion}, {asociacion.provincia}
📅 <b>Aprobada:</b> {asociacion.fecha_aprobacion.strftime("%d/%m/%Y %H:%M")}

✉️ Email de confirmación enviado a la asociación.
🎉 Ya pueden acceder al sistema.
    """
    
    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_rechazo(asociacion, motivo):
    """Envía notificación de asociación rechazada"""
    mensaje = f"""
❌ <b>ASOCIACIÓN RECHAZADA</b>

📋 <b>Asociación:</b> {asociacion.nombre}
📧 <b>Email:</b> {asociacion.email}
📅 <b>Rechazada:</b> {asociacion.fecha_rechazo.strftime("%d/%m/%Y %H:%M")}

📝 <b>Motivo:</b>
{motivo}

✉️ Email explicativo enviado a la asociación.
    """

    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_rechazo_web(nombre_asociacion, email_asociacion, motivo):
    """Envía notificación de asociación rechazada desde el panel web"""
    from django.utils import timezone

    mensaje = f"""
❌ <b>ASOCIACIÓN RECHAZADA (PANEL WEB)</b>

📋 <b>Asociación:</b> {nombre_asociacion}
📧 <b>Email:</b> {email_asociacion}
📅 <b>Rechazada:</b> {timezone.now().strftime("%d/%m/%Y %H:%M")}

📝 <b>Motivo:</b>
{motivo}

✉️ Email explicativo enviado a la asociación.
🗑️ <b>La asociación ha sido eliminada permanentemente del sistema.</b>

<i>Acción realizada por: Administrador Web</i>
    """

    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_suspension(asociacion):
    """Envía notificación de asociación suspendida"""
    animales_count = asociacion.animales.count()
    
    mensaje = f"""
⏸️ <b>ASOCIACIÓN SUSPENDIDA</b>

📋 <b>Asociación:</b> {asociacion.nombre}
📧 <b>Email:</b> {asociacion.email}
📍 <b>Ubicación:</b> {asociacion.poblacion}, {asociacion.provincia}
📅 <b>Suspendida:</b> {asociacion.fecha_modificacion_estado.strftime("%d/%m/%Y %H:%M")}

🐕 <b>Animales afectados:</b> {animales_count}

⚠️ La asociación no puede acceder, pero sus animales siguen visibles.
    """
    
    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_reactivacion(asociacion):
    """Envía notificación de asociación reactivada"""
    animales_count = asociacion.animales.count()
    
    mensaje = f"""
🔄 <b>ASOCIACIÓN REACTIVADA</b>

📋 <b>Asociación:</b> {asociacion.nombre}
📧 <b>Email:</b> {asociacion.email}
📍 <b>Ubicación:</b> {asociacion.poblacion}, {asociacion.provincia}
📅 <b>Reactivada:</b> {asociacion.fecha_modificacion_estado.strftime("%d/%m/%Y %H:%M")}

🐕 <b>Animales disponibles:</b> {animales_count}

✅ La asociación ya puede acceder normalmente al sistema.
    """
    
    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_eliminacion(asociacion):
    """Envía notificación de asociación eliminada"""
    animales_count = asociacion.animales.count()
    
    mensaje = f"""
🗑️ <b>ASOCIACIÓN ELIMINADA</b>

📋 <b>Asociación:</b> {asociacion.nombre}
📧 <b>Email:</b> {asociacion.email}
📍 <b>Ubicación:</b> {asociacion.poblacion}, {asociacion.provincia}
📅 <b>Eliminada:</b> {asociacion.fecha_modificacion_estado.strftime("%d/%m/%Y %H:%M")}

🐕 <b>Animales que tenía:</b> {animales_count}

❌ Eliminación permanente. No pueden acceder y sus animales no aparecen.
    """
    
    return enviar_mensaje_telegram(mensaje)

def enviar_notificacion_nuevo_animal(animal):
    """Envía notificación cuando una asociación registra un nuevo animal"""
    mensaje = f"""
🐕 <b>NUEVO ANIMAL REGISTRADO</b>

🏷️ <b>Nombre:</b> {animal.nombre}
🐾 <b>Tipo:</b> {animal.tipo_de_animal}
🎨 <b>Raza:</b> {animal.raza}
📍 <b>Ubicación:</b> {animal.poblacion}, {animal.provincia}

🏢 <b>Asociación:</b> {animal.asociacion.nombre}
📅 <b>Registrado:</b> {animal.fecha_creacion.strftime("%d/%m/%Y %H:%M")}
    """
    
    return enviar_mensaje_telegram(mensaje)

def enviar_estadisticas_diarias():
    """Envía un resumen diario de la actividad de la plataforma"""
    from .models import RegistroAsociacion, CreacionAnimales
    from django.utils import timezone
    from datetime import datetime, timedelta

    hoy = timezone.now().date()
    ayer = hoy - timedelta(days=1)

    # Obtener estadísticas
    nuevas_asociaciones = RegistroAsociacion.objects.filter(fecha_registro__date=ayer).count()
    asociaciones_aprobadas = RegistroAsociacion.objects.filter(fecha_aprobacion__date=ayer).count()
    nuevos_animales = CreacionAnimales.objects.filter(fecha_creacion__date=ayer).count()
    total_asociaciones = RegistroAsociacion.objects.filter(estado='activa').count()
    total_animales = CreacionAnimales.objects.filter(adoptado=False).count()

    mensaje = f"""
📊 <b>RESUMEN DIARIO - {ayer.strftime("%d/%m/%Y")}</b>

📈 <b>Actividad de ayer:</b>
• 🆕 Nuevas asociaciones: {nuevas_asociaciones}
• ✅ Asociaciones aprobadas: {asociaciones_aprobadas}
• 🐕 Nuevos animales: {nuevos_animales}

📊 <b>Totales actuales:</b>
• 🏢 Asociaciones activas: {total_asociaciones}
• 🐾 Animales disponibles: {total_animales}

🌟 ¡Siguiendo adelante con la misión de ayudar a los animales!
    """

    return enviar_mensaje_telegram(mensaje)

# ==================== FUNCIONES DE REGISTRO DE ASOCIACIÓN ====================

def iniciar_registro_asociacion(chat_id):
    """Inicia el proceso de registro de una nueva asociación"""
    mensaje = """
🏢 REGISTRO DE NUEVA ASOCIACIÓN

Voy a pedirte los siguientes datos paso a paso:

1️⃣ Nombre de la asociación
2️⃣ Email de contacto
3️⃣ Teléfono
4️⃣ Dirección completa
5️⃣ Población
6️⃣ Provincia
7️⃣ Código postal
8️⃣ Contraseña (para acceso al sistema)

Para comenzar, por favor envíame el NOMBRE de la asociación:
    """

    # Guardar estado inicial
    guardar_estado_conversacion(chat_id, 'esperando_nombre', {})

    enviar_mensaje_telegram(mensaje)
    logger.info(f"Proceso de registro iniciado para chat {chat_id}")

def procesar_paso_registro(chat_id, texto):
    """Procesa cada paso del registro de asociación"""
    estado_actual = obtener_estado_conversacion(chat_id)

    if not estado_actual:
        enviar_mensaje_telegram("❌ No hay proceso de registro activo. Usa /registrar para comenzar.")
        return

    estado = estado_actual['estado']
    datos = estado_actual['datos']

    # PASO 1: Nombre
    if estado == 'esperando_nombre':
        from .models import RegistroAsociacion

        # Validar que el nombre no exista
        if RegistroAsociacion.objects.filter(nombre=texto).exists():
            enviar_mensaje_telegram(f"❌ Ya existe una asociación con el nombre '{texto}'. Por favor, elige otro nombre:")
            return

        datos['nombre'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_email', datos)
        enviar_mensaje_telegram(f"✅ Nombre: {texto}\n\nAhora envíame el EMAIL de contacto:")

    # PASO 2: Email
    elif estado == 'esperando_email':
        import re
        # Validar formato de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', texto):
            enviar_mensaje_telegram("❌ El formato del email no es válido. Por favor, envía un email correcto:")
            return

        datos['email'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_telefono', datos)
        enviar_mensaje_telegram(f"✅ Email: {texto}\n\nAhora envíame el TELÉFONO de contacto:")

    # PASO 3: Teléfono
    elif estado == 'esperando_telefono':
        # Validar que tenga solo números, espacios y símbolos telefónicos
        texto_limpio = texto.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')
        if not texto_limpio.isdigit() or len(texto_limpio) < 9:
            enviar_mensaje_telegram("❌ El teléfono debe contener al menos 9 dígitos. Por favor, envía un teléfono válido:")
            return

        datos['telefono'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_direccion', datos)
        enviar_mensaje_telegram(f"✅ Teléfono: {texto}\n\nAhora envíame la DIRECCIÓN completa:")

    # PASO 4: Dirección
    elif estado == 'esperando_direccion':
        if len(texto) < 5:
            enviar_mensaje_telegram("❌ La dirección es demasiado corta. Por favor, envía una dirección completa:")
            return

        datos['direccion'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_poblacion', datos)
        enviar_mensaje_telegram(f"✅ Dirección: {texto}\n\nAhora envíame la POBLACIÓN:")

    # PASO 5: Población
    elif estado == 'esperando_poblacion':
        if len(texto) < 2:
            enviar_mensaje_telegram("❌ La población es demasiado corta. Por favor, envía un nombre válido:")
            return

        datos['poblacion'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_provincia', datos)
        enviar_mensaje_telegram(f"✅ Población: {texto}\n\nAhora envíame la PROVINCIA:")

    # PASO 6: Provincia
    elif estado == 'esperando_provincia':
        if len(texto) < 2:
            enviar_mensaje_telegram("❌ La provincia es demasiado corta. Por favor, envía un nombre válido:")
            return

        datos['provincia'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_codigo_postal', datos)
        enviar_mensaje_telegram(f"✅ Provincia: {texto}\n\nAhora envíame el CÓDIGO POSTAL:")

    # PASO 7: Código postal
    elif estado == 'esperando_codigo_postal':
        if not texto.replace(' ', '').isalnum() or len(texto) < 4:
            enviar_mensaje_telegram("❌ El código postal no es válido. Por favor, envía un código postal correcto:")
            return

        datos['codigo_postal'] = texto
        guardar_estado_conversacion(chat_id, 'esperando_password', datos)
        enviar_mensaje_telegram(f"✅ Código postal: {texto}\n\nFinalmente, envíame la CONTRASEÑA para acceso al sistema (mínimo 6 caracteres):")

    # PASO 8: Password (último paso)
    elif estado == 'esperando_password':
        if len(texto) < 6:
            enviar_mensaje_telegram("❌ La contraseña debe tener al menos 6 caracteres. Por favor, envía una contraseña más segura:")
            return

        datos['password'] = texto

        # Crear la asociación
        crear_asociacion_desde_telegram(chat_id, datos)

def crear_asociacion_desde_telegram(chat_id, datos):
    """Crea la asociación con todos los datos recopilados"""
    try:
        from .models import RegistroAsociacion

        logger.info(f"Creando nueva asociación desde Telegram: {datos['nombre']}")

        # Crear la asociación con estado 'activa' (ya aprobada por el admin)
        asociacion = RegistroAsociacion.objects.create(
            nombre=datos['nombre'],
            email=datos['email'],
            telefono=datos['telefono'],
            direccion=datos['direccion'],
            poblacion=datos['poblacion'],
            provincia=datos['provincia'],
            codigo_postal=datos['codigo_postal'],
            password=make_password(datos['password']),  # Hashear la contraseña
            estado='activa',  # Directamente activa
            aprobada_por='Admin Telegram',
            fecha_aprobacion=timezone.now()
        )

        logger.info(f"Asociación {asociacion.nombre} creada exitosamente con ID: {asociacion.id}")

        # Limpiar estado de conversación
        limpiar_estado_conversacion(chat_id)

        # Mensaje de confirmación
        mensaje_confirmacion = f"""
✅ ASOCIACIÓN CREADA EXITOSAMENTE

📋 Datos registrados:
• Nombre: {asociacion.nombre}
• Email: {asociacion.email}
• Teléfono: {asociacion.telefono}
• Dirección: {asociacion.direccion}
• Población: {asociacion.poblacion}
• Provincia: {asociacion.provincia}
• Código postal: {asociacion.codigo_postal}

🎉 Estado: ACTIVA
📅 Fecha: {asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M")}
🔑 ID: {asociacion.id}

La asociación ya puede acceder al sistema con:
• Usuario: {asociacion.nombre}
• Contraseña: (la que configuraste)

🌐 URL de acceso: http://127.0.0.1:8000/login/
        """

        enviar_mensaje_telegram(mensaje_confirmacion)
        logger.info(f"Confirmación de creación enviada para {asociacion.nombre}")

    except Exception as e:
        logger.error(f"Error creando asociación desde Telegram: {e}", exc_info=True)
        limpiar_estado_conversacion(chat_id)
        enviar_mensaje_telegram(f"❌ Error al crear la asociación: {str(e)}\n\nPor favor, intenta de nuevo con /registrar")

# ==================== WEBHOOK Y MANEJO DE BOTONES ====================

def verify_telegram_webhook(request):
    """Verifica que el webhook provenga realmente de Telegram"""
    # Obtener el secret token configurado
    webhook_secret = os.environ.get('TELEGRAM_WEBHOOK_SECRET')
    if not webhook_secret:
        # Si no hay secret configurado, aceptar por compatibilidad
        return True

    # Verificar el header X-Telegram-Bot-Api-Secret-Token
    received_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    return received_token == webhook_secret

@csrf_exempt
def telegram_webhook(request):
    """Webhook completamente renovado para manejar correctamente las peticiones de Telegram"""

    # Logging detallado para debugging
    logger.info("=== WEBHOOK TELEGRAM RECIBIDO ===")
    logger.info(f"Método HTTP: {request.method}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Content-Length: {len(request.body) if request.body else 0}")
    logger.info(f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}")
    logger.info(f"Remote-Addr: {request.META.get('REMOTE_ADDR', 'Unknown')}")

    # Manejar peticiones GET (health check)
    if request.method == 'GET':
        logger.info("GET request recibida - webhook health check")
        return JsonResponse({
            'status': 'webhook_active',
            'method': 'GET',
            'message': 'Telegram webhook is running'
        })

    # Solo procesar peticiones POST
    if request.method != 'POST':
        logger.warning(f"Método no permitido: {request.method}")
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Verificar que hay contenido
        if not request.body:
            logger.error("Cuerpo de la petición vacío")
            return JsonResponse({'error': 'Empty request body'}, status=400)

        # Decodificar el JSON de forma segura
        try:
            # Asegurar decodificación UTF-8 correcta
            raw_body = request.body
            if isinstance(raw_body, bytes):
                body_str = raw_body.decode('utf-8', errors='replace')
            else:
                body_str = str(raw_body)

            data = json.loads(body_str)
            logger.info(f"JSON decodificado correctamente. Tipo de actualización: {list(data.keys())}")

        except UnicodeDecodeError as e:
            logger.error(f"Error de decodificación UTF-8: {e}")
            return JsonResponse({'error': 'UTF-8 decode error'}, status=400)
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {e}")
            logger.error(f"Contenido recibido (primeros 500 chars): {request.body[:500]}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Verificar que es una actualización válida de Telegram
        if not isinstance(data, dict):
            logger.error("Los datos no son un diccionario válido")
            return JsonResponse({'error': 'Invalid data format'}, status=400)

        # Manejar callback queries (botones presionados)
        if 'callback_query' in data:
            callback_query = data['callback_query']
            logger.info(f"Callback query detectado: {callback_query}")

            # Validar estructura del callback
            if not all(key in callback_query for key in ['id', 'data']):
                logger.error("Callback query inválido - faltan campos requeridos")
                return JsonResponse({'error': 'Invalid callback query'}, status=400)

            callback_data = callback_query['data']
            callback_id = callback_query['id']

            # Extraer información del mensaje
            message = callback_query.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            message_id = message.get('message_id')

            if not chat_id or not message_id:
                logger.error("Información de mensaje incompleta en callback")
                return JsonResponse({'error': 'Incomplete message info'}, status=400)

            logger.info(f"Procesando callback: {callback_data} | Chat: {chat_id} | Message: {message_id}")

            # Procesar diferentes tipos de callbacks
            try:
                if callback_data.startswith('aprobar_'):
                    logger.info("Procesando aprobación...")
                    return manejar_aprobacion(callback_data, chat_id, message_id, callback_id)

                elif callback_data.startswith('rechazar_'):
                    logger.info("Procesando rechazo...")
                    return manejar_rechazo(callback_data, chat_id, message_id, callback_id)

                elif callback_data.startswith('ver_'):
                    logger.info("Mostrando detalles...")
                    return manejar_ver_detalles(callback_data, chat_id, message_id, callback_id)

                elif callback_data.startswith('eliminar_'):
                    logger.info("Solicitando confirmación de eliminación...")
                    return manejar_eliminar_asociacion(callback_data, chat_id, message_id, callback_id)

                elif callback_data.startswith('confirmar_eliminar_'):
                    logger.info("Procesando eliminación confirmada...")
                    return manejar_confirmar_eliminar(callback_data, chat_id, message_id, callback_id)

                else:
                    logger.warning(f"Callback no reconocido: {callback_data}")
                    responder_callback(callback_id, "Acción no reconocida")
                    return JsonResponse({'status': 'unrecognized_callback', 'data': callback_data})

            except Exception as callback_error:
                logger.error(f"Error procesando callback: {callback_error}")
                responder_callback(callback_id, "Error interno del servidor")
                return JsonResponse({'error': 'Callback processing failed'}, status=500)

        # Manejar mensajes de texto normales (comandos y respuestas)
        elif 'message' in data:
            message = data['message']
            texto = message.get('text', '')
            chat_id = message.get('chat', {}).get('id')

            if not chat_id:
                logger.error("Chat ID no encontrado en el mensaje")
                return JsonResponse({'error': 'Invalid message format'}, status=400)

            logger.info(f"Mensaje de texto recibido de chat {chat_id}: {texto}")

            # Procesar comandos
            if texto.startswith('/'):
                comando = texto.split()[0].lower()

                if comando == '/registrar' or comando == '/nueva_asociacion':
                    logger.info(f"Comando de registro recibido desde chat {chat_id}")
                    iniciar_registro_asociacion(chat_id)
                    return JsonResponse({'status': 'registration_started'})

                elif comando == '/cancelar':
                    limpiar_estado_conversacion(chat_id)
                    enviar_mensaje_telegram("❌ Proceso cancelado.")
                    return JsonResponse({'status': 'cancelled'})

                elif comando == '/ayuda' or comando == '/help':
                    mensaje_ayuda = """
🤖 COMANDOS DISPONIBLES

📋 Gestión de Asociaciones:
• /registrar - Registrar nueva asociación
• /nueva_asociacion - Alias de /registrar
• /cancelar - Cancelar proceso actual

ℹ️ Información:
• /ayuda - Mostrar esta ayuda
• /help - Alias de /ayuda

💡 Nota: Los botones en los mensajes te permiten aprobar, rechazar o eliminar asociaciones de forma interactiva.
                    """
                    enviar_mensaje_telegram(mensaje_ayuda)
                    return JsonResponse({'status': 'help_sent'})

                else:
                    enviar_mensaje_telegram(f"❌ Comando no reconocido: {comando}\n\nUsa /ayuda para ver los comandos disponibles.")
                    return JsonResponse({'status': 'unknown_command'})

            # Si no es comando, verificar si hay un proceso de registro activo
            else:
                estado = obtener_estado_conversacion(chat_id)
                if estado:
                    # Procesar el texto como parte del registro
                    procesar_paso_registro(chat_id, texto)
                    return JsonResponse({'status': 'registration_step_processed'})
                else:
                    # Mensaje normal sin proceso activo
                    logger.info(f"Mensaje sin proceso activo: {texto}")
                    return JsonResponse({'status': 'message_received', 'action': 'no_action_needed'})

        # Otros tipos de actualizaciones
        else:
            logger.info(f"Actualización de Telegram no procesada: {list(data.keys())}")
            return JsonResponse({'status': 'update_not_processed', 'keys': list(data.keys())})

    except Exception as e:
        logger.error(f"Error general en webhook: {e}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'error': 'Internal server error',
            'message': str(e)[:100]  # Limitar mensaje de error
        }, status=500)

def manejar_aprobacion(callback_data, chat_id, message_id, callback_query_id):
    """Maneja la aprobación directa desde Telegram"""
    try:
        # Extraer ID de la asociación
        asociacion_id = callback_data.split('_')[1]
        logger.info(f"Iniciando aprobación para asociación ID: {asociacion_id}")

        # Importar aquí para evitar imports circulares
        from .models import RegistroAsociacion
        from .views import enviar_email_aprobacion

        asociacion = RegistroAsociacion.objects.get(id=asociacion_id)
        logger.info(f"Estado actual de la asociación {asociacion.nombre}: {asociacion.estado}")

        if asociacion.estado == 'activa':
            logger.warning("Asociación ya estaba aprobada")
            responder_callback(callback_query_id, "Ya estaba aprobada")
            return JsonResponse({'status': 'already_approved'})

        # Aprobar la asociación
        logger.info(f"Aprobando asociación ID: {asociacion_id}")
        asociacion.aprobar(admin_name="Admin Telegram", notas="Aprobada desde Telegram")
        logger.info(f"Asociación {asociacion.nombre} aprobada. Nuevo estado: {asociacion.estado}")

        # IMPORTANTE: Responder al callback PRIMERO para quitar el loading
        logger.info(f"Intentando responder callback con ID: {callback_query_id}")
        callback_result = responder_callback(callback_query_id)
        logger.info(f"Resultado de responder_callback: {callback_result}")

        # Enviar email a la asociación
        email_status = ""
        try:
            enviar_email_aprobacion(asociacion)
            email_status = "Email de confirmacion enviado"
            logger.info("Email de aprobación enviado exitosamente")
        except Exception as email_error:
            logger.error(f"Error enviando email de aprobación: {email_error}")
            email_status = "Error enviando email (aprobacion exitosa)"

        # NUEVO: Enviar un nuevo mensaje en lugar de editar el antiguo
        nuevo_mensaje = f"""ASOCIACION APROBADA

Asociacion: {asociacion.nombre}
Email: {asociacion.email}
Ubicacion: {asociacion.poblacion}, {asociacion.provincia}
Aprobada: {asociacion.fecha_aprobacion.strftime("%d/%m/%Y %H:%M")}

{email_status}"""

        send_result = enviar_mensaje_telegram(nuevo_mensaje)
        logger.info(f"Resultado de enviar nuevo mensaje: {send_result}")

        logger.info(f"Aprobación de {asociacion.nombre} completada exitosamente")
        return JsonResponse({'status': 'approved'})

    except ObjectDoesNotExist:
        logger.error(f"Asociación con ID {asociacion_id} no encontrada")
        responder_callback(callback_query_id, "Asociación no encontrada")
        return JsonResponse({'status': 'not_found', 'message': 'Asociación no encontrada'})
    except Exception as e:
        logger.error(f"Error en manejar_aprobacion: {e}", exc_info=True)
        responder_callback(callback_query_id, f"Error: {str(e)[:30]}")
        return JsonResponse({'status': 'error', 'message': str(e)})

def manejar_rechazo(callback_data, chat_id, message_id, callback_query_id):
    """Maneja el rechazo directo - elimina la asociación inmediatamente"""
    try:
        asociacion_id = callback_data.split('_')[1]
        logger.info(f"Iniciando rechazo directo para asociación ID: {asociacion_id}")

        from .models import RegistroAsociacion
        from .views import enviar_email_rechazo

        asociacion = RegistroAsociacion.objects.get(id=asociacion_id)

        # Verificar que esté pendiente
        if asociacion.estado != 'pendiente':
            logger.warning(f"Asociación {asociacion.nombre} no está pendiente (estado: {asociacion.estado})")
            responder_callback(callback_query_id, f"Asociación ya procesada: {asociacion.get_estado_display()}")
            return JsonResponse({'status': 'already_processed', 'current_state': asociacion.estado})

        # Guardar datos antes de eliminar
        nombre_asociacion = asociacion.nombre
        email_asociacion = asociacion.email
        poblacion = asociacion.poblacion
        provincia = asociacion.provincia

        logger.info(f"Rechazando y eliminando asociación: {nombre_asociacion}")

        # Enviar email de rechazo con motivo estándar
        email_status = "Email de rechazo enviado"
        try:
            enviar_email_rechazo(asociacion, "La asociación no cumple con los requisitos mínimos establecidos para el registro en la plataforma.")
            logger.info("Email de rechazo enviado exitosamente")
        except Exception as e:
            logger.error(f"Error enviando email de rechazo: {e}")
            email_status = "No se pudo enviar el email (asociación eliminada)"

        # ELIMINAR la asociación inmediatamente del sistema
        asociacion.delete()
        logger.info(f"Asociación {nombre_asociacion} eliminada permanentemente de la base de datos")

        # IMPORTANTE: Responder al callback PRIMERO para quitar el loading
        responder_callback(callback_query_id, "Asociacion rechazada y eliminada")

        # Actualizar el mensaje en Telegram
        nuevo_mensaje = f"""ASOCIACION RECHAZADA Y ELIMINADA

Asociacion: {nombre_asociacion}
Email: {email_asociacion}
Ubicacion: {poblacion}, {provincia}
Rechazada: {timezone.now().strftime("%d/%m/%Y %H:%M")}

ELIMINADA PERMANENTEMENTE del sistema
{email_status}

Motivo: No cumple con los requisitos minimos establecidos

Accion realizada por: Admin Telegram
Estado: Completada exitosamente"""

        editar_mensaje_telegram(chat_id, message_id, nuevo_mensaje)

        logger.info(f"Rechazo y eliminación de {nombre_asociacion} completada exitosamente")
        return JsonResponse({'status': 'rejected_and_deleted'})

    except ObjectDoesNotExist:
        logger.error(f"Asociación con ID {asociacion_id} no encontrada")
        responder_callback(callback_query_id, "Asociación no encontrada")
        return JsonResponse({'status': 'not_found', 'message': 'Asociación no encontrada'})
    except Exception as e:
        logger.error(f"Error en manejar_rechazo: {e}", exc_info=True)
        responder_callback(callback_query_id, f"Error interno: {str(e)[:30]}")
        return JsonResponse({'status': 'error', 'message': str(e)})


# Función manejar_confirmar_rechazo removida - ahora el rechazo es directo sin confirmación

def manejar_ver_detalles(callback_data, chat_id, message_id, callback_query_id):
    """Muestra los detalles completos de la asociación con enlace directo al panel admin"""
    try:
        asociacion_id = callback_data.split('_')[1]

        from .models import RegistroAsociacion
        import os
        from django.conf import settings

        asociacion = RegistroAsociacion.objects.get(id=asociacion_id)

        # Obtener la URL base del panel de administración de manera dinámica
        # Primero intentar obtener la URL de ngrok si está disponible
        try:
            import requests
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            if response.status_code == 200:
                tunnels = response.json().get('tunnels', [])
                if tunnels:
                    ngrok_url = tunnels[0]['public_url']
                    admin_url = f"{ngrok_url}/admin/panel/"
                    asociacion_detail_url = f"{ngrok_url}/admin/info/{asociacion.token_aprobacion}/"
                    logger.info(f"Usando URL de ngrok para enlaces: {ngrok_url}")
                else:
                    raise Exception("No hay túneles activos")
        except:
            # Si no hay ngrok, usar configuración por defecto
            if hasattr(settings, 'RENDER_EXTERNAL_HOSTNAME') and settings.RENDER_EXTERNAL_HOSTNAME:
                # En producción (Render)
                admin_url = f"https://{settings.RENDER_EXTERNAL_HOSTNAME}/admin/panel/"
                asociacion_detail_url = f"https://{settings.RENDER_EXTERNAL_HOSTNAME}/admin/info/{asociacion.token_aprobacion}/"
            else:
                # En desarrollo local
                admin_url = "http://127.0.0.1:8000/admin/panel/"
                asociacion_detail_url = f"http://127.0.0.1:8000/admin/info/{asociacion.token_aprobacion}/"

        # IMPORTANTE: Responder al callback PRIMERO para quitar el loading
        responder_callback(callback_query_id, "Detalles cargados")

        mensaje = f"""DETALLES DE LA ASOCIACION

Informacion Basica:
• Nombre: {asociacion.nombre}
• Email: {asociacion.email}
• Telefono: {asociacion.telefono}

Ubicacion:
• Direccion: {asociacion.direccion}
• Poblacion: {asociacion.poblacion}
• Provincia: {asociacion.provincia}
• Codigo Postal: {asociacion.codigo_postal}

Estado:
• Estado actual: {asociacion.get_estado_display()}
• Fecha registro: {asociacion.fecha_registro.strftime("%d/%m/%Y %H:%M")}
• ID: {asociacion.id}

Panel web: {admin_url}
Detalles: {asociacion_detail_url}
        """

        # Botones según el estado
        if asociacion.estado == 'pendiente':
            botones = [
                [
                    {
                        "text": "Aprobar",
                        "callback_data": f"aprobar_{asociacion.id}"
                    },
                    {
                        "text": "Rechazar",
                        "callback_data": f"rechazar_{asociacion.id}"
                    }
                ],
                [
                    {
                        "text": "Eliminar",
                        "callback_data": f"eliminar_{asociacion.id}"
                    }
                ],
                [
                    {
                        "text": "Ir al Panel Web",
                        "url": admin_url
                    }
                ]
            ]
        else:
            botones = [
                [
                    {
                        "text": f"Estado: {asociacion.get_estado_display()}",
                        "callback_data": f"estado_{asociacion.id}"
                    }
                ],
                [
                    {
                        "text": "Eliminar",
                        "callback_data": f"eliminar_{asociacion.id}"
                    }
                ],
                [
                    {
                        "text": "Ir al Panel Web",
                        "url": admin_url
                    }
                ]
            ]

        editar_mensaje_telegram(chat_id, message_id, mensaje, botones)

        return JsonResponse({'status': 'details_shown'})

    except ObjectDoesNotExist:
        logger.error(f"Asociación con ID {asociacion_id} no encontrada")
        responder_callback(callback_query_id, "Asociación no encontrada")
        return JsonResponse({'status': 'not_found', 'message': 'Asociación no encontrada'})
    except Exception as e:
        logger.error(f"Error en manejar_ver_detalles: {e}", exc_info=True)
        responder_callback(callback_query_id, f"Error: {str(e)[:30]}")
        return JsonResponse({'status': 'error', 'message': str(e)})

def manejar_eliminar_asociacion(callback_data, chat_id, message_id, callback_query_id):
    """Muestra confirmación antes de eliminar una asociación"""
    try:
        asociacion_id = callback_data.split('_')[1]
        logger.info(f"Solicitando confirmación para eliminar asociación ID: {asociacion_id}")

        from .models import RegistroAsociacion

        asociacion = RegistroAsociacion.objects.get(id=asociacion_id)

        # IMPORTANTE: Responder al callback PRIMERO para quitar el loading
        responder_callback(callback_query_id, "Confirma la eliminacion")

        # Contar animales asociados
        animales_count = asociacion.animales.count()

        # Mensaje de confirmación
        mensaje = f"""CONFIRMACION DE ELIMINACION

Estas a punto de eliminar la asociacion:

Nombre: {asociacion.nombre}
Email: {asociacion.email}
Ubicacion: {asociacion.poblacion}, {asociacion.provincia}
Estado: {asociacion.get_estado_display()}
Animales registrados: {animales_count}

ADVERTENCIA:
Esta accion es PERMANENTE e IRREVERSIBLE.
Se eliminara:
- La asociacion completa
- Todos sus animales ({animales_count})
- Todos los datos relacionados

Estas seguro de que deseas continuar?
        """

        # Botones de confirmación
        botones = [
            [
                {
                    "text": "SI, Eliminar Permanentemente",
                    "callback_data": f"confirmar_eliminar_{asociacion.id}"
                }
            ],
            [
                {
                    "text": "NO, Cancelar",
                    "callback_data": f"ver_{asociacion.id}"
                }
            ]
        ]

        editar_mensaje_telegram(chat_id, message_id, mensaje, botones)

        return JsonResponse({'status': 'delete_confirmation_shown'})

    except ObjectDoesNotExist:
        logger.error(f"Asociación con ID {asociacion_id} no encontrada")
        responder_callback(callback_query_id, "Asociación no encontrada")
        return JsonResponse({'status': 'not_found', 'message': 'Asociación no encontrada'})
    except Exception as e:
        logger.error(f"Error en manejar_eliminar_asociacion: {e}", exc_info=True)
        responder_callback(callback_query_id, f"Error: {str(e)[:30]}")
        return JsonResponse({'status': 'error', 'message': str(e)})

def manejar_confirmar_eliminar(callback_data, chat_id, message_id, callback_query_id):
    """Elimina permanentemente una asociación después de confirmación"""
    try:
        asociacion_id = callback_data.split('_')[2]  # confirmar_eliminar_ID
        logger.info(f"Eliminando permanentemente asociación ID: {asociacion_id}")

        from .models import RegistroAsociacion

        asociacion = RegistroAsociacion.objects.get(id=asociacion_id)

        # Guardar datos antes de eliminar
        nombre_asociacion = asociacion.nombre
        email_asociacion = asociacion.email
        poblacion = asociacion.poblacion
        provincia = asociacion.provincia
        animales_count = asociacion.animales.count()

        logger.info(f"Datos guardados. Procediendo a eliminar: {nombre_asociacion}")

        # ELIMINAR PERMANENTEMENTE
        asociacion.delete()
        logger.info(f"Asociación {nombre_asociacion} eliminada permanentemente de la base de datos")

        # IMPORTANTE: Responder al callback PRIMERO para quitar el loading
        responder_callback(callback_query_id, "Asociacion eliminada")

        # Actualizar el mensaje en Telegram
        nuevo_mensaje = f"""ASOCIACION ELIMINADA PERMANENTEMENTE

Asociacion eliminada:
- Nombre: {nombre_asociacion}
- Email: {email_asociacion}
- Ubicacion: {poblacion}, {provincia}

Datos eliminados:
- Asociacion completa
- {animales_count} animales registrados
- Todos los datos relacionados

Fecha de eliminacion: {timezone.now().strftime("%d/%m/%Y %H:%M")}
Eliminada por: Admin Telegram

Operacion completada exitosamente
        """

        editar_mensaje_telegram(chat_id, message_id, nuevo_mensaje)

        logger.info(f"Eliminación de {nombre_asociacion} completada exitosamente")
        return JsonResponse({'status': 'deleted_successfully'})

    except ObjectDoesNotExist:
        logger.error(f"Asociación con ID {asociacion_id} no encontrada")
        responder_callback(callback_query_id, "Asociación no encontrada")
        return JsonResponse({'status': 'not_found', 'message': 'Asociación no encontrada'})
    except Exception as e:
        logger.error(f"Error en manejar_confirmar_eliminar: {e}", exc_info=True)
        responder_callback(callback_query_id, f"Error interno: {str(e)[:30]}")
        return JsonResponse({'status': 'error', 'message': str(e)})

# ==================== FUNCIONES DE PRUEBA ====================

def probar_telegram():
    """Función para probar la configuración de Telegram"""
    mensaje = "🧪 Prueba de configuración - ¡Telegram funcionando correctamente!"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje
    }

    try:
        response = requests.post(url, data=data)
        print(f"Respuesta: {response.status_code}")
        print(f"Contenido: {response.text}")

        if response.status_code == 200:
            print("✅ ¡Telegram configurado correctamente!")
            return True
        else:
            print("❌ Error en la configuración")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_botones_telegram():
    """Función para probar el sistema de botones de Telegram"""
    mensaje = """
🧪 <b>PRUEBA DEL SISTEMA DE BOTONES</b>

Esta es una prueba para verificar que los botones de Telegram funcionan correctamente.

📋 <b>Funciones disponibles:</b>
• ✅ Botón de Aprobación
• ❌ Botón de Rechazo
• 👁️ Botón de Más Detalles

🔧 <b>Estado:</b> Sistema de prueba activo
    """

    # Botones de prueba
    botones = [
        [
            {
                "text": "✅ Prueba Aprobar",
                "callback_data": "test_aprobar_123"
            },
            {
                "text": "❌ Prueba Rechazar",
                "callback_data": "test_rechazar_123"
            }
        ],
        [
            {
                "text": "👁️ Prueba Detalles",
                "callback_data": "test_ver_123"
            }
        ]
    ]

    try:
        resultado = enviar_mensaje_telegram(mensaje, botones)
        if resultado:
            print("✅ Mensaje de prueba con botones enviado exitosamente")
            print("💡 Presiona los botones en Telegram para probar el webhook")
            return True
        else:
            print("❌ Error enviando mensaje de prueba")
            return False
    except Exception as e:
        print(f"❌ Error en prueba de botones: {e}")
        return False

def verificar_webhook_url():
    """Verifica la configuración del webhook de Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            webhook_info = data.get('result', {})

            logger.info("Informacion del Webhook:")
            logger.info(f"   URL: {webhook_info.get('url', 'No configurada')}")
            logger.info(f"   Pendientes: {webhook_info.get('pending_update_count', 0)}")
            logger.info(f"   Ultima actualizacion: {webhook_info.get('last_error_date', 'Nunca')}")

            if webhook_info.get('url'):
                logger.info("Webhook configurado correctamente")
                return True
            else:
                logger.warning("Webhook no configurado")
                return False
        else:
            logger.error(f"Error obteniendo info del webhook: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Error verificando webhook: {e}")
        return False