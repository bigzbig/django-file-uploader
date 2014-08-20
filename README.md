Django File Uploader Decorator
==============================

Introduction
------------

Decorator moves uploaded files to a specified location. Default path to the file is made up of the following parts:

    /<settings.MEDIA>/<table_name>/<field_name>/<derived_from_the_id>/

Name of subdirectory derive from the ID - i.e., that is calculated based on the ID. The reason for such splitting is file system performance. A special feature provides even distribution of files in directories and does not allow to exceed a specified maximum number of files in a single directory.

The filename is changed according to the scheme:

    <filename>-<datetime_now>-<id>.<ext>

In the filename all letters are downcased, diacritical marks are removed and spaces are replaced by hyphens '-'. The filename is cut to the proper length because the full path cannot be longer than 255 characters. The current date is added to refresh the browser cache for file substitution, and ID for easier identification and to ensure uniqueness.

After removing or replacing files, old files and empty paths in the media directory are removed.

Basic usage
-----------

    from django.db import models
    from django_file_uploader.decorators import upload_files
    
    @upload_files()
    class Images(models.Model):
        image = models.ImageField(upload_to='.', max_length=255)


SEO friendly extras
-------------------

Sometimes we want to have more control over the appearance of the file path to give an permalinks glow.

We can change ImageField attribute *upload_to*. The path specified in the *upload_to* replaces the table name in the default-looking path.

    /<settings.MEDIA>/<upload_to>/<field_name>/<derived_from_the_id>/

The *upload_files* decorator has only one parameter named *prepopulated_fields*. It works similarly to *prepopulated_fields* defined in ModelAdmin, but generated is filename not slug.


For example:

    from django.db import models
    from django_file_uploader.decorators import upload_files
    
    @upload_files({'image': ('name',)})
    class Images(models.Model):
        name = models.CharField(max_length=255)
        image = models.ImageField(upload_to='images', max_length=255)

The basename will look like this:

    <name_value>-<datetime_now>-<id>.<ext>
