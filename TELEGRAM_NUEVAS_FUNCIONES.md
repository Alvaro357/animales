# Nuevas Funcionalidades de Telegram

Este documento describe las dos nuevas funcionalidades implementadas en el sistema de Telegram para la gestión de asociaciones.

## Tabla de Contenidos

1. [Registro de Asociaciones desde Telegram](#1-registro-de-asociaciones-desde-telegram)
2. [Eliminación de Asociaciones](#2-eliminación-de-asociaciones)
3. [Comandos Disponibles](#comandos-disponibles)
4. [Detalles Técnicos](#detalles-técnicos)
5. [Pruebas](#pruebas)

---

## 1. Registro de Asociaciones desde Telegram

### Descripción
Permite al administrador registrar una nueva asociación directamente desde Telegram mediante un flujo conversacional paso a paso.

### Cómo usar

1. **Iniciar el proceso:**
   ```
   /registrar
   ```
   o
   ```
   /nueva_asociacion
   ```

2. **Seguir las instrucciones:**
   El bot te pedirá cada dato en orden:

   - **Paso 1:** Nombre de la asociación
     - Valida que no exista ya en el sistema

   - **Paso 2:** Email de contacto
     - Valida formato de email (ejemplo@dominio.com)

   - **Paso 3:** Teléfono
     - Mínimo 9 dígitos
     - Permite espacios, guiones, paréntesis y símbolo +

   - **Paso 4:** Dirección completa
     - Mínimo 5 caracteres

   - **Paso 5:** Población
     - Mínimo 2 caracteres

   - **Paso 6:** Provincia
     - Mínimo 2 caracteres

   - **Paso 7:** Código postal
     - Mínimo 4 caracteres alfanuméricos

   - **Paso 8:** Contraseña
     - Mínimo 6 caracteres
     - Se hasheará automáticamente con Django

3. **Confirmación:**
   Al completar todos los pasos, recibirás un mensaje de confirmación con:
   - Todos los datos registrados
   - ID de la asociación
   - Estado (ACTIVA)
   - Instrucciones de acceso

### Características

- **Validación en tiempo real:** Cada dato se valida antes de continuar
- **Estado activo:** La asociación se crea directamente activa (sin necesidad de aprobación)
- **Seguridad:** La contraseña se hashea usando `make_password()` de Django
- **Cancelación:** Puedes cancelar en cualquier momento con `/cancelar`
- **Unicidad:** Verifica que el nombre de asociación no exista

### Ejemplo de uso

```
Admin: /registrar

Bot: 🏢 REGISTRO DE NUEVA ASOCIACIÓN
     Voy a pedirte los siguientes datos paso a paso...
     Para comenzar, por favor envíame el NOMBRE de la asociación:

Admin: Protectora Animales Madrid

Bot: ✅ Nombre: Protectora Animales Madrid
     Ahora envíame el EMAIL de contacto:

Admin: contacto@protectora-madrid.org

Bot: ✅ Email: contacto@protectora-madrid.org
     Ahora envíame el TELÉFONO de contacto:

[... continúa el proceso ...]

Bot: ✅ ASOCIACIÓN CREADA EXITOSAMENTE
     📋 Datos registrados:
     • Nombre: Protectora Animales Madrid
     • Email: contacto@protectora-madrid.org
     [...]
     🎉 Estado: ACTIVA
```

---

## 2. Eliminación de Asociaciones

### Descripción
Permite eliminar permanentemente una asociación existente desde Telegram con un sistema de doble confirmación.

### Cómo usar

1. **Acceder a los detalles:**
   - Presiona el botón "👁️ Más Detalles" en cualquier notificación de asociación
   - O usa el botón "👁️ Más Detalles" en el mensaje de registro

2. **Iniciar eliminación:**
   - Presiona el botón "🗑️ Eliminar"

3. **Leer la advertencia:**
   El bot mostrará:
   - Datos completos de la asociación
   - Número de animales que serán eliminados
   - Advertencia de que la acción es IRREVERSIBLE

4. **Confirmar o cancelar:**
   - **✅ SÍ, Eliminar Permanentemente:** Elimina la asociación
   - **❌ NO, Cancelar:** Vuelve a los detalles sin eliminar

5. **Confirmación final:**
   Si confirmas, recibirás un resumen de lo eliminado:
   - Nombre de la asociación eliminada
   - Datos de contacto
   - Número de animales eliminados
   - Fecha y hora de la eliminación
   - Confirmación de éxito

### Características

- **Doble confirmación:** Previene eliminaciones accidentales
- **Información completa:** Muestra qué se eliminará antes de confirmar
- **Eliminación en cascada:** Elimina automáticamente todos los animales asociados
- **Irreversible:** La eliminación es permanente (usa `asociacion.delete()`)
- **Logging completo:** Todas las acciones se registran en los logs

### Advertencia

⚠️ **IMPORTANTE:** Esta acción NO se puede deshacer. Cuando eliminas una asociación:
- Se elimina permanentemente de la base de datos
- Se eliminan TODOS sus animales registrados
- Se eliminan todos los datos relacionados
- No hay forma de recuperar la información

### Ejemplo de uso

```
[En detalles de una asociación]

Admin: [Presiona 🗑️ Eliminar]

Bot: ⚠️ CONFIRMACIÓN DE ELIMINACIÓN
     Estás a punto de eliminar la asociación:

     📋 Nombre: Asociación Ejemplo
     📧 Email: ejemplo@email.com
     🐾 Animales registrados: 15

     🚨 ADVERTENCIA:
     Esta acción es PERMANENTE e IRREVERSIBLE.

     ¿Estás seguro de que deseas continuar?

     [✅ SÍ, Eliminar Permanentemente] [❌ NO, Cancelar]

Admin: [Presiona ✅ SÍ, Eliminar Permanentemente]

Bot: 🗑️ ASOCIACIÓN ELIMINADA PERMANENTEMENTE

     📋 Asociación eliminada:
     • Nombre: Asociación Ejemplo
     • Email: ejemplo@email.com

     📊 Datos eliminados:
     • Asociación completa
     • 15 animales registrados
     • Todos los datos relacionados

     ✅ Operación completada exitosamente
```

---

## Comandos Disponibles

### Comandos principales

| Comando | Alias | Descripción |
|---------|-------|-------------|
| `/registrar` | `/nueva_asociacion` | Inicia el proceso de registro de asociación |
| `/cancelar` | - | Cancela el proceso de registro actual |
| `/ayuda` | `/help` | Muestra la lista de comandos disponibles |

### Comandos de prueba (solo desarrollo)

Estos comandos están disponibles en las funciones de prueba del archivo:

```python
from myapp.telegram_utils import probar_telegram, probar_botones_telegram

probar_telegram()  # Prueba conexión básica
probar_botones_telegram()  # Prueba sistema de botones
```

---

## Detalles Técnicos

### Archivos modificados

#### `myapp/telegram_utils.py`

**Nuevas funciones agregadas:**

1. **Sistema de estados conversacionales:**
   ```python
   guardar_estado_conversacion(chat_id, estado, datos)
   obtener_estado_conversacion(chat_id)
   limpiar_estado_conversacion(chat_id)
   ```

2. **Registro de asociaciones:**
   ```python
   iniciar_registro_asociacion(chat_id)
   procesar_paso_registro(chat_id, texto)
   crear_asociacion_desde_telegram(chat_id, datos)
   ```

3. **Eliminación de asociaciones:**
   ```python
   manejar_eliminar_asociacion(callback_data, chat_id, message_id, callback_query_id)
   manejar_confirmar_eliminar(callback_data, chat_id, message_id, callback_query_id)
   ```

**Modificaciones en funciones existentes:**

1. **`telegram_webhook()`:**
   - Agregado procesamiento de comandos de texto
   - Agregado procesamiento de respuestas en flujo de registro
   - Agregado manejo de comandos `/registrar`, `/cancelar`, `/ayuda`

2. **`manejar_ver_detalles()`:**
   - Agregado botón "🗑️ Eliminar" en ambos estados (pendiente y otros)

3. **Callbacks procesados:**
   - `eliminar_{id}` → Muestra confirmación
   - `confirmar_eliminar_{id}` → Ejecuta eliminación

### Estructura de datos

#### Estado conversacional

```python
ESTADOS_CONVERSACION[chat_id] = {
    'estado': 'esperando_nombre',  # o esperando_email, esperando_telefono, etc.
    'datos': {
        'nombre': 'Asociación Ejemplo',
        'email': 'ejemplo@email.com',
        # ... resto de datos
    },
    'timestamp': datetime.now()
}
```

#### Estados del flujo de registro

1. `esperando_nombre`
2. `esperando_email`
3. `esperando_telefono`
4. `esperando_direccion`
5. `esperando_poblacion`
6. `esperando_provincia`
7. `esperando_codigo_postal`
8. `esperando_password`

### Validaciones implementadas

| Campo | Validación |
|-------|-----------|
| Nombre | Unicidad en base de datos |
| Email | Regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` |
| Teléfono | Mínimo 9 dígitos (permite +, -, espacios, paréntesis) |
| Dirección | Mínimo 5 caracteres |
| Población | Mínimo 2 caracteres |
| Provincia | Mínimo 2 caracteres |
| Código postal | Mínimo 4 caracteres alfanuméricos |
| Contraseña | Mínimo 6 caracteres |

### Seguridad

- **Hashing de contraseñas:** Usa `make_password()` de Django
- **Validación de formato:** Regex y validaciones personalizadas
- **Logging completo:** Todas las acciones se registran
- **Doble confirmación:** Para acciones destructivas
- **Estados aislados:** Cada chat tiene su propio estado

### Base de datos

Al crear una asociación desde Telegram:

```python
RegistroAsociacion.objects.create(
    nombre=datos['nombre'],
    email=datos['email'],
    telefono=datos['telefono'],
    direccion=datos['direccion'],
    poblacion=datos['poblacion'],
    provincia=datos['provincia'],
    codigo_postal=datos['codigo_postal'],
    password=make_password(datos['password']),  # Hasheada
    estado='activa',  # Directamente activa
    aprobada_por='Admin Telegram',
    fecha_aprobacion=timezone.now()
)
```

Al eliminar una asociación:

```python
asociacion.delete()  # Eliminación en cascada automática
```

Los animales asociados se eliminan automáticamente gracias al `on_delete=models.CASCADE` en el modelo `CreacionAnimales`.

---

## Pruebas

### Script de prueba

Se ha creado un script de prueba interactivo:

```bash
python test_telegram_nuevas_funciones.py
```

**Opciones disponibles:**

1. Probar conexión con Telegram
2. Enviar mensaje de ayuda con comandos disponibles
3. Simular inicio de registro
4. Enviar resumen de funcionalidades implementadas

### Pruebas manuales recomendadas

#### 1. Probar registro completo

```
1. Enviar: /registrar
2. Completar todos los pasos
3. Verificar que la asociación se creó:
   - En panel de admin web
   - En la base de datos
4. Intentar login con las credenciales
```

#### 2. Probar validaciones

```
1. Enviar: /registrar
2. Nombre duplicado → Debe rechazar
3. Email inválido (sin @) → Debe rechazar
4. Teléfono corto (menos de 9 dígitos) → Debe rechazar
5. Contraseña corta (menos de 6 caracteres) → Debe rechazar
```

#### 3. Probar cancelación

```
1. Enviar: /registrar
2. Completar 3-4 pasos
3. Enviar: /cancelar
4. Verificar que el estado se limpió
5. Enviar texto normal → No debe procesarse como paso
```

#### 4. Probar eliminación

```
1. Ir a detalles de una asociación
2. Presionar 🗑️ Eliminar
3. Verificar advertencia y datos mostrados
4. Presionar ❌ NO, Cancelar → Debe volver a detalles
5. Presionar 🗑️ Eliminar nuevamente
6. Presionar ✅ SÍ, Eliminar Permanentemente
7. Verificar eliminación en base de datos
```

#### 5. Probar eliminación de asociación con animales

```
1. Crear asociación de prueba
2. Agregar 5-10 animales a esa asociación
3. Eliminar la asociación desde Telegram
4. Verificar que:
   - La asociación ya no existe
   - Los animales también fueron eliminados
   - El mensaje muestra el conteo correcto
```

### Verificación en logs

Todas las acciones se registran. Verificar en los logs:

```python
# Inicio de registro
[INFO] Proceso de registro iniciado para chat {chat_id}

# Cada paso
[INFO] Estado guardado para chat {chat_id}: esperando_email

# Creación exitosa
[INFO] Creando nueva asociación desde Telegram: Asociación Ejemplo
[INFO] Asociación Asociación Ejemplo creada exitosamente con ID: 123
[INFO] Confirmación de creación enviada para Asociación Ejemplo

# Eliminación
[INFO] Solicitando confirmación para eliminar asociación ID: 123
[INFO] Eliminando permanentemente asociación ID: 123
[INFO] Datos guardados. Procediendo a eliminar: Asociación Ejemplo
[INFO] Asociación Asociación Ejemplo eliminada permanentemente de la base de datos
[INFO] Eliminación de Asociación Ejemplo completada exitosamente
```

---

## Casos de uso

### Caso 1: Alta rápida de asociación de confianza

**Situación:** El administrador conoce personalmente a una asociación y quiere darle acceso inmediato.

**Solución:**
1. Usar `/registrar` en Telegram
2. Ingresar todos los datos en 2-3 minutos
3. La asociación queda activa inmediatamente
4. Compartir las credenciales con la asociación

### Caso 2: Limpieza de asociaciones inactivas

**Situación:** Hay asociaciones que ya no operan y tienen animales antiguos.

**Solución:**
1. Revisar lista de asociaciones en panel admin
2. Para cada una inactiva, ver detalles en Telegram
3. Usar botón 🗑️ Eliminar
4. Confirmar para limpiar la base de datos

### Caso 3: Corrección de registro erróneo

**Situación:** Se registró una asociación con datos incorrectos.

**Solución:**
1. Eliminar la asociación con datos incorrectos
2. Volver a registrarla con `/registrar`
3. Ingresar los datos correctos

---

## Limitaciones conocidas

1. **Almacenamiento de estados en memoria:**
   - Los estados se pierden si se reinicia el servidor
   - En producción, considerar usar Redis o base de datos

2. **Un proceso por vez por chat:**
   - Solo se puede tener un proceso de registro activo
   - No afecta en uso normal (un solo admin)

3. **Sin edición de datos:**
   - No se puede volver atrás en el proceso
   - Usar `/cancelar` y empezar de nuevo si hay error

4. **Eliminación irreversible:**
   - No hay papelera de reciclaje
   - Considerar agregar soft-delete en futuras versiones

---

## Mejoras futuras sugeridas

1. **Persistencia de estados:**
   - Usar Redis o tabla en base de datos
   - Permite reiniciar servidor sin perder procesos

2. **Edición de asociaciones:**
   - Comando `/editar {id}` para modificar datos
   - Flujo similar al de registro

3. **Soft delete:**
   - No eliminar permanentemente, solo marcar como eliminada
   - Posibilidad de recuperar en 30 días

4. **Confirmación por email:**
   - Enviar email a la asociación con sus credenciales
   - Confirmación de creación

5. **Bulk operations:**
   - Listar todas las asociaciones
   - Eliminar múltiples asociaciones de una vez

6. **Estadísticas:**
   - Comando `/stats` para ver métricas
   - Resumen de asociaciones creadas/eliminadas por período

---

## Soporte y troubleshooting

### Problema: El bot no responde a /registrar

**Soluciones:**
1. Verificar que el webhook esté configurado:
   ```python
   from myapp.telegram_utils import verificar_webhook_url
   verificar_webhook_url()
   ```

2. Verificar que ngrok esté corriendo:
   ```bash
   curl http://localhost:4040/api/tunnels
   ```

3. Revisar logs del servidor Django

### Problema: El estado se pierde a mitad del registro

**Causa:** El servidor se reinició o hubo un error.

**Solución:**
1. Enviar `/cancelar` para limpiar
2. Volver a empezar con `/registrar`

### Problema: No aparece el botón de eliminar

**Solución:**
1. Verificar que estés viendo los detalles (botón 👁️)
2. Actualizar el archivo telegram_utils.py
3. Reiniciar el servidor Django

### Problema: La asociación no se crea

**Verificar:**
1. Logs del servidor para errores
2. Que todos los campos pasaron validación
3. Que el nombre no exista ya
4. Permisos de base de datos

---

## Conclusión

Las nuevas funcionalidades implementadas proporcionan:

✅ **Mayor eficiencia:** Registro rápido sin usar panel web
✅ **Mejor control:** Eliminación con confirmación desde Telegram
✅ **Validación robusta:** Todos los datos se validan antes de guardar
✅ **Seguridad:** Contraseñas hasheadas, doble confirmación para acciones destructivas
✅ **Trazabilidad:** Logging completo de todas las acciones

Estas herramientas hacen que la gestión de asociaciones sea más ágil y cómoda para el administrador, permitiendo realizar las operaciones más comunes directamente desde Telegram sin necesidad de acceder al panel web.
