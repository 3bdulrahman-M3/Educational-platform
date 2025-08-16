from django.contrib import admin
from .models import Session, Participant, BookingRequest, SessionMaterial, Notification


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'subject', 'level', 'date', 'status',
                    'max_participants', 'available_spots', 'created_at']
    list_filter = ['status', 'level', 'subject', 'date', 'created_at']
    search_fields = ['title', 'description', 'subject', 'creator__email',
                     'creator__first_name', 'creator__last_name']
    readonly_fields = ['created_at', 'updated_at', 'available_spots', 'participant_count']
    date_hierarchy = 'date'

    fieldsets = (
        ('Session Information', {
            'fields': ('title', 'description', 'subject', 'level', 'date', 'duration', 'max_participants')
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
    list_display = ['user', 'session', 'role', 'status', 'joined_at']
    list_filter = ['role', 'status', 'joined_at', 'session__status']
    search_fields = ['user__email', 'user__first_name',
                     'user__last_name', 'session__title']
    readonly_fields = ['joined_at']

    fieldsets = (
        ('Participant Information', {
            'fields': ('user', 'session', 'role', 'status')
        }),
        ('Timestamps', {
            'fields': ('joined_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'session', 'status', 'requested_at']
    list_filter = ['status', 'requested_at', 'session__status']
    search_fields = ['user__email', 'user__first_name',
                     'user__last_name', 'session__title', 'message']
    readonly_fields = ['requested_at']

    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'session', 'message', 'status')
        }),
        ('Timestamps', {
            'fields': ('requested_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SessionMaterial)
class SessionMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'session', 'type', 'uploaded_by', 'uploaded_at']
    list_filter = ['type', 'uploaded_at', 'session__status']
    search_fields = ['title', 'session__title', 'uploaded_by__email',
                     'uploaded_by__first_name', 'uploaded_by__last_name']
    readonly_fields = ['uploaded_at']

    fieldsets = (
        ('Material Information', {
            'fields': ('title', 'session', 'type', 'url', 'file', 'file_name')
        }),
        ('Upload Information', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'read', 'created_at']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['user__email', 'user__first_name',
                     'user__last_name', 'title', 'message']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'message', 'type', 'session')
        }),
        ('Status', {
            'fields': ('read',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
