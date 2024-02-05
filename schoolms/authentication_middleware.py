from django.core.exceptions import PermissionDenied
import jwt
from rest_framework.permissions import BasePermission

from users.utils import decode_token


class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, _):
        try:
            auth_token = request.META.get("HTTP_AUTHORIZATION", None)
        except KeyError:
            raise PermissionDenied("Authentication credentials were not provided.")
        
        
        if not auth_token:
            raise PermissionDenied("User is not authorized.")

    
        user = decode_token(auth_token)
        if not user:
            raise PermissionDenied("Invalid token or user does not exist.")

        request.user = user
        return True