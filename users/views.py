import datetime
from school_administration.models import Department
from schoolms.authentication_middleware import IsAuthenticatedCustom
from users.helpers import (
    ProcessUserRoles,
    get_all_roles,
    get_role,
)
from users.models import CustomUser, Lecturer, Student
from django.core.exceptions import ObjectDoesNotExist
from users.serializers import (
    AuthSerializer,
    CustomUserSerializer,
    LecturerSerializer,
    StudentSerializer,
    UpdatePasswordSerializer,
)
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.user_permissions import IsAdminUser
import io
import csv
from users.utils import get_access_token
from django.utils.crypto import get_random_string
from rest_framework.viewsets import ModelViewSet
from django.db import transaction, models
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from utils.helpers import generate_random_id

# Create your views here.

User = get_user_model()


class CreateUserView(APIView):
    serializer_class = CustomUserSerializer

    # def create(self, request, *args, **kwargs):
    #     if "user_file" in request.FILES:
    #         file = request.FILES["user_file"]
    #         # role = request.data.get('role', 'student')
    #         role = request.query_params.get("role", "student")
    #         decoded_file = file.read().decode("utf-8").splitlines()
    #         reader = csv.DictReader(io.StringIO(decoded_file))

    #         #  create users from csv
    #         users = []
    #         errors = []
    #         for row in reader:
    #             row["password"] = get_random_string()
    #             row["role"] = role
    #             user_serializer = self.serializer_class(data=row)
    #             if user_serializer.is_valid():
    #                 users.append(user_serializer.validated_data)
    #             else:
    #                 errors.append(user_serializer.errors)
    #         if errors:
    #             return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             # create the users
    #             for user_data in users:
    #                 user = User.objects.create_user(**user_data)
    #                 user.set_password(user_data["password"])
    #                 user.save()

    #             # perform a celery task to email the username and password

    #             return Response(
    #                 {"message": "Users created successfully."},
    #                 status=status.HTTP_200_OK,
    #             )

    #     else:
    #         # just a single creation
    #         user_serializer = self.serializer_class(data=request.data)
    #         user_serializer.is_valid(raise_exception=True)
    #         user_serializer.save()
    #         return Response(
    #             {
    #                 "message": "User created successfully.",
    #                 "user": user_serializer.data,
    #             },
    #             status=status.HTTP_200_OK,
    #         )

    def post(self, request):
        user_serializer = self.serializer_class(data=request.data)

        user_serializer.is_valid(raise_exception=True)
        user = None

        try:
            user = CustomUser.objects.create_user(**user_serializer.validated_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        #  serialize user data
        user_serializer = self.serializer_class(user)
        return Response(
            {
                "message": "User created successfully.",
                "user": user_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    serializer_class = AuthSerializer

    def post(self, request):
        valid_request = self.serializer_class(data=request.data)
        valid_request.is_valid(raise_exception=True)

        user = authenticate(
            username=valid_request.data["email"],
            password=valid_request.data.get("password", None),
        )

        if not user:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST
            )
        expiry = 360
        access = get_access_token(
            {
                "user_id": user.id,
            },
            expiry,
        )

        return Response(
            {
                "access_token": access,
            },
            status=status.HTTP_200_OK,
        )
        # once a user logs in he should be prompted to reset his password


# class ResetPasswordView(APIView):
#     serializer_class = UpdatePasswordSerializer

#     def post(self, request):
#         valid_request = self.serializer_class(data=request.data)
#         valid_request.is_valid(raise_exception=True)

#         email = verify_link(valid_request.validated_data["token"], True)
#         if not email:
#             return Response({"error": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)
#         user = User.objects.get(email=email)
#         user.set_password(valid_request.validated_data["password"])
#         user.save()

#         return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)


class CurrentUser(APIView):
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedCustom,)

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentCreateView(APIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticatedCustom, IsAdminUser]

    year = datetime.date.today().year
    current_year_slashed = str(year)[-2:]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        # Call the process_data method to process data from the uploaded file
        role_model = Student  # or Lecturer, depending on the role model
        role_serializer = (
            StudentSerializer  # or LecturerSerializer, depending on the role
        )
        role_field_name = "matric_no"
        processor = ProcessUserRoles(role_model, role_serializer, role_field_name)
        # we get a file upload
        if request.FILES:
            file = request.FILES["student_file"]
            student_serialized, student_error_response = processor.process_student_data(
                file
            )
            if student_error_response:
                return Response(
                    student_error_response, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {
                    "message": f" {len(student_serialized.data)} Students created successfully.",
                },
                status=status.HTTP_200_OK,
            )

        else:
            # Call the create_single_user_and_role method to create a single student user and role
            student_serialized, student_error_response = (
                processor.create_single_student_and_role(request.data)
            )

            if student_error_response:
                return student_error_response

            return Response(
                {
                    "message": "Student created successfully.",
                    "data": student_serialized.data,
                },
                status=status.HTTP_200_OK,
            )

    # @action(detail=False, methods=['get'], url_path='get-by-matric/(?P<matric_no>[^/.]+)')
    # def get_by_matric(self, request, matric_no=None):
    #     student = self.get_queryset().filter(matric_no=matric_no).first()
    #     if student:
    #         serializer = self.get_serializer(student)
    #         return Response(serializer.data)
    #     else:
    #         return Response({"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        student_id = kwargs.get("pk")

        if student_id:
            # Retrieve a single role by ID using the get_role function
            return get_role(student_id, Student, self.serializer_class)

        # If no ID is provided, get all roles using the get_all_roles function
        return get_all_roles(Student, self.serializer_class)

    def update(self, request, *args, **kwargs):
        student_id = kwargs.get("pk")
        student = Student.objects.get(pk=student_id)
        serializer = StudentSerializer(student, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Student updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        student_id = kwargs.get("pk")
        student = Student.objects.get(pk=student_id)
        student.delete()
        return Response(
            {"message": "Student deleted successfully."}, status=status.HTTP_200_OK
        )


class LecturerCreateView(APIView):
    serializer_class = LecturerSerializer
    queryset = Lecturer.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    year = datetime.date.today().year
    current_year_slashed = str(year)[-2:]

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        # Call the process_data method to process data from the uploaded file
        role_model = Lecturer  # or Lecturer, depending on the role model
        role_serializer = (
            LecturerSerializer  # or LecturerSerializer, depending on the role
        )
        role_field_name = "staff_id"
        processor = ProcessUserRoles(role_model, role_serializer, role_field_name)
        # we get a file upload
        if request.FILES:
            file = request.FILES["lecturer_file"]
            lecturer_serialized, lecturer_error_response = (
                processor.process_lecturer_data(file)
            )
            if lecturer_error_response:
                return Response(
                    lecturer_error_response, status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {
                    "message": f" {len(lecturer_serialized.data)} Lecturers created successfully.",
                },
                status=status.HTTP_200_OK,
            )

        else:
            # Call the create_single_user_and_role method to create a single Lecturer user and role
            lecturer_serialized, lecturer_error_response = (
                processor.create_single_lecturer_and_role(request.data)
            )

            if lecturer_error_response:
                return lecturer_error_response

            return Response(
                {
                    "message": "Lecturer created successfully.",
                    "data": lecturer_serialized.data,
                },
                status=status.HTTP_200_OK,
            )

    def get(self, request, *args, **kwargs):

        lecturer_id = kwargs.get("pk")

        if lecturer_id:
            return get_role(lecturer_id, Lecturer, self.serializer_class)

        return get_all_roles(Lecturer, self.serializer_class)

    def patch(self, request, *args, **kwargs):
        lecturer_id = kwargs.get("pk")
        lecturer = Lecturer.objects.get(pk=lecturer_id)
        serializer = LecturerSerializer(lecturer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Lecturer updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        lecturer_id = kwargs.get("pk")
        lecturer = Lecturer.objects.get(pk=lecturer_id)
        lecturer.delete()
        return Response(
            {"message": "Lecturer deleted successfully."}, status=status.HTTP_200_OK
        )


class StudentCourseRegisterView:
    pass
