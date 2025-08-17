from django.contrib import admin
from .models import FirebaseUser,Contact

# @admin.register(FirebaseUser)
# class FirebaseUserAdmin(admin.ModelAdmin):
#     list_display = ('email', 'full_name', 'phone', 'uid')
#     search_fields = ('email', 'first_name', 'last_name', 'uid')
#     # readonly_fields = ('uid')

#     def full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}".strip()

#     full_name.short_description = 'Name'
# admin.py
from django.contrib import admin
from .models import FirebaseUser
from django.utils.html import format_html

@admin.register(FirebaseUser)
class FirebaseUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'uid_short', 'phone', 'is_active', 'date_joined')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'uid', 'phone')
    readonly_fields = ('uid', 'date_joined', 'last_login')
    fieldsets = (
        (None, {'fields': ('uid', 'email', 'is_active')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'address')}),
        ('Media', {'fields': ('avatar',)}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )

    def full_name(self, obj):
        return obj.get_full_name()
    full_name.short_description = 'Full Name'

    def uid_short(self, obj):
        return f"{obj.uid[:8]}..." if obj.uid else ""
    uid_short.short_description = 'UID (short)'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Optional: Sync changes back to Firebase
        try:
            updates = {}
            if obj.first_name and obj.last_name:
                updates['display_name'] = f"{obj.first_name} {obj.last_name}"
            if obj.email:
                updates['email'] = obj.email
            
            if updates:
                from firebase_admin import auth
                auth.update_user(obj.uid, **updates)
        except Exception as e:
            self.message_user(request, f"Firebase sync failed: {str(e)}", level='ERROR')



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