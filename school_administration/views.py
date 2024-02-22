from datetime import datetime
from django.http import Http404
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

from school_administration.models import Department, Faculty, Level
from schoolms.authentication_middleware import IsAuthenticatedCustom
from users.user_permissions import IsAdminUser, IsLecturer
from .helpers import ProcessFaculty, ProcessDepartments, generate_random_id
from .serializers import (
    DepartmentSerializer,
    FacultySerializer,
    LevelResponseSerializer,
    LevelSerializer,
    StudentDepartmentSerializer,
)
from django.db import IntegrityError, transaction
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.


class CreateFacultyView(ModelViewSet):
    serializer_class = FacultySerializer
    queryset = Faculty.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):

        # Handle single creation
        # get department data so we can get the id
        department_names = request.data.get("departments")
        if department_names and not isinstance(department_names, list):
            department_names = [name.strip() for name in department_names.split(",")]
        else:
            # if department_names is not a list, convert it to a list
            department_names = department_names

        department_ids = []
        try:

            if department_names:
                for department_name in department_names:
                    department = get_object_or_404(Department, name=department_name)
                    department_ids.append(department.id)

            request.data["departments"] = department_ids
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            return Response(
                {
                    "error": f"{request.data['name']} exist already, update if you need to"
                },
                status=status.HTTP_409_CONFLICT,
            )  # conflict error
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic()
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": f"{instance.name} deleted successfuly"},
            status=status.HTTP_204_NO_CONTENT,
        )


class UploadFacultyView(APIView):
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def post(self, request, *args, **kwargs):
        # Check if the file exists in the request.FILES dictionary
        if "faculty_file" in request.FILES:
            file = request.FILES.get("faculty_file")
            if file:
                try:
                    process_faculties = ProcessFaculty(file)
                    response = process_faculties.process_data()
                    return response
                except Exception as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(
                {"error": "No file found in the request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateDepartmentView(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request):

        faculty_id = request.data.get("faculty")
        # get faculty object
        try:
            faculty = Faculty.objects.get(id=faculty_id)
        except Faculty.DoesNotExist:
            return Response(
                {"error": f"Faculty {faculty_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # levels
        levels_input = request.data.get("level")
        level_ids = []

        if levels_input:
            if not isinstance(levels_input, list):
                levels_input = [levels_input]
            for level_name in levels_input:
                department_unique_name = generate_random_id(
                    request.data["short_name"], level_name
                )

                try:
                    level, _ = Level.objects.get_or_create(
                        name=department_unique_name, level=level_name
                    )
                    level_ids.append(level.id)
                except Level.DoesNotExist:
                    return Response(
                        {"error": f"Level {level_name} does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

        request.data["level"] = level_ids

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Add the department to the faculty
        faculty.departments.add(serializer.data["id"])

        # Associate each level with the department
        for level_id in level_ids:
            try:
                level = Level.objects.get(id=level_id)
                level.department.add(serializer.data["id"])
            except Level.DoesNotExist:
                return Response(
                    {"error": f"Level {level_id} does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic()
    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)  # Use perform_update instead of self.update
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)  # Use perform_destroy instead of self.destroy
        return Response(
            {"message": f"{instance.name} deleted successfuly"},
            status=status.HTTP_204_NO_CONTENT,
        )


class UploadDepartmentView(APIView):
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def post(self, request, *args, **kwargs):
        # Check if the file exists in the request.FILES dictionary
        faculty_id = request.data.get("faculty_id")

        if "department_file" in request.FILES:
            file = request.FILES.get("department_file")
            if file:
                try:
                    process_departments = ProcessDepartments(file, faculty_id)
                    response = process_departments.process_data()
                    return response
                except Exception as e:
                    return Response(
                        {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
        else:
            return Response(
                {"error": "No file found in the request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LevelViewSet(ModelViewSet):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        department_id = request.data.get("department_id")
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return Response(
                {"error": f"Department with id {department_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        #  get currrent year
        current_year = datetime.now().year
        department_unique_name = generate_random_id(department.short_name, current_year)

        #  we create a unique name for that department
        request.data["name"] = department_unique_name
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        #  so we then add the level to the department
        department.level.add(serializer.data["id"])

        updated_data = {**serializer.data, "department": department.name}

        return Response(updated_data, status=status.HTTP_201_CREATED)


class GetStudentsInDepartement(APIView):
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def get(self, request, *args, **kwargs):
        # get the department id
        department_id = kwargs.get("department_id")
        try:
            department = Department.objects.get(id=department_id)
            if not department:
                return Response(
                    {"message": f"Department with id {department_id} does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            students = department.students.all()
            if not students:
                return Response(
                    {"message": f"No students found in {department.name}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            
            serializer = StudentDepartmentSerializer(students, many=True)
            return Response(
                {"message": f"Students in {department.name}", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        except Department.DoesNotExist:
            return Response(
                {"message": f"Department with id {department_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )


class GetDepartmentLevel(APIView):
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def get(self, request, *args, **kwargs):
        department_id = kwargs.get("department_id")
        try:
            department = get_object_or_404(Department, id=department_id)
            levels = department.level.all()
            if not levels:
                return Response(
                    {"message": f"No level found for {department.name}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = LevelResponseSerializer(levels, many=True)
            return Response(
                {"message": f"Levels in {department.name}", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response(
                {"message": f"Department with id {department_id} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"message": f"Level not found for {department.name}, {str(e)}"},
                status=status.HTTP_404_NOT_FOUND,
            )
