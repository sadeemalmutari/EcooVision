from django.contrib import admin
from .models import  Person, Activity, Room

# Register your models here.
admin.site.register(Person)
admin.site.register(Activity)
admin.site.register(Room)
admin.site.site_title = "Evi"
admin.site.site_header = "Evi-Admin Panel"
