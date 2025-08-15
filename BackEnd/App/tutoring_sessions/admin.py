from django.contrib import admin
from .models import Session, Participant


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'date', 'status',
                    'max_participants', 'available_spots', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['title', 'description', 'creator__email',
                     'creator__first_name', 'creator__last_name']
    readonly_fields = ['created_at', 'updated_at', 'available_spots']
    date_hierarchy = 'date'

    fieldsets = (
        ('Session Information', {
            'fields': ('title', 'description', 'date', 'max_participants')
        }),
        ('Status & Creator', {
            'fields': ('status', 'creator')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'role', 'joined_at']
    list_filter = ['role', 'joined_at', 'session__status']
    search_fields = ['user__email', 'user__first_name',
                     'user__last_name', 'session__title']
    readonly_fields = ['joined_at']

    fieldsets = (
        ('Participant Information', {
            'fields': ('user', 'session', 'role')
        }),
        ('Timestamps', {
            'fields': ('joined_at',),
            'classes': ('collapse',)
        }),
    )
