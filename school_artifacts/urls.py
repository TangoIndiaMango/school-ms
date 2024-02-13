# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SessionViewSet, SemesterViewSet

router = DefaultRouter()
router.register(r'sessions', SessionViewSet)
router.register(r'semesters', SemesterViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
