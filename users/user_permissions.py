from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """only admin users can have this permission

    Args:
        BasePermission (_type_): _description_
    """

    def has_permission(self, request, view):
        return request.user.is_active and request.user.is_admin


class IsStudent(BasePermission):
    """only student users can have this permission

    Args:
        BasePermission (_type_): _description_
    """

    def has_permission(self, request, view):
        return request.user.is_active and request.user.is_student


class IsLecturer(BasePermission):
    """only teacher users can have this permission

    Args:
        BasePermission (_type_): _description_
    """

    def has_permission(self, request, view):
        return request.user.is_active and request.user.is_lecturer
