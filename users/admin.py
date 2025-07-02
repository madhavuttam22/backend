from django.contrib import admin
from .models import FirebaseUser

@admin.register(FirebaseUser)
class FirebaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone', 'uid')
    search_fields = ('email', 'first_name', 'last_name', 'uid')
    readonly_fields = ('uid',)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    full_name.short_description = 'Name'
