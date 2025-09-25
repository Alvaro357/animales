#!/usr/bin/env python
"""
Script de prueba completo para verificar el funcionamiento de los botones de Telegram
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import RegistroAsociacion
from myapp.telegram_utils import enviar_mensaje_telegram
from django.utils import timezone
from datetime import datetime

def crear_asociacion_prueba():
    """Crea una asociación de prueba si no existe"""
    # Buscar o crear una asociación de prueba
    asociacion, created = RegistroAsociacion.objects.get_or_create(
        email='prueba_telegram@test.com',
        defaults={
            'nombre': 'Asociación de Prueba Telegram',
            'telefono': '600000000',
            'direccion': 'Calle Test 123',
            'poblacion': 'Ciudad de Prueba',
            'provincia': 'Madrid',
            'codigo_postal': '28001',
            'password': 'test123',
            'estado': 'pendiente',
            'fecha_registro': timezone.now()
        }
    )

    if not created:
        # Si ya existía, asegurarnos de que esté pendiente
        asociacion.estado = 'pendiente'
        asociacion.save()
        print(f"Usando asociación existente: {asociacion.nombre} (ID: {asociacion.id})")
    else:
        print(f"Creada nueva asociación de prueba: {asociacion.nombre} (ID: {asociacion.id})")

    return asociacion

def enviar_mensaje_prueba(asociacion):
    """Envía un mensaje de prueba con botones interactivos"""

    mensaje = f"""
🧪 <b>PRUEBA DEL SISTEMA DE BOTONES</b>

Esta es una asociación de prueba para verificar que los botones funcionan correctamente.

🏢 <b>Información de prueba:</b>
• 🏷️ <b>Nombre:</b> {asociacion.nombre}
• 📧 <b>Email:</b> {asociacion.email}
• 📞 <b>Teléfono:</b> {asociacion.telefono}
• 📍 <b>Ubicación:</b> {asociacion.poblacion}, {asociacion.provincia}
• 📅 <b>Fecha:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}

⏳ <b>Estado:</b> {asociacion.get_estado_display()}

🆔 <b>ID:</b> {asociacion.id}

🔧 <b>Instrucciones de prueba:</b>
1. Presiona "✅ Aprobar" para aprobar la asociación
2. Presiona "❌ Rechazar" para rechazar y eliminar
3. Presiona "👁️ Más Detalles" para ver información completa
    """

    # Botones con callback_data reales
    botones = [
        [
            {
                "text": "✅ Aprobar",
                "callback_data": f"aprobar_{asociacion.id}"
            },
            {
                "text": "❌ Rechazar",
                "callback_data": f"rechazar_{asociacion.id}"
            }
        ],
        [
            {
                "text": "👁️ Más Detalles",
                "callback_data": f"ver_{asociacion.id}"
            }
        ]
    ]

    return enviar_mensaje_telegram(mensaje, botones)

def main():
    print("=" * 50)
    print("PRUEBA COMPLETA DEL SISTEMA DE BOTONES DE TELEGRAM")
    print("=" * 50)

    # Crear asociación de prueba
    print("\n1. Creando asociación de prueba...")
    asociacion = crear_asociacion_prueba()

    # Enviar mensaje con botones
    print("\n2. Enviando mensaje a Telegram con botones interactivos...")
    resultado = enviar_mensaje_prueba(asociacion)

    if resultado:
        print("\nMensaje enviado exitosamente!")
        print("\nINSTRUCCIONES:")
        print("   1. Abre Telegram y busca el mensaje")
        print("   2. Prueba cada uno de los tres botones:")
        print("      - Aprobar: Debe aprobar la asociacion")
        print("      - Rechazar: Debe rechazar y eliminar la asociacion")
        print("      - Mas Detalles: Debe mostrar informacion detallada con enlaces")
        print("\n   3. Verifica que los botones respondan correctamente")
        print("   4. Revisa los logs del servidor Django para ver el procesamiento")
    else:
        print("\nError enviando el mensaje")
        print("   Verifica la configuracion del bot de Telegram")

    print("\n" + "=" * 50)
    print("PRUEBA FINALIZADA")
    print("=" * 50)

if __name__ == '__main__':
    main()