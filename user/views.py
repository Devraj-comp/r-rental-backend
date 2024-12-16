from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, UserProfileSerializer

from rest_framework.exceptions import NotAuthenticated

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authentication import TokenAuthentication

from rest_framework.exceptions import ValidationError

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # token['role'] = user.role
        try:
            token['role'] = user.userprofile.role
            token['id'] = user.userprofile.id
            print('this user_id', token['id'])
        except:
            token['role'] = 'undefined'
            token['id'] = 'undefined'
        # ...

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    # permission_classes = (permissions.AllowAny)
    permission_classes = [permissions.AllowAny]


class UserCreateView(APIView):
    def post(self, request, format = None):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"msg": "User created successfully. "}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

# class UserListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     def get(self, request, format=None):
#         profiles = UserProfile.objects.all()
#         serializer = UserProfileSerializer(profiles, many=True)
#         return Response(serializer.data)

# class UserListView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     def get(self, request, format=None):
#         try:
#             profiles = request.user.userprofile
#             serializer = UserProfileSerializer(UserProfile)
#             return Response(serializer.data, status=200)
#         except:
#             return Response({"detail": "User profile not found."}, status=404)

class CurrentUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        print("Auth user: ", request.user)
        print("Auth header: ", request.META.get('HTTP_AUTHORIZATION'))
        try:
            # Ensure the user has a profile, then return the profile's data
            user_profile = request.user.userprofile
            return Response({
                'username': request.user.username,
                'email': request.user.email,
                'role': user_profile.role,
                'id': user_profile.id,
            })
        except AttributeError:
            raise NotAuthenticated(detail = "Authentication credentifals were not provided")
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)
        
class UserListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [JWTAuthentication]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    http_method_names = ['get']
    lookup_field = 'id'


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    

# google sigin
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework_simplejwt.tokens import RefreshToken

from google.auth.transport import requests
from google.oauth2 import id_token as google_id_token
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests as external_requests
from django.conf import settings

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def exchange_auth_code(self, code):
        # Exchange authorization code for tokens
        token_endpoint = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": "http://localhost:8000/user/api/v1/auth/google-login/",
            "grant_type": "authorization_code",
        }
        response = external_requests.post(token_endpoint, data=data)
        
        if response.status_code == 200:
            return response.json()
        return {"error": response.json()}

    def verify_google_token(self, id_token):
        try:
            # Verify and decode the ID token
            CLIENT_ID = settings.GOOGLE_OAUTH_CLIENT_ID
            id_info = google_id_token.verify_oauth2_token(id_token, requests.Request(), CLIENT_ID)

            return {
                "email": id_info["email"],
                "name": id_info.get("name"),
                "picture": id_info.get("picture"),
                "google_id": id_info["sub"],
            }
        except ValueError as e:
            return {"error": str(e)}

    def get_or_create_google_user(self, email, name):
        user = User.objects.filter(email=email).first()
        if user:
            return user, False
        else:
            # Create a new user
            user = User.objects.create_user(
                username=email.split("@")[0],
                email=email,
                first_name=name.split()[0] if name else "",
                last_name=" ".join(name.split()[1:]) if name else "",
                password=None,  # No password for Google login
            )
            return user, True

    def generate_jwt_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def get(self, request, *args, **kwargs):
        # Handle redirect from Google with authorization code
        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange authorization code for tokens
        tokens = self.exchange_auth_code(code)
        if "error" in tokens:
            return Response({"error": tokens["error"]}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the ID token and get user info
        id_token = tokens.get("id_token")
        google_user = self.verify_google_token(id_token)
        if "error" in google_user:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

        # Create or retrieve the user
        user, created = self.get_or_create_google_user(google_user["email"], google_user["name"])

        # Generate JWT tokens
        jwt_token = self.generate_jwt_for_user(user)
        print("Google login flow completed successfully")

        return Response({
            "access": jwt_token["access"],
            "refresh": jwt_token["refresh"],
            "user": {
                "email": user.email,
                "name": f"{user.first_name} {user.last_name}",
            },
        }, status=status.HTTP_200_OK)


# class GoogleLoginView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def verify_google_token(self, token):
#         try:
#             id_info = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

#             return {
#                 "email": id_info["email"],
#                 "name": id_info.get("name"),
#                 "picture": id_info.get("picture"),
#                 "google_id": id_info["sub"],
#             }
#         except ValueError as e:
#             return {"error": str(e)}

#     def get_or_create_google_user(self, email, name):
#         user = User.objects.filter(email=email).first()
#         if user:
#             return user, False
#         else:
#             # Create a new user
#             user = User.objects.create_user(
#                 username=email.split("@")[0],
#                 email=email,
#                 first_name=name.split()[0] if name else "",
#                 last_name=" ".join(name.split()[1:]) if name else "",
#                 password=None,  # No password for Google login
#             )
#             return user, True

#     def generate_jwt_for_user(self, user):
#         refresh = RefreshToken.for_user(user)
#         return {
#             "access": str(refresh.access_token),
#             "refresh": str(refresh),
#         }

#     def post(self, request, *args, **kwargs):
#         id_token = request.data.get("id_token")

#         # Verify the token
#         google_user = self.verify_google_token(id_token)
#         if "error" in google_user:
#             return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

#         # Retrieve or create the user
#         user, created = self.get_or_create_google_user(google_user["email"], google_user["name"])

#         # Generate JWT tokens
#         jwt_token = self.generate_jwt_for_user(user)
#         print("the google login view function is triggered")

#         return Response({
#             "access": jwt_token["access"],
#             "refresh": jwt_token["refresh"],
#             "user": {
#                 "email": user.email,
#                 "name": f"{user.first_name} {user.last_name}",
#             },
#         }, status=status.HTTP_200_OK)


        
# google login view DRF
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings

# callback view
from urllib.parse import urljoin
import json
import requests
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import jwt
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from allauth.socialaccount.models import SocialToken, SocialAccount


# # new google login callback
# class GoogleSignupCallback(APIView):

@login_required
def google_login_callback(request):
    user = request.user

    social_accounts = SocialAccount.objects.filter(user=user)
    print("Social accound for user:", social_accounts)

    social_account = social_accounts.first()

    if not social_account:
        print("No scoial account for user:", user)
        return redirect('http://localhost:8000/login/callback/?error=NoSocialAccount')
    token = SocialToken.objects.filter(account=social_account, account__providers='google').first()

    if token:
        print('Google token found:', token.token)
        refresh = RefreshToken.objects.filter(user)
        access_token = str(refresh.access_tokne)
        return redirect(f'http://localhost:8000/login/callback/?access_token={access_token}')
    else:
        print('No google token found for user', user)
        return redirect(f'http://localhost:8000/login/callback/?error=NoGoogleToken')

@csrf_exempt
def validate_google_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            google_access_token = data.get('access_token')
            print(google_access_token)

            if not google_access_token:
                return JsonResponse({'detail': 'Access token is missing'}, status=400)
            return JsonResponse({'valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON'}, status=400)
    return JsonResponse({'detail': 'Method not allowed'}, statusj=405)

class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        # googlelogin function

        code = request.GET.get("code")
        if not code:
            return Response({"error": "Authorization code not provided"}, status=400)

        # Exchange the authorization code for access and ID tokens
        token_endpoint = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,  # Add this to your Django settings
            "redirect_uri": "http://localhost:8000/user/api/v1/auth/google/callback/",
            "grant_type": "authorization_code",
        }

        try:
            response = requests.post(token_endpoint, data=data)
            response.raise_for_status()
            tokens = response.json()

            # Extract ID token and access token
            id_token = tokens.get("id_token")
            access_token = tokens.get("access_token")

            decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})
            print("the decodes: ",decoded_id_token)
            print("the google login callback function is triggered")

            return Response({
                "id_token": id_token,
                "access_token": access_token,
            })
        
        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=400)
        


from .models import *
from .serializers import *
from .services import *
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView

class GoogleLoginApi(APIView):
    def get(self, request, *args, **kwargs):
        auth_serializer = AuthSerializer(data=request.GET)
        auth_serializer.is_valid(raise_exception=True)
        
        validated_data = auth_serializer.validated_data
        user_data, jwt_token = createJwtToken(validated_data)
        
        response = redirect(settings.BASE_APP_URL)
        response.set_cookie('dsandeavour_access_token', jwt_token, max_age = 60 * 24 * 60 * 60)
        return response
    
    def post(self, request, *args, **kwargs):
        pass