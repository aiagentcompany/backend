from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .tokens import account_activation_token
from .email_utils import send_email
from .serializers import *

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        link = f"{os.getenv('FRONTEND_ACTIVATION_URL')}{token}&uid={uid}"
        send_email("Verify Your Email", f"Click to verify: {link}", [user.email])

class ActivateView(generics.GenericAPIView):
    def get(self, request):
        uid = request.GET.get("uid")
        token = request.GET.get("token")
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            if account_activation_token.check_token(user, token):
                user.is_active = True
                user.save()
                return Response({"status": "verified"})
        except:
            pass
        return Response({"error": "Invalid link"}, status=400)

class ResetRequestView(generics.GenericAPIView):
    serializer_class = ResetRequestSerializer

    def post(self, request):
        email = request.data["email"]
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            link = f"{os.getenv('FRONTEND_RESET_URL')}{token}&uid={uid}"
            send_email("Reset Password", f"Click to reset: {link}", [user.email])
        except User.DoesNotExist:
            pass
        return Response({"status": "email sent"})

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        token = request.data["token"]
        uid = force_str(urlsafe_base64_decode(request.data["uid"]))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.set_password(request.data["password"])
            user.save()
            return Response({"status": "password reset"})
        return Response({"error": "Invalid token"}, status=400)
