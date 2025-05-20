# forms.py
from django import forms
from .models import RegistroAsociacion
from .models import CreacionAnimales


class RegistroAsociacionForm(forms.ModelForm):
    class Meta:
        model = RegistroAsociacion
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm',
                'autocomplete': 'given-name',
                'id': 'name',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900  outline-1 outline-offset-1 outline-gray-300 placeholder:text-gray-400 sm:text-sm',
                'autocomplete': 'new-password',
                'id': 'password'

            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm/6',
                'autocomplete': 'email',
                'id': 'email',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm/6',
                'autocomplete': 'phone',
                'id': 'phone',
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm/6',
                'autocomplete': 'street-address',
                'id': 'direccion',
            }),
            'poblacion': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm/6',
                'autocomplete': 'address-level2',
                'id': 'poblacion',
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm/6',
                'autocomplete': 'address-level1',
                'id': 'provincia',
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 focus:outline-cyan-400 sm:text-sm/6',
                'autocomplete': 'postal-code',
                'id': 'codigo_postal',
            }),
        }

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 text-gray-900 placeholder:text-gray-400 sm:text-sm',
            'autocomplete': 'username',
            'id': 'username'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 text-gray-900 placeholder:text-gray-400 sm:text-sm',
            'autocomplete': 'current-password',
            'id': 'password'
        })
    )
    remember_me = forms.BooleanField(required=False, initial=False, label="Recuérdame")


class CreacionAnimalesForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': 'Nombre del animal'
        })
    )
    tipo_de_animal = forms.CharField(
        label='Tipo de animal',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': 'Ej: perro, gato...'
        })
    )
    imagen = forms.ImageField(
        label='Foto del animal',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-cyan-400 hover:file:bg-indigo-100'
        })
    )

    video = forms.FileField(
        label='Video del animal',
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-cyan-400 hover:file:bg-indigo-100'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': 'ejemplo@email.com'
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=130,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': '+34 600 123 456'
        })
    )
    poblacion = forms.CharField(
        label='Población',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': 'Ciudad o pueblo'
        })
    )
    provincia = forms.CharField(
        label='Provincia',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': 'Ej: Barcelona, Madrid...'
        })
    )
    codigo_postal = forms.CharField(
        label='Código Postal',
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
            'placeholder': '08001'
        })
    )

    # Guarda los datos como modelo
    def save(self):
        data = self.cleaned_data
        imagen = data.pop('imagen', None)
        video = data.pop('video', None)
        instancia = CreacionAnimales.objects.create(**data)
        if imagen:
            instancia.imagen = imagen
        if video:
            instancia.video = video
        instancia.save()
        return instancia