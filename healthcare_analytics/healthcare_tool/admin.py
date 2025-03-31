from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Department, Doctor, Patient, Nurse, Bed, Revenue

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Nurse)
admin.site.register(Bed)
admin.site.register(Revenue)
