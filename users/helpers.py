from django.shortcuts import get_object_or_404
from school_administration.models import Department, Level
from users.models import Designation, Lecturer, Student
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
    def __init__(self, role_model, role_serializer, role_field_name):
        self.role_model = role_model
        self.role_serializer = role_serializer
        self.role_field_name = role_field_name

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

    def read_csv_into_key_values(self, file):

        decoded_file = file.read().decode("utf-8")
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
                role_data["student_department"] = row.get("student_department")
                role_data["level"] = row.get("level")
            if self.role_model == Lecturer:
                role_data["staff_id"] = row.get("staff_id")
                role_data["designation"] = row.get("designation")
                role_data["lecturer_department"] = row.get("lecturer_department")
                role_data["qualification"] = row.get("qualification")
                role_data["level"] = row.get("level")
            roles.append(role_data)

        return roles

    def process_student_data(self, file):

        roles = self.read_csv_into_key_values(file)
        # print(roles)
        created_roles = []
        errors = []

        for role_data in roles:
            try:
                #  create the customUser
                user_data = role_data.pop("user")
                # print(user_data)
                user_serializer = CustomUserSerializer(data=user_data)
                if user_serializer.is_valid():
                    user = user_serializer.save()

                    # Get or create department
                    department_name = role_data.get("student_department")
                    department = get_object_or_404(Department, name=department_name)
                    # print(department_name, department.name)

                    # Get or create level
                    level_name = role_data.get("level")
                    level = get_object_or_404(Level, level=level_name)

                    role_data["student_department"] = department
                    role_data["level"] = level
                    role_data["user"] = user
                    # print(role_data)

                    role_instance = self.role_model.objects.create(**role_data)

                    #  add student to department list
                    # student = role_instance
                    department.students.add(role_instance)

                    created_roles.append(role_instance)
                else:
                    errors.append(user_serializer.errors)
                    continue

            except IntegrityError as e:
                errors.append(f"Integrity error: {str(e)}")
            except Exception as e:
                errors.append(str(e))

        if created_roles:
            serialized_roles = self.get_serializer_class()(created_roles, many=True)
            return serialized_roles, errors
        else:
            return None, errors

    def process_lecturer_data(self, file):
        roles = self.read_csv_into_key_values(file)
        created_roles = []
        errors = []

        for role_data in roles:
            with transaction.atomic():
                try:
                    #  create the customUser
                    user_data = role_data.pop("user")

                    user_serializer = CustomUserSerializer(data=user_data)
                    if user_serializer.is_valid():
                        user = user_serializer.save()

                        # Get department
                        department_name = role_data.get("lecturer_department")
                        if department_name:
                            department = get_object_or_404(
                                Department, name=department_name
                            )
                        else:
                            department_name = None

                        # Get level
                        level_name = role_data.get("level")

                        if level_name:
                            level = get_object_or_404(Level, level=level_name)
                        else:
                            level = None
                        role_data["lecturer_department"] = department
                        role_data["level"] = level
                        role_data["user"] = user

                        role_instance = self.role_model.objects.create(**role_data)

                        department.lecturers.add(role_instance)
                        role_instance.save()

                        created_roles.append(role_instance)
                    else:
                        errors.append(user_serializer.errors)
                        continue

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
        if self.role_model == Lecturer:
            return LecturerSerializer
        else:
            raise ValueError("Invalid role model")

    def create_single_student_and_role(self, request_data):
        try:
            with transaction.atomic():
                # Create a user and get the created user
                user = self.create_user(request_data)

                department = request_data.get("student_department", None)
                _department = get_object_or_404(Department, id=department)
                # get the department levels
                dept_levels = _department.level.all()
                # check if the id of the level is in that level
                level_id = request_data.get("level")
                if level_id not in [level.id for level in dept_levels]:
                    return None, Response(
                        {"error": f"Level {level_id} not found in {_department.name}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                #  get level
                _level = dept_levels.get(id=level_id)
                print(_level)
                # _level = get_object_or_404(Level, level=request_data.get("level"))

                role_data = {
                    "user": user,
                    "student_department": _department,
                    "level": _level,
                }

                if self.role_field_name in request_data:
                    role_data[self.role_field_name] = request_data[self.role_field_name]

                # Use create to create and save the role instance
                role_instance = self.role_model.objects.create(**role_data)

                # assign student or lecturer to department
                _department.students.add(role_instance)

                serialized = self.role_serializer(role_instance)
                role_instance.save()

                return serialized, None
        except IntegrityError as e:
            return None, Response(
                {
                    "error": f"Error creating duplicate reocrd {self.role_model.__name__}: {str(e)}"
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

    def create_single_lecturer_and_role(self, request_data):
        try:
            with transaction.atomic():
                # Create a user and get the created user
                user = self.create_user(request_data)

                department_name = request_data.get("lecturer_department", None)
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
                    "lecturer_department": _department,
                    "level_id": _level.id,
                }

                if self.role_field_name in request_data:
                    role_data[self.role_field_name] = request_data[self.role_field_name]

                # Use create to create and save the role instance
                role_instance = self.role_model.objects.create(**role_data)

                # assign student or lecturer to department
                _department.lecturers.add(role_instance)

                serialized = self.role_serializer(role_instance)
                role_instance.save()

                return serialized, None
        except IntegrityError as e:
            return None, Response(
                {
                    "error": f"Error creating duplicate reocrd {self.role_model.__name__}: {str(e)}"
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


class ProcessCreateStudents:
    def __init__(
        self, role_model, role_serializer, role_field_name, department, level, password
    ):
        self.role_model = role_model
        self.role_serializer = role_serializer
        self.role_field_name = role_field_name
        self.department = department
        self.level = level
        self.password = password

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

    def read_csv_into_key_values(self, file):

        decoded_file = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))
        roles = []

        for row in reader:
            role_data = {
                "user": {
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                    "password": self.password,
                    "residential_address": row.get("residential_address"),
                    "home_address": row.get("home_address"),
                    "date_of_birth": row.get("date_of_birth"),
                    "gender": row.get("gender"),
                    "role": "student",
                }
            }
            if self.role_model == Student:
                role_data["matric_no"] = row.get("matric_no")
                role_data["student_department"] = self.department
                role_data["level"] = self.level

            roles.append(role_data)

        return roles

    def process_student_data(self, file):

        roles = self.read_csv_into_key_values(file)
        # print(roles)
        created_roles = []
        errors = []

        for role_data in roles:
            try:
                #  create the customUser
                user_data = role_data.pop("user")
                # print(user_data)
                user_serializer = CustomUserSerializer(data=user_data)
                if user_serializer.is_valid():
                    user = user_serializer.save()

                    role_data["student_department"] = self.department
                    role_data["level"] = self.level
                    role_data["user"] = user
                    # print(role_data)

                    role_instance = self.role_model.objects.create(**role_data)

                    #  add student to department list
                    # student = role_instance
                    self.department.students.add(role_instance)

                    created_roles.append(role_instance)
                else:
                    errors.append(user_serializer.errors)
                    continue

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
        if self.role_model == Lecturer:
            return LecturerSerializer
        else:
            raise ValueError("Invalid role model")

    def create_single_student_and_role(self, request_data):
        try:
            with transaction.atomic():
                # Create a user and get the created user
                user = self.create_user(request_data)

                role_data = {
                    "user": user,
                    "student_department": self.department,
                    "level": self.level,
                }

                if self.role_field_name in request_data:
                    role_data[self.role_field_name] = request_data[self.role_field_name]

                # Use create to create and save the role instance
                role_instance = self.role_model.objects.create(**role_data)

                # assign student or lecturer to department
                self.department.students.add(role_instance)

                serialized = self.role_serializer(role_instance)
                role_instance.save()

                return serialized, None
        except IntegrityError as e:
            return None, Response(
                {
                    "error": f"Error creating duplicate reocrd {self.role_model.__name__}: {str(e)}"
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



class ProcessCreateLecturer:
    def __init__(
        self,
        role_model,
        role_serializer,
        role_field_name,
        password,
        department=None,
        designation=None,
    ):
        self.role_model = role_model
        self.role_serializer = role_serializer
        self.role_field_name = role_field_name
        self.department = department
        self.designation = designation
        self.password = password

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

    def read_csv_into_key_values(self, file):

        decoded_file = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))
        roles = []

        for row in reader:
            role_data = {
                "user": {
                    "first_name": row.get("first_name"),
                    "last_name": row.get("last_name"),
                    "email": row.get("email"),
                    "phone": row.get("phone"),
                    "password": self.password,
                    "residential_address": row.get("residential_address"),
                    "home_address": row.get("home_address"),
                    "date_of_birth": row.get("date_of_birth"),
                    "gender": row.get("gender"),
                    "role": "lecturer",
                }
            }
            if self.role_model == Lecturer:
                role_data["staff_id"] = row.get("staff_id")
                role_data["lecturer_department"] = self.department
                role_data["designation"] = self.designation
                role_data["qualification"] = row.get("qualification")

            roles.append(role_data)

        return roles

    def process_lecturer_data(self, file):

        roles = self.read_csv_into_key_values(file)
        # print(roles)
        created_roles = []
        errors = []

        for role_data in roles:
            try:
                #  create the customUser
                user_data = role_data.pop("user")
                # print(user_data)
                user_serializer = CustomUserSerializer(data=user_data)
                if user_serializer.is_valid():
                    user = user_serializer.save()

                    role_data["lecturer_department"] = self.department
                    role_data["designation"] = self.designation
                    role_data["user"] = user
                    # print(role_data)

                    role_instance = self.role_model.objects.create(**role_data)

                    #  add student to department list
                    # student = role_instance
                    if self.department is not None:
                        self.department.lecturers.add(role_instance)

                    created_roles.append(role_instance)
                else:
                    errors.append(user_serializer.errors)
                    continue

            except IntegrityError as e:
                errors.append(f"Integrity error: {str(e)}")
            except Exception as e:
                errors.append(str(e))

        if created_roles:
            serialized_roles = LecturerSerializer(created_roles, many=True)
            return serialized_roles, errors
        else:
            return None, errors

    def create_single_lecturer_and_role(self, request_data):
        try:
            with transaction.atomic():
                # Create a user and get the created user
                user = self.create_user(request_data)

                role_data = {
                    "user": user,
                    "lecturer_department": self.department,
                    "designation": self.designation,
                }

                if self.role_field_name in request_data:
                    role_data[self.role_field_name] = request_data[self.role_field_name]

                # Use create to create and save the role instance
                role_instance = self.role_model.objects.create(**role_data)

                serialized = self.role_serializer(role_instance)
                role_instance.save()
                # assign student or lecturer to department
                if self.department is not None:
                    self.department.lecturers.add(role_instance)

                return serialized, None
        except IntegrityError as e:
            return None, Response(
                {
                    "error": f"Error creating duplicate reocrd {self.role_model.__name__}: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return None, Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
