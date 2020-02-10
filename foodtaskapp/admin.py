from django.contrib import admin

from . import models

admin.site.register(models.Restaurant)
admin.site.register(models.Customer)
admin.site.register(models.Driver)
admin.site.register(models.Meal)
