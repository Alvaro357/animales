# management/commands/poblar_animales.py
# Crear esta estructura: myapp/management/commands/poblar_animales.py

import random
import hashlib
import requests
import io
import time
import cloudinary
import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from myapp.models import RegistroAsociacion, CreacionAnimales

class Command(BaseCommand):
    help = 'Poblar la base de datos con 500 animales variados con fotos en Cloudinary'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True
        )

    def descargar_y_subir_imagen(self, tipo_animal, indice):
        """Descarga una imagen de un servicio externo y la sube a Cloudinary"""
        seed = hashlib.md5(f"{tipo_animal}_{indice}_{random.randint(1,10000)}".encode()).hexdigest()[:8]

        # URLs de imágenes según el tipo de animal
        if tipo_animal == 'Perro':
            urls = [
                f"https://placedog.net/400/300?id={indice % 100 + random.randint(1, 50)}",
                f"https://loremflickr.com/400/300/dog?lock={indice + random.randint(1, 1000)}",
            ]
        elif tipo_animal == 'Gato':
            width = 400 + (indice % 10)
            height = 300 + (indice % 10)
            urls = [
                f"https://placekitten.com/{width}/{height}",
                f"https://loremflickr.com/400/300/cat?lock={indice + random.randint(1, 1000)}",
            ]
        elif tipo_animal == 'Conejo':
            urls = [
                f"https://loremflickr.com/400/300/rabbit?lock={indice + random.randint(1, 1000)}",
                f"https://loremflickr.com/400/300/bunny?lock={indice + random.randint(1, 1000)}",
            ]
        elif tipo_animal == 'Pájaro':
            urls = [
                f"https://loremflickr.com/400/300/bird?lock={indice + random.randint(1, 1000)}",
                f"https://loremflickr.com/400/300/parrot?lock={indice + random.randint(1, 1000)}",
            ]
        else:
            urls = [
                f"https://loremflickr.com/400/300/pet?lock={indice + random.randint(1, 1000)}",
                f"https://loremflickr.com/400/300/animal?lock={indice + random.randint(1, 1000)}",
            ]

        # Intentar descargar y subir la imagen
        for url in urls:
            try:
                # Descargar la imagen
                response = requests.get(url, timeout=15, allow_redirects=True)
                if response.status_code == 200 and len(response.content) > 1000:
                    # Subir a Cloudinary directamente desde la URL
                    result = cloudinary.uploader.upload(
                        url,
                        folder=f"animales/fotos/{tipo_animal.lower()}",
                        public_id=f"{tipo_animal.lower()}_{indice}_{seed}",
                        resource_type="image",
                        overwrite=True
                    )
                    return result.get('secure_url')
            except Exception as e:
                continue

        # Si falla, usar un placeholder de Cloudinary
        try:
            placeholder_url = f"https://res.cloudinary.com/demo/image/upload/w_400,h_300,c_fill/sample.jpg"
            result = cloudinary.uploader.upload(
                placeholder_url,
                folder=f"animales/fotos/{tipo_animal.lower()}",
                public_id=f"{tipo_animal.lower()}_{indice}_{seed}_placeholder",
                resource_type="image",
                overwrite=True
            )
            return result.get('secure_url')
        except:
            return None

    def handle(self, *args, **options):
        # Verificar que hay asociaciones
        asociaciones = list(RegistroAsociacion.objects.filter(estado__in=['activa', 'pendiente']))
        if not asociaciones:
            self.stdout.write(self.style.ERROR('No hay asociaciones disponibles. Crea al menos una asociación primero.'))
            return

        # Datos para generar animales realistas
        nombres_perro = [
            'Max', 'Bella', 'Charlie', 'Lucy', 'Cooper', 'Luna', 'Buddy', 'Daisy', 'Rocky', 'Molly',
            'Duke', 'Sophie', 'Bear', 'Sadie', 'Tucker', 'Chloe', 'Jake', 'Zoe', 'Rex', 'Maya',
            'Leo', 'Mia', 'Zeus', 'Nala', 'Oscar', 'Emma', 'Toby', 'Lola', 'Rusty', 'Ruby',
            'Bruno', 'Coco', 'Simba', 'Kira', 'Thor', 'Nina', 'Ace', 'Dora', 'Storm', 'Vera',
            'Chico', 'Canela', 'Paco', 'Estrella', 'Rambo', 'Princesa', 'Firulais', 'Negra'
        ]

        nombres_gato = [
            'Oliver', 'Luna', 'Milo', 'Bella', 'Charlie', 'Chloe', 'Simba', 'Nala', 'Leo', 'Lily',
            'Max', 'Sophie', 'Felix', 'Mia', 'Tiger', 'Zoe', 'Oscar', 'Emma', 'Shadow', 'Ruby',
            'Smokey', 'Princess', 'Oreo', 'Midnight', 'Whiskers', 'Angel', 'Boots', 'Patches',
            'Garfield', 'Misty', 'Tigger', 'Ginger', 'Salem', 'Snowball', 'Mittens', 'Pepper',
            'Michi', 'Pelusa', 'Gatito', 'Blanquita', 'Negro', 'Copito', 'Manchas', 'Rayado'
        ]

        nombres_otros = [
            'Bunny', 'Coco', 'Snowball', 'Oreo', 'Pepper', 'Cotton', 'Hazel', 'Honey', 'Ginger', 'Peanut',
            'Tweety', 'Sunny', 'Sky', 'Cloud', 'Storm', 'Rainbow', 'Flash', 'Bolt', 'Spark', 'Star',
            'Nibbles', 'Whiskers', 'Fluffy', 'Marshmallow', 'Caramel', 'Chocolate', 'Vanilla', 'Sugar'
        ]

        razas_perro = [
            'Labrador', 'Golden Retriever', 'Pastor Alemán', 'Bulldog Francés', 'Bulldog Inglés',
            'Beagle', 'Poodle', 'Rottweiler', 'Yorkshire Terrier', 'Chihuahua', 'Boxer', 'Husky',
            'Border Collie', 'Cocker Spaniel', 'Schnauzer', 'Mastín', 'Galgo', 'Podenco',
            'Mestizo', 'Cruce', 'Sin raza definida', 'Mix', 'Callejero'
        ]

        razas_gato = [
            'Persa', 'Siamés', 'Maine Coon', 'Británico de Pelo Corto', 'Ragdoll', 'Bengal',
            'Abisinio', 'Ruso Azul', 'Sphynx', 'Scottish Fold', 'Norwegian Forest',
            'Común Europeo', 'Mestizo', 'Callejero', 'Sin raza definida', 'Cruce', 'Doméstico'
        ]

        razas_otros = [
            'Holandés', 'Enano', 'Gigante', 'Angora', 'Rex', 'Cabeza de León',  # Conejos
            'Canario', 'Periquito', 'Cotorra', 'Ninfa', 'Agapornis', 'Jilguero',  # Pájaros
            'Hámster Dorado', 'Hámster Ruso', 'Cobaya', 'Chinchilla', 'Hurón', 'Reptil'  # Otros
        ]

        colores = [
            'Negro', 'Blanco', 'Marrón', 'Gris', 'Dorado', 'Rubio', 'Rojizo', 'Chocolate',
            'Crema', 'Canela', 'Tricolor', 'Bicolor', 'Atigrado', 'Manchado', 'Moteado',
            'Negro y blanco', 'Marrón y blanco', 'Gris y blanco', 'Dorado y blanco'
        ]

        provincias_es = [
            'Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Málaga', 'Bilbao', 'Zaragoza',
            'Murcia', 'Palma', 'Las Palmas', 'Córdoba', 'Valladolid', 'Vigo', 'Gijón',
            'Alicante', 'Granada', 'Santander', 'Pamplona', 'Toledo', 'Burgos', 'Salamanca',
            'Albacete', 'Cáceres', 'Badajoz', 'Jaén', 'Huelva', 'Ourense', 'León',
            'Tarragona', 'Castellón', 'Almería', 'Cádiz', 'Lugo', 'Ávila', 'Cuenca'
        ]

        poblaciones = {
            'Madrid': ['Madrid', 'Móstoles', 'Alcalá de Henares', 'Fuenlabrada', 'Leganés'],
            'Barcelona': ['Barcelona', 'Hospitalet', 'Terrassa', 'Badalona', 'Sabadell'],
            'Valencia': ['Valencia', 'Alicante', 'Elche', 'Castellón', 'Torrent'],
            'Sevilla': ['Sevilla', 'Jerez', 'Dos Hermanas', 'Alcalá de Guadaíra', 'Utrera'],
            'Málaga': ['Málaga', 'Marbella', 'Fuengirola', 'Torremolinos', 'Benalmádena']
        }

        descripciones_templates = [
            "{nombre} es un {tipo} muy {adjetivo1} y {adjetivo2}. Le encanta {actividad} y busca una familia que le dé mucho amor.",
            "Conoce a {nombre}, un adorable {tipo} de {edad}. Es {personalidad} y se lleva bien con {compatible}.",
            "{nombre} es un {tipo} {adjetivo1} que necesita un hogar. Es perfecto para familias con {familia_tipo}.",
            "Este precioso {tipo} llamado {nombre} está buscando su hogar definitivo. Es {personalidad} y muy {adjetivo2}.",
            "{nombre} es un {tipo} rescatado que busca una segunda oportunidad. Le gusta {actividad} y es muy {adjetivo1}."
        ]

        adjetivos1 = ['cariñoso', 'juguetón', 'tranquilo', 'activo', 'dulce', 'noble', 'inteligente', 'fiel']
        adjetivos2 = ['sociable', 'obediente', 'mimoso', 'alegre', 'paciente', 'protector', 'curioso', 'amoroso']
        personalidades = ['muy sociable', 'algo tímido pero cariñoso', 'extremadamente juguetón', 'muy tranquilo', 'super activo']
        actividades = ['jugar en el parque', 'dar paseos', 'jugar con pelotas', 'recibir caricias', 'correr al aire libre']
        compatibles = ['niños', 'otros animales', 'personas mayores', 'toda la familia', 'gatos', 'perros']
        familia_tipos = ['niños', 'experiencia', 'mucho tiempo', 'jardín', 'paciencia']
        edades = ['pocos meses', '1 año', '2 años', '3 años', '4 años', '5 años', 'edad adulta']

        # Contadores para distribución
        total_animales = 500
        perros_cantidad = int(total_animales * 0.40)  # 40% = 200
        gatos_cantidad = int(total_animales * 0.35)   # 35% = 175
        otros_cantidad = total_animales - perros_cantidad - gatos_cantidad  # 25% = 125

        self.stdout.write(f'Creando {perros_cantidad} perros, {gatos_cantidad} gatos y {otros_cantidad} otros animales...')

        animales_creados = 0

        # Crear perros
        for i in range(perros_cantidad):
            nombre = random.choice(nombres_perro)
            asociacion = random.choice(asociaciones)
            provincia = random.choice(provincias_es)
            poblacion = poblaciones.get(provincia, [provincia])[0] if provincia in poblaciones else provincia
            
            descripcion = random.choice(descripciones_templates).format(
                nombre=nombre,
                tipo='perro',
                adjetivo1=random.choice(adjetivos1),
                adjetivo2=random.choice(adjetivos2),
                actividad=random.choice(actividades),
                personalidad=random.choice(personalidades),
                edad=random.choice(edades),
                compatible=random.choice(compatibles),
                familia_tipo=random.choice(familia_tipos)
            )

            # Descargar y subir imagen a Cloudinary
            imagen_url = self.descargar_y_subir_imagen('Perro', i)

            animal = CreacionAnimales.objects.create(
                asociacion=asociacion,
                nombre=f"{nombre} {random.randint(1, 999)}" if random.random() < 0.3 else nombre,
                tipo_de_animal='Perro',
                raza=random.choice(razas_perro),
                color=random.choice(colores),
                email=asociacion.email,
                telefono=asociacion.telefono,
                poblacion=poblacion,
                provincia=provincia,
                codigo_postal=f"{random.randint(10000, 52999)}",
                descripcion=descripcion,
                adoptado=random.random() < 0.15,  # 15% adoptados
                imagen=imagen_url if imagen_url else ''
            )
            animales_creados += 1

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Creados {i + 1} perros (subidos a Cloudinary)...')

        # Crear gatos
        for i in range(gatos_cantidad):
            nombre = random.choice(nombres_gato)
            asociacion = random.choice(asociaciones)
            provincia = random.choice(provincias_es)
            poblacion = poblaciones.get(provincia, [provincia])[0] if provincia in poblaciones else provincia
            
            descripcion = random.choice(descripciones_templates).format(
                nombre=nombre,
                tipo='gato',
                adjetivo1=random.choice(adjetivos1),
                adjetivo2=random.choice(adjetivos2),
                actividad=random.choice(['dormir al sol', 'jugar con ratones de juguete', 'explorar', 'ronronear']),
                personalidad=random.choice(personalidades),
                edad=random.choice(edades),
                compatible=random.choice(compatibles),
                familia_tipo=random.choice(familia_tipos)
            )

            # Descargar y subir imagen a Cloudinary
            imagen_url = self.descargar_y_subir_imagen('Gato', i)

            animal = CreacionAnimales.objects.create(
                asociacion=asociacion,
                nombre=f"{nombre} {random.randint(1, 999)}" if random.random() < 0.3 else nombre,
                tipo_de_animal='Gato',
                raza=random.choice(razas_gato),
                color=random.choice(colores),
                email=asociacion.email,
                telefono=asociacion.telefono,
                poblacion=poblacion,
                provincia=provincia,
                codigo_postal=f"{random.randint(10000, 52999)}",
                descripcion=descripcion,
                adoptado=random.random() < 0.12,  # 12% adoptados
                imagen=imagen_url if imagen_url else ''
            )
            animales_creados += 1

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Creados {i + 1} gatos (subidos a Cloudinary)...')

        # Crear otros animales
        tipos_otros = ['Conejo', 'Pájaro', 'Otros']
        for i in range(otros_cantidad):
            tipo = random.choice(tipos_otros)
            if tipo == 'Conejo':
                nombres_pool = ['Copito', 'Pelusa', 'Blanquito', 'Orejitas', 'Saltarín'] + nombres_otros[:15]
            elif tipo == 'Pájaro':
                nombres_pool = ['Pío', 'Cantor', 'Plumitas', 'Colorín', 'Melodía'] + nombres_otros[10:20]
            else:
                nombres_pool = nombres_otros

            nombre = random.choice(nombres_pool)
            asociacion = random.choice(asociaciones)
            provincia = random.choice(provincias_es)
            poblacion = poblaciones.get(provincia, [provincia])[0] if provincia in poblaciones else provincia
            
            descripcion = random.choice(descripciones_templates).format(
                nombre=nombre,
                tipo=tipo.lower(),
                adjetivo1=random.choice(adjetivos1),
                adjetivo2=random.choice(adjetivos2),
                actividad=random.choice(['explorar', 'jugar', 'socializar', 'ejercitarse']),
                personalidad=random.choice(personalidades),
                edad=random.choice(edades),
                compatible=random.choice(compatibles),
                familia_tipo=random.choice(familia_tipos)
            )

            # Descargar y subir imagen a Cloudinary
            imagen_url = self.descargar_y_subir_imagen(tipo, i)

            animal = CreacionAnimales.objects.create(
                asociacion=asociacion,
                nombre=f"{nombre} {random.randint(1, 999)}" if random.random() < 0.3 else nombre,
                tipo_de_animal=tipo,
                raza=random.choice(razas_otros),
                color=random.choice(colores),
                email=asociacion.email,
                telefono=asociacion.telefono,
                poblacion=poblacion,
                provincia=provincia,
                codigo_postal=f"{random.randint(10000, 52999)}",
                descripcion=descripcion,
                adoptado=random.random() < 0.10,  # 10% adoptados
                imagen=imagen_url if imagen_url else ''
            )
            animales_creados += 1

            if (i + 1) % 10 == 0:
                self.stdout.write(f'  Creados {i + 1} otros animales (subidos a Cloudinary)...')

        self.stdout.write(
            self.style.SUCCESS(
                f'¡Éxito! Se han creado {animales_creados} animales:\n'
                f'- {perros_cantidad} perros\n'
                f'- {gatos_cantidad} gatos\n'
                f'- {otros_cantidad} otros animales\n'
                f'Distribuidos entre {len(asociaciones)} asociaciones'
            )
        )

        # Estadísticas finales
        total_db = CreacionAnimales.objects.count()
        adoptados = CreacionAnimales.objects.filter(adoptado=True).count()
        disponibles = total_db - adoptados
        
        self.stdout.write(
            self.style.WARNING(
                f'\nEstadísticas totales en la BD:\n'
                f'- Total animales: {total_db}\n'
                f'- Disponibles: {disponibles}\n'
                f'- Adoptados: {adoptados}'
            )
        )