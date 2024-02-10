from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.views import CreateCourseView, GetCourseByDepartment

router = DefaultRouter(trailing_slash=False)

router.register("courses", CreateCourseView, basename="courses")
# router.register("courses", CreateCourseView, basename="courses")

urlpatterns = [
    path("", include(router.urls)),
    path("course", GetCourseByDepartment.as_view(), name="get-course-by-dept"),
]
