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

    class Meta:
        db_table = 'asociaciones' #Para asegurarte de que pone de nombre asociaciones

    def __str__(self):
        return self.nombre

class CreacionAnimales(models.Model):
    asociacion = models.ForeignKey(RegistroAsociacion, on_delete=models.CASCADE, related_name='animales')
    nombre = models.CharField(max_length=100)
    tipo_de_animal = models.CharField(max_length=200)
    raza = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='animales/imagenes/', blank=True, null=True)
    video = models.FileField(upload_to='animales/videos/', blank=True, null=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=130)
    poblacion = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    adoptado = models.BooleanField(default=False)

    class Meta:
        db_table = 'Animales'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre