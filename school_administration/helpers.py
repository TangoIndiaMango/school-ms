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
        print(reader)

        for row in reader:
            faculty_name = row.get("name", None)
            # print(faculty_name)
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

        return faculties

    def process_data(self):
        """
        Process the data and create the faculty and department objects.
        """
        faculties = self.read_csv_into_key_values()
        # print(faculties)
        errors = []
        #  create faculties
        for faculty_name, faculty_data in faculties.items():
            try:
                with transaction.atomic():
                    faculty_obj, _ = Faculty.objects.get_or_create(
                        name=faculty_data["name"],
                        defaults={"short_name": faculty_data["short_name"]},
                    )

                    dean_name = faculty_data.get("dean", None)
                    if dean_name:
                        dean = Lecturer.objects.filter(name=dean_name).first()
                        faculty_obj.dean = dean

                    department_names = faculty_data.get("departments", [])
                    for department_name in department_names:
                        department_obj = Department.objects.get(
                            name=department_name, faculty=faculty_obj
                        )
                        faculty_obj.departments.set(department_obj)

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


class ProcessDepartments:
    def __init__(self, file, faculty_id):
        self.file = file
        self.faculty_id = faculty_id

    def read_csv_into_key_values(self):
        """
        Read the CSV file and return a dictionary with the key as the faculty name and the value as the department details.
        """
        faculties = {}
        decoded_file = self.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded_file))

        for row in reader:
            levels = [level.strip() for part in row["level"].split(", ") for level in part.split() if level.strip()]
            dept_details = {
                "name": row.get("name", None),
                "short_name": row["short_name"],
                "qualification": row["qualification"],
                "level": levels,
            }
            row["faculty"] = self.faculty_id
            faculties.setdefault(row["faculty"], []).append(dept_details)

        return faculties

    def process_data(self):
        faculties = self.read_csv_into_key_values()
        errors = []
        print("THESE ARE FACULTIES",faculties)

        for faculty, depts in faculties.items():
            try:
                faculty_obj = Faculty.objects.get(id=faculty)
            except Faculty.DoesNotExist:
                errors.append(f"Faculty '{faculty.name}' not found.")
                continue
            for dept in depts:

                try:
                    department_obj, created = Department.objects.get_or_create(
                        name=dept["name"],
                        defaults={
                            "short_name": dept["short_name"],
                            "qualification": dept["qualification"],
                        }
                    )
                    if not created:
                        errors.append(f"Department '{dept['name']}' already exists.")
                        continue
                    faculty_obj.departments.add(department_obj)

                    
                    # if not isinstance(dept["level"], list):
                    #     dept["level"] = [dept["level"]]
                    print("THESE ARE LEVELS", dept["level"])
                    if dept["level"]:
                        for level in dept["level"]:
                            department_unique_name = generate_random_id(dept["short_name"], level)
                            try:
                                level_obj, _ = Level.objects.get_or_create(
                                    name=department_unique_name,
                                    defaults={"level": level},
                                )
                                dept["level"] = level_obj.id
                                department_obj.level.add(level_obj)
                            except Exception as e:
                                errors.append(f"Error getting level '{dept['level']}': {e}")
                            print("Just finished", level)
                except IntegrityError as e:
                    errors.append(f"Error processing department '{dept['name']}': {e}")
                    continue

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Data processed successfully."},
                status=status.HTTP_200_OK,
            )
