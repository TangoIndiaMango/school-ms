from datetime import datetime
from django.http import Http404
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from school_administration.models import Department, Faculty, Level
from schoolms.authentication_middleware import IsAuthenticatedCustom
from users.user_permissions import IsAdminUser
from .helpers import ProcessFaculty, ProcessDepartments, generate_random_id
from .serializers import DepartmentSerializer, FacultySerializer, LevelSerializer
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
            # Handle single creation
            # get department data so we can get the id
            department_names = request.data.get("departments")
            if department_names and not isinstance(department_names, list):
                department_names = [
                    name.strip() for name in department_names.split(",")
                ]
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
                    {"error": f"{request.data['name']} exist already, update if you need to"}, status=status.HTTP_409_CONFLICT
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


class CreateDepartmentView(ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    @transaction.atomic()
    def create(self, request):
        # upload file
        if "department_file" in request.FILES:
            # Handle file upload
            file = request.FILES["department_file"]
            try:
                process_faculties = ProcessDepartments(file)
                response = process_faculties.process_data()
                return response
            except Exception as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # single creation
            # get faculty name
            faculty_name = str(request.data.get("faculty"))
            # get faculty object
            faculty = Faculty.objects.get(name=faculty_name)
            # add faculty to request data
            request.data["faculty"] = faculty.id

            # levels we do the same for courses, students, lecturers
            levels_input = request.data.get("level")

            if isinstance(levels_input, int):
                levels_input = [str(levels_input)]
            elif isinstance(levels_input, str):
                levels_input = [
                    name.strip() for name in levels_input.split(",") if name.strip()
                ]

            level_ids = []
            if levels_input:
                for level_name in levels_input:
                    try:
                        level = Level.objects.get(level=level_name)
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
            # headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic()
    def update(self, request, *args, **kwargs):

        instance = self.get_object()
        faculty_name = request.data.get("faculty")
        # get faculty object
        faculty = Faculty.objects.get(name=faculty_name)
        # add faculty to request data
        request.data["faculty"] = faculty.id

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


class LevelViewSet(ModelViewSet):
    serializer_class = LevelSerializer
    queryset = Level.objects.all()
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def create(self, request, *args, **kwargs):
        department_id = request.data.get("department_id")
        department = Department.objects.get(id=department_id)
        #  get currrent year
        current_year = datetime.now().year
        department_unique_name = generate_random_id(department.short_name, current_year)
    
        #  we create a unique name for that department
        request.data["name"] = department_unique_name
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        #  so we then add the level to the department
        department.level.add(serializer.data["id"])
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
