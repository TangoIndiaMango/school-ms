from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.views import (
    ApprovedRegCourses,
    CreateCourseView,
    DepartmentCourses,
    DepartmentLevelCourses,
    GetDepartmentCourses,
    GetDepartmentLevelCourses,
    LevelCourses,
    RegisterCourseView,
    SingleDepartmentCourses,
    UploadCourseView,
    UploadDepartmentCourses,
)

router = DefaultRouter(trailing_slash=False)

router.register("courses", CreateCourseView, basename="courses")
# router.register("courses", CreateCourseView, basename="courses")
router.register("department", DepartmentCourses, basename="course-by-dept")
router.register("departments", SingleDepartmentCourses, basename="dept-courses")
router.register("level/department", DepartmentLevelCourses, basename="course-by-level")
router.register("level", LevelCourses, basename="course-by-level")
router.register("approve-course", ApprovedRegCourses, basename="approve-reg-courses")


# Student
router.register("register", RegisterCourseView, basename="course-by-level")


urlpatterns = [
    path("", include(router.urls)),
    path("dept/<str:id>", GetDepartmentCourses.as_view(), name="department"),
    path(
        "departments/<str:department_id>/levels/<str:level_id>",
        GetDepartmentLevelCourses.as_view(),
        name="department",
    ),
    path(
        "courses/department/file",
        UploadDepartmentCourses.as_view(),
        name="upload-department-courses",
    ),
    path(
        "upload/courses",
        UploadCourseView.as_view(),
        name="upload-courses",
    ),
]
