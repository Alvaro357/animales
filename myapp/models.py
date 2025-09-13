from django.db import models
from django.contrib.auth.models import User

class RegistroAsociacion(models.Model):
    nombre = models.CharField(max_length=50, unique=True) 
    password = models.CharField(max_length=130)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    direccion = models.CharField(max_length=200)
    poblacion = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='Fotos/', blank=True, null=True)

    class Meta:
        db_table = 'asociaciones' #Para asegurarte de que pone de nombre asociaciones

    def __str__(self):
        return self.nombre

class CreacionAnimales(models.Model):
    asociacion = models.ForeignKey(RegistroAsociacion, on_delete=models.CASCADE, related_name='animales')
    nombre = models.CharField(max_length=100)
    tipo_de_animal = models.CharField(max_length=200)
    raza = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='Fotos/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=130)
    poblacion = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    adoptado = models.BooleanField(default=False)
    color = models.CharField(
        max_length=100, 
        help_text="Color del animal (ej: marrón, negro, blanco, manchado, etc.)",
        blank=False,
        null=False,
        default="No especificado"  # Para animales existentes
    )

    class Meta:
        db_table = 'Animales'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    


class AnimalFavorito(models.Model):
    usuario_ip = models.GenericIPAddressField()  # Para usuarios no registrados
    asociacion = models.ForeignKey(RegistroAsociacion, on_delete=models.CASCADE, null=True, blank=True)  # Para asociaciones
    animal = models.ForeignKey(CreacionAnimales, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario_ip', 'animal']