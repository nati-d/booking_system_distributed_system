from django.contrib import admin
from .models import Ticket, Notification

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'created_by', 'assigned_to', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'created_by__username', 'assigned_to__username')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'user', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('ticket__title', 'user__username', 'message')

