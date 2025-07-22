# api/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"Session for {self.user.username} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"

class ChatMessage(models.Model):
    SENDER_CHOICES = [('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(null=True, blank=True)
    class Meta: ordering = ['timestamp']
    def __str__(self): return f"[{self.timestamp.strftime('%H:%M:%S')}] {self.sender}: {self.message[:50]}..."

class OperationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    operation = models.CharField(max_length=100, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_success = models.BooleanField(default=True)
    details = models.JSONField()
    class Meta: ordering = ['-timestamp']
    def __str__(self):
        status = "SUCCESS" if self.is_success else "FAILURE"
        return f"{self.operation} by {self.user.username if self.user else 'System'} - {status}"

class SystemMetric(models.Model):
    """
    Stores time-series data for system performance monitoring.
    """
    METRIC_CHOICES = [
        ('cpu_usage', 'CPU Usage (%)'),
        ('memory_usage', 'Memory Usage (MB)'),
        ('inference_time', 'Inference Time (ms)'),
    ]
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metric_name = models.CharField(max_length=50, choices=METRIC_CHOICES, db_index=True)
    metric_value = models.FloatField()

    class Meta:
        ordering = ['-timestamp']
        # FIX: 'index_together' is deprecated. Replaced with the 'indexes' option.
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} at {self.timestamp}"
