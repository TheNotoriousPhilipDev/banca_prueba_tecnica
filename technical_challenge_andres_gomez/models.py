from django.db import models

from django.db import models

class Registro(models.Model):
    nombre_archivo = models.CharField(max_length=255, unique=True)  # Nombre del archivo
    url_archivo = models.URLField()  # URL del archivo en S3
    peso_archivo = models.CharField(max_length=50)  # Peso en KB o MB
    fecha_subida = models.DateTimeField(auto_now_add=True)  # Fecha de subida

    def __str__(self):
        return self.nombre_archivo

