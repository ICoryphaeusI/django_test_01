from django.db import models
import os

# Create your models here.

class File(models.Model):
    file = models.FileField(upload_to='files')

    def __str__(self):
        return os.path.basename(self.file.name)