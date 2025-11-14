from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import LoginSerializer, MeSerializer


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result["user"]

        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "tenant_id": str(user.tenant_id) if user.tenant_id else None,
                    "email": user.email,
                    "roles": [user.role],
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "tokens": {
                    "access_token": result["access_token"],
                    "refresh_token": result["refresh_token"],
                    "expires_in": 3600,
                    "token_type": "Bearer",
                },
            },
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user
