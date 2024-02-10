import csv
import io
from django.db import IntegrityError, transaction
from django.db.models.functions import Lower
from courses.models import Course
from school_administration.models import Department, Level
from school_artifacts.models import Semester
from rest_framework.response import Response
from rest_framework import status


# @transaction.atomic
# def create_courses_from_csv(file, serializer_class, Model, unique_fields):
#     decoded_file = file.read().decode("utf-8")
#     reader = csv.DictReader(io.StringIO(decoded_file))

#     # Dictionary to map semester names to corresponding IDs
#     semester_dict = {
#         semester.name.lower(): semester.id for semester in Semester.objects.all()
#     }

#     # Dictionary to map department names to corresponding IDs
#     department_dict = {
#         department.name.lower(): department.id
#         for department in Department.objects.all()
#     }

#     level_dict = {level.level.lower(): level.id for level in Level.objects.all()}

#     # Load existing unique fields into a set
#     existing_unique_fields = {
#         field: set(Model.objects.values_list(Lower(field), flat=True))
#         for field in unique_fields
#     }

#     courses_to_create = []
#     errors = []
#     for row in reader:
#         # Convert keys to lowercase
#         row = {key.lower(): value.strip() for key, value in row.items()}

#         row["course_semester"] = semester_dict.get(row["course_semester"].lower())
#         row["department_course"] = department_dict.get(row["department_course"].lower())
#         row["course_level"] = level_dict.get(row["course_level"].lower())

#         if not row["department_course"]:
#             errors.append(f"Department not found for course '{row['course_name']}'.")
#             continue

#         serializer = serializer_class(data=row)
#         if serializer.is_valid():
#             # Check uniqueness for each unique field
#             duplicate_fields = [
#                 field
#                 for field in unique_fields
#                 if row[field] in existing_unique_fields[field]
#             ]
#             if not duplicate_fields:
#                 # Add lowercase data to existing unique fields set
#                 for field in unique_fields:
#                     existing_unique_fields[field].add(row[field])
#                 course_instance = serializer.save()
#                 courses_to_create.append(course_instance)
#             else:
#                 error_message = {
#                     field: f"Duplicate value for {field}: {row[field]}"
#                     for field in duplicate_fields
#                 }
#                 errors.append({"duplicate_error": error_message, "data": row})
#         else:
#             errors.append(serializer.errors)

#     return {
#         "data": f"{len(courses_to_create)} courses created successfully.",
#         "errors": errors,
#     }


class ProcessCourse:
    def __init__(self, file):
        self.file = file

    def read_csv_into_key_values(self):
        """
        Read the CSV file and return a dictionary with the key as the course name and the value as the course details.
        """
        departments = {}
        decoded_file = self.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))

        for row in reader:
            course_details = {
                "course_name": row.get("course_name", None),
                "course_code": row.get("course_code", None),
                "course_description": row.get("course_description", None),
                "course_unit": row.get("course_unit", None),
                "course_credit": row.get("course_credit", None),
                "mark": row.get("mark", None),
                "course_status": row.get("course_status", None),
            }
            department = row["department"]
            departments.setdefault(department, []).append(course_details)

        return departments

    def proces_data(self):
        departments = self.read_csv_into_key_values()
        errors = []

        for department, courses in departments.items():
            try:
                department_obj = Department.objects.get(name__iexact=department)

                created_courses = []

                for course in courses:
                    course_status = self.convert_to_bool(course["course_status"])
                    course_obj = Course.objects.create(
                        course_name=course["course_name"],
                        course_code=course["course_code"],
                        course_description=course["course_description"],
                        course_unit=course["course_unit"],
                        course_credit=course["course_credit"],
                        mark=course["mark"],
                        course_status=course_status,
                    )
                    created_courses.append(course_obj)

                department_obj.courses.set(created_courses)

            except Department.DoesNotExist:
                errors.append(f"Department '{department}' not found.")
                continue
            except IntegrityError:
                errors.append(f"Course '{course['course_name']}' already exists.")
                continue
            except Exception as e:
                errors.append(f"Error processing course '{course['course_name']}': {e}")

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Data processed successfully."},
                status=status.HTTP_200_OK,
            )

    def convert_to_bool(self, value):
        if isinstance(value, bool):
            return value
        elif value.lower() in ["true", "t", "yes", "y"]:
            return True
        elif value.lower() in ["false", "f", "no", "n"]:
            return False
        else:
            raise ValueError("Invalid boolean value")
