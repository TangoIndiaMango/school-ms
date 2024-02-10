from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from school_administration.models import Department, Faculty, Level
from schoolms.authentication_middleware import IsAuthenticatedCustom
from users.user_permissions import IsAdminUser
from .helpers import ProcessFaculty, ProcessDepartments
from .serializers import DepartmentSerializer, FacultySerializer, LevelSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status

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

        # upload file
        if "faculty_file" in request.FILES:
            file = request.FILES["faculty_file"]
            process_faculties = ProcessFaculty(file)
            response = process_faculties.process_data()
            return response
        else:
            # single creation
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            process_depts = ProcessDepartments(request.FILES["department_file"])
            response = process_depts.process_data()
            return response

        else:
            # single creation
            # get faculty name
            faculty_name = request.data.get("faculty")
            # get faculty object
            faculty = Faculty.objects.get(name=faculty_name)
            # add faculty to request data
            request.data["faculty"] = faculty.id

            # levels
            levels = request.data.get("levels")
            if levels:
                request.data["levels"] = [
                    Level.objects.get(name=level).id for level in levels
                ]

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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
