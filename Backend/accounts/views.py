from rest_framework import permissions
from rest_framework import generics
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer
from helpers.responseHandler import success_response, error_response

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("User registered successfully!", 201)
        return error_response(serializer.errors, 400)


class LoginView(APIView):
    permission_classes=[permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(serializer.validated_data, 200)
        return error_response(serializer.errors, 400)


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data, context={"request": request})
        print(serializer)
        if serializer.is_valid():
            refresh_token = serializer.validated_data["refresh_token"]

            try:
                if not refresh_token:
                    return error_response("Refresh token is required", 400)
                token = RefreshToken(refresh_token)

                token.blacklist()


                return success_response("Logout Successfully", 205)

            except Exception as e:
                return error_response("An error occurred during logout. Please try again.",
                    401,
                )

        return error_response(serializer.errors, 400)