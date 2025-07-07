from django.contrib import admin
from .models import FirebaseUser,Contact

@admin.register(FirebaseUser)
class FirebaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone', 'uid')
    search_fields = ('email', 'first_name', 'last_name', 'uid')
    # readonly_fields = ('uid')

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    full_name.short_description = 'Name'



@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'
    list_editable = ('is_resolved',)  # Allows marking as resolved directly from list view
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'subject', 'message')
        }),
        ('Metadata', {
            'fields': ('created_at', 'is_resolved'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)  # Make creation timestamp read-only