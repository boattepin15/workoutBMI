from django.urls import path
from .views import HomeView, BodyAnalysisCreateView, BodyAnalysisDetailView, BodyAnalysisListView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('analysis/create/', BodyAnalysisCreateView.as_view(), name='analysis_create'),
    path('analysis/result/<int:pk>/', BodyAnalysisDetailView.as_view(), name='analysis_result'),
    path('history/', BodyAnalysisListView.as_view(), name='history'),
]
