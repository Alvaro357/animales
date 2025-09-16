from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail  # Enviar correos
from django.contrib.auth.decorators import login_required # Para exigir el login poner "@login_required"
from functools import wraps
from .forms import RegistroAsociacionForm, LoginForm, CreacionAnimalesForm
from .models import RegistroAsociacion, CreacionAnimales
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json


def session_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('esta_logueado'):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper


# Toggle de adopción AJAX
@session_login_required
def toggle_adopcion_ajax(request, animal_id):
    if request.method == 'POST':
        try:
            # Obtener la asociación logueada
            asociacion_id = request.COOKIES.get('asociacion_id')
            if not asociacion_id:
                return JsonResponse({'error': 'Sesión no válida'}, status=401)
                
            asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
            
            # Buscar el animal que pertenece a esta asociación
            animal = CreacionAnimales.objects.get(id=animal_id, asociacion=asociacion)
            animal.adoptado = not animal.adoptado
            animal.save()
            
            return JsonResponse({'adoptado': animal.adoptado})
        except CreacionAnimales.DoesNotExist:
            return JsonResponse({'error': 'Animal no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# Registro
def registro_asociacion(request):
    if request.method == 'POST':
        form = RegistroAsociacionForm(request.POST, request.FILES)
        if form.is_valid():
            asociacion = form.save(commit=False)
            password = form.cleaned_data['password']
            asociacion.password = make_password(password)
            asociacion.save()

            send_mail(
                subject='🆕 Nueva asociación registrada',
                message=f'Se ha registrado una nueva asociación:\n\n'
                        f'Nombre: {asociacion.nombre}\n'
                        f'Email: {asociacion.email}\n'
                        f'Teléfono: {asociacion.telefono}\n'
                        f'Dirección: {asociacion.direccion}, {asociacion.poblacion}, {asociacion.provincia}, {asociacion.codigo_postal}',
                from_email=None,
                recipient_list=['alvaro_m_a@icloud.com'],
                fail_silently=False,
            )
            return redirect('Inicio')
        else:
            # Agregar esto para debuggear errores del formulario
            print("Errores del formulario:", form.errors)
    else:
        form = RegistroAsociacionForm()

    return render(request, 'registro_asociacion.html', {'form': form})


# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember_me')
            try:
                asociacion = RegistroAsociacion.objects.get(nombre=username)

                # Verifica la contraseña
                if check_password(password, asociacion.password):
                    # Guardamos la cookie y la sesión si todo es correcto
                    response = redirect('inicio')
                   
                    max_age = 86400  # 24 horas en segundos
                    response.set_cookie('asociacion_id', asociacion.id, max_age=max_age)
                   
                    # Guardamos en la sesión
                    request.session['esta_logueado'] = True
                    request.session['asociacion_nombre'] = asociacion.nombre
                    print(response)
                    return response
                else:
                    form.add_error(None, 'Contraseña incorrecta.')
            except RegistroAsociacion.DoesNotExist:
                form.add_error(None, 'No existe una asociación con ese nombre.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


#Comprobación
def comprobacion(request):
    asociacion_id = request.COOKIES.get('asociacion_id')

    if asociacion_id:
        try:
            asociacion = RegistroAsociacion.objects.get(id=asociacion_id)

            # Aseguramos que se guarda en la sesión (por si no estaba)
            request.session['esta_logueado'] = True
            request.session['asociacion_nombre'] = asociacion.nombre

            return render(request, 'home.html', {
                'asociacion': asociacion,
                'logueado': True
            })
        except RegistroAsociacion.DoesNotExist:
            pass

    # Si no hay cookie válida, eliminamos la sesión también por si acaso
    request.session.flush()
    return redirect('login')


#logout
def logout_view(request):
    response = redirect('inicio')

    # Eliminamos la cookie de la sesión
    response.delete_cookie('asociacion_id')

    # Limpiamos la sesión
    request.session.flush()

    return response


#Inicio
def Inicio(request):
    # Verificamos si hay una cookie de la asociación
    animales = CreacionAnimales.objects.all()
    asociacion_id = request.COOKIES.get('asociacion_id')
    mis_animales = None
    
    if asociacion_id:
        try:
            asociacion = RegistroAsociacion.objects.get(id=asociacion_id)
            mis_animales = CreacionAnimales.objects.filter(asociacion=asociacion)
            
            return render(request, 'index.html', {
                'asociacion': asociacion,
                'logueado': True,
                'animales': animales,
                'mis_animales': mis_animales  # Animales de la asociación logueada
            })
        except RegistroAsociacion.DoesNotExist:
            pass
            
    return render(request, 'index.html', {
        'logueado': False, 
        'animales': animales,
        'mis_animales': None
    })


@session_login_required
def crear_animal(request):
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    
    if request.method == 'POST':
        # Debug: imprimir todos los datos recibidos
        print("POST data:", request.POST)
        
        form = CreacionAnimalesForm(request.POST, request.FILES, asociacion=asociacion)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.asociacion = asociacion
            
            # PROCESAR COLOR MANUALMENTE
            color_predefinido = request.POST.get('color_predefinido', '')
            color_personalizado = request.POST.get('color_personalizado', '')
            color_final = request.POST.get('color', '')
            
            # Lógica para determinar el color final
            if color_predefinido and color_predefinido != 'Otro':
                animal.color = color_predefinido
            elif color_predefinido == 'Otro' and color_personalizado:
                animal.color = color_personalizado
            elif color_final:
                animal.color = color_final
            else:
                animal.color = "No especificado"
            
            print(f"Color final asignado: {animal.color}")
            animal.save()
            return redirect('mis_animales')
        else:
            print("Errores del formulario:", form.errors)
    else:
        form = CreacionAnimalesForm(asociacion=asociacion)
    
    return render(request, 'creacion_de_animales.html', {
        'form': form,
        'asociacion': asociacion
    })


def pagina_inicio(request):
    animales = CreacionAnimales.objects.all()
    return render(request, 'inicio.html', {'animales': animales})


def vista_animal(request, animal_id):
    animal = get_object_or_404(CreacionAnimales, id=animal_id)
    return render(request, 'vista_animal.html', {'animal': animal})


@session_login_required
def lista_animales_asociacion(request):
    # Obtener la asociación logueada
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    
    # Obtener solo los animales de esta asociación
    animales = CreacionAnimales.objects.filter(asociacion=asociacion)
    
    return render(request, 'vista_animal.html', {
        'animales': animales,
        'asociacion': asociacion
    })


@session_login_required
def editar_animal(request, animal_id):
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    animal = get_object_or_404(CreacionAnimales, id=animal_id, asociacion=asociacion)
    
    if request.method == 'POST':
        # IMPORTANTE: Procesar el color igual que en crear_animal
        color_predefinido = request.POST.get('color_predefinido', '')
        color_personalizado = request.POST.get('color_personalizado', '')
        color_final = request.POST.get('color', '')
        
        # Lógica para determinar el color final
        if color_predefinido and color_predefinido != 'Otro':
            nuevo_color = color_predefinido
        elif color_predefinido == 'Otro' and color_personalizado:
            nuevo_color = color_personalizado
        elif color_final:
            nuevo_color = color_final
        else:
            nuevo_color = "No especificado"
        
        # Actualizar todos los campos
        animal.nombre = request.POST.get('nombre')
        animal.tipo_de_animal = request.POST.get('tipo_de_animal')
        animal.raza = request.POST.get('raza')
        animal.color = nuevo_color  # ← ESTO ES LO IMPORTANTE
        animal.email = request.POST.get('email')
        animal.telefono = request.POST.get('telefono')
        animal.poblacion = request.POST.get('poblacion')
        animal.provincia = request.POST.get('provincia')
        animal.codigo_postal = request.POST.get('codigo_postal')
        animal.descripcion = request.POST.get('descripcion')
        
        # Manejar archivos
        if 'imagen' in request.FILES:
            animal.imagen = request.FILES['imagen']
        if 'video' in request.FILES:
            animal.video = request.FILES['video']
        
        animal.save()
        return redirect('mis_animales')
    
    return render(request, 'editar_animal.html', {  # ← Asegúrate de que apunte al template correcto
        'animal': animal,
        'asociacion': asociacion
    })


@session_login_required
def eliminar_animal(request, animal_id):
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    animal = get_object_or_404(CreacionAnimales, id=animal_id, asociacion=asociacion)
    
    if request.method == 'POST':
        animal.delete()
        return redirect('mis_animales')
    
    return render(request, 'confirmar_eliminar.html', {
        'animal': animal,
        'asociacion': asociacion
    })


def mis_animales(request):
    if not request.session.get('esta_logueado'):
        return redirect('login')
    
    asociacion_id = request.COOKIES.get('asociacion_id')
    mis_animales = CreacionAnimales.objects.filter(asociacion_id=asociacion_id)
    
    return render(request, 'mis_animales.html', {
        'mis_animales': mis_animales,
        'asociacion_nombre': request.session.get('asociacion_nombre')
    })


# Vista para favoritos
def mis_favoritos(request):
    """
    Vista para mostrar la página de favoritos del usuario.
    Pasa todos los animales disponibles para que JavaScript pueda filtrar
    los favoritos desde localStorage.
    """
    # Obtener todos los animales disponibles
    animales = CreacionAnimales.objects.all().order_by('-id')
    
    context = {
        'animales': animales,
        'page_title': 'Mis Favoritos - Adopta'
    }
    
    return render(request, 'mis_favoritos.html', context)


def obtener_animales_favoritos(request):
    """
    Vista AJAX para obtener solo los animales que están en favoritos.
    Recibe una lista de IDs desde el frontend y devuelve los datos de esos animales.
    """
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            ids_favoritos = data.get('favoritos', [])
            
            # Filtrar animales por los IDs favoritos
            animales_favoritos = CreacionAnimales.objects.filter(id__in=ids_favoritos)
            
            # Convertir a lista de diccionarios
            animales_data = []
            for animal in animales_favoritos:
                animal_dict = {
                    'id': animal.id,
                    'nombre': animal.nombre,
                    'tipo': animal.tipo_de_animal,
                    'raza': animal.raza,
                    'email': animal.email,
                    'telefono': animal.telefono,
                    'poblacion': animal.poblacion,
                    'provincia': animal.provincia,
                    'descripcion': animal.descripcion,
                    'imagen': animal.imagen.url if animal.imagen else None,
                }
                animales_data.append(animal_dict)
            
            return JsonResponse({
                'success': True,
                'animales': animales_data,
                'total': len(animales_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def buscador_avanzado(request):
    """
    Vista para mostrar la página del buscador avanzado.
    Obtiene todas las opciones disponibles para los filtros.
    """
    import json
    
    # Separar datos por tipo de animal para mayor precisión
    datos_por_tipo = {
        'perros': {
            'razas': list(CreacionAnimales.objects.filter(
                tipo_de_animal__icontains='perro'
            ).values_list('raza', flat=True).distinct().order_by('raza')),
            'colores': list(CreacionAnimales.objects.filter(
                tipo_de_animal__icontains='perro'
            ).values_list('color', flat=True).distinct().order_by('color')),
            'provincias': list(CreacionAnimales.objects.filter(
                tipo_de_animal__icontains='perro'
            ).values_list('provincia', flat=True).distinct().order_by('provincia'))
        },
        'gatos': {
            'razas': list(CreacionAnimales.objects.filter(
                tipo_de_animal__icontains='gato'
            ).values_list('raza', flat=True).distinct().order_by('raza')),
            'colores': list(CreacionAnimales.objects.filter(
                tipo_de_animal__icontains='gato'
            ).values_list('color', flat=True).distinct().order_by('color')),
            'provincias': list(CreacionAnimales.objects.filter(
                tipo_de_animal__icontains='gato'
            ).values_list('provincia', flat=True).distinct().order_by('provincia'))
        },
        'otros': {
            'tipos': list(CreacionAnimales.objects.exclude(
                tipo_de_animal__icontains='perro'
            ).exclude(
                tipo_de_animal__icontains='gato'
            ).values_list('tipo_de_animal', flat=True).distinct().order_by('tipo_de_animal')),
            'colores': list(CreacionAnimales.objects.exclude(
                tipo_de_animal__icontains='perro'
            ).exclude(
                tipo_de_animal__icontains='gato'
            ).values_list('color', flat=True).distinct().order_by('color')),
            'provincias': list(CreacionAnimales.objects.exclude(
                tipo_de_animal__icontains='perro'
            ).exclude(
                tipo_de_animal__icontains='gato'
            ).values_list('provincia', flat=True).distinct().order_by('provincia'))
        }
    }
    
    # Limpiar datos nulos/vacíos
    for categoria in datos_por_tipo.values():
        for key, lista in categoria.items():
            categoria[key] = [item for item in lista if item and str(item).strip()]
    
    # Obtener valores únicos para los filtros generales (por si los necesitas)
    razas_disponibles = CreacionAnimales.objects.values_list('raza', flat=True).distinct().order_by('raza')
    provincias_disponibles = CreacionAnimales.objects.values_list('provincia', flat=True).distinct().order_by('provincia')
    colores_disponibles = CreacionAnimales.objects.values_list('color', flat=True).distinct().order_by('color')
    tipos_disponibles = CreacionAnimales.objects.values_list('tipo_de_animal', flat=True).distinct().order_by('tipo_de_animal')
    
    # Filtrar valores vacíos o nulos
    razas_disponibles = [raza for raza in razas_disponibles if raza and raza.strip()]
    provincias_disponibles = [provincia for provincia in provincias_disponibles if provincia and provincia.strip()]
    colores_disponibles = [color for color in colores_disponibles if color and color.strip()]
    tipos_disponibles = [tipo for tipo in tipos_disponibles if tipo and tipo.strip()]
    
    # Convertir a JSON para pasar al template
    datos_por_tipo_json = json.dumps(datos_por_tipo, ensure_ascii=False)
    
    context = {
        'razas_disponibles': razas_disponibles,
        'provincias_disponibles': provincias_disponibles,
        'colores_disponibles': colores_disponibles,
        'tipos_disponibles': tipos_disponibles,
        'datos_por_tipo': datos_por_tipo_json,  # JSON string para JavaScript
        'datos_debug': datos_por_tipo,  # Datos raw para debug si los necesitas
    }
    
    return render(request, 'buscador_avanzado.html', context)


def resultados_busqueda(request):
    """
    Vista para mostrar los resultados de la búsqueda avanzada.
    Filtra los animales según los criterios seleccionados.
    """
    # Obtener parámetros de búsqueda
    raza = request.GET.get('raza', '')
    ubicacion = request.GET.get('ubicacion', '')
    color = request.GET.get('color', '')
    tipo = request.GET.get('tipo', '')
    
    # Empezar con todos los animales
    animales = CreacionAnimales.objects.all()
    
    # Aplicar filtros si existen
    if raza:
        animales = animales.filter(raza__icontains=raza)
    
    if ubicacion:
        animales = animales.filter(provincia__icontains=ubicacion)
    
    if color:
        animales = animales.filter(color__icontains=color)
    
    if tipo:
        animales = animales.filter(tipo_de_animal__icontains=tipo)
    
    # Contar resultados
    total_resultados = animales.count()
    
    # Crear mensaje de búsqueda
    filtros_aplicados = []
    if raza:
        filtros_aplicados.append(f"raza: {raza}")
    if ubicacion:
        filtros_aplicados.append(f"ubicación: {ubicacion}")
    if color:
        filtros_aplicados.append(f"color: {color}")
    if tipo:
        filtros_aplicados.append(f"tipo: {tipo}")
    
    mensaje_busqueda = f"Resultados para: {', '.join(filtros_aplicados)}" if filtros_aplicados else "Todos los animales"
    
    context = {
        'animales': animales,
        'total_resultados': total_resultados,
        'mensaje_busqueda': mensaje_busqueda,
        'filtros': {
            'raza': raza,
            'ubicacion': ubicacion,
            'color': color,
            'tipo': tipo,
        }
    }
    
    return render(request, 'resultados_busqueda.html', context)

