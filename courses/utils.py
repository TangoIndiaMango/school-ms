import csv
import io
from django.db import transaction
from django.db.models.functions import Lower
from courses.models import Course
from school_administration.models import Department, Level
from school_artifacts.models import Semester

@transaction.atomic
def create_courses_from_csv(file, serializer_class, Model, unique_fields):
    decoded_file = file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded_file))

    # Dictionary to map semester names to corresponding IDs
    semester_dict = {semester.name.lower(): semester.id for semester in Semester.objects.all()}
    
    # Dictionary to map department names to corresponding IDs
    department_dict = {department.name.lower(): department.id for department in Department.objects.all()}
    
    level_dict = {level.level.lower(): level.id for level in Level.objects.all()}

    # Load existing unique fields into a set
    existing_unique_fields = {
        field: set(Model.objects.values_list(Lower(field), flat=True))
        for field in unique_fields
    }

    courses_to_create = []
    errors = []
    for row in reader:
        # Convert keys to lowercase
        row = {key.lower(): value.strip() for key, value in row.items()}
        
        row["course_semester"] = semester_dict.get(row["course_semester"].lower())
        row["department_course"] = department_dict.get(row["department_course"].lower())
        row["course_level"] = level_dict.get(row["course_level"].lower())
        
        if not row["department_course"]:
            errors.append(f"Department not found for course '{row['course_name']}'.")
            continue
  
        serializer = serializer_class(data=row)
        if serializer.is_valid():
            # Check uniqueness for each unique field
            duplicate_fields = [
                field
                for field in unique_fields
                if row[field] in existing_unique_fields[field]
            ]
            if not duplicate_fields:
                # Add lowercase data to existing unique fields set
                for field in unique_fields:
                    existing_unique_fields[field].add(row[field])
                course_instance = serializer.save()
                courses_to_create.append(course_instance)
            else:
                error_message = {
                    field: f"Duplicate value for {field}: {row[field]}"
                    for field in duplicate_fields
                }
                errors.append({"duplicate_error": error_message, "data": row})
        else:
            errors.append(serializer.errors)

    return {
        "data": f"{len(courses_to_create)} courses created successfully.",
        "errors": errors,
    }
