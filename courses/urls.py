from django.urls import path, include
from rest_framework.routers import DefaultRouter

from courses.views import CreateCourseView

router = DefaultRouter(trailing_slash=False)

router.register("courses", CreateCourseView, basename="courses")

urlpatterns = [
    path("", include(router.urls)),
]
