from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, RegisterView, TestViewSet, QuestionViewSet, StudentTestViewSet, SubmissionViewSet

# 1. Create a router and register
router = DefaultRouter()
router.register(r'tests', TestViewSet, basename='test')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'student/tests', StudentTestViewSet, basename='student-test')
# This creates /api/submissions/ AND our custom /api/submissions/start/
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    # APIViews use .as_view()
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # ViewSets use the router
    # This automatically creates all routes for /tests/ and /tests/<id>/
    path('', include(router.urls)),
]