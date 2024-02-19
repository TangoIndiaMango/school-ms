from rest_framework import viewsets

from schoolms.authentication_middleware import IsAuthenticatedCustom
from users.user_permissions import IsAdminUser
from .models import Session, Semester
from .serializers import SessionSerializer, SemesterSerializer
from rest_framework import status
from rest_framework.response import Response


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    permission_classes = (
        IsAuthenticatedCustom,
        IsAdminUser,
    )

    def create(self, request, *args, **kwargs):
        session = request.data.get("session")
        # get setion from the sesion table
        session_obj = Session.objects.get(id=session)

        request.data["session"] = session_obj.id
        # then we go ahead to serialize and save
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        session_obj.semesters.add(serializer.data["id"])

        return Response(
            {"message": "Semester created", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

def get_active_session(request):
    session = Session.objects.filter(is_active=True).first()
    if session:
        return Response(
            {"message": "Active Session", "data": SessionSerializer(session).data},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"message": "No active session found"}, status=status.HTTP_404_NOT_FOUND
    )

def get_active_semester(request):
    semester = Semester.objects.filter(is_active=True, session__isactive=True).first()
    if semester:
        return Response(
            {"message": "Active Semester", "data": SemesterSerializer(semester).data},
            status=status.HTTP_200_OK,
        )
    return Response(
        {"message": "No active semester found"}, status=status.HTTP_404_NOT_FOUND
    )

def get_active_semester():
    return Semester.objects.filter(is_active=True, session__is_active=True).first()
