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