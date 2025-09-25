#!/usr/bin/env python
"""
Script para probar los botones de Telegram sin emojis problemáticos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.telegram_utils import enviar_mensaje_telegram
from myapp.models import RegistroAsociacion

def probar_botones_reales():
    """Envía un mensaje de prueba con botones funcionales"""

    # Obtener una asociación real para probar (si existe)
    asociacion_test = RegistroAsociacion.objects.filter(estado='pendiente').first()

    if asociacion_test:
        print(f"Encontrada asociacion de prueba: {asociacion_test.nombre} (ID: {asociacion_test.id})")

        # Crear mensaje real con botones funcionales
        mensaje = f"""PRUEBA DE SISTEMA DE BOTONES

Asociacion de prueba: {asociacion_test.nombre}
ID: {asociacion_test.id}
Estado: {asociacion_test.estado}

Presiona cualquier boton para probar:"""

        # Botones con IDs reales
        botones = [
            [
                {
                    "text": "Aprobar",
                    "callback_data": f"aprobar_{asociacion_test.id}"
                },
                {
                    "text": "Rechazar",
                    "callback_data": f"rechazar_{asociacion_test.id}"
                }
            ],
            [
                {
                    "text": "Ver Detalles",
                    "callback_data": f"ver_{asociacion_test.id}"
                }
            ]
        ]

        resultado = enviar_mensaje_telegram(mensaje, botones)

        if resultado:
            print("EXITO: Mensaje de prueba enviado con botones funcionales!")
            print("Ve a Telegram y presiona los botones.")
            print("Observa los logs del servidor Django para ver si los callbacks se procesan.")
            return True
        else:
            print("ERROR: No se pudo enviar el mensaje")
            return False

    else:
        print("No se encontraron asociaciones pendientes para probar")
        # Enviar mensaje genérico
        mensaje = """PRUEBA DE SISTEMA DE BOTONES (GENERICA)

No hay asociaciones pendientes en la base de datos.
Estos botones devuelveran error, pero puedes ver si el webhook funciona:"""

        botones = [
            [
                {
                    "text": "Prueba Aprobar",
                    "callback_data": "aprobar_test"
                },
                {
                    "text": "Prueba Rechazar",
                    "callback_data": "rechazar_test"
                }
            ]
        ]

        resultado = enviar_mensaje_telegram(mensaje, botones)

        if resultado:
            print("EXITO: Mensaje generico enviado")
            print("Los botones daran error, pero puedes ver si llegan al webhook")
            return True
        else:
            print("ERROR: No se pudo enviar mensaje generico")
            return False

def main():
    print("=== PRUEBA DE BOTONES DE TELEGRAM ===")
    print()

    # Probar el sistema
    resultado = probar_botones_reales()

    print()
    print("=== INSTRUCCIONES ===")
    print("1. Ve a tu bot de Telegram")
    print("2. Presiona cualquier boton")
    print("3. Observa los logs del servidor Django")
    print("4. El webhook debe procesar el callback sin error 400")
    print()

    if resultado:
        print("PRUEBA COMPLETADA - Revisa Telegram y los logs del servidor")
    else:
        print("PRUEBA FALLIDA - Revisa la configuracion de Telegram")

if __name__ == "__main__":
    main()