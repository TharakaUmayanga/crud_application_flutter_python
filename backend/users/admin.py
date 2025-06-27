from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'age', 'created_at']
    list_filter = ['created_at', 'updated_at', 'age']
    search_fields = ['name', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone_number', 'age')
        }),
        ('Address Information', {
            'fields': ('address',)
        }),
        ('Profile Picture', {
            'fields': ('profile_picture',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
