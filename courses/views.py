from django.forms import IntegerField
from django.http import Http404
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from courses.models import CourseRegistration
from courses.utils import ProcessCourse, ProcessDepartmentCourse
from school_administration.models import Department, Level
from school_artifacts.views import get_active_semester
from schoolms.authentication_middleware import IsAuthenticatedCustom
from rest_framework.response import Response
from rest_framework import status
from users.models import Student
from users.user_permissions import IsAdminUser, IsLecturer, IsStudent
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
    DepartmentCoursesSerializer,
    GetCourseByDepartmentSerializer,
    GetCourseByLevelSerializer,
)

# Create your views here.

class CreateCourseView(ModelViewSet):
    serializer_class = CreateCourseSerializer
    queryset = Course.objects.all()
    permission_classes = (IsAuthenticatedCustom, IsAdminUser)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        
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

class UploadCourseView(APIView):
    permission_classes = (IsAuthenticatedCustom, IsAdminUser)

    def post(self, request, *args, **kwargs):
        if "course_file" not in request.FILES:
            return Response(
                {"message": "No file found"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES["course_file"]
        if not file:
            return Response(
                {"message": "Empty file found"}, status=status.HTTP_400_BAD_REQUEST
            )

        process = ProcessCourse(file)
        return process.create_courses()

    
class DepartmentCourses(ModelViewSet):
    serializer_class = GetCourseByDepartmentSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
        IsLecturer,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        if "dept_courses" in request.FILES:
            file = request.FILES["dept_courses"]
            if not file:
                return Response(
                    {"message": "No file found"}, status=status.HTTP_400_BAD_REQUEST
                )
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


class UploadDepartmentCourses(APIView):
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def post(self, request, *args, **kwargs):
        department_id = request.data.get("department_id", None)
        if department_id is None:
            return Response(
                {"message": "Department ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file = request.FILES.get("dept_courses")
        if file is None:
            return Response(
                {"message": "No file found"}, status=status.HTTP_400_BAD_REQUEST
            )

        process = ProcessDepartmentCourse(file, department_id)
        return process.department_courses()


class SingleDepartmentCourses(ModelViewSet):
    serializer_class = DepartmentCoursesSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser
    )

    def create(self, request, *args, **kwargs):
        try:
            department_id = request.data.get("department_id", None)
            department = get_object_or_404(Department, id=department_id)
            course_ids = request.data.get("courses", [])

            # existing courses for dept
            existing_courses = department.courses.values_list("id", flat=True)

            # get out existing courses from the new one
            new_dept_courses = [
                deptcourse
                for deptcourse in course_ids
                if deptcourse not in existing_courses
            ]

            # then get the new courses provided
            courses = Course.objects.filter(
                Q(id__in=new_dept_courses) | Q(id__in=existing_courses)
            )

            department.courses.set(courses)
            department.save()

            serializer = self.serializer_class(courses, many=True)
        except Http404 as e:
            return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)


class DepartmentLevelCourses(ModelViewSet):
    serializer_class = DepartmentCoursesSerializer
    queryset = Course.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        file = request.query_params.get("file")
        if file:
            file = request.FILES["file"]
            if not file:
                return Response(
                    {"message": "No file found"}, status=status.HTTP_400_BAD_REQUEST
                )
            process = ProcessCourse(file)
            return process.level_courses()
        else:
            try:
                # Get department and level IDs from request data
                department_id = request.data.get("department")
                level_id = request.data.get("level")

                # Retrieve department object
                department = get_object_or_404(Department, id=department_id)

                # Get DepartmentLevel instance for the specified level
                department_level = department.level.get(id=level_id)

                course_ids = request.data.get("courses", [])

                # Retrieve existing courses for the level
                existing_course_ids = department_level.courses.values_list(
                    "id", flat=True
                )

                # Filter out existing course IDs from the new list
                new_course_ids = [
                    cid for cid in course_ids if cid not in existing_course_ids
                ]

                # Fetch Course objects based on the provided IDs
                courses = Course.objects.filter(Q(id__in=new_course_ids))

                # fetch courses from the department course
                # courses = department.courses.filter(Q(courses__id__in=new_course_ids))

                if not courses.exists():
                    return Response(
                        {
                            "message": f"No course {courses.name} found for the provided IDs."
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Set the courses for the department level
                department_level.courses.add(*courses)
                # department.courses.add(*courses) #add the course to the department if it doesnt exist

                # before we add the courses to the department level, we need to check if the course is already in the department
                if not department.courses.filter(
                    courses__id__in=new_course_ids
                ).exists():
                    department.courses.add(*courses)
                    department.save()

                serializer = self.serializer_class(courses, many=True)

                return Response(
                    {"message": f"Courses added successfully to {department_level}.", "data": serializer.data},
                )
            except Http404 as e:
                return Response({"message": str(e)}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RegisterCourseView(ModelViewSet):
    serializer_class = CourseRegistarionSerializer
    queryset = CourseRegistration.objects.all()
    permission_classes = (IsAuthenticatedCustom,)

    def get_queryset(self):
        if self.request.user.is_lecturer:
            return CourseRegistration.objects.all()
        if self.request.user.is_admin:
            return CourseRegistration.objects.all()
        if self.request.user.is_student:
            return CourseRegistration.objects.filter(student=self.request.user)
        return CourseRegistration.objects.none()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        #  get student that wants to register
        student_id = request.query_params.get("student")
        level_id = [request.data.get("level")]
        department_id = request.data.get("department")

        student = get_object_or_404(Student, id=student_id)

        active_semester = get_active_semester()
        # check for the student in the db
        if not student:
            return Response(
                {"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )

        department = get_object_or_404(Department, id=department_id)
        # check if the course is in the department
        db_courses = department.courses.filter(level__id__in=level_id)
        if not db_courses.exists():
            return Response(
                {
                    "message": f"No Course available found for registration in this department {department.name}"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # existing_reg_courses = student.courses.

        # new_courses = db_courses.exclude(id__in=existing_reg_courses)
        # if not new_courses.exists():
        #     return Response(
        #         {"message": f"No Course available found for registration in this department {department.name}"}, status=status.HTTP_404_NOT_FOUND
        #     )

        course_registration = CourseRegistration.objects.create(
            student=student, semester=active_semester
        )

        course_registration.courses.add(*db_courses)
        course_registration.save()

        return Response(
            {"message": "Course registered successfully"},
            status=status.HTTP_200_OK,
        )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        student_id = request.data.get("student")
        course = get_object_or_404(Course, id=course_id)
        student = get_object_or_404(Student, id=student_id)
        course_registration = CourseRegistration.objects.filter(student=student).first()
        if not course_registration:
            return Response(
                {"message": "No course registration found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        course_registration.courses.add(course)
        course_registration.save()
        return Response(
            {"message": "Course registered successfully"},
            status=status.HTTP_200_OK,
        )


class ApprovedRegCourses(ModelViewSet):
    queryset = CourseRegistration.objects.filter(approved=True)
    serializer_class = CourseRegistarionSerializer
    permission_classes = (IsAuthenticatedCustom, IsAdminUser)

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        # Get the course registration ID from kwargs
        course_reg_id = request.query_params.get("course_reg")
        approved = request.data.get("approved")
        # Get the course registration object from the database
        course_registration_instance = get_object_or_404(
            CourseRegistration, id=course_reg_id
        )
        # Update the approved flag based on the approved
        course_registration_instance.approved = approved
        course_registration_instance.save()
        # Serialize the updated course registration object
        serializer = self.serializer_class(course_registration_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetDepartmentCourses(APIView):
    serializer_class = CourseResponseSerializer
    queryset = Course.objects.all()
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

        try:
            department = get_object_or_404(Department, id=department_id)
            # level = get_object_or_404(Level, id=level_id)
            department_level = department.level.get(id=level_id)
        except Exception as e:
            return Response(
                {"message": f"Level not found for {department.name}, {str(e)}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except department.DoesNotExist:
            return Response(
                {"message": "Department not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Http404:
            return Response(
                {"message": "Department or Level not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        courses = Course.objects.filter(department=department, level=department_level)
        serializer = CourseResponseSerializer(courses, many=True)
        if not serializer.data:
            return Response(
                {
                    "message": f"No courses found for department {department.name} at level {department_level.level}"
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "message": f"{department.name} {department_level.level} Level Courses",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class GetRegisteredCourses(APIView):
    serializer_class = CourseResponseSerializer
    queryset = Course.objects.all()
    permission_classes = (IsAuthenticatedCustom,)

    def get(self, request, *args, **kwargs):
        student_id = kwargs.get("id")
        student = get_object_or_404(Student, id=student_id)
        if not student:
            return Response(
                {"message": "Student not found"}, status=status.HTTP_404_NOT_FOUND
            )
        courses = student.courses.all()
        serializer = CourseResponseSerializer(courses, many=True)
        if not serializer.data:
            return Response(
                {"message": "No courses registered"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Courses registered", "data": serializer.data},
            status=status.HTTP_200_OK,
        )


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
