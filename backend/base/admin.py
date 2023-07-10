from django.contrib import admin
from .models import UserProfile, Role, User
admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(User)
# Register your models here.
