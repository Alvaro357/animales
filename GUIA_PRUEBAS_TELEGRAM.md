# GUIA RAPIDA: COMO PROBAR LOS BOTONES DE TELEGRAM

## Opcion 1: Prueba Automatizada (Recomendada)

### Ejecutar el test completo:

```bash
cd C:\Users\Alvaro\OneDrive\Escritorio\asociaciones-de-animales
python test_telegram_botones_completo.py
```

**Resultado esperado:**
- 6/6 tests pasados
- Mensajes enviados a Telegram
- Asociaciones de prueba creadas y procesadas
- Verificacion de todas las funciones

**Tiempo estimado:** 30-60 segundos

---

## Opcion 2: Prueba Manual en Telegram

### Paso 1: Preparar el entorno

```bash
# 1. Iniciar el servidor Django
python manage.py runserver

# 2. En otra terminal, iniciar ngrok
ngrok http 8000

# 3. Copiar la URL de ngrok (ejemplo: https://abc123.ngrok-free.app)
```

### Paso 2: Configurar el webhook

```bash
# Abrir Python y ejecutar:
python
>>> from myapp.telegram_utils import *
>>> import requests
>>>
>>> # Configurar webhook (reemplaza con tu URL de ngrok)
>>> url = "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/setWebhook"
>>> requests.post(url, data={"url": "https://TU-URL-NGROK.ngrok-free.app/telegram/webhook/"})
>>>
>>> # Verificar que funciono
>>> verificar_webhook_url()
```

### Paso 3: Crear una asociacion de prueba

**Opcion A: Desde la web**
1. Ve a: http://127.0.0.1:8000/registro/
2. Completa el formulario
3. Envia el registro
4. Automaticamente recibiras notificacion en Telegram

**Opcion B: Desde Python**
```bash
python
>>> import os, django
>>> os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
>>> django.setup()
>>>
>>> from myapp.models import RegistroAsociacion
>>> from myapp.telegram_utils import enviar_notificacion_nueva_asociacion
>>> from django.contrib.auth.hashers import make_password
>>>
>>> # Crear asociacion de prueba
>>> asociacion = RegistroAsociacion.objects.create(
...     nombre="Test Manual",
...     email="test@test.com",
...     telefono="666777888",
...     direccion="Calle Test 123",
...     poblacion="Madrid",
...     provincia="Madrid",
...     codigo_postal="28000",
...     password=make_password("test123"),
...     estado='pendiente'
... )
>>>
>>> # Enviar notificacion a Telegram
>>> enviar_notificacion_nueva_asociacion(asociacion, None)
```

### Paso 4: Probar botones en Telegram

1. **Abre Telegram** y busca el mensaje del bot
2. **Presiona cada boton** y verifica:

**Boton "Aprobar":**
- El mensaje debe actualizarse con confirmacion
- La asociacion debe cambiar a estado 'activa'
- Debe enviarse un email de aprobacion

**Boton "Rechazar":**
- El mensaje debe actualizarse
- La asociacion debe eliminarse de la base de datos
- Debe enviarse un email de rechazo

**Boton "Mas Detalles":**
- El mensaje debe mostrar toda la informacion
- Debe mostrar nuevos botones (Aprobar, Rechazar, Eliminar, Ir al Panel Web)

**Boton "Eliminar":**
- Debe mostrar mensaje de confirmacion con advertencia
- Debe mostrar botones "SI, Eliminar" y "NO, Cancelar"

**Boton "SI, Eliminar Permanentemente":**
- La asociacion y sus animales deben eliminarse
- El mensaje debe confirmar la eliminacion

### Paso 5: Verificar en la base de datos

```bash
python
>>> from myapp.models import RegistroAsociacion
>>>
>>> # Ver todas las asociaciones
>>> for a in RegistroAsociacion.objects.all():
...     print(f"{a.nombre} - {a.estado}")
>>>
>>> # Ver asociaciones activas
>>> RegistroAsociacion.objects.filter(estado='activa').count()
>>>
>>> # Ver asociaciones pendientes
>>> RegistroAsociacion.objects.filter(estado='pendiente').count()
```

---

## Opcion 3: Probar funciones especificas

### Probar solo la aprobacion:

```python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import RegistroAsociacion
from myapp.telegram_utils import manejar_aprobacion

# Buscar una asociacion pendiente
asociacion = RegistroAsociacion.objects.filter(estado='pendiente').first()

# Simular callback de aprobacion
callback_data = f"aprobar_{asociacion.id}"
chat_id = "6344843081"
message_id = "999999"
callback_query_id = "test_callback"

response = manejar_aprobacion(callback_data, chat_id, message_id, callback_query_id)

# Verificar resultado
asociacion.refresh_from_db()
print(f"Estado: {asociacion.estado}")  # Debe ser 'activa'
print(f"Aprobada por: {asociacion.aprobada_por}")  # Debe ser 'Admin Telegram'
```

### Probar solo el rechazo:

```python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import RegistroAsociacion
from myapp.telegram_utils import manejar_rechazo
from django.contrib.auth.hashers import make_password

# Crear asociacion de prueba
asociacion = RegistroAsociacion.objects.create(
    nombre="Test Rechazo",
    email="rechazo@test.com",
    telefono="666777888",
    direccion="Calle Test",
    poblacion="Madrid",
    provincia="Madrid",
    codigo_postal="28000",
    password=make_password("test123"),
    estado='pendiente'
)

asociacion_id = asociacion.id
print(f"Asociacion creada: ID={asociacion_id}")

# Simular callback de rechazo
callback_data = f"rechazar_{asociacion_id}"
response = manejar_rechazo(callback_data, "6344843081", "999999", "test_callback")

# Verificar que fue eliminada
existe = RegistroAsociacion.objects.filter(id=asociacion_id).exists()
print(f"Asociacion eliminada: {not existe}")  # Debe ser True (eliminada)
```

### Probar solo ver detalles:

```python
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import RegistroAsociacion
from myapp.telegram_utils import manejar_ver_detalles

# Buscar cualquier asociacion
asociacion = RegistroAsociacion.objects.first()

# Simular callback
callback_data = f"ver_{asociacion.id}"
response = manejar_ver_detalles(callback_data, "6344843081", "999999", "test_callback")

print(f"Response: {response.status_code}")  # Debe ser 200
```

---

## Opcion 4: Probar envio de mensajes

### Mensaje simple:

```python
from myapp.telegram_utils import enviar_mensaje_telegram

resultado = enviar_mensaje_telegram("Hola! Este es un mensaje de prueba")
print(f"Enviado: {resultado}")
```

### Mensaje con botones:

```python
from myapp.telegram_utils import enviar_mensaje_telegram

botones = [
    [
        {"text": "Boton 1", "callback_data": "test_1"},
        {"text": "Boton 2", "callback_data": "test_2"}
    ],
    [
        {"text": "Boton 3", "callback_data": "test_3"}
    ]
]

resultado = enviar_mensaje_telegram("Mensaje con botones de prueba", botones)
print(f"Enviado: {resultado}")
```

---

## Verificar Estado del Sistema

### Ver configuracion de Telegram:

```python
from myapp.telegram_utils import verificar_webhook_url

verificar_webhook_url()
```

### Ver estadisticas:

```python
from myapp.models import RegistroAsociacion, CreacionAnimales

print("=== ESTADISTICAS ===")
print(f"Total asociaciones: {RegistroAsociacion.objects.count()}")
print(f"Pendientes: {RegistroAsociacion.objects.filter(estado='pendiente').count()}")
print(f"Activas: {RegistroAsociacion.objects.filter(estado='activa').count()}")
print(f"Suspendidas: {RegistroAsociacion.objects.filter(estado='suspendida').count()}")
print(f"Total animales: {CreacionAnimales.objects.count()}")
```

---

## Comandos Utiles

### Ver logs del servidor Django:

```bash
# En Windows
Get-Content telegram_webhook.log -Tail 50

# En Linux/Mac
tail -f telegram_webhook.log
```

### Ver webhook info desde Telegram:

```bash
curl "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/getWebhookInfo"
```

### Eliminar webhook (para pruebas locales):

```bash
curl -X POST "https://api.telegram.org/bot8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU/deleteWebhook"
```

---

## Solucionar Problemas Comunes

### Problema: "Webhook no recibe callbacks"

**Solucion:**
1. Verificar que ngrok este corriendo
2. Verificar que el webhook este configurado con la URL correcta
3. Verificar que Django este corriendo
4. Ver logs de Django para errores

### Problema: "Los botones no hacen nada"

**Solucion:**
1. Verificar que el webhook este configurado
2. Ver logs de Django (debe aparecer "Callback query detectado")
3. Verificar que el callback_data tenga el formato correcto

### Problema: "Error 400 Bad Request"

**Solucion:**
- En pruebas: Es normal (message_id simulados)
- En produccion: Verificar que los IDs de mensaje sean validos

### Problema: "Asociacion no se aprueba"

**Solucion:**
1. Verificar que el estado sea 'pendiente'
2. Ver logs para errores
3. Verificar que la asociacion exista en la BD

---

## Checklist de Verificacion

- [ ] Servidor Django corriendo
- [ ] Ngrok configurado (solo si pruebas manuales)
- [ ] Webhook configurado en Telegram
- [ ] Bot de Telegram activo
- [ ] Base de datos accesible
- [ ] Variables de entorno configuradas
- [ ] Logs visibles para debugging

---

## Resultado Esperado

Si todo funciona correctamente, deberas ver:

1. **En Telegram:**
   - Mensajes con botones bien formateados
   - Botones que responden al presionarlos
   - Mensajes que se actualizan despues de acciones
   - Feedback visual (spinner desaparece)

2. **En la base de datos:**
   - Estados que cambian correctamente
   - Fechas que se registran
   - Eliminaciones que ocurren

3. **En el email:**
   - Emails de aprobacion enviados
   - Emails de rechazo enviados
   - Contenido correcto

4. **En los logs:**
   - Sin errores criticos
   - Operaciones registradas
   - Callbacks procesados

---

**NOTA IMPORTANTE:**

Los errores de "editMessage" y "answerCallbackQuery" en pruebas automatizadas son **NORMALES** porque estamos usando IDs de mensaje simulados. En uso real con Telegram, estos errores NO ocurriran.

---

**FIN DE LA GUIA**
