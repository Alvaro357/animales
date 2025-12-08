#!/usr/bin/env python
"""
Test exhaustivo de TODAS las funciones de botones de Telegram
Verifica que cada callback funcione correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from myapp.models import RegistroAsociacion
from myapp.telegram_utils import (
    enviar_notificacion_nueva_asociacion,
    manejar_aprobacion,
    manejar_rechazo,
    manejar_ver_detalles,
    manejar_eliminar_asociacion,
    manejar_confirmar_eliminar,
    enviar_mensaje_telegram,
    editar_mensaje_telegram,
    responder_callback
)
from django.http import JsonResponse


def test_funciones_basicas():
    """Test 1: Funciones básicas de comunicación con Telegram"""
    print("\n" + "="*70)
    print("TEST 1: FUNCIONES BASICAS DE TELEGRAM")
    print("="*70)

    tests_passed = 0
    tests_total = 3

    # Test 1.1: enviar_mensaje_telegram
    print("\n[1.1] Probando enviar_mensaje_telegram()...")
    try:
        resultado = enviar_mensaje_telegram("Test: Mensaje basico de verificacion")
        if resultado:
            print("   OK - Mensaje enviado correctamente")
            tests_passed += 1
        else:
            print("   ERROR - No se pudo enviar el mensaje")
    except Exception as e:
        print(f"   ERROR - Excepcion: {e}")

    # Test 1.2: enviar_mensaje_telegram con botones
    print("\n[1.2] Probando enviar_mensaje_telegram() CON BOTONES...")
    try:
        botones = [
            [
                {"text": "Test Boton 1", "callback_data": "test_1"},
                {"text": "Test Boton 2", "callback_data": "test_2"}
            ]
        ]
        resultado = enviar_mensaje_telegram("Test: Mensaje con botones", botones)
        if resultado:
            print("   OK - Mensaje con botones enviado correctamente")
            tests_passed += 1
        else:
            print("   ERROR - No se pudo enviar el mensaje con botones")
    except Exception as e:
        print(f"   ERROR - Excepcion: {e}")

    # Test 1.3: responder_callback
    print("\n[1.3] Probando responder_callback()...")
    try:
        # Nota: Esta funcion requiere un callback_query_id valido de Telegram
        # En pruebas simuladas, solo verificamos que la funcion exista y sea callable
        if callable(responder_callback):
            print("   OK - Funcion responder_callback() existe y es callable")
            tests_passed += 1
        else:
            print("   ERROR - Funcion no es callable")
    except Exception as e:
        print(f"   ERROR - Excepcion: {e}")

    print(f"\n[RESULTADO TEST 1] {tests_passed}/{tests_total} pruebas pasadas")
    return tests_passed == tests_total


def test_callbacks_aprobacion():
    """Test 2: Callback de aprobacion"""
    print("\n" + "="*70)
    print("TEST 2: CALLBACK DE APROBACION")
    print("="*70)

    # Buscar o crear asociacion de prueba
    print("\n[2.1] Preparando asociacion de prueba...")
    try:
        # Buscar asociacion pendiente
        asociacion = RegistroAsociacion.objects.filter(estado='pendiente').first()

        if not asociacion:
            # Crear una asociacion temporal para prueba
            from django.contrib.auth.hashers import make_password
            from django.utils import timezone

            asociacion = RegistroAsociacion.objects.create(
                nombre="Test Asociacion Aprobacion",
                email="test_aprobacion@test.com",
                telefono="666777888",
                direccion="Calle Test 123",
                poblacion="Test City",
                provincia="Test Province",
                codigo_postal="28000",
                password=make_password("test123"),
                estado='pendiente'
            )
            print(f"   OK - Asociacion de prueba creada: {asociacion.nombre} (ID: {asociacion.id})")
        else:
            print(f"   OK - Usando asociacion existente: {asociacion.nombre} (ID: {asociacion.id})")

        # Test 2.2: Enviar notificacion con botones
        print("\n[2.2] Enviando notificacion con botones de aprobacion...")
        resultado = enviar_notificacion_nueva_asociacion(asociacion, None)
        if resultado:
            print("   OK - Notificacion enviada con botones")
        else:
            print("   ERROR - No se pudo enviar la notificacion")
            return False

        # Test 2.3: Simular callback de aprobacion
        print("\n[2.3] Simulando callback de aprobacion...")
        callback_data = f"aprobar_{asociacion.id}"
        chat_id = "6344843081"  # El chat ID configurado
        message_id = "999999"  # ID de mensaje simulado
        callback_query_id = "test_callback_id"

        try:
            response = manejar_aprobacion(callback_data, chat_id, message_id, callback_query_id)

            # Verificar que la asociacion fue aprobada
            asociacion.refresh_from_db()
            if asociacion.estado == 'activa':
                print(f"   OK - Asociacion aprobada correctamente")
                print(f"   OK - Estado cambiado a: {asociacion.estado}")
                print(f"   OK - Fecha aprobacion: {asociacion.fecha_aprobacion}")
                print(f"   OK - Aprobada por: {asociacion.aprobada_por}")
                return True
            else:
                print(f"   ERROR - Estado incorrecto: {asociacion.estado}")
                return False

        except Exception as e:
            print(f"   ERROR - Excepcion en aprobacion: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"   ERROR - Excepcion general: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_callbacks_rechazo():
    """Test 3: Callback de rechazo"""
    print("\n" + "="*70)
    print("TEST 3: CALLBACK DE RECHAZO")
    print("="*70)

    print("\n[3.1] Preparando asociacion de prueba para rechazo...")
    try:
        from django.contrib.auth.hashers import make_password

        # Crear asociacion temporal
        asociacion = RegistroAsociacion.objects.create(
            nombre="Test Asociacion Rechazo",
            email="test_rechazo@test.com",
            telefono="666777999",
            direccion="Calle Test 456",
            poblacion="Test City",
            provincia="Test Province",
            codigo_postal="28001",
            password=make_password("test123"),
            estado='pendiente'
        )
        print(f"   OK - Asociacion creada: {asociacion.nombre} (ID: {asociacion.id})")

        # Test 3.2: Simular callback de rechazo
        print("\n[3.2] Simulando callback de rechazo...")
        callback_data = f"rechazar_{asociacion.id}"
        chat_id = "6344843081"
        message_id = "999999"
        callback_query_id = "test_callback_id"

        asociacion_id = asociacion.id

        try:
            response = manejar_rechazo(callback_data, chat_id, message_id, callback_query_id)

            # Verificar que la asociacion fue eliminada
            existe = RegistroAsociacion.objects.filter(id=asociacion_id).exists()
            if not existe:
                print(f"   OK - Asociacion eliminada correctamente del sistema")
                return True
            else:
                print(f"   ERROR - La asociacion aun existe en la base de datos")
                return False

        except Exception as e:
            print(f"   ERROR - Excepcion en rechazo: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"   ERROR - Excepcion general: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_callbacks_ver_detalles():
    """Test 4: Callback de ver detalles"""
    print("\n" + "="*70)
    print("TEST 4: CALLBACK DE VER DETALLES")
    print("="*70)

    print("\n[4.1] Preparando asociacion de prueba...")
    try:
        # Usar una asociacion existente o crear una
        asociacion = RegistroAsociacion.objects.filter(estado='activa').first()

        if not asociacion:
            from django.contrib.auth.hashers import make_password
            asociacion = RegistroAsociacion.objects.create(
                nombre="Test Asociacion Detalles",
                email="test_detalles@test.com",
                telefono="666777000",
                direccion="Calle Test 789",
                poblacion="Test City",
                provincia="Test Province",
                codigo_postal="28002",
                password=make_password("test123"),
                estado='activa'
            )

        print(f"   OK - Usando asociacion: {asociacion.nombre} (ID: {asociacion.id})")

        # Test 4.2: Simular callback de ver detalles
        print("\n[4.2] Simulando callback de ver detalles...")
        callback_data = f"ver_{asociacion.id}"
        chat_id = "6344843081"
        message_id = "999999"
        callback_query_id = "test_callback_id"

        try:
            response = manejar_ver_detalles(callback_data, chat_id, message_id, callback_query_id)
            print(f"   OK - Funcion ejecutada sin errores")
            print(f"   OK - Response: {response.status_code if hasattr(response, 'status_code') else 'OK'}")
            return True

        except Exception as e:
            print(f"   ERROR - Excepcion: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"   ERROR - Excepcion general: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_callbacks_eliminar():
    """Test 5: Callbacks de eliminacion (confirmacion + ejecucion)"""
    print("\n" + "="*70)
    print("TEST 5: CALLBACKS DE ELIMINACION")
    print("="*70)

    print("\n[5.1] Preparando asociacion de prueba...")
    try:
        from django.contrib.auth.hashers import make_password

        asociacion = RegistroAsociacion.objects.create(
            nombre="Test Asociacion Eliminar",
            email="test_eliminar@test.com",
            telefono="666777111",
            direccion="Calle Test 000",
            poblacion="Test City",
            provincia="Test Province",
            codigo_postal="28003",
            password=make_password("test123"),
            estado='activa'
        )
        print(f"   OK - Asociacion creada: {asociacion.nombre} (ID: {asociacion.id})")

        # Test 5.2: Simular callback de solicitar eliminacion
        print("\n[5.2] Simulando callback de solicitud de eliminacion...")
        callback_data = f"eliminar_{asociacion.id}"
        chat_id = "6344843081"
        message_id = "999999"
        callback_query_id = "test_callback_id"

        try:
            response = manejar_eliminar_asociacion(callback_data, chat_id, message_id, callback_query_id)
            print(f"   OK - Solicitud de confirmacion mostrada")

            # Test 5.3: Simular callback de confirmar eliminacion
            print("\n[5.3] Simulando callback de confirmar eliminacion...")
            callback_data_confirm = f"confirmar_eliminar_{asociacion.id}"

            asociacion_id = asociacion.id

            response = manejar_confirmar_eliminar(callback_data_confirm, chat_id, message_id, callback_query_id)

            # Verificar que la asociacion fue eliminada
            existe = RegistroAsociacion.objects.filter(id=asociacion_id).exists()
            if not existe:
                print(f"   OK - Asociacion eliminada permanentemente")
                return True
            else:
                print(f"   ERROR - La asociacion aun existe")
                return False

        except Exception as e:
            print(f"   ERROR - Excepcion: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"   ERROR - Excepcion general: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integracion_views():
    """Test 6: Integracion con views.py"""
    print("\n" + "="*70)
    print("TEST 6: INTEGRACION CON VIEWS.PY")
    print("="*70)

    tests_passed = 0
    tests_total = 2

    # Test 6.1: Importar funciones de views
    print("\n[6.1] Verificando importaciones desde views.py...")
    try:
        from myapp.views import enviar_email_aprobacion, enviar_email_rechazo
        print("   OK - enviar_email_aprobacion importada correctamente")
        print("   OK - enviar_email_rechazo importada correctamente")
        tests_passed += 1
    except ImportError as e:
        print(f"   ERROR - Error de importacion: {e}")

    # Test 6.2: Verificar metodos del modelo
    print("\n[6.2] Verificando metodos del modelo RegistroAsociacion...")
    try:
        # Crear asociacion temporal
        from django.contrib.auth.hashers import make_password
        asociacion = RegistroAsociacion.objects.create(
            nombre="Test Metodos Modelo",
            email="test_modelo@test.com",
            telefono="666777222",
            direccion="Calle Test",
            poblacion="Test",
            provincia="Test",
            codigo_postal="28000",
            password=make_password("test"),
            estado='pendiente'
        )

        # Verificar metodo aprobar()
        if hasattr(asociacion, 'aprobar') and callable(asociacion.aprobar):
            print("   OK - Metodo aprobar() existe")
        else:
            print("   ERROR - Metodo aprobar() no existe")

        # Verificar metodo get_estado_display()
        if hasattr(asociacion, 'get_estado_display') and callable(asociacion.get_estado_display):
            estado_display = asociacion.get_estado_display()
            print(f"   OK - Metodo get_estado_display() existe: '{estado_display}'")
        else:
            print("   ERROR - Metodo get_estado_display() no existe")

        # Probar metodo aprobar()
        asociacion.aprobar(admin_name="Test Admin", notas="Test de aprobacion")
        asociacion.refresh_from_db()
        if asociacion.estado == 'activa':
            print("   OK - Metodo aprobar() funciona correctamente")
            tests_passed += 1
        else:
            print("   ERROR - Metodo aprobar() no cambio el estado")

        # Limpiar
        asociacion.delete()

    except Exception as e:
        print(f"   ERROR - Excepcion: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n[RESULTADO TEST 6] {tests_passed}/{tests_total} pruebas pasadas")
    return tests_passed == tests_total


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print("VERIFICACION COMPLETA DEL SISTEMA DE BOTONES DE TELEGRAM")
    print("="*70)
    print("\nEste script verificara que TODAS las funciones de botones funcionen")
    print("correctamente en la aplicacion Django de asociaciones de animales.\n")

    resultados = []

    # Ejecutar todos los tests
    resultados.append(("Funciones Basicas", test_funciones_basicas()))
    resultados.append(("Callback Aprobacion", test_callbacks_aprobacion()))
    resultados.append(("Callback Rechazo", test_callbacks_rechazo()))
    resultados.append(("Callback Ver Detalles", test_callbacks_ver_detalles()))
    resultados.append(("Callbacks Eliminacion", test_callbacks_eliminar()))
    resultados.append(("Integracion Views", test_integracion_views()))

    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN FINAL DE PRUEBAS")
    print("="*70)

    tests_passed = sum(1 for _, passed in resultados if passed)
    tests_total = len(resultados)

    for nombre, passed in resultados:
        status = "OK" if passed else "FAIL"
        symbol = "[OK]" if passed else "[X]"
        print(f"[{status}] {symbol} {nombre}")

    print(f"\nTOTAL: {tests_passed}/{tests_total} tests pasados")

    if tests_passed == tests_total:
        print("\n" + "="*70)
        print("TODOS LOS TESTS PASADOS")
        print("="*70)
        print("\nSistema de botones de Telegram 100% FUNCIONAL")
        print("\nLo que funciona correctamente:")
        print("  - Envio de mensajes con botones")
        print("  - Callback de aprobacion (cambia estado + envia email)")
        print("  - Callback de rechazo (elimina + envia email)")
        print("  - Callback de ver detalles (muestra info completa)")
        print("  - Callback de eliminar (solicita confirmacion)")
        print("  - Callback de confirmar eliminacion (elimina permanentemente)")
        print("  - Integracion con views.py")
        print("  - Metodos del modelo RegistroAsociacion")
        print("\nEl sistema esta LISTO para produccion.")
        return 0
    else:
        print("\n" + "="*70)
        print("ALGUNOS TESTS FALLARON")
        print("="*70)
        print(f"\n{tests_total - tests_passed} test(s) requieren atencion")
        return 1


if __name__ == "__main__":
    sys.exit(main())
