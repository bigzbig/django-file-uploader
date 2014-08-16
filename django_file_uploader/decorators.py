# -*- coding: utf-8 -*-
import os, shutil, datetime
from django.db.models import signals
from django.db import models
from django.db import connection, transaction
from django.conf import settings
from django.template.defaultfilters import slugify
from django_file_uploader.utils import create_path_with_limit, rm_empty_path


def _upload_pre_save(instance, **kwargs):
    # TODO
    # In Django 1.5. new parametr "update_fields" added
    if not instance.pk:
        return
    old = instance.__class__.objects.get(pk=instance.pk)
    fields = instance.__class__._meta.fields
    for field in fields:
        if not isinstance(field, models.FileField):
            continue

        f = getattr(instance, field.name)
        o = getattr(old, field.name)

        path = f.path if f else None
        old_path = o.path if o else None

        if old_path and (old_path != path):
            dirname = os.path.dirname(old_path)
            os.unlink(old_path)
            rm_empty_path(dirname)


def _upload_post_save(instance, **kwargs):

    cursor = connection.cursor()
    fields = instance.__class__._meta.fields
    table_name = instance.__class__._meta.db_table
    params = instance.__class__.upload_files_decorator_parameters
    prepopulated_fields = params.get('prepopulated_fields')
    
    for field in fields:
        if not isinstance(field, models.FileField):
            continue

        source = getattr(instance, field.name)
        if not source:
            continue

        path = source.path
        field_name = field.name

        if not path:
            continue

        upload_dir = os.path.dirname(field.generate_filename(instance, ''))
        if upload_dir == '.':
            upload_dir = table_name

        upload_dir = os.path.join(
            upload_dir,
            field_name, # for field idetyfication
            create_path_with_limit(instance.pk)
        )

        full_upload_dir = os.path.join(settings.MEDIA_ROOT, upload_dir)

        now = datetime.datetime.utcnow().strftime('%y%m%d%H%M%S')
        basename = os.path.basename(path)
        filename, ext = os.path.splitext(basename)
        max_name_length = 254 \
            - len(upload_dir) \
            - len(now) \
            - len(str(instance.pk)) \
            - len(ext) \
            - 3 # num separators

        name = ''
        if prepopulated_fields and field_name in prepopulated_fields:
            items = [getattr(instance, n) for n in prepopulated_fields.get(field_name)]
            name = slugify('-'.join(items))

        if len(name) < 1:
            name = slugify(filename)

        name = name[:max_name_length]
            
        basename = '%s-%s-%s%s' % (
            name,
            now, # for update browser cache
            instance.pk, # for unique and identification
            ext)

        dest_path = os.path.join(full_upload_dir, basename)
        dest_link = os.path.join(upload_dir, basename)

        temp_path = os.path.join(full_upload_dir, name)
        if path[:len(temp_path)] == temp_path:
            continue

        if not os.path.exists(full_upload_dir):
            os.makedirs(full_upload_dir)

        shutil.copy2(path, dest_path)
        if not os.path.exists(full_upload_dir):
            continue

        os.unlink(path)
        dirname = os.path.dirname(path)
        rm_empty_path(dirname)
        setattr(instance, field_name, dest_link)

        query = "UPDATE %s SET %s='%s' WHERE id=%s" % (
            table_name, field_name, dest_link, instance.id)
        cursor.execute(query)
    transaction.commit_unless_managed()


def _upload_post_delete(instance, **kwargs):
    fields = instance.__class__._meta.fields
    for field in fields:
        if not isinstance(field, models.FileField):
            continue

        f = getattr(instance, field.name)
        if f and os.path.exists(f.path):
            dirname = os.path.dirname(f.path)
            os.unlink(f.path)
            rm_empty_path(dirname)

from functools import wraps

def upload_files(prepopulated_fields=None):

    def decor(cls):
        setattr(cls, 'upload_files_decorator_parameters', {
            'prepopulated_fields': prepopulated_fields})
        signals.pre_save.connect(_upload_pre_save, sender=cls)
        signals.post_save.connect(_upload_post_save, sender=cls)
        signals.post_delete.connect(_upload_post_delete, sender=cls)
        return cls
    return decor
