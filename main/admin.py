from django.contrib import admin
# from .models import Job, Application,Application_Status, Category, Location
from main.models import *

# from tinymce.widgets import TinyMCE
from django.db import models
from .models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class InternshipAdmin(admin.ModelAdmin):
    fieldsets= [
        ("Title/Date", {"fields": ["company", "role", "category", "date_published"] }),
        ("Job_Time",{"fields":["location"]}),
        ("charges",{"fields":["charges"] }),
        ("Content", {"fields": ["content"]}),
        ("Image", {"fields": ["image"]}),
    ]

admin.site.register(User)                                   #registering the User in Admin
admin.site.register(Application)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Service, InternshipAdmin)                           #registering the Job in Admin
admin.site.register(Company)
admin.site.register(Student)
admin.site.register(Comment_model)

