import csv
import io
from rest_framework import status
from rest_framework.response import Response

from school_administration.models import Department, Faculty


def match_dept_name(department_name):
    try:
        _department = Department.objects.get(name=department_name)
        return _department, None
    except Department.DoesNotExist:
        error = {
            "error": f"{department_name} not found. Please register the department."
        }
        return None, error


# def create_data_from_csv(file, serializer_class, Model):
#     decoded_file = file.read().decode("utf-8")
#     reader = csv.DictReader(io.StringIO(decoded_file))

#     existing_names = set(Model.objects.values_list("name", flat=True))
#     existing_short_names = set(Model.objects.values_list("short_name", flat=True))

#     rows = []
#     errors = []
#     for row in reader:
#         department_name = row.get("department", None)
#         if department_name:
#             department, error = match_dept_name(department_name)
#             if error is not None:
#                 errors.append(error)
#                 continue
#             row["department"] = department.id if department else None

#         serializer = serializer_class(data=row)
#         if serializer.is_valid():
#             record_data = serializer.validated_data
#             name = record_data["name"]
#             short_name = record_data["short_name"]

#             if name not in existing_names and short_name not in existing_short_names:
#                 rows.append(Model(**record_data))
#                 existing_names.add(name)
#                 existing_short_names.add(short_name)
#             else:
#                 errors.append(
#                     {"name": "Duplicate name or short name", "data": record_data}
#                 )
#         else:
#             errors.append(serializer.errors)


#     if rows:
#         Model.objects.bulk_create(rows)
#         return {
#             "data": f"{len(rows)} {Model._meta.verbose_name_plural} created successfully.",
#             "errors": errors,
#         }
#     else:
#         return {
#             "data": "No data to create.",
#             "errors": errors,
#         }


def create_data_from_csv(file, serializer_class, Model, unique_fields):
    decoded_file = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded_file))

    # Create a set for each unique field
    existing_unique_fields = {
        field: set(Model.objects.values_list(field, flat=True))
        for field in unique_fields
    }

    rows = []
    errors = []
    for row in reader:
        department_name = row.get("department", None)
        if department_name:
            department, error = match_dept_name(department_name)
            if error is not None:
                errors.append(error)
                continue
            row["department"] = department.id if department else None

        serializer = serializer_class(data=row)
        if serializer.is_valid():
            record_data = serializer.validated_data

            # Check for uniqueness for each unique field
            duplicate_fields = [
                field
                for field in unique_fields
                if record_data[field] in existing_unique_fields[field]
            ]

            if not duplicate_fields:
                for field in unique_fields:
                    existing_unique_fields[field].add(record_data[field])
                rows.append(Model(**record_data))
            else:
                error_message = {
                    field: f"Duplicate value for {field}: {record_data[field]}"
                    for field in duplicate_fields
                }
                errors.append({"duplicate_error": error_message, "data": record_data})
        else:
            errors.append(serializer.errors)

    if rows:
        Model.objects.bulk_create(rows)
        return {
            "data": f"{len(rows)} {Model._meta.verbose_name_plural} created successfully.",
            "errors": errors,
        }
    else:
        return {
            "data": "No data to create.",
            "errors": errors,
        }


from django.db import transaction


def bulk_insert(records, Model):
    try:
        with transaction.atomic():
            Model.objects.bulk_create(records, ignore_conflict=True)
    except Exception as e:
        raise Exception(f"An error occurred while creating records: {e}")


from django.db.models.functions import Lower


def create_data_new(file, serializer_class, Model, unique_fields, batch_size=1000):
    decoded_file = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded_file))

    faculties = Faculty.objects.annotate(lower_name=Lower("name")).values_list(
        "lower_name", "id"
    )
    print(faculties)
    faculty_dict = {name: faculty_id for name, faculty_id in faculties}

    # load exisiting records into a set
    existing_unique_fields = {
        field: set(Model.objects.values_list(field, flat=True))
        for field in unique_fields
    }

    rows = []
    errors = []
    for row in reader:
        faculty_name = row.get("faculty", None).lower()
        record_name = row.get("department_name", None)

        row["faculty"] = faculty_dict.get(faculty_name, None)
        if not row["faculty"]:
            errors.append(
                f"Faculty '{faculty_name}' not found for record '{record_name}'."
            )
            continue

        serializer = serializer_class(data=row)
        if serializer.is_valid():
            record_data = serializer.validated_data

            # Check for uniqueness for each unique field
            duplicate_fields = [
                field
                for field in unique_fields
                if record_data[field] in existing_unique_fields[field]
            ]
            if not duplicate_fields:
                for field in unique_fields:
                    existing_unique_fields[field].add(record_data[field])
                rows.append(Model(**record_data))
            else:
                error_message = {
                    field: f"Duplicate value for {field}: {record_data[field]}"
                    for field in duplicate_fields
                }
                errors.append({"duplicate_error": error_message, "data": record_data})

            if len(rows) >= batch_size:
                bulk_insert(rows, Model)
                rows.clear()

        else:
            errors.append(serializer.errors)

    if rows:
        bulk_insert(rows, Model)

    return errors


import random


def generate_random_id(department_code, year):
    """
    Generate a unique 4-digit matric number for a student.

    :param department_code: Code of the department
    :param year: Year of enrollment
    :param existing_numbers: A set of already existing numbers for the department and year
    :return: A unique matric number
    """

    try:
        number = str(random.randint(0, 9999)).zfill(4)
        rand_id = f"{department_code}/{year}/{number}"

        return rand_id
    except:
        raise Exception(
            "Unable to generate a unique matric number after several attempts."
        )

    # existing_number in param
    # max_attempts = 10000  # Maximum attempts to find a unique number
    # for _ in range(max_attempts):
    #     number = str(random.randint(0, 9999)).zfill(4)
    #     rand_id = f"{department_code}/{year}/{number}"
    #     if rand_id not in existing_numbers:
    #         return rand_id

    # raise Exception("Unable to generate a unique matric number after several attempts.")
