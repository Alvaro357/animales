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
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                asociacion = RegistroAsociacion.objects.get(nombre=username)
                if check_password(password, asociacion.password):
                    response = redirect('Inicio')
                    max_age = 86400  # 24 horas en segundos
                    response.set_cookie('asociacion_id', asociacion.id, max_age=max_age)
                    
                    # Guardamos en la sesión
                    request.session['esta_logueado'] = True
                    request.session['asociacion_nombre'] = asociacion.nombre
                    return response
                else:
                    form.add_error(None, 'Contraseña incorrecta.')
            except RegistroAsociacion.DoesNotExist:
                form.add_error(None, 'No existe una asociación con ese nombre.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


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
                    response = redirect('Inicio')
                   
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
    response = redirect('Inicio')

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


def session_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('esta_logueado'):
            return view_func(request, *args, **kwargs)
        return redirect('login')  # o la URL que uses para login
    return wrapper

@session_login_required
def crear_animal(request):
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    
    if request.method == 'POST':
        form = CreacionAnimalesForm(request.POST, request.FILES, asociacion=asociacion)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.asociacion = asociacion  # Asignar la asociación
            animal.save()
            return redirect('Inicio')
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
        form = CreacionAnimalesForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            return redirect('Inicio')
    else:
        form = CreacionAnimalesForm(instance=animal)
    
    return render(request, 'editar_animal.html', {
        'form': form,
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

@session_login_required
def toggle_adopcion(request, animal_id):
    asociacion_id = request.COOKIES.get('asociacion_id')
    asociacion = get_object_or_404(RegistroAsociacion, id=asociacion_id)
    animal = get_object_or_404(CreacionAnimales, id=animal_id, asociacion=asociacion)
    
    animal.adoptado = not animal.adoptado
    animal.save()
    
    return redirect('Inicio')


def mis_animales(request):
    if not request.session.get('esta_logueado'):
        return redirect('login')
    
    asociacion_id = request.COOKIES.get('asociacion_id')
    mis_animales = CreacionAnimales.objects.filter(asociacion_id=asociacion_id)
    
    return render(request, 'mis_animales.html', {
        'mis_animales': mis_animales,
        'asociacion_nombre': request.session.get('asociacion_nombre')
    })