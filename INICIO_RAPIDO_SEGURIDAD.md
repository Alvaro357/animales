# Inicio Rápido - Sistema de Seguridad Admin Login

## Como Usar el Nuevo Sistema

### Acceder al Panel de Administración

1. **Iniciar el servidor**:
   ```bash
   python manage.py runserver
   ```

2. **Navegar al login de admin**:
   ```
   http://localhost:8000/admin/login/
   ```

3. **Ingresar contraseña**:
   - Usar la contraseña configurada en `mysite/settings.py`
   - Variable: `ADMIN_PASSWORD`

---

## Comportamiento del Sistema

### Si ingresas la contraseña CORRECTA:
- Te redirige al panel de administración
- Limpia cualquier intento fallido previo
- Puedes trabajar normalmente

### Si ingresas la contraseña INCORRECTA:

#### 1er intento fallido:
```
Contraseña incorrecta
Te quedan 2 intentos antes de ser bloqueado.
```

#### 2do intento fallido:
```
Contraseña incorrecta
Advertencia: Te queda 1 intento. Después serás bloqueado por 15 minutos.
```

#### 3er intento fallido:
```
Has excedido el número máximo de intentos. Acceso bloqueado por 15 minutos.

[Contador visual mostrando tiempo restante]
[Formulario deshabilitado]
[Efecto de pulsación roja]
```

---

## Qué Hacer Si Quedas Bloqueado

### Opción 1: Esperar 15 minutos
- La página se recargará automáticamente cuando expire el tiempo
- No necesitas hacer nada, solo esperar

### Opción 2: Limpiar la sesión (para desarrollo)

#### Método A - Borrar cookies del navegador:
1. Abrir DevTools (F12)
2. Ir a Application → Cookies
3. Borrar la cookie `sessionid`
4. Recargar la página

#### Método B - Usar modo incógnito:
1. Abrir ventana de incógnito
2. Navegar a `/admin/login/`
3. Intentar nuevamente

#### Método C - Usar Django shell (para pruebas):
```bash
python manage.py shell
```

```python
from django.contrib.sessions.models import Session
Session.objects.all().delete()
exit()
```

### Opción 3: Cambiar la duración del bloqueo (solo para desarrollo)

1. Abrir `myapp/views.py`
2. Buscar línea 82:
   ```python
   BLOCK_DURATION_MINUTES = 15
   ```
3. Cambiar a 1 minuto para pruebas:
   ```python
   BLOCK_DURATION_MINUTES = 1
   ```
4. Guardar y reiniciar el servidor

---

## Configuración Personalizada

### Cambiar el número de intentos permitidos

**Ubicación**: `myapp/views.py`, línea 81

```python
MAX_ATTEMPTS = 3  # Cambiar este número
```

Ejemplos:
- `MAX_ATTEMPTS = 5` - Más permisivo (5 intentos)
- `MAX_ATTEMPTS = 2` - Más estricto (2 intentos)

### Cambiar la duración del bloqueo

**Ubicación**: `myapp/views.py`, línea 82

```python
BLOCK_DURATION_MINUTES = 15  # Cambiar este número
```

Ejemplos:
- `BLOCK_DURATION_MINUTES = 30` - Bloqueo más largo
- `BLOCK_DURATION_MINUTES = 5` - Bloqueo más corto
- `BLOCK_DURATION_MINUTES = 1` - Para pruebas rápidas

---

## Verificar que Funciona

### Test Rápido Manual:

1. **Ir al login**: `http://localhost:8000/admin/login/`

2. **Intentar 1 vez mal**:
   - Ingresar cualquier contraseña incorrecta
   - Deberías ver: "Te quedan 2 intentos"

3. **Intentar 2 veces mal**:
   - Ingresar otra contraseña incorrecta
   - Deberías ver: "Te queda 1 intento"

4. **Intentar 3 veces mal**:
   - Ingresar otra contraseña incorrecta
   - Deberías ver:
     * Mensaje de bloqueo
     * Contador "15 minutos"
     * Formulario deshabilitado
     * Efecto de pulsación roja

### Test Automatizado:

```bash
python manage.py test test_admin_login_security.AdminLoginSecurityTest -v 2
```

Deberías ver:
```
Ran 9 tests in 0.043s
OK
```

---

## Preguntas Frecuentes

### P: Olvidé la contraseña de admin, cómo la cambio?

**R**: Editar `mysite/settings.py`:
```python
ADMIN_PASSWORD = 'tu_nueva_contraseña'
```

### P: Puedo desactivar temporalmente la seguridad?

**R**: No recomendado, pero puedes aumentar los intentos:
```python
MAX_ATTEMPTS = 999  # Prácticamente infinito
```

### P: Cómo veo qué IPs están bloqueadas?

**R**: Usar Django shell:
```bash
python manage.py shell
```

```python
from django.contrib.sessions.models import Session
for s in Session.objects.all():
    data = s.get_decoded()
    if 'admin_login_attempts' in data:
        print(data['admin_login_attempts'])
```

### P: El bloqueo afecta a todos los usuarios?

**R**: No, solo afecta a la IP específica que falló los intentos.

### P: Funciona detrás de un proxy o VPN?

**R**: Sí, el sistema detecta la IP real usando `HTTP_X_FORWARDED_FOR`.

### P: Qué pasa si dos personas comparten la misma IP?

**R**: Ambas quedan bloqueadas si se exceden los intentos. Esto puede pasar en:
- Redes corporativas con NAT
- WiFi público
- IPs compartidas de ISP

**Solución**: Aumentar `MAX_ATTEMPTS` o implementar whitelist.

---

## Archivos de Referencia

- **Documentación completa**: `SECURITY_ADMIN_LOGIN.md`
- **Resumen de implementación**: `IMPLEMENTACION_SEGURIDAD_RESUMEN.md`
- **Tests automatizados**: `test_admin_login_security.py`
- **Código de vista**: `myapp/views.py` (líneas 67-182)
- **Template**: `myapp/templates/admin_login.html`

---

## Soporte

Si encuentras problemas:

1. Verificar que el servidor está corriendo
2. Verificar que `ADMIN_PASSWORD` está configurado en settings
3. Limpiar sesiones y cookies
4. Ejecutar tests: `python manage.py test test_admin_login_security`
5. Revisar logs en consola del servidor

---

**Última actualización**: 2025-11-18
**Versión**: 1.0
