#!/usr/bin/env python
import requests
import json

# Configuración del bot
TELEGRAM_BOT_TOKEN = '8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU'

# Obtener URL de ngrok
try:
    response = requests.get('http://localhost:4040/api/tunnels')
    tunnels = response.json()['tunnels']
    ngrok_url = tunnels[0]['public_url']
    webhook_url = f"{ngrok_url}/telegram/webhook/"
    print(f"URL de ngrok detectada: {ngrok_url}")
    print(f"URL del webhook: {webhook_url}")
except Exception as e:
    print(f"Error obteniendo URL de ngrok: {e}")
    print("Usando URL local por defecto...")
    webhook_url = "http://localhost:8000/telegram/webhook/"

# Configurar el webhook
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
data = {
    'url': webhook_url,
    'drop_pending_updates': False,  # No eliminar actualizaciones pendientes
    'allowed_updates': ['message', 'callback_query', 'inline_query']
}

print("\nConfigurando webhook...")
response = requests.post(url, data=data)

if response.status_code == 200:
    result = response.json()
    if result.get('ok'):
        print("Webhook configurado exitosamente!")
        print(f"   URL: {webhook_url}")

        # Verificar configuración
        info_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo"
        info_response = requests.get(info_url)
        if info_response.status_code == 200:
            info = info_response.json().get('result', {})
            print("\nInformacion del webhook:")
            print(f"   - URL: {info.get('url')}")
            print(f"   - Actualizaciones pendientes: {info.get('pending_update_count', 0)}")
            if info.get('last_error_message'):
                print(f"   - Ultimo error: {info.get('last_error_message')}")
    else:
        print(f"Error: {result.get('description', 'Unknown error')}")
else:
    print(f"Error HTTP: {response.status_code}")
    print(response.text)

print("\nPrueba los botones en Telegram para verificar que funcionan correctamente.")