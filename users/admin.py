from django.contrib import admin
from .models import FirebaseUser

@admin.register(FirebaseUser)
class FirebaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'phone', 'uid', 'created_at')
    search_fields = ('email', 'name', 'uid')
    readonly_fields = ('uid', 'created_at')
