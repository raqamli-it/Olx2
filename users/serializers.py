from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmailVerification

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "full_name", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        # Email verification code yaratamiz
        code = EmailVerification.generate_code()
        EmailVerification.objects.create(user=user, code=code)
        # Email orqali kod yuborish (keyin views.py ichida qilamiz)
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Bunday foydalanuvchi yo‘q")

        try:
            verification = EmailVerification.objects.filter(user=user, code=code).latest("created_at")
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Kod noto‘g‘ri")

        if verification.is_expired():
            raise serializers.ValidationError("Kod muddati tugagan")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.is_active = True
        user.save()
        EmailVerification.objects.filter(user=user).delete()
        return user
