# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    
    # Definimos los roles usando una clase interna
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MANAGER = 'MANAGER', 'Gerente'
        CASHIER = 'CAJERO', 'Cajero'
        DELIVERY = 'DELIVERY', 'Repartidor'
    
    # El superusuario por defecto no tendrá uno de estos roles
    # Por eso permitimos que sea nulo (null=True) y en blanco (blank=True)
    role = models.CharField(
        max_length=50, 
        choices=Role.choices, 
        null=True, 
        blank=True
    )
