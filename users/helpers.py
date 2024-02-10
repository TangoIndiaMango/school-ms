from django.shortcuts import get_object_or_404
from school_administration.models import Department, Level
from users.models import Lecturer, Student
from users.serializers import (
    CustomUserSerializer,
    CustomUser,
    LecturerSerializer,
    StudentSerializer,
)
from django.db import IntegrityError, transaction
from django.utils.crypto import get_random_string
import csv
import io
from rest_framework.response import Response
from rest_framework import status

from utils.helpers import generate_random_id
from django.http import Http404


def create_user(data):
    # Create a user
    user_data = {
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": data.get("email"),
        "password": data.get("password", get_random_string(12)),
        "phone": data.get("phone"),
        "role": "student",
    }
    # print(user_data, sep="\n")
    with transaction.atomic():
        user_serializer = CustomUserSerializer(data=user_data)
        if user_serializer.is_valid():
            try:
                user = CustomUser.objects.create_user(**user_serializer.validated_data)
                return user
            except Exception as e:
                raise Exception(str(e))
        else:
            raise Exception(user_serializer.errors)


# Create a function to create users and associated roles (student or lecturer)


def create_users_and_roles_file(
    request, file_key, role_field_name, role_model, role_serializer
):
    if file_key not in request.FILES:
        return None, Response(
            {"error": f"No {file_key} provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    current_year = "2024"
    file = request.FILES[file_key]
    decoded_file = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded_file))
    year = request.data.get("year", current_year)

    errors = []
    created_roles = []

    for row in reader:
        # Create a CustomUser for each role and get the created user
        user = create_user(row)

        department_name = row.get("department", None)
        department = Department.objects.filter(name=department_name).first()

        if department:
            # Store the department ID for the user
            row["department"] = department.id
        else:
            # If the department doesn't exist, handle the error but continue processing
            row["department"] = None
            errors.append(
                {
                    "error": f"{department_name} not found. Please create the department and upload {file_key} again."
                }
            )
            continue

        if not row.get(role_field_name):
            row[role_field_name] = generate_random_id(department, year)

        role_instance = role_model.objects.create(
            department=department, **{role_field_name: row[role_field_name]}, user=user
        )
        created_roles.append(role_instance)

        serialized_roles = role_serializer(created_roles, many=True)

    return serialized_roles, errors


def create_single_user_and_role(
    request_data, role_model, role_serializer, role_field_name
):
    try:
        # Create a user and get the created user
        user = create_user(request_data)

        department_name = request_data.get("department", None)
        _department = Department.objects.get(name=department_name)
        if not _department:
            return None, Response(
                {
                    "error": f"{department_name} not found. Please create the department and upload again."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_data = {"department": _department, "user": user}

        if role_field_name in request_data:
            role_data[role_field_name] = request_data[role_field_name]

        # Use create to create and save the role instance
        role_instance = role_model.objects.create(**role_data)
        serialized = role_serializer(role_instance)

        return serialized, None
    except Exception as e:
        return None, Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_role(role_id, Model, serializer_class):
    try:
        # Retrieve a single role by ID
        role = Model.objects.get(pk=role_id)
        serializer = serializer_class(role)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Model.DoesNotExist:
        return Response(
            {"message": f"{Model.__name__} not found"}, status=status.HTTP_404_NOT_FOUND
        )


def get_all_roles(Model, serializer_class):
    # Get all roles
    roles = Model.objects.all()
    if len(roles) == 0:
        return Response(
            {"message": f"{Model.__name__} has no records"},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = serializer_class(roles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class ProcessUserRoles:
    def __init__(self, ):
        pass

    @staticmethod
    def create_user(data):
        """
        Create a user based on provided data.
        """
        user_data = {
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": data.get("email"),
            "password": data.get("password", get_random_string(12)),
            "phone": data.get("phone"),
            "residential_address": data.get("residential_address"),
            "home_address": data.get("home_address"),
            "date_of_birth": data.get("date_of_birth"),
            "gender": data.get("gender"),
            "role": data.get("role"),
        }
        with transaction.atomic():
            user_serializer = CustomUserSerializer(data=user_data)
            if user_serializer.is_valid():
                try:
                    user = CustomUser.objects.create(**user_serializer.validated_data)
                    return user
                except Exception as e:
                    raise Exception(str(e))
            else:
                raise Exception(user_serializer.errors)

    def read_csv_into_key_values(self):

        decoded_file = self.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))
        roles = []

        for row in reader:
            role_data = {
                "user": {
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                    "password": row.get("password", get_random_string(12)),
                    "residential_address": row.get("residential_address"),
                    "home_address": row.get("home_address"),
                    "date_of_birth": row.get("date_of_birth"),
                    "gender": row.get("gender"),
                    "role": row.get("role"),
                }
            }
            if self.role_model == Student:
                role_data["matric_no"] = row.get("matric_no")
            elif self.role_model == Lecturer:
                role_data["staff_no"] = row.get("staff_no")
                role_data["designation"] = row.get("designation")
            roles.append(role_data)

        return roles

    def process_data(self):

        roles = self.read_csv_into_key_values()
        created_roles = []
        errors = []

        for role_data in roles:
            try:
                with transaction.atomic():
                    #  create the customUser
                    user_data = role_data.pop("user")
                    print(user_data)
                    user_serializer = CustomUserSerializer(data=user_data)
                    if user_serializer.is_valid():
                        user = user_serializer.save()

                        # Get or create department
                        department_name = role_data.get("department")
                        department = get_object_or_404(Department, name=department_name)

                        # Get or create level
                        level_name = role_data.get("level")
                        level = get_object_or_404(Level, level=level_name)

                        role_data = {
                            "user": user,
                            "department": department,
                            "level": level,
                            **role_data,  # Add additional fields like matric_no or staff_no
                        }

                        role_instance = self.role_model.objects.create(**role_data)

                        role_instance.department.add(department)
                        created_roles.append(role_instance)
                    else:
                        errors.append(user_serializer.errors)

            except IntegrityError as e:
                errors.append(f"Integrity error: {str(e)}")
            except Exception as e:
                errors.append(str(e))

        if created_roles:
            serialized_roles = self.get_serializer_class()(created_roles, many=True)
            return serialized_roles, errors
        else:
            return None, errors

    def get_serializer_class(self):
        if self.role_model == Student:
            return StudentSerializer
        elif self.role_model == Lecturer:
            return LecturerSerializer
        else:
            raise ValueError("Invalid role model")

    def create_single_user_and_role(
        self, request_data, role_model, role_serializer, role_field_name
    ):
        try:
            with transaction.atomic():
                # Create a user and get the created user
                user = self.create_user(request_data)

                department_name = request_data.get("student_dept", None)
                _department = get_object_or_404(Department, name=department_name)
                _level = get_object_or_404(Level, level=request_data.get("level"))
                if not _department:
                    return None, Response(
                        {
                            "error": f"{department_name} not found. Please create the department and upload again."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                role_data = {
                    "user": user,
                    "student_dept_id": _department.id,
                    "level_id": _level.id,
                }

                if role_field_name in request_data:
                    role_data[role_field_name] = request_data[role_field_name]

                # Use create to create and save the role instance
                role_instance = role_model.objects.create(**role_data)

                # assign student or lecturer to department
                role_instance.department.add(_department)

                serialized = role_serializer(role_instance)
                role_instance.save()

                return serialized, None
        except IntegrityError as e:
            return None, Response(
                {
                    "error": f"Error creating duplicate reocrd {role_model.__name__}: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Http404 as e:
            return None, Response(
                {"error": f"Department not found: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return None, Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_role(role_id, Model, serializer_class):
        try:
            # Retrieve a single role by ID
            role = Model.objects.get(pk=role_id)
            serializer = serializer_class(role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Model.DoesNotExist:
            return Response(
                {"message": f"{Model.__name__} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @staticmethod
    def get_all_roles(Model, serializer_class):
        # Get all roles
        roles = Model.objects.all()
        if len(roles) == 0:
            return Response(
                {"message": f"{Model.__name__} has no records"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = serializer_class(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @staticmethod
    # def update_role(role_id, request_data, Model, serializer_class, field_name):
    #     try:
    #         # Retrieve a single role by ID
    #         role = Model.objects.get(pk=role_id)
    #         role_data = {field_name: request_data.get(field_name)}
    #         role.update(**role_data)
    #         serializer = serializer_class(role)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Model.DoesNotExist:
    #         return Response(
    #             {"message": f"{Model.__name__} not found"},
    #             status=status.HTTP_404_NOT_FOUND,
    #         )
