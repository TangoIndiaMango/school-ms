from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CreateDepartmentView,
    CreateFacultyView,
    GetDepartmentLevel,
    GetStudentsInDepartement,
    LevelViewSet,
    UploadDepartmentView,
    UploadFacultyView,
)

router = DefaultRouter(trailing_slash=False)

router.register("departments", CreateDepartmentView, basename="departments")
router.register("faculties", CreateFacultyView, basename="faculties")
router.register("levels", LevelViewSet, basename="levels")

urlpatterns = [
    path("", include(router.urls)),
    path("dept/levels/<str:department_id>", GetDepartmentLevel.as_view(), name="get_department_levels"),
    path("dept/students/<str:department_id>", GetStudentsInDepartement.as_view(), name="get_students_in_department"),
    path("upload/departments", UploadDepartmentView.as_view(), name="upload_department_data"),
    path("upload/faculties", UploadFacultyView.as_view(), name="upload_faculty_data"),
]
