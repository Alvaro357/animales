"""
Script para configurar automáticamente el webhook de Telegram
"""
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8107454170:AAGPtW3_Dit2nnIRWrQatWzc-7_K0RrAVGU')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '6344843081')

def obtener_ip_publica():
    """Intenta obtener la IP pública del servidor"""
    try:
        response = requests.get('https://api.ipify.org')
        return response.text
    except:
        return None

def configurar_webhook_local():
    """Configura el webhook para desarrollo local"""
    print("\nPara desarrollo local, necesitas exponer tu servidor local a internet.")
    print("Opciones recomendadas:")
    print("\n1. Usar ngrok (recomendado):")
    print("   - Instala ngrok: https://ngrok.com/download")
    print("   - Ejecuta: ngrok http 8000")
    print("   - Copia la URL HTTPS que te proporciona (ej: https://abc123.ngrok.io)")
    print("\n2. Usar localtunnel:")
    print("   - Instala: npm install -g localtunnel")
    print("   - Ejecuta: lt --port 8000")
    print("\nUna vez tengas la URL pública, ejecuta este script de nuevo y selecciona 'Configurar webhook manual'")

def configurar_webhook(url):
    """Configura el webhook en Telegram"""
    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"

    # Configurar el webhook con todos los tipos de actualizaciones necesarios
    params = {
        'url': url,
        'allowed_updates': ['message', 'callback_query', 'inline_query'],
        'drop_pending_updates': False  # No eliminar actualizaciones pendientes
    }

    response = requests.post(telegram_url, json=params)

    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            print(f"\nEXITO: Webhook configurado correctamente!")
            print(f"URL del webhook: {url}")
            verificar_webhook()
            return True
        else:
            print(f"\nERROR configurando webhook: {data.get('description', 'Sin descripción')}")
            return False
    else:
        print(f"\nERROR HTTP configurando webhook: {response.status_code}")
        return False

def verificar_webhook():
    """Verifica el estado actual del webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            webhook_info = data['result']
            print("\n=== ESTADO DEL WEBHOOK ===")
            print(f"URL configurada: {webhook_info.get('url', 'No configurado')}")
            print(f"Actualizaciones pendientes: {webhook_info.get('pending_update_count', 0)}")

            if webhook_info.get('last_error_date'):
                print(f"ADVERTENCIA - Ultimo error: {webhook_info.get('last_error_message', 'Sin detalles')}")
            else:
                print("Estado: Sin errores recientes")

            return webhook_info.get('url', '')
    return None

def enviar_mensaje_prueba():
    """Envía un mensaje de prueba con botones"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    mensaje = {
        'chat_id': CHAT_ID,
        'text': '🧪 *MENSAJE DE PRUEBA*\n\nPrueba los botones de callback:',
        'parse_mode': 'Markdown',
        'reply_markup': {
            'inline_keyboard': [
                [
                    {'text': '✅ Botón Aprobar', 'callback_data': 'test_aprobar'},
                    {'text': '❌ Botón Rechazar', 'callback_data': 'test_rechazar'}
                ],
                [
                    {'text': '👁️ Botón Ver Detalles', 'callback_data': 'test_ver'}
                ]
            ]
        }
    }

    response = requests.post(url, json=mensaje)
    if response.status_code == 200 and response.json()['ok']:
        print("\nMensaje de prueba enviado. Verifica los botones en Telegram.")
        return True
    else:
        print("\nError enviando mensaje de prueba")
        return False

def main():
    print("="*60)
    print("CONFIGURADOR DE WEBHOOK PARA TELEGRAM BOT")
    print("="*60)

    # Verificar estado actual
    webhook_actual = verificar_webhook()

    if webhook_actual:
        print(f"\nWebhook actual: {webhook_actual}")
        opcion = input("\nQue deseas hacer?\n1. Mantener configuración actual\n2. Cambiar webhook\n3. Enviar mensaje de prueba\n\nOpcion: ")
    else:
        print("\nNo hay webhook configurado actualmente.")
        opcion = "2"

    if opcion == "2":
        print("\n" + "="*40)
        print("CONFIGURAR NUEVO WEBHOOK")
        print("="*40)

        print("\n1. Desarrollo local (ngrok/localtunnel)")
        print("2. Servidor con IP pública")
        print("3. Configuración manual (ya tienes la URL)")

        tipo = input("\nSelecciona el tipo de configuración: ")

        if tipo == "1":
            configurar_webhook_local()
        elif tipo == "2":
            ip = obtener_ip_publica()
            if ip:
                print(f"\nIP pública detectada: {ip}")
                puerto = input("Puerto donde corre Django (default 8000): ") or "8000"
                webhook_url = f"http://{ip}:{puerto}/telegram/webhook/"
                print(f"\nNOTA: Telegram requiere HTTPS. Considera usar un proxy reverso con SSL.")
                confirmar = input(f"\nConfigurar webhook con URL: {webhook_url}? (s/n): ")
                if confirmar.lower() == 's':
                    configurar_webhook(webhook_url)
            else:
                print("No se pudo detectar la IP pública")
                configurar_webhook_local()
        elif tipo == "3":
            webhook_url = input("\nIngresa la URL completa del webhook (debe terminar en /telegram/webhook/): ").strip()
            if webhook_url:
                if not webhook_url.endswith('/telegram/webhook/'):
                    webhook_url = webhook_url.rstrip('/') + '/telegram/webhook/'
                configurar_webhook(webhook_url)

    elif opcion == "3":
        enviar_mensaje_prueba()

    print("\n" + "="*60)
    print("INSTRUCCIONES FINALES:")
    print("="*60)
    print("\n1. Asegurate de que Django esté corriendo:")
    print("   python manage.py runserver")
    print("\n2. Si usas ngrok, mantenlo ejecutándose:")
    print(" " \
    "  ngrok http 8000")
    print("\n3. Prueba el sistema registrando una nueva asociación")
    print("\n4. Los logs del webhook aparecerán en la consola de Django")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()