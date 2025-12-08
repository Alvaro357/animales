# Ejemplos Prácticos de Uso - Telegram

Este documento muestra ejemplos reales de cómo usar las nuevas funcionalidades de Telegram.

## Índice

1. [Registro Completo de Asociación](#ejemplo-1-registro-completo-de-asociación)
2. [Registro con Validación de Errores](#ejemplo-2-registro-con-validación-de-errores)
3. [Cancelación de Registro](#ejemplo-3-cancelación-de-registro)
4. [Eliminación de Asociación](#ejemplo-4-eliminación-de-asociación)
5. [Eliminación Cancelada](#ejemplo-5-eliminación-cancelada)

---

## Ejemplo 1: Registro Completo de Asociación

### Conversación paso a paso

```
ADMIN:
/registrar

BOT:
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

ADMIN:
Protectora de Animales San Fernando

BOT:
✅ Nombre: Protectora de Animales San Fernando

Ahora envíame el EMAIL de contacto:

ADMIN:
contacto@protectora-sanfernando.org

BOT:
✅ Email: contacto@protectora-sanfernando.org

Ahora envíame el TELÉFONO de contacto:

ADMIN:
+34 912 345 678

BOT:
✅ Teléfono: +34 912 345 678

Ahora envíame la DIRECCIÓN completa:

ADMIN:
Calle de los Olivos, 25

BOT:
✅ Dirección: Calle de los Olivos, 25

Ahora envíame la POBLACIÓN:

ADMIN:
San Fernando de Henares

BOT:
✅ Población: San Fernando de Henares

Ahora envíame la PROVINCIA:

ADMIN:
Madrid

BOT:
✅ Provincia: Madrid

Ahora envíame el CÓDIGO POSTAL:

ADMIN:
28830

BOT:
✅ Código postal: 28830

Finalmente, envíame la CONTRASEÑA para acceso al sistema (mínimo 6 caracteres):

ADMIN:
Protectora2025!

BOT:
✅ ASOCIACIÓN CREADA EXITOSAMENTE

📋 Datos registrados:
• Nombre: Protectora de Animales San Fernando
• Email: contacto@protectora-sanfernando.org
• Teléfono: +34 912 345 678
• Dirección: Calle de los Olivos, 25
• Población: San Fernando de Henares
• Provincia: Madrid
• Código postal: 28830

🎉 Estado: ACTIVA
📅 Fecha: 19/11/2025 14:30
🔑 ID: 42

La asociación ya puede acceder al sistema con:
• Usuario: Protectora de Animales San Fernando
• Contraseña: (la que configuraste)

🌐 URL de acceso: http://127.0.0.1:8000/login/
```

### Resultado en la base de datos

```python
# Nueva entrada en RegistroAsociacion:
{
    'id': 42,
    'nombre': 'Protectora de Animales San Fernando',
    'email': 'contacto@protectora-sanfernando.org',
    'telefono': '+34 912 345 678',
    'direccion': 'Calle de los Olivos, 25',
    'poblacion': 'San Fernando de Henares',
    'provincia': 'Madrid',
    'codigo_postal': '28830',
    'password': 'pbkdf2_sha256$...',  # Hasheada
    'estado': 'activa',
    'aprobada_por': 'Admin Telegram',
    'fecha_aprobacion': datetime.now(),
    'fecha_registro': datetime.now()
}
```

---

## Ejemplo 2: Registro con Validación de Errores

### Nombre duplicado

```
ADMIN:
/registrar

BOT:
Para comenzar, por favor envíame el NOMBRE de la asociación:

ADMIN:
Protectora Madrid

BOT:
❌ Ya existe una asociación con el nombre 'Protectora Madrid'.
Por favor, elige otro nombre:

ADMIN:
Protectora Madrid Norte

BOT:
✅ Nombre: Protectora Madrid Norte

Ahora envíame el EMAIL de contacto:
```

### Email inválido

```
BOT:
Ahora envíame el EMAIL de contacto:

ADMIN:
contacto.protectora

BOT:
❌ El formato del email no es válido.
Por favor, envía un email correcto:

ADMIN:
contacto@protectora.com

BOT:
✅ Email: contacto@protectora.com

Ahora envíame el TELÉFONO de contacto:
```

### Teléfono corto

```
BOT:
Ahora envíame el TELÉFONO de contacto:

ADMIN:
912345

BOT:
❌ El teléfono debe contener al menos 9 dígitos.
Por favor, envía un teléfono válido:

ADMIN:
912345678

BOT:
✅ Teléfono: 912345678

Ahora envíame la DIRECCIÓN completa:
```

### Contraseña corta

```
BOT:
Finalmente, envíame la CONTRASEÑA para acceso al sistema (mínimo 6 caracteres):

ADMIN:
1234

BOT:
❌ La contraseña debe tener al menos 6 caracteres.
Por favor, envía una contraseña más segura:

ADMIN:
Pass2025!

BOT:
✅ ASOCIACIÓN CREADA EXITOSAMENTE
[... resto del mensaje ...]
```

---

## Ejemplo 3: Cancelación de Registro

### Cancelar en medio del proceso

```
ADMIN:
/registrar

BOT:
Para comenzar, por favor envíame el NOMBRE de la asociación:

ADMIN:
Asociación Test

BOT:
✅ Nombre: Asociación Test

Ahora envíame el EMAIL de contacto:

ADMIN:
test@example.com

BOT:
✅ Email: test@example.com

Ahora envíame el TELÉFONO de contacto:

ADMIN:
/cancelar

BOT:
❌ Proceso cancelado.

ADMIN:
Hola

BOT:
[No hay respuesta - no hay proceso activo]
```

### Reiniciar después de cancelar

```
ADMIN:
/cancelar

BOT:
❌ Proceso cancelado.

ADMIN:
/registrar

BOT:
🏢 REGISTRO DE NUEVA ASOCIACIÓN

Voy a pedirte los siguientes datos paso a paso:
[... nuevo proceso comienza desde cero ...]
```

---

## Ejemplo 4: Eliminación de Asociación

### Proceso completo

```
[Admin ve notificación de una asociación o usa el panel]

ADMIN:
[Presiona botón: 👁️ Más Detalles]

BOT:
👁️ DETALLES DE LA ASOCIACIÓN

📋 Información Básica:
• Nombre: Asociación Temporal
• Email: temporal@test.com
• Teléfono: 600123456

📍 Ubicación:
• Dirección: Calle Falsa 123
• Población: Madrid
• Provincia: Madrid
• Código Postal: 28001

📊 Estado:
• Estado actual: Activa
• Fecha registro: 15/11/2025 10:00
• ID: 38

🔗 Enlaces Administrativos:
• 🏠 Panel Principal
• 📋 Vista Detallada

¿Qué deseas hacer?

[Botones: ✅ Aprobar | ❌ Rechazar]
[Botón: 🗑️ Eliminar]
[Botón: 🔗 Ir al Panel Web]

ADMIN:
[Presiona botón: 🗑️ Eliminar]

BOT:
⚠️ CONFIRMACIÓN DE ELIMINACIÓN

Estás a punto de eliminar la asociación:

📋 Nombre: Asociación Temporal
📧 Email: temporal@test.com
📍 Ubicación: Madrid, Madrid
📊 Estado: Activa
🐾 Animales registrados: 12

🚨 ADVERTENCIA:
Esta acción es PERMANENTE e IRREVERSIBLE.
Se eliminará:
• La asociación completa
• Todos sus animales (12)
• Todos los datos relacionados

¿Estás seguro de que deseas continuar?

[Botones: ✅ SÍ, Eliminar Permanentemente | ❌ NO, Cancelar]

ADMIN:
[Presiona botón: ✅ SÍ, Eliminar Permanentemente]

BOT:
🗑️ ASOCIACIÓN ELIMINADA PERMANENTEMENTE

📋 Asociación eliminada:
• Nombre: Asociación Temporal
• Email: temporal@test.com
• Ubicación: Madrid, Madrid

📊 Datos eliminados:
• Asociación completa
• 12 animales registrados
• Todos los datos relacionados

📅 Fecha de eliminación: 19/11/2025 15:45
👤 Eliminada por: Admin Telegram

✅ Operación completada exitosamente
```

### En la base de datos

```python
# ANTES de eliminar:
RegistroAsociacion.objects.filter(id=38).exists()  # True
CreacionAnimales.objects.filter(asociacion_id=38).count()  # 12

# DESPUÉS de eliminar:
RegistroAsociacion.objects.filter(id=38).exists()  # False
CreacionAnimales.objects.filter(asociacion_id=38).count()  # 0
# ↑ Eliminados en CASCADE automáticamente
```

---

## Ejemplo 5: Eliminación Cancelada

### Cambio de opinión

```
ADMIN:
[Presiona botón: 🗑️ Eliminar en detalles de asociación]

BOT:
⚠️ CONFIRMACIÓN DE ELIMINACIÓN

Estás a punto de eliminar la asociación:

📋 Nombre: Asociación Importante
📧 Email: importante@example.com
🐾 Animales registrados: 45

🚨 ADVERTENCIA:
Esta acción es PERMANENTE e IRREVERSIBLE.
Se eliminará:
• La asociación completa
• Todos sus animales (45)
• Todos los datos relacionados

¿Estás seguro de que deseas continuar?

[Botones: ✅ SÍ, Eliminar Permanentemente | ❌ NO, Cancelar]

ADMIN:
[Presiona botón: ❌ NO, Cancelar]

BOT:
👁️ DETALLES DE LA ASOCIACIÓN

📋 Información Básica:
• Nombre: Asociación Importante
• Email: importante@example.com
[... vuelve a mostrar detalles completos ...]

[Botones: ✅ Aprobar | ❌ Rechazar]
[Botón: 🗑️ Eliminar]
[Botón: 🔗 Ir al Panel Web]
```

### Resultado

- La asociación NO se eliminó
- Volvió a la vista de detalles
- Todos los datos permanecen intactos

---

## Ejemplo 6: Uso de Comando de Ayuda

```
ADMIN:
/ayuda

BOT:
🤖 COMANDOS DISPONIBLES

📋 Gestión de Asociaciones:
• /registrar - Registrar nueva asociación
• /nueva_asociacion - Alias de /registrar
• /cancelar - Cancelar proceso actual

ℹ️ Información:
• /ayuda - Mostrar esta ayuda
• /help - Alias de /ayuda

💡 Nota: Los botones en los mensajes te permiten aprobar,
rechazar o eliminar asociaciones de forma interactiva.
```

```
ADMIN:
/help

BOT:
[Mismo mensaje de ayuda que /ayuda]
```

---

## Ejemplo 7: Comando No Reconocido

```
ADMIN:
/listar

BOT:
❌ Comando no reconocido: /listar

Usa /ayuda para ver los comandos disponibles.
```

---

## Ejemplo 8: Múltiples Registros en Secuencia

```
ADMIN:
/registrar

[... completa registro de Asociación A ...]

BOT:
✅ ASOCIACIÓN CREADA EXITOSAMENTE
[Asociación A - ID: 50]

ADMIN:
/registrar

[... completa registro de Asociación B ...]

BOT:
✅ ASOCIACIÓN CREADA EXITOSAMENTE
[Asociación B - ID: 51]

ADMIN:
/registrar

[... completa registro de Asociación C ...]

BOT:
✅ ASOCIACIÓN CREADA EXITOSAMENTE
[Asociación C - ID: 52]
```

**Resultado:**
- 3 asociaciones creadas en menos de 10 minutos
- Todas activas inmediatamente
- Sin necesidad de acceder al panel web

---

## Consejos de Uso

### Para Registro Eficiente

1. **Prepara los datos antes:**
   - Ten todos los datos listos antes de iniciar
   - Copia/pega desde un documento si es necesario

2. **Verifica antes de enviar:**
   - Revisa cada dato antes de enviarlo
   - Las validaciones ayudan pero mejor prevenir

3. **Usa contraseñas seguras:**
   - Mínimo 6 caracteres (el sistema lo valida)
   - Combina letras, números y símbolos

### Para Eliminación Segura

1. **Lee la advertencia completa:**
   - Verifica el número de animales afectados
   - Confirma que es la asociación correcta

2. **Piénsalo dos veces:**
   - La eliminación es IRREVERSIBLE
   - No hay recuperación posible

3. **Considera alternativas:**
   - ¿Puedes suspender en lugar de eliminar?
   - ¿Los datos pueden ser útiles en el futuro?

### Atajos de Teclado (en Telegram Desktop)

- `Ctrl + K` - Buscar chat
- `Ctrl + ↑` - Editar último mensaje enviado
- `Esc` - Cerrar ventana actual

---

## Escenarios Comunes

### Escenario 1: Alta de urgencia en fin de semana

**Situación:** Es domingo y una protectora necesita acceso urgente.

**Solución:**
```
1. Admin abre Telegram en móvil
2. /registrar
3. Completa los datos en 3 minutos
4. Asociación activa inmediatamente
5. Comparte credenciales por WhatsApp
```

### Escenario 2: Limpieza de asociaciones duplicadas

**Situación:** Hay 3 asociaciones con nombres similares (duplicados).

**Solución:**
```
1. Ver detalles de cada una
2. Identificar la correcta
3. Eliminar las duplicadas (2)
4. Verificar en panel web
```

### Escenario 3: Migración desde sistema antiguo

**Situación:** Tienes 50 asociaciones en Excel que migrar.

**Solución:**
```
Para cada asociación:
1. /registrar
2. Copiar datos desde Excel
3. Pegar en Telegram
4. Repetir para todas
5. Verificar en panel que todas estén activas
```

---

## Troubleshooting por Ejemplos

### Problema: "El bot no responde"

```
ADMIN:
/registrar

[... sin respuesta después de 30 segundos ...]

SOLUCIÓN:
1. Verificar que Django esté corriendo
2. Verificar que ngrok esté activo
3. Revisar logs de error
4. Reintentar
```

### Problema: "Perdí el progreso del registro"

```
ADMIN:
/registrar
[... completa 5 pasos ...]
[Servidor se reinicia]

BOT:
❌ No hay proceso de registro activo. Usa /registrar para comenzar.

SOLUCIÓN:
1. /registrar
2. Empezar de nuevo (no hay recuperación)
```

### Problema: "Eliminé por error"

```
ADMIN:
[Eliminó asociación equivocada]

SOLUCIÓN:
❌ NO HAY RECUPERACIÓN AUTOMÁTICA

Opciones:
1. Si tienes backup de BD → Restaurar
2. Si tienes los datos → /registrar nuevamente
3. Contactar a la asociación para re-registrarse
```

---

## Conclusión

Estos ejemplos muestran el uso real de las nuevas funcionalidades. Recuerda:

- **Registro:** Rápido, validado, seguro
- **Eliminación:** Permanente, irreversible, con doble confirmación
- **Comandos:** Simples, intuitivos, con ayuda integrada

Para más información, consulta:
- `TELEGRAM_NUEVAS_FUNCIONES.md` - Documentación completa
- `RESUMEN_IMPLEMENTACION_TELEGRAM.md` - Resumen técnico
- `DIAGRAMA_FLUJOS_TELEGRAM.txt` - Diagramas de flujo
