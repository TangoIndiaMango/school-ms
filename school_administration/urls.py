from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateDepartmentView, CreateFacultyView, LevelViewSet

router = DefaultRouter(trailing_slash=False)

router.register("departments", CreateDepartmentView, basename="departments")
router.register("faculties", CreateFacultyView, basename="faculties")
router.register("levels", LevelViewSet, basename="levels")

urlpatterns = [
    path("", include(router.urls)),
]