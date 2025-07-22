from django.contrib import admin
from .models import ChatSession, ChatMessage, OperationLog, SystemMetric


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time')
    list_filter = ('start_time', 'user')
    search_fields = ('user__username',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender', 'message', 'timestamp')
    list_filter = ('timestamp', 'sender', 'session__user')
    search_fields = ('message', 'session__user__username')
    readonly_fields = ('timestamp',)

@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'operation', 'is_success', 'ip_address')
    list_filter = ('timestamp', 'operation', 'is_success', 'user')
    search_fields = ('operation', 'user__username', 'ip_address')
    readonly_fields = ('timestamp',)

@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'metric_name', 'metric_value')
    list_filter = ('metric_name', 'timestamp')

