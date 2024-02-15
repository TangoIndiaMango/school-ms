from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.views import (
    CreateCourseView,
    DepartmentCourses,
    GetDepartmentCourses,
    GetDepartmentLevelCourses,
    LevelCourses,
    RegisterCourseView,
)

router = DefaultRouter(trailing_slash=False)

router.register("courses", CreateCourseView, basename="courses")
# router.register("courses", CreateCourseView, basename="courses")
router.register("department", DepartmentCourses, basename="course-by-dept")
router.register("level", LevelCourses, basename="course-by-level")


# Student
router.register("register", RegisterCourseView, basename="course-by-level")


urlpatterns = [
    path("", include(router.urls)),
    path("departments/<str:id>", GetDepartmentCourses.as_view(), name="department"),
    path("departments/<str:department_id>/levels/<str:level_id>", GetDepartmentLevelCourses.as_view(), name="department"),
    
]
