from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(unique=True, max_length=15)

    def __str__(self):
        return self.name
