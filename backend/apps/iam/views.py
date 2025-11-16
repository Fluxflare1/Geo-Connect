from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .serializers import (
    LoginSerializer, 
    MeSerializer, 
    MeUpdateSerializer, 
    ChangePasswordSerializer
)


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


class MeView(APIView):
    """
    GET  /api/v1/auth/me       -> current user profile
    PATCH /api/v1/auth/me      -> update basic profile fields
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = MeUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MeSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    POST /api/v1/auth/change-password
    Body: { "old_password": "...", "new_password": "..." }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Optionally you can invalidate refresh tokens here if you're using JWT,
        # e.g. by blacklisting the current token.
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )
