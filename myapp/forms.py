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


class CreacionAnimalesForm(forms.ModelForm):
    class Meta:
        model = CreacionAnimales
        fields = ['nombre', 'tipo_de_animal', 'raza', 'imagen', 'video', 
                 'email', 'telefono', 'poblacion', 'provincia', 
                 'codigo_postal', 'descripcion', 'adoptado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': 'Nombre del animal'
            }),
            'tipo_de_animal': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm'
            }),
            'raza': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': 'Ej: pastor alemán, border collie...'
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-cyan-400 hover:file:bg-indigo-100'
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-cyan-400 hover:file:bg-indigo-100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': 'ejemplo@email.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': '+34 600 123 456'
            }),
            'poblacion': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': 'Ciudad o pueblo'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': 'Ej: Barcelona, Madrid...'
            }),
            'codigo_postal': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': '08001'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:border-cyan-400 sm:text-sm',
                'placeholder': 'Descripción del animal',
                'rows': 4
            }),
            'adoptado': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-cyan-400 focus:ring-cyan-400 border-gray-300 rounded'
            })
        }
    
    def __init__(self, *args, **kwargs):
        asociacion = kwargs.pop('asociacion', None)
        super().__init__(*args, **kwargs)
        
        if asociacion:
            # Autocompletar campos con datos de la asociación
            self.fields['email'].initial = asociacion.email
            self.fields['telefono'].initial = asociacion.telefono
            self.fields['poblacion'].initial = asociacion.poblacion
            self.fields['provincia'].initial = asociacion.provincia
            self.fields['codigo_postal'].initial = asociacion.codigo_postal

    # Guarda los datos como modelo
def save(self, commit=True):
    data = self.cleaned_data
    imagen = data.pop('imagen', None)
    video = data.pop('video', None)
    instancia = CreacionAnimales(**data)  # todavía no se guarda en la base de datos

    if imagen:
        instancia.imagen = imagen
    if video:
        instancia.video = video

    if commit:
        instancia.save()

    return instancia
