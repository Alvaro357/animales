"""
Script de prueba para las nuevas funcionalidades de Telegram

Este script prueba:
1. Registro de asociación mediante comando /registrar
2. Eliminación de asociación con confirmación

INSTRUCCIONES DE USO:
1. Asegúrate de que el servidor Django esté corriendo: python manage.py runserver
2. Asegúrate de que ngrok esté activo: ngrok http 8000
3. Ejecuta este script: python test_telegram_nuevas_funciones.py
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.telegram_utils import (
    enviar_mensaje_telegram,
    iniciar_registro_asociacion,
    TELEGRAM_CHAT_ID,
    probar_telegram
)

def menu_principal():
    """Muestra el menú principal de pruebas"""
    print("\n" + "="*60)
    print("PRUEBA DE NUEVAS FUNCIONALIDADES DE TELEGRAM")
    print("="*60)
    print("\nOpciones disponibles:")
    print("1. Probar conexión con Telegram")
    print("2. Enviar mensaje de ayuda con comandos disponibles")
    print("3. Simular inicio de registro (envía instrucciones)")
    print("4. Enviar resumen de funcionalidades implementadas")
    print("0. Salir")
    print("\nNOTA: Para probar el flujo completo, usa los comandos en Telegram:")
    print("  • /registrar - Inicia el proceso de registro paso a paso")
    print("  • /ayuda - Muestra los comandos disponibles")
    print("  • Usa los botones 🗑️ Eliminar en los detalles de asociación")
    print("="*60)

def probar_conexion():
    """Prueba la conexión básica con Telegram"""
    print("\n[TEST] Probando conexión con Telegram...")
    resultado = probar_telegram()
    if resultado:
        print("✅ Conexión exitosa!")
    else:
        print("❌ Error en la conexión")
    return resultado

def enviar_mensaje_ayuda():
    """Envía un mensaje con los comandos disponibles"""
    print("\n[TEST] Enviando mensaje de ayuda...")
    mensaje = """
🤖 COMANDOS DISPONIBLES

📋 Gestión de Asociaciones:
• /registrar - Registrar nueva asociación
• /nueva_asociacion - Alias de /registrar
• /cancelar - Cancelar proceso actual

ℹ️ Información:
• /ayuda - Mostrar esta ayuda
• /help - Alias de /ayuda

💡 Nota: Los botones en los mensajes te permiten aprobar, rechazar o eliminar asociaciones de forma interactiva.
    """

    resultado = enviar_mensaje_telegram(mensaje)
    if resultado:
        print("✅ Mensaje de ayuda enviado exitosamente!")
    else:
        print("❌ Error enviando mensaje")
    return resultado

def simular_inicio_registro():
    """Simula el inicio del proceso de registro"""
    print("\n[TEST] Iniciando proceso de registro...")
    print("NOTA: Esta función enviará las instrucciones al chat de Telegram.")
    print("Para continuar, debes usar el comando /registrar directamente en Telegram.")

    try:
        iniciar_registro_asociacion(TELEGRAM_CHAT_ID)
        print("✅ Instrucciones de registro enviadas!")
        print("\nPasos que seguirá el sistema:")
        print("  1. Solicitará el nombre de la asociación")
        print("  2. Solicitará el email")
        print("  3. Solicitará el teléfono")
        print("  4. Solicitará la dirección")
        print("  5. Solicitará la población")
        print("  6. Solicitará la provincia")
        print("  7. Solicitará el código postal")
        print("  8. Solicitará la contraseña")
        print("  9. Creará la asociación automáticamente")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def enviar_resumen_implementacion():
    """Envía un resumen de las funcionalidades implementadas"""
    print("\n[TEST] Enviando resumen de implementación...")

    mensaje = """
🎉 NUEVAS FUNCIONALIDADES IMPLEMENTADAS

✅ 1. REGISTRO DE ASOCIACIONES DESDE TELEGRAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Comando: /registrar o /nueva_asociacion

🔄 Flujo conversacional paso a paso:
1️⃣ Nombre de la asociación (valida unicidad)
2️⃣ Email (valida formato)
3️⃣ Teléfono (mínimo 9 dígitos)
4️⃣ Dirección completa
5️⃣ Población
6️⃣ Provincia
7️⃣ Código postal
8️⃣ Contraseña (mínimo 6 caracteres, hasheada automáticamente)

✨ Características:
• Validación en tiempo real de cada campo
• La asociación se crea con estado 'activa'
• Contraseña hasheada con make_password()
• Tokens de gestión generados automáticamente
• Confirmación detallada al finalizar

✅ 2. ELIMINACIÓN DE ASOCIACIONES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗑️ Botón agregado en detalles de asociación

🔒 Proceso con doble confirmación:
1. Al presionar 🗑️ Eliminar, muestra:
   • Datos de la asociación
   • Número de animales afectados
   • Advertencia de acción irreversible

2. Requiere confirmación explícita:
   • ✅ SÍ, Eliminar Permanentemente
   • ❌ NO, Cancelar

3. Al confirmar:
   • Elimina asociación permanentemente
   • Elimina todos los animales asociados (CASCADE)
   • Muestra resumen de lo eliminado
   • Registra en logs la acción

🛡️ SEGURIDAD Y VALIDACIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Sistema de estados conversacionales
• Validación de formato de email (regex)
• Validación de teléfono (mínimo 9 dígitos)
• Nombres de asociación únicos
• Contraseñas hasheadas con Django
• Logging completo de todas las acciones
• Confirmación obligatoria para eliminación

📋 COMANDOS DISPONIBLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/registrar - Registrar nueva asociación
/nueva_asociacion - Alias de /registrar
/cancelar - Cancelar proceso actual
/ayuda o /help - Mostrar ayuda

🔧 IMPLEMENTACIÓN TÉCNICA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos modificados:
📄 myapp/telegram_utils.py
  • Sistema de estados conversacionales
  • Funciones: iniciar_registro_asociacion()
  • Funciones: procesar_paso_registro()
  • Funciones: crear_asociacion_desde_telegram()
  • Funciones: manejar_eliminar_asociacion()
  • Funciones: manejar_confirmar_eliminar()
  • Webhook actualizado para comandos
  • Callbacks actualizados

💡 Ahora puedes probar usando:
• /registrar en este chat
• Botón 🗑️ en detalles de asociación
    """

    resultado = enviar_mensaje_telegram(mensaje)
    if resultado:
        print("✅ Resumen enviado exitosamente!")
        print("\nPuedes ver el resumen completo en Telegram.")
    else:
        print("❌ Error enviando resumen")
    return resultado

def main():
    """Función principal"""
    while True:
        menu_principal()

        try:
            opcion = input("\nSelecciona una opción (0-4): ").strip()

            if opcion == '0':
                print("\n¡Hasta luego!")
                break
            elif opcion == '1':
                probar_conexion()
            elif opcion == '2':
                enviar_mensaje_ayuda()
            elif opcion == '3':
                simular_inicio_registro()
            elif opcion == '4':
                enviar_resumen_implementacion()
            else:
                print("❌ Opción no válida. Por favor, selecciona 0-4.")

            input("\nPresiona Enter para continuar...")

        except KeyboardInterrupt:
            print("\n\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPresiona Enter para continuar...")

if __name__ == '__main__':
    print("\n🚀 Iniciando script de prueba...")
    print("Asegúrate de que:")
    print("  1. Django esté corriendo (python manage.py runserver)")
    print("  2. ngrok esté activo (ngrok http 8000)")
    print("  3. El webhook de Telegram esté configurado")

    try:
        main()
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
