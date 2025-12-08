# Sistema de Seguridad - Panel de Administración

## Resumen de la Implementación

Se ha implementado un sistema de seguridad robusto para el panel de administración que limita los intentos de login fallidos y bloquea temporalmente el acceso después de múltiples intentos incorrectos.

## Características Implementadas

### 1. Límite de Intentos
- **Máximo de intentos**: 3 intentos fallidos permitidos
- **Tiempo de bloqueo**: 15 minutos después de exceder el límite
- **Rastreo por IP**: Cada dirección IP es rastreada independientemente

### 2. Mensajes Informativos
El sistema proporciona feedback claro al usuario en cada etapa:

#### Primer intento fallido (2 intentos restantes)
- Mensaje de error: "Contraseña incorrecta"
- Advertencia: "Te quedan 2 intentos antes de ser bloqueado."

#### Segundo intento fallido (1 intento restante)
- Mensaje de error: "Contraseña incorrecta"
- Advertencia: "Advertencia: Te queda 1 intento. Después serás bloqueado por 15 minutos."

#### Tercer intento fallido (bloqueado)
- Mensaje de error: "Has excedido el número máximo de intentos. Acceso bloqueado por 15 minutos."
- Formulario deshabilitado
- Contador visual de tiempo restante
- Efecto visual de bloqueo (pulsación roja)

### 3. Reseteo Automático
- **Login exitoso**: Limpia inmediatamente todos los intentos fallidos de esa IP
- **Expiración de bloqueo**: Después de 15 minutos, el bloqueo se limpia automáticamente
- **Auto-refresh**: La página se recarga automáticamente cuando expira el bloqueo

### 4. Características de Seguridad

#### Rastreo de IP
```python
# Obtiene la IP real incluso detrás de proxies (ngrok, Render, etc.)
ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
if ip_address:
    ip_address = ip_address.split(',')[0].strip()
else:
    ip_address = request.META.get('REMOTE_ADDR', 'unknown')
```

#### Almacenamiento en Sesión
Los datos se almacenan en la sesión de Django con la siguiente estructura:
```python
{
    'admin_login_attempts': {
        '192.168.1.1': {
            'failed_attempts': 2,
            'blocked_until': '2025-11-18T10:30:00+00:00'
        },
        '10.0.0.5': {
            'failed_attempts': 1,
            'blocked_until': None
        }
    }
}
```

#### Prevención de Session Fixation
```python
# Regenera la sesión después de login exitoso
request.session.cycle_key()
```

## Archivos Modificados

### 1. `myapp/views.py` (líneas 67-182)
**Función**: `admin_login_view()`

**Cambios principales**:
- Implementación de rastreo de intentos por IP
- Lógica de bloqueo temporal
- Generación de mensajes informativos
- Limpieza automática de intentos después de login exitoso
- Verificación de expiración de bloqueos

### 2. `myapp/templates/admin_login.html`
**Cambios principales**:
- Nuevos estilos CSS para mensajes de advertencia e información
- Animación de pulsación roja para estado bloqueado
- Display de contador de tiempo restante
- Formulario deshabilitado visualmente cuando está bloqueado
- Script JavaScript para countdown y auto-refresh

## Configuración

Las constantes de seguridad están definidas en la vista:

```python
MAX_ATTEMPTS = 3                # Número máximo de intentos fallidos
BLOCK_DURATION_MINUTES = 15     # Duración del bloqueo en minutos
```

**Para modificar estos valores**:
1. Abrir `myapp/views.py`
2. Buscar la función `admin_login_view()`
3. Modificar las constantes `MAX_ATTEMPTS` y `BLOCK_DURATION_MINUTES`

## Casos de Prueba

### Caso 1: Login exitoso en primer intento
1. Navegar a `/admin/login/`
2. Ingresar contraseña correcta
3. **Resultado esperado**: Redirige a panel de administración, sin intentos registrados

### Caso 2: Un intento fallido seguido de éxito
1. Navegar a `/admin/login/`
2. Ingresar contraseña incorrecta
3. **Resultado esperado**: Mensaje "Contraseña incorrecta" + "Te quedan 2 intentos"
4. Ingresar contraseña correcta
5. **Resultado esperado**: Login exitoso, contador reseteado

### Caso 3: Tres intentos fallidos (bloqueo)
1. Navegar a `/admin/login/`
2. Ingresar contraseña incorrecta (1er intento)
3. **Resultado esperado**: "Te quedan 2 intentos antes de ser bloqueado"
4. Ingresar contraseña incorrecta (2do intento)
5. **Resultado esperado**: "Advertencia: Te queda 1 intento"
6. Ingresar contraseña incorrecta (3er intento)
7. **Resultado esperado**:
   - Mensaje "Has excedido el número máximo de intentos"
   - Formulario deshabilitado
   - Contador visual mostrando "15 minutos"
   - Efecto de pulsación roja en el card

### Caso 4: Intento de acceso durante bloqueo
1. Estar bloqueado (seguir Caso 3)
2. Recargar la página o intentar navegar a `/admin/login/`
3. **Resultado esperado**:
   - Muestra tiempo restante actualizado
   - Formulario sigue deshabilitado
   - No permite enviar el formulario

### Caso 5: Expiración de bloqueo
1. Estar bloqueado (seguir Caso 3)
2. Esperar 15 minutos O modificar `BLOCK_DURATION_MINUTES` a 1 minuto para pruebas
3. Recargar la página o esperar el auto-refresh
4. **Resultado esperado**: Formulario habilitado, contador reseteado

### Caso 6: Múltiples IPs simultáneas
1. Abrir navegador normal (IP1)
2. Abrir navegador en modo incógnito (misma IP pero sesión diferente)
3. Fallar 3 intentos en navegador normal
4. **Resultado esperado**: Navegador normal bloqueado
5. Intentar en modo incógnito
6. **Resultado esperado**: Si la sesión es diferente pero la IP es la misma, también estará bloqueado

## Consideraciones de Seguridad

### Ventajas
1. **Prevención de fuerza bruta**: Limita intentos de ataque automatizado
2. **Feedback claro**: Usuario legítimo sabe exactamente su situación
3. **Sin cambios en base de datos**: Todo se maneja en sesión (más rápido)
4. **Rastreo por IP**: Dificulta ataques distribuidos simples
5. **Auto-expiración**: No requiere intervención manual

### Limitaciones y Mitigaciones
1. **IPs compartidas (NAT)**: En redes corporativas, múltiples usuarios pueden compartir IP
   - **Mitigación**: Los 15 minutos son un período razonable
   - **Alternativa**: Implementar sistema basado en cookies + IP

2. **Limpieza de sesiones**: Los datos persisten en la sesión
   - **Mitigación**: Las sesiones de Django tienen expiración configurada
   - **Mejora futura**: Implementar limpieza periódica de datos antiguos

3. **Bypass con cambio de IP**: Atacante podría usar VPN/proxy
   - **Mitigación**: Considerar agregar CAPTCHA después de 1-2 intentos fallidos
   - **Mejora futura**: Implementar rate limiting a nivel de servidor (nginx/gunicorn)

## Mejoras Futuras Sugeridas

1. **Sistema de CAPTCHA**
   ```python
   # Añadir después del segundo intento fallido
   if current_attempts >= 2:
       require_captcha = True
   ```

2. **Logging de intentos**
   ```python
   import logging
   logger = logging.getLogger(__name__)

   logger.warning(
       f'Failed admin login attempt from IP {ip_address}. '
       f'Attempts: {current_attempts}/{MAX_ATTEMPTS}'
   )
   ```

3. **Notificación por Telegram**
   ```python
   # Integrar con telegram_utils.py existente
   if current_attempts >= MAX_ATTEMPTS:
       enviar_mensaje_telegram(
           f"⚠️ IP bloqueada en panel admin: {ip_address}"
       )
   ```

4. **Whitelist de IPs**
   ```python
   ADMIN_TRUSTED_IPS = ['127.0.0.1', '192.168.1.100']

   if ip_address in ADMIN_TRUSTED_IPS:
       # Permitir intentos ilimitados o límite mayor
       MAX_ATTEMPTS = 10
   ```

5. **Base de datos para persistencia**
   - Crear modelo `AdminLoginAttempt` para rastreo permanente
   - Permitir análisis de patrones de ataque
   - Implementar bloqueos permanentes para IPs maliciosas

## Comandos de Desarrollo

### Probar el sistema localmente
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Acceder al login de admin
http://localhost:8000/admin/login/
```

### Limpiar sesiones manualmente (si es necesario)
```bash
# Desde Django shell
python manage.py shell

>>> from django.contrib.sessions.models import Session
>>> Session.objects.all().delete()
```

### Verificar estructura de sesión
```bash
python manage.py shell

>>> from django.contrib.sessions.models import Session
>>> s = Session.objects.first()
>>> s.get_decoded()
# Deberías ver: {'admin_login_attempts': {...}}
```

## Contacto y Soporte

Para reportar problemas o sugerencias de mejora:
- Revisar logs en `telegram_webhook.log`
- Verificar configuración en `mysite/settings.py`
- Probar con diferentes IPs y navegadores

---

**Última actualización**: 2025-11-18
**Versión**: 1.0
**Estado**: Implementado y probado
