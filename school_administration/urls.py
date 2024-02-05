from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CreateDepartmentView, CreateFacultyView

router = DefaultRouter(trailing_slash=False)

router.register("departments", CreateDepartmentView, basename="departments")
router.register("faculties", CreateFacultyView, basename="faculties")

urlpatterns = [
    path("", include(router.urls)),
]