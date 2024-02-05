# def verify_link(token, email=False):
#     try:
#         v_user = VerificationUser.objects.get(token=token)

from datetime import datetime, timedelta
from django.conf import settings
import jwt
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
from school_administration.models import Department
from users.serializers import CustomUserSerializer
from utils.helpers import generate_random_id
from .models import CustomUser
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.pagination import PageNumberPagination


def get_access_token(payload, hours=24):
    token = jwt.encode(
        {"expiry": datetime.now() + timedelta(hours=hours), **payload},
        settings.SECRET_KEY,
        algorithm="HS256",
        json_encoder=DjangoJSONEncoder,
    )

    return token


def decode_token(bearer_token):
    if not bearer_token:
        return None

    token = bearer_token[7:]

    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return None

    if "user_id" not in decoded_token:
        return None

    try:
        user = CustomUser.objects.get(id=decoded_token["user_id"])
        return user
    except CustomUser.DoesNotExist:
        return None



import csv
import io

# import datetime

# def create_users_from_csv(file, user_role, id_field_name, generate_id_func, serializer_class):
#     decoded_file = file.read().decode('utf-8')
#     reader = csv.DictReader(io.StringIO(decoded_file))
#     year = datetime.date.today().year
#     current_year_slashed = str(year)[-2:]
#     department= "DEPT"

#     created_objects = []
#     errors = []

#     for row in reader:
#         # Prepare user data
#         user_data = {
#             'first_name': row.get('first_name'),
#             'last_name': row.get('last_name'),
#             'email': row.get('email'),
#             'password': get_random_string(12),
#             'phone': row.get('phone'),
#             'role': user_role,
#         }

#         user_serializer = CustomUserSerializer(data=user_data)
#         if user_serializer.is_valid():
#             user = user_serializer.save()
#             row['user'] = user.id
#             row[id_field_name] = generate_id_func(department=department, year=current_year_slashed)
#             obj_serializer = serializer_class(data=row)

#             if obj_serializer.is_valid():
#                 created_objects.append(obj_serializer.validated_data)
#             else:
#                 errors.append(obj_serializer.errors)
#         else:
#             errors.append(user_serializer.errors)

#     return created_objects, errors


# def post(self, request, *args, **kwargs):
# if "student_file" in request.FILES:
#     file = request.FILES["student_file"]
#     decoded_file = file.read().decode("utf-8").splitlines()
#     reader = csv.DictReader(io.StringIO(decoded_file))
#     matric_no = request.data.get("matric_no", None)
#     year = request.data.get("year", self.current_year_slashed)
#     department = request.data.get("department", None)


#     students = []
#     errors = []
#     for row in reader:
#         # Create a CustomUser for each student
#         user_data = {
#             "first_name": row.get("first_name"),
#             "last_name": row.get("last_name"),
#             "email": row.get("email"),
#             "password": get_random_string(12),
#             "phone": row.get("phone"),
#             "role": "student",
#         }
#         user_serializer = CustomUserSerializer(data=user_data)
#         if user_serializer.is_valid():
#             user = user_serializer.save()
#             row["user"] = user.id
#             row["matric_no"] = generate_random_id(
#                 department, year
#             )
#             student_serializer = self.serializer_class(data=row)
#             if student_serializer.is_valid():
#                 students.append(student_serializer.validated_data)
#             else:
#                 errors.append(student_serializer.errors)
#         else:
#             errors.append(user_serializer.errors)

#     if errors:
#         return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
#     else:
#         Student.objects.bulk_create([Student(**data) for data in students])
#         return Response(
#             {"message": "Students created successfully."},
#             status=status.HTTP_200_OK,
#         )
