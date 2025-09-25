"""
Script para verificar y configurar el webhook de Telegram
"""
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("ERROR: No se encontro TELEGRAM_BOT_TOKEN en las variables de entorno")
    exit(1)

# Verificar el estado actual del webhook
def verificar_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            webhook_info = data['result']
            print("Estado del Webhook:")
            print(f"   URL: {webhook_info.get('url', 'No configurado')}")
            print(f"   Tiene certificado personalizado: {webhook_info.get('has_custom_certificate', False)}")
            print(f"   Conexiones pendientes: {webhook_info.get('pending_update_count', 0)}")

            if webhook_info.get('last_error_date'):
                print(f"   ADVERTENCIA - Ultimo error: {webhook_info.get('last_error_message', 'Sin detalles')}")
                print(f"   Fecha del error: {webhook_info.get('last_error_date')}")
            else:
                print("   OK - Sin errores recientes")

            print(f"   Métodos permitidos: {webhook_info.get('allowed_updates', ['Todos'])}")
            return webhook_info.get('url', '')
    else:
        print(f"ERROR verificando webhook: {response.status_code}")
        return None

# Configurar el webhook
def configurar_webhook(webhook_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    # Configurar el webhook con todos los tipos de actualizaciones
    params = {
        'url': webhook_url,
        'allowed_updates': ['message', 'callback_query', 'inline_query']
    }

    response = requests.post(url, json=params)

    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            print("EXITO: Webhook configurado exitosamente!")
            return True
        else:
            print(f"ERROR configurando webhook: {data.get('description', 'Sin descripcion')}")
            return False
    else:
        print(f"ERROR HTTP configurando webhook: {response.status_code}")
        return False

# Eliminar el webhook (para pruebas)
def eliminar_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)

    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            print("Webhook eliminado")
            return True
    return False

# Obtener actualizaciones pendientes
def obtener_actualizaciones():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            updates = data['result']
            print(f"\nActualizaciones pendientes: {len(updates)}")
            for update in updates[-5:]:  # Mostrar las últimas 5
                if 'callback_query' in update:
                    callback = update['callback_query']
                    print(f"   - Callback: {callback.get('data', 'Sin datos')}")
                    print(f"     De: {callback.get('from', {}).get('username', 'Desconocido')}")
            return updates
    return []

if __name__ == "__main__":
    print("Verificando configuracion del Bot de Telegram\n")

    # Verificar estado actual
    webhook_actual = verificar_webhook()

    print("\n" + "="*50)

    # Preguntar al usuario qué hacer
    if webhook_actual:
        print(f"\nWebhook actual: {webhook_actual}")
        opcion = input("\nQue deseas hacer?\n1. Mantener webhook actual\n2. Cambiar webhook\n3. Eliminar webhook y usar polling\n4. Ver actualizaciones pendientes\n\nOpcion: ")
    else:
        opcion = input("\nADVERTENCIA: No hay webhook configurado\n\nQue deseas hacer?\n1. Configurar webhook\n2. Ver actualizaciones pendientes\n\nOpcion: ")
        if opcion == "2":
            opcion = "4"

    if opcion == "2" or (opcion == "1" and not webhook_actual):
        nueva_url = input("\nIngresa la URL del webhook (ejemplo: https://tu-ngrok-url.ngrok.io/telegram/webhook/): ").strip()
        if nueva_url:
            if configurar_webhook(nueva_url):
                print("\nEXITO: Webhook configurado correctamente")
                # Verificar de nuevo
                verificar_webhook()
    elif opcion == "3":
        if eliminar_webhook():
            print("Ahora puedes obtener actualizaciones con polling")
    elif opcion == "4":
        obtener_actualizaciones()

    print("\nVerificacion completa")