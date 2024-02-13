import csv
import io
from rest_framework import status
from rest_framework.response import Response
from django.db.models.functions import Lower
from school_administration.models import Department, Faculty, Level
import random
from django.db.models import Q
from django.db import IntegrityError, transaction

from users.models import Lecturer


class ProcessFaculty:
    def __init__(self, file):
        self.file = file

    def read_csv_into_key_values(self):
        """
        Read the CSV file
        """
        faculties = {}
        decoded_file = self.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))

        #  in a case where we upload departments with it

        for row in reader:
            faculty_name = row.get("faculty", None)
            if faculty_name:
                faculty_details = {
                    "name": faculty_name,
                    "short_name": row.get("short_name", ""),
                    "dean": row.get("dean", None),
                    "departments": [
                        d.strip()
                        for d in row.get("departments", "").split(",")
                        if d.strip()
                    ],
                }
                faculties[faculty_name] = faculty_details

    def process_data(self):
        """
        Process the data and create the faculty and department objects.
        """
        faculties = self.read_csv_into_key_values()
        errors = []
        #  create faculties
        for faculty_name, faculty_data in faculties.items():
            try:
                with transaction.atomic():
                    faculty_obj = Faculty.objects.get_or_create(
                        name=faculty_data["name"],
                        defaults={"short_name": faculty_data["short_name"]},
                    )

                    dean_name = faculty_data.get("dean", None)
                    if dean_name:
                        dean, created = Lecturer.objects.get(name=dean_name)
                        faculty_obj.dean = dean

                    department_names = faculty_data.get("departments", [])
                    for department_name in department_names:
                        department_obj = Department.objects.get(
                            name=department_name, faculty=faculty_obj
                        )
                        faculty_obj.departments.add(department_obj)

                    # save the faculty
                    faculty_obj.save()
            except IntegrityError as e:
                errors.append(f"Faculty '{faculty_name}' already exists")
            except Exception as e:
                errors.append(f"Error processing faculty '{faculty_name}': {e}")

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Data processed successfully."},
                status=status.HTTP_200_OK,
            )


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


class ProcessDepartments:
    def __init__(self, file):
        self.file = file

    def read_csv_into_key_values(self):
        """
        Read the CSV file and return a dictionary with the key as the faculty name and the value as the department details.
        """
        faculties = {}
        decoded_file = self.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))

        for row in reader:
            levels = [
                level.strip()
                for part in row["level"].split(", ")
                for level in part.split()
            ]
            dept_details = {
                "name": row.get("name", None),
                "short_name": row["short_name"],
                "qualification": row["qualification"],
                "level": levels,
            }
            faculty = row["faculty"]
            faculties.setdefault(faculty, []).append(dept_details)

        return faculties

    def process_data(self):
        faculties = self.read_csv_into_key_values()
        errors = []

        for faculty, depts in faculties.items():
            try:
                faculty_obj = Faculty.objects.get(name__iexact=faculty)

                dept_objs = []
                level_ids = {}

                for dept in depts:
                    level_ids.update(self.get_level_ids(dept["level"]))

                    department_obj = Department.objects.create(
                        name=dept["name"],
                        short_name=dept["short_name"],
                        qualification=dept["qualification"],
                    )
                    department_obj.level.set(level_ids.values())
                    dept_objs.append(department_obj)

                faculty_obj.departments.set(dept_objs)

            except Faculty.DoesNotExist:
                errors.append(f"Faculty '{faculty}' not found.")
            except IntegrityError:
                errors.append(f"Department '{dept['name']}' already exists.")
            except KeyError:
                errors.append(f"Missing required field in CSV file.")
            except Exception as e:
                errors.append(str(e))

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Data processed successfully."},
                status=status.HTTP_200_OK,
            )

    def get_level_ids(self, levels):
        """
        Retrieve or create Level objects and return a dictionary with level names as keys and corresponding IDs as values.
        """
        level_ids = {}
        for level_name in levels:
            if level_name not in level_ids:
                level_obj, _ = Level.objects.get_or_create(level__iexact=level_name)
                level_ids[level_name] = level_obj.id
        return level_ids
