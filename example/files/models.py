# -*- coding: utf-8 -*-
from django.db import models
from django_file_uploader.decorators import upload_files


@upload_files({'image': ('name',)})
class Images(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='.', max_length=255)