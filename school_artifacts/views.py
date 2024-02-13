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
        session_obj = Session.objects.get(name=session)

        request.data["session"] = session_obj.id
        # then we go ahead to serialize and save
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Semester created", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
