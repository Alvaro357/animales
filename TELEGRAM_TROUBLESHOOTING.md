# Telegram Bot Troubleshooting Guide
## Sistema de Adopción de Animales - Documentación de Problemas de Botones

### 📋 RESUMEN DEL PROBLEMA

Los botones de Telegram (Aprobar, Rechazar, Más detalles) se envían correctamente pero **no responden** cuando se presionan. Django muestra "Bad Request (400)" cuando se accede a la URL de ngrok.

**Configuración actual:**
- Webhook URL: `https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/`
- Entorno: Desarrollo local con ngrok
- Framework: Django 5.1.7
- Bot Token: Configurado (8107454170:...)
- Chat ID: Configurado (6344843081)

---

## 🔍 ANÁLISIS DEL CÓDIGO ACTUAL

### Archivos Involucrados
- `myapp/telegram_utils.py` - Lógica del bot y webhook
- `mysite/settings.py` - Configuración de Django
- `myapp/urls.py` - Routing del webhook
- `myapp/middleware.py` - Middleware para ngrok

### Estado del Webhook
✅ La URL del webhook responde con GET: `{"status": "webhook_active", "method": "GET"}`
❌ Los callbacks de botones no se procesan correctamente

---

## 🚨 POSIBLES CAUSAS DEL PROBLEMA

### 1. **CONFIGURACIÓN DEL WEBHOOK DE TELEGRAM**

#### 1.1 Webhook no registrado en Telegram
**Problema:** El webhook puede no estar registrado correctamente en los servidores de Telegram.

**Diagnóstico:**
```bash
# Verificar configuración actual
curl -X GET "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/getWebhookInfo"
```

**Solución:**
```bash
# Eliminar webhook anterior
curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/deleteWebhook"

# Registrar nuevo webhook
curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/setWebhook" \
  -d "url=https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/"
```

#### 1.2 Webhook con URL diferente
**Problema:** Telegram está enviando callbacks a una URL diferente a la configurada.

**Verificación:**
- Comprobar si hay múltiples webhooks configurados
- Verificar que la URL en Telegram coincide exactamente con ngrok

#### 1.3 Límite de actualizaciones pendientes
**Problema:** Telegram tiene un límite de 100 actualizaciones pendientes.

**Solución:**
```bash
# Limpiar actualizaciones pendientes
curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/setWebhook" \
  -d "url=https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/" \
  -d "drop_pending_updates=true"
```

### 2. **PROBLEMAS DE NGROK**

#### 2.1 Headers de ngrok faltantes
**Problema:** ngrok requiere headers específicos para funcionar correctamente.

**Actual en middleware.py:**
```python
if request.path == '/telegram/webhook/':
    request.META['HTTP_ACCEPT'] = '*/*'
```

**Solución mejorada:**
```python
def process_request(self, request):
    if request.path == '/telegram/webhook/':
        # Headers requeridos por ngrok
        request.META['HTTP_ACCEPT'] = '*/*'
        request.META['HTTP_USER_AGENT'] = 'TelegramBot'
        # Evitar el warning de ngrok
        request.META['HTTP_NGROK_SKIP_BROWSER_WARNING'] = 'true'
    return None
```

#### 2.2 Página de advertencia de ngrok
**Problema:** ngrok puede mostrar una página de advertencia que interfiere con el webhook.

**Solución:**
- Agregar header `ngrok-skip-browser-warning: true`
- Usar dominios personalizados de ngrok
- Configurar ngrok para omitir warnings

#### 2.3 Límites de ngrok gratuito
**Problema:** La versión gratuita de ngrok tiene limitaciones.

**Limitaciones:**
- 120 conexiones por minuto
- URLs que cambian al reiniciar
- Posibles interrupciones de servicio

### 3. **CONFIGURACIÓN DE DJANGO**

#### 3.1 Problemas de CSRF
**Problema:** Django rechaza las peticiones POST sin token CSRF válido.

**Estado actual:**
```python
@csrf_exempt  # ✅ Está aplicado correctamente
def telegram_webhook(request):
```

#### 3.2 Configuración de ALLOWED_HOSTS
**Estado actual:** ✅ Configurado correctamente
```python
ALLOWED_HOSTS = [
    'f6f52d6fb2cd.ngrok-free.app',  # ✅
    '*.ngrok-free.app',             # ✅
    '*',                            # ✅ Temporalmente para debugging
]
```

#### 3.3 Configuración de CSRF_TRUSTED_ORIGINS
**Estado actual:** ✅ Configurado correctamente
```python
CSRF_TRUSTED_ORIGINS = [
    'https://f6f52d6fb2cd.ngrok-free.app',  # ✅
    'https://*.ngrok-free.app',             # ✅
]
```

#### 3.4 Middlewares conflictivos
**Posible problema:** El orden de middlewares puede estar causando conflictos.

**Orden actual:**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'myapp.middleware.NgrokMiddleware',      # ✅ Antes de CSRF
    'django.middleware.csrf.CsrfViewMiddleware',
    # ... resto de middlewares
]
```

### 4. **PROBLEMAS EN EL CÓDIGO DEL WEBHOOK**

#### 4.1 Manejo de JSON malformado
**Problema:** Si Telegram envía JSON malformado, el webhook falla.

**Código actual:**
```python
try:
    data = json.loads(request.body)
except:
    print("Error parseando JSON del webhook")  # ❌ No retorna respuesta
```

**Solución:**
```python
try:
    data = json.loads(request.body)
except json.JSONDecodeError as e:
    print(f"Error parseando JSON: {e}")
    return JsonResponse({'status': 'invalid_json'}, status=400)
```

#### 4.2 Verificación de seguridad deshabilitada
**Problema actual:**
```python
# SECURITY: Verificar que el webhook es válido (temporalmente deshabilitado para ngrok)
# if not verify_telegram_webhook(request):
```

**Riesgo:** Cualquier puede enviar peticiones al webhook.

#### 4.3 Errores de encoding en Windows
**Problema detectado:** UnicodeEncodeError al usar emojis en print statements.

**Solución:**
```python
# Reemplazar todos los prints con emojis
print("📡 Información del Webhook:")  # ❌ Falla en Windows
print("Información del Webhook:")     # ✅ Funciona
```

#### 4.4 Importes circulares
**Problema potencial:**
```python
from .models import RegistroAsociacion  # Dentro de funciones
from .views import enviar_email_aprobacion
```

### 5. **PROBLEMAS DE CONECTIVIDAD**

#### 5.1 Timeout de conexiones
**Problema:** Django puede tardar demasiado en responder, causando timeout en Telegram.

**Telegram timeout:** 60 segundos máximo

**Solución:**
- Optimizar consultas a la base de datos
- Usar procesamiento asíncrono para operaciones pesadas
- Responder rápidamente al callback y procesar después

#### 5.2 SSL/TLS Issues
**Problema:** Problemas con certificados SSL de ngrok.

**Verificación:**
```bash
curl -v https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/
```

#### 5.3 Firewall o proxy corporativo
**Problema:** Restricciones de red que bloquean webhooks de Telegram.

### 6. **PROBLEMAS DE ESTRUCTURA DE DATOS**

#### 6.1 Formato de callback_data incorrecto
**Formato actual:** `aprobar_123`, `rechazar_123`, `ver_123`

**Verificar que:**
- Los IDs de asociación son válidos
- No hay caracteres especiales
- La longitud no excede 64 bytes

#### 6.2 Respuesta de callback faltante
**Problema:** No se llama `answerCallbackQuery` causando que el botón mantenga el spinner.

**Código actual:** ✅ Implementado correctamente
```python
def responder_callback(callback_query_id, texto="Procesado"):
    # ... implementación correcta
```

---

## 🔧 SOLUCIONES PASO A PASO

### SOLUCIÓN 1: VERIFICAR Y RECONFIGURAR WEBHOOK

```bash
# 1. Verificar estado actual
curl -X GET "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/getWebhookInfo"

# 2. Eliminar webhook actual
curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/deleteWebhook"

# 3. Esperar 5 segundos
sleep 5

# 4. Configurar nuevo webhook
curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/setWebhook" \
  -d "url=https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/" \
  -d "drop_pending_updates=true"

# 5. Verificar configuración
curl -X GET "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/getWebhookInfo"
```

### SOLUCIÓN 2: MEJORAR MIDDLEWARE DE NGROK

**Archivo:** `myapp/middleware.py`
```python
class NgrokMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'ngrok' in request.META.get('HTTP_HOST', ''):
            request.META['HTTP_X_FORWARDED_HOST'] = request.META.get('HTTP_HOST')
            request.META['HTTP_X_FORWARDED_PROTO'] = 'https'

        # Para webhooks de Telegram - Mejorado
        if request.path == '/telegram/webhook/':
            request.META['HTTP_ACCEPT'] = '*/*'
            request.META['HTTP_USER_AGENT'] = 'TelegramBot'
            request.META['HTTP_NGROK_SKIP_BROWSER_WARNING'] = 'true'
            request.META['HTTP_CONTENT_TYPE'] = 'application/json'

        return None
```

### SOLUCIÓN 3: MEJORAR MANEJO DE ERRORES EN WEBHOOK

**Archivo:** `myapp/telegram_utils.py`
```python
@csrf_exempt
def telegram_webhook(request):
    try:
        print("=== WEBHOOK RECIBIDO ===")
        print(f"Método: {request.method}")
        print(f"Path: {request.path}")
        print(f"Content-Type: {request.content_type}")

        if request.method == 'GET':
            return JsonResponse({'status': 'webhook_active', 'method': 'GET'})

        if request.method != 'POST':
            return JsonResponse({'status': 'method_not_allowed'}, status=405)

        # Validar Content-Type
        if not request.content_type.startswith('application/json'):
            print(f"Content-Type incorrecto: {request.content_type}")
            return JsonResponse({'status': 'invalid_content_type'}, status=400)

        # Parse JSON con mejor manejo de errores
        try:
            if not request.body:
                print("Body vacío recibido")
                return JsonResponse({'status': 'empty_body'}, status=400)

            data = json.loads(request.body.decode('utf-8'))
            print(f"Datos recibidos: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            return JsonResponse({'status': 'invalid_json', 'error': str(e)}, status=400)
        except UnicodeDecodeError as e:
            print(f"Error de encoding: {e}")
            return JsonResponse({'status': 'encoding_error', 'error': str(e)}, status=400)

        # Verificar si es un callback de botón
        if 'callback_query' not in data:
            print("No es un callback_query, ignorando")
            return JsonResponse({'status': 'not_callback_query'})

        callback_query = data['callback_query']

        # Validar estructura del callback
        required_fields = ['data', 'message', 'id']
        for field in required_fields:
            if field not in callback_query:
                print(f"Campo requerido faltante: {field}")
                return JsonResponse({'status': 'invalid_callback_structure'}, status=400)

        callback_data = callback_query['data']
        chat_id = callback_query['message']['chat']['id']
        message_id = callback_query['message']['message_id']

        print(f"Callback recibido: {callback_data}")
        print(f"Chat ID: {chat_id}, Message ID: {message_id}")

        # Procesar diferentes acciones con timeout
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Procesamiento excedió 50 segundos")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(50)  # 50 segundos de timeout

        try:
            if callback_data.startswith('aprobar_'):
                return manejar_aprobacion(callback_data, chat_id, message_id, callback_query['id'])
            elif callback_data.startswith('rechazar_'):
                return manejar_rechazo(callback_data, chat_id, message_id, callback_query['id'])
            elif callback_data.startswith('ver_'):
                return manejar_ver_detalles(callback_data, chat_id, message_id, callback_query['id'])
            elif callback_data.startswith('confirmar_rechazo_'):
                return manejar_confirmar_rechazo(callback_data, chat_id, message_id, callback_query['id'])
            else:
                print(f"Callback no reconocido: {callback_data}")
                responder_callback(callback_query['id'], "Acción no reconocida")
                return JsonResponse({'status': 'unknown_callback'})
        finally:
            signal.alarm(0)  # Cancelar timeout

    except TimeoutError:
        print("Timeout procesando webhook")
        return JsonResponse({'status': 'timeout'}, status=408)
    except Exception as e:
        print(f"Error en webhook: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
```

### SOLUCIÓN 4: COMANDO DE DIAGNÓSTICO

**Crear:** `myapp/management/commands/test_telegram.py`
```python
from django.core.management.base import BaseCommand
from myapp.telegram_utils import *
import requests
import json

class Command(BaseCommand):
    help = 'Diagnóstica problemas con Telegram'

    def handle(self, *args, **options):
        self.stdout.write("=== DIAGNÓSTICO DE TELEGRAM ===")

        # 1. Verificar conexión básica
        self.stdout.write("1. Verificando conexión básica...")
        if probar_telegram():
            self.stdout.write(self.style.SUCCESS("✅ Conexión básica OK"))
        else:
            self.stdout.write(self.style.ERROR("❌ Error en conexión básica"))

        # 2. Verificar webhook
        self.stdout.write("2. Verificando webhook...")
        webhook_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        try:
            response = requests.get(webhook_url)
            webhook_info = response.json()
            self.stdout.write(f"URL configurada: {webhook_info['result'].get('url', 'Ninguna')}")
            self.stdout.write(f"Actualizaciones pendientes: {webhook_info['result'].get('pending_update_count', 0)}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error obteniendo info: {e}"))

        # 3. Probar webhook local
        self.stdout.write("3. Probando webhook local...")
        test_url = "http://127.0.0.1:8000/telegram/webhook/"
        try:
            response = requests.get(test_url)
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ Webhook local responde"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Webhook local error: {response.status_code}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error conectando a webhook local: {e}"))

        # 4. Enviar botones de prueba
        self.stdout.write("4. Enviando botones de prueba...")
        if probar_botones_telegram():
            self.stdout.write(self.style.SUCCESS("✅ Botones enviados - Pruébalos en Telegram"))
        else:
            self.stdout.write(self.style.ERROR("❌ Error enviando botones"))
```

---

## 🐛 COMANDOS DE DEBUGGING

### Verificar logs de Django
```bash
# Ejecutar servidor con logs detallados
python manage.py runserver --verbosity=2

# Ver logs en tiempo real
tail -f debug.log
```

### Verificar webhook de Telegram
```bash
# Información del webhook
curl -X GET "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/getWebhookInfo"

# Actualizaciones pendientes
curl -X GET "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/getUpdates"
```

### Probar webhook manualmente
```bash
# Simular callback de Telegram
curl -X POST "https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/" \
  -H "Content-Type: application/json" \
  -H "ngrok-skip-browser-warning: true" \
  -d '{
    "callback_query": {
      "id": "test123",
      "data": "test_aprobar_123",
      "message": {
        "chat": {"id": 6344843081},
        "message_id": 123
      }
    }
  }'
```

### Verificar conectividad de ngrok
```bash
# Verificar que ngrok funciona
curl -H "ngrok-skip-browser-warning: true" https://f6f52d6fb2cd.ngrok-free.app/

# Verificar headers
curl -v https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Configuración Básica
- [ ] Token de bot válido y configurado
- [ ] Chat ID correcto
- [ ] ngrok ejecutándose en puerto 8000
- [ ] Django server ejecutándose
- [ ] URL de webhook configurada en Telegram

### Configuración de Django
- [ ] ALLOWED_HOSTS incluye dominio ngrok
- [ ] CSRF_TRUSTED_ORIGINS configurado
- [ ] @csrf_exempt en webhook function
- [ ] Middleware de ngrok activo
- [ ] URL pattern para webhook configurada

### Configuración de Telegram
- [ ] Webhook registrado con setWebhook
- [ ] No hay actualizaciones pendientes (< 100)
- [ ] Webhook responde con 200 OK
- [ ] getWebhookInfo muestra URL correcta

### Debugging
- [ ] Logs de Django activos
- [ ] Print statements en webhook function
- [ ] Respuesta a callback_query implementada
- [ ] Manejo de errores implementado

---

## 🚀 PASOS INMEDIATOS RECOMENDADOS

### PRIORIDAD ALTA
1. **Reconfigurar webhook completamente**
   ```bash
   curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/deleteWebhook"
   sleep 5
   curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/setWebhook" \
     -d "url=https://f6f52d6fb2cd.ngrok-free.app/telegram/webhook/" \
     -d "drop_pending_updates=true"
   ```

2. **Mejorar manejo de errores en webhook**
   - Implementar mejor parsing de JSON
   - Agregar logs más detallados
   - Verificar Content-Type de requests

3. **Crear comando de diagnóstico**
   - Comando Django para probar Telegram
   - Verificación automática de configuración

### PRIORIDAD MEDIA
1. **Optimizar middleware de ngrok**
   - Agregar más headers específicos
   - Mejor detección de requests de Telegram

2. **Implementar sistema de logs**
   - Logs estructurados para debugging
   - Archivo de log específico para Telegram

### PRIORIDAD BAJA
1. **Migrar a solución de producción**
   - Usar servicio de hosting real
   - Configurar dominio personalizado
   - Implementar certificado SSL propio

---

## 📞 CONTACTO Y SOPORTE

Para problemas adicionales:

1. **Logs de Django:** Revisar archivo de logs o consola
2. **Telegram API:** Documentación oficial en https://core.telegram.org/bots/api
3. **ngrok Issues:** Verificar status en https://status.ngrok.com/

---

## 📋 NOTAS TÉCNICAS ADICIONALES

### Limitaciones Conocidas
- **ngrok gratuito:** 120 conexiones/minuto
- **Telegram callbacks:** Timeout de 60 segundos
- **Django DEBUG=True:** Configuración de desarrollo activa

### Mejoras Futuras
1. Implementar queue system para procesamiento async
2. Agregar métricas y monitoring
3. Implementar rate limiting
4. Configurar SSL certificates propios
5. Migrar a webhook con autenticación mejorada

---

*Documento generado: 24/09/2025*
*Última actualización: Análisis completo del código actual*