from django.forms import IntegerField
from django.http import Http404
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from courses.models import CourseRegistration
from courses.utils import ProcessCourse
from school_administration.models import Department, Level
from schoolms.authentication_middleware import IsAuthenticatedCustom
from rest_framework.response import Response
from rest_framework import status
from users.models import Student
from users.user_permissions import IsAdminUser, IsStudent
import io
import csv
from django.db import transaction
from school_artifacts.models import Session, Semester
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.models.functions import Lower
from .serializers import (
    CourseRegistarionSerializer,
    CourseResponseSerializer,
    CreateCourseSerializer,
    Course,
    CourseUploadSerializer,
    GetCourseByDepartmentSerializer,
)

# Create your views here.


class CreateCourseView(ModelViewSet):
    serializer_class = CreateCourseSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        # we want to be able to create a single course and also upload a csv file and create all the courses
        # in the csv file
        if "course_file" in request.FILES:
            file = request.FILES["course_file"]
            process = ProcessCourse(file)
            return process.create_courses()

        else:
            # just a single creation
            # Validate and save course
            course_serializer = self.serializer_class(data=request.data)
            course_serializer.is_valid(raise_exception=True)
            course_serializer.save()

            return Response(
                {"message": "Course created successfully."},
                status=status.HTTP_200_OK,
            )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        self.perform_destroy(course)
        return Response(
            {
                "message": f"{course.course_code} deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class DepartmentCourses(ModelViewSet):
    serializer_class = GetCourseByDepartmentSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        if "dept_courses" in request.FILES:
            file = request.FILES["dept_courses"]
            process = ProcessCourse(file)
            return process.department_courses()
        else:
            try:
                department_name = request.data.get("department_name", None)
                department = get_object_or_404(Department, name__iexact=department_name)
                course_name = request.data.get("course_name", None)
                course = get_object_or_404(Course, course_name__iexact=course_name)

                department.courses.add(course)
                department.save()
                serializer = self.serializer_class(course)
            except Http404 as e:
                return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data)


class LevelCourses(ModelViewSet):
    serializer_class = GetCourseByDepartmentSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def post(self, request, *args, **kwargs):
        if "level_courses" in request.FILES:
            file = request.FILES["level_courses"]
            process = ProcessCourse(file)
            return process.level_courses()
        else:
            
            level_name = request.data.get("level", None)
            level = get_object_or_404(Level, level__iexact=level_name)
            course_name = request.data.get("course_name", None)
            course = get_object_or_404(Course, course_name__iexact=course_name)

            level.courses.add(course)
            level.save()
            serializer = self.serializer_class(course)
            return Response(serializer.data)
            # return Response({"message": "Level courses added successfully."})


class RegisterCourseView(ModelViewSet):
    serializer_class = CourseRegistarionSerializer
    queryset = CourseRegistration.objects.all()
    permission_classes = (IsAuthenticatedCustom,)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        #  get student that wants to register
        student_id = request.query_params.get("student_id")

        # check for the student in the db
        student = get_object_or_404(Student, id=student_id)
        if not student:
            return Response(
                {"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )
        #  check if the course is in the student department
        if not student.student_department.courses.filter(
            course_name__iexact=request.data.get("course")
        ).exists():
            return Response(
                {"message": "Course not found in your department"},
                status=status.HTTP_404_NOT_FOUND,
            )

        active_session = get_object_or_404(Session, is_active=True)
        active_semester = get_object_or_404(
            Semester, is_active=True, session=active_session
        )

        #  check if student is already registered in the course
        if CourseRegistration.objects.filter(
            student=student, semester=active_semester
        ).exists():
            return Response(
                {"message": "You are already registered in this course"},
                status=status.HTTP_403_FORBIDDEN,
            )

        course_name = request.data.get("course")
        # check if the course is active
        if not CourseRegistration.objects.filter(
            course__course_name=course_name, course_status=True
        ).exists():
            return Response(
                {"message": "Course is not active"}, status=status.HTTP_403_FORBIDDEN
            )

        course = get_object_or_404(Course, course_name=course_name)

        request.data["course"] = course.course.id
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        #  we set the active semseter
        serializer.validated_data["semester"] = active_semester
        serializer.validated_data["student"] = student_id

        # register the student for the course
        self.create(serializer)
        student.courses.add(course)
        return Response(
            {"message": "Course registered", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Course updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"{instance.name} deleted"},
            status=status.HTTP_200_OK,
        )


class CourseRegistrationView(ModelViewSet):
    queryset = CourseRegistration.objects.all()
    serializer_class = CourseRegistarionSerializer
    permission_classes = (
        IsAuthenticatedCustom,
        IsStudent,
    )

    def create(self, request, *args, **kwargs):
        # Get active session and semester
        active_session = get_object_or_404(Session, is_active=True)
        active_semester = get_object_or_404(
            Semester, is_active=True, session=active_session
        )

        # Filter courses based on the active session and semester
        courses = Course.objects.filter(
            Q(course_semester=active_semester) | Q(course_semester__isnull=True),
            department=request.user.student.department,
        )

        # You can further filter courses based on any other criteria if needed

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Assign active session and semester to the course registration
        serializer.validated_data["session"] = active_session
        serializer.validated_data["semester"] = active_semester

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class GetDepartmentCourses(APIView):
    permission_classes = (IsAuthenticatedCustom,)

    def get(self, request, *args, **kwargs):
        department_id = kwargs.get("id")
        departement = get_object_or_404(Department, id=department_id)
        if not departement:
            return Response(
                {"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND
            )

        courses = Course.objects.filter(department=department_id)
        serializer = CourseResponseSerializer(courses, many=True)
        if not serializer.data:
            return Response(
                {"message": f"No courses in {departement}"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": f"Courses in {departement}", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

        # try:
        #     department = get_object_or_404(Department, id=department_id)
        #     courses = department.courses.all()
        #     serializer = CourseResponseSerializer(courses, many=True)
        #     return Response({"message": "Courses in this department", "data": serializer.data})
        # except Http404:
        #     return Response({"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND)


class GetDepartmentLevelCourses(APIView):
    permission_classes = (IsAuthenticatedCustom,)

    def get(self, request, *args, **kwargs):
        department_id = kwargs.get("department_id")
        level_id = kwargs.get("level_id")

        courses = Course.objects.filter(department=department_id, level=level_id)
        serializer = CourseResponseSerializer(courses, many=True)
        if not serializer.data:
            return Response(
                {"message": f"No courses in level department of dept"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": f"Levels", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
