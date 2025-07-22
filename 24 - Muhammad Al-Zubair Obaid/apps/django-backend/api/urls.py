from django.urls import path
from .views import AiRequestView

urlpatterns = [
    path('ai-request/', AiRequestView.as_view(), name='ai-request'),
    # path('admin/run-command/', AdminOperationView.as_view(), name='admin-run-command'),
    # path('analytics/dashboard/', AnalyticsDashboardView.as_view(), name='analytics-dashboard'),
]
