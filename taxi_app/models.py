from django.db import models

class Car(models.Model):
    CLASS_CHOICES = [
        ('Econom', 'Econom'),
        ('Comfort', 'Comfort'),
        ('Business', 'Business'),
    ]
    car_id = models.AutoField(primary_key=True)
    car_name = models.CharField(max_length=100, default="Default Car")
    car_class = models.CharField(max_length=10, choices=CLASS_CHOICES, default="Econom")
    price_per_km = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True) 
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.car_name

    class Meta:
        db_table = 'Car' 