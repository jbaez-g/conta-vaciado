from django.db import models
from django.contrib.auth.models import User

# 1. EL PADRE (Representa la "Carpeta" o el evento de carga)
class ProcesoVaciado(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre_archivo_original = models.CharField(max_length=255)
    
    # Datos generales para mostrar en la lista sin consultar los hijos
    rut_cliente = models.CharField(max_length=20)
    nombre_cliente = models.CharField(max_length=150)
    cantidad_periodos = models.IntegerField(default=0) # Ej: 12 meses

    def __str__(self):
        return f"{self.nombre_cliente} ({self.fecha_creacion})"

# 2. EL HIJO (Cada mes individual que venía en el PDF)
class DetalleF29(models.Model):
    proceso = models.ForeignKey(ProcesoVaciado, related_name='detalles', on_delete=models.CASCADE)
    
    anio = models.IntegerField()
    mes = models.CharField(max_length=20)
    
    # Montos
    ingresos = models.IntegerField(default=0)
    compras_netas = models.IntegerField(default=0)
    compras_exentas = models.IntegerField(default=0)
    boletas_honorarios = models.IntegerField(default=0)
    ppm = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.mes}-{self.anio}"