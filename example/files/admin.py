# -*- coding: utf-8 -*-
from django.contrib import admin
from files.models import Images

class ImagesAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Images, ImagesAdmin)
