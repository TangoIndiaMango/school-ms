from school_administration.models import Department
from users.serializers import CustomUserSerializer, CustomUser
from django.db import transaction
from django.utils.crypto import get_random_string
import csv
import io
from rest_framework.response import Response
from rest_framework import status

from utils.helpers import generate_random_id


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
            {"message": f"{Model.__name__} not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )

def get_all_roles(Model, serializer_class):
    # Get all roles
    roles = Model.objects.all()
    if len(roles) == 0:
        return Response(
            {"message": f"{Model.__name__} has no records"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = serializer_class(roles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)