from django.urls import path, include

from rest_framework.routers import DefaultRouter

from users.views import (
    CurrentUser,
    LoginView,
    CreateUserView,
    # ResetPasswordView,)
    StudentCreateView,
    LecturerCreateView,
    UploadLecturerView,
    UploadStudentView,
)

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path("", include(router.urls)),
    path("login/", LoginView.as_view(), name="login"),
    path("student/", StudentCreateView.as_view(), name="student-create"),
    path("lecturer/", LecturerCreateView.as_view(), name="lecturer-create"),
    path("create/", CreateUserView.as_view(), name="user-create"),
    path("user/", CurrentUser.as_view(), name="logged-in-user"),
    path("student/<str:pk>/", StudentCreateView.as_view(), name="student"),
    path("lecturer/<str:pk>/", LecturerCreateView.as_view(), name="lecturer"),
    path('upload-student/', UploadStudentView.as_view(), name='upload_student'),
    path('upload-lecturer/', UploadLecturerView.as_view(), name='upload_lecturer'),
    # path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    # path("student-list/", StudentCreateView.as_view(), name="student-list")
]
