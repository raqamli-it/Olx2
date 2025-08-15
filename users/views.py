from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RegisterSerializer, VerifyEmailSerializer
from .models import EmailVerification, User


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        # Email kod yuborish
        verification = EmailVerification.objects.filter(user=user).latest("created_at")
        send_mail(
            subject="Tasdiqlash kodi",
            message=f"Sizning tasdiqlash kodingiz: {verification.code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Email muvaffaqiyatli tasdiqlandi"}, status=status.HTTP_200_OK)
