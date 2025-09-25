import requests

# Tu token de Telegram
BOT_TOKEN = "8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU"

# Primero eliminar el webhook existente
print("1. Eliminando webhook existente...")
delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
response = requests.get(delete_url)
print(f"   Resultado: {response.json()}")

# Ahora obtener las actualizaciones
print("\n2. Obteniendo actualizaciones...")
updates_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(updates_url)
data = response.json()

if data['ok']:
    if data['result']:
        print("\n3. Mensajes encontrados:")
        for update in data['result']:
            if 'message' in update:
                chat = update['message']['chat']
                print(f"\n   Chat ID: {chat['id']}")
                print(f"   Tipo: {chat.get('type', 'private')}")
                if 'username' in chat:
                    print(f"   Usuario: @{chat['username']}")
                if 'first_name' in chat:
                    print(f"   Nombre: {chat['first_name']}")
                if 'text' in update['message']:
                    print(f"   Mensaje: {update['message']['text']}")
    else:
        print("\n   No hay mensajes. Envía un mensaje a tu bot primero.")
        print("   Busca tu bot en Telegram y envíale cualquier mensaje como 'Hola'")
else:
    print(f"\n   Error: {data}")

print("\n4. Para restaurar el webhook más tarde (si lo necesitas):")
print(f"   https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url=TU_URL_DEL_WEBHOOK")