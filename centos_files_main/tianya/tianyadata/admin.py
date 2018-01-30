from django.contrib import admin

# Register your models here.
from django.contrib import admin
from tianyadata.models import Story, Links, Index

# Register your models here.
admin.site.register(Story)
admin.site.register(Links)
admin.site.register(Index)
